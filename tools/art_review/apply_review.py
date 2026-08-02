#!/usr/bin/env python3
"""apply_review.py -- wire art-review verdicts into the P(Doom)1 asset pipeline.

The review app writes a verdict-state file (default
``tools/art_review/review_state.json``) keyed by asset_id:

    gen:<category>:<base_id>:<variant>   generated art, file lives at
        <art-root>/art_generated/<category>/v1/<base_id>_<variant>_<size>.png
    px:<relpath>                         pixellab art, file/dir lives at
        <art-root>/art_source/<relpath>  (relpath may point at a single PNG, a
        rotation directory of PNGs, or -- the review app's usual form -- a PNG
        path WITHOUT its .png extension; the resolver tries all of these)

Each value is ``{verdict, note, tags, updated_at}`` with verdict in
{keep, iterate, discard} (the review app's v2 tri-state). Legacy files still
carrying the old {keep, maybe, reroll} model are migrated on read: maybe and
reroll both fold into ``iterate``; ``discard`` is new.

Verdict semantics:
    keep     accept the asset as-is.
    iterate  on-brief but not final -> REGENERATE to compare/hone (the reroll
             action emits these). The old maybe/reroll both land here.
    discard  OFF-brief / wrong direction -> NOT regenerated; it signals the brief
             itself needs reconsidering. The report lists these (with notes) as a
             brief-reconsideration list; they never enter the regenerate manifest.

Three actions, all supporting --dry-run and --art-root (default "."):

    report    Count + list keep/iterate/discard verdicts, PLUS the promotion
              gate: promotable vs blocked vs held counts for every KEEP.
              EXITS NONZERO if any KEEP is blocked (unmapped category,
              unresolvable source, or nothing under the 1MB git cap) -- an
              approved asset that cannot move is a pipeline bug and must fail
              at review time, not surface silently at promote time
              (silent-wrongness family: issues #1027 / #1075). Discards are
              surfaced WITH their notes as a brief-reconsideration list.
    promote   Copy each KEEP asset's PNG (largest size that fits the 1MB git
              cap, for generated art) into the correct godot/assets/
              destination, creating dirs as needed. Files over the cap are
              NEVER copied (pre-commit check-added-large-files --maxkb=1000
              would reject the commit anyway; docs/art/ART_MASTERS_POLICY.md).
              Exits nonzero if any KEEP was blocked.
    reroll    Emit tools/assets/manifests/reroll_<YYYY-MM-DD>.json describing each
              ITERATE asset (id, category, source_file, note, original_prompt),
              split by pipeline (gpt vs pixellab) to feed the next generation run.
              (Discards are deliberately excluded -- they are brief problems, not
              re-roll fodder.)

Stdlib only; no third-party deps. Godot must run an --import pass after a promote
to register the new files -- this tool never launches Godot.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import shutil
import sys
from pathlib import Path

# --- category -> godot/assets destination map ------------------------------
# Keyed by the asset's category. For generated art the category is the
# art_generated/<category> subdir (== the manifest's asset_type). For pixellab
# art the category is derived from the relpath (see _px_category).
#
# A mapping value is one of:
#   str                     destination dir under the art root
#   list[(prefix, str)]     per-base_id-prefix routing, first match wins,
#                           "" as catch-all (round3_rerolls mixes action
#                           icons with dossier/painterly portraits)
#   Hold(reason)            EXPLICITLY not-for-promotion. Reviewed art that
#                           must NOT enter godot/ -- Godot packs the entire
#                           godot/ tree into the .pck (issue #787), so a
#                           wrong destination silently bloats the build.
#
# INVARIANT (enforced by report's promotion gate + tests/test_art_promotion_pipeline.py):
# every category that can appear in review_state.json MUST resolve to a str or
# a Hold. An unmapped category is a loud failure, never a silent skip.


class Hold:
    """Explicit not-for-promotion marker: a legitimate mapping outcome."""

    def __init__(self, reason):
        self.reason = reason


GEN_DEST = {
    "game_icons": "godot/assets/icons/generated",
    "ui_icons": "godot/assets/icons/generated",
    "action_icons_missing": "godot/assets/icons/generated",
    "iconset_round2": "godot/assets/icons/generated",
    "core_resource_icons": "godot/assets/icons/generated",
    "round3_rerolls": [
        ("dossier_", "godot/assets/portraits/generated"),
        ("painterly_", "godot/assets/portraits/generated"),
        ("", "godot/assets/icons/generated"),
    ],
    "researcher_portraits_pilot": "godot/assets/portraits/generated",
    "hero_banners": "godot/assets/images/heroes",
    "round3_rerolls_banners": "godot/assets/images/heroes",
    "screen_backgrounds": "godot/assets/images/backgrounds",
    "env_scenes": "godot/assets/images/scenes",
    "scene_art_wave2": "godot/assets/images/scenes",
    "terminal_textures": "godot/assets/textures/generated",
    "env_textures": "godot/assets/textures/generated",
    "crt_frame_overlay": "godot/assets/textures/generated",
    "ui_frames": "godot/assets/ui/frames",
}
PX_DEST = {
    "props": "godot/assets/office_floor/props",
    "characters": "godot/assets/office_floor/characters",
    # was office_floor/tiles -- no such dir exists; the game's tilesets live
    # in godot/assets/office_floor/tilesets (latent wrong-destination fix).
    "tilesets": "godot/assets/office_floor/tilesets",
    "cats": "godot/assets/cats/generated",
    "icons": "godot/assets/icons/generated",
    "backgrounds": "godot/assets/images/backgrounds",
    "icon_hires": Hold(
        "hi-res icon source variants (issue #787 bloat class): the game references "
        "sized icons already in godot/assets/icons; re-importing ~318 files (~52MB) "
        "needs Pip's explicit ruling"
    ),
}
# first-path-segment overrides: batch dirs whose names would fool the token
# scan (e.g. iconset_2026-07-21's gen_cat_doom_* must NOT land in cats/).
PX_PREFIX_CATEGORY = {
    "icon_hires": "icon_hires",
    "iconset_2026-07-21": "icons",
    "settings_bg_2026-07-21": "backgrounds",
    "cats_incoming": "cats",
}
# relpath segment -> category (any segment, first match in path order).
PX_TOKEN_CATEGORY = {
    "props": "props",
    "objects": "props",
    "chairs": "props",
    "kitchen": "props",
    "windows": "props",
    "environment": "props",
    "characters": "characters",
    "founder": "characters",
    "cosmetics": "characters",
    "tilesets": "tilesets",
    "cats": "cats",
    "icons": "icons",
}
# batch dirs whose ROOT-level loose files are character style probes.
PX_BATCH_DEFAULT_CATEGORY = {"pixellab_2026-07-16": "characters"}

# git art cap: pre-commit check-added-large-files runs with --maxkb=1000 and
# docs/art/ART_MASTERS_POLICY.md forbids >1MB art in git. Anything bigger can
# NEVER be committed, so promote must never copy it into godot/.
MAX_PROMOTE_BYTES = 1000 * 1024

DEFAULT_STATE = "tools/art_review/review_state.json"
MANIFEST_DIR = "tools/assets/manifests"
VERDICTS = ("keep", "iterate", "discard")
# legacy -> v2; applied on read so pre-v2 state files still work.
VERDICT_MIGRATE = {"maybe": "iterate", "reroll": "iterate"}


def migrate_verdict(raw):
    """Normalise a stored verdict to the v2 model. keep/iterate/discard pass
    through; legacy maybe/reroll fold into iterate; anything else -> ''."""
    v = (raw or "").strip().lower()
    if v in VERDICTS:
        return v
    return VERDICT_MIGRATE.get(v, "")


# --- asset_id parsing / resolution -----------------------------------------
class Asset:
    """A parsed review entry with its resolved source file(s)."""

    def __init__(self, asset_id, verdict, note, tags, art_root):
        self.id = asset_id
        self.verdict = verdict
        self.note = note or ""
        self.tags = tags or []
        self.art_root = art_root
        self.kind = None  # "gen" | "px" | None (unparseable)
        self.category = None
        self.base_id = None  # gen only
        self.variant = None  # gen only
        self.relpath = None  # px only
        self.pipeline = None  # "gpt" | "pixellab"
        self.sources = []  # list[Path] of resolved existing PNGs
        self.promote_file = None  # Path chosen to promote (largest UNDER-CAP for gen)
        self.best_file = None  # largest file regardless of cap (reroll reporting)
        self.size_capped = False  # True if the cap forced a smaller pick than best
        self.error = None
        self._parse()

    # -- parse the id and resolve files on disk --
    def _parse(self):
        if self.id.startswith("gen:"):
            self.kind = "gen"
            self.pipeline = "gpt"
            self._parse_gen()
        elif self.id.startswith("px:"):
            self.kind = "px"
            self.pipeline = "pixellab"
            self._parse_px()
        else:
            self.error = "unrecognised asset_id prefix (expected gen: or px:)"

    def _parse_gen(self):
        # gen:<category>:<base_id>:<variant>  -- base_id may itself contain no
        # colon in practice, but split defensively: first token category, last
        # token variant, everything between is the base_id.
        parts = self.id.split(":")
        if len(parts) < 4:
            self.error = "malformed gen id (need gen:<category>:<base_id>:<variant>)"
            return
        self.category = parts[1]
        self.variant = parts[-1]
        self.base_id = ":".join(parts[2:-1])
        gen_dir = self.art_root / "art_generated" / self.category / "v1"
        pattern = f"{self.base_id}_{self.variant}_*.png"
        matches = sorted(gen_dir.glob(pattern))
        if not matches:
            # Some categories (e.g. ui_icons) write <base_id>_<size>.png with no
            # _<variant> segment. Fall back to matching on base_id alone.
            fallback = sorted(gen_dir.glob(f"{self.base_id}_*.png"))
            matches = [m for m in fallback if _looks_like_size_stem(m, self.base_id)]
        if not matches:
            self.error = f"no file matching {gen_dir}/{pattern}"
            return
        self.sources = matches
        self.best_file = _largest_by_size(matches)
        fits = [m for m in matches if m.stat().st_size <= MAX_PROMOTE_BYTES]
        self.promote_file = _largest_by_size(fits) if fits else None
        self.size_capped = bool(fits) and self.promote_file != self.best_file

    def _parse_px(self):
        self.relpath = self.id[len("px:") :]
        # relpath may be given relative to art_source/ (natural) or relative to
        # the art-root (includes the leading art_source/). The review app also
        # writes single-PNG relpaths WITHOUT the .png extension. Try, in order:
        # each base as-is (file or rotation dir), then base + ".png".
        candidates = []
        for base in (self.art_root / "art_source" / self.relpath, self.art_root / self.relpath):
            candidates.append(base)
            candidates.append(base.with_name(base.name + ".png"))
        target = next((c for c in candidates if c.exists()), None)
        if target is None:
            tried = "; ".join(str(c) for c in candidates)
            self.error = f"no file/dir at any of: {tried}"
            return
        self._target_is_dir = target.is_dir()
        if self._target_is_dir:
            self.sources = sorted(target.glob("*.png"))
            if not self.sources:
                self.error = f"directory {target} has no PNGs"
                return
        else:
            self.sources = [target]
        self.category = _px_category(self.relpath)
        # promote copies every under-cap source PNG for px (rotation sets stay
        # together); promote_file holds the first for reporting convenience.
        self.best_file = self.sources[0]
        fits = [s for s in self.sources if s.stat().st_size <= MAX_PROMOTE_BYTES]
        self.promote_file = fits[0] if fits else None
        self.size_capped = bool(fits) and len(fits) != len(self.sources)

    # -- destination mapping for a promote --
    def dest_rule(self):
        """Raw mapping outcome: a destination str, a Hold, or None (unmapped)."""
        if self.kind == "gen":
            return _gen_dest_rel(self.category, self.base_id)
        if self.kind == "px":
            return PX_DEST.get(self.category) if self.category else None
        return None

    def dest_dir(self):
        rel = self.dest_rule()
        return (self.art_root / rel) if isinstance(rel, str) else None

    def promote_sources(self):
        """Source files promote would copy: all under-cap PNGs for px, the
        largest under-cap size for gen. Empty if nothing fits the git cap."""
        if self.kind == "gen":
            return [self.promote_file] if self.promote_file else []
        return [s for s in self.sources if s.stat().st_size <= MAX_PROMOTE_BYTES]

    def promotion_status(self):
        """Classify a KEEP asset for the promotion gate.

        Returns (status, detail) with status one of:
          promotable          -> detail = destination rel path
          held                -> detail = Hold reason (explicit not-for-promotion)
          blocked-unresolved  -> detail = resolution error (pipeline bug)
          blocked-unmapped    -> detail = missing category mapping (pipeline bug)
          blocked-size        -> detail = nothing fits the 1MB git cap
        """
        if self.error:
            return ("blocked-unresolved", self.error)
        rule = self.dest_rule()
        if rule is None:
            return ("blocked-unmapped", f"no destination for category {self.category!r}")
        if isinstance(rule, Hold):
            return ("held", rule.reason)
        if not self.promote_sources():
            return (
                "blocked-size",
                "every candidate file exceeds the 1MB git cap "
                "(docs/art/ART_MASTERS_POLICY.md; pre-commit --maxkb=1000)",
            )
        return ("promotable", rule)

    def dest_name(self, src: Path):
        """Destination path RELATIVE to dest_dir (may contain subdirs for px)."""
        # generated: strip the _<variant> suffix for a clean game path
        # (matches promote_assets.py convention: art id vN -> base name).
        if self.kind == "gen":
            stem = src.stem  # e.g. icon_doom_v2_1024
            marker = f"_{self.variant}_"
            if marker in stem:
                stem = stem.replace(marker, "_", 1)
            return stem + src.suffix
        # pixellab: the leaf filename alone is NOT the identity -- e.g.
        # cat_walk_cat1/walk_east_0 vs cat_walk_cat2/walk_east_0 are different
        # cats. Preserve the relpath below the batch dir (dropping segments
        # that merely repeat this asset's category token), mirroring the
        # existing per-set dirs under godot/assets/office_floor/.
        parts = [
            seg
            for seg in Path(self.relpath).as_posix().split("/")[1:]
            if PX_TOKEN_CATEGORY.get(seg) != self.category
        ]
        if not self._target_is_dir and parts:
            parts = parts[:-1]  # last segment names the file itself; use src.name
        return "/".join(parts + [src.name]) if parts else src.name


def _looks_like_size_stem(path: Path, base_id: str):
    """True if path stem is <base_id>_<int> or <base_id>_<variant>_<int>."""
    stem = path.stem
    if not stem.startswith(base_id + "_"):
        return False
    tail = stem[len(base_id) + 1 :].split("_")[-1]
    return tail.isdigit()


def _largest_by_size(paths):
    """Pick the PNG with the largest trailing _<size> in the filename."""

    def size_of(p: Path):
        stem = p.stem
        tail = stem.rsplit("_", 1)[-1]
        try:
            return int(tail)
        except ValueError:
            return -1

    return max(paths, key=size_of)


def _px_category(relpath: str):
    """Category for a pixellab relpath. Precedence: batch-dir override,
    then segment tokens, then the loose "cat" fallback, then batch default."""
    parts = Path(relpath).as_posix().split("/")
    if parts and parts[0] in PX_PREFIX_CATEGORY:
        return PX_PREFIX_CATEGORY[parts[0]]
    for seg in parts:
        if seg in PX_TOKEN_CATEGORY:
            return PX_TOKEN_CATEGORY[seg]
    # loose fallback: any segment containing "cat" -> cats
    if any("cat" in seg for seg in parts):
        return "cats"
    if parts and parts[0] in PX_BATCH_DEFAULT_CATEGORY:
        return PX_BATCH_DEFAULT_CATEGORY[parts[0]]
    return None


def _gen_dest_rel(category, base_id):
    """Destination for a generated-art category: str, Hold, or None.
    List rules route by base_id prefix, first match wins ("" = catch-all)."""
    rule = GEN_DEST.get(category)
    if rule is None or isinstance(rule, (str, Hold)):
        return rule
    for prefix, dest in rule:
        if (base_id or "").startswith(prefix):
            return dest
    return None


def _fmt_rule(rule):
    if isinstance(rule, Hold):
        return "[NOT FOR PROMOTION] " + rule.reason
    if isinstance(rule, str):
        return rule
    return "; ".join("{} -> {}".format(p or "*", d) for p, d in rule)


# --- review_state.json loading ---------------------------------------------
def load_state(state_path: Path):
    if not state_path.is_file():
        return None
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"error: {state_path} is not valid JSON: {e}")
    if not isinstance(raw, dict) or not raw:
        return {}
    return raw


def parse_assets(state: dict, art_root: Path):
    assets = []
    for asset_id, val in state.items():
        if not isinstance(val, dict):
            continue
        verdict = migrate_verdict(val.get("verdict"))
        if verdict not in VERDICTS:
            continue
        assets.append(Asset(asset_id, verdict, val.get("note"), val.get("tags"), art_root))
    return assets


# --- original_prompt lookup (gpt manifests) --------------------------------
def build_prompt_index(art_root: Path):
    """Map base_id -> prompt from every gpt manifest under tools/assets/manifests.

    A manifest asset's prompt is its ``prompt`` or ``prompt_tail`` field. Files
    without an ``assets`` list (e.g. our own reroll_*.json) are skipped.
    """
    index = {}
    mdir = art_root / MANIFEST_DIR
    if not mdir.is_dir():
        return index
    for mf in sorted(mdir.glob("*.json")):
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        assets = data.get("assets") if isinstance(data, dict) else None
        if not isinstance(assets, list):
            continue
        for a in assets:
            if not isinstance(a, dict):
                continue
            aid = a.get("id")
            if not aid:
                continue
            prompt = a.get("prompt") or a.get("prompt_tail") or ""
            index[aid] = {"prompt": prompt, "manifest": mf.name}
    return index


# --- actions ----------------------------------------------------------------
STATUS_FLAG = {
    "promotable": "",
    "held": "  [HELD]",
    "blocked-unresolved": "  [UNRESOLVED]",
    "blocked-unmapped": "  [NO-DEST]",
    "blocked-size": "  [OVER-1MB]",
}
BLOCKED_STATUSES = ("blocked-unmapped", "blocked-unresolved", "blocked-size")


def _contested(promotables):
    """Destinations claimed by more than one promotable KEEP.

    dest_name strips the variant marker (art id vN -> base name), so keeping
    BOTH v1 and v2 of a base makes them collapse onto ONE game path -- the
    last copy would silently win. Returns {dest Path: [Asset, ...]} for every
    contested destination.
    """
    claims = {}
    for a in promotables:
        dest_dir = a.dest_dir()
        for src in a.promote_sources():
            claims.setdefault(dest_dir / a.dest_name(src), []).append(a)
    return {d: ass for d, ass in claims.items() if len(ass) > 1}


def _promotion_gate(keeps):
    """Bucket KEEP assets by promotion status.

    Returns (buckets, n_blocked, contested) where buckets adds a "contested"
    bucket (assets whose destination collides with another keep's -- pulled
    OUT of promotable), n_blocked counts per-asset pipeline bugs, and
    contested is the {dest: [assets]} collision map.
    """
    buckets = {s: [] for s in STATUS_FLAG}
    buckets["contested"] = []
    for a in keeps:
        buckets[a.promotion_status()[0]].append(a)
    contested = _contested(buckets["promotable"])
    if contested:
        losers = []
        seen = set()
        for ass in contested.values():
            for a in ass:
                if id(a) not in seen:
                    seen.add(id(a))
                    losers.append(a)
        buckets["contested"] = losers
        buckets["promotable"] = [a for a in buckets["promotable"] if id(a) not in seen]
    n_blocked = sum(len(buckets[s]) for s in BLOCKED_STATUSES)
    return buckets, n_blocked, contested


def action_report(assets):
    groups = {v: [] for v in VERDICTS}
    for a in assets:
        groups[a.verdict].append(a)
    print("== review verdict report ==")
    print(
        "counts: keep={} iterate={} discard={} (total {})".format(
            len(groups["keep"]), len(groups["iterate"]), len(groups["discard"]), len(assets)
        )
    )
    print("  keep    -> promote     iterate -> regenerate (reroll)     discard -> rethink brief")

    # -- promotion gate: a keep that cannot move is a pipeline bug, and it
    # must fail HERE, at review time -- not silently at promote time
    # (silent-wrongness family, issues #1027 / #1075).
    keeps = groups["keep"]
    buckets, n_blocked, contested = _promotion_gate(keeps)
    n_bytes = sum(f.stat().st_size for a in buckets["promotable"] for f in a.promote_sources())
    print("\n== promotion gate (keeps only) ==")
    print(
        "promotable: {} of {} keeps ({:.1f} MB would enter godot/assets)".format(
            len(buckets["promotable"]), len(keeps), n_bytes / 1e6
        )
    )
    print(
        "held (explicit not-for-promotion): {}    contested-destination: {}    "
        "blocked: {} (unmapped-category={} unresolved-source={} over-size-cap={})".format(
            len(buckets["held"]),
            len(buckets["contested"]),
            n_blocked,
            len(buckets["blocked-unmapped"]),
            len(buckets["blocked-unresolved"]),
            len(buckets["blocked-size"]),
        )
    )
    if buckets["held"]:
        reasons = {}
        for a in buckets["held"]:
            reasons.setdefault(a.promotion_status()[1], []).append(a)
        for reason, items in reasons.items():
            print(f"  held x{len(items)}: {reason}")
    if contested:
        print(
            "\n[FAIL] {} destination path(s) contested by {} keeps -- multiple kept "
            "variants collapse onto one game filename (variant marker is stripped); "
            "the last copy would silently overwrite the rest. Un-keep all but one "
            "variant per base, or rule on a naming change:".format(
                len(contested), len(buckets["contested"])
            )
        )
        for dest, ass in sorted(contested.items(), key=lambda kv: str(kv[0]))[:15]:
            ids = ", ".join(a.id for a in ass)
            print(f"  {dest.name}  <-  {ids}")
        if len(contested) > 15:
            print(f"  ... and {len(contested) - 15} more contested destination(s)")
    if n_blocked:
        print("\n[FAIL] {} approved asset(s) cannot be promoted -- pipeline bug:".format(n_blocked))
        for status in BLOCKED_STATUSES:
            rollup = {}
            for a in buckets[status]:
                key = a.promotion_status()[1] if status != "blocked-unresolved" else a.category
                rollup.setdefault(key, []).append(a)
            for key, items in sorted(rollup.items(), key=lambda kv: -len(kv[1])):
                print(f"  {status} x{len(items)}: {key}  (e.g. {items[0].id})")
        print("  fix the map/resolver in tools/art_review/apply_review.py; this report")
        print("  exits nonzero until every keep is promotable or explicitly held.")

    for v in VERDICTS:
        print(f"\n-- {v} ({len(groups[v])}) --")
        for a in groups[v]:
            loc = a.error if a.error else str(a.promote_file or a.best_file)
            flag = STATUS_FLAG.get(a.promotion_status()[0], "") if a.verdict == "keep" else ""
            print(f"  {a.id}{flag}")
            print(f"      pipeline={a.pipeline} category={a.category} -> {loc}")
            if a.note:
                print(f"      note: {a.note}")
    # a dedicated brief-reconsideration list: discards are the loudest signal
    # that a brief is wrong, so spotlight them (with notes) at the end.
    discards = groups["discard"]
    print(f"\n== brief-reconsideration list (discards: {len(discards)}) ==")
    if not discards:
        print("  none -- no OFF-brief assets flagged.")
    else:
        print("  These are OFF-brief / wrong-direction. They are NOT regenerated;")
        print("  treat each as a prompt to reconsider the brief itself.")
        for a in discards:
            note = a.note.strip() if a.note else "(no note given)"
            print(f"  - {a.id}")
            print(f"      {note}")
    n_gate_fail = n_blocked + len(buckets["contested"])
    if n_gate_fail:
        print(
            f"\n[FAIL] promotion gate: {n_blocked} keep(s) blocked, "
            f"{len(buckets['contested'])} contested (see gate summary above)."
        )
        return 1
    return 0


def action_promote(assets, dry_run):
    keeps = [a for a in assets if a.verdict == "keep"]
    print("== promote KEEP assets ==")
    print("category -> destination map in use:")
    for k, v in sorted(GEN_DEST.items()):
        print(f"  gen  {k:<28} -> {_fmt_rule(v)}")
    for k, v in sorted(PX_DEST.items()):
        print(f"  px   {k:<28} -> {_fmt_rule(v)}")
    print()
    if not keeps:
        print("no keep verdicts -- nothing to promote.")
        return 0
    _, _, contested = _promotion_gate(keeps)
    contested_ids = {a.id for ass in contested.values() for a in ass}
    n_copied = n_skipped = n_held = n_capped = n_contested = 0
    n_bytes = 0
    for a in keeps:
        status, detail = a.promotion_status()
        if status == "held":
            print(f"HOLD {a.id}: {detail}")
            n_held += 1
            continue
        if status in BLOCKED_STATUSES:
            print(f"SKIP {a.id}: {detail}")
            n_skipped += 1
            continue
        if a.id in contested_ids:
            print(f"CONTEST {a.id}: destination filename claimed by another keep (see report)")
            n_contested += 1
            continue
        dest_dir = a.dest_dir()
        if a.size_capped:
            n_capped += 1
        # generated: one file (largest under the git cap). pixellab: every
        # under-cap source PNG. Over-cap files are NEVER copied -- pre-commit
        # check-added-large-files (--maxkb=1000) would reject the commit.
        for src in a.promote_sources():
            dst = dest_dir / a.dest_name(src)
            rel_src = _rel(src, a.art_root)
            rel_dst = _rel(dst, a.art_root)
            if dry_run:
                print(f"DRY  {rel_src}  ->  {rel_dst}")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"COPY {rel_src}  ->  {rel_dst}")
            n_copied += 1
            n_bytes += src.stat().st_size
    verb = "would copy" if dry_run else "copied"
    print(
        f"\n{verb} {n_copied} file(s), {n_bytes / 1e6:.1f} MB into godot/assets; "
        f"skipped {n_skipped} asset(s); contested {n_contested} asset(s); "
        f"held {n_held} asset(s)."
    )
    if n_capped:
        print(
            f"size cap: {n_capped} asset(s) had their largest file over the 1MB git cap; "
            "the largest UNDER-cap size was chosen instead (masters stay in art_generated/, "
            "see docs/art/ART_MASTERS_POLICY.md)."
        )
    print(
        "NOTE: run a Godot --import pass to register the new files "
        "(e.g. `godot --headless --path godot --import`). This tool does not."
    )
    if n_skipped or n_contested:
        print(
            f"[FAIL] {n_skipped} keep(s) blocked, {n_contested} contested -- "
            "run `report` for the gate summary."
        )
        return 1
    return 0


def action_reroll(assets, prompt_index, art_root, dry_run):
    rerolls = [a for a in assets if a.verdict == "iterate"]
    print("== regenerate (iterate) manifest ==")
    if not rerolls:
        print("no iterate verdicts -- nothing to emit.")
        return 0
    manifest = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "note": "ITERATE assets + review notes, split by pipeline. These are "
        "on-brief but not final -- feed the note-refined prompts into the next "
        "generate_images.py run (gpt) or pixellab regen list to compare/hone. "
        "Discards are excluded (they are brief problems, see `report`).",
        "gpt": [],
        "pixellab": [],
    }
    unresolved = 0
    for a in rerolls:
        # reroll cares about the SOURCE, not the git cap: prefer the promote
        # pick but fall back to the best (possibly over-cap) file.
        src = a.promote_file or a.best_file
        entry = {
            "id": a.id,
            "category": a.category,
            "source_file": _rel(src, art_root) if src else "",
            "note": a.note,
            "original_prompt": "",
        }
        if a.error:
            entry["error"] = a.error
            unresolved += 1
        if a.kind == "gen":
            hit = prompt_index.get(a.base_id)
            if hit:
                entry["original_prompt"] = hit["prompt"]
                entry["source_manifest"] = hit["manifest"]
            manifest["gpt"].append(entry)
        elif a.kind == "px":
            manifest["pixellab"].append(entry)
        else:
            entry["error"] = a.error or "unparseable id"
            manifest.setdefault("unknown", []).append(entry)

    today = _dt.date.today().isoformat()
    out_path = art_root / MANIFEST_DIR / f"reroll_{today}.json"
    text = json.dumps(manifest, indent=2, ensure_ascii=True) + "\n"
    print(
        "gpt={} pixellab={} unknown={} unresolved-source={}".format(
            len(manifest["gpt"]),
            len(manifest["pixellab"]),
            len(manifest.get("unknown", [])),
            unresolved,
        )
    )
    if dry_run:
        print(f"DRY  would write {_rel(out_path, art_root)}:\n")
        print(text)
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"wrote {_rel(out_path, art_root)}")
    return 0


def _rel(path: Path, root: Path):
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return str(path)


# --- cli --------------------------------------------------------------------
def build_parser():
    p = argparse.ArgumentParser(
        prog="apply_review.py",
        description="Wire art-review verdicts into the P(Doom)1 asset pipeline "
        "(report / promote keeps / emit reroll manifest).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="asset_id scheme:\n"
        "  gen:<category>:<base_id>:<variant>  -> art_generated/<category>/v1/"
        "<base_id>_<variant>_<size>.png\n"
        "  px:<relpath>                        -> art_source/<relpath> (file, "
        "rotation dir, or extensionless PNG path)\n\n"
        "exit codes: nonzero from report/promote when any KEEP asset is blocked\n"
        "(unmapped category / unresolvable source / nothing under the 1MB cap).\n"
        "Explicit Hold (not-for-promotion) entries are reported but do not fail.\n\n"
        "examples:\n"
        "  python tools/art_review/apply_review.py report\n"
        "  python tools/art_review/apply_review.py promote --dry-run\n"
        "  python tools/art_review/apply_review.py reroll --dry-run\n"
        "  python tools/art_review/apply_review.py report "
        "--state /tmp/review_state.json --art-root .",
    )
    p.add_argument(
        "action",
        choices=["report", "promote", "reroll"],
        help="report: counts+list + promotion gate (fails if any keep is "
        "blocked); promote: copy keeps into godot/assets (over-1MB files never "
        "copied); reroll: emit reroll_<date>.json of ITERATE assets to "
        "regenerate (discards excluded).",
    )
    p.add_argument(
        "--art-root",
        default=".",
        help="repo root that holds art_generated/, art_source/, godot/, "
        "tools/ (default: current dir).",
    )
    p.add_argument(
        "--state",
        default=None,
        help=f"path to the review state file (default: <art-root>/{DEFAULT_STATE}).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would happen; write/copy nothing.",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    art_root = Path(args.art_root).expanduser()
    if not art_root.is_dir():
        sys.exit(f"error: --art-root {art_root} is not a directory")
    state_path = Path(args.state) if args.state else art_root / DEFAULT_STATE

    state = load_state(state_path)
    if state is None:
        print(f"no verdicts yet -- {state_path} does not exist.")
        return 0
    if not state:
        print(f"no verdicts yet -- {state_path} is empty.")
        return 0

    assets = parse_assets(state, art_root)
    if not assets:
        print("no verdicts yet -- state has no keep/iterate/discard entries.")
        return 0

    if args.action == "report":
        return action_report(assets)
    if args.action == "promote":
        return action_promote(assets, args.dry_run)
    if args.action == "reroll":
        prompt_index = build_prompt_index(art_root)
        return action_reroll(assets, prompt_index, art_root, args.dry_run)
    return 1


if __name__ == "__main__":
    sys.exit(main())

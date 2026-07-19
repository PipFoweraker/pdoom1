#!/usr/bin/env python3
"""apply_review.py -- wire art-review verdicts into the P(Doom)1 asset pipeline.

The review app writes a verdict-state file (default
``tools/art_review/review_state.json``) keyed by asset_id:

    gen:<category>:<base_id>:<variant>   generated art, file lives at
        <art-root>/art_generated/<category>/v1/<base_id>_<variant>_<size>.png
    px:<relpath>                         pixellab art, file/dir lives at
        <art-root>/art_source/<relpath>  (relpath may point at a single PNG or a
        rotation directory of PNGs)

Each value is ``{verdict, note, tags, updated_at}`` with verdict in
{keep, maybe, reroll} (the review app's tri-state).

Three actions, all supporting --dry-run and --art-root (default "."):

    report    Count + list keep/maybe/reroll verdicts.
    promote   Copy each KEEP asset's PNG (largest size for generated art) into
              the correct godot/assets/ destination, creating dirs as needed.
    reroll    Emit tools/assets/manifests/reroll_<YYYY-MM-DD>.json describing each
              REROLL asset (id, category, source_file, note, original_prompt),
              split by pipeline (gpt vs pixellab) to feed the next generation run.

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
# art the category is derived from the relpath (props/characters/tilesets/cats).
GEN_DEST = {
    "game_icons": "godot/assets/icons/generated",
    "ui_icons": "godot/assets/icons/generated",
    "hero_banners": "godot/assets/images/heroes",
    "screen_backgrounds": "godot/assets/images/backgrounds",
    "env_scenes": "godot/assets/images/scenes",
    "terminal_textures": "godot/assets/textures/generated",
    "env_textures": "godot/assets/textures/generated",
    "ui_frames": "godot/assets/ui/frames",
}
PX_DEST = {
    "props": "godot/assets/office_floor/props",
    "characters": "godot/assets/office_floor/characters",
    "tilesets": "godot/assets/office_floor/tiles",
    "cats": "godot/assets/cats/generated",
}
# pixellab category tokens we recognise inside a relpath, in priority order.
PX_CATEGORY_TOKENS = ["props", "characters", "tilesets", "cats"]

DEFAULT_STATE = "tools/art_review/review_state.json"
MANIFEST_DIR = "tools/assets/manifests"
VERDICTS = ("keep", "maybe", "reroll")


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
        self.promote_file = None  # Path chosen to promote (largest for gen)
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
        self.promote_file = _largest_by_size(matches)

    def _parse_px(self):
        self.relpath = self.id[len("px:") :]
        # relpath may be given relative to art_source/ (natural) or relative to
        # the art-root (includes the leading art_source/). Try both.
        candidates = [
            self.art_root / "art_source" / self.relpath,
            self.art_root / self.relpath,
        ]
        target = next((c for c in candidates if c.exists()), None)
        if target is None:
            self.error = f"no file/dir at {candidates[0]} (or {candidates[1]})"
            return
        if target.is_dir():
            self.sources = sorted(target.glob("*.png"))
            if not self.sources:
                self.error = f"directory {target} has no PNGs"
                return
        else:
            self.sources = [target]
        self.category = _px_category(self.relpath)
        # promote copies every source PNG for px (rotation sets stay together);
        # promote_file holds the first for single-file reporting convenience.
        self.promote_file = self.sources[0]

    # -- destination directory for a promote --
    def dest_dir(self):
        if self.kind == "gen":
            rel = GEN_DEST.get(self.category)
        elif self.kind == "px":
            rel = PX_DEST.get(self.category) if self.category else None
        else:
            rel = None
        return (self.art_root / rel) if rel else None

    def dest_name(self, src: Path):
        # generated: strip the _<variant> suffix for a clean game path
        # (matches promote_assets.py convention: art id vN -> base name).
        if self.kind == "gen":
            stem = src.stem  # e.g. icon_doom_v2_1024
            marker = f"_{self.variant}_"
            if marker in stem:
                stem = stem.replace(marker, "_", 1)
            return stem + src.suffix
        return src.name


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
    parts = Path(relpath).as_posix().split("/")
    for token in PX_CATEGORY_TOKENS:
        if token in parts:
            return token
    # loose fallback: any segment containing "cat" -> cats
    if any("cat" in seg for seg in parts):
        return "cats"
    return None


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
        verdict = (val.get("verdict") or "").strip().lower()
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
def action_report(assets):
    groups = {v: [] for v in VERDICTS}
    for a in assets:
        groups[a.verdict].append(a)
    print("== review verdict report ==")
    print(
        "counts: keep={} maybe={} reroll={} (total {})".format(
            len(groups["keep"]), len(groups["maybe"]), len(groups["reroll"]), len(assets)
        )
    )
    for v in VERDICTS:
        print(f"\n-- {v} ({len(groups[v])}) --")
        for a in groups[v]:
            loc = a.error if a.error else str(a.promote_file)
            flag = "  [UNRESOLVED]" if a.error else ""
            print(f"  {a.id}{flag}")
            print(f"      pipeline={a.pipeline} category={a.category} -> {loc}")
            if a.note:
                print(f"      note: {a.note}")
    return 0


def action_promote(assets, dry_run):
    keeps = [a for a in assets if a.verdict == "keep"]
    print("== promote KEEP assets ==")
    print("category -> destination map in use:")
    for k, v in sorted(GEN_DEST.items()):
        print(f"  gen  {k:<20} -> {v}")
    for k, v in sorted(PX_DEST.items()):
        print(f"  px   {k:<20} -> {v}")
    print()
    if not keeps:
        print("no keep verdicts -- nothing to promote.")
        return 0
    n_copied = n_skipped = 0
    for a in keeps:
        if a.error:
            print(f"SKIP {a.id}: {a.error}")
            n_skipped += 1
            continue
        dest_dir = a.dest_dir()
        if dest_dir is None:
            print(f"SKIP {a.id}: no destination for category {a.category!r}")
            n_skipped += 1
            continue
        # generated: one file (largest). pixellab: every source PNG.
        srcs = [a.promote_file] if a.kind == "gen" else a.sources
        for src in srcs:
            dst = dest_dir / a.dest_name(src)
            rel_src = _rel(src, a.art_root)
            rel_dst = _rel(dst, a.art_root)
            if dry_run:
                print(f"DRY  {rel_src}  ->  {rel_dst}")
            else:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"COPY {rel_src}  ->  {rel_dst}")
            n_copied += 1
    verb = "would copy" if dry_run else "copied"
    print(f"\n{verb} {n_copied} file(s); skipped {n_skipped} asset(s).")
    print(
        "NOTE: run a Godot --import pass to register the new files "
        "(e.g. `godot --headless --path godot --import`). This tool does not."
    )
    return 0


def action_reroll(assets, prompt_index, art_root, dry_run):
    rerolls = [a for a in assets if a.verdict == "reroll"]
    print("== reroll manifest ==")
    if not rerolls:
        print("no reroll verdicts -- nothing to emit.")
        return 0
    manifest = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "note": "Rejected assets + review notes, split by pipeline. Feed the "
        "note-refined prompts into the next generate_images.py run (gpt) "
        "or pixellab regen list.",
        "gpt": [],
        "pixellab": [],
    }
    unresolved = 0
    for a in rerolls:
        src = a.promote_file if a.promote_file else None
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
        "  px:<relpath>                        -> art_source/<relpath> (file or "
        "rotation dir)\n\n"
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
        help="report: counts+list; promote: copy keeps into godot/assets; "
        "reroll: emit reroll_<date>.json for rejects.",
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
        print("no verdicts yet -- state has no keep/maybe/reroll entries.")
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

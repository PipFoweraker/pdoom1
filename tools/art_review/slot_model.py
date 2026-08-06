#!/usr/bin/env python3
"""slot_model.py -- the ONE definition of "slot cluster" and "frame role".

Both the picker page (build_slot_picker.py) and the merge step
(apply_slot_picks.py) import this. That is deliberate and it is the same
anti-rot move `apply_review.dest_rule_for_id` already makes ("so the report
gate, the gallery preflight and the coverage tests share ONE mapping logic").
If the builder and the merger clustered independently, a pick recorded against
cluster X could land on cluster Y after a regeneration -- silently. Here they
cannot disagree, because there is only one function.

Nothing in this module writes anything. It reads review_state.json through
apply_review's own resolution, so the promotable set is byte-identical to what
the promotion gate reports.

Vocabulary (ADR-0019 / docs/design/ASSET_PAYLOAD_ANALYSIS_2026-08-06.md):
  Library  -- an asset with a `keep` verdict. The default, unlabeled state.
  chosen   -- a property of the (asset, SLOT) PAIRING, recorded as a manifest
              entry. NOT a verdict, NOT a flag on the asset. This module never
              reads or writes a verdict; picks live in the selection record.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_review  # noqa: E402

# --- pools are exempt from collapse ----------------------------------------
# ADR-0019 pt 3: these consumers read DIRECTORIES as variety pools
# (worker_variant_pool.gd, portrait_library.gd, office_cat.gd), so multiplicity
# there is demand, not redundancy. A pool has no single winner, so it has no
# slot to pick and never enters this tool.
POOL_DEST_PREFIXES = (
    "godot/assets/office_floor/",
    "godot/assets/cats/",
    "godot/assets/effects/doom_overlays",
    "godot/assets/portraits/",
)

# --- the 15 saving-3 frame roles -------------------------------------------
# 512px PICTURES of a 12px corner. These are UI SOURCE MATERIAL, not finished
# art; the decision shape is "keep the painted texture or replace it with
# geometry", which is a different question from "which variant wins a slot",
# so they get their own section and never appear as icon clusters.
FRAME_ROLE_STEMS = (
    "ui_frame_corner_tl",
    "ui_frame_corner_tr",
    "ui_frame_corner_bl",
    "ui_frame_corner_br",
    "ui_frame_top",
    "ui_frame_bottom",
    "ui_frame_left",
    "ui_frame_right",
    "doom_meter_frame",
    "frame_button",
    "frame_panel_plain",
    "frame_panel_ornate",
    "crt_frame_bezel_heavy",
    "crt_frame_curved_glass",
    "crt_frame_vignette_light",
)

FRAME_TREATMENTS = ("styleboxflat", "nineslice", "whole", "drop")

# --- draw sizes, measured from consumer code, not guessed -------------------
# Every entry cites the line that sets it. "which of these looks best at 512"
# is the wrong question when the game draws 70 logical px; the page renders at
# DRAW_PX (and at 2x, because project.godot sets
# window/stretch/mode="canvas_items" so a 4K canvas scales a 70-px tile to
# ~140 physical px).  native=True means the source is already at or below the
# size the game draws it, so there is nothing to shrink.
DRAW_RULES = {
    "godot/assets/icons/generated": (70, "action_bar_renderer.gd:227 custom_minimum_size 70x70"),
    "godot/assets/images/heroes": (408, "fanfare_popup.gd:107 custom_minimum_size Vector2(408, 0)"),
    "godot/assets/textures/generated": (0, "tiling texture -- drawn at native size"),
    "godot/assets/images/backgrounds": (0, "fills a 1920x1080 viewport; sources are <=1536 wide"),
    "godot/assets/images/scenes": (0, "fills a 1920x1080 viewport; sources are <=1536 wide"),
    "godot/assets/images/vignettes": (0, "full-screen overlay -- native"),
    "godot/assets/images/events": (0, "no consumer today (images/events/README.md)"),
}
DEFAULT_DRAW = (0, "no measured consumer; shown at native size")

_SIZE_TOK = re.compile(r"_(\d{2,4})$")
_VAR_TOK = re.compile(r"_v\d+")
_DATE_TOK = re.compile(r"_\d{8}$")


def role_stem(filename):
    """Collapse a promotable filename to its ROLE.

    Strips, in order: a trailing batch date (_20260719), a trailing size token
    (_512), every _vN variant marker, then a size token again (variant markers
    sit mid-stem, e.g. icon_doom_v2_1024).

    HONESTY NOTE, carried from the analysis: this heuristic is the weakest link
    in the whole measurement. It merges cross-batch assets that share a stem
    but differ in content, and it FAILS to merge same-role assets with
    unrelated names (grant_proposal vs apply_grant is a known near-duplicate
    pair it misses). It is a +/-15% estimate of the role count. The true slot
    list can only come from the demand manifest; this tool exists to produce
    the picks that manifest will pin. Treat a cluster as "these definitely
    compete", never as "nothing else competes".
    """
    stem = Path(filename).stem
    stem = _DATE_TOK.sub("", stem)
    stem = _SIZE_TOK.sub("", stem)
    stem = _VAR_TOK.sub("", stem)
    stem = _SIZE_TOK.sub("", stem)
    return stem


def variant_rank(filename):
    """Sort key: the variant number, then the size token, then the name.

    Used to order candidates inside a cluster so the batch shortcuts ("apply
    v3 across this group") line up, and so the 2026-08-03 highest-variant
    convention is the visually last card.
    """
    stem = Path(filename).stem
    vm = re.findall(r"_v(\d+)", stem)
    sm = _SIZE_TOK.search(stem)
    return (int(vm[-1]) if vm else 0, int(sm.group(1)) if sm else 0, stem)


def variant_label(filename):
    """'v3' / 'v1 (implicit)' -- v1 files carry no marker in this convention."""
    vm = re.findall(r"_v(\d+)", Path(filename).stem)
    return "v%s" % vm[-1] if vm else "v1*"


def is_pool(dest):
    return any(dest.startswith(p) for p in POOL_DEST_PREFIXES)


def draw_rule(dest):
    return DRAW_RULES.get(dest, DEFAULT_DRAW)


class Candidate:
    """One promotable FILE competing for a slot, plus its review provenance."""

    def __init__(self, asset, src, entry):
        self.asset_id = asset.id
        self.dest = asset.dest_rule()
        self.src = src
        self.rel = src.relative_to(REPO).as_posix()
        self.name = src.name
        self.bytes = src.stat().st_size
        self.note = (entry or {}).get("note") or ""
        self.tags = (entry or {}).get("tags") or []
        self.variant = variant_label(src.name)
        self.px = None  # (w, h), filled lazily by the builder if Pillow is up

    def key(self):
        return self.rel


class Cluster:
    """A contested slot: >1 Library candidate, one winner, the rest stay
    Library assets no manifest entry names (which is not a status to record --
    it is the ABSENCE of a record)."""

    def __init__(self, dest, stem, candidates):
        self.dest = dest
        self.stem = stem
        self.candidates = sorted(candidates, key=lambda c: variant_rank(c.name))
        self.draw_px, self.draw_why = draw_rule(dest)

    @property
    def slot_id(self):
        return "%s/%s" % (self.dest, self.stem)

    @property
    def bytes(self):
        return sum(c.bytes for c in self.candidates)

    def default_pick(self):
        """The 2026-08-03 contested-keeps convention: highest variant wins.
        A DEFAULT, not a decision -- the page shows it as a hint only and
        never writes it."""
        return self.candidates[-1].rel


class FrameRole:
    def __init__(self, stem, candidates):
        self.stem = stem
        self.candidates = sorted(candidates, key=lambda c: variant_rank(c.name))

    @property
    def role_id(self):
        return self.stem

    @property
    def bytes(self):
        return sum(c.bytes for c in self.candidates)


def build_model(repo=REPO, state_path=None):
    """Return (clusters, frame_roles, stats).

    clusters:    [Cluster]  -- contested slots only (>1 candidate). A slot with
                 exactly one candidate needs no taste; it is already resolved.
    frame_roles: [FrameRole] -- the 15 saving-3 roles.
    """
    sp = Path(state_path) if state_path else repo / apply_review.DEFAULT_STATE
    state = apply_review.load_state(sp)
    if state is None:
        sys.exit("error: no review state at %s" % sp)
    assets = apply_review.parse_assets(state, repo)
    keeps = [a for a in assets if a.verdict == "keep"]
    buckets, _n_blocked, _contested = apply_review._promotion_gate(keeps)
    promotable = buckets["promotable"]

    frames = {}
    roles = {}
    n_pool = 0
    n_prom_files = 0
    for a in promotable:
        dest = a.dest_rule()
        entry = state.get(a.id)
        for src in a.promote_sources():
            n_prom_files += 1
            cand = Candidate(a, src, entry)
            stem = role_stem(src.name)
            if stem in FRAME_ROLE_STEMS:
                frames.setdefault(stem, []).append(cand)
                continue
            if is_pool(dest):
                n_pool += 1
                continue
            roles.setdefault((dest, stem), []).append(cand)

    clusters = [Cluster(d, s, c) for (d, s), c in roles.items() if len(c) > 1]
    clusters.sort(key=lambda c: (-c.bytes, c.slot_id))
    frame_roles = [FrameRole(s, c) for s, c in frames.items()]
    frame_roles.sort(key=lambda f: FRAME_ROLE_STEMS.index(f.stem))

    slot_files = sum(len(v) for v in roles.values())
    stats = {
        "state_entries": len(state),
        "keeps": len(keeps),
        "promotable_assets": len(promotable),
        "promotable_files": n_prom_files,
        "promotable_bytes": sum(f.stat().st_size for a in promotable for f in a.promote_sources()),
        "pool_files_exempt": n_pool,
        "frame_roles": len(frame_roles),
        "frame_files": sum(len(v) for v in frames.values()),
        "frame_bytes": sum(c.bytes for v in frames.values() for c in v),
        "slot_files": slot_files,
        "slot_roles": len(roles),
        "alternates": slot_files - len(roles),
        "contested_clusters": len(clusters),
        "contested_files": sum(len(c.candidates) for c in clusters),
        "contested_bytes": sum(c.bytes for c in clusters),
    }
    return clusters, frame_roles, stats

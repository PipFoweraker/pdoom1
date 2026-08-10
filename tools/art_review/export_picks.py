#!/usr/bin/env python3
"""export_picks.py -- turn the gallery review state into a picks file the
art-night runner will actually accept.

Layer: BRIDGE (review -> generate)
Reads:  tools/art_review/review_state.json
Writes: a flat JSON list of gallery ids, which is one of the two shapes
        tools/assets/run_art_night.py::load_picks accepts verbatim.

WHY THIS EXISTS
---------------
`run_art_night.py --picks tools/art_review/review_state.json` aborted with
"[ABORT] L2 needs picks and none parsed", and the cause is two independent
mismatches, not one:

  1. SHAPE. load_picks' dict branch expects ``{id: [tag, tag]}`` -- a LIST of
     tag strings per id. review_state.json stores
     ``{id: {"verdict": ..., "tags": [], "note": ..., "updated_at": ...}}``.
     Iterating that value yields the FIELD NAMES ("verdict", "tags", "note",
     "updated_at"), none of which are in FAVOURABLE_TAGS, so every entry is
     silently non-favourable. Note the failure mode: not a crash, a shrug.

  2. VOCABULARY. Even with the shape fixed, load_picks' FAVOURABLE_TAGS set is
     {love, like, promote, favour, favor, hero, yes, keep}. The gallery's
     "iterate" verdict is not in it -- and "iterate" is precisely the verdict
     L2 is for ("this direction is right, vary it"). "keep" means "this image
     is good", which is an L3 signal, not an L2 one.

Rather than widen load_picks' tag vocabulary (which would change the runner's
contract for every wave and quietly make "keep" mean "vary this"), this script
emits the OTHER accepted shape: a flat list of ids. load_picks takes a list
as-is with no tag filtering at all, so the verdict policy lives here, in the
review layer, where it is readable and arguable.

Usage:
    python tools/art_review/export_picks.py --verdict iterate --batch an0807 \
        --out tools/art_review/picks_l2_an0807_iterate.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_STATE = REPO / "tools" / "art_review" / "review_state.json"
DEFAULT_SPEC = REPO / "tools" / "assets" / "manifests" / "art_night_2026-08-07.json"

# Mirrors run_art_night.py. Duplicated deliberately so this script can report
# what WOULD be dropped instead of handing the runner a list it will silently
# thin. If the runner's regexes change, this comment is the pointer.
CELL_RE = re.compile(r"^(s\d{2})_(r\d{2})_(p\d{2})")
FAMILY_CELL_RE = re.compile(r"^(s\d{2})_(f\d{2})")


def parse_cell(cand, families):
    tail = cand.split(":")[-2] if cand.startswith("gen:") else Path(cand).name
    m = CELL_RE.match(tail)
    if m:
        return m.groups()
    fm = FAMILY_CELL_RE.match(tail)
    if fm and fm.group(2) in families:
        fam = families[fm.group(2)]
        return (fm.group(1), fam["rendering"], fam["palette"])
    return None


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--spec", default=str(DEFAULT_SPEC))
    ap.add_argument(
        "--verdict",
        action="append",
        required=True,
        help="verdict to include; repeatable (iterate / keep / maybe / reroll)",
    )
    ap.add_argument(
        "--batch",
        default=None,
        help="substring an id must contain (e.g. an0807). Omit to take every batch.",
    )
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    families = {f["id"]: f for f in spec.get("families", [])}

    wanted = {v.lower() for v in args.verdict}
    selected = [
        k
        for k, rec in state.items()
        if isinstance(rec, dict)
        and str(rec.get("verdict", "")).lower() in wanted
        and (args.batch is None or args.batch in k)
    ]

    kept, dropped, seen = [], [], set()
    for cand in sorted(selected):
        cell = parse_cell(cand, families)
        if cell is None:
            dropped.append(cand)
            continue
        if cell in seen:
            dropped.append(cand + "  (duplicate cell " + "_".join(cell) + ")")
            continue
        seen.add(cell)
        kept.append(cand)

    Path(args.out).write_text(json.dumps(kept, indent=2) + "\n", encoding="utf-8")

    print(f"state       : {args.state}  ({len(state)} entries)")
    print(f"verdicts    : {sorted(wanted)}   batch filter: {args.batch}")
    print(f"selected    : {len(selected)}")
    print(f"written     : {len(kept)} unique (subject, rendering, palette) cells -> {args.out}")
    if dropped:
        print(f"dropped     : {len(dropped)} (reported, never silent)")
        for d in dropped:
            print(f"      {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

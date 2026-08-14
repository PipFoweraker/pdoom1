#!/usr/bin/env python3
"""notes_brief.py -- turn the reviewer's notes into the brief for the next round.

Layer: OBSERVE -> DECIDE
Invoked by: human, after merge_gallery_export.py

WHY THIS EXISTS
---------------
A note in review_state.json is a comment field: real, tracked, diffable, and
completely invisible unless someone greps for it. The 2026-08-06 taste
measurement found that the single most useful artifact in the whole art loop was
a note Pip typed ELEVEN DAYS EARLIER asking for a coherence pass -- it was right,
it was actionable, and it sat unread for eleven days because nothing ever read
notes back. Verdicts have four consumers (apply_review report/promote/reroll,
the gallery baseline, the taste measurement, the slot model). Notes had none.

So notes are promoted to an output. This script reads the ONE verdict store and
writes ONE generated markdown file, grouped so the next generation round can act
on it: what to keep doing, what to change, and what was thrown out and why.

ANTI-ROT (the DQ_INDEX pattern)
-------------------------------
docs/art/NOTES_BRIEF.md is GENERATED and carries a do-not-hand-edit header, the
same shape as docs/game-design/DQ_INDEX.md. `--check` fails if the tracked file
is stale, so it can gate pre-commit later without anyone having to remember.
This is deliberately NOT a third store: the note itself lives only in
review_state.json. This file is a VIEW, and a stale view is a build failure
rather than a slow lie -- which is the failure mode of the hand-maintained
decisions/README.md index.

Usage:
    python tools/art_review/notes_brief.py           # rewrite the brief
    python tools/art_review/notes_brief.py --check   # fail if stale
    python tools/art_review/notes_brief.py --stdout  # print, write nothing
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "tools" / "art_review" / "review_state.json"
OUT = REPO / "docs" / "art" / "NOTES_BRIEF.md"

VERDICT_MIGRATE = {"maybe": "remix", "reroll": "remix", "iterate": "remix"}
VERDICTS = ("keep", "remix", "shelf", "discard")
# Section order is the order the brief should be READ in: what to preserve
# first, what to fix second, what to stop doing last.
SECTIONS = [
    ("keep", "KEEP -- what is working, preserve it"),
    ("remix", "REMIX -- what to change in the next round"),
    ("shelf", "SHELF -- right but not now; each carries a return condition"),
    ("discard", "DISCARD -- what to stop generating"),
    ("", "UNJUDGED -- noted but no verdict yet"),
]

HEADER = """<!-- GENERATED FILE -- DO NOT HAND-EDIT.
Regenerate: python tools/art_review/notes_brief.py
Source of truth: tools/art_review/review_state.json (the note field).
Edit a note by re-reviewing the asset in art_generated/full_gallery.html and
merging the export with tools/art_review/merge_gallery_export.py -- editing this
file directly is lost work, because the next regeneration overwrites it. -->

# Art notes -- the brief for the next generation round

Every line below is something the reviewer typed while looking at a specific
picture. Notes are grouped by verdict, then by the batch the asset came from,
because "the value structure is muddy in the aubergine palette" is only
actionable if you can see it was said about eleven images in one block and not
once about anything else.

Read the ITERATE section first when writing the next prompt queue: those are
pictures judged worth having but not as generated.
"""


def migrate(v):
    v = (v or "").strip().lower()
    if v in VERDICTS:
        return v
    return VERDICT_MIGRATE.get(v, "")


def batch_of(asset_id):
    """Best-effort human batch name from an asset id, matching the gallery."""
    if asset_id.startswith("gen:"):
        return "art_generated/" + asset_id.split(":", 2)[1]
    if asset_id.startswith("px:"):
        rel = asset_id[3:]
        return "art_source/" + rel.split("/", 1)[0]
    if asset_id.startswith("file:"):
        rel = asset_id[5:]
        parts = rel.split("/")
        return "/".join(parts[:2]) if len(parts) > 1 else rel
    return "(unclassified)"


def collect(state):
    """{verdict: {batch: [(asset_id, note)]}} plus a flat count."""
    out = defaultdict(lambda: defaultdict(list))
    n = 0
    for aid, entry in sorted(state.items()):
        if not isinstance(entry, dict):
            continue
        note = (entry.get("note") or "").strip()
        if not note:
            continue
        n += 1
        out[migrate(entry.get("verdict"))][batch_of(aid)].append((aid, note))
    return out, n


# Words that carry a craft judgement. Counting them is a cheap way to surface
# "you have said `muddy` fourteen times" -- a theme the reviewer never wrote
# down as a theme, because each note was about one picture.
THEME_WORDS = re.compile(
    r"\b(mud+y|flat|noisy|busy|washed|blur+y|soft|dark|bright|contrast|value|"
    r"palette|colou?r|light|lighting|composition|texture|grain|detail|prop|"
    r"legib\w*|read\w*|coheren\w*|consisten\w*|silhouette|edge|crop|face|"
    r"people|person|figure|text|letter\w*|logo|sign\w*|emoji|border|"
    r"transparen\w*|tile|seam|aliasing|banding)\b",
    re.I,
)


def themes(state, top=18):
    c = Counter()
    for entry in state.values():
        if not isinstance(entry, dict):
            continue
        seen = set()
        for w in THEME_WORDS.findall(entry.get("note") or ""):
            w = w.lower()
            if w not in seen:  # count DOCUMENTS not occurrences
                seen.add(w)
                c[w] += 1
    return c.most_common(top)


def render(state):
    grouped, n_notes = collect(state)
    lines = [HEADER.rstrip(), ""]
    n_assets = len([k for k, v in state.items() if isinstance(v, dict)])
    lines.append(
        f"**{n_notes} notes** across {n_assets} judged assets "
        f"({(100.0 * n_notes / n_assets):.0f} percent of judgements carry a note)."
        if n_assets
        else "**0 notes.**"
    )
    lines.append("")

    th = themes(state)
    if th:
        lines.append("## Recurring words")
        lines.append("")
        lines.append(
            "How many separate notes mention each craft term. A term near the top "
            "is a standing instruction the next prompt should carry, not a "
            "one-off reaction."
        )
        lines.append("")
        lines.append("| term | notes mentioning it |")
        lines.append("| --- | --- |")
        for w, c in th:
            lines.append(f"| {w} | {c} |")
        lines.append("")

    for verdict, title in SECTIONS:
        by_batch = grouped.get(verdict)
        if not by_batch:
            continue
        total = sum(len(v) for v in by_batch.values())
        lines.append(f"## {title} ({total})")
        lines.append("")
        for batch in sorted(by_batch):
            items = by_batch[batch]
            lines.append(f"### {batch} ({len(items)})")
            lines.append("")
            for aid, note in items:
                flat = " ".join(note.split())
                lines.append(f"- `{aid}` -- {flat}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if the file is stale")
    ap.add_argument("--stdout", action="store_true", help="print, write nothing")
    args = ap.parse_args(argv)

    if not STATE.is_file():
        sys.exit(f"error: {STATE} not found")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        sys.exit(f"error: {STATE} is not an object")

    text = render(state)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    if args.check:
        if not OUT.is_file():
            print(f"[!] {OUT.relative_to(REPO)} does not exist -- run notes_brief.py")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(
                f"[!] {OUT.relative_to(REPO)} is STALE. "
                f"Run: python tools/art_review/notes_brief.py"
            )
            return 1
        print(f"[+] {OUT.relative_to(REPO)} is current")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    n_notes = sum(
        1 for e in state.values() if isinstance(e, dict) and (e.get("note") or "").strip()
    )
    print(f"[+] wrote {OUT} ({n_notes} notes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

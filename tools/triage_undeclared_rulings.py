#!/usr/bin/env python3
"""Sort the UNDECLARED prose-scan hits into real work, references, and noise.

Layer: OBSERVE

WHY
---
`scripts/generate_rulings.py` reports every line that READS like a ruling but
carries no `RULING:` declaration. That list is deliberately over-inclusive -- a
false positive costs one glance, a false negative loses a decision -- and it has
grown past 200 entries, which is the size at which a work list stops being read.

This splits it. The prose scan cannot tell a DECLARATION from a MENTION, and
almost all of the volume turns out to be mentions: a changelog citing a past
ruling, a doc explaining that something was ruled elsewhere, a tool's docstring
recording why it behaves as it does. Those need no action and should not sit in
a work list pretending to.

CATEGORIES
  noise      -- the regex matched something that is not about a ruling at all
                ("ruled out", "ruled the day", "flagged, not ruled")
  reference  -- cites a ruling made elsewhere, usually with its date. No action:
                the ruling exists, this is prose about it.
  mechanism  -- a tool docstring or code comment recording the ruling that
                governs THAT code. Ideal candidates for a RULING: line, because
                the mechanism is right there.
  candidate  -- reads like a decision with no visible home. Read these.

Nothing here is authoritative. It is a reading order, not a verdict.

Usage:
  python tools/triage_undeclared_rulings.py            # summary
  python tools/triage_undeclared_rulings.py --show candidate
  python tools/triage_undeclared_rulings.py --md report.md
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RULINGS = REPO / "docs" / "rulings" / "rulings.json"

# Ordered: first match wins, so the most specific patterns come first.
NOISE = [
    (r"\bruled? out\b", "'ruled out' -- an exclusion, not a ruling"),
    (r"\bnot ruled\b|\bunruled\b|\bnothing ruled\b", "explicitly says it is NOT ruled"),
    (r"\bruled the day\b|\bover-?ruled\b", "idiom"),
    (r"UNDECLARED|prose that reads like a ruling", "the scanner describing itself"),
]
REFERENCE = [
    (r"\(ruled\s+(on\s+)?\d{4}-\d{2}-\d{2}", "cites a dated ruling in parentheses"),
    (r"\bruled by \w+,?\s+\d{4}-\d{2}-\d{2}", "cites 'ruled by X, DATE'"),
    (r"\bruled\s+\d{4}-\d{2}-\d{2}", "cites a dated ruling inline"),
    (r"\bper (his|her|their|the) ruling\b|\bagainst .{0,20}rulings? of\b", "refers back"),
    (r"\balready ruled\b|\bwas ruled\b|\bhas ruled\b|\bhe ruled\b|\bshe ruled\b", "past tense"),
]
CODEISH = (".py", ".gd")


def classify(entry: dict) -> tuple[str, str]:
    text = entry["text"]
    src = entry["source"]
    for rx, why in NOISE:
        if re.search(rx, text, re.I):
            return "noise", why
    for rx, why in REFERENCE:
        if re.search(rx, text, re.I):
            path = src.rsplit(":", 1)[0]
            if path.endswith(CODEISH):
                return "mechanism", "cited in code that implements it"
            return "reference", why
    path = src.rsplit(":", 1)[0]
    if path.endswith(CODEISH):
        return "mechanism", "in code, no date cited"
    return "candidate", "reads like a decision with no visible home"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", help="print every entry in one category")
    ap.add_argument("--md", type=pathlib.Path, help="write a markdown report")
    args = ap.parse_args()

    if not RULINGS.exists():
        sys.exit("no rulings.json -- run scripts/generate_rulings.py first")
    doc = json.loads(RULINGS.read_text(encoding="utf-8"))
    undeclared = doc.get("undeclared", [])

    buckets: dict[str, list] = collections.defaultdict(list)
    for e in undeclared:
        cat, why = classify(e)
        buckets[cat].append((e, why))

    order = ["candidate", "mechanism", "reference", "noise"]
    total = len(undeclared)
    lines = [
        "# Undeclared ruling triage (GENERATED)",
        "",
        "> `tools/triage_undeclared_rulings.py`. A reading order, not a verdict.",
        f"> {total} prose-scan hits, {doc.get('count', 0)} declared rulings.",
        "",
        "| category | n | share | action |",
        "|---|---:|---:|---|",
    ]
    action = {
        "candidate": "**read these**",
        "mechanism": "cheap wins -- the mechanism is already there",
        "reference": "none -- the ruling exists elsewhere",
        "noise": "none -- false positive",
    }
    for cat in order:
        n = len(buckets[cat])
        lines.append(f"| {cat} | {n} | {n/total*100:.0f}% | {action[cat]} |")
    lines.append("")

    for cat in order:
        if cat == "noise":
            continue
        rows = buckets[cat]
        lines += [f"## {cat} -- {len(rows)}", ""]
        for e, why in rows[: 200 if cat == "candidate" else 60]:
            lines.append(f"- `{e['source']}`")
            lines.append(f"  - {e['text'][:150]}")
        lines.append("")

    md = "\n".join(lines) + "\n"
    if args.md:
        args.md.write_text(md, encoding="utf-8", newline="")
        print(f"wrote {args.md}")
    if args.show:
        for e, why in buckets.get(args.show, []):
            print(f"{e['source']}\n   {e['text'][:160]}\n   ({why})\n")
        return 0
    if not args.md:
        for cat in order:
            n = len(buckets[cat])
            print(f"  {cat:10} {n:4}  {n/total*100:3.0f}%   {action[cat]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

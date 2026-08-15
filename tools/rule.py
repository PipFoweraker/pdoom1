#!/usr/bin/env python3
"""Capture a ruling in one command, and show the precedent before you make it.

Layer: -- (see NOTE ON LAYER below)

WHY THIS EXISTS
---------------
Pip, 2026-08-15: a verbal ruling is worse than a script to capture it, "because
these will show up again in similar flavours".

The convention (`docs/rulings/RULINGS_CONVENTION.md`) lets a `RULING:` line be
written anywhere. Most belong next to the code they govern -- write those by
hand, in that file, where the next person to touch it will see them. This tool
is for the other kind: a ruling with no home yet. It appends to
`docs/rulings/LEDGER.md` and regenerates the index.

THE PART THAT MATTERS MORE THAN THE APPEND
------------------------------------------
A ruling log fails by becoming write-only. This repo has the proof: the
`element:<thing>` harvest vocabulary has existed for months and 2 of 7,944
assets carry a tag. A field nobody is ASKED about at the right moment does not
get filled in.

So this tool shows PRECEDENT before it writes. Rule on `art-lineage` and it
prints every prior `art-lineage` ruling first. That is the whole "similar
flavours" ask, and it is the reason to use this rather than opening the ledger
in an editor.

It also fuzzy-matches new flavour slugs against existing ones. A corpus split
across `art-lineage`, `art_lineage` and `artlineage` cannot be recalled by
flavour at all, and typos are the likeliest way that happens.

NOTE ON LAYER
-------------
The tools index taxonomy is GENERATE / PROVE / OBSERVE / SWEEP. This tool
CAPTURES: it writes a new source fact rather than deriving, asserting or
reporting on existing ones. Rather than force it into a layer it does not fit,
the declaration is left undeclared and the gap is recorded here. Whether
"capture" joins the taxonomy is itself a ruling, and not one to make by picking
a word in a docstring.

Usage
-----
    python tools/rule.py "the epoch counter starts at 1" --flavour art-lineage
    python tools/rule.py "masters are written verbatim" --flavour art-provenance \\
        --mechanism tools/assets/check_credentials.py
    python tools/rule.py "..." --flavour art-lineage --supersedes pdoom1:2026-08-01:1a2b3c4d

    python tools/rule.py --flavour art-lineage      # precedent only, writes nothing
    python tools/rule.py --flavours                 # list every known flavour
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "docs" / "rulings" / "LEDGER.md"
GENERATOR = REPO / "scripts" / "generate_rulings.py"

sys.path.insert(0, str(REPO / "scripts"))

import generate_rulings as gr  # noqa: E402

# ' -- ' separates fields in a declaration, so a ruling containing it would be
# silently truncated at parse time -- the text after the separator would be read
# as a field and dropped. Refuse rather than mangle.
FIELD_SEP = " -- "


def load_rulings() -> list[dict]:
    rulings, _undeclared, _errors = gr.collect()
    return rulings


def print_precedent(flavour: str, rulings: list[dict]) -> int:
    hits = [r for r in rulings if r["flavour"] == flavour]
    if not hits:
        return 0
    print(f"\n  PRECEDENT -- {len(hits)} prior ruling(s) in {flavour!r}:\n")
    for r in hits:
        mark = "  [SUPERSEDED]" if r["superseded_by"] else ""
        print(f"    {r['date']}{mark}  {r['ruling']}")
        print(f"        mechanism: {r['mechanism'] or '-- none --'}")
        print(f"        id:        {r['id']}")
        print(f"        source:    {r['source']}\n")
    return len(hits)


def check_flavour(flavour: str, rulings: list[dict]) -> None:
    """Warn when a flavour looks like a typo of an existing one."""
    known = sorted({r["flavour"] for r in rulings})
    if flavour in known:
        return
    normalised = {k.replace("-", "").replace("_", "").lower(): k for k in known}
    probe = flavour.replace("-", "").replace("_", "").lower()
    if probe in normalised:
        print(
            f"\n  [!] {flavour!r} differs from the existing {normalised[probe]!r} only by "
            f"punctuation or case.\n      A corpus split across both cannot be recalled by "
            f"flavour. Use the existing one unless the difference is intended."
        )
        return
    close = difflib.get_close_matches(flavour, known, n=3, cutoff=0.7)
    if close:
        print(f"\n  [!] {flavour!r} is new. Similar existing flavours: {', '.join(close)}")
    elif known:
        print(f"\n  [i] {flavour!r} is a new flavour. Existing: {', '.join(known)}")


def build_line(args, ruling: str) -> str:
    parts = [f"RULING: {args.date} -- {ruling}", f"flavour: {args.flavour}"]
    if args.mechanism:
        parts.append(f"mechanism: {args.mechanism}")
    if args.supersedes:
        parts.append(f"supersedes: {args.supersedes}")
    if args.by != "Pip":
        parts.append(f"by: {args.by}")
    return FIELD_SEP.join(parts)


def append_and_regenerate(line: str) -> int:
    if not LEDGER.exists():
        print(f"FATAL: {LEDGER.relative_to(REPO).as_posix()} does not exist.", file=sys.stderr)
        return 1
    text = LEDGER.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    # newline="" forces LF; the Windows default writes CRLF, which the
    # mixed-line-ending hook then rewrites mid-commit.
    LEDGER.write_text(text + line + "\n", encoding="utf-8", newline="")
    print(f"\n  appended to {LEDGER.relative_to(REPO).as_posix()}:\n    {line}\n")

    result = subprocess.run(
        [sys.executable, str(GENERATOR)], capture_output=True, text=True, cwd=str(REPO)
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        print("\n  [!] the index did not regenerate cleanly. The ruling IS recorded in the")
        print("      ledger; run `python scripts/generate_rulings.py` to see what it says.")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Capture a ruling, after showing what was already ruled in its flavour."
    )
    ap.add_argument("ruling", nargs="?", help="the ruling, one sentence")
    ap.add_argument("--flavour", help="slug grouping recurring questions of the same kind")
    ap.add_argument("--mechanism", help="the guard/gate/trigger that will RE-ASK this")
    ap.add_argument("--supersedes", help="id of the ruling this replaces")
    ap.add_argument("--by", default="Pip", help="who ruled (default: Pip)")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="YYYY-MM-DD")
    ap.add_argument("--flavours", action="store_true", help="list known flavours and exit")
    ap.add_argument("--dry-run", action="store_true", help="print the line; write nothing")
    args = ap.parse_args()

    rulings = load_rulings()

    if args.flavours:
        counts: dict[str, int] = {}
        for r in rulings:
            counts[r["flavour"]] = counts.get(r["flavour"], 0) + 1
        if not counts:
            print("no rulings recorded yet.")
            return 0
        print(f"{len(counts)} flavour(s):\n")
        for flavour, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  {n:3}  {flavour}")
        return 0

    if not args.flavour:
        ap.error("--flavour is required (it is how a ruling is recalled later)")

    # Precedent-only mode: no ruling text means "what did I already decide here?"
    if not args.ruling:
        n = print_precedent(args.flavour, rulings)
        if not n:
            print(f"no prior rulings in flavour {args.flavour!r}.")
            check_flavour(args.flavour, rulings)
        return 0

    ruling = args.ruling.strip()
    if FIELD_SEP in ruling:
        print(
            f"REFUSED: the ruling text contains {FIELD_SEP!r}, which separates fields in a\n"
            f"         declaration. Everything after it would be parsed as a field and lost.\n"
            f"         Reword without ' -- ' (a comma, semicolon or colon reads fine).",
            file=sys.stderr,
        )
        return 1
    try:
        dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"REFUSED: --date {args.date!r} is not YYYY-MM-DD.", file=sys.stderr)
        return 1
    if args.supersedes and not any(r["id"] == args.supersedes for r in rulings):
        print(
            f"REFUSED: --supersedes {args.supersedes!r} matches no known ruling id.\n"
            f"         Find it with: python tools/rule.py --flavour {args.flavour}",
            file=sys.stderr,
        )
        return 1

    # Precedent BEFORE the write, so it can still change your mind.
    print_precedent(args.flavour, rulings)
    check_flavour(args.flavour, rulings)

    line = build_line(args, ruling)
    if args.dry_run:
        print(f"\n  DRY RUN, nothing written:\n    {line}")
        return 0
    return append_and_regenerate(line)


if __name__ == "__main__":
    sys.exit(main())

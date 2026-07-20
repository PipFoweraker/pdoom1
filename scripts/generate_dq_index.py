"""Generate docs/game-design/DQ_INDEX.md from WORKSHOP_2_BACKLOG.md.

The backlog file is the single source of truth for design questions (DQs);
this script derives a compact status table from it so the index can never
rot the way a hand-maintained one would (see the stale decisions/README.md
for the failure mode this avoids).

Usage:
    python scripts/generate_dq_index.py          # (re)write the index
    python scripts/generate_dq_index.py --check  # exit 1 if index is stale

A DQ mention is any bold span starting with DQ-<n>, e.g.
    **DQ-12 . Rival narrative presence** ...
    **DQ-18 -- EXECUTED** ...
Status is the first status keyword found in the bold span; a DQ mentioned
several times takes its highest-precedence status. Anything without a
keyword is "open".
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "game-design" / "WORKSHOP_2_BACKLOG.md"
OUT = ROOT / "docs" / "game-design" / "DQ_INDEX.md"

# Highest precedence wins when a DQ is mentioned more than once.
STATUS_PRECEDENCE = {
    "RESOLVED": 3,
    "EXECUTED": 3,
    "SEEDED": 2,
    "PRIORITISED": 2,
    "PARKED": 1,
    "open": 0,
}

BOLD_DQ = re.compile(r"\*\*(DQ-\d+(?:\s+ext)?\b[^*]*)\*\*")

# Non-ASCII separators used in the backlog prose; the emitted index must be
# ASCII (enforce-standards hook).
ASCII_MAP = {
    "·": "-",
    "–": "--",
    "—": "--",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "≤": "<=",
    "≥": ">=",
}


def to_ascii(text: str) -> str:
    for src, dst in ASCII_MAP.items():
        text = text.replace(src, dst)
    return text.encode("ascii", "replace").decode("ascii")


def parse_mention(bold: str) -> tuple[str, str, str]:
    """Return (dq_id, title, status) from one bold DQ span."""
    text = to_ascii(bold).strip()
    m = re.match(r"(DQ-\d+(?:\s+ext)?)", text)
    dq_id = m.group(1)
    rest = text[m.end() :].strip(" -.:")
    status = "open"
    title = rest
    for keyword in STATUS_PRECEDENCE:
        if keyword != "open" and keyword in rest:
            status = keyword
            title = rest.split(keyword)[0]
            break
    title = title.strip(" -.:(")
    return dq_id, title, status


def collect() -> list[tuple[str, str, str, int]]:
    """Return [(dq_id, title, status, lineno)] deduped by precedence."""
    entries: dict[str, tuple[str, str, int]] = {}
    for lineno, line in enumerate(SRC.read_text(encoding="utf-8").splitlines(), 1):
        for match in BOLD_DQ.finditer(line):
            dq_id, title, status = parse_mention(match.group(1))
            prev = entries.get(dq_id)
            if prev is None or (STATUS_PRECEDENCE[status] > STATUS_PRECEDENCE[prev[1]]):
                # Keep the longest title seen so a bare status line like
                # "DQ-18 -- EXECUTED" does not erase the descriptive title.
                best_title = title
                if prev is not None and len(prev[0]) > len(title):
                    best_title = prev[0]
                entries[dq_id] = (best_title, status, lineno)

    def sort_key(dq_id: str) -> tuple[int, int]:
        num = int(re.search(r"\d+", dq_id).group(0))
        return (num, 1 if "ext" in dq_id else 0)

    return [(dq_id, *entries[dq_id]) for dq_id in sorted(entries, key=sort_key)]


def render() -> str:
    rows = collect()
    lines = [
        "# DQ index (GENERATED -- do not hand-edit)",
        "",
        "> Derived from `WORKSHOP_2_BACKLOG.md` (the single source of truth)",
        "> by `scripts/generate_dq_index.py`. Regenerate with:",
        "> `python scripts/generate_dq_index.py`. A pre-commit check fails",
        "> commits that change the backlog without regenerating this file.",
        "",
        "| DQ | Title | Status | Backlog line |",
        "|---|---|---|---|",
    ]
    for dq_id, title, status, lineno in rows:
        lines.append(f"| {dq_id} | {title} | {status} | {lineno} |")
    lines.append("")
    open_count = sum(1 for r in rows if r[2] == "open")
    lines.append(
        f"Total: {len(rows)} DQs -- {open_count} open, "
        f"{len(rows) - open_count} with a terminal or advanced status."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
            print("DQ_INDEX.md is stale. Run: python scripts/generate_dq_index.py")
            return 1
        return 0
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate godot/data/credits.json from CREDITS.md.

Layer: GENERATE

CREDITS.md (repo root) is the single source of truth for who gets credited.
It sits OUTSIDE godot/, so it is not bundled into the .pck; this script derives
a shipped, ASCII-only JSON copy that the in-game credits screen renders. Same
anti-rot pattern as generate_dq_index.py / generate_adr_index.py: a
hand-maintained second copy of the credits is exactly how decisions/README.md
went stale.

Usage:
    python scripts/generate_credits.py          # (re)write godot/data/credits.json
    python scripts/generate_credits.py --check  # exit 1 if the JSON is stale

Three rules decide what reaches a player's screen. They exist because a credits
screen that prints "[Pip to fill]" at a contributor is worse than one that omits
the line:

1. PLACEHOLDER DROP. Any bullet or paragraph still carrying a
   "[... to fill ...]" / "[... to confirm ...]" marker is omitted entirely.
   For a CAT row, only the credit line is dropped -- the cat itself still shows,
   because the photo shipped whether or not the credit form is confirmed.
2. MAINTAINER-NOTE SKIP. A bullet or paragraph containing a `backticked`
   identifier is prose aimed at maintainers (file paths, symbol names), not at
   players, and is not shipped. This is why the source file can carry parsing
   instructions next to the table without leaking them into the game.
3. NOTES-FOR-PIP CUTOFF. Everything from the "### Notes for Pip" heading down is
   a working checklist and never ships.

The cats table is the load-bearing part: `Asset` values are reconciled against
CAT_NAMES in godot/scripts/ui/office_cat.gd by
godot/tests/unit/test_credits_data.gd, so a cat added to one and not the other
fails the fast gate rather than silently going uncredited.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "CREDITS.md"
OUT = ROOT / "godot" / "data" / "credits.json"

CATS_SECTION = "Cats"
CUTOFF = re.compile(r"^###\s+Notes for Pip", re.IGNORECASE)
PLACEHOLDER = re.compile(r"\[[^\]]*\bto (?:fill|confirm)\b[^\]]*\]", re.IGNORECASE)
CODE_SPAN = re.compile(r"`[^`]+`")

# Written as escapes, not as literal characters: scripts/enforce_standards.py
# rejects any non-ASCII codepoint in a .py file, and a transliteration table is
# the one place where the source naturally wants to contain the very characters
# the gate forbids. (generate_dq_index.py carries the literal form and predates
# the incremental check, so it is never re-scanned -- do not copy it.)
ASCII_MAP = {
    "\u00b7": "-",  # middle dot
    "\u2013": "--",  # en dash
    "\u2014": "--",  # em dash
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
    "\u2264": "<=",
    "\u2265": ">=",
    "\u2026": "...",  # ellipsis
}


def to_ascii(text: str) -> str:
    for src, dst in ASCII_MAP.items():
        text = text.replace(src, dst)
    return text.encode("ascii", "replace").decode("ascii")


def plain(text: str) -> str:
    """Strip the markdown a Label cannot render, keeping the words."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)  # links -> text
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", text)  # italics
    return to_ascii(re.sub(r"\s+", " ", text).strip())


def has_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER.search(text))


def is_maintainer_note(text: str) -> bool:
    return bool(CODE_SPAN.search(text))


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    title = ""
    body: list[str] = []
    for line in lines:
        if CUTOFF.match(line):
            break
        if line.startswith("## "):
            if title:
                sections.append((title, body))
            title = to_ascii(line[3:].strip())
            body = []
        elif title:
            body.append(line)
    if title:
        sections.append((title, body))
    return sections


def parse_blocks(body: list[str]) -> list[dict]:
    """Group a section body into bullets and paragraphs, then filter."""
    blocks: list[tuple[str, list[str]]] = []
    for raw in body:
        line = raw.rstrip()
        stripped = line.strip()
        is_rule = bool(stripped) and set(stripped) <= set("-*_") and len(stripped) >= 3
        if not stripped or is_rule or stripped.startswith(">") or stripped.startswith("|"):
            blocks.append(("break", []))
            continue
        if stripped.startswith("- "):
            blocks.append(("item", [stripped[2:]]))
        elif line.startswith(" ") and blocks and blocks[-1][0] in ("item", "note"):
            blocks[-1][1].append(stripped)  # continuation of the previous block
        elif blocks and blocks[-1][0] == "note":
            blocks[-1][1].append(stripped)
        else:
            blocks.append(("note", [stripped]))

    entries: list[dict] = []
    for kind, parts in blocks:
        if kind == "break":
            continue
        text = " ".join(parts)
        if has_placeholder(text) or is_maintainer_note(text):
            continue
        rendered = plain(text)
        if rendered:
            entries.append({"kind": kind, "text": rendered})
    return entries


def parse_cats(body: list[str]) -> list[dict]:
    cats: list[dict] = []
    for raw in body:
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 3:
            continue
        name, credit, asset = cells
        if name.lower() == "cat" or set(name) <= set("-: "):
            continue  # header / separator row
        cats.append(
            {
                "name": plain(name),
                "credited_to": "" if has_placeholder(credit) else plain(credit),
                "asset": plain(asset),
            }
        )
    return cats


def build() -> dict:
    lines = SRC.read_text(encoding="utf-8").splitlines()
    sections: list[dict] = []
    cats: list[dict] = []
    for title, body in split_sections(lines):
        if title == CATS_SECTION:
            cats = parse_cats(body)
            entries = [e for e in parse_blocks(body) if e["kind"] == "note"]
        else:
            entries = parse_blocks(body)
        if entries:
            sections.append({"title": title, "entries": entries})
    return {
        "_generated": (
            "GENERATED from CREDITS.md by scripts/generate_credits.py -- "
            "do not hand-edit. Run the script; a pre-commit --check blocks staleness."
        ),
        "cats": cats,
        "sections": sections,
    }


def render() -> str:
    text = json.dumps(build(), indent=2, ensure_ascii=True) + "\n"
    non_ascii = [c for c in text if ord(c) > 127]
    if non_ascii:
        raise SystemExit(f"generate_credits: non-ASCII leaked into the output: {non_ascii[:5]}")
    return text


def main() -> int:
    content = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != content:
            print("godot/data/credits.json is stale. Run: python scripts/generate_credits.py")
            return 1
        return 0
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

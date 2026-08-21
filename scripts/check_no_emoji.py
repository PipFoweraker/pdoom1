#!/usr/bin/env python3
"""Blocking no-emoji / ASCII enforcement for the Godot tree (issue #744).

Layer: PROVE

Two rules, deliberately split (see CLAUDE.md "ASCII-only"):

  * godot/**/*.gd (excluding vendored addons/) and godot/data/**/*.json MUST be
    pure ASCII -- no codepoint above U+007F at all. These are source and
    player-facing data; the house style is ASCII-flavoured chrome ("[M]", ">>",
    "[ESC] close", "->", "--").
  * godot/**/*.tscn may contain engine-serialized unicode that must not be
    touched, so ONLY emoji (Unicode emoji blocks + variation selectors) are
    blocked there, not all non-ASCII.
  * EXCEPT (issue #1035): AUTHORED string properties in .tscn
    (text/tooltip_text/placeholder_text) are source, not engine serialization,
    and they are player-facing. Those lines MUST be pure ASCII, same as .gd.
    Real arrows / em-dashes / bullet glyphs accumulated in exactly this gap.

This hook is BLOCKING (exit 1 on any violation). It replaces the old
non-blocking, auto-fix-oriented Unicode handling in enforce_standards.py, which
let a coffee emoji ship.

Usage:
    python scripts/check_no_emoji.py          # scan the tree, exit 1 on violations
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GODOT = PROJECT_ROOT / "godot"

# --- .tscn exclusions ------------------------------------------------------
# None. The shared-Theme lane (issue #743, merged 2026-07-21) stripped the
# last emoji from the menu scenes, so the hook enforces every .tscn.
TSCN_EXCLUDE: set[str] = set()


def is_emoji(cp: int) -> bool:
    """True for codepoints in the Unicode emoji / pictographic-symbol blocks.

    Covers the source blocks Unicode draws emoji from (misc symbols, dingbats,
    supplemental symbols & pictographs, transport, etc.) plus variation
    selectors and regional indicators. Deliberately does NOT flag plain arrows
    (U+2190..U+21FF), geometric dots (U+25A0..U+25FF) or dashes -- those are
    handled as ASCII violations in .gd/.json but are left to #743 in .tscn.
    """
    return (
        0x1F000 <= cp <= 0x1FAFF  # emoji & pictographs (all planes-1 emoji)
        or 0x2600 <= cp <= 0x26FF  # misc symbols (weather, warning, gear, skull...)
        or 0x2700 <= cp <= 0x27BF  # dingbats (checks, crosses, stars, scissors...)
        or 0x2300 <= cp <= 0x23FF  # technical (play/pause/skip media glyphs)
        or 0x2B00 <= cp <= 0x2BFF  # misc symbols & arrows (star U+2B50...)
        or 0x1F1E6 <= cp <= 0x1F1FF  # regional indicators (flags)
        or 0xFE00 <= cp <= 0xFE0F  # variation selectors
        or cp in (0x2122, 0x2139, 0x24C2)  # (tm), info, (M)
    )


def _rel(p: Path) -> str:
    return p.relative_to(PROJECT_ROOT).as_posix()


def _iter(base: Path, suffix: str):
    for p in base.rglob("*" + suffix):
        yield p


def scan_ascii(base: Path, suffix: str, skip_addons: bool):
    """Yield (relpath, line, col, cp) for every codepoint > U+007F."""
    for p in _iter(base, suffix):
        rel = _rel(p)
        if skip_addons and "/addons/" in rel:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            for col, ch in enumerate(line, 1):
                if ord(ch) > 0x7F:
                    yield rel, ln, col, ord(ch)


def scan_emoji(base: Path, suffix: str, exclude: set):
    """Yield (relpath, line, col, cp) for every emoji codepoint."""
    for p in _iter(base, suffix):
        rel = _rel(p)
        if rel in exclude:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for ln, line in enumerate(text.splitlines(), 1):
            for col, ch in enumerate(line, 1):
                if is_emoji(ord(ch)):
                    yield rel, ln, col, ord(ch)


# Opening line of an authored .tscn string property we enforce ASCII on.
# Deliberately narrow: only these three properties are human-authored UI copy;
# everything else in a .tscn is treated as engine serialization and left alone.
TSCN_AUTHORED_RE = re.compile(r'^\s*(?:text|tooltip_text|placeholder_text)\s*=\s*"')


def _unescaped_quote_count(s: str) -> int:
    """Count unescaped double-quotes, so multiline authored strings can be
    tracked across lines (Godot serializes embedded quotes as \\")."""
    n = 0
    i = 0
    while i < len(s):
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == '"':
            n += 1
        i += 1
    return n


def scan_tscn_authored_ascii(base: Path, suffix: str, exclude: set):
    """Yield (relpath, line, col, cp) for non-ASCII inside AUTHORED .tscn string
    properties (text / tooltip_text / placeholder_text), issue #1035.

    The emoji-only rule for .tscn exists to protect engine-serialized unicode;
    authored UI strings are source and player-facing, so they get the full
    ASCII rule. Multiline strings (odd quote count on the opening line) are
    followed until the closing quote so wrapped prose is covered too.
    """
    for p in _iter(base, suffix):
        rel = _rel(p)
        if rel in exclude:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_string = False
        for ln, line in enumerate(text.splitlines(), 1):
            if not in_string:
                if not TSCN_AUTHORED_RE.match(line):
                    continue
                in_string = _unescaped_quote_count(line) % 2 == 1
            else:
                in_string = _unescaped_quote_count(line) % 2 == 0
            for col, ch in enumerate(line, 1):
                if ord(ch) > 0x7F:
                    yield rel, ln, col, ord(ch)


def scan_json_decoded_ascii(base: Path):
    r"""Yield (relpath, line, col, cp) for non-ASCII in a JSON file's DECODED values.

    WHY THIS EXISTS, AND WHY scan_ascii IS NOT ENOUGH
    -------------------------------------------------
    scan_ascii reads the file text and rejects any codepoint above U+007F. That
    is exactly right for .gd, where the source and the string are the same thing.
    It is blind on .json, because JSON escapes non-ASCII as \uXXXX -- six ASCII
    characters. A file can therefore be byte-for-byte pure ASCII while every
    string a player reads is not.

    Measured 2026-08-21 (#1163): godot/data/historical_events.json carried
    "UK AI Safety Institute \u00e2\u2020\u2019 AI Security Institute" and one
    sibling. Those three codepoints are U+00E2 U+2020 U+2019 -- the cp1252 misread
    of UTF-8 E2 86 92, i.e. a mangled U+2192 RIGHTWARDS ARROW. Two titles shipped
    to players as mojibake for weeks, and THIS SCRIPT PRINTED
    "OK: godot .gd/.json are pure ASCII" on every run, because at the byte level
    they were.

    The line/col reported is the line the offending escape appears on in the
    source file, found by searching for the literal escape, so the message points
    somewhere a human can edit. Where that fails the value path is reported at
    line 0, which is honest about not knowing rather than guessing a location.
    """
    for p in _iter(base, ".json"):
        rel = _rel(p)
        try:
            text = p.read_text(encoding="utf-8")
            doc = json.loads(text)
        except (UnicodeDecodeError, OSError, ValueError):
            # A JSON file that will not parse is a different guard's problem; this
            # one must not swallow it, but it also must not claim a finding it
            # cannot substantiate.
            continue

        lines = text.splitlines()

        def locate(ch):
            needle = "\\u%04x" % ord(ch)  # the 6-char escape, not the character
            for ln, line in enumerate(lines, 1):
                col = line.lower().find(needle.lower())
                if col >= 0:
                    return ln, col + 1
            return 0, 0

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(k)
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
            elif isinstance(node, str):
                for ch in node:
                    if ord(ch) > 0x7F:
                        ln, col = locate(ch)
                        yield_target.append((rel, ln, col, ord(ch)))

        yield_target = []
        walk(doc)
        for item in yield_target:
            yield item


def main() -> int:
    violations = []
    violations += list(scan_ascii(GODOT, ".gd", skip_addons=True))
    violations += list(scan_ascii(GODOT / "data", ".json", skip_addons=False))
    # The escaped half: pure-ASCII bytes can still decode to non-ASCII strings.
    violations += list(scan_json_decoded_ascii(GODOT / "data"))
    violations += list(scan_emoji(GODOT, ".tscn", TSCN_EXCLUDE))
    violations += list(scan_tscn_authored_ascii(GODOT, ".tscn", TSCN_EXCLUDE))

    if not violations:
        print(
            "[no-emoji] OK: godot .gd/.json are pure ASCII in bytes and in "
            "decoded JSON values; .tscn are emoji-free"
        )
        return 0

    print("[no-emoji] BLOCKING: non-ASCII / emoji found (issue #744):")
    for rel, ln, col, cp in violations:
        print("  %s:%d:%d  U+%04X" % (rel, ln, col, cp))
    print(
        "\n%d violation(s). Replace with ASCII: em-dash -> '--', arrows -> '->',\n"
        "ellipsis -> '...', bullets/dots -> '-'/'*', emoji -> remove or a [TAG].\n"
        "See CLAUDE.md 'ASCII-only' and docs/art/PALETTE_AND_DOOM_INTENSITY.md." % len(violations)
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

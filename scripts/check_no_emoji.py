#!/usr/bin/env python3
"""Blocking no-emoji / ASCII enforcement for the Godot tree (issue #744).

Two rules, deliberately split (see CLAUDE.md "ASCII-only"):

  * godot/**/*.gd (excluding vendored addons/) and godot/data/**/*.json MUST be
    pure ASCII -- no codepoint above U+007F at all. These are source and
    player-facing data; the house style is ASCII-flavoured chrome ("[M]", ">>",
    "[ESC] close", "->", "--").
  * godot/**/*.tscn may contain engine-serialized unicode that must not be
    touched, so ONLY emoji (Unicode emoji blocks + variation selectors) are
    blocked there, not all non-ASCII.

This hook is BLOCKING (exit 1 on any violation). It replaces the old
non-blocking, auto-fix-oriented Unicode handling in enforce_standards.py, which
let a coffee emoji ship.

Usage:
    python scripts/check_no_emoji.py          # scan the tree, exit 1 on violations
"""

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


def main() -> int:
    violations = []
    violations += list(scan_ascii(GODOT, ".gd", skip_addons=True))
    violations += list(scan_ascii(GODOT / "data", ".json", skip_addons=False))
    violations += list(scan_emoji(GODOT, ".tscn", TSCN_EXCLUDE))

    if not violations:
        print("[no-emoji] OK: godot .gd/.json are pure ASCII, .tscn are emoji-free")
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

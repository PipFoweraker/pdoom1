#!/usr/bin/env python3
"""check_scene_nav.py -- enforce the single-scene-navigation-chokepoint invariant.

WHY (v0.11.0 release-blocker, docs/LEADERBOARD_CRASH_DIAGNOSIS.md):
    Calling get_tree().change_scene_to_file() synchronously from inside an _input()/
    _gui_input() handler segfaulted the RELEASE build (0xc0000005, before the new scene's
    _ready) -- a full scene load+instantiate mid input-dispatch. The pattern was latent in
    ~5 screens; game-over just detonated first.

THE INVARIANT THIS ENFORCES:
    ALL scene navigation goes through the SceneTransition autoload
    (godot/autoload/scene_transition.gd), which ALWAYS defers the swap onto a clean idle
    frame. No other .gd may call change_scene_to_file / change_scene_to_packed /
    reload_current_scene directly. That makes the crash class structurally impossible
    instead of relying on every call site to remember to defer.

USAGE:
    python tools/check_scene_nav.py            # scan the whole godot/ tree (CI mode)
    python tools/check_scene_nav.py <files...> # check specific files (pre-commit passes these)

    Exit 0 = clean. Exit 1 = at least one direct navigation call outside the chokepoint.

ESCAPE HATCH (use sparingly, with justification):
    Append  # scene-nav-allow  to a line to exempt it (e.g. a genuinely one-off tool).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot"

# The ONE file allowed to call the raw engine navigation API.
SANCTIONED = (GODOT_ROOT / "autoload" / "scene_transition.gd").resolve()

BANNED = ("change_scene_to_file", "change_scene_to_packed", "reload_current_scene")
# Match an actual METHOD CALL (.name( ), not prose that merely names the method. This alone
# skips docstrings/comments like "do not call change_scene_to_file() directly" (no leading dot).
BANNED_RE = re.compile(r"\.(?:" + "|".join(BANNED) + r")\s*\(")

ALLOW_MARKER = "# scene-nav-allow"
TRIPLE_QUOTES = ('"""', "'''")


def _code_part(line: str) -> str:
    """Strip a trailing '#' comment so inline comments don't false-positive."""
    hashpos = line.find("#")
    return line if hashpos == -1 else line[:hashpos]


def scan_file(path: Path) -> list[tuple[int, str]]:
    if path.resolve() == SANCTIONED:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    hits: list[tuple[int, str]] = []
    in_docstring = (
        False  # inside a """...""" / '''...''' block (GDScript docstrings are string literals)
    )
    for i, raw in enumerate(text.splitlines(), start=1):
        # Toggle docstring state on each triple-quote delimiter (handles multi-line docstrings;
        # an even count on one line leaves state unchanged, e.g. a single-line """doc""").
        delims = sum(raw.count(q) for q in TRIPLE_QUOTES)
        was_in_docstring = in_docstring
        if delims % 2 == 1:
            in_docstring = not in_docstring
        if was_in_docstring or in_docstring and delims % 2 == 1:
            # Line is part of a docstring block -- prose, not code.
            continue
        if ALLOW_MARKER in raw:
            continue
        if BANNED_RE.search(_code_part(raw)):
            hits.append((i, raw.strip()))
    return hits


def iter_targets(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(a) for a in argv if a.endswith(".gd")]
    return sorted(GODOT_ROOT.rglob("*.gd"))


def main(argv: list[str]) -> int:
    violations: list[tuple[Path, int, str]] = []
    for path in iter_targets(argv):
        if not path.exists():
            continue
        for lineno, snippet in scan_file(path):
            violations.append((path, lineno, snippet))

    if not violations:
        return 0

    print("ERROR: direct scene-navigation calls found outside SceneTransition.")
    print("       Route them through SceneTransition.go_to(path) / .reload() instead.")
    print("       (SceneTransition always defers the swap -- see")
    print("        godot/autoload/scene_transition.gd and docs/LEADERBOARD_CRASH_DIAGNOSIS.md)")
    print()
    for path, lineno, snippet in violations:
        try:
            rel = path.resolve().relative_to(REPO_ROOT)
        except ValueError:
            rel = path
        print(f"  {rel}:{lineno}: {snippet}")
    print()
    print(
        f"{len(violations)} violation(s). Fix, or annotate a genuine exception with '{ALLOW_MARKER}'."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

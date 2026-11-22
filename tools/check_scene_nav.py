#!/usr/bin/env python3
"""check_scene_nav.py -- enforce the single-scene-navigation-chokepoint invariant.

Layer: PROVE

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
    python tools/check_scene_nav.py --self-test  # prove the scanner can still return BOTH answers

    Exit 0 = clean. Exit 1 = at least one direct navigation call outside the chokepoint.

WHY --self-test EXISTS (added 2026-08-24, issue #1265):
    This gate has been blocking in pre-commit AND in quality-checks.yml since the v0.11.0
    crash, and in that whole time it has only ever printed nothing and exited 0. A gate
    that has never gone red is indistinguishable from `def main(): return 0`. The
    self-test asserts BOTH answers, and one of its cases is drawn from real code rather
    than a fixture: godot/autoload/scene_transition.gd genuinely calls
    change_scene_to_file() and reload_current_scene(), so the SANCTIONED exemption is
    load-bearing -- scan_text() must flag those exact lines while scan_file() must not.
    If someone widens the exemption to a directory, that case goes red.

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


def scan_text(text: str) -> list[tuple[int, str]]:
    """Return [(lineno, stripped_line)] for every banned CALL in `text`.

    Split out from scan_file() so --self-test can exercise the decision without
    writing files, and so the SANCTIONED exemption stays visibly separate from the
    detection: scan_text says "is this a direct navigation call", scan_file says
    "and is this file allowed to make one".
    """
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


def scan_file(path: Path) -> list[tuple[int, str]]:
    if path.resolve() == SANCTIONED:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return scan_text(text)


# --- self-test fixtures ----------------------------------------------------
# Every form the scanner must NOT flag. Each line is a shape that has actually
# appeared in this tree.
SELF_TEST_CLEAN = '''extends Node

## Do not call get_tree().change_scene_to_file() directly -- prose in a comment.
func _on_pressed() -> void:
\tSceneTransition.go_to("res://scenes/menu.tscn")
\tSceneTransition.reload()  # not get_tree().reload_current_scene()

func _legacy() -> void:
\tget_tree().change_scene_to_file("res://scenes/x.tscn")  # scene-nav-allow

var doc = """
\tget_tree().change_scene_to_packed(packed)
"""
'''

# Every form the scanner MUST flag -- the v0.11.0 crash shape and its two siblings.
SELF_TEST_DIRTY = """extends Control

func _gui_input(event: InputEvent) -> void:
\tget_tree().change_scene_to_file("res://scenes/leaderboard.tscn")

func _b() -> void:
\tget_tree().change_scene_to_packed(_packed)

func _c() -> void:
\tget_tree().reload_current_scene()
"""


def self_test() -> int:
    """Prove the checker can return BOTH answers (CLAUDE.md: a published command must be
    shown capable of returning the other answer)."""
    ok = True

    clean = scan_text(SELF_TEST_CLEAN)
    if clean:
        ok = False
        print("SELF-TEST FAIL: clean navigation forms were flagged: %r" % (clean,))
    else:
        print("  [ok] the five clean forms pass")
        print("       (SceneTransition call / prose in a ## comment / inline comment /")
        print("        an annotated %s exception / a triple-quoted block)" % ALLOW_MARKER)

    dirty = scan_text(SELF_TEST_DIRTY)
    found = {name for _, line in dirty for name in BANNED if name in line}
    if len(dirty) != 3 or found != set(BANNED):
        ok = False
        print(
            "SELF-TEST FAIL: expected all 3 banned calls, got %d %r" % (len(dirty), sorted(found))
        )
    else:
        print("  [ok] all three banned calls are caught, including the v0.11.0 shape")
        print("       (change_scene_to_file from inside _gui_input -- 0xc0000005)")

    # Real history, not a fixture: the sanctioned file DOES make these calls. The
    # exemption is therefore load-bearing, and both halves of it must hold.
    if not SANCTIONED.is_file():
        ok = False
        print("SELF-TEST FAIL: sanctioned file missing: %s" % SANCTIONED)
    else:
        raw = SANCTIONED.read_text(encoding="utf-8", errors="replace")
        in_sanctioned = scan_text(raw)
        if not in_sanctioned:
            ok = False
            print(
                "SELF-TEST FAIL: scene_transition.gd no longer contains a raw navigation\n"
                "                call, so the SANCTIONED exemption proves nothing. Either the\n"
                "                chokepoint moved, or the detector stopped detecting."
            )
        elif scan_file(SANCTIONED) != []:
            ok = False
            print("SELF-TEST FAIL: the sanctioned chokepoint was itself reported")
        else:
            print(
                "  [ok] the chokepoint makes %d raw call(s) that scan_text flags and"
                % len(in_sanctioned)
            )
            print("       scan_file exempts -- the exemption is load-bearing, not decorative")

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def iter_targets(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(a) for a in argv if a.endswith(".gd")]
    return sorted(GODOT_ROOT.rglob("*.gd"))


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

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

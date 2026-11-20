#!/usr/bin/env python3
"""check_pause_timers.py -- every SceneTree.create_timer() must state its pause intent.

Layer: PROVE

WHY (#1341, #1343; docs/design/PAUSE_SEMANTICS.md):
    SceneTree.create_timer(time_sec, process_always = true, ...) DEFAULTS
    process_always to TRUE, i.e. the timer IGNORES SceneTree.paused. That default is
    how the month-playback loop ticked six days and a month boundary straight through
    the pause menu on the shipped v0.14.4 build (#1341). Nobody chose it; the engine did.

THE INVARIANT THIS ENFORCES:
    Every create_timer( call under godot/ (addons and tests excepted) passes the second
    argument explicitly -- `false` (stops while paused; the house default) or `true`
    (keeps running while paused; say why in a comment beside it). The guard does not
    judge WHICH answer is right; it makes the author give one.

    Tweens and Timer nodes are NOT checked: both inherit their node's process_mode,
    which is pausable by default -- the safe direction. create_timer is the one surface
    whose default points the other way.

USAGE:
    python tools/check_pause_timers.py              # scan the whole godot/ tree (CI mode)
    python tools/check_pause_timers.py <files...>   # check specific files (pre-commit)
    python tools/check_pause_timers.py --self-test  # prove it can return BOTH answers

    Exit 0 = clean. Exit 1 = at least one create_timer( with no explicit pause intent.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GODOT_ROOT = REPO_ROOT / "godot"
EXCLUDED_DIRS = ("addons", "tests")

CALL_RE = re.compile(r"\bcreate_timer\s*\(")


def strip_comments_and_strings(text: str) -> str:
    """Blank out comments and string literals, preserving offsets and newlines.

    So prose that mentions create_timer( -- a ## doc comment, a docstring, a log
    message -- is never mistaken for a call, and a ',' inside a string argument is
    never counted as an argument separator.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "#":
            while i < n and text[i] != "\n":
                out[i] = " "
                i += 1
            continue
        if c in "\"'":
            quote = c * 3 if text.startswith(c * 3, i) else c
            start = i
            i += len(quote)
            while i < n and not text.startswith(quote, i):
                if text[i] == "\\":
                    i += 1
                elif text[i] == "\n" and len(quote) == 1:
                    break  # unterminated single-line string; stop at end of line
                i += 1
            i = min(n, i + len(quote))
            for j in range(start, i):
                if text[j] != "\n":
                    out[j] = " "
            continue
        i += 1
    return "".join(out)


def _top_level_arg_count(code: str, open_paren: int) -> int | None:
    """Arguments of the call whose '(' is at open_paren. None if it never closes."""
    depth = 0
    commas = 0
    saw_token = False
    for k in range(open_paren, len(code)):
        ch = code[k]
        if ch in "([{":
            depth += 1
            if depth > 1:
                saw_token = True
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return commas + 1 if saw_token else 0
        elif depth == 1 and ch == ",":
            commas += 1
        elif depth >= 1 and not ch.isspace():
            saw_token = True
    return None


def scan_text(text: str) -> list[tuple[int, str]]:
    """Return [(lineno, source_line)] for each create_timer( without a 2nd argument."""
    code = strip_comments_and_strings(text)
    lines = text.splitlines()
    hits: list[tuple[int, str]] = []
    for m in CALL_RE.finditer(code):
        nargs = _top_level_arg_count(code, m.end() - 1)
        if nargs is not None and nargs >= 2:
            continue
        lineno = code.count("\n", 0, m.start()) + 1
        hits.append((lineno, lines[lineno - 1].strip() if lineno <= len(lines) else ""))
    return hits


def _in_scope(path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(GODOT_ROOT.resolve())
    except ValueError:
        return False
    return path.suffix == ".gd" and rel.parts[0] not in EXCLUDED_DIRS


def scan_file(path: Path) -> list[tuple[int, str]]:
    if not _in_scope(path):
        return []
    try:
        return scan_text(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return []


# --- self-test fixtures ----------------------------------------------------
SELF_TEST_CLEAN = '''extends Node

## Prose: the engine default of create_timer(t) ignores the pause.
func a() -> void:
\tawait get_tree().create_timer(0.5, false).timeout
\tvar t := get_tree().create_timer(4.0, true)  # keeps running: dev harness
\tawait get_tree().create_timer(
\t\tfoo(1, 2),
\t\tfalse
\t).timeout
\tprint("create_timer(1) in a log line is not a call")
\tvar doc = """
\tget_tree().create_timer(3.0)
\t"""
'''

# The #1341 shape and its siblings: one argument, a nested call that hides a comma,
# a multi-line call, and a comma that lives only inside a string.
SELF_TEST_DIRTY = """extends Node

func a() -> void:
\tawait get_tree().create_timer(day_tick_seconds).timeout
\tawait get_tree().create_timer(max(0.1, x)).timeout
\tawait get_tree().create_timer(
\t\t0.3
\t).timeout
\tawait get_tree().create_timer(lookup("a,b")).timeout
"""


def self_test() -> int:
    """Prove the checker can return BOTH answers."""
    ok = True
    clean = scan_text(SELF_TEST_CLEAN)
    if clean:
        ok = False
        print("SELF-TEST FAIL: explicit / prose forms were flagged: %r" % (clean,))
    else:
        print("  [ok] explicit false/true, multi-line explicit, prose, log string, docstring: pass")

    dirty = scan_text(SELF_TEST_DIRTY)
    if len(dirty) != 4:
        ok = False
        print("SELF-TEST FAIL: expected 4 bare create_timer calls flagged, got %r" % (dirty,))
    else:
        print("  [ok] the four implicit-default forms are all flagged")

    # Real code, not a fixture: game_manager.gd is the #1341 site. It must pass, and it
    # also MENTIONS create_timer( in a comment -- so a scanner that stopped stripping
    # comments would go red here.
    gm = GODOT_ROOT / "scripts" / "game_manager.gd"
    if gm.exists():
        gm_hits = scan_file(gm)
        if gm_hits:
            ok = False
            print("SELF-TEST FAIL: game_manager.gd (the fixed #1341 site) flagged: %r" % gm_hits)
        else:
            print("  [ok] game_manager.gd (the fixed #1341 site) passes")
        stripped = gm.read_text(encoding="utf-8").replace(", false).timeout", ").timeout")
        if len(scan_text(stripped)) < 2:
            ok = False
            print("SELF-TEST FAIL: reverting the #1341 fix in memory was NOT detected")
        else:
            print("  [ok] reverting the #1341 fix in memory is detected")

    print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    if argv:
        files = [Path(a) for a in argv]
    else:
        files = sorted(GODOT_ROOT.rglob("*.gd"))
    bad = 0
    for f in files:
        for lineno, line in scan_file(f):
            bad += 1
            try:
                shown = f.resolve().relative_to(REPO_ROOT)
            except ValueError:
                shown = f
            print(
                "%s:%d: create_timer() with no explicit process_always: %s" % (shown, lineno, line)
            )
    if bad:
        print(
            "\n%d create_timer call(s) rely on the engine default process_always=TRUE, which"
            " IGNORES the pause menu (#1341). Pass the second argument explicitly: false to"
            " stop while paused (house default), or true with a comment saying why it must"
            " keep running. See docs/design/PAUSE_SEMANTICS.md." % bad
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

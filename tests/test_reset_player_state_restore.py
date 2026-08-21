#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Forced-state tests for tools/reset_player_state.py restore().

WHY THIS EXISTS
---------------
Until 2026-08-21 `restore()` skipped any destination that already existed and
then printed "[OK] Restore complete." and returned 0 regardless. `leaderboards/`
exists as soon as the game has run once, so a bare `--restore` skipped the entire
directory and reported success.

This is the disaster-recovery tool for the incident that destroyed a 50-entry
league board on 2026-07-31. It could not perform the one restore it exists for,
while telling the operator that it had. A recovery tool that cannot distinguish
"restored everything" from "restored nothing" converts a recoverable loss into a
believed-recovered loss, which is strictly worse than having no tool.

The estate's rule: a claimed safety property needs a FORCED failure, because a
guard seen only in its passing state has not been shown to work. Case 1 below IS
the 2026-07-31 shape, constructed rather than waited for.

Everything runs in a temp directory. No real user data is read or written.

Run:  python tests/test_reset_player_state_restore.py     (exit 0 = pass)
"""

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "reset_player_state", ROOT / "tools" / "reset_player_state.py"
)
rps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rps)

failures = []


def check(cond, msg):
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        failures.append(msg)


def make_root(tmp, live_names, backup_names):
    """A user-data dir with a backup, and optionally live copies in the way."""
    root = Path(tmp)
    backup = root / (rps.BACKUP_PREFIX + "20260731_160443")
    backup.mkdir(parents=True)
    for n in backup_names:
        d = backup / n
        d.mkdir()
        (d / "board.json").write_text('{"entries": 50}', encoding="utf-8")
    for n in live_names:
        d = root / n
        d.mkdir()
        (d / "board.json").write_text('{"entries": 0}', encoding="utf-8")
    return root


def run_restore(root, overwrite=False):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = rps.restore(root, overwrite=overwrite)
    return code, buf.getvalue()


print("reset_player_state.restore() -- forced states")
print("=" * 74)

# --- 1. THE 2026-07-31 SHAPE ------------------------------------------------
print("\n1. EVERYTHING SKIPPED -- the state that used to print [OK]")
with tempfile.TemporaryDirectory() as tmp:
    root = make_root(tmp, live_names=["leaderboards"], backup_names=["leaderboards"])
    code, out = run_restore(root)
    check(code != 0, "returns NON-ZERO when nothing was restored (was 0)")
    check("[FAILED]" in out, "says [FAILED] rather than [OK]")
    check("[OK] Restore complete" not in out, "does NOT print the success line")
    check("NOTHING WAS RESTORED" in out, "names the outcome in words, not just an exit code")
    check(
        (root / "leaderboards" / "board.json").read_text(encoding="utf-8") == '{"entries": 0}',
        "and it did NOT silently overwrite -- the live copy is untouched",
    )

# --- 2. the recovery path actually recovers ---------------------------------
print("\n2. --overwrite -- a real recovery, destroying nothing")
with tempfile.TemporaryDirectory() as tmp:
    root = make_root(tmp, live_names=["leaderboards"], backup_names=["leaderboards"])
    code, out = run_restore(root, overwrite=True)
    check(code == 0, "returns 0 when the restore genuinely happened")
    check(
        (root / "leaderboards" / "board.json").read_text(encoding="utf-8") == '{"entries": 50}',
        "the 50-entry board is back",
    )
    aside = [p for p in root.iterdir() if ".superseded-" in p.name]
    check(len(aside) == 1, "the live copy was moved aside, not deleted (%d found)" % len(aside))
    check(
        (aside[0] / "board.json").read_text(encoding="utf-8") == '{"entries": 0}',
        "and the superseded copy still holds what was there 30 seconds ago",
    )

# --- 3. partial is not success ----------------------------------------------
print("\n3. PARTIAL -- one restored, one blocked, must not read as success")
with tempfile.TemporaryDirectory() as tmp:
    root = make_root(tmp, live_names=["leaderboards"], backup_names=["leaderboards", "settings"])
    code, out = run_restore(root)
    check(code != 0, "returns NON-ZERO on a partial restore")
    check("[PARTIAL]" in out, "says [PARTIAL] and names what was left alone")
    check((root / "settings").is_dir(), "the item that COULD be restored was restored")

# --- 4. the clean case still works ------------------------------------------
print("\n4. CLEAN -- nothing in the way, must still succeed")
with tempfile.TemporaryDirectory() as tmp:
    root = make_root(tmp, live_names=[], backup_names=["leaderboards", "settings"])
    code, out = run_restore(root)
    check(code == 0, "returns 0")
    check("[OK] Restore complete" in out, "prints the success line")
    check((root / "leaderboards").is_dir() and (root / "settings").is_dir(), "both items are back")

print()
if failures:
    print("FAILED:")
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("OK: restore() cannot report success without restoring, --overwrite recovers")
print("    without destroying, and a partial restore is not a success.")

#!/usr/bin/env python3
"""Reset this machine's P(Doom) player state to a genuine first-launch experience.

WHY THIS EXISTS (2026-07-31, league day). Pip's local config had carried
`scenario_id="crisis"` and `difficulty=2` for an unknown length of time. Two things
followed, and neither announced itself:

  1. A recorded "playtest of the league build" was actually a playtest of Crisis Mode
     (doom starting at 65, year 2020). It validated a configuration no league player
     would run.
  2. Four endgame tests went red on this machine and green in CI, because the GameConfig
     autoload reads the real user config and the tests never pinned what they needed.

Dev state leaking into what is supposed to be a fresh-player observation is the same
silent-wrongness family as everything else in issue #1027: it looked right.

USE IT before any recorded playtest, any pre-release ceremony run, and any "does a new
player understand this screen" check -- i.e. every time the loop comes round again.

    python tools/reset_player_state.py            # show what WOULD be cleared
    python tools/reset_player_state.py --apply    # back up, then clear
    python tools/reset_player_state.py --apply --keep-identity
    python tools/reset_player_state.py --restore  # undo the most recent --apply

DRY RUN BY DEFAULT, matching intelligent_ascii_converter.py's posture after #773 --
a destructive tool that fires on a bare invocation is a trap.

NOTHING IS DELETED. --apply moves the whole user-data directory into a timestamped
backup beside it, so any run can be recovered with --restore or by hand.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

APP_NAME = "P(Doom)"
BACKUP_PREFIX = "_backup_"

# What a first-launch player has. Anything not listed here is state THEY would not have.
FIRST_LAUNCH_KEEPS: tuple[str, ...] = ()

# Cleared unless --keep-identity. These are the ones that change what the GAME does,
# as opposed to merely what it remembers.
BEHAVIOUR_BEARING = {
    "config.cfg": "scenario_id / difficulty / seed / onboarding flags -- the 2026-07-31 trap",
    "leaderboards": "local board files; stale entries make a fresh board look populated",
    "saves": "a resumable save changes the first thing the player sees",
    "achievements.json": "unlock state",
    "install_id.txt": "install identity for the launch ping",
    "keybinds.cfg": "rebinds a new player would not have",
    "theme.cfg": "theme selection",
    "flight_recorder": "prior session recordings",
    "bug_reports": "prior reports + screenshots",
    "ui_evolution": "UI telemetry",
    "screenshots": "prior screenshots",
    "scenarios": "user-installed scenario packs",
    "shader_cache": "regenerated on launch; cleared so first-launch timing is honest",
    "vulkan": "driver pipeline cache; same reason as shader_cache",
    "logs": "prior logs",
}

IDENTITY_FILES = {"config.cfg", "install_id.txt"}


def user_data_root() -> Path:
    """Godot's user:// on this platform, for this app."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if not base:
            raise SystemExit("APPDATA is not set -- cannot locate Godot user data.")
        return Path(base) / "Godot" / "app_userdata" / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Godot" / "app_userdata" / APP_NAME
    return Path.home() / ".local" / "share" / "godot" / "app_userdata" / APP_NAME


def entries_to_clear(root: Path, keep_identity: bool) -> list[Path]:
    out = []
    for child in sorted(root.iterdir()):
        if child.name.startswith(BACKUP_PREFIX):
            continue  # never recurse into our own backups
        if child.name in FIRST_LAUNCH_KEEPS:
            continue
        if keep_identity and child.name in IDENTITY_FILES:
            continue
        out.append(child)
    return out


def describe(root: Path, keep_identity: bool) -> int:
    if not root.exists():
        print("[OK] No user data at %s -- already a first launch." % root)
        return 0
    targets = entries_to_clear(root, keep_identity)
    if not targets:
        print("[OK] Nothing to clear at %s" % root)
        return 0
    print("Godot user data: %s" % root)
    print("")
    print("WOULD CLEAR %d item(s):" % len(targets))
    for t in targets:
        note = BEHAVIOUR_BEARING.get(t.name, "")
        kind = "dir " if t.is_dir() else "file"
        print("  [%s] %-22s %s" % (kind, t.name, ("-- " + note) if note else ""))
    if keep_identity:
        kept = sorted(n for n in IDENTITY_FILES if (root / n).exists())
        if kept:
            print("")
            print("KEEPING (--keep-identity): %s" % ", ".join(kept))
            print("  NOTE: config.cfg is where scenario_id lives. Keeping it keeps the trap.")
    print("")
    print("Nothing has changed. Re-run with --apply to back up and clear.")
    return 0


def apply(root: Path, keep_identity: bool) -> int:
    if not root.exists():
        print("[OK] No user data at %s -- already a first launch." % root)
        return 0
    targets = entries_to_clear(root, keep_identity)
    if not targets:
        print("[OK] Nothing to clear at %s" % root)
        return 0

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = root / (BACKUP_PREFIX + stamp)
    backup.mkdir(parents=True, exist_ok=False)

    for t in targets:
        shutil.move(str(t), str(backup / t.name))
        print("  moved %s" % t.name)

    print("")
    print("[OK] Cleared %d item(s). Backup: %s" % (len(targets), backup))
    print("[OK] Next launch is a genuine first-launch experience.")
    print("")
    print("VERIFY BEFORE RECORDING -- the point of this script is that you check:")
    print("  - pre-game screen shows Scenario = 'Standard Game'")
    print("  - difficulty shows Standard and is disabled (#1058)")
    print("  - the leaderboard screen is EMPTY for this board")
    print("  - the first-launch welcome overlay appears")
    print("")
    print("Undo with: python tools/reset_player_state.py --restore")
    return 0


def restore(root: Path, overwrite: bool = False) -> int:
    """Undo the most recent --apply.

    WHY THIS REFUSES RATHER THAN REPORTS SUCCESS
    ---------------------------------------------
    Until 2026-08-21 this function skipped any destination that already existed
    and then printed "[OK] Restore complete." and returned 0 regardless. Because
    `leaderboards/` exists as soon as the game runs once, a bare --restore
    skipped THE ENTIRE DIRECTORY and reported success. This is the
    disaster-recovery tool for the incident that destroyed a 50-entry league
    board on 2026-07-31, and it could not perform the one restore it exists for
    while telling the operator it had.

    A recovery tool that cannot distinguish "restored everything" from
    "restored nothing" is worse than no recovery tool, because it converts a
    recoverable loss into a believed-recovered loss.

    Two changes, and neither of them destroys anything:
      - The outcome is COUNTED, and the exit code and final line follow the
        count. Nothing restored plus something skipped is a FAILURE.
      - --overwrite moves the live copy aside to <name>.superseded-<stamp>
        before restoring over it, so the operator can still get back to the
        state they were in thirty seconds ago.
    """
    if not root.exists():
        raise SystemExit("No user data directory at %s" % root)
    backups = sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith(BACKUP_PREFIX))
    if not backups:
        raise SystemExit("No backups found in %s" % root)
    newest = backups[-1]
    print("Restoring from %s" % newest)

    restored, skipped, superseded = [], [], []
    stamp = time.strftime("%Y%m%d_%H%M%S")
    for child in sorted(newest.iterdir()):
        dest = root / child.name
        if dest.exists():
            if not overwrite:
                skipped.append(child.name)
                print("  SKIP %s (already present -- not overwriting)" % child.name)
                continue
            aside = root / ("%s.superseded-%s" % (child.name, stamp))
            shutil.move(str(dest), str(aside))
            superseded.append(aside.name)
            print("  moved live %s aside to %s" % (child.name, aside.name))
        shutil.move(str(child), str(dest))
        restored.append(child.name)
        print("  restored %s" % child.name)

    try:
        newest.rmdir()
    except OSError:
        print("  (backup dir kept: it still holds skipped items)")

    print("")
    print(
        "  restored %d, skipped %d, moved aside %d" % (len(restored), len(skipped), len(superseded))
    )

    if skipped and not restored:
        print("")
        print("[FAILED] NOTHING WAS RESTORED. Every item in the backup already exists")
        print("         at the destination, so all %d were skipped." % len(skipped))
        print("         Skipped: %s" % ", ".join(skipped))
        print("")
        print("         This is the state that used to print [OK]. If you are recovering")
        print("         real data, re-run with --overwrite: the live copies are moved to")
        print("         <name>.superseded-<stamp> first, so nothing is destroyed either way.")
        return 1

    if skipped:
        print("")
        print(
            "[PARTIAL] Restored %d, but %d item(s) already existed and were left alone:"
            % (len(restored), len(skipped))
        )
        print("          %s" % ", ".join(skipped))
        print("          Re-run with --overwrite if those are the ones you need.")
        return 1

    print("[OK] Restore complete -- %d item(s)." % len(restored))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Reset local P(Doom) player state to a first-launch experience.",
    )
    ap.add_argument("--apply", action="store_true", help="actually clear (default is a dry run)")
    ap.add_argument("--restore", action="store_true", help="undo the most recent --apply")
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="with --restore: move a live copy aside to <name>.superseded-<stamp> and restore "
        "over it. Nothing is destroyed. Needed for a real recovery, because a bare "
        "--restore skips anything that already exists and leaderboards/ always does.",
    )
    ap.add_argument(
        "--keep-identity",
        action="store_true",
        help="keep config.cfg + install_id.txt (WARNING: config.cfg carries scenario_id)",
    )
    args = ap.parse_args()

    root = user_data_root()
    if args.restore:
        return restore(root, overwrite=args.overwrite)
    if args.apply:
        return apply(root, args.keep_identity)
    return describe(root, args.keep_identity)


if __name__ == "__main__":
    sys.exit(main())

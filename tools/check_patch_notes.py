#!/usr/bin/env python3
"""check_patch_notes.py -- the shipped version must have patch notes to show.

Layer: PROVE. Cheap, offline, no Godot launch (~10ms).

WHY THIS EXISTS, STATED HONESTLY:
    This check is NOT new. godot/tests/unit/test_patch_notes.gd already asserts that
    patch_notes.json has an entry for the shipped version, and that the entry says
    something. That test was written after patch_notes.json went three releases stale
    (last entry 0.11.0 while 0.14.0 was live).

    What is new is the TIER. That assertion lives only in the GUT suite, which needs
    a Godot binary and an import pass. Nothing in pre-commit runs it, so the guard is
    absent from the one gate that fires on every commit -- the commit that bumps
    version.txt and forgets patch_notes.json passes locally and only goes red later,
    if someone runs the Godot tier at all. This is a Python mirror of the same
    assertions, wired into pre-commit so the bump and the notes travel together.

WHAT GOES WRONG WITHOUT IT (the failure it is pointed at):
    godot/scripts/ui/whats_new_modal.gd looks up GameConfig.get_current_version() in
    data/patch_notes.json. No entry means the What's New modal falls through to
    _display_fallback_notes(). Nothing errors. The player is simply told the release
    had nothing to say, which is a value meaning "I could not tell" rendered as a
    value meaning "fine" (Pip's ruling, 2026-08-23).

THE CHAIN THIS CLOSES:
    version.txt  --(tools/sync_version.py --check)-->  game_config.gd CURRENT_VERSION
                 --(this tool)-->                      godot/data/patch_notes.json
    The first link was already gated; the second was not, in this tier.

STATE AT TIME OF WRITING (2026-08-24): 0.14.3 IS present, so this is latent. That is
    the point -- nothing kept it that way.

USAGE:
    python tools/check_patch_notes.py           # report; exit 0 clean, 1 problem
    python tools/check_patch_notes.py --quiet   # print only on failure

EXIT CODES:
    0  patch_notes.json has a usable entry for version.txt's version
    1  it does not (missing entry, empty entry, unreadable/misshapen file)
    2  could not run the check at all (version.txt absent)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "version.txt"
PATCH_NOTES_FILE = REPO_ROOT / "godot" / "data" / "patch_notes.json"

# The keys whats_new_modal.gd renders as body lines. An entry that fills none of them
# renders a blank modal, which is the fallback message with extra steps.
BODY_KEYS = ("added", "fixed", "changed")


def check(version_file: Path = VERSION_FILE, notes_file: Path = PATCH_NOTES_FILE) -> List[str]:
    """Return a list of problems. Empty list means clean."""
    if not version_file.exists():
        return ["MISSING {} -- cannot tell which version shipped".format(version_file)]

    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        return ["EMPTY {} -- cannot tell which version shipped".format(version_file)]

    if not notes_file.exists():
        return [
            "MISSING {}".format(notes_file),
            "  The What's New modal would show its fallback to every player.",
        ]

    try:
        data = json.loads(notes_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ["UNREADABLE {}: {}".format(notes_file, exc)]

    # Mirror whats_new_modal.gd's ingest_patch_notes_text() shape guard: valid JSON is
    # not the same as the shape the modal reads.
    if not isinstance(data, dict) or not isinstance(data.get("versions"), list):
        return [
            "{} is not an object with a 'versions' array".format(notes_file.name),
            "  whats_new_modal.gd reads patch_notes_data['versions'] and would find nothing.",
        ]

    entry = None
    for candidate in data["versions"]:
        # The modal matches the EXACT string from GameConfig.get_current_version(), so
        # a "v" prefix or a trailing space here is the same failure as no entry at all.
        if isinstance(candidate, dict) and candidate.get("version") == version:
            entry = candidate
            break

    if entry is None:
        listed = [str(v.get("version")) for v in data["versions"] if isinstance(v, dict)]
        return [
            "no entry for the shipped version {} in {}".format(version, notes_file.name),
            "  version.txt says {}; patch_notes.json lists {}".format(
                version, ", ".join(listed[:5]) or "(nothing)"
            ),
            "  Every player would be told this release had no notes.",
            "  Fix: add a {} entry to {}.".format(version, notes_file.name),
        ]

    problems: List[str] = []
    if not str(entry.get("title", "")).strip():
        problems.append(
            "the {} entry has no title -- the modal renders it in the header".format(version)
        )

    sections = entry.get("sections", {})
    if not isinstance(sections, dict):
        sections = {}
    body_count = len(entry.get("highlights", []) or [])
    for key in BODY_KEYS:
        body_count += len(sections.get(key, []) or [])
    if body_count == 0:
        problems.append(
            "the {} entry has no highlights and no added/fixed/changed lines -- "
            "it renders a blank modal, which is the fallback with extra steps".format(version)
        )

    return problems


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check godot/data/patch_notes.json covers version.txt's version"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="print only on failure (for hook wrappers)"
    )
    args = parser.parse_args(argv)

    if not VERSION_FILE.exists():
        print("[patch-notes] CANNOT CHECK: {} not found".format(VERSION_FILE))
        return 2

    problems = check()

    if problems:
        print("[patch-notes] FAIL:")
        for problem in problems:
            print("  - {}".format(problem))
        print("[patch-notes] Same assertion as godot/tests/unit/test_patch_notes.gd,")
        print("[patch-notes] run here because pre-commit cannot run the Godot tier.")
        return 1

    if not args.quiet:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
        print("[patch-notes] OK: patch_notes.json has a non-empty entry for {}".format(version))
    return 0


if __name__ == "__main__":
    sys.exit(main())

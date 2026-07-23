#!/usr/bin/env python3
"""Heuristic guard: did this diff need a ladder_version bump (or get one it didn't need)?

Part of the build-vs-ladder version split
(docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md, Section 4.2). The dangerous
silent failure is a HUMAN forgetting to bump ``ladder_version.txt`` on a
gameplay PR (which silently keeps incomparable scores on one board), or bumping
it on a cosmetic one (which needlessly forks the board). This script flags both
as WARNINGS on a PR diff.

This is a SMELL DETECTOR, not a proof: a comment-only edit inside
``godot/scripts/core/`` is a false positive, and an RNG-stream refactor hidden
in a file outside the allowlist is a false negative (the golden-replay
determinism backstop in the slow test tier is the stronger signal for that).
Warnings are meant to be acked by a reviewer against the Section 3.3 checklist,
not to hard-block.

Usage::

    python tools/check_ladder_bump.py                  # diff vs origin/main, warn only
    python tools/check_ladder_bump.py --base <ref>     # explicit base ref
    python tools/check_ladder_bump.py --strict         # exit 1 on any warning (CI gate)

Default exit code is 0 even with warnings (advisory); ``--strict`` turns
warnings into a failing exit for pipelines that want an explicit ack step.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LADDER_FILE = "ladder_version.txt"

# Gameplay surface (spec Section 4.2): paths where a change plausibly alters
# scores, trajectories, seeds, or RNG streams on a fixed seed -- i.e. the
# Section 3.1 bump triggers. Everything else is presumed cosmetic (Section 3.2).
GAMEPLAY_PREFIXES = (
    "godot/scripts/core/",  # game logic: game_state, turn_manager, actions, doom, finance, ...
    "godot/data/",  # data-driven balance/events/actions/scenarios (JSON)
)
GAMEPLAY_BASENAMES = ("seed_schedule.gd",)  # ADR-0005 seed schedules -- part of a seed's identity
# Paths under the prefixes above that are NOT gameplay surface (dev/test-only).
EXCLUDE_PREFIXES = (
    "godot/tests/",
    "godot/scripts/dev/",
)
# Godot metadata churn, never gameplay: .uid = stable resource IDs, .import = import
# metadata (both tracked on purpose, see CLAUDE.md).
EXCLUDE_SUFFIXES = (
    ".uid",
    ".import",
)


def _git_diff_names(spec: list[str]) -> str:
    return subprocess.run(
        ["git", "diff", "--name-only", *spec],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def changed_files(base: str) -> list[str]:
    """Names of files changed between base and the working tree (committed + staged + unstaged)."""
    try:
        try:
            # Merge-base diff (what the PR actually adds). Needs enough history.
            out = _git_diff_names([f"{base}...HEAD"])
        except subprocess.CalledProcessError:
            # Shallow-clone fallback (CI checkouts often lack the merge base):
            # a plain two-endpoint diff overcounts (includes base-side drift) but
            # only ever makes this advisory check noisier, never silent.
            out = _git_diff_names([base, "HEAD"])
        # Also fold in uncommitted work so the check is useful pre-commit, not just on PRs.
        out += _git_diff_names(["HEAD"])
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise SystemExit(f"[check_ladder_bump] git diff against {base!r} failed: {exc}")
    return sorted({line.strip() for line in out.splitlines() if line.strip()})


def is_gameplay_surface(path: str) -> bool:
    p = path.replace("\\", "/")
    if any(p.startswith(x) for x in EXCLUDE_PREFIXES):
        return False
    if any(p.endswith(x) for x in EXCLUDE_SUFFIXES):
        return False
    if any(p.startswith(x) for x in GAMEPLAY_PREFIXES):
        return True
    return any(p.endswith("/" + name) or p == name for name in GAMEPLAY_BASENAMES)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="origin/main",
        help="base ref to diff against (default: origin/main)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on any warning (default: advisory, exit 0)",
    )
    args = parser.parse_args()

    files = changed_files(args.base)
    gameplay = [f for f in files if is_gameplay_surface(f)]
    ladder_bumped = LADDER_FILE in files

    warnings: list[str] = []
    if gameplay and not ladder_bumped:
        warnings.append(
            "gameplay-surface files changed but ladder_version.txt was NOT bumped.\n"
            "  If this diff can change any score, trajectory, seed schedule, or RNG\n"
            "  stream on a fixed seed (spec Section 3.3 checklist), bump\n"
            "  ladder_version.txt and run: python tools/sync_version.py\n"
            "  Gameplay-surface files in this diff:\n"
            + "".join(f"    - {f}\n" for f in gameplay[:20])
            + (f"    ... and {len(gameplay) - 20} more\n" if len(gameplay) > 20 else "")
        )
    if ladder_bumped and not gameplay:
        warnings.append(
            "ladder_version.txt was bumped but NO gameplay-surface files changed.\n"
            "  A cosmetic-only patch must NOT fork the leaderboard (spec Section 3.2).\n"
            "  If the gameplay change lives outside the path allowlist, ack this; else\n"
            "  revert the ladder bump."
        )

    if not warnings:
        state = "bumped" if ladder_bumped else "not bumped"
        print(
            f"[check_ladder_bump] OK: {len(gameplay)} gameplay-surface file(s) changed, "
            f"ladder_version.txt {state} -- consistent."
        )
        return 0

    for w in warnings:
        print(f"[check_ladder_bump] WARNING: {w}")
    if args.strict:
        print("[check_ladder_bump] --strict: treating warnings as failure")
        return 1
    print("[check_ladder_bump] advisory mode: not failing the build. Reviewer must ack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

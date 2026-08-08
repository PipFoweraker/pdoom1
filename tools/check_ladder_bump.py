#!/usr/bin/env python3
"""Heuristic guard: did this diff need a ladder_version bump (or get one it didn't need)?

Layer: PROVE -- under --strict this fails the build unless a human acks in writing

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
So a warning is not "you must bump" -- it is "a human must say, in writing,
which of the two it is". ``--strict`` enforces exactly that: warnings fail the
build UNLESS the ack text (see ``--ack-env``) carries a ``ladder-ack:`` line.

Why the ack instead of a plain hard-fail (issue #1178): the ladder legitimately
moves ONCE PER EPOCH, not once per PR (L1..L4 across hundreds of PRs), so
"gameplay files changed and the ladder did not move" is the NORMAL case. A bare
hard-fail would go red on nearly every gameplay PR and be switched off again --
which is how this check spent its whole life behind ``|| true``.

Usage::

    python tools/check_ladder_bump.py                  # diff vs origin/main, warn only
    python tools/check_ladder_bump.py --base <ref>     # explicit base ref
    python tools/check_ladder_bump.py --strict         # exit 1 on unacked warnings (CI gate)
    LADDER_ACK="ladder-ack: cosmetic copy fix" python tools/check_ladder_bump.py --strict

Default exit code is 0 even with warnings (advisory, for local and gate-ritual
use); ``--strict`` is what CI runs, and CI runs it WITHOUT ``|| true``.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LADDER_FILE = "ladder_version.txt"

# A reviewer's written ack, looked for in the --ack-env text (in CI: the PR body,
# or a synthesised line when the `ladder-ack` label is applied). The reason is
# mandatory and must be substantive -- "ladder-ack: y" is not a decision record.
ACK_PATTERN = re.compile(
    r"^[^\S\n]*ladder-ack[^\S\n]*:[^\S\n]*(\S.*?)[^\S\n]*$", re.IGNORECASE | re.MULTILINE
)
ACK_MIN_REASON_CHARS = 8

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
# metadata (both tracked on purpose, see CLAUDE.md). ".md" is prose that ships in
# the .pck but cannot move a score -- it was a real false positive: the #1137 run
# named godot/data/events/overrides/README.md as gameplay surface.
EXCLUDE_SUFFIXES = (
    ".uid",
    ".import",
    ".md",
)
# Exact paths under a gameplay prefix that are prose, not rules. Kept as an explicit
# short list rather than a pattern, so adding one is a decision someone made.
# patch_notes.json is release copy read only by godot/scripts/ui/whats_new_modal.gd;
# it changes on EVERY release, so leaving it in made the strict gate demand an ack
# on every release PR -- the exact noise that got '|| true' added in the first place.
EXCLUDE_PATHS = ("godot/data/patch_notes.json",)


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
    if p in EXCLUDE_PATHS:
        return False
    if any(p.startswith(x) for x in EXCLUDE_PREFIXES):
        return False
    if any(p.endswith(x) for x in EXCLUDE_SUFFIXES):
        return False
    if any(p.startswith(x) for x in GAMEPLAY_PREFIXES):
        return True
    return any(p.endswith("/" + name) or p == name for name in GAMEPLAY_BASENAMES)


def find_ack(text: str) -> str | None:
    """The reviewer's written ack reason, or None if the text carries no usable ack.

    A ``ladder-ack:`` line with a too-short reason is deliberately NOT an ack --
    the point of the mechanism is that someone had to state which case this is.
    """
    for match in ACK_PATTERN.finditer(text or ""):
        reason = match.group(1).strip()
        if len(reason) >= ACK_MIN_REASON_CHARS:
            return reason
    return None


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
        help="exit 1 on any warning that carries no written ack (this is what CI runs)",
    )
    parser.add_argument(
        "--ack-env",
        default="LADDER_ACK",
        help=(
            "name of the environment variable searched for a 'ladder-ack: <reason>' "
            "line (default: LADDER_ACK). Only consulted under --strict."
        ),
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

    if not args.strict:
        print("[check_ladder_bump] advisory mode (no --strict): not failing. Reviewer must ack.")
        return 0

    ack = find_ack(os.environ.get(args.ack_env, ""))
    if ack:
        print(f"[check_ladder_bump] ACKED by reviewer via {args.ack_env}: {ack}")
        print("[check_ladder_bump] --strict: warning(s) acked in writing, passing.")
        return 0

    print(
        "[check_ladder_bump] --strict: FAILING. The warning above is not a demand to bump --\n"
        "  it is a demand that a human state, in writing, which case this is.\n"
        "  To ack, do EITHER:\n"
        "    - add a line to the PR body:  ladder-ack: <reason, at least "
        f"{ACK_MIN_REASON_CHARS} chars>\n"
        "    - or apply the 'ladder-ack' label to the PR,\n"
        "  then re-run this job. Decide against the Section 3.3 checklist in\n"
        "  docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md. If the diff CAN change a\n"
        "  score/trajectory/seed/RNG stream on a fixed seed, bump ladder_version.txt and\n"
        "  run: python tools/sync_version.py"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

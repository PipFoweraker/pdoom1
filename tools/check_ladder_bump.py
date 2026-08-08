#!/usr/bin/env python3
"""Guard: did this diff need a ladder_version bump (or get one it did not need)?

Layer: PROVE -- this gate FAILS the build. It was advisory (`|| true`) until
issue #1178, and in that state it produced a worthless signal in both
directions on two consecutive releases:

  * It MISSED the #1137 historical-deck retime for 31 hours. That PR changed
    which events fire on a given seed -- the textbook Section 3.1 trigger --
    but it landed in ``godot/autoload/event_service.gd`` and the old
    ``GAMEPLAY_PREFIXES`` allowlist covered only ``godot/scripts/core/`` and
    ``godot/data/``. A human caught it at cut time, not CI.
  * It WARNED on the v0.14.0 epoch cut, which was correct. An epoch cut is by
    construction a version-files-only commit; the gameplay change it pays for
    landed in an earlier PR. The old check could only see one PR.

Both failures are fixed here, and both fixes are proven against real history by
``tests/test_check_ladder_bump.py`` (the #1137 range must go RED, the v0.14.0
and v0.14.1 cuts must go GREEN).

Spec: ``docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md`` Sections 3.1/3.2
(what bumps the ladder) and 4.2 (this guard). The rule it enforces: the ladder
version bumps if and only if two identical inputs (same seed, same player
choices) could produce a different score, trajectory, or RNG stream than the
previous epoch.

WHAT CHANGED, AND WHY
---------------------

1. **Polarity inverted: gameplay is the DEFAULT inside ``godot/``.** The old
   allowlist had to enumerate every gameplay directory in advance and was
   therefore wrong the first time a gameplay system moved. Here, everything
   under ``godot/`` counts as gameplay surface UNLESS it is on the cosmetic
   denylist below. A new directory, a new autoload, a system moved between
   folders -- all fail safe (flagged) instead of failing silent. The costs are
   asymmetric: a missed bump silently merges scores earned under different
   rules onto one board and cannot be undone after players have played; a
   spurious flag costs one line in a commit message.

2. **It can see an epoch cut.** When a diff bumps the ladder, the question is
   NOT "did this PR change gameplay" -- an epoch cut never does. The question
   is "did anything since the PREVIOUS epoch change gameplay". So the second
   check looks back over the whole epoch window (last ladder-bumping commit ..
   HEAD), not the PR. See ``previous_epoch_commit``.

3. **An omission now has to be answered, not merely not-forgotten.** A gameplay
   diff that deliberately does not bump the ladder (a refactor with no
   behavioural change, a comment edit inside ``core/``) declares so with a
   ``Ladder-Impact:`` line in a commit message or the PR body::

       Ladder-Impact: none -- comment-only edit, no reachable behaviour change
       Ladder-Impact: bump

   Without that line the gate fails. This is the point: the guard cannot decide
   whether a diff changes behaviour, and pretending otherwise is what produced
   the two useless signals above. It CAN insist that a human stated an answer,
   in a place that is preserved in git and readable at cut time.

WHAT IT STILL CANNOT SEE
------------------------

* **RNG-stream changes outside ``godot/``**, or inside a denylisted cosmetic
  path. A UI file that consumes a ``randi()`` draw would shift the stream and
  not be flagged. The golden-replay determinism backstop (spec 4.2, slow tier)
  is the only real answer to that; this is a path heuristic.
* **Whether the gameplay change in an epoch window is the one that justified
  the bump.** It proves only that the epoch contains SOME gameplay change.
* **A false ``Ladder-Impact: none``.** The declaration is trusted. It converts
  a silent omission into an attributable statement; it does not verify it.
* **Shallow clones.** The epoch lookback needs history back to the previous
  ladder bump. If the repository is shallow and the previous epoch commit is
  unreachable, the epoch-window check is SKIPPED with a loud message rather
  than passing quietly (CI checks out with ``fetch-depth: 0`` so this should
  not fire there).

Usage::

    python tools/check_ladder_bump.py                     # diff vs origin/main
    python tools/check_ladder_bump.py --base <ref>        # explicit base
    python tools/check_ladder_bump.py --base A --head B   # historical range
    python tools/check_ladder_bump.py --advisory          # never fail (opt-in)

Exit 1 on any finding unless ``--advisory``. A ``Ladder-Impact:`` declaration
may also be supplied out-of-band via the ``LADDER_DECLARATION_TEXT`` env var
(CI feeds it the PR body).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LADDER_FILE = "ladder_version.txt"

# ---------------------------------------------------------------------------
# What counts as gameplay surface (spec Sections 3.1 / 3.2)
# ---------------------------------------------------------------------------

# Everything the shipped game is built from. Outside this root nothing can
# change a run outcome (scripts/, tools/, docs/, .github/ are CI and prose).
GAMEPLAY_ROOT = "godot/"

# Cosmetic / non-behavioural areas inside the game root (spec Section 3.2:
# "UI layout, panels, main_ui.gd presentation, colors, fonts", music, art,
# copy, tooling/CI/docs). A change here is presumed NOT to alter any score or
# trajectory. This list is the ONLY thing standing between a file and being
# treated as gameplay -- adding to it is a deliberate act.
COSMETIC_PREFIXES = (
    "godot/addons/",  # third-party editor addons, not shipped logic
    "godot/assets/",  # art, audio, fonts
    "godot/docs/",  # prose
    "godot/scenes/",  # scene layout (presentation); logic lives in scripts/
    "godot/scripts/debug/",  # dev-only
    "godot/scripts/dev/",  # dev-only
    "godot/scripts/ui/",  # spec 3.2: presentation
    "godot/tests/",  # tests cannot change a shipped run
    "godot/theme/",  # colors/fonts
    "godot/tools/",  # in-editor tooling
)

# Individual cosmetic files inside otherwise-gameplay directories.
COSMETIC_FILES = (
    "godot/build_stamp.txt",  # build provenance marker
    "godot/data/credits.json",  # names, not rules
    "godot/data/icon_mapping.json",  # which icon renders, not what happens
    "godot/data/patch_notes.json",  # player-facing copy (ships in every patch)
    "godot/export_presets.cfg",  # build config (a sync_version.py target)
    "godot/project.godot",  # engine config (a sync_version.py target)
)

# Non-behavioural file kinds anywhere in the tree. `.uid`/`.import` are Godot
# metadata tracked on purpose (CLAUDE.md); `.md` is prose.
COSMETIC_SUFFIXES = (
    ".import",
    ".md",
    ".uid",
)

# ---------------------------------------------------------------------------
# Release-cut lines: real gameplay files whose ONLY change on a release commit
# is a stamped or curated release constant.
# ---------------------------------------------------------------------------

# godot/autoload/game_config.gd is genuinely gameplay surface (it holds
# effective_difficulty(), the league difficulty lock). But it is also a
# sync_version.py stamp target, so EVERY release cut touches it. If the only
# lines that moved are these release constants, the file is not evidence of a
# gameplay change.
RELEASE_LINE_FILES = ("godot/autoload/game_config.gd",)
RELEASE_LINE_PATTERNS = (
    re.compile(r"^\s*const CURRENT_VERSION\b"),  # stamped from version.txt
    re.compile(r"^\s*const LADDER_VERSION\b"),  # stamped from ladder_version.txt
    re.compile(r"^\s*const INTRO_VERSION\b"),  # cold-open content version (cosmetic)
    # Rolling which seed is FEATURED does not change what happens on any given
    # seed, so per spec 3.1 it is not a bump trigger -- it starts a new board by
    # SEED, not a new epoch. Judgement call, stated so it can be argued with.
    re.compile(r"^\s*const FEATURED_SEED_OVERRIDE\b"),
)

DECLARATION_RE = re.compile(r"^\s*Ladder-Impact:\s*(none|bump|n/a)\b", re.IGNORECASE | re.MULTILINE)


# ---------------------------------------------------------------------------
# git plumbing
# ---------------------------------------------------------------------------


def _git(args: list[str], check: bool = True) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=check,
    ).stdout


class Range:
    """A diff range that knows how to name and re-diff its own files."""

    def __init__(self, base: str, head: str) -> None:
        self.base = base
        self.head = head
        try:
            # Merge-base diff: what this branch ADDS, ignoring base-side drift.
            _git(["merge-base", base, head])
            self.spec = [f"{base}...{head}"]
        except subprocess.CalledProcessError:
            # Shallow checkouts often lack the merge base. Two-endpoint diff
            # overcounts (folds in base-side commits) but is never silent.
            self.spec = [base, head]

    def names(self) -> list[str]:
        out = _git(["diff", "--name-only", *self.spec])
        if self.head == "HEAD":
            # Fold in uncommitted work so the check is useful pre-commit too.
            out += _git(["diff", "--name-only", "HEAD"])
        return sorted({line.strip() for line in out.splitlines() if line.strip()})

    def patch_lines(self, path: str) -> list[str]:
        """Added/removed content lines for one path (no +++/--- headers)."""
        out = _git(["diff", "-U0", *self.spec, "--", path])
        if self.head == "HEAD":
            out += _git(["diff", "-U0", "HEAD", "--", path])
        return [
            ln[1:]
            for ln in out.splitlines()
            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))
        ]

    def commit_messages(self) -> str:
        try:
            return _git(["log", "--format=%B", f"{self.base}..{self.head}"])
        except subprocess.CalledProcessError:
            return ""


def previous_epoch_commit(rng: Range) -> str | None:
    """The last commit that changed ladder_version.txt BEFORE this range.

    An epoch cut carries no gameplay change of its own -- the gameplay it pays
    for landed earlier. So the window to inspect is [previous epoch .. HEAD],
    not [PR base .. HEAD]. Returns None when no earlier epoch is reachable
    (first epoch ever, or a shallow clone).
    """
    try:
        touched = _git(["log", "--format=%H", rng.head, "--", LADDER_FILE]).split()
        in_range = set(_git(["rev-list", f"{rng.base}..{rng.head}"]).split())
    except subprocess.CalledProcessError:
        return None
    for sha in touched:  # newest first
        if sha not in in_range:
            return sha
    return None


def is_shallow() -> bool:
    return _git(["rev-parse", "--is-shallow-repository"], check=False).strip() == "true"


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------


def is_cosmetic_path(path: str) -> bool:
    """True when the path alone proves the change cannot alter a run."""
    p = path.replace("\\", "/")
    if not p.startswith(GAMEPLAY_ROOT):
        return True
    if p.endswith(COSMETIC_SUFFIXES):
        return True
    if p in COSMETIC_FILES:
        return True
    return p.startswith(COSMETIC_PREFIXES)


def gameplay_files(rng: Range, files: list[str]) -> list[str]:
    out = []
    for path in files:
        p = path.replace("\\", "/")
        if is_cosmetic_path(p):
            continue
        if p in RELEASE_LINE_FILES and _release_lines_only(rng, p):
            continue
        out.append(p)
    return out


def _release_lines_only(rng: Range, path: str) -> bool:
    """True when every changed line in `path` is a release constant."""
    lines = rng.patch_lines(path)
    if not lines:
        return False  # nothing to prove; treat as a real change
    return all(any(pat.match(ln) for pat in RELEASE_LINE_PATTERNS) for ln in lines)


def declaration(rng: Range) -> str | None:
    """The Ladder-Impact declaration, from commit messages or CI-supplied text."""
    for text in (os.environ.get("LADDER_DECLARATION_TEXT", ""), rng.commit_messages()):
        m = DECLARATION_RE.search(text or "")
        if m:
            return m.group(0).strip()
    return None


# ---------------------------------------------------------------------------


def _bullets(paths: list[str], limit: int = 20) -> str:
    shown = "".join(f"    - {p}\n" for p in paths[:limit])
    if len(paths) > limit:
        shown += f"    ... and {len(paths) - limit} more\n"
    return shown


def run(base: str, head: str) -> list[str]:
    """Return a list of findings (empty == the diff is self-consistent)."""
    rng = Range(base, head)
    files = rng.names()
    gameplay = gameplay_files(rng, files)
    ladder_bumped = LADDER_FILE in files
    findings: list[str] = []

    # Direction 1 -- gameplay changed, ladder did not move, nobody said why.
    if gameplay and not ladder_bumped:
        decl = declaration(rng)
        if decl is None:
            findings.append(
                "gameplay-surface files changed, ladder_version.txt was NOT bumped,\n"
                "  and no Ladder-Impact declaration was found.\n"
                "  Answer the spec Section 3.3 checklist, then either bump\n"
                "  ladder_version.txt (and run: python tools/sync_version.py), or add\n"
                "  a line to a commit message or the PR body saying why not:\n"
                "      Ladder-Impact: none -- <one line of reasoning>\n"
                "  Gameplay-surface files in this diff:\n" + _bullets(gameplay)
            )
        else:
            print(f"[check_ladder_bump] declared: {decl}")

    # Direction 2 -- ladder bumped. An epoch cut is version-files-only by
    # construction, so ask about the EPOCH, not this diff.
    if ladder_bumped:
        prev = previous_epoch_commit(rng)
        if prev is None:
            if is_shallow():
                print(
                    "[check_ladder_bump] SKIP epoch-window check: no earlier ladder bump\n"
                    "  reachable in a shallow clone. Check out with fetch-depth: 0 to arm it."
                )
            else:
                print(
                    "[check_ladder_bump] epoch-window check: no earlier ladder bump in\n"
                    "  history (this is epoch 1) -- nothing to compare against."
                )
        else:
            window = Range(prev, head)
            win_gameplay = gameplay_files(window, window.names())
            short = prev[:8]
            if win_gameplay:
                print(
                    f"[check_ladder_bump] epoch window {short}..{head}: "
                    f"{len(win_gameplay)} gameplay-surface file(s) changed since the "
                    "previous epoch -- the bump is justified."
                )
            elif declaration(window) is not None:
                print(
                    "[check_ladder_bump] epoch window has no gameplay-surface file, "
                    "but the bump is declared -- accepted."
                )
            else:
                findings.append(
                    "ladder_version.txt was bumped, but NO gameplay-surface file has\n"
                    f"  changed since the previous epoch ({short}).\n"
                    "  A cosmetic-only epoch fork scatters comparable scores across two\n"
                    "  boards for nothing (spec Section 3.2). Either revert the bump, or\n"
                    "  -- if the gameplay change is invisible to a path heuristic (an RNG\n"
                    "  reorder in a cosmetic path, a server-side rule) -- declare it:\n"
                    "      Ladder-Impact: bump -- <one line of reasoning>"
                )

    if not findings:
        state = "bumped" if ladder_bumped else "not bumped"
        print(
            f"[check_ladder_bump] OK: {len(gameplay)} gameplay-surface file(s) changed, "
            f"ladder_version.txt {state} -- consistent."
        )
    return findings


# ---------------------------------------------------------------------------
# Self-test: prove the gate against real history, every CI run
# ---------------------------------------------------------------------------

# "A guard that has never been shown to fail is not evidence" -- issue #1178,
# and issue #640 before it (CI reported green while running zero tests). These
# are real commits on main, and each one is a case this gate got WRONG before
# #1178. They run in the same CI step that arms the gate.
SELF_TEST_CASES = (
    (
        "1137 historical-deck retime -- changes which events fire on a seed, no bump",
        "8791ba47^",
        "8791ba47",
        1,
        "MUST FAIL: the real 31-hour miss",
    ),
    (
        "1101 net fix in godot/autoload/event_service.gd -- old allowlist was blind here",
        "d7b47a1a^",
        "d7b47a1a",
        1,
        "MUST FAIL: gameplay surface outside godot/scripts/core and godot/data",
    ),
    (
        "v0.14.0 epoch cut -- version files only, ladder L3 -> L4",
        "7368e237^",
        "7368e237",
        0,
        "MUST PASS: a correct epoch cut never carries its own gameplay change",
    ),
    (
        "v0.14.1 patch cut -- ladder held at L4, patch_notes.json touched",
        "0dc8adb9^",
        "0dc8adb9",
        0,
        "MUST PASS: player-facing copy is not gameplay surface",
    ),
)


def self_test() -> int:
    os.environ.pop("LADDER_DECLARATION_TEXT", None)
    ran = failed = skipped = 0
    for name, base, head, expected, why in SELF_TEST_CASES:
        try:
            _git(["rev-parse", "--verify", f"{head}^{{commit}}"])
            _git(["rev-parse", "--verify", f"{base}^{{commit}}"])
        except subprocess.CalledProcessError:
            print(f"[self-test] SKIP  {name}\n           (history unreachable -- shallow clone?)")
            skipped += 1
            continue
        print(f"\n[self-test] CASE  {name}\n            {why}")
        findings = run(base, head)
        for f in findings:
            print(f"[check_ladder_bump] FAIL: {f}")
        actual = 1 if findings else 0
        ran += 1
        verdict = "OK" if actual == expected else "MISMATCH"
        if actual != expected:
            failed += 1
        print(f"[self-test] {verdict}: expected exit {expected}, got {actual}")

    print(f"\n[self-test] {ran} case(s) ran, {failed} mismatch(es), {skipped} skipped.")
    if ran == 0:
        print("[self-test] FAIL: nothing ran, so nothing was proven. Need full git history")
        print("            (actions/checkout with fetch-depth: 0).")
        return 1
    if failed:
        print("[self-test] FAIL: the gate does not reproduce its own acceptance history.")
        return 1
    print("[self-test] PASS: red on both real misses, green on both real release cuts.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ladder-bump consistency gate.")
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="report findings but always exit 0 (opt-out of the gate)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="deprecated no-op: failing is now the default",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="replay the historical acceptance cases (#1178) and verify red/green",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    findings = run(args.base, args.head)
    for f in findings:
        print(f"[check_ladder_bump] FAIL: {f}")
    if not findings:
        return 0
    if args.advisory:
        print("[check_ladder_bump] --advisory: not failing the build.")
        return 0
    print(
        "[check_ladder_bump] Gate armed (issue #1178). Spec: "
        "docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md Section 3.3."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

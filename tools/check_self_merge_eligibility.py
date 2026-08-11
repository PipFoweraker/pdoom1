#!/usr/bin/env python3
"""Guard: does this PR actually qualify for the self-merge class it claims?

Layer: PROVE -- this gate FAILS the PR check when a claim is unsupported.

WHY THIS EXISTS
---------------

Ruling ``RULED_2026-08-10_pr-self-merge-and-four-more.md`` R1 lets a seat merge
two PR classes without Pip:

  * **Guard** -- adds or repairs a check, gate, alarm or CI condition. YES, on green.
  * **Docs** -- corrects documentation to match measured reality. YES, on green.
  * Anything touching a public claim, an entity boundary, a rule, or anything
    irreversible -- NO, still Pip.

The labels ``class:guard`` and ``class:docs`` were created in three repos on
2026-08-10 and, until this file existed, they **promised eligibility and checked
nothing**. That is precisely the defect that retired ``ship:hotpatch-48h`` on the
same day: a label that asserts a property no mechanism enforces is a claim, not a
control. R1 attaches two conditions, and this gate mechanises the first one:

  1. **Estate rule Section 5g still applies to the guard class.** "A guard PR
     merged without a RED run observed and its run ID recorded is not an
     installed guard, it is an untested one."
  2. Say what you merged. (Social; not mechanisable here.)

WHAT IT ENFORCES
----------------

Five rules, in this order (first failure wins the message, all are reported):

  1. ``needs:pip`` present alongside a class label -> FAIL, whatever the rest of
     the evidence says. The label means blocked on Pip and nobody else; a
     self-merge class cannot override it.
  2. Both ``class:guard`` and ``class:docs`` -> FAIL. A PR is one class or
     neither. Two claims means the author has not decided which review standard
     they are asking to skip.
  3. Neither class label -> PASS, neutral. **This check must never block a
     normal PR.** It has an opinion only about PRs that claim an exemption.
     Note the deliberate reading of rule 1 this implies: ``needs:pip`` on its
     own, with no class label, is NOT a failure. A hold that nobody is trying
     to skip is the normal state of a queued PR, and turning every held PR red
     would teach everyone to ignore this check -- which is how a control decays
     back into a label. ``needs:pip`` is a veto on a CLAIM; with no claim there
     is nothing to veto. Flip ``BLOCKED_FAILS_ALONE`` if that judgement is
     overruled.
  4. ``class:docs`` -> PASS only if EVERY changed path is documentation (rule
     below). Any non-doc path is listed by name.
  5. ``class:guard`` -> PASS only if the PR body carries a RED-run declaration
     in the fixed format below.

THE ``RED-RUN`` TOKEN
---------------------

::

    RED-RUN: <run-url-or-run-id> -- <one line: what was broken to make it fail>

Design copied deliberately from ``tools/check_ladder_bump.py``'s
``Ladder-Impact:`` line, which solved the same problem (a required human
declaration, preserved by git, parsed by a regex, with a mandatory substantive
reason so the magic words alone are not enough). Reusing its shape means one
format to learn and one failure-message style to read.

What the gate can and cannot see: it verifies that a plausible run reference and
a reason were **stated**, not that the run exists, that it was red, or that it
was red for the stated reason. Same trust boundary as ``Ladder-Impact:`` -- it
converts a silent omission into an attributable statement. The reviewer clicks
the link.

WHAT COUNTS AS DOCUMENTATION (this repo)
----------------------------------------

A path is documentation if it ends in ``.md``, ``.rst`` or ``.txt``, or lives
under ``docs/`` -- EXCEPT the machine-read ``.txt`` files listed in
``NOT_DOCUMENTATION``. That exception is not theoretical here: ``version.txt``
and ``ladder_version.txt`` are the version and leaderboard-epoch SSOTs (CLAUDE.md
-- a silent drift forks the board key), ``requirements*.txt`` are dependency
pins, and ``godot/build_stamp.txt`` / ``godot/steam_appid.txt`` are engine data
packed into the shipped ``.pck``. All five end in ``.txt`` and none of them is
prose. Everything under ``godot/addons/`` is vendored third-party code.

Usage::

    python tools/check_self_merge_eligibility.py --base origin/main
    python tools/check_self_merge_eligibility.py --paths-file changed.txt
    python tools/check_self_merge_eligibility.py --self-test

Inputs arrive by environment variable, never inlined into a shell command, since
both are attacker-influenced on a fork PR:

  * ``PR_LABELS``  -- JSON array or comma/newline separated label names
  * ``PR_BODY``    -- the pull request body text

Exit 1 on any finding, 0 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

GUARD_LABEL = "class:guard"
DOCS_LABEL = "class:docs"
BLOCKED_LABEL = "needs:pip"

# Does needs:pip fail a PR that claims no self-merge class? No, by the argument
# in the module docstring (rule 3). One constant, so overruling it is one edit.
BLOCKED_FAILS_ALONE = False

# ---------------------------------------------------------------------------
# What counts as documentation
# ---------------------------------------------------------------------------

DOC_SUFFIXES = (".md", ".rst", ".txt")
DOC_PREFIXES = ("docs/",)

# Machine-read files that merely happen to end in a doc suffix. Editing one of
# these is never "correcting documentation to match measured reality"; it moves
# a version, a dependency pin, or shipped engine data.
NOT_DOCUMENTATION = (
    "ladder_version.txt",  # leaderboard epoch SSOT (forks the board key)
    "version.txt",  # version SSOT
    "requirements.txt",  # dependency pin
    "requirements-dev.txt",  # dependency pin
    "godot/build_stamp.txt",  # build provenance, packed into the .pck
    "godot/steam_appid.txt",  # engine/platform data
)

# Vendored third-party trees: a .md or .txt in here is upstream's, not ours.
NOT_DOCUMENTATION_PREFIXES = ("godot/addons/",)

# ---------------------------------------------------------------------------
# The RED-RUN declaration (shape adopted from check_ladder_bump.DECLARATION_RE)
# ---------------------------------------------------------------------------

RED_RUN_FORMAT = "RED-RUN: <run-url-or-run-id> -- <what was broken to make it fail>"

# A reference is either a URL or a bare numeric run id. GitHub run ids are long
# integers; requiring >= 6 digits rejects "RED-RUN: 1 -- trust me" without
# pretending to validate the id.
RED_RUN_RE = re.compile(
    r"^[^\S\n]*RED-RUN:[^\S\n]*(?P<ref>https?://\S+|[0-9]{6,})"
    r"[^\S\n]*(?:--|:)?[^\S\n]*(?P<reason>.*?)[^\S\n]*$",
    re.IGNORECASE | re.MULTILINE,
)

# Same threshold and same argument as check_ladder_bump: a verdict with a token
# reason records that someone typed the magic words, not what they did.
RED_RUN_MIN_REASON_CHARS = 8


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------


def parse_labels(raw: str) -> list[str]:
    """Label names from a JSON array, or a comma/newline separated list.

    GitHub Actions can hand us either shape depending on how the workflow
    interpolates ``github.event.pull_request.labels``; accept both rather than
    silently seeing zero labels (which would pass everything).
    """
    text = (raw or "").strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            loaded = []
        names = []
        for item in loaded:
            if isinstance(item, dict):
                item = item.get("name", "")
            if isinstance(item, str) and item.strip():
                names.append(item.strip())
        return names
    return [part.strip() for part in re.split(r"[,\n]", text) if part.strip()]


def is_documentation(path: str) -> bool:
    """True when the path alone proves the change is prose."""
    p = path.replace("\\", "/").strip()
    if not p:
        return False
    if p in NOT_DOCUMENTATION:
        return False
    if p.startswith(NOT_DOCUMENTATION_PREFIXES):
        return False
    if p.startswith(DOC_PREFIXES):
        return True
    return p.endswith(DOC_SUFFIXES)


def find_red_run(text: str) -> str | None:
    """The RED-RUN declaration in `text`, or None if it carries no usable one."""
    for m in RED_RUN_RE.finditer(text or ""):
        if len(m.group("reason").strip()) >= RED_RUN_MIN_REASON_CHARS:
            return m.group(0).strip()
    return None


# ---------------------------------------------------------------------------
# git plumbing (only used when the caller does not supply the paths)
# ---------------------------------------------------------------------------


def _git(args: list[str], check: bool = True) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=check,
    ).stdout


def changed_paths(base: str, head: str = "HEAD") -> list[str]:
    try:
        _git(["merge-base", base, head])
        spec = [f"{base}...{head}"]
    except subprocess.CalledProcessError:
        # Shallow checkouts often lack the merge base. Two-endpoint diff
        # overcounts but is never silent.
        spec = [base, head]
    out = _git(["diff", "--name-only", *spec])
    if head == "HEAD":
        out += _git(["diff", "--name-only", "HEAD"])
    return sorted({line.strip() for line in out.splitlines() if line.strip()})


# ---------------------------------------------------------------------------
# the gate
# ---------------------------------------------------------------------------


def _bullets(paths: list[str], limit: int = 20) -> str:
    shown = "".join(f"    - {p}\n" for p in paths[:limit])
    if len(paths) > limit:
        shown += f"    ... and {len(paths) - limit} more\n"
    return shown


def run(labels: list[str], paths: list[str], body: str) -> list[str]:
    """Return a list of findings (empty == this PR may claim what it claims)."""
    names = {label.strip().lower() for label in labels}
    guard = GUARD_LABEL in names
    docs = DOCS_LABEL in names
    findings: list[str] = []

    # Rule 1 -- needs:pip beats every class label (but see BLOCKED_FAILS_ALONE:
    # a hold nobody is trying to skip is not this check's business).
    if BLOCKED_LABEL in names and (guard or docs or BLOCKED_FAILS_ALONE):
        claimed = [lb for lb in (GUARD_LABEL, DOCS_LABEL) if lb in names]
        findings.append(
            f"{BLOCKED_LABEL} is present, so this PR is blocked on Pip and nobody else.\n"
            "  A self-merge class does not override it (R1: the ruling names two\n"
            "  classes a seat MAY merge, not a way to clear a hold).\n"
            f"  Claimed class label(s): {', '.join(claimed) or 'none'}\n"
            f"  Fix: remove {BLOCKED_LABEL} once Pip has answered, or drop the class label."
        )

    # Rule 2 -- one class or neither.
    if guard and docs:
        findings.append(
            f"both {GUARD_LABEL} and {DOCS_LABEL} are present. A PR is one class or\n"
            "  neither. The two classes carry different evidence requirements (a guard\n"
            "  owes a RED run; docs owes a docs-only diff), so a PR claiming both has\n"
            "  not said which standard it is asking to be held to.\n"
            "  Fix: remove one label, or split the PR."
        )

    # Rule 3 -- neither class label: this check has no opinion.
    if not guard and not docs:
        if not findings:
            print(
                "[self-merge-eligibility] NEUTRAL: no self-merge class label "
                f"({GUARD_LABEL} / {DOCS_LABEL}) on this PR -- nothing claimed, nothing\n"
                "  to check. Normal review applies and this check does not block."
            )
            if BLOCKED_LABEL in names:
                print(
                    f"  ({BLOCKED_LABEL} is present. That is a hold for a human to lift, "
                    "not a claim\n   for this gate to refuse -- it only fails when a class "
                    "label tries to skip it.)"
                )
        return findings

    # Rule 4 -- docs class: every changed path must be documentation.
    if docs and not guard:
        offenders = [p for p in paths if not is_documentation(p)]
        if not paths:
            findings.append(
                f"{DOCS_LABEL} is claimed but the diff contains no changed paths.\n"
                "  An empty docs PR corrects no documentation. If the paths could not be\n"
                "  computed (shallow clone, missing base ref), fix the checkout rather\n"
                "  than passing this check on no evidence."
            )
        elif offenders:
            findings.append(
                f"{DOCS_LABEL} is claimed, but this PR changes files that are not\n"
                "  documentation. The docs class is 'corrects documentation to match\n"
                "  measured reality' (R1) -- it is not a shortcut for a mixed PR.\n"
                "  Documentation here means: a path under docs/, or a file ending in\n"
                f"  {', '.join(DOC_SUFFIXES)} -- excluding machine-read files such as\n"
                "  version.txt, ladder_version.txt, requirements*.txt, and vendored\n"
                "  trees under godot/addons/.\n"
                "  Not documentation:\n" + _bullets(sorted(offenders)) + "  Fix: split the "
                f"non-doc changes into their own PR, or drop {DOCS_LABEL}."
            )
        else:
            print(
                f"[self-merge-eligibility] {DOCS_LABEL}: all {len(paths)} changed "
                "path(s) are documentation."
            )

    # Rule 5 -- guard class: Section 5g wants a RED run on the record.
    if guard and not docs:
        declared = find_red_run(body)
        if declared is None:
            findings.append(
                f"{GUARD_LABEL} is claimed, but the PR body carries no RED-RUN\n"
                "  declaration. Estate rule Section 5g: a guard merged without a RED run\n"
                "  observed and its run ID recorded is not an installed guard, it is an\n"
                "  untested one. Make the new check fail on purpose, then record the run\n"
                "  that failed.\n"
                "  Add one line to the PR body, exactly this shape:\n"
                f"      {RED_RUN_FORMAT}\n"
                "  Examples:\n"
                "      RED-RUN: https://github.com/OWNER/REPO/actions/runs/1234567890"
                " -- ran with the assertion inverted\n"
                "      RED-RUN: 1234567890 -- guard label with no RED-RUN line in the body\n"
                f"  The reason is mandatory and must be at least {RED_RUN_MIN_REASON_CHARS}"
                " characters: a bare run id\n"
                "  records that a job went red, not that THIS guard is what made it go red."
            )
        else:
            print(f"[self-merge-eligibility] {GUARD_LABEL} declared: {declared}")

    if not findings:
        claimed = GUARD_LABEL if guard else DOCS_LABEL
        print(
            f"[self-merge-eligibility] OK: {claimed} is supported by the evidence in this "
            "PR.\n  Eligible for self-merge on green (R1). Say what you merged where Pip "
            "will see it."
        )
    return findings


# ---------------------------------------------------------------------------
# Self-test: prove the rules without GitHub, on every CI run
# ---------------------------------------------------------------------------

_RED_URL = "https://github.com/PipFoweraker/pdoom1/actions/runs/1234567890"

# (name, labels, paths, body, expected exit, why)
SELF_TEST_CASES = (
    (
        "no class label at all",
        [],
        ["godot/scripts/core/doom_system.gd"],
        "",
        0,
        "MUST PASS: a normal PR is never blocked by this check",
    ),
    (
        "unrelated labels only",
        ["bug", "ship:now"],
        ["godot/scripts/core/doom_system.gd"],
        "",
        0,
        "MUST PASS: only the two class labels mean anything here",
    ),
    (
        "needs:pip alone, no class label",
        ["needs:pip"],
        ["godot/scripts/core/doom_system.gd"],
        "",
        0,
        "MUST PASS: a hold nobody is trying to skip is not this gate's business",
    ),
    (
        "docs class, prose only",
        ["class:docs"],
        ["docs/ROADMAP.md", "CHANGELOG.md", "docs/design/JAM_PRINT_SHEETS_2026-08-05.txt"],
        "",
        0,
        "MUST PASS: every path is documentation",
    ),
    (
        "docs class, one code file smuggled in",
        ["class:docs"],
        ["docs/ROADMAP.md", "godot/scripts/core/doom_system.gd"],
        "",
        1,
        "MUST FAIL: the docs class is not a shortcut for a mixed PR",
    ),
    (
        "docs class touching the ladder epoch SSOT",
        ["class:docs"],
        ["ladder_version.txt"],
        "",
        1,
        "MUST FAIL: .txt suffix, but it forks the leaderboard board key",
    ),
    (
        "guard class with a recorded RED run",
        ["class:guard"],
        [".github/workflows/self-merge-eligibility.yml"],
        f"Adds the gate.\n\nRED-RUN: {_RED_URL} -- label present, no declaration in body\n",
        0,
        "MUST PASS: Section 5g satisfied, run id on the record",
    ),
    (
        "guard class with no declaration",
        ["class:guard"],
        [".github/workflows/self-merge-eligibility.yml"],
        "Adds the gate. Trust me, it works.\n",
        1,
        "MUST FAIL: an unproven guard is an untested one (Section 5g)",
    ),
    (
        "guard class, run id but no reason",
        ["class:guard"],
        [".github/workflows/self-merge-eligibility.yml"],
        "RED-RUN: 1234567890\n",
        1,
        "MUST FAIL: a bare id says a job went red, not that this guard did it",
    ),
    (
        "needs:pip beats the guard class",
        ["class:guard", "needs:pip"],
        [".github/workflows/self-merge-eligibility.yml"],
        f"RED-RUN: {_RED_URL} -- deliberately inverted assertion\n",
        1,
        "MUST FAIL: blocked on Pip, and a class label cannot clear a hold",
    ),
    (
        "needs:pip beats the docs class",
        ["class:docs", "needs:pip"],
        ["docs/ROADMAP.md"],
        "",
        1,
        "MUST FAIL: same rule, other class",
    ),
    (
        "both class labels",
        ["class:guard", "class:docs"],
        ["docs/ROADMAP.md"],
        f"RED-RUN: {_RED_URL} -- deliberately inverted assertion\n",
        1,
        "MUST FAIL: a PR is one class or neither",
    ),
)


def self_test() -> int:
    ran = failed = 0
    for name, labels, paths, body, expected, why in SELF_TEST_CASES:
        print(f"\n[self-test] CASE  {name}\n            {why}")
        findings = run(labels, paths, body)
        for f in findings:
            print(f"[self-merge-eligibility] FAIL: {f}")
        actual = 1 if findings else 0
        ran += 1
        if actual != expected:
            failed += 1
        verdict = "OK" if actual == expected else "MISMATCH"
        print(f"[self-test] {verdict}: expected exit {expected}, got {actual}")

    print(f"\n[self-test] {ran} case(s) ran, {failed} mismatch(es).")
    if failed:
        print("[self-test] FAIL: the gate does not reproduce its own rules.")
        return 1
    print(
        "[self-test] PASS: neutral on unlabelled PRs, red on every unsupported claim, "
        "green on the two supported ones."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-merge class eligibility gate (R1).")
    parser.add_argument("--base", default="origin/main", help="base ref (default: origin/main)")
    parser.add_argument("--head", default="HEAD", help="head ref (default: HEAD)")
    parser.add_argument(
        "--paths-file",
        help="file with one changed path per line (default: compute from git diff)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="replay the rule table hermetically and verify red/green (no GitHub needed)",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    labels = parse_labels(os.environ.get("PR_LABELS", ""))
    body = os.environ.get("PR_BODY", "")
    if args.paths_file:
        text = Path(args.paths_file).read_text(encoding="utf-8")
        paths = [ln.strip() for ln in text.splitlines() if ln.strip()]
    else:
        paths = changed_paths(args.base, args.head)

    print(f"[self-merge-eligibility] labels: {', '.join(labels) if labels else '(none)'}")
    print(f"[self-merge-eligibility] changed paths: {len(paths)}")

    findings = run(labels, paths, body)
    for f in findings:
        print(f"[self-merge-eligibility] FAIL: {f}")
    if not findings:
        return 0
    print(
        "[self-merge-eligibility] Ruling: RULED_2026-08-10_pr-self-merge-and-four-more.md R1. "
        "A label that checks nothing is a claim, not a control."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

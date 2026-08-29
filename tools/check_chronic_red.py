#!/usr/bin/env python3
"""Find workflows that have been red so long nobody reads them any more.

Layer: PROVE

WHY THIS EXISTS (issue #1279, and five days of proof in August 2026)
--------------------------------------------------------------------
A gate that is always red is worse than no gate. It costs the same CI minutes,
occupies the same square in the checks panel, and teaches every reader to skip
it -- so the day it goes red for a REAL reason, that red is indistinguishable
from the noise and nobody looks.

That is not a theory here. `release-ledger.yml` failed on every run from
2026-08-24 to 2026-08-29 because its generator emitted a trailing blank line
that the end-of-file-fixer hook stripped, making its own `--check`
unsatisfiable. On 2026-08-28 it went red for the reason it was BUILT for --
v0.14.4 bumped, tagged, and never published -- and that red looked exactly like
the previous seven. The alarm fired on the day and could not be heard.

`docs-sync.yml` is the same shape and still open as #1279: it fails on
pull_request for a missing `pull-requests: write` permission, which has nothing
to do with documentation sync. #1279 names this tool as the intended remedy and
it did not exist until now.

THE THING A NAIVE VERSION GETS WRONG
------------------------------------
Counting consecutive failures per WORKFLOW misses docs-sync entirely. Measured
2026-08-29: its overall streak is ZERO, because its push-to-main runs pass. It
is its `pull_request` runs that are 39-for-39 red. A workflow can be reliably
green on one trigger and reliably red on another, and the red one is where
reviewers live.

So the unit of measurement is (workflow, event), never the workflow alone.

THREE OUTCOMES, NOT TWO
    0  measured: no undeclared chronic red.
    1  measured: an undeclared chronic red, or a declaration that is now stale.
    2  COULD NOT MEASURE: no `gh`, no token, or the API refused. Not a pass.
       A run that could not ask the question must never answer it -- the lesson
       from scripts/generate_release_metadata.py on the day it was first gated.

USAGE
    python tools/check_chronic_red.py              # report the census
    python tools/check_chronic_red.py --check      # gate: exit 1 on an undeclared one
    python tools/check_chronic_red.py --self-test  # prove it returns BOTH answers

RULING: 2026-08-29 -- a workflow red for three consecutive runs of the same trigger must be fixed or declared, because an undeclared chronic red makes every later red unreadable -- flavour: guard-doctrine -- mechanism: tools/check_chronic_red.py --check in .github/workflows/guards.yml
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict

# How many consecutive failures of the SAME trigger before a red is "chronic".
# Three, not two: two can be one bad change and its revert, which is a normal
# afternoon. Three consecutive means nobody fixed it between two attempts.
STREAK_THRESHOLD = 3

# How many recent runs to consider per workflow. The API returns newest-first;
# this is a per-workflow cap, then split by event.
RUN_WINDOW = 60

# Conclusions that count as a measured outcome. `cancelled`, `skipped` and
# `action_required` are NOT failures and must not extend a streak -- a cancelled
# run measured nothing, and folding it into a red would manufacture chronic-ness
# out of someone hitting the stop button.
FAILING = ("failure", "timed_out", "startup_failure")
MEASURED = FAILING + ("success",)

# DECLARED CHRONIC REDS. Each entry MUST say why it is red and what clears it,
# because an undeclared chronic red is the defect and a silently permitted one is
# the same defect wearing a hat. Keyed by "<workflow file>:<event>".
#
# A declaration whose target is NO LONGER chronic is STALE and fails --check. The
# list only shrinks. That is deliberate: it is the mechanism that stops this file
# becoming the very thing it exists to prevent, a permanent list of permanent reds.
DECLARED = {
    "docs-sync.yml:pull_request": (
        "Issue #1279, open. Fails on the missing `pull-requests: write` permission "
        "needed to post its comment -- a reason unrelated to documentation sync, "
        "which is what makes it the worked example in this file's docstring. The "
        "permissions fix IS present in the workflow (see the `permissions:` block on "
        "the commenting job), but the trigger is narrow -- three .gd files plus "
        "docs/mechanics/** -- so no qualifying PR has run since 2026-08-22 and the "
        "fix is UNVERIFIED rather than confirmed. Clears itself: the first PR "
        "touching those paths either goes green (delete this entry) or does not "
        "(reopen the real bug)."
    ),
    "dev-blog-automation.yml:push": (
        "Dormant and failing since 2026-07-28. Content generation, not a gate: "
        "nothing ships or is blocked by it. Recorded here rather than fixed because "
        "the decision it needs is whether the dev blog is still automated at all "
        "(see docs/DEV_BLOG_DECISION_2026-08-21.md, which archived 49 pygame-era "
        "entries), and that is Pip's call, not a CI repair."
    ),
    "dev-blog-automation.yml:pull_request": (
        "The same workflow and the same pending decision as the push entry above, "
        "listed separately because the unit of measurement here is (workflow, event) "
        "and a declaration that covered a whole workflow would silence a trigger that "
        "might be failing for its own unrelated reason -- which is exactly how "
        "docs-sync.yml stayed invisible."
    ),
    "deploy-dreamhost.yml:push": (
        "Red on every run in the window, newest 2026-06-26 -- over two months "
        "stale, and the longest-standing red in the repository. Deployment, not a "
        "gate. Needs someone to say whether this deploy path is still real before "
        "anyone spends time on the failure itself."
    ),
    "release-ledger.yml:schedule": (
        "Fixed on 2026-08-29 in the change that made its gate satisfiable at all "
        "(the generator emitted a trailing blank line that end-of-file-fixer "
        "stripped, so `--write` then commit could not produce a state `--check` "
        "accepts). Its push and workflow_dispatch runs are green again; the 04:23 "
        "UTC cron has not fired since. Expected to clear on the next scheduled run, "
        "at which point this entry goes stale and --check will say so."
    ),
}


def _gh_json(path: str):
    """GET one API path via `gh`. Raises CouldNotMeasure on any failure.

    Deliberately NOT `--paginate`. That flag concatenates one JSON object per
    page into a single stream, which json.loads cannot read -- it fails with
    "Extra data: line 1 column N". Both endpoints here are explicitly capped
    (per_page on the runs endpoint, and the workflow count is small), so a single
    page is the whole answer and asking for more produces only a parse error.
    """
    try:
        proc = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
        )
    except (OSError, FileNotFoundError) as exc:
        raise CouldNotMeasure("`gh` is not runnable: %s" % exc)
    if proc.returncode != 0:
        raise CouldNotMeasure(
            "gh api %s exited %d: %s" % (path, proc.returncode, proc.stderr.strip()[:300])
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise CouldNotMeasure("gh api %s returned unparseable JSON: %s" % (path, exc))


class CouldNotMeasure(Exception):
    """The question could not be asked. Exit 2, never 0 and never 1."""


def streak_of(conclusions) -> int:
    """Consecutive failures counting back from the newest measured run.

    Non-measured conclusions (cancelled/skipped) are expected to be filtered out
    before this is called; a `success` stops the count.
    """
    n = 0
    for concl in conclusions:
        if concl == "success":
            break
        if concl in FAILING:
            n += 1
        else:
            break
    return n


def census(runs_by_key):
    """[(key, streak, fails, total, newest)] for every (workflow, event) seen."""
    rows = []
    for key, runs in runs_by_key.items():
        conclusions = [c for c, _ in runs]
        rows.append(
            (
                key,
                streak_of(conclusions),
                sum(1 for c in conclusions if c in FAILING),
                len(conclusions),
                runs[0][1] if runs else "-",
            )
        )
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows


def chronic(rows):
    """Rows at or over the streak threshold."""
    return [r for r in rows if r[1] >= STREAK_THRESHOLD]


def undeclared(rows):
    return [r for r in chronic(rows) if r[0] not in DECLARED]


def stale_declarations(rows):
    """Declared keys that are no longer chronic, plus ones that no longer exist.

    A declaration for a workflow/event pair the API never returns is also stale:
    the workflow was deleted or renamed and the entry now excuses nothing.
    """
    chronic_keys = {r[0] for r in chronic(rows)}
    seen_keys = {r[0] for r in rows}
    out = []
    for key in DECLARED:
        if key in chronic_keys:
            continue
        out.append((key, "no longer chronic" if key in seen_keys else "no such workflow/event"))
    return sorted(out)


def collect(window: int = RUN_WINDOW):
    """{"<file>:<event>": [(conclusion, date), ...]} newest-first."""
    data = _gh_json("repos/:owner/:repo/actions/workflows?per_page=100")
    workflows = data.get("workflows", []) if isinstance(data, dict) else []
    if not workflows:
        raise CouldNotMeasure("the workflows endpoint returned none")

    runs_by_key = defaultdict(list)
    for wf in workflows:
        path = wf.get("path", "")
        # dynamic/... entries are GitHub-managed (Copilot, Dependabot graph) and
        # have no file in this repo, so nobody here can fix or declare them.
        if not path.startswith(".github/workflows/"):
            continue
        fname = path.rsplit("/", 1)[-1]
        payload = _gh_json(
            "repos/:owner/:repo/actions/workflows/%s/runs?per_page=%d" % (wf["id"], window)
        )
        for run in payload.get("workflow_runs", []) if isinstance(payload, dict) else []:
            concl = run.get("conclusion")
            if concl not in MEASURED:
                continue
            runs_by_key["%s:%s" % (fname, run.get("event", "?"))].append(
                (concl, str(run.get("created_at", ""))[:10])
            )
    if not runs_by_key:
        raise CouldNotMeasure("no measured runs returned for any workflow")
    return runs_by_key


def render(rows) -> None:
    print("[chronic-red] %d (workflow, event) pair(s) with runs in the window." % len(rows))
    print()
    print("%-6s %-9s %-40s %-16s %s" % ("STREAK", "FAIL/TOT", "WORKFLOW", "EVENT", "NEWEST"))
    for key, streak, fails, total, newest in rows:
        if streak == 0 and fails == 0:
            continue
        fname, _, event = key.partition(":")
        mark = ""
        if streak >= STREAK_THRESHOLD:
            mark = "  DECLARED" if key in DECLARED else "  <== CHRONIC, UNDECLARED"
        print(
            "%-6d %-9s %-40s %-16s %s%s"
            % (streak, "%d/%d" % (fails, total), fname[:40], event[:16], newest, mark)
        )


def self_test() -> int:
    """Prove the classifier returns BOTH answers, on data that cannot vary."""
    ok = True

    def check(label, cond, detail=""):
        nonlocal ok
        if cond:
            print("  [ok] %s" % label)
        else:
            ok = False
            print("SELF-TEST FAIL: %s %s" % (label, detail))

    check("a clean history has streak 0", streak_of(["success"] * 5) == 0)
    check("three reds in a row is a streak of 3", streak_of(["failure"] * 3) == 3)
    check(
        "a success STOPS the count, even with reds behind it",
        streak_of(["success", "failure", "failure", "failure"]) == 0,
    )
    check(
        "a timeout counts as red -- it is a run that did not pass",
        streak_of(["timed_out", "failure"]) == 2,
    )
    check(
        "a CANCELLED run does not extend a streak (nobody measured anything)",
        streak_of(["cancelled", "failure", "failure"]) == 0,
        "a stop button must not manufacture chronic-ness",
    )

    # The docs-sync shape: green on one trigger, red on another. This is the case
    # a per-WORKFLOW counter misses, and the reason the key carries the event.
    mixed = {
        "docs-sync.yml:push": [("success", "2026-08-22")] * 4,
        "docs-sync.yml:pull_request": [("failure", "2026-08-22")] * 39,
    }
    rows = census(mixed)
    by_key = {r[0]: r for r in rows}
    check(
        "a workflow green on push and red on pull_request is caught on the PR half",
        by_key["docs-sync.yml:push"][1] == 0 and by_key["docs-sync.yml:pull_request"][1] == 39,
    )
    check(
        "and the PR half alone is chronic",
        [r[0] for r in chronic(rows)] == ["docs-sync.yml:pull_request"],
    )
    check(
        "a DECLARED chronic red does not fail the gate",
        undeclared(rows) == [],
        "docs-sync.yml:pull_request is in DECLARED",
    )

    fake = {"invented-workflow.yml:push": [("failure", "2026-08-29")] * 5}
    fake_rows = census(fake)
    check(
        "an UNDECLARED chronic red DOES fail the gate",
        len(undeclared(fake_rows)) == 1,
    )
    check(
        "a two-run red is NOT chronic (one change and its revert is an afternoon)",
        chronic(census({"x.yml:push": [("failure", "2026-08-29")] * 2})) == [],
    )

    # Stale declarations, in both flavours.
    healthy = {k: [("success", "2026-08-29")] * 4 for k in DECLARED}
    check(
        "a declaration whose target went green is reported STALE",
        len(stale_declarations(census(healthy))) == len(DECLARED),
    )
    check(
        "a declaration naming a workflow the API never returns is also STALE",
        any(reason == "no such workflow/event" for _, reason in stale_declarations(census(fake))),
    )
    check(
        "every DECLARED entry carries a non-trivial reason",
        all(isinstance(v, str) and len(v) > 60 for v in DECLARED.values()),
    )

    print("SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--check", action="store_true", help="exit 1 on an undeclared chronic red")
    ap.add_argument("--self-test", action="store_true", help="prove it returns BOTH answers")
    ap.add_argument("--window", type=int, default=RUN_WINDOW, help="runs to consider per workflow")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    try:
        runs_by_key = collect(args.window)
    except CouldNotMeasure as exc:
        print("[chronic-red] DID NOT COMPLETE -- %s" % exc)
        print("  This run establishes nothing. It is NOT evidence that no workflow")
        print("  is chronically red. `gh auth status` locally; in CI the job needs")
        print("  GH_TOKEN and `actions: read`.")
        return 2

    rows = census(runs_by_key)
    render(rows)

    bad = undeclared(rows)
    stale = stale_declarations(rows)

    if chronic(rows):
        print()
        print(
            "[chronic-red] %d chronic pair(s); %d declared, %d not."
            % (len(chronic(rows)), len(chronic(rows)) - len(bad), len(bad))
        )

    if not args.check:
        return 0

    rc = 0
    if bad:
        print()
        print("[chronic-red] FAIL: %d chronic red(s) with no declaration." % len(bad))
        print("  A red that has stood for %d runs of the same trigger is not a" % STREAK_THRESHOLD)
        print("  signal any more -- it is furniture, and it hides the next real one.")
        print("  Fix it, or add an entry to DECLARED in this file saying why it")
        print("  stands and what clears it.")
        for key, streak, fails, total, newest in bad:
            print("    %-48s streak %d, %d/%d, newest %s" % (key, streak, fails, total, newest))
        rc = 1
    if stale:
        print()
        print("[chronic-red] FAIL: %d stale declaration(s)." % len(stale))
        print("  These are no longer chronic. Delete the entry: this list only shrinks,")
        print("  which is what stops it becoming a permanent register of permanent reds.")
        for key, reason in stale:
            print("    %-48s %s" % (key, reason))
        rc = 1
    if rc == 0:
        print()
        print("[chronic-red] OK: every chronic red is declared, and every declaration bites.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

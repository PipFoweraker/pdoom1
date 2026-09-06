# The six soft-failed guards, actually run -- 2026-09-07

The coordination seat's estate sweep found **six sites in pdoom1** where a guard's failure
cannot fail anything (`|| true`, `|| echo`, `continue-on-error`). It deliberately stopped
at "nobody knows whether any of these are currently red" and asked for exit codes.

Here are the exit codes. **Measured on `pdoom1 @ origin/main`, verified `0 0` against
origin before running.**

The six sites reduce to **four distinct commands** -- `enforce_standards --check-all` and
`ci_health_integration --gate-check` each appear in two workflows.

| # | command | sites | exit | verdict |
|---|---|---|---|---|
| G1 | `validate_historical_data.py --verbose` | `data-validation.yml:59` | **0** | GREEN, and **hollow** -- see below |
| G2 | `enforce_standards.py --check-all` | `enhanced-cicd-pipeline.yml:155`, `quality-checks.yml:62` | **0** | GREEN. 0 errors, 5 warnings |
| G3 | `ci_health_integration.py --gate-check` | `enhanced-cicd-pipeline.yml:222`, `quality-checks.yml:261` | **1** | **RED**, and partly self-inflicted |
| G4 | `generate_mechanics_docs.py --check` | `docs-sync.yml:54` | **0** | GREEN, and **a false positive in the census** |

---

## G4 is not a swallowed guard. It is the conditional-step idiom.

`docs-sync.yml:54` carries `continue-on-error: true`, and the very next step is:

    - name: Update mechanics docs if out of sync
      if: steps.check_sync.outcome == 'failure'

**The `continue-on-error` exists so the workflow can branch on the outcome.** Without it
the job aborts and the auto-regeneration step never runs. That is the documented GitHub
Actions pattern for "check, and if it fails, fix it", not a guard switched off.

So pdoom1's real count of swallowed guards is **five sites / three commands**, not six.
Flagged so the estate census does not carry a number that overstates this repo.

## G3 is red -- and one of its two blockers is caused by the gate itself

    [DATA] Current Health Score: 30/100      Required Minimum: 60/100
    [URGENT] GATE BLOCKERS (2):
       - Excessive linting issues: 156804
       - Dirty working tree - uncommitted changes

**The second blocker is self-inflicted.** `scripts/health_tracker.py:43` creates
`project_health_history.db` in the project root, that path is **not gitignored** (verified:
`git check-ignore` returns nothing), and `ci_health_integration.py:215` then blocks on
`working_tree_clean == False`.

So the gate creates an untracked file and then fails because there is an untracked file.
Measured: the working tree was clean immediately before the run, and the only untracked
file afterwards was the database the run had just created. **In CI this fires every time**,
because CI starts from a clean clone.

**Fix is one line** -- add `project_health_history.db` to `.gitignore`. Not done here; this
document is a measurement, and the repo has a standing rule that a guard's behaviour change
is a decision rather than a tidy-up.

**The first blocker is real but almost certainly legacy-scoped.** The threshold is
`linting_issues > 100` (`ci_health_integration.py:204`) and the measured value is 156,804 --
1,568x the threshold. The workflow's own swallow message says why: *"non-blocking during
migration - linting issues in legacy Python files"*. So this gate was soft-failed
deliberately and with a stated reason.

**That is a defensible advisory setting.** What is not defensible, and is the actual
finding: **nobody recorded a date or a condition for revisiting it**, so "advisory during
the migration" has outlived any way of telling whether the migration is over.

## G1 is the interesting one: green, and it checks almost nothing

`validate_historical_data.py --verbose` exits 0 and prints:

    [SUCCESS] All historical data validated successfully
       Files checked: 3

Three files. And the run's own output shows what happened to them:

    Skipping shared\data\historical_timeline (not found)
      [OK] 2017.json
    Skipping shared\data\researchers (not found)
    Skipping non-researcher file personas.json (no top-level 'researchers' key)
      [OK] personas.json
    Skipping non-researcher file quirks.json (no top-level 'researchers' key)
      [OK] quirks.json
    Skipping shared\data\organizations (not found)
    Skipping godot\data\organizations (not found)

**Two of the three "checked" files were explicitly SKIPPED and then counted as OK.** The
third, `2017.json`, is the only file in `godot/data/historical_timeline/`.

**It never touches `historical_events.json`.** `grep -n "historical_events" scripts/validate_historical_data.py`
returns **nothing**. That is the 1,194-record file this week established carries 1,194
unmarked fabricated `safety_researcher_reaction` values and 1,194 unmarked `media_reaction`
values, with `reaction_provenance` appearing zero times.

It also probes four `shared/data/*` and `godot/data/organizations` paths that do not exist
-- the pre-Godot layout -- and reports each as a yellow "Skipping ... (not found)" rather
than as a failure.

**So the `|| true` on this one is not hiding a red. It is hiding that the check is
hollow**, which is the same shape as issue #640, where CI reported green while running zero
tests. A guard that passes by finding nothing to check is worse than one that fails,
because it produces positive evidence of correctness that nobody has to argue with.

**This one deserves the coordination seat's framing turned around:** the premise of their
note was that "the validator for `historical_events.json` cannot fail the run". The truer
and worse statement is that **there is no validator for `historical_events.json` at all.**

## G2 is genuinely green, with one warning worth naming

0 errors, 5 warnings, 1,015 TODO/FIXME comments counted. One warning reads:

    Unicode content can be auto-fixed with intelligent ASCII converter

**Do not act on that suggestion yet.** PR #1345 establishes that
`scripts/intelligent_ascii_converter.py` on `main` has a bare `"""` as a replacement value
at lines 106-111, so line 106 opens a triple-quoted string that swallows line 107: three of
six quote keys never existed and three mapped to literal comment text. It corrupts files it
is run against with `--apply`. A green guard currently recommends running a broken tool.

## What was measured, and what was not

**Measured:** the four exit codes above, on this machine, against origin state, with the
tree verified clean beforehand and restored afterwards (the run created
`project_health_history.db`; it was removed).

**NOT MEASURED:**
- Whether G3's 156,804 lint count is dominated by `archive/legacy-pygame/`. The workflow
  message asserts it; nobody has re-derived it.
- Whether these exit codes match what the same commands produce **in CI**, where the
  environment differs. G3's dirty-tree blocker is the one most likely to behave
  differently, and the reasoning above says it fires there too, but that is an inference
  from a clean clone, not an observation of one.
- The nine soft-fail sites in `pdoom1-website`. Different repo, different seat.

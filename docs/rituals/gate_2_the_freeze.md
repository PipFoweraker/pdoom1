# [Gate 2: THE FREEZE]

**When:** Wednesday PM, after the workshop blocks. Legacy name: G1.

Main freezes for mechanics. After the freeze only pack content, art, docs,
and bugfixes labelled league-critical may merge. `ladder_version.txt` is
final for the league at this line.

---

## Entry criteria

- [Gate 1: LAST POUR] PASSED, with its snapshot on disk.
- The fast gate is green on the head of `main` that is about to be frozen.
- The Commissioner is present. Nobody else can speak this gate.

## Mechanical checks

```
git fetch origin main && git rev-parse origin/main    # the frozen commit
python tools/sync_version.py --check                  # version + ladder agree
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
python tools/check_ladder_bump.py --base <last-league-tag>   # advisory
cat ladder_version.txt version.txt
```

| # | Check | Mechanical or judgement | Runnable now? |
|---|---|---|---|
| 1 | Frozen commit SHA recorded in the day-log | mechanical | yes |
| 2 | `sync_version.py --check` exits 0 | mechanical | yes |
| 3 | Fast gate green on that SHA (>= 300 tests collected) | mechanical | yes |
| 4 | `ladder_version.txt` value declared final and written down | judgement, recorded | yes |
| 5 | `check_ladder_bump.py` warnings reviewed and acked | judgement over a mechanical smell detector | yes |

Check 1 is new and matters more than it looks. Playbook v0 says "freeze
announced in the day-log", which records *that* a freeze happened but not
*what* was frozen. Without a SHA, "no new law crossed this line" has no
line. Every later gate should be able to name its base commit.

Check 5 is judgement over a smell detector: `check_ladder_bump.py` is not a
proof (its own docstring says so). Acking a warning is a legitimate outcome;
ignoring one silently is not -- and since #1178 that second half is machine-
enforced. CI runs the checker with `--strict` and WITHOUT `|| true`, so an
unacked warning now fails the PR; the ack is a `ladder-ack: <reason>` line in
the PR body (or the `ladder-ack` label). At this gate, run it without `--strict`
and record the ack in the day-log as before.

## The incantation

> *"Main is frozen at <SHA>. The ladder stands at L<N> and every copy of it
> agrees. The tests were counted, not assumed. No new law crosses this
> line. What is merged is the month. What is parked is the next."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "Main is frozen at <SHA>" | check 1 -- `git rev-parse origin/main` | mechanical |
| "the ladder stands at L<N>" | check 4 -- `ladder_version.txt` | mechanical read, declared final by judgement |
| "every copy of it agrees" | check 2 -- `sync_version.py --check` exit 0 | mechanical |
| "The tests were counted, not assumed" | check 3 -- the runner parses JUnit XML and enforces the floor (#640) | mechanical |
| "No new law crosses this line" | nothing -- a promise about the future | declaration |
| "What is merged is the month. What is parked is the next." | [Gate 1]'s snapshot | mechanical, inherited |

Two additions and one honesty note.

Added "Main is frozen at <SHA>": gives the freeze an actual line.

Added "the tests were counted, not assumed": this is the ceremony's answer
to the project's dominant failure mode, silent wrongness that looks right.
CI once reported green while running ZERO tests (#640, cold class cache ->
`quit(0)`). The runner now ignores GUT's exit code and hard-fails on a
below-floor count. Saying it out loud is cheap and names the exact thing
the project learned to distrust.

Left alone: *"No new law crosses this line. What is merged is the month.
What is parked is the next."* Nothing about it needs repair. It is the
best-scanning line in the ceremony and, like [Gate 1]'s closer, it is a
declaration -- it does not assert a fact that could be false, it creates an
obligation. It is listed above with "backed by: nothing" and that is
correct, not a defect.

## PENDING VOTE (#1025) -- do not adopt before the Council rules

The known ordering flaw: this gate can precede [Gate 4: PROVEN BUILD], so
the freeze can be spoken over content no human has ever launched. That is
exactly what happened 2026-07-29: the freeze was declared 22:28, and about
fifteen minutes earlier a launch had produced a full UI with no game state
(#1023).

Worth being precise about the blame: **no [Gate 2] line was untrue.** Every
check passed, because [Gate 2]'s checks are about the ladder and the merge
line, not about whether the thing runs. The gate did its job; the question
for the Council is whether its job is the right job.

Options on the ballot, stated without preference:

1. **Leave it.** The freeze is about law, not function; [Gate 4] is the
   functional gate.
2. **Add a smoke check here.** One extra line, e.g. *"and the thing
   launches"*, satisfied by running from source -- no build required.
3. **Reorder** so a proven build precedes the freeze. Cleanest in
   principle; pushes build work earlier into the week.
4. **Split [Gate 4]** into a cheap boots-check early plus the full proven
   artifact playtest where it now sits.

If option 2 or 4 carries, the candidate clause and its check are:

```
godot --path godot                # launch, start a run, observe turn 1 live
```
> *"...and the thing launches: a run exists, not a screen that resembles
> one."*

The wording is deliberate. `main.tscn` and `watch_screen.tscn` shipped
hardcoded placeholder text -- `Game not started...`, `Phase: Not Started`,
`58.5%`, `Turn 1` -- so a dead UI and a live game were visually identical.
A smoke check phrased as "the game looks fine" would have passed on the
corpse.

## When a line is FALSE

- **`sync_version.py --check` fails.** Hard stop, and the highest-severity
  failure at this gate. A silent version/ladder drift forks the board key.
  Fix, re-run, re-verify, then speak. Never freeze over a drift.
- **Fast gate red or below floor.** Do not freeze. A red fast gate at the
  freeze means the month's ruleset is unknown, not merely buggy.
- **`check_ladder_bump.py` warns.** Not a stop. Read the warning against
  the fork rule in `RELEASE_NOMENCLATURE.md`: *could two identical runs,
  played the same way, produce a different score, trajectory or RNG stream
  across this change?* YES -> bump minor + ladder before freezing. NO ->
  ack in the day-log with the reason and continue.
- **Something league-critical lands after the freeze.** This is legal and
  expected -- it is the escape hatch the freeze was designed with, and it
  fired this week (#1039, four presentation bugs; #1051, the resign path).
  What is NOT optional: the frozen SHA in the day-log is superseded, so
  record the new one, and [Gate 4] must be re-run from scratch on a re-cut.
  A league-critical merge invalidates any existing proven build. See
  `gate_4_proven_build.md`.

## Not verifiable from here

- **"No mechanics PR may merge past this line"** is a rule about the
  future, not a check. Nothing in the repository enforces it; only the
  Commissioner's discipline and the label convention do. Owner: the
  Commissioner. A branch-protection rule could make it mechanical; nobody
  has built one, and this sheet does not propose one unasked.

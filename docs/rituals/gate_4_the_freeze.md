# [Gate 4: THE FREEZE]

**When:** after [Gate 3: SEED BLESSING], before [Gate 5: PROVEN BUILD].
Legacy name: G1. Numbered Gate 2 (Wednesday PM, before the pack and the seed)
before the 2026-10-26 reorder (#1025).

The release branch is cut. `release/v0.X` is created from the epoch commit on
`main` (or, for a point release, the existing `release/v0.X` head is frozen),
per `RELEASING.md`. From this line the release branch takes only cherry-picked
fixes that meet the hotpatch criteria in `RELEASING.md`; `main` keeps moving
and is next month's. `ladder_version.txt` is final for the league at this line.
And before the line is spoken, the thing launches.

Ruled 2026-10-26 (#1025, `docs/rulings/DECISIONS_2026-10-26_return.md`
item 6): *"The Freeze (= the release-branch cut, plus a windowed check that a
run actually starts)"*. The gates run *decide, lock, prove, open*; this is the
lock.

---

## Entry criteria

- [Gate 1: LAST POUR] PASSED, with its snapshot on disk.
- [Gate 2: PACK BLESSED] spoken on one of its branches; [Gate 3: SEED
  BLESSING] PASSED, with its blessed seed and `L<N>` written down.
- The fast gate is green on the commit that is about to be cut.
- The Commissioner is present. Nobody else can speak this gate.

## Mechanical checks

```
git fetch origin --tags
git switch --detach <epoch-commit>                    # the commit about to be cut
python tools/check_class_cache.py --repair            # pre-flight FIRST, ~30ms
godot --path godot                                    # WINDOWED: start a run, observe turn 1 live
python tools/sync_version.py --check                  # version + ladder agree
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
python tools/check_ladder_bump.py --base <last-league-tag>   # advisory
cat ladder_version.txt version.txt
git switch -c release/v0.X <epoch-commit>             # RELEASING.md, command 1
git push origin release/v0.X                          # CI: godot-tests + guards run on it
git rev-parse origin/release/v0.X                     # the frozen commit
git grep -n "FEATURED_SEED_OVERRIDE: String" origin/release/v0.X -- godot/autoload/game_config.gd
```

For a point release on a live line, skip the `switch -c` / `push` pair: the
frozen commit is the existing `origin/release/v0.X` head, and every other
check runs against it. Use `python3` on Linux. Only Pip pushes tags; agents
may prepare and push the branch (`RELEASING.md`).

| # | Check | Mechanical or judgement | Runnable now? |
|---|---|---|---|
| 1 | Release branch cut and pushed; frozen SHA (`origin/release/v0.X`) recorded in the day-log | mechanical | yes |
| 2 | `sync_version.py --check` exits 0 | mechanical | yes |
| 3 | Fast gate green on that SHA (>= 300 tests collected) | mechanical | yes |
| 4 | `ladder_version.txt` value declared final, written down, and equal to the `L<N>` spoken at [Gate 3] | judgement, recorded; equality mechanical | yes |
| 5 | `check_ladder_bump.py` warnings reviewed and acked | judgement over a mechanical smell detector | yes |
| 6 | `FEATURED_SEED_OVERRIDE` on the release branch equals the seed blessed at [Gate 3] | mechanical (`git grep` on the remote ref) | yes |
| 7 | **The thing launches:** class-cache pre-flight, then a WINDOWED launch from source at the frozen commit, a run started, turn 1 observed live | mechanical pre-flight + human observation | yes |

Check 1 matters more than it looks. Playbook v0 said "freeze announced in the
day-log", which records *that* a freeze happened but not *what* was frozen.
Without a SHA, "no new law crosses this line" has no line. Every later gate
should be able to name its base commit. Under the release-branch model the
SHA is the head of a branch that exists on origin, which is also what the
release workflow's preflight later checks a tag against (RB003/RB004).

Check 4's equality half is new on 2026-10-26: the seed and ladder are now
blessed BEFORE the freeze, so a poured mechanics PR that bumped the ladder in
between would make the board key spoken at [Gate 3] wrong.

Check 5 is advisory by design: `check_ladder_bump.py` is a smell detector,
not a proof (its own docstring says so). Acking a warning is a legitimate
outcome; ignoring one silently is not.

Check 6 is the branch-level repeat of [Gate 3]'s seed check. [Gate 3] proved
the const was merged on the line about to be cut; this proves the cut carries
it. [Gate 5]'s check 9 proves the built artifact does.

### Check 7: the boot check (adopted 2026-10-26, #1025)

Why it exists: under the old order the freeze could be spoken over content no
human had ever launched. That is exactly what happened 2026-07-29: the freeze
was declared 22:28, and about fifteen minutes earlier a launch had produced a
full UI with no game state (#1023). No freeze line was untrue that night --
every check was about the ladder and the merge line, not about whether the
thing runs. The Council's answer is that the lock includes "it starts".

Three details are load-bearing:

1. **The wording.** *"...and the thing launches: a run exists, not a screen
   that resembles one."* `main.tscn` and `watch_screen.tscn` shipped hardcoded
   placeholder text -- `Game not started...`, `Phase: Not Started`, `58.5%`,
   `Turn 1` -- so a dead UI and a live game were visually identical. A check
   phrased as "the game looks fine" would have passed on the corpse. Observe
   something only a live run produces: an action taken, a turn advanced.
2. **Class-cache pre-flight first** (`tools/check_class_cache.py --repair`,
   per `CLAUDE.md`). A stale class cache produces the same "UI but no game"
   picture (2026-08-13); without the pre-flight the check can fail for a
   reason that has nothing to do with what is being frozen -- or, after a
   repair nobody noticed was needed, pass for one.
3. **Windowed, not headless.** #1023's suspected mechanism was a
   windowed-only `_ready()` abort that headless runs cannot see, and
   `godot --headless --quit` exits 0 through a whole parse-error cascade.

This is a from-source boot, not a playtest of the artifact. The artifact is
[Gate 5]'s job, and it is still the gate that catches presentation bugs.

## The incantation

> *"release/v0.X is cut at <SHA>. The ladder stands at L<N> and every copy of
> it agrees. The branch carries the seed we blessed. The tests were counted,
> not assumed. And the thing launches: a run exists, not a screen that
> resembles one. No new law crosses this line. What is merged is the month.
> What is parked is the next."*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "release/v0.X is cut at <SHA>" | check 1 -- `git rev-parse origin/release/v0.X` | mechanical |
| "the ladder stands at L<N>" | check 4 -- `ladder_version.txt`, equal to [Gate 3]'s | mechanical read, declared final by judgement |
| "every copy of it agrees" | check 2 -- `sync_version.py --check` exit 0 | mechanical |
| "The branch carries the seed we blessed" | check 6 -- the const on the remote branch | mechanical |
| "The tests were counted, not assumed" | check 3 -- the runner parses JUnit XML and enforces the floor (#640) | mechanical |
| "And the thing launches: a run exists, not a screen that resembles one" | check 7 -- pre-flight, windowed launch, live turn observed | human observation over a mechanical pre-flight |
| "No new law crosses this line" | nothing -- a promise about the future | declaration |
| "What is merged is the month. What is parked is the next." | [Gate 1]'s snapshot | mechanical, inherited |

Changed 2026-10-26: "Main is frozen at <SHA>" became "release/v0.X is cut at
<SHA>" (`main` no longer freezes; the release branch is the frozen line), and
two clauses were added with their checks -- the seed clause (check 6) and the
boot clause (check 7), the latter adopted from the PENDING VOTE box this sheet
carried until the ruling.

Earlier additions (2026-07-31): the SHA clause, which gives the freeze an
actual line, and "the tests were counted, not assumed" -- the ceremony's
answer to the project's dominant failure mode, silent wrongness that looks
right. CI once reported green while running ZERO tests (#640, cold class
cache -> `quit(0)`). The runner now ignores GUT's exit code and hard-fails on
a below-floor count.

Left alone: *"No new law crosses this line. What is merged is the month.
What is parked is the next."* Nothing about it needs repair. It is the
best-scanning line in the ceremony and, like [Gate 1]'s closer, it is a
declaration -- it does not assert a fact that could be false, it creates an
obligation. It is listed above with "backed by: nothing" and that is
correct, not a defect.

## When a line is FALSE

- **`sync_version.py --check` fails.** Hard stop, and the highest-severity
  failure at this gate. A silent version/ladder drift forks the board key.
  Fix on `main`, re-run, re-verify, then cut. Never freeze over a drift.
- **Fast gate red or below floor.** Do not cut. A red fast gate at the
  freeze means the month's ruleset is unknown, not merely buggy.
- **The ladder differs from the `L<N>` spoken at [Gate 3].** Do not cut on
  a board key nobody blessed. Re-bless at [Gate 3] with the real value, then
  return here.
- **The const on the branch is not the blessed seed.** Same rule: do not
  cut, or if the branch is already pushed, do not speak. Fix on `main`, then
  cut from the fixed commit (or cherry-pick to the live line), and re-check.
- **`check_ladder_bump.py` warns.** Not a stop. Read the warning against
  the fork rule in `RELEASE_NOMENCLATURE.md`: *could two identical runs,
  played the same way, produce a different score, trajectory or RNG stream
  across this change?* YES -> bump minor + ladder before freezing (which
  sends you back to [Gate 3], because the board key changes). NO -> ack in
  the day-log with the reason and continue.
- **The boot check fails (check 7).** Do not speak the gate. First confirm the
  pre-flight actually ran; if it reported a repair, launch again. If a run
  still does not exist, it is a crash / blocking-UX bug (hotpatch criteria 1
  and 3 in `RELEASING.md`): fix on `main`, then cut from the fixed commit or,
  if `release/v0.X` is already pushed, cherry-pick the fix to it, record the
  new head SHA, and re-run check 7 on it. If the cause cannot be found, record
  what you could not rule out and let the Commissioner rule -- #1023 stayed
  honestly open after five clean launches, and an honest open issue beats a
  confabulated all-clear.
- **Something league-critical lands after the freeze.** This is legal and
  expected -- it is the escape hatch the freeze was designed with, and it
  fired on the first run (#1039, four presentation bugs; #1051, the resign
  path). Under the release-branch model it lands on `main` first and is
  cherry-picked to `release/v0.X` (`git cherry-pick -x`, `RELEASING.md`
  command 2). What is NOT optional: the frozen SHA in the day-log is
  superseded, so record the new branch head, and [Gate 5] must be re-run from
  scratch on a re-cut. A league-critical merge invalidates any existing proven
  build. See `gate_5_proven_build.md`.

## Not verifiable from here

- **"Only hotpatch-criteria fixes reach the release branch"** is a rule
  about the future, and the criteria are judgement. The release workflow's
  preflight enforces the branch SHAPE (tag on the branch, version agreement,
  `RELEASING.md` "What is ENFORCED"); nothing enforces which fixes may be
  cherry-picked. Owner: the Commissioner.
- **The boot check proves one machine, one driver, from source.** It does
  not prove the exported artifact runs anywhere. Owner: [Gate 5].

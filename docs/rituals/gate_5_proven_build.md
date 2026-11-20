# [Gate 5: PROVEN BUILD]

**When:** after [Gate 4: THE FREEZE]; re-cut as often as anything lands on the
release branch after it. Legacy: G3. Numbered Gate 4 before the 2026-10-26
reorder (#1025).

The release artifact exists, proves it is fresh, and a human has played it.

---

## The evidence that this gate is the ceremony's best one

Recorded here rather than in a retro, because it is the strongest argument
in the ceremony's favour and it should be read at the gate.

Playing the built 0.13.2 artifact on 2026-07-30 found **four league-critical
bugs, none of which any test could see** (#1039):

1. The action queue was an `HBoxContainer` -- one unbounded row. Twenty
   queued actions marched off screen and pushed the interface out of view.
2. The leaderboard header declared 5 columns; the rows built 6. An
   undeclared baseline column shifted every heading rightward, so the `-`
   placeholder appeared under "Duration" and read as blank. **One missing
   header, two reported symptoms.**
3. The settings menu taught `[F8]` for bug reports; `keybind_manager.gd`
   says `KEY_N`. Worse: all three shipped platform notes said F8 too --
   every downloader on every platform had a dead key for the one action
   that feeds bugs back.
4. `Game not started...` was the permanent first line of every player's
   feed, because `log_message()` appends. It survived because
   `_render_feed()` clears it, so anyone who touched a filter watched it
   vanish and never knew.

Fast gate at the time: 995 tests, 0 failures, 96/96 files collected.
**Honest green, and blind to all four.** The suite is headless; these are
presentation-layer. Green means "nothing else broke", not "these work".

The gate earned its line. Do not weaken it to save an hour.

## Re-cutting is the expected path, not an exception

A build was cut, then **re-cut twice on the same day**. That is normal and
the sheet is written for it. The rule (#1039):

> Not a patch on top of the existing build -- two builds reporting the same
> ladder epoch while playing differently is a lie nothing can detect.

`sync_version.py --check` cannot catch it: it verifies file-to-const
agreement, not that the shipped bits match the ruleset the epoch claims.
The freshness marker proves the pack matches the tree at cut time, not that
the tree is the one you blessed. **Re-cut is the only mechanical answer.**

So: number your cuts. Cut 1, cut 2, cut 3. Every cut kills the one before,
and the playtest does not inherit across cuts -- a re-cut restarts this
gate at check 1, including the human playtest, at least for the surface the
change touched.

---

## Entry criteria

- [Gate 4: THE FREEZE] PASSED, and the frozen SHA (or its superseding
  league-critical SHA) is recorded. The cut is built from the head of
  `release/v0.X`, never from `main` (`RELEASING.md`).
- [Gate 2: PACK BLESSED] spoken on one of its two branches, and
  [Gate 3: SEED BLESSING] PASSED with its seed written down.
- Working tree clean; no agent is touching it. **No agent touches the
  working tree while a human is building from it** -- read-only or
  `isolation: "worktree"`. This rule was bought on 2026-07-30, when an
  agent proving a test could fail edited `main_ui.gd` in the live checkout
  mid-playtest and made a whole window of bisect results meaningless.
  "Do not commit" was never isolation.

## Mechanical checks

```
git fetch origin && git switch --detach origin/release/v0.X
python tools/sync_version.py --check
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
python tools/build_release.py                  # NEVER a raw godot --export
grep -n "^## " CHANGELOG.md | head -3          # heading carries the literal version
git rev-parse HEAD                             # the cut's base SHA -- record it
git rev-parse origin/release/v0.X              # ...and it must equal this
grep -n "FEATURED_SEED_OVERRIDE: String" godot/autoload/game_config.gd   # the seed inside the cut
```

| # | Check | Kind | Runnable now? |
|---|---|---|---|
| 1 | `build_release.py` exits 0 having PROVEN its marker in the .pck | mechanical | yes |
| 2 | `sync_version.py --check` exits 0 | mechanical | yes |
| 3 | Fast gate green, count above floor | mechanical | yes |
| 4 | Changelog heading carries the literal version string | mechanical (grep) | yes |
| 5 | Human playtest of the BUILT artifact, incl. soft-lock sweep | judgement, irreducible | yes |
| 6 | Cut number and base SHA written down | mechanical | yes |
| 7 | Release-URL verification | mechanical | **NO -- see below** |
| 8 | **The machine that proved it is a clean machine** | mechanical | yes |
| 9 | The seed inside the cut is the seed blessed at [Gate 3] | mechanical (const at the cut's base SHA vs the blessed seed) | yes |

Check 6 now also asserts the base SHA IS the release-branch head: a cut from
any other commit is a build of something nobody froze.

Check 9 moved here from [Gate 3: SEED BLESSING] on 2026-10-26 (it was that
sheet's check 3, "that const value is the one inside the blessed cut"). Once
the seed is blessed before the freeze, there is no cut at blessing time; this
is the first moment the question "will players post to the seed we spoke?" can
be answered about the artifact rather than about a branch. [Gate 4] check 6
asked it of the branch; this asks it of the cut. A re-cut re-asks it.

**Proving runs now play the blessed seed.** Under the old order the seed was
rolled after this gate, so proving runs landed on a board the league never
opened on. Now the build carries the league seed, so a proving run that is
submitted globally lands on the league board before it opens. Keep global
submission off on the proving machine (decline the consent prompt after
`reset_player_state.py`); [Gate 6]'s empty-board attestation (check 7) is
the backstop, and a board that is not empty there is a decision for the
Commissioner, not a cleanup task.

RULING: 2026-10-29 -- global score submission stays OFF on the machine used to prove a release build, because proving runs now play the league seed before the board opens -- flavour: league-integrity -- mechanism: docs/rituals/gate_6_board_opens.md check 7 (empty-board attestation)

Check 8 was added 2026-07-31, and the reason is specific rather than
hygienic.

Pip's local config carried `scenario_id="crisis"` for an unknown length of
time. Two consequences, and neither announced itself. A 14-minute recorded
playtest, taken and treated as a playtest of the league build, was actually a
playtest of Crisis Mode -- doom starting at 65, year 2020, a configuration no
league player would ever run. And four endgame tests went red on that machine
while staying green in CI, because the `GameConfig` autoload reads the real
user config and the tests had never pinned what they needed.

Check 5 -- the human playtest -- is the irreducible one on this sheet. Check 8
exists because check 5 is only worth what the machine under it is worth. A
human playing a configuration nobody else will play has proven nothing about
the artifact, and has proven it *convincingly*, which is worse than proving
nothing at all.

```
python tools/reset_player_state.py            # dry run: what would be cleared
python tools/reset_player_state.py --apply    # backs up, does not delete
```

Run it BEFORE check 5, never after. Then confirm by eye, on the pre-game
screen: Scenario reads **Standard Game**, difficulty reads **Standard and is
disabled**, and the board for this seed is **empty**.

On check 1: `build_release.py` nukes `godot/.godot`, plants a uniquely
named marker file, exports, and verifies the marker's filename survives in
the pack file table. It anchors on a FILENAME because GDScript is packed as
binary-tokenized `.gdc` and string literals do not survive as grep-able
text. A missing marker exits non-zero and loud. Its own docstring states
the limit: a clean verified pack proves the right bits shipped, **not that
the game runs on a real GPU**. Check 5 is the render gate.

Check 5's minimum sweep, from what actually broke: queue several actions
and confirm they wrap; check the leaderboard columns line up; press the
bug-report key the settings menu advertises and confirm something happens;
pause, use "Accept Your Fate", and confirm you land on the score screen and
can reach the leaderboard (#1051 -- that transition is the one that
segfaulted v0.11.0 and only reproduces in a real build).

### Check 7 was moved off this gate

Playbook v0 put "release URL verification green (the #998 fail-loud check:
every advertised door answers 200)" at this gate. **It is not runnable
here.** The tag does not exist yet, the GitHub Release object does not
exist, and the assets are not uploaded -- so either the check runs against
last release's URLs (proving nothing about this build) or it fails for the
correct reason and gets waved through, which trains the ceremony to wave
things through.

It moves to [Gate 6: BOARD OPENS], after the tag and assets exist, where
`python scripts/verify_release_urls.py --file public/releases/vX.Y.Z.json`
is a real check with a real answer. This is a direct application of the
sheet rule: a check that can only run later belongs to a later gate.

## The incantation

> *"This is cut <k>, from <SHA>; every earlier cut is dead. The build is
> fresh and proves it. The version speaks with one voice. The seed inside it
> is the seed we blessed. A human has
> played the thing we ship, not the thing we meant -- **and the machine that
> proved it is a clean machine.**"*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "This is cut <k>, from <SHA>" | check 6 | mechanical |
| "every earlier cut is dead" | declaration -- the re-cut discipline (#1039) | declaration |
| "The build is fresh and proves it" | check 1 -- the marker verification | mechanical |
| "The version speaks with one voice" | checks 2 and 4 | mechanical |
| "The seed inside it is the seed we blessed" | check 9 -- the const at the cut's base SHA | mechanical |
| "A human has played the thing we ship, not the thing we meant" | check 5 | human judgement, no substitute |
| "and the machine that proved it is a clean machine" | check 8 -- `reset_player_state.py`, then confirmed by eye | mechanical |

Changed 2026-10-26: added *"The seed inside it is the seed we blessed"*, the
clause [Gate 3] spoke as *"and it is inside the build we cut"* before the
reorder, moved here with its check.

Changed earlier: added the cut sentence. Everything else is playbook v0 verbatim.

Left alone, deliberately: all three original sentences. They are the
best-calibrated lines in the ceremony -- each maps to exactly one check,
none overclaims, and the third one caught four bugs on its first outing.
"The thing we ship, not the thing we meant" is doing real work: the
distinction between the artifact and the intention is precisely what
`test_game_start_actionable.gd` got wrong when it asserted the thing that
broke, and passed, because it instantiates `main.tscn` directly while the
player arrives via welcome -> config -> transition.

Removed: nothing from the spoken text. The release-URL clause was never in
the incantation, only in the checks; it moves to [Gate 6].

## When a line is FALSE

- **Marker missing / `build_release.py` non-zero.** Never ship. Do not
  retry the export alone -- the tool already nuked the cache, so a repeat
  failure is a real problem, not a flake. Investigate before re-cutting.
- **`sync_version.py --check` fails.** Fix, re-run, and **re-cut**. A
  version fix changes what should be inside the pack, so the existing pack
  is stale by definition.
- **Fast gate red.** Do not cut. Fix first; a cut from a red tree cannot be
  blessed, only re-cut later at the same cost.
- **The playtest finds a bug.** This is the expected outcome, not the
  exception. Triage against the freeze rules:
  - league-critical -> fix on `main`, cherry-pick to `release/v0.X` past
    the freeze (legal; `RELEASING.md` command 2), record the new base SHA,
    **re-cut**, and re-run check 5 over at least the surface the
    change touched. This is what happened for #1039 and #1051.
  - not league-critical -> file it, label it `ship:hotpatch-48h` or
    `ship:next-release`, and continue. Pip's ruling on where the line sits:
    *"they're all massively player experience changing. Violating the UI's
    consistency is critical."*
- **The seed inside the cut is not the blessed seed (check 9).** You do not
  have a proven build of the league. Do not bless a different seed to match.
  Fix the const on `main`, cherry-pick it to `release/v0.X`, re-check
  [Gate 4] check 6 on the new head, and **re-cut**. This is the exact "two
  builds, same epoch, different play" lie that nothing downstream can detect.
- **The playtest finds something unexplained.** Not automatically a stop.
  #1023 -- the boot ghost -- was left open, honestly unexplained, after
  five clean launches across three bisect paths. Record the mechanism you
  could not rule out (there, a windowed-only `_ready()` abort no headless
  test can see) and let the Commissioner rule. An honest open issue beats a
  confabulated all-clear.
- **You are out of time.** Slipping the league opening beats blessing an
  unplayed build. Ceremony production value is on the sacrificial list;
  this gate is explicitly not.

## Not verifiable from here

- **GPU / real-renderer behaviour** beyond what the Commissioner's own
  machine shows. One machine, one driver, one resolution. Layout bugs of
  the #1039 kind are invisible to headless tests and only partly visible to
  one human at one window size. Owner: the Commissioner, plus the
  playtester friend when available.
- **Anything about the tag, the Release object, or download URLs.** None of
  it exists yet. Owner: [Gate 6].

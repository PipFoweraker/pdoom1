# [Gate 4: PROVEN BUILD]

**When:** Thursday. Re-cut Friday if anything landed after. Legacy: G3.

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

- [Gate 2: THE FREEZE] PASSED, and the frozen SHA (or its superseding
  league-critical SHA) is recorded.
- [Gate 3: PACK BLESSED] spoken on one of its two branches.
- Working tree clean; no agent is touching it. **No agent touches the
  working tree while a human is building from it** -- read-only or
  `isolation: "worktree"`. This rule was bought on 2026-07-30, when an
  agent proving a test could fail edited `main_ui.gd` in the live checkout
  mid-playtest and made a whole window of bisect results meaningless.
  "Do not commit" was never isolation.

## Mechanical checks

```
python tools/sync_version.py --check
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
python tools/build_release.py                  # NEVER a raw godot --export
grep -n "^## " CHANGELOG.md | head -3          # heading carries the literal version
git rev-parse HEAD                             # the cut's base SHA -- record it
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
> fresh and proves it. The version speaks with one voice. A human has
> played the thing we ship, not the thing we meant -- **and the machine that
> proved it is a clean machine.**"*

## Per-line provenance

| Clause | Backed by | Kind |
|---|---|---|
| "This is cut <k>, from <SHA>" | check 6 | mechanical |
| "every earlier cut is dead" | declaration -- the re-cut discipline (#1039) | declaration |
| "The build is fresh and proves it" | check 1 -- the marker verification | mechanical |
| "The version speaks with one voice" | checks 2 and 4 | mechanical |
| "A human has played the thing we ship, not the thing we meant" | check 5 | human judgement, no substitute |
| "and the machine that proved it is a clean machine" | check 8 -- `reset_player_state.py`, then confirmed by eye | mechanical |

Changed: added the cut sentence. Everything else is playbook v0 verbatim.

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
  - league-critical -> fix, merge past the freeze (legal), record the new
    base SHA, **re-cut**, and re-run check 5 over at least the surface the
    change touched. This is what happened for #1039 and #1051.
  - not league-critical -> file it, label it `ship:hotpatch-48h` or
    `ship:next-release`, and continue. Pip's ruling on where the line sits:
    *"they're all massively player experience changing. Violating the UI's
    consistency is critical."*
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

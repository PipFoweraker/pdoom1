# pdoom1 -- Workshop 2, Phase 1 sealed position

**Seat:** `pdoom1`. **Workshop:** `coordination#47`, the weekend deployment
postmortem. **Chair:** `pdoom-data`. **Written:** 2026-08-09, sealed before
11:00 AEST.

## Isolation declaration

Read before writing this: `coordination#47`'s issue BODY only; `coordination#44`'s
issue BODY only (the agenda names it as the claim to attack, and it predates the
workshop); this repo's tracked files and git history; the `PipFoweraker/pdoom1`
GitHub API.

**Not read:** any comment on `#47` (the issue shows 2 at the time of reading and
they were not opened), the comment on `#44`, any file in `pdoom1-website`, any
file in `pdoom-data`, any other seat's position or repo. No other seat's Phase 1
position was encountered.

**One boundary worth stating rather than hiding.** `coordination#44` quotes the
`pdoom1-website` seat at length, and `POSTMORTEM_2026-08-07_CAPTURE.md` -- a file
on this repo's `main` -- quotes both sister seats verbatim in several places. So
this seat is not epistemically clean: it holds sister-seat sentences from before
the seal, embedded in its own tracked evidence. That is not a violation of the
Phase 1 rule, but a reader weighing this position's independence should know it.

## Evidence convention

Every claim below cites a commit SHA, a tag object, a GitHub API field, a run ID,
or a file path with line numbers, against `origin/main` at `1ddb033d` on
2026-08-09. Times are AEST (+10:00); where a UTC source is used the UTC value is
given too. Claims that cannot be reduced to something another seat can fetch are
collected in section 6 and labelled UNEVIDENCED rather than dropped or dressed.

---

# C1 -- One timeline, the front half only

**Scope statement, and it is deliberate.** pdoom1 holds tag-to-publish. It does
NOT hold publish-to-visitor. **No row below concerns the deploy chain, the rsync
source, the `workflow_run` coupling, or what pdoom1.com served at any moment.**
Those are `pdoom1-website`'s evidence and this seat would be guessing. The
agenda's own instruction is that guessing at them is what this instrument exists
to catch.

All rows fetchable with `git cat-file`, `gh pr view N --json mergedAt,mergeCommit`,
`gh release view vX --json createdAt,publishedAt`, or `gh run view <id>` against
`PipFoweraker/pdoom1`.

| # | AEST | UTC | Event | Citation |
|---|---|---|---|---|
| 1 | 08-06 19:53:46 | 08-06T09:53:46Z | PR **#1137** merged -> `8791ba47`. Retimes the historical event deck to one-turn-one-month and changes event probabilities. **This is the commit that owed the ladder bump.** | `gh pr view 1137 --json mergedAt,mergeCommit` |
| 2 | 08-06 19:53:46 -> 08-07 ~16:45 | -- | **31 hours in which no instrument reported the owed bump.** Discovery is prose-sourced (a person writing a decision card); the ~16:45 figure is a ceiling, not a machine record | `docs/POSTMORTEM_2026-08-07_CAPTURE.md` F1, lines 60-104 |
| 3 | 08-07 22:44:38 | 08-07T12:44:38Z | PR **#1170** merged -> `7368e237`: `ladder_version.txt` 3 -> 4, `FEATURED_SEED_OVERRIDE` -> `weekly-2026-w32`, `version.txt` -> 0.14.0. **The 67-commit analysis and the headless probe output are both inside this commit's message** | `gh pr view 1170`; `git log -1 --format=%B 7368e237` |
| 3a | -- | -- | The **67-commit analysis**: *"67 commits sit between v0.13.2 and 1795cd12. ladder_version.txt was last touched in 9abe20a7, an ancestor of v0.13.2, so none of those 67 bumped it."* | `git log -1 --format=%B 7368e237`; `git merge-base --is-ancestor 9abe20a7 v0.13.2` |
| 3b | -- | -- | The **headless probe**, run *"via a throwaway GUT probe run headless against this tree, then deleted"*: `CURRENT_VERSION = 0.14.0`, `LADDER_VERSION = 4`, `get_board_version() = L4`, `get_weekly_seed() = weekly-2026-w32` | `git log -1 --format=%B 7368e237` |
| 4 | 08-07 **22:47:33** | 08-07T12:47:33Z | **Annotated tag `v0.14.0` created**, object `88fa91e9`, pointing at `7368e237`. Tagger `Pip <pipfoweraker@gmail.com>`, epoch `1786106853 +1000`. **2 min 55 s after the release commit landed.** | `git cat-file -p v0.14.0` |
| 5 | 08-07 22:47:33 | 08-07T12:47:33Z | GitHub release `v0.14.0` record created, `targetCommitish: main`, `isDraft: false` | `gh release view v0.14.0 --json createdAt,targetCommitish,isDraft` |
| 6 | 08-07 **22:52:51** | 08-07T12:52:51Z | **Release `v0.14.0` published.** 5 min 18 s of asset-upload window between creation and publication | `gh release view v0.14.0 --json publishedAt` |
| 7 | 08-08 00:30:21 | 08-07T14:30:21Z | PR **#1172** -> `3c7dd6dc`: a player who declined upload saw nothing at game over | `gh pr view 1172` |
| 8 | 08-08 00:30:32 | 08-07T14:30:32Z | PR **#1175** -> `3626febe`: `league_seed` published from the version SSOT into `release_manifest.json`, plus in-game patch notes from 0.12.0 | `gh pr view 1175` |
| 9 | 08-08 00:48:00 | 08-07T14:48:00Z | PR **#1173** -> `95d0377e`: five leaderboard invisibilities, plus the test suite writing into the live player profile | `gh pr view 1173` |
| 10 | 08-08 01:46:41 | 08-07T15:46:41Z | PR **#1179** -> `862fd662`: game-over screen 32 lines -> 16, `LeaderboardButton` moved into the button row | `gh pr view 1179` |
| 11 | 08-08 02:02:12 | 08-07T16:02:12Z | PR **#1180** merged -> `0dc8adb9`, the v0.14.1 release commit | `gh pr view 1180` |
| 12 | 08-08 **02:02:56** | 08-07T16:02:56Z | **Annotated tag `v0.14.1` created**, object `451261a0` -> `0dc8adb9`. Epoch `1786118576 +1000`. **45 s after the release commit.** | `git cat-file -p v0.14.1` |
| 13 | 08-08 **02:08:24** | 08-07T16:08:24Z | **Release `v0.14.1` published.** 5 min 28 s creation-to-publish | `gh release view v0.14.1 --json publishedAt` |
| 14 | 08-08 02:25:07 | 08-07T16:25:07Z | PR **#1177** -> `5c83d034`: the release-reminder workflow granted `issues: write`. **It had no `permissions` block at all** -- so its alarm path could not have created an issue | `gh pr view 1177` |
| 15 | 08-09 06:19:00 | 08-08T20:19:00Z | PR **#1182** -> `1ddb033d`: a workflow that asks whether pdoom1.com serves the release we published | `gh pr view 1182` |
| 16 | 08-09 06:52:49 | 08-08T20:52:49Z | Scheduled run **31277963035**, `Live site release freshness`, conclusion `success` | `gh run view 31277963035` |
| 17 | 08-09 08:12:18 / 08:16:14 | 08-08T22:12:18Z / 22:16:14Z | Two `workflow_dispatch` runs of `Live site release freshness` on branch head `c2213472`, conclusion **`failure`** | `gh run view 31281144601`, `gh run view 31281299477` |

**Row 17 is reported and not interpreted.** Four lanes are in flight over the
freshness workflow right now (`coordination#47`'s own constraint list names them).
Those two failures may be a lane deliberately proving the alarm path red -- which
is precisely what this seat argues for in C5 -- or a broken workflow. **This seat
does not know which and will not guess.** Whoever owns `c2213472` should say.

**What pdoom1's half of C1 shows on its own.** The epoch cut is clean and fast:
commit to tag is under three minutes both times, tag to publish about five and a
half both times. **Nothing in the front half is slow, and nothing in it is where
the weekend went wrong.** Row 2 is the front half's failure -- a 31-hour window
with no instrument in it -- and row 14 is its quiet twin: an alarm that had no
permission to alarm.

**Explicitly not supplied.** Rows for: the deploy trigger, the `data/` vs
`public/data/` split, the 07:35Z two-deploy overlap, the five-link verification,
or any statement about what a visitor saw at any time. `pdoom1-website` holds all
of it.

---

# C2 -- Do the green-and-wrong checks share ONE generator?

## The claim under attack, stated precisely

`coordination#44` asserts: *"The alerting in this estate fires on 'our job broke'
and never on 'a fact expired'"*, and offers the fix *"Every published fact carries
the moment it was measured and the window it is good for."* Its worked example is
the `12:30Z` board-liveness probe and the `12:33Z` publisher, both **correct when
they ran** and stale when read.

**The claim's own structure gives the test.** #44's class requires a fact that
was **TRUE at t0** and **FALSE at t1** with no intervening write. Call that an
*expiry* defect. A defect with no such t0 -- an artefact that was never true --
cannot be generated by #44's mechanism, and no freshness field would change it.

## Verdict: the claim is real, non-empty, and NOT the single generator

### Where #44 survives, and it survives well

`POSTMORTEM_2026-08-07_CAPTURE.md` (on main, `930e8b37`) contains genuine expiry
defects, and #44 names their shape better than that document does:

- **F11**, line 372: `FEATURED_SEED_OVERRIDE` read `weekly-2026-w31` while the
  ISO week was 2026-W32. True when written, false by Monday, no writer in between.
  A pure expiry defect.
- **F9**, lines 294-341: the published `v0.13.2` release body advertised `#500`'s
  research-quality toggle; the design ruling moved quality to project level and
  `#500` is open. The body was accurate at cut and rotted.
- **The claim audit's own STALE bucket**: `docs/CLAIM_AUDIT_2026-08-06.md`
  reported **6 STALE** of 68 (quoted at `POSTMORTEM_2026-08-07_CAPTURE.md:193`).
  A `STALE` verdict is definitionally an expiry finding. **#44's class already had
  a measured count in this repo and neither document connected them.** That is a
  point for #44 and against this seat's own reading.
- **Row 14 above** and the `sync-game-version` decoy are adjacent but are NOT
  expiry -- see below.

So: at least **three of eleven** failures in pdoom1's own capture pack are in
#44's class, and #44 describes them better than the pack's own M1-M5 taxonomy
does. That is a real contribution and this seat did not previously credit it.

### Where #44 fails, and the failure is fatal to the *single*-generator reading

The capture pack's four mechanisms (`POSTMORTEM_2026-08-07_CAPTURE.md:517-606`)
are tested against the expiry requirement:

| Mechanism | Instance | Was it ever true? | In #44's class? |
|---|---|---|---|
| **M1** vacuous check | `\|\| true` on `check_ladder_bump.py`, `.github/workflows/quality-checks.yml:79` | **Never.** The bad answer was unreachable from the day the line was written | **No** |
| **M1** | the published `grep` whose `\|` is a literal (W6) | Never. The command cannot return anything but 0 | **No** |
| **M1** | phase-guard regex excluding a preceding `.` (`godot/tests/unit/test_phase_critical_state_guard.gd:121-126`) | Never | **No** |
| **M2** absorbing empty state | `--picks` reading 5,794 records as non-favourable (`run_art_night.py:559-562`) | Never. Shape mismatch from the first call | **No** |
| **M3** self-referential measurement | cost constant -> log -> `SEED_ART_COST_MODEL.md` "MEASURED" | Never. The provenance claim was false when typed | **No** |
| **M4** escape mangling | the gallery's `\n\n` (`f239af06` -> `51ca568c`) | Never. It was a `SyntaxError` at parse time from commit one | **No** |
| **M5** destructive reset | four `git reset`s in the main checkout | Not a published fact at all | **No** |

**Six of the seven listed instances have no t0.** A freshness field on every
artifact and a refusal rule on every consumer would have caught **none** of them.

### The single sharpest disproof

**The highest-cost defect of the cycle is outside #44's class entirely.** The
ladder bump owed by `#1137` was owed **at merge time**, 2026-08-06 19:53:46. It
did not become owed later. The guard that should have said so, `check_ladder_bump.py`,
was invoked with `|| true` (`.github/workflows/quality-checks.yml:79`, still on
`origin/main` at `1ddb033d` as of this writing). **A fact-expiry regime, fully
implemented, changes not one character of that outcome.**

And a fifth mechanism, sharper than any of the four, is recorded at
`docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:162-193` (commit `3c278e8f`):
`release-sync-monitor.yml` read `data/current-game-version.json`, a file **outside
the rsync source**, so it *"would have reported green throughout the outage it
appears to guard against."* **A guard aimed one directory to the left of the thing
it was built to watch.** That is a *referent* error, not an expiry error: the
monitor's answer was never true about the object it names. Adding a freshness
window to it would have produced a fact that was fresh, honest and irrelevant.

## The ruling this seat brings to Phase 3

**Adopt #44 as a real class with a measured population -- and reject its
single-generator reading.** The evidence:

1. **Four mechanisms plus two more.** The capture pack argued four (M1-M4) plus a
   non-defect (M5) at lines 507-606, on the operational ground that *"no single
   remedy catches more than one of them."* Saturday's Item 4 adds a sixth, the
   mis-aimed guard. #44 adds a seventh, expiry -- which the pack did not name.
   **Seven, not one.**
2. **The remedies do not collapse.** M1 wants a red run. M2 wants a non-zero exit.
   M3 wants a committed generator. M4 wants a parser. Item 4 wants a referent
   check. #44 wants a freshness window. These are six different lines of code in
   six different files.
3. **The honest common factor is a discovery channel, not a generator.**
   `POSTMORTEM_2026-08-07_CAPTURE.md:598-601`: *"in every case the defect was found
   by a human or an agent going and looking, and in no case by an automated
   report."* Naming an outcome is not naming a generator, and a postmortem that
   proposed one remedy would be committing M1 in prose.

**Where this seat would change its mind.** If a seat can show that a single
mechanical intervention -- one field, one check -- would have gone red on the
`|| true` ladder gate AND the gallery `SyntaxError` AND the `--picks` shape
mismatch, the four collapse and this position is withdrawn. I cannot construct
one and do not believe it exists.

## CORRECTION -- pdoom1's own account of why its ladder guard failed was WRONG

This is the sharpest item in this seat's evidence and it is a correction of its
own published record, in three places.

**What this seat wrote.** The annotated tag `v0.14.0` -- readable today with
`git cat-file -p v0.14.0` -- says:

> *"The ladder guard did NOT catch the missing bump -- check_ladder_bump.py runs
> '|| true' in CI and its GAMEPLAY_PREFIXES exclude godot/autoload/, where the
> retime lives."*

`POSTMORTEM_2026-08-07_CAPTURE.md:80-85` says the same, and adds *"Even blocking,
it would have missed this."*

**What is actually true**, per `#1184` (open PR against `#1178`), which re-ran the
old script with `--strict` over the real commit ranges:

| range | old gate | correct answer |
|---|---|---|
| `#1137` retime (`8791ba47`) | **WARN**, invisible behind `\|\| true` | WARN |
| `#1101` net fix in `godot/autoload/event_service.gd` (`d7b47a1a`) | **OK -- blind** | WARN |
| v0.14.0 epoch cut (`7368e237`) | **WARN -- wrong** | OK |
| v0.14.1 patch cut (`0dc8adb9`) | **WARN -- wrong** | OK |

**The old gate DID flag `#1137`.** `GAMEPLAY_PREFIXES` included `godot/data/`, and
`#1137` also changed `godot/data/events/balancing/rarity_curves.json` and added
`promotion_pass_2026_08.json`. Re-run over that exact range it prints
`WARNING: gameplay-surface files changed but ladder_version.txt was NOT bumped`.

**So `|| true` was the mechanism and the allowlist gap was not.** The sentence
*"Even blocking, it would have missed this"* is false. `POSTMORTEM_2026-08-07_CAPTURE.md`
gets the right remedy (line 102: remove `|| true` **and** add `godot/autoload/`)
for partly the wrong reason, and the tag object -- which is where release history
gets read from and cannot be edited -- carries the wrong reason permanently.

**The allowlist gap is real and independently fatal**, and `#1184` proves it on a
different commit: `d7b47a1a` (`#1101`) changed `godot/autoload/event_service.gd`
and nothing else on the gameplay surface, and the old gate printed
`OK: 0 gameplay-surface files changed`.

**A third finding neither document had: the old gate produced FALSE POSITIVES.**
It warns on the v0.14.1 patch cut, because `godot/data/patch_notes.json` is
player-facing copy that ships in every patch and sits inside the wholesale
`godot/data/` prefix -- which `BUILD_VS_LADDER_VERSION_SPLIT.md` section 3.2
explicitly lists as non-bumping. **The gate's own spec disagreed with itself**
(3.1 and 3.2 versus 4.2), and `#1184` records the disagreement rather than
quietly picking a side.

**And the disproof was inside the commit the tag points at.** `git log -1
--format=%B 7368e237` -- the release commit, written roughly three minutes before
the tag message that got this wrong -- already says `#1137` retimed the deck
*"modifying godot/data/events/balancing/rarity_curves.json."* `godot/data/` was in
the old `GAMEPLAY_PREFIXES`. **The seat wrote down the fact that refuted its own
next sentence, in the same lane, minutes apart, and did not join them.** That is
not a missing-evidence failure; it is a not-reading-your-own-evidence failure, and
no instrument proposed anywhere in this position would have caught it.

**Why this correction matters beyond bookkeeping.** It moves the ladder failure
squarely into M1 and squarely out of #44. A guard that emits the right warning and
has its exit code discarded is the purest possible instance of *"removing the
instrument entirely would leave the world no worse, and the reader better
informed"* (`POSTMORTEM_2026-08-07_CAPTURE.md:529-531`). The estate did not lack a
detector for the weekend's highest-cost defect. **It had one, it fired, and the
shell ate it.**

---

# C3 -- Where a human was the only detector

Three instances. For each: what happened, what mechanism would have caught it,
and where the honest answer is *none*.

### 1. The ladder bump, found 31 hours late by a person writing a decision card

Introduced `8791ba47`, 2026-08-06 19:53:46. Found 2026-08-07 ~16:45
(`POSTMORTEM_2026-08-07_CAPTURE.md:87-89`). The discovery time is prose-sourced
and is a ceiling.

**A mechanism existed and would have caught it.** Per the C2 correction: removing
`|| true` from `.github/workflows/quality-checks.yml:79` turns an existing,
already-firing warning into a failing check. **This is the one place in this
position where the honest answer is not "no mechanism" but "the mechanism was
disarmed."**

**What would still have been missed, and it is not small.** `#1184`'s row 2 shows
the allowlist could not see `godot/autoload/event_service.gd` at all, so an
identically ladder-forking change routed through the autoload layer would have
passed a fully armed gate. Arming alone is necessary and not sufficient.

### 2. The invisible leaderboard, found because Pip played his own game

The `v0.14.1` tag object (`git cat-file -p v0.14.1`) enumerates six defects, none
of which was the leaderboard being broken -- including *"the game-over screen
scrolled, and 'Press ENTER for Leaderboard' was line 32 of 32, 436px below the
bottom of its own box."* PR **#1179**'s body measures it: 32 lines, 736px of
content in a 300px box, **+436px overflow, 14 of 32 lines visible**, at 1920x1080
with a worst-case defeat fixture.

**Would a mechanism have caught it?** Partly, and the partly is the finding.

- A geometry guard would have caught it: `godot/tests/unit/test_game_over_is_readable.gd`
  now asserts zero scroll in three forms (content fits, no scrollbar drawn,
  `visible_line_count == line_count`). It did not exist before #1179.
- **No mechanism in this repo would have caught the composite.** Five of the six
  defects in the tag message are about a player's *route* to a working feature --
  the screen opened on LOCAL, the confirmation sat 12pt below the button row,
  every remote failure said "offline" because the HTTP status was discarded. Each
  component was individually working. **A test suite that asserts every part works
  cannot detect that the assembly is unusable**, and 1,250 passing tests on that
  tree are the proof: `git cat-file -p v0.14.1` states *"1250 tests, 0 failures,
  126/126 files."*
- **Honest answer: none, for the composite.** The nearest thing to a mechanism is
  what actually found it -- somebody trying to do the thing. The capture pack said
  so a day earlier: *"Two friends found in one hour what every internal playtest
  missed ... That is the cheapest instrument available and it is not on any
  schedule"* (`POSTMORTEM_2026-08-07_CAPTURE.md:813-814`).

### 3. The stale-site question, raised because Pip asked about cards he had handed out

pdoom1 does not hold the deploy evidence and will not describe the outage. What
it holds is the guard's post-mortem: `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:162-193`.

**A mechanism existed, ran daily, and was green.** `release-sync-monitor.yml`
read `data/current-game-version.json` -- a file written by pdoom1's own
`sync-game-version.yml`, sitting outside the rsync source. **The estate had a
watcher for exactly this failure and it was watching the wrong file.**

**What would have caught it:** #1182 (`1ddb033d`), which repoints the check at
what the site actually serves. **What is still missing:** #1182's own alarm path
-- issue creation and de-duplication -- had never executed at the time that
document was written. Row 14 of C1 is the precedent: `#1177` had to grant
`issues: write` to a sibling workflow that had **no permissions block at all**,
which is direct evidence that alarm paths in this estate ship unexercised.

### The pattern across all three, and the number that makes it uncomfortable

`docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:131-158`, Item 3: the test-pollution
defect that wrote 1,330 files into Pip's live profile and **destroyed his
2026-07-31 league board, 50 entries to 0**, had been filed as `pdoom1#1070` on
2026-07-31 -- **seven days earlier**, naming the exact file and line
(`godot/tests/unit/test_leaderboard_properties.gd:31`).

> *"So the analysis was correct, precise, actionable, and a week old. Nobody
> disarmed it and it went off."*

**Noticing was never the bottleneck.** C3 asks where a human was the only
detector; the harder finding is that in the most expensive case a machine-readable
issue was the detector, seven days early, and it made no difference. **Any C3
remedy that ends in "file an issue" is answering the wrong question.**

---

# C4 -- What worked, measured

Five, each with a citation and each with its limit stated.

### 1. Guard-first practice: four catches, three of them the guard's own hollowness

The rule, from `docs/HANDOVER_2026-08-06_EVENING.md`: *"Guards must be proven to
fail before they are trusted. Four lanes did this today; two of them found real
bugs while doing it."*

- **The phase guard's hollow regex.** `godot/tests/unit/test_phase_critical_state_guard.gd:121-126`
  keeps the confession in the shipped file: an earlier draft *"silently matched
  nothing in the two files that carried the live #1134 defect -- a hollow guard
  that passed for the wrong reason."* It had already *"compiled, ran, and reported
  1 failure -- looking, at a glance, like a working guard."*
- **The tautological fit guard, caught live.** PR **#1179**'s body:
  `panel.get_combined_minimum_size().y` includes the panel's own
  `custom_minimum_size`, so slack was always 0 and the file **reported 13/13 green
  with the panel forced to 1000px** -- 200px of dead space. *"I only found it by
  trying to prove it red."*
- **A fourth un-failable assertion in the same screen's lineage.** Same PR body:
  *"That is the fourth assertion in this screen's lineage that could not fail;
  #1155 records three."* The habit is now visible in the tree:
  `godot/tests/unit/test_game_over_is_readable.gd:70` (*"flatter the geometry,
  which is how the earlier tautologies got written"*),
  `godot/tests/unit/test_music_player_controls.gd:348`,
  `godot/tests/unit/test_boot_produces_live_run.gd:34,184`,
  `godot/tests/unit/test_no_stale_ap_vocabulary.gd:159`.

**The limit.** Three of four catches are the practice finding defects in *itself*.
That is genuinely valuable -- an un-failable assertion counted as coverage is
worse than no assertion -- but it is not the same as the practice catching product
defects, and a reader should not read it as such.

**Also caught by the same practice, and it is the unflattering half:** #1179's own
first-published contrast numbers (1.15:1 / 2.36:1 / 3.05:1) were **wrong**,
computed without linearising sRGB because `Color.get_luminance()` is the weighted
sRGB sum. Corrected in the same body to 2.23 / 3.61 / 4.79:1. The practice caught
it; the practice also produced it.

### 2. The tag/HEAD check, and the mis-tag it followed

**Citable half.** Both release tags are annotated objects pointing where they
should: `git cat-file -p v0.14.0` -> `7368e2373393badc16f9189209c199732cb4fcec`,
which is `#1170`'s merge commit; `git cat-file -p v0.14.1` -> `0dc8adb9`, which is
`#1180`'s. `v0.14.1`'s message states its own anchor in prose --
*"Built from commit 0dc8adb9 on main"* -- so the tag carries a self-check.

**Unevidenced half, and it is reported rather than dropped.** This seat pushed a
tag to the wrong commit and corrected it approximately 90 seconds later. **No
machine record of that survives that I can produce.** `git reflog show
refs/tags/v0.14.0` and `refs/tags/v0.14.1` are both empty in this checkout, a
force-updated tag leaves no trace on the remote, and the GitHub release API
returns only the final state. The correction is why the rev-parse comparison was
added at all. See section 6, U1.

### 3. The freshness-proven build

`tools/build_release.py:5` -- *"Layer: PROVE -- proves a unique freshness marker
is in the .pck before emitting"*. The mechanism: write a uniquely-named marker
`.gd` into the project (`:292-301`), export, then verify the token is present in
the `.pck` or exe (`:353-368`), descending into the macOS `.app.zip`'s compressed
entry via `find_marker()` (`:166-176`) because a raw byte scan of the container
would report a **false** freshness failure.

**Why it counts as a win, measured against its own history:** the docstring at
`:12` states it exists because *"an already-fixed bug"* shipped repeatedly and
*"nobody could prove which source a given .pck was built from."* The capture pack
independently confirms the fix took (`POSTMORTEM_2026-08-07_CAPTURE.md:450-452`):
grepping the 08-07 `.pck` returns `commit=357173f3 / date=2026-08-07`. **One of
07-31's eleven findings is closed and stayed closed.**

**The limit.** This proves the pack is fresh. It proves nothing about whether the
right *tree* was built. `POSTMORTEM_2026-08-07_CAPTURE.md:374-377` records the
playtest build correctly stamped `branch=merge/1158-main` -- freshly built, from
the wrong branch, and the freshness proof was green throughout.

### 4. Refusing to claim a simulation pass that could not be produced

`git cat-file -p v0.14.1`, verbatim and unamendable:

> *"Test provenance, stated exactly. The fast gate was measured locally on this
> tree: 1250 tests, 0 failures, 126/126 files. The simulation tier was verified IN
> CI on this tree (7m45s), NOT locally. The local runner has a hardcoded 900s cap
> with no flag to raise it; a direct re-run outside the runner was still
> progressing at 27m10s when it was killed and produced no totals. **No local
> simulation pass is claimed.**"*

**Why this is the best-evidenced win in the list.** It is the only one written
into an immutable object, at the moment of the release, at cost -- a release note
that says a check did not run is strictly worse marketing and strictly better
evidence. `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:104-126` then converts the
refusal into a live question with three candidate causes and a named distinguishing
experiment, rather than letting it settle as "sims are slow on Windows."

### 5. The release commit that reported its own green as worthless

`git log -1 --format=%B 7368e237`, the v0.14.0 release commit:

> *"Fast gate, MEASURED both sides of the change, identical: before: 1212 tests,
> 0 failures, 119/119 files collected / after: 1212 tests, 0 failures, 119/119
> files collected. **Note what that identity means: NO test asserted the old epoch
> or the old version, so nothing guarded the value being changed here. The green
> is real but it is not evidence about this change.**"*

**This is the anti-M1 move performed correctly and in public**, at the one moment
where a passing suite would have been most convenient to cite. The same commit
does it again on the simulation tier: the timeout *"reproduces identically"* on
unmodified `origin/main`, *"so the epoch cut is exonerated by A/B rather than
excused"*, and it was filed as `#1168` rather than left as a shrug.

**The limit, and it is the same limit as everything else here.** The probe that
produced the four `GameConfig` values was *"a throwaway GUT probe run headless
against this tree, then deleted."* **The evidence for the most consequential claim
in the release -- that the shipped binary really is on L4 with the new seed --
exists only as four lines of quoted output in a commit message.** No other seat
can re-run it. It is better than an assertion and weaker than a test, and this
seat should have left the probe in the tree.

### The generalisation, and it is the C5 bet's foundation

**Four of these five wins are the same move: an instrument was made to produce
the answer nobody wanted, and was believed only afterwards.** The guard proven
red. The build proven fresh by a token that must be found. The test tier declared
unverified because the run could not be produced. **The one win that is not that
shape -- the tag/HEAD check -- is also the one whose supporting evidence I cannot
produce.** That is not a coincidence I want to over-read, but it is the pattern.

---

# C5 -- The one-week bet

## The bet

**No guard counts as installed until a RED run of it has been observed and its
run ID recorded. Operationalised this week as: force each of the release path's
alarm paths into its failing state once, and record the run ID.**

Concretely, three, in this order:

1. **`Live site release freshness`** (`1ddb033d`, #1182) -- dispatch with
   `tolerance_minutes: 0` and confirm it **creates the issue**, not merely that it
   goes red. Per `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:195-201`, *"its
   alarm path -- issue creation and de-duplication -- has never executed once."*
2. **`check_ladder_bump.py` once #1184 lands** -- open a throwaway PR touching a
   gameplay-surface file with no bump and no `Ladder-Impact:` declaration, and
   confirm the **job fails**, not that the script prints a warning. The whole
   correction in C2 is that this repo already had a warning and lost it in a shell.
3. **`release-sync-monitor.yml`** -- confirm it now reads what the site serves and
   goes red when it does not.

## Why this one and not a better-sounding one

**It is the only intervention in this position that attacks the mechanism proven
to have hidden the cycle's highest-cost defect.** The ladder gate emitted the
correct warning over `#1137`'s range and `|| true` discarded it. A single observed
red run would have shown that in seconds.

**It generalises across mechanisms that do not otherwise share a remedy.** M1
(vacuous check) fails a red run by definition. Item 4's mis-aimed guard fails a
red run, because forcing the failing state means forcing it *about the real
object*. #44's expiry class is exactly a red run with the clock moved. It does not
catch M2, M3 or M4 and this seat is not claiming it does.

**It is cheap enough to be true.** No new file, no new field on every artifact, no
consumer changes. Three `workflow_dispatch` calls and one throwaway PR.

**What I am NOT betting on, and why.** Not #44's freshness-window design: it is a
field on every artifact and a check in every consumer, against a class of three
of eleven failures, and its own author records that `board.json` *"genuinely was
fine for months."* Not a new document: `POSTMORTEM_2026-08-07_CAPTURE.md:736-738`
already records *"The three documents produced today, all printed, none acted
on. This pack is a fourth."* A fifth would be ceremony.

## Predicted cost, stated so it can be wrong

| | Prediction |
|---|---|
| Agent time | **2-3 hours** total across the three |
| Pip attention | **zero**. No decision, no review gate, no ruling required |
| Game-code change | **none**. Workflow and CI only |
| New tracked files | **none required**; at most a line per guard in an existing release doc |
| CI minutes | negligible; three dispatches plus one throwaway PR |

**Predictions that make the bet falsifiable rather than decorative:**

- **~70%: at least one of the three alarm paths fails on its first forced fire**
  for a reason unrelated to the condition it watches -- a missing `permissions`
  block, a token scope, an untested `gh issue create`. Evidence base: `#1177`
  (`5c83d034`) had to grant `issues: write` to a workflow that had **no
  permissions block at all**, and C1 row 17 shows two `Live site release
  freshness` dispatches already at `failure` this morning.
- **~40%: at least one guard cannot be made to go red without a code change.**
  If so, that discovery is worth more than the exercise, and it is the same
  finding as the hollow phase-guard regex, one layer up.
- **~15%: a forced red run creates real noise** -- a spurious issue, a false
  alarm reaching Pip. Mitigation is dispatch-only with an explicit tolerance
  parameter, never a schedule change.

## The falsifier, with a date

**On 2026-08-16**, ask for three run IDs -- one per guard -- each showing the
guard in its FAILING state, each linked from a release artefact (a tag message, a
PR body, or a release doc). **If fewer than three exist, the bet was named and not
operated, and this seat should be told so in Workshop 3 rather than allowed to
re-propose it.**

Second falsifier, on the same date: if three red runs exist and a green-and-wrong
check nevertheless shipped during the week, the bet was operated and **wrong**,
and the correct response is to stop proposing guard hygiene and start on the
mechanism that actually fired.

---

# 6. Unevidenced claims, and pdoom1's own errors

The agenda rules that a claim existing only in a seat's session is not evidence.
These are marked rather than dropped, and this seat's position is weaker for
containing them -- which is the point of listing them.

**U1 -- The tag pushed to the wrong commit, corrected ~90 seconds later.**
**UNEVIDENCED.** This seat tagged a release at the wrong commit and corrected it
within about ninety seconds. I can produce no fetchable artefact: `git reflog show
refs/tags/v0.14.0` and `refs/tags/v0.14.1` are both empty in this checkout, a
force-updated tag leaves no remote trace, and `gh release view` returns final
state only. **What is checkable is only the end state** -- both tags now point at
the correct merge commits (C4 item 2). The rev-parse comparison exists because of
this incident, so the C4 win and this error are the same event seen from two
sides. If another seat holds a `git push --force` line or a webhook record, it
would settle this and I would like it in the minute.

**U2 -- "Pip's run is on the global board", asserted wrongly.** **UNEVIDENCED as
to the exact utterance; the mechanism is evidenced.** During the v0.14.1 lane this
seat queried the leaderboard server, saw rows on `(weekly-2026-w32, L4)`, and
reported that Pip's run was on the global board. **It had not checked the
`duration_seconds` field** -- the same field this seat had used roughly ten
minutes earlier, in the same session, to separate real runs from synthetic
test-suite rows.

The mechanism is corroborated on main:
`docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md:139-141` records that the test suite
*"injected 23 synthetic rows into the live `(weekly-2026-w32, L4)` board during a
release playtest"*, and `:72-76` names the discriminator: *"`duration_seconds`
reading 2.8-10s for 147-turn runs because `game_start_time` is never set on the
live path."* So a board query returning rows was **not** evidence that any of them
was a human run, and this seat had already established that.

**The generalisation is the same document's, at :76-77:** *"a field whose name and
contents disagree ... every check passed, because a check compares a value to
itself and none of them compares a value to its own label."* This seat used the
correct discriminator once, then made a claim without it. **An instrument used and
then not re-used is the same class as an instrument never built**, and it is worse
because the seat had already demonstrated it knew better.

**U3 -- The wrong account of why the ladder guard failed.** **EVIDENCED, and
corrected in full in C2.** The tag object `v0.14.0` and
`POSTMORTEM_2026-08-07_CAPTURE.md:80-85` both attribute the miss partly to the
`GAMEPLAY_PREFIXES` allowlist and state *"Even blocking, it would have missed
this."* `#1184`'s re-run shows the old gate DID warn over `#1137`'s range. **The
mechanism was `|| true`.** The tag cannot be edited; the correction lives here and
in `#1184`.

**U4 -- Discovery times in C1 row 2 and C3 item 1.** The ~16:45 figure is
prose-sourced from the capture pack and is a **ceiling**, not a machine record.
`CHRONICLE_2026-08-06_07.md:353-357` states the general form: *"the discovery
column is uniformly a ceiling, not the observation."*

**U5 -- Base rate for this document.** `docs/CLAIM_AUDIT_2026-08-06.md` examined
68 headline claims this seat published in one day and found **49 confirmed, 6
wrong, 7 uncheckable, 6 stale** -- an **8.8% wrong rate**
(`CHRONICLE_2026-08-06_07.md:479-484`). **This position has not been audited and a
reader should apply that rate to it.** Six of eleven of the wrong claims travelled
into merged PR bodies, sister repos, or artefacts handed to another seat.

---

# Summary of the positions pdoom1 brings to Phase 3

1. **C1:** the front half only, seventeen rows, all fetchable. **No deploy rows,
   deliberately.** The front half is fast and clean; its failure is a 31-hour
   window with no instrument in it and an alarm with no permission to alarm.
2. **C2:** **`coordination#44`'s class is real and its single-generator claim does
   not survive.** Seven mechanisms, six remedies, and the cycle's highest-cost
   defect sits outside #44's class entirely. **Correction: pdoom1's own published
   account of why its ladder guard failed was wrong -- `|| true` was the
   mechanism, the allowlist gap was a separate and independently fatal defect, and
   the old gate also produced false positives.**
3. **C3:** one instance where the mechanism existed and was disarmed; one where no
   mechanism would have caught the composite and the honest answer is *none*; one
   where the mechanism existed, ran daily, was green, and watched the wrong file.
   **And the sharper finding: in the most expensive case the detector existed, was
   correct, was seven days old, and made no difference.**
4. **C4:** guard-first practice (four catches, three of them its own hollowness);
   the tag/HEAD check (win evidenced, the mis-tag behind it not); the
   freshness-proven build (works, and proves the wrong thing about branch); and
   the refusal to claim an unproduced simulation pass, written into an immutable
   tag.
5. **C5:** **no guard counts as installed until a red run of it is recorded.**
   Three forced red runs this week. Predicted cost 2-3 agent-hours, zero Pip
   attention, no game-code change. **~70% that at least one alarm path fails on
   first fire for a reason unrelated to what it watches.** Falsifier dated
   2026-08-16.

*Sealed by the `pdoom1` seat, 2026-08-09, before 11:00 AEST. Written against
`origin/main` at `1ddb033d`. No other seat's Phase 1 position was read.*

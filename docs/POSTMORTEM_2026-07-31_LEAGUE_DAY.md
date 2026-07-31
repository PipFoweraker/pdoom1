# Postmortem capture -- Friday 2026-07-31, league day

**Status: RAW CAPTURE, written during the event.** Not a finished postmortem. Written
between 15:07 and 18:00 AEST while the work was happening, so the sequence is
trustworthy and the conclusions are provisional. Saturday's Restful Mortems session
should challenge everything in the "what it means" sections.

Companion to issue **#1027** (the phase-transition diagnosis) and to
`docs/SESSION_CAPTURE_2026-07-30.md`.

---

## The one-sentence version

In a single afternoon, seven separate defects were found; **not one of them was a
crash, and not one was reported by any guardrail** -- every one was discovered by a
human or an agent going and looking at a mechanism that appeared to be fine.

---

## Play by play

### 15:07 -- the slack hour opens

Pip: *"this is the slack hour for fun... How are we doing? What fun things can I
squeeze in? Have I forgotten anything?"*

Board opens 17:00. State at handover looked good: main green, zero open PRs on the
critical path, artifact built and playtested, seed rolled to `weekly-2026-w31`,
ladder L3.

The slack hour was budgeted for fun. It was spent entirely on defects, all of which
were already present and none of which was visible.

### 15:25 -- FINDING 1: Sandbox Mode was on the league board

The pre-game **scenario dropdown** was fully live, and scenario appears nowhere in
the board key (`get_board_version()` returns seed + ladder epoch only).

| Scenario | Opening position |
|---|---|
| Sandbox Mode | **$10,000,000**, 1000 compute, 500 research, 10 papers. In-game text: *"Unlimited resources"* |
| Crisis Mode | $150k, doom already at 65, starts 2020 |
| Bootstrap Mode | $500k, 200 compute, doom 40 |

A player could pick Sandbox from a visible dropdown and post turns-survived to the
same board as everyone else, unmarked.

**This is #1058 repeated.** At 11:14 that same morning, difficulty had been locked to
Standard for *exactly this reason* -- difficulty was persisted, real, and absent from
the board key. The scenario control sat **three rows above it on the same screen** and
was not checked. The fix shipped at 11:14 and the identical hole survived four more
hours, one control away.

**Why the first fix did not generalise:** #1058 was framed as "lock difficulty", not
as "find every input that changes the rules but not the key". A fix scoped to the
instance does not find the class.

Shipped as **#1060**: scenarios stay playable but are UNRANKED, with the player warned
at the moment of choice and again at game over. `GameConfig.is_ranked_run()` is a
named accessor rather than an inline check, specifically so a future board-write site
cannot quietly forget it.

### 15:30 -- FINDING 2: the morning's recorded playtest was of a different game

Pip's local `config.cfg` carried `scenario_id="crisis"`.

The 14-minute recorded playtest taken at 10:24 that morning -- treated by everyone,
including the midday handover, as a playtest of the league build -- was a playtest of
**Crisis Mode**: doom starting at 65, year 2020. A configuration no league player
would ever run.

**The severity is in the direction of the error.** It did not fail to prove the build
was good. It *appeared* to prove it, convincingly, with a recording and a transcript
and a list of findings. Confidence was manufactured, not earned.

Fix: `tools/reset_player_state.py` (dry-run default, backs up rather than deletes,
`--restore`). Now wired into **[Gate 4] check 8**: *"the machine that proved it is a
clean machine."*

### 15:35 -- FINDING 3: the red test was real, and the diagnosis was wrong

The midday handover reported `test_game_lifecycle_hygiene` red on main since that
morning, attributed to #1050 or #1051, with an open worry that the leaked node might
still be signal-connected -- which would mean doubled doom ticks and stale panels, a
correctness bug wearing a leak's clothes. It was called *"the highest-value unclaimed
task at handover."*

Running the test named the node in seconds: `ScenarioLoader`.

Every element of the diagnosis was wrong:

- **Not signal-connected.** No signals, no `_ready`, no `_process`, never added to the
  tree. Inert. The feared correctness bug did not exist.
- **Not from #1050/#1051.** Pre-existing since #483 / PR #494.
- **Not red in CI for a bad reason.** `_apply_scenario_overrides` returns early
  *before* the allocation when no scenario is set. CI has no scenario, so CI was
  legitimately green. It reddened only on machines with a scenario selected -- i.e.
  because of Finding 2.

**The lesson is about diagnosis under time pressure.** The handover was written
carefully, hedged honestly ("Not bisected further"), and was still wrong in three
ways -- because it reasoned from *when the symptom appeared* rather than from *what
the symptom named*. The test had been printing the answer the whole time.

### 15:50 -- FINDING 4: four tests that read the developer's own config

Four endgame tests were red locally and green in CI. Cause: `GameConfig` is an
autoload that loads the real user config, and the tests never pinned what they
needed. They were asserting against whatever `scenario_id` the machine happened to
hold.

A test whose result depends on the developer's saved preferences is not a test.
Fixed by pinning `scenario_id` in `before_each` and restoring in `after_each`.

### 16:19 -- the re-cut

`build_release.py` from `868c784e`. BUILD-VERIFY PASS. Fast gate 1001/0, 97-of-97.

### 17:05 -- FINDING 5: the download link served last week's game

**There was no `v0.13.2` tag and no v0.13.2 release.**

pdoom1.com's Download button points at
`releases/latest/download/PDoom-Windows.zip`. `latest` resolved to **v0.13.1**, which
ships **ladder L2** and seed **`weekly-2026-w30`**.

Had the league opened as planned: bless `(weekly-2026-w31, L3)`, announce, and every
downloader posts to `(weekly-2026-w30, L2)` -- wrong on **both** axes. The blessed
board sits empty all night. Nothing anywhere reports an error. The obvious reading
would have been "nobody played."

**[Gate 5] check 3 was written to catch exactly this** -- *"the seed the client posts
is the seed I speak, and it is inside the build we cut"* -- and it does not, because
it checks the const against **main**, never against **what the download actually
serves**. The gate had the right instinct and the wrong referent.

Proposed **check 9**: click the actual Download button and confirm the version served.
Not the API. Not main. The button.

### 17:33 -- FINDING 6: the orchestrator invented a constraint

Asked to choose how to handle Mac and Linux, the orchestrator presented Pip a
three-way decision (Windows-only / carry old assets forward / Windows-only with a
note) resting on the premise that Mac and Linux **could not be built tonight**.

Pip asked the obvious question -- *"Why can't we build mac and linux assets tonight?
Just time?"* -- and the premise collapsed. Export presets for all three platforms:
present. Godot 4.5.1 export templates including `macos.zip` and `linux_release.x86_64`:
installed. GodotSteam per-platform binaries: committed. `build_release.py --preset`:
supported.

Linux built and verified in minutes.

**This one is different in kind from the others and belongs in the postmortem for that
reason.** Findings 1-5 were latent defects in the system. This was a defect *in the
analysis*, generated live, under time pressure, by the party everyone was relying on
to check things. It was caught by a human asking a one-line question.

The failure mode is precisely the one this project keeps naming: a confident,
plausible, well-structured artifact -- a decision matrix with tradeoffs and a
recommendation -- resting on an unchecked assumption. The format signalled diligence
that the content did not contain.

### 17:40 -- FINDING 7: macOS is genuinely broken, and may always have been

macOS export from Windows produces a zip but fails:

```
Export: Relative symlinks are not supported, exported
  "libgodotsteam.macos.template_release.framework" might be broken!
WARNING: "...framework": Info.plist missing or invalid, new Info.plist generated
ERROR: LipO/MachO: Can't open file ".../Versions/Current/libgodotsteam"
ERROR: CodeSign: Invalid binary format
```

Two Windows-side losses compound. A macOS `.framework` needs `Versions/Current` to be
a **symlink**; on a Windows checkout it is a real directory. And the framework has no
`Info.plist`, so Godot generates one and derives `CFBundleExecutable` by truncating at
the first dot -- looking for `libgodotsteam` when the binary is
`libgodotsteam.macos.template_release`.

**The uncomfortable part:** our zip is 123.5 MB; v0.13.1's shipped macOS asset is
124.7 MB. v0.13.1 was almost certainly produced the same way, with the same defect.

**Nobody has ever proven a macOS build of this game runs.** That is not a regression
introduced tonight. It is a pre-existing unknown that nothing in the process was
shaped to surface, and it surfaced only because someone tried to build the platform
under time pressure.

### 17:45 -- FINDING 8: the release pipeline does not ship the build you prove

`enhanced-release.yml` fires on any `v*.*.*` tag and **builds its own assets on
`ubuntu-latest`** via `scripts/build_all_platforms.py`, publishing with
`draft: false` -- live immediately.

So the intended sequence was: record [Gate 4] saying *"A human has played the thing we
ship, not the thing we meant"* -- and then have the tag trigger a **different binary**,
built on a different machine, to become what players download. **The sentence would
have been false at the moment it was spoken**, on camera, and nothing would have
flagged it.

Compounding: `build_all_platforms.py` has **none** of `build_release.py`'s discipline
-- no `rm -rf .godot`, no freshness marker, no proof the pack reflects the source.
`build_release.py` exists *because* that failure burned ~12 cycles in v0.11.0. The
release path routes around the tool built to prevent the disaster.

Mitigation adopted: publish via CI, then **download the published artifact and play
that** for [Gate 4] check 5. This makes the claim literally true and closes the same
download-path blind spot as Finding 5.

### 17:49 -- FINDING 9: the sync alarm was never what it looked like

Website issue #203, "Leaderboard sync failing", had been treated all day as a possible
Gate 6 blocker, with the seed rollover as prime suspect (the timing matched).

**Nothing broke on 30 July. The sync had been dead for weeks and started telling the
truth on 30 July.**

Commit `52942224` -- *"make board-key loss loud -- green until it is not (#190)"* --
added a step adjudicating `continue-on-error` outcomes. Before it, every step was
`continue-on-error: true`, so the job **could not reach a failed state**. The runs
that reported **success** contain the identical error:

```
ERROR: No game repository configured. Run --setup first.
##[error]Process completed with exit code 1
```

Present on 29 July. Present on 20 July. Green both times.

Root cause: `scripts/game-integration.py` reads
`scripts/game-integration-config.json`, which is **in `.gitignore`** -- it can only
exist on a local dev machine, never on a runner.

The seed hypothesis was **refuted**: the failure is upstream of any data fetch and
predates L3 by ten days.

**The live board is published by a different workflow entirely** (`board-liveness.yml`,
green throughout). #203 was noise. There was never a board blocker.

**Two lessons, pulling opposite ways.** First: #190 worked exactly as designed -- it
converted a silent failure into a loud one, and the loud one looked like a new
emergency. *A newly-loud alarm is evidence about the alarm, not necessarily about the
world.* Second: a plausible causal story (seed rolled, sync broke, same day) survived
most of a day on timing alone, and shaped planning, until someone diffed the logs.

### 17:55 -- FINDING 10: the test suite writes to the player's profile

`test_leaderboard_properties.gd:31` constructs a **real** `Leaderboard`, which
persists to `user://leaderboards/`. So every fast-gate run deposits fake boards
(`leaderboard_test_prop_*__test.json`) into the developer's real player profile, where
the leaderboard dropdown -- built from local files, not the API -- lists them beside
genuine boards.

Proven by regeneration: `reset_player_state.py --apply` cleared the directory at
16:04; it held 14 files again by 16:49, including a fresh crop of `test_prop_*`, next
to a real `leaderboard_weekly-2026-w31__L3.json`.

This probably also explains a reported "Clear Local Scores did nothing" (#1066): the
clear may have worked and then been undone by a later test run. **The delete may be
innocent** -- worth confirming before anyone hunts a bug there.

### 17:56 -- FINDING 11: the shipped build lies about what it is

Pip, after the release went live: *"how will i know if this version of the game is
the right one when I get it from the website?"*

The obvious answer -- check the in-game build stamp -- is wrong. `build_stamp.txt`
**inside the published v0.13.2 build** reads:

```
commit=fd60eb6
date=2026-07-11
branch=feat/dev-build-overlay-ledger
```

Three weeks stale, naming a dead feature branch.

Cause: `tools/write_build_stamp.py` is invoked by `build_release.py` (local builds), and
by nothing in the CI path. `build_all_platforms.py` does not call it and
`enhanced-release.yml` does not either. So a CI release ships whatever
`build_stamp.txt` happened to be committed at that SHA -- and since the stamp is
written *by* a build and committed *after* it, the value at any given commit is always
the previous build's.

**The provenance display is the thing least able to be trusted about provenance.** It
does not fail; it confidently reports a plausible commit on a plausible date.

What actually worked, and it is worth generalising: **behavioural identification.**
Pip confirmed the build in about fifteen seconds by opening the scenario dropdown and
seeing the amber NOT RANKED warning -- code merged at 16:15 that day, which no earlier
build can render. A feature that cannot exist in the previous version is a stronger
identity check than any string the build prints about itself.

Also confirmed at 17:56, and predating tonight: the site's Linux download button
requests `releases/latest/download/PDoom.x86_64`, which **404s**. Windows and macOS
both return 200. Measured, not inferred.

---

## What it means (provisional -- challenge these Saturday)

### 1. The instance-versus-class problem is the expensive one

#1058 fixed difficulty at 11:14. The identical defect in scenario survived until
16:15, one control away on the same screen. The fix was scoped to the instance.

**Candidate practice:** when a defect is found, the fix is not complete until someone
has enumerated the *class* -- here, "every player-reachable input that changes the
rules but is absent from the board key." [Gate 5] check 8 now asserts the class, not
the instance.

### 2. Every failure was in the gap between a proxy and the thing itself

The pattern is sharper than "silent wrongness." Each defect lived where a **proxy for
truth had quietly detached from the truth**:

| Proxy that was checked | The thing that mattered |
|---|---|
| the board key is stable | runs on the board are comparable |
| main says seed w31 | the download serves seed w31 |
| the build we cut | the build CI publishes |
| the playtest was recorded | the playtest was of the shipping config |
| the workflow is green | the workflow did anything |
| CI is green | the developer's machine is representative |

Every proxy was chosen because it is cheap and *usually* faithful. Each stayed
faithful right up until it didn't, and nothing was watching the join.

### 3. Confidence-shaped output is a failure mode in its own right

Finding 6 was produced by the party doing the checking, and it was *more* dangerous
than a silent defect, because it arrived formatted as diligence -- a decision matrix,
tradeoffs, a recommendation. Structure is not evidence. It was caught because Pip
asked "why?" about a premise rather than choosing among the options offered.

**Candidate practice:** when presenting a constrained choice, state the constraint's
provenance in the same breath -- "verified by running X" or "assumed, not checked."
An unlabelled constraint should be read as unchecked.

### 4. The ceremony earned its keep, and its blind spots are now known

Four of ten findings surfaced *because* someone was walking gate checks. The gates
also proved improvable in-flight: check 8 was added to both [Gate 4] and [Gate 5]
during the day, each earned by a specific failure hours old.

Known remaining blind spot: **[Gate 5] check 3 verifies against main, not against the
download.** Proposed check 9.

Also recorded honestly: **the freeze was porous.** #1051 ("Accept Your Fate") is a new
feature that merged after the freeze line, and *no* post-freeze PR carried a
`league-critical` label -- so the exemption admitting the bugfixes was never actually
recorded anywhere. The rule existed and was not operated.

### 5. What went right, and should not be lost in the accounting

- **The slack hour existed.** Every finding above was found in time bought by
  deliberately not scheduling anything. Pip: *"this is why we left slack."*
- **`build_release.py` did its job** -- every cut was provably fresh, and that
  question never had to be re-litigated.
- **The min-test floor (#640) held.** 1001 tests, unchanged count across every run, so
  "no test silently vanished" was a check rather than a hope.
- **#190 worked**, even though its success looked like a new failure.
- **The gates converted vague unease into ordered, checkable claims** -- which is the
  only reason ten findings could be triaged rather than panicked over.

---

## Open items generated today

| Item | Where |
|---|---|
| Scenario runs unranked + warned | #1060, merged |
| Duration column meaningless vs turns | #1062 |
| Player/lab name on the first screen | #1063 |
| Play Again logic after a run ends | #1064 |
| *"critical ladder bug"* -- unresolved, needs the audio | #1065 |
| IP / trademark, due Mon 2026-08-03 | #1061 |
| Bug reports never leave the player's disk | #1057 |
| Leaderboard dropdown shows dev test seeds | #1066 |
| Test suite writes to the real user profile | #1066 comment -- **needs its own issue** |
| macOS framework broken on Windows checkouts; no macOS build ever verified | **needs an issue** |
| `enhanced-release.yml` builds its own assets, bypassing `build_release.py` | **needs an issue** |
| `build_release.py` hardcodes `PDoom.exe` output name regardless of preset | **needs an issue** |
| v0.13.1 shipped no unversioned Linux alias -- site's Linux button likely long broken | **needs an issue** |
| Sync workflow: gate the dead steps to `workflow_dispatch` | website, needs an issue |
| [Gate 5] check 9: verify what the Download button serves | ritual sheets |

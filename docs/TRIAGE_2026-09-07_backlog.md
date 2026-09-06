# Backlog triage, 2026-09-07 -- 213 open issues

Read while Pip was ill (2026-09-02..07). Read-only pass: nothing was closed,
labelled, commented on or committed. This document is the only artifact.

**Evidence standard.** Every claim in a heading, table cell or bolded sentence
below names a command you can run. Where a check was not run, the row says
`NOT VERIFIED` rather than asserting. Claims re-used from the previous triage
(`docs/ISSUE_TRIAGE_2026-08-06.md`, a month old) are marked as such and were
re-verified where it mattered.

Repo state this was checked against:

    git log -1 --format=%H          # 66534ee4, 2026-09-07 01:13 +1000
    cat version.txt                 # 0.14.4
    cat ladder_version.txt          # 6

---

## The headline, in three lines

1. **A guard is refusing to publish releases because these issues are open.**
   `scripts/check_release_notes.py` RN003 blocked the v0.14.3 publish with
   7 fatal findings for citing #1225, #1038 and #1223 as delivered while they
   were open. Closing stale-open issues is not tidying here; it is unblocking
   the release pipeline. Command: `git show 161240be`.
2. **A test is red on main right now.** `python -m pytest
   tests/test_ascii_compliance.py` -> `1 failed, 3 passed` (#1331).
3. **A dated commitment went past due while Pip was ill.** #1343 declares
   `COMMITMENT<colon> 2026-09-04` (cited, not declared); today is 2026-09-07.

---

## 1. Duplicates and near-duplicates

Recommended survivors are the newest issue that carries the most measurement.
**Close nothing from this section without reading the survivor first** -- in two
clusters the duplicate carries a detail the survivor lacks (noted inline).

### 1A. Auto-generated release checklists -- pure duplicates (5 closeable)

`gh issue list --label checklist --state open`

| Version | Issues | Recommendation |
|---|---|---|
| v0.14.2 | #1252 | Close -- superseded, `cat version.txt` is 0.14.4 |
| v0.14.3 | #1302, #1304 | **Identical bodies, same day.** Keep neither; both are superseded by v0.14.4 |
| v0.14.4 | #1324, #1328 | **Identical bodies, same day.** Keep ONE (#1328), close the other |
| v0.14.4 | #1325 | `WARNING Pre-Release Checks Failed` -- close when the v0.14.4 checklist closes |

The generator emits two checklist issues per release. That is the actual bug
behind this cluster and it is not filed anywhere; #1299 is adjacent but is
about workflow independence, not double-filing. NOT VERIFIED which workflow
emits the duplicate pair.

### 1B. Leaderboard identity and dev-mode integrity -- four issues, one defect

| Issue | Ask |
|---|---|
| #788 | Mark dev-mode-used runs with a visible badge, do not exclude |
| #1012 | No dev-mode/verification field reaches a submitted score |
| #1042 | Score payload should emit player name AND lab name, plus a dev-mode flag |
| #812 | Show lab name + operator name on the board by default |

**Recommended survivor: #1012** (broadest; states the anti-cheat design that
already exists in `verification_tracker.gd` and why it does not reach the
board). Close #788 and #1042 as duplicates of it, quoting #788's "mark, do not
exclude" ruling into #1012 -- that ruling is the part #1012 lacks.

#812 is a **separate, largely-fixed** case: see section 2.

Verification: `grep -rn "dev_mode_used\|dev_touched" godot/ --include=*.gd`
returns nothing, so the flag genuinely does not exist on any of the three.

### 1C. Bug reports die on the player's disk -- #800 and #1057

Same defect, filed twice five days apart. **Recommended survivor: #1057** (it
maps both halves of the pipeline and names the built-but-uncalled website
intake). Close #800 as a duplicate.

Both have a **stale premise** -- see section 3.

### 1D. Cross-platform release -- #917, #805, #1071

The 08-06 triage already folded #805 into #917 ("keeping three copies of one
problem open is how 201 happens"). It is still open a month later.
**Survivor: #917.** Close #805. Keep #1071 separate only if the macOS
`libgodotsteam` framework failure is treated as its own engineering task; if
not, fold it too.

### 1E. Hiring pipeline -- eight overlapping issues

#789, #813, #830, #833, #954, #961, #1091, #1225.

**Survivor for the UI/UX half: #1225** (it is actively shipping item by item,
4 of 5 landed). **Survivor for the design spine: #833.** #954 and #830 were
already marked "absorbed into UI arch Phase 2" by the 08-06 triage -- NOT
re-verified that Phase 2 shipped the click-through, so verify before closing.
#961 is a ruling, not a duplicate (section 5).

### 1F. "The game emits an artifact so the website stops guessing"

#994 (calibration.json), #1011 (keybinds), #962 (frontier labs), plus the
#1042 half of cluster 1B. Not duplicates -- four different artifacts -- but
**one lane with one piece of shared infrastructure**, and none of them has
started. `ls godot/data/calibration.json` -> No such file or directory.
Recommend grouping under a single emit-infrastructure epic rather than closing
any.

### 1G. "Schedule a half-day workshop" -- #889, #984, #1210

Three issues whose entire content is a request to book time. Two have
**already missed their own windows** (section 3). Recommend one standing
workshop-queue issue, or three calendar entries per
`docs/calendar/COMMITMENTS.md`, and close all three.

### 1H. Office visual direction -- #1229, #1319, #1321, #944, #894

#1319 explicitly says it is not a duplicate of #1229, and it is right (#1229 is
direction, #1319 is the measured current state). But five issues describe one
lane. Recommend #1319 as the survivor with the others linked, not closed --
#894 and #1321 each carry unique content.

---

## 2. Already fixed on main -- close these

The known failure mode: squash-merge does not fire closes-keywords here
(CLAUDE.md), so a fix lands and the issue stays open. **This section is the
most valuable one in the document.**

### Verified against the code today (run the command, see for yourself)

| Issue | What is true now | Command |
|---|---|---|
| **#1070** Test suite writes REAL leaderboard files into the dev profile | `_isolated_env()` sandboxes `APPDATA` per-checkout; the runner no longer inherits the parent profile | `grep -n "_isolated_env" scripts/run_godot_tests.py` -> line 74; body at 74-109 |
| **#1224** No font-size SSOT (378 sites) | The SSOT exists and the ratchet passes | `grep -n "default_font_size" godot/theme/base_theme.tres` -> `19`; `python tools/check_font_sizes.py` -> `OK` |
| **#621** Build lane L9: no balance-config surface exists | Balance autoload ships | `ls godot/autoload/balance.gd`; commit `8459f6e0` |
| **#500** Research Quality (Rushed/Standard/Thorough) | Mechanic shipped | `grep -rn "research_quality" godot/scripts/core/game_state.gd`; commit `30f3c6d5`. **Close as superseded by #1090**, which asks to move it, not build it |
| **#648** team_player uncapped-stacking exploit | The trait was retired into a quirk channel; there is no team_player trait to exploit | `grep -rn "team_player" godot/scripts/core/turn_manager.gd` -> line 176, "retired team_player trait -> quirk team_productivity_add channel" |
| **#613 / #614 / #615** Build lanes L2 / L3 / L4 | Founder hours, conferences and event tiers all ship | `ls godot/scripts/core/conferences.gd godot/scripts/core/conference_trip.gd godot/scripts/core/event_tiers.gd godot/scripts/core/window_resolver.gd godot/scripts/core/month_plan.gd` |

### Verified by a squash-merge commit that names the issue

Command for every row: `git log --oneline --all --grep="<number>"`.

| Issue | Commit | Title |
|---|---|---|
| **#802** In-game music controller | `5731dd2e` | feat(audio): let players pick the track from the pause menu (#802) (#1146) |
| **#1126** Local/Global toggle un-presses on fetch failure | `c48d79e0` | fix(leaderboard): make a failed global fetch VISIBLE (#1126) (#1127) |
| **#600** Dev overlays cannot read live state | `71f2ad6a` | fix: dev/F3 overlays read live game state (#600) (#607) |
| **#601** Ledger UX | `4d73afb9` | fix: ledger dialog fills + toggles + red warnings (#601, #602) (#610) |
| **#603** Fanfare backdrop + bug-report Submit | `77709b05` | fix: fanfare dimming backdrop + bug-report thanks disables Submit (#603) (#606) |
| **#1063** Set player + lab name on the first screen | `a8a858ec` | feat(identity): one-time default-name prompt at upload (#1063, #957) (#1133) |
| **#1093** Generation paid for, outputs never reviewed | `b13afb05`, `6cc776c4` | fix(art): unblock 605 approved assets; second-pass promotion map |
| **#903** Quirk/perk icon set | `02b72e4c` | art(quirks): 16-icon quirk set with valence colour-coding (#903) (#909) |

**#1126 was already listed as fixed by the 2026-08-06 triage and is still
open a month later.** That is the whole failure mode in one issue.

### Partially fixed -- re-scope rather than close

| Issue | What landed | What remains |
|---|---|---|
| **#812** lab + operator name on board | `2487c6bf` (#1176) carries both identity fields client-side | `leaderboard_sync.gd:231` comments that the server "cannot yet take" the operator name. The remaining half is server-side |
| **#1225** five hiring things | 4 of 5 items: `bbf218b4` (item 4), `c35c862b` (item 2), `20283bc5` (item 5), `9af8b175`. `git show 161240be` says "four of #1225's five items shipped" | One item. **Identify and finish it, then close -- this issue is blocking release publication (RN003)** |
| **#1223** Action Queue vs Attention header | `28ffbce2` (#1273) stopped the header calling committed Attention "queued" | Rest of the three-widget contradiction. Also blocking RN003 |
| **#917** cross-OS releases | `72f75865`, `18d19792` | No gdextension packaging found in `enhanced-release.yml` (`grep -n "gdextension" .github/workflows/enhanced-release.yml` -> nothing). Item 1 of its own DoD is open |
| **#1008** release feed index | `9bbadf90` semver-sorts the feed | The generated feed is still never committed back. NOT VERIFIED whether a `--check` gate was added |
| **#1009** devblog automation | `255c91d1` made it manual-only (the holding fix) | Draft-generator rebuild |
| **#880** Financing submenu | `godot/data/icon_mapping.json:121` now has a `financing` entry | Cost figures NOT VERIFIED |
| **#800 / #1057** bug reporter | `bug_report_panel.gd:113` now says "saved locally on your device", with a copy/open-tracker/open-folder exit row (see the `#1281` comment at line 170) | Auto-transmit still does not exist. `grep -rn "HTTPRequest" godot/scripts --include=*.gd` -> nothing |

**Count: 14 issues recommended for outright close in this section, 8 more to
re-scope.**

---

## 3. Stale premise -- the claim is no longer true

| Issue | The claim | What is true now |
|---|---|---|
| **#648** | "team_player trait whose synergy bonus stacked without a cap" | The trait is retired. `turn_manager.gd:176` |
| **#800** | "the confirmation UI actively tells the tester it was transmitted" | It now says the opposite. `bug_report_panel.gd:113` |
| **#500** | Research quality needs building | It exists; #1090 says it is in the wrong place |
| **#186, #187, #188** | Media / regulations / geopolitics missing from the game | Filed 2025-08-20 against the pygame v0.2 build. The engine, economy and design language have all been replaced. Re-file from current premises or close |
| **#763, #803** | Reasoning at days-granularity | Overtaken by the turn = ONE MONTH ruling (#1125, 2026-08-05). Per 08-06 triage; NOT re-verified |
| **#961** | `game_state.gd:104 const MAX_CANDIDATES` | The constant is unchanged at 6 but has MOVED to `game_state.gd:172` (`grep -n "MAX_CANDIDATES" godot/scripts/core/game_state.gd`). The line refs in the issue body are stale; the defect is not |
| **#894** | Deferred, no foundations | Anchor Sockets V2 shipped (`a89f5ca4`, "part-anchored effects on animated sprites (#894 #900 #913)"). One named foundation is now in place |
| **#1023** | LEAGUE-CRITICAL: game does not initialise | Overtaken by events -- the league ran on the shipped build. Per 08-06 triage |

### Stale by DATE (the premise is a deadline that has passed)

| Issue | Its own date | Days past as of 2026-09-07 |
|---|---|---|
| **#1343** | `COMMITMENT<colon> 2026-09-04` (cited, not declared) pause-semantics sweep, "for the league patch" | **3 days overdue** |
| **#1061** | "DUE Monday 2026-08-03", and Pip asked to be FORCED | **35 days overdue** |
| **#984** | Workshop "target window: week of 2026-08-10" | ~4 weeks past |
| **#950** item 4 | Anniversary feed line "if system date == 2026-07-30" | Expired; that item is now dead code if it shipped, moot if it did not |
| **#808** | "do this review ON OR AFTER 2026-08-24" | Now actionable -- this one has ripened, not rotted |

---

## 4. The real ship list

**Treat the existing labels as evidence, not truth**, as instructed: 27 issues
carry `ship:next-release` and several date from July. The list below is built
from what a command says is broken today, not from labels.

### Genuinely blocking (verified)

| Issue | Why it blocks | Proof |
|---|---|---|
| **#1225, #1223, #1038** | `scripts/check_release_notes.py` RN003 **refused to publish v0.14.3** for citing these as delivered while open | `git show 161240be` -- 7 fatal RN003 findings |
| **#1331** | ASCII compliance test is RED on main | `python -m pytest tests/test_ascii_compliance.py` -> `1 failed, 3 passed` |
| **#1343** | Dated commitment, past due, scoped for the league patch | `docs/PAUSE_SEMANTICS_SWEEP.md`; `#1341` partial fix landed as `82fa10a1` but the sweep is separate |
| **#1325** | Pre-release checks failed for v0.14.4, the current version | `cat version.txt` -> 0.14.4 |

### Release-integrity issues that are real but not blocking a build

#1290 (no tag protection -- "the most privileged act has less review than
merging a docs change"), #1299 (pre-release-checks cannot block
enhanced-release; two workflows, one trigger), #1310 (in-game patch notes cite
open issues, unguarded), #1279 (Documentation Sync red on 100% of PR runs
since 2026-07-28 -- `git log -3 -- .github/workflows/sync-documentation.yml`
shows no recent repair), #1269 (RELEASING.md says ship from a release branch;
four releases shipped from main).

These five are the "we taught ourselves to ignore red" family. They are the
highest-leverage non-blocking work in the backlog.

### Everything else is backlog

Of the 213, my read is roughly:
- ~22 closeable now (sections 1 and 2)
- ~8 blocking or integrity-critical (above)
- ~25 needing a Pip ruling (section 5)
- the remainder is deliberately-parked design and art material -- workshops,
  future epochs, voice-memo captures. **That is not neglect, but it is why the
  counter never falls.**

NOT VERIFIED: I did not audit all 27 `ship:next-release` labels individually
against current main. The four I did check (#506, #545, #721, #722) are all
genuinely unstarted -- `ls godot/data/help/` does not exist and
`grep -rln "TutorialManager" godot/ --include=*.gd` returns nothing, so #721
and #722 are real, unstarted, and correctly labelled.

---

## 5. Needs a Pip ruling

Scannable. Each is one yes/no or pick-one. Answer them in a batch.

**Overdue and personal**

1. **#1061** -- IP/trademark: have you spoken to the Australian lawyers yet, yes/no? (35 days past your own due date; you asked to be forced.)

**Release and process**

2. **#1343** -- The pause-semantics sweep missed its 2026-09-04 date: re-commit to a new date, or descope it to the #1341 fix already shipped?
3. **#1269** -- Adopt the release-branch model for real, or amend RELEASING.md to say we ship from main?
4. **#1290** -- Turn on tag protection now, yes/no?
5. **#1299** -- Merge pre-release-checks INTO enhanced-release as a gating job, or accept that it is advisory?
6. **#1025** -- Does [Gate 2: THE FREEZE] move after [Gate 4: PROVEN BUILD], yes/no? (Council of Elders vote, was wanted before "next week's league".)
7. **#1266 / #1267** -- Does the league-cycle handbook get CREATED (it appears not to exist), or is an existing doc renamed into the role?

**Design calls blocking build work**

8. **#961** -- Fixed candidate-pool cap, or scale it with reputation/org-size/an upgrade? (W3 was meant to rule this; it did not. The constant is still 6.)
9. **#1090** -- Confirm Research Quality moves off the Plan screen to research-project level, yes/no? (If yes, #500 closes with it.)
10. **#903** -- Retire the dead 15-perk `staff_perks_panel.gd` catalogue in favour of quirks-as-perks, or keep both? (16 icons vs 32.)
11. **#958** -- Should the lab-name field pre-fill a random name by DEFAULT? (Today it is opt-in: `game_config.gd:13` defaults to `DEFAULT_LAB_NAME`, and `pregame_setup.gd:205` only randomizes on a button press.)
12. **#788 / #1012** -- Confirm the ruling is MARK dev-assisted runs, never exclude them, yes/no?
13. **#822** -- Does overbooking Attention get TEETH (forced cancel-or-pay), or stay a flat reject?
14. **#823** -- Layered overlapping leagues, or hard cutover?
15. **#1193** -- The #1137 retime made a simulated run ~38% more expensive: is that the intended event density, yes/no?
16. **#1004** -- Is "next epoch" now, for the three parked upgrade mechanics (chairs attrition, board oversight, ethicist headcount)?
17. **#1015** -- Do we pair with a visual/graphic designer in response to the AI-art immune-reaction concern, yes/no? (Raised by a funder alongside a donation.)
18. **#1014** -- Browser demo, or code-signing (#683), as the next "people cannot run the game" fix? Pick one.
19. **#1142** -- Chinese localisation before end of year: still a goal, yes/no?
20. **#1257** -- Add a sixth `origin` value (`authored_art`) for the incoming pixel artist, yes/no?
21. **#1258** -- P6 worktree rule: build the mechanism, or delete the rule? (It carries its own deletion trigger.)
22. **#529** -- The parked CRT/terminal aesthetic: unpark or kill? (Open since June.)
23. **#786** -- CREDITS.md names: your preferred handle, the musician's, playtester acknowledgements. Only you can fill these.

**Scheduling (three issues that are only a request for time)**

24. **#889** (Architecture Week), **#984** (audit mechanics, window missed), **#1210** (the first ten turns) -- book them as calendar commitments, or close all three and stop tracking time as issues? Pick one.

**Cheap and expiring**

25. **#950** -- The creative harvest: approve items 1-3 and 5-12, or close the whole issue? (Item 4, the anniversary beat, has expired.)

---

## What I did not check

Stated plainly, because a complete-looking report with plausible claims is
worth less than a short one with checked claims:

- I did not run the game. Every UI claim here is from source, not from play.
- I did not run the fast gate or the simulation tier.
- I did not read the comment threads on most issues -- bodies only. Rulings
  made in comments will be missed.
- I did not individually audit the 103 unlabelled issues for ship-relevance.
- The 08-06 triage's "absorbed into UI arch Phase 2/Phase 1" claims (#936,
  #954, #828, #830) are **repeated but NOT re-verified**. Verify before closing.
- I did not verify which workflow emits duplicate release-checklist issues.

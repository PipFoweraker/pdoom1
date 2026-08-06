# Issue triage, 2026-08-06 -- all 201 open issues, bucketed

Prompted by Pip, 2026-08-06: *"I still feel like we have 200 issues open and
none of them are being worked on?"*

**Short answer: the feeling is roughly half right.** 201 issues are open. But
~50 of them (25%) are not waiting on work at all -- they are already fixed on
main (squash-merge never fires closes-keywords here, per CLAUDE.md), or their
premise has been overtaken by rulings (turn = ONE MONTH, the UI architecture
doc, the AP retirement). Another 27 are waiting on a decision only Pip can
make. The genuine, sized, waiting backlog is ~116 -- and most of THAT is
design-epic material filed deliberately for future epochs, not neglected bugs.
Eight more were fixed today in the PR that carries this document.

## The counts

| Bucket | Count | Meaning |
|---|---|---|
| DONE ALREADY (verified against code) | 8 | close now, evidence below |
| DONE ALREADY (likely -- verify then close) | 15 | commit references found; one grep each from proof |
| STALE / OVERTAKEN | 19 | premise changed; close or re-file |
| DRIVE-BY -- fixed in this PR | 8 | see PR |
| DRIVE-BY -- still available | 8 | real <30-min fixes, listed below |
| NEEDS PIP | 27 | blocked on a decision only he can make |
| REAL WORK | 116 | genuine backlog (mostly design epics + owned lanes) |
| **Total** | **201** | |

**Confidence:** the 8 verified-done claims were each checked against the code
on main at `78be0370` (grep/read, evidence quoted below) -- high confidence.
The 15 likely-done rest on commit-message references to the issue number plus
circumstantial code evidence -- close them only after the one-line check named
per item. Bucket assignment for the other ~150 is title/body-level triage
against the recent rulings; expect a handful of misfiles, not dozens.

## Why the pile is not moving (the single biggest reason)

**Closed-in-fact-but-open-on-GitHub is the default outcome of this repo's
merge process.** Squash-merge does not fire closes-keywords (documented in
CLAUDE.md), so every fix that lands without a manual close leaves its issue
open. At least 23 of the 201 (11%+) are in that state. The pile LOOKS static
because its denominator never shrinks -- work is landing (100+ commits since
07-26 alone), but the counter only ever goes up. A weekly 10-minute
"close what merged" sweep (or a bot that parses `(#NNN)` from merged PR
titles and comments on the issue) would fix the *perception* problem, which
is the problem Pip actually reported.

Secondary reason: ~58% of the open set is deliberately-parked design/epic
material (workshops, future epochs, art programs). Those are backlog by
intent, not neglect -- but they sit in the same undifferentiated count.

---

## DONE ALREADY -- verified, close these now (8)

Evidence checked against main at `78be0370` on 2026-08-06.

- **#959** Surrender button -> "Accept Your Fate" shipped in PR #1051
  (commit `8ed05128`). Code: `godot/scenes/pause_menu.tscn`,
  `godot/scripts/ui/pause_menu.gd`, guard test
  `godot/tests/unit/test_resign_destructive.gd`.
- **#1126** Local/Global toggle silently un-presses on fetch failure -> fixed
  in PR #1127 (commit `c48d79e0`): `leaderboard_screen.gd` now carries
  `_global_fetch_failed`, a visible failure state and a retry path; regression
  test `test_leaderboard_global_failure_visible.gd` exists.
- **#1030** "Game not started..." permanent first feed line -> the string is
  GONE from `godot/scenes/ui/watch_screen.tscn` (grep returns nothing).
  Part (b) (dead `TurnCountLabel`) is the same defect class as #1031 --
  fold the residue there and close this.
- **#1037** stale player-facing "AP" vocabulary -> swept by PRs #1050
  (`4eaac15b`, "finish killing player-facing AP") and #1116 (`4f4715d3`,
  "kill the last player-facing AP"); `docs/GLOSSARY.md` exists; blocking guard
  test `test_no_stale_ap_vocabulary.gd` locks it. Remaining "AP" strings are
  historical patch notes and the dev overlay, both ruled legitimate by that
  test.
- **#1067** releases ship a stale `build_stamp.txt` -> CI exports now route
  through `tools/build_release.py` (which runs `write_build_stamp.py` and
  proves freshness), per PR #1114 (`d0cf8e30`);
  `.github/workflows/enhanced-release.yml:160-181` documents exactly this.
- **#1072** `build_release.py` hardcodes `PDoom.exe` -> output filename is now
  derived from the preset's own `export_path` in `export_presets.cfg`
  (`tools/build_release.py:31-32,118-128`), PR #1099 (`129545ea`).
- **#1068** Linux download button 404s -> same PR #1099 publishes the Linux
  alias. (The website half was the button target; the release-asset half is
  what this repo owed.)
- **#1023** LEAGUE-CRITICAL: game does not initialise on launch -> overtaken
  by events: [Gate 4] was earned on a proven 0.13.2 build, the league ran on
  it 07-31, and every playtest since (#1041 on 07-30, #1085 on 08-01, #1132 on
  08-05) records full live runs. Whatever the 07-29 boot failure was, the
  shipped thing starts. Close with a pointer to #1026 (the five-whys is the
  remaining obligation, and it is a separate issue).

## DONE ALREADY -- likely, one check each before closing (15)

- **#957** operator name + own-row highlight -- PR #1133 (`a8a858ec`)
  references it; `leaderboard_screen.gd:555` highlights the just-set row.
  Check: operator name renders on the board.
- **#958** lab-name variety + random default -- the lab-name generator shipped
  in #1133, and #1135 was filed as the future content pass, which implies the
  core landed. Check #1135 covers the remainder, then close as superseded.
- **#1063** set player + lab name on the first screen -- PR #1133's title is
  "one-time default-name prompt at upload"; check that satisfies Pip's
  intent (prompt-at-upload vs first-screen field).
- **#793** office staff all render as the same oversized sprite -- shrink
  landed in PR #1081 (`2780f50c`, "(#793)"); worker variant pool landed via
  #922/#947/#969. Check: distinct appearance_id -> distinct sprites live.
- **#801** narrative cold-open + first-turn direction --
  `cold_open_sequence.gd` ships and is marked "#801 SHIP-NOW CORE"; #1130
  landed turn-1 direction; #1136 fixed the copy. Check for unshipped sub-items.
- **#791** early lease spend / office lock-in -- landed in `9abe20a7`
  ("3-office lease decision + lock-in ... (#791 #811)").
- **#811** Workshop 3 -- it happened (07-27..29; day-log `30202936`, split
  `7658a2df`). An event issue whose event occurred.
- **#900** pre-WS-3 art ramp -- executed across the 07-26/27 generation days
  (a dozen commits reference #900). Event occurred.
- **#925** W3 pre-build engineering -- same: W3 is over.
- **#600** dev overlays can't read live game state -- #1134 (filed 08-06)
  shows F3 reading state and injecting events, and `test_debug_overlay.gd`
  regression-tests the errors tab (#600's symptom). Check the nudge-button
  wiring sub-item, then close.
- **#619** achievements skeleton -- achievement toasts shipped and were
  visually fixed in v0.13.2 (`16c9cb5b`). Check observer-only scope, close.
- **#802** in-game music controller -- PR #1129 (`2f40d5df`) shipped "a music
  player". Check whether it is the dev-gated one or player-facing; if
  dev-only, keep open but re-scope.
- **#929** art verdict provenance -- `f239af06` ("track the verdict state --
  2,713 human judgements were one disk failure from gone") looks like exactly
  this. Check append-only capture, close.
- **#1026** post-league mortem on #1023 -- postmortem docs merged
  (`e086d9eb` eleven findings, `8167566f`, `ecc12773`). Check the five-whys
  specifically covers the boot failure; if yes close, if no it stays.
- **#1102** what pdoom1 wants from pdoom-data -- the memo shipped in
  `149ffad2` ("docs(memos): #1106, #1102"). Check the memo answers the ask.

## STALE / OVERTAKEN -- premise changed, close or re-file (19)

Turn = ONE MONTH ruling (#1125, 2026-08-05) and the UI architecture doc
(`docs/design/UI_ARCHITECTURE_2026-08-06.md`) do most of the retiring here.

- **#798** Buy Compute submenu -- ABSORBED by the UI architecture doc, by
  name ("#798 is ABSORBED rather than rejected").
- **#622** main_ui decomposition build lane -- superseded by the same doc's
  phased plan (Phase 1 IS this, with a current map).
- **#763** strategic-options unlock at month grain -- turn IS a month now;
  the retime lane (#1125) owns pacing surface language.
- **#803** conferences days-granularity fine-tuning -- same: days-granularity
  reasoning predates turn=month. Needs re-ruling, not this issue.
- **#789** hiring onboarding as "AP-sink prompts" -- AP was deleted (#996);
  the surviving intent lives in #1091 + UI arch Phase 2.
- **#577** UI jitter on hover -- re-observed as #1132's "mouse-over jiggle";
  UI arch Phase 1 owns the componentized fix.
- **#794** PLAN gantt bigger font -- the Plan screen is being rebuilt whole
  (#1043, UI arch Phase 4); a font tweak to the old screen is dead work.
- **#828 / #830 / #954** hiring queue-visibility / statefulness / full
  candidate card -- all absorbed into UI arch Phase 2's candidate-card
  pipeline (the doc claims them).
- **#936** attention items force menu compaction -- UI arch Phase 1 geometry
  contract owns this.
- **#1132** playtest 655/C55 memo -- its items are distributed: cap-of-10 and
  submenus into the UI arch doc, month review into #1100 (landed), jiggle
  into Phase 1. Close as consumed input.
- **#186 / #187 / #188** media / regulations / geopolitics systems -- filed
  January against v0.2 (the pygame game). The engine, economy, and design
  language have all been replaced. Re-file from current premises if wanted.
- **#437** automated blog publishing -- superseded by #1009's narrower
  draft-generator ruling (never auto-publish).
- **#500** Research Quality (Rushed/Standard/Thorough) -- superseded by #1090:
  the ruling moved quality to research-project level; #500 describes the
  global-toggle world.
- **#805** macOS/Linux tester builds -- folded into #917 (robust cross-OS
  releases) + #1071 (macOS never verified); keeping three copies of one
  problem open is how 201 happens.
- **#1018** ADR supersession scan -- folded into #1049 (ADR
  correctness/staleness/cohesion pass), which is broader and newer.

## DRIVE-BY -- fixed in this PR (7)

#1062, #1035, #1032, #1029, #700, #882, #1064 -- details in the PR body. All
player-visible or run-protecting, none touching simulation, events data, art
tooling, or the #1120 keyboard surface.

**#1134 was an eighth and is withdrawn.** This PR carried a phase guard on the
F3 event injection. Pip ruled the fix is to REMOVE the debug event-trigger, not
to guard it, and #1143 landed that removal before this branch rebased -- so the
guarded functions no longer exist. #1134 is fixed on main by #1143, not here.
The general lesson is the one this whole document is about: two branches open on
one issue at once, and the merge order decides which fix is real.

## DRIVE-BY -- still available, next batch (8)

- **#1046** main-screen ladder-fork warning (draft copy is in the issue).
- **#1017** ship a FIRST-RUN.txt in the release zip (macOS instructions
  currently reach nobody).
- **#1053** `build_release.py` refuses stale/dirty trees.
- **#1128** `sync-documentation.yml` stops `git add .` in a foreign checkout.
- **#812** leaderboard shows lab + operator name by default (display-only if
  the entry already carries both -- check first).
- **#1066** hide `test-*` seeds from the public seed filter; make Clear Local
  Scores clear them.
- **#1086** onboard-now tooltip: include the Attention cost + format money
  (verify whether the costs dict or only the tooltip is wrong -- if the dict,
  it grazes sim behaviour and needs more care).
- **#753** docs typographic ASCII sweep (mechanical, low value, safe).

## NEEDS PIP -- blocked on his decision (27)

Overdue flag first: **#1061 IP/trademark follow-up was DUE Monday 2026-08-03**
and is still open three days later. He asked to be forced.

Decision-shaped: #526 (find the CSIRO retro UI -- only he knows what he saw),
#529 (parked CRT aesthetic -- unpark or kill), #786 (CREDITS names), #808
(dated reflective review, on/after 08-24), #823 (layered-league liveops
policy), #889 (schedule architecture week), #950 (creative harvest --
pick or discard), #961 (candidate pool cap -- W3 was supposed to rule it;
did it?), #984 (schedule the audit-mechanics workshop), #1004 (parked
upgrade mechanics review), #1015 (AI-art positioning stance), #1025 (gate
ordering ritual), #1027 (guarded-cycle process design), #1038 (trust
declarations scope), #1052 (DQ-21 event data shape), #1065 (undiagnosed
"critical ladder bug" -- only he can say what he meant), #1093 (art review
decision session -- the assets are unblocked, the session needs him).

Close-when-consumed records: #1074, #1075, #1076, #1077, #1078, #1094
(postmortem inputs -- close when the postmortem is declared done), #1097,
#1111, #1112, #1131 (ruling records -- close as their lanes execute; #1111 is
being executed by the retime lane right now).

## REAL WORK -- genuine, sized, waiting (116)

Grouped; full numbers so nothing hides.

- **Owned by running lanes (do not touch):** #825, #986, #967, #1016 (event
  retime lane); #567, #575, #602, #1028, #1011 (keyboard/nav, PR #1120);
  #934, #745, #848, #850 (art tooling); #1043, #1090 (UI arch phases 3-4);
  #1125 (the retime GO itself).
- **Player-facing bugs/UX, unowned:** #565, #578, #595, #601, #603, #703,
  #707, #714, #755, #777, #790, #855, #880, #881, #882-siblings, #955, #1031,
  #1033, #1034, #1041, #1044, #1064-residue, #1085 -> fold into #820 (window
  modes -- the minimise bug is unspecified window-mode behaviour; #820 is the
  fix vehicle), #1086, #1088, #1089, #1091.
- **Leaderboard/league integrity:** #648, #700-siblings, #788, #812, #1012,
  #1042, #1046, #1066.
- **Release/deploy/infra:** #506, #545, #608, #723, #724, #810, #917, #962,
  #994, #1008, #1009, #1014, #1017, #1020, #1036, #1053, #1055, #1056, #1057
  (+ dup #800 -- same defect, website intake now exists; consolidate), #1070,
  #1071, #1115, #1117, #1128.
- **Design epics / future epochs (parked by intent):** #236, #467, #471,
  #473, #475, #476, #508, #528, #574, #579, #613, #614, #615, #621, #804,
  #809, #813, #814, #819, #820, #822, #824, #826, #833, #894, #903, #912,
  #913, #923, #924, #940, #944, #951, #953, #956, #987, #1004-siblings,
  #1024, #1049, #1088-design-half, #1092, #1109, #1113, #1121, #1135.
- **Docs/observability:** #721, #722, #815, #816, #817, #818, #826, #1009,
  #1049.

Consolidation candidates inside REAL WORK (each merge shrinks the count
honestly): #800+#1057 (bug reports), #812+#957-residue+#1042 (leaderboard
identity), #820+#1085 (window modes), #917+#1071 (cross-OS).

---

*Generated as part of the 2026-08-06 drive-by PR. Buckets are a snapshot;
the DONE-verified evidence was checked against main at `78be0370`. Do not
hand-maintain this file -- re-run the triage instead.*

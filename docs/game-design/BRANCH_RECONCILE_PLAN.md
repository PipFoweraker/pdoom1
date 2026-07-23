# Branch Reconcile Plan -- fable/no-emoji-enforcement vs origin/main

Date: 2026-07-23 (pre-Friday-v0.13 investigation, READ-ONLY -- nothing merged yet).
Evidence: `git fetch origin` run fresh; all counts below from that fetch.
Merge-base: `b21d52d4` "docs(design): DQ-34 -- leaderboard disclosure tiers" (2026-07-21).

## 1. Divergence size

`git rev-list --left-right --count origin/main...HEAD` -> **28 (main-only) vs 10 (branch-only)**.

- main since base: 2995 files changed, +13334/-10644 (mostly art/asset moves + the
  ASCII purge + v0.12.0 features).
- branch since base: 100 files changed, +7717/-341.
- The branch is **LOCAL-ONLY** (no `origin/fable/no-emoji-enforcement`), so history
  rewriting is technically allowed -- but see section 4 for why merge still wins.
- `git cherry origin/main HEAD` marks all 10 branch commits `+` (none patch-identical
  to main), BUT two are *semantic* duplicates that main landed independently:
  - branch `a53bd649` leaderboard crash fix == main `e4c1d6ab` (#779). Already
    converged: `scene_transition.gd`, `check_scene_nav.py`, `build_release.py` are
    byte-identical between HEAD and origin/main (verified, diff empty).
  - branch `a274a09d`/`7e74e651` enforce-standards work overlaps main `fbe84aea`
    (#751 blocking no-emoji + godot-tree purge). NOT converged -- real conflict.

Branch-only content (this session's work): cold-open onboarding #801, portal shader
+ F6 harness, incremental enforce-standards + cp1252/converter fixes, copy corpus,
design docs, plus **UNCOMMITTED** version-split (ladder_version.txt,
check_ladder_bump.py, sync_version.py edits, board-key split in leaderboard files)
and #789 (hiring_pipeline +291 lines, month_controller, window_resolver, tests).

Main-only content the branch lacks (v0.12.0): version SSOT bump to 0.12.0
(`26463b`), first-launch welcome overlay + show_hints (#783), A/B layout harness +
ui_layout flag (#778), PLAN header icons (#797), **488MB .pck purge** (#792),
regression-net tests (#780), office floor layer (#765), menu_theme.tres (#749),
art batches (#761/#754/#752), blocking ASCII enforcement + whole-godot-tree
punctuation purge (#751), doom label/modal fixes (#774).

## 2. Conflict hotspots

Trial merge (`git merge-tree --write-tree origin/main HEAD`, no worktree touched)
produces **9 content conflicts + 1 file-location conflict**:

| File | Nature | Risk |
|---|---|---|
| godot/scripts/ui/main_ui.gd | main +304/-80 (icons, A/B harness, doom label, office floor) vs branch +113/-65 committed AND +47/-11 uncommitted (#789/cold-open hint) | HIGH -- the one real hand-merge |
| scripts/enforce_standards.py | main: blocking no-emoji rules (#751) vs branch: incremental mode + cp1252 fix | HIGH -- wrong resolution either re-hollows enforcement or re-slows every local commit |
| .pre-commit-config.yaml | same pair as above | HIGH (same reason) |
| godot/autoload/game_config.gd | main adds show_hints + ui_layout; branch adds last_seen_intro_version / play_intros / show_first_lever_hint; PLUS version stamp 0.11.0 vs 0.12.0; PLUS uncommitted version-split edits | HIGH for the version line (board-key fork = fatal), LOW for the vars (adjacent additions, union both) |
| godot/scripts/ui/settings_menu.gd | main's hints/layout toggles vs branch's play_intros toggle | MED -- union |
| godot/scripts/ui/config_confirmation.gd | both added confirm rows | MED -- union |
| CLAUDE.md, docs/ARCHITECTURE.md, docs/DEVELOPERGUIDE.md | both sides documented their work | LOW -- union |
| FILE LOCATION: godot/assets/dump_october_31_2025/hero-bg-2400w.webp (+.import) | branch added file inside a dir main RENAMED to art_source/ (#792 pck purge) | HIGH consequence, easy fix -- must land in art_source/, and the godot/assets/ copy must NOT resurrect (re-bloats the .pck) |

Second wave AFTER committing the session work: the uncommitted #789/version-split
edits touch 14 files main also changed -- but main's changes to
window_resolver/researcher/month_controller/replay_simulator/game_manager/
verification_tracker/defaults.json are PURELY the #751 ASCII punctuation purge
(verified by diff: em-dash -> `--`, section sign -> `S`). Resolution rule is
mechanical: keep branch semantics, keep main punctuation. leaderboard_screen.gd /
game_over_screen.gd currently auto-merge but the uncommitted edits sit near main's
changed lines -- expect small conflicts there too.

## 3. What v0.12.0 added that a careless merge would RE-BREAK

1. **.pck size**: #792 purged ~488MB and the dump_october_31_2025 dir moved out of
   godot/. A wrong rename-conflict resolution re-ships it in the .pck.
2. **Blocking ASCII enforcement** (#751): resolving enforce_standards.py to the
   branch side alone would silently un-block emoji again -- the exact regression
   this branch was named to prevent. Merge BOTH: main's rules + branch's
   incremental fast-path.
3. **Version SSOT / leaderboard board-key**: branch stamps 0.11.0 everywhere
   (game_config.gd, project.godot, export_presets, welcome.tscn). Taking any
   branch-side version stamp forks the board-key. Resolve to 0.12.0, then run
   `python tools/sync_version.py` and let `--check` prove it. The branch's
   version-split work changes sync_version.py itself -- reconcile deliberately.
4. **show_hints / ui_layout config plumbing** (#783/#778): lives in the same
   game_config.gd/settings_menu.gd regions as the branch's play_intros work;
   dropping either side's block loses a shipped feature.

## 4. Recommended path: (i) MERGE origin/main INTO the branch, then branch -> main

Why not (ii) rebase: 10 commits replayed one-by-one against a main that contains a
DIFFERENT version of the same leaderboard fix and enforcement work -> the same
files conflict repeatedly across multiple replayed commits (main_ui.gd and
enforce_standards.py each appear in 2-3 branch commits). One merge = one
conflict-resolution session against the exact conflict list already enumerated
above by merge-tree. Rebase is only "clean history" -- worthless vs Friday risk.

Why not (iii) cherry-pick onto fresh branch: same repeated-conflict problem as
rebase, plus real risk of silently dropping one of the 10 commits or the
interdependencies between them (cold-open touches game_config + main_ui + settings
across commits). Estimated probability of losing something: ~20-30% vs ~5% for
merge (everything is either in a commit or a conflict marker you must look at).

Merge wins because: single sitting, conflict set known in advance (this doc),
history preserved for bisecting, and the merged result can run the FULL test gate
before main is touched. Branch being local-only removes rebase's one advantage
(no shared-history concern either way).

### Step sequence

1. **Commit the session work FIRST, on the branch, BEFORE any merge.**
   Two commits: (a) version-split (ladder_version.txt, check_ladder_bump.py,
   tools/commit.py + README, sync_version.py, leaderboard_sync/verification_tracker/
   leaderboard_screen + test_board_version_split.gd + .uid), (b) #789
   (hiring_pipeline, month_controller, window_resolver, researcher, replay_simulator,
   game_manager, game_over_screen, main_ui, defaults.json, tests) + the two design
   docs. Stage files EXPLICITLY (never `git add -A`); commit in the foreground with
   zero parallel tool calls (settings.local.json hook trap).
2. `git fetch origin main` (again, immediately before merging).
3. `git merge origin/main` on fable/no-emoji-enforcement. Resolve:
   - main_ui.gd: hand-merge (budget 1-2h; keep main's icon/A-B/doom-label/office
     blocks AND branch's cold-open hint + #789 wiring).
   - enforce_standards.py + .pre-commit-config.yaml: main's blocking rules +
     branch's incremental mode + cp1252 fix. Both must survive.
   - game_config.gd: union all vars; version line -> 0.12.0.
   - settings_menu.gd / config_confirmation.gd / 3 docs: union.
   - hero-bg-2400w.webp(+.import): place under art_source/dump_october_31_2025/;
     confirm nothing re-appears under godot/assets/dump_october_31_2025/.
   - core-file punctuation conflicts: branch semantics + main ASCII punctuation.
4. Version reconciliation: version.txt stays 0.12.0 (bump to 0.13.0 happens as its
   own release commit later, per RELEASE_CHECKLIST); run
   `python tools/sync_version.py` then `--check`; sanity-check ladder_version.txt
   semantics against the 0.12 board-key.
5. Gates on the merged branch BEFORE PR: `python scripts/run_godot_tests.py --quick
   --ci-mode --min-tests 300` AND `--simulation` (sim/replay code was touched by
   #789 -- non-negotiable this time), `python tools/check_scene_nav.py`, full
   enforce-standards scan. Do NOT stage `.import` churn from the test import pass.
6. Push branch, PR -> main, Pip admin-merges. Cut v0.13 from main via
   `python tools/build_release.py` only after the version-bump commit.

Fallback if step 3 goes sideways: `git merge --abort` restores the branch exactly
(work is committed by then), and nothing on main was ever at risk.

# Branch and worktree debt census -- 2026-09-07

Read-only census, machine: this Windows checkout at
`G:\Documents\Organising_Life\Code\pdoom1`. No branch was deleted, no worktree
was pruned or moved, nothing was committed or pushed. Every verdict below names
the exact command that produced it; re-run any of them to check this report,
per the repo's own "assert from source, not summary" rule
(`docs/CLAIM_AUDIT_2026-08-06.md`).

Prior work consulted first, as instructed:
`coordination/SEAT_2026-08-30_pdoom1-branches.md` (2026-08-30, debian-laptop,
`/home/pip/Repos/pdoom1*`) and the "70 unmerged remote branches, 42 with no
PR" figure from coordination issue #119.

## If you only do one thing

**Go to the debian-laptop checkout and look at `fix/identity-truncation`.**
This census cannot reach it -- it is a LOCAL-ONLY branch on a different
machine (`git ls-remote origin refs/heads/fix/identity-truncation` returns
nothing from this machine, checked below) -- but the SEAT file's diagnosis of
it is independently re-confirmed against TODAY's main, from here, right now:

- `godot/scripts/leaderboard.gd:26` on today's `origin/main` (82fa10a1) still
  reads `const BOARD_NAME_MAX_BYTES := 40` -- unchanged since the SEAT file
  was written.
- `godot/scripts/ui/game_over_screen.gd` still builds its identity fields with
  bare `LineEdit.new()` (lines 534, 545) and `grep -n "max_length"` on that
  file returns nothing at all -- the unbounded-name bug is still live.
- `godot/scripts/ui/pregame_setup.gd:206-210` still does
  `lab_name_input.text = random_name; GameConfig.lab_name = random_name`
  verbatim, matching the "Roll desync" the SEAT file named.

So the bug this branch fixes is not fixed, nine days after that was written,
and the fix itself is invisible to every git command run from this machine.
That combination -- confirmed-still-needed, confirmed-unreachable-from-here --
is a worse debt position than anything found on this machine, where the
worst case is "unmerged for a few weeks," not "unmerged and one machine away
from being forgotten entirely."

Second choice, reachable from THIS machine today: `spike-resolve-time-spend`
(local branch, see table below) -- a real, never-PR'd mechanic (per-tick
Attention debit for queued actions), oldest unmerged content found (newest
commit 2026-07-24, six weeks stale), and a branch name that would not match
a `fix/*`/`feat/*`-only filter in a careless cleanup script.

## Scope note -- this is NOT the same inventory as issue #119

`git branch -r` from this machine today lists **13 branches on `origin`**
(excluding `origin/main` and `origin/HEAD`), not 70:

    GIT_TERMINAL_PROMPT=0 git fetch origin --prune
    git branch -r | wc -l    # 15, minus origin/HEAD and origin/main = 13

`git ls-remote --heads origin | wc -l` independently returns 13. This is a
real disagreement with issue #119's "70 unmerged remote branches, 42 with no
PR," and it is not this census being wrong -- the SEAT file itself records
six branches deleted on 2026-08-30, and the sheer number of MERGED PRs found
below (54, all independently verified) shows a large amount of cleanup
landed between #119 being filed and today. **Bias here: trust today's
count over the week-old one; the gap is explained by real merges, not by
missing branches.** Where this census disagrees with #119 is exactly here:
the pile is much smaller today than "70 branches" describes, at least on
`origin`. It may still be true that a snapshot closer to #119's filing date
had 70 -- this census cannot speak to history, only to today.

## Worktree finding not in any prior document: Temp worktrees are emptied husks

`git worktree list` shows 44 worktrees (plus the main checkout). Of the 17
worktrees living under `C:/Users/Pip/AppData/Local/Temp/claude/`, **16 have
had every tracked file's content deleted from disk**, leaving only empty
directory skeletons and the `.git` pointer file. Evidence, reproducible:

    cd "C:/Users/Pip/AppData/Local/Temp/claude/wt-1165fix"
    git status --porcelain | cut -c1-2 | sort | uniq -c
    #    9668 D
    find . -type f | wc -l
    #    1        (only the .git pointer file itself)

The same pattern (`9643`-`9675` files all showing ` D`, 1-2 real files left
on disk) was confirmed for `wt-cal`, `wt-gover`, `wt-rel1411`, `wt-weekplan`,
and by extension the rest of the `wt-*` set below. This looks like Windows
Temp-folder cleanup (AV or OS disk cleanup) reclaimed file contents in
`AppData/Local/Temp`, which is not a durable location, while leaving the git
worktree registration (`.git/worktrees/<name>/`) in the main repo intact.

**This does NOT threaten any commit.** A linked worktree's committed history
lives in the main repo's object database, not in the worktree's own files;
every branch tip named below was read successfully with plain `git log` /
`git diff` from the main checkout regardless of whether its worktree is a
husk. What IS true: those 16 directories are worthless as working
directories right now (any attempt to build or edit in them will fail or
silently operate on nothing) and are candidates for `git worktree remove
--force` once their branch's fate is separately decided (which this census
does, per branch, below) -- removal was NOT performed here per the hard
constraint.

The one exception in that Temp folder, `pdoom1-1331-ascii`, is intact (9855
real files, 43 genuinely modified) and briefly showed `locked initializing`
in one `git worktree list` call and no longer showed it about ten minutes
later in a second call. That is direct evidence of another process actively
creating or operating on that worktree concurrently with this census. **Do
not touch it; its state changed while being observed.** See the LOCKED
table below.

## Category: LOCKED / DO NOT TOUCH

| worktree / branch | evidence | why |
|---|---|---|
| `.claude/worktrees/intro-preview` (`feat/intro-portal-stitch-1112`) | `git worktree list --porcelain` shows `locked initializing` | git-locked |
| `.claude/worktrees/rel-0140` (`release/v0.14.0-L4`) | `git worktree list --porcelain` shows `locked initializing` | git-locked, and a release worktree |
| `Temp/claude/pdoom1-1331-ascii` (`chore/1331-ascii-sweep`) | `git worktree list` showed it `locked` on first read, unlocked ~10 min later on second read; `git status --porcelain` shows 43 real uncommitted modifications, HEAD == `origin/main` exactly | actively changing state during this census -- something else is using it right now |
| `Temp/claude/wt-build1411` (detached HEAD `0dc8adb9`, release v0.14.1 #1180) | `git -C <path> log -1` | detached HEAD tied to a release build, per the task's own "or anything tied to a release" clause -- even though the underlying commit is a confirmed-merged ancestor of main (see SAFE table), the worktree itself is a build artifact |
| `Temp/claude/wt-rel1411` (`release/v0.14.1`) | branch name + worktree name | tied to a release, per the same clause, despite the branch content also being confirmed merged |
| `G:/tmp/pdoom1-rel-0140-build` (detached HEAD `7368e237`, release v0.14.0-L4 #1170) | `git -C <path> log -1`; has `M godot/build_stamp.txt` and one untracked `.uid` file | detached HEAD build worktree tied to a release |

Note: three of these six (`wt-build1411`, `wt-rel1411`, `pdoom1-rel-0140-build`)
would otherwise qualify SAFE TO DELETE by content (their commits are
confirmed-merged ancestors of main, see below) -- they are placed here purely
because of the hard constraint's "tied to a release or an in-flight build"
clause, not because their content is at risk.

## Category: SAFE TO DELETE

Method for every row below: either (a) `git rev-list --count main..<branch>`
returns `0` (every commit on the branch is already an ancestor of `main` by
direct lineage), or (b) the branch has a GitHub PR in state `MERGED`, and
`git merge-base --is-ancestor <PR mergeCommit oid> main` returns true (the
squash/merge commit that landed the PR's content is provably on `main`
today). Command template for (b):

    gh pr view <N> --json mergeCommit -q .mergeCommit.oid
    git merge-base --is-ancestor <oid> main && echo ANCESTOR

### Worktrees safe to remove (branch content proven on main; worktree itself may also be a Temp husk, noted)

| worktree | branch | proof |
|---|---|---|
| `.claude/worktrees/agent-a0862ed0aac42a60c` | `chore/issue-triage-and-driveby` | ahead=0 AND PR #1144 merged, ancestor confirmed |
| `.claude/worktrees/agent-a10397150b529bc54` | `fix/leaderboard-toggle-and-smartscreen` | PR #1127 merged, ancestor confirmed |
| `.claude/worktrees/agent-a113a21864e175c6e` | `fix/action-visibility` | PR #1130 merged, ancestor confirmed |
| `.claude/worktrees/agent-a211530237d213bf9` | `tools/generate-tools-index` | PR #1123 merged, ancestor confirmed |
| `.claude/worktrees/agent-a2804e1ae93df7db7` | `feat/player-identity-and-lab-names` | PR #1133 merged, ancestor confirmed |
| `.claude/worktrees/agent-a2bb15362e1ede0f0` | `fix/ci-uses-build-release` | PR #1114 merged, ancestor confirmed |
| `.claude/worktrees/agent-a33fd8c389079de51` | `fix/keyboard-and-navigation` | PR #1120 merged, ancestor confirmed |
| `.claude/worktrees/agent-a3daedcde238c6a09` | `fix/art-map-second-pass` | PR #1122 merged, ancestor confirmed |
| `.claude/worktrees/agent-a46b2d41431e0c857` | `fix/player-facing-text-and-numbers` | PR #1116 merged, ancestor confirmed |
| `.claude/worktrees/agent-a491659697302ac9b` | `feat/self-updater` | PR #1110 merged, ancestor confirmed |
| `.claude/worktrees/agent-a4d2ae7a22441d8ea` | `chore/retire-dead-paths` | PR #1118 merged, ancestor confirmed |
| `.claude/worktrees/agent-a5e57193550c404e4` | `fix/copy-teaches-the-real-game` | PR #1136 merged, ancestor confirmed |
| `.claude/worktrees/agent-a60b060637508bb75` | `tools/find-dead-code` | PR #1124 merged, ancestor confirmed |
| `.claude/worktrees/agent-a6e140f0a047c54bb` | `nav-rescue` -- **wait, see caveat below** | see caveat |
| `.claude/worktrees/agent-a71a4c2a3c6da1833` | `fix/syntax-gate-compiles` | PR #1119 merged, ancestor confirmed |
| `.claude/worktrees/agent-a88b66ca2f2b2a91a` | `fix/dev-overlay-in-release` | PR #1129 merged, ancestor confirmed |
| `.claude/worktrees/agent-adb457d779ca16eda` | `feat/event-retime-and-promotions` | PR #1137 merged, ancestor confirmed |
| `.claude/worktrees/agent-add3730b0c0261b7e` | `fix/art-promotion-pipeline` | PR #1107 merged, ancestor confirmed |
| `.claude/worktrees/agent-afd05352ff54b0768` | `tools/action-taxonomy-checker` | PR #1139 merged, ancestor confirmed |
| `.claude/worktrees/chronicle` | `docs/chronicle-2026-08-06_07` | PR #1167 merged, ancestor confirmed |
| `.claude/worktrees/credits-cats` | `feat/credits-screen-cats` | PR #1161 merged, ancestor confirmed |
| `.claude/worktrees/music-pause-menu` | `feat/pause-menu-music-controls` | PR #1146 merged, ancestor confirmed |
| `.claude/worktrees/pause-menu-legibility` | `feat/pause-menu-legibility` | PR #1155 merged, ancestor confirmed |
| `.claude/worktrees/postmortem-0807` | `docs/postmortem-2026-08-07-capture` | PR #1169 merged, ancestor confirmed |
| `.claude/worktrees/retire-debug-event-trigger` | `fix/1134-retire-debug-event-trigger` | PR #1143 merged, ancestor confirmed |
| `Temp/claude/wt-1165fix` (husk) | `fix/1165-changelog-and-dead-writes` | PR #1194 merged, ancestor confirmed |
| `Temp/claude/wt-1181` (husk) | `fix/1181-sim-timeout-flag` | PR #1192 merged, ancestor confirmed |
| `Temp/claude/wt-cal` (husk) | `feat/commitment-calendar` | PR #1197 merged, ancestor confirmed |
| `Temp/claude/wt-gameover` (husk) | `ui/game-over-legibility` | PR #1179 merged, ancestor confirmed |
| `Temp/claude/wt-ladder1178` (husk) | `fix/1178-arm-ladder-guard` | PR #1184 merged, ancestor confirmed |
| `Temp/claude/wt-lbfix` (husk) | `fix/gameover-optout-visible` | PR #1172 merged, ancestor confirmed |
| `Temp/claude/wt-lbvis` (husk) | `fix/leaderboard-visibility-set` | PR #1173 merged, ancestor confirmed |
| `Temp/claude/wt-playername` (husk) | `fix/leaderboard-player-name` | PR #1176 merged, ancestor confirmed |
| `Temp/claude/wt-rn1165` (husk) | `guard/1165-release-notes` | PR #1183 merged, ancestor confirmed |
| `Temp/claude/wt-shareset` (husk) | `feat/art-share-set` | PR #1166 merged, ancestor confirmed |
| `Temp/claude/wt-ws2seal` (husk) | `docs/workshop-2-position` | PR #1191 merged, ancestor confirmed |

**Caveat on `agent-a6e140f0a047c54bb` / `nav-rescue`:** local branch
`nav-rescue` has NO merged PR under that name and `git rev-list --count
main..nav-rescue` = 2 (not 0). `git diff main...nav-rescue --stat` shows a
real 1010-line diff including a whole test file
(`test_navigation_principles.gd`) not present on main. Its sibling
`fix/keyboard-and-navigation` (PR #1120) IS merged and covers similar
ground, but `nav-rescue`'s own content is NOT proven present. **This one
does not belong in SAFE TO DELETE -- moved to CANNOT DETERMINE below; the
table row above is wrong and is left in only so the correction is visible
rather than silently fixed.**

### Other local branches safe to delete (no worktree attached)

All below: `git rev-list --count main..<branch>` = 0, or a merged PR with
ancestor-confirmed merge commit (both checked per branch, same commands as
above). Newest-commit date shown for reference only, not for the verdict.

| branch | proof | newest commit |
|---|---|---|
| `feat/art-review-v3-vocabulary` | ahead=0 (also confirmed via `git branch --merged origin/main`) | 2026-08-14 |
| `copy-review-pack-2026-08-09` | ahead=0 AND PR #1195 merged, ancestor confirmed | 2026-08-09 |
| `log-saturday-items` | ahead=0 | 2026-08-08 |
| `monday-stack-2026-08-10` (LOCAL branch -- see the ORIGIN branch of the same name in HAS UNIQUE WORK, they differ) | ahead=0, tip is content of merged PR #1192 | 2026-08-10 |
| `nav-baseline` | ahead=0 | 2026-08-06 |
| `recover-seat-voice` | ahead=0 | 2026-08-07 |
| `pr/1238` (a ref, not a normal branch) | PR #1238 (`provenance/author-and-reviewer-fields`) merged, ancestor confirmed | -- |
| `art/gallery-study-modes-v2` | PR #1162 merged, ancestor confirmed | 2026-08-07 |
| `art/l2-picks-bridge-1158` | PR #1164 merged, ancestor confirmed | 2026-08-07 |
| `art/run-2026-08-07-queue` | PR #1158 merged, ancestor confirmed | 2026-08-07 |
| `audit/claim-audit-2026-08-06` | PR #1160 merged, ancestor confirmed | 2026-08-06 |
| `audit/phase-guard-class` | PR #1145 merged, ancestor confirmed | 2026-08-06 |
| `chore/issue-mining-2026-08-06` | PR #1153 merged, ancestor confirmed | 2026-08-06 |
| `ci/freshness-force-alarm` | PR #1189 merged, ancestor confirmed | 2026-08-09 |
| `docs/asset-provenance-scope` | PR #1157 merged, ancestor confirmed | 2026-08-06 |
| `docs/laptop-debian-setup` | PR #1199 merged, ancestor confirmed | 2026-08-10 |
| `docs/league-cutover-playbook` | PR #1190 merged, ancestor confirmed | 2026-08-09 |
| `docs/taste-profile-2026-08-06-clean` | PR #1159 merged, ancestor confirmed | 2026-08-06 |
| `docs/workshop-tri-repo-prep-2026-08-06` | PR #1156 merged, ancestor confirmed | 2026-08-06 |
| `fix/release-reminder-permissions` | PR #1177 merged, ancestor confirmed | 2026-08-08 |
| `lane/manifest-seed-patchnotes` | PR #1175 merged, ancestor confirmed | 2026-08-07 |
| `release/v0.14.0-L4` | PR #1170 merged, ancestor confirmed (see LOCKED note: its worktree `rel-0140` and its `G:/tmp` build copy are held for release-tied reasons, but the BRANCH content itself is safe) | 2026-08-07 |
| `release/v0.14.1` | PR #1180 merged, ancestor confirmed (same release caveat as above for its worktrees) | 2026-08-08 |
| `tooling/slot-picker` | PR #1154 merged, ancestor confirmed | 2026-08-06 |
| `origin/feat/art-review-v3-vocabulary` (remote copy) | `git branch -r --merged origin/main` lists it directly | 2026-08-14 |

Plus **20 local `worktree-agent-a*` branches**, all with `git rev-list
--count main..<branch>` = 0 (checked as a batch): `worktree-agent-a0862ed0aac42a60c`,
`a10397150b529bc54`, `a113a21864e175c6e`, `a211530237d213bf9`,
`a2804e1ae93df7db7`, `a2bb15362e1ede0f0`, `a33fd8c389079de51`,
`a3daedcde238c6a09`, `a46b2d41431e0c857`, `a491659697302ac9b`,
`a4d2ae7a22441d8ea`, `a5e57193550c404e4`, `a60b060637508bb75`,
`a6e140f0a047c54bb`, `a71a4c2a3c6da1833`, `a88b66ca2f2b2a91a`,
`adb457d779ca16eda`, `add3730b0c0261b7e`, `afa5e8e7ecba756d2`,
`afd05352ff54b0768`. These are leftover tracking-branch names for the
`agent-*` worktrees above (one, `afa5e8e7ecba756d2`, has no worktree left at
all -- an orphaned branch pointer only).

Also, three `pr1144` / `pr1154` / `pr1155` / `pr1179`-style local branches
looked at first glance like duplicates of already-merged siblings by tip
subject line, but **do not go in this table** -- see CANNOT DETERMINE, they
are provably NOT ancestors and carry real, sizeable diffs.

## Category: HAS UNIQUE WORK

Every row: `git rev-list --count main..<branch>` > 0 AND no merged PR found
by exact head match (`gh pr list --head <branch> --state all`) AND
`git diff main...<branch> --stat` shows real content.

| branch | commits ahead | newest commit | what it is |
|---|---|---|---|
| `origin/fix/null-reaction-guard` | 1 | **2026-08-30** (newest of any unmerged item found) | has OPEN PR #1339 already -- low loss-risk, just needs review/merge |
| `origin/budget/rulings-2026-08-24` | 2 | 2026-08-24 | has OPEN PR #1291 already -- low loss-risk |
| `origin/monday-stack-2026-08-10` (REMOTE -- distinct from the local branch of the same name, which is fully merged, see SAFE table) | 1 | 2026-08-10 | adds `docs/MONDAY_STACK_2026-08-10.md` (776 lines) and a runsheet HTML never merged |
| `docs/week-2026-08-10-plan` (local; also on `origin`; also has worktree `wt-weekplan`, a Temp husk) | 1 | 2026-08-09/10 | adds `docs/design/WEEK_2026-08-10_PLAN.md` (384 lines) + `tools/runsheet/week-2026-08-10-plan.html` (362 lines) -- note an untracked copy of this exact HTML sits in the working tree right now (`git status` at session start) |
| `fix/game-over-leaderboard-route` (local; also on `origin`; also has worktree `wt-gover`, a Temp husk) | 1 | 2026-08-07 | adds `test_game_over_leaderboard_route.gd` (140-line test, not on main) plus a route fix; main DOES already have a `_continue_to_leaderboard` path (via later, differently-scoped PRs #1172/#1173), so part of this may be superseded -- the test file specifically is not duplicated anywhere on main |
| `jira-export-2026-08-10` | 1 | 2026-08-10 | one file, `docs/jira/export_2026-08-10.jsonl` (209 lines) -- a data dump, low mechanical risk either way |
| `fix/release-sync-dispatch-guard` | 1 | 2026-08-08 | one file, `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md` (77 lines) |
| `docs/recording-guide-levels` | 1 | **2026-07-31** (oldest unmerged item found) | one file, `docs/guides/RECORDING_SETUP_OBS.md` (62 lines) |
| `spike-resolve-time-spend` | 2 | **2026-07-24** (second-oldest, and never had a PR at all) | `feat(l3): per-tick action resolution -- queued cards resolve over day-ticks` + `spike(attention): move Attention debit from queue-time to resolve-time` -- a real mechanic change, see "if you only do one thing" |
| `fix/changelog-honesty-1165` (origin only, PR #1187 CLOSED not merged) | 1 | 2026-08-09 | adds `scripts/check_changelog_claims.py` (does not exist on main) -- but issue #1165 is closed and a DIFFERENT branch (`fix/1165-changelog-and-dead-writes`, PR #1194) landed a changelog fix instead; likely superseded, worth a diff read before reviving, not a blind cherry-pick |
| `fix/ladder-bump-guard-1178` (origin only, PR #1185 CLOSED not merged) | 1 | 2026-08-09 | main's `tools/check_ladder_bump.py` already has `--self-test` (12 hits for the term) via the DIFFERENT merged branch `fix/1178-arm-ladder-guard` (PR #1184) -- likely superseded, same caveat |
| `fix/sim-timeout-flag-1181` (origin only, PR #1186 CLOSED not merged) | 1 | 2026-08-09 | main's `scripts/run_godot_tests.py` already has `DID NOT COMPLETE` (2 hits) via the DIFFERENT merged branch `fix/1181-sim-timeout-flag` (PR #1192) -- likely superseded, same caveat |

## Category: CANNOT DETERMINE

| item | what is unresolved | command that would settle it |
|---|---|---|
| `nav-rescue` (worktree `agent-a6e140f0a047c54bb`) | 2 commits ahead, real 1010-line diff including a whole test file, no merged PR found under this name; overlaps `fix/keyboard-and-navigation` (already merged) but is not proven identical or subsumed | `git diff main...nav-rescue -- godot/tests/unit/test_navigation_principles.gd` then confirm by name whether that test exists anywhere on main today (`find godot/tests -name test_navigation_principles.gd`) |
| `pr1144` | 1 commit ahead, real 487-line diff (incl. `scripts/check_no_emoji.py`), tip is NOT an ancestor of main, no PR found by exact head match even though its subject closely echoes merged PR #1144 (`chore/issue-triage-and-driveby`) | `git diff chore/issue-triage-and-driveby...pr1144 --stat` to see what, if anything, `pr1144` adds beyond the branch that actually merged |
| `pr1154` | 3 commits ahead, real 2154-line diff, tip NOT an ancestor; near-identical tip SHA history to merged `tooling/slot-picker` (PR #1154) but not proven identical | `git diff tooling/slot-picker...pr1154 --stat` |
| `pr1155` | 2 commits ahead, real 905-line diff (incl. `test_music_player_controls.gd`), tip NOT an ancestor; subject echoes merged `feat/pause-menu-legibility` (PR #1155) | `git diff feat/pause-menu-legibility...pr1155 --stat` |
| `pr1179` | 2 commits ahead, real 1289-line diff, tip NOT an ancestor; subject/tip-era matches merged `ui/game-over-legibility` (PR #1179) but content not proven identical | `git diff ui/game-over-legibility...pr1179 --stat` |
| `fix/exploit-001-fire-desk`, `fix/identity-truncation`, `chore/dead-code-sweep`, `fix/adr-0015-doom-literals` (the four "protected" branches from the 2026-08-30 SEAT file) | Confirmed **not present on `origin`** from this machine (`git ls-remote origin refs/heads/<name>` returns empty for all four) and not present as local branches here either -- they exist only on the debian-laptop checkout named in that file, which this census cannot reach | On debian-laptop: `cd /home/pip/Repos/pdoom1 && git branch --list 'fix/identity-truncation' 'fix/exploit-001-fire-desk' 'chore/dead-code-sweep' 'fix/adr-0015-doom-literals'` plus the worktree paths named in the SEAT file, to confirm they still exist and re-run the SEAT file's own merge-tree/ahead checks against today's main |
| Whether any of the 16 emptied "husk" Temp worktrees have SEPARATE uncommitted work that existed before the disk wipe | The wipe destroyed the evidence; nothing on disk can answer this now | None -- if a shadow copy, VSS snapshot, or antivirus quarantine folder retained pre-wipe copies of `Temp/claude/wt-*`, that is the only remaining avenue, and it degrades over time |
| Exact trigger and timing of the Temp-folder file wipe | Pattern is consistent with a Windows Temp-cleanup/AV sweep but no log was inspected for this census | Check Windows "Storage Sense" settings/history and any AV quarantine/cleanup log around the dates these worktrees were last touched (their directory mtimes, e.g. `wt-1165fix` at 2026-08-22 13:17) |

## Summary of counts

- Remote branches on `origin` today (excl. `main`/`HEAD`): **13** (fetched
  and pruned fresh; disagrees sharply with issue #119's "70 unmerged,
  42 no PR" -- real cleanup landed since, see scope note above).
- Local branches examined: **90** (excl. `main`).
- Worktrees examined (excl. main checkout): **44**.
- LOCKED / DO NOT TOUCH: **6** worktrees (2 git-locked, 1 actively
  changing state mid-census, 3 release-build-tied).
- SAFE TO DELETE: **19 worktrees** + **~63 branches** (54 independently
  ancestor-proven via merged PR, plus ~9 more via direct `ahead=0`
  ancestry, including 20 `worktree-agent-a*` names), all with the exact
  command shown per row.
- HAS UNIQUE WORK: **11 branches**, two of them (`fix/null-reaction-guard`,
  `budget/rulings-2026-08-24`) already tracked by an open PR and therefore
  low-risk; the rest are the actual debt worth a human look, oldest being
  `spike-resolve-time-spend` (2026-07-24) and `docs/recording-guide-levels`
  (2026-07-31).
- CANNOT DETERMINE: **5 named local branches** (`nav-rescue`, `pr1144`,
  `pr1154`, `pr1155`, `pr1179`), **4 branches named in the prior SEAT file
  that are unreachable from this machine**, plus open questions about the
  Temp-folder file wipe.

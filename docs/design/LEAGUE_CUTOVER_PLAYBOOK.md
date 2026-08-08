# League cutover playbook

**What this is.** A phase-by-phase procedure for cutting a league epoch, built
from the two cutovers the estate actually ran and instrumented on 2026-08-07
(`v0.14.0`, an epoch fork L3 -> L4, and `v0.14.1`, a same-epoch patch). It exists
because Pip asked, 2026-08-09:

> "we also want to start accommodating our predictable build, uplift and
> deployment times into any public facing league scheduling announcement. Can we
> get things properly queued up and then do a relatively hard and fast cutover,
> from a player's perspective"

**The short answer to that question is: not yet, and this document says exactly
which piece is missing.** The machine half of a cutover is predictable to within
ten seconds. The half that decides what a player sees on pdoom1.com has never
once been observed completing without a human dispatching workflows by hand.

**Evidence rule.** Every duration below traces to a run ID, a git object, a
GitHub API timestamp, or a named issue. Anything derived rather than observed is
marked **ESTIMATE** and shows its derivation. Anything unobserved is marked
**UNMEASURED** and is not smoothed into an average. This document will be quoted
back as fact in a public schedule, which is the specific failure mode this seat
spent 2026-08-06/08 cataloguing (`docs/POSTMORTEM_2026-08-07_CAPTURE.md` F5:
six of 68 headline claims published in one day were wrong).

**Clock.** All times UTC unless suffixed AEST. Local dev machine is `+10:00`.

**Companions, and what this extends rather than replaces.**

- `docs/RELEASE_NOMENCLATURE.md` -- CANONICAL definitions of Seed / Epoch /
  Theme and the fork rule. Unchanged by this document.
- `docs/RELEASE_AND_LEAGUE_CYCLE.html` -- **the existing epoch-cut runbook**
  (section 5, written for the L1 -> L2 cut). It already has the mechanical
  sequence: bump both numbers in one release commit, `sync_version.py --check`,
  `tools/build_release.py`, the backend step that aliases the legacy board and
  points the featured board at the new key, `gh release create --target main`,
  announce. **This playbook adds the four things it does not have**: a tagging
  step with SHA verification (6.1 is what its absence cost), a live-site
  freshness verification step (6.2/6.3), a playtest gate before publish (6.4),
  and measured durations. It is also still written L1 -> L2 while the estate is
  at L4, and is pinned for reflective review on/after 2026-08-24.
- `docs/RELEASE_CALENDAR.html` -- calendar only, rendered 2026-07-26, and
  **factually wrong for the window this document measures**: it schedules
  Fri 2026-08-07 as "epoch -> L3". The actual cut was L3 -> L4 (`ladder_version.txt`
  reads `4`). Same off-by-one as #1152, which does not name this file.
- `.github/RELEASE_CHECKLIST.md` -- predates CI-side building (it still says
  "Open Godot ... Project -> Export"); the build now happens in
  `enhanced-release.yml`. Stale in places.

**Version SSOT paths, because they are easy to guess wrong:** `version.txt` and
`ladder_version.txt` are both at the **repo root**, not under `godot/`. They read
`0.14.1` and `4` on `origin/main` at the time of writing.

---

## 1. The measured timeline

### 1.1 `v0.14.0` -- the epoch cut (L3 -> L4, seed roll to `weekly-2026-w32`)

| UTC | Elapsed from tag | Event | Source |
|---|---|---|---|
| 11:51:30 | -56:03 | PR #1170 opened, branch `release/v0.14.0-L4` | `gh pr view 1170 --json createdAt` |
| 11:51:34 -> 11:58:03 | | `Godot Tests` on the release PR, **6m29s** | run `31175769588` |
| 12:21:09 | -26:24 | website `Auto-Update Data` scheduled run. Latest release was still `v0.13.2`. **Correct when it ran; stale 31 minutes later.** | website run `31177816316` |
| 12:44:38 | -02:55 | PR #1170 merged -> `7368e237` | `gh pr view 1170 --json mergedAt` |
| **12:45:53** | **-01:40** | **Tag `v0.14.0` written at `237636d1` -- the WRONG COMMIT, on an art branch.** See 6.1 | tag object `64588f82`, tagger `1786106753 +1000` |
| 12:45:58 -> 12:50:02 | | Release workflow runs on the wrong commit. `Build Godot Game (All Platforms)` **SUCCEEDS**; the run dies at `Generate Release Feeds & Metadata` | run `31179577205` job list |
| 12:46:11 | | `Pre-Release Checks` FAILS on the wrong tag, at step `Check version in project.godot` | run `31179576741` step list |
| 12:46:54 | -00:39 | Wrong tag DELETED (`64588f82 -> 00000000`) | `gh api repos/PipFoweraker/pdoom1/activity` |
| **12:47:33** | **0:00** | Tag `v0.14.0` re-created at `7368e237` | `gh api .../git/tags/88fa91e9...`; `git for-each-ref` -> `2026-08-07T22:47:33+10:00` |
| 12:47:39 -> 12:47:58 | +00:25 | `Pre-Release Checks` **success** | run `31179700716` |
| 12:47:39 -> 12:53:25 | +05:52 | `Enhanced Release` **success** | run `31179700780` |
| **12:52:51** | **+05:18** | **Release `v0.14.0` published on GitHub. A player can download it from this instant.** | `gh release list` |
| 13:45 (approx) | +57:27 | Five defects making the leaderboard effectively invisible are named, from a playtest of the SHIPPED build. See 6.4 | `coordination#40` comment `createdAt` `2026-08-07T13:45:06Z` |
| 13:51:30, 13:56:17 | | Two hand-dispatched website deploys. Site still wrong. | website runs `31184667410`, `31185066840` |
| **14:01:11** | **+1:13:38** | **A human hand-dispatches website `Auto-Update Data`.** | website run `31185482168`, `event=workflow_dispatch` |
| **14:03:49** | **+1:16:16** | **pdoom1.com serves `v0.14.0`.** | website run `31185669845`; timeline corroborated by `pdoom1-website#285` |

**Publish -> site correct: 1h 10m 58s, and only because a person intervened.**
Total PR-open -> site correct: **2h 12m 19s**.

### 1.2 `v0.14.1` -- the patch cut (same board key, no fork)

| UTC | Elapsed from tag | Event | Source |
|---|---|---|---|
| 15:46:41 | -16:15 | PR #1179 merged (first of the two content merges) | `mergedAt` |
| 15:52:52 | -10:04 | PR #1180 opened, branch `release/v0.14.1` | `createdAt` |
| 15:52:56 -> 16:01:28 | | `Godot Tests` on the release PR, **8m32s** -- the long pole of the PR gate | run `31194819397` |
| 16:02:12 | -00:44 | PR #1180 merged -> `0dc8adb9` | `mergedAt` |
| **16:02:56** | **0:00** | Tag `v0.14.1` created at `0dc8adb9` | `git for-each-ref` -> `2026-08-08T02:02:56+10:00` |
| 16:03:10 | +00:14 | `Enhanced Release` starts (run `31195680192`) | `gh run view 31195680192 --json createdAt` |
| 16:03:19 -> 16:03:43 | +00:47 | job: Validate Historical Data & Schemas, **24s** | run job list |
| 16:03:46 -> 16:06:33 | +03:37 | job: **Build Godot Game (All Platforms), 2m47s** -- the whole cross-platform build, freshness-proven, inside CI | same |
| 16:06:36 -> 16:07:13 | +04:17 | job: Generate Release Feeds & Metadata, 37s | same |
| 16:07:16 -> 16:07:48 | +04:52 | job: Create Release Manifest, 32s | same |
| 16:07:57 -> 16:08:30 | +05:34 | job: Create GitHub Release, 33s | same |
| **16:08:24** | **+05:28** | **Release `v0.14.1` published. Downloadable from this instant.** | `gh release list` |
| 16:08:33 -> 16:08:56 | +06:00 | job: Verify Release Download URLs, 23s | same |
| 16:08:39 -> 16:09:04 | +06:08 | job: **Sync Version to Website, green.** The site was still stale for another 17 minutes. | same |
| 16:09:05 | +06:09 | Release workflow completes. **Total 5m55s.** | run `31195680192` `updatedAt` |
| **16:21:21** | **+18:25** | **A human hand-dispatches website `Auto-Update Data`.** | website run `31197159587`, `event=workflow_dispatch` |
| 16:24:39 -> 16:25:02 | | website manual DreamHost deploy | website run `31197423254` |
| **16:26:24** | **+23:28** | **pdoom1.com serves `v0.14.1`.** | website run `31197532818` |

**Publish -> site correct: 18m 00s, and only because a person intervened.**
Total PR-open -> site correct: **33m 32s**.

### 1.3 The whole incident arc

The epoch cut and its corrective patch, treated as one player-visible event:

**`v0.14.0` published 12:52:51Z -> `v0.14.1` live on pdoom1.com 16:26:24Z =
3h 33m 33s.** That is the honest end-to-end for a league cutover that had to be
patched, and being patched is the normal case, not the exception -- both epoch
cuts this estate has done at speed needed one.

**The release-cut lane itself: 1h 38m 24s.** Measured as PR #1173's merge
(14:48:00Z -- the last leaderboard fix before the release lane took over) to
pdoom1.com serving `v0.14.1` (16:26:24Z). That interval contains two PR merges
(#1179, #1180), a hand-checked release body, tag verification, a
freshness-proven cross-platform build in CI, publish, and the hand-dispatched
site update. **Caveat: the lane's own start instant is not machine-recorded.**
14:48:00Z is the best-supported proxy, so treat 1h38m as a reconstruction with a
firm end and a soft start, not a stopwatch reading.

### 1.4 The numbers worth carrying forward

| Phase | v0.14.0 | v0.14.1 | Predictable? |
|---|---|---|---|
| Release PR open -> merged | 53m 08s | 9m 20s | **No.** Human review of the release body dominates; the CI floor is 6-9 min of `Godot Tests` |
| Merge -> tag pushed | 2m 55s | 44s | Manual, small |
| **Tag -> release published** | **5m 18s** | **5m 28s** | **YES. Two samples, 10s apart. This is the only tight number in the pipeline.** |
| Publish -> pdoom1.com correct (hand-dispatched) | 1h 10m 58s | 18m 00s | **No.** Both required a human; the 53-minute spread is the human's reaction time, not the machine's |
| Publish -> pdoom1.com correct (unattended) | never observed | never observed | **UNMEASURED.** See section 3 |

**Godot Tests is the CI long pole everywhere**: 6m29s and 8m32s on the two
release PRs (runs `31175769588`, `31194819397`). Every other pdoom1 check on
those PRs finished inside 2m03s.

---

## 2. What can be pre-staged, and what must happen at cutover

Pip's requirement is *"properly queued up and then a relatively hard and fast
cutover, from a player's perspective."* The mechanical answer, from the tables
above: **the player-visible switch is the release-publish instant, and everything
before it can be pre-staged.** The publish itself is a tag push plus 5m30s.

### 2.1 Pre-stageable -- do these BEFORE the announced cutover instant

| # | Item | Why it can be pre-staged | Evidence it is real work |
|---|---|---|---|
| S1 | **All content PRs merged to main and green.** | The release PR should contain the version bump and nothing else. | `v0.14.1` merged #1179 sixteen minutes before the tag; that ordering is the pattern to keep |
| S2 | **Version + ladder bump prepared on a `release/*` branch**, `python tools/sync_version.py` run, `sync_version.py --check` passing. | Nothing player-visible changes until the tag. | `v0.14.0` did this on `release/v0.14.0-L4` (PR #1170) |
| S3 | **Release body hand-checked in the PR, not after the tag.** | The tag message is the artifact the website reads the board key out of (`pdoom1-website` did exactly that for `v0.14.0`). Fixing it after publish means editing a published release. | `coordination#40`: the website resolved the board key from the tag message, not from the release notes |
| S4 | **`Godot Tests` green on the release branch.** | 6-9 min, and it is the long pole. Running it at cutover puts nine minutes of variance inside the announced window. | runs `31175769588`, `31194819397` |
| S5 | **PLAYTEST THE ACTUAL RELEASE CANDIDATE BUILD.** See 2.3 -- this is the gate that was skipped and it cost `v0.14.1`. | | |
| S6 | **The board key decided and blessed, and `pdoom1-website` told the exact string.** | `docs/LEAGUE_SEED_LEDGER.md` step 2 requires an explicit human blessing before any page may present a seed. Establishing one string on the night took three seats and a since-deleted probe. | `coordination#40`, 2026-08-07/08 |
| S7 | **CHANGELOG section for the version exists.** | `pre-release-checks.yml` hard-fails on a tag whose version is absent from `CHANGELOG.md`. A cutover is a poor time to discover that. | `.github/workflows/pre-release-checks.yml`, step `Check CHANGELOG updated` |
| S8 | **The pre-announcement text agreed with `pdoom1-website`** and scheduled, with the go-live copy drafted but unpublished. Their surface, their call -- see section 5. | | |

### 2.2 Must happen AT cutover (the hard-and-fast part)

| # | Item | Measured cost | Notes |
|---|---|---|---|
| C1 | Merge the release PR | 44s -> 2m55s to the tag | |
| C2 | **Push the tag at the merge commit** | instant | **Verify the SHA before pushing.** Section 6.1 |
| C3 | Wait for `Enhanced Release` | **5m 18s / 5m 28s to publish**; 5m55s to workflow completion | This includes the full cross-platform build (2m47s) |
| C4 | Confirm the release exists with all platform assets | seconds | `verify-release-urls` job does it, +23s |
| C5 | **Make pdoom1.com reflect it** | 18m -> 1h11m, hand-dispatched | **This is the unpredictable step.** Section 3 |
| C6 | Confirm the board key is live and taking scores | minutes | Probe `score_api.php` at the new `(seed, ladder)` |

**Minimum player-visible cutover, if C5 were solved: tag push + 5m30s.**
That is a number a public schedule could be built on. It is not the number today.

### 2.3 The human gate that must not be assumed away

`v0.14.0`'s playtest happened **after** the release published, not before, and
the clock on it is tight:

| From publish (12:52:51Z) | Event | Source |
|---|---|---|
| +27m 28s | First playtest-derived defect filed -- issue #1171, body quoting the ruling as *"Pip, 2026-08-07 ~23:30, during the v0.14.0 playtest"* | `gh issue view 1171 --json createdAt` -> 13:20:19Z |
| +28m 54s | Pip's score reaches the server on `(weekly-2026-w32, L4)`, 147 turns | `coordination#40` quoting `score_api.php`, `date` 23:21:45 AEST |
| +36m 49s | First remediation branch cut, `fix/gameover-optout-visible` | activity log, 13:29:40Z |
| +39m 02s | `coordination#40` filed, summarising the playtest | issue `createdAt` 13:31:53Z |

**The play itself was three ranked runs, one of 147 turns** (PR #1172 body;
issue #1171: *"Pip invested 147 turns tonight before discovering a run produced
nothing"*). `v0.14.1` was tagged 3h 10m after `v0.14.0` published, entirely to
undo what those runs found.

**The playbook rule that follows: the release-candidate build is played, by a
human, before the tag is pushed -- and it is played on the surfaces the release
claims to change.** For a league cutover that means, explicitly, reaching the
global leaderboard and seeing a score land on the new board key. The `v0.14.0`
playtest did play the game; it did not check the surface the epoch cut was about.

**Cost of this gate: UNMEASURED.** The bounds above are publish-to-first-finding,
not session length. No record states how long the three runs took, and the
147-turn run's start instant is not recorded anywhere. Do not put a number on
this in a public schedule until one exists. **What the bounds DO support: a
league-surface playtest returns its first finding inside half an hour.** Treat
that as the floor for scheduling the gate, and put the announced cutover instant
at least a day after the release candidate is built, not the same hour.

**Instrument this on the next cut.** Record the RC build instant, the playtest
start instant, and the playtest end instant. Three timestamps turn the largest
unmeasured cost in this playbook into a number.

---

## 3. The player-visible window, stated honestly

**The truthful sentence today:**

> The release exists on GitHub, downloadable, within about five and a half
> minutes of the tag being pushed. pdoom1.com reflects it somewhere between
> eighteen minutes and several hours later, and the only path that has ever been
> observed working end to end is a person hand-dispatching two workflows on the
> website repo.

**A public schedule cannot be built on that spread.** Not because the spread is
wide -- a wide-but-known window can be announced -- but because **the upper bound
has never been measured.** The two data points are 18m and 1h11m, and both are
measurements of how fast a human noticed, not of how fast the pipeline runs.

### 3.1 What the unattended path would cost, derived

**ESTIMATE. Never observed for a real release.** Derivation, each component
measured separately:

| Component | Value | Source |
|---|---|---|
| website `auto-update-data.yml` cron period | 6h (`cron: '0 */6 * * *'`) | read from that file, recorded in `pdoom1#1182` and `pdoom1-website#285` |
| observed GitHub scheduler slip on that workflow | 10m 54s to 21m 09s | website runs `31177816316` (12:21:09 for a 12:00 slot), `31206454613` (18:20:01), `31271281068` (18:10:54) |
| the deploy does NOT ride the bot push | -- | `pdoom1-website#289` measured this: the deploy that carried `version.json` to production on the `v0.14.0` cut was `workflow_run` off Board liveness, not `push` |
| observed data-run -> deploy gap | 14m 05s | website `Auto-Update Data` 18:20:01 -> `Auto-Deploy to DreamHost` 18:34:06 (run `31207544099`) on 2026-08-07 |
| CDN propagation | UNMEASURED | nobody has instrumented it |

**Worst case, summing the measured components: about 6h 35m.** `pdoom1#1182`
independently derived "call it 6h45m" including CDN and set its alarm tolerance
at 480 minutes on that basis. The brief's "~7h" is the same estimate rounded up.
**All three are arithmetic on cron periods. None is a measurement.**

### 3.2 The event-driven path is proven dead, not merely slow

This is the part that makes the window unpredictable rather than just long.

- `sync-game-version.yml` POSTs `{"event_type": "game_version_sync"}` to the
  website's dispatch endpoint. **Nothing on the website subscribes to it**, and
  the dispatch API returns 204 either way, so the sending side cannot tell.
  Measured by the website seat: `git grep -c game_version_sync` in
  `pdoom1-website` -> zero hits, and
  `gh api "repos/PipFoweraker/pdoom1-website/actions/runs?event=repository_dispatch"`
  -> **empty list. No `repository_dispatch` run has ever executed on that
  repository.** (`pdoom1-website#289`)
- On the `v0.14.1` cut, the `Sync Version to Website` job went **green at
  16:09:04Z** and the site was still stale until **16:26:24Z**. A green sync job
  is not evidence the site is fresh. (run `31195680192` job list)
- `pdoom1-website#289` is the open proposal that would fix this -- add
  `repository_dispatch: types: [game_version_sync]` to `auto-update-data.yml` and
  keep the cron as a backstop. **It is the website's surface and their call.**

### 3.3 What would have to change to make the window predictable

Stated as conditions, not as a design, because the fixes are mostly not ours:

1. **`pdoom1-website#289` lands** (or an equivalent), so a release publish drives
   the site instead of a clock. Their repo, their call.
2. **The ordering hazard named in #289 is closed on our side.** The website
   derives `latest_release.platforms` from the release's actual asset filenames.
   A dispatch arriving mid-upload publishes a version with missing platforms.
   That half is pdoom1's: fire the dispatch after assets are attached, not at
   release-create. Until it is closed, making the pipeline fast makes a new race
   reachable for the first time.
3. **`pdoom1-website#285`'s closing condition passes unattended** -- the live
   site's version equals the latest release tag within 10 minutes of publish,
   with nobody dispatching anything.
4. **The freshness alarm's paths are observed, not assumed.** `pdoom1` PR #1182
   (merged `2026-08-08T20:19:00Z`, `1ddb033d`) added
   `.github/workflows/live-site-release-freshness.yml` -- a 2-hourly
   cache-busted read of the live site with a 480-minute tolerance. **Its alarm
   path has now fired once**: run `31281144601`,
   `2026-08-08T22:12:18Z`, `workflow_dispatch` on branch
   `ci/freshness-force-alarm` -- compare job red, `Alert -- the live site is
   serving a stale release` **success**. That closes the open question logged in
   `docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md` ITEM 4. **The `resolve` path
   is still unexercised** (`Close the rolling issue when the site catches up`
   was skipped), so the guard can still open an issue nothing ever closes --
   which is the shape `pdoom1-website#149`, `#204` and `#230` already
   demonstrated.

**Until condition 3 passes, the honest public phrasing is a soft window, not a
time:** "the new league goes live on Friday; the download is available
immediately and the site catches up shortly after." Do not announce a minute.

---

## 4. Ladder and epoch handling -- what happens to players' scores

This is the question players will actually ask, and getting it wrong destroys
trust in the board permanently.

### 4.1 The mechanics

- The board key is **`(seed, ladder_version)`**. `GameConfig.get_board_version()`
  returns `"L" + LADDER_VERSION`; the seed comes from `FEATURED_SEED_OVERRIDE`,
  a constant compiled into the `.pck`.
- **A patch release cannot move the board key.** No `v0.14.x` could move it off
  `(weekly-2026-w32, L4)`; only an L5 fork can. This was stated to
  `pdoom1-website` on the night and is what let them build against L4 while
  `v0.14.1` was in flight (`coordination#40`).
- Because the seed is a compiled constant, **rolling the seed needs a rebuild**.
  A seed roll is a release, not a config change.
- The fork rule (`docs/RELEASE_NOMENCLATURE.md`): *"Could two identical runs,
  played the same way, produce a different score, trajectory, or RNG stream
  across this change?"* YES -> bump minor and ladder. NO -> patch only.

### 4.2 The sentences the announcement must contain

Not copy -- these are the **facts the copy must convey**, and `pdoom1-website`
owns the wording:

1. **Old scores are not deleted and are not merged.** They remain valid and
   visible under their old board key, as a closed epoch. This is the confirmed
   position: the `v0.14.0` tag message says *"L3 scores remain valid and visible
   under L3"*, and the website's reading -- *"keep reachable as a closed epoch,
   do not merge, do not delete"* -- was confirmed by this seat on
   `coordination#40`.
2. **Runs on the new build are not comparable to the old board.** That is the
   entire point of a fork, and it is why the old board stops moving rather than
   being wiped.
3. **The old board stops accepting new entries in practice**, because shipped
   clients post to the key compiled into them. Nobody's score is "lost"; the
   board is simply finished.
4. **Which board is the live one, by exact key**, so a player can tell whether
   they are looking at history or at the current league.
5. **If the player does not update, their runs land on the old board.** That is
   a real, supported outcome, not an error -- but they should know it before they
   play, not after.

### 4.3 The failure this prevents

On the `v0.14.0` cut, for roughly the first hours after publish, pdoom1.com
presented the **closed** `(weekly-2026-w31, L3)` board -- 6 entries, frozen --
as the live one, while play landed on `(weekly-2026-w32, L4)`, a board the site
never asked about. Anyone following the links Pip published that night saw a
leaderboard that would never move again. (`coordination#40`, filed
`2026-08-07T13:31:53Z`; board counts independently verified against
`score_api.php` by the coordination seat.)

**And the API cannot be used to discover the right key.** All four
seed/version combinations returned `ok=true`, including two that had never
existed. A probe that cannot fail cannot detect that the key changed, and
POSTing to a nonsense key silently creates it -- which is how two junk boards
(`agent-probe-h2-20260807__L4`, `agent-probe-live-20260807__L4`) came to exist
server-side with no delete endpoint.

**Playbook consequence: the new board key is PUSHED to the website as a string,
before the cutover, and never derived by them.** A website-derived seed stranded
23 submissions in July. `release_manifest.json` now emits `league_seed` as a
structured field alongside `ladder_version` (landed in #1175, merged
`2026-08-07T14:30:32Z` -- about twenty minutes after the `v0.14.0` tag, so the
shipped `v0.14.0` manifest does not carry it and `v0.14.1` onward does).
**Assert it as a cutover check:**

```bash
curl -sL <release-asset-url>/release_manifest.json | jq '{ladder_version, league_seed}'
```

---

## 5. The timing contract offered to `pdoom1-website`

The commentary is theirs. This is what pdoom1 undertakes to give them, so they
can pre-announce without saying anything that is not yet true.

| Phase | pdoom1 does | pdoom1 tells the website | Safe for them to say |
|---|---|---|---|
| **T-7d** | Board key decided; blessing obtained | The exact `(seed, ladder_epoch)` strings, and the intended cutover date | "a new league is coming on <date>" |
| **T-1d** | Release candidate built and played (2.3) | Confirm or withdraw the date; state what happens to old scores (4.2) | The date, and the score-continuity facts |
| **T-0** | Merge, verify tag SHA, push tag | "cutover started" | "we are cutting over now" |
| **T+5m30s** | Release published, assets verified | "release published, tag `vX.Y.Z`, board key `(seed, LN)`" -- with the release URL | **The release exists.** This is the first moment anything is true for a player |
| **T+?** | Confirm the live site serves it | the measured lag for this cut | "the site is updated" -- **only after this confirmation** |
| **T+?** | Confirm the new board takes a real score | board key is live | "the new board is open" |

**The rule that makes the contract worth having: the website should never
announce a state pdoom1 has not confirmed.** On the `v0.14.0` cut the reverse
happened in both directions -- links to a stale site were published, and this
seat asserted for eight hours that the site was stale on the strength of a single
`curl` taken **before the release was published** (recorded in
`.github/workflows/live-site-release-freshness.yml`'s own header, which is why
that check now carries a cache-buster and a `no-cache` header).

**What raises the stakes.** The estate has just proven it can publish a release
the site does not reflect for over an hour with every check green. A public
schedule makes that failure **visible to players** rather than merely
embarrassing internally: a player told "live at 8pm" who finds the old version
advertised concludes the board is broken, and that is the one conclusion the
leaderboard cannot recover from. That is the argument for `pdoom1` PR #1182 (the
live-site freshness check -- comparison proven red, alarm path proven once on
2026-08-08, **resolve path still unexercised**) and for `pdoom1-website#289`
(the event-driven path, which is the actual fix rather than the detector).

---

## 6. What went wrong on 2026-08-07/08, and what this playbook does about each

### 6.1 The tag was pushed at the wrong commit

**Measured, not recalled, and undocumented in prose anywhere in the estate until
now** -- the only machine record of the deletion is the GitHub repo activity log.

| UTC | Event | Source |
|---|---|---|
| 12:45:53 | Annotated tag object `64588f82` written, tag `v0.14.0` | `git cat-file -p 64588f82` tagger line `1786106753 +1000` |
| 12:45:57 / 12:45:58 | `Pre-Release Checks` and `Enhanced Release` start on `head_sha=237636d1` | runs `31179576741`, `31179577205` |
| 12:46:11 | `Pre-Release Checks` **FAILS**, at step `Check version in project.godot` | run `31179576741` step list |
| **12:46:54** | **Tag deleted**: `branch_deletion refs/tags/v0.14.0 64588f82 -> 00000000` | `gh api "repos/PipFoweraker/pdoom1/activity?per_page=100"` |
| 12:47:33 | Tag re-created as `88fa91e9` -> `7368e237` | `gh api repos/PipFoweraker/pdoom1/git/tags/88fa91e9...` |

`64588f82` pointed at `237636d1e772e841e41f5f411ee14aa05608e3f8` --
`art(l3): fire the hero wave -- 24 of 140 images landed, the API credit ran out`.
`git merge-base --is-ancestor 237636d1 origin/main` returns non-zero and
`git branch -a --contains 237636d1` names only `art/l2-picks-bridge-1158`:
**the epoch tag was briefly on an art branch that is not on main and never was.**
Total exposure **100 seconds**.

**The worst part is what the wrong tag's message said.** It contained the line:

> "Tagged at `237636d1e772e841e41f5f411ee14aa05608e3f8`, the commit the verified
> artifact is built from."

**A build-provenance assertion, about the wrong commit, in the one artifact the
website reads release facts out of.** That sentence was removed from the
recreated tag rather than corrected, so the surviving `v0.14.0` tag makes no
provenance claim at all.

**Resolved, because it would otherwise sit as an open question:** the published
`v0.14.0` was built from `7368e237`, not from `237636d1`. The release was
created by the `Create GitHub Release` job of run `31179700780`, whose
`head_sha` is `7368e237`
(`gh run view 31179700780 --json headSha`), and `gh api
repos/PipFoweraker/pdoom1/releases/tags/v0.14.0` reports
`author=github-actions[bot]`, `created_at=12:47:33Z`,
`published_at=12:52:51Z`, `target_commitish=main`. The wrong-commit build
completed and was never published.

Two things are true about how it was stopped, and the second is the finding:

- **The right guard fired.** `pre-release-checks.yml` failed at step
  `Check version in project.godot` on the wrong tag (run `31179576741`) and
  passed on the right one (run `31179700716`). That guard did its job.
- **The guard could not have stopped the release.** `pre-release-checks.yml` and
  `enhanced-release.yml` are **independent workflows on the same trigger**;
  nothing in the release workflow waits for the checks workflow. The wrong-commit
  release run (`31179577205`) got through `Validate Historical Data & Schemas`
  and **completed a full cross-platform `Build Godot Game` on the wrong tree**,
  dying only at `Generate Release Feeds & Metadata` at 12:49:57Z. The publish was
  blocked by a downstream feed job, **not** by the guard that correctly
  identified the problem.

**Playbook:** C2 states the SHA verification explicitly, before the push:

```bash
git fetch origin main
git rev-parse origin/main                 # the merge commit of the release PR
git rev-parse <tag>^{commit}              # must be identical
git merge-base --is-ancestor <tag>^{commit} origin/main && echo ON-MAIN
```

**Owed as a change, not made here:** `enhanced-release.yml` should not be able to
build and publish a tag that `pre-release-checks.yml` rejects. Filing that is
outside this document's scope (the brief forbids workflow changes) and it belongs
with whoever owns the release workflow lane.

### 6.2 The site version was mis-stated, in both directions

pdoom1.com served `v0.13.2` while the repo held `v0.14.0`, with green ticks
throughout, while the link was already being shared
(`pdoom1-website#285`, created `2026-08-07T14:11:47Z`, still OPEN, zero
comments). Separately, this seat asserted that the site was stale on the strength
of one `curl` taken **before** the release published -- an assertion that
happened to be true and was not evidence.

**Provenance split, because the two halves are not equally supported.** The
stale-site half is fully evidenced by #285's own timeline table and the release
API. The "eight hours" figure for the second half is **UNVERIFIED**: its only
record is the body of PR #1182 itself, the remediating change, and no
timestamped record of the curl, the span, or the assertion was found in `docs/`,
`dev-blog/`, or any issue thread. It is a self-report inside the fix. Cited here
because the mechanism is real and the number is not established.

**Playbook:** the contract in section 5 says the website announces "the site is
updated" only after pdoom1 confirms it, and confirmation means a **cache-busted
read of the live site**, not a read of the repo file and not a read taken at a
moment somebody chose:

```bash
curl -s "https://pdoom1.com/data/version.json?cb=$(date +%s)" | jq -r .latest_release.version
gh release view --repo PipFoweraker/pdoom1 --json tagName --jq .tagName
```

### 6.3 The guard was aimed at a decoy file

`release-sync-monitor.yml` (ours, daily `cron: '17 6 * * *'`) reads
`repos/PipFoweraker/pdoom1-website/contents/data/current-game-version.json`
through the GitHub API -- a file in the website **repo**, sitting **outside the
rsync source**, so it cannot change what a visitor sees. It has exactly one
reader in the estate: that monitor. **A guard aimed one directory to the left of
the thing it was built to watch**, and it would have reported green throughout
the outage it appears to guard against
(`docs/POSTMORTEM_SATURDAY_ITEMS_2026-08-08.md` ITEM 4).

**Do not delete the decoy file as dead weight** -- it would break the monitor.
`pdoom1#1182` adds the live-site check that asks the real question.

**Playbook:** every cutover check names **which assertion it makes** -- "the
repo has been updated" and "the live site serves that update" are two different
sentences, and the whole bug was conflating them.

### 6.4 The leaderboard was invisible in a shipped build

**Five as first counted, seven as finally fixed** -- the count grew as the lane
worked, and using any single number without saying which is unsupported.

The five named in `coordination#40` (`createdAt` `2026-08-07T13:31:53Z`), from a
playtest of the **shipped** build: a leaderboard screen defaulting to the local
view and fetching global only on a toggle press; a submit confirmation rendered
at 12pt below the buttons; every remote failure reporting "offline" regardless of
cause; an anonymous player getting one nudge then permanent silence; and a
remembered decline showing nothing.

| PR | Created -> merged | Adds |
|---|---|---|
| #1172 | 13:30:08Z -> 14:30:21Z | defect 5 (declined player saw nothing) |
| #1173 | 14:03:33Z -> 14:48:00Z | defects 1-4, **plus a sixth found on the way**: two sources for one board key |
| #1179 | 15:23:48Z -> 15:46:41Z | **the seventh**: `> Press ENTER for Leaderboard` was line 32 of 32, **436px below the bottom of its own box** |
| #1180 | 15:52:52Z -> 16:02:12Z | cuts `v0.14.1`. Board key does not move |

The `v0.14.1` tag message enumerates six. The seventh came from Pip on league
night -- *"the game-over screen is really hard to read and still involves
scrolling..."* -- which is the same discovery channel as everything else here: a
person opening the thing.

**One more mis-stated state, recorded because it is the same class as 6.2:**
PR #1173's body says *"v0.14.0 is tagged at `7368e237` and built but **not
published**"*. It was published at 12:52:51Z, 70 minutes before that PR was
opened at 14:03:33Z. Wrong by the clock, inside the remediation for a defect
caused by not checking the clock.

**This is the sharpest argument for gate S5/2.3.** An epoch cut whose entire
player-facing point is a new board shipped with the board unreachable, and the
release-night playtest did not check it because nothing said to.

**Playbook:** the release-candidate playtest, before the tag, must exercise the
surfaces the release claims to change. For a league cutover: reach the global
leaderboard, submit, and see the score land on the new board key.

### 6.5 Smaller, recorded so they are not rediscovered

- **`Release Reminder` failed on both tags** (runs `31179576301`, `31195679690`)
  because the workflow had no `permissions:` block at all and the checklist step
  403'd. Fixed by #1177, merged `2026-08-07T16:25:07Z` -- **17 minutes after the
  release it failed on**. A gate that reds on something it does not gate trains
  the reader to discount reds.
- **Three docs are off by one on the ladder.** `docs/RELEASE_NOMENCLATURE.md`'s
  dated calendar and `docs/ROADMAP.md` both map `v0.14 -> L3`; so does
  `docs/RELEASE_CALENDAR.html`, which schedules Fri 2026-08-07 as "epoch -> L3".
  The actual cut was **L3 -> L4**. Filed as #1152, still open -- and **#1152 does
  not name the HTML calendar**, so fixing the issue as written would leave the
  wrong number live in the most calendar-shaped artifact in the repo.
  **A public league schedule derived from any of the three would publish the
  wrong epoch. Fix #1152, and widen it to the HTML, before that happens.**
- **`docs/LEAGUE_SEED_LEDGER.md` was cited on `coordination#40` as satisfied and
  does not exist in git** -- `git log --all -- "*SEED_LEDGER*"` is empty on every
  branch. See section 8 item 6.

---

## 7. Abort criteria

Cheap to write now, impossible to think about mid-cutover. **These apply after
the cutover has been announced.** Announcing and then not shipping costs less
than shipping a broken league; the board is the asset, and the board is what
breaks.

### 7.1 HARD ABORT -- do not push the tag

| Condition | Why |
|---|---|
| `git rev-parse <tag>^{commit}` is not `origin/main`'s merge commit, or `merge-base --is-ancestor` fails | 6.1. This happened. |
| `Godot Tests` is not green on the release branch head | The only broad functional gate the estate has |
| `sync_version.py --check` reports drift | A silent version drift forks the board key -- fatal, per `CLAUDE.md` |
| The ladder decision is unresolved -- the fork rule says YES and `ladder_version.txt` did not move, or vice versa | This is exactly `v0.14.0`'s F1: main carried a ladder-forking change on an unbumped ladder for 31 hours and every guard passed |
| The release-candidate playtest could not reach the global leaderboard | 6.4. This shipped once. |
| `CHANGELOG.md` has no section for the version | `pre-release-checks.yml` will fail the tag anyway; better to know first |
| The board key has not been blessed, or `pdoom1-website` has not been given the exact strings | `coordination#40`. A site presenting a closed epoch as live is worse than a late release |

### 7.2 ABORT THE ANNOUNCEMENT, not the release

Ship the release, do not run the public go-live commentary:

| Condition | Why |
|---|---|
| pdoom1.com has not caught up and no human is available to dispatch | Section 3. The unattended path is UNMEASURED; do not promise a time you cannot make |
| The new board key does not take a real score on a probe | Players arriving to a board that rejects them is the trust-destroying case |
| `pdoom1-website` has not confirmed their pages point at the new key | A live announcement pointing at a closed epoch is 4.3 repeating in public |

### 7.3 STOP AND FIX, mid-cutover

| Condition | Action |
|---|---|
| The release published with missing platform assets | The website derives platforms from asset filenames (`pdoom1-website#289`); a partial asset set publishes a wrong download page. Fix assets before letting the site update |
| `release_manifest.json` lacks `league_seed` | Regression in a merged feature (#1175). The website's seed discovery depends on it |
| A defect is found in the shipped build that makes the league surface unusable | Cut the patch immediately and do NOT roll the ladder for it -- a patch cannot move the board key, so the league survives the fix. This is exactly what `v0.14.1` did |

### 7.4 What is NOT an abort

- **The site being slow to catch up, when a human is available.** 18m to 1h11m
  is the observed normal. Announce softly (section 3.3) and it costs nothing.
- **A red `Release Reminder`.** It gates nothing (6.5).
- **A red slow simulation tier.** Non-blocking by policy (`CLAUDE.md`).

---

## 8. What is NOT predictable yet -- the summary

Stated plainly because the whole purpose of this document is scheduling accuracy,
and a playbook that pretended the deploy window were tight would be a false claim
in a document about not making false claims.

1. **The unattended publish-to-live-site window has never been measured.** Both
   observed cutovers were hand-dispatched. The "~6h45m worst case" is arithmetic
   on cron periods (`pdoom1#1182`), not an observation. **This is the single
   biggest thing blocking a public schedule.**
2. **The event-driven path is proven non-functional**, not merely slow: no
   `repository_dispatch` run has ever executed on `pdoom1-website`
   (`pdoom1-website#289`).
3. **The playtest gate has no measured duration.** It is a real cost and the
   playbook refuses to estimate it.
4. **CDN propagation is uninstrumented.**
5. **The freshness alarm's RESOLVE path has never run.** Comparison proven red,
   alarm proven once (run `31281144601`, 2026-08-08T22:12:18Z), `resolve`
   skipped. A guard that can open an issue and not close it is
   `pdoom1-website#149`/`#204`/`#230` waiting to happen.
6. **`docs/LEAGUE_SEED_LEDGER.md` does not exist.** It was cited on
   `coordination#40` as satisfying the seed-blessing step;
   `git log --all -- "*SEED_LEDGER*"` is empty on every branch. The blessing was
   real, its record is three comments and a deleted probe, and **a cutover
   procedure that depends on a document nobody else can read is not a
   procedure.** Commit it or say plainly that it is a plan.

**What IS predictable, and can be announced today: tag push -> downloadable
release, 5m18s and 5m28s across two measurements.**

---

## 9. Method

Every timing above came from one of these.

```bash
# Releases and tags
GIT_TERMINAL_PROMPT=0 gh release list --limit 8
git for-each-ref --sort=-creatordate \
  --format='%(refname:short) %(creatordate:iso-strict) %(objectname:short)' refs/tags
git rev-list -n1 v0.14.0 && git cat-file -p v0.14.0
git merge-base --is-ancestor 237636d1 origin/main; echo $?

# Workflow runs, both repos, by date
GIT_TERMINAL_PROMPT=0 gh api "repos/PipFoweraker/pdoom1/actions/runs?created=2026-08-07&per_page=100" \
  --jq '.workflow_runs[] | [.created_at,.updated_at,.name,.head_branch,.head_sha,.event,.conclusion,(.id|tostring)] | @tsv'
GIT_TERMINAL_PROMPT=0 gh api "repos/PipFoweraker/pdoom1-website/actions/runs?created=2026-08-07&per_page=100" \
  --jq '.workflow_runs[] | [.created_at,.updated_at,.name,.event,.conclusion,(.id|tostring)] | @tsv'

# Per-job phase breakdown of a release run
GIT_TERMINAL_PROMPT=0 gh run view 31195680192 --json jobs \
  --jq '.jobs[] | [.name,.startedAt,.completedAt,.conclusion] | @tsv'

# Why a run failed, step by step
GIT_TERMINAL_PROMPT=0 gh run view 31179576741 --json jobs --jq '.jobs[].steps[] | [.name,.conclusion] | @tsv'

# PR open/merge instants
GIT_TERMINAL_PROMPT=0 gh pr view 1170 --json number,createdAt,mergedAt,headRefName

# Cross-repo issues cited
GIT_TERMINAL_PROMPT=0 gh issue view 40 -R PipFoweraker/coordination --json body,comments
GIT_TERMINAL_PROMPT=0 gh issue view 285 -R PipFoweraker/pdoom1-website --json body
GIT_TERMINAL_PROMPT=0 gh issue view 289 -R PipFoweraker/pdoom1-website --json body
GIT_TERMINAL_PROMPT=0 gh pr view 1182 -R PipFoweraker/pdoom1 --json body   # a PR, not an issue

# The tag deletion -- the ONLY machine record of it
GIT_TERMINAL_PROMPT=0 gh api "repos/PipFoweraker/pdoom1/activity?per_page=100" \
  --jq '.[] | select(.ref|test("v0.14")) | [.timestamp,.activity_type,.ref,.before,.after] | @tsv'
git cat-file -p 64588f82   # the deleted tag object, still readable locally
```

**No generator was written.** The join is across two repos' Actions APIs, git
plumbing, and three issue threads, hand-ordered, with the trust decisions in
sections 3 and 8 carrying the value. A script would have run once.

**This document's own falsifier.** If the next epoch cut (`v0.15`, targeted
2026-09-04 per `docs/ROADMAP.md`) runs without any phase in section 2 being
pre-staged, and without a measured publish-to-live-site number being recorded,
then this is another printed document nobody acted on and the correct response is
to stop producing them.

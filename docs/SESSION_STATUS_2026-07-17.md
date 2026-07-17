# Session status + glide path -- 2026-07-17 ~2:30pm

> Orchestrator handoff / pre-compaction snapshot. The alpha is close: the game boots, the hiring
> pipeline is playable + fixed, tests are green. This is the map to land/build/ship.

## Ship branch
`feat/hiring-phase-b-pipeline` @ `f6ccb27` = the alpha. Contains: Phase-B hiring pipeline +
attention-reserve fix + sourcing redesign + quirk system + game-start hotfix + promise-fix(B).
**Fast gate: 444 tests / 0 failures (verified).** Playtest worktree (imported, current):
`.claude/worktrees/playtest-664/godot`.

## PRs / branches -- bring-in status
| PR | branch -> base | state | tests |
|---|---|---|---|
| #685 | fix/promise-currency -> #664 | MERGED into #664 (promises cost papers/compute/governance, not a rep-bomb; 6-turn-safety test) | 444/0 |
| #686 | feat/ui-quick-wins -> #664 | READY to merge into #664: PLAN/WATCH toggle (key V), tidy turn/date, in-flight hiring progress | 437/0 |
| #687 | feat/test-strategy-uplift -> main | READY: ADR-0017 + load-all smoke test (proven to catch the parse error) + property tests, red-first | 420/0, 96/0 sim |
| #680 | feat/leaderboard-sync-client -> main | READY (needs host): LeaderboardSync autoload; set base_url/token/enabled in godot/data/leaderboard_config.json | 431/0 |
| #682 | feat/adaptive-music -> main | READY (optional for alpha): doom-band adaptive music, PLACEHOLDER audio, 5 audio docs | 421/0 |
| -- | feat/reroll-review | **NOT on main** -- built gallery HTML works in gallery-wt; the images(art/reroll-sweep-01)+build_reroll change need a clean re-commit (earlier commit timed out) | -- |
| -- | art/reroll-sweep-01 | 101 re-roll images preserved, unmerged | -- |

## HANGING ACTIONS (do not drop)
- **ART REVIEW (Pip):** open `G:\...\.claude\worktrees\gallery-wt\tools\art_review\style_review.html`
  -- original sweep + the 101-asset re-roll batch; keyboard nav (arrows, K/M/R, N=note, Export). Pick, paste back.
- **RE-ROLL PRESERVATION (Claude, post-compaction):** commit `art_source/pixellab_2026-07-17/reroll/`
  + the `build_reroll()` change in `tools/art_review/build.py` to main (do it in small steps -- 177
  files + a 1.6MB HTML timed out as one command; commit images+build.py without the regenerable HTML).
- **SCORE SYNC GO-LIVE:** deploy `server/leaderboard/score_api.php` to a Dreamhost host -> set the
  game config + the website's `config.json.scoreApi` to the same host. Website #133 is aligned to our
  frozen contract (read-only consumer) and just needs the host.
- **MUSIC:** #682 prototype in (placeholder audio). Pip's parallel Fable run did the DSP analysis +
  a motif-hunt plan (SuperCollider/Strudel). Reference tracks captured: `docs/audio/REFERENCE_TRACKS.md`.
  Next (Pip-driven): SuperCollider install + motif hunt.
- **EVENT-FLOOD FIX (the principled one):** add an importance/salience tier to the feed. Maps to
  pdoom-data's A/B/C/D tier system (#25 there); show high-salience by default, more with Situational
  Awareness. Fixes game issue #630, scales the 2018->2026 corpus, backdoor-builds the SA mechanic.
- **BUG-REPORT ENDPOINT (answer for the website agent):** pdoom1's `bug_reporter.gd` formats reports
  for **GitHub issue submission** (`format_for_github` -> GitHub API) -- NOT a custom server endpoint.
  Bug reports = GitHub issues; no Dreamhost endpoint needed (unlike scores). Relay this.
- **P0 ship batch** (from `docs/game-design/UI_FEATURES_STACK.md`): quit -> Main Menu default;
  defeat title/cause fix (said "AI Destroyed Humanity" while cause was rep-collapse); event-feed filter.

## Cross-repo alignment (good news)
- **pdoom1-website #133**: the other Claude confirmed the game->website score path was broken
  post-migration and ALIGNED to our frozen PHP contract (see its `docs/GAME_UPLIFT_PLAN.md`) -- it's a
  read-only consumer, no parallel store. Flagged a version-of-truth mess (version.txt 0.11.0 vs
  hardcoded 0.4.1/0.6.0) for website-side cleanup.
- **pdoom-data #25**: A(1166 arxiv, in-game)/B(3966)/C(1375)/D(42) event tiers = the importance layer.

## Playtest findings (2026-07-17, seed weekly-2026-w0)
- Two deaths, both rep-collapse from the promise-as-reputation bug (turn 14 & 229) -- FIXED by #685.
- Baseline (do-nothing) survives 588 turns; played runs 14 & 229 -- promises were the early-loss vector.
- Design heuristics (in memory + stack): no loss in first ~6 turns; easy info-transition/pain-payoff;
  rage-quit friction; turn=plan-period + show date; feed channel discipline.

## Glide path to ship
1. Pip: art pick-pass + confirm ship scope (does the alpha include sync #680 / music #682?).
2. Merge #686 -> #664; verify gate. (#664 is the alpha content.)
3. Fire P0 ship batch (quit-to-menu, defeat-title, event-feed filter) onto #664.
4. Merge #687 (tests) to main; #680/#682 to main per scope.
5. Merge #664 -> main = alpha. Export Windows build.
6. Deploy PHP + wire config -> score sync live -> website reads.
7. Event-flood-via-tiers + rest of the stack = post-alpha hotpatches.

## Key facts
- Reputation starts 50; death at rep <= 0 (collapse warn at 10). Balance in defaults.json.
- Frozen score contract: `docs/strategy/BACKEND_AND_DATA_ARCHITECTURE.md`.
- Generations left ~1591 (pixellab). Art palette/intensity: `docs/art/PALETTE_AND_DOOM_INTENSITY.md`.

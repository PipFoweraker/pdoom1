# Workshop #2 Backlog — Parked Items Register

> **Purpose.** Every question or errand *parked* (not freelanced) during the workshop-#1
> build lanes lands here, so nothing evaporates across lanes and we clear them **in one
> fell swoop**. Two kinds of item:
> - **Design questions (DQ)** → resolved *with Fable at workshop #2* (which also needs
>   first playtest data + a fresh kickoff doc; the original `FABLE_SESSION_KICKOFF.md` is
>   EXECUTED/stale).
> - **Engineering errands (EE)** → a batched cleanup pass; no design judgment needed.
>
> Each item cites its source PR. Update status here as items are resolved.

## Design questions — for Fable workshop #2

### DQ-1 · Victory condition removal  *(source: PR #550, ADR-0002)*
ADR-0002 says "there is no victory condition," but `check_win_lose()` still ends the game
with `victory=true` at doom ≤ 0, and `test_game_state.gd` asserts it. WS-A removed only the
victory *bonus from scoring*, not the condition. Removal is a mechanics change that
**interacts with the mortality guarantee (WS-1 ledger interest)** — without that guarantee
a doom-pinned-at-0 run could go immortal, which ADR-0002 itself warns against.
**Decision needed:** remove the doom≤0 victory branch, and must WS-1 land first?

### DQ-2 · Baseline yardstick under turns-scoring  *(source: PR #550)*
The "vs no-action baseline" comparison now compares `(turns, doom_integral)` tuples. Is a
no-action baseline still the right reference under turns-survived scoring, or does the
yardstick want rethinking?

### DQ-3 · Cross-version leaderboard UX  *(source: PR #550)*
Boards are now keyed by `(seed, game_version)`, so they display as separate `seed (version)`
entries in the browser. Intended UX, or should it aggregate/filter by version explicitly?

### DQ-4 · Character-creation re-roll within a seed  *(source: PR #552)*
Ruling **already applied**: *same seed → same starting staff* (seed-keyed leaderboards +
replay demand it; this also resolved WS-B #551's "determinism vs per-seed variety"
question). **Open:** whether a future character-creation screen lets you re-roll *within* a
seed. Deferred — not implemented, not precluded.

### DQ-5 · Empty-seed determinism contract  *(source: PR #552)*
`GameState._init` still derives a `Time.get_ticks_usec()` seed when the seed string is
empty — so **only explicitly-seeded games are deterministic/replayable** (empty =
intentionally random). Pip's leaning: accept this contract for now. Cleaner eventual
contract: *every* game (incl. "random" ones) generates and records a concrete seed.
**Confirm** the interim contract and whether to tighten it later.

## Engineering errands — batched cleanup pass

### EE-1 · Legacy `game_controller`/`end_game_screen` path  *(source: PR #550)*
Still constructs `ScoreEntry` with `doom_integral` defaulting to 0 (no accrual wired) and
an unversioned board. Appears superseded by the `game_manager`/`game_over_screen`/`main_ui`
path. **Remove it, or wire it to the new scoring?** (Left alone in WS-A — out of scope, low
risk.)

### EE-2 · Event-registry serialization  *(source: PR #552)*
`triggered_events`/`event_cooldowns` (moved to `GameState` instance state in WS-0) are
**not** in `to_dict`/`from_dict`. Replay rebuilds them from turn 0, so replay/score is
unaffected — but a mid-game **save/load** would forget event history. Fold into the
save/load pass.

### EE-3 · Delete website composite formula  *(source: PR #550, cross-repo)*
`pdoom1-website/scripts/verification_logic.py` still holds the old composite score formula.
Per ADR-0002 #4 it is **deleted, not synced** — separate `pdoom1-website` PR. The in-game
submission payload already carries `turns_survived` + `doom_integral` instead of `score`.

### EE-4 · Website static-JSON board wiring  *(source: PR #551, cross-repo)*
Wiring the exported replay artifact to the static-JSON board path lives in the
`pdoom1-website` repo — deferred, same bucket as EE-3. Postgres stays parked (ADR-0006).

## In-flight (not parked — sequencing only)
- **WS-B #551** rebases onto WS-0 (`c1c52fd`) and re-adds the hash comparison to
  `replay_simulator.verify()` (currently score-only pending determinism). Handled in the
  build pipeline, not workshop #2.

---
*Register opened 2026-07-05 after WS-0 merge. Sources: PR #550 (WS-A), #551 (WS-B draft),
#552 (WS-0).*

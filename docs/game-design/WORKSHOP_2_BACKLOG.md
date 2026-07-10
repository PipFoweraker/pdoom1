# Workshop #2 Backlog — Parked Items Register

> **Purpose.** Every question or errand *parked* (not freelanced) during the workshop-#1
> build lanes lands here, so nothing evaporates and we clear it **in one fell swoop**.
> Three buckets:
> - **Design questions (DQ)** — need judgment; resolved *with Fable at workshop #2* (which
>   also wants first playtest data + a fresh kickoff doc; `FABLE_SESSION_KICKOFF.md` is
>   EXECUTED/stale).
> - **Deferred build lanes (BL)** — no design blocker, just queued implementation (mostly
>   the ledger's player-facing slice — the engine landed, the UI didn't).
> - **Engineering errands (EE)** — batched cleanup, no design judgment.
>
> Each item cites its source PR. Update status here as items resolve.
> Lanes captured: WS-A #550, WS-B #551, WS-0 #552, WS-C #554, WS-1 #555.

## Design questions — for Fable workshop #2

- **DQ-1 · Victory condition removal — RESOLVED** *(#550, ADR-0002)* — the doom≤0 victory
  branch is **removed**. Proven safe by the exploit sweep: with rival labs contributing
  scaling doom (#562), a clean safety run is now *finite* (dies of doom, no immortal runs),
  so removing the win no longer creates an immortal-run exploit. The game is now unwinnable
  by design (ADR-0002 thesis: you can only buy time).
- **DQ-2 · Baseline yardstick** *(#550)* — is the no-action baseline still the right
  reference under turns-survived scoring?
- **DQ-3 · Cross-version leaderboard UX** *(#550)* — `(seed, game_version)` boards show as
  separate `seed (version)` entries. Aggregate/filter by version, or leave split?
- **DQ-4 · Character-creation re-roll within a seed** *(#552)* — ruling applied: *same seed
  → same starting staff*. Whether a future char-creation screen lets you re-roll *within* a
  seed is deferred (not implemented, not precluded).
- **DQ-5 · Empty-seed determinism contract** *(#552)* — only explicitly-seeded games are
  deterministic (empty falls back to `Time`). Confirm interim contract; tighten later so
  every ranked game records a concrete seed?
- **DQ-6 · Schedule provenance in the replay artifact** *(#554)* — replay accepts a
  schedule, but the exported artifact doesn't yet *carry* it. Should the schedule travel
  with the run, or be recoverable from `(seed, version)` via a seed registry? (Ties to WS-B
  artifact format + EE-2.)
- **DQ-7 · Governance player-facing design** *(#555)* — `governance` added as an engine
  `float` (a ledger currency per ADR-0003), but its scale, starting value, how the player
  raises/spends it, and its UI are **undesigned**.
- **DQ-8 · Balance constants** *(#555, #562)* — ledger escalation rates
  (`DOOM_PER_UNPAID_1000`, interest, loan multiple) and rival doom pressure are
  **placeholders**. Rival magnitude softened `0.05 → 0.025` as a first step toward longer
  games; full tuning (game length, sink pricing) still open — a playtest-driven pass.
- **DQ-9 · Receivables / counterparty content** *(#555)* — the `Entry` model supports the
  receivable (favor/pledge) side, but content is unbuilt and **overlaps ADR-0007 alliances**
  (WS-3). Design together?
- **DQ-10 · Inward-SA / ledger visibility** *(#555)* — how much of the player's *own* ledger
  is visible is undecided; overlaps WS-2 SA and the inward-SA deferral (ADR-0008).

## Deferred build lanes — follow-up implementation (no design blocker)

> These are why WS-1's ledger is **engine + soak only** right now — it works and is
> mortality-proven, but a player can't yet interact with it. A "WS-1b" slice covers BL-1..4.

- **BL-1 · Ledger action/UI wiring** *(#555)* — content factories (loan, funding-with-
  strings, desperation payroll, staff rider) exist but aren't clickable actions in
  `actions.gd`/UI yet. **The ledger is not player-facing until this lands.**
- **BL-2 · Exposure trigger wiring** *(#555)* — `expose()` is built + tested but not fired
  by any WS-C scheduled cause or rival action (needs an `expose_liability` cause handler).
- **BL-3 · Staff-rider hire/departure wiring** *(#555)* — factory exists; hiring/departure
  don't yet create or flip-to-secret ledger entries.
- **BL-4 · Full-pipeline soak fidelity** *(#555)* — the mortality soak uses a controlled
  doom model in-test, not the full TurnManager rival/doom pipeline; a full-pipeline soak is
  a follow-up (does not weaken the current proof).
- **BL-5 · Action-taking vetting bots** *(#554)* — WS-C brackets seeds by event-choice
  policy only; greedy-safety / capability-rush action-taking bots are a seam.

## Engineering errands — batched cleanup pass

- **EE-1 · Legacy `game_controller`/`end_game_screen` path** *(#550)* — constructs
  `ScoreEntry` with `doom_integral`=0 + unversioned board; appears superseded. Remove or
  wire to new scoring.
- **EE-2 · Save/load serialization** *(#552, #555)* — `triggered_events`/`event_cooldowns`
  (WS-0) and ledger entries (WS-1) aren't rebuilt by `from_dict`. Replay is unaffected
  (rebuilds from turn 0); a mid-game **save/load** would forget them. One save/load pass
  clears both.
- **EE-3 · Delete website composite formula** *(#550, cross-repo)* — `pdoom1-website/
  scripts/verification_logic.py` still holds the old formula; delete, not sync (ADR-0002).
- **EE-4 · Website static-JSON board wiring** *(#551, cross-repo)* — wire the exported
  replay artifact to the static-JSON board path. Postgres stays parked (ADR-0006).
- **EE-5 · Vetting envelope config source** *(#554)* — envelope thresholds are a passable
  dict (default provided); wiring to a JSON/league config file is a seam.
- **EE-6 · Schedule content pipeline** *(#554, content)* — ADR-0005 names `pdoom-data` as
  feedstock (real timeline → scheduled causes); mechanism exists, content pipeline unbuilt.

---
*Register opened 2026-07-05 (post WS-0). Last synced after WS-1 #555.*

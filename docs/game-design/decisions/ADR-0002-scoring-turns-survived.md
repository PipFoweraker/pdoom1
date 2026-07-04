# ADR-0002 — Scoring: turns survived, lexicographic doom-integral tiebreak, flows only

- **Status:** ACCEPTED (Pip, in-session)
- **Date:** 2026-07-04
- **Session:** Fable workshop #1

## Context

The implemented score formula — `(100−doom)×1000 + papers×5000 + researchers×2000 +
turn×500 + money×0.1 + 50,000 victory bonus (doom<20)` — was scaffolding built to test
the end-game screen, never a design statement (Pip, this session). It existed in three
copies (`godot/scripts/ui/game_over_screen.gd`, `godot/scripts/core/baseline_simulator.gd`,
`pdoom1-website/scripts/verification_logic.py`), a standing sync hazard the code comments
already worried about. It also contradicted the design philosophy twice: the money term
paid players to hoard (an **anti-sink**, directly worsening the source-rich/sink-poor
disease), and the victory bonus implied a win condition in a game whose thesis is that
you cannot win, only buy time.

## Decision

1. **The composite formula is dead in all three locations**, including the victory bonus.
   There is no victory condition.
2. **Score is lexicographic: turns survived strictly dominant; doom-integral tiebreak.**
   Each turn survived, the engine accrues `100 − doom` into the tiebreaker (area under
   the survival curve, "doom-years averted"). No blended constant — no stewardship total
   can ever outrank a survived turn. Display: **"Turn 14 · 862"**.
3. **Flows only, never stocks.** Score may never value anything the player *holds at
   death* (money, papers, researchers, reputation). Any end-state stock term is an
   anti-sink. Future score terms must be per-turn or per-event flows through world
   state; if a proposed term is a stock at death, it is rejected on sight.
4. **The engine is the sole scoring authority.** Score accrues per-turn inside the sim,
   so headless replay recomputes it for free. Other repos treat score as opaque — the
   website formula in `verification_logic.py` is deleted, not synced.
5. **Boards are keyed by `(seed, game_version)`.** Balance patches naturally rotate the
   meta; old scores never lie about the current game. Score-formula changes are patch
   content.
6. **Post-mortem reveal only.** No live score ticker; the run is played on the world's
   terms (doom, instruments), and the death screen is where accounting happens.

## Requirement created: the mortality guarantee

With no victory condition, nothing formally ends a stabilized game, and lexicographic
turns-scoring with immortal runs is a broken leaderboard. **Some pressure must grow
without bound** so every run ends and turn counts stay finite and meaningful. Natural
candidate: compounding Liability Ledger interest (ADR-0003); escalating wave amplitude
and rising base doom are alternates. The mechanism is open; the requirement is not.

## Beacons served

- Rams #10: the formula is two integers and a comparison rule.
- Rams #6: the tiebreaker is literally the area under the doom trend graph the game
  already ships — the score display and the instrument are the same object.
- MaRo Interaction: every sink becomes a score pump routed through the sim (money only
  becomes score by being spent on things that change the world), so scoring powers the
  sink architecture instead of fighting it.
- Philosophy fit: survival time is the score and must be skill-legible; turn counts as
  PoE-style badges with community milestone semantics ("I got to turn 20").

## Rejected alternatives

- **Composite/weighted formula** — anti-sink, illegible, sync-hazardous (see Context).
- **Pure doom-integral (K=0)** — undervalues wretched late-game survival; Pip's ruling:
  the reward for early prep is holding off the pivotal crunch longer, so desperate turns
  at doom 97 must pay full turn value.
- **Blended per-turn constant (score += (100−doom) + K)** — subsumed by lexicographic,
  which removes the tuning dial entirely.
- **Humans-alive-at-end as a score term** — double-counts the integral; retained as
  *presentation* of the integral only (see WORLD_AND_LORE).

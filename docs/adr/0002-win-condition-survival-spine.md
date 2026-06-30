<!--
status: accepted
date: 2026-06-30
deciders: Pip
-->

# ADR-0002: Win condition — survival spine with a rare apex victory

- **Status:** Accepted
- **Date:** 2026-06-30
- **Deciders:** Pip
- **Related:** `docs/GAME_DESIGN_CANON.md` §2

## Context

Three live docs described three materially different win conditions:

- `README.md` / `STEAM_INTEGRATION_ROADMAP.md`: "Survive 100 turns with P(Doom) at 0%" (timed survival).
- `docs/mechanics/*`: "Reduce P(Doom) to 0%" (instant win on reaching zero).
- `PLAYERGUIDE.md`: "Survive as long as possible… beat your previous best" (endless high-score, *no* win).

The shipping code is unambiguous. `godot/scripts/core/game_state.gd:378` `check_win_lose()` (called
from `turn_manager.gd:550`):

- **Victory:** `doom <= 0`
- **Defeat:** `doom >= 100` **OR** `reputation <= 0`
- There is **no turn limit** in this path.

(Note: `godot/scripts/game_controller.gd:163` contains a second, divergent win/lose implementation that
loses on money/compute = 0 and has no doom-victory. It is not canonical and must be reconciled or
removed — tracked separately as a code task.)

## Decision

**The code's `check_win_lose()` is mechanically canonical.** On top of it, the *design framing* is:

P(Doom) is **primarily a survival / high-score game**. Doom trends upward (the Doom Spiral / positive
feedback). A run's achievement is **how long and how low the player holds P(Doom)** — a score, ranked
on the weekly-seeded leaderboard. Driving doom to **0 (ASI solved) is a real but rare apex victory**
for mastery play, not the expected outcome. Most runs end in loss; by design the outcome is legible
before doom hits 100%, so the player may **concede gracefully** (locking their score) rather than grind
to the floor. Doom 100% is the hard floor: total civilisational failure.

"Survive N turns with low P(Doom)" is welcome as a **leaderboard benchmark / achievement**, never as
the win state.

## Consequences

- `README.md`, `STEAM_INTEGRATION_ROADMAP.md`, and `PLAYERGUIDE.md` are corrected to this framing
  (PLAYERGUIDE's survival framing was largely right but wrongly denied the apex victory exists).
- New backlog item: a **graceful-concession ("resign → lock score") mechanic** — not yet built.
- Tuning implication: a design dial remains open — is the apex victory reachable by skilled players, or
  deliberately near-mythical? This affects the Safety Flywheel vs Doom Spiral balance and is *not*
  fixed by this ADR.
- `game_controller.gd`'s divergent win/lose code must be reconciled to `game_state.gd`.

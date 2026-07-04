# ADR-0005 — Emergent doom waves: author causes, never outcomes; seed = RNG + schedule

- **Status:** ACCEPTED
- **Date:** 2026-07-04
- **Session:** Fable workshop #1

## Context

Doom arrives in waves. The fork: **authored** waves (designed timings — pacing
guaranteed, sim partly theater) vs **emergent** waves (arising from opponent behavior
plus the player's accumulated ledger — pure, attributable, pacing at the mercy of the
dynamics). Pip chose emergent, with a thumb on the scale: *"I think the doom's waves are
emergent. We might lean our thumbs on the scale at certain points… For example,
rival_lab could get a wave of funding at point X."*

## Decision

### Author causes, never outcomes

The designer's thumb may touch **inputs to the sim** — a funding wave hits rival_lab at
turn 9, a regulation lapses, a key researcher defects — and the wave that reaches the
player is whatever the sim does with that cause given opponent state and the player's
ledger. The thumb never touches the doom variable directly. This one rule keeps three
prior commitments intact:

- the sim never lies (every spike has a discoverable cause → scheduled events are SA
  content for free);
- replay verification is unaffected (scheduled causes are deterministic given seed and
  version);
- repeatability: same seed, same causes, so players learn the terrain — "the turn-9
  funding wave on this week's seed" becomes community vocabulary, and opening theory
  extends beyond your own moves into known weather.

### A seed = RNG seed + event schedule

This redefinition is also the cheap implementation of **seasons as scenarios**: a
"compute-overhang week" is a schedule dense with compute-cost causes — no engine
changes. Patches rotate the meta by rotating world-model assumptions, which is more
honest than nerfing numbers. Feedstock: the `pdoom-data` repo (1,194 curated real
AI-timeline events, actively maintained) — real events, lightly fictionalized, as
schedule entries. This closes Pip's "historical events affecting the game" patch
ambition with existing infrastructure.

### Seed vetting replaces wave authoring

The cost of emergent, stated honestly: pacing guarantees weaken — the same cause
produces different waves depending on state, so some seeds will be degenerate (dead by
turn 3, or a snoozefest). **Curation replaces authorship**: run candidate seeds through
`baseline_simulator.gd` headless (no-action baseline plus crude heuristic bots) and
reject seeds whose doom trajectory falls outside a playability envelope before
publishing. Pip is a seed *curator*, not a wave author — the SimCity thumb with quality
control, built once.

### Rejected: player-triggered disasters

Pip, explicitly: hardness is baked into game settings for the engine, never a
player-facing disaster menu. (Player-*chosen* difficulty modifiers at run start are a
separate parked item — ADR-0008.)

## Beacons

- Rams #6: every spike has a real cause inside the sim.
- Rams #10: seasons, geopolitics-as-content (ADR-0008), and historical-event integration
  all ride one mechanism (the schedule) with zero new engine systems.
- MaRo Surprise + Inertia: scheduled causes are clocks the player can buy lead time on
  (ADR-0004).

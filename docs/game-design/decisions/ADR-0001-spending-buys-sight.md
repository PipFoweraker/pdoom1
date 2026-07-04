# ADR-0001 — Situational Awareness as the primary sink ("spending buys sight")

- **Status:** ACCEPTED, as amended by ADR-0004 (channels/provenance, lead-time
  semantics, decision-flip acceptance test, simulate-everything/gate-the-view)
- **Date:** 2026-07-04
- **Session:** pre-workshop framing (Opus); tested and amended in Fable workshop #1

## Context

P(Doom)1 is **source-rich and sink-poor**: money and reputation accumulate faster than
anything competes to spend them, which is mechanically identical to being vulnerable to
simple dominant-strategy exploits. We need sinks that force tradeoffs.

The game already decomposes doom into sources internally (base rate, capability research,
opponent labs) and already distinguishes **undiscovered** opponents (small *random*,
invisible doom) from **discovered** ones (computed, *legible* doom). Discovery already
converts fog into information — the substrate for an information economy exists.

## Decision (proposed)

Make **Situational Awareness** the flagship sink category. Spending money/reputation buys
*perception of the true game state*: doom decomposes into visible sub-sources only to the
degree the player has paid for sight. This unifies three previously-separate threads —
the Insight System (skill-gated visibility), the CRT unlockable-viewport aesthetic, and
the discoverable-frontier-labs system — into one feature: **buying sight unlocks
screens.**

## Beacons served / violated

- **Serves:** Rams #6 (honest — fog is truthful, not gamey), #2 (useful — you buy better
  decisions). MaRo Interaction (money splits three ways: sight / safety / progress),
  Surprise (low-SA players get blindsided), Catch-Up (cheap emergency-SA burst), Flavor
  (epistemic horror is the actual theme of the AI-race genre).
- **At risk:** Rams #10 (must fold Insight + viewports + labs into ONE system, not three
  panels) and #5 (unobtrusive — SA UI must not become clutter / analysis-paralysis).

## Interaction contract

Reads/writes: **money** and/or **reputation** (cost), **doom visibility/granularity**
(effect), **opponent-lab discovery** (generalized), **action availability** (see the hard
constraint below).

## Hard constraint (falsification test)

**Every unit of sight the player buys MUST open at least one decision that was invisible
before.** A viewport that reveals detail but unlocks no new action is a tax with extra UI,
and fails. Any SA feature that can't name the newly-unlocked decision is rejected.

## Rejected alternatives
<!-- To fill from the workshop: e.g. pure money sinks (cosmetics only), doom as single
     opaque number, sight-as-free-upgrade. Record why each loses. -->

## Consequences / open questions

- Does granular doom-counting need a new subsystem, or can it re-tag existing doom
  sources? (Lean: re-tag — Rams #10.)
- Pacing interaction: games currently end in ~7–8 turns; does an information economy need
  a longer game to pay off?
- What's the catch-up lever's exact shape?
- Measurement: build the exploit-finder / auto-playtester (deterministic RNG + headless
  Godot) to baseline the dominant strategy *before* SA lands, so we can prove it closed
  exploits rather than eyeball it.

## Workshop #1 outcome (2026-07-04)

Hypothesis accepted, amended by ADR-0004. The open questions above resolved as follows:

- Granular doom-counting: **re-tag confirmed** — simulate everything, gate only the view
  (ADR-0004 §1). No new subsystem.
- Pacing: target shape is now long-tailed ("several hundred turns" as the deep-run tail,
  median deaths early); exact wall-clock targets deliberately open (ADR-0008).
- Catch-up lever: **desperation levers priced in liabilities** (ADR-0003) — catch-up and
  tragedy-generation are one mechanism; no rubber-banding.
- Measurement: still owed; folds naturally into the seed-vetting harness (ADR-0005) and
  decision-flip telemetry (ADR-0004 §4).
- New since proposal: within one patch, a dominant loop is **content, not exploit**
  (chess openings); the sin is dominance across all seeds/patches — that is what kills
  both the ladder and the teaching claim.

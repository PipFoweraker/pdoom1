# SEED: Sim Speed Control + Complexity-not-Difficulty

> LOSSLESS capture of two Pip ideas raised 2026-07-25 (post-proposal-read, banked
> for WS-3). RAW SEEDS, not decided canon. [PIP] = verbatim / near-verbatim;
> [CLAUDE-note] = secretariat connection, reword or discard freely.
> Feeds WS-3 (#811) and the dev-mode / accessibility lanes.

## 1. Sim speed control (dev + play) [PIP]
> "an ability to change the game's functional speed will be emergent and very
> useful so I can set up a sim, set interrupts to low, and play out a couple of
> strategies using, like, quarters instead of months or really flying through
> things."

[CLAUDE-note] Two coupled knobs: (a) TIME GRANULARITY (advance by quarter, or
batch-advance N months) and (b) INTERRUPT SUPPRESSION (auto-resolve / lower the
response-window + event pauses so a run plays end-to-end without stopping). Payoff:
a fast strategy-trajectory observer for balance work -- run a policy to the end,
watch the streams, spot the divide-by-one infi-glitch before a player does.
Connections:
- Reuses the determinism/replay backend (ADR-0006) and the tests/unit/simulation
  full-run harness -- "fly through a strategy" is that harness surfaced as a
  dev-mode control, not new engine.
- Sits on PerfLog (#867, landed) for the timing/anomaly readout, and on
  PlanController (CARVE 1) + the per-tick resolution spike where "advance" hooks in.
- Dev-gated (BuildInfo.is_dev_build); does NOT ship as a player control or touch
  the ladder. Near-term high-value build for PIP's own sim-testing, orthogonal to
  the release train.

## 2. Complexity-not-difficulty [PIP]
> "instead of having *difficulty* settings, we reduce the *complexity* of the sim
> by greying-out or accepting-as-default or automatically chaining some actions
> together to make there be less customisation but also fewer decisions at the
> *simpler* level."
> (caveat: "not too wedded ... mildly becoming attracted to obfuscating or
> retiring difficulty settings; let people fiddle with sliders or values in the
> customise option in more detail if they want to change the sim. I think
> Factorio's approach here works better, although for them the gameplay remains
> mostly the same and it's just the world that generates different IIRC.")

[CLAUDE-note] Accessibility via REMOVING DECISIONS (auto-chain / default / grey-out)
rather than nerfing numbers. Real tension to resolve at WS-3: the DESIGN_PHILOSOPHY
thesis is "the hardness lives in the DECISIONS, not the interface" (the crisp-parts /
MaRo-Rams lens). Auto-chaining REMOVES decisions -- the very thing the thesis says the
hardness lives in. Factorio's actual model (which Pip cites) does the OPPOSITE: keep
the decision-set constant, vary the WORLD/params via customise sliders. Two distinct
levers are tangled here:
- LEVER A (Factorio-faithful): a "customise" surface exposing sim PARAMETERS
  (sliders/values) for players who want to change the world -- gameplay decisions
  unchanged.
- LEVER B (Pip's simpler-level): auto-chain/default/grey-out to reduce DECISION COUNT
  for a gentler mode -- difficulty-via-decision-removal, which cuts against the
  suffer-core thesis if applied to the CORE loop.
Candidate reconciliation: Lever B is legitimate as an ONBOARDING RAMP (early turns
auto-defaulted, decisions unlocked as the player graduates -- the lenticular /
"easy to learn" face), NOT as a permanent easy-mode that guts the decision core.
Lever A is the "power-user customise" face. Retiring named difficulty tiers in favour
of A+B is coherent. Pip: not wedded; flagged for WS-3 as a philosophy knob.

**Related:** DESIGN_PHILOSOPHY.md (crisp parts / brutal decisions), the Theme A
standing lens in WORKSHOP_3_PREP.md, ADR-0006 (replay backend), PerfLog (#867),
MAIN_UI_SEAM_MAP.md (CARVE 1 PlanController), the per-tick resolution spike.

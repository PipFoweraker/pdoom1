# Two-Act Structure, Counterfactual Scoring & Time Compression

> **Status**: Concept — captured from design discussion, NOT yet ratified
> **Created**: 2026-06-26
> **Related**: #500 (Research Quality), `RISK_SYSTEM.md`, #512 (Doom Trend Graph)
> **Owner**: Pip (architect). This doc is a capture for review, not a build spec.

## Why this doc exists

A #500 design session expanded into the game's macro-structure. This captures the
framing so it is not lost and so it stops contaminating the concrete #500 work.
**#500 does not depend on any open question here** — it proceeds against a fixed
`get_months_per_turn() → 1.0` helper (see "Bridge to #500"). Everything below is the
larger frame #500 will slot into later.

---

## Executive summary

The game is reframed from "drive p(Doom) to 0" to a **counterfactual-defense game**:
beat a deterministic *baseline trajectory* while a fictional antagonist actively pushes
the world worse than it really is. This single reframe pays for three things at once:

1. **Liability shield** — catastrophe is caused by a *fictional time-ported antagonist*,
   not by real labs. Real-world AI history is the neutral *baseline*; the fiction is the
   *delta*. We never assert that real frontier labs doom the world.
2. **Stakes** — p(Doom) can legitimately reach 100 because the antagonist is the causal
   force taking it past the real baseline. No player intervention → antagonist wins → 100.
3. **Replayability / scoring** — a fixed seed determines baseline + antagonist + event
   deck, so players on the same seed are directly comparable (daily-seed leaderboard).

The structure splits at "now": **determinism comes from history being known,
stochasticity from the future being unknown.**

```
  2017 ───────────── Act I (deterministic) ─────────────► NOW ──── Act II (probabilistic) ────► Singularity
  player arrives,           known history,                  │        no history exists;
  freshly time-ported       foreknowledge is the verb       │        risk pools drive events;
                                                            │        narrative/conspiracy layer
                                              ACT TRANSITION EVENT
                                              (big in-game beat; some score locked in)
```

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-26 | **Counterfactual-defense frame** (beat a baseline, don't zero doom) | Solves liability + stakes + scoring simultaneously |
| 2026-06-26 | **Determinism boundary = "now"** | History known → scripted/deterministic; future unknown → probabilistic |
| 2026-06-26 | **Foreknowledge is the Act I mechanic** | Resolves "deterministic past vs player agency": player can't change *whether* real events happen, but exploits *knowing* they will |
| 2026-06-26 | **Antagonist diverges from the present forward** (option b, not "caused real history") | Keeps the liability shield intact; Act I = run-up against roughly-real history |
| 2026-06-26 | **Objective is two-layered: survive (binary) + score (continuous)** | "Hold to baseline" is a flat *win* but a great *score*; survival = don't let antagonist hit 100 |
| 2026-06-26 | **Baseline is computed per-seed by a single no-player run** | Deterministic reference; versioned (see below) |
| 2026-06-26 | **Baseline is versioned** (league patches / data updates re-baseline) | Scores are only comparable within a baseline version |
| 2026-06-26 | **Variable time-per-turn; granularity tracks proximity to singularity** | Coarse over the known past, fine into the speculative future (Civ's nonlinear calendar, inverted) |
| 2026-06-26 | **Magnitudes defined per calendar-time, divided by time-per-turn** | Decouples balance from game-length/speed; the bridge to #500 |

---

## Core concepts

### The baseline (the thing you race)
- For a given **seed**, the engine runs the timeline **once with no player** to produce
  that seed's **baseline score / doom trajectory**.
- The baseline is **versioned** — it shifts with "league patches," historical-data
  updates, and balance changes. Scores are comparable only *within* a baseline version.
- In Act I the baseline is *real history*. (See the seam below for Act II.)

### The player
- The player's **first action is arrival** — freshly time-ported into the start date
  (currently 2017-07; see `game_state.gd` `DEFAULT_START_*`).
- The player **cannot change whether real-world events happen** — those are largely
  destined. What the player can do is **exploit foreknowledge** (positioning, timing,
  resource build) — a payoff that rewards meta-savvy and repeat players especially.

### The antagonist (the "rival picks the opposite starter")
- A time-ported adversary, intended to live in the existing `rivals.gd` system as a
  special-cased rival — a **shadow player in the same action space, opposite values**
  (player leans safety → antagonist leans capabilities).
- Identity: the **temporal pursuer pulled into the time-whorl** with the protagonist during
  the send-back (see `INTRO_CINEMATIC.md`). NOT McCarthy — McCarthy is the heroic quartermaster
  who hoarded the compute and sends you back. The antagonist's job is to make the bad timeline
  recur. *(Specific identity/archetype still open.)*

### Determinism & strategy-sharing (Act I)
- The deterministic, pseudo-RNG-driven first act makes it possible to **force-find the
  optimal strategy for any given configuration** and to **share "builds"**: punch in a
  seed/config string and **autorun the first N computations**.
- The codebase already values seed-determinism: `VerificationTracker.record_rng_outcome`
  is threaded through `turn_manager` and `risk_pool`. This is the substrate for a
  build-sharing / replay tool.

### The act transition
- Crossing "now" should be a **big in-game event**, not a silent tick.
- **Some elements of the score lock in** at the transition (Act I performance becomes a
  sealed component of the final score). *Which* elements lock is OPEN.

### Act II (probabilistic, present → singularity)
- This is where the **risk-pool system** (see `RISK_SYSTEM.md`) comes into its own:
  hidden pools, probabilistic + threshold event triggers. Act II *is* the system already
  built.
- Intended home for **speculative / narrative content** — shadowy conspiracies in the
  spirit of *Papers, Please*, branching doom/singularity scenarios.
- **OPEN — the elegant problem:** how to port Act I's game elements into a regime where
  **event timing is no longer guaranteed**. Needs a clean solution.

---

## Time & turn granularity (Civ VI lesson, applied)

Verified Civ VI behaviour (Standard = 1× baseline): game *speed* scales cumulative
**costs** and **turn count** together (Online ~0.5× / ~250 turns → Marathon 3× / 1500
turns) but does **not** scale **movement** or per-turn flat effects. Consequence:
"progress per turn" stays ~invariant; what changes is **granularity** (number of decision
points). The famous failure mode is the asymmetry — anything expressed per-turn that
*should* be per-calendar-time silently rebalances when turn count changes.

**Applied here:**
- Use **variable time-per-turn**: months/turn over the known past (review), weeks-or-finer
  into the future (where the game actually is). This is Civ's nonlinear calendar inverted
  — we compress *recent* history and *expand* the speculative future — and it auto-
  accelerates tension toward the singularity.
- **Current code is the longest-possible speed**: `game_state.gd:57` hardcodes "1 day/turn,
  weekdays only," which is ~2,340 turns to reach the present — fine for a short fixed
  scenario, untenable for a span-to-present campaign. Replace the hardcoded day-step with
  `time_per_turn = span / turns_for_selected_speed`.
- **Two live scaling bugs to fix when the length system lands** (NOT #500 blockers):
  1. Risk-event probability is rolled **per turn** at `pool/100` (`risk_pool.gd:148`) — at
     equal pool levels a long game fires proportionally more events. Fix:
     `probability = pool/100 * months_per_turn`.
  2. `risk_pool` decay was a hardcoded `2.0`/turn — speed-dependent total decay. Being set
     to `var decay_rate = 0.0` under #500 (matches `RISK_SYSTEM.md` "active reduction only").

---

## The structural seam to design deliberately (not a bug — a decision)

The **comparison target changes at "now."** In Act I the baseline is *real history* (a
legible ghost to race). The moment the player perturbs Act I, **there is no historical
future** to compare against in Act II. So Act II scoring must reference either:
- (a) the **antagonist's no-player counterfactual simulation** (what doom would do if you
  stopped acting), or
- (b) **peers on the same seed** (leaderboard-relative).

You maintain *two* reference trajectories and switch which one scores you at the
transition. Design it on purpose.

Related discipline: **the score axis must stay legible even though risk is hidden.** Doom
(headline meter) vs baseline = the visible score; the *risk pools* (latent causes) stay
insight-gated (`risk_pool.get_narrative_hint(insight_level)`). Visible effect, hidden
cause — fine, *if* doom-vs-baseline never gets buried behind the insight gate.

---

## Bridge to #500 (what actually matters now)

#500 needs **one** thing from all of the above: magnitudes expressed **per calendar-month**
and divided by a `get_months_per_turn()` helper that **returns `1.0` today**. That makes
total accumulated risk over a game invariant across any future speed/length choice — only
granularity changes. #500 ships now and auto-rescales when the length system arrives.
Nothing in this doc blocks #500.

---

## Player-facing review: the Ledger & the Redacted zone

Decisions with passive/constant effects need a place to be *reviewed and understood*,
even if off the main UI — the Civ analogue is drilling into your upkeep budget. Proposed
component: a **Lab Ledger / Briefing** page (button or hotkey), with two zones:

- **Known Effects (transparent):** every active passive modifier the player owns or can
  see — research-quality stance (speed ×, and its risk deltas, which are *known* because
  the player chose them), upgrade passives, researcher productivity/doom contributions,
  per-turn research & upkeep (the "budget" drill-down), visible doom sources.
- **Redacted Effects (insight-gated):** the **hidden risk pools**, rendered as
  redacted/obscured entries (████) that the player knows *exist* but cannot read. This is
  the spooky "things affecting you that you're oblivious to" zone — and it is the UI
  realisation of the Insight/Situational-Awareness system. It reads straight off the
  existing `risk_pool.get_narrative_hint(pool, insight_level)` ladder:
  - insight 0 → "[REDACTED] — N unseen factors are shaping your lab."
  - rising insight → vague → directional → specific → quantified (progressive de-redaction).

This makes hidden risk *legible-as-hidden*: the player feels the fog and is motivated to
invest in Insight skills to lift it. For initial release, insight is a **dev-mode toggle**
(0 normally; 7+ under F3), per `RISK_SYSTEM.md:390`.

Dependency: the Ledger needs risk data surfaced to the UI layer. `risk_pool` already has
`get_all_narrative_hints(insight_level)` and `get_dev_mode_data()`; expose via a
`GameManager.get_risk_hints(insight_level)` accessor (the UI gets dicts, not the live
object). **Recommend the Ledger be its own issue** — it's larger than #500 and reusable by
every future passive-effect system.

## Open Questions (for Pip's review)

- [ ] Act-transition event: what does it look like, and **which score elements lock in**?
- [ ] Act II element-porting: how do Act I mechanics survive un-guaranteed event timing?
- [ ] Act II scoring reference: antagonist-counterfactual vs peer-relative (or both)?
- [ ] Antagonist identity / archetype / intro sequence (the "rival starter" beat).
- [ ] Span invariant: fixed turn count (span grows over real years → months/turn drifts) vs
      fixed months/turn (turn count grows). Fixed turn count = stable ~3h "Normal" UX.
- [ ] Speed tiers & exact turn counts (Sprint/Short/Normal/Long/Marathon).
- [ ] Historical-timeline content must be populated **through the present** or Act I runs
      out of scripted events near "now."
- [ ] Narrative layer scope for Act II (conspiracy mechanics à la *Papers, Please*).

# ADR-0016 — League metabolism: the game trails reality by one month

- **Status:** ACCEPTED (shape; pipeline build + league-notes format owed)
- **Date:** 2026-07-13
- **Session:** Fable workshop #3, beat 1

## Context

The scouting beat's variance question ("what does a veteran re-scout per run?") was
answered by moving the variance out of the seed and into time. Pip: *"i'm considering
making the leagues and associated patches that long as well - that means I can run the
game a month behind real time, update real world events into the engine, balance patch,
test, and deploy in a way that doesn't demand my full-time attention."*

Pip's mature-cycle articulation: *"collect real world events, suggestions on papers etc,
value shifts from previous month's run of data, patch the game once a month and load the
event logs into the game, the game's 'real time turn' progresses forward a month, a new
seed is generated for seed-racers, and the league launches fresh with notes etc."*

## Decision

1. **Monthly league cycle.** Each real month: collect real-world events/papers/data
   shifts → author a **world-update pack** (ADR-0005 schedule entries, fed from the
   pdoom-data repositories) → the game's real-time frontier advances one month → new
   baseline seed(s) generated → league launches with notes.
2. **Run-start stays 2017** (ADR-0009 anchor holds; Pip ~80% on this fork). Fixed real
   history is the shared macro map — Factorio-mode openings accepted at the macro grain;
   per-seed variance lives in the **micro-social layer** (hire pool, contacts, meetup
   yields). SC2 model: known map pool, scout the opponent's build; the pool rotates
   monthly. *Parked experiment (the other ~20%): a "jump in at present-month" mode that
   runs 2017→present as baseline.*
3. **Cadences decoupled: world-updates ≠ balance patches.** World-updates are monthly,
   light, expected — a "mild lore and sprint refresh." Balance patches are slower and
   legible-event-grade (philosophy canon: patches are the community heartbeat, argued
   about, never ambient weather). Real material is *always* welcome into pdoom-data;
   mechanics impact can lag at its own speed.
4. **One month per baseline seed is the explore-exploit window** — allows a few full
   playthroughs of a 6–8 hr decent run before rotation. Pip: timing "feels about right."
5. **The ops constraint is a design input.** The pipeline must run at ≤1 day/week of
   founder effort sustained: LLM-drafted world-update packs reviewed and submitted to
   Pip; junior-dev offload path if funding lands. Pip: *"this can't take up more than 1
   day a week of effort over long periods of time without it going public and actually
   having engagement pretty darn soon."*

## Beacons served / violated

- **Rams #6 (honest):** the game is tethered to the real race — each league, another
  month of the actual timeline enters the engine. Candidate third structural claim
  (alongside no-win and adoption-routing); not yet ratified as never-patch canon.
- **Rams #10:** world-update packs reuse ADR-0005's schedule format and the L9 data
  externalization; no new engine system — the league is a content cadence plus a
  frontier config value.
- **MaRo Surprise/Discovery:** monthly rotation, not seed randomness, is the veteran
  freshness engine.

## Interaction contract

Reads/writes: **ADR-0005 seed schedules** (packs are schedule entries; pdoom-data is the
feedstock — EE-6 promoted, this is its customer), **ADR-0009 fiction anchors** (2017
start reaffirmed), **ADR-0006 replay/versioning** (runs are per-league artifacts; DQ-3
cross-version boards become league UX), **L9 Balance separation** (balance constants and
world packs are distinct data surfaces on distinct cadences).

## Rejected alternatives

- **Run-start rides the leagues** (start ~present-day): loses the 2017 arc and the
  village-era early fiction. Rejected for the default mode; survives only as the parked
  present-month experiment.
- **Monolithic monthly world+balance patch:** ambient-noise patches violate the
  patch-as-heartbeat philosophy. Decoupled instead.
- **Per-seed macro world regeneration** (Civ-style map variance): fiction can't tolerate
  it (2017 start is semi-historical) and Pip doesn't need it — Factorio-mode accepted.

## Amendments (2026-07-13, handover round)

- **League baseline = one seed** (possibly one seed with a few variants — the elegant
  home for the parked present-month mode). One seed is promoted by default; players can
  generate and share their own — **anyone can host a mini-league by posting a baseline
  seed.** Community structure from seed-sharing, no new infrastructure.
- **Canon-ness ruled ~75%** — bake deeply into config. Pip's reason: without the
  reality-tether the game drifts from its guiding star as "a tool / scenario builder /
  argument fosterer."

## Consequences / open questions

- **Pipeline build** (EE-6 promoted): structured monthly world-diff format an agent can
  draft and Pip approves. Estimate 1–2 days/month once built; the sustainability risk is
  real (solo liveops decay) — treat the pipeline as a product feature, not an aspiration.
- League-notes format, seed-racer norms, what happens to in-flight runs at rollover
  (per-league artifacts suggest: they finish on their league's version).
- Engagement dependency named by Pip: the cadence only pays if the game is public with
  real players "pretty darn soon" — sequencing pressure on L1..Ln.
- The fixed 2017→present history grows by a month every league — the macro opening gets
  *longer* over time. Watch for opening fatigue; the parked present-month mode is the
  relief valve if it bites.

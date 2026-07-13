# ADR-0015 — No printed doom deltas: doom is computed from world state

- **Status:** ACCEPTED (Pip confirmed 2026-07-13); intermediary vocabulary owed (DQ-21)
- **Date:** 2026-07-13
- **Session:** Fable workshop #3, beat 1

## Context

The current build carries literal doom bumps on event/action definitions (legacy of the
prototype engine). Pip's ruling: *"hardcoding doom counters into things seems really like
a legacy design philosophy and as we get sophisticated things should defer to, like,
having impacts on things that have impacts on doom so we move more towards downstream
effects rather than single source-destination number bumps."*

Timing evidence: the 2026-07-13 death-attribution finding showed accounting breaks
exactly where causality goes indirect (debt deaths mis-filed as doom/cash;
`desperation_spam` 3→16 ledger deaths corrected). The L6 root-cause classifier now
follows chains — the instrument that makes indirection safe exists.

## Decision

1. **No action or event definition carries a literal doom field.** Effects target
   intermediary world-state variables (e.g. lab capability, deployment pressure,
   governance quality, public salience — v1 vocabulary owed, DQ-21); doom is computed
   from world state each day tick.
2. **The intermediary vocabulary is curated.** Adding an intermediary is an ADR-grade
   act — the restraint working-rule extends: a new intermediary must prove it can't be a
   read/write on existing ones.
3. **Guard rule: no unattributable doom.** Every doom-affecting intermediary must be
   reachable by the L6 attribution chain; indirection may never produce "I don't know
   what killed me" (ADR-0004 lead-time/legibility).
4. **The doom function is structure; intermediary pricing is numbers.** The function is
   patched rarely and publicly (it is the game's executable thesis about AI risk — the
   community can argue with it the way they argue balance patches); event/action
   magnitudes on intermediaries are the freely-tuned layer. MtG framing: events are
   cards, the doom function is the rules.
5. **Migration:** the L9 Balance data schema deprecates direct doom fields; the L1
   re-denomination pass (ADR-0009 consequence) performs the conversion; exploit sweeps
   are the regression instrument.

## Beacons served / violated

- **Rams #6 (honest):** mirrors reality — nothing "adds doom" directly; things change
  capabilities, incentives, and governance, which change hazard.
- **Rams #10 (as little design as possible):** N scattered doom dials collapse to K
  shared intermediaries + one function, K ≪ N.
- **MaRo Interaction:** shared intermediaries make mechanics read/write each other for
  free — an event boosting deployment pressure interacts with everything else touching
  deployment pressure, instead of owning a private pipe to doom.

## Interaction contract

Reads/writes: **ADR-0005** (extends author-causes-never-outcomes from designer
discipline to schema discipline), **L9 Balance schema** (field deprecation),
**L6 attribution** (must traverse intermediaries — the guard's enforcement point),
**exploit-finder** (regression on migration; future sweeps tune intermediary prices),
**ADR-0013 cost-of-debt** (debt cascades route through intermediaries, matching the
corrected death-attribution picture).

## Rejected alternatives

- **Status quo (per-definition doom deltas):** distributed hardcoding — dozens of
  tuning sites, exploit surface everywhere, zero cross-event interaction, and
  attribution can only say "this event had +2 printed on it."
- **Hybrid (some direct, some routed):** rejected — exceptions erode the guard rule and
  make the schema dishonest about where doom comes from.

## Consequences / open questions

- **DQ-21:** v1 intermediary vocabulary — starter set + semantics, needed before the L1
  data conversion.
- Doom-function form (level vs hazard-rate composition) — design with DQ-21.
- Balance levers get coarser by design: you fix an overtuned event by changing its
  intermediary magnitudes (its stats), never by editing the rules. Known cost, accepted.
- Single-point-of-failure risk: if the doom function is wrong, everything is wrong.
  Mitigation: it's one inspectable function (arguable, testable), and sweeps regress it.

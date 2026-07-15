# Architecture / Design Decision Records (ADRs)

Lightweight decision log for P(Doom)1 game-design and mechanics choices. One file per
decision, numbered. Captures the *decision and its reasoning* so later implementation
agents (and future-Pip) inherit intent, not just outcome.

Status values: `PROPOSED` → `ACCEPTED` / `REJECTED` / `SUPERSEDED-BY-000X`.

Copy `ADR-TEMPLATE.md` for new records. Keep them short: the *why* and the *rejected
alternatives* matter more than the *what*.

## Index

| # | Title | Status | Summary |
|---|---|---|---|
| [0001](ADR-0001-spending-buys-sight.md) | Situational Awareness as the primary sink ("spending buys sight") | ACCEPTED (as amended by ADR-0004) | SA is the flagship sink for the source-rich/sink-poor economy — spending money/reputation buys visibility into doom sources. |
| [0002](ADR-0002-scoring-turns-survived.md) | Scoring: turns survived, lexicographic doom-integral tiebreak, flows only | ACCEPTED | Replaces the three-copy ad hoc score formula with turns-survived as primary, a doom-integral tiebreak, and no money/hoarding term. |
| [0003](ADR-0003-liability-ledger.md) | The Liability Ledger (two-sided): every mitigation is a loan | ACCEPTED (build first) | Every doom mitigation is modeled as a loan with a repayment/consequence chain, not a free action — the flagship new system. |
| [0004](ADR-0004-sa-channels-lead-time.md) | SA amended: channels with provenance, lead-time semantics, decision-flip test | ACCEPTED (amends & accepts ADR-0001; build second) | Refines SA into provenance-tagged channels with lead time, gated by a decision-flip acceptance test rather than a raw admin/god-mode view. |
| [0005](ADR-0005-emergent-waves-seed-schedules.md) | Emergent doom waves: author causes, never outcomes; seed = RNG + schedule | ACCEPTED | Doom waves emerge from opponent behavior and the player's ledger (not authored timings); designers author causes, seeded by RNG + schedule. |
| [0006](ADR-0006-replay-artifact-backend.md) | The replay string is the canonical run artifact; backend wiring order | ACCEPTED | The seeded-RNG + hash-chain replay backend (already ~80% built) is confirmed as the canonical run artifact, with a wiring order for the rest. |
| [0007](ADR-0007-alliances-third-client.md) | Alliances: the third client of Ledger + SA (treaty = shared liability + shared sight) | ACCEPTED (build third, after ADR-0003/0004) | Alliances are un-deferred and built as a third client of the Ledger and SA systems — a treaty shares liability and sight between parties. |
| [0008](ADR-0008-deferrals-and-rejections.md) | Deferrals, folds, and rejections (the negative space of workshop #1) | ACCEPTED | Records what workshop #1 explicitly deferred, folded into other ADRs, or rejected, each with its revisit trigger, so decisions aren't silently lost. |
| [0009](ADR-0009-plan-months-two-speeds.md) | Turn structure: plan-months, two decision speeds, day as resolution tick | ACCEPTED | Formalizes the drift from week-based planning to day-tick resolution: a MONTH is the decision-cadence layer over day-grain sim ticks. |
| [0010](ADR-0010-adoption-routing.md) | Adoption routing (soft-with-teeth): doom bends where work is adopted | ACCEPTED | Safety work no longer bends doom directly/privately; it must be adopted (routed through conferences/papers/orgs) to have effect, killing the safety-spam dominant strategy. |
| [0011](ADR-0011-effort-economy.md) | The effort economy: founder hours, staff lanes, manager compression | ACCEPTED (shape; researcher archetype content owed) | Replaces the single fungible AP pool with founder Attention + separate per-staff action lanes, compressed by managers. |
| [0012](ADR-0012-event-response-taxonomy.md) | Event response taxonomy: un-snoozable, deferrable, expiring | ACCEPTED | Gives DEFER a real taxonomy (un-snoozable / deferrable / expiring) so it isn't a universal free-snooze button that kills the reserve-vs-greed tension. |
| [0013](ADR-0013-cost-of-debt-engine.md) | Financing instruments & the cost-of-debt engine | ACCEPTED (shape; numbers owed to the sweep) | Replaces flat 25%/turn loan placeholders with one shared pricing engine covering both loans and DEFER carrying-costs. |
| [0014](ADR-0014-conferences-presence-location.md) | Conferences, presence, and minimal location | ACCEPTED (v1 shape; yields/numbers owed to the sweep) | Defines what "attending a conference" is (v1: minimal presence/location mechanic, not a full subgame) as the adoption chain's socialization step. |
| [0015](ADR-0015-no-printed-doom-deltas.md) | No printed doom deltas: doom is computed from world state | ACCEPTED (intermediary vocabulary owed) | Retires hardcoded doom bumps on event/action definitions; doom becomes a computed function of named world-state intermediary streams (see doom_system.gd). |
| [0016](ADR-0016-league-metabolism.md) | League metabolism: the game trails reality by one month | ACCEPTED (shape; pipeline build + league-notes format owed) | Moves scouting/meta variance out of the RNG seed and into time: the game runs a month behind real time so real-world events and balance patches can feed in. |

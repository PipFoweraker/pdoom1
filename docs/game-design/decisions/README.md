# Architecture decision records (GENERATED -- do not hand-edit)

> Derived from the ADR files in this directory by
> `scripts/generate_adr_index.py`. Regenerate with:
> `python scripts/generate_adr_index.py`. A pre-commit check fails
> commits that change an ADR without regenerating this file.
>
> This index went stale by hand twice before it was generated (missing
> ADR-0018, pre-amendment statuses) -- see the 2026-08-03 ADR/DQ audit.
> **Trust the ADR files themselves for anything load-bearing.**

| ADR | Title | Status | Date | Amended | Summary |
|---|---|---|---|---|---|
| [ADR-0001](ADR-0001-spending-buys-sight.md) | Situational Awareness as the primary sink ("spending buys sight") | ACCEPTED * | 2026-07-04 |  | SA is the flagship sink for the source-rich/sink-poor economy -- spending money/reputation buys visibility into doom sources. |
| [ADR-0002](ADR-0002-scoring-turns-survived.md) | Scoring: turns survived, lexicographic doom-integral tiebreak, flows only | ACCEPTED * | 2026-07-04 |  | Replaces the three-copy ad hoc score formula with turns-survived as primary, a doom-integral tiebreak, and no money/hoarding term. |
| [ADR-0003](ADR-0003-liability-ledger.md) | The Liability Ledger (two-sided): every mitigation is a loan | ACCEPTED * | 2026-07-04 |  | Every doom mitigation is modeled as a loan with a repayment/consequence chain, not a free action -- the flagship new system. |
| [ADR-0004](ADR-0004-sa-channels-lead-time.md) | SA amended: channels with provenance, lead-time semantics, decision-flip test | ACCEPTED * | 2026-07-04 |  | Refines SA into provenance-tagged channels with lead time, gated by a decision-flip acceptance test rather than a raw admin/god-mode view. |
| [ADR-0005](ADR-0005-emergent-waves-seed-schedules.md) | Emergent doom waves: author causes, never outcomes; seed = RNG + schedule | ACCEPTED | 2026-07-04 |  | Doom waves emerge from opponent behavior and the player's ledger (not authored timings); designers author causes, seeded by RNG + schedule. |
| [ADR-0006](ADR-0006-replay-artifact-backend.md) | The replay string is the canonical run artifact; backend wiring order | ACCEPTED | 2026-07-04 |  | The seeded-RNG + hash-chain replay backend (already ~80% built) is confirmed as the canonical run artifact, with a wiring order for the rest. |
| [ADR-0007](ADR-0007-alliances-third-client.md) | Alliances: the third client of Ledger + SA (treaty = shared liability + shared sight) | ACCEPTED * | 2026-07-04 |  | Alliances are un-deferred and built as a third client of the Ledger and SA systems -- a treaty shares liability and sight between parties. |
| [ADR-0008](ADR-0008-deferrals-and-rejections.md) | Deferrals, folds, and rejections (the negative space of workshop #1) | ACCEPTED * | 2026-07-04 |  | Records what workshop #1 explicitly deferred, folded into other ADRs, or rejected, each with its revisit trigger, so decisions aren't silently lost. |
| [ADR-0009](ADR-0009-plan-months-two-speeds.md) | Turn structure: plan-months, two decision speeds, day as resolution tick | ACCEPTED | 2026-07-12 |  | Formalizes the drift from week-based planning to day-tick resolution: a MONTH is the decision-cadence layer over day-grain sim ticks. |
| [ADR-0010](ADR-0010-adoption-routing.md) | Adoption routing (soft-with-teeth): doom bends where work is adopted | ACCEPTED | 2026-07-12 |  | Safety work no longer bends doom directly/privately; it must be adopted (routed through conferences/papers/orgs) to have effect, killing the safety-spam dominant strategy. |
| [ADR-0011](ADR-0011-effort-economy.md) | The effort economy: founder hours, staff lanes, manager compression | ACCEPTED * | 2026-07-12 | 2026-07-27, 2026-07-28 | Replaces the single fungible AP pool with founder Attention + separate per-staff action lanes, compressed by managers. |
| [ADR-0012](ADR-0012-event-response-taxonomy.md) | Event response taxonomy: un-snoozable, deferrable, expiring | ACCEPTED | 2026-07-12 |  | Gives DEFER a real taxonomy (un-snoozable / deferrable / expiring) so it isn't a universal free-snooze button that kills the reserve-vs-greed tension. |
| [ADR-0013](ADR-0013-cost-of-debt-engine.md) | Financing instruments & the cost-of-debt engine | ACCEPTED * | 2026-07-12 |  | Replaces flat 25%/turn loan placeholders with one shared pricing engine covering both loans and DEFER carrying-costs. |
| [ADR-0014](ADR-0014-conferences-presence-location.md) | Conferences, presence, and minimal location | ACCEPTED * | 2026-07-12 | 2026-07-27 | Defines what "attending a conference" is (v1: minimal presence/location mechanic, not a full subgame) as the adoption chain's socialization step. |
| [ADR-0015](ADR-0015-no-printed-doom-deltas.md) | No printed doom deltas: doom is computed from world state | ACCEPTED * | 2026-07-13 |  | Retires hardcoded doom bumps on event/action definitions; doom becomes a computed function of named world-state intermediary streams (see doom_system.gd). |
| [ADR-0016](ADR-0016-league-metabolism.md) | League metabolism: the game trails reality by one month | ACCEPTED * | 2026-07-13 |  | Moves scouting/meta variance out of the RNG seed and into time: the game runs a month behind real time so real-world events and balance patches can feed in. |
| [ADR-0017](ADR-0017-anti-hollow-test-strategy.md) | Anti-hollow test strategy (load-time smoke + property-based invariants) | ACCEPTED | 2026-07-17 |  | Targets "hollow" tests that pass without exercising what they protect (zero-test CI, UI-parse-error-with-436-passing); adds load-time smoke and property-based invariants so a green suite means the code actually ran. |
| [ADR-0018](ADR-0018-render-only-office-doctrine.md) | Render-only office doctrine: no spatial fact becomes a gameplay input | DRAFT * | 2026-07-27 |  | The office floor renders state and never produces it -- no spatial fact (grid cell, occupancy, adjacency) may become a gameplay input, so the sim stays headless-testable and the view stays free to change. |
| [ADR-0019](ADR-0019-pull-from-demand-asset-pipeline.md) | Pull-from-demand asset pipeline: the pack is a function of declared demand | ACCEPTED | 2026-08-03 |  | The pack becomes a function of DECLARED DEMAND rather than an accumulation of past approvals: Library admission is taste-gated, but only a demand manifest pulls a size-declared derivative into godot/assets, making "packed but undemanded" unrepresentable rather than merely rejected. |

Total: 19 ADRs -- 18 ACCEPTED, 1 DRAFT. 2 carry amendments.

`*` marks a status carrying a qualifier that this index drops (12 of them, e.g. "ACCEPTED as design; build third"). Read the ADR for the condition -- the qualifier is often the load-bearing part.

## A second ADR series exists, and its numbers collide

`docs/adr/` holds 5 further record(s) not indexed here: `0001-retire-develop-branch.md`, `0002-win-condition-survival-spine.md`, `0003-godot-migration.md`, `0004-self-describing-data.md`, `README.md`.

The two series share numbers, and their respective ADR-0002s give
OPPOSITE answers on whether the game has a victory condition (#809).
This generator reads only the design series rather than silently
merging two schemes. Resolving the collision -- fold in, rename to an
ENG- prefix, or index separately -- is an open call (#1018).

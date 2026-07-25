# Research streams -- compute vs non-compute, and the fluid influence web

> Status: PROPOSAL for Workshop 3 (issue #811, LOCKED Wed 2026-07-30). Drafted
> 2026-07-25 by a design agent from Pip's 2026-07-25 dump
> (SEED_ENDGAME_AND_VIOLENCE.md items 2 and 3). Nothing here is ratified.
> Companion to OFFICE_ECONOMY_PROPOSAL.md (Theme B) and to the ADR-0011
> research-pipeline scoping (RESEARCH_IDEA_PAPER_PIPELINE_GAP.md,
> WS3_FINISH_OR_DROP.md Section 2). Claims are grounded in ADR-0009/0011/0013/
> 0015, SEED_RIVAL_AND_DEVELOPMENTS.md, and greps of `godot/scripts` +
> `godot/data` on 2026-07-25. Inferences are marked [INFERRED]. All numbers are
> DIALS, not values -- magnitudes are the sweep's job, shape is WS-3's.

---

## 0. The one-paragraph pitch

Research splits into two streams with different fuels, different payoff
periods, and different downstream impacts. **Compute-heavy** work burns a
purchasable, burnable resource with procurement lead time (compute joins the
office/finance economy: spot buys are expensive and fast, contracts are cheap
and lease-shaped); it pays off FAST and LEGIBLY (months-scale artifacts,
benchmark-shaped results) but its artifacts go STALE as the frontier advances,
its fleet bills doom through the already-wired `W_compute` stream, and it makes
you VISIBLE. **Non-compute** work burns only researcher-months and founder
hours; it pays off SLOWLY and NOISILY (theory and governance are hit-or-miss)
but its artifacts ENDURE and keep you quiet. The two streams pump different
axes of a three-axis INFLUENCE WEB -- Politics / Money / Technology, the
polyvirate from SEED_RIVAL_AND_DEVELOPMENTS -- and that web, not a tech tree,
is the progression structure: capabilities are GATES that read your CURRENT
influence levels (decaying, contested, convertible-at-a-loss), so nothing is
ever permanently unlocked and the rival can argue influence away from you.
Progression you must MAINTAIN is what "robust to fluid argument about
influence" cashes out to.

---

## 1. What is real vs absent today (verified 2026-07-25)

Greps across `godot/scripts/**` and `godot/data/**` for compute / stream /
influence / unlock / tech_tree:

| Piece | Status |
|---|---|
| `compute` resource | **EXISTS.** Scalar, starts at 100 (`data/balance/defaults.json` `starting_resources.compute`). Burned 1.0/researcher/turn flat (`compute.per_researcher_per_turn`; `turn_manager.gd:130-171,238-244` -- #576 made it a real consumable). Researchers stop working at compute 0 (the `has_compute` gate). |
| Per-stream burn rates | **PARKED HOOK.** `turn_manager.gd:166-168` literally says: "PARKED (#576 follow-up): researchers request compute at different rates". This proposal is that follow-up, typed by stream. |
| `buy_compute` action | **EXISTS, VIOLATES ADR-0009.** $50k, instant delivery (`data/actions/core.json:13-20`). ADR-0009 rule 5: "Nothing strategic resolves instantaneously." Compute procurement has no lead time today -- the exact thing Pip's item 2 adds. |
| Compute doom stream | **WIRED, DORMANT.** `dedicated_ai_compute` intermediary = `state.compute` ("cheap proxy in v1", `doom_system.gd:222-223`); stream term at `doom_system.gd:269-270` with `W_compute = 0.0` (`defaults.json:82`). Activating the dual-use price of a big fleet is a one-dial change. |
| Compute promises | **EXIST.** `compute` is a researcher appetite (ADR-0011 s8); `compute_budget` promise mints a ledger obligation denominated in compute (`defaults.json:45`, principal 20, fuse 8). A compute-starved lab already defaults on promises. |
| Compute engineers | **EXIST, THIN.** `hire_compute_engineer` ("improves compute efficiency", `data/actions/hiring.json:25-27`); `state.compute_engineers` counted in stationery burn and the debug overlay. A natural efficiency dial for the compute stream. |
| Research streams / typed research | **ABSENT.** Research is one fungible scalar via an undirected RNG drip (`turn_manager.gd:178-236`); no topic, no idea, no workstream object. Fully diagnosed in RESEARCH_IDEA_PAPER_PIPELINE_GAP.md; the fix ladder (MINIMAL/MODERATE) is already scoped and ADR-0011 MODERATE is ACCEPTED. |
| Tech tree | **ABSENT -- good.** No unlock/prereq system exists anywhere in `godot/scripts`. This proposal is the structure that PREVENTS one being built by default. |
| Influence stocks | **ABSENT as player-facing; the MATH SHAPE EXISTS.** The ADR-0015 intermediaries (`global_alarm`, `global_panic`) are exactly accumulate-per-tick + decay stocks (`alarm_decay`/`panic_decay`, `defaults.json:89-90`). Influence axes are three more stocks of the same shape -- reuse, not a new engine class. |
| Polyvirate axes | **NAMED, UNCONFIRMED.** Politics / Money / Technology with RPS ordering (Politics beats Money beats Technology beats Politics) -- SEED_RIVAL_AND_DEVELOPMENTS Section 1 + open question 3. This proposal assumes the trio; WS-3 confirms (Q3 below). |
| Frontier advance (staleness clock) | **EXISTS.** `frontier_capability` per actor drives the overhang stream (`doom_system.gd:259-263`); ADR-0016 advances the frontier monthly via world packs. A "results go stale as the frontier moves" clock costs nothing new. |

Bottom line: like the office economy, this is a new SYSTEM on existing RAILS.
Compute already burns, already has a doom stream, already carries promises;
the workstream substrate is already ruled (ADR-0011); the influence stocks are
the same math as the social intermediaries. Rams #10 build.

---

## 2. The core design

### 2a. Two streams, one substrate

Every workstream (ADR-0011 s4 -- the L2 object; or, pre-L2, every
`focus_topic` from the pipeline-gap MINIMAL) carries one new data field:

    compute_intensity: 0.0 .. N   (compute units consumed per assigned
                                   researcher per month; 0 = desk work)

Two streams, then, are not two engines -- they are the two ends of one dial on
the one substrate the pipeline-gap doc scopes. "Compute-heavy" = workstreams
with high `compute_intensity`; "non-compute" = zero-or-low. The player never
learns a second system; they learn that SOME work eats the fleet and some
does not.

Recommended v1 stance [INFERRED]: expose it to the PLAYER as two named
streams (crisp parts, mentally modellable, matches Pip's wording), implement
it as the continuous field (sweepable, no schema churn if WS-3 later wants a
middle tier). The seed's own open question -- "two discrete streams or a
spectrum?" -- resolves as: discrete in fiction and UI, continuous in data. Q2
below ratifies this.

The asymmetry table (the actual design content):

| Axis | Compute-heavy | Non-compute |
|---|---|---|
| Fuel | Compute units/month (purchased, lead time, fungible, surge-able) | Researcher-months + founder hours (hired, onboarded, slow to scale, walk out the door) |
| Payoff period (ADR-0009 durations) | SHORT: 2-4 plan-months per artifact when fully fed | LONG: 4-8 plan-months per artifact |
| Delivery variance | LOW variance when fed -- benchmark-shaped, predictable ("we ran the evals, here are numbers") | HIGH variance -- breakthrough or fizzle (theory/governance are hit-or-miss) |
| Starvation mode | Progress CRAWLS or stalls when compute-starved; fuel is the binding constraint | Progress walks out the door when PEOPLE leave; retention is the binding constraint |
| Artifact shelf-life | STALES as the frontier advances (empirical results on last year's models age out) | ENDURES (theory, governance frameworks, norms do not stale with the frontier) |
| Downstream pump (Section 2e) | Technology influence + hype; adoption is FAST but decays | Politics influence; adoption is SLOW but durable |
| Doom bill | Fleet bills doom via `W_compute` (dual-use pricing, ADR-0011 s7) | None from the work itself |
| Visibility | HIGH -- a big fleet is legible to rivals/state (feeds the aggro/violence visibility thread, SEED item 5) | LOW -- quiet work keeps you off the radar |

The strategic texture this buys [INFERRED]: a TEMPO choice. Burst (raise money
-> buy compute -> fast legible results -> hype and Technology influence -> more
money) is the capabilities-flavored flywheel -- fast, expensive, doom-billing,
visible, and its outputs rot. Cultivate (hire -> retain -> slow uncertain
theory/governance -> durable Politics influence) is the safety-flavored long
game -- cheap to sustain, quiet, robust, and slow. Every real lab sits
somewhere on this line, which is the reality-tether working for us.

### 2b. Compute as procured fuel with lead time

Kill instant `buy_compute`. Compute procurement becomes plan-speed,
duration-bearing, and priced by the machinery that already exists
(ADR-0013's `FinanceEngine` -- same move as the office proposal's lease menu):

- **Spot compute:** short duration (delivery within the month), steep per-unit
  premium. The firefighting buy. Price scales with the hype cycle [INFERRED --
  ADR-0013 already prices raises by hype; compute demand is the same market].
- **Contract compute:** cheaper per unit, delivery lead time of 1-3 months,
  and a COMMITTED monthly spend for a term -- a recurring, lease-shaped
  obligation. This is the second predictable liability after rent
  (OFFICE_ECONOMY_PROPOSAL 2c), riding whichever rail WS-3 picks for rent
  (its Q2): payroll-style deduction or recurring ledger payable. Breaking a
  compute contract early bills a break fee, exactly the lease pattern.
- **Own cluster (AMBITIOUS tier only):** capex + office-tier requirement
  (racks need floor space and power -- couples to the office ladder), best
  unit economics, zero flexibility.

Why lead time is the load-bearing part [INFERRED]: it converts "I need
compute" from a spend into a PLAN. You must forecast next quarter's
compute-heavy workstreams a procurement-cycle ahead; a surprise opportunity
(a hot eval window, a rival's model to probe) forces the spot premium or a
cannibalize. That is ADR-0009's response-window economy reaching into
research, and it is what makes the two payoff PERIODS felt rather than
cosmetic: the compute stream's short artifact cycle hides a long fuel cycle
in front of it.

Compute engineers become the efficiency dial: each reduces effective
`compute_intensity` of assigned workstreams by a data-driven fraction
(their existing one-line fiction, "improves compute efficiency", landed
literally).

### 2c. Payoff periods, mapped to ADR-0009

ADR-0009 rule 5 says strategic actions have durations; ADR-0011 s4 says
workstreams run multi-month and produce artifacts. The streams differentiate
INSIDE that contract, adding no new time machinery:

- Compute-heavy workstream, fully fed: `duration_months` drawn from a SHORT
  band (anchor 2-4). Feeding below `compute_intensity` stretches the
  duration proportionally (crawl, never free).
- Non-compute workstream: `duration_months` from a LONG band (anchor 4-8),
  insensitive to compute, with an outcome ROLL at completion (breakthrough /
  solid / fizzle) whose variance is the stream's signature. Seeded child-RNG
  per the determinism discipline (RESEARCH_IDEA_PAPER_PIPELINE_GAP Section 3).
- Both emit artifacts at completion (papers first; systems/campaigns later
  per ADR-0011) -- artifact value routes through world-state FLOWS
  (adoption, alarm, absorption, influence), never a scored stock (ADR-0002
  rule 3 -- same constraint the pipeline-gap doc flags).

Guard rule respected: nothing here hangs a decision on the day tick. Feeding,
assignment, and procurement are all plan-speed; the day tick only advances
progress and burns fuel.

### 2d. Downstream impacts (what each stream DOES to the world)

- **Doom:** activate `W_compute` (one dial, `defaults.json:82`) so
  `dedicated_ai_compute` -- the fleet you hold -- prices the dual-use bet.
  Capabilities-flavored compute work also feeds `frontier_capability["player"]`
  as it already does conceptually via capability research; safety-flavored
  compute work (evals, interpretability at scale) raises `safety_absorption`.
  No printed doom anywhere (ADR-0015); the strip errand (WS3_FINISH_OR_DROP
  Section 5) keeps new stream content born clean.
- **Staleness:** each compute-heavy artifact records the frontier level at
  completion; its downstream contribution (adoption credit, Technology
  influence) DECAYS as the frontier advances past it (frontier already
  advances -- rival progress now, ADR-0016 monthly packs later). Non-compute
  artifacts decay slowly or not at all. This is the "different downstream
  impacts" made mechanical, and it feeds the league metabolism: every monthly
  world-pack frontier bump devalues everyone's stale empirical results --
  the world moves whether you do or not.
- **Visibility:** fleet size feeds the visibility/aggro thread (SEED item 5's
  "you got big enough to be a target"). Parked as a read-hook: the violence
  workstream reads `dedicated_ai_compute` when it lands; nothing to build
  here now. [INFERRED]
- **Influence:** the pumps -- Section 2e.

### 2e. The fluid influence web (item 3 -- the anti-tech-tree)

Seed item 3, with its own CLAUDE-note flag standing (INTERPRETATION -- confirm
with Pip): progression must be robust to influence being contested and argued
fluidly; prefer a fluid influence model over a locked tree.

The structure: **three influence stocks + gates that read current state.**

1. **Three stocks:** `influence.politics`, `influence.money`,
   `influence.technology` -- accumulate-and-decay stocks of exactly the
   `global_alarm` shape (gain per source event, multiplicative decay per
   tick). Reuse the intermediary pattern; no new engine class.
   - Technology is pumped by compute-heavy artifacts (staleness-decayed),
     hype, frontier position.
   - Politics is pumped by non-compute artifacts (governance/policy/theory
     socialized), conference presence, door time (founder hours).
   - Money is pumped by runway, raise history, revenue -- largely a READ of
     the finance state rather than a separate accumulator [INFERRED --
     candidate simplification; WS-3 can rule Money = f(balance sheet) and
     keep only two true stocks].

2. **Gates, not nodes:** every "unlock" in the game is an affordance with a
   THRESHOLD EXPRESSION over current influence, e.g. "Government consultation
   door: Politics >= 40", "Frontier-model access: Technology >= 35",
   "Institutional round: Money >= 30 AND Politics >= 15". A gate OPENS when
   the expression holds and CLOSES when it stops holding (with a grace
   period so a flicker is not a slam -- dial). In-flight uses survive;
   new uses do not.

3. **The RPS pressure (the polyvirate's teeth):** in any CONTEST -- rival
   envoy showdown, adoption battle, funding fight, late-game confrontation --
   each side leads with its dominant axis, and the fixed ordering applies a
   VISIBLE modifier: Politics beats Money beats Technology beats Politics.
   The player can mentally model it ("I built Technology; their Politics play
   discounts me here") -- Pip's Pokemon-legibility requirement verbatim.

4. **Convertibility with friction:** influence is not siloed -- Money can buy
   lobbyists (Money -> Politics at a lossy rate), Technology can be licensed
   (Technology -> Money), Politics can win compute allocations (Politics ->
   Technology). Conversions are plan-speed actions with durations and poor
   exchange rates (dial). Fluidity means no gate has a unique path; friction
   means the pump you built still matters.

Why this is ROBUST where a tree is fragile -- the four properties, named so
WS-3 can test candidate content against them:

- **State-reads, not history-reads.** A tree edge, once traversed, is
  permanent history. A gate reads NOW: the rival arguing influence away from
  you (contest events, smear campaigns, out-lobbying) closes doors you
  thought you owned. Progression must be MAINTAINED -- which is the whole
  fantasy of influence, and mechanically what "contested fluidly" means.
- **Contested by construction.** Rival actions and world events add/subtract
  the SAME stocks the player builds. There is no player-only progression
  track for the rival to be bolted onto later; the rival plays on the same
  three axes from day one (and their axis choice is the RPS read the seed's
  "shop over the road advertising Politics" vignette wants).
- **No unique paths.** Threshold expressions plus lossy conversion mean any
  gate is reachable from any build at a price. Kills the solved-order
  problem that makes tech trees degenerate into a wiki build-order.
- **Locally arguable.** [INFERRED -- the design-process reading of "robust to
  argument"] Adding or retuning a gate is a one-line threshold change that
  restructures nothing. In a prereq DAG, every content argument is a graph
  surgery; here WS-N can argue "should the government door need Politics 40
  or 55" forever without breaking anything else. The structure is robust to
  the DESIGN argument as well as the in-fiction one -- both readings of
  Pip's sentence are served, and WS-3 should confirm which he meant (Q1).

UI sketch (not this proposal's scope to spec): one panel, three bars with
gate-markers at thresholds, rival levels ghosted in silhouette (Carmen
Sandiego register -- inferred, not exact). No tree screen exists to build.

### 2f. How the two halves join

The streams are the PUMPS; the web is the RESERVOIR; the gates are what the
water is FOR. Compute-heavy research is the fast, expensive, decaying pump
into Technology; non-compute research is the slow, durable pump into
Politics; the finance game is Money. The tempo choice in 2a becomes a
POSITION choice on the web -- and the RPS means no position dominates,
because the rival's counter-position discounts yours in contests. That is
the portfolio-forcing structure ADR-0011's sweep target asks for ("a managed
portfolio must beat every constant line"), extended from effort allocation
to strategic identity. [INFERRED]

---

## 3. MINIMAL / MODERATE / AMBITIOUS ladder

Same form as RESEARCH_IDEA_PAPER_PIPELINE_GAP.md and the office proposal.
Every tier changes the sim -> forks the ladder -> EPOCH only, never a patch.
Batch with the ADR-0011 MINIMAL fork if both land the same epoch (one fork,
not two -- same point WS3_FINISH_OR_DROP makes for the ADR-0010 partition).

### MINIMAL -- typed burn + honest procurement (days-scale)

Rides the pipeline-gap MINIMAL (focus topics), does not wait for L2:

- `compute_intensity` per focus topic (data field on the topic table).
  Researcher burn becomes `compute_intensity[focus_topic]` instead of the
  flat 1.0 -- landing the parked #576 follow-up at `turn_manager.gd:166-168`.
  Compute-starved researchers on heavy topics crawl (existing `has_compute`
  gate, now proportional).
- `buy_compute` becomes duration-bearing (delivery in N ticks) -- removes a
  standing ADR-0009 rule-5 violation. One action edit + a pending-delivery
  entry.
- Data prep for the web: tag existing actions/artifacts with the influence
  axis they WOULD pump (inert field, no stocks yet).
- What it proves: does fuel-vs-people differentiation read at all; does
  procurement lead time create plan pressure.
- What it lacks: no workstreams, no contracts, no influence stocks, no RPS.

### MODERATE -- the real build (the recommended WS-3 target) [INFERRED]

Everything in MINIMAL, plus -- gated on the L2/#613 workstream substrate
(this tier IS a lane of that build, not a rival to it):

- Workstreams typed by `compute_intensity`; assignment UI shows people AND
  fuel; duration bands per Section 2c (short/fed vs long/high-variance).
- Procurement instruments: spot vs contract via
  `FinanceEngine.generate_offers()` (new instrument family, ADR-0013
  pattern); contract = recurring obligation on the rent rail; break fee.
- Activate `W_compute` (fleet bills doom); safety-compute work raises
  `safety_absorption`; artifact staleness clock vs frontier.
- Influence stocks v1: Technology + Politics as decaying stocks (Money as a
  finance read, per 2e simplification); 3-6 gates converting the most
  tree-tempting planned unlocks into threshold reads; one UI panel.
- RPS modifier applied in ONE contest surface first (rival adoption battles
  or envoy events -- whichever the Developments build lands first), visible
  in the result copy.

### AMBITIOUS -- market, argument, and the graduated rival (next-epoch-plus)

- Compute MARKET: hype-cycle pricing, supply-squeeze events fed by monthly
  world packs (ADR-0016 -- GPU shortages are real-world feedstock), rivals
  bidding on the same supply; sell/sublease spare fleet.
- Own-cluster instrument (capex + office-tier floor-space requirement).
- Full contested influence: rival as a graduated agent (SEED open Q1) running
  its own pumps and arguing gates open/closed; influence-conversion action
  family; multi-axis gate expressions everywhere.
- Late-game: visibility read (fleet size + influence profile) feeding the
  violence/aggro threshold work (SEED item 5) -- that workstream's design,
  not this one's.

Fork note: MINIMAL's data schema (compute_intensity per topic, axis tags)
must be a strict subset of MODERATE's (same fields on workstreams) so the
upgrade is a migration-free epoch. AMBITIOUS is its own future proposal.

---

## 4. The dials (tune in data, rule the SHAPE at WS-3)

All live in balance data. Anchors are for the sweep, not proposals to ship
[INFERRED throughout]:

| Dial | Anchor | The constraint that sets it |
|---|---|---|
| `compute_intensity` (heavy topics) | 3-6 units/researcher/month vs 0 for desk work | Must make a 3-researcher heavy workstream FELT against a 100-compute stock within ~2 months untopped -- if starting compute lasts a year, procurement never becomes a plan. |
| `compute_intensity` (non-compute) | 0 | Crisp parts: the stream identity is the zero. A "light" middle tier is a WS-N addition, not v1. |
| Spot premium | 2-3x contract unit price | Big enough that living on spot is a diagnosable leak; small enough that one emergency buy is a priced regret, not a run-ender. |
| Contract lead time | 1-3 months | Must exceed one plan cycle (else it is spot with paperwork) and stay under the short payoff band (else nobody contracts). |
| Contract term / break fee | 6-12 months / 2-3 months' committed spend | Mirrors the lease dial logic: commitment device, priced regret. |
| Heavy duration band | 2-4 months fed | Short enough to contrast with non-compute; long enough that no artifact lands inside one plan month (ADR-0009 no-instant-strategy). |
| Non-compute duration band | 4-8 months | The long game must overlap era-scale (multiple months of retention risk is the stream's real cost). |
| Fizzle/breakthrough split (non-compute) | ~25% / ~15%, rest solid | High enough variance to feel hit-or-miss; bounded so a fizzle streak is bad luck, not a death spiral. Seeded child-RNG. |
| `W_compute` | small positive (sweep from 0) | The dual-use bill: holding a big fleet must COST doom-rate visibly, but the overhang stream stays the dominant term (it is the thesis; compute is a contributor). |
| Staleness half-life (heavy artifacts) | 6-12 months of frontier advance | Fast enough that resting on old evals fails; slow enough that the short band is worth running. |
| Influence decay | ~0.99/tick (politics), tech decays via staleness instead | Politics rots if unattended (door time is upkeep); Technology rots by frontier, not calendar -- two different decay FICTIONS, one math shape. |
| Gate thresholds | 3-6 gates, first at reachable-by-month-~8 levels | Gates must open mid-run for most builds; a gate nobody reaches is a tree branch nobody argues about. |
| Gate grace period | 1 month below threshold before close | Flicker-proofing; keeps closes legible ("you lost the room") not noisy. |
| RPS modifier | +/- 20-30% on contest outcomes | Big enough to mentally model and plan around (Pip's Pokemon test); small enough that position never auto-wins a contest. |
| Conversion friction | 30-50% loss, 1-2 month duration | No unique paths, but the pump you built must stay the cheap path. |

Sweep hooks: bot policy axes = {all-compute, all-desk, balanced,
contract-early vs spot-only} x {tech-pump, politics-pump, convert-heavy};
targets = no constant stream-allocation dominates (extends the ADR-0011
portfolio target); no policy where never-contracting beats contracting
(else lead time is dead weight); staleness must show up as a measurable
decay in all-compute bots' late influence.

---

## 5. Coupling contract (what this reads/writes)

- **ADR-0011 / L2 (#613):** the streams are a TYPING of the workstream
  substrate, not a parallel system -- MODERATE here is a lane of the L2
  build. Compute promises (`compute_budget` ledger entries) finally have a
  demand signal: a researcher with a compute appetite on a starved heavy
  workstream is the promise-default story writing itself.
- **ADR-0009:** durations differentiate the streams; procurement lead time
  is plan pressure; nothing on the day tick but burn and progress.
- **ADR-0013 / finance_engine:** spot/contract compute = a new instrument
  family on the existing pricing engine (hype prices the purpose); contract
  rides the rent rail decision (office proposal Q2 -- decide ONCE for both).
- **ADR-0015 / doom_system:** `W_compute` activation; `dedicated_ai_compute`
  stops being a dead proxy; safety-compute raises `safety_absorption`;
  influence stocks reuse the intermediary accumulate/decay pattern. Born
  clean of printed doom (the Section-5 strip discipline).
- **ADR-0010 (adoption):** artifact staleness modulates adoption credit;
  the socialize step is the Politics pump for papers. Sequencing note: the
  ADR-0010 v1 absorption partition (WS3_FINISH_OR_DROP Section 1) should
  land BEFORE or WITH the influence pumps, or fast Technology adoption
  re-opens the basement-spam shape it exists to close. [INFERRED]
- **ADR-0016 (league metabolism):** monthly frontier advance drives
  staleness; compute supply-squeeze events are pack feedstock -- the
  reality-tether reaches the research economy.
- **OFFICE_ECONOMY_PROPOSAL:** contract compute is the second lease-shaped
  liability (shared rail, shared teaching curve); own-cluster (AMBITIOUS)
  reads office tier for floor space.
- **SEED_RIVAL_AND_DEVELOPMENTS:** the polyvirate gets its mechanical home;
  the rival's axis choice + RPS is the "shop over the road" read; contest
  events are the Developments engine's mechanical teeth candidate (its open
  Q2).
- **ADR-0002 (scoring):** influence stocks and artifacts are world state
  producing flows; nothing here is a scored stock. Score stays
  turns-survived, untouched.
- **Ladder:** every tier forks (sim change); epoch-only, batch with the
  ADR-0011 MINIMAL fork where possible.

---

## 6. Crisp questions WS-3 must decide

1. **Ratify the anti-tree.** Gates-on-decaying-contested-influence (state-
   reads, not history-reads) is THE progression structure -- no prereq tech
   tree, now or later. This is the biggest call in the doc: it forecloses a
   familiar structure permanently. Also: confirm the item-3 interpretation
   (the seed's own CLAUDE-note flags it) -- did Pip mean in-fiction contested
   influence, design-process robustness, or both? The structure serves both,
   but the reading changes emphasis. [INFERRED interpretation]
2. **Discrete or spectrum?** Two named streams in fiction/UI, continuous
   `compute_intensity` in data (recommended) -- or truly discrete? The seed
   asks this verbatim.
3. **Confirm the polyvirate.** Politics/Money/Technology as the axis set
   (SEED Q3), with the streams pumping Technology (compute) and Politics
   (non-compute) -- and is Money a true stock or a read of the finance state
   (2e simplification)?
4. **Procurement rail.** Does contract compute ride the same rail as rent
   (office Q2)? Decide the recurring-obligation rail ONCE for both
   instruments so the ledger/payroll choice does not fork.
5. **`W_compute` activation and sequencing.** Does the player's own fleet
   bill doom from MODERATE day one, and does this land before/with/after
   the ADR-0010 v1 absorption partition (both touch the same stream
   engine and both fork the ladder)?
6. **Which epoch, and what batches?** MINIMAL is days-scale and could ride
   the same epoch as the pipeline-gap MINIMAL (one fork). MODERATE is a lane
   of L2/#613. Given the office economy and hire-epic are competing for the
   same windows, sequence explicitly. [INFERRED capacity judgment]
7. **Gate content v1.** Which 3-6 affordances become the first gates?
   Candidates: government consultation door, frontier-model access,
   institutional funding round, invited-gathering stream (the ADR-0014
   piece WS3_FINISH_OR_DROP suggests deferring -- a gate gives it a home),
   late-game state-actor contact. Pick ones a mid-run player actually
   reaches.

---

## 7. Out of scope (named so they stay out)

- The violence/military system (SEED items 4-5) -- this doc only leaves it
  read-hooks (fleet visibility, influence profile).
- The Developments/Sightings narrative engine -- contest events are its
  customer, not its spec.
- Conference/adoption build order -- ruled in WS3_FINISH_OR_DROP (0014 after
  0010-v1); this doc only couples to the result.
- Compute market simulation depth (order books, futures) -- AMBITIOUS caps at
  offers + squeeze events; anything deeper is fiddle (Rams #10).
- A fourth influence axis (Culture/Public) -- the public-opinion system
  exists separately (PUBLIC_OPINION_SYSTEM.md); folding it in is a WS-N
  argument the gate structure can absorb LATER without surgery -- which is
  the point of the structure.
- UI spec for the influence panel and assignment screen -- lands with the
  plan-screen redesign already owed (ADR-0011 Consequences).

# Office economy -- lease, floor-space, hire caps (WS-3 Theme B proposal)

> Status: PROPOSAL for Workshop 3 (issue #811, LOCKED Wed 2026-07-30 -- note the
> WS-3 prep chatter sometimes says 07-29; #811 is the scheduling SSOT). Drafted
> 2026-07-25 by a research agent so Theme B has something to workshop against
> (WORKSHOP_3_PREP.md Section 5, decision 4: "if Office economy is in scope,
> someone must WRITE the proposal first"). Nothing here is ratified. Claims are
> grounded in issue #791, ADR-0009/0011/0013, SEED_RIVAL_AND_DEVELOPMENTS.md,
> DESIGN_PHILOSOPHY.md, and greps of `godot/scripts` + `godot/data` on
> 2026-07-25. Inferences are marked [INFERRED]. All numbers below are DIALS,
> not values -- magnitudes are the sweep's job (DQ-8), shape is WS-3's.

---

## 0. The one-paragraph pitch

The office is the early game's shape-giver. You start in a bedroom/basement
that HARD-CAPS your hires; with your starting money you are forced into one
small, real decision early -- WHICH lease to sign -- and that lease is the first
loan-shaped thing every run signs: cash down, rent falling due every month
(predictable ledger liability), a break fee if you leave (switching cost). The
thesis is Pip's #791 ruling verbatim: "first unlocks small-now,
bigger-over-time; switching costs." Signing the first real lease is also the
fictional seam where startup-era becomes office-era (SEED doc: the "Step Up"
beat) -- it flips the event pools and finally gives the office-floor render
surface a game-state input. Philosophy anchor: "we don't power up the player,
we power up the office" -- progression lives in the org, and the office IS the
org's body.

---

## 1. What is real vs absent today (verified 2026-07-25)

Greps across `godot/scripts/**` and `godot/data/**` for
lease/rent/floor_space/hire_cap/office_tier/era:

| Piece | Status |
|---|---|
| Lease / rent / floor-space system | **ABSENT.** No core system, no data file, no GameState field. |
| Hire cap | **ABSENT.** The only cap is `state.MAX_CANDIDATES` (candidate POOL size, `hiring_pipeline.gd:186`) -- employed headcount is unbounded. |
| Office render surface | **EXISTS, UI-only.** `godot/scripts/ui/office_floor/` (office_floor.gd, employee_sprite.gd, employee_fsm.gd): desks, sprites, collaboration. `@export var office_tier: int = 0` (office_floor.gd:52) is never driven by game state -- the tier is a dead knob waiting for this system. #793 tracks its art bugs; the surface is live. |
| `office_maintenance` action | **EXISTS as a no-op** ($5000 + 1 AP "improves morale slightly", `data/actions/operations.json`) -- the 1,300-commits-ago proof-of-concept money sink, being REMOVED from the board in v0.13.1 (SEED doc appendix). Its retirement leaves the office with zero mechanical presence. |
| Era / event-pool gating | **ABSENT.** `core_events.json` events gate on `min_turn` / `trigger_condition` / probability; no era or beat tag exists. |
| Rent-shaped payment rails | **TWO EXIST.** (a) Payroll: direct per-tick deduction (`turn_manager.gd:109`, `Clock.annual_to_per_turn`) with a named `funding_starvation` death cause. (b) Ledger: `Ledger.Entry` payables with fuse/interest/counterparty (`ledger.gd`). Rent can ride either -- Section 4 question Q2. |
| Lease pricing machinery | **EXISTS.** `finance_engine.gd` is a stateless pricing engine (org type / counterparty / typed rep / hype / leverage) whose `generate_offers()` already mints 2-3 concurrent standing offers with expiry. A lease menu is a new instrument family on an existing engine, not a new engine. |
| Starting cash | $245,000 (`data/balance/defaults.json` `starting_resources.money`). Attention is 20/month (`attention.per_month`, `game_state.gd:234`). |

Bottom line: the office economy is a genuinely NEW system, but every rail it
needs (ledger, pricing engine, month boundary, render surface, data-driven
actions) already exists. This is a Rams #10 build: reads/writes on existing
machinery, one new data file, one new GameState surface.

---

## 2. The core design

### 2a. Office tiers as a data-driven ladder

A small data file (`godot/data/offices.json` or a `balance/defaults.json`
block -- self-describing per ADR-0004-data) defining ~4 tiers:

- **Tier 0 -- bedroom/basement.** Free. Hire cap: severe (the "hard base
  limit" of #791). No deposit, no rent, no meeting room. The starting state.
- **Tier 1 -- the first real lease.** Small office. The forced early decision.
- **Tier 2 -- a real floor.** Mid-game. Where managers/teams live (ADR-0011).
- **Tier 3 -- the building.** Late-game; mostly reserved space for the era
  when "payroll is automated" (ADR-0011 endpoint vignette).

Each tier carries: `hire_cap`, `deposit`, `rent_per_month`, `break_fee`,
`fitout_cost`, `min_term_months`, plus an `era` tag (Section 2d) and the
`office_tier` int the render surface already exports.

### 2b. Hire cap = desks (the spatial constraint)

`GameState` gains a derived `hire_cap` from the current office tier. The
hiring pipeline refuses (or the offer stage warns and blocks) when
`employed_count >= hire_cap`. This is #791's pointer ("hiring cap on
GameState") landed literally.

Design intent: the cap is what makes the lease decision REAL. Without it,
tier 0 is merely cheap and no one ever moves. With it, the third hire (or
whichever the dial says) is impossible until you sign -- the game's first
"small-now" unlock whose payoff is everything that team later produces
("bigger-over-time").

Recommended semantics [INFERRED]: **HARD cap, crisp refusal** ("No desk. Get
an office."), not a soft overcrowding debuff. Rationale: crisp-parts thesis
(#811) -- a debuff is interface mush, a locked door is a legible decision
prompt. The soft variant is Q1 for Pip.

Cap magnitudes want to align with the management-grain phase changes Pip has
already ruled ("as a CEO, I care about managing the first half dozen people or
so. Then I probably want team leaders..."): tier 1 caps around the half-dozen,
tier 2 is where managers become mandatory-feeling, so the SPATIAL ladder and
the MANAGEMENT ladder reinforce each other instead of inventing two curves.
[INFERRED]

### 2c. The lease as a priced liability (not a bespoke sink)

The lease is a financing instrument, priced and offered by the machinery that
already exists:

- **Offer menu:** reuse `FinanceEngine.generate_offers()` -- a "seek office"
  action at plan speed mints 2-3 standing lease offers with expiry (#811
  agenda item 1's "choose 1 of 3 offices" falls out of the existing
  offer-optionality pattern for free).
- **Pricing inputs:** org type, counterparty (the LANDLORD is a counterparty
  -- commercial agent vs university sublet vs a philanthropist's spare floor,
  each with strings), typed reputation, leverage. ADR-0013's engine, new
  instrument family.
- **Signing:** pays `deposit + fitout` cash now (the forced early spend of
  #791) and opens the recurring rent obligation.
- **Rent cadence:** falls due at the MONTH BOUNDARY (ADR-0009 -- routine
  obligations live at plan grain; nothing hangs on the day tick).
- **Switching costs:** breaking a lease early bills the `break_fee` (a ledger
  payable with a short fuse), and the move itself has a duration during which
  the office is disrupted (ADR-0009 durations; a visible, timed debuff per
  the one-status-layer ruling). Moving is a plan-speed strategic action.

Why this matters beyond the office: rent is the first PREDICTABLE,
NON-COMPOUNDING liability every run meets. It teaches the appetite/promise/
ledger loop safely -- the player learns "obligations fall due on a clock"
weeks before the compounding instruments can kill them, consistent with "the
opening is nearly unlosable; the ruin you build there finishes you later."
[INFERRED framing, but it follows directly from ADR-0003 + the 6-month floor
ruling.]

### 2d. The era seam (what the lease unlocks beyond desks)

SEED_RIVAL_AND_DEVELOPMENTS.md: the beat ladder (...Office Crisis, Step Up)
"leads to early-midgame and we shift out of startup-era to office-era", and
the era shift "signifies changes in the styles of events that the event pools
can draw from."

Proposal: **signing the tier-1 lease IS the Step Up beat** -- the concrete,
player-authored act that flips `startup_era -> office_era`. Mechanically:

- Events gain an optional `era` tag (extends the existing trigger fields; no
  new engine). Startup-era pool: Cat Encounter, Kind Stranger, Local Problem
  flavor. Office-era pool: Office Crisis genre, landlord/rent-review events,
  the parked janitor/ambient-upkeep idea (tier 2+, per its own note "probably
  only relevant once we get larger offices").
- `office_tier` finally drives the render surface (office_floor.gd:52) -- the
  player SEES the era shift as a bigger room filling with desks. Progression
  lives in the org; the office is its visible body.
- Larger tiers carry ambient upkeep that scales with org size (the janitor
  seed) -- office-era texture, NOT a tier-0/1 mechanic.

This keeps the era shift legible and earned rather than calendar-driven, which
matches the aggro-threshold philosophy ("keys to the visibility of the
player's impacts, not the calendar"). [INFERRED alignment -- WS-3 should
confirm the lease is the trigger rather than one trigger among several.]

### 2e. Attention coupling (the AP sink, done carefully)

#791 asks for rent as a "predictable AP/cash sink". Two readings:

- **Literal:** rent-due charges Attention every month. On-theme ("Admin is
  painful in this game, I want that to be part of the overhead") but it is a
  flat tax that no decision can improve -- pure interface pain, zero decision
  content. MaRo/Rams lens says beware.
- **Demand-typed (recommended [INFERRED]):** office admin is a TYPED DEMAND
  (the ops/admin category, DQ-24) that ops staff can absorb (ADR-0011 point
  6: "ops/admin staff reduce the founder-price of routine actions and
  automate whole classes"). Early game: rent-due pings you for a point of
  Attention (painful, felt). Hire an ops person: the demand routes to them.
  The sink exists AND buying it away is a real decision -- exactly the
  staff-buy-back-founder-time loop. Exceptions (rent review, landlord
  dispute, missed payment) stay founder-priced.

---

## 3. MINIMAL / MODERATE / AMBITIOUS ladder

Same form as RESEARCH_IDEA_PAPER_PIPELINE_GAP.md. All three tiers change
gameplay -> ALL fork the ladder -> this lands in an EPOCH (monthly release
train), never a patch. Corollary: the build-vs-ladder version split
(DISTRIBUTION_AND_PATCHING.md) does not block this work (epochs fork anyway),
but the epoch that carries it must be labeled as forking.

### MINIMAL -- cap + one lease (days-scale)

- `hire_cap` on GameState, derived from an `office_tier` int (0/1).
- One plan-speed action: "Sign a lease" (tier 0 -> 1). Fixed data-driven
  deposit + rent. Rent rides the PAYROLL rail (same per-month deduction path,
  same funding-starvation death attribution) -- no finance_engine involvement
  yet.
- Wire `office_tier` into office_floor.gd.
- Data: an `offices` block in `balance/defaults.json` (2 tiers).
- What it proves: does the cap + forced spend give the early game shape?
  Sweepable immediately (bot policies: sign-early vs sign-late vs never).
- What it lacks: no choice-of-3, no switching costs, no era gate. The lease is
  a door, not yet a decision.

### MODERATE -- the real Theme B (the recommended WS-3 target; ~1-2 weeks) [INFERRED]

Everything in MINIMAL, plus:

- **Choose 1 of 3:** lease offers via `FinanceEngine.generate_offers()` with
  landlord counterparties and standing-offer expiry (#811 agenda item 1).
- **Lease as contract:** deposit, term, break fee; rent as a recurring ledger
  payable (or payroll-rail with a ledger-backed break fee -- Q2); switching
  costs real (break fee + move duration + disruption debuff).
- **Era gate:** `era` tag on events; tier-1 signing flips startup->office
  pools; Office Crisis genre gets a home.
- **Attention:** demand-typed office admin, absorbable by ops staff (2e).
- 3-4 tiers in data; tier 2+ exists but is mostly runway for later content.

### AMBITIOUS -- the procurement/floor-space substrate (next-epoch-plus)

- Desks/equipment as fungible inventory with lead times (#804's two-clock
  procurement: order-early-vs-wait tension, laptop auto-provision from office
  stock -- #811 agenda item 2 already wants the laptop half).
- Floor-space as continuous area rather than tier caps; sublet/downsize;
  multi-site (a second city ties to regional influence / meetups).
- Landlord as a persistent relationship counterparty; office address as a
  finance_engine pricing input (VCs price the garage differently).
- Ambient upkeep + janitor as office-era texture scaling with org size.
- Dependencies: the L2 effort-economy substrate (#613) and the #804 inventory
  layer. Do NOT gate MODERATE on any of this.

Fork note: MINIMAL->MODERATE is additive (MINIMAL's data schema should be a
strict subset of MODERATE's so the epoch after can upgrade without a second
migration). AMBITIOUS is a different substrate; treat it as its own future
proposal once #804 is scheduled.

---

## 4. The dials (tune in data, rule the SHAPE at WS-3)

All live in balance data, none hardcoded. Starting points are anchors for the
sweep, not proposals to ship [INFERRED throughout]:

| Dial | Anchor | The constraint that sets it |
|---|---|---|
| `offices.tier0.hire_cap` | 2-3 | Must bind BEFORE the player has a working team -- the cap is what forces the lease decision. If most runs never feel it, it does not exist. |
| `offices.tier1.hire_cap` | 6-8 | The "first half dozen people" management grain; tier 2 should start where managers become the answer. |
| `offices.tier2.hire_cap` | 15-20 | Manager-era; pairs with ADR-0011 team structure. |
| `offices.tier1.deposit + fitout` | 10-25% of starting cash ($25k-60k vs $245k) | Big enough to be a real spend ("force a little spend", #791), small enough that the opening stays nearly-unlosable (the 6-month floor ruling T9). |
| `offices.tier1.rent_per_month` | 5-15% of typical monthly burn at that headcount | Real-world SME anchor is rent ~= 5-10% of payroll; rent should be FELT in the runway math but never be the thing that kills you alone -- deaths route through the ledger cascade, attributably. |
| `rent cadence` | Monthly, at the month boundary | ADR-0009; not a dial so much as a rule -- do not hang rent on the day tick. |
| `offices.tierN.break_fee` | 2-4 months' rent | Switching cost big enough that WHICH lease you sign matters (commitment device), small enough that correcting a mistake is a priced regret, not a run-ender. |
| `move_duration` / disruption | days-scale, visible debuff | One-status-layer ruling: a timed, legible debuff, never a hidden penalty. |
| `attention.rent_admin` | 1 Attention/month at tier 1, absorbable by ops staff | The #791 AP sink, made buyable-away (2e). Exceptions stay founder-priced. |
| `era_flip_tier` | 1 | Which tier flips startup->office era. If tier 1 proves too early in playtest, this is a one-int retune. |

Sweep hooks: bot policy axes = {never-lease, lease-ASAP, lease-at-cap,
lease-late}; floor target = no standard policy dies under 6 months BECAUSE of
rent; exploit check = no policy where staying at tier 0 forever dominates
(if it does, the cap is too loose or tier-1 payoff too weak).

---

## 5. Coupling contract (what this reads/writes)

- **ADR-0011 (effort economy):** rent = the predictable liability + typed
  admin demand; ops staff absorb it (the staff-buy-back-time loop gets its
  first concrete recurring demand). Hire cap gives the hiring pipeline
  (#789) a spatial gate. The cap magnitudes co-move with the management
  grain.
- **ADR-0013 / finance_engine.gd:** lease offers are a new instrument family
  on the existing pricing engine; landlord = counterparty; the choose-1-of-3
  menu is `generate_offers()` reused. No new pricing code path.
- **ADR-0003 / ledger.gd:** break fees (and optionally rent itself, Q2) are
  ledger payables -- deaths stay attributable ("the lease break fee is what
  cascaded me").
- **ADR-0009:** lease/move at plan speed with durations; rent at the month
  boundary; landlord disputes can open response windows (ADR-0012 taxonomy).
- **Era shift (SEED doc):** tier-1 signing = the Step Up beat; `era` tag on
  event pools; office-era genres (Office Crisis, rent review, janitor
  ambience at tier 2+) get their gate.
- **Render surface (#793):** `office_tier` becomes state-driven; the art
  lane's fixes land on a surface that now means something.
- **#804 procurement:** AMBITIOUS-tier extension point; MODERATE stays
  decoupled except laptop-from-office-stock if #811 item 2 lands it first.
- **Scoring/ladder:** no scoring change; forks the ladder purely because
  legal action space and economy change (epoch-only, per the release train).

---

## 6. Crisp questions WS-3 must decide

1. **Cap semantics:** hard cap (crisp refusal: "no desk") vs soft cap
   (overcrowding debuffs)? Recommendation on the table: HARD (crisp parts,
   brutal decisions). [INFERRED]
2. **Rent rail:** payroll-style monthly deduction (simple, predictable,
   reuses funding-starvation attribution) vs recurring ledger payable
   (uniform liability machinery, post-mortem trail, but ledger entries are
   currently one-shot -- recurring minting is new plumbing)? MINIMAL can ship
   payroll-rail and migrate; decide the END state now so the data schema
   does not churn.
3. **Is the first lease FORCED or attractive?** Tier-0 cap of 2 makes it
   near-forced; cap of 4 makes it a timing choice. Which early-game feel does
   Pip want -- everyone signs by turn ~3-5, or lease-timing as a strategy
   axis?
4. **What differentiates the 3 offices?** Price/capacity only (clean,
   sweepable) vs strategic texture (location -> which meetups/SA channels/
   counterparties are near -- couples to regional influence and the scouting
   tree)? Texture is tempting but drags Theme A/C scope in. [INFERRED risk]
5. **Era flip:** is signing tier 1 THE startup->office transition, or one
   input among several (headcount, first paper, first manager)? One trigger
   is legible; multiple is realistic. Crisp-parts lens says one.
6. **Does the bedroom price your money?** Should org address feed
   finance_engine pricing (VCs discount the garage) -- now, later
   (AMBITIOUS), or never?
7. **Which epoch?** MINIMAL vs MODERATE for the next forking epoch, given
   the other WS-3 lanes (#789 hire-epic, L2 effort economy) competing for
   the same window. MODERATE is recommended only if the L2/#613 lane is NOT
   also landing that epoch. [INFERRED capacity judgment]
8. **Downsizing/exit:** can you go DOWN a tier (fire the office to save the
   org)? Cheap to allow via the same break-fee machinery; decide whether the
   fiction wants it day one.

---

## 7. Out of scope (named so they stay out)

- Per-desk/per-room placement, pathfinding gameplay -- the office floor stays
  a RENDER surface, not a sim (Rams #10).
- The #804 procurement/inventory layer beyond the laptop hook (its own
  next-epoch item).
- Multi-site / relocation-to-another-city (regional influence is a scouting-
  tree topic).
- A morale/comfort sim tied to office quality -- office quality may surface as
  flavor and (later) a pricing input, never a mood engine ("bother," not HR
  gravity).
- Janitor/ambient upkeep implementation (tier 2+ office-era content; the seed
  stays parked in SEED_RIVAL_AND_DEVELOPMENTS.md appendix).

# End-game and the arrival of violence (WS-3 proposal)

> Status: PROPOSAL for Workshop 3 (issue #811, LOCKED Wed 2026-07-30). Drafted
> 2026-07-25 by a design agent from `SEED_ENDGAME_AND_VIOLENCE.md` (Pip's
> 2026-07-25 brain dump) so the end-game/violence seed has something to
> workshop against, in the same form as `OFFICE_ECONOMY_PROPOSAL.md`. Nothing
> here is ratified. Claims are grounded in the seed doc, DESIGN_PHILOSOPHY.md,
> ADR-0002 (survival spine, root docs/adr/0002), ADR-0003 (liability ledger),
> ADR-0015 (doom streams), DESPERATION_SOLVER.md, DIAL5 proposals (B+C+D
> ratified 2026-07-14), SEED_RIVAL_AND_DEVELOPMENTS.md, WORLD_AND_LORE.md, and
> greps of `godot/scripts` + `godot/data` on 2026-07-25. Inferences are marked
> [INFERRED]. All numbers are DIALS -- magnitudes are the sweep's job, shape is
> WS-3's.

---

## 0. The one-paragraph pitch

The arrival of violence is the end-game's phase marker: the point where the
world is frightened enough that force enters the repertoire, and where being
visible means being a target. It replaces today's calendar-keyed "endgame"
(one constant, `endgame_turn: 200`) with a world-state trigger; it supplies
the diegetic content the ratified DIAL5-C attention ramp was always going to
need (violence eats attention -- yours, or your security chief's); and it
resolves Pip's sharpest fork with his own instinct made mechanical: diving
into military at violence-onset is a desperation trap the solver can prove
(same monotone shape as the desperation lever), while a QUIET, EARLY security
hedge is negative-EV insurance that occasionally, expensively, isn't a trap --
the difference between the two is LEAD TIME, which is already the game's
deepest rule ("tragedy requires lead time"). Violence never reduces doom and
never wins the game; it buys survival months in a world that is ending, at
prices denominated in the thesis itself (a safety lab with a militia has lost
the argument -- mechanically: military posture corrodes the adoption
credibility that the apex victory runs through).

---

## 1. What is real vs absent today (verified 2026-07-25)

Greps across `godot/scripts/**` and `godot/data/**` for
military/violence/security/aggro/endgame/escalation:

| Piece | Status |
|---|---|
| End-game trigger | **EXISTS as a calendar constant.** `events.endgame_turn: 200` (`data/balance/defaults.json:10`); the ONLY thing it does is flip `window_demand_budget` 3 -> 6 (`month_controller.gd:51-56`). This is the code face of the seed's named flaw: "overly simplistic and not consuming enough attention." |
| Military / violence content | **ABSENT.** No actions, events, or state. The only hits are pre-horizon historical texture (`data/historical_events.json`: Project Maven, military-AI papers) -- which is fine and stays. |
| Security / defence capacity | **ABSENT** as a stock. `risk_pool.gd` has an `insider_threat` pool (adjacent, internal-facing); nothing outward-facing. |
| Rival aggression | **DORMANT FIELD.** `RivalLab.aggression: float = 0.5` (`rivals.gd:27`) only sets a `focus` label at init; no attack behavior exists. DQ-22 (aggro-threshold midgame) owes the mechanism; roadmap earmarks it as the v0.13 workshop (WS-4 / Theme E). |
| Desperation-trap machinery + verdict | **EXISTS AND PROVEN.** `desperation_lever` (`actions.gd:392`, `data/actions/financing.json:23`) plants a secret compounding governance liability. DESPERATION_SOLVER.md: firing it earlier/more is monotonically WORSE; it converts doom-root deaths into ledger-root deaths and costs median months. The trap SHAPE this proposal reuses is solver-verified. |
| Doom-stream landing sites | **WIRED, ZERO CONTENT.** Nine-stream engine (ADR-0015): `global_panic`, `global_alarm`, `ambient_risk` streams live; typed dampers and scheduled pulses wired with no content (WS3_FINISH_OR_DROP.md Section 1). Violence-era pressure has a clean intake: `add_stream_input()` is the single authority. |
| Attention/window economy | **EXISTS; scarcity ratified, decimals deferred.** Window face cost 1 vs supply 20 (the 6.7x oversupply finding); DIAL5 package B+C+D RATIFIED 2026-07-14 (demand rise + era scaling + uninsured premium), numbers after doom recalibration. Violence-era demand is DIAL5-C's missing diegetic content. |
| Death machinery | **EXISTS.** `death_attribution.gd` (L6 chain); ledger-root vs doom-root death causes distinguished in the solver harness. Epitaph end-states exist as lore (WORLD_AND_LORE.md), not yet as a content system. |
| Defeat conditions | doom >= 100 OR reputation <= 0 (ADR-0002); graceful concession is a backlogged mechanic, not built. |

Bottom line: like the office economy, this is a genuinely NEW content layer,
but every rail it needs (streams, ledger, windows, response taxonomy, death
attribution, the solver harness) already exists. The one hard dependency that
does NOT exist is the DQ-22 rival-aggro midgame -- Section 5 treats that as a
sequencing fact, not a blocker for the shape decision.

---

## 2. The core design

### 2a. THE fork: is "dive into military" a winning branch or a trap?

Pip's seed: the player "should be pretty outgunned unless they dive hard into
military opti[ons]". The secretariat note names the tension: a safety lab
pivoting to military power cuts against the thesis. Pip's own instinct,
relayed for this proposal: "a trap that occasionally, expensively, isn't."
Both readings, designed mechanically, then the recommendation.

**Reading B -- legitimate branch.** Military/security is a fourth strategic
posture (beside Mogul/Hustler/Operator: call it the Hardened lab). Mechanics:
a `security_posture` stock built over months via plan-speed actions with real
durations (guards, hardening, counter-intel, later drone-swarm rents from the
2037 vignette). Payoff: violence-class windows cost less attention and do
less damage; directed-violence events (raids, black-bags) roll against
posture; high posture deflects or downgrades them. The branch WINS by
surviving the violent end-game longer than any unhardened build can --
survival time is the score (ADR-0002), so outliving the soft labs is a
legitimate ladder strategy. What makes it a real branch: the payoff is
denominated in the actual scoring currency (months), and the cost curve is
paid in the same resources as every other strategy (money, attention, rep).

**Reading T -- desperation trap.** Military options are a late-game lever
family with the proven desperation shape: visible help now (this month's raid
deflected, this window cheaper), compounding bill later. The bills, each on
existing machinery:
- **Ledger:** arming mints liabilities -- contractor dependencies with fuses,
  a secret entry per dirty capability (exposure converts to rep/governance
  damage, ADR-0003 verbatim machinery).
- **Doom streams:** militarizing an AI lab legitimizes the security-race
  framing -> inputs to `global_panic` and `frontier_capability` pressure
  [INFERRED stream mapping -- exact streams are a WS-3/sweep call]. Your
  protection accelerates the thing killing everyone.
- **Adoption corrosion:** the apex path and the majority doom share bend only
  through adoption (ADR-0010). A militarized lab's safety work stops being
  adopted -- posture applies a damper-blocker or credibility multiplier < 1 on
  adoption credit [INFERRED mechanism; the principle is the thesis itself].
- **People:** the moral crusader resigns (WORLD_AND_LORE archetype 3's
  departure trigger, generalized); attachment built to be spent.

**The recommendation -- Pip's instinct, formalized as a LEAD-TIME keyed
mechanic.** Do not choose between the readings; make TIMING the variable that
selects between them, because the machinery for that already exists and the
game already teaches it:

- **The DIVE (buy military AT or AFTER violence-onset) is the trap.** Panic
  procurement is priced like the desperation lever: expensive, fast, dirty --
  instant posture, maximal liability minting, worst stream side-effects.
  Solver-provable: `dive_at_onset` policy must be median-negative months vs
  baseline, with death-cause conversion (doom-root -> ledger/exposure-root),
  exactly the DESPERATION_SOLVER fingerprint.
- **The HEDGE (buy quiet security EARLY, with months of lead time) is the
  "occasionally, expensively, isn't."** Slow, legal, boring: negative EV at
  the median (most seeds, the posture is money and attention you wasted --
  insurance usually is), but in high-violence seeds it converts into real
  survival months. The tail pays; the mode does not. This is
  slack-as-insurance (DESIGN_PHILOSOPHY, "On the turn") applied to the
  end-game, and tragedy-requires-lead-time applied to force.
- **Honest-trap discipline (the DQ-25 lesson):** the desperation lever's open
  question was whether its cost is "intended cost you can see coming, or a
  mispriced sucker-lever." For military, make ALL costs visible (rep hit,
  staff departures, upkeep, ledger entries on the books) -- the only
  irreducibly hidden variable is whether THIS seed's end-game will be violent
  enough to repay the premium. Uncertainty about the world is honest;
  hidden pricing is not.
- **The thesis cap:** military posture never reduces doom, and above a
  posture threshold the doom-0 apex victory is unreachable (adoption
  corrosion makes the last damper unbuildable). A militarized safety lab can
  outlive the other labs; it cannot save the world. [INFERRED as mechanism;
  as principle it is the seed's own tension resolved in favor of the thesis.]

Why not pure Reading B: it makes "outgunned unless they dive" a build-order
tax and turns the end of the world into a tower-defence layer -- and it
contradicts the desperation-levers-are-the-only-catch-up ruling (ADR-0003).
Why not pure Reading T: if military NEVER pays, the seed's "pretty outgunned
unless" clause is a lie, players solve it once ("never touch it") and the
whole content layer becomes scenery. The lead-time split keeps the decision
live every run: how much premium, how early, against how much seed
uncertainty. [INFERRED judgement throughout this paragraph.]

### 2b. The trigger: what fires the arrival of violence

Three candidates from the seed, one recommendation.

- **Candidate 1 -- rival aggro-threshold (DQ-22).** Violence = the top rungs
  of the rival attack ladder (litigation -> psyops -> ... -> force).
- **Candidate 2 -- doom threshold.** Violence when doom crosses a band.
- **Candidate 3 -- player visibility.** You got big enough to be a target;
  the reputation ladder (seed item 4) points here.

**Recommended: a TWO-AXIS trigger -- world fear ARMS violence; player
visibility AIMS it.** [INFERRED -- this is the proposal's main design move.]

- **Axis 1 (arming): world fear.** A derived band over existing world state
  (inputs: `global_panic`, doom level, frontier proximity -- read-only over
  ADR-0015 streams, no new state). When the world crosses into the fear band,
  violence enters the event repertoire GLOBALLY: the feed starts carrying
  violence happening to OTHERS (a rival's datacenter sabotaged, a researcher
  abducted elsewhere). The era arrives whether or not you matter -- doom is
  the background climbing (Doom-is-a-rate ruling); its late texture is force.
- **Axis 2 (aiming): your visibility.** Your share of the violence is
  allocated by visibility/reputation/impact -- the same key as DQ-22's ruled
  midgame line ("rival attention keys to the visibility of the player's
  impacts, not the calendar"). Low-visibility labs watch the violence era in
  the feed; high-visibility labs get the conference-room windows.
- **Division of labor with DQ-22:** the rival aggro ladder stays the MIDGAME
  system (rivals attack your interests); state/world violence is the ENDGAME
  layer ABOVE it. The handoff: DQ-22's top rungs (leak-seeking, psyops) are
  the fear-band's leading indicators. One escalation vocabulary, two owners.
  [INFERRED -- WS-3 should ratify the handoff explicitly so the DQ-22
  workshop (v0.13 / WS-4) inherits a boundary, not a collision.]
- **What this replaces:** `endgame_turn: 200`. The calendar step dies; the
  window-budget ramp keys to the fear band / escalation level (Section 2c).
  Calendar-keyed endgame is exactly the aggro-philosophy violation the
  midgame ruling already rejected.

**The point of no return -- escalation as a RATCHET.** Crossing into the fear
band should be "incredibly hard to recover from" (seed) without being an
unwinnable flag (survival spine: legible steepness, never a hidden loss).
Mechanism: an `escalation` level that violent events increment; it applies
standing pressure into the fear-band inputs (a feedback loop: violence
frightens the world, fear licenses violence). De-escalation exists but only
at sacred-object grade -- the doom-floor pattern (falls are legal, sustained
falls are a balance bug) applied to escalation. Recovery is a designed
near-impossibility, not an impossibility: the drama of the near-terminal
state is that the exits are visible and unaffordable. [INFERRED mechanism;
the ratchet-with-expensive-exits shape follows the ADR-0003 catch-up ruling.]

### 2c. The attention fix: violence is what makes the end-game expensive

The seed names the flaw: "not consuming enough attention, we are
under-pressured to spend enough each turn at this point." DIAL5-C already
ratified the SHAPE of the fix (era-scaling window demand and cost, endgame
demand ~5-6 windows at face ~4 = structurally uncoverable solo). What was
missing is the CONTENT that justifies the ramp. Violence is that content:

1. **Violence-class windows carry the top face costs** (DIAL5-C's spawn ~2 ->
   endgame ~4 curve gets its endgame examples here), several of them legally
   unignorable (already ruled: "some events legally unignorable" with default
   IGNORE penalties). A raid is not a newsletter.
2. **Chained demands.** Directed-violence events spawn follow-up windows
   (investigation, funeral, evacuation approval, retaliation decision) over
   subsequent ticks -- the 2037 vignette's "5 delegates to 10 meetings"
   arithmetic, made of event chains rather than a new meeting system.
   [INFERRED mechanism -- rides ADR-0012 response taxonomy.]
3. **Security upkeep is a standing attention demand.** Posture costs
   attention monthly (briefings, approvals -- typed to the Technical/Infra/
   Security demand category, DQ-24), absorbable by a security-chief hire the
   way ops staff absorb admin. The asymmetry that makes the fork bite: with
   NO posture, violence windows are dearer and nastier; with posture, you pay
   the standing tax instead. **Either way the violence era eats attention --
   the player only chooses the SHAPE of the bill** (spiky uninsured vs flat
   insured). That is the DIAL5-D insurance logic, promoted to the era level.
4. **Delegation pressure completes the office thesis.** Endgame demand
   exceeding founder supply is only coverable by the built office (managers
   absorb window classes, security chief absorbs the security category) --
   "we don't power up the player, we power up the office" expressed as the
   end-game's survival constraint, which DIAL5-C explicitly reached for.

### 2d. Failure-mode content: sourcing the terminal textures

Seed item 1: derive end-game content from the real failure-mode literature --
Yudkowsky's "AGI Ruin: A List of Lethalities", the AI-2027 / AI-2040 scenario
work. Guardrail (WORLD_AND_LORE, event-horizon rule, Pip verbatim): "we're
not saying or implying labs really do any of the truly weird stuff" -- author
the FEEL of the failure modes, never a claim that they are happening.

Mechanism -- a **failure-mode content pack**, pure data:

- **Epitaph families:** each death gets a terminal vignette keyed to the
  DOMINANT doom stream at death (the nine-stream decomposition gives the key
  for free; `death_attribution.gd` already knows the root). Lethality-list
  items and scenario beats become epitaph FAMILIES: overhang-root deaths draw
  from foom/sharp-turn textures; global_panic-root from panic-cascade and
  hypnodrone-register textures ("HypNOTised: 2.1B" is already the canon tone
  anchor); ledger-root deaths stay bureaucratic (the fraud collapse). This is
  "the game explains your death" delivered as worldbuilding.
- **Late Developments beats** (Section 2e) draw incident texture from the
  same pack -- sighting-grade fragments of failure modes in progress, in
  Papers-Please deadpan.
- **Sourcing discipline (the dosage guardrail, operationalized):**
  (a) paraphrase MECHANISMS of failure, never advocacy or attribution -- no
  named real actor ever appears post-horizon; (b) everything post-horizon is
  openly OUR timeline (seeds are timelines -- divergence is the premise);
  (c) the register stays flat CRT deadpan -- the moment a beat reads as an
  argument the player should believe, it is over-dosed; (d) dosage is a dial
  (events/month at terminal bands), swept like any other number; (e) the
  spooky-removals boundary holds under violence: abduction, black-bag,
  mind-hacked, wireheaded -- **nobody grossly murdered on screen** (the ruled
  personnel boundary, now the whole violence register's boundary). [The
  (a)-(d) discipline is INFERRED operationalization of the ruled guardrail;
  (e) extends an existing ruling and needs Pip's explicit yes.]
- **Reality-tether hygiene:** failure-mode content is FICTION-side (post
  horizon) and must not ride the ADR-0016 world-update packs (reality-side,
  pre-horizon). Two content lanes, never mixed in one file. [INFERRED]

### 2e. The reputation-loss escalation curve (a Developments beat ladder)

Seed item 4: early rep loss = "you get beaten up at a party"; late rep loss =
"helmeted government agents crash in through your conference room windows and
black bag you into a helicopter." Same mechanical event (reputation down,
maybe a ledger rider), escalating FICTION.

Mechanism: an `escalation_rung` tag on Developments beats (the
SEED_RIVAL_AND_DEVELOPMENTS narrative-pressure engine -- this proposal
supplies its late rungs). The pool draws rep-loss dressing by the current
rung, which is a function of era x fear band x your visibility:

| Rung | Era / trigger state | Rep-loss register | Example beats |
|---|---|---|---|
| 0 | startup, pre-fear | comedic, personal | beaten up at a party; roasted in a comment thread |
| 1 | office era | professional | scathing review; grant pulled; litigation threat |
| 2 | midgame, DQ-22 aggro | adversarial | psyops, poach raids, leak-seeking (the ruled rival attack list) |
| 3 | fear band, low visibility | ambient dread | violence in the feed, aimed at others; your board asks about YOUR security |
| 4 | fear band, high visibility | state-level, spooky | the raid; the black-bag helicopter; researchers mind-hacked by cultists (2037 vignette) |

Plus one AUTHORED beat per run: **the Knock** -- the first directed-violence
event, staged as a legible, remembered arrival (the inverse of the Step Up
beat: Step Up flips startup->office; the Knock announces you have entered the
part of the game the office era was building toward). Beats after the Knock
are pool-drawn; the Knock itself is scripted staging on a systemic trigger --
author causes, never outcomes. [INFERRED -- the one-authored-beat pattern is
new and needs Pip's taste check; everything else rides the beat-tag design
the rival seed already sketches.]

---

## 3. MINIMAL / MODERATE / AMBITIOUS ladder

All three tiers change legal action space or event economy -> all fork the
ladder -> epoch-only, never a patch. Sequencing reality: rungs 0-2 of the
escalation ladder belong to DQ-22 (the v0.13 rivals workshop); this
proposal's tiers are deliberately buildable WITHOUT the rival ladder existing
first, but they get better with it.

### MINIMAL -- the fear band + the bill shape (days-scale) [INFERRED sizing]

- Derive a `fear_band` read-only from existing streams (no new state); key
  `window_demand_budget` to it and DELETE `endgame_turn` (one constant dies,
  one function changes: `month_controller.gd:51-56`).
- One violence-class event genre (~8-12 events, data-only) gated on the
  band: high face cost, some unignorable, rungs 3-4 dressing only.
- One `security_posture` int, bought via 2-3 plan-speed actions on existing
  action + ledger machinery (build duration = the lead-time mechanic; the
  panic-buy variant exists from day one, priced dirty, minting a liability).
  Posture discounts violence-window face costs. No upkeep yet.
- Solver policies {never, hedge_early, dive_at_onset}; gate: dive is
  median-negative.
- What it proves: does a world-state endgame trigger + expensive windows fix
  the under-pressured late game? What it lacks: no ratchet, no targeting
  axis, no epitaphs, no upkeep -- violence is weather, not yet a spiral.

### MODERATE -- the real proposal (the recommended target; ~1-2 weeks) [INFERRED]

Everything in MINIMAL, plus:
- **Two-axis trigger:** visibility-keyed targeting (directed vs ambient
  violence); the Knock as the authored first-directed beat.
- **Escalation ratchet:** violent events increment `escalation`; standing
  feedback into fear-band inputs; sacred-object-grade de-escalation only;
  telemetry flag on any un-caused de-escalation (doom-floor pattern).
- **Military fork, full pricing:** hedge vs dive as the same posture bought
  at different speeds/prices; upkeep as a typed standing attention demand
  absorbable by a security-chief hire; adoption-credibility corrosion above
  a posture threshold (the thesis cap); staff departure riders.
- **Failure-mode pack v1:** epitaph families keyed to dominant death stream;
  rung-tagged late Developments beats; dosage dial.
- **Solver gates, full set:** Section 4's sweep hooks.

### AMBITIOUS -- the confrontation layer (next-epoch-plus, post-DQ-22)

- Direct late-game conflict mechanics vs the rival ("we confront them more
  directly in the late game" -- the rival seed's act 3), on the DQ-22 agent
  model once it exists.
- Delegates-and-meetings scarcity as a real allocation system (5 delegates,
  10 meetings); evacuation/relocation decisions (Berlin -> Mongolia bunker);
  defensive drone-swarm RENTS (recurring ledger liabilities, not purchases).
- State actors as counterparties (treaty votes, the whip register at
  world scale) -- ADR-0007 machinery at the top of the escalation ladder.
- Dependencies: DQ-22 rival agent model, ADR-0011 L2 delegation substrate,
  ADR-0010 adoption v1 (the thesis cap needs adoption to exist to corrode).
  Do NOT gate MODERATE on any of this.

Fork note: MINIMAL -> MODERATE is additive (fear band, posture int, and event
schema are strict subsets). AMBITIOUS is a different layer riding the DQ-22
workshop's output; treat as its own proposal when that workshop lands.

---

## 4. The dials (tune in data, rule the SHAPE at WS-3)

All live in balance data. Anchors are sweep starting points, not proposals to
ship [INFERRED throughout]:

| Dial | Anchor | The constraint that sets it |
|---|---|---|
| `violence.fear_band_arm` | doom-band ~60-70 equivalent on the composite | Must arrive AFTER the DQ-22 midgame has had time to be felt (violence is the escalation of an existing fight, not the first fight). If most runs die before the band, it does not exist -- check against the ~15-month median. |
| `violence.targeting_visibility` | top ~third of the rep/visibility range | Low-vis labs must genuinely spectate the era (ambient-only) -- hiding must be a real, costed strategy, or visibility is fake. |
| `violence.window_face_cost` | 3-4 Attention | DIAL5-C's endgame cost anchor, worn by its content. Never below ordinary windows. |
| `window_demand_budget` by band | 3 pre-band -> 5-6 in-band -> +1-2 at high escalation | Replaces `endgame_turn`; endpoint per DIAL5-C: uncoverable solo, coverable by a built office. |
| `security.build_months` | 2-4 months (hedge path) | THE lead-time dial: long enough that onset-diving cannot replicate it, short enough that a mid-game read of the world can still act on it. |
| `security.panic_multiplier` | 3-5x hedge price, instant, + liability | The dive premium. Solver must show dive median-negative at this price; if dive ever goes median-positive, raise this first. |
| `security.upkeep_attention` | 1-2/month per posture tier, absorbable | The standing-tax shape of the bill; security chief absorbs like ops absorbs admin (DQ-24 typing). |
| `security.window_discount` | ~30-50% face + damage downgrade on directed events | The hedge's tail payoff. Big enough to be decisive in violent seeds; must never make violence windows CHEAPER than pre-band windows (posture mutes the era, never deletes it). |
| `security.adoption_corrosion_threshold` | above tier ~2 of ~4 | The thesis cap: past it, adoption credit multiplier < 1 and the apex is unreachable. Low tiers stay clean so the hedge is not automatically apex-forfeiting. |
| `escalation.increment / decay` | +1 per directed event; decay 0 by default | The ratchet. Any nonzero decay is sacred-object priced. Telemetry-flag un-caused declines (doom-floor pattern). |
| `failure_mode.dosage` | ~1-2 texture beats/month at terminal bands | The persuasion-piece guardrail: below the "reads as an argument" line; swept for tone by hand, not by bot. |
| `the_knock.min_lead` | >= 1 month of rung-3 ambient beats first | The Knock must be foreshadowed, never the first signal -- tragedy requires lead time, applied to staging. |

Sweep hooks: policy axes = {never_military, hedge_early, hedge_late,
dive_at_onset, dive_always}; gates: (1) dive_at_onset and dive_always
median-negative with death-cause conversion (the DESPERATION_SOLVER
fingerprint reproduced -- if absent, the trap is mispriced); (2) hedge_early
median mildly negative but max/tail POSITIVE in high-violence seeds (the
"occasionally, expensively, isn't" shape -- if hedge is median-positive,
military is a tax not a bet; if its tail never pays, the seed's "outgunned
unless" is a lie); (3) no policy sustains doom decline via military anything
(it must never touch doom downward); (4) floor target: the fear band never
fires under month ~10 on standard policies [INFERRED anchor].

---

## 5. Coupling contract (what this reads/writes)

- **ADR-0002 (survival spine):** violence extends the spine's late slope --
  more survivable months for the prepared, none of it a win. The thesis cap
  writes the apex-victory reachability rule (posture forecloses doom-0).
  Graceful concession gets its natural moment: the post-Knock state is where
  "resign -> lock score" earns its keep. [INFERRED tie]
- **ADR-0003 (ledger) + DESPERATION_SOLVER:** the dive is a new member of the
  proven desperation family (visible help, compounding bill, death-cause
  conversion); panic-buys and dirty capabilities mint ledger entries, some
  secret with exposure fuses. The solver harness is the acceptance test.
- **ADR-0015 (streams):** fear band reads streams; escalation writes stream
  inputs via `add_stream_input()`; NO printed doom anywhere in violence
  content (the data-strip discipline from birth -- WS3_FINISH_OR_DROP S5).
- **DIAL5 B+C+D (ratified):** violence content IS the era-scaling story:
  face costs at C's endgame anchor, upkeep as B-style typed demand with
  staff buyback, posture as D's insurance logic at era scale.
- **DQ-22 (rivals aggro, v0.13 workshop):** rungs 0-2 belong to it; this
  proposal owns rungs 3-4 and hands the DQ-22 workshop a fixed boundary:
  rivals attack your INTERESTS; the violence era attacks your EXISTENCE.
  Rival aggression (`rivals.gd:27`) stays the midgame key; fear band is the
  endgame key.
- **Developments engine (SEED_RIVAL_AND_DEVELOPMENTS):** rung tags extend the
  beat-archetype design; the Knock joins Step Up as the second authored
  era-seam beat. One engine, two seams.
- **DQ-24 / ADR-0011:** security is a demand TYPE in the existing taxonomy
  (Technical/Infra/Security), absorbed by a matching hire -- no new currency,
  no new panel (restraint rule holds).
- **WORLD_AND_LORE:** event-horizon guardrail governs all failure-mode
  content; spooky-removals boundary governs the violence register; the 2037
  vignette is MODERATE's feel target and AMBITIOUS's content list.
- **Scoring/ladder:** no scoring change; forks the ladder because event
  economy and action space change (epoch-only, release-train rules).

---

## 6. Crisp questions WS-3 must decide

1. **THE fork (decide this first):** ratify "dive = trap, hedge = negative-EV
   insurance with a real tail, lead time is the selector"? Or does Pip want
   a true Reading-B military branch (survival-legitimate at any timing)?
   Everything in Sections 3-4 reshapes if B.
2. **The thesis cap:** does military posture above a threshold foreclose the
   doom-0 apex victory (a militarized safety lab can outlive the world but
   not save it)? This is the moral-status call the seed flagged; it is one
   line of design and a worldview.
3. **Trigger shape:** two-axis (world fear arms globally, visibility aims at
   you) vs single-key (doom band alone, or rival-aggro alone)? And ratify
   the DQ-22 boundary: rivals own rungs 0-2 / interests; violence era owns
   rungs 3-4 / existence -- so the v0.13 workshop inherits a clean seam.
4. **Ratchet semantics:** zero-decay escalation with sacred-object-only
   de-escalation, or slow ambient decay? (Zero-decay is the "incredibly hard
   to recover" reading; any decay softens the point-of-no-return claim.)
5. **The bill's shape:** confirm the either-way-you-pay attention design
   (uninsured = spiky expensive windows; insured = standing upkeep tax) --
   this is what makes the late game "consume enough attention" in BOTH
   builds. If Pip wants a low-attention stealth endgame to exist, say so
   now; it changes the targeting dial's meaning.
6. **Violence register boundary:** confirm spooky-removals extends to state
   violence -- black-bag yes, on-screen gore never -- and confirm the Knock
   as an authored beat (one scripted staging on a systemic trigger).
7. **Failure-mode dosage + lane hygiene:** ratify the sourcing discipline
   (mechanism-paraphrase only, post-horizon only, fiction lane never mixed
   into ADR-0016 reality packs) and the ~1-2 beats/month dosage anchor.
8. **Which epoch:** MINIMAL is buildable now (it deletes `endgame_turn` and
   ships one genre + one stock); MODERATE wants the DQ-22 workshop output
   nearby. Recommendation [INFERRED]: MINIMAL in the epoch after WS-3's
   primary lanes; MODERATE lands with or just after the v0.13 rivals epoch
   so both ends of the escalation ladder arrive within a league or two.

---

## 7. Out of scope (named so they stay out)

- **Compute vs non-compute research streams** (seed item 2) -- a WS-3 Theme C
  / ADR-0011 substrate axis, not a violence topic. Needs its own half-page.
- **Tech-tree robustness / fluid influence** (seed item 3) -- a design
  CONSTRAINT on future progression work (prefer fluid influence over rigid
  prereqs), logged; no tree is proposed here or should be.
- **A combat system.** No hit points, no tactical layer, no unit combat --
  violence arrives as events, windows, ledger entries, and epitaphs. If an
  implementation needs a battle resolver, it has left the design.
- **Rival agent modelling** (one silhouette vs procedural force) -- the DQ-22
  / WS-4 workshop's question; this proposal only consumes its output.
- **Player-initiated violence.** The player can arm, harden, and retaliate
  within event choices; an "attack rival" action lane is deliberately absent
  until the confrontation layer (AMBITIOUS) is designed against the DQ-22
  agent model. [INFERRED boundary -- and a deliberate thesis statement.]
- **Present-day-actor implications.** Nothing in the violence era claims or
  implies real labs or governments do these things (event-horizon rule);
  pre-horizon historical military-AI texture (Project Maven et al.) stays
  factual and stays pre-horizon.

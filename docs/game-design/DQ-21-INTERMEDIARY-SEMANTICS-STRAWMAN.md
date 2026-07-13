# DQ-21 — Intermediary semantics v1 (STRAWMAN, for Pip veto)

> **Status: STRAWMAN, ROUND 3. Fable Lane 0, workshop #3 build wave.**
> Pip's veto round 1 applied (2026-07-13): §2 is rebuilt as a **ROUND-2 STRAWMAN**
> (named component streams + typed dampers; the MIN_FLOOR clamp and the global
> governance-damping multiplier are **deleted**), §2b (sacred-object chains — two senses)
> is **new**, and rulings are marked in the veto checklist (✅ ruled · 🟡 provisional ·
> ⬜ open). Round 3 (same day): Q-CONFLICT-1 confirmed; two-instrument display ruling
> added to §2. Everything not marked ✅ remains vetoable.
> This document proposes clean names + semantics for the eight doom intermediaries Pip
> seeded (WORKSHOP_2_BACKLOG DQ-21, 2026-07-13), and a v1 doom-function *shape*. It exists
> to be vetoed line-by-line. Every judgment call is collected in **Questions for Pip** at
> the end — read that first if you only have five minutes.
>
> **Constraint honoured (ADR-0015 §2):** adding an intermediary is an ADR-grade act. This
> strawman invents **no** new intermediaries beyond Pip's eight. Merges/splits are offered
> **only** as veto questions, never taken unilaterally.

## What Pip actually said (verbatim anchor)

DQ-21 backlog entry, Pip's list, verbatim:

> `general_capability` (diffusion + mass adoption), `frontier_capability` (plus per-actor
> variants), `global_compute`, `global_dedicated_AI_compute` (smaller, scarcer, more
> valuable, likely controlled early), `something_for_attitudes_of_political_pressures`
> (naming owed), `ambient_capability_-_risk_background_levels`, `global_alarm`,
> `global_panic`.

And on form:

> Form: **rate, accumulating** (~75% ruling) — experienced as a rate while history ticks
> the level up; 2017 spawn starts lower, builds slower than current balance. Doom **can**
> go down, but only at the end of long effort chains, priced in sacred objects.

Pip's own note: the *names* are bad but the **pairs** carry the intent; the distinctions
(alarm vs panic, compute vs dedicated-compute) are load-bearing. This strawman treats the
distinctions as the thing to preserve and the strings as freely-renamable.

---

## 1. The eight intermediaries

Naming convention proposed: clean `snake_case`, no leading `global_` unless the scope
distinction is load-bearing (alarm/panic keep it because per-actor alarm is a different,
un-seeded thing). Pip's verbatim string is retained in each heading so grep can find it.

### 1.1 `general_capability`  *(verbatim: `general_capability`)*

- **Definition.** The diffused, commoditized floor of AI capability — what any actor
  (including a bad one) can already do off open weights, APIs, published methods, mass
  adoption. Trails the frontier by a diffusion lag. This is the "who can do harm at all"
  level; it is a ratchet (diffusion rarely un-happens).
- **Raises:** time / the schedule (open-source releases, API commoditization — ADR-0016
  league pipeline feeds the real diffusion timeline); adoption of *capability* work
  (ADR-0010 routing — an adopted capability paper is diffusion); rival deployment.
- **Lowers:** almost never in practice (ratchet). A deliberate un-diffusion (recall,
  moratorium that sticks) is a *sacred-object chain* outcome, not a routine lever.
- **Enters doom via:** the `diffusion` term — raises the hazard *floor*; more actors,
  more surface. Slow, broad, hard to reverse.
- **Read/written by:** schedule causes (ADR-0005/0016) write it; ADR-0010 adoption
  routing writes it when the adopted work is capability-flavored; doom function reads it.

### 1.2 `frontier_capability`  *(verbatim: `frontier_capability` + per-actor variants)*

- **Definition.** The leading edge — what the single most-advanced actor can do, ahead of
  diffusion. Modelled as a **map `actor -> level`** (`frontier_capability[player]`,
  `frontier_capability[rival_A]`, …); the seeded "per-actor variants" are **indices into
  one intermediary, not eight new intermediaries** (ADR-0015 restraint). The scalar the
  doom function reads is `max` over actors (or top-k); the gap `frontier − general` is the
  *overhang*.
- **Raises:** research workstreams on the capability lane (ADR-0011 §7 dual-use); rival
  trajectories (ADR-0005 waves); gated by `dedicated_ai_compute` (you cannot push frontier
  past your compute).
- **Lowers:** frontier does not fall; a *relative* fall happens when others advance past a
  frozen actor (attrition, defunding — a rival event, DQ-22).
- **Enters doom via:** the `overhang` term — frontier capability *not matched by* safety
  absorption / governance is the **acute** hazard (as opposed to general_capability's
  chronic floor). Also feeds `general_capability` on a lag (today's frontier is tomorrow's
  diffusion).
- **Read/written by:** ADR-0011 workstreams + ADR-0005 rival waves write it; **DQ-22
  aggro-threshold reads it** — the *visibility* of the player's `frontier_capability[player]`
  is a prime trigger for rivals turning hostile ("the world starts shooting back"); doom
  function reads `max`/overhang.

### 1.3 `global_compute`  *(verbatim: `global_compute`)*

- **Definition.** Total worldwide compute — the whole ocean, most of it doing payroll and
  cat videos. The slow macro substrate (fab output, datacenter buildout). Rises roughly
  monotonically with the real timeline.
- **Raises:** schedule/league only (ADR-0016 — this is macro-map furniture, largely
  outside player influence, matching "environmental forces the player can't influence").
- **Lowers:** effectively never at game grain (a fab war / supply shock is a rare
  scheduled event).
- **Enters doom via:** **indirectly, through `dedicated_ai_compute`** — see 1.4. The
  strawman position is that `global_compute` does **not** have its own doom term; it is a
  *derivation input* that sets the ceiling and the diffusion pace.
- **Read/written by:** schedule writes; `dedicated_ai_compute` derivation reads;
  `general_capability` diffusion pace reads.
- **✅ RULED (round 2, Pip):** stack-level crispness holds — **no standing player lever
  governs `global_compute`** — but content MAY touch it: edge-case events (e.g. autocratic
  crackdowns on PC-grade compute) are legal at the cards level per ADR-0005. Pip: *"I
  might be able to solve this at the cards-level, not the stack-level, to use a M:TG
  analogy."*

### 1.4 `dedicated_ai_compute`  *(verbatim: `global_dedicated_AI_compute`)*

- **Definition.** The scarce, organized subset of `global_compute` actually assembled for
  large training runs — the navigable *fleet* inside the ocean. Pip's gloss: "smaller,
  scarcer, more valuable, likely controlled early." This is the **chokepoint** — the pool
  small enough that governance, export controls, and alliances can actually grip it, unlike
  the ocean of `global_compute`.
- **Raises:** buildout / investment (schedule); player or rival compute acquisition
  (dual-use lane pays in compute — ADR-0011 §7); alliances that pool it (ADR-0007).
- **Lowers:** compute governance — export controls, treaty caps, chokepoint action
  (ADR-0007 counterparties + political_pressure); this is one of the few *player-reachable*
  levers on the capability side.
- **Enters doom via:** the `compute_pressure` term and by **gating `frontier_capability`**.
  Because it is controllable, it is the seam where governance work converts into a real
  frontier slowdown — i.e. where alarm→governance→compute-cap becomes a doom-rate dampener.
- **Read/written by:** schedule + ADR-0011 acquisition write; ADR-0007 alliance/governance
  actions write (the cap); `frontier_capability` derivation reads it as a ceiling; doom
  function reads it.

**The compute pair, stated once:** `global_compute` is the slow, uncontrollable ocean that
sets the ceiling and the diffusion clock; `dedicated_ai_compute` is the small controllable
fleet that actually fuels the frontier and is the only compute a governance play can grip.
Design payload: **compute governance targets the dedicated pool** — you can't regulate the
ocean, you can regulate the clusters.

### 1.5 `political_pressure`  *(verbatim: `something_for_attitudes_of_political_pressures`)*

- **Definition.** The **directional** disposition of the political/regulatory environment
  toward AI — a *signed* axis, not a magnitude. Positive = pressure toward competent
  governance (funding safety, caps, coordination); negative = pressure toward acceleration
  (national-champion racing, deregulation, "we must beat them"). "Attitudes of political
  pressures" = the world's current lean and how hard it is pushing.
- **Raises (toward governance):** adopted safety work (ADR-0010); `global_alarm` (see 1.7);
  governance-lane workstreams (ADR-0011 archetype #2, "your best door to government
  adoption"); the player's lobbying chains (ADR-0003 — the "job as a lobbyist" ledger arc).
- **Lowers (toward acceleration):** `global_panic` (see 1.8); rival lobbying; racing
  incentives; the player's own dual-use success being read as proof racing pays.
- **Enters doom via:** *(round 2 — the single global damping term is retired, see §2)*
  positive `political_pressure` gates the availability and strength of **typed dampers**
  on specific streams (e.g. a compute-cap damper on the compute stream, a regulation
  damper on a release pulse); negative `political_pressure` weakens/blocks dampers and
  feeds the panic/racing side. Strawman wiring — see R2-Q2.
- **Read/written by:** ADR-0010 adoption, ADR-0011 governance archetype, ADR-0003 lobbying
  chains, alarm/panic all write; doom function reads.
- **⚠ CONFLICT — ✅ CONFIRMED (Pip, round 3):** **two distinct objects.**
  `political_pressure` = world-state intermediary (the world's disposition). The existing
  `game_state.gd governance: float = 50.0` stays a **player-currency stub** whose DQ-7
  design will define it as a **lever that writes into** the world intermediary. Vintage
  placeholder, cheap to rename.

### 1.6 `ambient_risk`  *(verbatim: `ambient_capability_-_risk_background_levels`)*

- **Definition.** The background hazard level the player cannot meaningfully influence — the
  integrated environmental forces that make "the background of Doom nearly always trending
  up" (DESIGN_PHILOSOPHY, 2026-07-13). This is the **base of the always-climbing rate**, and
  the primary carrier of the "2017 starts lower, builds slower" behavior: `ambient_risk` is
  low at spawn and climbs as the real race enters the seed timeline.
- **Raises:** the schedule/league almost exclusively (ADR-0016 reality-tether — this is the
  "~75% canon, baked deep into config" number Pip described). Year-keyed.
- **Lowers:** not by routine play. A structural, worldwide de-risking is the archetypal
  *sacred-object* endgame outcome — long chain, priced in sacred objects.
- **Enters doom via:** the **baseline stream** (§2) — the slow, year-keyed trend under
  everything else. *(Round 2: no longer a hard `MIN_FLOOR` clamp — "the background nearly
  always climbs" is now a property of the baseline's schedule plus the Q-FN-1 telemetry
  invariant, not an engine `max()`.)* This is the intermediary that most directly *is*
  "doom is a rate."
- **Read/written by:** schedule/league config writes (ADR-0016); doom function reads as its
  base term.
- **Note on the dash in the name:** the verbatim `ambient_capability_-_risk_background_levels`
  reads as *"capability-risk background levels."* Strawman treats it as **one** scalar
  (background hazard). Whether it should **split** into `ambient_capability` vs
  `ambient_risk` is an ADR-grade decision → veto Q-SPLIT-1 (not taken here).

### 1.7 `global_alarm`  *(verbatim: `global_alarm`)*

- **Definition (strawman semantics — the load-bearing half of the pair).** **Productive
  concern.** Alarm is society/governance taking the problem seriously in a *coordinated,
  competent* way: it funds safety, enables caps, slows reckless racing, makes safety work
  adoptable. Alarm is the "good" awareness — concern that converts into governance.
- **Raises:** legible safety work being *adopted* (ADR-0010); credible warnings that land
  correctly; incidents *interpreted competently*; high-fidelity SA/media channels
  (ADR-0014) carrying real signal.
- **Lowers:** time/habituation (alarm decays if not fed); an incident mishandled converts
  alarm→panic rather than raising alarm; cynicism.
- **Enters doom via:** *(round 2 — global damping retired, see §2)* alarm is the input
  that lets `political_pressure` go positive and stick, and thereby **gates typed
  dampers**: alarm + positive political_pressure is what makes governance-grade dampers
  (compute caps, regulation on release pulses, safety adoption) purchasable and effective.
  **Alarm never touches doom directly** (it is not "−doom"); it enables the governance
  that dampens specific streams. This keeps ADR-0015's indirection honest.
- **Read/written by:** ADR-0010 adoption + ADR-0004/0014 SA channels + ADR-0005 incident
  causes write; `political_pressure` and doom function read.

### 1.8 `global_panic`  *(verbatim: `global_panic`)*

- **Definition (strawman semantics — the other half).** **Counterproductive flailing.**
  Panic is fear *without* competent coordination: it fuels bad regulation (either
  restrictive theater that drives work underground / offshore, or reactive nationalist
  racing — "we must beat them"), erodes careful work, spikes short-term reputational chaos,
  and *accelerates* the race it is afraid of. Panic is the "bad" awareness — the same fear
  energy as alarm, pointed the wrong way.
- **Raises:** incidents interpreted *badly* / sensationalized (low-fidelity media,
  ADR-0014); rival psyops and reputational attacks (DQ-22, "the world starts shooting
  back"); the player's own reckless *high-visibility* capability moves; a mishandled crisis.
- **Lowers:** time/habituation; competent public communication (a founder-hour spend);
  converting the moment into alarm by handling it well.
- **Enters doom via:** the **panic stream** (additive, §2) — panic *raises* `doom_rate`
  (bad regulation + racing) and pushes `political_pressure` negative. It is the social-side
  accelerant.
- **Read/written by:** ADR-0005 incident causes + ADR-0014 low-fidelity channels + DQ-22
  rival attacks write; `political_pressure` and doom function read.

**Alarm vs panic, stated once (the pair Pip flagged as load-bearing):** same fear, opposite
sign of usefulness. **Alarm = concern that coordinates → governance → slows the climb.
Panic = fear that flails → bad regulation + racing → speeds the climb.** Which one an
awareness event becomes depends on the *epistemic quality of the surrounding environment
and how the player handles it* — a well-run org converts scare-events into alarm; a
flailing one (or a rival's psyop) converts them into panic. They are **not** two ends of
one variable: a society can be simultaneously highly alarmed *and* highly panicked (the
realistic case), so they are two variables, not a signed one (→ veto Q-MERGE-1).

---

## 2. The doom function (ROUND-2 STRAWMAN — streams + typed dampers)

> **Round-1 shape retired by Pip's veto:** the `MIN_FLOOR` engine clamp (Q-FN-1,
> **rejected** — replaced by an instrumentation invariant) and the single bounded
> multiplicative governance-damping term (**ruled too restrictive** — replaced by typed
> dampers on named streams). The never-reverses clamp is **deleted**; net-negative rate
> turns are legal. Pip: downward spikes are legal *"if a player pulls something
> impressive off."* **The floor is an instrument, not a clamp.**

Design principle (round 2): **complexity lives in superposition; legibility lives in
components.** `doom_rate` is a plain **sum of named streams**; each stream is individually
attributable via the L6 chip system, and the "wiggly stock-market like lines" Pip wants
are the *emergent interference pattern of legible streams* — never noise injected anywhere.

Design rules this shape must satisfy (ADR-0015 + DESIGN_PHILOSOPHY 2026-07-13, as amended
by veto round 1):

1. **Doom is a rate that accumulates.** The player experiences `doom_rate`; history ticks
   `doom_level` up (or, on net-negative turns, down) by integrating it. Death when
   `doom_level` crosses a threshold; the **badge is the date** (ADR-0009 / WORLD_AND_LORE).
2. **The background nearly always climbs — statistically, not by clamp.** The baseline
   stream's year-keyed schedule does the climbing; the engine never forces the sum positive.
3. **Q-FN-1 invariant (the floor as instrument):** doom rate MAY go negative; the engine
   **strongly logs/flags (debug + telemetry) any turn where `doom_rate ≤ 0` AND no
   sacred-object-grade cause fired that turn.** A quiet negative turn is a balance bug or
   an exploit specimen, not a crash — the sweep and telemetry police it.
4. **No printed doom.** No action/event writes doom; they write intermediaries, inject
   scheduled pulses, or grant typed dampers. Doom is computed each day tick (ADR-0015 §1).
5. **Attributable.** Every stream is named → the L6 chain (EE-8) can say what is killing
   (or saving) you, per component, per tick (ADR-0015 §3, ADR-0004 legibility).

Pseudocode (illustrative — not GDScript; magnitudes are `Balance` config, not here):

```
# ── Per day tick. doom_rate = sum of NAMED streams. ──

func compute_doom_rate(s, t) -> (float, Dict):
    streams = {}

    # (a) baseline — ambient_risk, year-keyed schedule (§1.6). The slow trend under
    #     everything; 2017: low and slow — the steady build IS the early grind.
    streams["baseline"] = s.ambient_risk

    # (b) overhang — acute frontier hazard (§1.2)
    streams["overhang"] = W_FRONTIER * max(0.0, s.frontier_capability_max - safety_absorption(s))

    # (c) diffusion — chronic floor from general_capability (§1.1)      [R2-Q1: own stream?]
    streams["diffusion"] = W_GENERAL * s.general_capability

    # (d) compute — dedicated_ai_compute fuel term (§1.4)               [R2-Q1: own stream?]
    streams["compute"] = W_COMPUTE * compute_pressure(s.dedicated_ai_compute)

    # (e) panic — additive social accelerant (§1.8)
    streams["panic"] = W_PANIC * s.global_panic

    # (f) SCHEDULED PULSES — ADR-0005 schedule entries inject time-shaped rate bumps:
    #     anticipation ramp → spike → decay tail. Pip: "we can predict an increase in
    #     Doom around the time these 3 new models are going to be released."
    for pulse in s.schedule.active_pulses(t):
        streams["pulse:" + pulse.id] = pulse.envelope(t)     # ramp/spike/tail shape

    # (g) CYCLIC CONTENT STREAMS — recurring content-defined waves (hype cycles,
    #     funding seasons, election years) — periodic pulses on the same machinery.
    for cyc in s.content.cyclic_streams(t):
        streams["cycle:" + cyc.id] = cyc.value(t)

    # ── TYPED DAMPERS ── player mitigations attach to SPECIFIC streams, with durations.
    # damper = (target_stream, strength(t), expires_at). Granted by completed workstreams,
    # adopted safety work, governance wins (gated by alarm/political_pressure, §1.5/§1.7).
    # NO global multiplier. NO never-reverses clamp.
    for d in s.active_dampers(t):
        streams[d.target] -= d.strength(t)          # may push a component negative [R2-Q9]

    rate = sum(streams.values())                     # superposition — MAY be negative

    # Q-FN-1 replacement: the floor is an INSTRUMENT, not a clamp.
    if rate <= 0.0 and not s.sacred_grade_cause_fired(t):
        telemetry.flag("negative_rate_without_sacred_cause", t, streams)   # loud: debug + telemetry
    return rate, streams                              # streams dict feeds the L6 chips


func day_tick(s, t):
    s.doom_rate, s.doom_streams = compute_doom_rate(s, t)
    s.doom_level += s.doom_rate * DAY_DT     # may FALL on net-negative turns — legal

    # Discrete level reductions: sacred-object chains (§2b) — gauntlet payouts and/or
    # sacrifice payments post one-off negatives to doom_level, on top of the rate.
    for chain in s.completed_sacred_chains(t):
        s.doom_level -= chain.reduction
        if chain.has_sacrifice: ledger.burn(chain.sacrifice)   # §2b(b)/(c)

    if s.doom_level >= DOOM_DEATH_THRESHOLD:
        end_run(date = t)                     # the badge is the date
```

Why this shape (mechanism, not decoration):

- **Superposition produces the texture.** Baseline trend + pulse envelopes + cyclic waves
  + damper expiries interfere into exactly the "wiggly stock-market like lines" Pip asked
  for — and every wiggle decomposes into named components on inspection (L6 chips can show
  the stack per tick). Complexity in the sum, legibility in the parts.
- **Scheduled pulses make the reality-tether mechanical** (ADR-0016): a league update that
  says "three frontier models release in March" is literally three pulse entries with
  anticipation ramps — the market *pricing in* a release before it happens, then the spike,
  then the decay tail as the world absorbs it.
- **Typed dampers replace the global multiplier.** A mitigation is now a *targeted, timed*
  purchase: a compute-cap treaty damps the compute stream for its duration; a competent
  public-comms play damps panic; pre-emptive policy work might damp an upcoming release
  pulse (R2-Q3). This kills the round-1 problem (one scalar hid *what* governance was
  actually gripping) and buys per-stream attribution for free.
- **Negative turns are earned, visible, and policed.** Stacking enough dampers or landing
  a chain payout can push the sum below zero — legal, feels earned ("pulls something
  impressive off"), and any negative turn *without* a sacred-grade cause trips the
  telemetry flag, so the sweep catches damper-stacking exploits instead of a clamp hiding
  them.
- Every stream names an intermediary or a schedule entry → L6 attributes a death to
  "frontier overhang" vs "panic-driven racing" vs "the March release pulse," satisfying
  ADR-0015 §3.

### Display implications — two instruments (✅ RULED, Pip 2026-07-13)

Pip, verbatim: *"we can have the satisfaction of watching something like the delta Doom
rise and fall in response to our observed outputs, and then the actual, accumulated Doom
can steadily grind upwards with much subtler gradients over time, so the player has (or,
better yet, can earn) tighter feedback loops."*

- **(a) The delta-doom (rate) display** — visibly rises and falls in response to player
  outputs. The **high-frequency feedback surface**, decomposable into the named streams
  via the L6 chip system (click the wiggle, see the stack).
- **(b) The accumulated doom level** — grinding upward with much subtler gradients. The
  **structural-dread surface**; the thing whose crossing date is the badge.
- **The tighter feedback loop is EARNED.** Instrument *resolution* — stream decomposition,
  pulse forecasting ("a release spike is coming in March") — is progression content, built
  and unlocked in the power-up-the-office register (DESIGN_PHILOSOPHY "On the hero and the
  office"): better instruments are things the org constructs, not settings.
- **The free layer is owned by ADR-0004's lead-time rule and is never paywalled:** the
  coarse doom band and becoming-lethal warnings stay free — the world may always shout
  about what is becoming lethal; what you *buy* is resolution and lead time, never the
  existence of the warning.

**What is NOT specified here (correctly):** all magnitudes (`W_*`, `DOOM_DEATH_THRESHOLD`,
the `ambient_risk` year curve, pulse envelope parameters, damper strengths/durations,
chain reduction sizes). Those are the freely-tuned `Balance` layer (ADR-0015 §4: "the
function is structure; pricing is numbers"). This document is the structure; the
exploit-finder + playtests price it.

## 2b. Sacred-object chains — two senses (ROUND-2 STRAWMAN)

> Term attribution: "sacred objects" is Pip's own 2026-07-13 wording — *"trading off
> increasingly sacred objects / values / projects"* (DESIGN_PHILOSOPHY, doom-as-rate
> entry). Round 1 conflated two distinct mechanisms under the phrase; Pip's veto round
> split them.

**(a) Gauntlet chains** — multi-stage-gated pipelines, **each gate failable**. Pip's
ur-example: *impactful paper → shown at conference → wins award → gains political traction
→ applied to policy.* This is ADR-0010's research→adoption pipeline run to its endgame,
and the machinery already exists: ADR-0011 workstreams (the stages), ADR-0009 durations
(each stage takes months), ADR-0014 conference gates (attendance is literally a gate).
Doom reduction is the **completed-chain payout**; nothing is sacrificed — **the difficulty
IS the gauntlet** (many failable gates × long durations × opportunity cost).

**(b) Sacrifice payments** — burning an accumulated, **hard-to-replace stock**. Pip's
example: cashing a strong equity position in a frontier lab. Also in the class: flagship
projects (killing the thing the org is known for), veteran hires (attachment-is-built-
to-be-spent, DESIGN_PHILOSOPHY "On the hero and the office"), mission purity (the
crusader walks, §DQ-15 archetype 3). The price is a ledger burn (ADR-0003), and the pain
scales with how long you fed the stock.

**(c) Composition candidate:** the strongest reductions require **both** — chain
completion is *eligibility*, the sacrifice is *payment*. You ran the gauntlet to the
policy table; now what are you willing to give up to get it signed?

**(d) The dual-use loop closes.** Capabilities equity accepted early (billed doom per
ADR-0011 §7 — the priced temptation) can be **burned late for doom reduction** — the
deepest ledger arc in the game gets an endgame redemption branch. Take the accel VC's
money in 2019; spend the equity position in 2033 to buy the world a year.

---

## 3. Migration note (for the L1 re-denomination pass)

Current literal-doom sites the L1 pass must convert to intermediary writes (grep targets):
`turn_manager.gd` base `doom_rise` → `ambient_risk` schedule (the baseline stream);
`capabilities_doom` → `frontier_capability`/`general_capability` writes; `doom_reduction`
(safety researchers) → `global_alarm`/`political_pressure` writes that gate **typed
dampers** (§2), **not** a direct −doom; `opponents` doom contributions → per-actor
`frontier_capability` + rival-driven `panic`. New schema surface from round 2: ADR-0005
schedule entries gain a **pulse envelope** field (ramp/spike/tail — R2-Q6).
ADR-0015 §5: L9 schema deprecates direct doom fields; exploit sweeps are the regression.

---

## Questions for Pip (veto checklist)

> **Status key:** ✅ ruled/applied (round 1) · 🟡 provisional, confirm pending · ⬜ open.

**Names (all freely overridable — ⬜ open):**
- ⬜ **Q-NAME-1** `dedicated_ai_compute` for `global_dedicated_AI_compute` — accept, or keep `global_` prefix? (alt: `frontier_compute`)
- ⬜ **Q-NAME-2** `political_pressure` for `something_for_attitudes_of_political_pressures` — accept? (alts: `regulatory_climate`, `political_will`, `governance_stance`)
- ⬜ **Q-NAME-3** `ambient_risk` for `ambient_capability_-_risk_background_levels` — accept? (alt: `background_hazard`)
- ⬜ **Q-NAME-4** Keep `general_capability`, `frontier_capability`, `global_compute`, `global_alarm`, `global_panic` verbatim as the code names? (assumed yes)

**Load-bearing semantics (⬜ open):**
- ⬜ **Q-SEM-ALARM/PANIC** Accept alarm = *productive concern → governance*, panic = *counterproductive flailing → bad regulation + racing*, same fear opposite usefulness?
- ⬜ **Q-SEM-COMPUTE** Accept `global_compute` = uncontrollable ocean (ceiling + diffusion clock), `dedicated_ai_compute` = controllable fleet (frontier fuel + the only governable pool)?
- ⬜ **Q-SEM-POLITICAL** Accept `political_pressure` as a **signed** axis (positive = toward governance, negative = toward acceleration), not a magnitude?

**Structural judgment calls — round-1 rulings applied:**
- ✅ **Q-FN-1** `MIN_FLOOR` **REJECTED as an engine clamp.** Replaced by the instrumentation invariant (§2 rule 3): rate may go negative; any `rate ≤ 0` turn without a sacred-object-grade cause is loudly logged/flagged (debug + telemetry). Pip: downward spikes legal *"if a player pulls something impressive off."* The floor is an instrument, not a clamp.
- ✅ **Q-FN-2** Bounded global governance-damping **RULED too restrictive.** Restructured to named component streams + **typed dampers with durations** (§2); the never-reverses clamp is deleted; net-negative turns legal, policed by Q-FN-1's invariant.
- 🟡 **Q-FN-3** Reshaped by round 2: routine dampers can now push the *rate* negative; sacred-object chains (§2b) remain the discrete *level* reductions and the policing category for the Q-FN-1 invariant. Residual: R2-Q7 (what counts as sacred-grade).
- ✅ **Q-ASYM-1** Superseded by the stream restructure — panic stays an additive stream; alarm is no longer a multiplier at all (it gates dampers, R2-Q2).
- ⬜ **Q-FN-4** `frontier_capability` enters as **overhang** (`frontier − safety_absorption`), general_capability as a **chronic floor** — accept the acute-vs-chronic split? (Now partly folded into R2-Q1 stream membership.)

**Scope / does-it-enter-directly:**
- ✅ **Q-COMPUTE-DIRECT** **RULED: cards, not stack** (§1.3). No *standing* player lever governs `global_compute`; edge-case content events (autocratic crackdowns on PC-grade compute) are legal at the cards level per ADR-0005. Pip: *"I might be able to solve this at the cards-level, not the stack-level, to use a M:TG analogy."*
- ⬜ **Q-FRONTIER-INDEX** `frontier_capability` per-actor variants are **indices into one intermediary** (map actor→level), doom reads `max`/top-k — accept? Or should `frontier_capability[player]` be its own named thing (it already behaves specially for DQ-22 aggro)?

**Merges/splits (ADR-grade — surfaced, not taken; ⬜ open):**
- ⬜ **Q-MERGE-1** Keep `global_alarm` and `global_panic` as **two** variables (society can be both at once), rather than one signed "public_response"? (strawman says two; confirm)
- ⬜ **Q-SPLIT-1** `ambient_capability_-_risk_background_levels` — one scalar (`ambient_risk`), or split into `ambient_capability` vs `ambient_risk`? (strawman keeps one; the dash in your string hints at two)
- ⬜ **Q-MERGE-2** Any of the eight you now think should collapse into a read/write on another (ADR-0015 restraint test)? Candidate to pressure-test: is `general_capability` just `frontier_capability` on a lag + a diffusion function, i.e. derivable rather than stored?

**Conflicts:**
- ✅ **Q-CONFLICT-1** **CONFIRMED (Pip, round 3):** two distinct objects. `political_pressure` = world-state intermediary; the `game_state.gd governance: float = 50.0` stays a player-currency **stub** whose DQ-7 design will define it as a lever that **writes into** the world intermediary. Vintage placeholder, cheap to rename.
- ✅ **Q-CONFLICT-2** Mapping **ACCEPTED**; Pip reserves revisit. Pip's principle, verbatim: *"our architecture should be robust to some numbers shifts if things are moving laterally, not up and down, as we establish hierarchies and embed them into our structural tree."*

**ROUND-2 questions (new — raised by the streams/dampers restructure; all ⬜):**
- ⬜ **R2-Q1 · Stream-list completeness vs the eight.** Your ruling named baseline / overhang / panic / pulses / cyclic. This strawman *keeps* `diffusion` (general_capability) and `compute` (dedicated_ai_compute) as their own streams so all eight intermediaries still enter the function somewhere. Confirm they're streams — or fold diffusion into baseline and compute into overhang (as an input to `safety_absorption`/frontier), or drop one?
- ⬜ **R2-Q2 · Where alarm/political_pressure now live.** Strawman: they have **no stream of their own** — they gate typed-damper availability/strength (§1.5/§1.7). Accept, or should high alarm be its own (small, negative?) stream?
- ⬜ **R2-Q3 · Damper targeting rules.** Which streams are damper-eligible? Can pre-emptive policy damp a *scheduled pulse* (regulating a model release before it lands)? Is the baseline stream damper-proof (it reads as "the world," not a grippable thing)?
- ⬜ **R2-Q4 · Damper grants, durations, stacking.** Granted by completed workstreams / adoption / governance wins, with expiries — who prices them (Balance layer, yes, but which *systems* mint them)? Do multiple dampers on one stream stack additively, and is there a per-stream cap?
- ⬜ **R2-Q5 · Cyclic streams content.** Are cyclic streams just *looping scheduled pulses* (one machinery, ADR-0005) or a distinct type? Candidate instances owed: hype cycles, funding winters, election years.
- ⬜ **R2-Q6 · Pulse envelope schema.** Ramp/spike/decay-tail parameterization becomes a field on ADR-0005 schedule entries — L1/L9 schema addition; confirm shape vocabulary (attack/sustain/release is the obvious three-knob version).
- ⬜ **R2-Q7 · "Sacred-object-grade cause" definition** for the Q-FN-1 telemetry invariant: does a big stack of ordinary dampers legitimately produce a negative turn (no flag), or do only chain payouts / sacrifices count as flag-suppressing causes?
- ⬜ **R2-Q8 · Gauntlet vs sacrifice payout split (§2b).** Does a pure gauntlet completion (no sacrifice) pay a *small* reduction with sacrifice as a multiplier, or is composition (c) mandatory for any level reduction?
- ⬜ **R2-Q9 · Negative components.** A damper can push an individual stream below zero in this pseudocode (a damped pulse becomes a relief dip). Clamp each stream at 0, or allow negative components?

---

*DQ-21 strawman — Fable Lane 0, workshop #3 build wave, 2026-07-13. Round 2: Pip veto
round 1 applied same day (streams + typed dampers, floor-as-instrument, sacred-object
two senses). Round 3: Q-CONFLICT-1 confirmed; two-instrument display ruling. Serves
ADR-0015; consumes ADR-0011 researcher model; feeds the L1 re-denomination pass, the
L9 schema, and the ADR-0005 pulse-envelope schema addition.*

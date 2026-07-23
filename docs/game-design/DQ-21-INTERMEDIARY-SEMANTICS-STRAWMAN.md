# DQ-21 — Intermediary semantics v1 (VETOED — round 4, rulings applied)

> **Status: FULLY VETOED, ROUND 4 (2026-07-13). Fable Lane 0, workshop #3 build wave.**
> Pip completed the full veto sheet; every question in the checklist now carries its
> ruling. Only three items remain non-final, by design: **R2-Q4** (damper pricing —
> DEFERRED to next workshop beat, with a research errand), **R2-Q5** (cyclic streams —
> OPEN by direction: prefer emergent over hardcoded; v1 ships none), and **R2-Q9**
> (stream clamp — v1 ruling with a LOUD revisit marker). History: round 1 = initial
> strawman; round 2 = streams + typed dampers, MIN_FLOOR clamp and global damping
> multiplier deleted, §2b added; round 3 = Q-CONFLICT-1 confirmed + two-instrument
> display ruling; round 4 = full sheet (this revision).
> This document defines names + semantics for the eight doom intermediaries Pip seeded
> (WORKSHOP_2_BACKLOG DQ-21, 2026-07-13) and the v1 doom-function *shape*. The veto
> checklist at the end is now the ruling record.
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
- **Enters doom via:** the **diffusion stream** ([x] R2-Q1 confirmed: its own stream) —
  raises the hazard *floor*; more actors, more surface. Slow, broad, hard to reverse.
- **Read/written by:** schedule causes (ADR-0005/0016) write it; ADR-0010 adoption
  routing writes it when the adopted work is capability-flavored; doom function reads it.
- **[x] RULED (round 4, Q-MERGE-2):** stays a **stored** intermediary in v1 (not derived
  from `frontier_capability` + lag); derive later only if the exploit sweep shows
  redundancy.

### 1.2 `frontier_capability`  *(verbatim: `frontier_capability` + per-actor variants)*

- **Definition.** The leading edge — what the single most-advanced actor can do, ahead of
  diffusion. Modelled as a **map `actor -> level`** (`frontier_capability[player]`,
  `frontier_capability[rival_A]`, …); the seeded "per-actor variants" are **indices into
  one intermediary, not eight new intermediaries** (ADR-0015 restraint). The scalar the
  doom function reads is `max` over actors (or top-k); the gap `frontier − general` is the
  *overhang*.
- **[x] RULED (round 4, Q-FRONTIER-INDEX):** indices-into-one-map confirmed, **and** the
  player's slice gets its own name since DQ-22 aggro reads it specially — proposed name
  (Fable's, veto-able like all names): **`player_frontier`**, an alias for
  `frontier_capability[player]`, the variable rival aggro-thresholds key on.
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
- **Enters doom via:** **indirectly, through `dedicated_ai_compute`** — see 1.4.
  `global_compute` does **not** have its own doom term ([x] confirmed via Q-SEM-COMPUTE);
  it is a *derivation input* that sets the ceiling and the diffusion pace.
- **Read/written by:** schedule writes; `dedicated_ai_compute` derivation reads;
  `general_capability` diffusion pace reads.
- **[x] RULED (round 2, Pip):** stack-level crispness holds — **no standing player lever
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
- **Enters doom via ([x] R2-Q2 ruled: gate-only, no stream of its own):** positive
  `political_pressure` gates the availability and strength of **typed dampers** on
  specific streams (e.g. a compute-cap damper on the compute stream, a regulation damper
  on a release pulse); negative `political_pressure` weakens/blocks dampers and feeds the
  panic/racing side. (Contrast `global_alarm`, which round 4 gave a small stream of its
  own *in addition to* its gating role — §1.7.)
- **Read/written by:** ADR-0010 adoption, ADR-0011 governance archetype, ADR-0003 lobbying
  chains, alarm/panic all write; doom function reads.
- **Forward-integration note (round 4, Pip):** *"this will probably need to be built into
  component risk factors. Note future intent to integrate real world risk and harm
  taxonomies like the MIT AI Risk work into the game."* (Pip verbatim; his "Rist"
  normalized to "Risk".) Reference taxonomy source: the **MIT AI Risk Repository** —
  when `political_pressure` (and the risk-side intermediaries generally) decompose into
  component risk factors, that decomposition should map onto a real-world risk/harm
  taxonomy rather than an invented one. Future ADR-grade work; noted here so the v1
  scalar is understood as a placeholder for a componentized structure.
- **[!] CONFLICT — [x] CONFIRMED (Pip, round 3):** **two distinct objects.**
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
  reads as *"capability-risk background levels."* **[x] RULED (round 4, Q-SPLIT-1): one
  scalar** — no split into `ambient_capability` vs `ambient_risk`.

### 1.7 `global_alarm`  *(verbatim: `global_alarm`)*

- **Definition ([x] semantics confirmed round 4, Q-SEM-ALARM/PANIC — the load-bearing half
  of the pair).** **Productive
  concern.** Alarm is society/governance taking the problem seriously in a *coordinated,
  competent* way: it funds safety, enables caps, slows reckless racing, makes safety work
  adoptable. Alarm is the "good" awareness — concern that converts into governance.
- **Raises:** legible safety work being *adopted* (ADR-0010); credible warnings that land
  correctly; incidents *interpreted competently*; high-fidelity SA/media channels
  (ADR-0014) carrying real signal.
- **Lowers:** time/habituation (alarm decays if not fed); an incident mishandled converts
  alarm→panic rather than raising alarm; cynicism.
- **Enters doom via ([x] R2-Q2 CHANGED, round 4 — alarm now has BOTH roles):**
  1. **A small stream of its own** in the doom function — a modest, direct contribution
     reflecting that a genuinely alarmed world is somewhat safer even before formal
     governance lands (norms shift, reviewers get pickier, deployments get double-checked).
     Sign: negative (a small standing relief), inherited from the R2-Q2 question wording
     — magnitude deliberately small; the heavy lifting stays in dampers. *(Sign choice is
     Fable's reading of the ruling — flagged; see the R2-Q9 revisit note for the
     interaction with the stream clamp.)*
  2. **The damper gate** (unchanged from round 2): alarm is the input that lets
     `political_pressure` go positive and stick, making governance-grade dampers (compute
     caps, regulation on release pulses, safety adoption) purchasable and effective.
  `political_pressure` remains gate-only; alarm is the only social variable with a
  direct stream.
- **Read/written by:** ADR-0010 adoption + ADR-0004/0014 SA channels + ADR-0005 incident
  causes write; `political_pressure` and doom function read.

### 1.8 `global_panic`  *(verbatim: `global_panic`)*

- **Definition ([x] semantics confirmed round 4, Q-SEM-ALARM/PANIC — the other half).**
  **Counterproductive flailing.**
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
realistic case), so they are two variables, not a signed one ([x] CONFIRMED, round 4,
Q-MERGE-1).

---

## 2. The doom function (streams + typed dampers — round-4 rulings applied)

> **Round-1 shape retired by Pip's veto:** the `MIN_FLOOR` engine clamp (Q-FN-1,
> **rejected** — replaced by an instrumentation invariant) and the single bounded
> multiplicative governance-damping term (**ruled too restrictive** — replaced by typed
> dampers on named streams). The never-reverses clamp is **deleted**; net-negative rate
> turns are legal. Pip: downward spikes are legal *"if a player pulls something
> impressive off."* **The floor is an instrument, not a clamp.**
> **Round 4:** all eight intermediaries confirmed as their own streams (R2-Q1); alarm
> gains a small stream (R2-Q2); baseline is damper-eligible (R2-Q3); the invariant is
> trend-grade at N=6 months (R2-Q7); streams clamp at 0 in v1 with a LOUD revisit
> marker (R2-Q9); no cyclic machinery in v1 (R2-Q5).

Design principle: **complexity lives in superposition; legibility lives in components.**
`doom_rate` is a plain **sum of named streams**; each stream is individually attributable
via the L6 chip system, and the "wiggly stock-market like lines" Pip wants are the
*emergent interference pattern of legible streams* — never noise injected anywhere.

Design rules (ADR-0015 + DESIGN_PHILOSOPHY 2026-07-13, as amended by veto rounds 1–4):

1. **Doom is a rate that accumulates.** The player experiences `doom_rate`; history ticks
   `doom_level` up (or, on net-negative turns, down) by integrating it. Death when
   `doom_level` crosses a threshold; the **badge is the date** (ADR-0009 / WORLD_AND_LORE).
2. **The background nearly always climbs — statistically, not by clamp.** The baseline
   stream's year-keyed schedule does the climbing; the engine never forces the sum positive.
3. **Trend-grade invariant ([x] R2-Q7 ruled, N=6):** doom rate MAY go negative on any turn;
   what the engine loudly flags (debug + telemetry) is a **sustained 6-month negative
   trend without sacred-object-grade causes**. A bot policy that sustains decline is an
   **exploit-sweep gate failure**. Single negative turns need no sacred cause — they're
   the "pulled something impressive off" moments.
4. **No printed doom.** No action/event writes doom; they write intermediaries, inject
   scheduled pulses, or grant typed dampers. Doom is computed each day tick (ADR-0015 §1).
5. **Attributable.** Every stream is named → the L6 chain (EE-8) can say what is killing
   (or saving) you, per component, per tick (ADR-0015 §3, ADR-0004 legibility).

Pseudocode (illustrative — not GDScript; magnitudes are `Balance` config, not here):

```
# ── Per day tick. doom_rate = sum of NAMED streams. All eight intermediaries
#    enter as their own streams ([x] R2-Q1 confirmed). ──

func compute_doom_rate(s, t) -> (float, Dict):
    streams = {}

    # (a) baseline — ambient_risk, year-keyed schedule (§1.6). The slow trend under
    #     everything; 2017: low and slow — the steady build IS the early grind.
    streams["baseline"] = s.ambient_risk

    # (b) overhang — acute frontier hazard (§1.2)
    streams["overhang"] = W_FRONTIER * max(0.0, s.frontier_capability_max - safety_absorption(s))

    # (c) diffusion — chronic floor from general_capability (§1.1)
    streams["diffusion"] = W_GENERAL * s.general_capability

    # (d) compute — dedicated_ai_compute fuel term (§1.4)
    streams["compute"] = W_COMPUTE * compute_pressure(s.dedicated_ai_compute)

    # (e) panic — additive social accelerant (§1.8)
    streams["panic"] = W_PANIC * s.global_panic

    # (f) alarm — small direct stream ([x] R2-Q2 changed, round 4): a genuinely alarmed
    #     world is slightly safer even before formal governance lands. Small by design;
    #     the heavy lifting stays in dampers (which alarm also gates, §1.7).
    streams["alarm"] = -W_ALARM * s.global_alarm          # W_ALARM small; sign per §1.7

    # (g) SCHEDULED PULSES — ADR-0005 schedule entries inject time-shaped rate bumps
    #     ([x] R2-Q6: envelope is a schedule-entry schema field): anticipation ramp →
    #     spike → decay tail. Pip: "we can predict an increase in Doom around the time
    #     these 3 new models are going to be released."
    for pulse in s.schedule.active_pulses(t):
        streams["pulse:" + pulse.id] = pulse.envelope(t)

    # (R2-Q5: NO distinct cyclic-stream machinery in v1 — Pip prefers cycles emergent
    #  from mechanisms; revisit as workshopping continues.)

    # ── TYPED DAMPERS ── player mitigations attach to SPECIFIC streams, with durations.
    # damper = (target_stream, strength(t), expires_at). Granted by completed workstreams,
    # adopted safety work, governance wins (gated by alarm/political_pressure, §1.5/§1.7).
    # Targeting ([x] R2-Q3): baseline is NOT damper-proof; scheduled pulses ARE
    # damper-eligible (pre-emptive policy against an anticipated release spike —
    # inferred from Pip's prior model-release scenario, flagged as inferred not explicit).
    # v1 clamp (R2-Q9, LOUD REVISIT MARKER): dampers cannot push a hazard stream below 0.
    for d in s.active_dampers(t):
        streams[d.target] = max(0.0, streams[d.target] - d.strength(t))
    # NOTE: the alarm stream is natively negative by design and is not damper-produced,
    # so the v1 clamp does not apply to it — this asymmetry is part of the R2-Q9 revisit.

    rate = sum(streams.values())                     # superposition — MAY be negative

    # Trend-grade invariant ([x] R2-Q7, N=6): flag sustained decline, not single dips.
    if trailing_trend(s.rate_history, months=6) < 0.0 and not s.sacred_grade_causes_in_window(months=6):
        telemetry.flag("sustained_negative_trend_without_sacred_cause", t, streams)  # loud
        # exploit sweep: a bot policy sustaining this state FAILS the gate
    return rate, streams                              # streams dict feeds the L6 chips


func day_tick(s, t):
    s.doom_rate, s.doom_streams = compute_doom_rate(s, t)
    s.doom_level += s.doom_rate * DAY_DT     # may FALL on net-negative turns — legal

    # Discrete level reductions: sacred-object chains (§2b, as revised round 4) —
    # gauntlet payouts, with sacrifice as an emergent situational cost, not a formula.
    for chain in s.completed_sacred_chains(t):
        s.doom_level -= chain.reduction
        if chain.has_sacrifice: ledger.burn(chain.sacrifice)   # §2b: many, not all

    if s.doom_level >= DOOM_DEATH_THRESHOLD:
        end_run(date = t)                     # the badge is the date
```

Why this shape (mechanism, not decoration):

- **Superposition produces the texture.** Baseline trend + pulse envelopes + damper
  grants and expiries interfere into exactly the "wiggly stock-market like lines" Pip
  asked for — and every wiggle decomposes into named components on inspection (L6 chips
  can show the stack per tick). Complexity in the sum, legibility in the parts.
- **Scheduled pulses make the reality-tether mechanical** (ADR-0016): a league update that
  says "three frontier models release in March" is literally three pulse entries with
  anticipation ramps — the market *pricing in* a release before it happens, then the spike,
  then the decay tail as the world absorbs it.
- **Typed dampers replace the global multiplier.** A mitigation is a *targeted, timed*
  purchase: a compute-cap treaty damps the compute stream for its duration; a competent
  public-comms play damps panic; pre-emptive policy work damps an upcoming release pulse
  ([x] R2-Q3 — pulse-damping inferred from Pip's model-release scenario; baseline is also
  damper-eligible, ruled explicitly). This kills the round-1 problem (one scalar hid
  *what* governance was actually gripping) and buys per-stream attribution for free.
- **Decline is earned, visible, and policed at trend grain.** Single negative turns are
  free wins ("pulled something impressive off"); a *sustained* 6-month decline without
  sacred-grade causes trips the telemetry flag and fails the exploit-sweep gate — the
  sweep catches damper-stacking exploits instead of a clamp hiding them.
- Every stream names an intermediary or a schedule entry → L6 attributes a death to
  "frontier overhang" vs "panic-driven racing" vs "the March release pulse," satisfying
  ADR-0015 §3.

### Display implications — two instruments ([x] RULED, Pip 2026-07-13)

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

## 2b. Sacred-object chains — two senses (revised round 4)

> Term attribution: "sacred objects" is Pip's own 2026-07-13 wording — *"trading off
> increasingly sacred objects / values / projects"* (DESIGN_PHILOSOPHY, doom-as-rate
> entry). Round 1 conflated two distinct mechanisms under the phrase; round 2 split
> them; **round 4 rejected composition as a hard gate** (see (c)).

**(a) Gauntlet chains** — multi-stage-gated pipelines, **each gate failable**. Pip's
ur-example: *impactful paper → shown at conference → wins award → gains political traction
→ applied to policy.* This is ADR-0010's research→adoption pipeline run to its endgame,
and the machinery already exists: ADR-0011 workstreams (the stages), ADR-0009 durations
(each stage takes months), ADR-0014 conference gates (attendance is literally a gate).
Doom reduction is the **completed-chain payout**; nothing need be sacrificed — **the
difficulty IS the gauntlet** (many failable gates × long durations × opportunity cost).

**(b) Sacrifice payments** — burning an accumulated, **hard-to-replace stock**. Pip's
example: cashing a strong equity position in a frontier lab. Also in the class: flagship
projects (killing the thing the org is known for), veteran hires (attachment-is-built-
to-be-spent, DESIGN_PHILOSOPHY "On the hero and the office"), mission purity (the
crusader walks, §DQ-15 archetype 3). The price is a ledger burn (ADR-0003), and the pain
scales with how long you fed the stock.

**(c) Composition — [x] REJECTED as a hard gate (round 4, R2-Q8).** Pip, verbatim:
*"doesn't actually require sacrifice. Earlier thoughts thought of as papers etc as a
grind. Players might be able to seize opportunities when they come up, sacrifice will be
required for many good results, but not all and not deterministically, but because it's
hard to do hard things."* Cashed out:
- **Gauntlet completion alone CAN pay level reductions.** No sacrifice requirement.
- **Sacrifice is an emergent, situational cost of doing hard things** — many gates, when
  you reach them, will *happen* to demand giving something up (the policy win needs the
  capabilities partnership dropped; the treaty needs your equity divested) — but this is
  content-situational, **not a design formula**, and never deterministic.
- **Opportunity-seizing is legal and rewarded.** A player positioned to grab a rare
  moment (the right incident, the right room, the right month) may bank a reduction
  cheaply. That's skill expressing itself, not a leak — the trend-grade invariant (§2
  rule 3), not a sacrifice tax, is what polices sustained decline.

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
schedule entries gain a **pulse envelope** field (ramp/spike/tail — [x] R2-Q6 confirmed).
ADR-0015 §5: L9 schema deprecates direct doom fields; exploit sweeps are the regression.

---

## Veto checklist — RULING RECORD (round 4: full sheet completed)

> **Status key:** [x] RESOLVED (ruling recorded) · DEFERRED (R2-Q4) · OPEN by design
> (R2-Q5) · [!] RESOLVED-v1 with LOUD revisit marker (R2-Q9).

**Names — all [x] APPROVED (round 4):**
- [x] **Q-NAME-1** `dedicated_ai_compute` **APPROVED**.
- [x] **Q-NAME-2** `political_pressure` **APPROVED** (signed axis).
- [x] **Q-NAME-3** `ambient_risk` **APPROVED**.
- [x] **Q-NAME-4** Rest verbatim **APPROVED**: `general_capability`, `frontier_capability`, `global_compute`, `global_alarm`, `global_panic`.

**Load-bearing semantics — all [x] CONFIRMED (round 4):**
- [x] **Q-SEM-ALARM/PANIC** **CONFIRMED**: alarm = productive concern → governance; panic = counterproductive flailing → bad regulation + racing; two-variable framing (see Q-MERGE-1).
- [x] **Q-SEM-COMPUTE** **CONFIRMED**: ocean-vs-fleet framing; cards-level exceptions legal (see Q-COMPUTE-DIRECT).
- [x] **Q-SEM-POLITICAL** **CONFIRMED**: `political_pressure` = the world's disposition, signed axis, distinct from the player governance stub (Q-CONFLICT-1). **Addition (Pip, verbatim; "Rist" normalized to "Risk"):** *"this will probably need to be built into component risk factors. Note future intent to integrate real world risk and harm taxonomies like the MIT AI Risk work into the game."* Reference taxonomy source: the **MIT AI Risk Repository** (see §1.5 forward-integration note).

**Structural:**
- [x] **Q-FN-1** `MIN_FLOOR` **REJECTED as an engine clamp** (round 2). Replaced by the instrumentation invariant, refined trend-grade by R2-Q7. Pip: downward spikes legal *"if a player pulls something impressive off."* The floor is an instrument, not a clamp.
- [x] **Q-FN-2** Bounded global governance-damping **RULED too restrictive** (round 2). Restructured to named component streams + typed dampers with durations (§2); never-reverses clamp deleted.
- [x] **Q-FN-3** Resolved via rounds 2+4: dampers can push the *rate* negative; sacred-object chains (§2b) are the discrete *level* reductions; the R2-Q7 trend-grade invariant (now ruled, N=6) polices sustained decline.
- [x] **Q-ASYM-1** Superseded by the stream restructure (round 2); alarm's role finalized by R2-Q2 (round 4).
- [x] **Q-FN-4** **CONFIRMED (round 4)**: overhang = acute hazard, `general_capability` = chronic floor.
- [x] **Q-COMPUTE-DIRECT** **RULED: cards, not stack** (round 2, §1.3). No standing player lever on `global_compute`; edge-case content events legal per ADR-0005. Pip: *"I might be able to solve this at the cards-level, not the stack-level, to use a M:TG analogy."*
- [x] **Q-FRONTIER-INDEX** **CONFIRMED (round 4)**: indices into one map, **and** the player's slice is separately named since DQ-22 aggro reads it — proposed `player_frontier` (Fable's name proposal, §1.2).

**Merges/splits:**
- [x] **Q-MERGE-1** **CONFIRMED (round 4)**: two variables (society can be both alarmed and panicked at once).
- [x] **Q-SPLIT-1** **CONFIRMED (round 4)**: one scalar (`ambient_risk`); no split.
- [x] **Q-MERGE-2** **RESOLVED (round 4, per recommendation)**: `general_capability` stays **stored** in v1; derive it later only if the exploit sweep shows redundancy.

**Conflicts:**
- [x] **Q-CONFLICT-1** **CONFIRMED (round 3)**: two distinct objects; the `game_state.gd governance` float stays a player-currency stub whose DQ-7 design will define it as a lever writing into `political_pressure`.
- [x] **Q-CONFLICT-2** Mapping **ACCEPTED** (round 2); Pip reserves revisit. Pip's principle, verbatim: *"our architecture should be robust to some numbers shifts if things are moving laterally, not up and down, as we establish hierarchies and embed them into our structural tree."*

**Round-2 questions — rulings (round 4):**
- [x] **R2-Q1** **CONFIRMED**: all eight intermediaries enter as their own streams (baseline, overhang, diffusion, compute, panic, alarm, + pulses from the schedule).
- [x] **R2-Q2** **CHANGED**: `global_alarm` becomes a **small stream itself** *in addition to* gating typed-damper availability/strength (both roles, §1.7); `political_pressure` remains **gate-only** (§1.5).
- [x] **R2-Q3** **RULED**: the baseline stream is **NOT damper-proof**. Pulse-damping (pre-emptive policy against an anticipated release spike): **YES** — provenance: *inferred from Pip's prior model-release scenario (mitigations stacked against an anticipated spike)*, flagged as inferred, not explicit.
- **R2-Q4** **DEFERRED to next workshop beat.** Pip's instruction, verbatim: *"prompt agent to find examples from real history to baseline with or against."* **Research errand logged:** historical analogs of policy/institutional responses damping technology risks (candidates to research: CFC/Montreal Protocol, nuclear test-ban and nonproliferation regimes, automotive/aviation safety regulation, leaded-petrol and asbestos phase-outs) — to baseline damper magnitudes and durations against real response curves.
- **R2-Q5** **OPEN with direction**: Pip prefers cycles **emergent from mechanisms** over a hardcoded cyclic type — *"I feel like there might be ways of making these emergent from mechanisms as we keep workshopping them."* **v1 ships no distinct cyclic machinery.**
- [x] **R2-Q6** **CONFIRMED**: pulse envelope (ramp/spike/tail) becomes an ADR-0005 schedule-entry schema field (L1/L9 schema addition).
- [x] **R2-Q7** **CONFIRMED, N=6**: trend-grade invariant — a **sustained 6-month negative trend without sacred-object-grade causes flags loudly** (debug + telemetry); a bot policy sustaining decline is an **exploit-sweep gate failure**. Single negative turns are legal without ceremony.
- [x] **R2-Q8** **REVISED — composition REJECTED as a hard gate.** Pip, verbatim: *"doesn't actually require sacrifice. Earlier thoughts thought of as papers etc as a grind. Players might be able to seize opportunities when they come up, sacrifice will be required for many good results, but not all and not deterministically, but because it's hard to do hard things."* §2b rewritten: gauntlet completion alone CAN pay level reductions; sacrifice is an emergent situational cost of hard things, not a design formula; opportunity-seizing is legal and rewarded.
- [!] **R2-Q9** **RESOLVED-v1 with LOUD REVISIT MARKER**: streams clamp at 0 in v1 (dampers cannot push a hazard stream negative). Pip, verbatim: *"make careful note to revisit, noting we had had some discussions in this recently and am not settled."* **REVISIT NOTE:** the round-4 alarm stream (R2-Q2) is *natively* negative and sits outside the clamp — the clamp/negative-component boundary is exactly the unsettled ground; re-open both together.

---

*DQ-21 — Fable Lane 0, workshop #3 build wave, 2026-07-13. Round 2: streams + typed
dampers, floor-as-instrument, sacred-object two senses. Round 3: Q-CONFLICT-1 confirmed;
two-instrument display ruling. Round 4: full veto sheet applied — document now a ruling
record; remaining non-final items: R2-Q4 (deferred + research errand), R2-Q5 (open by
design), R2-Q9 (v1 + revisit marker). Serves ADR-0015; consumes ADR-0011 researcher
model; feeds the L1 re-denomination pass, the L9 schema, and the ADR-0005 pulse-envelope
schema addition.*

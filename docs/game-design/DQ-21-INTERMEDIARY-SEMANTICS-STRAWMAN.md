# DQ-21 — Intermediary semantics v1 (STRAWMAN, for Pip veto)

> **Status: STRAWMAN. Fable Lane 0, workshop #3 build wave. Nothing here is ruled.**
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
  *derivation input* that sets the ceiling and the diffusion pace. (Flagged in veto — if
  Pip wants it to bite directly, that's a one-line add.)
- **Read/written by:** schedule writes; `dedicated_ai_compute` derivation reads;
  `general_capability` diffusion pace reads.

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
- **Enters doom via:** the `governance` damping term — positive `political_pressure`
  (especially combined with alarm) *slows* the climb by enabling caps on
  `dedicated_ai_compute` and safety adoption; negative `political_pressure` *amplifies*
  (removes the brakes, feeds the race). **Damping only — it slows the rate, it does not
  make doom fall.** (See §2 on why.)
- **Read/written by:** ADR-0010 adoption, ADR-0011 governance archetype, ADR-0003 lobbying
  chains, alarm/panic all write; doom function reads.
- **⚠ CONFLICT:** the engine already has `game_state.gd: var governance: float = 50.0`
  (DQ-7, an ADR-0003 ledger currency, starts 50, player raises/spends). That is a **player
  resource**; this intermediary is **world state**. They are not obviously the same object,
  and they must not silently collide. See veto Q-CONFLICT-1.

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
- **Enters doom via:** the `ambient` base term — the floor of `doom_rate`, ensuring the
  climb almost never stops (the `MIN_FLOOR` in §2). This is the intermediary that most
  directly *is* "doom is a rate."
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
- **Enters doom via:** the `governance` damping term — alarm is the input that lets
  `political_pressure` go positive and stick, which lets `dedicated_ai_compute` be capped
  and safety be adopted. **Alarm never touches doom directly** (it is not "−doom"); it
  enables the *governance* that dampens the rate. This keeps ADR-0015's indirection honest
  and matches "you can't win, only buy time."
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
- **Enters doom via:** the `flailing` amplification term — panic *raises* `doom_rate`
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

## 2. The doom function (v1 shape)

Design rules this shape must satisfy (all from ADR-0015 + DESIGN_PHILOSOPHY 2026-07-13):

1. **Doom is a rate that accumulates.** The player experiences `doom_rate`; history ticks
   `doom_level` upward by integrating it. Death when `doom_level` crosses a threshold; the
   **badge is the date** of crossing (ADR-0009 / WORLD_AND_LORE).
2. **The background almost always climbs.** `doom_rate` has a positive floor (`ambient_risk`);
   governance can *slow* it, not casually reverse it.
3. **Doom falls only at the end of long effort chains, priced in sacred objects.** The only
   path to a *negative* contribution to `doom_level` is a completed sacred-object chain — a
   discrete, gated event, not a routine per-tick term.
4. **No printed doom.** No action/event writes doom; they write the intermediaries. Doom is
   computed each day tick from world state (ADR-0015 §1).
5. **Attributable.** Every term traces through named intermediaries so the L6 attribution
   chain (EE-8) can say what is killing you (ADR-0015 §3, ADR-0004 legibility).

Pseudocode (illustrative — not GDScript; magnitudes are `Balance` config, not here):

```
# ── Per day tick. Inputs are the eight world-state intermediaries. ──

func compute_doom_rate(s) -> float:
    # (a) BASE — the always-climbing floor. 2017: low; climbs via the league timeline.
    base = s.ambient_risk                        # §1.6  the "doom is a rate" carrier

    # (b) CAPABILITY HAZARD
    overhang  = max(0.0, s.frontier_capability_max - safety_absorption(s))   # acute, §1.2
    diffusion = s.general_capability                                          # chronic floor, §1.1
    compute   = compute_pressure(s.dedicated_ai_compute)                     # frontier fuel, §1.4
    capability_term = W_FRONTIER*overhang + W_GENERAL*diffusion + W_COMPUTE*compute

    # (c) SOCIAL ACCELERANT — panic flails the rate upward. §1.8
    flailing = W_PANIC * s.global_panic

    # raw upward pressure
    rate = base + capability_term + flailing

    # (d) GOVERNANCE DAMPING — alarm + positive political_pressure SLOW the climb.
    #     Bounded in [0, GOV_MAX_DAMP]; can never invert the sign. §1.5, §1.7
    gov = governance_quality(s.global_alarm, s.political_pressure)   # -> [0, GOV_MAX_DAMP]
    rate = rate * (1.0 - gov)

    # (e) The world nearly always trends up.
    return max(rate, MIN_FLOOR)


func day_tick(s):
    s.doom_rate = compute_doom_rate(s)
    s.doom_level += s.doom_rate * DAY_DT           # history ticks the level up

    # The ONLY path by which doom_level falls: a completed sacred-object chain posts a
    # discrete negative. Priced by consuming a sacred object (a ledger entry representing
    # a sacrificed value / project — ADR-0003). Not a per-tick term; a gated event outcome.
    for chain in s.completed_sacred_chains_this_tick:
        s.doom_level -= chain.reduction            # gated, expensive, rare
        ledger.spend_sacred_object(chain.price)    # tension through sacrifice

    if s.doom_level >= DOOM_DEATH_THRESHOLD:
        end_run(date = s.today)                     # the badge is the date
```

Why this shape (mechanism, not decoration):

- **`base = ambient_risk` + `MIN_FLOOR`** are what make doom *a rate that nearly always
  climbs*. At 2017 spawn `ambient_risk` is small, so the climb is slow — the "steady build
  *is* the early grind." Current build's flat `doom_rise = 5` (turn_manager) is exactly the
  printed-delta legacy ADR-0015 kills; here the "5" dissolves into `ambient_risk`'s
  year-keyed schedule.
- **Governance is multiplicative damping, clamped ≥ 0 net.** Alarm + political_pressure can
  make the climb *slow* but never spontaneously *negative*. That enforces "only at the end
  of long chains can the player's impacts directly reduce Doom." Direct reduction lives
  **only** in the sacred-object branch of `day_tick`, never in `compute_doom_rate`.
- **Panic is additive, alarm is multiplicative-damping** — deliberately asymmetric: panic
  can spike the rate hard and fast (bad regulation is quick); alarm can only ever *bleed off
  a fraction* of the standing pressure (competent governance is slow and bounded). This is
  the honesty claim in mechanism form. (→ veto Q-ASYM-1: is the asymmetry too punishing?)
- Every term names an intermediary → L6 can attribute a death to "frontier overhang" vs
  "panic-driven racing" vs "the background just climbed," satisfying ADR-0015 §3.

**What is NOT specified here (correctly):** all magnitudes (`W_*`, `MIN_FLOOR`, `GOV_MAX_DAMP`,
`DOOM_DEATH_THRESHOLD`, the `ambient_risk` year curve, sacred-chain reduction sizes). Those
are the freely-tuned `Balance` layer (ADR-0015 §4: "the function is structure; pricing is
numbers"). This document is the structure; the exploit-finder + playtests price it.

---

## 3. Migration note (for the L1 re-denomination pass)

Current literal-doom sites the L1 pass must convert to intermediary writes (grep targets):
`turn_manager.gd` base `doom_rise` → `ambient_risk` schedule; `capabilities_doom` →
`frontier_capability`/`general_capability` writes; `doom_reduction` (safety researchers) →
`global_alarm`/`political_pressure` writes feeding the damping term, **not** a direct −doom;
`opponents` doom contributions → per-actor `frontier_capability` + rival-driven `panic`.
ADR-0015 §5: L9 schema deprecates direct doom fields; exploit sweeps are the regression.

---

## Questions for Pip (veto checklist — every judgment call, one line each)

**Names (all freely overridable):**
- **Q-NAME-1** `dedicated_ai_compute` for `global_dedicated_AI_compute` — accept, or keep `global_` prefix? (alt: `frontier_compute`)
- **Q-NAME-2** `political_pressure` for `something_for_attitudes_of_political_pressures` — accept? (alts: `regulatory_climate`, `political_will`, `governance_stance`)
- **Q-NAME-3** `ambient_risk` for `ambient_capability_-_risk_background_levels` — accept? (alt: `background_hazard`)
- **Q-NAME-4** Keep `general_capability`, `frontier_capability`, `global_compute`, `global_alarm`, `global_panic` verbatim as the code names? (assumed yes)

**Load-bearing semantics:**
- **Q-SEM-ALARM/PANIC** Accept alarm = *productive concern → governance*, panic = *counterproductive flailing → bad regulation + racing*, same fear opposite usefulness?
- **Q-SEM-COMPUTE** Accept `global_compute` = uncontrollable ocean (ceiling + diffusion clock), `dedicated_ai_compute` = controllable fleet (frontier fuel + the only governable pool)?
- **Q-SEM-POLITICAL** Accept `political_pressure` as a **signed** axis (positive = toward governance, negative = toward acceleration), not a magnitude?

**Structural judgment calls in the doom function:**
- **Q-FN-1** Doom is a rate with a positive `MIN_FLOOR` so the background nearly always climbs — accept the floor?
- **Q-FN-2** Governance (alarm + political_pressure) is **multiplicative damping clamped ≥ 0 net** — it slows, never reverses. Accept? (this is what enforces "direct reduction only at chain-end")
- **Q-FN-3** Direct doom *reduction* lives **only** in the sacred-object chain branch (discrete, gated, priced in a ledger sacred-object), never as a per-tick term. Accept?
- **Q-ASYM-1** Panic is **additive** (fast, hard spikes), alarm is **multiplicative-damping** (slow, bounded bleed-off). Accept the asymmetry, or is it too punishing?
- **Q-FN-4** `frontier_capability` enters as **overhang** (`frontier − safety_absorption`), general_capability as a **chronic floor** — accept the acute-vs-chronic split?

**Scope / does-it-enter-directly:**
- **Q-COMPUTE-DIRECT** `global_compute` has **no** direct doom term (bites only through `dedicated_ai_compute` + diffusion pace). Accept, or should the ocean bite directly?
- **Q-FRONTIER-INDEX** `frontier_capability` per-actor variants are **indices into one intermediary** (map actor→level), doom reads `max`/top-k — accept? Or should `frontier_capability[player]` be its own named thing (it already behaves specially for DQ-22 aggro)?

**Merges/splits (ADR-grade — surfaced, not taken):**
- **Q-MERGE-1** Keep `global_alarm` and `global_panic` as **two** variables (society can be both at once), rather than one signed "public_response"? (strawman says two; confirm)
- **Q-SPLIT-1** `ambient_capability_-_risk_background_levels` — one scalar (`ambient_risk`), or split into `ambient_capability` vs `ambient_risk`? (strawman keeps one; the dash in your string hints at two)
- **Q-MERGE-2** Any of the eight you now think should collapse into a read/write on another (ADR-0015 restraint test)? Candidate to pressure-test: is `general_capability` just `frontier_capability` on a lag + a diffusion function, i.e. derivable rather than stored?

**Conflicts found (see also the mapping question below):**
- **Q-CONFLICT-1** `political_pressure` (world-state intermediary) vs the existing `game_state.gd governance: float = 50.0` (DQ-7 player *ledger currency*). Same object, or two distinct things that need distinct names? If distinct, does the player-currency `governance` *write* the world-state `political_pressure` (spend-to-shift), or stay separate?
- **Q-CONFLICT-2** ADR-0015's illustrative vocabulary ("lab capability, deployment pressure, governance quality, public salience") does not map 1:1 onto your eight. Strawman mapping: deployment pressure ≈ `general_capability`; governance quality ≈ `political_pressure`+`global_alarm`; public salience ≈ `global_alarm`/`global_panic` split. Confirm the mapping, or is a term missing you meant to seed?

---

*DQ-21 strawman — Fable Lane 0, workshop #3 build wave, 2026-07-13. Serves ADR-0015;
consumes ADR-0011 researcher model; feeds the L1 re-denomination pass and the L9 schema.*

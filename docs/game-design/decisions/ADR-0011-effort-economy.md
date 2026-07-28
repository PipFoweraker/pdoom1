# ADR-0011 -- The effort economy: founder hours, staff lanes, manager compression

- **Status:** ACCEPTED (shape); researcher archetype roster content owed (DQ-15)
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 2 (issue #596)

## Context

Current build: one global AP pool, spent instantly; staff add to the pool; researchers
are single-function; banking exists but does nothing. The sweep's diagnosis in mechanism
terms: one fungible currency + state-independent payoffs => constant-policy argmax
(`safety_lean`) dominates. Pip's rulings across beats 1-2: banking is dead (ADR-0009);
*"I have never been around unassigned workers before, because there's always been a
backlog"*; *"each new employee is kinda cutting down the time I need to do other
things"*; managers *"stop employees from annoying me with employee things."*

## Decision

1. **No global AP pool.** The pool illusion dies; staff never add founder AP.
2. **Founder hours** (sacred, roughly fixed per month -- canon since ADR-0008): spent on
   **doors** (stakeholder face-time; which rooms you're in locks strategic paths),
   **approvals** (hires, direction rulings -- "approve this salary," not paperwork
   clicks), **audits** (skip-level ground-truthing), and **reserve** (instant-speed
   firefighting, ADR-0009).
3. **Staff effort is per-person**, assigned at plan speed to workstreams from a backlog.
   **Idle staff don't exist; unmanaged staff do** -- unassigned researchers self-direct
   per their agenda (whose ordering of the backlog wins?).
4. **Workstreams** run multi-month and produce artifacts (papers, systems, campaigns) --
   ADR-0009's no-instant-strategy rule, cashed out.
5. **Managers are interrupt shields with agenda riders:** they absorb their team's class
   of response windows (ADR-0009 economy), compress the plan screen (team -> allocation
   + standing policy; members visually housed under the manager), and report upward via
   a **Celine's-law channel** -- an inward SA channel with fidelity loss. The sim never
   lies; *characters do*. Skip-level audits (founder hours) re-ground truth. Folds
   ADR-0008's deferred inward-SA into existing SA machinery.
6. **Ops/admin staff reduce the founder-price of routine actions** and automate whole
   classes over time (endpoint: 2037 vignette's "payroll is automated").
7. **The dual-use lane is priced:** capabilities work pays money/compute/hype and bills
   doom (with ADR-0010's typed attention: accel VCs fund reckless success).
8. **Researcher model (shape):** *lane preference* (fictionalized real agendas -- e.g.
   interpretability, evals, theory/agent-foundations, governance) x *appetites* (compute,
   prestige/first-author, mentees, money, mission purity -- **promises made to retain
   staff are ledger entries**) x rare *quirk riders* (philosophical stances, secret
   successionist -- an exposure-event genre reusing ADR-0003 machinery, not a lane).

## Beacons served / violated

- **Rams #10:** managers reuse the window economy + SA channels; quirks reuse exposure
  events; banking deleted; no new player-facing currency -- typed effort is a *split* of
  an existing one.
- **MaRo Interaction:** typed lanes force a portfolio; with ADR-0010, the constant
  policy is structurally unavailable, not merely under-rewarded.
- **Honest:** "nobody wants to bring the boss bad news" -- late-discovered doom via rosy
  reporting mirrors the real failure mode.

## Interaction contract

Reads/writes: **response windows** (ADR-0009 -- manager value denominated there),
**SA** (inward channel, fidelity, audits), **Liability Ledger** (agenda riders, retention
promises, dual-use bills), **reputation** (per-person, ADR-0010 -- hires are reputation
seeds who recruit juniors), **replay/exploit-finder** (assignment policies join the
policy space).

## Rejected alternatives

- **Global pool with staff as AP-adders:** sweep-proven degenerate; also violates
  founder-hours canon.
- **Idle unassigned staff:** no such thing ("there's always a backlog").
- **Managers as output multipliers:** rejected -- their value is founder-attention
  arbitrage, not throughput.
- **Soft reserve fallback:** already rejected in ADR-0009.

## Consequences / open questions

- **DQ-15:** researcher archetype roster -- Pip to author 3-5 vignette-style archetypes
  (lane / unmanaged drift / appetite / optional quirk).
- Plan-screen redesign: assignment UI, manager housing, team-satisfaction report
  replacing per-member detail under management.
- Retention/morale stays minimal v1: appetites bite through promises (ledger) and
  departure riders, not a mood sim (ADR-0008 register: "bother," not HR gravity).
- Sweep target: a managed portfolio must beat every constant line; new bot policy axes
  (assignment + response + publish/socialize).
- Balance seam: founder-hour prices for doors/audits/approvals are the new tuning
  surface -- they set the whole game's attention economy.

## Amendment 2026-07-27

WS-3a day rulings (day-log: `WS3A_DAYLOG_2026-07-27.md`), dated additions
only -- the Decision section above is unchanged.

**(a) AP pool dead as a design concept, 2026-07-27 11:37.** Pip's R1 ruling:
"AP confirmed dead (RIP AP, dead 1h03m. Long live A!)." This is the design
death, not the code death -- `action_points` remains what actions actually
spend today (verified: Workstream objects, founder-hour typing, and manager
shields were all unbuilt at time of ruling). **Deletion rides the T2
migration** (LADDER_0011.md's 4-rung ladder): AP cannot die in code before
its replacement plumbing exists to spend against.

**(b) T3 rung picked.** Of the 4-rung effort-economy ladder (LADDER_0011.md,
A1-A17), Pip picked **T3 as the absolute minimum** -- "to kill AP and keep
Attention," reading only the T3 headline before deciding (deliberate). T3 =
Workstream substrate + AP pool deletion (8 JSONs + ~94 `.gd` refs migrating
to typed Attention) + founder-hour typing + a CARVE-1 gate on the higher
rungs. Substrate core landed same day: PR #981 (Workstream object, 8-entry
backlog.json, one-person-one-bet assignment, self-direction with
`reported_progress` vs `actual_progress` fields, compute_intensity billing;
AP itself untouched by this PR, deferred to T2).

**(c) FOUR-WAY founder hours ruled** (R4 ballot 4, ~1615), overriding the
2-way default in LADDER_0011.md's T3 recommendation. The 4-way split
(doors/approvals/audits/reserve, this ADR's point 2) is enabled by
**optimistic self-reporting as the first distortion source**: unassigned
researchers self-direct AND report progress optimistically (already being
built in T1's substrate core, per (b) above); AUDIT hours ground-truth
reported-vs-actual. This is the concrete mechanism this ADR's point 5
("nobody wants to bring the boss bad news") cashes out as, one epoch early --
picked the same day the repo's own silent-promise audit ran (thematic
resonance Pip flagged explicitly). Later T4 managers add a SECOND distortion
source; audits generalize rather than rework. **Reported-vs-actual seam
shipped in PR #981** (deterministic per-person optimism hash, no new RNG).

**Formal review timer: 2026-08-31** (post-v0.14 epoch; adjustable), carrying
the ADR-0018 review-by-clause pattern. Review question: did optimistic
self-reporting + audits earn its complexity, or does 4-way collapse to 2-way
+ manager-era audits? A half-day workshop, **#984**, is scheduled against
this review.

Risk accepted knowingly: this is extra scope inside a break-everything week,
covered by the day's audacity ruling (daily ladder bumps, 3-4 accepted
breaks priced in, logged as lessons).

Founder-hour-typing lane itself (the mechanism that spends the 4-way split)
is scheduled **Tuesday** -- it consumes T1's merged substrate and was
deliberately not parallelized with T1 the same night.

## Amendment 2026-07-28 -- T2 landed: AP deleted in code, 2-way hours live

Build record for the T2 lane. The Decision section above is unchanged; this
records what shipped and the calls the lane had to make.

**(d) The AP pool is DELETED in code**, closing amendment (a). Gone:
`GameState.action_points` / `max_action_points` / `committed_ap` /
`reserved_ap` / `used_event_ap` and their reserve methods;
`turn_manager._step_grant_action_points` (there is now NO per-turn founder
grant of any kind -- point 1's "the pool illusion dies" is now structural,
not a convention); the Balance keys `starting_resources.action_points` and
`action_points.per_staff`. The cost key in all action / event / scenario
data is `attention` (72 keys, 13 files). `action_points` survives ONLY as a
read-only alias in `GameActions.attention_cost()` for content that lags the
code; nothing writes it. Difficulty now scales the monthly Attention grant
(24 / 20 / 16) rather than a per-turn cap. Removing the grant step is
RNG-safe -- it drew nothing from `state.rng`, so recorded replay streams are
unchanged.

**(e) 2-way founder hours shipped as the floor**, ahead of the 4-way split
ruled in (c). Every Attention spend is **PLANNING** (planner mind: queuing
strategic work, direction, approvals) or **OPERATING** (presence: response
windows, hiring loop, travel, interviews). Typed pools are **additive
accounting over the authoritative scalar** -- the shape N2 used for typed
reputation -- so `attention_total`/`attention_spent` stay authoritative and
every caller that only knows the aggregate still works. **Overflow is
asymmetric**: operating may eat planning hours (a crisis costs you the month
you meant to spend thinking), planning may never eat operating (you cannot
retroactively have been in the room). The 4-way split subdivides these two
in a later lane; `GameActions.hour_type()` and `GameState._cost_hour_type()`
are the single points that lane changes.

This also closes the seam **#980** named: conference travel drains OPERATING
hours only, with overflow forbidden. Away costs operator presence, not
planner mind.

**(f) The crisp reserve is deliberately UNTYPED.** Gating `set_reserve` on
the operating pool was built, then reverted: the reserve is the emergency
channel, and an emergency is exactly where the type wall is allowed to break
(cannibalizing already lets operating overflow into planning). Capping the
pre-declared reserve at operating hours forbids at PLAN time what the
overflow rule permits at CRISIS time, and it silently truncated the implicit
end-of-month reserve #789's hiring flow depends on. Pinned by a test so the
call cannot be reverted silently.

**(g) `staff_rider` re-expressed.** The contractor action used to mint +2
into the founder pool, which point 1 forbids outright. It now grants +2
OPERATING hours for the month (point 6: ops/admin staff reduce the founder-
price of routine work -- bought presence). It cannot buy planner mind.

**Balance is knowingly disturbed** under the day's audacity ruling: the
planning pool is a real cap on strategic cards per month, and
`attention.planning_share` (0.6) is hand-set, not swept. Re-price with the
exploit-finder before the ADR's own review date.

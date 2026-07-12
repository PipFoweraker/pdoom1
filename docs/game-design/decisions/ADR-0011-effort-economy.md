# ADR-0011 — The effort economy: founder hours, staff lanes, manager compression

- **Status:** ACCEPTED (shape); researcher archetype roster content owed (DQ-15)
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 2 (issue #596)

## Context

Current build: one global AP pool, spent instantly; staff add to the pool; researchers
are single-function; banking exists but does nothing. The sweep's diagnosis in mechanism
terms: one fungible currency + state-independent payoffs ⇒ constant-policy argmax
(`safety_lean`) dominates. Pip's rulings across beats 1–2: banking is dead (ADR-0009);
*"I have never been around unassigned workers before, because there's always been a
backlog"*; *"each new employee is kinda cutting down the time I need to do other
things"*; managers *"stop employees from annoying me with employee things."*

## Decision

1. **No global AP pool.** The pool illusion dies; staff never add founder AP.
2. **Founder hours** (sacred, roughly fixed per month — canon since ADR-0008): spent on
   **doors** (stakeholder face-time; which rooms you're in locks strategic paths),
   **approvals** (hires, direction rulings — "approve this salary," not paperwork
   clicks), **audits** (skip-level ground-truthing), and **reserve** (instant-speed
   firefighting, ADR-0009).
3. **Staff effort is per-person**, assigned at plan speed to workstreams from a backlog.
   **Idle staff don't exist; unmanaged staff do** — unassigned researchers self-direct
   per their agenda (whose ordering of the backlog wins?).
4. **Workstreams** run multi-month and produce artifacts (papers, systems, campaigns) —
   ADR-0009's no-instant-strategy rule, cashed out.
5. **Managers are interrupt shields with agenda riders:** they absorb their team's class
   of response windows (ADR-0009 economy), compress the plan screen (team → allocation
   + standing policy; members visually housed under the manager), and report upward via
   a **Celine's-law channel** — an inward SA channel with fidelity loss. The sim never
   lies; *characters do*. Skip-level audits (founder hours) re-ground truth. Folds
   ADR-0008's deferred inward-SA into existing SA machinery.
6. **Ops/admin staff reduce the founder-price of routine actions** and automate whole
   classes over time (endpoint: 2037 vignette's "payroll is automated").
7. **The dual-use lane is priced:** capabilities work pays money/compute/hype and bills
   doom (with ADR-0010's typed attention: accel VCs fund reckless success).
8. **Researcher model (shape):** *lane preference* (fictionalized real agendas — e.g.
   interpretability, evals, theory/agent-foundations, governance) × *appetites* (compute,
   prestige/first-author, mentees, money, mission purity — **promises made to retain
   staff are ledger entries**) × rare *quirk riders* (philosophical stances, secret
   successionist — an exposure-event genre reusing ADR-0003 machinery, not a lane).

## Beacons served / violated

- **Rams #10:** managers reuse the window economy + SA channels; quirks reuse exposure
  events; banking deleted; no new player-facing currency — typed effort is a *split* of
  an existing one.
- **MaRo Interaction:** typed lanes force a portfolio; with ADR-0010, the constant
  policy is structurally unavailable, not merely under-rewarded.
- **Honest:** "nobody wants to bring the boss bad news" — late-discovered doom via rosy
  reporting mirrors the real failure mode.

## Interaction contract

Reads/writes: **response windows** (ADR-0009 — manager value denominated there),
**SA** (inward channel, fidelity, audits), **Liability Ledger** (agenda riders, retention
promises, dual-use bills), **reputation** (per-person, ADR-0010 — hires are reputation
seeds who recruit juniors), **replay/exploit-finder** (assignment policies join the
policy space).

## Rejected alternatives

- **Global pool with staff as AP-adders:** sweep-proven degenerate; also violates
  founder-hours canon.
- **Idle unassigned staff:** no such thing ("there's always a backlog").
- **Managers as output multipliers:** rejected — their value is founder-attention
  arbitrage, not throughput.
- **Soft reserve fallback:** already rejected in ADR-0009.

## Consequences / open questions

- **DQ-15:** researcher archetype roster — Pip to author 3–5 vignette-style archetypes
  (lane / unmanaged drift / appetite / optional quirk).
- Plan-screen redesign: assignment UI, manager housing, team-satisfaction report
  replacing per-member detail under management.
- Retention/morale stays minimal v1: appetites bite through promises (ledger) and
  departure riders, not a mood sim (ADR-0008 register: "bother," not HR gravity).
- Sweep target: a managed portfolio must beat every constant line; new bot policy axes
  (assignment + response + publish/socialize).
- Balance seam: founder-hour prices for doors/audits/approvals are the new tuning
  surface — they set the whole game's attention economy.

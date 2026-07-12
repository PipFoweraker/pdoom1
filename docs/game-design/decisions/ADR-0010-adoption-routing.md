# ADR-0010 — Adoption routing (soft-with-teeth): doom bends where work is adopted

- **Status:** ACCEPTED
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 2 (issue #596 root cause)

## Context

The exploit sweep's dominant line (`safety_lean`, basement safety-spam, median 37 turns
vs 7 for passive) exists because safety research bends doom **directly, privately, and
state-independently** — papers are decorative, conferences float disconnected. Pip's
paper taxonomy (this session): papers raise awareness, build the *writer's* reputation,
speed follow-on work, and get **adopted** — into government policy or frontier-lab
practice, including rivals'. Pip's normative ground, verbatim:

> *"people voluntarily adopting good actions will generate the space for better actions
> to come about, and this is how small and middle power players can affect things —
> norm and market setting"*

## Decision

**Soft-with-teeth routing:**

1. **Your own lab's doom contribution is basement-fixable.** Private safety work makes
   *your* lab safer, no adoption required. (Honest: you really can secure your own shop
   in private.)
2. **World/rival doom — the majority share (#562 rival scaling) — bends only through
   adoption:** research → paper → socialization (conferences, summits, direct
   stakeholder work) → adoption by labs and/or governments → doom bends. Unadopted
   world-facing research is a PDF.
3. **Reputation is per-person and per-org**, and attention is *typed*: safety successes
   attract interviews/grants/safety applicants; reckless capability moves attract accel
   VC money. Both directions are priced, neither is forbidden (the dual-use temptation
   is a design feature — see DESIGN_PHILOSOPHY, tension/tradeoffs).
4. Papers additionally speed follow-on work (tech-tree effect) and unlock mitigations.
5. **Event-horizon guardrail (lore):** the player's influence over other labs becomes
   substantial mostly *after* the run crosses the real-world event horizon — the game
   never implies real labs do the truly weird late-game stuff. (WORLD_AND_LORE.)

## Beacons served / violated

- **Rams #6 (honest):** the mechanic *is* Pip's real-world theory of change — norm and
  market setting by small/middle powers. Structure, not numbers; don't patch it for
  freshness (per the philosophy doc's load-bearing-structure rule).
- **MaRo Interaction:** research, reputation, conferences, and rivals now interlock;
  the social layer stops being decoration.
- Kills the dominant line **by construction**: basement-spam can't reach the dominant
  doom mass, so no payoff buff to safety-spam can restore it.

## Interaction contract

Reads/writes: **rival-doom pipeline** (#562 — rival share must dominate the integral
for teeth), **reputation** (per-person + per-org, new read/write), **conference/travel**
(promoted from flavor to load-bearing — the socialization step), **Liability Ledger**
(funding-with-strings, promises), **SA** (awareness essays raise it), **exploit-finder**
(new sweep target: publish-and-socialize must beat basement-spam).

## Rejected alternatives

- **Strong routing** (ALL safety value requires adoption): less honest — you can
  privately secure your own lab — and it needlessly breaks the existing own-lab safety
  architecture.
- **Status quo** (direct doom reduction): sweep-proven degenerate.

## Consequences / open questions

- Safety research splits: **internal hardening** (own-lab, private) vs **publishable
  agendas** (world-facing, adoption-routed).
- Conference/travel design (agenda item 4) is promoted: it's now the mandatory middle of
  the value chain, not garnish.
- Balance verification target for the next sweep: rival/world doom share must dominate
  the integral, or the teeth are cosmetic.
- Adoption *by whom* needs a counterparty model — overlaps ADR-0007 alliances and DQ-9
  receivables; design together.

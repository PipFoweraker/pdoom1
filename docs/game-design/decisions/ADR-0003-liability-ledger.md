# ADR-0003 — The Liability Ledger (two-sided): every mitigation is a loan

- **Status:** ACCEPTED as design; build first among the new systems
- **Date:** 2026-07-04
- **Session:** Fable workshop #1

## Context

Pip's generative image (preserved because the chain *is* the idea): *"like taking out a
credit card to save the mortgage, then taking a job as a lobbyist to pay off the credit
card, then lobbying to weaken financial regulation on AI firms which then leads to an
increase in AI driven fraud which then funds Antagonist_Lab"* — plus *"the first waves of
doom might be easier to beat down but require some kinds of sacrifice where you get
diminishing returns."*

Doom arrives in waves (ADR-0005). Each wave can be beaten down, but every suppression
lever generates a liability that feeds a later wave or weakens a later lever. The
adversary "adapts" — not via a difficulty slider, but because **the player's own ledger
is the difficulty curve.**

## Decision

One system — a ledger of trades that pay now and bill later — absorbing four issue-list
items that were previously separate: loan repayment, funding-with-strings, the
governance→bribery→blackmail cascade, and reputation-as-spendable.

**Entry shape (design-level, not code):** a liability has a *source* (what trade created
it), a *currency* (what it bills in: money, reputation, governance, doom), a *fuse*
(when it bills), an *interest profile* (how it grows), a *secrecy flag*, and a *side*.

**The ledger is two-sided:**

- **Payables** — what you owe. Debt service, strings on funding, corroded governance,
  secrets that can be exposed.
- **Receivables** — favors and pledges owed *to you*, held **per-actor**. **Influence is
  not a resource** (decided by Pip): there is no global influence number; there is
  leverage over *this* lab, a favor owed by *that* actor. Reputation remains the only
  global social currency. Receivables carry **counterparty risk** — a pledge is not a
  vote until cast (see ADR-0007).

**Secrecy and exposure:** entries flagged `secret` can be *exposed* by rival actions or
scheduled causes; exposure converts them into reputation/governance damage or a
blackmail offer — which is itself a new liability, continuing the chain. Blackmail is
ledger **content** (one event type), not a system.

**Desperation levers are the catch-up system:** within-run recovery options exist but
are priced as desperation, never offered as rubber-banding — every claw-back trades a
visible resource for a corrosive liability (the payroll coinflip → governance ↓ →
bribery vulnerability → blackmail chain). Catch-up and tragedy-generation are the same
mechanism. There is no other catch-up: runs are short-median, and the next run is the
catch-up.

**Staff ride on this system:** staff are AP-leverage with liability riders (ADR-0008) —
a disgruntled ex-researcher is a secret entry, a whistleblower is an exposure event, a
manager is insurance that shortens fuses on people-liabilities.

## What this system delivers structurally

- **The exponential turn ladder:** turn 15 is hard because of everything you did to
  reach turn 12 — deep runs are exactly as heroic as the PoE-badge philosophy needs.
- **Death attributability:** your killer is traceable through your own ledger — "this is
  the bill for turn 2," manufactured structurally rather than scripted.
- **Skill expression:** debt portfolio selection and sequencing — which liabilities you
  take, in what order, which you repay before the fuse burns. Triage-in-time.
- **The mortality guarantee candidate** (ADR-0002): compounding interest ensures no
  immortal runs.

## Boundary conditions (the failure modes to design against)

- If every fix breeds a bigger problem, the game degenerates into an inevitability
  queue. Liabilities must be **heterogeneous**: different fuses, different currencies,
  some repayable, some only transformable.
- A disciplined player must genuinely be able to run a **lean ledger at the cost of
  tempo** — the clean-hands path must exist even if it rarely tops boards.
- **No parallel economy.** The ledger reads/writes existing resources (money,
  reputation, governance, AP, doom) only. If an implementation needs a new player-facing
  currency, it has left the design.

## Beacons served / violated

- Serves: MaRo Interaction (reads/writes ≥4 existing resources), Inertia (fuses are
  clocks), Surprise (exposures, defections), Catch-Up (desperation levers). Rams #10
  (four issues, one mechanic).
- At risk: Rams #5 (ledger UI must not become a spreadsheet — visibility of your own
  ledger can itself be partial; see inward-SA deferral, ADR-0008).

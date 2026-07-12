# ADR-0013 — Financing instruments & the cost-of-debt engine

- **Status:** ACCEPTED (shape; numbers owed to the sweep)
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 3 (agenda items 3+4 merged)

## Context

Flat 25%/turn loans were a day-cadence artifact (ADR-0009) and a placeholder (DQ-8).
With DEFER routing through the Ledger (ADR-0009/0012), loan terms and defer
carrying-costs need one pricing engine, or the two halves of the flagship drift apart.

## Decision

**One pricing engine for all liabilities** (loans, defers, funding-with-strings),
taking these arguments at Pip's weights:

- **Org type — major.** Set at character/org creation; ties directly to building
  early-game agency into setup (DQ-4 adjacent; "the opening is a commitment device").
- **Counterparty / stakeholder risk & interest — major.** Who you owe changes what it
  costs (VC, government, philanthropist, rival's proxy — counterparty dread lives here,
  ADR-0007 register).
- **Reputation — typed.** Safety-rep and finance-rep price debt *differently*, and
  reputation affects grants, equity raises, and loans through different channels
  (ADR-0010 typed attention, applied to capital).
- **Hype — scoped to the raise's purpose.** Fundraising is purpose-tagged and the hype
  cycle prices the purpose; **no internal earmarked budgets** (rejected as fiddly —
  granularity lives in the raise, not the spend).
- **Existing ledger load — minor direct**, mostly indirect through reputation and
  counterparty appetite.

**Instruments beyond debt** (all Ledger objects):

- **Equity** (for-profits): early capital comes on good terms but eats equity — and
  equity is a more valuable bargaining chip mid/late game. Selling cheap early is a
  priced regret.
- **Board seats** (nonprofits' equity-approximate): cash for seats that *curtail the
  player's options in voting mechanisms* (hard dependency on DQ-7 governance design).
- **Research-agenda narrowing**: cash for scope — the funder's strings constrain which
  workstreams are legal.

**The early-game curve, stated as design intent:** pure philanthropy is starved — the
first thing players feel is the difficulty of getting enough cash in the door from any
purely philanthropic approach. Trading (equity, agenda, capabilities work) buys speed —
reputation and publication pipelines spike faster — and bills against **late-game
optionality** (the capabilities route compromises later government/political
influence). Financing is "every mitigation is a loan" applied to itself.

## Beacons served / violated

- **Rams #6:** an honest cost-of-capital function — org type, counterparty, reputation,
  purpose — instead of a flat magic number.
- **MaRo Interaction:** capital now interlocks with reputation (typed), hype, governance
  (board seats), and the rival race.
- The PoE exponential-difficulty ladder gets its mechanism: compounding early trades
  *are* the difficulty curve (ADR-0003 thesis, now with a pricing engine).

## Interaction contract

Reads/writes: **Ledger** (all instruments are entries), **reputation** (typed, both
directions), **hype cycle** (purpose pricing), **char/org creation** (org type; DQ-4),
**governance/voting** (board seats curtail votes — DQ-7 now has a customer),
**rival pipeline** (funding starvation cascade, ADR-0012).

## Rejected alternatives

- **Flat rates:** day-cadence placeholder, dies with ADR-0009.
- **Internal earmarked budgets** (money "for" things): fiddly; purpose granularity
  lives in the raise.
- **Separate pricing for loans vs defers:** one engine or the flagship forks.

## Consequences / open questions

- **Numbers owed to the sweep** (DQ-8): rate curves per org type/counterparty, equity
  dilution schedule, board-seat prices. Instrument root-cause death attribution first
  (ADR-0012) or tuning is blind.
- **DQ-7 (governance)** is now load-bearing twice over: the board-seat instrument needs
  the voting mechanics it curtails.
- Equity model granularity (cap table vs a single dilution scalar) — start scalar
  (Rams #10), upgrade only if bargaining-chip play demands it.
- Character/org setup design (org type as the pricing engine's biggest input) — feeds
  the early-game agency thread.

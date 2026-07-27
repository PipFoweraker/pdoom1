# SEED: Nonprofit / For-profit -- the real divergence

> Status: SEED (options for Pip to rule on, Wed 2026-07-29 W-3b). NOT ratified.
> Written 2026-07-27 as the design half of the EARLYGAME lane, against Pip's
> ruling: "Agree I want 1 or 2 more layers of depth for non-profit, for-profit."
> Feeds #811 agenda item 1. `[PIP]` = verbatim; `[INFERRED]` = Claude's read;
> everything else is grounded in code greps of `godot/scripts/core` +
> `godot/data/balance/defaults.json` on 2026-07-27.
>
> The ask is ONE OR TWO more layers, not a whole subsystem. Each option below is
> sized so a single one is a day of work, and every option names what it costs.

---

## 0. What the fork is TODAY (verified 2026-07-27)

`GameState.org_type` is a real field ("nonprofit" | "for_profit", game_state.gd),
set at org creation and read by exactly one consumer:
`FinanceEngine.context_from_state()`. It does two things and nothing else:

| Existing fork | Where | Size of the effect |
|---|---|---|
| Interest-rate multiplier | `financing.org_factors` (defaults.json): nonprofit 1.0, for_profit 0.9, academic 1.05 | for-profit borrows ~10% cheaper. Invisible without a spreadsheet. |
| One instrument gate | `vc_equity.availability.org_types: ["for_profit"]` | a nonprofit never sees the equity offer. This is the ONLY qualitative fork that exists. |

That is the "pricing-only split" #811 names as Friday's ship. The honest
assessment: **a 10% rate difference is not a decision, it is a rounding error**,
and one hidden menu item is a fork the player may never notice they were on the
wrong side of. The instrument gate, though, is the shape worth extending -- the
machinery (`availability.org_types`, `org_factors`, `counterparty_factors`) is
already general, so every option in Layer A below is DATA, not code.

Constraint from #791's philosophy that governs all of this: **forks must bite
EARLY and grow** ("first unlocks should have small immediate strategic impact,
growing over time -- switching costs"). A divergence that only matters at turn 60
is not a fork, it is flavour text.

---

## 1. Layer A -- funding ACCESS asymmetry (beyond price)

The thesis: the two org forms should not have the same doors with different price
tags. They should have DIFFERENT DOORS.

### A1. Instrument availability fork (data only)

Split `financing.instruments` availability by org type properly, not just for
`vc_equity`:

| Instrument | nonprofit | for_profit |
|---|---|---|
| philanthropy (gift, scarce) | available | unavailable |
| funding_strings (agenda riders) | available, common | available, rare |
| bank_loan | available, priced worse | available, priced better |
| vc_equity | unavailable (today's gate) | available above hype/rep floor |

- **Cost**: ~an hour. Pure `defaults.json` edits on shipped machinery.
- **Bites early**: yes -- the very first `seek_financing` shows a different menu.
- **Risk**: nonprofit's menu could end up strictly worse, i.e. a trap choice.
  Mitigation is A2 or B1, which give nonprofit something for-profit cannot buy.
- **Sweep hook**: no bot policy should show one org type dominating on median
  survival.

### A2. Funding CADENCE fork (the one Claude would ship) [INFERRED]

Same money, different clock -- reuses ADR-0009 durations, which already exist for
the hiring pipeline's jobs:

- **Nonprofit money is LUMPY and SLOW.** A grant is applied for now and resolves
  in months; when it lands it is large and restricted. You plan around a cliff.
- **For-profit money is FAST and DILUTIVE.** A round closes in weeks, on worse
  terms if you are in a hurry, and each one costs a slice of control.

- **Cost**: ~a day. The duration-job pattern is `hiring_pipeline.jobs` verbatim;
  the offer expiry is `FinanceEngine.offer_live`.
- **Bites early**: yes, and it changes HOW YOU PLAN, not just what you can afford
  -- which is the crisp-parts test (#811: "suffer-hardness lives in the DECISIONS").
- **Risk**: the lumpy path can dead-end a nonprofit run before the 6-month floor.
  Guard: keep the tier-0/tier-1 office spend small enough that a missed grant is a
  setback, not a death (which the office lane's $10k-46k band already respects).

### A3. Strings-shape fork

Both forms get money with a cost, but the COST IS A DIFFERENT CURRENCY: nonprofit
money bills in **governance** (agenda narrowing -- funders tell you what to work
on); for-profit money bills in **equity + board seats** (control loss). Both
already mint as ledger riders in `FinanceEngine.accept_offer` (`agenda_narrowing`,
`equity_dilution`, `board_seat` -- currently inert standing entries).

- **Cost**: low to author, HIGH to make real -- the riders are inert today. Making
  a board seat or an agenda narrowing actually constrain play is its own lane
  (DQ-7), and that is the whole cost.
- **Bites early**: only if the riders do something, which they do not yet.
- [INFERRED] Recommend as the SECOND layer, or defer until DQ-7 schedules.

---

## 2. Layer B -- reputation DYNAMICS asymmetry

ADR-0010's typed reputation (`safety_rep` / `finance_rep`) is already the pricing
input; today both org types convert it identically (`_rep_for_channel` picks a
channel per instrument, not per org). That is the cheapest untapped asymmetry in
the codebase.

### B1. Conversion-rate fork

Nonprofit converts SAFETY reputation into funding efficiently and finance
reputation barely at all; for-profit is the mirror. Concretely: make
`rep_rate_relief` and the deposit/principal relief org-scaled.

- **Cost**: ~half a day (one coefficient lookup becomes org-keyed).
- **Bites early**: yes -- it changes which actions are worth taking in the first
  ten turns (publish vs raise), which is a real strategy fork.
- **Risk**: it can read as invisible, because it is still a number under a number.
  Pair with B3, which is legible.

### B3. Hype asymmetry (the legible one, and it is already wired) [INFERRED]

The EARLYGAME build just promoted `hype` to a real GameState field, written by the
new `scout_shitpost` action and read by `FinanceEngine.is_available` (vc_equity
gates on `min_hype: 25`). The asymmetry writes itself:

- **For-profit: hype is fuel.** ~7 shitposts opens the equity door. Being loud is
  how you get funded.
- **Nonprofit: hype is a liability.** The people who fund safety nonprofits read
  the replies. Hype above a threshold should DEGRADE nonprofit funding access
  (raise the philanthropy/grant floor, or price the strings worse).

- **Cost**: ~an hour, on top of what shipped today. One availability term plus one
  org-keyed sign flip.
- **Bites early**: extremely -- scouting is the FIRST thing the cold-open hands the
  player (the new onboarding handoff), so the very first scouting choice already
  means two different things depending on the org form chosen at creation.
- **Why Claude likes this one**: it is a single mechanic that makes the same button
  good for one org and bad for the other. No new system, no new number on screen,
  and it teaches the fork by consequence instead of by tooltip.

### B2. Scandal-damage fork

A scandal (rival exposure, secret liability surfacing) costs a nonprofit
mission legitimacy (governance floor -- the whole asset) and costs a for-profit
cost-of-capital (rate penalty). Cheap to author on the existing cause/exposure
paths; bites only when a scandal fires, so it is LATE-biting by nature. [INFERRED]
Recommend as flavour on top of whichever layer ships, not as a layer itself.

---

## 3. Layer C -- endgame POSTURE (design now, build later)

Not a candidate for this epoch; recorded so Friday's pricing-only split does not
paint into a corner.

- **C1. Terminal states differ.** For-profit gets ACQUISITION as a legal terminal
  state (you exit; someone else inherits your doom contribution). Nonprofit has no
  exit -- it either persists or starves. This is the sharpest possible late fork
  and it costs a scoring conversation (ADR-0002 lexicographic score), so it is a
  workshop topic, not a build.
- **C2. Late-game constraint differs.** Nonprofit late runway is grant-dependent
  (starvation risk); for-profit can always raise but the board can remove you
  (agency loss). Both are "you lose control of the thing you built", in opposite
  directions.
- **C3. Violence/endgame texture** -- see SEED_ENDGAME_AND_VIOLENCE.md; the two
  forms should meet the arrival of violence differently (legitimacy vs assets).

**Corner-avoidance rule for Friday**: nothing shipping Friday should assume the
two org types share a terminal state or a scoring shape. Keep the org_type read
out of scoring entirely for now -- it is currently absent from scoring, and that
is the right default.

---

## 4. Claude's recommendation (Pip rules Wednesday)

**Ship two layers: A2 (cadence) + B3 (hype asymmetry).**

Reasoning chain, negative case first: A1 alone risks a strictly-worse nonprofit
menu (a trap choice, which violates the no-early-loss principle); A3 and B2 depend
on machinery that is inert today (the riders, the exposure paths), so they would
be promises rather than mechanics -- exactly the silent-promise failure the text
audit caught; C is a scoring conversation, not a build. B1 is cheap and real but
invisible. What survives that filter is A2, which changes how each form PLANS, and
B3, which is nearly free because today's build already added the field and the
action that writes it, and which bites at the earliest possible moment (the first
scouting choice out of the cold-open).

Together they answer "what is actually different about being a nonprofit?" with
two sentences a player can say out loud after one run: *"my money arrives in
lumps, months late"* and *"being loud online makes my funders trust me less."*

## 5. Questions for Pip

1. One layer or two? (A2 is a day; A2+B3 is a day plus an hour.)
2. Does a nonprofit run need a door for-profit does not have -- i.e. is
   philanthropy nonprofit-EXCLUSIVE, or just nonprofit-cheaper?
3. Hype for a nonprofit: actively harmful (Claude's read) or merely useless?
   Harmful is the stronger fork and the crueller one.
4. Is ACQUISITION (C1) a terminal state you want at all, or does every run end in
   the same place?
5. Should `academic` (the third `org_factors` key, already in defaults.json and
   currently unreachable) become a real third org form, or be deleted?

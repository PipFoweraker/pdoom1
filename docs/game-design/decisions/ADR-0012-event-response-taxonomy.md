# ADR-0012 — Event response taxonomy: un-snoozable, deferrable, expiring

- **Status:** ACCEPTED
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, beat 3 (ledger bite)

## Context

ADR-0009 gave every response window a DEFER option routing through the Ledger. Left
uniform, DEFER becomes a universal snooze button and the reserve-vs-greed gamble loses
its sting (why hold reserve when everything waits?). Pip's ruling drew the taxonomy from
real-world texture: some things wait expensively, some don't wait at all, and some
correctly get no response.

## Decision

Four event classes:

1. **Un-snoozable** — the window closes this turn: HANDLE (reserve or cannibalize) or
   IGNORE at list price; DEFER is not for sale. Pip's classes: **movement of people
   across state borders; emergency services; threat of legal action; scenario/story
   events.** This class is what keeps reserve worth holding.
2. **Deferrable** — DEFER mints a Ledger entry with a carrying cost priced per-event by
   the ADR-0013 engine.
3. **Standing offers** — open for N turns, then expire to a natural no-engage (possible
   reputation loss where a response was expected). Expiry mints **no** ledger entry —
   the offer simply evaporates.
4. **No-action-correct** — some events legitimately deserve nothing. Taking no action
   is not always a mistake, and the game must not punish it uniformly.

**The infinite to-do list is diegetic.** Standing offers and deferrals may accumulate
past what the UI foregrounds; items falling out of visibility is a *real phenomenon
being modeled*, not a UI bug. Pip, verbatim: *"Doom Arrives With Your To-Do List Being
Infinitely Long Still is a real possibility that I'm not shy of playing into."*

**The ledger's kill path is a cascade, not a death screen.** Entries are called due;
if you can't pay, consequences execute: unpaid staff work on for a period suffering
damage → leave → work lost/abandoned → severe reputation penalties → credit lockout →
funding starvation → rival pulls ahead → doom spikes. The ledger doesn't kill you — it
feeds you to the thing that does, legibly. Register: **tragedy** ("I saw it coming"),
which requires the player to have had a *real chance* to raise money in the interim —
hence:

**Fundraising has lead time.** Money lands turns after the raise begins (ADR-0009's
duration rule applied to cash). Core tension named: **spiky-in, smooth-out** cash flow,
with cash as the game's most fungible resource.

## Beacons served / violated

- **Rams #6 (honest):** the taxonomy mirrors real deferability; the infinite backlog is
  played straight instead of hidden.
- **Rams #10:** standing offers and no-action events need no ledger machinery at all;
  only true deferrals touch the flagship.
- **MaRo Interaction:** un-snoozables make reserve (ADR-0009) and event content
  interlock; the cascade chains ledger → staff → reputation → funding → rival → doom.

## Interaction contract

Reads/writes: **response windows** (ADR-0009), **Ledger** (defer intake + called-due
cascade), **reputation** (expiry losses, default penalties), **staff** (unpaid-work
damage, departures, abandoned work), **rival pipeline** (funding starvation → rival
lead), **ADR-0013 pricing engine** (carrying costs).

## Rejected alternatives

- **Universal DEFER** (everything snoozable): kills the reserve gamble.
- **Ledger death as its own game-over type:** rejected — defaults cascade into the
  existing doom/cash deaths through legible intermediate wreckage.
- **Expiry-as-liability** (expired offers mint entries): rejected — evaporation is the
  honest model for most offers, and the ledger should carry *chosen* debts.

## Consequences / open questions

- **Event content schema:** class field, expiry N, response-expected flag, carrying-cost
  hook.
- **Exploit-finder must attribute deaths to root-cause chains** — a doom death
  downstream of a default is a *ledger* death for balance accounting; "dies of doom"
  currently hides the cascade. Instrument before tuning.
- **UI (backlog'd):** per-resource per-turn delta indicators; event-log improvement —
  the one human ledger-death specimen (turn 23) was low-resolution because the player
  couldn't see the spiral; legibility work is what makes future specimens usable.
- Class shares per era (how much of the event stream is un-snoozable) — a tuning
  surface, sweep-driven.

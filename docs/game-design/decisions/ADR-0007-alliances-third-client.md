# ADR-0007 — Alliances: the third client of Ledger + SA (treaty = shared liability + shared sight)

- **Status:** ACCEPTED as design; build **third**, strictly after ADR-0003 and ADR-0004
- **Date:** 2026-07-04
- **Session:** Fable workshop #1

## Context — why the original deferral was wrong in kind

The pre-workshop triage parked alliances/voting as a "big isolated system." Pip's own
purpose statement convicts that: *"there isn't really consensus anywhere on the best
approaches on how to deal with AI risk, other than try to coordinate pause / stop
functions."* Coordination is the one lever the real-world model endorses — and the
game's strategy space omitted it. For an artifact that teaches the way Civ teaches, a
game with no coordination mechanic quietly argues coordination doesn't exist. That is a
structural falsehood, not a missing feature. What was *right* in the deferral was
sequencing: alliances need almost no new machinery **because they are made of the other
two systems' parts.**

## Decision

**A treaty is a shared liability plus shared sight**: mutual ledger entries (obligations
with fuses; defection = the exposure event running in reverse) plus a mutual SA channel
(alliance-sight: slow, public, obligates you).

**Votes are scheduled causes** (ADR-0005): a treaty vote at turn X is visible terrain,
with more lead time if you've bought it (ADR-0004).

**The whip loop** — from Pip's House of Cards image: *"there are critical votes coming
up, and people are wavering. have you got them?"* Whipping a vote means spending money,
reputation, and favors to acquire **pledges** — receivables in the two-sided ledger
(ADR-0003). A pledge is not a vote until cast: receivables carry counterparty risk (a
lab under financial pressure wavers; a rival counter-whips; a scandal flips a
signatory). **Wavering is computed from counterparty state, never scripted** — author
causes, never outcomes: the vote result is simmed. "Have you got them?" is a *sight*
question about your own receivables, which gives alliance-sight a job only it can do and
passes the decision-flip test trivially (knowing who wavers changes whether you shore
up, buy a replacement vote, or write the treaty off).

**Influence is not a resource** (decided by Pip): no global influence stat — a fourth
currency would be the parallel-economy trap, and less thematic (leverage is over *this*
lab, *that* actor). Influence *is* the receivables column, per-actor. Reputation stays
global and public. Fallback on record if playtests show per-actor favors overwhelm
players: a global influence pool as the legibility compromise — build the honest version
first.

## Sequencing discipline (binding)

Built third, after the Ledger and outward SA, because it is assembled from their parts.
**The vote screen must not be built early because it is dramatic** — a vote UI without a
working ledger underneath is theater.

## Beacons

- MaRo Interaction: reads money, reputation, SA; writes doom (treaty effects) and the
  ledger both ways. Surprise: the defection you didn't see. Inertia: a looming vote is a
  clock inside the clock.
- Rams #10: not one new system — one new *column* (already in ADR-0003) plus one event
  genre.
- Flavor/thesis: this is where the game's real-world subject — coordination under
  mistrust — actually lives.

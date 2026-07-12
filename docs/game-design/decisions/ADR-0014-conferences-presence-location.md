# ADR-0014 — Conferences, presence, and minimal location

- **Status:** ACCEPTED (v1 shape; yields/numbers owed to the sweep)
- **Date:** 2026-07-12
- **Session:** Fable workshop #2, closing beat

## Context

ADR-0010 made socialization the mandatory middle of the research→adoption value chain
with no ruling on what attending *is*. Pip's rulings, this beat, with one ambition
flagged: *"Part of me wants to make a conference attendance subgame, that's how critical
I think these kinds of things are going to be for the game."* (Subgame parked; v1 is
attendance + yields.)

## Decision

1. **Conferences are scheduled world events on the seed timeline** (ADR-0005 schedule
   entries — the geopolitics-as-content pattern, reused). Annual majors announce ~9
   months ahead: plannable at plan speed, and opening theory can grow around known
   calendars. **Smaller/exclusive gatherings unlock behind contacts or safety
   reputation** — invitation-gated event stream.
2. **Founder attendance ≫ delegate attendance.** Founder pays founder-hours + travel
   cash and gets the full yield: meaningful options opened, first-degree connections,
   SA boosts. Delegates (a staff-month + travel cash) yield less but give coverage —
   the 2037 "5 delegates to 10 meetings" scarcity, seeded from turn one. Travel cash
   deliberately bites early (spiky cash flow, ADR-0012).
3. **Conferences are accelerants and discovery venues, not the adoption roll itself.**
   Adoption happens out in the world (ADR-0010); attendance *speeds* adoption of your
   published work, builds reputation mechanically faster (especially introductions),
   and **mints contacts-as-receivables** — the Ledger's friendly column gets its content
   source (DQ-9's customer).
4. **Discovery-by-presence.** You discover actors, alliances, and intentions by being
   where they are (the units-moving-on-the-map analog); news/newsletters are the
   cheaper, lower-fidelity discovery channel. Presence is effectively an SA channel
   flavor alongside espionage/alliance/media/research.
5. **Location exists minimally in v1:** HQ defaults American (park foreign legal-regime
   modeling); the player can substantially base teams overseas — cheaper hires, with
   different downstream influence/politics effects (mid/late-game payoff). Event schema
   carries `where` from day one.
6. **Ad-hoc meetings/opportunities stay instant-speed windows** (ADR-0009/0012), some
   gated by contacts/rep. (Pip's "book a longer trip for planned meetings" instinct is
   week-grain thinking — at month grain the trip is a plan allocation.)

## Beacons served / violated

- **MaRo Interaction:** conferences interlock papers (ADR-0010), reputation, SA,
  receivables, travel cash, and founder-hours — six systems, zero new currencies.
- **Rams #10:** accelerant not a new mechanic; schedule entries not a system; subgame
  parked; foreign law parked.
- **Rams #6:** this is how the field actually works — the hallway track is where
  adoption starts.

## Interaction contract

Reads/writes: **seed schedule** (ADR-0005 entries + 9-month announcements), **founder
hours** (ADR-0011), **cash** (travel), **reputation** (typed, per-person — delegate
yield should scale with the delegate's own reputation), **SA** (presence channel),
**Ledger receivables** (contacts; DQ-9), **adoption pipeline** (ADR-0010 accelerant).

## Rejected alternatives

- **Adoption rolls at the conference itself:** adoption lives in the world; conferences
  only accelerate it.
- **Full geo/legal modeling in v1:** parked; `where` field + overseas basing only.
- **Conference subgame in v1:** parked to backlog as a flagged ambition.

## Consequences / open questions

- Yield numbers, invitation thresholds, travel prices — sweep-tuned (after EE-8).
- Receivable/contact object format — design with DQ-9 + ADR-0007 counterparties.
- Delegate yield scaling with per-person reputation (hires as reputation seeds,
  ADR-0011) — natural, verify it doesn't make star-delegate spam dominant.
- Overseas-basing downstream effects (influence/politics) — mid/late-game content,
  design at workshop #3.

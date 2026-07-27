# ADR-0018 -- Render-only office doctrine: no spatial fact becomes a gameplay input

- **Status:** DRAFT (formal confirm at 2026-07-27 R3a block; review-by 2027-07-27)
- **Date:** 2026-07-27
- **Session:** R3a prep / docs lane

## Context

The office floor (`godot/scripts/ui/office_floor/office_sandbox.gd`) is a dev-tool
sandbox for placing props and previewing worker sprites on a 32px snap grid
(`GRID := 32.0`, `_snap_to_grid()`, `_cell_of()` at lines 52-58 and 874-893). It
already computes pixel coordinates, grid cells, and occupancy keys. Two spatial
build lanes were provisionally on Tuesday's plan: a first-class tile-grid
implementation and a camera/real-estate application of it to shipped gameplay.

`docs/game-design/OFFICE_ECONOMY_PROPOSAL.md` section 7 ("Out of scope") already
named the target precedent: *"Per-desk/per-room placement, pathfinding gameplay --
the office floor stays a RENDER surface, not a sim (Rams #10)."* That line covered
the office-economy proposal specifically. This ADR generalizes it into standing
doctrine for the whole engine, and rules explicitly on the sandbox's grid, on
click-driven interaction, and on Wednesday's decorating math.

Pip, 2026-07-27 ~0950 (verbatim intent): *"No spatial fact will ever become a
gameplay input."*

The structural precedent is the 2026-07-25 modal soft-locks: bugs caused by a
second, UI-side notion of state drifting out of sync with the sim's actual state
(a dual-source-of-truth failure class -- two stores of "what is true," reconciled
imperfectly, produce exactly the class of bug where the screen and the sim
disagree and the player gets stuck). A spatial layer that fed gameplay would
recreate the same shape of risk at a larger scale: coordinates as a second,
render-side state store that the sim would have to trust.

## Decision

The office view is a render surface driven one-way from the deterministic sim.
**The sim owns counts and quantities; the render owns coordinates.**

**Amendment 2026-07-27 (Pip ruling 1143 + facilitator reweight, "a(3)-lite"):**
a first-class integer grid type -- `Vector2i` col/row addressing, footprint
occupancy, snap -- **is approved as render-layer infrastructure.** Its
consumers are prop placement, decorating render, walk theatre, and
click-targets. This is chosen over both rejected options it replaces:
formalizing the sandbox's ad hoc string-keyed 32px snap (that debt is retired
by this grid superseding it), and the original tier-integers-only clause
(overturned 2026-07-27 by Pip: *"having the sim be a useful part of the game is
growing on me and this gives me room downstream to explore with less technical
debt"*). Scope guard, non-negotiable: this grid is explicitly **not** a
pathfinding or simulation grid; nothing sim-side may read cell state -- the
doctrine's arrow rule (sim owns counts and quantities; the render owns
coordinates) governs it fully, unchanged. Tile addressing for anything
sim-facing remains **tier integers only** (ADR-0014's presence/location tiers,
office-era tiers) -- never (x, y) coordinates, never grid cells, never pixel
positions, as sim-side input.

### Three riders (part of the ruling)

**(a) Review clause.** This decision is re-reviewed within one year, by
**2027-07-27**, as part of standing decision reviews. If office gameplay has by
then out-grown tier integers, that review is where a spatial model gets
re-litigated -- not an ad hoc exception beforehand.

**(b) Render-local cosmetic interactions are unrestricted.** Clicking a coffee
pot and having it boil, a worker idling into a new pose, ambient office flavor --
none of this touches the sim. This is **not an exception** to the doctrine; it is
**outside its scope**. The doctrine governs the input -> sim boundary. A
render-local effect is input -> render only: no sim read, no sim write, nothing
serialized, nothing replayed. If an interaction never crosses into the sim, this
ADR has nothing to say about it.

**(c) Click-the-render as a command surface is permitted, under the
entity-ID invariant.** A click on a rendered object MAY dispatch a sim action --
but the action serializes as `(action, entity_id)`, never as coordinates.
Replays record entity-scoped actions, not click positions. Every render-click
command must also have a non-spatial path (an action menu reachable without
touching the render at all), so the render is always a convenience input method,
never the only way to issue the command.

Two named rot modes are forbidden under this rider, because both smuggle a
spatial fact back into gameplay through the side door:

1. **Clickability conditioned on placement** -- e.g. "a worker is only
   assignable when their sprite is near a desk." The moment eligibility depends
   on rendered position, position has become a gameplay input.
2. **Command availability conditioned on placement** -- e.g. "the coffee pot is
   only usable if it has been placed in the kitchen." Same failure: a spatial
   fact (which room a prop's sprite sits in) is gating a sim action.

Eligibility and availability may depend only on sim-owned state (tier,
ownership, unlocked/owned flags, resource costs) -- never on where something is
drawn.

## Beacons served / violated

- **Rams #10 (as little design as possible):** hardens the office-economy
  proposal's own stated precedent (section 7) into an engine-wide rule instead of
  letting a spatial-gameplay system grow by increment. Directly cancels two
  planned build lanes rather than building them and pruning later.
- **Rams #6 (honest):** the entity-ID invariant keeps replays and the leaderboard
  honest about what actually happened (an action on an entity), instead of
  encoding an incidental rendering detail (where a sprite happened to be) as if
  it were part of the game's history.
- Cost: the office floor's affordances are permanently render-flavor-only;
  future proposals wanting spatial gameplay (base-building, pathing puzzles)
  are foreclosed by default and must clear the 2027-07-27 review, not tack on
  quietly.

## Interaction contract

- **Reads:** `godot/scripts/ui/office_floor/office_sandbox.gd` (the dev-tool grid
  this ADR declines to promote), `docs/game-design/OFFICE_ECONOMY_PROPOSAL.md`
  section 7 (the precedent this ADR generalizes), ADR-0006 (replay/versioning --
  entity-scoped actions must stay replayable under its format), ADR-0014
  (presence/location tiers -- the only spatial addressing that ships).
- **Writes:** no engine code (doctrine-only ADR). Constrains future writes to
  `godot/scripts/ui/office_floor/**`, any future decorating/placement system, and
  the action-serialization format (must stay `(action, entity_id)` for any
  render-click command).

## Rejected alternatives

- **Promote the sandbox's existing ad hoc string-keyed 32px snap-hack to
  first-class, as-is.** Rejected: that hack was a dev-preview convenience,
  not a designed type, and formalizing it unchanged would carry its
  string-keyed debt into production. This is distinct from what the a(3)-lite
  amendment approves -- a fresh `Vector2i` grid type that replaces and retires
  the hack, not the hack itself promoted wholesale.
- **Camera/real-estate application built on that grid.** Rejected for the same
  reason and on the same day -- it is downstream of the grid becoming
  first-class, so it falls with it.
- **Allow click-to-command without the entity-ID invariant (record raw click
  coordinates in the action/replay).** Rejected: coordinates in the replay log
  make the render surface part of the game's deterministic history, and any
  future re-layout of the office view would silently change what old replays
  mean. Entity IDs are layout-independent by construction.
- **Gate room-scoped flavor text or clickability on placement ("in the
  kitchen").** Rejected as one of the two named rot modes -- flavor is fine,
  but the moment placement gates a *command* or *eligibility*, position has
  become a gameplay input through the side door.
- **No review clause (treat this as permanent).** Rejected: Pip's ruling was
  explicitly scoped to be re-examined in a year, not enshrined as unchangeable
  canon; a hardcoded review-by date keeps the door open on the record rather
  than requiring a future ADR to discover it needs reopening.

## Consequences / open questions

- **Tuesday's two planned spatial build lanes are cancelled as unnecessary**:
  the tile-grid implementation and the camera/real-estate application built on
  it. Neither reaches production; the sandbox's existing 32px snap remains a
  dev-tool only.
- **Wednesday's decorating math is constrained** to tier/ownership-keyed inputs
  only -- props owned, spend, tier -- never positions, never coordinates, never
  grid cells. Any decorating-math design that wants "where a prop sits" as an
  input needs to first clear this ADR's review, not route around it.
  Wednesday's decorating-math block must hold the doctrine line explicitly:
  decor value keys off ownership/tier/spend (sim-side counts), never off
  placement; placement is expression only. A placement-priced decor bonus
  would be a spatial fact becoming a gameplay input, which this ADR forbids.
- **The camera question is a triggered decision**, not a standing one: a
  Camera2D enters consideration only when a ruled office tier exceeds one
  fixed-rect screen; until then fixed-rect Control + duplicate-instance
  compare (lease-upsell) stand. Nothing built under those is discarded by a
  later camera -- the Control becomes viewport content.
- **The determinism/replay/leaderboard system (ADR-0006) is the load-bearing
  beneficiary.** Spatial state, if it existed as a gameplay input, would need
  its own serialization and deterministic replay path (coordinates, grid state,
  occupancy) alongside the existing sim state -- a second thing to keep
  byte-identical across runs and version-stable across leaderboard epochs. This
  doctrine removes that entire surface from the replay contract by construction.
- **The dual-source-of-truth failure class (2026-07-25 modal soft-locks) is the
  structural precedent** for refusing a second state store here: those soft-locks
  came from UI-side state drifting from sim-side state under imperfect
  reconciliation. A spatial render layer promoted to a gameplay input would be
  exactly that pattern -- render-side coordinates as a second "what is true" the
  sim would need to stay synced with -- at a larger and more failure-prone
  surface than a single modal.
- Open: the entity-ID invariant's exact serialization shape for render-click
  commands (which action verbs, which entity types) is not specified here --
  that is implementation detail for whichever future ADR or ticket introduces
  the first render-click command, constrained to land inside this doctrine.
- Open: what "clears the 2027-07-27 review" looks like procedurally (who
  convenes it, what evidence would justify reopening) is not specified; parked
  for the standing decision-review process to pick up.

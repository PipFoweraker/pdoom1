# SEED: Asset Registry + Verdict Semantics + Generation Strategy

> **RAW SEED, not decided canon.** Feeds WS-3 (#811) + the art-integration
> system. Status: SEED.
>
> Tags: [PIP] = Pip's framing 2026-07-25, [CLAUDE-note] = secretariat
> articulation (reword/discard freely).

This captures the office-economy + art-integration seam: how the art-triage
verdicts should feed a data-driven asset registry, and how future art
generation rounds should be aimed. Nothing here is built yet.

---

## 1. Verdict semantics (what the contact-sheet triage tags MEAN) [PIP, refined 2026-07-25]

The 5 verdict tags from the art triage (`art_source/pixellab_verdicts.json`) do
NOT all mean the same thing -- meaning depends on asset kind.

- **PROMOTE a person/cat** = "canonical entity: register it into the schema as
  representing someone, and BUILD IT AS A WALKING ASSET." Some 8-direction
  character/cat groups are effectively the walk-cycle frames already; others are
  static 8-direction stills that need walk frames generated. So
  promote-character -> (a) a schema entity + (b) a walk-asset build task.
- **PROMOTE a prop** = "add it to the draw-pool, categorised by kind/tier tags."
  Static, no animation.
- **FAVOUR** = softer positive (keep/prefer), not necessarily canonical.
- **DISFAVOUR / DISLIKE** = a MOVE-AWAY-FROM signal: not merely "don't place
  it," but "don't GENERATE more things like this in future." Feeds forward as
  negative/avoid guidance for later generation rounds.

[CLAUDE-note] Implication: the analyzer's `promote_list` splits into two queues
-- a walk-asset build queue (characters/cats) and a registry-pool queue (props).
The disfavour list becomes negative-prompt guidance, not just an exclusion.

---

## 2. Target architecture: data-driven asset registry [PIP question, confirmed]

[PIP] "the game goes 'I want a scummy level chair here, so I'll pick one that
fits these criteria and put it into the office according to these rules' or
something along those lines?"

[CLAUDE-note] Yes -- this is a tagged asset registry + query-based instantiation
+ placement rules, three layers:

- **REGISTRY (schema):** each asset is an entry with structured tags -- kind
  (chair/desk/cat/worker), tier (scummy/decent/premium), entity/role (for
  people: this sprite = a researcher), footprint (tiles occupied), allowed
  facings, animation (static vs walk-cycle), style tags. ("the list of things
  the game draws from")
- **SELECTION (query):** the game issues a semantic request ("chair,
  tier=scummy, 1x1, against-wall") -> registry returns matches -> weighted pick
  chooses one.
- **PLACEMENT (rules):** grid-snap, facing-by-context (wall-hugging faces
  inward), spacing, no-overlap, Y-based z-sort.

Payoff: content scales WITHOUT code -- new chair = tag it + drop in pool, no new
logic. This is why curation-first (the triage) is the right order: the promote
lists seed the registry.

This system does NOT exist yet; it is a WS-3 / office-economy build. Relate to
ADR-0004 (self-describing data) and the office_floor system
(`godot/scripts/ui/office_floor/`).

---

## 3. Generation strategy for future rounds [PIP]

Aim for a SLIGHT EXCESS of assets, then refresh/upgrade over time. Generate
toward the GAPS the analyzer surfaces (currently zero-promote: floor/wall
tilesets, windows, icon_doom, structural props) rather than more of the
over-covered (cats/walk was promoted 72x).

Apply a shared coherence-instruction preamble to every prompt (consistent
implied light / palette / pixel density) so new outputs cohere with existing
keepers.

Use the disfavour list as move-away-from negatives.

Provenance (prompt+params) must be captured per generation so we know what
produced things we liked and can re-generate with coherence instructions added.

---

## Related

- `docs/game-design/WORKSHOP_3_PREP.md`
- `tools/art_review/README.md`
- The office sandbox
  (`godot/scenes/ui/office_floor/office_sandbox.tscn`)
- ADR-0004 (self-describing data)

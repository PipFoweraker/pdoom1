# Pixellab batch -- 2026-07-27 prop re-base bulk + facing pilot (queue D+E)

Execution of the 2026-07-26 native-grain-vanguard verdict (Pip: native grain
won; generate large then downscale; the medium-detail dial probe was
unanimously positive; re-prompt desk_scummy rather than re-roll it). Feeds
issues #900 #925.

Review sheet: `art_generated/prop_rebase_sheet.html` (regenerate with
`python tools/art_review/build_prop_rebase_sheet.py`).

## Prop catalog scope

The catalog this lane covers is the 5 props that actually exist as a
lineage: `water_cooler`, `filing_cabinet`, `server_cluster` (all 3 already in
`godot/data/office/props_manifest.json`, tagged `decent`-only, `review: true`)
plus `desk` and `door` (net-new from the 2026-07-26 vanguard, filling gaps Pip
flagged -- no current in-game art existed for either). **This is the whole
catalog**, not a budget-limited subset -- there is no larger prop list to draw
from yet, so breadth here means "every prop got covered," not "every prop we
could think of." Extending the catalog (more prop types) is a design-backlog
item, not something this lane invented art for.

## Generation method (per Pip's 2026-07-27 ruling)

`create_map_object`, basic mode, transparent bg, view `high top-down`,
outline `single color outline`, **medium detail / medium shading** (the
2026-07-26 dial probe's winning detail level, folded in here as the DEFAULT,
not a side probe). Common prompt suffix on every roll (unchanged from the
vanguard): *heavy black outline, deep shadow beneath, straight-on centered
symmetrical view-locked, warm-grime lived-in office, muted teal-olive-slate
palette, warm amber accent only.*

**Generate large, then downscale** (Pip's ruling -- downscaled-from-large
read "way better, fewer chunks"): every prop generates at 2x its native
target canvas, then downscales with PIL `Image.resize(..., Image.LANCZOS)`
to the native size. LANCZOS (not nearest-neighbour) was the deliberate
choice: nearest-neighbour at a clean 2x ratio just re-produces the same
"chunky" grain Pip was moving away from; a smooth resampling filter is what
actually buys the "fewer chunks" read he described. Both the native
(downscaled, KEPT) and the 2x large_source (provenance) files are on disk;
the sheet shows native with an expandable large_source underneath.

Native canvas sizes (unchanged from the vanguard, real-world-height-derived
against the 2-tile/64px worker): water_cooler 40x48, filing_cabinet 40x52,
server_cluster 112x80, desk 72x48, door 48x80.

## D: prop re-base (16 map-object jobs, 2 rolls per prop-tier except door)

| prop-tier | rolls | native size | notes |
|---|---|---|---|
| water_cooler_scummy | 2 | 40x48 | grimy/dented/rust prompt |
| water_cooler_decent | 2 | 40x48 | clean/tidy prompt |
| filing_cabinet_scummy | 2 | 40x52 | battered/dented/rust prompt |
| filing_cabinet_decent | 2 | 40x52 | tidy/label-slots prompt |
| server_cluster | 2 | 112x80 | single tier (no scummy/decent split in the catalog) |
| desk_scummy | 2 | 72x48 | **RE-PROMPTED, see below** |
| desk_decent | 2 | 72x48 | tidy desk + slim monitor prompt |
| door_scummy | 1 | 48x80 | battered/scuffed prompt |
| door_decent | 1 | 48x80 | clean/brass-handle prompt |

Door got 1 roll each (not 2) -- it was the last combo before the run's
concurrency ceiling made every submission a retry, and 1 clean roll per tier
was judged sufficient breadth (door is a simple low-detail-variance shape
compared to desk/cooler/cabinet). Flag for a second roll if Pip wants it.

### desk_scummy re-prompt (the flagged weak roll)

2026-07-26 vanguard verdict: `desk_scummy_native_r1` "reads as a lone CRT,
desk surface lost." This lane does NOT reuse that prompt. New prompt
explicitly forces desk-surface visibility:

    cluttered office desk viewed from above at an angle, WIDE wooden desk
    surface clearly visible on all sides of a bulky beige CRT monitor
    sitting centered on top of the desk, coffee rings and grime stains
    across the visible desktop, scattered loose papers and a chipped mug
    sitting ON the desk surface beside the monitor, desk legs visible
    beneath the desktop, desk surface reads clearly larger than the monitor,
    [+ house suffix]

Eyeball read (Claude, pre-Pip): both desk_scummy rolls at native size show a
visibly wider desk plane than the monitor, with a mug/printer/papers spread
across it -- the "lone CRT" failure mode does not recur at a glance. Pip
should confirm on the sheet.

## E: desk facing pilot (4 map-object jobs, 1 roll each)

Evidence for Wednesday's decorating-math block: is a facing-direction variant
(front-facing vs side-profile) worth the 2-4x art cost of authoring every
prop twice? One roll each of front-facing and side-profile, scummy + decent:

| combo | native size | notes |
|---|---|---|
| desk_front_scummy | 72x48 | front edge facing viewer, same silhouette family as the D desk_scummy rolls |
| desk_front_decent | 72x48 | front edge facing viewer, decent tier |
| desk_side_scummy | 48x48 | rotated to side profile, narrow edge forward |
| desk_side_decent | 48x48 | rotated to side profile, narrow edge forward |

This is a SMALL evidence probe, not a decision -- Pip rules on whether the
side-profile silhouette reads well enough at this scale to justify doubling
authoring cost across the whole prop catalog.

## Generation cost (pixellab, this sub-lane)

20 create_map_object jobs (16 D + 4 E) at 2x canvas, basic mode -- per the
2026-07-26 vanguard's confirmed ~1 gen/object rate at THIS SIZE CLASS
(objects here are larger than the vanguard's, but create_map_object basic
mode billing was flat ~1/object there regardless of size within its
32-400px range). Balance before this run's start: 5793 remaining. Balance
after D+E+the rest of the run's other queue items: see the run's final
report. Well inside the ~450-gen cap for this queue item -- the catalog's
small size (5 props), not the budget, was the limiting factor on total roll
count. If Pip wants more depth (more rolls per tier) rather than more
breadth, there is ample budget headroom to spend on additional rolls of any
combo above.

## Rate-limiting note (operational)

Tier 3's per-submission rate limiter rejected roughly half of all
create_map_object calls in this lane with "rate limit exceeded" (distinct
from the 20-concurrent-job hard cap, which also triggered separately on the
worker walk-animation batches running in parallel). All rejections were
pre-billing (no generation consumed) and cleared on retry within ~10-30s.
Two jobs (`desk_front_scummy_r1`, `desk_side_decent_r1`) sat at "processing
95%, eta ~0s" for an unusually long tail (several minutes, dozens of retries)
before their download endpoints returned 200 -- both eventually succeeded, no
data was lost, but a retry-with-backoff pattern (used here: up to 20 retries
at ~8s spacing, checked against get_map_object's own status in parallel) is
worth keeping as house practice in any future lane that fires >15 concurrent
props.

## Follow-up hooks

- If Pip promotes native grain + medium detail as the house standard: update
  `godot/data/office/props_manifest.json` with `desk` and `door` entries
  (new prop ids) and re-measure `canvas_px` / `subject_px` / `anchor_px` /
  `footprint_tiles` against the NEW art (PIL alpha bbox, per
  `docs/art/PROP_MANIFEST.md`) -- the manifest's existing 3 entries also need
  their `art` swapped to the new files and `review: true` cleared once Pip
  rules on footprint/tier questions.
- E's facing-pilot verdict feeds the Wednesday decorating-math discussion
  directly -- do not pre-empt it by wiring facing variants into the manifest
  schema until Pip rules.

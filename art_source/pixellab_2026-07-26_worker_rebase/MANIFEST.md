# Pixellab worker re-base at size 64 -- 2026-07-26

The sim-character roster regenerated at the CONFIRMED 64px standard (Pip,
2026-07-26 evening: "64 pixels were just so much better all other comparisons
felt irrelevant"). The size-48 round-2 workers
(art_source/pixellab_2026-07-26_round2/) are superseded probes. Feeds issues
#900 (round-2 art push) and #793 (worker variant pool). NO godot/ wiring in
this lane -- the variant-pool registry consumes these AFTER Pip's triage.

Review sheet: `art_generated/worker_rebase_sheet.html` (regenerate with
`python tools/art_review/build_worker_rebase_sheet.py`; images embedded as
data URIs so the copy in the main checkout works standalone; inline animated
players for every walk/roll direction).

## Generation settings

`create_character` standard mode, humanoid, **size 64 (emits 92x92 canvas)**,
low top-down, 8 directions, single color black outline, high detail, basic
shading. Descriptions reuse the round-2 prompts verbatim (plus the two
briefed extensions and yes-ands below). Every walk/action prompt carries the
CLEAN-ALPHA house rule language ("clean transparent background under feet in
every frame, no white halo" -- docs/art/PIXELLAB_OPERATIONS.md).

Walk cycles: template `walk`, all 8 directions, 6 frames/direction, for the
five standard walkers. worker_crutch_m walk and worker_wheelchair_f roll are
**v3 customs** (4 cardinals, 9 frames incl. reference, 2 gens/direction at
the 92px canvas -- the v3 cost formula crossed the 1-gen threshold, SCHEMA
ceil(92*92*8/65536)=2, confirmed by the tool's quoted "cost: 8 generations
(2/dir x 4)").

## Roster (provenance: briefed vs yes-and)

| folder | pixellab id | provenance | notes |
|---|---|---|---|
| worker_hijab_f | 828e2e3d-9c81-4641-894c-f9cd036a8cf3 | briefed re-base | round-2 prompt at 64; walk 8-dir (group fc1b57d0-f847-438f-98ed-cc69a2f49676) |
| worker_black_m | 692cdbd7-925d-4dc2-86e5-38035f2fccb1 | briefed re-base | round-2 prompt at 64; walk 8-dir (group 195bb633-7bd8-4ee6-9ca8-7535e057caa0); state-pilot source (state group 4d85d2cb-3f00-4b97-b6dc-ce30c180a712) |
| worker_wheelchair_f | 0a231b6f-244d-459f-aa17-3727be0074a6 | briefed re-base | round-2 prompt at 64; **yes-and: v3 roll cycle**, 4 cardinals (group e41ce223-fa41-4c2c-8cff-5c224eca359c) -- round 2 had no wheelchair locomotion |
| worker_crutch_m | 90622a05-9423-4523-99c4-b9e32733583f | briefed re-base | round-2 prompt at 64; v3 crutch-walk, 4 cardinals (group 7f32a6e7-60b4-49f7-a221-7baf75fb134c) |
| worker_crutch_m_v2 | 7eb220d2-7f28-4bfd-af0f-f236abd86343 | yes-and alternate | stills only; prompt forces "crutch visible from every viewing angle" -- see legibility verdict |
| worker_glasses_badge_m | 02dfc725-e9ff-42c3-a36f-f518f10d0003 | briefed extension | size-probe accessory set (round glasses + teal lanyard + white ID badge) + house palette suffix; walk 8-dir (group 75b58eac-5efe-4cc9-b660-176d03a2c670) |
| worker_grey_f | 2f14fada-c496-44fa-b32a-368ccfefa53f | briefed extension | older woman, short grey hair, reading glasses on cord; walk 8-dir (group a77522c9-5283-4dff-9ab8-d78e4b54ee3f) |
| worker_headphones_m | 20705f27-8678-4491-9f0b-d4297b87f4ba | yes-and | young Latino man, trimmed beard, charcoal headphones around neck; walk 8-dir (group 67ced205-04d4-4306-ab7c-2cb2b1f79b92) |

Each folder: `rotations/{south,...}.png` (8) + `animations/<name>/<dir>/
frame_NNN.png` + pixellab `metadata.json` (full prompts + params).

### State pilot at 64 (create_character_state, worker_black_m)

| state | new character id | edit |
|---|---|---|
| worker_black_m_state_working | fc1096a7-2ccc-4b72-a23e-c3b663d30817 | seated typing pose, hands raised as if typing, legs bent as if on office chair |
| worker_black_m_state_idle | 961258e7-61ea-4629-ac26-2b0ed3e719b0 | standing relaxed, one hand holding amber coffee mug |
| worker_black_m_state_stressed | d599571f-69c5-4f44-8386-347d7eea3255 | slumped, shoulders hunched, hand pressed to forehead |

All three landed on the first roll; palette snapped to source
(use_color_palette_from_reference). 8 rotations each. The bundle zip's
shared metadata.json (covering base + all 3 states) lives in
worker_black_m/metadata.json; state folders carry rotations only.

## QC gate (tools/art_review/qc_sprite_frames.py -- PIL)

Checks: (1) clean alpha -- no near-white opaque pixels (min(R,G,B)>=235,
alpha>=128) in the lower third of any frame; (2) canvas consistency; (3)
frame continuity -- silhouette-centroid jump <=10px AND silhouette IoU >=0.55
between adjacent frames (limb-teleport suspects).

**Result 2026-07-26: 400 frames, 11 variants/folders, ALL 92x92, 0 alpha
failures, 0 continuity suspects.** The clean-alpha prompt language + PIL
verify loop from the cat refinement lane held at size 64 with zero re-rolls.

### Legibility verdicts (the flagged watch items)

- **worker_crutch_m front legibility at 64: RESOLVED for south.** The 48px
  version's front view was flagged weak; at 64 the crutch reads clearly in
  the south rotation AND is planted rhythmically in all 9 south walk frames
  (visible handle + shaft + ground contact). Caveat: it reads closer to a
  cane than a cuffed forearm crutch at this scale, and the **east/west
  rotations + walks dropped the crutch entirely** (model treats it as an
  occluded accessory side-on). worker_crutch_m_v2 forces "visible from every
  angle": it gains a thin stick in E/W/N but the south view grows an
  ambiguous second stick and the crutch reads thinner overall. Both are on
  the sheet -- triage call is Pip's.
- **worker_wheelchair_f:** side/diagonal rotations read unmistakably (large
  spoked wheel, hand on rim) -- same as the round-2 finding. Front-on (south)
  the wheels barely read; inherent to the low top-down front angle, not a
  re-roll target. The yes-and roll cycle turns the wheel spokes convincingly
  in east/west; south roll reads as subtle bobbing.
- **worker_glasses_badge_m:** the probe's accessory richness survives
  production: glasses, lanyard and chest badge all read at 92x92.

## Generation cost (pixellab)

- Balance BEFORE lane: **5949 generations remaining** ($0.00 credits,
  **Tier 3 Pixel Architect**, 7419 total -- first lane on the upgraded tier).
- Balance AFTER lane: **5812** -> **137 generations total**.
- Decomposition (partially bracketed; walks/states overlapped in flight so
  per-op isolation was not possible this lane):
  - 8 statics (7 roster + crutch v2) x 1 gen = 8
  - v3 customs: wheelchair roll 8 + crutch walk 8 (quoted "2/dir x 4" by the
    tool at the 92px canvas) = 16
  - remaining 113 = 5 template walks (40 direction-jobs) + 3 states. If
    states ran at the round-2 measured ~21/state (63), walks land at ~1.25
    gens/direction -- BELOW the round-2 isolated 2.1/dir. Tier 3 and/or
    queue state may change effective billing; next lane should isolate one
    walk block to re-measure.
- Tier 3 concurrency observed: hard cap **20 jobs** (error text
  "need 8 job slots but only N available (M/20 used)"); submissions beyond
  the cap fail fast with a clean error instead of "heavy load"; zero
  heavy-load failures all lane.

## Ops notes for future lanes

- The `download` endpoint (api.pixellab.ai/mcp/characters/<id>/download)
  needs no auth, returns 423/JSON while animations are still generating,
  and bundles state-group siblings into one zip (base + one folder per
  state, named from the edit text's first words).
- Characters do NOT auto-delete like map objects, but everything here was
  downloaded in-lane anyway (house rule).

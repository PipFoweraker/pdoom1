# Pixellab batch -- 2026-07-26 prop NATIVE-GRAIN vanguard

Vanguard lane gating the ~500-gen prop re-base (issues #900, #925). Question:
should office props be regenerated at native pixel grain (small canvases whose
pixels land 1 art px = 2 screen px, matching the 32px-art floor at the world's
2x) instead of reusing the current larger-canvas art (fine grain; oversized at
manifest scale, smooth mush when downscaled to realistic proportion)?

Decision sheet: `art_generated/prop_grain_vanguard_sheet.html`, built by
`tools/art_review/gen_prop_grain_sheet.py` (review_style module; regenerate any
time from the PNGs in this folder).

## Balance (get_balance brackets, per PIXELLAB_OPERATIONS.md)

- Account: Tier 3 "Pixel Architect", subscription active. Monthly pool now
  reads 7419 total (Tier 1 was 2000 -- first measured Tier 3 pool figure).
- Start of lane: 5826 remaining (1593 used).
- End of lane: 5793 remaining (1626 used).
- **Delta: 33 generations for 32 kept map objects (~1.03 gen/object)** --
  confirms the ~1 gen/prop create_map_object rate from 2026-07-19, unchanged
  on Tier 3. The one extra gen over nominal is unexplained (possibly one of
  the rate-limited submissions partially billed); too small to chase.
- Failures: 5 submissions rate-limited at ~14 jobs in flight ("rate limit
  exceeded", NOT billed) and refired successfully ~3 min later. Tier 3
  advertises 20 concurrent [verify]; the MCP submission path throttled earlier
  than that. No "heavy load" failures; no server-side timeouts.

## Generation params

All via `create_map_object` (basic mode, transparent bg), view `high top-down`,
outline `single color outline` -- the locked 2026-07-19 house recipe, changing
ONLY canvas size (and detail on the dial rolls). Common prompt suffix on every
roll: *heavy black outline, deep shadow beneath, straight-on centered
symmetrical view-locked, warm-grime lived-in office, muted teal-olive-slate
palette, warm amber accent only.*

Three sub-batches:

- `native/` (21 rolls) -- **the candidates.** True-proportion canvases sized
  from real-world height vs the 2-tile (64 art px) worker: water_cooler 40x48
  (target ~1.3 tiles), filing_cabinet 40x52 (~1.45), server_cluster 112x80
  (~2.2 tall, ~3 wide), desk 72x48 (~1.35 incl monitor), door 48x80 (~2.25).
  `high detail` + `detailed shading`. Scummy/decent tier variants where the
  ladder has them (cooler, cabinet, desk, door; server single-tier).
- `manifest_scale/` (6 rolls) -- **controls.** Same prompts at the CURRENT
  oversized manifest canvases (64x120 / 72x112 / 128x120) to separate the
  grain variable from the scale variable.
- `dial/` (5 rolls) -- one `medium detail` + `medium shading` roll per prop at
  the native canvas (detail-density dial for Pip).

## Clean-alpha check (house rule)

PIL scan over every PNG: near-white pixels with partial alpha (halo/matting)
and faint speckles (alpha 1..40). **All 32 files: 0 halo px, 0 speckle px.**
create_map_object output is clean at these sizes; no re-rolls needed for alpha.

## Lane eyeball read (Claude, pre-Pip)

- **Native grain wins on the trio.** At 2x the small gens sit ON the floor's
  pixel grid; chunky outlines read like the same world as the concrete tiles
  and the 2026-07-19 tilesets. The current art at manifest scale is not
  actually grain-wrong (it also lands ~2 screen px/art px) -- it is
  **proportion-wrong** (3.25-3.5 tiles vs the 2-tile worker), and fixing the
  proportion by downscaling the current art produces sub-pixel smooth mush
  (the (a2) strip on the sheet). So the re-base is really buying correct
  scale + native grain together; the sheet makes that split visible.
- **Manifest-scale controls** came out fine-grained and glossy -- they look
  like MORE detailed versions of the current art, i.e. re-generating at the
  old canvases does not fix the mismatch. Evidence the size change, not the
  re-roll, is what matters.
- Weak rolls: `desk_scummy_native_r1` (reads as a lone CRT, desk surface
  lost), `water_cooler_scummy_native_r1` (stray green blob at the base).
  Both got second rolls; re-roll further in the follow-up batch if Pip
  promotes the direction.
- The `medium detail` dial rolls are simpler/flatter; at 40-48px canvases the
  high-detail rolls still read chunky, so the dial is taste, not necessity.

## Files

- `native/` -- 21 PNGs: `<prop>_<tier>_native_rN.png` (server has no tier).
- `manifest_scale/` -- 6 PNGs: `<trio-prop>_manifestscale_rN.png`.
- `dial/` -- 5 PNGs: `<prop>_dial_medium_rN.png`.
- Pixellab object IDs per file: `object_ids.json` (map objects auto-delete
  after 8 h server-side, so these IDs are provenance only -- the PNGs here are
  the durable artifact).

## Follow-up hooks

- If Pip promotes native grain: full prop re-base (~500 gens) at
  true-proportion canvases; update `props_manifest.json` heights (all trio
  entries carry `review: true` today) and re-measure anchors on the new art.
- Desk and door fill the drawn-circle gap Pip flagged (no current in-game
  art) -- promotable directly regardless of the re-base verdict.

# Pixellab batch -- 2026-07-27 worker round 2 (queue A+B)

Two worker-roster items from the 2026-07-27 background art run (issues #900
#793), same house standard as `pixellab_2026-07-26_worker_rebase/`:
`create_character` standard mode, humanoid, size 64 (emits 92x92 canvas), low
top-down, 8 directions, single color black outline, high detail, basic
shading; template `walk`, all 8 directions, 6 frames/direction. Clean-alpha
house language included in every prompt ("clean transparent background under
feet in every frame, no white halo").

Review sheet: `art_generated/worker_round2_sheet.html` (regenerate with
`python tools/art_review/build_worker_round2_sheet.py`).

## A. worker_headphones_m_r2 -- REROLL

Pip's dislike on the 2026-07-26 `worker_headphones_m` roll: the headphones
were sometimes INVISIBLE (occluded by hair/hood in some rotations). This is
a fresh character (not a state edit) with the prompt hardened to force large,
clearly-visible over-ear headphones in every direction:

    young Latino office worker man, trimmed dark beard, warm brown skin, teal
    collared office shirt, LARGE prominent black over-ear headphones worn on
    his head at all times, thick padded ear cups clearly visible and NEVER
    hidden by hair or hood, thick headband visible over the top of the head,
    headphones same size and clearly visible from every rotation angle
    including back and side views, friendly relaxed expression, cozy pixel
    art RPG office worker, warm muted teal-olive-slate palette, cartoony
    retro style, pixel art, clean transparent background under feet in every
    frame, no white halo

pixellab character id: `2843c26a-afe7-4254-b076-8c6c5dc7555a`
walk animation group: see `metadata.json` (folder
`animations/walking_clean_transparent_background_under_feet_in/`, PixelLab's
auto-slug of the action_description).

Eyeball read (Claude, pre-Pip): headband + large round ear cups read clearly
in south, both side profiles, and both back-diagonals on the rotation stills
-- the failure mode from 2026-07-26 (headphones vanishing) does not recur at
a glance. Pip should confirm on the sheet, especially the north (back) view
where hair coverage is highest risk.

## B. worker_grey_black_f -- FRESH (worker pool, not cast)

    older Black woman office worker, short natural grey hair, warm brown
    skin, cardigan over a simple blouse, thin reading glasses, calm
    confident expression, cozy pixel art RPG office worker, warm muted
    teal-olive-slate palette, cartoony retro style, pixel art, clean
    transparent background under feet in every frame, no white halo

pixellab character id: `e82d4f98-896d-49cb-b1b1-890cb9940d5f`

## Files

Zip-native layout per character (matches the 2026-07-26 rebase convention):
`<variant>/rotations/{south,...}.png` (8) + `<variant>/animations/<slug>/
<direction>/frame_*.png` (8 dirs x 6 frames) + `<variant>/metadata.json`
(full API prompt/params provenance).

## Generation cost (pixellab, this sub-lane)

- create_character x2 = 2 gens
- animate_character (template walk, 8 dirs) x2 characters = 16 direction-jobs;
  observed ~1 gen/direction at this canvas per the 2026-07-26 lane precedent
  (not isolated this lane -- ran interleaved with queue C/D/E).

## Follow-up hooks

- QC gate (`tools/art_review/qc_sprite_frames.py`) was NOT run against this
  sub-lane in-run (time-boxed); run it before promoting either variant --
  the 2026-07-26 rebase found zero failures at this exact canvas/prompt
  style, so a clean result is expected but unverified here.
- If Pip promotes worker_headphones_m_r2: retire the 2026-07-26
  worker_headphones_m (the "sometimes invisible" version) from the variant
  pool rather than keeping both.

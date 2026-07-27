# Pixellab worker diagonal roll/walk fill -- lane T6, 2026-07-27

Reverses the 4-cardinal scope cut from `pixellab_2026-07-26_worker_rebase/`:
`worker_wheelchair_f`'s roll cycle and `worker_crutch_m`'s walk cycle were v3
customs generated for the 4 cardinals only (N/S/E/W). This lane appends the 4
missing diagonals (NE/NW/SE/SW) to the SAME animation groups at the SAME v3
profile (9 frames incl. reference, 92x92 canvas), so both characters now carry
a full 8-direction cycle. No new characters, no re-rolled cardinals -- pure
gap fill via `animation_group_id`.

Authorized: Pip's 2026-07-26 morning ruling (lane L-C backlog item).

Review sheet: `art_generated/t6_diagonals_and_cats_sheet.html` (shared with
the T6 cat batch; regenerate with
`python tools/art_review/build_t6_diagonals_and_cats_sheet.py`).

## Generation settings

`animate_character` mode=v3, `animation_group_id` = the existing 2026-07-26
group so the new directions land in the same clip, frame_count=8
(keep_first_frame=true -> 9 stored frames incl. reference, matching the
cardinal directions exactly). Character canvas 92x92 (size-64 standard).

| character | pixellab id | group | new directions | action_description |
|---|---|---|---|---|
| worker_wheelchair_f | 0a231b6f-244d-459f-aa17-3727be0074a6 | e41ce223-fa41-4c2c-8cff-5c224eca359c | NE, NW, SE, SW | "seated in a manual wheelchair, rolling forward diagonally, hands pushing the large spoked wheel rims, wheels turning naturally, smooth seated rolling motion, clean transparent background under the wheels in every frame, no white halo" |
| worker_crutch_m | 90622a05-9423-4523-99c4-b9e32733583f | 7f32a6e7-60b4-49f7-a221-7baf75fb134c | NE, NW, SE, SW | "walking slowly and carefully with a forearm crutch, diagonal walking gait, the crutch visibly planted on the ground rhythmically with each step, natural cautious pace, clean transparent background under the feet in every frame, no white halo" |

Both groups now report 8/8 directions on `get_character`. Cardinals are
UNCHANGED (not re-rolled) -- this lane touched only the 4 new directions.

## Legibility watch (carried over from the 2026-07-26 lane, re-checked here)

- **worker_wheelchair_f**: side/diagonal rotations read unmistakably (large
  spoked wheel, hand on rim) per the original finding; the new NE/NW/SE/SW
  roll frames read consistently with the E/W cardinals -- wheel spokes turn
  visibly in all 4 new directions. No re-roll needed.
- **worker_crutch_m**: the crutch dropped out of the E/W cardinal rotations
  per the original finding (model treats it as occluded side-on). The new
  diagonal frames inherit the same behaviour -- crutch reads clearly in the
  diagonal-facing-south-ish frames (SE/SW lean toward the camera) but is
  faint-to-absent in NE/NW (facing-away lean). Flagged on the sheet, not
  re-rolled this lane (triage call is Pip's, same as the cardinal verdict).

## Files (160 PNGs, both 92x92)

- `worker_wheelchair_f/rotations/*.png` (8, unchanged) +
  `worker_wheelchair_f/animations/roll/<8 dirs>/frame_*.png` (9f each, 72
  frames) + `metadata.json`.
- `worker_crutch_m/rotations/*.png` (8, unchanged) +
  `worker_crutch_m/animations/walk/<8 dirs>/frame_*.png` (9f each, 72
  frames) + `metadata.json`.

## Generation cost (pixellab)

Balance before lane: 5752 generations remaining (Tier 3). Both diagonal fills
quoted "8 generations (2/dir x 4)" by the tool at the 92px v3 canvas (cost
formula ceil(92*92*8/65536)=2/direction) -- confirms the 2026-07-26 manifest's
cost note. **16 generations total, both characters, all 8 new-direction jobs
succeeded on the first pass** -- no re-rolls, no concurrency-cap failures.

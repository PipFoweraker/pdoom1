# Pixellab cat round -- lane T6, 2026-07-27 (tabby refresh + eldritch non-heft side)

Cat next-round work per Pip's locked rules (2026-07-26/27 morning ruling):
heft language applies to every cat EXCEPT eldritch; licking/sitting poses are
dropped entirely (office-cat flourish clips shipped 2026-07-26 but are not
being repeated); butt_flash_north ships for any NEW identity. Modest round,
two items:

1. **Tabby hefty side-view refresh** -- black_side_heft and purple_side_heft
   already promoted clean at E/W (`cat_sweep_verdicts.json`); tabby's open
   item was the diagonal MIXING-BOUNDARY PROBE
   (`cat_b2_tabby_side_heft/animations/walk_side_diag_probe/`), which only
   got bare "like" verdicts on NE/NW/SE/SW (never "promote") -- weaker than
   the E/W pair. This lane generates a genuinely distinct diagonal take
   (not a re-roll of the probe) for direct comparison.
2. **Eldritch round in its ORIGINAL (non-heft) direction** -- the heft trio's
   eldritch member (`cat_sweep_eldritch_side_heft`) got "disfavour" across
   every direction in the 2026-07-26 sweep (east/west/all 4 diagonals) --
   the empirical basis for the "heft everywhere EXCEPT eldritch" rule. This
   lane gives eldritch a SIDE-VIEW character built from its own ORIGINAL
   `cat_eldritch_r2` prompt (no heft language) instead, since eldritch had
   no non-heft side-view option before this lane (only low-top-down).

Review sheet: `art_generated/t6_diagonals_and_cats_sheet.html` (shared with
the T6 worker diagonal batch; regenerate with
`python tools/art_review/build_t6_diagonals_and_cats_sheet.py`).

## Pipeline note applied (from `pixellab_2026-07-27_cat_west_variants/MANIFEST.md`)

Identical template+direction `animate_character` calls on the same character
return CACHED results, not new generations. The tabby refresh avoids this by
using **v3 mode** (not the template mode the original probe used) with a
weightier, more deliberate action_description -- a mode change, not just a
new animation_name, so it queues genuinely fresh jobs (confirmed: 4 distinct
new job IDs, not "already complete").

## Item 1: tabby diagonal v3 refresh

`animate_character` on `cat_b2_tabby_side_heft` (id
`42976b8d-6b3c-4fb0-ab9e-4acbb90abb43`, unchanged, EXISTING character --
no re-create), mode=v3, frame_count=8 (9 stored incl. reference), new group
`walk_side_diag_v3refresh` (group id `6a37e6d7-a65c-4575-9429-bddc3e2c7a47`):

> stocky heavy tabby cat walking diagonally, side view, thick barrel body
> swaying with weighty steps, broad chest, short sturdy legs planting firmly,
> all four legs visible in a natural feline gait, deliberate heavy-footed
> pace

Directions: NE, NW, SE, SW (4 jobs, all succeeded first pass). The sheet
pairs this v3refresh clip against the original `walk_side_diag_probe`
template clip per direction so Pip can pick a winner (or keep both as
distinct "cautious mixing" vs "confident heft" reads).

## Item 2: eldritch non-heft side-view character

New character `cat_eldritch_side_original` (id
`f9af0f30-8542-4658-bc31-f3804e362193`), `create_character` standard mode,
quadruped/cat template, **view=side**, size 48 (68x68 canvas), 8 directions,
single color black outline, medium detail, basic shading -- description
copied VERBATIM from `cat_eldritch_r2`'s original creation prompt (the
low-top-down original, NOT the rejected heft side variant):

> a black cat with glowing violet eyes and a glowing collar emblem, faint
> eldritch violet aura, unsettling doom cat, warm grimy pixel art, heavy
> black outline, deep contrast shadows

Animation: template `walk-8-frames`, directions E/W + all 4 diagonals (6
jobs, group `d7d809d5-2e5e-47f4-9e5b-e7f66622486a`) -- N/S skipped
deliberately (side-view N/S is the empirically-settled "never ship,
bipedal-horror" rule from the 2026-07-26 cat sweep, issue #912). Plus
`butt_flash_north` v3 custom (issue #913, new identity -> gets one per the
locked rule), 1 direction (north), group `abaa3ac6-07c1-4a16-95d1-b33e57097a25`:

> jet black eldritch cat walking away from the viewer on all four legs, seen
> from behind, tail raised straight up showing the rear, only the back of
> the head and ears and tail visible, no eyes visible, natural feline
> walking gait

All 7 animation jobs (6 walk + 1 butt-flash) succeeded first pass; one job
(walk NE) ran unusually slow in queue (~770s ETA vs ~60s for its siblings)
but completed clean, same clip quality as the rest -- flagged as a queue
hiccup, not a content re-roll target.

## Skipped per locked rules

- No sitting/licking clips generated for either subject this round (the
  locked "skip licking/sitting poses entirely" rule).
- No heft language anywhere in the eldritch prompt (the locked "heft
  everywhere EXCEPT eldritch" rule).
- No butt_flash for tabby refresh (not a new identity -- same character,
  same existing butt_flash_north clip from 2026-07-26 covers it already).

## Files (101 PNGs)

- `cat_b2_tabby_side_heft/animations/walk_side_diag_v3refresh/<4 dirs>/
  frame_*.png` (9f each, 36 frames). Rotations/other clips for this
  character are NOT duplicated here -- they already live in
  `pixellab_2026-07-26_cat_sweep/cat_b2_tabby_side_heft/`.
- `cat_eldritch_side_original/rotations/*.png` (8) +
  `cat_eldritch_side_original/animations/walk_ew_diag/<6 dirs>/frame_*.png`
  (8f each, 48 frames) +
  `cat_eldritch_side_original/animations/butt_flash_north/north/frame_*.png`
  (9f) + `metadata.json`. New character, self-contained.

## Generation cost (pixellab)

Balance before lane: 5752 generations remaining (Tier 3), continuous with
the worker diagonal batch above in the same session.

| item | jobs | cost |
|---|---|---|
| tabby diagonal v3 refresh (4 dirs) | 4 | 4 generations (1/dir, 68x68 v3 canvas) |
| eldritch character create | 1 | 1 generation (standard mode) |
| eldritch walk E/W+diag (6 dirs, template) | 6 | 6 generations (1/dir template) |
| eldritch butt_flash_north (1 dir, v3) | 1 | 1 generation |
| **cat lane total** | 12 | **12 generations** |

Modest round as briefed (target ~30-50 gens; actual spend was lean because
both items reused existing characters/prompts instead of open-ended
exploration -- nothing was cut for budget, the scope was just narrow this
round: one diagonal refresh + one new non-heft side character).

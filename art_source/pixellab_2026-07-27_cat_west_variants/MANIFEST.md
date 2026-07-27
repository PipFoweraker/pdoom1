# Pixellab batch -- 2026-07-27 cat west-walk variants (queue C)

Queue item C of the 2026-07-27 background art run (issues #900 #913):
`cat_sweep_black_side_heft`'s WEST-direction walk was flagged as having
problems on the 2026-07-26 cat sweep. This lane generates fresh WEST-only
variants of the SAME character/rotation (id
`55bf4986-ac8e-4419-bce6-aeb6892e0c56`, the locked side-view hefty black cat
recipe -- see `pixellab_2026-07-26_cat_sweep/MANIFEST.md`) for a direct
side-by-side pick. No re-roll of the character itself; only the WEST walk
animation job varies.

Pick sheet: `art_generated/cat_west_walk_picks.html` (regenerate with
`python tools/art_review/build_cat_west_walk_picks.py`).

## Variants (5 total, 2 pre-existing + 3 new)

| clip | source | type | frames | notes |
|---|---|---|---|---|
| walk_ew | 2026-07-26 (not re-spent) | template walk-8-frames | 8 | the BASELINE, flagged-problem clip |
| walk_west_cleanfix | 2026-07-26 (not re-spent) | v3 custom | 9 (ref+8) | a prior "clean fix" attempt, kept for comparison |
| west_walk_v3_template6 | NEW this lane | template walk-6-frames | 6 | different frame-count template -- distinct generation (walk-8-frames on the same character+direction DEDUPES to the cached baseline, confirmed empirically: two attempts at template walk-8-frames both returned "already complete" instead of queuing new jobs) |
| west_walk_v4_v3custom | NEW this lane | v3 custom | 9 (ref+8) | prompt: "stocky heavy cat walking west, side view, thick barrel body swaying with weighty steps, all four legs visible in a natural feline gait" |
| west_walk_v5_v3custom | NEW this lane | v3 custom | 9 (ref+8) | prompt: "chunky heavy cat walking west at a slow deliberate pace, side view, broad chest, short sturdy legs planting firmly with each step" |

Two more v3-custom variants (v6/v7) were planned but dropped after repeated
concurrency-cap rejections ("need 1 job slots but only -1 available,
21/20 used") during a very busy queue window (this run also had ~35 prop
map-object jobs and 2 worker 8-dir walk batches in flight); 5 variants
already covers the "4-6 variants" brief so they were not retried.

## Dedup gotcha (operational note for future lanes)

Calling `animate_character` with the SAME `template_animation_id` +
`direction` on a character that already has that clip returns
`status: already complete` and does NOT queue a new generation, regardless of
a different `animation_name` -- template-mode results are keyed on
(character, template, direction), not on the label. To get a genuinely
different west-walk render, either use a DIFFERENT template (e.g.
walk-6-frames vs walk-8-frames) or `mode="v3"` with a distinct
`action_description`.

## Files

`cat_sweep_black_side_heft/rotations/*.png` (8, unchanged reference) +
`cat_sweep_black_side_heft/animations/<clip>/west/frame_*.png` for each of
the 5 clips above + `metadata.json` (full API provenance for the whole
character, including sibling directions/clips not relevant to this pick).

## Generation cost (pixellab, this sub-lane)

3 new animation jobs (west_walk_v3_template6, v4_v3custom, v5_v3custom) = 3
generations. walk_ew and walk_west_cleanfix cost nothing this lane (reused
2026-07-26 pixels via the character's existing animation groups).

## Follow-up hooks

- Pip picks a winner via the sheet's verdict chips (favour/promote); the
  splice point (which frames actually get used, if fewer than the full
  clip) is a renderer decision, not an art decision -- flag on the sheet if
  a variant needs trimming like the butt-flash clips do.
- If none of the 3 new variants beat the baseline, walk_ew stays -- this
  lane treats "no change" as a valid outcome, not a failure.

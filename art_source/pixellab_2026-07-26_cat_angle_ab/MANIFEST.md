# Cat angle A/B -- 2026-07-26 (vanguard experiment for issue #900)

Pip's ruling (issue #900): cats get main-character fidelity via the per-entity
angle cheat -- regenerate cats ONE graduation more side-on while humans/scene
hold "low top-down". This folder is the A/B evidence generated BEFORE the main
round-2 cat sweep commits to the angle.

## View-enum findings (what the API actually offers)

`create_character` exposes exactly FOUR `view` values:

| view | angle | notes |
|---|---|---|
| `high top-down` | ~35 deg from above | steeper than house standard |
| `low top-down` | ~20 deg, classic 3/4 RPG | house standard (humans/scene) |
| `side` | eye-level | the ONE graduation down -- used here |
| `oblique` | 3/4 oblique projection | BETA, max 128px, 4-dir, standard-mode only; already proven BROKEN for characters (2026-07-16 V6) |

There is NO intermediate 3/4-side option between `low top-down` and `side`.
`oblique` is a projection style, not an intermediate camera angle, and it
distorted figures in the 2026-07-16 tests -- not a candidate. So "one
graduation more side-on" == `side`.

## Size note (one-dial discipline)

The tasking said "size 64 (emits 68x68)". Those two facts belong to different
batches: the API pads canvas ~40%, so size 48 -> 68x68 (the promoted
`cat_walk_cat{1,2}` walkers, 2026-07-16) and size 64 -> 92x92 (the 2026-07-19
rotation stills). The in-flight round-2 lane (`cat_*_r2` on the pixellab
account) is also emitting 68x68. To keep this A/B one-dial against the
PROMOTED walkers, both new cats use **size 48 (68x68 canvas)**. Consequence:
the cat1 pair is a clean angle-only A/B (68x68 vs 68x68); the cat_black pair
also differs in canvas (old still is 92x92) -- flagged on the sheet.

## Generation parameters (both cats)

`create_character`: mode `standard`, `body_type=quadruped`, `template=cat`,
8 directions, size 48 (68x68 canvas), view **`side`**, single color black
outline, high detail, basic shading.

| subject | pixellab id | description prompt |
|---|---|---|
| cat1_tabby_side | c1e6652d-d6e1-4fa7-aa43-af88a95e433b | cute orange tabby cat with darker orange stripes, faintly singed fur, cream muzzle and paws, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |
| cat_black_side | 46b7b253-0a2e-4cc2-be0a-1d640f6c431f | cute fluffy black cat with amber orange eyes, dark charcoal fur, slightly grumpy expression, cozy pet cat, warm bright colors, cartoony retro RPG style, pixel art |

Walk animation (tabby only): `animate_character` template mode,
`template_animation_id=walk-8-frames`, directions south/north/east/west
(4 jobs), group 567d8c22-450b-4776-8be9-c1f75aad3ddf.

## Credits

| checkpoint | generations remaining |
|---|---|
| before | 964 (1036/2000 used) |
| after | 958 (1042/2000 used) |

**6 generations total**: 2 character creates (1 each) + 4 walk directions
(1 each). $0.00 credits; Tier 1 subscription generations only.

## Files (48 PNGs, all 68x68)

- `cat1_tabby_side/rotations/{south,east,north,west,south-east,north-east,north-west,south-west}.png` (8)
- `cat1_tabby_side/walk/walk_{south,north,east,west}_{0..7}.png` (32)
- `cat_black_side/rotations/{8 directions}.png` (8)

## Comparison sheet

`art_generated/cat_angle_ab.html` (gitignored derived output; regenerate with
`python tools/art_review/build_cat_angle_ab_sheet.py`) -- old low-top-down
frames beside new side-view frames at 1x/2x, on a tiled office-floor strip
(`godot/assets/office_floor/tilesets/floor_concrete.png` interior tile), with
animated walk-cycle players for old vs new.

## A/B references (the "old" side of the sheet)

- Old cat1 walk: `art_source/pixellab_2026-07-16/cat_walk_cat1/` (68x68, low top-down)
- Old cat1 stills: `art_source/pixellab_2026-07-16/15-Cat1-singed-tabby_*.png` (68x68)
- Old cat_black stills: `art_source/pixellab_2026-07-19/characters/cat_black/rotations/` (92x92, low top-down)

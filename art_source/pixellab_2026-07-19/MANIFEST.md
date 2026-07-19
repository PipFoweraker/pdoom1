# Pixellab volume generation -- 2026-07-19

Generated via the pixellab MCP to fill the visually-empty office/lab. Grounded in the
locked style from `docs/art/reviews/2026-07-17-overnight-sweep.md` +
`docs/art/PALETTE_AND_DOOM_INTENSITY.md`:

> warm-grime base + heavy-outline heft + deeper shadow, view-locked
> (straight-on/centered) to fix rotation; muted teal-olive-slate palette with warm
> amber as the only saturated accent; screens clearly powered/glowing.

Common prompt suffix on props: *heavy black outline, deep shadow beneath, straight-on
centered symmetrical view-locked, warm-grime lived-in office, muted teal-olive-slate
palette, warm amber accent only.*

Generation params (props / `create_map_object`): view `high top-down`, `high detail`,
`detailed shading`, `single color outline`, transparent bg. Sizes vary per object
(48-144px). One roll each (spares are the tier/variant siblings, not repeat rolls) --
re-roll the weak ones in the review tool.

Tilesets (`create_topdown_tileset`): 32px Wang tiles, `high top-down`, `selective
outline`, `medium shading/detail`. Floors are seamless single-material (lower==upper,
transition 0); walls likewise (the terrain-transition wall variants timed out server-side
and were refired as seamless). Each tileset = `<name>.png` (tile atlas) + `<name>.json`
(Wang metadata for Godot autotiling).

Characters (`create_character`): standard mode, 8 directions, `low top-down`, size 64
(~92px canvas), `single color black outline`, `high detail`. Humanoids + quadruped cats.
Each character = a folder of 8 rotation PNGs (`rotations/{south,east,...}.png`).

NOTE: pixellab map objects auto-delete after 8h; all assets were downloaded to disk here.
The review tool picks these up from `art_source/`.

## Totals
- **48 props** (`props/`) -- office/lab furniture + compute + break-room + decor, in
  scummy/decent/mega tiers where relevant.
- **5 seamless tilesets** (`tilesets/`) -- 3 floors + 2 walls, each a png tile-atlas +
  a json Wang metadata file for Godot autotiling.
- **10 characters** (`characters/`) -- 8 humanoids + 2 quadruped cats, 8 rotation PNGs each
  (80 sprite PNGs).
- **133 PNGs total.** ~96 pixellab generations spent (balance 1591 -> 1495 remaining).

One roll per subject (the "spares" are the tier/variant siblings). Weak ones to re-roll in
the review tool; a few small/simple objects (desk_lamp, floor_lamp, exit_sign, office_phone,
wall_decent tileset) came back sparse and are the first re-roll candidates.

Known re-roll/reruns during this batch: the two office cats and eccentric_genius failed
once with "heavy load" and were refired; the terrain-transition wall tilesets timed out
server-side and were refired as seamless single-material walls.


## Full generated asset list

### Props (props/) -- 48 objects
- armchair_1.png
- bookshelf_1.png
- box_stack_1.png
- cable_spool_1.png
- cardboard_box_1.png
- chair_decent_1.png
- chair_mega_1.png
- chair_scummy_1.png
- coat_rack_1.png
- coffee_machine_1.png
- corkboard_1.png
- couch_waiting_1.png
- desk_decent_1.png
- desk_lamp_1.png
- desk_mega_1.png
- desk_scummy_1.png
- exit_sign_1.png
- filing_cabinet_1.png
- filing_cabinet_tall_1.png
- fire_extinguisher_1.png
- floor_lamp_1.png
- kitchen_bench_decent_1.png
- kitchen_bench_scummy_1.png
- laptop_1.png
- microwave_1.png
- mini_fridge_1.png
- monitor_doomcurve_1.png
- monitor_dual_1.png
- monitor_mega_1.png
- monitor_single_1.png
- office_phone_1.png
- pc_mega_1.png
- pc_scummy_1.png
- plant_dead_1.png
- plant_small_1.png
- plant_tall_1.png
- printer_mega_copier_1.png
- printer_small_1.png
- recycling_bin_1.png
- server_cluster_mega_1.png
- server_rack_single_1.png
- snack_table_1.png
- standing_whiteboard_1.png
- trash_can_1.png
- wall_clock_1.png
- water_cooler_1.png
- whiteboard_blank_1.png
- whiteboard_equations_1.png

### Tilesets (tilesets/) -- 5 seamless Wang sets (png atlas + json)
- floor_carpet_1.png (+ floor_carpet_1.json)
- floor_concrete_1.png (+ floor_concrete_1.json)
- floor_lino_1.png (+ floor_lino_1.json)
- wall_decent_1.png (+ wall_decent_1.json)
- wall_scummy_1.png (+ wall_scummy_1.json)

### Characters (characters/) -- 10 characters, 8 rotations each
- cat_black/ (8 rotation pngs)
- cat_tabby/ (8 rotation pngs)
- eccentric_genius/ (8 rotation pngs)
- founder/ (8 rotation pngs)
- researcher_labcoat/ (8 rotation pngs)
- worker_blouse_f/ (8 rotation pngs)
- worker_cardigan_older/ (8 rotation pngs)
- worker_headphones_young/ (8 rotation pngs)
- worker_hoodie_m/ (8 rotation pngs)
- worker_shirt_glasses_m/ (8 rotation pngs)

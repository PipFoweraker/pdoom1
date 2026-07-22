# Re-roll run -- 2026-07-21 (approved queue execution)

Execution of the **Re-roll work queue** in
`docs/art/reviews/SWEEP_REVIEW_2026-07-17.md` after Pip approved the Rulings
(unifying principle "Doom is a layer, not a repaint", style lock, 7 rulings) and
greenlit the queue on 2026-07-21. Assets land under
`art_source/pixellab_2026-07-21-rerolls/<group>/`; see that folder's `MANIFEST.md`
for the full id<->file table.

- Pipeline: pixellab MCP. Tools per category matched the original batch
  (`tools/art_review` + `art_source/pixellab_2026-07-17/reroll/MANIFEST.md`):
  props/windows/founder/cosmetics -> `create_map_object`; cats/characters ->
  `create_character`; floor/wall surfaces -> `create_topdown_tileset`.
- Style lock applied to every prompt: warm-grime base + heavy black outline +
  deep contrast shadows, view-locked straight-on/centered, monitors powered/glowing,
  no keyboard/mouse unless a full workstation.
- Credits: pixellab subscription generations. Start 577 used / 1423 remaining;
  after this run 656 used / 1344 remaining = **79 generations spent**. $0.00 cash
  credits used (subscription covers it). Balance was never a constraint.
- Download mechanism: pixellab `get_*` returns stable download URLs
  (`/mcp/map-objects/<id>/download`, `/mcp/tilesets/<id>/image|/metadata`, and
  per-direction character rotation URLs). No auth needed; saved directly to disk
  and PNG-validated. Rate cap observed: ~4-5 concurrent jobs, so work ran in
  batches of ~4.

## Groups completed

### Group 1 -- Tilesets via create_topdown_tileset (seamless, distinct per-surface material)
Root-cause fix: the sweep floors/walls were generated as map objects (single
object on transparent bg), never as tiling textures. Regenerated as Wang tilesets
(32x32, transition 0.25, low top-down, single-colour outline, detailed shading),
distinct material prompt per surface. Each yields `<key>.png` (atlas) +
`<key>.metadata.json`.

| surface | tileset id |
|---|---|
| floor_concrete | 9f3e4695-e0e2-450e-9e9f-d553ac894abd |
| floor_lino | 6ab69350-6353-439d-99fb-e24c4f727aa7 |
| floor_carpet | f7984b8c-8776-4b13-bac7-ab91e7dda202 |
| wall_scummy | 6a5632a9-e56a-432c-8433-c01b784ac472 |
| wall_decent | 3bde872f-9867-4a44-b239-3c2342aaf8ff |

### Group 2 -- Windows as frame + swappable sky
Applied the layer principle: static frame (specify windowsill + edging, hollow
centre) rendered SEPARATELY from the sky/weather panel, to be composited in-engine
per weather/doom state. All 120x96, side view. Doomy sky pulled band-3 palette
(deep aubergine + blood-red + creeping violet) from PALETTE_AND_DOOM_INTENSITY.md.
- window_frame_1/2/3: 4d91830b / 3778d4cb / 56f68de6
- sky_clear_1/2: 517f7ca6 / d51a2c23
- sky_storm_1/2: f1ac4ae9 / 4392b3d1
- sky_doomy_1/2: e1925248 / a18f248e

NOTE for in-engine wiring: the generated frames read as frames but their centre
is light/near-opaque, not fully transparent. Compositing must colour-key/mask the
frame centre so the sky layer shows through (or author the frame mask in-engine).

### Group 3 -- Doom assets via the intensity ladder (base identity stable, doom = surrounding FX + collar/emblem glow)
Cats kept a black base identity; doom expressed as violet eye/collar glow +
aura, per the unifying principle (not a repaint). Quadruped cat template, low
top-down, 8 directions each; saved as `<key>_<roll>.png` (south) + `_<dir>.png`.
- cat_eldritch_1/2: ca20613e / d13a61ca
- cat_purple_1/2: 821531d5 / c82bf943 (roll 2 re-run after an initial heavy-load failure)
The doomy sky (Group 2) also serves this group's `window_weather_doomy` / `sky_doomy`.

### Group 4 -- Founder via back-framing + 3/4 reference
Reframed per ruling 4: the CHAIR is the hero, seen from behind, a seated figure's
silhouette just cresting the backrest; plus a 3/4 reference-sheet variant. 96x120.
- founder_back_1/2: 91cee793 / ce5b8bc6
- founder_threequarter_1: 3f0dcbae

### Group 5 -- Kitchen bench as wall-integrated counter
Per ruling 6: wall-snapping counter segment with kitchenette signifiers (sink,
teabag jar, instant-coffee pot, sugar packets, dishwasher, microwave), explicitly
NO office-desk drawers, not plant-overloaded. 128x96.
- kitchen_bench_scummy_1/2: 4d994b39 / a06e7201
- kitchen_bench_decent_1/2: 17b8d152 / bcf3a79f

### Group 6 -- Chairs differentiated (decent != mega)
Per ruling 7: chair_decent = no armrests, small round backrest, dull green /
plasticky office-blue; chair_mega = fancier, not over-lit/regal. 96x104.
- chair_mega_1/2: db9c2330 / ca0d7ffb
- chair_decent_1/2 (blue, green): 8db9e7d3 / 1b29e930

### Group 9 -- Clean single-variance re-rolls (style locked, view locked)
Straight re-runs of the same prompt, view-locked. trash re-rolled explicitly as
recycling; desk_mega_screen re-rolled as screen-only (no desk); monitor_mega_startup
as two chunky CRTs.
- desk_mega_1/2: dd620090 / 98a7c2c3
- monitor_mega_1/2: ab0fc620 / ba5a3025
- monitor_mega_startup_1/2: 236847e0 / c7524760
- pc_mega_1/2: 845a7223 / edbff351
- server_cluster_mega_1: 2e8b4ca7
- filing_cabinet_1: b2fd909a
- printer_1/2: 6d5fee5c / 59e74f42
- trash_recycling_1/2: 6236c0a5 / 46769bcd
- meeting_table_1/2: 22b69955 / e3cdcddb
- water_cooler_1/2: 9f1b246f / 8f5dfbe6
- coat_rack_1/2: 59cb02ab / 42cd63a8
- desk_mega_screen_1: 86afa0cf
- door_scummy_1/2: afcb43e1 / 16f38e04

### Group 10 -- Characters (re-roll generic/flat, style locked)
Humanoid, low top-down, 8 directions each. cast_eccentric_genius done as the
FEMALE variant Pip requested.
- cast_eccentric_genius_f_1: 6172cd82
- cast_woman_lead_older_1: 340a796f
- cast_black_woman_young_1: 6ee72591
- cast_wheelchair_user_1: 1abce614 (re-run after an initial heavy-load failure)

### Group 11 -- Cosmetics (re-roll rejected rolls, style locked)
Accessory items on plain bg, side view.
- hat_medium_1/2: 8bcc1df4 / 3d3b735b
- hat_sports_1/2: 4ec67b61 / b12e9727
- lab_coat_1/2: 358ebc6e / f381f1fa

### Bonus (round-2 cell with an obvious corrected approach)
- office-library **bookshelf** ("[RE-ROLLING] laminate / office-shelfy, less wood"):
  re-rolled as grey laminate/metal office shelving with binders + box files, no wood.
  bookshelf_1/2: 5b717d36 / e1c101b2. (Filed under objects/.)

## Groups deferred (not a pixellab job -- per the rulings themselves)

### Group 7 -- Icons: OUT of pixellab (ruling 5) AND round-2 override
Ruling 5 pulls icons out of pixellab onto the gpt-image-1 pipeline
(`tools/assets/generate_images.py`, needs an OpenAI key). Not run here: (a) wrong
pipeline for this pixellab task, (b) round-2 verdicts REVERSE the icon_doom
direction entirely -- Pip: "abandon this direction, too skully... agents to
reconsider entire approach". So icon_doom is now blocked on a NEW approach ruling
(see below), and icon_compute should be produced on the gpt-image-1 pipeline in a
separate pass, not pixellab.

### Group 8 -- UI chrome/filler: author in-engine or create_ui_asset (ruling 5)
ui_panel_frame / ui_texture_tile / ui_indicator_dot were rejected precisely
because `map_object` is the wrong tool. Ruling says author in-engine (9-slice/CSS)
or via `create_ui_asset`. This is an engine-authoring task, not an art-generation
re-roll, so it is intentionally NOT regenerated here.

## Needs approach ruling (round-2 re-roll cells with no obvious corrected approach)

The round-2 export added 16 re-roll verdicts. The ones that map cleanly to an
existing queue group were executed within that group (meeting_table roll 1 ->
Group 9; wall_decent roll 2 -> Group 1; cast_wheelchair_user roll 3 -> Group 10;
cat_eldritch roll 4 -> Group 3; bookshelf -> bonus above). The remainder have no
corrected-approach text in the rulings and were NOT freestyled:

- **icon_doom roll 1/2/3** -- Pip rejected the entire skull direction ("too
  skully, needs to be more icon-like"; "directionally away from this strongly";
  "fine for a death metal game, not our vibe... reconsider entire approach"). The
  Group-7 "robot-flavoured skull" ruling is now contradicted. Needs a fresh doom-icon
  concept ruling before regeneration.
- **Style-matrix cells** (baseline / desk, baseline / monitor, futurepunk / desk,
  futurepunk / monitor, heavy-outline / character, moody-contrast / desk,
  moody-contrast / monitor) -- these are style-exploration matrix cells. Style is
  already locked to warm-grime, so re-rolling losing-style cells has no target
  approach; they are effectively moot unless Pip wants specific assets rebuilt in
  the locked style.
- **era-ladder e1_startup** ("top of monitor missing, has keyboard") -- belongs to
  the 2026-07-16-era-ladder batch, outside every queue group; needs an era-ladder
  re-roll ruling.

## Viewer dataset

`tools/art_review/build.py` hardcodes the re-roll source path to
`art_source/pixellab_2026-07-17/reroll` and a fixed cell-id scheme. The new
`pixellab_2026-07-21-rerolls/` tree is NOT auto-discovered, so `build.py` was NOT
run -- wiring it in is a non-trivial build.py change (new batch discovery +
cell-id scheme + manifest entries). The next review round needs a dataset update
to surface these assets in the viewer.

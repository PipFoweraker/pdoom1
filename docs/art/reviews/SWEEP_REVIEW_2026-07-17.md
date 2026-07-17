# P(Doom)1 -- Sweep Review 2026-07-17

> Source of truth for Pip's verdicts on the 2026-07-17 pixel-art sweep + re-roll
> batches (pixellab office/character/prop assets). Verbatim capture of Pip's
> review, followed by Claude's design rulings and a held re-roll work queue.
> Cell ids match the `tools/art_review` viewer scheme
> (`sweep:<category>:<key>:<roll>`, `reroll:<category>:<key>:<roll>`,
> `<batch-id>:<style>__<subject>`). This markdown is authoritative; the viewer's
> `verdicts.json` is a best-effort mirror.

## Style direction

Winning direction: warm-grime base + heavy-outline heft + deeper shadow,
view-locked (symmetrical/straight-on/centered) to fix rotation. Monitors are the
weak subject (composition); keep screens clearly powered/glowing.

## Winning styles

Winning style: 2026-07-16-style-matrix warm-grime.

## Keep

- desk_mega roll 1 (sweep:props:desk_mega:1) -- good, unsure if shadow under desk hurts transparency; likes detail/texture; undecided on game-responsive monitors (later UI update)
- desk_mega roll 4 (sweep:props:desk_mega:4) -- second favourite
- monitor_mega roll 1 (sweep:props:monitor_mega:1)
- monitor_mega roll 2 (sweep:props:monitor_mega:2)
- pc_mega roll 4 (sweep:props:pc_mega:4) -- keep as default so we can move on
- server_cluster_mega roll 2 (sweep:props:server_cluster_mega:2) -- good colouring
- server_cluster_mega roll 3 (sweep:props:server_cluster_mega:3) -- good density and intensity
- kitchen_bench_decent roll 3 (sweep:props:kitchen_bench_decent:3) -- nice
- filing_cabinet roll 1 (sweep:props:filing_cabinet:1)
- filing_cabinet roll 3 (sweep:props:filing_cabinet:3)
- printer roll 3 (sweep:props:printer:3) -- nice
- printer roll 4 (sweep:props:printer:4) -- keep as early-era
- trash_can roll 1 (sweep:props:trash_can:1) -- good
- trash_can roll 4 (sweep:props:trash_can:4) -- start era keep
- meeting_table roll 3 (sweep:props:meeting_table:3) -- dramatic lighting is great, want more samples of it
- water_cooler_reroll roll 3 (sweep:props:water_cooler_reroll:3)
- coat_rack_reroll roll 1 (sweep:props:coat_rack_reroll:1)
- coat_rack_reroll roll 2 (sweep:props:coat_rack_reroll:2)
- floor_lino roll 1 (sweep:environment:floor_lino:1)
- wall_scummy roll 3 (sweep:environment:wall_scummy:3)
- wall_scummy roll 4 (sweep:environment:wall_scummy:4)
- door_scummy roll 4 (sweep:environment:door_scummy:4)
- door_scummy roll 1 (sweep:environment:door_scummy:1)
- door_decent roll 3 (sweep:environment:door_decent:3)
- door_decent roll 4 (sweep:environment:door_decent:4)
- window_weather_clear roll 4 (sweep:environment:window_weather_clear:4)
- window_weather_clear roll 1 (sweep:environment:window_weather_clear:1) -- lighting direction maybe weird, good asset
- window_weather_storm roll 4/3/1 (sweep:environment:window_weather_storm:4,3,1) -- good defaults, needs rework
- window_weather_doomy roll 3 (sweep:environment:window_weather_doomy:3) -- not good but use as default for testing while we iterate
- cat_eldritch roll 4 (sweep:cats_body_type_quadruped_template_cat:cat_eldritch:4) -- keep for baseline
- cat_purple roll 1 (sweep:cats_body_type_quadruped_template_cat:cat_purple:1)
- base_worker_restyle roll 1 (sweep:characters_use_create_character:base_worker_restyle:1) -- best of an OK bunch, rest feel a little under
- base_worker_restyle roll 4 (sweep:characters_use_create_character:base_worker_restyle:4)
- cast_black_woman_young roll 1 (sweep:characters_use_create_character:cast_black_woman_young:1)
- cast_woman_lead_older roll 1 (sweep:characters_use_create_character:cast_woman_lead_older:1)
- cast_wheelchair_user roll 4 (sweep:characters_use_create_character:cast_wheelchair_user:4)
- founder_silhouette roll 3 (sweep:characters_use_create_character:founder_silhouette:3) -- all bad but tolerate for testing. Wrong orientation. Should mostly see chair and silhouette; chair is the visual focus
- hat_medium roll 3/1 (sweep:cosmetics_overlays:hat_medium:3,1)
- hat_sports roll 4 (sweep:cosmetics_overlays:hat_sports:4)
- lab_coat roll 3/4 (sweep:cosmetics_overlays:lab_coat:3,4)
- lanyard_badge roll 2 (sweep:cosmetics_overlays:lanyard_badge:2)
- lanyard_badge roll 3 (sweep:cosmetics_overlays:lanyard_badge:3) -- feels advanced/doomy, maybe keep/recycle for that
- headphones roll 3/1/2 (sweep:cosmetics_overlays:headphones:3,1,2) -- like all of these, want variants on characters if that works
- cat_purple roll 3 (reroll:cats:cat_purple:3) -- eyes good, maybe too bright, agree and move on
- cat_purple roll 4 (reroll:cats:cat_purple:4) -- excellent pose, ears weird; experiment keeping cat same base colour and changing effects around it with doom colouring instead; colour range good for effects but maybe not the cat itself
- cast_eccentric_genius roll 2 (reroll:characters:cast_eccentric_genius:2) -- would love a female version, might scan better as a woman, otherwise same
- founder roll 1 (reroll:founder:founder:1) -- great, also want one facing the other way, maybe 3/4 like reference sheets
- founder roll 3 (reroll:founder:founder:3) -- great
- icon_compute roll 3 (reroll:icons:icon_compute:3)
- chair_decent roll 3/1 (reroll:objects:chair_decent:3,1)
- chair_mega roll 2/1 (reroll:objects:chair_mega:2,1) -- fine
- coat_rack roll 3/2/1 (reroll:objects:coat_rack:3,2,1)
- desk_mega_screen roll 2/3 (reroll:objects:desk_mega_screen:2,3)
- filing_cabinet roll 1 (reroll:objects:filing_cabinet:1) -- check angle, like this visual
- filing_cabinet roll 2 (reroll:objects:filing_cabinet:2) -- if we keep a scummy version, like this
- kitchen_bench_decent roll 2/4 (reroll:objects:kitchen_bench_decent:2,4)
- kitchen_bench_scummy roll 1/2 (reroll:objects:kitchen_bench_scummy:1,2)
- meeting_table roll 2/4/3 (reroll:objects:meeting_table:2,4,3)
- monitor_mega_startup roll 2/1/3 (reroll:objects:monitor_mega_startup:2,1,3)
- pc_mega roll 1/3 (reroll:objects:pc_mega:1,3)
- printer roll 2/3/4 (reroll:objects:printer:2,3,4)
- server_cluster_mega roll 2/1 (reroll:objects:server_cluster_mega:2,1)
- server_cluster_mega roll 4 (reroll:objects:server_cluster_mega:4) -- maybe rotate 90deg or check lighting (server-rack lighting rules could differ)
- trash_recycling roll 4 (reroll:objects:trash_recycling:4) -- amazing
- trash_recycling roll 1 (reroll:objects:trash_recycling:1) -- pretty good
- trash_recycling roll 2 (reroll:objects:trash_recycling:2) -- good side view
- water_cooler roll 1 (reroll:objects:water_cooler:1) -- excellent
- floor_carpet roll 1 (reroll:tilesets:floor_carpet:1)
- sky_clear roll 1/3 (reroll:windows:sky_clear:1,3)
- sky_doomy roll 1/2/4 (reroll:windows:sky_doomy:1,2,4)
- sky_storm roll 1/4 (reroll:windows:sky_storm:1,4)
- window_frame roll 1/2/3 (reroll:windows:window_frame:1,2,3)

## Maybe

- desk_mega roll 3 (sweep:props:desk_mega:3) -- nothing spectacular; desktop bg nice but desk weirdly symmetrical (2 grey then 2 red objects)
- chair_decent roll 4/2 (sweep:props:chair_decent:4,2)
- monitor_mega roll 3 (sweep:props:monitor_mega:3) -- has keyboard+mouse; be explicit whether it has them
- kitchen_bench_scummy roll 2/3 (sweep:props:kitchen_bench_scummy:2,3) -- boundaries on the side; clearer architectural/positioning decisions; design/philosophy check
- kitchen_bench_decent roll 1 (sweep:props:kitchen_bench_decent:1)
- printer roll 2 (sweep:props:printer:2) -- check lighting and positioning
- meeting_table roll 2 (sweep:props:meeting_table:2)
- water_cooler_reroll roll 1 (sweep:props:water_cooler_reroll:1)
- coat_rack_reroll roll 3 (sweep:props:coat_rack_reroll:3)
- floor_carpet roll 1 (sweep:environment:floor_carpet:1)
- floor_lino roll 4 (sweep:environment:floor_lino:4)
- floor_concrete roll 1/2/3/4 (sweep:environment:floor_concrete:1-4) -- Claude check if this is what it is meant to be, even vaguely
- wall_scummy roll 1 (sweep:environment:wall_scummy:1) -- defer to Claude if this is what we want
- wall_decent roll 3 (sweep:environment:wall_decent:3) -- maybe as something else, not a wall segment
- door_scummy roll 3 (sweep:environment:door_scummy:3)
- door_decent roll 1 (sweep:environment:door_decent:1) -- lighting weird
- door_decent roll 2 (sweep:environment:door_decent:2) -- too visually flat
- window_weather_clear roll 3 (sweep:environment:window_weather_clear:3)
- cat_purple roll 4 (sweep:...:cat_purple:4) -- keep for playtesting
- cast_black_woman_young roll 3 (sweep:...:cast_black_woman_young:3) -- good overall but accentuate or de-accentuate belly/lighting around tummy
- cast_black_woman_young roll 4 (sweep:...:cast_black_woman_young:4)
- cast_woman_lead_older roll 3 (sweep:...:cast_woman_lead_older:3)
- hat_sports roll 2 (sweep:cosmetics_overlays:hat_sports:2)
- lanyard_badge roll 1 (sweep:cosmetics_overlays:lanyard_badge:1)
- lanyard_badge roll 4 (sweep:cosmetics_overlays:lanyard_badge:4) -- feels chunky; standby for special-access asset
- headphones roll 4 (sweep:cosmetics_overlays:headphones:4)
- ui_panel_frame roll 4 (sweep:ui_filler_map_object:ui_panel_frame:4) -- keep in case we want something ornate, unsure these generations worked well
- ui_texture_tile roll 4 (sweep:ui_filler_map_object:ui_texture_tile:4)
- ui_texture_tile roll 3 (sweep:ui_filler_map_object:ui_texture_tile:3) -- at least something that might tile shittily
- ui_indicator_dot roll 2/1 (sweep:ui_filler_map_object:ui_indicator_dot:2,1)
- icon_compute roll 4 (sweep:ui_filler_map_object:icon_compute:4) -- slightly computer-chip-ish, under-specified
- icon_doom roll 3 (sweep:ui_filler_map_object:icon_doom:3) -- best artistically, still too human
- icon_doom roll 1 (sweep:ui_filler_map_object:icon_doom:1) -- too purple and teethy
- cat_purple roll 1 (reroll:cats:cat_purple:1) -- egyptian/alienish
- cast_eccentric_genius roll 1 (reroll:characters:cast_eccentric_genius:1) -- bit frazzled, too close to stereotype
- founder roll 2 (reroll:founder:founder:2) -- only one hand is good; if cat eyes in the midriff it would be nearly perfect
- founder roll 4 (reroll:founder:founder:4) -- like the colour
- icon_compute roll 2/1 (reroll:icons:icon_compute:2,1)
- chair_decent roll 4 (reroll:objects:chair_decent:4)
- chair_mega roll 3 (reroll:objects:chair_mega:3) -- bit bright
- coat_rack roll 4 (reroll:objects:coat_rack:4)
- filing_cabinet roll 4 (reroll:objects:filing_cabinet:4) -- meh
- server_cluster_mega roll 3 (reroll:objects:server_cluster_mega:3) -- lighting good, angle+foreshortening weird
- trash_recycling roll 3 (reroll:objects:trash_recycling:3) -- average
- water_cooler roll 3 (reroll:objects:water_cooler:3) -- quite angled view
- floor_lino roll 1 (reroll:tilesets:floor_lino:1)
- wall_decent roll 1 (reroll:tilesets:wall_decent:1)
- wall_scummy roll 1 (reroll:tilesets:wall_scummy:1) -- see notes; if we keep, keep; else re-roll approx half to work variation into tiling sets
- sky_storm roll 2/3 (reroll:windows:sky_storm:2,3)

## Re-roll

- desk_mega roll 2 (sweep:props:desk_mega:2) -- single-colour screen less attractive now; least interesting for future screen-responsiveness
- chair_mega roll 1 -- fancier; roll 2 -- needs fancier; roll 3 -- weirdly over-lit (lower half good shadows); roll 4 -- very flat, needs fancier
- chair_decent roll 1 -- differentiate from chair_mega; roll 3 -- differentiate: could lack armrests, be more circular, smaller/less backrest, dull green or unpleasant plasticky office-carpet blue
- monitor_mega roll 4 (sweep:props:monitor_mega:4) -- angling too strong; re-roll as startup-mode mega monitor = 2 large chunky CRTs
- pc_mega roll 1 (sweep:props:pc_mega:1) -- unsure how displayed in-game; consider orientation/display-angle vs neighbours; also has office-plant leaves over it
- pc_mega roll 2/3 (sweep:props:pc_mega:2,3) -- angle consistency check
- server_cluster_mega roll 1 (sweep) -- looks like a city block, no cables; roll 4 -- too solid visually
- kitchen_bench_scummy roll 1 (sweep) -- consider size/positioning vs others; roll 4 -- boundaries on side, architectural/philosophy check
- kitchen_bench_decent roll 2 (sweep) -- no potplants; roll 4 -- looks like a desk, no potplants
- filing_cabinet roll 2 (sweep) -- too angly; roll 4 -- lacking depth in shadows, boring, make nicer or worse
- printer roll 1 (sweep) -- re-roll
- trash_can roll 3 (sweep) -- re-roll but make explicitly recycling; roll 2 -- re-roll, neater and explicitly recycling
- meeting_table roll 4 (sweep) -- too thin
- water_cooler_reroll roll 2/4 (sweep)
- coat_rack_reroll roll 4 (sweep)
- floor_carpet roll 2 (sweep) -- why is this in a circle lol; roll 3 -- too small; roll 4 -- indistinguishable
- floor_lino roll 2/3 (sweep) -- did not work as a texture
- wall_scummy roll 2 (sweep) -- re-roll, did not ask for the circular downlight
- wall_decent roll 1/4 (sweep) -- this ain't no wall segment lol
- door_scummy roll 2 (sweep)
- window_weather_clear roll 2 (sweep) -- no windowsill/edging, deliberately call or dont call for these
- window_weather_storm roll 2 (sweep) -- no frames. Claude: do we actually want frames and backgrounds rendered separately?
- window_weather_doomy roll 1/2/4 (sweep) -- doomy ones need more style-guide input and significant rework, probably mechanically
- cat_eldritch roll 3 (sweep) -- needs more Visual Doom; do we need a universal philosophy/intensity reference to modify/define asset differences? @Claude
- cat_eldritch roll 2/1 (sweep) -- more glow, maybe collar and emblem to highlight
- cat_purple roll 2 (sweep) -- too smiley; roll 3 -- head too big
- cast_black_woman_young roll 2 (sweep)
- cast_woman_lead_older roll 2/4 (sweep)
- cast_wheelchair_user roll 2 (sweep) -- too flat visually
- cast_eccentric_genius roll 1/2/3/4 (sweep) -- too generic
- founder_silhouette roll 1/2/4 (sweep) -- Claude, weirdly called for and incoherent, spend time thinking how to remedy all of these
- hat_medium roll 2/4 (sweep); hat_sports roll 3/1 (sweep); lab_coat roll 2/1 (sweep)
- ui_panel_frame roll 3 -- angled; roll 2 -- ew; roll 1 -- poorly defined
- ui_texture_tile roll 2 -- these are objects, probably wrong prompt or image model; roll 1 -- ew
- ui_indicator_dot roll 3/4
- icon_compute roll 3/2 -- bad; roll 1 -- bad, generic, off-brand, maybe start thinking colour palettes
- icon_doom roll 2 -- bad, try a robot-flavoured skull instead; roll 4 -- pity-inducing, too much yellowing and anatomy
- cat_purple roll 2 (reroll:cats) -- a bit washed out
- cast_eccentric_genius roll 3 (reroll) -- too flat; roll 4 -- meh
- icon_compute roll 4 (reroll:icons)
- icon_doom roll 4 (reroll:icons) -- all a bit Heavy Metal magazine cover
- chair_decent roll 2 (reroll:objects)
- chair_mega roll 4 (reroll:objects) -- bit too glowing, bit too regal
- desk_mega_screen roll 1/4 (reroll:objects) -- has a desk, bad
- filing_cabinet roll 3 (reroll:objects) -- meh
- kitchen_bench_decent roll 3 (reroll:objects) -- looks like an office desk; want something integrable with an office wall; roll 1
- kitchen_bench_scummy roll 3/4 (reroll:objects) -- too many plants/objects; want jar of teabags, pot of instant coffee, sugar packets, dishwasher+sink signifiers, maybe microwave on bench/floating shelf; drawers look like office-desk drawers, avoid
- meeting_table roll 1 (reroll:objects) -- too many chairs, more like a grand+weird meeting table
- monitor_mega_startup roll 4 (reroll:objects) -- too inward-facing
- printer roll 1 (reroll:objects)
- pc_mega roll 4/2 (reroll:objects) -- too angly
- water_cooler roll 2 (reroll:objects) -- meh; roll 4 -- looks like dildo
- floor_concrete roll 1 (reroll:tilesets) -- all patterns have same wiggly tile-ness in different colours; should be more individual variation
- sky_clear roll 4/2 (reroll:windows)
- window_frame roll 4 (reroll:windows)

## Other notes

Style matrix + office-library observations.

- baseline/desk (2026-07-16-style-matrix:baseline__desk) -- probably favourite desk but a little rotated; likes clutter/objects
- baseline/monitor -- one of the weakest monitors, dull/unpowered; flavour fine
- baseline/character -- good character, good colour identity, professional attire
- futurepunk/desk -- a little too bright/shiny; potted plant+wastepaper bin nice
- futurepunk/monitor -- poor composition
- heavy-outline/desk -- satisfying heft; objects have good visual distinction
- warm-grime/desk -- clutter+coziness+object on PC tower all excellent
- warm-grime/monitor -- good, but looks like a CD player coming out of it; acceptable first-pass
- warm-grime/character -- glasses render weirdly, otherwise good
- moody-contrast/desk -- angling weird, has a chair, wouldnt work as single asset; likes increased shadows/moodiness
- moody-contrast/monitor -- bit of a miss
- moody-contrast/character -- likes expression/tone, a little cynical, more individualistic; likes shadows+mood tuning
- office-library chair -- looks small vs others, OK; a little too modern for a starting chair
- office-library bookshelf -- looks more home than office; less wood, laminate or more office-shelfy
- office-library whiteboard -- good
- office-library water_cooler -- extremely good; maybe too angled/wrong perspective direction
- office-library plant -- excellent
- office-library server_rack -- extremely excellent; direction/lighting maybe slightly wrong/wrong direction, unclear
- office-library couch -- excellent
- office-library coat_rack -- excellent; shoes neater/less domestic; office coatrack a bit neater
- meeting_table roll 1 (sweep:props) -- chairs too high
- wall_decent roll 2 (sweep:environment) -- this ain't no wall segment lol
- base_worker_restyle roll 2 (sweep) -- head a little unclear; roll 3 -- looks a bit angry
- cast_wheelchair_user roll 1 (sweep) -- looks kinda cranky; roll 3 -- meh

## Rulings (Claude)

### Unifying principle -- "Doom is a layer, not a repaint."

The base asset is rendered doom-neutral and stable; doom intensity is a SEPARATE
additive layer (glow/aura, sky-swap, colour-grade), never baked into the base.
This resolves many rejects at once:

- Cat keeps its base colour with doom effects AROUND it.
- Windows split into a static frame + a swappable sky.
- Monitors stay powered/glowing as a light layer.
- Eldritch = more glow, not more repaint.

### Style lock

warm-grime base + heavy-outline heft + deeper shadow. View-locked: straight-on /
centered / symmetrical orthographic (this kills the "too angly / wrong
orientation" rejects). Exceptions only where explicitly wanted (e.g. founder 3/4
reference-sheet). Monitors always powered/glowing; default NO keyboard/mouse
peripherals unless the asset is explicitly a full workstation.

### Rulings on Pip's tagged questions

1. **Floors/walls (floor_concrete, floor_lino, wall_*):** these failed because
   they were generated as pixellab MAP OBJECTS (single object on transparent bg),
   not tileable textures. That is the root cause of "did not work as a texture",
   "same wiggly-ness in different colours", and "this ain't no wall segment".
   Fix: regenerate via `create_topdown_tileset` (seamless tiling) with a DISTINCT
   material prompt per surface.
2. **Windows:** YES, separate the FRAME (static architectural sprite; specify
   windowsill + edging explicitly) from the SKY/WEATHER (swappable background
   layer driven by doom). Combinatorially cheaper and enables weather
   transitions. Direct application of the layer principle.
3. **Doom intensity reference:** YES needed. Upgrade
   `docs/art/PALETTE_AND_DOOM_INTENSITY.md` into an operational ladder (per level:
   glow hex, glow amount, ambient, distortion) that every doomy/eldritch/weather
   prompt references. Cat keeps base identity; doom via surrounding FX +
   collar/emblem glow.
4. **founder_silhouette:** the prompt asked for an abstract "silhouette" ->
   incoherent output. Reframe so the CHAIR is the hero, seen from BEHIND
   (back-framing), a figure's silhouette just cresting the backrest; add a 3/4
   reference-sheet angle variant. Matches the existing operator back-framing
   direction.
5. **Icons (icon_compute/icon_doom) + UI filler (ui_panel_frame/ui_texture_tile):**
   pull these OUT of pixellab. `map_object` is the wrong tool for icons/UI
   chrome/tileable textures. Icons -> gpt-image-1 pipeline (`tools/assets`) with a
   locked palette from the hero image; doom icon -> robot-flavoured skull; compute
   icon -> rethink (GPU/stacked-cores glyph, not a literal chip). UI
   panels/textures -> author in-engine (9-slice/CSS) or pixellab
   `create_ui_asset`, not object sweeps.
6. **Kitchen bench:** it is a WALL-INTEGRATED counter segment (snaps to a wall),
   not a free-standing desk. Signifiers: teabag jar, instant-coffee pot, sugar
   packets, sink, dishwasher, optional microwave/floating shelf. NOT office-desk
   drawers; NOT plant-overloaded.
7. **Chairs:** chair_decent must diverge from chair_mega -- no armrests, more
   circular/smaller backrest, dull green or plasticky office-blue. chair_mega =
   fancier but not over-lit or regal.

## Re-roll work queue

HELD pending Pip go. Grouped by the corrected approach from the rulings above.
Keys are the affected asset ids (sweep + reroll batches). Nothing here is
actioned until Pip greenlights the queue.

- **Tilesets via `create_topdown_tileset` (seamless, distinct per-surface material):**
  `sweep:environment:floor_concrete`, `sweep:environment:floor_lino`,
  `sweep:environment:floor_carpet`, `sweep:environment:wall_scummy`,
  `sweep:environment:wall_decent`, `reroll:tilesets:floor_concrete`,
  `reroll:tilesets:floor_lino`, `reroll:tilesets:wall_scummy`,
  `reroll:tilesets:wall_decent`. (floor tiles previously came out as map objects,
  not textures; wall segments came out as objects, not tiling wall.)
- **Windows as frame + swappable sky:** frame = `reroll:windows:window_frame`
  (static, specify windowsill + edging); sky layer =
  `sweep:environment:window_weather_clear/storm/doomy`,
  `reroll:windows:sky_clear/sky_storm/sky_doomy`. Render frame and sky
  separately, composite in-engine per weather/doom state.
- **Doom assets via the intensity ladder (base identity stable, doom = surrounding
  FX + collar/emblem glow):** `sweep:cats_body_type_quadruped_template_cat:cat_eldritch`,
  `sweep:cats_body_type_quadruped_template_cat:cat_purple`,
  `reroll:cats:cat_purple`, `sweep:environment:window_weather_doomy`,
  `reroll:windows:sky_doomy`. Pull glow hex + amount from
  `PALETTE_AND_DOOM_INTENSITY.md` bands.
- **Founder via back-framing + 3/4 reference-sheet:**
  `sweep:characters_use_create_character:founder_silhouette`,
  plus 3/4 angle variants of the kept `reroll:founder:founder` rolls
  (Pip wants founder facing the other way / 3/4).
- **Kitchen bench as wall-integrated counter (kitchenette signifiers, no office
  drawers, not plant-overloaded):** `sweep:props:kitchen_bench_scummy`,
  `sweep:props:kitchen_bench_decent`, `reroll:objects:kitchen_bench_scummy`,
  `reroll:objects:kitchen_bench_decent`.
- **Chairs differentiated (decent != mega):** `sweep:props:chair_mega`,
  `sweep:props:chair_decent`, `reroll:objects:chair_mega`,
  `reroll:objects:chair_decent`. chair_decent: no armrests, more
  circular/smaller backrest, dull green or plasticky office-blue; chair_mega:
  fancier, not over-lit/regal.
- **Icons via gpt-image-1 pipeline (`tools/assets`), not pixellab map_object:**
  `sweep:ui_filler_map_object:icon_compute`,
  `sweep:ui_filler_map_object:icon_doom`, `reroll:icons:icon_compute`,
  `reroll:icons:icon_doom`. doom icon -> robot-flavoured skull; compute icon ->
  GPU/stacked-cores glyph, not a literal chip; locked palette from hero image.
- **UI chrome/filler out of object sweeps (author in-engine or `create_ui_asset`):**
  `sweep:ui_filler_map_object:ui_panel_frame`,
  `sweep:ui_filler_map_object:ui_texture_tile`,
  `sweep:ui_filler_map_object:ui_indicator_dot`.
- **Clean single-variance re-rolls (style locked, just re-run the same prompt
  view-locked):** `sweep:props:desk_mega`, `sweep:props:monitor_mega`,
  `sweep:props:pc_mega`, `sweep:props:server_cluster_mega`,
  `sweep:props:filing_cabinet`, `sweep:props:printer`, `sweep:props:trash_can`
  (make explicitly recycling), `sweep:props:meeting_table`,
  `sweep:props:water_cooler_reroll`, `sweep:props:coat_rack_reroll`,
  `sweep:environment:door_scummy`, `reroll:objects:desk_mega_screen`,
  `reroll:objects:filing_cabinet`, `reroll:objects:meeting_table`,
  `reroll:objects:monitor_mega_startup`, `reroll:objects:pc_mega`,
  `reroll:objects:printer`, `reroll:objects:water_cooler`.
- **Characters (re-roll the generic/flat ones, style locked):**
  `sweep:characters_use_create_character:cast_eccentric_genius`,
  `sweep:characters_use_create_character:cast_woman_lead_older`,
  `sweep:characters_use_create_character:cast_black_woman_young`,
  `sweep:characters_use_create_character:cast_wheelchair_user`,
  `reroll:characters:cast_eccentric_genius` (Pip wants a female variant).
- **Cosmetics (re-roll the rejected rolls, style locked):**
  `sweep:cosmetics_overlays:hat_medium`, `sweep:cosmetics_overlays:hat_sports`,
  `sweep:cosmetics_overlays:lab_coat`.

# Sweep review -- Pip's picks (2026-07-17, overnight sweep of 168 assets)

> Verbatim capture of Pip's Export from the art-review tool. Source of truth for
> re-roll instructions + keeper decisions. Parsed into tools/art_review/verdicts.json
> so the tool preloads it.

## Style direction
Winning direction: warm-grime base + heavy-outline heft + deeper shadow, view-locked (symmetrical/straight-on/centered) to fix rotation. Monitors are the weak subject (composition); keep screens clearly powered/glowing.

## Winning styles
- 2026-07-16-style-matrix: **warm-grime**

## Keep
- desk_mega roll 1 -- good; check desk shadow vs transparency; monitor game-responsiveness is a maybe-later-UI question
- desk_mega roll 4 -- second favourite
- monitor_mega roll 1
- monitor_mega roll 2
- pc_mega roll 4 -- keep as default so we can move on
- server_cluster_mega roll 2 -- good colouring
- server_cluster_mega roll 3 -- good density and intensity
- kitchen_bench_decent roll 3 -- nice
- filing_cabinet roll 1
- filing_cabinet roll 3
- printer roll 3 -- nice
- printer roll 4 -- keep as early-era
- trash_can roll 1 -- good
- trash_can roll 4 -- start-era keep
- meeting_table roll 3 -- dramatic lighting great, want more samples of it
- water_cooler_reroll roll 3
- coat_rack_reroll roll 1
- coat_rack_reroll roll 2
- floor_lino roll 1
- wall_scummy roll 3
- wall_scummy roll 4
- door_scummy roll 4
- door_scummy roll 1
- door_decent roll 3
- door_decent roll 4
- window_weather_clear roll 4
- window_weather_clear roll 1 -- lighting direction maybe weird, good asset
- window_weather_storm roll 4 / 3 / 1 -- good defaults, needs rework
- window_weather_doomy roll 3 -- not good but a default for testing while iterating
- cat_eldritch roll 4 -- keep for baseline
- cat_purple roll 1
- base_worker_restyle roll 1 -- best of an OK bunch, rest feel under
- base_worker_restyle roll 4
- cast_black_woman_young roll 1
- cast_woman_lead_older roll 1
- cast_wheelchair_user roll 4
- founder_silhouette roll 3 -- all bad but tolerable for testing; WRONG ORIENTATION; should mostly see the chair + silhouette; chair is the visual focus
- hat_medium roll 3 / 1
- hat_sports roll 4
- lab_coat roll 3 / 4
- lanyard_badge roll 2
- lanyard_badge roll 3 -- feels advanced/doomy, keep/recycle for that
- headphones roll 3 / 1 / 2 -- like all; want to see variants ON characters

## Maybe
- desk_mega roll 3 -- weirdly symmetrical (2 grey + 2 red objects)
- chair_decent roll 4 / 2
- monitor_mega roll 3 -- has keyboard+mouse; be explicit whether monitors include them
- kitchen_bench_scummy roll 2 / 3 -- side boundaries; need clearer architectural/positioning decisions (design/philosophy check)
- kitchen_bench_decent roll 1
- printer roll 2 -- check lighting + positioning
- meeting_table roll 2
- water_cooler_reroll roll 1
- coat_rack_reroll roll 3
- floor_carpet roll 1
- floor_lino roll 4
- floor_concrete rolls 1-4 -- Claude check if this is even vaguely a floor
- wall_scummy roll 1 -- defer to Claude
- wall_decent roll 3 -- not a wall segment, maybe something else
- door_scummy roll 3
- door_decent roll 1 -- lighting weird
- door_decent roll 2 -- too flat
- window_weather_clear roll 3
- cat_purple roll 4 -- keep for playtesting
- cast_black_woman_young roll 3 -- accentuate or de-accentuate belly/lighting
- cast_black_woman_young roll 4
- cast_woman_lead_older roll 3
- hat_sports roll 2
- lanyard_badge roll 1
- lanyard_badge roll 4 -- chunky; standby for a special-access asset
- headphones roll 4
- ui_panel_frame roll 4 -- keep in case we want ornate; unsure these generated well
- ui_texture_tile roll 4 / 3 -- might tile poorly?
- ui_indicator_dot roll 2 / 1
- icon_compute roll 4 -- slightly chip-ish; under-specified
- icon_doom roll 3 -- best artistically, still too human
- icon_doom roll 1 -- too purple and teethy

## Re-roll (with direction)
- desk_mega roll 2 -- single-colour screen least interesting vs image screens
- chair_mega rolls 1-4 -- needs FANCIER; roll 3 over-lit (lower half good); roll 4 too flat
- chair_decent rolls 1/3 -- must DIFFERENTIATE from chair_mega: no arm rests, more circular, smaller/less backrest, dull green or plasticky office-blue
- monitor_mega roll 4 -- angle too strong; re-roll as a STARTUP-mode mega monitor = 2 large chunky CRTs
- pc_mega rolls 1/2/3 -- angle/orientation consistency; roll 1 has plant leaves over it; think about how it sits near other items
- server_cluster_mega roll 1 -- looks like a city block, no cables
- server_cluster_mega roll 4 -- too solid
- kitchen_bench_scummy rolls 1/4 -- size/positioning vs others; side boundaries
- kitchen_bench_decent rolls 2/4 -- no potplants; roll 4 looks like a desk
- filing_cabinet roll 2 -- too angly
- filing_cabinet roll 4 -- lacks shadow depth, boring
- printer roll 1
- trash_can rolls 2/3 -- make explicitly RECYCLING, neater
- meeting_table roll 4 -- too thin
- water_cooler_reroll rolls 2/4
- coat_rack_reroll roll 4
- floor_carpet rolls 2/3/4 -- not tiling (circle, too small, indistinguishable)
- floor_lino rolls 2/3 -- didn't work as texture
- wall_scummy roll 2 -- unrequested circular downlight
- wall_decent rolls 1/2/4 -- not a wall segment
- door_scummy roll 2
- window_weather_clear roll 2 -- no windowsill/edging; deliberately call for these
- window_weather_storm roll 2 -- no frames. Claude: do we want frame + background rendered SEPARATELY?
- window_weather_doomy rolls 1/2/4 -- doomy needs style-guide input + significant rework, probably mechanically
- cat_eldritch roll 3 -- needs more Visual Doom. Need a UNIVERSAL intensity/philosophy reference? @Claude
- cat_eldritch rolls 1/2 -- more glow, maybe collar + emblem
- cat_purple roll 2 -- too smiley
- cat_purple roll 3 -- head too big
- cast_black_woman_young roll 2
- cast_woman_lead_older rolls 2/4
- cast_wheelchair_user roll 2 -- too flat
- cast_eccentric_genius rolls 1-4 -- ALL too generic
- founder_silhouette rolls 1/2/4 -- weirdly called for + incoherent; Claude rethink all of these
- hat_medium rolls 2/4
- hat_sports rolls 1/3
- lab_coat rolls 1/2
- ui_panel_frame rolls 1/2/3 -- angled / poorly defined / ew
- ui_texture_tile rolls 1/2 -- these are objects, wrong prompt/model
- ui_indicator_dot rolls 3/4
- icon_compute rolls 1/2/3 -- generic, off-brand; start thinking colour palette?
- icon_doom roll 2 -- try a ROBOT-flavoured skull
- icon_doom roll 4 -- too much yellowing/anatomy

## Cross-cutting asks to Claude (extracted)
1. Floors/walls/UI-textures did not come out as tileable textures -- check + fix the approach.
2. Windows: do we want the frame and the weather background rendered as SEPARATE layers?
3. Doom assets (cats, doomy windows): need a UNIVERSAL doom-intensity / philosophy reference to define/modulate intensity.
4. UI icons: off-brand -- start a colour palette / brand spec.
5. Founder silhouette: rethink entirely -- chair is the visual focus, silhouette seated, correct orientation.
6. Asset architecture/positioning: several props have implied side "boundaries"; need clearer decisions on how assets sit in space (relates to prop-only vs tileset room).
7. Be explicit per-asset about included sub-items (does a monitor come with keyboard/mouse; does a kitchen bench include plants).

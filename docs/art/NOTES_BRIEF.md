<!-- GENERATED FILE -- DO NOT HAND-EDIT.
Regenerate: python tools/art_review/notes_brief.py
Source of truth: tools/art_review/review_state.json (the note field).
Edit a note by re-reviewing the asset in art_generated/full_gallery.html and
merging the export with tools/art_review/merge_gallery_export.py -- editing this
file directly is lost work, because the next regeneration overwrites it. -->

# Art notes -- the brief for the next generation round

Every line below is something the reviewer typed while looking at a specific
picture. Notes are grouped by verdict, then by the batch the asset came from,
because "the value structure is muddy in the aubergine palette" is only
actionable if you can see it was said about eleven images in one block and not
once about anything else.

Read the ITERATE section first when writing the next prompt queue: those are
pictures judged worth having but not as generated.

**111 notes** across 2713 judged assets (4 percent of judgements carry a note).

## Recurring words

How many separate notes mention each craft term. A term near the top is a standing instruction the next prompt should carry, not a one-off reaction.

| term | notes mentioning it |
| --- | --- |
| colour | 8 |
| silhouette | 4 |
| signalling | 4 |
| blurry | 4 |
| contrast | 3 |
| transparent | 3 |
| lighting | 2 |
| edge | 2 |
| face | 2 |
| reading | 2 |
| composition | 1 |
| dark | 1 |
| grain | 1 |
| coherence | 1 |
| texture | 1 |
| washed | 1 |
| figure | 1 |
| person | 1 |

## KEEP -- what is working, preserve it (32)

### art_generated/endgame_concepts (1)

- `gen:endgame_concepts:attention_stack_buried_desk:v2` -- human too identifiable, otherwise, good, backgroundf weirdness good also

### art_generated/game_icons (4)

- `gen:game_icons:doom_meter_frame:v2` -- I have no idea what this is for and will watch out for it
- `gen:game_icons:doom_meter_frame:v3` -- this ouroborous like flavour is intersting, explore it more with a few other variants?
- `gen:game_icons:icon_acquire_startup:v1` -- This icon style is different and interesting, LLM, describe the prompts and so on to me that generated these?
- `gen:game_icons:indicator_status_critical:v3` -- DINg this bell is very good pickup, bureaucratic, I like it

### art_generated/iconset_round2 (2)

- `gen:iconset_round2:gen_type_pdoom_us:v1` -- There is something emerging with an emergent P from a doom meter filling up becoming the P in p(Doom) here that is strongly attractive, excellent. Keep and use this as a basis for more re-rolls as an avolutionary step.
- `gen:iconset_round2:gen_type_pdoom_us:v2` -- motifs playing in with a p shape in pdoom is a good directional step, iterate on this and sprad out widely, feed notes back up to style guide and refresh llm instructions accordingly. Exceptional.

### art_generated/treatment_sweep (1)

- `gen:treatment_sweep:treat_print_poster:v2` -- It would be good to get versions of this with some other colour schemes, this was very striking and well liked

### art_generated/ui_icons (3)

- `gen:ui_icons:action_research_robustness:v2` -- ok for now
- `gen:ui_icons:button_upgrade_normal:v2` -- exccellent
- `gen:ui_icons:employee_role_security:v2` -- This being on a lanyard is amazing. Strong positive note. COnsider us using this in other employee_role icons. Consider propogating this up into design documents. Amazing. A++

### art_source/cats_incoming (2)

- `px:cats_incoming/office_cat_base` -- This will do as first iteration, but I want like a dozen children now we have this to go off
- `px:cats_incoming/small-doom-cat` -- This feels like an upload of an ancient thing we generated last year, this is mostly for archive and inspo at this point although some of the hints around doom-glow are showing which is nice

### art_source/pixellab_2026-07-16 (5)

- `px:pixellab_2026-07-16/sweep/props/kitchen_bench_scummy_3.png` -- needs to be delineated as a corner asset
- `px:pixellab_2026-07-16/sweep/ui_filler_map_object/ui_panel_frame_2.png` -- better descriptor names in future pls
- `px:pixellab_2026-07-16/sweep/ui_filler_map_object/ui_panel_frame_3.png` -- better descriptor names in future pls
- `px:pixellab_2026-07-16/sweep/ui_filler_map_object/ui_panel_frame_4.png` -- better descriptor names in future pls
- `px:pixellab_2026-07-16/sweep/ui_filler_map_object/ui_texture_tile_1.png` -- better descriptor names in future pls

### art_source/pixellab_2026-07-17 (5)

- `px:pixellab_2026-07-17/reroll/objects/meeting_table_1` -- super grand meeting table
- `px:pixellab_2026-07-17/reroll/objects/meeting_table_2` -- good medium sized meeting table
- `px:pixellab_2026-07-17/reroll/objects/pc_mega_2` -- noting orientation amybe as tag
- `px:pixellab_2026-07-17/reroll/objects/pc_mega_3` -- noting orientation amybe as tag, this is the best
- `px:pixellab_2026-07-17/reroll/objects/pc_mega_4` -- noting orientation amybe as tag

### art_source/pixellab_2026-07-19 (7)

- `px:pixellab_2026-07-19/props/desk_lamp_1` -- experimeting with tags, like the lamp
- `px:pixellab_2026-07-19/props/desk_mega_1` -- This is a very particular corner desk orientation, which might be relevant
- `px:pixellab_2026-07-19/props/exit_sign_1` -- Amazing
- `px:pixellab_2026-07-19/props/filing_cabinet_tall_1` -- We will want TODO logic about where these spawn and pathing
- `px:pixellab_2026-07-19/props/office_phone_1` -- Amazing, candidate for future animation
- `px:pixellab_2026-07-19/props/printer_mega_copier_1` -- Very cool copier
- `px:pixellab_2026-07-19/props/snack_table_1` -- I note this is very top-down perspective

### art_source/pixellab_2026-07-21-rerolls (1)

- `px:pixellab_2026-07-21-rerolls/kitchen/kitchen_bench_scummy_1` -- note this is corner / diagonal asset

### art_source/vignettes_2026-07-28 (1)

- `px:vignettes_2026-07-28/01_cat-in-the-alley.png` -- This will do for now but please give me, like, 10 variants to choose from? Maybe some vesrions where the cat's arrival is doom-portentous and some where it's saviour-portentous?

## ITERATE -- what to change in the next round (66)

### art_generated/action_icons_missing (1)

- `gen:action_icons_missing:lobby_government:v1` -- briefcase needs to be colour and visually distinct from foreground

### art_generated/game_icons (12)

- `gen:game_icons:action_funding_grant_proposal:v1` -- The yellow is a little unsubtle, this could maybe have the tick come down in intensity a little
- `gen:game_icons:action_funding_grant_proposal:v2` -- the background of this is inconsistnent
- `gen:game_icons:action_management_team_building:v2` -- Avoid cockleg problems, this is very funny though
- `gen:game_icons:action_strategic_acquire_startup:v2` -- too dark, brighten, decrease grain slightly
- `gen:game_icons:action_strategic_acquire_startup:v3` -- Brighten, increase contrast, consider lighting some of the windows gently
- `gen:game_icons:action_strategic_lobby_government:v1` -- different colour beifcase, try lighting some windows
- `gen:game_icons:action_strategic_sabotage:v1` -- Needs a bit more lightness and colour, slightly increase contrast around interior edge of hood
- `gen:game_icons:action_strategic_sabotage:v2` -- slightly incrase contrast around lower edge of hood for better delineation withou revealing face
- `gen:game_icons:doom_bg_critical:v3` -- Not nuclear symbol. Experiment with new, geometric abstract represtation of doom escalation
- `gen:game_icons:doom_bg_safe:v1` -- Not a lock. try a more symbolic reprsentation in the abstract. Consider an alien culture's represetion of safe from boba principles.
- `gen:game_icons:doom_glow_effect:v3` -- I'm not sure if these are meant to be glow effect samples for us to base things off or somehting else, but I feel like the doom glow effecst we have decided will be applied as mechanistic filters and so an LLM should revisit the necessity for these assets in particular
- `gen:game_icons:doom_meter_frame:v1` -- This might not need an icon, revert to instructions and confirm back to user if needed

### art_generated/hero_banners (7)

- `gen:hero_banners:hero_founder_silhouette:v1` -- silhouette too boviously male, too obviously signalling Operator
- `gen:hero_banners:hero_founder_silhouette:v2` -- silhouette too boviously male, too obviously signalling Operator
- `gen:hero_banners:hero_founder_silhouette:v3` -- silhouette too boviously male, too obviously signalling Operator
- `gen:hero_banners:hero_founder_silhouette:v4` -- silhouette too boviously male, too obviously signalling Operator
- `gen:hero_banners:hero_paperwork_saves_world:v1` -- let's iterate on this iudea and go for something a bit less literal, maybe? try anorger 5 very diverse variants and we'll see where we end up
- `gen:hero_banners:hero_server_doom_altar:v1` -- Let's try with one more androgynous operator? If this is late game they might have a cool cloak with a collar or a hood or something
- `gen:hero_banners:hero_server_doom_altar:v2` -- andogynous operator please, otherwise, good, maybe give them a cape or cloak or be carrying equipment or san umbrella or protective gear or somesuch

### art_generated/iconset_round2 (2)

- `gen:iconset_round2:gen_cat_evil:v3` -- eyes too well defined
- `gen:iconset_round2:gen_cat_evil:v4` -- eyes have too mcuh definition, breaks immersion

### art_generated/round3_rerolls (2)

- `gen:round3_rerolls:grant_proposal_r3:v1` -- Entirely rebase instructions for this, reading LLM, and branch out into several variats so we can move away from cliche
- `gen:round3_rerolls:grant_proposal_r3:v2` -- Entirely rebase instructions for this, reading LLM, and branch out into several variats so we can move away from cliche

### art_generated/scene_art_wave2 (2)

- `file:art_generated/scene_art_wave2/v1/event_opportunity_v1.webp` -- make figures less obviously men?
- `file:art_generated/scene_art_wave2/v1/event_opportunity_v2.webp` -- Try making fihgures more androgynous and less obvious, otherwise, good

### art_generated/screen_backgrounds (7)

- `gen:screen_backgrounds:bg_defeat:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_main_grid:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_panel_texture:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_settings:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_tartan_stripe:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_victory:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after
- `gen:screen_backgrounds:bg_welcome_lab:v1` -- All these seeem wildly incorrect, investgiate but I think this is just a misfiring of what we're after

### art_generated/ui_icons (16)

- `gen:ui_icons:action_facility_data_center:v2` -- This would be fine for a high spooky thing but a more realistic icon would be great.
- `gen:ui_icons:action_facility_security_upgrade:v1` -- Good, try a second colour for the camera. Meta note: I think we want to craete some style design rules about, like primary and secondary clour groupings in our icons for a next-generation coherence pass because we keep getting things that are individually good, subtly with mayn upsides, but need coherence in direction. We can extract this from pulling detailed analysis of the little features of images I like and striving for collapsing into coherence from there. This is otherwise an excellent image.
- `gen:ui_icons:action_facility_upgrade_compute:v2` -- a bit too simple, try with more depth and texture and richness, decrease arrow size by 15%
- `gen:ui_icons:action_policy_audit_requirement:v1` -- this fits a dull and washed out scheme, tag it as such asnd keep as back up or for a sample of tone review
- `gen:ui_icons:action_research_alignment:v1` -- Make the arrow and bottom cog one colour and the upper cog a differnet colour to highlight difference
- `gen:ui_icons:action_research_alignment:v2` -- this will do for now, uninspired
- `gen:ui_icons:action_research_capability_control:v2` -- try a represntation of a mechanical governor device or some other astute enginerring reference
- `gen:ui_icons:action_research_red_teaming:v1` -- one red team one blue team, not chess
- `gen:ui_icons:action_research_red_teaming:v2` -- one red team one blue team, combat, not chess, can be engineers facing each other off
- `gen:ui_icons:action_research_robustness:v1` -- try incraesing saturation slightly and emboldening shield, otherwise, good
- `gen:ui_icons:button_upgrade_hover:v2` -- too bendy
- `gen:ui_icons:employee_role_engineer:v1` -- I think with role types we want a human as persona in the icon to emphssisse this is a role, this is true across all employee_role icons in this batchm, these will do as backups or paceholders
- `gen:ui_icons:employee_role_researcher:v1` -- try with a more ML neural net image in the beacon
- `gen:ui_icons:employee_status_burned_out:v1` -- this si danerously close to a mtg symbol. think about better repersentaiton for emotinal burnout
- `gen:ui_icons:ui_governance_oversight:v1` -- needs more colour differentiation, ask or increase scope of style guide for assistance
- `gen:ui_icons:ui_governance_oversight:v2` -- needs more colour differentiation, ask or increase scope of style guide for assistance

### art_generated/wanasai_calls (1)

- `gen:wanasai_calls:atrium_face_smiling:v1` -- Having a human face makes it weird, see what happens if we give the figure (a) a mask, so it could be human or robot, (b) a copy of (a) but mybe make one of the arms or the person be ambiguouss or hinting at possibly being robotis as well, (c) have the figure still be fairly non-human but with more religious overtones as well as (d) a version of (c) but with more state-propoganda overtines

### art_source/cats_incoming (1)

- `px:cats_incoming/web-doom-cat.jpg` -- This is a genreated inage of a cat, it's not an actual named cat like the others

### art_source/pixellab_2026-07-16 (2)

- `px:pixellab_2026-07-16/props/cat_bed_basket.png` -- this needsd to be a cat bed basked without a cat in it
- `px:pixellab_2026-07-16/props/cat_litter_box.png` -- littler box without a cat in it

### art_source/pixellab_2026-07-17 (4)

- `px:pixellab_2026-07-17/reroll/objects/meeting_table_3` -- needs chairs both sides or no chairs
- `px:pixellab_2026-07-17/reroll/objects/pc_mega_1` -- this looks more like a medium or bad PC
- `px:pixellab_2026-07-17/reroll/objects/printer_1` -- weirdly wonky
- `px:pixellab_2026-07-17/reroll/tilesets/wall_scummy` -- Can we try a mostly bare garage wall

### art_source/pixellab_2026-07-19 (9)

- `px:pixellab_2026-07-19/props/fire_extinguisher_1` -- This looks very front-on, we want some logic in the game about where a fire extinguisher should go TODO
- `px:pixellab_2026-07-19/props/monitor_doomcurve_1` -- this monitor is weirdly angled
- `px:pixellab_2026-07-19/props/monitor_dual_1` -- Unsure on colours or if we are going with trnasparent screens or not?
- `px:pixellab_2026-07-19/props/monitor_mega_1` -- I feel like transparent screens lets us add sneaky responsive UI elements in underneath cheaply
- `px:pixellab_2026-07-19/props/monitor_single_1` -- I feel like transparent screens lets us add sneaky responsive UI elements in underneath cheaply
- `px:pixellab_2026-07-19/props/pc_mega_1` -- The angle on this seems weird in terms of perspective, this might not map correctly but would be cool if it was eventually ugpraded into a many-directional asset
- `px:pixellab_2026-07-19/props/printer_small_1` -- Test deploy this and we'll see
- `px:pixellab_2026-07-19/props/recycling_bin_1` -- This looks a little flat, and can really only be deplyoed against flat backgrounds
- `px:pixellab_2026-07-19/props/server_cluster_mega_1` -- This has some transparent shadows and positioning that needs to be carefully aligned and thought about, we might review on deploy

## DISCARD -- what to stop generating (4)

### art_source/pixellab_2026-07-26_size_probe (1)

- `px:pixellab_2026-07-26_size_probe/size_48/rotations/south-east.png` -- blurrrrry

### art_source/pixellab_2026-07-27_prop_rebase (3)

- `px:pixellab_2026-07-27_prop_rebase/native/desk_decent_r1.png` -- blurry
- `px:pixellab_2026-07-27_prop_rebase/native/desk_decent_r1_nearest.png` -- blurry?
- `px:pixellab_2026-07-27_prop_rebase/native/desk_front_decent_r1_nearest.png` -- blurry

## UNJUDGED -- noted but no verdict yet (9)

### art_generated/crisp_sweep (1)

- `gen:crisp_sweep:cheerful_propaganda_atrium_crisp:v2` -- the banker's lamp seems to have suffused into everything here for some reason

### art_generated/endgame_concepts (1)

- `gen:endgame_concepts:intro_bus_strangers_help:v1` -- this was a good composition but more recent versions have better approaches to keeping the protagonist unidentified - shoot from the back, silhouettes for either gender only, hoods, hats

### art_generated/endgame_concepts_gen2 (1)

- `gen:endgame_concepts_gen2:same_desire_two_field_strengths:v1` -- this is getting better but we ssem toh ave massively overindexed on the bankers lamp as an art asset./ This probably meansd we need to generate a bunch more asset descriptions that *could* be in scenes so that llm's can chooose between different sets of objects to populate scenes with

### art_generated/people_policy (1)

- `gen:people_policy:people_silhouette:v1` -- Silhouettes look a little fake

### art_source/pixellab_2026-07-17 (1)

- `px:pixellab_2026-07-17/reroll/cats/cat_eldritch_1.png` -- the eldritch cat was an early idea that is now mostly being discarded, we will in game doom enhance cats rather than mbaking it into their walk animations. This applies to the rest of the eldritch cats in this set.

### art_source/pixellab_2026-07-27_prop_rebase (3)

- `px:pixellab_2026-07-27_prop_rebase/large_source/desk_side_scummy_r1.png` -- this is a 3/4 shot side view, is that correct notation?
- `px:pixellab_2026-07-27_prop_rebase/large_source/server_cluster_r2.png` -- I think this type of picture needs to be differentiated somehow that it goes on a corner or facing a direction? LLM, advise me how we have planned on solving for this?
- `px:pixellab_2026-07-27_prop_rebase/native/water_cooler_scummy_r2_nearest.png` -- mostly discarded for being blurry

### art_source/vignettes_2026-07-28 (1)

- `px:vignettes_2026-07-28/04_conference-return.png` -- this operator seems too visible and obviously a man, maybe try making the scene more abstract, luggage on bed, overstuffed mailbox at an apartment door with packages buiding up outside, what's in the fridge, etc, try a gfew different scenes and options

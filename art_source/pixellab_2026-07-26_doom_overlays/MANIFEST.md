# Doom overlay sets -- 2026-07-26 (drop-in to the cat sweep batch)

Pip's mid-batch request: assets for "different kinds of doom generation ...
particle or animation overlays rather than just environmental effects", to
experiment with layering / subtle additions, with enough SETS that early
failures don't invalidate the thesis. Effort/spend envelope explicitly raised
("even quadrupling overall effort and image spend on this is fine").

Design keys off the two existing doom docs (read them first):

- `docs/art/DOOM_OVERLAY.md` -- "doom is a layer, not a repaint"; the current
  demo does the layer with canvas compositing (glow + grade + edge aura).
  These sprites are the OTHER candidate implementation: particle/animation
  overlay sprites composited in-engine.
- `docs/art/PALETTE_AND_DOOM_INTENSITY.md` -- the operational ladder; every
  family carries ONE hue drawn from the band table (never a rainbow; purple
  reserved for band 3+).

## Families (6) x 3 kept variants each, + hue-state variants

`create_1_direction_object`, view `top-down`, size 64 (16-candidate review
pack, 20 gens/pack); 3 diverse survivors selected per family (selection is
free); each survivor animated with `animate_object` v3, 8 frames (9 stored,
frame_000 = idle ref), 1 gen/loop. Hue variants via `create_object_state`
(1 gen each).

| family | band / axis | hue anchor | variants (folder names) |
|---|---|---|---|
| embers | 1-2 / catastrophe | `#E9752E` orange | faint, motes, flecks |
| arc | 2 / weirdness | `#5C7AC3` electric blue | branching, radialweb, zigzag |
| wisp | 3 / weirdness | `#7A3B8F` violet | slim, tendrils, curl |
| aura | 3 / weirdness | `#7A3B8F` violet | smokering, spikysigil, glowdisc |
| flame | 4 / catastrophe | `#DD5F4C` + `#F69168` fire | tongue, lowwide, sparking |
| void | 4 / weirdness (terminal) | `#0E0614` + `#96718F` rim | vortex, tentacles, jaggedrift |
| states | cross-band | hue-swapped from survivors | aura_amber (band 0-1), aura_red (band 2), wisp_blue (band 2), embers_red (band 3) |

## Object ids

| asset | pixellab object id | parent 16-pack |
|---|---|---|
| wisp/slim | 49ce24f4-ae72-4f12-87de-edfa3e4e1805 | 27c3b8df-004b-49ca-b656-a92c53a78403 |
| wisp/tendrils | 8f97e431-08f0-412b-80a3-a963bf754eb6 | 27c3b8df |
| wisp/curl | b41ebb2f-4505-4c51-ba03-692a6bae7a61 | 27c3b8df |
| embers/faint | 0ad6ecc1-09ec-4a75-84e6-5f111d8bea10 | 6080f73f-2906-4d4b-bfae-10f63a011def |
| embers/motes | c7570ff3-9077-4336-8f42-5755b52e3beb | 6080f73f |
| embers/flecks | a1b12828-b7ec-42b9-809b-3150136e7f16 | 6080f73f |
| arc/branching | 00968ad0-7b48-497d-adb4-f78d9ec12787 | c179b497-e34c-4721-aa32-70d8daf8a45a |
| arc/radialweb | bcd4698e-b7b6-434b-b7cf-7ff367083c5d | c179b497 |
| arc/zigzag | 5e2d8622-7337-491e-be3c-7a619a23bd9d | c179b497 |
| aura/smokering | b2b7479c-e7dd-4332-8c39-1b1806ba3e14 | de497dbf-53c2-48db-b4b2-87a6d921691a |
| aura/spikysigil | 2fa4dea2-0a08-48ae-a652-2942a816517f | de497dbf |
| aura/glowdisc | 9e561ec4-76f1-4591-b1f9-006499302597 | de497dbf |
| flame/tongue | f47fdbf2-d0c9-412a-af85-61632c861d75 | 934e17ee-da25-4f0f-bbdc-4356fc9a91d2 |
| flame/lowwide | 0a0287e1-7d14-463c-bc82-89d715ba8461 | 934e17ee |
| flame/sparking | c02a41ee-bffc-4611-b97f-4bcba710978c | 934e17ee |
| void/vortex | 28179f73-3467-4849-a798-bb5a8db08c6f | 7edf9c07-5044-42d5-81b9-732d07127300 |
| void/tentacles | 12dba514-2e89-43b4-b1dd-02912e0f77d5 | 7edf9c07 |
| void/jaggedrift | 0cf0c547-cce7-4acf-bf26-3a652ee7845d | 7edf9c07 |
| states/aura_amber | f9e0083a-6ea8-4980-965a-97235c3441cc | state of aura/glowdisc |
| states/aura_red | 17c48c5a-22f4-4f4e-8ecc-8961e957f988 | state of aura/spikysigil |
| states/wisp_blue | 24676503-4407-4040-8b73-b4194f22c351 | state of wisp/slim |
| states/embers_red | 8b29a76a-5efc-4428-a780-f5de66eaef8c | state of embers/motes |

Loops: ALL 22 assets are animated -- 18 family variants + all 4 hue states
(aura_red and embers_red were initially stills-only; the mid-batch cap-lift
ruling "do not ration" added their loops too). Nothing cut.

## Layout

`{family}/{variant}/idle.png` + `{family}/{variant}/loop/frame_000..008.png`
(frame_000 = the idle reference; loop folder absent = still-only variant).
All 64x64 RGBA, transparent background.

## How to judge (sheet sections 6-7)

`art_generated/cat_sweep_sheet.html` section 6 shows every variant's loop;
section 7 is the LAYERING LAB: each combo composites an overlay over a
walking cat on the office floor with live dials -- opacity slider, blend mode
(normal / screen ~= the additive "lighter" pass / lighten / hard-light), and
behind/in-front z-order. The question per combo: does a sprite overlay get
close enough to the shader-style doom pass to be worth the renderer lane?

## Verdict-relevant notes (lane eyeball, pre-Pip)

| family | read |
|---|---|
| wisp | Loops sway with drifting sparkle motes -- reads immediately as rising doom-smoke. slim = the subtle default; tendrils = band-3.5 flavour. |
| embers | Motes shift and twinkle between frames -- proper particle drift. faint variant is nearly subliminal at 1x (good: the subtle end of the dial). |
| arc | The loop RE-DRAWS bolt shapes per frame, so it flickers like real arcing rather than wobbling one bolt. radialweb reads as a glitch-aura for machines. |
| aura | glowdisc pulse has big amplitude (deep violet -> near-white); at full opacity it overpowers a 68px cat -- the lab's opacity dial at ~40-60% is the intended operating range. |
| flame | Standard licking fire, hue on-ladder. |
| void | vortex/tentacles/jaggedrift give three distinct "floor corruption" silhouettes. |
| states | Hue swap for 1 gen keeps silhouette EXACTLY -- the cheapest axis for band-parallel sets. amber glowdisc is the most shippable band-0/1 asset in the batch. |

## Credits

| stage | gens |
|---|---|
| 6 x 16-candidate packs (create_1_direction_object, 64px) | 120 |
| 22 x v3 loop animations (18 variants + all 4 hue states) | ~101 |
| 4 x hue states (create_object_state) | 4 |
| **overlay lane total (by used-counter residual)** | **~225** |

Cost datapoints (MEASURED by balance deltas): 16-candidate 64px pack = 20
gens (~1.25/candidate); object state = 1 gen; **object v3 loop at 64x64x8
~= 5 gens** (aggregate) -- note this is NOT the 1 gen/direction that
CHARACTER v3 animation costs at 68x68; the object pipeline bills ~5x. Four
loop jobs crashed before start ("not charged") and were re-queued at no
cost.

Batch accounting (plan-independent `generations_used` counter, since Pip
upgraded the account to Tier 3 mid-batch): 1102 used at batch start ->
1394 at close = **292 gens both lanes** (cat lane ~67, overlay lane ~225);
6025 remaining on the upgraded pool at close.

# Pixellab round 2 (non-cat) -- 2026-07-26

Round-2 gap fill per issue #900 (Pip ruling 2026-07-26: push generation forward,
dollars are noise per docs/art/SEED_ART_COST_MODEL.md). Cats intentionally ABSENT
-- gated on Pip's A/B verdict on PR #911. No godot/ wiring in this round; triage
comes first (contact sheet at art_generated/round2_noncat_contact_sheet.html,
copied to the main checkout).

House standard locked this round (learned in the PR #911 cat lane):
- create_character views are [high top-down, low top-down, side, oblique(BETA)].
  Scene standard: **low top-down**.
- Canvas math: API pads ~40% -- **size 48 emits a 68x68 canvas** (the
  promoted-walker standard); size 64 emits 92x92. Everything here is size 48.

Style grounding: docs/art/reviews/2026-07-17-overnight-sweep.md +
docs/art/PALETTE_AND_DOOM_INTENSITY.md (warm-grime base, heavy outline, muted
teal-olive-slate palette, warm amber the only saturated accent; doom family is
the red-purple exception).

## Generation cost (pixellab)

- Balance BEFORE round: **958 generations remaining** ($0.00 credits, Tier 1).
- Balance after statics (4 billed characters + 18 map objects; 1 character
  failed on "heavy load" and was NOT billed): **936** -> statics cost 22 gens.
- Balance after the walk-cycle block (2 characters x template `walk` x 4
  cardinal directions, NOTHING else in flight): **919** ->
  **isolated walk-cycle cost: 17 gens for 8 direction-jobs (~2.1
  gens/direction OBSERVED)**. Nominal doc rate is 1 gen/direction for template
  mode; the observed 2x is the datapoint the cost model wanted -- do not plan
  walk cycles at 1/direction.
- Balance after the create_character_state pilot: **898** -> **21 gens for ONE
  state**. The tool itself quoted ~20-40 gens/state up front, over the pilot's
  20-gen budget, so the pilot STOPPED at one state (no stressed/idle rolls).
  Verdict for #793 planning: states via create_character_state are Gemini-tier
  priced (~20-40 gens each), NOT a cheap pose source; a 3-pose set per worker
  would run ~60+ gens.
- Balance END of round: **898** (958 -> 898 = **60 gens total**: 22 statics +
  17 walk cycles + 21 state pilot).

gpt-image-1.5 lane (separate wallet, OpenAI): 7 core resource icons x $0.06 =
**$0.42** (see art_prompts/core_resource_icons.yaml generation_history).

## 1. Office workers (characters/) -- retires the 180px orphan

`create_character` standard mode, humanoid, **size 48 (68x68 canvas)**, low
top-down, 8 directions, single color black outline, high detail. Diversity per
Pip's 2026-07-21 standing rule (feeds the #793 variant pool): ethnic +
disability representation across the four variants.

| name | pixellab id | notes |
|---|---|---|
| worker_hijab_f | 573c076b-b982-4210-81fc-5f7b6c099f82 | young South Asian woman, dark teal hijab, olive cardigan; + walk (template, S/N/E/W, group 84aecb4c-d6d0-48c0-bf80-23109acda855) |
| worker_black_m | 38f3a047-3cb4-4d12-bf56-1407d779c4c5 | Black man, slate shirt, lanyard; + walk (template, S/N/E/W, group b9b282aa-ef6b-441d-b9fa-ca284e26dda4); state pilot source |
| worker_wheelchair_f | f98d8524-ea05-4b70-bc28-9b6e76218b20 | middle-aged white woman, manual wheelchair; no walk anim (wheelchair locomotion is its own future anim) |
| worker_crutch_m | cb8b2b15-2146-4811-a61d-5dfe2aa79cb0 | older East Asian man, forearm crutch, amber sweater vest; first roll d88274ec failed ("heavy load", not billed), refired |

Each folder: `rotations/{south,...}.png` (8) + `animations/<name>/<dir>/N.png`
frames where animated + pixellab `metadata.json`.

### State pilot (create_character_state, worker_black_m)

| state | new character id | edit |
|---|---|---|
| working (folder `worker_black_m_state_working/`) | cbadc929-ddbb-44fa-9f3c-29235d07ba74 | seated typing pose, hands raised as if typing, legs bent as if on an office chair; palette snapped to source |

One state only: the tool quoted ~20-40 gens/state (Gemini tier), over the
pilot budget; actual billed cost 21 gens (balance-bracketed). South rotation
reads as a plausible seated-typing sprite for compositing onto chairs.

Quality notes for triage: worker_wheelchair_f reads clearly in side/diagonal
rotations. worker_crutch_m's forearm crutch is weakly legible in the south
(front-on) view at 48px -- check side rotations before promoting.

## 2. Window plain variants (props/) -- window_clean + window_scummy regen

Previous round: window_clean/window_scummy 0-promoted (blank washed-out panes);
the window_weather_* set (clear/storm/doomy) was 12/12 promoted. This round
matches the promoted set's generation params: `create_map_object`, 120x96, low
top-down, high detail, detailed shading, single color outline.

FINDING (recorded for future prompts): "clean/plain office window" collapses to
a blank featureless pane -- the exact rejected failure -- unless the prompt
explicitly forces **a dark sturdy frame + a distant city skyline** (present in
all 12 promoted weather variants). Rolls 1-4 used the naive phrasing (kept for
evidence); rolls 5+ force frame+skyline and land the style.

| key | roll | pixellab id | prompt family |
|---|---|---|---|
| window_clean | 1 | cb32fc46-6de2-4622-b6cb-f8c1a8f8d72f | naive (blank-pane failure) |
| window_clean | 2 | 163d0ddd-f06e-4010-b558-5dbdf976dd26 | naive (blank-pane failure) |
| window_clean | 3 | 15fa1be4-d3b5-4d6a-bf56-f645e26bfcf3 | naive (blank-pane failure) |
| window_clean | 4 | 7b7233b6-5666-49fa-ba52-8e8920ad4c32 | naive (frame, empty glass) |
| window_clean | 5 | 7efa7cbd-a944-4127-a74b-96e93263dc5e | frame+skyline forced |
| window_clean | 6 | 0afb7a24-ad36-48e5-841b-d98bd5c50167 | frame+skyline forced (strong) |
| window_clean | 7 | 6a4bf95b-5e0d-4f92-94d9-f5c42fed040b | frame+skyline forced |
| window_clean | 8 | 6e83619d-62d8-41bd-8430-bcb645b44303 | frame+skyline forced |
| window_scummy | 1 | a8ba66fa-cccd-494e-9653-246106391037 | naive (landed anyway -- strong) |
| window_scummy | 2 | ffa0ac59-b4c9-4a5a-b90c-f28c0ae7dd17 | naive (decent) |
| window_scummy | 3 | 04d13002-3d4d-4ad2-ac81-57a9fbcd5530 | naive (frameless, weak) |
| window_scummy | 4 | 45f555f4-4176-4f68-a1bb-14a99e5955be | naive (frameless, weak) |
| window_scummy | 5 | 4a1842b3-4cc8-4ea8-a0fd-eabea9c3d8f3 | frame+skyline forced (strong) |
| window_scummy | 6 | 179f14f8-e070-433d-89f5-62c6a1e52f15 | frame+skyline forced (strong) |

## 3. icon_doom re-rolls (icons/) -- 8/8 previously rejected

All 8 prior rejects (2026-07-16 sweep + 2026-07-17 reroll) were literal
red/purple **skulls** -- generic horror iconography, off-brand for an AI-risk
game. These 4 rolls use skull-free concepts in the doom red-purple family,
48x48 `create_map_object`, transparent bg:

| file | pixellab id | concept |
|---|---|---|
| icon_doom_gauge_1 | 9e87bfb7-f063-495a-ac76-ad5d55199cf6 | risk gauge, needle pinned in crimson zone |
| icon_doom_curve_2 | 13e19878-8c97-4512-9850-5cac844d5f69 | rising doom curve ending in flare (came back weak) |
| icon_doom_orb_3 | bc84714c-2471-4199-bba5-36fd260dbf28 | dark orb, red-purple vortex core |
| icon_doom_hourglass_4 | d1606fe2-6b07-4815-a5d8-abf1512cbd35 | hourglass, crimson sand nearly out |

## 4. Core resource icons (gpt-image-1.5 lane, NOT in this folder)

The 7 theme_manager.gd:112-118 placeholders (logo, money, compute, research,
doom, paper, reputation) generated via tools/assets/generate_images.py with
art_prompts/core_resource_icons.yaml -- the same global_icon_base +
surface_tarkov formula as the quirk icons Pip called "fresher and bolder".
Outputs: art_generated/core_resource_icons/v1/<id>_{1024,512,256,128,64}.png
(art_generated/ is gitignored; the YAML with full generation_history IS
committed). 1024px masters are 1.8-2.2MB each ->
G:/tmp/pdoom1-art-masters/core_resource_icons_v1_2026-07-26/ per
docs/art/ART_MASTERS_POLICY.md.

NOTE: pixellab map objects auto-delete after 8h; all PNGs downloaded here.

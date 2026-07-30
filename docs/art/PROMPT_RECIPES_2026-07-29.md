# Prompt recipes -- 2026-07-29 night batches

Working reference for lifting phrases out of, not a report. Everything in a
fenced block below is the EXACT string that went to the model tonight.

- Manifests: `tools/assets/manifests/crisp_sweep.json`,
  `tools/assets/manifests/new_subjects.json`
- Outputs: `art_generated/crisp_sweep/v1/`, `art_generated/new_subjects/v1/`
- Rules source: `docs/art/ENDGAME_CONCEPT_REVIEW_2026-07-29.md` (A1-A10,
  **PROVISIONAL**)

## The model and the size cap, plainly

- **Model:** `gpt-image-1.5` (OpenAI Images API), the default in
  `tools/assets/generate_images.py`. Snapshot id noted in that file as
  `gpt-image-1.5-2025-12-16`. `gpt-image-1` retires 2026-10-23.
- **Hard size cap: 1536x1024 for landscape.** That is the maximum the backend
  will emit. Portrait is 1024x1536, square is 1024x1024.
- **There is no upscale path in this pipeline.** `generate_images.py` requests
  the master at `default_size`, then only ever LANCZOS-*downscales* it to the
  widths in `output_sizes` (1536 / 1024 / 768 / 512 here). Nothing in the tool
  produces a pixel that the API did not.
- Consequence: **"crispen" is a prompt-language lever, not a resolution
  lever.** If a genuinely larger master is ever needed it has to come from a
  separate upscaler run on the 1536 PNG (Real-ESRGAN / topaz / equivalent),
  outside this script. Do not claim upscaling happened here.
- Cost model used for estimates (estimates only, not billed truth):
  1536x1024 ~ $0.09/image, 1024x1024 ~ $0.06/image.

## The shared style block, quoted

Six strings, concatenated with `, ` in this order, then the theme's
`color_bias`, then the asset's `prompt_tail`. That concatenation is all
`build_full_prompt()` does. Identical in both manifests tonight, and lifted
verbatim from `endgame_concepts_gen2.json` so the three batches are
comparable.

### `poster_base`

```
wide cinematic POSTER ART illustration for a video game, painterly warm-grime texture with heavy dark outlines and deep shadow, full-bleed edge-to-edge opaque composition that completely fills the frame with no transparency and no cut-outs and no border, lived-in physical props and real architecture rather than abstract shapes, every object in frame must be immediately identifiable as a specific real thing -- a car, a filing cabinet, a pallet, a transformer -- and never a generic boxy shape, because an unrecognisable object is visual noise rather than a prop, no text, no lettering, no signage, no numerals, no logo, no watermark, no UI overlay, high production value, landscape orientation
```

### `poster_lighting`

```
DISCIPLINED AND UNDERSTATED LIGHTING, roughly 75 percent more subtle than a typical dramatic game illustration: mood must NEVER come from the main light source, so the ordinary room lights, street lights and work lights in the scene are plain neutral white or plain warm tungsten exactly as they would really be, never tinted red or green or purple for atmosphere; coloured light is permitted ONLY where a real fixture in the world would genuinely emit that colour, for example an emergency beacon, a screen, an indicator lamp, a corona arc or the impossible thing itself; if one emergency or alarm source IS the mood, then every other light in frame must be a visibly different and clearly ordinary source; at most one ambient source plus one glowing source, most of the frame kept dark with separated pockets of light, restraint over drama
```

### `poster_palette`

```
colour language from the P(Doom)1 hero art with palette anchored per weirdness tier so colour stays consistent across the set even when composition and style do not: grounds always in void #0e0614, deep aubergine #170a1c, ink brown #14040c, deep indigo #181b3b and #2e2547; LOW weirdness scenes take exactly one warm CRT amber accent #e8a33d / #f6a800; MEDIUM weirdness scenes take exactly one cold electric-blue screen-glow accent #5c7ac3; HIGH weirdness scenes take exactly one eldritch violet accent in the fixed indigo-violet range #7a3b8f; never stack multiple saturated glows in one image; small non-saturated secondary notes such as a single tiny distant green pinprick are allowed purely to open up depth
```

### `poster_people`

```
NO PEOPLE BY DEFAULT -- the player is a bureaucrat and the poster art is about everyone else, so incidental figures are removed rather than restyled, because default generated people read as interesting generic strangers and imply the viewer should be responding to a protagonist rather than simply observing; where a figure is unavoidable it must be an ANDROGYNOUS SILHOUETTE with no readable gender cues, no distinguishing jewellery, no distinctive hairstyle and no face detail; where several figures are unavoidable they must be a genuinely varied ordinary group of office staff in plain institutional workwear rather than a row of similar-looking models; the player character and any hero figure is NEVER shown, and any figure standing in for the viewer must have its identity destroyed by blocking, backlighting and occlusion rather than merely turned away
```

### `poster_props`

```
props must be era-correct and consistent with the game's own set dressing: a banker's desk lamp is ALWAYS the green glass shade on a brass stem, office chairs, rubber date stamps, manila folders, ring binders, CRT and early-flatscreen monitors, chain-link fencing that hangs correctly on its posts with a real top rail, real tension wire and believable sag rather than fading into nothing; ABSOLUTELY NO BARBED WIRE and no razor wire anywhere, it reads wrong; uncrewed machines are directly manufactured and therefore have NO COCKPIT, NO CANOPY and no windows for a pilot, which is the single clearest tell of a purpose-built drone
```

### `poster_safety`

```
strictly no blood and no gore anywhere in the image, damage to machines shown as mechanical breakage with glowing green or blue coolant and hydraulic fluid only, no wounded people, no real-world brands or insignia or logos, no identifiable real people, nothing sexualised, all human figures fully and modestly clothed in ordinary institutional workwear
```

### The world-flavour prefix on every `color_bias`

```
a bureaucratic world with weirdness leaking in at the edges; ordinary institutional competence rendered straight while something impossible happens deadpan in the same frame; the three flavours of strangeness available are pure eldritch intrusion from another dimension, technology run amok, and environmental collapse, and any one image should commit to only one of them; restrained and elegant, never garish, never lurid
```

## Axis 1 -- CRISPNESS (the three modifiers, side by side)

Appended to the world-flavour prefix as `<world flavour>; <modifier>`. These
are the only strings that differ between the three arms of the sweep. Copy
whichever one you want.

### `_soft`

```
CRISPNESS TREATMENT -- SOFT (control arm): atmospheric and painterly, visible haze and aerial perspective separating the planes, softened and broken edges, diffuse falloff around every light, real depth-of-field blur in the near foreground and in the far distance, materials suggested with loose brushwork rather than described, small and distant forms allowed to dissolve into tone; the picture reads as mood first and detail second
```

### `_crisp`

```
CRISPNESS TREATMENT -- CRISP: sharp focus from the nearest foreground to the far background with NO depth-of-field blur anywhere in the frame, NO atmospheric haze, NO aerial perspective, NO fog, NO bloom and NO glow spill; high micro-detail in every material -- aggregate and form-tie marks in concrete, individual wires in mesh, tool marks, weld beads, paint chips and grime lines in metal, dust and fine scratches on glass, legible paper fibre and print texture; hard clean silhouette edges that separate the subject from what is behind it; small distant forms remain fully legible as specific identifiable objects at their scale; specular highlights are tight and hard-edged rather than soft glows; the picture reads as detail first and mood second
```

### `_graphic`

```
CRISPNESS TREATMENT -- GRAPHIC: poster-like flat clarity, compressed tonal range built from a small number of clearly separated value steps rather than continuous gradients, strong simplified shape reading in which every element is recognisable from its silhouette alone, deliberate flat areas carrying little internal texture, hard boundaries between shapes, high figure-to-ground contrast, no haze, no bloom, no soft gradient transitions, no depth-of-field blur; the whole composition must survive being reproduced small and in low fidelity and still read correctly
```

**What stays fixed across the crispness axis:** the entire shared style block,
the world-flavour prefix, and the whole of `prompt_tail` -- subject,
composition, camera, prop list, weirdness tier, palette accent and every
concept-specific fix. In `crisp_sweep.json` the three assets for one subject
carry a byte-identical `prompt_tail`; only `theme` changes. That is what makes
it a sweep rather than three re-rolls.

**What varies:** rendering fidelity language only -- focus, haze, micro-detail,
edge hardness, tonal-step count. Note that rendering-fidelity words had to be
*stripped out of the subject tails* to keep the axis clean (gen2's tails said
things like "rendered SHARP and crisply defined throughout" and "crisp painted
highlights"; those were removed or reworded to geometry language such as
"geometrically CORRECT -- true rectangles, straight unbroken edges"). If you
reuse a tail from `endgame_concepts_gen2.json`, do that same strip first or the
axis is contaminated.

## Axis 2 -- DOOM LEVEL

Carried in `prompt_tail`, not in the theme, because it changes what is in the
room as well as the colour. The `office_doom_*` trio is the controlled study:
one preamble string shared verbatim by all three, then one doom clause.

### Fixed preamble shared by all three doom levels

```
the small office of a modest independent AI-safety research lab, shot as a wide interior three-quarter view from just inside the doorway at standing eye height, IDENTICAL FRAMING AND IDENTICAL CAMERA POSITION every time: the same two pushed-together desks on the left, the same window in the back wall, the same whiteboard on the right-hand wall, the same bookshelf in the far right corner, the same kettle and mugs on the same low cabinet by the door, the same worn carpet tile floor, the same suspended ceiling; NO PEOPLE ANYWHERE IN THE ROOM and no figures visible through the window; the room must be read entirely through its objects
```

### The clause that varies

**doom LOW**

```
DOOM LEVEL LOW -- the room is ordinary, warm and lived-in and entirely fine: tidy-ish desks with two flat monitors asleep, a half-finished mug of tea, a potted plant that is clearly being watered, a bicycle helmet on a hook, a couple of framed prints hung straight, the whiteboard carrying a few clean simple diagram shapes with plenty of empty board left, the bookshelf comfortably half full; late afternoon daylight coming in through the window doing all the work, plus one banker's desk lamp with the green glass shade on a brass stem switched on at the near desk; LOW weirdness tier, the single warm amber #e8a33d accent is that lamp, every other light is plain untinted daylight or plain ordinary ceiling fluorescent, no coloured mood light anywhere; grounds still sit in the deep aubergine and ink family in the corners but the overall register is warm, calm and unremarkable; nothing in the room is wrong yet
```

**doom MID**

```
DOOM LEVEL MEDIUM -- the SAME room from the SAME camera, but the work has grown and started to press on the space: two more monitors have been added on stacked boxes, cables now run across the floor under gaffer tape, a second-hand server unit hums on the cabinet where the kettle used to have room, printouts and ring binders and manila folders are stacked on every horizontal surface and beginning to colonise the floor, the whiteboard is now dense with overlapping diagram shapes and arrows with no clean board left, the plant is browning, one framed print hangs slightly crooked; the daylight has gone blue and the window shows late dusk, the room is colder and greyer, the banker's lamp still on but no longer sufficient; MEDIUM weirdness tier, the single cold electric-blue #5c7ac3 accent is the screen glow off the monitors, every other light plain and untinted; something in the room is faintly wrong in a way that is hard to name -- the shadow under the far desk falls the wrong way relative to every other shadow in the room, and nothing else announces itself
```

**doom HIGH**

```
DOOM LEVEL HIGH -- the SAME room from the SAME camera, barely coping: equipment has taken the room over, racks and loose hardware where the bookshelf was, paper in drifts across the floor, chairs pushed aside and unused, cable bundles lashed to the ceiling grid, ceiling tiles removed, the whiteboard completely covered edge to edge and overwritten past legibility, the plant dead, the framed prints taken down and leaning against the skirting; DEEP INDIGO #181b3b AND #2e2547 DOMINATE THE WHOLE FRAME and the window shows only night; the ceiling fluorescents are dead and unlit, so the one thing holding out is the same banker's desk lamp with the green glass shade still burning on the near desk, a small stubborn pool of ordinary warm tungsten light in an otherwise indigo room; HIGH weirdness tier, so beyond that lamp the only other permitted saturated note is a single thin eldritch violet #7a3b8f seam of light along one wall junction where the wall no longer quite meets the ceiling; no coloured ambient light, no tinted room lighting, no fog, no glow spill -- the dread is structural and material, not atmospheric
```

Colour grammar being tested, stated compactly:

| doom | dominant ground | single permitted accent | source of the accent |
|---|---|---|---|
| low | warm neutrals, aubergine only in corners | warm amber `#e8a33d` | banker's desk lamp, an in-world fixture |
| mid | cold greys, blue dusk | cold electric blue `#5c7ac3` | monitor screen glow, an in-world fixture |
| high | deep indigo `#181b3b` / `#2e2547` dominant | warm amber holding out, plus one thin violet `#7a3b8f` seam | same desk lamp; the violet is the wrongness itself |

The invariant across all three (rule A1): **no ambient light is ever tinted.**
Every colour in frame is emitted by a nameable object. Doom expresses as
*which fixtures are still working* and *how much of the frame the ground
colour has taken*, never as a coloured room light.

## Axis 3 -- TREATMENT (which crispness arm a new subject gets)

Assignments used tonight in `new_subjects.json`:

| asset | treatment | doom | why |
|---|---|---|---|
| `office_doom_low` | crisp | low | trio holds treatment fixed so doom is the only variable |
| `office_doom_mid` | crisp | mid | trio holds treatment fixed so doom is the only variable |
| `office_doom_high` | crisp | high | trio holds treatment fixed so doom is the only variable |
| `server_altar` | graphic | high | symmetry and silhouette are the whole idea, so flat poster reading suits it |
| `lab_exterior_dusk` | soft | mid | the sky's wrongness needs soft gradient banding to be visible at all |
| `permit_wall` | crisp | low | paper fibre and stamp edges ARE the subject; softness would destroy it |

Fixed across the treatment axis: subject, camera, prop list, palette tier.
Varies: only the modifier string from Axis 1.

## Axis 4 -- PEOPLE POLICY

Rule A2. Three settings exist; tonight's batches used the strictest one
everywhere except the atrium, which needs a queue to read as a polling hall.

**Setting 0 -- none (default, and what `new_subjects.json` uses throughout).**
The `poster_people` style string already forbids figures; each tail also says
so locally, because a local restatement beats a global one in practice:

```
NO PEOPLE ANYWHERE IN THE ROOM and no figures visible through the window; the room must be read entirely through its objects
```

Other local phrasings used tonight, all interchangeable:

```
no people at all in frame, no destitution imagery, no distress
```

```
ABSOLUTELY NO PEOPLE, no robes, no candles, no religious iconography
```

```
NO PEOPLE AND NO HANDS in frame at all
```

```
NO PEOPLE anywhere, no silhouette in the lit window, no figures in the street
```

**Setting 1 -- unavoidable single figure: androgynous silhouette.**

```
rendered as dark androgynous silhouettes with no face detail and no distinguishing jewellery, and they are small and incidental
```

**Setting 2 -- unavoidable group: varied ordinary staff.**

```
the small queue of voters is a genuinely varied ordinary group of office workers in plain institutional clothing
```

Fixed across the people axis: everything else. Varies: only the clause above.
The failure mode being defended against, in Pip's words from the review, is
that default generated people read as "interesting generic people" who imply
the viewer should be *responding* rather than *observing*.

## How to reuse these for website imagery

For `pdoom1-website` work, the split is roughly: keep the discipline strings,
rewrite the subject strings, and loosen two constraints.

**Keep verbatim.** These are what make the set look like one set, and none of
them are game-specific:

- `poster_lighting` in full. The "75 percent more subtle" clause and "mood
  must NEVER come from the main light source" is the single highest-value
  string here and it transfers to any medium.
- `poster_palette` in full. The hex anchors are the brand.
- `poster_safety` in full. Non-negotiable on a public site.
- The no-text clause inside `poster_base` (`no text, no lettering, no signage,
  no numerals, no logo, no watermark, no UI overlay`). Web imagery gets its
  text from HTML, never from the model -- generated lettering is always
  slightly wrong and it dates the asset instantly.
- The A5 legibility clause: `every object in frame must be immediately
  identifiable as a specific real thing ... an unrecognisable object is visual
  noise rather than a prop`.

**Change.**

- **Aspect and size.** Website heroes usually want wider than 3:2 and the cap
  is 1536x1024. Generate at 1536x1024 and crop, do not ask for a banner
  aspect. For a retina 2x hero you must upscale outside this pipeline.
- **Treatment.** Prefer `_graphic` for anything that will sit behind text or
  render at card size, and `_crisp` for a full-bleed hero. `_soft` is the
  weakest choice on the web: haze plus JPEG plus a dark-mode background is
  where images turn to mud.
- **Composition safe area.** None of tonight's prompts reserve space for an
  overlay. Add an explicit clause, e.g. "the left third of the frame is quiet
  and low-contrast with no important detail, reserved for an overlay".
- **`poster_base`'s "painterly warm-grime texture with heavy dark outlines"**
  is a game-poster register. For a site that also has to look like a real
  research org, soften it or drop the heavy outlines.
- **Weirdness tier.** Public-facing pages probably want LOW almost everywhere.
  HIGH-tier violet reads as horror marketing.

**Provisional, not settled -- do not build a website style guide on these yet.**

- **All of A1-A10 are on probation.** The review file says so explicitly: they
  are "guidelines on probation, not settled law", and the gate on promoting
  any of them is a review of one full regeneration cycle. Tonight's batches
  plus `endgame_concepts_gen2` ARE that cycle. Nothing here has passed the
  gate.
- **A2 (no people) is flagged as the most likely to be over-broad** -- possibly
  really "no *incidental* people". A website almost certainly needs people
  somewhere, so treat A2 as a poster-art rule and re-decide it for web.
- **The three crispness modifiers are one night old and barely tested.** What
  the first run actually showed: mean edge-energy rose from `_soft` to `_crisp`
  on all four subjects, but by wildly different amounts -- drone +58 percent,
  atrium +26, chokehold +23, shuttered street +4. The +4 case is the
  interesting one, because looking at that pair the `_crisp` arm is plainly
  better at the exact defect it was aimed at (the chain-link fence hangs
  correctly and runs to a terminating post instead of dissolving) even though
  the metric barely moved -- rain and canvas texture swamp the high-frequency
  measurement. Judge these by eye on the specific prop that was failing, not by
  a sharpness statistic. Compare
  the `_soft` / `_crisp` / `_graphic` triples in `art_generated/crisp_sweep/v1/`
  before trusting the language; if `_crisp` did not visibly beat `_soft`, the
  lever is weaker than the wording implies and needs strengthening rather than
  reuse.
- **The doom colour grammar is a proposal**, generated to feed Pip's open
  design question, not an answer to it.
- Settled and safe to reuse regardless: A9 (the term is POSTER ART, a naming
  correction rather than a taste judgement) and the safety string.

## Reproducing tonight's runs

```
python tools/assets/generate_images.py --file tools/assets/manifests/crisp_sweep.json --variants 2 --dry-run
python tools/assets/generate_images.py --file tools/assets/manifests/crisp_sweep.json --variants 2 --yes
python tools/assets/generate_images.py --file tools/assets/manifests/new_subjects.json --variants 2 --dry-run
python tools/assets/generate_images.py --file tools/assets/manifests/new_subjects.json --variants 2 --yes
```

Two variants per asset because PART C of the review validated the pair method:
a single image cannot be reacted to usefully, a pair can.

# Prompt-language diff -- quirk icons vs earlier icon sets (2026-07-26)

Pip's read on the quirk-icon set (#903/#909): "fresher and bolder". This note
compares the actual prompt strings across three icon batches to find what
changed, what correlates with promotion, and what to keep doing.

## The three sets compared

| set | manifest | date / model | outcome (evidence) |
|---|---|---|---|
| quirk icons | `art_prompts/quirk_icons.yaml` | 2026-07-25, gpt-image-1.5 | 16/16 shipped to `godot/assets/icons/quirks/` the same day (PR #909) |
| employee_status family | `art_prompts/ui_icons.yaml` (category `employee_status`) | 2025-11-17, gpt-image-1 | `status: promoted` in-manifest; in-game since; ui_icons set overall: 58 promote / 5 dislike in `art_source/hero_verdicts.json` |
| iconset_round2 | `art_prompts/iconset_round2.yaml` | 2026-07-21, gpt-image-1.5 | 0 promote / 7 like / 4 dislike in `hero_verdicts.json` -- the 0-promoted set |

Confound to keep honest: iconset_round2 was partly a deliberate style
exploration (logo marks, seals, gauges, per-item restyles), so its 0-promote
outcome is not purely a prompt-language verdict. But the language differences
below are real and the promoted sets share the opposite habits.

## Diff 1 -- subject clause: one terse metaphor vs a scene essay

Quirk tails are a fixed formula, ~20-30 words: `circular indicator with a
[simple|large] X [doing Y], [2-4 word mood cue], plain dark background with
vignette`. The personality lives in a concrete VERB, not adjectives:

> "circular indicator with a simple round gauge dial with its needle pinned
> hard at maximum, small radiating alarm ticks, plain dark background with
> vignette" (doom_absolutist)

> "circular indicator with a simple battery symbol showing one dim low bar
> remaining, flat lifeless glow, plain dark background with vignette"
> (quiet_quitter)

> "circular indicator with a simple thermometer with its column surging and
> bursting at the top bulb, plain dark background with vignette" (runs_hot)

employee_status (promoted, 2025-11) already used the same skeleton, just less
boldly -- static symbols, no kinetic verb:

> "simple circular indicator with a solid green checkmark in center, clean
> crisp edges, soft green glow, plain dark background with vignette"
> (employee_status_active)

iconset_round2 tails run 50-80+ words, multi-clause, with inline hex codes,
parentheticals, and meta-commentary about how the image should be read:

> "a menacing but still cozy office-cat face, front-facing, channeling a black
> / dark-tabby cat with glowing amber laser-slit eyes (#F6A800 core fading to
> #E9752E glow) and a small glowing collar emblem; a subtle sinister
> narrowed-eye smirk; warm-red-to-aubergine graded ground (#B31217 rim light
> falling to #170A1C); the amber eye-glow is the single saturated accent. The
> \"evil\" reads from the narrowed..." (gen_cat_evil)

## Diff 2 -- colour: theme-level hue family vs hexes scattered in tails

quirk_icons moves ALL colour into theme-level `color_bias`, one accent family
per valence, with an explicit exclusion clause:

> "valence colour NEGATIVE -- the single saturated accent is an ominous
> crimson red glow (#E64D33 toward deep #B31A1A), dark desaturated grey-brown
> ground, no other saturated hue"

employee_status named colours ad hoc inside each tail ("solid green
checkmark", "yellow-orange color scheme", "dark red and grey tones") while its
theme said something else entirely ("desaturated teal and olive tones") -- it
worked, but set-level consistency came from luck and rerolls, not the manifest.

iconset_round2 put a ~10-hex narrative palette in `color_bias` ("grounds are
deep aubergine #170A1C and ink-brown #14040C ... souring toward orange #E9752E,
red-orange #E24A3B and deep red #B31217 as doom rises ...") AND repeated hexes
inside individual tails. Two colour authorities per image; neither wins
cleanly.

## Diff 3 -- base style: locked and reused vs re-invented per batch/item

quirk_icons reuses the promoted `global_icon_base` from ui_icons.yaml VERBATIM
("high-res 1024x1024 square game icon, single central symbol ... StarCraft 2 /
early-2000s XCOM ability icon feel ... strong chunky silhouette that reads
clearly at 64x64") plus `surface_tarkov`, and states the pattern out loud in
`_meta`: "Lock-base + colour-via-effects pattern ... one base circular
indicator treatment reused from the employee_status family ... ONLY the accent
hue tells valence."

iconset_round2 minted a new `house_base` ("painterly digital illustration ...
cozy-grimdark deadpan mood (lived-in office dread, quietly ominous, NEVER gory
-- no skulls, no blood, no death-metal)") and then restyled per item anyway
("re-rendered as crisp 8-bit / 16-bit PIXEL ART", logo marks, wax seals) -- so
the batch has no shared visual system for a reviewer to promote INTO.

## Three recommendations for future icon batches

1. **One metaphor, one verb, under ~25 words.** Keep the tail formula
   `"circular indicator with a simple X [doing Y], [2-4 word mood cue], plain
   dark background with vignette"`. Boldness comes from a kinetic verb
   ("needle pinned hard at maximum", "column surging and bursting"), never
   from stacking adjectives or explaining how the image should be read.

2. **Colour is a theme, not a tail.** Declare ONE accent hue family per theme
   in `color_bias` with 1-2 anchor hexes and the closing clause "no other
   saturated hue"; keep hex codes OUT of `prompt_tail`. This is what makes a
   set read as a system at 16-64px (valence/state legible from hue alone).

3. **Lock the base; A/B new styles separately.** Reuse the promoted
   `global_icon_base` verbatim for any production family and vary only glyph +
   accent. When a new look is wanted, run it as a small vanguard A/B (the
   cat-angle pattern, #900) BEFORE a production batch -- do not restyle
   per-item inside one set. iconset_round2 mixed painterly / pixel-art / logo
   briefs in one batch and promoted zero.

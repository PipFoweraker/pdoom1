# Next-round brief -- what Pip said while judging, 2026-08-14

**Captured by `seat:pdoom` from dictation during and after the first mass review.**
This is input to the NEXT generation round, not a verdict record. Verdicts live in
`tools/art_review/review_log.jsonl`.

---

## 1. The title-space axis does not have one winner

**The finding, from Pip's own dictation:** sweep step **`s4` is good on
`s05_r03_p09` and hated on `s10_r02_p08`.**

| named asset | verdict | his words |
|---|---|---|
| `s05_r03_p09 ... _s2` | keep | *"good negative space but it's dark, so we could use light font along the top"* |
| `s05_r03_p09 ... _s4` | keep | *"space on the right, possibly for vertial-stacked text or things that are dense"* |
| `s05_r03_p09 ... _s5` | keep | *"similar"* |
| `s10_r02_p08 ... _s4` | **discard** | *"I hate, avoid avoid undo bad"* |
| `s20_r01_p09 ... _s4` | shelf | *"maybe with some cunning cropping?"* |

**Why this matters more than five verdicts.** The seven `l2_a_*` blocks were
briefed as parameter sweeps -- vary one axis, hold everything else, pick ONE
winner per axis. That framing is in the gallery block headers as of today.

**For title-space it appears to be wrong.** The same step lands well on one
subject/palette and badly on another, which means the axis is **not separable**
from what it is applied to. A single winner would be a false summary.

**Consequence for the next round:** either sweep title-space *within* a fixed
subject and palette rather than across them, or accept that this axis needs a
winner per subject family and budget for it. **Do not let "one winner per axis"
collapse it.**

**Not yet known:** whether the other six axes (decay, distance, pitch, quiet,
style-tween, yaw) are separable. Nobody has judged enough of them to say. Treat
"one winner per axis" as a hypothesis per axis, not a rule.

## 2. Negative space plus abstraction is a PRINT format, not just a layout

> *"the abstract ones with lots of white space I think lend themselves to being
> printed on white paper and then cut out well"*

This is a distinct product idea from the poster/hero use, and it changes what
"good" means:

- **White ground stops being a compositional choice and becomes free stock.**
  Ink coverage is cost; unprinted paper is the cheapest element on the card.
- **The cut line becomes part of the composition.** An asset that reads well
  full-bleed may be unusable when the silhouette is the edge.
- **It suits the existing palette exactly**: a four-flat-ink screenprint with one
  signal-red accent is already print-native, and the `p06`-style inverted
  bright-paper palette is the obvious candidate ground.
- **Small-format legibility becomes the gate**, not poster value structure. A
  hero is judged at 1536px; a hand-out card is judged at 85mm.

**Feeds:** the P(Doom) cards Pip hands out, and the "make them cuter and more
engaging" ask. **The title-space sweep already generated for this** -- it is the
only block that deliberately varies reserved text area.

## 3. Text placement vocabulary worth carrying into prompts

From his notes, the useful distinctions are about WHERE the space is, and the
current sweep does not name them:

| shape | his phrasing | implies |
|---|---|---|
| dark band, top | *"dark, so we could use light font along the top"* | reversed-out type, banner-style |
| right-hand column | *"space on the right, vertial-stacked text or things that are dense"* | vertical lockup, or dense info -- a stat block, a URL, a QR |
| croppable | *"maybe with some cunning cropping"* | the space exists but not where the frame puts it |

**Suggestion for the next queue spec:** ask for the reserved area **by position
and by intended contents** ("a dark band across the top third for reversed-out
title type"), not by amount. The current sweep varies *how much*, and every one of
Pip's reactions was about *where* and *what for*.

## 4. Standing, unresolved

- **2400px.** Nothing generated can fill the website hero slot; the generator has
  only ever produced 1024x1024, 1536x1024, 1024x1536. Card printing may not care
  -- 85mm at 300dpi is ~1004px, so **1024 is enough for a card and not for a
  web hero.** Worth knowing before commissioning an upscale path.
- **Generation spend policy expires 2026-08-15.**

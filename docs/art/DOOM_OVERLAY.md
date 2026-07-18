# Doom Overlay -- "doom is a layer, not a repaint"

`tools/art_review/doom_overlay_preview.html` is a standalone, offline art-review
tool (double-click to open; no network/APIs). It demonstrates the core rendering
principle for P(Doom)1 doom intensity:

> A base asset is authored **doom-neutral**. Doom is composited **on top** as an
> ADDITIVE overlay -- radial glow + a low-alpha colour-grade + an edge aura --
> never a recolour of the base art file. The base pixels stay visible underneath.

## What it shows
Real repo assets (a cat photo, a pixellab operator sprite, a PC-tower prop, a
monitor prop) each render on a canvas. Two sliders drive the two doom axes; a
third scales overall intensity; toggles isolate each overlay pass; five presets
match the game's doom BANDS.

## The two axes
- **Weirdness** (the AI/computers themselves): green (ok) -> electric blue
  (acting up) -> violet (eldritch). Blue/violet stops come from
  `docs/art/palette.json` (extracted hero palette); the **green** stop is not in
  palette.json (the hero has no green) and is taken from the Axis-B table in
  `PALETTE_AND_DOOM_INTENSITY.md`.
- **Catastrophe** (real-world things going wrong): amber -> orange -> red ->
  fire. **Hand-sourced** -- palette.json has no warm amber at all, so these are
  tasteful hand-picked values, clearly labelled as such in the tool.

## Bands
The five presets map to the doom bands the game keys off (the same lookup shape
as a `MUSIC_TIER_BY_BAND` table): cosy / uneasy / spooky / eldritch / terminal.
Each band sets a `(weirdness, catastrophe)` pair; the overlay recomposites live.

## Compositing (how it stays additive)
- Glow: `globalCompositeOperation = "lighter"` radial gradients, one per axis.
- Grade: a low-alpha translucent tint gelled over the frame (base still reads).
- Edge aura: a coloured drop-shadow bloom cast off the sprite silhouette.
No `getImageData`/pixel readback -- the base image is never rewritten.

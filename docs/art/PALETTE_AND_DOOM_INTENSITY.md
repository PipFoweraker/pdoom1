# P(Doom)1 -- Palette + Doom-Intensity Spec

> The shared visual language, so agents (and humans) tune assets to *values*, not vibes.
> Grounded in Pip's own prior work: the midjourney hero bg
> (`godot/assets/dump_october_31_2025/hero-bg-2400w.webp`), the existing colour tokens in
> `glow_cat_button_design.md`, and the `art_prompts/hero_banners.yaml` colour bias.
> First pass -- Pip (son of an interior designer) will tune the swatches. Open
> `tools/art_review/palette.html` to eyeball them.

## The two registers (why the office looks warmer than the banners)
1. **Cozy office (pixel art, in-game floor):** warm, lived-in, a *little* pastel/textured, not
   hyper-saturated -- "cozy competence." This is the warm-grime-heft look.
2. **Dark dread (banners / high-doom / the edges):** near-black aubergine, painterly, the amber
   CRT glow as the *only* saturated accent -- "existential dread at the edges."
   They are the SAME world at different doom levels: the office is register 1 at low doom and
   slides toward register 2 as doom rises.

## Palette (real values)

### Grounds / darks (from the hero bg; the dread base)
| name | hex | source |
|---|---|---|
| Void | `#0E0614` | hero bottom-right avg |
| Deep aubergine | `#170A1C` | hero dominant (90%) |
| Ink brown | `#14040C` | hero bottom-left avg |
| Steel | `#1C2730` | glow_cat "Steel" |
| Graphite | `#0E1318` | glow_cat "Graphite" |

### Warm office base (register 1)
| name | hex | note |
|---|---|---|
| Warm panel | `#2B221A` | our pixel-tool panel |
| Warm line | `#3A2E22` | outline/edge warm |
| Cozy amber (CRT glow) | `#E8A33D` | the hero warm accent, pixel tuned |
| Amber (UI token) | `#F6A800` | glow_cat "Warn/Armed Amber" -- the ONLY saturated accent at rest |

### Neutrals
| name | hex |
|---|---|
| Chrome / slate | `#6B7C8C` |
| Off-white text | `#E9F2F2` |
| Teal (UI action) | `#1EC3B3` (hover `#0FA5A0`) |

## Colour semantics (Pip's rules -- what each hue MEANS)
Colour is not decoration here; it encodes game state. Two independent axes:

### Axis A -- CATASTROPHE (real-world things going wrong; "things actually catch fire")
Cozy amber sours toward red and then literal fire. This IS the existing glow_cat doom overlay.
| tier | hex | reads as |
|---|---|---|
| 0 cosy | `#F6A800` (amber) | normal, warm, focused |
| 1 uneasy | `#E9752E` (orange) | something is off |
| 2 alarmed | `#E24A3B` (red-orange) | warning strobes, soured glow |
| 3 critical | `#B31217` (deep red) | red curve climbing off the chart |
| 4 fire | `#DD5F4C` + `#F69168` flames | literal fire (hero: burning monitors) |

### Axis B -- WEIRDNESS (the AI / computers themselves)
Green = correct, blue = acting up, purple = eldritch. (Pip: green mostly means OK-ness, so it
reads as computers doing things *expectedly*; blue when they start acting up; purple only when it
crosses from regular-weird into ELDRITCH weird -- super-high doom / weird endgame.)
| level | hex | reads as |
|---|---|---|
| ok | `#3F8A5C` / `#234C34` (green) | computers working correctly/expectedly |
| acting up | `#354375` -> `#5C7AC3` (electric blue) | early weird, glitching, arcing (hero: blue lightning) |
| ELDRITCH | `#504673` -> `#7A3B8F` -> `#96718F` (violet) | it has gone wrong in a wrong way; endgame |

## Lighting discipline (Pip's rule)
**At most ONE ambient light + ONE weird/glowing source per lighting scene**, generally. The glow
source's hue is chosen from the axes above to signal *what kind* of trouble. Don't stack multiple
saturated glows -- the hero works because it's near-black with disciplined, separated pockets
(one red CRT here, one blue arc there, one green light there), not a rainbow.
Spooky palettes may appear in different FLAVOURS (not only purple); purple/electric-blue/CRT-green
don't blend as a whole, but read elegantly when separated by lots of dark/grey/blue negative space
(as in the hero + banners).

## Doom-intensity BANDS (the universal reference for cats, windows, glows, banners)
Combine the two axes into bands the game keys off. Assets are authored per-band.
| band | catastrophe | weirdness | office register | cat form | window sky |
|---|---|---|---|---|---|
| 0 Cosy | amber | green/none | warm cozy | singed tabby (gag) | clear / bright |
| 1 Uneasy | amber->orange | faint blue flicker | warm, dimming | tabby, alert | overcast |
| 2 Spooky | orange->red | blue arcing | shadows lengthen | spooky black cat | stormy, rain |
| 3 Eldritch | red | violet creeping | dark dread | eldritch cat (violet glow, smoke) | doomy red-purple |
| 4 Terminal | fire | full violet | near-black + flame | terminal/void cat | apocalyptic, fire-lit |

## How to prompt to this (for pixellab / any generator)
- Name the ambient + the single glow explicitly ("lit warm amber from the left, one cold blue
  screen-glow"). Never ask for many glows.
- For doom assets, state the BAND and pull the glow hex from the table.
- Keep base surfaces in the warm-office or dark-dread grounds; let the accent be the only saturated thing.
- Purple is EXPENSIVE -- reserve it for band 3+ (eldritch/endgame). Don't purple everything.

## Open for Pip (tune these)
- Exact swatch values (you'll eyedrop/adjust -- this is a first pass from real pixels).
- Whether green should ever appear as an *accent* in the cozy office (I've kept it as a
  computer-state signal only, per your note that green mostly = OK-ness).
- Number of swatches per set -- currently ~5 grounds, ~4 warm, ~3 neutral, 5+3 semantic. Expand/trim to taste.

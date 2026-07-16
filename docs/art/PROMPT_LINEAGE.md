# Art prompt lineage -- where the P(Doom)1 look came from

> Dev-history capture (2026-07-17). Preserving Pip's original image-generation prompt language
> (2025, gpt-image-1 / midjourney era) for the dev blog and future retrospectives -- and because
> it's the direct ancestor of the current palette + doom-intensity spec
> (`docs/art/PALETTE_AND_DOOM_INTENSITY.md`). Raw sources live in `art_prompts/*.yaml` and
> `godot/assets/dump_october_31_2025/`.

## The founding mood (from `art_prompts/hero_banners.yaml`)
Three reusable "style" fragments Pip wrote to bias every banner:

- **banner_scene_base** -- "a full illustrative SCENE with real environmental depth... lush
  StarCraft 2 / XCOM digital matte-painting, cinematic composition with foreground, midground and
  background layers, volumetric haze and soft god-rays, dramatic but restrained key lighting."
- **surface_tarkov** -- "Tarkov-style worn metal, scuffed brushed aluminium, chipped paint, dust,
  fingerprints and grime on every surface, lived-in industrial props, exposed cable runs and cheap
  office furniture that has seen years of use."
- **mood_cozy_dread** -- "cozy competence under existential dread, quiet and intimate yet quietly
  ominous, the warmth of late-night focus haunted by something larger looming just off-frame."

And the **colour bias** that still governs the world:
> "heavily desaturated palette of teal and olive with muted slate greys, warm amber CRT/monitor
> glow as the only saturated accent, deep shadow, low overall saturation."

## The three original heroes (quoted for posterity)
- **Title Screen Hero** -- "a dim near-future AI-safety lab and open-plan office at night, seen from
  a low three-quarter angle across a cluttered desk... banks of chunky CRT-style terminals... a
  single window shows a cold blue city skyline... warm and focused up close but the darkness at the
  edges is quietly ominous."
- **Doom Rising** -- "dread is escalating... the amber terminal glow has soured toward a harsh red,
  warning strobes and status lights flare... a wall of monitors shows a single rising red curve
  climbing off the top of its chart; smoke or thick haze creeps low across the floor." (This is
  literally Axis A -- Catastrophe -- described in prose two years before we formalized it.)
- **Strategic Moves Granted** -- "a shadowed boardroom... seated silhouetted board members (backs
  and shoulders, no close-up faces) turned toward a single illuminated seat." (The founder /
  operator silhouette lineage.)

## The colour system that already existed (from `glow_cat_button_design.md`, 2025-10-31)
Pip had already tokenised a UI colour system and -- crucially -- a **doom-tier overlay ladder**:
> Tier 0 -> none | Tier 1 `#F6A800 @6%` | Tier 2 `#E9752E @10%` | Tier 3 `#E24A3B @14%` | Tier 4 `#B31217 @18%`

That amber->red ladder is now **Axis A (Catastrophe)** in the spec, unchanged. Accents (Action Teal
`#1EC3B3`, Amber `#F6A800`), grounds (Graphite `#0E1318`, Steel `#1C2730`), and the "amber as the
only saturated accent" discipline all carried straight through.

## Other raw prompt sets preserved
`art_prompts/batch_2_actions_and_ui.yaml`, `batch_3_backgrounds.yaml`,
`batch_4_terminal_textures.yaml`, `ui_icons.yaml/.json` -- the action/UI/background/terminal prompt
banks from the same era. Kept as-is.

## The through-line
The look was never accidental: **cozy competence + existential dread + amber-as-the-only-accent +
lived-in grime**, with doom encoded as colour. The 2026 pixel-art pipeline (warm-grime-heft) and
the palette/doom-intensity spec are the same DNA, re-expressed at 48px. Good material for a
"how the P(Doom)1 look evolved" blog post.

## Note on heroes/banners going forward
Heroes and banners are painterly matte-paintings -- generate them on the **gpt-image-1 pipeline**
(`tools/assets/`, the existing 91-icon pipeline), NOT pixellab (which is a pixel-sprite engine).
pixellab is for the in-game pixel assets. Building out the banner prompt language there is its own
fun track.

# Shader-as-animation -- the reusable technique

_Established 2026-07-23 alongside `time_portal.gdshader` (the #801 cold-open
portal, UPGRADE layer). Captured here so the TECHNIQUE outlives the one portal._

## The idea (why this exists)

Every visual knob in a shader is a `uniform`. A Godot `Tween` can drive any
uniform at runtime, so you get smooth, cheap, fully-tunable animation with **no
per-frame CPU work and no re-generated frames** -- the GPU does it all from
`TIME` + the uniform values. This is a general animation capability, not a
one-off for the portal: reach for it instead of hand-animating sprites or
re-rendering frame sequences whenever an effect can be expressed procedurally
(pulses, wipes, reveals, glows, dissolves, distortions).

The design note that seeded this: `docs/game-design/COLD_OPEN_SEQUENCE.md` ->
"Reusable techniques + aesthetic motifs" -> _Shader-as-animation-capability_.

## The portal shader

`godot/assets/shaders/time_portal.gdshader` -- a procedural rotating vortex:
concentric spiralling rings, radial swirl distortion, a glowing core, and an
on-brand CRT scanline overlay. Looks good with ZERO tuning (ominous doom-red).

### The dials (uniforms)

| Uniform | Default | Range (demo) | What it does |
| --- | --- | --- | --- |
| `swirl_speed` | 0.6 | 0..3 | vortex rotation speed |
| `swirl_direction` | 1.0 | -1 / +1 | spin direction (CW / CCW) |
| `distortion` | 0.55 | 0..2 | radial swirl / spiral-arm curl |
| `ring_count` | 14.0 | 0..40 | concentric rings across the radius |
| `ring_thickness` | 0.5 | 0..1 | 0 = thin sharp rings, 1 = broad soft bands |
| `ring_strength` | 0.6 | 0..2 | how brightly the rings read |
| `glow_size` | 0.35 | 0..1 | radius of the glowing core |
| `glow_strength` | 1.6 | 0..4 | core brightness |
| `color_core` | (1.00, 0.85, 0.55) | -- | hot centre colour |
| `color_mid` | (0.95, 0.12, 0.10) | -- | body colour (doom-red) |
| `color_edge` | (0.35, 0.02, 0.05) | -- | dark rim colour |
| `scanline_intensity` | 0.12 | 0..1 | CRT scanline strength (0 = off) |
| `scanline_count` | 240.0 | 20..600 | number of scanlines |
| `edge_feather` | 0.08 | 0..0.5 | soft outer edge of the disc |
| `aspect` | 1.0 | -- | rect width/height (keeps the disc round) |
| `open_progress` | 1.0 | 0..1 | **Tween this to open the portal** |

Colour presets (also in the shader header): doom-red (default), CRT
phosphor-green (`TerminalTheme.GREEN` family), amber (`TerminalTheme.AMBER`).

## Instancing the portal

A `TextureRect` only draws when it HAS a texture (otherwise the fragment shader
never runs). Two easy options:

```gdscript
# Option A -- ColorRect (simplest; always covers its rect, no texture needed).
var rect := ColorRect.new()
rect.custom_minimum_size = Vector2(512, 512)
var mat := ShaderMaterial.new()
mat.shader = load("res://assets/shaders/time_portal.gdshader")
rect.material = mat
add_child(rect)

# Option B -- TextureRect (per COLD_OPEN spec) with a plain white placeholder.
var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
img.fill(Color.WHITE)
tex_rect.texture = ImageTexture.create_from_image(img)
tex_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
tex_rect.stretch_mode = TextureRect.STRETCH_SCALE
tex_rect.material = mat
```

Set `aspect` to the rect's `size.x / size.y` (and on `resized`) so the disc
stays circular on non-square rects. Set any dial with
`mat.set_shader_parameter("swirl_speed", 0.9)`.

## The reusable pattern: Tween a uniform

```gdscript
# Portal "pops into existence" -- grows from a point with a bright leading edge.
var tw := create_tween()
tw.tween_property(mat, "shader_parameter/open_progress", 1.0, 1.6) \
	.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
```

`open_progress = 0` -> the portal is a point (invisible). As it rises to `1` a
circular mask expands outward and a bright rim flashes at the growing front,
then settles into the steady vortex. Reverse the tween (1 -> 0) to CLOSE it.
The same one-liner animates ANY uniform -- e.g. spin up `swirl_speed`, bloom
`glow_strength`, or fade `scanline_intensity`.

Note: `"shader_parameter/<name>"` is the Tween property path for a
`ShaderMaterial` uniform. (In the demo harness we tween via a small method
instead, only so the on-screen slider follows along -- either works.)

## Wiring into the cold-open (for Pip, later)

`godot/scripts/ui/cold_open_sequence.gd` is Agent 1's SHIP-NOW core -- **do not
edit it as part of this technique drop.** When you want the portal in the
opening beat ("1. PORTAL opens (spinny effects) over black"):

1. Add a portal rect (Option A/B above) as the FIRST beat's visual, over the
   existing black `ColorRect`, before the text beats.
2. Start it closed: `mat.set_shader_parameter("open_progress", 0.0)`.
3. On the beat's tween timeline, tween `shader_parameter/open_progress` 0 -> 1
   (open), hold during the "portal open" beat, then either tween it back to 0
   (collapse) or fade the rect's `modulate:a` as the text fade-up begins.

That is the entire integration hook: the portal is a self-contained rect whose
one animation input is `open_progress`, driven by the same Tween machinery the
cold-open already uses for its fade-up/pop-in beats.

## Live tuning

Open `godot/scenes/dev/portal_shader_demo.tscn` in the editor and run it (F6, or
temporarily set it as the main scene). Every dial above is a live slider /
colour picker; preset buttons swap the palette; "Play open (0 -> 1)" previews
the reveal (with a loop toggle). Dev-only -- not referenced by any shipped flow.

// time_portal.gdshader -- procedural time-travel PORTAL for the #801 cold-open
// (UPGRADE layer). Pure canvas_item shader: a rotating radial swirl / vortex with
// concentric rings, radial UV distortion, a glowing core and an on-brand CRT
// scanline overlay. NO generated frames -- the spin is 100% procedural, driven by
// TIME plus the exposed uniforms below.
//
// REUSABLE ANIMATION TECHNIQUE
// ----------------------------
// Every visual knob is a `uniform`, so a Godot Tween can animate any of them at
// runtime for near-zero cost (no per-frame texture regen, no CPU work). The
// headline example is `open_progress` (0..1): Tween it 0 -> 1 and the portal
// "pops into existence" (grows from a point, with a bright expanding leading
// edge that flashes then settles). The SAME pattern -- Tween a shader uniform --
// is a general animation capability reusable across the game. See
// godot/assets/shaders/README_shader_animation.md.
//
// USAGE
// -----
//   * Put this ShaderMaterial on a ColorRect (simplest) or a TextureRect that
//     HAS a texture assigned (a TextureRect with no texture draws nothing, so
//     the fragment never runs -- give it any placeholder texture; the shader
//     ignores TEXTURE and writes its own COLOR).
//   * Defaults look good with ZERO tuning (ominous doom-red vortex).
//   * Live-tune every dial in godot/scenes/dev/portal_shader_demo.tscn.
//
// COLOUR PRESETS (copy into the three color uniforms; matches TerminalTheme)
//   Doom-red (DEFAULT):
//     color_core = (1.00, 0.85, 0.55)  color_mid = (0.95, 0.12, 0.10)  color_edge = (0.35, 0.02, 0.05)
//   CRT phosphor-green (TerminalTheme.GREEN family):
//     color_core = (0.75, 1.00, 0.80)  color_mid = (0.36, 0.93, 0.47)  color_edge = (0.03, 0.20, 0.08)
//   Amber (TerminalTheme.AMBER family):
//     color_core = (1.00, 0.92, 0.62)  color_mid = (1.00, 0.72, 0.20)  color_edge = (0.28, 0.14, 0.00)

shader_type canvas_item;
render_mode blend_mix;

// ---- Motion dials --------------------------------------------------------
uniform float swirl_speed = 0.6;       // vortex rotation speed (revs-ish/sec)
uniform float swirl_direction = 1.0;   // +1 = clockwise, -1 = counter-clockwise
uniform float distortion = 0.55;       // radial swirl distortion (spiral arm curl)

// ---- Ring dials ----------------------------------------------------------
uniform float ring_count = 14.0;       // number of concentric rings across radius
uniform float ring_thickness = 0.5;    // 0 = thin/sharp rings, 1 = broad/soft bands
uniform float ring_strength = 0.6;     // how brightly the rings read

// ---- Core glow dials -----------------------------------------------------
uniform float glow_size = 0.35;        // radius of the glowing core (0..1)
uniform float glow_strength = 1.6;     // core brightness

// ---- Colour dials (doom-red defaults; presets in the header) -------------
uniform vec3 color_core : source_color = vec3(1.00, 0.85, 0.55);
uniform vec3 color_mid  : source_color = vec3(0.95, 0.12, 0.10);
uniform vec3 color_edge : source_color = vec3(0.35, 0.02, 0.05);

// ---- CRT scanline overlay dials ------------------------------------------
uniform float scanline_intensity = 0.12;  // 0 = off, 1 = heavy
uniform float scanline_count = 240.0;      // number of scanlines top-to-bottom

// ---- Shape / reveal dials ------------------------------------------------
uniform float edge_feather = 0.08;     // soft outer edge of the disc (0..0.5)
uniform float aspect = 1.0;            // rect width/height, keeps the disc circular
uniform float open_progress = 1.0;     // 0..1 -- TWEEN THIS to open the portal

// Note: TAU and PI are built-in constants in the Godot shading language.

void fragment() {
	// Centre the UV and correct for the rect's aspect so the disc stays round.
	vec2 p = UV - vec2(0.5);
	p.x *= aspect;
	float r = length(p) * 2.0;         // ~0 at centre, ~1 at the disc rim
	float ang = atan(p.y, p.x);

	float t = TIME * swirl_speed * swirl_direction;

	// Radial swirl: rotate the sampling angle MORE toward the centre so the rings
	// curl into spiral arms. `distortion` sets how tight the curl is.
	float swirl = ang + t + swirl_direction * distortion * 8.0 / (r + 0.35);

	// Concentric (spiralling) rings. ring_thickness maps to a sharpening power:
	// thickness 1 -> broad soft bands, thickness 0 -> thin bright filaments.
	float rings = 0.5 + 0.5 * sin(r * ring_count * TAU - swirl * 2.0 - t * 3.0);
	float sharpen = 1.0 + (1.0 - clamp(ring_thickness, 0.0, 1.0)) * 6.0;
	rings = pow(rings, sharpen);

	// Hot glowing core, brightest at the centre, fading out by glow_size.
	float core = glow_strength * smoothstep(glow_size, 0.0, r);

	// Base body colour: core -> mid -> edge across the radius.
	vec3 col = mix(color_core, color_mid, smoothstep(0.0, glow_size * 1.5, r));
	col = mix(col, color_edge, smoothstep(glow_size * 1.5, 1.0, r));
	col += color_mid * rings * ring_strength;   // ring highlights
	col += color_core * core;                   // hot core

	// CRT scanline overlay (screen-space vertical modulation).
	float sl = 1.0 - scanline_intensity * (0.5 + 0.5 * sin(UV.y * scanline_count * 3.14159265));
	col *= sl;

	// Disc alpha: soft feathered rim so the portal blends into black.
	float disc = 1.0 - smoothstep(1.0 - edge_feather, 1.0, r);

	// --- open_progress reveal (the reusable "pop into existence") ----------
	// A growing circular mask: everything beyond the current open radius is
	// transparent, so at open_progress = 0 the portal is a point (invisible)
	// and at 1 it fills the disc. A bright leading edge flashes at the growing
	// front while opening, then fades as it settles.
	float open_r = clamp(open_progress, 0.0, 1.0) * 1.1;
	float mask = smoothstep(open_r, open_r - 0.06, r);       // 1 inside, 0 outside
	float front = smoothstep(0.12, 0.0, abs(r - open_r));    // bright expanding rim
	col += color_core * front * (1.0 - clamp(open_progress, 0.0, 1.0)) * 3.0;

	float alpha = disc * mask;
	COLOR = vec4(col, alpha) * COLOR;   // respect node modulate/self-modulate
}

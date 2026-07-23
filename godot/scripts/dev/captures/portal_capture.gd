extends Control
## Dev-only UNATTENDED capture scene for time_portal.gdshader (#801 cold-open portal).
##
## Unlike portal_shader_demo.gd (interactive live-tuning harness that needs button
## presses), this scene AUTO-PLAYS the portal reveal on load with NO input required,
## so it can be recorded head-less-of-a-human by Godot Movie Maker mode. See
## tools/capture_cinematic.py + tools/README_capture.md for the capture pipeline.
##
## The reveal is the reusable "Tween a shader uniform" technique: open_progress is
## tweened 0 -> 1 ("pop into existence"), the vortex then spins procedurally off TIME.
## With loop = true the reveal replays so an arbitrarily long capture never goes static.
##
## PURE DEV TOOL. No game state, no RNG, not shipped in any flow. Safe to delete.
## Capture output MUST live OUTSIDE godot/ (repo-root captures/) so it is never packed
## into the shipped .pck -- the runner writes there; this scene only renders.

const SHADER_PATH: String = "res://assets/shaders/time_portal.gdshader"

# ---- Capture dials (override in the .tscn or leave as-is) -------------------
## Seconds of the 0->1 reveal before the vortex settles into a steady spin.
@export var open_seconds: float = 1.6
## Replay the reveal on a loop so long captures keep moving (else it settles + spins).
@export var loop: bool = true
## Pause between loop replays (seconds). Only used when loop = true.
@export var loop_gap_seconds: float = 1.2
## Standalone-run backstop: self-quit after this many seconds so a bare
## `godot --path godot res://.../portal_capture.tscn` (no Movie Maker) still exits.
## 0 = never self-quit. When captured via the runner, --quit-after <frames> is the
## authoritative bound; keep this >= the capture duration so it does not cut early.
@export var self_quit_seconds: float = 0.0
## Optional palette preset: "" (shader default doom-red), "green", or "amber".
@export var palette: String = ""

const PALETTES: Dictionary = {
	"green": {
		"color_core": Color(0.75, 1.00, 0.80),
		"color_mid": Color(0.36, 0.93, 0.47),
		"color_edge": Color(0.03, 0.20, 0.08),
	},
	"amber": {
		"color_core": Color(1.00, 0.92, 0.62),
		"color_mid": Color(1.00, 0.72, 0.20),
		"color_edge": Color(0.28, 0.14, 0.00),
	},
}

var _mat: ShaderMaterial
var _portal: TextureRect
var _open_tween: Tween


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)

	# Near-black backdrop so the portal glow reads (matches the cold-open's black beat).
	var bg := ColorRect.new()
	bg.color = Color(0.0, 0.0, 0.0)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

	_mat = ShaderMaterial.new()
	_mat.shader = load(SHADER_PATH)
	_apply_palette()

	# A TextureRect only draws when it HAS a texture (else the fragment never runs);
	# the shader ignores TEXTURE and writes its own COLOR, so a white 8x8 stretched to
	# fill is an identity backdrop (same trick as portal_shader_demo.gd).
	_portal = TextureRect.new()
	var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	img.fill(Color.WHITE)
	_portal.texture = ImageTexture.create_from_image(img)
	_portal.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_portal.stretch_mode = TextureRect.STRETCH_SCALE
	_portal.material = _mat
	# Fill the viewport; keep the disc round by feeding the live aspect to the shader.
	_portal.set_anchors_preset(Control.PRESET_FULL_RECT)
	_portal.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_portal.resized.connect(_update_aspect)
	add_child(_portal)

	call_deferred("_update_aspect")
	_play_open()

	if self_quit_seconds > 0.0:
		# Sim-time timer: under Movie Maker this counts fixed-fps frames, so
		# self_quit_seconds seconds of footage, not wall-clock.
		var t := get_tree().create_timer(self_quit_seconds)
		t.timeout.connect(func() -> void: get_tree().quit())


func _apply_palette() -> void:
	var key := palette.to_lower()
	if PALETTES.has(key):
		var preset: Dictionary = PALETTES[key]
		for uni in preset.keys():
			_mat.set_shader_parameter(uni, preset[uni])


func _play_open() -> void:
	if _open_tween != null and _open_tween.is_valid():
		_open_tween.kill()
	_mat.set_shader_parameter("open_progress", 0.0)
	# THE REUSABLE PATTERN: Tween a shader uniform (see README_shader_animation.md).
	_open_tween = create_tween()
	_open_tween.tween_property(_mat, "shader_parameter/open_progress", 1.0, open_seconds) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	if loop:
		_open_tween.tween_interval(loop_gap_seconds)
		_open_tween.tween_callback(_play_open)


func _update_aspect() -> void:
	if _portal == null or _mat == null:
		return
	var sz: Vector2 = _portal.size
	var a: float = 1.0
	if sz.y > 0.0:
		a = sz.x / sz.y
	_mat.set_shader_parameter("aspect", a)

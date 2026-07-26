class_name AnchoredOverlay
extends AnimatedSprite2D
## Anchor Sockets V2 consumer (#894 #900 #913): plays an overlay SpriteFrames
## ATTACHED TO A NAMED ANCHOR of a host AnimatedSprite2D (a cat's eyes, its
## butt), instead of the sprite centre.
##
## Anchor data SSOT: res://data/office/anchor_sockets.json -- per sprite set,
## per clip (= host animation name), named sockets {name, px, layer} where px
## is the offset from the clip's feet anchor in SOURCE px (schema block in the
## JSON is authoritative; docs/art/PROP_MANIFEST.md "Anchor sockets" section).
##
## Behaviour:
##   * parented to the host; position re-resolves whenever the host's clip
##     (direction) changes -- a socket missing for the current clip hides the
##     overlay (e.g. 'butt' exists only on rear-facing + butt-flash clips).
##   * dials mirror the layering lab: blend ("normal"|"add"), opacity,
##     z-offset, overlay scale.
##   * footfall pulse (Pip ruling 2026-07-26): when the host's frame index
##     enters the clip's footfall_frames set, the overlay pulses (opacity +
##     scale bump, linear decay). Purely frame-index driven -- DETERMINISTIC,
##     no RNG anywhere in this class.
##
## V2 = per-direction STATIC offsets. V3 (future) adds per-frame tracks in the
## same JSON; this consumer would prefer them when present.

const SOCKETS_PATH := "res://data/office/anchor_sockets.json"

static var _data: Dictionary = {}
static var _load_attempted := false

var host: AnimatedSprite2D = null
var sprite_set: String = ""
var anchor_name: String = ""
var base_opacity: float = 1.0
var overlay_scale: float = 1.0
var z_offset: int = 1
var pulse_enabled: bool = true
var pulse_strength: float = 0.5      # opacity/scale bump at pulse peak
var pulse_decay: float = 3.0         # pulse units decayed per second

var enabled: bool = true             # master switch (demo toggle); overrides visibility

var _pulse: float = 0.0              # 1.0 at paw-strike, decays to 0
var _tint := Color(1, 1, 1, 1)

# --- static anchor-data access ----------------------------------------------

static func data() -> Dictionary:
	if not _load_attempted:
		_load_attempted = true
		_data = {}
		if FileAccess.file_exists(SOCKETS_PATH):
			var f := FileAccess.open(SOCKETS_PATH, FileAccess.READ)
			if f != null:
				var parsed = JSON.parse_string(f.get_as_text())
				f.close()
				if parsed is Dictionary:
					_data = parsed
	return _data


static func sprite_sets() -> Array:
	return data().get("sprites", {}).keys()


static func sprite_entry(p_set: String) -> Dictionary:
	return data().get("sprites", {}).get(p_set, {})


static func clip_entry(p_set: String, clip: String) -> Dictionary:
	return sprite_entry(p_set).get("clips", {}).get(clip, {})


## The {name, px, layer} socket dict, or {} when the clip has no such anchor.
static func socket_of(p_set: String, clip: String, p_anchor: String) -> Dictionary:
	for sk in clip_entry(p_set, clip).get("sockets", []):
		if sk is Dictionary and String(sk.get("name", "")) == p_anchor:
			return sk
	return {}


static func canvas_of(p_set: String) -> Vector2:
	var c: Array = sprite_entry(p_set).get("canvas_px", [])
	return Vector2(float(c[0]), float(c[1])) if c.size() == 2 else Vector2.ZERO


static func feet_of(p_set: String, clip: String) -> Vector2:
	var fp: Array = clip_entry(p_set, clip).get("feet_px", [])
	return Vector2(float(fp[0]), float(fp[1])) if fp.size() == 2 else Vector2.ZERO


static func footfalls_of(p_set: String, clip: String) -> Array:
	return clip_entry(p_set, clip).get("footfall_frames", [])

# --- instance ----------------------------------------------------------------

## Attach to `p_host` (reparents this node under it), playing `frames` at the
## named anchor. config dials: opacity, blend ("add"|"normal"), scale,
## z_offset, pulse (bool), pulse_strength, pulse_decay, tint (Color).
func attach(p_host: AnimatedSprite2D, p_set: String, p_anchor: String,
		frames: SpriteFrames, config: Dictionary = {}) -> void:
	host = p_host
	sprite_set = p_set
	anchor_name = p_anchor
	base_opacity = float(config.get("opacity", base_opacity))
	overlay_scale = float(config.get("scale", overlay_scale))
	z_offset = int(config.get("z_offset", z_offset))
	pulse_enabled = bool(config.get("pulse", pulse_enabled))
	pulse_strength = float(config.get("pulse_strength", pulse_strength))
	pulse_decay = float(config.get("pulse_decay", pulse_decay))
	_tint = config.get("tint", _tint)
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	centered = true
	set_overlay_frames(frames)
	if String(config.get("blend", "add")) == "add":
		var mat := CanvasItemMaterial.new()
		mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		material = mat
	else:
		material = null
	if get_parent() != host:
		if get_parent() != null:
			get_parent().remove_child(self)
		host.add_child(self)
	if not host.animation_changed.is_connected(_refresh):
		host.animation_changed.connect(_refresh)
	if not host.frame_changed.is_connected(_on_host_frame):
		host.frame_changed.connect(_on_host_frame)
	_refresh()


## Swap the overlay art (e.g. doom-flavour hue change) without re-anchoring.
func set_overlay_frames(frames: SpriteFrames) -> void:
	sprite_frames = frames
	if frames != null and frames.get_animation_names().size() > 0:
		play(frames.get_animation_names()[0])


func set_base_opacity(v: float) -> void:
	base_opacity = clampf(v, 0.0, 1.0)
	_apply_visual()


func set_tint(c: Color) -> void:
	_tint = c
	_apply_visual()


func set_enabled(v: bool) -> void:
	enabled = v
	_refresh()


## Re-resolve the anchor for the host's CURRENT clip. Hidden when the clip has
## no such socket (butt only exists on rear-facing + butt-flash clips).
func _refresh() -> void:
	if not enabled or host == null or sprite_set == "":
		visible = false
		return
	var clip := String(host.animation)
	var sk := socket_of(sprite_set, clip, anchor_name)
	if sk.is_empty():
		visible = false
		return
	visible = true
	var off: Array = sk.get("px", [0, 0])
	var canvas_pos := feet_of(sprite_set, clip) + Vector2(float(off[0]), float(off[1]))
	# Child of the host: host texture px -> host-local coords (host scale then
	# applies to us automatically). Mirrors the feet-anchor math of #906/#915.
	var local := canvas_pos + host.offset
	if host.centered:
		local -= canvas_of(sprite_set) * 0.5
	position = local
	z_as_relative = true
	z_index = -1 if String(sk.get("layer", "front")) == "behind" else z_offset
	_apply_visual()


## Footfall pulse: purely host-frame-index driven (deterministic, no RNG).
func _on_host_frame() -> void:
	if not pulse_enabled or host == null:
		return
	# int() both sides: JSON numbers parse as floats, host.frame is an int.
	for ff in footfalls_of(sprite_set, String(host.animation)):
		if int(ff) == host.frame:
			_pulse = 1.0
			_apply_visual()
			return


func _process(delta: float) -> void:
	if _pulse > 0.0:
		_pulse = maxf(0.0, _pulse - pulse_decay * delta)
		_apply_visual()


func _apply_visual() -> void:
	var boost := pulse_strength * _pulse
	modulate = Color(_tint.r, _tint.g, _tint.b,
		clampf(_tint.a * base_opacity * (1.0 + boost), 0.0, 1.0))
	var s := overlay_scale * (1.0 + 0.25 * boost)
	scale = Vector2(s, s)

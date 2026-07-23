extends Control
## Dev-only LIVE tuning harness for time_portal.gdshader (#801 cold-open portal).
##
## Left: a square preview rect running the portal ShaderMaterial.
## Right: a slider for EVERY float uniform + colour pickers + preset buttons, all
## wired live so Pip can dial the portal in-editor (run this scene: F6 with it
## open, or set as main scene temporarily). The "Play open (0 -> 1)" button Tweens
## `open_progress` to preview the "pop into existence" reveal -- this is the
## reusable technique: animate a shader uniform with a Tween.
##
## PURE DEV TOOL. No game state, no RNG, not shipped in any flow. Safe to delete.

const SHADER_PATH: String = "res://assets/shaders/time_portal.gdshader"

# Every float dial: [uniform_name, min, max, default, step]. Order = UI order.
const FLOAT_DIALS: Array = [
	["swirl_speed", 0.0, 3.0, 0.6, 0.01],
	["swirl_direction", -1.0, 1.0, 1.0, 2.0],   # toggle-ish: -1 or +1
	["distortion", 0.0, 2.0, 0.55, 0.01],
	["ring_count", 0.0, 40.0, 14.0, 1.0],
	["ring_thickness", 0.0, 1.0, 0.5, 0.01],
	["ring_strength", 0.0, 2.0, 0.6, 0.01],
	["glow_size", 0.0, 1.0, 0.35, 0.01],
	["glow_strength", 0.0, 4.0, 1.6, 0.01],
	["scanline_intensity", 0.0, 1.0, 0.12, 0.01],
	["scanline_count", 20.0, 600.0, 240.0, 1.0],
	["edge_feather", 0.0, 0.5, 0.08, 0.01],
	["open_progress", 0.0, 1.0, 1.0, 0.01],
]

# Colour dials: [uniform_name, default Color].
const COLOR_DIALS: Array = [
	["color_core", Color(1.00, 0.85, 0.55)],
	["color_mid", Color(0.95, 0.12, 0.10)],
	["color_edge", Color(0.35, 0.02, 0.05)],
]

# Colour presets (matches the header block in the shader + TerminalTheme families).
const PRESETS: Dictionary = {
	"Doom red": {
		"color_core": Color(1.00, 0.85, 0.55),
		"color_mid": Color(0.95, 0.12, 0.10),
		"color_edge": Color(0.35, 0.02, 0.05),
	},
	"Phosphor green": {
		"color_core": Color(0.75, 1.00, 0.80),
		"color_mid": Color(0.36, 0.93, 0.47),
		"color_edge": Color(0.03, 0.20, 0.08),
	},
	"Amber": {
		"color_core": Color(1.00, 0.92, 0.62),
		"color_mid": Color(1.00, 0.72, 0.20),
		"color_edge": Color(0.28, 0.14, 0.00),
	},
}

var _mat: ShaderMaterial
var _preview: TextureRect
var _sliders: Dictionary = {}         # uniform_name -> HSlider
var _value_labels: Dictionary = {}    # uniform_name -> Label
var _color_buttons: Dictionary = {}   # uniform_name -> ColorPickerButton
var _open_progress_slider: HSlider
var _loop: bool = false
var _open_tween: Tween


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)

	var bg := ColorRect.new()
	bg.color = Color(0.03, 0.04, 0.05)   # near-black so the portal glow reads
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

	var split := HBoxContainer.new()
	split.set_anchors_preset(Control.PRESET_FULL_RECT)
	split.add_theme_constant_override("separation", 16)
	add_child(split)

	# ---- Left: the live preview -------------------------------------------
	var preview_wrap := CenterContainer.new()
	preview_wrap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	preview_wrap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	split.add_child(preview_wrap)

	_mat = ShaderMaterial.new()
	_mat.shader = load(SHADER_PATH)

	_preview = TextureRect.new()
	_preview.custom_minimum_size = Vector2(520, 520)
	# A TextureRect needs SOME texture to draw (else fragment never runs). The
	# shader ignores TEXTURE and writes its own COLOR; a plain white 8x8 stretched
	# to fill is an identity backdrop.
	var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	img.fill(Color.WHITE)
	_preview.texture = ImageTexture.create_from_image(img)
	_preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_preview.stretch_mode = TextureRect.STRETCH_SCALE
	_preview.material = _mat
	_preview.resized.connect(_update_aspect)
	preview_wrap.add_child(_preview)

	# ---- Right: the dial panel --------------------------------------------
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(360, 0)
	panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	split.add_child(panel)

	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(scroll)

	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 6)
	scroll.add_child(col)

	_add_header(col, "TIME PORTAL -- live dials")

	for dial in FLOAT_DIALS:
		_add_float_row(col, dial)

	_add_header(col, "Colour")
	for cd in COLOR_DIALS:
		_add_color_row(col, cd[0], cd[1])

	_add_header(col, "Presets")
	var preset_row := HBoxContainer.new()
	for preset_name in PRESETS.keys():
		var pb := Button.new()
		pb.text = preset_name
		pb.pressed.connect(_apply_preset.bind(preset_name))
		preset_row.add_child(pb)
	col.add_child(preset_row)

	_add_header(col, "Reveal (open_progress Tween)")
	var play := Button.new()
	play.text = "Play open (0 -> 1)"
	play.pressed.connect(_play_open)
	col.add_child(play)

	var loop_chk := CheckBox.new()
	loop_chk.text = "Loop the open"
	loop_chk.toggled.connect(func(on: bool) -> void: _loop = on; if on: _play_open())
	col.add_child(loop_chk)

	var reset := Button.new()
	reset.text = "Reset all dials"
	reset.pressed.connect(_reset_all)
	col.add_child(reset)

	# Push every default into the material.
	_reset_all()
	call_deferred("_update_aspect")


func _add_header(parent: Control, text: String) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", 16)
	l.add_theme_color_override("font_color", Color(1.0, 0.72, 0.20))  # AMBER
	var sep := HSeparator.new()
	parent.add_child(sep)
	parent.add_child(l)


func _add_float_row(parent: Control, dial: Array) -> void:
	var uni: String = dial[0]
	var lo: float = dial[1]
	var hi: float = dial[2]
	var def: float = dial[3]
	var step: float = dial[4]

	var row := VBoxContainer.new()
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	var head := HBoxContainer.new()
	var name_l := Label.new()
	name_l.text = uni
	name_l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(name_l)
	var val_l := Label.new()
	val_l.text = str(def)
	val_l.add_theme_color_override("font_color", Color(0.36, 0.93, 0.47))  # GREEN
	head.add_child(val_l)
	row.add_child(head)

	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = step
	s.value = def
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.value_changed.connect(func(v: float) -> void:
		_mat.set_shader_parameter(uni, v)
		val_l.text = ("%.2f" % v) if step < 1.0 else str(int(v)))
	row.add_child(s)

	parent.add_child(row)
	_sliders[uni] = s
	_value_labels[uni] = val_l
	if uni == "open_progress":
		_open_progress_slider = s


func _add_color_row(parent: Control, uni: String, def: Color) -> void:
	var row := HBoxContainer.new()
	var l := Label.new()
	l.text = uni
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	var cpb := ColorPickerButton.new()
	cpb.custom_minimum_size = Vector2(90, 28)
	cpb.color = def
	cpb.edit_alpha = false
	cpb.color_changed.connect(func(c: Color) -> void: _mat.set_shader_parameter(uni, c))
	row.add_child(cpb)
	parent.add_child(row)
	_color_buttons[uni] = cpb


func _apply_preset(preset_name: String) -> void:
	var preset: Dictionary = PRESETS[preset_name]
	for uni in preset.keys():
		var c: Color = preset[uni]
		_mat.set_shader_parameter(uni, c)
		if _color_buttons.has(uni):
			_color_buttons[uni].color = c


func _reset_all() -> void:
	for dial in FLOAT_DIALS:
		var uni: String = dial[0]
		var def: float = dial[3]
		_mat.set_shader_parameter(uni, def)
		if _sliders.has(uni):
			_sliders[uni].value = def
	for cd in COLOR_DIALS:
		_mat.set_shader_parameter(cd[0], cd[1])
		if _color_buttons.has(cd[0]):
			_color_buttons[cd[0]].color = cd[1]
	_update_aspect()


func _play_open() -> void:
	if _open_tween != null and _open_tween.is_valid():
		_open_tween.kill()
	# THE REUSABLE PATTERN: Tween a shader uniform. We tween a proxy via a method
	# so the preview slider tracks along; a direct
	# _open_tween.tween_property(_mat, "shader_parameter/open_progress", 1.0, t)
	# also works if you don't need the slider to follow.
	_mat.set_shader_parameter("open_progress", 0.0)
	if _open_progress_slider != null:
		_open_progress_slider.set_value_no_signal(0.0)
	_open_tween = create_tween()
	_open_tween.tween_method(_set_open_progress, 0.0, 1.0, 1.6) \
		.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	if _loop:
		_open_tween.tween_interval(0.6)
		_open_tween.tween_callback(_play_open)


func _set_open_progress(v: float) -> void:
	_mat.set_shader_parameter("open_progress", v)
	if _open_progress_slider != null:
		_open_progress_slider.set_value_no_signal(v)
	if _value_labels.has("open_progress"):
		_value_labels["open_progress"].text = "%.2f" % v


func _update_aspect() -> void:
	if _preview == null or _mat == null:
		return
	var sz: Vector2 = _preview.size
	var a: float = 1.0
	if sz.y > 0.0:
		a = sz.x / sz.y
	_mat.set_shader_parameter("aspect", a)

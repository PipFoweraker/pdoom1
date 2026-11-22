class_name TerminalTheme
extends RefCounted
## First-pass terminal / mainframe styling register for the Plan/Watch scaffold
## (BUILD_BRIEF_PLAN_WATCH_UI "Aesthetic": amber/green CRT, boxes + rules, lightly
## modernized -- NOT literal retro). This is a THIN static helper: a palette + a few
## StyleBoxFlat/font builders that the Plan/Watch UI applies over the default greys.
## Deliberately code-driven (no .tres churn) so Pip can react and a follow-up art lane
## can promote it to a real Theme resource + scanline shader.
##
## SKINS (spike/ui-skins, 2026-11-22): the palette below used to be `const`. It is now
## `static var`, so a UI skin (godot/data/ui_skins.json, applied by ThemeManager) can
## swap it at runtime. Every call site (`TerminalTheme.AMBER`, `style_panel(...)`) is
## unchanged. A swap reaches whatever is BUILT after it -- panels style themselves once,
## in _ready -- so ThemeManager applies the skin at boot and the switcher reloads the
## scene. Values below are the "default" skin; reset() restores them exactly.

# --- Palette (the "default" skin) ------------------------------------------
# Near-black, faintly green-tinted phosphor background.
static var BG_DARK := Color(0.035, 0.05, 0.043)
static var PANEL_BG := Color(0.07, 0.093, 0.082)
static var PANEL_BG_DEEP := Color(0.05, 0.066, 0.058)

# Feed background: the main-UI off-black register (#170A1C, matching the turn-counter
# box and the backdrop scrim) at high alpha so the live feed stays legible over the
# office backdrop (#762). Deliberately the purple-black register, not the green panels.
static var FEED_BG := Color(0.09, 0.04, 0.11, 0.88)

# Amber = PLAN register (strategy, calm). Green = WATCH register (tactics, live).
static var AMBER := Color(1.0, 0.72, 0.20)
static var AMBER_DIM := Color(0.66, 0.48, 0.16)
static var GREEN := Color(0.36, 0.93, 0.47)
static var GREEN_DIM := Color(0.21, 0.56, 0.30)

static var TEXT := Color(0.82, 0.86, 0.78)
static var TEXT_DIM := Color(0.50, 0.58, 0.50)
static var RULE := Color(0.20, 0.36, 0.26)          # box borders / hairlines
static var RULE_BRIGHT := Color(0.30, 0.52, 0.36)

# --- Shape + type (skinnable) -----------------------------------------------
static var FONT_NAMES := PackedStringArray(["Consolas", "DejaVu Sans Mono", "Courier New", "monospace"])
static var CORNER_RADIUS := 0        # terminals have square corners
static var BORDER_WIDTH := 1
## Optional vertical background gradient, top -> bottom. Empty = flat BG_DARK.
static var BG_GRADIENT: Array = []

## The id of the skin currently loaded into the vars above ("default" = untouched).
static var current_skin := "default"

# json token name -> static var name. One table, so the data file and the code cannot
# disagree about what a token is called.
const TOKENS := {
	"bg_dark": "BG_DARK", "panel_bg": "PANEL_BG", "panel_bg_deep": "PANEL_BG_DEEP",
	"feed_bg": "FEED_BG", "amber": "AMBER", "amber_dim": "AMBER_DIM", "green": "GREEN",
	"green_dim": "GREEN_DIM", "text": "TEXT", "text_dim": "TEXT_DIM", "rule": "RULE",
	"rule_bright": "RULE_BRIGHT",
}

static var _defaults: Dictionary = {}


static func _capture_defaults() -> void:
	if not _defaults.is_empty():
		return
	for var_name in TOKENS.values():
		_defaults[var_name] = _get_var(var_name)
	_defaults["FONT_NAMES"] = FONT_NAMES
	_defaults["CORNER_RADIUS"] = CORNER_RADIUS
	_defaults["BORDER_WIDTH"] = BORDER_WIDTH
	_defaults["BG_GRADIENT"] = BG_GRADIENT


static func _set_var(var_name: String, value) -> void:
	# Static vars are not reachable through Object.set() on the class, so dispatch by name.
	match var_name:
		"BG_DARK": BG_DARK = value
		"PANEL_BG": PANEL_BG = value
		"PANEL_BG_DEEP": PANEL_BG_DEEP = value
		"FEED_BG": FEED_BG = value
		"AMBER": AMBER = value
		"AMBER_DIM": AMBER_DIM = value
		"GREEN": GREEN = value
		"GREEN_DIM": GREEN_DIM = value
		"TEXT": TEXT = value
		"TEXT_DIM": TEXT_DIM = value
		"RULE": RULE = value
		"RULE_BRIGHT": RULE_BRIGHT = value
		"FONT_NAMES": FONT_NAMES = value
		"CORNER_RADIUS": CORNER_RADIUS = value
		"BORDER_WIDTH": BORDER_WIDTH = value
		"BG_GRADIENT": BG_GRADIENT = value


static func _get_var(var_name: String):
	match var_name:
		"BG_DARK": return BG_DARK
		"PANEL_BG": return PANEL_BG
		"PANEL_BG_DEEP": return PANEL_BG_DEEP
		"FEED_BG": return FEED_BG
		"AMBER": return AMBER
		"AMBER_DIM": return AMBER_DIM
		"GREEN": return GREEN
		"GREEN_DIM": return GREEN_DIM
		"TEXT": return TEXT
		"TEXT_DIM": return TEXT_DIM
		"RULE": return RULE
		"RULE_BRIGHT": return RULE_BRIGHT
	return null


static func reset() -> void:
	"""Restore the default skin exactly (the values declared above)."""
	if _defaults.is_empty():
		current_skin = "default"
		return
	for var_name in _defaults:
		_set_var(var_name, _defaults[var_name])
	current_skin = "default"


static func apply_skin(skin_id: String, skin: Dictionary) -> void:
	"""Load a skin dict (one entry of ui_skins.json) into the palette. Tokens it omits keep
	their DEFAULT value (reset first), so a partial skin never inherits a previous one."""
	_capture_defaults()
	reset()
	var palette: Dictionary = skin.get("palette", {})
	for token in palette:
		if TOKENS.has(token):
			_set_var(TOKENS[token], _parse_color(palette[token]))
	if skin.has("font_names"):
		FONT_NAMES = PackedStringArray(skin["font_names"])
	if skin.has("corner_radius"):
		CORNER_RADIUS = int(skin["corner_radius"])
	if skin.has("border_width"):
		BORDER_WIDTH = int(skin["border_width"])
	var grad: Array = []
	for c in skin.get("bg_gradient", []):
		grad.append(_parse_color(c))
	BG_GRADIENT = grad
	current_skin = skin_id


static func _parse_color(v) -> Color:
	# A token is "#rrggbb" / "#rrggbbaa", or {"hex": ..., "hand": "<why>"} when it was
	# hand-set rather than sampled (tools/ui_skins/sample_palette.py).
	if v is Dictionary:
		v = v.get("hex", "#ff00ff")
	return Color.html(str(v))


static func box(border: Color, bg = null, border_width = null) -> StyleBoxFlat:
	"""A boxed panel in the terminal register -- flat fill + a single hairline rule."""
	var sb := StyleBoxFlat.new()
	sb.bg_color = PANEL_BG if bg == null else bg
	sb.border_color = border
	sb.set_border_width_all(BORDER_WIDTH if border_width == null else int(border_width))
	sb.set_corner_radius_all(CORNER_RADIUS)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 4
	sb.content_margin_bottom = 4
	return sb


static func mono_font() -> SystemFont:
	"""The skin's text face (default: best-available system monospace), without shipping
	a font asset. Degrades gracefully to the platform default if none match."""
	var f := SystemFont.new()
	f.font_names = FONT_NAMES
	return f


static func style_panel(node: Control, border = null, bg = null) -> void:
	"""Apply the boxed-panel look to any PanelContainer-like Control (adds a 'panel' stylebox)."""
	if node == null:
		return
	node.add_theme_stylebox_override("panel", box(RULE if border == null else border, bg))


static func style_feed(label: RichTextLabel) -> void:
	"""The WATCH feed / message log: monospace, dim green-tinted text on an off-black
	panel so it reads over the office backdrop (#762)."""
	if label == null:
		return
	label.add_theme_font_override("normal_font", mono_font())
	label.add_theme_color_override("default_color", TEXT)
	# Opaque-ish panel behind the feed text -- RichTextLabel paints its "normal" stylebox
	# as the background. #170A1C @ 0.88 alpha matches the main-UI register (turn-counter box).
	var bg := StyleBoxFlat.new()
	bg.bg_color = FEED_BG
	bg.set_corner_radius_all(CORNER_RADIUS)
	bg.content_margin_left = 8
	bg.content_margin_right = 8
	bg.content_margin_top = 6
	bg.content_margin_bottom = 6
	label.add_theme_stylebox_override("normal", bg)


static func make_background() -> Control:
	"""The full-screen backdrop: flat BG_DARK, or a vertical gradient when the skin has one."""
	if BG_GRADIENT.size() < 2:
		var rect := ColorRect.new()
		rect.color = BG_DARK
		return rect
	var offsets := PackedFloat32Array()
	var colors := PackedColorArray()
	for i in BG_GRADIENT.size():
		offsets.append(float(i) / float(BG_GRADIENT.size() - 1))
		colors.append(BG_GRADIENT[i])
	var g := Gradient.new()
	g.offsets = offsets
	g.colors = colors
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill_from = Vector2(0, 0)
	tex.fill_to = Vector2(0, 1)
	tex.width = 4
	tex.height = 256
	var tr := TextureRect.new()
	tr.texture = tex
	tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	tr.stretch_mode = TextureRect.STRETCH_SCALE
	return tr


static func build_root_theme() -> Theme:
	"""A Theme for the root Window, so the skin also reaches every STOCK control (buttons,
	plain panels, labels, popups) that never calls style_panel. Deliberately sets NO
	font size: the size SSOT stays godot/theme/base_theme.tres (#1224), which this theme
	falls through to. Returns null for the default skin -- default stays byte-identical."""
	if current_skin == "default":
		return null
	var t := Theme.new()
	t.default_font = mono_font()
	var panel := box(RULE, PANEL_BG)
	for type_name in ["Panel", "PanelContainer", "PopupPanel", "TooltipPanel"]:
		t.set_stylebox("panel", type_name, panel)
	t.set_stylebox("panel", "PopupMenu", box(RULE_BRIGHT, PANEL_BG_DEEP))
	var normal := box(RULE, PANEL_BG_DEEP)
	var hover := box(AMBER, PANEL_BG_DEEP)
	var pressed := box(AMBER, AMBER_DIM)
	var disabled := box(RULE, BG_DARK)
	for type_name in ["Button", "OptionButton", "MenuButton", "CheckBox", "CheckButton"]:
		t.set_stylebox("normal", type_name, normal)
		t.set_stylebox("hover", type_name, hover)
		t.set_stylebox("pressed", type_name, pressed)
		t.set_stylebox("hover_pressed", type_name, pressed)
		t.set_stylebox("disabled", type_name, disabled)
		t.set_stylebox("focus", type_name, box(AMBER, Color(0, 0, 0, 0)))
		t.set_color("font_color", type_name, TEXT)
		t.set_color("font_hover_color", type_name, AMBER)
		t.set_color("font_pressed_color", type_name, TEXT)
		t.set_color("font_hover_pressed_color", type_name, TEXT)
		t.set_color("font_focus_color", type_name, TEXT)
		t.set_color("font_disabled_color", type_name, TEXT_DIM)
	t.set_color("font_color", "Label", TEXT)
	t.set_color("default_color", "RichTextLabel", TEXT)
	t.set_color("font_color", "PopupMenu", TEXT)
	t.set_color("font_hover_color", "PopupMenu", AMBER)
	t.set_color("font_color", "LineEdit", TEXT)
	t.set_stylebox("normal", "LineEdit", box(RULE, PANEL_BG_DEEP))
	t.set_stylebox("background", "ProgressBar", box(RULE, PANEL_BG_DEEP))
	var fill := StyleBoxFlat.new()
	fill.bg_color = AMBER
	t.set_stylebox("fill", "ProgressBar", fill)
	return t

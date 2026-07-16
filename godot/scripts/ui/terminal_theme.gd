class_name TerminalTheme
extends RefCounted
## First-pass terminal / mainframe styling register for the Plan/Watch scaffold
## (BUILD_BRIEF_PLAN_WATCH_UI "Aesthetic": amber/green CRT, boxes + rules, lightly
## modernized — NOT literal retro). This is a THIN static helper: a palette + a few
## StyleBoxFlat/font builders that the Plan/Watch UI applies over the default greys.
## Deliberately code-driven (no .tres churn) so Pip can react and a follow-up art lane
## can promote it to a real Theme resource + scanline shader.

# --- Palette ---------------------------------------------------------------
# Near-black, faintly green-tinted phosphor background.
const BG_DARK := Color(0.035, 0.05, 0.043)
const PANEL_BG := Color(0.07, 0.093, 0.082)
const PANEL_BG_DEEP := Color(0.05, 0.066, 0.058)

# Amber = PLAN register (strategy, calm). Green = WATCH register (tactics, live).
const AMBER := Color(1.0, 0.72, 0.20)
const AMBER_DIM := Color(0.66, 0.48, 0.16)
const GREEN := Color(0.36, 0.93, 0.47)
const GREEN_DIM := Color(0.21, 0.56, 0.30)

const TEXT := Color(0.82, 0.86, 0.78)
const TEXT_DIM := Color(0.50, 0.58, 0.50)
const RULE := Color(0.20, 0.36, 0.26)          # box borders / hairlines
const RULE_BRIGHT := Color(0.30, 0.52, 0.36)


static func box(border: Color, bg: Color = PANEL_BG, border_width: int = 1) -> StyleBoxFlat:
	"""A boxed panel in the terminal register — flat fill + a single hairline rule."""
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_width)
	sb.set_corner_radius_all(0)  # terminals have square corners
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 4
	sb.content_margin_bottom = 4
	return sb


static func mono_font() -> SystemFont:
	"""Best-available system monospace — the 'monospace-ish' the brief asks for, without
	shipping a font asset. Degrades gracefully to the platform default if none match."""
	var f := SystemFont.new()
	f.font_names = PackedStringArray(["Consolas", "DejaVu Sans Mono", "Courier New", "monospace"])
	return f


static func style_panel(node: Control, border: Color = RULE, bg: Color = PANEL_BG) -> void:
	"""Apply the boxed-panel look to any PanelContainer-like Control (adds a 'panel' stylebox)."""
	if node == null:
		return
	node.add_theme_stylebox_override("panel", box(border, bg))


static func style_feed(label: RichTextLabel) -> void:
	"""The WATCH feed / message log: monospace, dim green-tinted text."""
	if label == null:
		return
	label.add_theme_font_override("normal_font", mono_font())
	label.add_theme_color_override("default_color", TEXT)

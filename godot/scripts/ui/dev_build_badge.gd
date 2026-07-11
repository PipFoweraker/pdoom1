extends CanvasLayer
class_name DevBuildBadge
## Always-visible "DEV BUILD" corner badge (playtester couldn't tell which build he ran).
##
## A high-contrast amber-on-dark badge pinned to the top-right corner, drawn on its own
## CanvasLayer so it floats over everything on both the main game screen and the
## welcome/loading screen. Shows GameConfig.CURRENT_VERSION plus the per-commit build
## stamp from BuildInfo (git short hash + date) so a tester can confirm the exact build.
##
## Gated on BuildInfo.is_dev_build(): if that constant is flipped false for a release
## cut, the badge instances but hides itself. On-screen look still needs a human eye.
##
## Usage: `add_child(DevBuildBadge.new())` from any screen's _ready().

## High layer so the badge sits above normal UI and other CanvasLayers (e.g. overlays).
const BADGE_LAYER := 200

func _ready() -> void:
	layer = BADGE_LAYER
	if not BuildInfo.is_dev_build():
		visible = false
		return
	_build_badge()

func _build_badge() -> void:
	# Anchor a container to the top-right corner of the viewport.
	var anchor := Control.new()
	anchor.name = "DevBadgeAnchor"
	anchor.anchor_left = 1.0
	anchor.anchor_right = 1.0
	anchor.anchor_top = 0.0
	anchor.anchor_bottom = 0.0
	anchor.offset_left = -360.0
	anchor.offset_top = 8.0
	anchor.offset_right = -8.0
	anchor.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(anchor)

	# The badge panel — dark translucent base with a bright glowing amber border for
	# an unmissable "not a real build" read.
	var panel := PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.size_flags_horizontal = Control.SIZE_SHRINK_END

	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.12, 0.10, 0.02, 0.88)
	style.border_color = Color(1.0, 0.72, 0.0, 1.0)  # bright amber "glow" edge
	style.set_border_width_all(3)
	style.set_corner_radius_all(6)
	style.content_margin_left = 12
	style.content_margin_right = 12
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	# Soft outer shadow to fake a glow around the badge.
	style.shadow_color = Color(1.0, 0.72, 0.0, 0.35)
	style.shadow_size = 6
	panel.add_theme_stylebox_override("panel", style)
	anchor.add_child(panel)

	var label := Label.new()
	label.name = "DevBadgeLabel"
	label.text = BuildInfo.get_badge_text()
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_font_size_override("font_size", 15)
	label.add_theme_color_override("font_color", Color(1.0, 0.82, 0.25))
	# Dark outline so the amber text stays legible over any background (menu art, etc.).
	label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	label.add_theme_constant_override("outline_size", 4)
	panel.add_child(label)

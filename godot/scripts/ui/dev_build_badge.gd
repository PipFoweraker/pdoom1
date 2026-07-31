extends CanvasLayer
class_name DevBuildBadge
## Corner build-identity badge, pinned top-right on every screen.
##
## Two faces, decided by BuildInfo.is_dev_build():
##   - Dev/debug runs (editor, debug-template exports): the loud amber "DEV BUILD"
##     badge with the full git stamp, so a playtester can confirm exactly which
##     build he is running.
##   - Exported release builds: a quiet version-only label ("v0.13.2"). The public
##     v0.13.2 release shipped the amber banner to players, who read it as "I have
##     the wrong file" (issue #1067) -- releases keep the support value (which build
##     is this?) without the scare.
##
## Layout: the panel's RIGHT edge is pinned to the viewport's right edge and its
## width is computed from the content, growing leftward -- so it can never run off
## the right edge. (The old code positioned the panel's LEFT edge at a fixed
## -360 px offset and let the panel take its natural width to the right; any stamp
## text wider than ~352 px overflowed the screen and clipped mid-word, which is
## exactly what the shipped v0.13.2 did.) If the window is narrower than the text,
## the label ellipsizes instead of overflowing the left edge.
##
## Usage: `add_child(DevBuildBadge.new())` from any screen's _ready().

## High layer so the badge sits above normal UI and other CanvasLayers (e.g. overlays).
const BADGE_LAYER := 200

## Gap kept between the badge and the screen edges.
const EDGE_MARGIN := 8.0

var _panel: PanelContainer
var _label: Label

func _ready() -> void:
	layer = BADGE_LAYER
	_build_badge(BuildInfo.is_dev_build())
	get_viewport().size_changed.connect(_fit_to_viewport)
	_fit_to_viewport()

func _build_badge(dev: bool) -> void:
	_panel = PanelContainer.new()
	_panel.name = "BuildBadgePanel"
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Pin the RIGHT edge; _fit_to_viewport() sets offset_left so the panel grows
	# leftward from there and the right edge can never be crossed.
	_panel.anchor_left = 1.0
	_panel.anchor_right = 1.0
	_panel.anchor_top = 0.0
	_panel.anchor_bottom = 0.0
	_panel.offset_right = -EDGE_MARGIN
	_panel.offset_top = EDGE_MARGIN
	_panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN

	var style := StyleBoxFlat.new()
	_label = Label.new()
	_label.name = "BuildBadgeLabel"
	_label.text = BuildInfo.get_badge_text()
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	if dev:
		# Dark translucent base with a bright glowing amber border for an
		# unmissable "not a real build" read.
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
		_label.add_theme_font_size_override("font_size", 15)
		_label.add_theme_color_override("font_color", Color(1.0, 0.82, 0.25))
	else:
		# Release: quiet, small, no border, no glow -- an identity tag, not a warning.
		style.bg_color = Color(0.05, 0.06, 0.09, 0.5)
		style.set_border_width_all(0)
		style.set_corner_radius_all(4)
		style.content_margin_left = 8
		style.content_margin_right = 8
		style.content_margin_top = 3
		style.content_margin_bottom = 3
		_label.add_theme_font_size_override("font_size", 12)
		_label.add_theme_color_override("font_color", Color(0.72, 0.75, 0.80, 0.9))

	# Dark outline so the text stays legible over any background (menu art, etc.).
	_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	_label.add_theme_constant_override("outline_size", 4 if dev else 3)

	_panel.add_theme_stylebox_override("panel", style)
	_panel.add_child(_label)
	add_child(_panel)

## Size the panel to its content, clamped to the viewport width, right edge pinned.
## When the window is narrower than the text, switch the label to ellipsis trimming
## (which releases the label's minimum-width claim) so the badge shrinks to fit
## instead of running off the LEFT edge.
func _fit_to_viewport() -> void:
	if _panel == null or _label == null:
		return
	_label.text_overrun_behavior = TextServer.OVERRUN_NO_TRIMMING
	var need := _panel.get_combined_minimum_size().x
	var max_w := get_viewport().get_visible_rect().size.x - 2.0 * EDGE_MARGIN
	if need > max_w:
		_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		need = max_w
	_panel.offset_left = _panel.offset_right - need

extends Control
class_name DoomTrendGraph
## Doom trend sparkline (#512). Fixed 0-100 Y axis with bushfire zone bands behind the line,
## area fill under the line (semantic doom color -- can go near-black), and an ember-bright
## stroke (get_doom_stroke_color) so the line stays legible even at terminal doom.
## Click to request an expanded full-history view.
##
## Feed it with set_history(state["doom_history"]). Window-limits to the last `window_size`
## points for the always-on widget; set window_size <= 0 to plot the entire history (expand view).

signal expand_requested

@export var window_size: int = 12        # recent turns shown; <= 0 = full history
@export var show_zone_bands: bool = true
@export var band_alpha: float = 0.09     # faint reference only (playtest: avoid loud rainbow)
@export var show_dots: bool = true       # dot at each doom data point (screen6)
@export var fill_alpha: float = 0.28
@export var line_width: float = 2.0
@export var pad: float = 4.0             # inner padding (px)
@export var clickable: bool = true       # always-on widget = true; expanded panel = false

var _history: PackedFloat32Array = PackedFloat32Array()

func _ready() -> void:
	if custom_minimum_size == Vector2.ZERO:
		custom_minimum_size = Vector2(120, 44)
	mouse_filter = Control.MOUSE_FILTER_STOP if clickable else Control.MOUSE_FILTER_IGNORE
	if clickable:
		tooltip_text = "Doom trend -- click to expand"

func set_history(values) -> void:
	"""Accepts any float array (e.g. state['doom_history'])."""
	_history = PackedFloat32Array(values)
	queue_redraw()

func _gui_input(event: InputEvent) -> void:
	if not clickable:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		expand_requested.emit()

func _draw() -> void:
	var w: float = size.x
	var h: float = size.y
	if w <= 0.0 or h <= 0.0:
		return

	# Zone bands: faint reference only (kept subtle so the LINE's color carries the story).
	if show_zone_bands:
		var steps: int = 24
		for i in range(steps):
			var y0: float = (float(i) / steps) * h
			var y1: float = (float(i + 1) / steps) * h
			var doom_here: float = (1.0 - float(i) / steps) * 100.0
			var c: Color = ThemeManager.get_doom_color(doom_here)
			c.a = band_alpha
			draw_rect(Rect2(0.0, y0, w, y1 - y0), c)

	if _history.size() < 2:
		return

	var n: int = _history.size()
	var start: int = 0
	if window_size > 0:
		start = maxi(0, n - window_size)
	var count: int = n - start
	var span_x: float = w - pad * 2.0
	var span_y: float = h - pad * 2.0
	var step: float = span_x / float(maxi(1, count - 1))

	var pts: PackedVector2Array = PackedVector2Array()
	var vals: PackedFloat32Array = PackedFloat32Array()
	for i in range(count):
		var v: float = clampf(_history[start + i], 0.0, 100.0)
		var x: float = pad + step * float(i)
		var y: float = pad + (1.0 - v / 100.0) * span_y
		pts.append(Vector2(x, y))
		vals.append(v)

	# Area fill under the line -- semantic color of the latest doom.
	var fill_col: Color = ThemeManager.get_doom_color(vals[count - 1])
	fill_col.a = fill_alpha
	var poly: PackedVector2Array = PackedVector2Array(pts)
	poly.append(Vector2(pts[count - 1].x, h - pad))
	poly.append(Vector2(pts[0].x, h - pad))
	draw_colored_polygon(poly, fill_col)

	# Trend line -- colored PER SEGMENT by the doom value at that point, so the line itself
	# tells the bushfire story over time (playtest feedback). Stroke variant stays legible.
	for i in range(count - 1):
		var seg_col: Color = ThemeManager.get_doom_stroke_color(vals[i + 1])
		draw_line(pts[i], pts[i + 1], seg_col, line_width, true)

	# Dot at each data point, colored by its own doom value.
	if show_dots:
		for i in range(count):
			draw_circle(pts[i], line_width + 1.0, ThemeManager.get_doom_stroke_color(vals[i]))

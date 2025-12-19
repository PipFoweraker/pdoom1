extends Control
class_name TechDebtIndicator
## Technical Debt Visualization Component (Issue #416)
## A compact indicator showing technical debt level with visual feedback

signal debt_clicked()
signal debt_hovered(debt_info: Dictionary)
signal debt_unhovered()

# Visual constants
const BAR_WIDTH: float = 120.0
const BAR_HEIGHT: float = 16.0
const THRESHOLD_LOW: float = 25.0
const THRESHOLD_MODERATE: float = 50.0
const THRESHOLD_HIGH: float = 75.0

# State
var current_debt: float = 0.0
var debt_status: String = "minimal"
var is_hovered: bool = false

# Colors for different debt levels
const DEBT_COLORS = {
	"minimal": Color(0.3, 0.8, 0.3),      # Green
	"low": Color(0.6, 0.8, 0.3),          # Yellow-green
	"moderate": Color(0.9, 0.7, 0.2),     # Orange
	"high": Color(0.9, 0.4, 0.2),         # Red-orange
	"critical": Color(0.9, 0.2, 0.2)      # Red
}

# Warning messages for tooltip
const DEBT_WARNINGS = {
	"minimal": "Technical debt under control. Systems stable.",
	"low": "Some technical debt accumulating. Consider an audit.",
	"moderate": "Technical debt building up. Failure risk increasing.",
	"high": "High technical debt! Increased failure chance. Audit recommended.",
	"critical": "CRITICAL: Extreme technical debt. High failure risk!"
}


func _ready():
	custom_minimum_size = Vector2(BAR_WIDTH + 60, BAR_HEIGHT + 8)
	mouse_filter = Control.MOUSE_FILTER_STOP

	# Connect mouse events
	mouse_entered.connect(_on_mouse_entered)
	mouse_exited.connect(_on_mouse_exited)


func _draw():
	# Background bar
	var bg_rect = Rect2(50, 4, BAR_WIDTH, BAR_HEIGHT)
	draw_rect(bg_rect, Color(0.15, 0.15, 0.15), true)
	draw_rect(bg_rect, Color(0.4, 0.4, 0.4), false, 1.0)

	# Fill bar based on debt level
	var fill_width = (current_debt / 100.0) * BAR_WIDTH
	if fill_width > 0:
		var fill_rect = Rect2(50, 4, fill_width, BAR_HEIGHT)
		var fill_color = DEBT_COLORS.get(debt_status, Color.GRAY)
		draw_rect(fill_rect, fill_color, true)

	# Draw threshold markers
	_draw_threshold_marker(THRESHOLD_LOW, Color(0.5, 0.7, 0.3, 0.6))
	_draw_threshold_marker(THRESHOLD_MODERATE, Color(0.8, 0.6, 0.2, 0.6))
	_draw_threshold_marker(THRESHOLD_HIGH, Color(0.8, 0.3, 0.2, 0.6))

	# Label
	var font = ThemeDB.fallback_font
	var font_size = 11
	var label_color = Color.WHITE if is_hovered else Color(0.8, 0.8, 0.8)
	draw_string(font, Vector2(2, BAR_HEIGHT), "Debt:", HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, label_color)

	# Value text
	var value_text = "%.0f%%" % current_debt
	var value_color = DEBT_COLORS.get(debt_status, Color.WHITE)
	draw_string(font, Vector2(BAR_WIDTH + 54, BAR_HEIGHT), value_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, value_color)

	# Hover highlight
	if is_hovered:
		var highlight_rect = Rect2(0, 0, size.x, size.y)
		draw_rect(highlight_rect, Color(1, 1, 1, 0.1), true)


func _draw_threshold_marker(threshold: float, color: Color):
	"""Draw a vertical line marker at the given threshold"""
	var x_pos = 50 + (threshold / 100.0) * BAR_WIDTH
	draw_line(Vector2(x_pos, 4), Vector2(x_pos, 4 + BAR_HEIGHT), color, 1.0)


func update_debt(debt_value: float, status: String = ""):
	"""Update the displayed debt value"""
	current_debt = clamp(debt_value, 0.0, 100.0)

	# Auto-determine status if not provided
	if status == "":
		if current_debt < 10.0:
			debt_status = "minimal"
		elif current_debt < 25.0:
			debt_status = "low"
		elif current_debt < 50.0:
			debt_status = "moderate"
		elif current_debt < 75.0:
			debt_status = "high"
		else:
			debt_status = "critical"
	else:
		debt_status = status

	queue_redraw()


func get_tooltip_info() -> Dictionary:
	"""Get info for tooltip display"""
	var failure_chance = 0.0
	if current_debt >= 20.0:
		failure_chance = (current_debt - 20.0) * 0.2  # 2% per 10 debt above 20

	return {
		"debt": current_debt,
		"status": debt_status,
		"warning": DEBT_WARNINGS.get(debt_status, ""),
		"failure_chance": failure_chance,
		"color": DEBT_COLORS.get(debt_status, Color.WHITE)
	}


func _on_mouse_entered():
	is_hovered = true
	queue_redraw()
	debt_hovered.emit(get_tooltip_info())


func _on_mouse_exited():
	is_hovered = false
	queue_redraw()
	debt_unhovered.emit()


func _gui_input(event: InputEvent):
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			debt_clicked.emit()

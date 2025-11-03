extends Control
class_name DoomMeter
## Visual doom meter - circular "Doomsday Clock" gauge with color transitions

@export var doom_value: float = 50.0:
	set(value):
		doom_value = clamp(value, 0.0, 100.0)
		queue_redraw()

@export var doom_momentum: float = 0.0:
	set(value):
		doom_momentum = value
		queue_redraw()

@export var gauge_thickness: float = 12.0
@export var show_momentum_indicator: bool = true

# Color thresholds
const COLOR_SAFE = Color(0.3, 0.8, 0.3)        # <30% - green
const COLOR_WARNING = Color(0.9, 0.7, 0.2)     # 30-60% - yellow
const COLOR_DANGER = Color(0.9, 0.3, 0.2)      # 60-80% - orange
const COLOR_CRITICAL = Color(0.7, 0.1, 0.1)    # >80% - red
const COLOR_BACKGROUND = Color(0.110, 0.153, 0.188, 0.3)  # Steel translucent

var pulse_time: float = 0.0
var pulse_speed: float = 2.0

func _ready():
	custom_minimum_size = Vector2(100, 100)
	set_process(doom_value >= 80.0)  # Only animate pulse at critical levels

func _process(delta: float):
	if doom_value >= 80.0:
		pulse_time += delta * pulse_speed
		queue_redraw()

func _draw():
	var center = size / 2
	var radius = min(size.x, size.y) / 2 - gauge_thickness - 5

	# Background circle
	draw_arc(center, radius, 0, TAU, 64, COLOR_BACKGROUND, gauge_thickness, true)

	# Doom arc
	var doom_angle = (doom_value / 100.0) * TAU
	var doom_color = get_doom_color(doom_value)

	# Add pulsing effect at critical levels
	var current_thickness = gauge_thickness
	if doom_value >= 80.0:
		var pulse_factor = 1.0 + sin(pulse_time) * 0.15
		current_thickness *= pulse_factor
		doom_color = doom_color.lerp(Color.WHITE, sin(pulse_time) * 0.2)

	# Draw doom arc (starts at top, clockwise)
	draw_arc(center, radius, -PI/2, -PI/2 + doom_angle, 64, doom_color, current_thickness, true)

	# Doom percentage text
	var doom_text = "%d%%" % doom_value
	var font = get_theme_default_font()
	var font_size = 24
	var text_size = font.get_string_size(doom_text, HORIZONTAL_ALIGNMENT_CENTER, -1, font_size)
	var text_pos = center - text_size / 2
	draw_string(font, text_pos, doom_text, HORIZONTAL_ALIGNMENT_CENTER, -1, font_size, doom_color)

	# Momentum indicator (arrow)
	if show_momentum_indicator and abs(doom_momentum) > 0.1:
		var momentum_pos = center + Vector2(0, 20)
		var arrow_color = Color.RED if doom_momentum > 0 else Color.GREEN
		var arrow_char = "↑" if doom_momentum > 0 else "↓"
		var momentum_text = "%s %.1f" % [arrow_char, abs(doom_momentum)]
		var momentum_size = font.get_string_size(momentum_text, HORIZONTAL_ALIGNMENT_CENTER, -1, 14)
		draw_string(font, momentum_pos - momentum_size / 2, momentum_text, HORIZONTAL_ALIGNMENT_CENTER, -1, 14, arrow_color)

func get_doom_color(doom: float) -> Color:
	"""Get color based on doom tier"""
	if doom < 30.0:
		return COLOR_SAFE
	elif doom < 60.0:
		# Blend green to yellow
		var t = (doom - 30.0) / 30.0
		return COLOR_SAFE.lerp(COLOR_WARNING, t)
	elif doom < 80.0:
		# Blend yellow to orange
		var t = (doom - 60.0) / 20.0
		return COLOR_WARNING.lerp(COLOR_DANGER, t)
	else:
		# Blend orange to red
		var t = (doom - 80.0) / 20.0
		return COLOR_DANGER.lerp(COLOR_CRITICAL, t)

func set_doom(value: float, momentum: float = 0.0):
	"""Update doom value and momentum"""
	doom_value = value
	doom_momentum = momentum

	# Enable/disable pulse animation
	set_process(doom_value >= 80.0)
	if doom_value < 80.0:
		pulse_time = 0.0

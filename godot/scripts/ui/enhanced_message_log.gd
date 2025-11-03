extends RichTextLabel
## Enhanced Message Log - Styled, scrollable game messages with icons and timestamps

@export var max_messages: int = 100
@export var show_timestamps: bool = false
@export var auto_scroll: bool = true
@export var fade_old_messages: bool = true

var message_count: int = 0

func _ready():
	# Apply theme styling
	add_theme_color_override("default_color", ThemeManager.get_color("text"))
	add_theme_font_size_override("normal_font_size", ThemeManager.get_font_size("body"))

	# Enable BBCode
	bbcode_enabled = true

	# Connect to theme changes
	ThemeManager.theme_changed.connect(_on_theme_changed)

func _on_theme_changed(theme_name: String):
	add_theme_color_override("default_color", ThemeManager.get_color("text"))
	add_theme_font_size_override("normal_font_size", ThemeManager.get_font_size("body"))

## Add a styled message to the log
func add_message(message: String, message_type: String = "info"):
	message_count += 1

	# Get color based on message type
	var color = _get_message_color(message_type)

	# Format message
	var formatted_msg = ""

	if show_timestamps:
		var time = Time.get_time_dict_from_system()
		formatted_msg += "[color=gray][%02d:%02d:%02d][/color] " % [time.hour, time.minute, time.second]

	# Add icon/prefix based on type
	var prefix = _get_message_prefix(message_type)
	if prefix != "":
		formatted_msg += "[color=%s]%s[/color] " % [color.to_html(), prefix]

	# Add the actual message
	formatted_msg += "[color=%s]%s[/color]" % [color.to_html(), message]

	# Append to log
	append_text(formatted_msg + "\n")

	# Trim old messages
	if message_count > max_messages:
		_trim_old_messages()

	# Auto-scroll to bottom
	if auto_scroll:
		scroll_to_line(get_line_count())

## Get color for message type
func _get_message_color(message_type: String) -> Color:
	match message_type:
		"success", "positive":
			return ThemeManager.get_color("success")
		"warning", "caution":
			return ThemeManager.get_color("warning")
		"error", "danger":
			return ThemeManager.get_color("error")
		"system", "phase":
			return ThemeManager.get_color("accent")
		"doom":
			return ThemeManager.get_color("error")
		"action":
			return Color(0.5, 0.8, 1.0)  # Light blue
		"event":
			return Color(1.0, 0.8, 0.5)  # Gold
		_:
			return ThemeManager.get_color("text")

## Get prefix icon/symbol for message type
func _get_message_prefix(message_type: String) -> String:
	match message_type:
		"success":
			return "✓"
		"error":
			return "✗"
		"warning":
			return "⚠"
		"info":
			return "ℹ"
		"action":
			return "→"
		"event":
			return "★"
		"doom":
			return "☠"
		_:
			return ""

## Trim old messages when exceeding limit
func _trim_old_messages():
	var lines = text.split("\n")
	var keep_count = max_messages - 10  # Keep 90 when limit is 100

	if lines.size() > keep_count:
		var new_lines = lines.slice(lines.size() - keep_count, lines.size())
		clear()
		text = "\n".join(new_lines)
		message_count = keep_count

## Clear all messages
func clear_log():
	clear()
	message_count = 0

## Add a separator line
func add_separator(separator_char: String = "─"):
	var separator = separator_char.repeat(50)
	add_message(separator, "system")

## Add a section header
func add_header(header_text: String):
	add_separator()
	add_message(header_text.to_upper(), "system")
	add_separator()

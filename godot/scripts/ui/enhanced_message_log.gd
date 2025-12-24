extends RichTextLabel
## Enhanced Message Log - Styled, scrollable game messages with icons and timestamps

@export var max_messages: int = 100
@export var show_timestamps: bool = false
@export var auto_scroll: bool = true
@export var fade_old_messages: bool = true
@export var persist_history: bool = true

var message_count: int = 0
var message_history: Array[Dictionary] = []  # Raw messages for persistence
const HISTORY_FILE = "user://action_history.json"

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

	# Store in history for persistence
	if persist_history:
		var entry = {
			"message": message,
			"type": message_type,
			"timestamp": Time.get_unix_time_from_system()
		}
		message_history.append(entry)
		# Trim history if too large
		while message_history.size() > max_messages * 2:
			message_history.pop_front()

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

## Save action history to file
func save_history():
	if not persist_history or message_history.is_empty():
		return

	var file = FileAccess.open(HISTORY_FILE, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(message_history, "\t"))
		file.close()
		print("[MessageLog] Saved %d history entries" % message_history.size())

## Load action history from file
func load_history():
	if not persist_history:
		return

	if not FileAccess.file_exists(HISTORY_FILE):
		return

	var file = FileAccess.open(HISTORY_FILE, FileAccess.READ)
	if file:
		var json_text = file.get_as_text()
		file.close()

		var json = JSON.new()
		var error = json.parse(json_text)
		if error == OK:
			var data = json.get_data()
			if data is Array:
				message_history.clear()
				for entry in data:
					message_history.append(entry)
				print("[MessageLog] Loaded %d history entries" % message_history.size())

				# Display last 20 entries on load
				_replay_recent_history(20)

## Replay recent history to the display
func _replay_recent_history(count: int):
	var start_idx = max(0, message_history.size() - count)
	for i in range(start_idx, message_history.size()):
		var entry = message_history[i]
		var msg = entry.get("message", "")
		var msg_type = entry.get("type", "info")

		# Skip persistence flag temporarily to avoid duplication
		persist_history = false
		add_message(msg, msg_type)
		persist_history = true

## Get full history as array
func get_full_history() -> Array:
	return message_history.duplicate()

## Clear history file
func clear_history():
	message_history.clear()
	if FileAccess.file_exists(HISTORY_FILE):
		DirAccess.remove_absolute(HISTORY_FILE)
	print("[MessageLog] History cleared")

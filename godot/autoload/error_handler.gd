extends Node
## Global Error Handler - Centralized error management and logging

signal error_occurred(error: GameError)
signal warning_occurred(warning: String)

## Error severity levels
enum Severity {
	INFO,    # Informational message
	WARNING, # Recoverable issue
	ERROR,   # Serious issue, may affect gameplay
	FATAL    # Critical error, game cannot continue
}

## Error categories for better organization
enum Category {
	GAME_STATE,     # State validation errors
	RESOURCES,      # Resource management errors
	ACTIONS,        # Action execution errors
	EVENTS,         # Event system errors
	TURN,           # Turn management errors
	SAVE_LOAD,      # Persistence errors
	CONFIG,         # Configuration errors
	VALIDATION      # General validation errors
}

## Structured error class
class GameError:
	var severity: Severity
	var category: Category
	var message: String
	var context: Dictionary = {}
	var timestamp: float
	var stack_trace: Array = []

	func _init(sev: Severity, cat: Category, msg: String, ctx: Dictionary = {}):
		severity = sev
		category = cat
		message = msg
		context = ctx
		timestamp = Time.get_ticks_msec() / 1000.0
		stack_trace = get_stack()

	func to_dict() -> Dictionary:
		return {
			"severity": Severity.keys()[severity],
			"category": Category.keys()[category],
			"message": message,
			"context": context,
			"timestamp": timestamp,
			"stack_trace": stack_trace
		}

	func format_message() -> String:
		var severity_str = Severity.keys()[severity]
		var category_str = Category.keys()[category]
		var ctx_str = ""
		if context.size() > 0:
			ctx_str = " [Context: %s]" % JSON.stringify(context)
		return "[%s/%s] %s%s" % [severity_str, category_str, message, ctx_str]

# Error history for debugging
var error_history: Array[GameError] = []
var max_history_size: int = 100
var log_to_console: bool = true
var log_to_file: bool = false
var log_file_path: String = "user://error_log.txt"

func _ready():
	print("[ErrorHandler] Initialized - Ready to catch errors")

## Report an error with full context
func report_error(severity: Severity, category: Category, message: String, context: Dictionary = {}) -> GameError:
	var game_error = GameError.new(severity, category, message, context)

	# Add to history
	error_history.append(game_error)
	if error_history.size() > max_history_size:
		error_history.pop_front()

	# Log to console if enabled
	if log_to_console:
		var color_code = _get_color_for_severity(severity)
		print_rich("[color=%s]%s[/color]" % [color_code, game_error.format_message()])

	# Log to file if enabled
	if log_to_file:
		_write_to_log_file(game_error)

	# Emit signal
	if severity >= Severity.ERROR:
		error_occurred.emit(game_error)
	elif severity == Severity.WARNING:
		warning_occurred.emit(game_error.message)

	return game_error

## Convenience methods for different severity levels
func info(category: Category, message: String, context: Dictionary = {}) -> GameError:
	return report_error(Severity.INFO, category, message, context)

func warning(category: Category, message: String, context: Dictionary = {}) -> GameError:
	return report_error(Severity.WARNING, category, message, context)

func report_err(category: Category, message: String, context: Dictionary = {}) -> GameError:
	return report_error(Severity.ERROR, category, message, context)

func fatal(category: Category, message: String, context: Dictionary = {}) -> GameError:
	return report_error(Severity.FATAL, category, message, context)

## Validation helper - returns true if valid, reports error if not
func validate(condition: bool, category: Category, error_message: String, context: Dictionary = {}) -> bool:
	if not condition:
		report_err(category, error_message, context)
		return false
	return true

## Validation helper with custom severity
func validate_with_severity(condition: bool, severity: Severity, category: Category, error_message: String, context: Dictionary = {}) -> bool:
	if not condition:
		report_error(severity, category, error_message, context)
		return false
	return true

## Get recent errors
func get_recent_errors(count: int = 10) -> Array[GameError]:
	var start_idx = max(0, error_history.size() - count)
	return error_history.slice(start_idx)

## Get errors by category
func get_errors_by_category(category: Category) -> Array[GameError]:
	var filtered: Array[GameError] = []
	for error in error_history:
		if error.category == category:
			filtered.append(error)
	return filtered

## Get errors by severity
func get_errors_by_severity(severity: Severity) -> Array[GameError]:
	var filtered: Array[GameError] = []
	for error in error_history:
		if error.severity == severity:
			filtered.append(error)
	return filtered

## Clear error history
func clear_history():
	error_history.clear()
	print("[ErrorHandler] Error history cleared")

## Export error log for debugging
func export_error_log() -> String:
	var log_lines: Array[String] = []
	log_lines.append("=== P(Doom) Error Log ===")
	log_lines.append("Generated: %s" % Time.get_datetime_string_from_system())
	log_lines.append("Total Errors: %d" % error_history.size())
	log_lines.append("")

	for error in error_history:
		log_lines.append(error.format_message())
		if error.context.size() > 0:
			log_lines.append("  Context: %s" % JSON.stringify(error.context, "  "))
		log_lines.append("")

	return "\n".join(log_lines)

## Save error log to file
func save_error_log_to_file(file_path: String = "") -> bool:
	var path = file_path if file_path != "" else log_file_path
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("Failed to open log file for writing: %s" % path)
		return false

	file.store_string(export_error_log())
	file.close()
	print("[ErrorHandler] Error log saved to: %s" % path)
	return true

## Get error statistics
func get_error_stats() -> Dictionary:
	var stats = {
		"total": error_history.size(),
		"by_severity": {},
		"by_category": {}
	}

	# Count by severity
	for sev in Severity.values():
		stats["by_severity"][Severity.keys()[sev]] = 0

	# Count by category
	for cat in Category.values():
		stats["by_category"][Category.keys()[cat]] = 0

	# Tally up
	for error in error_history:
		stats["by_severity"][Severity.keys()[error.severity]] += 1
		stats["by_category"][Category.keys()[error.category]] += 1

	return stats

## Private helpers

func _get_color_for_severity(severity: Severity) -> String:
	match severity:
		Severity.INFO:
			return "cyan"
		Severity.WARNING:
			return "yellow"
		Severity.ERROR:
			return "orange"
		Severity.FATAL:
			return "red"
		_:
			return "white"

func _write_to_log_file(error: GameError):
	var file = FileAccess.open(log_file_path, FileAccess.READ_WRITE)
	if file == null:
		# Try to create new file
		file = FileAccess.open(log_file_path, FileAccess.WRITE)
		if file == null:
			push_error("Failed to open/create log file: %s" % log_file_path)
			return

	file.seek_end()
	file.store_line(error.format_message())
	file.close()

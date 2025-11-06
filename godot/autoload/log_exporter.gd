extends Node
## Log Exporter - Export game state and error logs for debugging

const LOG_DIR = "user://logs"

func _ready():
	# Create logs directory
	var dir = DirAccess.open("user://")
	if not dir.dir_exists("logs"):
		dir.make_dir("logs")

	# Connect to keybind signals
	KeybindManager.log_export_requested.connect(_on_log_export_requested)

	print("[LogExporter] Ready. Logs directory: %s" % OS.get_user_data_dir() + "/logs")

func _on_log_export_requested():
	export_full_log()

## Export comprehensive game log
func export_full_log() -> String:
	var timestamp = Time.get_datetime_dict_from_system()
	var filename = "pdoom_log_%04d%02d%02d_%02d%02d%02d.txt" % [
		timestamp.year,
		timestamp.month,
		timestamp.day,
		timestamp.hour,
		timestamp.minute,
		timestamp.second
	]

	var path = LOG_DIR.path_join(filename)
	var file = FileAccess.open(path, FileAccess.WRITE)

	if file == null:
		push_error("Failed to create log file: %s" % path)
		NotificationManager.error("Log export failed!")
		return ""

	# Write header
	file.store_line("=".repeat(80))
	file.store_line("P(Doom) Game Log Export")
	file.store_line("Generated: %s" % Time.get_datetime_string_from_system())
	file.store_line("=".repeat(80))
	file.store_line("")

	# Game state
	if GameManager and GameManager.is_initialized:
		file.store_line("--- GAME STATE ---")
		file.store_line("Turn: %d" % GameManager.state.turn)
		file.store_line("Doom: %.1f%%" % GameManager.state.doom)
		file.store_line("Money: $%.0f" % GameManager.state.money)
		file.store_line("Compute: %.1f" % GameManager.state.compute)
		file.store_line("Research: %.1f" % GameManager.state.research_progress)
		file.store_line("Papers: %d" % GameManager.state.papers_published)
		file.store_line("Reputation: %d" % GameManager.state.reputation)
		file.store_line("Researchers: %d" % GameManager.state.researchers.size())
		file.store_line("Seed: %s" % GameManager.state.game_seed)
		file.store_line("")

		# Researchers
		if GameManager.state.researchers.size() > 0:
			file.store_line("--- RESEARCHERS ---")
			for researcher in GameManager.state.researchers:
				file.store_line("  - %s (%s, Skill: %d, Salary: $%.0f)" % [
					researcher.researcher_name,
					researcher.specialization,
					researcher.skill_level,
					researcher.current_salary
				])
			file.store_line("")

		# Recent actions
		file.store_line("--- TURN HISTORY ---")
		var history_size = mini(10, GameManager.state.turn)
		file.store_line("(Last %d turns)" % history_size)
		file.store_line("")

	# Error log
	if ErrorHandler:
		file.store_line("--- ERROR LOG ---")
		var error_log = ErrorHandler.get_error_log()
		file.store_line(error_log)
		file.store_line("")

	# System info
	file.store_line("--- SYSTEM INFO ---")
	file.store_line("OS: %s" % OS.get_name())
	file.store_line("Godot: %s" % Engine.get_version_info().string)
	file.store_line("Locale: %s" % OS.get_locale())
	file.store_line("Screen: %dx%d" % [
		DisplayServer.screen_get_size().x,
		DisplayServer.screen_get_size().y
	])
	file.store_line("")

	# Keybinds
	file.store_line("--- KEYBINDS ---")
	file.store_line("Profile: %s" % KeybindManager.current_profile)
	for action in KeybindManager.keybinds.keys():
		var key_name = KeybindManager.get_key_name(action)
		var desc = KeybindManager.keybinds[action]["description"]
		file.store_line("  %s: %s" % [desc, key_name])
	file.store_line("")

	file.store_line("=".repeat(80))
	file.store_line("End of log")
	file.store_line("=".repeat(80))

	file.close()

	var full_path = OS.get_user_data_dir().path_join("logs").path_join(filename)
	print("[LogExporter] Exported log: %s" % full_path)

	NotificationManager.success("Log exported to logs/")

	return full_path

## Open logs folder
func open_logs_folder():
	var path = OS.get_user_data_dir().path_join("logs")
	OS.shell_open(path)

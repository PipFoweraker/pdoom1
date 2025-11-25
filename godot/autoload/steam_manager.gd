extends Node
## Steam Integration Manager
##
## Handles initialization, authentication, and Steam API interactions.
## Works as graceful fallback when Steam is not available.

## Emitted when Steam initialization completes
signal steam_initialized(success: bool)
## Emitted when player info is loaded
signal player_info_loaded(steam_id: int, name: String)

## Whether Steam is available and initialized
var is_steam_enabled: bool = false
## The player's Steam ID
var steam_id: int = 0
## The player's Steam display name
var player_name: String = ""
## Steam app ID (will be loaded from steam_appid.txt)
var app_id: int = 480  # Default to Spacewar for testing

func _ready():
	# Load app ID from steam_appid.txt
	_load_app_id()

	# Only initialize if running through Steam
	if OS.has_feature("steam"):
		print("[Steam] Detected Steam runtime")
		_initialize_steam()
	else:
		print("[Steam] Not running through Steam - using fallback mode")
		is_steam_enabled = false
		steam_initialized.emit(false)

func _load_app_id():
	"""Load Steam App ID from steam_appid.txt"""
	var app_id_path = "res://steam_appid.txt"
	if FileAccess.file_exists(app_id_path):
		var file = FileAccess.open(app_id_path, FileAccess.READ)
		if file:
			var content = file.get_as_text().strip_edges()
			app_id = int(content)
			print("[Steam] Loaded App ID: %d" % app_id)
		else:
			push_warning("[Steam] Could not open steam_appid.txt")
	else:
		push_warning("[Steam] steam_appid.txt not found - using default App ID 480 (Spacewar)")

func _initialize_steam():
	"""Initialize the Steamworks API"""
	# Check if GodotSteam is available
	if not Engine.has_singleton("Steam"):
		push_error("[Steam] GodotSteam singleton not found - plugin may not be installed correctly")
		is_steam_enabled = false
		steam_initialized.emit(false)
		return

	# Initialize Steam
	var init_response = Steam.steamInit()

	# Handle both dictionary and bool returns
	var status_ok = false
	if typeof(init_response) == TYPE_DICTIONARY:
		status_ok = (init_response.get('status', 0) == 1)
		if not status_ok:
			push_error("[Steam] Failed to initialize: %s" % init_response.get('verbal', 'Unknown error'))
	elif typeof(init_response) == TYPE_BOOL:
		status_ok = init_response

	if not status_ok:
		is_steam_enabled = false
		steam_initialized.emit(false)
		return

	# Steam initialized successfully
	is_steam_enabled = true

	# Get player info
	steam_id = Steam.getSteamID()
	player_name = Steam.getPersonaName()

	print("[Steam] Initialized successfully")
	print("[Steam] Player: %s (ID: %d)" % [player_name, steam_id])

	steam_initialized.emit(true)
	player_info_loaded.emit(steam_id, player_name)

func _process(_delta):
	"""Run Steam callbacks every frame"""
	if is_steam_enabled:
		Steam.run_callbacks()

func unlock_achievement(achievement_id: String):
	"""Unlock a Steam achievement"""
	if not is_steam_enabled:
		return

	# Check if already unlocked
	var achievement_data = Steam.getAchievement(achievement_id)
	if achievement_data and achievement_data['achieved']:
		return  # Already unlocked

	# Unlock the achievement
	var success = Steam.setAchievement(achievement_id)
	if success:
		print("[Steam] Unlocked achievement: %s" % achievement_id)
		Steam.storeStats()  # Save achievement progress
	else:
		push_warning("[Steam] Failed to unlock achievement: %s" % achievement_id)

func get_achievement_status(achievement_id: String) -> Dictionary:
	"""Get achievement unlock status"""
	if not is_steam_enabled:
		return {'achieved': false, 'unlock_time': 0}

	return Steam.getAchievement(achievement_id)

func clear_achievement(achievement_id: String):
	"""Clear an achievement (for testing only)"""
	if not is_steam_enabled:
		return

	Steam.clearAchievement(achievement_id)
	Steam.storeStats()
	print("[Steam] Cleared achievement: %s" % achievement_id)

func reset_all_stats(achievements_too: bool = true):
	"""Reset all stats and optionally achievements (for testing only)"""
	if not is_steam_enabled:
		return

	Steam.resetAllStats(achievements_too)
	print("[Steam] Reset all stats (achievements: %s)" % achievements_too)

func get_stat_int(stat_name: String) -> int:
	"""Get an integer stat value"""
	if not is_steam_enabled:
		return 0

	return Steam.getStatInt(stat_name)

func set_stat_int(stat_name: String, value: int):
	"""Set an integer stat value"""
	if not is_steam_enabled:
		return

	Steam.setStatInt(stat_name, value)
	Steam.storeStats()

func get_stat_float(stat_name: String) -> float:
	"""Get a float stat value"""
	if not is_steam_enabled:
		return 0.0

	return Steam.getStatFloat(stat_name)

func set_stat_float(stat_name: String, value: float):
	"""Set a float stat value"""
	if not is_steam_enabled:
		return

	Steam.setStatFloat(stat_name, value)
	Steam.storeStats()

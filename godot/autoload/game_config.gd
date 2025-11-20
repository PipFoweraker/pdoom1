extends Node
## Global Game Configuration Singleton
## Manages persistent settings and game state across scenes

# Player/Game Configuration
var player_name: String = "Researcher"
var lab_name: String = "AI Safety Lab"
var game_seed: String = ""  # Empty = weekly challenge seed
var difficulty: int = 1  # 0=Easy, 1=Standard, 2=Hard

# Audio Settings
var master_volume: int = 80  # 0-100
var sfx_volume: int = 80  # 0-100
var music_volume: int = 80  # 0-100

# Graphics Settings
var graphics_quality: int = 1  # 0=Low, 1=Medium, 2=High
var fullscreen: bool = false

# Game State
var current_game_active: bool = false
var games_played: int = 0
var config_mode: String = "default"  # "default" = weekly seed (locked), "custom" = user configured

# Config file path
const CONFIG_FILE = "user://config.cfg"

# Signals for config changes
signal config_changed(key: String, value)
signal config_loaded()
signal config_saved()

func _ready():
	print("[GameConfig] Initializing global configuration...")
	load_config()
	apply_audio_settings()
	apply_graphics_settings()
	print("[GameConfig] Configuration loaded and applied")

## Save configuration to disk
func save_config() -> void:
	print("[GameConfig] Saving configuration...")

	var config = ConfigFile.new()

	# Player section
	config.set_value("player", "name", player_name)
	config.set_value("player", "last_lab_name", lab_name)
	config.set_value("player", "games_played", games_played)

	# Game section
	config.set_value("game", "difficulty", difficulty)
	config.set_value("game", "last_seed", game_seed)

	# Audio section
	config.set_value("audio", "master_volume", master_volume)
	config.set_value("audio", "sfx_volume", sfx_volume)
	config.set_value("audio", "music_volume", music_volume)

	# Graphics section
	config.set_value("graphics", "quality", graphics_quality)
	config.set_value("graphics", "fullscreen", fullscreen)

	# Save to file
	var err = config.save(CONFIG_FILE)
	if err != OK:
		print("[GameConfig] ERROR: Failed to save config: ", err)
	else:
		print("[GameConfig] Configuration saved successfully")
		config_saved.emit()

## Load configuration from disk
func load_config() -> void:
	print("[GameConfig] Loading configuration...")

	var config = ConfigFile.new()
	var err = config.load(CONFIG_FILE)

	if err != OK:
		print("[GameConfig] No existing config found, using defaults")
		return

	# Load player settings
	player_name = config.get_value("player", "name", player_name)
	lab_name = config.get_value("player", "last_lab_name", lab_name)
	games_played = config.get_value("player", "games_played", games_played)

	# Load game settings
	difficulty = config.get_value("game", "difficulty", difficulty)
	game_seed = config.get_value("game", "last_seed", game_seed)

	# Load audio settings
	master_volume = config.get_value("audio", "master_volume", master_volume)
	sfx_volume = config.get_value("audio", "sfx_volume", sfx_volume)
	music_volume = config.get_value("audio", "music_volume", music_volume)

	# Load graphics settings
	graphics_quality = config.get_value("graphics", "quality", graphics_quality)
	fullscreen = config.get_value("graphics", "fullscreen", fullscreen)

	print("[GameConfig] Configuration loaded successfully")
	config_loaded.emit()

## Apply audio settings to audio buses
func apply_audio_settings() -> void:
	# Master bus (index 0)
	var master_db = linear_to_db(master_volume / 100.0)
	AudioServer.set_bus_volume_db(0, master_db)

	var sfx_db = 0.0
	var music_db = 0.0

	# SFX bus (index 1) - if it exists
	if AudioServer.get_bus_count() > 1:
		sfx_db = linear_to_db(sfx_volume / 100.0)
		AudioServer.set_bus_volume_db(1, sfx_db)

	# Music bus (index 2) - if it exists
	if AudioServer.get_bus_count() > 2:
		music_db = linear_to_db(music_volume / 100.0)
		AudioServer.set_bus_volume_db(2, music_db)
		print("[GameConfig] Audio settings applied - Master: %d%% (%.1f dB), SFX: %d%% (%.1f dB), Music: %d%% (%.1f dB)" % [master_volume, master_db, sfx_volume, sfx_db, music_volume, music_db])
	elif AudioServer.get_bus_count() > 1:
		print("[GameConfig] Audio settings applied - Master: %d%% (%.1f dB), SFX: %d%% (%.1f dB)" % [master_volume, master_db, sfx_volume, sfx_db])
	else:
		print("[GameConfig] Audio settings applied - Master: %d%% (%.1f dB)" % [master_volume, master_db])

## Apply graphics settings
func apply_graphics_settings() -> void:
	# Fullscreen mode
	if fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)

	# TODO: Apply graphics quality settings
	# For now, Godot uses default quality settings
	print("[GameConfig] Graphics settings applied - Fullscreen: %s, Quality: %d" % [fullscreen, graphics_quality])

## Update a setting and optionally save
func set_setting(key: String, value, save_immediately: bool = false) -> void:
	match key:
		"player_name":
			player_name = value
		"lab_name":
			lab_name = value
		"game_seed":
			game_seed = value
		"difficulty":
			difficulty = value
		"master_volume":
			master_volume = value
			apply_audio_settings()
		"sfx_volume":
			sfx_volume = value
			apply_audio_settings()
		"music_volume":
			music_volume = value
			apply_audio_settings()
		"graphics_quality":
			graphics_quality = value
			apply_graphics_settings()
		"fullscreen":
			fullscreen = value
			apply_graphics_settings()
		_:
			print("[GameConfig] WARNING: Unknown setting: ", key)
			return

	config_changed.emit(key, value)

	if save_immediately:
		save_config()

## Get difficulty as string
func get_difficulty_string() -> String:
	match difficulty:
		0:
			return "Easy"
		1:
			return "Standard"
		2:
			return "Hard"
		_:
			return "Unknown"

## Get graphics quality as string
func get_graphics_quality_string() -> String:
	match graphics_quality:
		0:
			return "Low"
		1:
			return "Medium"
		2:
			return "High"
		_:
			return "Unknown"

## Get all configuration as dictionary (for GameManager)
func get_game_config() -> Dictionary:
	return {
		"player_name": player_name,
		"lab_name": lab_name,
		"game_seed": game_seed,
		"difficulty": difficulty,
		"difficulty_string": get_difficulty_string()
	}

## Reset game configuration to defaults (keep settings)
func reset_game_config() -> void:
	player_name = "Researcher"
	lab_name = "AI Safety Lab"
	game_seed = ""
	difficulty = 1
	print("[GameConfig] Game configuration reset to defaults")

## Increment games played counter
func increment_games_played() -> void:
	games_played += 1
	save_config()
	print("[GameConfig] Games played: %d" % games_played)

## Get weekly challenge seed (generate based on current week)
func get_weekly_seed() -> String:
	# Generate seed based on current year and week number
	var time = Time.get_datetime_dict_from_system()
	var year = time.year
	var week = Time.get_ticks_msec() / 1000 / 60 / 60 / 24 / 7  # Rough week calculation
	return "weekly-%d-w%d" % [year, week % 52]

## Get display seed (weekly or custom)
func get_display_seed() -> String:
	if game_seed.is_empty():
		return get_weekly_seed()
	return game_seed

## Format money with comma separators (e.g., $245,000)
## Issue #436 - Player feedback: add commas to all $ references
## Note: Not static because GameConfig is an autoload singleton
func format_money(amount: float) -> String:
	var is_negative = amount < 0
	var abs_amount = abs(amount)

	# Convert to string and split at decimal point
	var int_part = int(abs_amount)
	var decimal_part = abs_amount - int_part

	# Format integer part with commas
	var int_str = str(int_part)
	var formatted = ""
	var count = 0

	# Add commas from right to left
	for i in range(int_str.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			formatted = "," + formatted
		formatted = int_str[i] + formatted
		count += 1

	# Add negative sign if needed
	if is_negative:
		formatted = "-$" + formatted
	else:
		formatted = "$" + formatted

	# Add decimal part if significant (for costs like $2,500.50)
	if decimal_part > 0.01:
		formatted += "%.2f" % decimal_part
		formatted = formatted.replace("0.", ".")

	return formatted

## Debug print current configuration
func print_config() -> void:
	print("[GameConfig] === Current Configuration ===")
	print("  Player: %s" % player_name)
	print("  Lab: %s" % lab_name)
	print("  Seed: %s" % get_display_seed())
	print("  Difficulty: %s" % get_difficulty_string())
	print("  Master Volume: %d%%" % master_volume)
	print("  SFX Volume: %d%%" % sfx_volume)
	print("  Music Volume: %d%%" % music_volume)
	print("  Graphics: %s" % get_graphics_quality_string())
	print("  Fullscreen: %s" % fullscreen)
	print("  Games Played: %d" % games_played)
	print("========================================")

extends Node
## Global Game Configuration Singleton
## Manages persistent settings and game state across scenes

# Player/Game Configuration
var player_name: String = "Researcher"
var lab_name: String = "AI Safety Lab"
var game_seed: String = ""  # Empty = weekly challenge seed
var difficulty: int = 1  # 0=Easy, 1=Standard, 2=Hard
var scenario_id: String = ""  # Empty = standard game, otherwise scenario pack ID

# Baseline Computation Mode (Issue #372)
# 0 = Auto (precomputed for weekly, eager for custom)
# 1 = Eager (compute at game start, ready by end)
# 2 = Blind (compute on-demand at game end)
var baseline_mode: int = 0

# Audio Settings
var master_volume: int = 50  # 0-100
var sfx_volume: int = 50  # 0-100
var music_volume: int = 50  # 0-100

# Graphics Settings
var graphics_quality: int = 1  # 0=Low, 1=Medium, 2=High
var fullscreen: bool = false

# Accessibility Settings
var colorblind_mode: bool = false  # Adds patterns/symbols alongside colors

# Interface Settings
# Rival-lab intel lines in the WATCH feed (the "rivals" channel, v0 of the future
# News feedline / DQ-32). Default ON; players who find rival chatter noisy can hide
# it. Display-only -- the underlying log content and simulation are unchanged.
var show_rivals_feed: bool = true

# Leaderboard Settings
# Opt-out for uploading scores to the global leaderboard (LeaderboardSync).
# Default ON for alpha; players who flip it off keep local scores only.
var submit_scores_global: bool = true

# Game State
var current_game_active: bool = false
var games_played: int = 0
var config_mode: String = "default"  # "default" = weekly seed (locked), "custom" = user configured

# L7 (#618) save/load handoff (transient, not saved to config file): the welcome
# screen sets this before switching to main.tscn; MainUI's autostart consumes it
# and boots GameManager.load_saved_game() instead of start_new_game().
var pending_load_path: String = ""

# Version tracking for What's New feature
var last_seen_version: String = ""  # Empty = never seen patch notes

# Cold-open intro gate (#801). Mirrors the last_seen_version / whats_new show-once
# pattern, but is a SEPARATE track: a player may have seen patch notes yet never the
# intro, and we may want to force a re-intro on a major narrative revision WITHOUT
# re-showing patch notes. Persisted in the "game" section next to last_seen_version.
var last_seen_intro_version: String = ""  # "" = never seen the cold-open

# Master opt-out for story intros / cinematics (#801). Persisted in the "game" section.
#
# REUSABLE CONVENTION -- "auto-flip on player signal + reversible settings toggle"
# (Pip's general preference pattern): a PLAYER ACTION quietly sets a persistent
# preference (here: completing a hold-to-skip auto-flips play_intros = false, respecting
# the "I skip intros" signal), and the settings menu ALWAYS lets the player undo it (the
# "Play story intros" toggle re-enables it). This lets players configure their runs by
# doing, while keeping every such auto-flip reversible. Reuse this shape elsewhere.
var play_intros: bool = true

# Transient (NOT persisted): set true by the cold-open on completion; main_ui reads it
# to pulse the first lever (hire) button once as an advisor nudge, then clears it.
# Pure presentation -- never touches game state, RNG, or score.
var show_first_lever_hint: bool = false
# Single source of truth for the game version is version.txt at the repo root.
# This const is the runtime copy: it is STAMPED from version.txt by
# tools/sync_version.py (metadata overrides hard values). Do not hand-edit --
# bump version.txt then run `python tools/sync_version.py`. CI's `--check` mode
# fails if this drifts from version.txt. Kept as a compiled-in const (not a
# runtime file read) because version.txt lives outside res:// and the leaderboard
# board-key derives from this value, so it must resolve identically in exported
# builds where a res:// text read is not guaranteed to be packed.
const CURRENT_VERSION: String = "0.11.0"

# Cold-open intro content version (#801). Independent of CURRENT_VERSION on purpose:
# ordinary patch releases must NOT re-trigger the intro. Bump this ONLY when the
# cold-open content changes enough to warrant a forced re-show.
const INTRO_VERSION: String = "1"

# Leaderboard State (transient, not saved)
var latest_leaderboard_entry: String = ""  # UUID of most recent score entry

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
	config.set_value("game", "scenario_id", scenario_id)
	config.set_value("game", "last_seen_version", last_seen_version)
	config.set_value("game", "last_seen_intro_version", last_seen_intro_version)
	config.set_value("game", "play_intros", play_intros)
	config.set_value("game", "baseline_mode", baseline_mode)

	# Audio section
	config.set_value("audio", "master_volume", master_volume)
	config.set_value("audio", "sfx_volume", sfx_volume)
	config.set_value("audio", "music_volume", music_volume)

	# Graphics section
	config.set_value("graphics", "quality", graphics_quality)
	config.set_value("graphics", "fullscreen", fullscreen)

	# Accessibility section
	config.set_value("accessibility", "colorblind_mode", colorblind_mode)

	# Interface section
	config.set_value("interface", "show_rivals_feed", show_rivals_feed)

	# Leaderboard section
	config.set_value("leaderboard", "submit_scores_global", submit_scores_global)

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
	scenario_id = config.get_value("game", "scenario_id", scenario_id)
	last_seen_version = config.get_value("game", "last_seen_version", last_seen_version)
	last_seen_intro_version = config.get_value("game", "last_seen_intro_version", last_seen_intro_version)
	play_intros = config.get_value("game", "play_intros", play_intros)
	baseline_mode = config.get_value("game", "baseline_mode", baseline_mode)

	# Load audio settings
	master_volume = config.get_value("audio", "master_volume", master_volume)
	sfx_volume = config.get_value("audio", "sfx_volume", sfx_volume)
	music_volume = config.get_value("audio", "music_volume", music_volume)

	# Load graphics settings
	graphics_quality = config.get_value("graphics", "quality", graphics_quality)
	fullscreen = config.get_value("graphics", "fullscreen", fullscreen)

	# Load accessibility settings
	colorblind_mode = config.get_value("accessibility", "colorblind_mode", colorblind_mode)

	# Load interface settings
	show_rivals_feed = config.get_value("interface", "show_rivals_feed", show_rivals_feed)

	# Load leaderboard settings
	submit_scores_global = config.get_value("leaderboard", "submit_scores_global", submit_scores_global)

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
		"colorblind_mode":
			colorblind_mode = value
		"submit_scores_global":
			submit_scores_global = value
		"play_intros":
			play_intros = value
		"baseline_mode":
			baseline_mode = value
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

## Get baseline mode as string (Issue #372)
func get_baseline_mode_string() -> String:
	match baseline_mode:
		0:
			return "Auto"  # Precomputed for weekly, eager for custom
		1:
			return "Eager"  # Compute at game start
		2:
			return "Blind"  # Compute on-demand at end
		_:
			return "Unknown"

## Check if we should use precomputed baseline (weekly league with known baseline)
func should_use_precomputed_baseline() -> bool:
	# Weekly league games use precomputed baselines (mode 0 with empty seed)
	return baseline_mode == 0 and game_seed.is_empty()

## Check if we should start background baseline at game start
func should_start_background_baseline() -> bool:
	# Eager mode always, or Auto mode with custom seed
	return baseline_mode == 1 or (baseline_mode == 0 and not game_seed.is_empty())

## Get all configuration as dictionary (for GameManager)
func get_game_config() -> Dictionary:
	return {
		"player_name": player_name,
		"lab_name": lab_name,
		"game_seed": game_seed,
		"difficulty": difficulty,
		"difficulty_string": get_difficulty_string(),
		"scenario_id": scenario_id
	}

## Reset game configuration to defaults (keep settings)
func reset_game_config() -> void:
	player_name = "Researcher"
	lab_name = "AI Safety Lab"
	game_seed = ""
	difficulty = 1
	scenario_id = ""
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

## Check if there are unseen patch notes (new version since last seen)
func has_unseen_patch_notes() -> bool:
	if last_seen_version.is_empty():
		return true  # Never seen any patch notes
	return last_seen_version != CURRENT_VERSION

## Mark current version's patch notes as seen
func mark_patch_notes_seen() -> void:
	last_seen_version = CURRENT_VERSION
	save_config()
	print("[GameConfig] Patch notes marked as seen for version %s" % CURRENT_VERSION)

## Check if the cold-open intro should play (#801).
## Gated PURELY on last_seen_intro_version (NOT games_played) so it is immune to the
## increment_games_played() ordering in config_confirmation.gd: that increment runs
## BEFORE we route to the intro, which would break a games_played==0 test.
func should_show_intro() -> bool:
	# play_intros is the master gate: if the player opted out (or auto-opted-out via a
	# hold-to-skip), NO intro shows -- even a bumped INTRO_VERSION stays suppressed until
	# they re-enable it in settings.
	if not play_intros:
		return false
	return last_seen_intro_version != INTRO_VERSION

## Mark the cold-open intro as seen for the current INTRO_VERSION. Called on intro
## completion OR skip (a skip counts as seen, same as the whats-new modal).
func mark_intro_seen() -> void:
	last_seen_intro_version = INTRO_VERSION
	save_config()
	print("[GameConfig] Cold-open intro marked as seen for intro version %s" % INTRO_VERSION)

## Get the current game version
func get_current_version() -> String:
	return CURRENT_VERSION

## Debug print current configuration
func print_config() -> void:
	print("[GameConfig] === Current Configuration ===")
	print("  Player: %s" % player_name)
	print("  Lab: %s" % lab_name)
	print("  Seed: %s" % get_display_seed())
	print("  Difficulty: %s" % get_difficulty_string())
	print("  Scenario: %s" % (scenario_id if not scenario_id.is_empty() else "Standard"))
	print("  Master Volume: %d%%" % master_volume)
	print("  SFX Volume: %d%%" % sfx_volume)
	print("  Music Volume: %d%%" % music_volume)
	print("  Graphics: %s" % get_graphics_quality_string())
	print("  Fullscreen: %s" % fullscreen)
	print("  Colorblind Mode: %s" % colorblind_mode)
	print("  Games Played: %d" % games_played)
	print("  Baseline Mode: %s" % get_baseline_mode_string())
	print("  Last Seen Version: %s" % last_seen_version)
	print("  Last Seen Intro Version: %s" % last_seen_intro_version)
	print("  Current Version: %s" % CURRENT_VERSION)
	print("========================================")

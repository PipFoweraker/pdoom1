extends Node
## Global Game Configuration Singleton
## Manages persistent settings and game state across scenes

# Player/Game Configuration
# Install-default identity as NAMED consts: the game-over default-identity
# prompt (Pip 2026-08-06, after two friends' scores landed as identical
# "AI Safety Lab" rows) compares against these, so the field initialisers,
# reset_game_config() and has_default_identity() must all read the same pair.
const DEFAULT_PLAYER_NAME := "Researcher"
const DEFAULT_LAB_NAME := "AI Safety Lab"
var player_name: String = DEFAULT_PLAYER_NAME
var lab_name: String = DEFAULT_LAB_NAME
var game_seed: String = ""  # Empty = weekly challenge seed
var difficulty: int = 1  # 0=Easy, 1=Standard, 2=Hard -- the player's stored PREFERENCE. What a run actually PLAYS at is effective_difficulty() below (league lock, #1058/#1084).
var org_type: String = "nonprofit"  # Early-game org form: "nonprofit" | "for_profit" (DQ-19). Set at pregame; default flow forces nonprofit.
var scenario_id: String = ""  # Empty = standard game, otherwise scenario pack ID

# --- League difficulty lock (#1058, enforced at CONSUMPTION per #1084) ---------------
# While true, every run PLAYS at Standard: GameManager._apply_difficulty_settings()
# reads effective_difficulty() below, so no menu write, config.cfg edit, or nav route
# into main.tscn can start a non-Standard run. The raw `difficulty` field above stays
# the player's stored preference, honoured again the day this const flips false.
# Enforcing here -- where the value becomes game state -- rather than in pregame_setup
# (one of six routes into main.tscn) is the #1060 shape: a named accessor at the choke
# point, not a lock on one screen.
const LEAGUE_DIFFICULTY_LOCK := true
const LEAGUE_LOCKED_DIFFICULTY := 1  # Standard
# One tooltip everywhere the lock disables a control (pregame_setup + settings_menu).
const DIFFICULTY_LOCK_TOOLTIP := "Locked to Standard for the first leagues -- every score sits on one comparable board. Difficulty tiers return once the board can tell them apart."
# TEST SEAM ONLY (the perf_log override pattern): null => follow the const; true/false
# => forced. Lets the simulation tier keep exercising the Easy/Hard scaling machinery
# that returns when the lock lifts. Never set this from UI or gameplay code.
var _difficulty_lock_override = null

func is_difficulty_locked() -> bool:
	if _difficulty_lock_override != null:
		return bool(_difficulty_lock_override)
	return LEAGUE_DIFFICULTY_LOCK

## The difficulty a run actually PLAYS at. EVERY consumer must route through this;
## reading the raw field at a consumption site is how #1084 happened.
func effective_difficulty() -> int:
	if is_difficulty_locked():
		return LEAGUE_LOCKED_DIFFICULTY
	if difficulty < 0 or difficulty > 2:
		return 1  # invalid persisted value degrades to Standard (issue #447 family)
	return difficulty

# Baseline Computation Mode (Issue #372)
# 0 = Auto (precomputed for weekly, eager for custom)
# 1 = Eager (compute at game start, ready by end)
# 2 = Blind (compute on-demand at game end)
var baseline_mode: int = 0

# Audio Settings
var master_volume: int = 50  # 0-100
var sfx_volume: int = 50  # 0-100
# 0-100. DEFAULT ONLY -- load_config() below passes the current value as the
# ConfigFile fallback, so an existing user://config.cfg always wins and nobody
# who has already moved the slider is touched by a change here.
# History: 50 -> 20 (Pip 2026-07-24, "too loud/intense on first playtest")
#          20 -> 15 (Pip 2026-08-01 11:38, after twice turning it down by hand
#          mid-playtest; he landed on 13% unprompted on 2026-07-31).
# Buses multiply: default_bus_layout.tres routes Music -> Master, so the music a
# fresh player actually hears is master 50% x music 15% = 0.075 linear
# (-22.5 dBFS). The beds are normalised to ~-16 LUFS, so that is ~-38.5 LUFS at
# the output -- audible under speech, roughly 1.2 dB above the 13% Pip chose.
var music_volume: int = 15

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

# Onboarding gameplay hints (issue #720). Master switch for in-play help surfaces
# (the getting-started hint, the first-launch welcome overlay, and any future hint
# surface). Default ON; players who find hints noisy can flip it off. View-only --
# never touches game state, RNG, turn order, or scoring.
var show_hints: bool = true

# A/B UI layout switch (UI_PROPOSALS_2026-07-22 section 4). Scaffolding for Pip's
# in-game iteration: "classic" = today's PLAN/WATCH arrangement (pixel-identical);
# "proposed" = the P6/P9/P10/P11 assembly (constrained cat, grouped action submenus,
# committed-queue gantt, space reclaim). Container-reflow only -- never touches the sim.
# The loser is deleted once Pip picks; this flag is not a permanent feature.
var ui_layout: String = "classic"
const UI_LAYOUTS := ["classic", "proposed"]

# Leaderboard Settings -- IDENTITY CONSENT model (privacy ruling 2026-07-26).
# Submitting to the global board shares PLAYER NAME + LAB NAME + score publicly,
# so it requires an EXPLICIT one-time opt-in: submit_scores_global is the
# remembered choice, leaderboard_consent_asked records that the player actually
# MADE that choice (via the game-over prompt or the Settings toggle -- flipping
# the toggle counts as the explicit click). The effective gate is asked AND
# opted-in (LeaderboardSync.should_submit). Both reversible any time in Settings.
# MIGRATION: pre-ruling configs persisted submit_scores_global=true (the old
# default-ON alpha posture) without any explicit click; consent_asked defaults
# false, so those players get the one-time prompt at their next game over.
var submit_scores_global: bool = false
var leaderboard_consent_asked: bool = false
# One-time gracious nudge (privacy ruling): an ANONYMOUS player (empty name/lab)
# who reaches score submission without having opted in gets exactly ONE friendly
# reminder that the global board exists; this flag persists so later
# playthroughs stay silent. See LeaderboardSync.consent_flow_state.
var leaderboard_reminder_shown: bool = false
# One-time default-identity prompt (Pip 2026-08-06): a player about to UPLOAD a
# score while still carrying the unedited install defaults gets exactly ONE
# chance to claim a name first -- a public board of identical "Researcher --
# AI Safety Lab" rows is one nobody can find themselves on. Keeping the default
# is a legitimate answer; this flag persists either way (set at SHOW time, the
# leaderboard_reminder_shown shape above), so the question is never asked twice.
# See LeaderboardSync.default_identity_prompt_state -- deliberately LAYERED ON
# TOP of the consent flow, never a change to it: consent still decides WHETHER
# an upload can happen; this only decides whether the name is worth a one-time
# ask first.
var default_identity_prompt_shown: bool = false

# Privacy: anonymous launch ping opt-out (#799). The ping is a single Plausible
# event on boot carrying ONLY a random install UUID + version + OS + first_launch
# -- no hardware ids, no PII (UpdateCheck.build_ping_body is the whitelist).
# DECOUPLED from the leaderboard gate (coordinator ruling 2026-07-26, flagged in
# PR #942 for Pip's Tuesday veto): the leaderboard gate above now means IDENTITY
# consent specifically, and the ping carries no identity, so it honours only
# this default-ON toggle (UpdateCheck.should_send_ping).
var send_launch_ping: bool = true

# PRIVACY POSTURE SSOT: docs/PRIVACY_POSTURE.md (two-tier model, ruled
# 2026-07-26). Repo-root user_privacy.json is the machine-readable posture
# record (rewritten to match the ruling; legacy Python-era keys preserved
# there under legacy_python_era, unread by this build):
#   tier 1 (identity: leaderboard) -> leaderboard_consent_asked AND
#     submit_scores_global above (legacy opt_in_leaderboard maps here; the
#     opt-in-default-OFF postures agree)
#   tier 2 (anonymous: launch ping) -> send_launch_ping above, default ON,
#     decoupled from tier 1 (approved by Pip 2026-07-26).

# Update notice: the remote version the player dismissed on the welcome screen
# (#799 "don't re-nag every launch for the same version"). Stored WITHOUT the
# v prefix. A future release newer than this shows the notice again.
var dismissed_update_version: String = ""

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
# THE ONBOARDING -> SCOUTING HANDOFF (#811 item 1: "the cold-open's final beat should hand
# an active scouting choice, not end on narrative"). The cold-open sets these on its way
# out; main_ui pulses whichever action id is named here instead of a hardcoded one. Two
# transient strings is the whole wire -- the seam is deliberately tiny so re-pointing the
# handoff at a different first choice later is a one-line content change, not a refactor.
var first_lever_action_id: String = "scouting"
var first_lever_hint_text: String = "Advisor: you do not know anything yet. Go and find out -- scouting (the glowing button)."
# First-launch welcome overlay show-once gate (issue #720). Reuses the
# last_seen_version show-once shape: once the welcome/help overlay has been shown
# it is marked seen and PERSISTED, so it never re-appears on later launches -- even
# if the player quits before finishing a game (which would leave games_played at 0).
var welcome_seen: bool = false
# Single source of truth for the game version is version.txt at the repo root.
# This const is the runtime copy: it is STAMPED from version.txt by
# tools/sync_version.py (metadata overrides hard values). Do not hand-edit --
# bump version.txt then run `python tools/sync_version.py`. CI's `--check` mode
# fails if this drifts from version.txt. Kept as a compiled-in const (not a
# runtime file read) because version.txt lives outside res:// and the leaderboard
# board-key derives from this value, so it must resolve identically in exported
# builds where a res:// text read is not guaranteed to be packed.
const CURRENT_VERSION: String = "0.14.4"

# Cold-open intro content version (#801). Independent of CURRENT_VERSION on purpose:
# ordinary patch releases must NOT re-trigger the intro. Bump this ONLY when the
# cold-open content changes enough to warrant a forced re-show.
const INTRO_VERSION: String = "1"

# Ladder (ruleset/epoch) version -- the build-vs-ladder version split
# (docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md). SSOT is ladder_version.txt at
# the repo root; STAMPED here by tools/sync_version.py exactly like CURRENT_VERSION
# (do not hand-edit; `--check` fails on drift). This integer bumps ONLY when
# gameplay/scoring/seed/RNG rules change (spec Section 3 checklist) -- cosmetic
# patches bump version.txt alone, so everyone stays on the same leaderboard.
# Epoch L1 == the current ruleset. NOTE: #789 hiring-stitch changes gameplay and
# bumps this to 2 at the v0.13 epoch cut (spec DECISION C2) -- do not bump earlier.
const LADDER_VERSION: String = "6"

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
	config.set_value("interface", "ui_layout", ui_layout)
	config.set_value("interface", "show_hints", show_hints)

	# Onboarding section (issue #720)
	config.set_value("onboarding", "welcome_seen", welcome_seen)

	# Leaderboard section (identity consent, privacy ruling 2026-07-26)
	config.set_value("leaderboard", "submit_scores_global", submit_scores_global)
	config.set_value("leaderboard", "consent_asked", leaderboard_consent_asked)
	config.set_value("leaderboard", "reminder_shown", leaderboard_reminder_shown)
	config.set_value("leaderboard", "identity_prompt_shown", default_identity_prompt_shown)

	# Privacy + updates section (#799)
	config.set_value("privacy", "send_launch_ping", send_launch_ping)
	config.set_value("updates", "dismissed_update_version", dismissed_update_version)

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
	ui_layout = config.get_value("interface", "ui_layout", ui_layout)
	if not UI_LAYOUTS.has(ui_layout):
		ui_layout = "classic"  # guard against a stale/garbage persisted value
	show_hints = config.get_value("interface", "show_hints", show_hints)

	# Load onboarding settings (issue #720)
	welcome_seen = config.get_value("onboarding", "welcome_seen", welcome_seen)

	# Load leaderboard settings (identity consent, privacy ruling 2026-07-26)
	submit_scores_global = config.get_value("leaderboard", "submit_scores_global", submit_scores_global)
	leaderboard_consent_asked = config.get_value("leaderboard", "consent_asked", leaderboard_consent_asked)
	leaderboard_reminder_shown = config.get_value("leaderboard", "reminder_shown", leaderboard_reminder_shown)
	default_identity_prompt_shown = config.get_value("leaderboard", "identity_prompt_shown", default_identity_prompt_shown)

	# Load privacy + updates settings (#799)
	send_launch_ping = config.get_value("privacy", "send_launch_ping", send_launch_ping)
	dismissed_update_version = config.get_value("updates", "dismissed_update_version", dismissed_update_version)

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
		"show_hints":
			show_hints = value
		"show_rivals_feed":
			# Settings-menu row for the WATCH feed's rival-intel preference. The WATCH
			# screen's own filter button predates this case and writes the var + saves
			# directly (main_ui._on_rivals_filter_changed); both paths land on the same
			# persisted field.
			show_rivals_feed = value
		"submit_scores_global":
			submit_scores_global = value
		"send_launch_ping":
			send_launch_ping = value
		"play_intros":
			play_intros = value
		"ui_layout":
			# Reject unknown layout names so the UI never applies a garbage flag.
			if not UI_LAYOUTS.has(value):
				print("[GameConfig] WARNING: Unknown ui_layout: ", value)
				return
			ui_layout = value
		"baseline_mode":
			baseline_mode = value
		_:
			print("[GameConfig] WARNING: Unknown setting: ", key)
			return

	config_changed.emit(key, value)

	if save_immediately:
		save_config()

## Get difficulty as string (the RAW stored preference -- for settings UI)
func get_difficulty_string() -> String:
	return _difficulty_name(difficulty)

## The difficulty the run actually PLAYS at, as a string (league lock aware)
func get_effective_difficulty_string() -> String:
	return _difficulty_name(effective_difficulty())

func _difficulty_name(value: int) -> String:
	match value:
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

## True while EITHER identity field still holds the unedited install default.
## Either alone keeps the board entry generic (the board renders the lab name;
## consent shares both names), so either alone keeps the one-time prompt armed.
## Exact match on purpose: "unedited default" means literally these strings --
## a player who deliberately typed something else, however close, has chosen it.
func has_default_identity() -> bool:
	return player_name.strip_edges() == DEFAULT_PLAYER_NAME or lab_name.strip_edges() == DEFAULT_LAB_NAME

## Reset game configuration to defaults (keep settings)
func reset_game_config() -> void:
	player_name = DEFAULT_PLAYER_NAME
	lab_name = DEFAULT_LAB_NAME
	game_seed = ""
	difficulty = 1
	scenario_id = ""
	print("[GameConfig] Game configuration reset to defaults")

## Increment games played counter
func increment_games_played() -> void:
	games_played += 1
	save_config()
	print("[GameConfig] Games played: %d" % games_played)

## Manual featured-league seed override. Non-empty PINS the featured/default
## league seed -- the metabolic cycle rotates it at Pip's call ("manual for now",
## see docs/RELEASE_AND_LEAGUE_CYCLE.html). To rotate the league, edit this const
## (or clear it to fall back to the calendar-week auto-seed below).
##
## THE SEED NAMES THE ISO WEEK THE LEAGUE OPENS IN. That convention was followed
## by all five rolls to date (w30 on 2026-07-24, w31 on 07-31, w32 on 08-07,
## w33 on 08-13, w34 on 08-23) but was written down NOWHERE until 2026-08-24 --
## the ritual sheet carried only examples. It is now stated here, at the const
## it governs, and in docs/releases/RELEASE_LINKING_TO_0.20.md.
##
## RULING: 2026-08-24 -- the featured seed names the ISO week the league opens in, so a league that slips is renamed to the week it actually runs and the slip is recorded in the log, never hidden in the label -- flavour: league-seeds -- mechanism: godot/autoload/game_config.gd get_weekly_seed
##
## Precedent, and the reason this is a rule rather than a preference: on
## 2026-07-30 the const still read `weekly-2026-w30` and was corrected to
## `weekly-2026-w31` BEFORE that cut (docs/rituals/gate_5_seed_blessing.md).
## A stale week number has always been treated here as a defect to fix before
## cutting, because a board key cannot be tidied afterwards -- "filtering
## standings is editing them".
const FEATURED_SEED_OVERRIDE: String = "weekly-2026-w35"

## Get weekly challenge seed (the featured/default league seed).
func get_weekly_seed() -> String:
	if not FEATURED_SEED_OVERRIDE.is_empty():
		return FEATURED_SEED_OVERRIDE
	# FIX: previously used Time.get_ticks_msec() (ms since ENGINE START, always
	# < 1 week for any real session), which froze the week at 0. Derive the week
	# from the real wall-clock date so it advances weekly.
	#
	# FIX 2026-08-24: this used to compute `(doy - 1) / 7 + 1` against
	# `time.year` and format with `%d`. That is NOT the ISO week, and it
	# disagrees with every seed ever blessed, starting 2027-01-01 and never
	# re-converging. Measured against the convention:
	#
	#     2026-07-24 .. 2026-12-25   naive == ISO        (agrees all of 2026)
	#     2027-01-01   naive weekly-2027-w1  vs ISO weekly-2026-w53
	#     2027-01-08   naive weekly-2027-w2  vs ISO weekly-2027-w01
	#     2027-02-05   naive weekly-2027-w6  vs ISO weekly-2027-w05
	#
	# Three defects firing on one date: wrong ISO YEAR (1 Jan 2027 is in ISO
	# week 53 OF 2026), wrong week NUMBER, and no zero-padding -- and
	# `weekly-2027-w1` and `weekly-2027-w01` are different strings, so they are
	# different boards. This is dead code while FEATURED_SEED_OVERRIDE is set,
	# which is exactly why it could rot unnoticed; clearing the override is a
	# one-character change that would have armed it.
	#
	# v0.19 is scheduled for Friday 2027-01-01 (accepted by Pip, 2026-08-24),
	# so the bug's fire date and a league night are the same evening.
	var time := Time.get_datetime_dict_from_system()
	return iso_week_seed(int(time.year), int(time.month), int(time.day))

## Days in a Gregorian year.
static func _days_in_year(year: int) -> int:
	var leap := year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
	return 366 if leap else 365

## Ordinal day of the year, 1-based.
static func _day_of_year(year: int, month: int, day: int) -> int:
	var days_before := [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
	var doy: int = int(days_before[month - 1]) + day
	var leap := year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
	if month > 2 and leap:
		doy += 1
	return doy

## ISO-8601 weekday, Monday=1 .. Sunday=7, via Zeller-style day-of-week.
static func _iso_weekday(year: int, month: int, day: int) -> int:
	# Sakamoto's algorithm returns 0=Sunday .. 6=Saturday.
	var t := [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
	var y := year
	if month < 3:
		y -= 1
	var dow: int = (y + y / 4 - y / 100 + y / 400 + int(t[month - 1]) + day) % 7
	# Remap 0=Sunday -> 7 so Monday=1 .. Sunday=7.
	return 7 if dow == 0 else dow

## The league seed string for a calendar date, keyed on the ISO WEEK.
##
## ISO-8601: a week belongs to the year that contains its Thursday. That is why
## 2027-01-01 is `weekly-2026-w53` and not `weekly-2027-w01` -- the week
## containing it has its Thursday in 2026. The zero-padding is load-bearing:
## a board key is an exact string, so `w1` and `w01` are different boards.
static func iso_week_seed(year: int, month: int, day: int) -> String:
	var doy := _day_of_year(year, month, day)
	var dow := _iso_weekday(year, month, day)
	# The Thursday of this week decides which ISO year the week belongs to.
	var thursday_doy: int = doy - dow + 4
	var iso_year := year
	if thursday_doy < 1:
		iso_year = year - 1
		thursday_doy += _days_in_year(iso_year)
	elif thursday_doy > _days_in_year(year):
		iso_year = year + 1
		thursday_doy -= _days_in_year(year)
	var week: int = (thursday_doy - 1) / 7 + 1
	return "weekly-%d-w%02d" % [iso_year, week]

## Get display seed (weekly or custom)
func get_display_seed() -> String:
	if game_seed.is_empty():
		return get_weekly_seed()
	return game_seed

# =============================================================================
# NUMBER FORMAT POLICY (#1087) -- the ONE place player-facing numbers are made.
# Ruling and rationale: docs/NUMBER_FORMATS.md. Short version:
#   money      -> whole dollars, grouped, NO cents ("$197,208")
#   scalars    -> whole units, grouped ("82", "3,400") -- compute/research/rep/papers
#   percent    -> one decimal, because p(doom) fractions DO carry meaning ("14.2%")
#   deltas     -> explicit sign, same base format ("+$1,200", "-3")
# A raw float must never reach the player. Anything that prints a number to a
# player MUST route through one of these; `str(value)` / "%s" on a Variant is
# how `money: 3000.0` shipped into a tooltip.
# =============================================================================

## Group an integer magnitude with thousands separators. Rounds (never truncates:
## truncation made $1,999.99 read as "$1,999", understating the balance).
func format_grouped(value: float) -> String:
	var n: int = int(round(abs(value)))
	var s := str(n)
	var out := ""
	var count := 0
	for i in range(s.length() - 1, -1, -1):
		if count > 0 and count % 3 == 0:
			out = "," + out
		out = s[i] + out
		count += 1
	return out

## Format money with comma separators (e.g., $245,000)
## Issue #436 - Player feedback: add commas to all $ references
## Issue #1087 - CENTS ARE NEVER SHOWN. A lab budget rendered to the cent
## ("$197,207.69") implies cent-grain decisions exist; none do. Rounded, not
## truncated, so the displayed figure is the nearest true dollar.
## Note: Not static because GameConfig is an autoload singleton
func format_money(amount: float) -> String:
	var sign_str := "-" if amount < 0 else ""
	return "%s$%s" % [sign_str, format_grouped(amount)]

## A money CHANGE. Always signed, so "+$1,200" and "-$238" are unambiguous.
func format_money_delta(amount: float) -> String:
	var sign_str := "+" if amount >= 0.0 else "-"
	return "%s$%s" % [sign_str, format_grouped(amount)]

## A resource scalar (compute, research, reputation, papers, staff, attention).
## Whole units: the engine carries floats, but no mechanic trades in 0.1 compute,
## so "82.0" was precision the player could not act on.
func format_scalar(value: float) -> String:
	var sign_str := "-" if value < 0 else ""
	return sign_str + format_grouped(value)

## A resource-scalar CHANGE. Always signed.
func format_scalar_delta(value: float) -> String:
	var sign_str := "+" if value >= 0.0 else "-"
	return sign_str + format_grouped(value)

## A percentage. One decimal by default -- p(doom) is the one number whose
## fraction is load-bearing (momentum is visible at sub-point grain).
##
## TIES ROUND AWAY FROM ZERO, EXPLICITLY, ON EVERY PLATFORM. The obvious
## implementation -- `"%.1f" % value` alone -- delegates to the platform's printf,
## and the two disagree on exact halves: MSVC rounds half away from zero, glibc
## rounds half to even. So `format_percent(14.25)` printed "14.3" on Pip's Windows
## machine and "14.2" on the Ubuntu CI runner, and the test asserting it passed
## locally while main's Godot Tests job was red (2026-08-05).
##
## Two players reading different doom figures from the same state is a small
## inconsistency and an unacceptable one for a game whose score is a leaderboard
## claim, so this rounds BEFORE formatting and the tie direction is a stated
## decision rather than an inherited accident. round() in Godot is half-away-from-
## zero on all platforms; the multiply/divide keeps the value on the same side of
## the boundary that printf then renders.
func format_percent(value: float, decimals: int = 1) -> String:
	var places: int = max(0, decimals)
	var factor: float = pow(10.0, places)
	var rounded: float = round(value * factor) / factor
	return ("%." + str(places) + "f%%") % rounded

## Resources whose player-facing unit is a percentage.
const _PERCENT_RESOURCES := ["doom", "p_doom", "pdoom"]

## Player-facing NAME for an internal resource key ("safety_absorption" ->
## "Safety Absorption"). Kills dict-key leakage in cost/effect tooltips.
func format_resource_name(key: String) -> String:
	match key:
		"money":
			return "Money"
		"attention":
			return "Attention"
		"doom":
			return "p(Doom)"
		"compute":
			return "Compute"
		"research":
			return "Research"
		"reputation":
			return "Reputation"
		"papers":
			return "Papers"
		_:
			return key.replace("_", " ").capitalize()

## Player-facing AMOUNT for an internal resource key. Never returns a raw float.
func format_resource_amount(key: String, value) -> String:
	var v := float(value)
	if key == "money":
		return format_money(v)
	if key in _PERCENT_RESOURCES:
		return format_percent(v)
	return format_scalar(v)

## "Money $3,000" / "Compute 12" -- the tooltip line form. Replaces
## "  %s: %s" % [key, value], which is what printed `money: 3000.0` (#1087).
func format_resource(key: String, value) -> String:
	return "%s %s" % [format_resource_name(key), format_resource_amount(key, value)]

## Signed line form for an EFFECT: "Reputation +5", "Money -$3,000".
func format_resource_delta(key: String, value) -> String:
	var v := float(value)
	if key == "money":
		return "%s %s" % [format_resource_name(key), format_money_delta(v)]
	if key in _PERCENT_RESOURCES:
		return "%s %s%s" % [format_resource_name(key), ("+" if v >= 0.0 else ""), format_percent(v)]
	return "%s %s" % [format_resource_name(key), format_scalar_delta(v)]

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

## #1029: clear the seen-it flag so the cold-open intro plays again on the next
## launch into a run. "" = never seen (the gate is an inequality against
## INTRO_VERSION). Presentation state only -- no run/ladder impact. Note the
## play_intros master gate still applies: if intros are toggled off, resetting
## this does nothing until they are re-enabled.
func reset_intro_seen() -> void:
	last_seen_intro_version = ""
	save_config()
	print("[GameConfig] Cold-open intro reset -- will replay on next launch")

## Get the current game version
func get_current_version() -> String:
	return CURRENT_VERSION

## The value that scopes leaderboard boards (ADR-0002 #5). This is the LADDER
## epoch ("L<n>"), NOT the build version -- cosmetic build bumps must not fork the
## board. EVERY board-key site (local board filename, remote submit/fetch,
## current-board select) must route through this single accessor; never rebuild
## the key from CURRENT_VERSION. Provenance sites (share line, bug report, the
## replay artifact's build tag) stay on CURRENT_VERSION -- they answer "which
## binary", not "which ruleset".
## BACKEND NOTE (separate task, do NOT attempt client-side): the PHP score API at
## api.pdoom1.com must also key boards by this ladder value, and the live
## v0.12.0 board must be aliased to L1 server-side so introducing the split does
## not fork the existing board.
func get_board_version() -> String:
	return "L" + LADDER_VERSION

## Does this run count for the leaderboard? (Pip's ruling, 2026-07-31)
##
## Scenario packs rewrite the starting state -- Sandbox Mode opens with $10,000,000
## and 1000 compute, Crisis Mode with doom already at 65. Scenario appears NOWHERE
## in the board key (see get_board_version above: seed + ladder epoch only), so
## before this gate a Sandbox run posted turns-survived to the SAME board as a
## Standard run, unmarked and silently incomparable. Exactly the hole #1058 closed
## for difficulty, one control further down the same pre-game screen.
##
## The ruling was NOT to remove the scenarios -- they stay playable. An unranked
## run is locked out of the board and the player is told so twice: at the moment
## they pick the scenario, and again on the game-over screen. Warned, not blocked.
##
## SINGLE SOURCE OF TRUTH: every board-write site must route through this. There
## is exactly one today (GameOverScreen._persist_and_submit_score); a second one
## added later that forgets this check silently reopens the hole.
##
## TWO inputs, one gate:
##   1. scenario_id -- a scenario rewrites the starting position (chosen pre-game,
##      so a single check covers it);
##   2. alpha_tools_used -- the sticky one-way Alpha Tools flag below (a dev power
##      can be used MID-RUN, so it must be a flag on the run, not a pre-game check).
func is_ranked_run() -> bool:
	if alpha_tools_used:
		return false  # sticky one-way Alpha Tools flag (decision card 2026-08-01)
	return scenario_id.strip_edges().is_empty()

# --- Alpha Tools (decision card docs/decision-cards/2026-08-01_dev-powers-nomenclature.html;
# ruled by Pip via PR #1096: "alpha-tools naming and wording settled") -----------------
#
# Player-facing name for the dev powers an alpha build ships (the F3 overlay's pokes,
# the backslash overlay's nudges / day-step / event injection). Using ANY of them makes
# the run UNRANKED via is_ranked_run() above. The flag is STICKY AND ONE-WAY per run
# (Factorio's "this save has been marked" pattern): a dev power can be used at turn 30
# after 20 honest turns, so a pre-game check cannot cover it, and turning the tool back
# off must NOT restore ranking -- otherwise the exploit is trivial and, worse,
# accidental. RUN-scoped, not build-scoped: reset ONLY at the run boundary
# (GameManager.start_new_game), carried through the SaveLoad envelope so a save/load
# cycle cannot launder it, and deliberately NOT persisted to config.cfg (that would
# taint the NEXT run).
var alpha_tools_used: bool = false
var alpha_tools_first_use_turn: int = -1

signal alpha_tools_first_used(turn: int)

# Settled wording (the card's "ready-made" section). Shown in the established NOT
# RANKED amber Color(1.0, 0.75, 0.25) -- amber already means "off the record" in two
# places; do not invent another colour.
const ALPHA_TOOLS_TOGGLE_WARNING := "[!] ALPHA TOOLS -- using any of these takes this run off the leaderboard, permanently. These tools will not exist in the finished game."
const ALPHA_TOOLS_GAME_OVER_NOTICE := "NOT RANKED: Alpha Tools were used in this run. Play without them for the board."

## Mark this run as having used an Alpha Tool. Returns true only on the FIRST use in
## the run -- callers show the mid-run warning exactly then (shown, never silent: a
## score that simply never appears is this project's signature failure, #1027).
func mark_alpha_tools_used(turn: int = -1) -> bool:
	if alpha_tools_used:
		return false  # one-way: later uses (or toggling the tool off) change nothing
	alpha_tools_used = true
	alpha_tools_first_use_turn = turn
	print("[GameConfig] ALPHA TOOLS used (turn %d) -- this run is now permanently UNRANKED" % turn)
	alpha_tools_first_used.emit(turn)
	return true

## The mid-run first-use warning -- the one place the player learns the flag is one-way.
func alpha_tools_first_use_message() -> String:
	if alpha_tools_first_use_turn >= 0:
		return "[!] This run is now UNRANKED. Alpha Tools were used on turn %d. Turning them off does not undo this." % alpha_tools_first_use_turn
	return "[!] This run is now UNRANKED. Alpha Tools were used. Turning them off does not undo this."

## RUN-boundary reset. Legitimate callers: GameManager.start_new_game() (fresh run
## starts clean) and load_saved_game (which immediately restores the SAVED run's own
## flag from the envelope). Nothing player-reachable may call this mid-run -- that
## would un-stick the one-way flag.
func reset_alpha_tools_flag() -> void:
	alpha_tools_used = false
	alpha_tools_first_use_turn = -1

## Should the first-launch welcome/help overlay be shown? (issue #720)
## True only on a genuine first launch (no games played yet), when it has never
## been shown before, and while gameplay hints are enabled. The welcome_seen gate
## makes this show-once even if the player quits before finishing a game.
func should_show_welcome() -> bool:
	return show_hints and games_played == 0 and not welcome_seen

## Mark the welcome overlay as shown so it never re-appears (issue #720).
func mark_welcome_seen() -> void:
	if welcome_seen:
		return
	welcome_seen = true
	save_config()
	print("[GameConfig] Welcome overlay marked as seen")

## Debug print current configuration
func print_config() -> void:
	print("[GameConfig] === Current Configuration ===")
	print("  Player: %s" % player_name)
	print("  Lab: %s" % lab_name)
	print("  Seed: %s" % get_display_seed())
	print("  Difficulty: %s (stored preference: %s)" % [get_effective_difficulty_string(), get_difficulty_string()])
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

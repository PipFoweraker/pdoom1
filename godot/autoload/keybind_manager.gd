extends Node
## Keybind Manager - Modular keybinding system with profile support
## Inspired by StarCraft 2 keybinding UX

# Keybind categories
enum Category {
	GAMEPLAY,
	DEBUG,
	ADMIN,
	UI,
	SCREENSHOT
}

# Default keybinds (customizable)
var keybinds: Dictionary = {
	# Screenshots & Logging
	"screenshot": {"key": KEY_BRACKETLEFT, "category": Category.SCREENSHOT, "description": "Take Screenshot"},
	# Moved off backslash (KEY_F12) so backslash is free for the DEV MODE overlay (owner request).
	"export_log": {"key": KEY_F12, "category": Category.ADMIN, "description": "Export Game Log"},

	# Debug & Admin
	"debug_overlay": {"key": KEY_F3, "category": Category.DEBUG, "description": "Toggle Debug Overlay (User)"},
	# Backslash toggles the full DEV MODE overlay (state readout + dev controls). Gated on
	# BuildInfo.DEV_BUILD by the overlay itself. Reclaimed backslash from export_log/bug_reporter.
	"dev_mode": {"key": KEY_BACKSLASH, "category": Category.DEBUG, "description": "Toggle Dev Mode Overlay"},
	# Playtest flight recorder (WORKSHOP_2_BACKLOG "Playtest deep-dive protocol"): one press
	# dumps a screenshot + state snapshot + marker note. Gated on BuildInfo.DEV_BUILD by
	# FlightRecorder itself, same pattern as dev_mode. Rebound from F9 to F6 (Pip playtest:
	# F9 collides with his Nvidia overlay hotkey). F6 is otherwise unused.
	"flight_recorder": {"key": KEY_F6, "category": Category.DEBUG, "description": "Flight Recorder Capture (screenshot + state + note)"},
	# UI evolution capture rail (Pip's "it went from this... to this..." ask, 2026-07-27):
	# one silent press drops a screenshot + one-line context (scene/version/turn) for later
	# devblog/anniversary montages. Gated on BuildInfo.is_dev_build() by UIEvolutionRecorder
	# itself, same pattern as flight_recorder. F7 is otherwise unused.
	"ui_evolution_shot": {"key": KEY_F7, "category": Category.DEBUG, "description": "UI Evolution Capture (screenshot + context line)"},
	"admin_mode": {"key": KEY_BRACKETRIGHT, "category": Category.ADMIN, "description": "Toggle Admin Mode"},

	# Gameplay
	"end_turn": {"key": KEY_SPACE, "category": Category.GAMEPLAY, "description": "End Turn"},
	"undo_action": {"key": KEY_Z, "category": Category.GAMEPLAY, "description": "Undo Last Action"},
	"clear_queue": {"key": KEY_C, "category": Category.GAMEPLAY, "description": "Clear Action Queue"},
	# "cancel" (was KEY_ESCAPE) DELETED 2026-08-04 (#602 navigation audit). Nothing read
	# this bind: ESC is matched as a raw KEY_ESCAPE in ~10 handlers and funnelled through
	# ModalStack.handle_escape(). Listing it in the rebind screen promised a rebind that
	# could never take. ESC is a RESERVED key by design -- see RESERVED_KEYS below.

	# UI Navigation
	# "next_tab"/"prev_tab" (were TAB / Shift+TAB) DELETED 2026-08-04 (#602 navigation
	# audit). Nothing has ever handled them -- there is no tab bar; TabManager holds two
	# views (main + Employee) reached by a visible button and left by ESC. They must NOT
	# be wired up now either: TAB is Godot's GUI focus-traversal key, and a global handler
	# that swallowed it would stop the player moving between the bug-report form's fields
	# -- the same class of defect as #575. TAB is RESERVED; see RESERVED_KEYS below.
	# Moved off backslash to N (N already opened the bug reporter) -- backslash is now DEV MODE.
	"bug_reporter": {"key": KEY_N, "category": Category.UI, "description": "Open Bug Reporter"},
	# "employee_tab": {"key": KEY_E, "category": Category.UI, "description": "Employee Screen"},  # DISABLED: moving to main UI
	"settings": {"key": KEY_F10, "category": Category.UI, "description": "Settings Menu"},
	"open_ledger": {"key": KEY_L, "category": Category.UI, "description": "Open Liability Ledger"},

	# Quick Menu Access (configurable shortcuts for common menus)
	"menu_hire": {"key": KEY_H, "category": Category.GAMEPLAY, "description": "Open Hiring Menu"},
	"menu_fundraise": {"key": KEY_F, "category": Category.GAMEPLAY, "description": "Open Fundraising Menu"},
	# "menu_research" (was KEY_R) DELETED 2026-08-04 (#602 navigation audit). There is no
	# research SUBMENU -- safety_research / capability_research / publish_paper are direct
	# action-bar items -- so nothing ever handled this bind. It still appeared in the
	# keybind screen, which meant the game ADVERTISED a key that did nothing (audit
	# principle P4: no advertised key is inert). Worse, R is also dialog choice 4, so the
	# rebind screen implied R was spoken for when it was not.
	"menu_publicity": {"key": KEY_P, "category": Category.GAMEPLAY, "description": "Open Publicity Menu"},
	"menu_travel": {"key": KEY_T, "category": Category.GAMEPLAY, "description": "Open Travel Menu"},

	# Actions (Number keys 1-9 for quick action access)
	"action_1": {"key": KEY_1, "category": Category.GAMEPLAY, "description": "Trigger Action 1"},
	"action_2": {"key": KEY_2, "category": Category.GAMEPLAY, "description": "Trigger Action 2"},
	"action_3": {"key": KEY_3, "category": Category.GAMEPLAY, "description": "Trigger Action 3"},
	"action_4": {"key": KEY_4, "category": Category.GAMEPLAY, "description": "Trigger Action 4"},
	"action_5": {"key": KEY_5, "category": Category.GAMEPLAY, "description": "Trigger Action 5"},
	"action_6": {"key": KEY_6, "category": Category.GAMEPLAY, "description": "Trigger Action 6"},
	"action_7": {"key": KEY_7, "category": Category.GAMEPLAY, "description": "Trigger Action 7"},
	"action_8": {"key": KEY_8, "category": Category.GAMEPLAY, "description": "Trigger Action 8"},
	"action_9": {"key": KEY_9, "category": Category.GAMEPLAY, "description": "Trigger Action 9"},

	# Additional Gameplay shortcuts
	# Description wording is #1116's (the "AP" -> "Attention" copy pass); the bind itself
	# is what #602 needed -- ENTER read through KeybindManager instead of a raw keycode.
	"commit_plan": {"key": KEY_ENTER, "category": Category.GAMEPLAY, "description": "Commit Plan & Reserve Attention"},
	# View toggle (PLAN <-> WATCH). Was a hardcoded KEY_V in main_ui._input and therefore
	# invisible to the rebind screen -- #602 principle P4 cuts both ways: an advertised key
	# must work, and a working key must be advertised.
	"toggle_view": {"key": KEY_V, "category": Category.UI, "description": "Toggle PLAN / WATCH View"},
}

## Keys the game answers to that are deliberately NOT rebindable, with the reason. This
## is the honest half of #602 principle P4 ("no advertised key is inert, no working key
## is unadvertised"): a key belongs in `keybinds` above OR here, never in neither and
## never in both. Documented rather than silently absent, so the next audit can see the
## ruling instead of rediscovering the gap.
const RESERVED_KEYS := {
	"escape": "ESC is the universal back/close key (audit principle P5). It routes through "
		+ "ModalStack.handle_escape() and every screen's own back handler; allowing a rebind "
		+ "would let a player strand themselves in a modal with no way out.",
	"tab": "TAB / Shift+TAB belong to Godot's GUI focus traversal. Claiming them globally "
		+ "would break moving between fields in the bug-report form (#575's defect class), "
		+ "so no game action may bind them.",
	"choice_keys": "Q/W/E/R/A/S/D/F/Z (and 1-9 as an alias) select modal choices. They are "
		+ "positional labels rendered onto the buttons themselves (DialogKeys), not "
		+ "standalone actions, so there is nothing stable to rebind.",
}

# Active profile
var current_profile: String = "default"
var profiles: Dictionary = {}  # profile_name -> keybind dict

# Config file
const CONFIG_PATH = "user://keybinds.cfg"
const KEYBINDS_CONFIG_VERSION = 6  # bump when default binds change; stale saved configs refresh to defaults
var config = ConfigFile.new()

# Signals
signal keybind_changed(action: String, new_key: int)
signal profile_loaded(profile_name: String)
signal screenshot_requested
signal log_export_requested
signal admin_mode_toggled
signal debug_overlay_toggled
signal dev_mode_toggled
signal flight_recorder_requested
signal ui_evolution_shot_requested

func _ready():
	load_keybinds()
	print("[KeybindManager] Loaded profile: %s" % current_profile)

## Load keybinds from config file
func load_keybinds():
	var err = config.load(CONFIG_PATH)

	if err == OK:
		# Defaults changed since this config was written? Refresh from defaults. Otherwise a
		# stale saved bind silently overrides the new default (e.g. the F3 debug overlay was
		# stuck on the old '~' bind -- issue #564). In beta this resets custom rebinds on a
		# default change; the alternative is defaults that never take effect.
		var saved_version = config.get_value("settings", "config_version", 1)
		if saved_version < KEYBINDS_CONFIG_VERSION:
			current_profile = config.get_value("settings", "current_profile", "default")
			var stale_profiles = config.get_value("settings", "profiles", ["default"])
			for profile in stale_profiles:
				profiles[profile] = keybinds.duplicate(true)
			if not profiles.has(current_profile):
				profiles[current_profile] = keybinds.duplicate(true)
			apply_profile(current_profile)  # applies defaults + saves with the new version
			return

		# Load current profile
		current_profile = config.get_value("settings", "current_profile", "default")

		# Load all profiles
		var profile_list = config.get_value("settings", "profiles", ["default"])
		for profile in profile_list:
			# Start with default keybinds, then override with saved values
			profiles[profile] = keybinds.duplicate(true)

			# Only load saved values if the section exists
			if config.has_section(profile):
				for action in keybinds.keys():
					# Use has_section_key to avoid warnings for missing keys
					if config.has_section_key(profile, action):
						var saved_key = config.get_value(profile, action)
						profiles[profile][action] = saved_key

		# Apply current profile
		if profiles.has(current_profile):
			apply_profile(current_profile)
		else:
			# Profile doesn't exist, create it
			profiles[current_profile] = keybinds.duplicate(true)
			save_keybinds()
	else:
		# First run - create default profile
		profiles["default"] = keybinds.duplicate(true)
		save_keybinds()

## Save keybinds to config file
func save_keybinds():
	config.set_value("settings", "config_version", KEYBINDS_CONFIG_VERSION)
	config.set_value("settings", "current_profile", current_profile)
	config.set_value("settings", "profiles", profiles.keys())

	# Save all profiles
	for profile_name in profiles.keys():
		for action in profiles[profile_name].keys():
			config.set_value(profile_name, action, profiles[profile_name][action])

	config.save(CONFIG_PATH)

## Apply a keybind profile
func apply_profile(profile_name: String):
	if not profiles.has(profile_name):
		push_error("Profile '%s' not found" % profile_name)
		return

	current_profile = profile_name
	keybinds = profiles[profile_name].duplicate(true)
	profile_loaded.emit(profile_name)
	save_keybinds()

## Create a new profile based on current keybinds
func create_profile(profile_name: String):
	if profiles.has(profile_name):
		push_warning("Profile '%s' already exists" % profile_name)
		return false

	profiles[profile_name] = keybinds.duplicate(true)
	save_keybinds()
	return true

## Delete a profile
func delete_profile(profile_name: String):
	if profile_name == "default":
		push_error("Cannot delete default profile")
		return false

	if not profiles.has(profile_name):
		return false

	profiles.erase(profile_name)
	if current_profile == profile_name:
		apply_profile("default")
	else:
		save_keybinds()
	return true

## Rebind a key
func rebind(action: String, new_key: int, modifier_shift: bool = false, modifier_ctrl: bool = false, modifier_alt: bool = false):
	if not keybinds.has(action):
		push_error("Action '%s' not found" % action)
		return false

	keybinds[action]["key"] = new_key
	keybinds[action]["shift"] = modifier_shift
	keybinds[action]["ctrl"] = modifier_ctrl
	keybinds[action]["alt"] = modifier_alt

	# Update current profile
	profiles[current_profile] = keybinds.duplicate(true)

	keybind_changed.emit(action, new_key)
	save_keybinds()
	return true

## Check if a key event matches an action
func is_action_pressed(event: InputEvent, action: String) -> bool:
	if not event is InputEventKey:
		return false

	if not keybinds.has(action):
		return false

	var bind = keybinds[action]

	# Check key match
	if event.keycode != bind["key"]:
		return false

	# Check modifiers
	if bind.get("shift", false) != event.shift_pressed:
		return false
	if bind.get("ctrl", false) != event.ctrl_pressed:
		return false
	if bind.get("alt", false) != event.alt_pressed:
		return false

	return event.pressed and not event.echo

## Get human-readable key name
func get_key_name(action: String) -> String:
	if not keybinds.has(action):
		return "Unbound"

	var bind = keybinds[action]
	var key_name = OS.get_keycode_string(bind["key"])

	var modifiers = []
	if bind.get("ctrl", false):
		modifiers.append("Ctrl")
	if bind.get("shift", false):
		modifiers.append("Shift")
	if bind.get("alt", false):
		modifiers.append("Alt")

	if modifiers.size() > 0:
		return "%s + %s" % ["+".join(modifiers), key_name]
	return key_name

## Get all actions in a category
func get_actions_by_category(category: Category) -> Array:
	var actions = []
	for action in keybinds.keys():
		if keybinds[action]["category"] == category:
			actions.append(action)
	return actions

## True if a text-entry widget (LineEdit/TextEdit) currently owns GUI focus.
## Global keybinds must yield to text fields so typed characters reach the field
## instead of firing shortcuts (issues #575, #567). Used as a gate by this
## autoload's _input and by MainUI's shortcut handling.
func is_text_input_focused() -> bool:
	var vp := get_viewport()
	if vp == null:
		return false
	var focus_owner := vp.gui_get_focus_owner()
	return focus_owner is LineEdit or focus_owner is TextEdit

## Process input for global keybinds
func _input(event: InputEvent):
	if not event is InputEventKey:
		return

	# Yield to focused text fields -- never steal characters being typed (#575).
	# A bug-report form or any LineEdit/TextEdit must receive letters like 'n'/'t'
	# rather than having them trigger global shortcuts.
	if is_text_input_focused():
		return

	# Screenshot
	if is_action_pressed(event, "screenshot"):
		screenshot_requested.emit()
		get_viewport().set_input_as_handled()

	# Export log
	elif is_action_pressed(event, "export_log"):
		log_export_requested.emit()
		get_viewport().set_input_as_handled()

	# Debug overlay (user mode)
	elif is_action_pressed(event, "debug_overlay"):
		debug_overlay_toggled.emit()
		get_viewport().set_input_as_handled()

	# Dev mode overlay (backslash) -- full state readout + dev controls (dev builds only)
	elif is_action_pressed(event, "dev_mode"):
		dev_mode_toggled.emit()
		get_viewport().set_input_as_handled()

	# Flight recorder (F6) -- screenshot + state snapshot + marker note in one press
	# (dev builds only; FlightRecorder itself gates on BuildInfo.is_dev_build()).
	elif is_action_pressed(event, "flight_recorder"):
		flight_recorder_requested.emit()
		get_viewport().set_input_as_handled()

	# UI evolution capture (F7) -- screenshot + one-line context, no popup
	# (dev builds only; UIEvolutionRecorder itself gates on BuildInfo.is_dev_build()).
	elif is_action_pressed(event, "ui_evolution_shot"):
		ui_evolution_shot_requested.emit()
		get_viewport().set_input_as_handled()

	# Admin mode
	elif is_action_pressed(event, "admin_mode"):
		admin_mode_toggled.emit()
		get_viewport().set_input_as_handled()

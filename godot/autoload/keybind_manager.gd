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
	"export_log": {"key": KEY_BACKSLASH, "category": Category.ADMIN, "description": "Export Game Log"},

	# Debug & Admin
	"debug_overlay": {"key": KEY_ASCIITILDE, "category": Category.DEBUG, "description": "Toggle Debug Overlay (User)"},
	"admin_mode": {"key": KEY_BRACKETRIGHT, "category": Category.ADMIN, "description": "Toggle Admin Mode"},

	# Gameplay
	"end_turn": {"key": KEY_SPACE, "category": Category.GAMEPLAY, "description": "End Turn"},
	"clear_queue": {"key": KEY_C, "category": Category.GAMEPLAY, "description": "Clear Action Queue"},
	"cancel": {"key": KEY_ESCAPE, "category": Category.GAMEPLAY, "description": "Cancel/Back"},

	# UI Navigation
	"next_tab": {"key": KEY_TAB, "category": Category.UI, "description": "Next Tab"},
	"prev_tab": {"key": KEY_TAB, "shift": true, "category": Category.UI, "description": "Previous Tab"},
	"bug_reporter": {"key": KEY_F8, "category": Category.UI, "description": "Open Bug Reporter"},
	"employee_tab": {"key": KEY_E, "category": Category.UI, "description": "Employee Screen"},
	"settings": {"key": KEY_F10, "category": Category.UI, "description": "Settings Menu"},

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
	"skip_turn": {"key": KEY_ENTER, "category": Category.GAMEPLAY, "description": "Skip Turn"},
}

# Active profile
var current_profile: String = "default"
var profiles: Dictionary = {}  # profile_name -> keybind dict

# Config file
const CONFIG_PATH = "user://keybinds.cfg"
var config = ConfigFile.new()

# Signals
signal keybind_changed(action: String, new_key: int)
signal profile_loaded(profile_name: String)
signal screenshot_requested
signal log_export_requested
signal admin_mode_toggled
signal debug_overlay_toggled

func _ready():
	load_keybinds()
	print("[KeybindManager] Loaded profile: %s" % current_profile)

## Load keybinds from config file
func load_keybinds():
	var err = config.load(CONFIG_PATH)

	if err == OK:
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

## Process input for global keybinds
func _input(event: InputEvent):
	if not event is InputEventKey:
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

	# Admin mode
	elif is_action_pressed(event, "admin_mode"):
		admin_mode_toggled.emit()
		get_viewport().set_input_as_handled()

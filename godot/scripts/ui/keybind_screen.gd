extends Control
## Keybinding Configuration Screen - SC2-style keybind management

# UI References
@onready var profile_dropdown = $MarginContainer/VBoxContainer/Header/ProfileSection/ProfileDropdown
@onready var new_profile_button = $MarginContainer/VBoxContainer/Header/ProfileSection/NewProfileButton
@onready var delete_profile_button = $MarginContainer/VBoxContainer/Header/ProfileSection/DeleteProfileButton
@onready var keybind_container = $MarginContainer/VBoxContainer/ScrollContainer/KeybindContainer
@onready var back_button = $MarginContainer/VBoxContainer/Footer/BackButton
@onready var reset_button = $MarginContainer/VBoxContainer/Footer/ResetButton

# State
var waiting_for_key: String = ""  # Action currently being rebound
var waiting_button: Button = null

# Category colors
const CATEGORY_COLORS = {
	KeybindManager.Category.GAMEPLAY: Color.LIGHT_BLUE,
	KeybindManager.Category.DEBUG: Color.YELLOW,
	KeybindManager.Category.ADMIN: Color.ORANGE,
	KeybindManager.Category.UI: Color.LIGHT_GREEN,
	KeybindManager.Category.SCREENSHOT: Color.PINK
}

func _ready():
	_populate_profile_dropdown()
	_build_keybind_list()

	# Connect signals
	profile_dropdown.item_selected.connect(_on_profile_selected)
	new_profile_button.pressed.connect(_on_new_profile_pressed)
	delete_profile_button.pressed.connect(_on_delete_profile_pressed)
	back_button.pressed.connect(_on_back_pressed)
	reset_button.pressed.connect(_on_reset_pressed)

	KeybindManager.keybind_changed.connect(_on_keybind_changed)

func _populate_profile_dropdown():
	profile_dropdown.clear()

	var profiles = KeybindManager.profiles.keys()
	profiles.sort()

	for i in range(profiles.size()):
		var profile_name = profiles[i]
		profile_dropdown.add_item(profile_name)

		if profile_name == KeybindManager.current_profile:
			profile_dropdown.selected = i

func _build_keybind_list():
	# Clear existing entries
	for child in keybind_container.get_children():
		child.queue_free()

	# Group by category
	var categories = {}
	for action in KeybindManager.keybinds.keys():
		var category = KeybindManager.keybinds[action]["category"]
		if not categories.has(category):
			categories[category] = []
		categories[category].append(action)

	# Build UI for each category
	var category_order = [
		KeybindManager.Category.GAMEPLAY,
		KeybindManager.Category.UI,
		KeybindManager.Category.DEBUG,
		KeybindManager.Category.SCREENSHOT,
		KeybindManager.Category.ADMIN
	]

	for category in category_order:
		if not categories.has(category):
			continue

		# Category header
		var header = _create_category_header(category)
		keybind_container.add_child(header)

		# Sort actions alphabetically
		categories[category].sort()

		# Add each keybind row
		for action in categories[category]:
			var row = _create_keybind_row(action)
			keybind_container.add_child(row)

		# Spacer
		var spacer = Control.new()
		spacer.custom_minimum_size = Vector2(0, 10)
		keybind_container.add_child(spacer)

func _create_category_header(category: KeybindManager.Category) -> PanelContainer:
	var panel = PanelContainer.new()

	var style = StyleBoxFlat.new()
	style.bg_color = CATEGORY_COLORS.get(category, Color.GRAY).darkened(0.5)
	panel.add_theme_stylebox_override("panel", style)

	var label = Label.new()
	label.text = "  " + KeybindManager.Category.keys()[category]
	label.add_theme_font_size_override("font_size", 16)
	label.add_theme_color_override("font_color", Color.WHITE)

	panel.add_child(label)
	return panel

func _create_keybind_row(action: String) -> HBoxContainer:
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 20)

	# Description
	var desc_label = Label.new()
	desc_label.text = KeybindManager.keybinds[action]["description"]
	desc_label.custom_minimum_size = Vector2(300, 0)
	desc_label.add_theme_font_size_override("font_size", 14)
	row.add_child(desc_label)

	# Current key button
	var key_button = Button.new()
	key_button.text = KeybindManager.get_key_name(action)
	key_button.custom_minimum_size = Vector2(150, 0)
	key_button.pressed.connect(_on_rebind_pressed.bind(action, key_button))
	row.add_child(key_button)

	# Clear button
	var clear_button = Button.new()
	clear_button.text = "Clear"
	clear_button.custom_minimum_size = Vector2(80, 0)
	clear_button.pressed.connect(_on_clear_pressed.bind(action))
	row.add_child(clear_button)

	return row

func _on_rebind_pressed(action: String, button: Button):
	if waiting_for_key != "":
		# Cancel previous rebind
		if waiting_button:
			waiting_button.text = KeybindManager.get_key_name(waiting_for_key)

	waiting_for_key = action
	waiting_button = button
	button.text = "Press any key..."
	button.add_theme_color_override("font_color", Color.YELLOW)

func _on_clear_pressed(action: String):
	# Set to an unmapped key
	KeybindManager.rebind(action, KEY_NONE)
	_build_keybind_list()

func _input(event: InputEvent):
	if waiting_for_key == "" or not event is InputEventKey:
		return

	if not event.pressed or event.echo:
		return

	# Capture the key
	var new_key = event.keycode
	var shift = event.shift_pressed
	var ctrl = event.ctrl_pressed
	var alt = event.alt_pressed

	# Check for conflicts
	var conflict = _find_key_conflict(new_key, shift, ctrl, alt)
	if conflict != "":
		_show_conflict_warning(conflict)

	# Apply rebind
	KeybindManager.rebind(waiting_for_key, new_key, shift, ctrl, alt)

	# Reset state
	if waiting_button:
		waiting_button.text = KeybindManager.get_key_name(waiting_for_key)
		waiting_button.remove_theme_color_override("font_color")

	waiting_for_key = ""
	waiting_button = null

	# Rebuild to show new binding
	_build_keybind_list()

	# Mark input as handled
	get_viewport().set_input_as_handled()

func _find_key_conflict(key: int, shift: bool, ctrl: bool, alt: bool) -> String:
	for action in KeybindManager.keybinds.keys():
		if action == waiting_for_key:
			continue

		var bind = KeybindManager.keybinds[action]
		if bind["key"] == key:
			if bind.get("shift", false) == shift and bind.get("ctrl", false) == ctrl and bind.get("alt", false) == alt:
				return action

	return ""

func _show_conflict_warning(conflicting_action: String):
	var desc = KeybindManager.keybinds[conflicting_action]["description"]
	print("[Keybinds] Warning: Key conflicts with '%s'" % desc)

	# Could add a popup dialog here

func _on_keybind_changed(action: String, new_key: int):
	print("[Keybinds] %s rebound to %s" % [action, OS.get_keycode_string(new_key)])

func _on_profile_selected(index: int):
	var profile_name = profile_dropdown.get_item_text(index)
	KeybindManager.apply_profile(profile_name)
	_build_keybind_list()

func _on_new_profile_pressed():
	# Simple dialog to get profile name
	var dialog = AcceptDialog.new()
	dialog.title = "New Profile"
	dialog.dialog_text = "Enter profile name:"

	var line_edit = LineEdit.new()
	line_edit.placeholder_text = "my_profile"
	dialog.add_child(line_edit)

	add_child(dialog)
	dialog.popup_centered()

	dialog.confirmed.connect(func():
		var new_name = line_edit.text.strip_edges()
		if new_name != "":
			if KeybindManager.create_profile(new_name):
				_populate_profile_dropdown()
				KeybindManager.apply_profile(new_name)
				_build_keybind_list()
		dialog.queue_free()
	)

func _on_delete_profile_pressed():
	if KeybindManager.current_profile == "default":
		print("[Keybinds] Cannot delete default profile")
		return

	var dialog = ConfirmationDialog.new()
	dialog.title = "Delete Profile"
	dialog.dialog_text = "Delete profile '%s'?" % KeybindManager.current_profile

	add_child(dialog)
	dialog.popup_centered()

	dialog.confirmed.connect(func():
		if KeybindManager.delete_profile(KeybindManager.current_profile):
			_populate_profile_dropdown()
			_build_keybind_list()
		dialog.queue_free()
	)

func _on_reset_pressed():
	# Reset current profile to defaults
	var dialog = ConfirmationDialog.new()
	dialog.title = "Reset Keybinds"
	dialog.dialog_text = "Reset all keybinds to default?"

	add_child(dialog)
	dialog.popup_centered()

	dialog.confirmed.connect(func():
		# Delete and recreate current profile
		var current = KeybindManager.current_profile
		KeybindManager.delete_profile(current)
		KeybindManager.create_profile(current)
		KeybindManager.apply_profile(current)
		_build_keybind_list()
		dialog.queue_free()
	)

func _on_back_pressed():
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

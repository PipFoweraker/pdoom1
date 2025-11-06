extends Control
## Welcome/Setup Screen - Matches pygame UI style

@onready var title_label = $VBox/Title
@onready var subtitle_label = $VBox/Subtitle
@onready var menu_container = $VBox/MenuContainer
@onready var launch_lab_button = $VBox/MenuContainer/LaunchLabButton
@onready var custom_seed_button = $VBox/MenuContainer/CustomSeedButton
@onready var settings_button = $VBox/MenuContainer/SettingsButton
@onready var guide_button = $VBox/MenuContainer/GuideButton
@onready var keybindings_button = $VBox/MenuContainer/KeybindingsButton
@onready var leaderboard_button = $VBox/MenuContainer/LeaderboardButton
@onready var exit_button = $VBox/MenuContainer/ExitButton

var menu_buttons: Array[Button] = []
var selected_index: int = 0

func _ready():
	print("[WelcomeScreen] Initializing...")

	# Collect all menu buttons in order
	menu_buttons = [
		launch_lab_button,
		custom_seed_button,
		settings_button,
		guide_button,
		keybindings_button,
		leaderboard_button,
		exit_button
	]

	# Connect button signals
	launch_lab_button.pressed.connect(_on_launch_lab_pressed)
	custom_seed_button.pressed.connect(_on_custom_seed_pressed)
	settings_button.pressed.connect(_on_settings_pressed)
	guide_button.pressed.connect(_on_guide_pressed)
	keybindings_button.pressed.connect(_on_keybindings_pressed)
	leaderboard_button.pressed.connect(_on_leaderboard_pressed)
	exit_button.pressed.connect(_on_exit_pressed)

	# Enable input processing for keyboard navigation
	set_process_input(true)

	# Focus first button
	_update_button_focus()

func _input(event: InputEvent):
	"""Handle keyboard navigation matching pygame behavior"""
	if event is InputEventKey and event.pressed and not event.echo:
		# Arrow keys for navigation
		if event.keycode == KEY_UP or event.keycode == KEY_W:
			selected_index = (selected_index - 1) % menu_buttons.size()
			_update_button_focus()
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		elif event.keycode == KEY_DOWN or event.keycode == KEY_S:
			selected_index = (selected_index + 1) % menu_buttons.size()
			_update_button_focus()
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		# Enter or Space to activate selected button
		elif event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			menu_buttons[selected_index].emit_signal("pressed")
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		# Number keys 1-5 for direct selection
		elif event.keycode >= KEY_1 and event.keycode <= KEY_5:
			var index = event.keycode - KEY_1
			if index < menu_buttons.size():
				selected_index = index
				menu_buttons[selected_index].emit_signal("pressed")
				var viewport = get_viewport()
				if viewport:
					viewport.set_input_as_handled()

func _update_button_focus():
	"""Update visual focus indicator on buttons"""
	for i in range(menu_buttons.size()):
		if i == selected_index:
			menu_buttons[i].grab_focus()
			# Bright blue with white border when selected
			menu_buttons[i].modulate = Color(0.6, 0.8, 1.0)
		else:
			# Dark blue normal state
			menu_buttons[i].modulate = Color(0.3, 0.4, 0.6)

func _on_launch_lab_pressed():
	print("[WelcomeScreen] Launching lab with default seed...")
	# Set default config mode and show confirmation screen
	GameConfig.config_mode = "default"
	GameConfig.seed = ""  # Use weekly seed
	GameConfig.difficulty = 1  # Standard difficulty
	var err = get_tree().change_scene_to_file("res://scenes/config_confirmation.tscn")
	if err != OK:
		print("[WelcomeScreen] ERROR: Failed to load config confirmation scene, error code: ", err)
		push_error("Failed to load config_confirmation.tscn")

func _on_custom_seed_pressed():
	print("[WelcomeScreen] Opening pre-game setup...")
	# Show pre-game setup dialog
	var err = get_tree().change_scene_to_file("res://scenes/pregame_setup.tscn")
	if err != OK:
		print("[WelcomeScreen] ERROR: Failed to load pregame setup, error code: ", err)

func _on_settings_pressed():
	print("[WelcomeScreen] Opening settings menu...")
	var err = get_tree().change_scene_to_file("res://scenes/settings_menu.tscn")
	if err != OK:
		print("[WelcomeScreen] ERROR: Failed to load settings, error code: ", err)

func _on_guide_pressed():
	print("[WelcomeScreen] Opening player guide...")
	var err = get_tree().change_scene_to_file("res://scenes/player_guide.tscn")
	if err != OK:
		print("[WelcomeScreen] ERROR: Failed to load guide, error code: ", err)

func _on_keybindings_pressed():
	print("[WelcomeScreen] Opening keybindings...")
	get_tree().change_scene_to_file("res://scenes/keybind_screen.tscn")

func _on_leaderboard_pressed():
	print("[WelcomeScreen] Opening leaderboard...")
	get_tree().change_scene_to_file("res://scenes/leaderboard_screen.tscn")

func _on_exit_pressed():
	print("[WelcomeScreen] Exiting game...")
	get_tree().quit()

func _show_placeholder_dialog(title: String, message: String):
	"""Show a simple placeholder dialog for unimplemented features"""
	var dialog = AcceptDialog.new()
	dialog.title = title
	dialog.dialog_text = message
	dialog.size = Vector2(400, 250)
	add_child(dialog)
	dialog.popup_centered()

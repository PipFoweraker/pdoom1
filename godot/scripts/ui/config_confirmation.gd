extends Control
## Configuration Confirmation Screen - Shows locked-in game settings before launch
## Used for default pathway to show what options are configured

# UI References
@onready var player_name_label = $Panel/VBox/FieldsContainer/PlayerNameRow/ValueLabel
@onready var lab_name_label = $Panel/VBox/FieldsContainer/LabNameRow/ValueLabel
@onready var seed_label = $Panel/VBox/FieldsContainer/SeedRow/ValueLabel
@onready var difficulty_label = $Panel/VBox/FieldsContainer/DifficultyRow/ValueLabel
@onready var funding_label = $Panel/VBox/FieldsContainer/FundingRow/ValueLabel
@onready var launch_button = $Panel/VBox/ButtonRow/LaunchButton
@onready var back_button = $Panel/VBox/ButtonRow/BackButton
@onready var customize_button = $Panel/VBox/ButtonRow/CustomizeButton

func _ready():
	print("[ConfigConfirmation] Initializing with mode: %s" % GameConfig.config_mode)

	# Load configuration from GameConfig
	_display_configuration()

	# Focus launch button
	launch_button.grab_focus()

func _display_configuration():
	"""Display all configuration options, greying out locked ones"""

	# Player name (always editable via customize button)
	player_name_label.text = GameConfig.player_name if GameConfig.player_name != "" else "Researcher"

	# Lab name (always editable via customize button)
	lab_name_label.text = GameConfig.lab_name if GameConfig.lab_name != "" else "AI Safety Lab"

	# Seed - LOCKED for default pathway
	if GameConfig.config_mode == "default":
		var weekly = GameConfig.get_weekly_seed()
		seed_label.text = "%s (Weekly Challenge)" % weekly
		seed_label.modulate = Color(0.5, 0.5, 0.5)  # Grey out
	else:
		seed_label.text = GameConfig.get_display_seed()
		seed_label.modulate = Color(1, 1, 1)  # Normal color

	# Difficulty - LOCKED for default pathway
	if GameConfig.config_mode == "default":
		difficulty_label.text = "Standard (Regulatory)"
		difficulty_label.modulate = Color(0.5, 0.5, 0.5)  # Grey out
		GameConfig.difficulty = 1  # Force standard difficulty
	else:
		difficulty_label.text = ["Easy (Conservative)", "Standard (Regulatory)", "Hard (Aggressive)"][GameConfig.difficulty]
		difficulty_label.modulate = Color(1, 1, 1)  # Normal color

	# Starting funding - Always $245,000 (from game_state.gd:5)
	funding_label.text = GameConfig.format_money(245000)
	funding_label.modulate = Color(0.5, 0.5, 0.5)  # Grey out (always locked)

func _on_launch_pressed():
	"""Launch the game with confirmed settings"""
	print("[ConfigConfirmation] Launching game...")

	# Ensure config mode settings are applied
	if GameConfig.config_mode == "default":
		GameConfig.seed = ""  # Use weekly seed
		GameConfig.difficulty = 1  # Force standard difficulty

	# Save configuration
	GameConfig.save_config()

	# Print configuration for debugging
	GameConfig.print_config()

	# Increment games played counter
	GameConfig.increment_games_played()

	# Mark game as active
	GameConfig.current_game_active = true

	# Transition to main game
	get_tree().change_scene_to_file("res://scenes/main.tscn")

func _on_back_pressed():
	"""Return to welcome screen"""
	print("[ConfigConfirmation] Returning to welcome screen")
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _on_customize_pressed():
	"""Go to full pregame setup to customize all options"""
	print("[ConfigConfirmation] Opening pregame setup for customization")
	get_tree().change_scene_to_file("res://scenes/pregame_setup.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()
		elif event.keycode == KEY_ENTER:
			if not launch_button.disabled:
				_on_launch_pressed()

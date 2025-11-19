extends Control
## Pre-Game Setup Screen - Configure player name, lab name, seed, and difficulty using GameConfig

# UI References
@onready var player_name_input = $Panel/VBox/FieldsContainer/PlayerNameRow/LineEdit
@onready var lab_name_input = $Panel/VBox/FieldsContainer/LabNameRow/LineEdit
@onready var seed_input = $Panel/VBox/FieldsContainer/SeedRow/HBox/LineEdit
@onready var difficulty_option = $Panel/VBox/FieldsContainer/DifficultyRow/OptionButton
@onready var launch_button = $Panel/VBox/ButtonRow/LaunchButton
@onready var random_button = $Panel/VBox/FieldsContainer/LabNameRow/LabelRow/RandomButton
@onready var weekly_button = $Panel/VBox/FieldsContainer/SeedRow/HBox/WeeklyButton

# Random lab name components (ported from pygame)
var lab_prefixes = [
	"Advanced", "Applied", "Center for", "Institute for",
	"Laboratory of", "Division of", "Department of",
	"Initiative for", "Research into", "Foundation for"
]

var lab_topics = [
	"AI Safety", "Machine Learning", "Artificial Intelligence",
	"Computational Intelligence", "Cognitive Systems",
	"Neural Networks", "Autonomous Systems", "Intelligent Agents",
	"Beneficial AI", "Aligned Intelligence"
]

var lab_suffixes = [
	"Research", "Studies", "Analysis", "Exploration",
	"Development", "Innovation", "Excellence"
]

func _ready():
	print("[PreGameSetup] Initializing...")

	# Load values from GameConfig
	player_name_input.text = GameConfig.player_name
	lab_name_input.text = GameConfig.lab_name
	seed_input.text = GameConfig.game_seed
	difficulty_option.selected = GameConfig.difficulty

	# Set up button icons
	_setup_button_icons()

	# Focus player name input
	player_name_input.grab_focus()

	# Validate launch button state
	_update_launch_button()

func _setup_button_icons():
	"""Replace button text/emoji with icons where available"""
	# Random button icon
	var random_icon = IconLoader.get_config_icon("random")
	if random_icon:
		random_button.text = ""
		random_button.icon = random_icon
		random_button.expand_icon = true

	# Weekly button icon
	var date_icon = IconLoader.get_config_icon("date")
	if date_icon:
		weekly_button.icon = date_icon
		weekly_button.expand_icon = true

func _update_launch_button():
	"""Enable/disable launch button based on required fields"""
	var can_launch = true

	# Require player name
	if player_name_input.text.strip_edges().length() == 0:
		can_launch = false

	# Require lab name
	if lab_name_input.text.strip_edges().length() == 0:
		can_launch = false

	launch_button.disabled = not can_launch

func _on_player_name_changed(new_text: String):
	"""Handle player name input change"""
	GameConfig.player_name = new_text.strip_edges()
	_update_launch_button()

func _on_lab_name_changed(new_text: String):
	"""Handle lab name input change"""
	GameConfig.lab_name = new_text.strip_edges()
	_update_launch_button()

func _on_seed_changed(new_text: String):
	"""Handle seed input change"""
	GameConfig.game_seed = new_text.strip_edges()

func _on_difficulty_selected(index: int):
	"""Handle difficulty selection"""
	GameConfig.difficulty = index
	print("[PreGameSetup] Difficulty selected: ", ["Easy", "Standard", "Hard"][index])

func _on_random_lab_name_pressed():
	"""Generate a random lab name"""
	var random_name = _generate_random_lab_name()
	lab_name_input.text = random_name
	GameConfig.lab_name = random_name
	_update_launch_button()

	print("[PreGameSetup] Generated random lab name: ", random_name)

func _generate_random_lab_name() -> String:
	"""Generate a random lab name from components"""
	var prefix = lab_prefixes[randi() % lab_prefixes.size()]
	var topic = lab_topics[randi() % lab_topics.size()]
	var suffix = lab_suffixes[randi() % lab_suffixes.size()]

	# Randomly choose format
	var formats = [
		"%s %s %s" % [prefix, topic, suffix],
		"%s %s" % [topic, suffix],
		"%s %s" % [prefix, topic]
	]

	return formats[randi() % formats.size()]

func _on_weekly_seed_pressed():
	"""Clear seed to use weekly challenge seed"""
	seed_input.text = ""
	GameConfig.game_seed = ""
	print("[PreGameSetup] Using weekly challenge seed: ", GameConfig.get_weekly_seed())

func _on_launch_pressed():
	"""Launch the game with configured settings"""
	if launch_button.disabled:
		return

	# Set custom config mode (allows all options to be edited)
	GameConfig.config_mode = "custom"

	# Save configuration
	GameConfig.save_config()

	# Print configuration for debugging
	GameConfig.print_config()

	print("[PreGameSetup] Going to configuration confirmation...")

	# Go to confirmation screen (consistent UX with default pathway)
	get_tree().change_scene_to_file("res://scenes/config_confirmation.tscn")

func _on_cancel_pressed():
	"""Return to welcome screen"""
	print("[PreGameSetup] Cancelled, returning to welcome screen")
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_cancel_pressed()
		elif event.keycode == KEY_ENTER:
			if not launch_button.disabled:
				_on_launch_pressed()

extends Control
## Pre-Game Setup Screen - Configure player name, lab name, seed, and difficulty

# UI References
@onready var player_name_input = $Panel/VBox/FieldsContainer/PlayerNameRow/LineEdit
@onready var lab_name_input = $Panel/VBox/FieldsContainer/LabNameRow/LineEdit
@onready var seed_input = $Panel/VBox/FieldsContainer/SeedRow/HBox/LineEdit
@onready var difficulty_option = $Panel/VBox/FieldsContainer/DifficultyRow/OptionButton
@onready var launch_button = $Panel/VBox/ButtonRow/LaunchButton

# Game configuration
var game_config = {
	"player_name": "Researcher",
	"lab_name": "AI Safety Lab",
	"seed": "",  # Empty for weekly challenge
	"difficulty": 1  # 0=Easy, 1=Standard, 2=Hard
}

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

	# Set default values
	player_name_input.text = game_config.player_name
	lab_name_input.text = game_config.lab_name
	seed_input.text = game_config.seed
	difficulty_option.selected = game_config.difficulty

	# Focus player name input
	player_name_input.grab_focus()

	# Validate launch button state
	_update_launch_button()

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
	game_config.player_name = new_text.strip_edges()
	_update_launch_button()

func _on_lab_name_changed(new_text: String):
	"""Handle lab name input change"""
	game_config.lab_name = new_text.strip_edges()
	_update_launch_button()

func _on_seed_changed(new_text: String):
	"""Handle seed input change"""
	game_config.seed = new_text.strip_edges()

func _on_difficulty_selected(index: int):
	"""Handle difficulty selection"""
	game_config.difficulty = index
	print("[PreGameSetup] Difficulty selected: ", ["Easy", "Standard", "Hard"][index])

func _on_random_lab_name_pressed():
	"""Generate a random lab name"""
	var random_name = _generate_random_lab_name()
	lab_name_input.text = random_name
	game_config.lab_name = random_name
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
	game_config.seed = ""
	print("[PreGameSetup] Using weekly challenge seed")

func _on_launch_pressed():
	"""Launch the game with configured settings"""
	if launch_button.disabled:
		return

	print("[PreGameSetup] Launching game with config: ", game_config)

	# Store config globally (using autoload singleton)
	# TODO: Create GameConfig autoload singleton
	# For now, just transition to main game
	get_tree().change_scene_to_file("res://scenes/main.tscn")

	# TODO: Pass configuration to game manager
	# The game manager should read this configuration on startup

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

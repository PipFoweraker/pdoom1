extends Control
## Pre-Game Setup Screen - Configure player name, lab name, seed, and difficulty using GameConfig

# UI References
@onready var player_name_input = $Panel/VBox/FieldsContainer/PlayerNameRow/LineEdit
@onready var lab_name_input = $Panel/VBox/FieldsContainer/LabNameRow/LineEdit
@onready var seed_input = $Panel/VBox/FieldsContainer/SeedRow/HBox/LineEdit
@onready var difficulty_option = $Panel/VBox/FieldsContainer/DifficultyRow/OptionButton
@onready var scenario_option = $Panel/VBox/FieldsContainer/ScenarioRow/OptionButton
@onready var scenario_description = $Panel/VBox/FieldsContainer/ScenarioRow/Description
@onready var launch_button = $Panel/VBox/ButtonRow/LaunchButton
@onready var random_button = $Panel/VBox/FieldsContainer/LabNameRow/LabelRow/RandomButton
@onready var weekly_button = $Panel/VBox/FieldsContainer/SeedRow/HBox/WeeklyButton

# Available scenarios (populated at runtime)
var available_scenarios: Array[Dictionary] = []

# Org-form choice control (built programmatically in _setup_org_type_choice)
var org_type_option: OptionButton

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

	# Populate scenarios dropdown
	_populate_scenarios()

	# Early-game org-form choice (DQ-19)
	_setup_org_type_choice()

	# Focus player name input
	player_name_input.grab_focus()

	# Validate launch button state
	_update_launch_button()

func _populate_scenarios():
	"""Load and populate the scenarios dropdown"""
	var loader = ScenarioLoader.new()
	available_scenarios = loader.get_available_scenarios()

	scenario_option.clear()

	var selected_index = 0
	for i in range(available_scenarios.size()):
		var scenario = available_scenarios[i]
		scenario_option.add_item(scenario.get("title", "Unknown"), i)

		# Check if this is the currently selected scenario
		if scenario.get("id", "") == GameConfig.scenario_id:
			selected_index = i

	scenario_option.selected = selected_index
	_update_scenario_description(selected_index)

	print("[PreGameSetup] Loaded %d scenarios" % available_scenarios.size())

func _update_scenario_description(index: int):
	"""Update the scenario description label"""
	if index >= 0 and index < available_scenarios.size():
		var scenario = available_scenarios[index]
		scenario_description.text = scenario.get("description", "No description available")

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

func _on_scenario_selected(index: int):
	"""Handle scenario selection"""
	if index >= 0 and index < available_scenarios.size():
		var scenario = available_scenarios[index]
		GameConfig.scenario_id = scenario.get("id", "")
		_update_scenario_description(index)
		print("[PreGameSetup] Scenario selected: %s" % scenario.get("title", "Unknown"))

func _setup_org_type_choice():
	"""Add the early-game org-form choice (DQ-19). Built in code to avoid a .tscn edit
	on launch day. Non-profit (default) vs for-profit changes FinanceEngine pricing and
	unlocks for-profit-only instruments (e.g. vc_equity)."""
	var container := $Panel/VBox/FieldsContainer
	if container == null:
		return
	var row := HBoxContainer.new()
	row.name = "OrgTypeRow"
	var label := Label.new()
	label.text = "Org Form:"
	label.custom_minimum_size = Vector2(140, 0)
	org_type_option = OptionButton.new()
	org_type_option.add_item("Non-profit", 0)
	org_type_option.add_item("For-profit", 1)
	org_type_option.selected = (1 if GameConfig.org_type == "for_profit" else 0)
	org_type_option.item_selected.connect(_on_org_type_selected)
	row.add_child(label)
	row.add_child(org_type_option)
	container.add_child(row)

func _on_org_type_selected(index: int):
	"""Handle org-form selection"""
	GameConfig.org_type = ("for_profit" if index == 1 else "nonprofit")
	print("[PreGameSetup] Org form: %s" % GameConfig.org_type)

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
	SceneTransition.go_to("res://scenes/config_confirmation.tscn")

func _on_cancel_pressed():
	"""Return to welcome screen"""
	print("[PreGameSetup] Cancelled, returning to welcome screen")
	SceneTransition.go_to("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_cancel_pressed()
		elif event.keycode == KEY_ENTER:
			if not launch_button.disabled:
				_on_launch_pressed()

extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements
@onready var turn_label = $ResourceDisplay/TurnLabel
@onready var money_label = $ResourceDisplay/MoneyLabel
@onready var compute_label = $ResourceDisplay/ComputeLabel
@onready var research_label = $ResourceDisplay/ResearchLabel
@onready var papers_label = $ResourceDisplay/PapersLabel
@onready var reputation_label = $ResourceDisplay/ReputationLabel
@onready var doom_label = $ResourceDisplay/DoomLabel
@onready var ap_label = $ResourceDisplay/APLabel
@onready var phase_label = $BottomBar/PhaseLabel
@onready var message_log = $ContentArea/RightPanel/MessageScroll/MessageLog
@onready var actions_list = $ContentArea/LeftPanel/ActionsScroll/ActionsList

@onready var init_button = $BottomBar/ControlButtons/InitButton
@onready var test_action_button = $BottomBar/ControlButtons/TestActionButton
@onready var end_turn_button = $BottomBar/ControlButtons/EndTurnButton

# Reference to GameManager
var game_manager: Node

# Track queued actions
var queued_actions: Array = []
var current_turn_phase: String = "NOT_STARTED"

func _ready():
	print("[MainUI] Initializing UI...")

	# Get GameManager reference
	game_manager = get_node("../GameManager")

	# Connect to GameManager signals
	game_manager.game_state_updated.connect(_on_game_state_updated)
	game_manager.turn_phase_changed.connect(_on_turn_phase_changed)
	game_manager.action_executed.connect(_on_action_executed)
	game_manager.error_occurred.connect(_on_error_occurred)
	game_manager.actions_available.connect(_on_actions_available)

	log_message("[color=yellow]UI Ready. Click 'Init Game' to start.[/color]")

func _on_init_button_pressed():
	log_message("[color=cyan]Initializing game...[/color]")
	init_button.disabled = true
	game_manager.start_new_game("test-seed")

func _on_test_action_button_pressed():
	log_message("[color=cyan]Selecting action: hire_safety_researcher[/color]")
	game_manager.select_action("hire_safety_researcher")

func _on_end_turn_button_pressed():
	if queued_actions.size() == 0:
		log_message("[color=yellow]No actions queued! Select actions first.[/color]")
		return

	log_message("[color=cyan]Ending turn with %d queued actions...[/color]" % queued_actions.size())

	# Clear queued actions (will be repopulated after turn processes)
	queued_actions.clear()
	update_queued_actions_display()

	game_manager.end_turn()

func _on_game_state_updated(state: Dictionary):
	print("[MainUI] State updated: ", state)

	# Update resource displays
	turn_label.text = "Turn: %d" % state.get("turn", 0)
	money_label.text = "Money: $%.0f" % state.get("money", 0)
	compute_label.text = "Compute: %.1f" % state.get("compute", 0)
	research_label.text = "Research: %.1f" % state.get("research", 0)
	papers_label.text = "Papers: %d" % state.get("papers", 0)
	reputation_label.text = "Rep: %.0f" % state.get("reputation", 0)
	doom_label.text = "Doom: %.1f%%" % state.get("doom", 0)
	ap_label.text = "AP: %d" % state.get("action_points", 0)

	# Color-code doom (green < 30, yellow < 70, red >= 70)
	var doom = state.get("doom", 0)
	if doom < 30:
		doom_label.modulate = Color(0.2, 1.0, 0.2)
	elif doom < 70:
		doom_label.modulate = Color(1.0, 1.0, 0.2)
	else:
		doom_label.modulate = Color(1.0, 0.2, 0.2)

	# Enable controls after first init
	if state.get("turn", 0) >= 0:
		test_action_button.disabled = false
		init_button.disabled = true

		# Note: Actions are now included in init_game response
		# No need to call get_available_actions() separately

	# Check game over
	if state.get("game_over", false):
		var victory = state.get("victory", false)
		if victory:
			log_message("[color=gold]VICTORY! You survived![/color]")
		else:
			log_message("[color=red]GAME OVER! The AI destroyed humanity.[/color]")

		# Disable controls
		test_action_button.disabled = true
		end_turn_button.disabled = true

func _on_turn_phase_changed(phase_name: String):
	print("[MainUI] Phase changed: ", phase_name)

	current_turn_phase = phase_name

	# Update phase label with color coding
	var phase_color = "white"
	var phase_display = phase_name

	if phase_name == "turn_start" or phase_name == "TURN_START":
		phase_color = "red"
		phase_display = "TURN START (Processing...)"
		end_turn_button.disabled = true
	elif phase_name == "action_selection" or phase_name == "ACTION_SELECTION":
		phase_color = "green"
		phase_display = "ACTION SELECTION (Ready)"
		end_turn_button.disabled = false
	elif phase_name == "turn_end" or phase_name == "TURN_END":
		phase_color = "yellow"
		phase_display = "TURN END (Executing...)"
		end_turn_button.disabled = true

	phase_label.text = "[color=%s]Phase: %s[/color]" % [phase_color, phase_display]

	log_message("[color=magenta]Turn Phase: " + phase_name + "[/color]")

func _on_action_executed(result: Dictionary):
	print("[MainUI] Action executed: ", result)

	var message = result.get("message", "Action completed")
	log_message("[color=lime]" + message + "[/color]")

	# Show any additional messages from action
	if result.has("messages"):
		for msg in result.get("messages", []):
			log_message("[color=white]  " + str(msg) + "[/color]")

	# Note: GameManager now handles auto-starting next turn

func _on_error_occurred(error_msg: String):
	print("[MainUI] Error: ", error_msg)
	log_message("[color=red]ERROR: " + error_msg + "[/color]")

func log_message(text: String):
	"""Add a message to the log with timestamp"""
	var timestamp = Time.get_ticks_msec() / 1000.0
	message_log.text += "\n[color=gray][%.1fs][/color] %s" % [timestamp, text]

	# Auto-scroll to bottom
	await get_tree().process_frame
	var scroll = message_log.get_parent() as ScrollContainer
	if scroll:
		scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _on_actions_available(actions: Array):
	"""Populate action list dynamically"""
	print("[MainUI] Populating ", actions.size(), " actions")

	# Clear existing action buttons (except test button for now)
	for child in actions_list.get_children():
		if child.name != "TestActionButton":
			child.queue_free()

	# Get current state for affordability checking
	var current_state = game_manager.get_game_state()

	# Create button for each action
	for action in actions:
		var action_id = action.get("id", "")
		var action_name = action.get("name", "Unknown")
		var action_cost = action.get("costs", {})
		var action_description = action.get("description", "")
		var category = action.get("category", "other")

		# Create button
		var button = Button.new()
		button.text = action_name

		# Check if player can afford this action
		var can_afford = true
		var missing_resources = []

		for resource in action_cost.keys():
			var cost = action_cost[resource]
			var available = current_state.get(resource, 0)

			if available < cost:
				can_afford = false
				missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

		# Add cost info to tooltip
		var tooltip = action_description + "\n\nCosts:"
		for resource in action_cost.keys():
			tooltip += "\n  %s: %s" % [resource, action_cost[resource]]

		if not can_afford:
			tooltip += "\n\n[CANNOT AFFORD]"
			for msg in missing_resources:
				tooltip += "\n  Missing: " + msg
			button.disabled = true
			button.modulate = Color(0.6, 0.6, 0.6)  # Gray out unaffordable

		button.tooltip_text = tooltip

		# Connect button press
		button.pressed.connect(func(): _on_dynamic_action_pressed(action_id, action_name))

		# Add to list
		actions_list.add_child(button)

	log_message("[color=cyan]Loaded %d available actions[/color]" % actions.size())

func _on_dynamic_action_pressed(action_id: String, action_name: String):
	"""Handle dynamic action button press"""
	log_message("[color=cyan]Selecting action: %s[/color]" % action_name)

	# Track queued action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func update_queued_actions_display():
	"""Update the message log to show queued actions"""
	if queued_actions.size() > 0:
		var action_names = []
		for action in queued_actions:
			action_names.append(action.get("name", "Unknown"))
		log_message("[color=lime]Queued actions (%d): %s[/color]" % [queued_actions.size(), ", ".join(action_names)])
	else:
		log_message("[color=gray]No actions queued[/color]")

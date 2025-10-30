extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements
@onready var turn_label = $ResourceDisplay/TurnLabel
@onready var money_label = $ResourceDisplay/MoneyLabel
@onready var compute_label = $ResourceDisplay/ComputeLabel
@onready var safety_label = $ResourceDisplay/SafetyLabel
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
	game_manager.event_triggered.connect(_on_event_triggered)

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
	turn_label.text = "Turn: " + str(state.get("turn", 0))
	money_label.text = "Money: $" + str(state.get("money", 0))
	compute_label.text = "Compute: " + str(state.get("compute", 0))
	safety_label.text = "Safety: " + str(state.get("safety", 0))

	# Log state change
	log_message("[color=green]State updated - Turn %d | $%d | Compute: %d | Safety: %d[/color]" % [
		state.get("turn", 0),
		state.get("money", 0),
		state.get("compute", 0),
		state.get("safety", 0)
	])

	# Enable controls after first init
	if state.get("turn", 0) >= 0:
		test_action_button.disabled = false
		init_button.disabled = true

		# Refresh action list to update affordability
		if state.get("turn", -1) >= 0:
			game_manager.get_available_actions()

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

func _on_turn_phase_changed(phase_info: Dictionary):
	print("[MainUI] Phase changed: ", phase_info)

	var phase_name = phase_info.get("phase", "UNKNOWN")
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

	# Handle pending events
	if phase_info.has("pending_events") and phase_info["pending_events"].size() > 0:
		log_message("[color=yellow]%d Events triggered![/color]" % phase_info["pending_events"].size())
		for event in phase_info["pending_events"]:
			log_message("[color=yellow]  - " + str(event.get("name", "Unknown Event")) + "[/color]")

	# Handle events array (alternative format)
	if phase_info.has("events") and phase_info["events"].size() > 0:
		for event in phase_info["events"]:
			game_manager.event_triggered.emit(event)

func _on_action_executed(result: Dictionary):
	print("[MainUI] Action executed: ", result)

	var message = result.get("message", "Action completed")
	log_message("[color=lime]" + message + "[/color]")

	# Show any additional messages from action
	if result.has("messages"):
		for msg in result.get("messages", []):
			log_message("[color=white]  " + str(msg) + "[/color]")

	# After turn ends, automatically start new turn
	if result.has("turn_number"):
		log_message("[color=cyan]Auto-starting turn %d...[/color]" % result.get("turn_number"))
		await get_tree().create_timer(0.5).timeout  # Small delay for readability
		game_manager.start_turn()

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
		var action_cost = action.get("cost", {})
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

func _on_event_triggered(event: Dictionary):
	"""Show event popup dialog"""
	print("[MainUI] Event triggered: ", event)

	var event_name = event.get("name", "Unknown Event")
	var event_description = event.get("description", "")
	var choices = event.get("choices", [])

	# Create popup dialog
	var dialog = AcceptDialog.new()
	dialog.title = event_name
	dialog.dialog_text = event_description
	dialog.size = Vector2(500, 300)

	# Add choice buttons
	for choice in choices:
		var choice_id = choice.get("id", "")
		var choice_text = choice.get("text", "")

		dialog.add_button(choice_text, false, choice_id)

	# Connect custom action signal
	dialog.custom_action.connect(func(choice_id):
		game_manager.resolve_event(event.get("id", ""), choice_id)
		dialog.queue_free()
	)

	# Add to scene
	add_child(dialog)
	dialog.popup_centered()

	log_message("[color=yellow]Event: %s[/color]" % event_name)

func update_queued_actions_display():
	"""Update the message log to show queued actions"""
	if queued_actions.size() > 0:
		var action_names = []
		for action in queued_actions:
			action_names.append(action.get("name", "Unknown"))
		log_message("[color=lime]Queued actions (%d): %s[/color]" % [queued_actions.size(), ", ".join(action_names)])
	else:
		log_message("[color=gray]No actions queued[/color]")

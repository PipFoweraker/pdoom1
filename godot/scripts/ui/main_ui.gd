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
	game_manager.event_triggered.connect(_on_event_triggered)

	# Enable input processing for keyboard shortcuts
	set_process_input(true)

	log_message("[color=yellow]UI Ready. Click 'Init Game' to start.[/color]")
	log_message("[color=gray]Keyboard: 1-9 for actions, Space/Enter to end turn[/color]")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		# Number keys 1-9 for action shortcuts
		if event.keycode >= KEY_1 and event.keycode <= KEY_9:
			var action_index = event.keycode - KEY_1  # 0-indexed
			_trigger_action_by_index(action_index)
			get_viewport().set_input_as_handled()

		# Space or Enter to end turn
		elif event.keycode == KEY_SPACE or event.keycode == KEY_ENTER:
			if not end_turn_button.disabled:
				_on_end_turn_button_pressed()
				get_viewport().set_input_as_handled()

		# Escape to init game (if not started)
		elif event.keycode == KEY_ESCAPE:
			if not init_button.disabled:
				_on_init_button_pressed()
				get_viewport().set_input_as_handled()

func _trigger_action_by_index(index: int):
	"""Trigger action button by its index (for keyboard shortcuts)"""
	var buttons = actions_list.get_children()
	var action_buttons = []

	# Filter out category labels, get only buttons
	for child in buttons:
		if child is Button and child.name != "TestActionButton":
			action_buttons.append(child)

	if index < action_buttons.size():
		var button = action_buttons[index]
		if not button.disabled:
			button.emit_signal("pressed")
			log_message("[color=cyan]Keyboard shortcut: %d[/color]" % (index + 1))

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

	# Add employee blob display to AP label
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)
	var blob_display = ""
	for i in range(safety):
		blob_display += "[color=green]●[/color]"
	for i in range(capability):
		blob_display += "[color=red]●[/color]"
	for i in range(compute_eng):
		blob_display += "[color=blue]●[/color]"

	ap_label.text = "AP: %d  %s" % [state.get("action_points", 0), blob_display]

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
	"""Populate action list dynamically, grouped by category"""
	print("[MainUI] Populating ", actions.size(), " actions")

	# Clear existing action buttons (except test button for now)
	for child in actions_list.get_children():
		if child.name != "TestActionButton":
			child.queue_free()

	# Get current state for affordability checking
	var current_state = game_manager.get_game_state()

	# Group actions by category
	var categories = {}
	for action in actions:
		var category = action.get("category", "other")
		if not categories.has(category):
			categories[category] = []
		categories[category].append(action)

	# Define category order and display names
	var category_order = ["hiring", "resources", "research", "management", "other"]
	var category_names = {
		"hiring": "Hiring",
		"resources": "Resources",
		"research": "Research",
		"management": "Management",
		"other": "Other"
	}

	# Create sections for each category
	for category_key in category_order:
		if not categories.has(category_key):
			continue

		var category_actions = categories[category_key]
		if category_actions.is_empty():
			continue

		# Create category label
		var category_label = Label.new()
		category_label.text = "-- " + category_names.get(category_key, category_key.capitalize()) + " --"
		category_label.add_theme_color_override("font_color", Color(0.7, 0.7, 1.0))
		actions_list.add_child(category_label)

		# Create buttons for actions in this category
		for action in category_actions:
			var action_id = action.get("id", "")
			var action_name = action.get("name", "Unknown")
			var action_cost = action.get("costs", {})
			var action_description = action.get("description", "")

			# Create button
			var button = Button.new()
			button.text = "  " + action_name  # Indent actions under category

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

	log_message("[color=cyan]Loaded %d available actions in %d categories[/color]" % [actions.size(), categories.size()])

func _on_dynamic_action_pressed(action_id: String, action_name: String):
	"""Handle dynamic action button press"""
	log_message("[color=cyan]Selecting action: %s[/color]" % action_name)

	# Check if this is a submenu action
	var action = _get_action_by_id(action_id)
	if action.get("is_submenu", false):
		# Open submenu dialog instead of queuing
		_show_hiring_submenu()
		return

	# Track queued action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func _get_action_by_id(action_id: String) -> Dictionary:
	"""Helper to find action definition"""
	for action in GameActions.get_all_actions():
		if action.get("id") == action_id:
			return action
	return {}

func _show_hiring_submenu():
	"""Show popup dialog with hiring options"""
	var dialog = AcceptDialog.new()
	dialog.title = "Hire Staff"
	dialog.dialog_text = "Choose a staff member to hire:"
	dialog.size = Vector2(500, 400)

	# Create container for hiring buttons
	var vbox = VBoxContainer.new()

	# Get hiring options
	var hiring_options = GameActions.get_hiring_options()
	var current_state = game_manager.get_game_state()

	for option in hiring_options:
		var hire_id = option.get("id", "")
		var hire_name = option.get("name", "")
		var hire_desc = option.get("description", "")
		var hire_costs = option.get("costs", {})

		# Create button for this option
		var btn = Button.new()
		btn.text = "%s ($%d, %d AP)" % [hire_name, hire_costs.get("money", 0), hire_costs.get("action_points", 0)]

		# Check affordability
		var can_afford = true
		for resource in hire_costs.keys():
			if current_state.get(resource, 0) < hire_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.6, 0.6, 0.6)

		# Add tooltip
		btn.tooltip_text = hire_desc + "\n\nCosts: $%d, %d AP" % [hire_costs.get("money", 0), hire_costs.get("action_points", 0)]

		# Connect button
		btn.pressed.connect(func(): _on_hiring_option_selected(hire_id, hire_name, dialog))

		vbox.add_child(btn)

	# Add to dialog
	dialog.add_child(vbox)
	add_child(dialog)
	dialog.popup_centered()

func _on_hiring_option_selected(action_id: String, action_name: String, dialog: AcceptDialog):
	"""Handle hiring submenu selection"""
	dialog.queue_free()

	log_message("[color=cyan]Hiring: %s[/color]" % action_name)

	# Queue the actual hiring action
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

func _on_event_triggered(event: Dictionary):
	"""Handle event trigger - show popup dialog"""
	print("[MainUI] Event triggered: ", event.get("name", "Unknown"))

	log_message("[color=gold]EVENT: %s[/color]" % event.get("name", "Unknown"))

	# Create event popup dialog
	var dialog = AcceptDialog.new()
	dialog.title = event.get("name", "Event")
	dialog.dialog_text = event.get("description", "An event has occurred!")
	dialog.size = Vector2(600, 450)

	# Create container for option buttons
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)

	# Add each option as a button
	var options = event.get("options", [])
	var current_state = game_manager.get_game_state()

	for option in options:
		var choice_id = option.get("id", "")
		var choice_text = option.get("text", "")
		var costs = option.get("costs", {})

		var btn = Button.new()
		btn.text = choice_text
		btn.custom_minimum_size = Vector2(500, 45)

		# Check affordability
		var can_afford = true
		var missing_resources = []

		for resource in costs.keys():
			var cost = costs[resource]
			var available = current_state.get(resource, 0)

			if available < cost:
				can_afford = false
				missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

		# Add tooltip with costs/effects
		var tooltip = ""
		if not costs.is_empty():
			tooltip += "Costs:\n"
			for resource in costs.keys():
				tooltip += "  %s: %s\n" % [resource, costs[resource]]

		var effects = option.get("effects", {})
		if not effects.is_empty():
			tooltip += "\nEffects:\n"
			for resource in effects.keys():
				var value = effects[resource]
				var sign = "+" if value >= 0 else ""
				tooltip += "  %s: %s%s\n" % [resource, sign, value]

		if not can_afford:
			tooltip += "\n[CANNOT AFFORD]\n"
			for msg in missing_resources:
				tooltip += "  Missing: " + msg + "\n"
			btn.disabled = true
			btn.modulate = Color(0.6, 0.6, 0.6)

		btn.tooltip_text = tooltip

		# Connect button
		btn.pressed.connect(func(): _on_event_choice_selected(event, choice_id, dialog))

		vbox.add_child(btn)

	# Add to dialog
	dialog.add_child(vbox)
	add_child(dialog)
	dialog.popup_centered()

func _on_event_choice_selected(event: Dictionary, choice_id: String, dialog: AcceptDialog):
	"""Handle event choice selection"""
	dialog.queue_free()

	log_message("[color=cyan]Event choice: %s[/color]" % choice_id)

	# Tell game manager to resolve event
	game_manager.resolve_event(event, choice_id)

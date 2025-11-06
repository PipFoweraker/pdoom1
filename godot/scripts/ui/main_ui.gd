extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements (TopBar now has all resources in one line)
@onready var turn_label = $TopBar/TurnLabel
@onready var money_label = $TopBar/MoneyLabel
@onready var compute_label = $TopBar/ComputeLabel
@onready var research_label = $TopBar/ResearchLabel
@onready var papers_label = $TopBar/PapersLabel
@onready var reputation_label = $TopBar/ReputationLabel
@onready var doom_label = $TopBar/DoomLabel
@onready var ap_label = $TopBar/APLabel
@onready var phase_label = $BottomBar/PhaseLabel
@onready var message_log = $ContentArea/RightPanel/MessageScroll/MessageLog
@onready var actions_list = $ContentArea/LeftPanel/ActionsScroll/ActionsList
@onready var upgrades_list = $ContentArea/LeftPanel/UpgradesScroll/UpgradesList
@onready var info_label = $InfoBar/MarginContainer/InfoLabel
@onready var queue_container = $ContentArea/RightPanel/QueuePanel/QueueContainer
@onready var queue_hint = $ContentArea/RightPanel/QueuePanel/QueueContainer/QueueHint

@onready var init_button = $BottomBar/ControlButtons/InitButton
@onready var test_action_button = $BottomBar/ControlButtons/TestActionButton
@onready var reserve_ap_button = $BottomBar/ControlButtons/ReserveAPButton
@onready var clear_queue_button = $BottomBar/ControlButtons/ClearQueueButton
@onready var end_turn_button = $BottomBar/ControlButtons/EndTurnButton
@onready var cat_panel = $TopBar/CatPanel
@onready var doom_meter = $BottomBar/DoomMeterContainer/MarginContainer/DoomMeter
@onready var game_over_screen = $"../GameOverScreen"

# Reference to GameManager
var game_manager: Node

# Track queued actions
var queued_actions: Array = []
var current_turn_phase: String = "NOT_STARTED"

# Active dialog state for keyboard shortcuts
var active_dialog: Control = null
var active_dialog_buttons: Array = []

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
	set_process_unhandled_input(true)
	set_process_unhandled_key_input(true)  # For dialog shortcuts

	# Auto-initialize game when scene loads
	log_message("[color=cyan]Initializing game...[/color]")
	log_message("[color=gray]Keyboard: 1-9 for actions, Space/Enter to commit[/color]")

	# Call init on next frame to ensure everything is ready
	await get_tree().process_frame
	_on_init_button_pressed()

func _unhandled_key_input(event: InputEvent):
	"""Handle keyboard shortcuts for dialogs (runs after focus but before _unhandled_input)"""
	if event is InputEventKey and event.pressed and not event.echo:
		print("[MainUI] _unhandled_key_input called, keycode: %d, active_dialog: %s" % [event.keycode, active_dialog != null])
		# CRITICAL: Call the dialog's input handler if one is active
		if active_dialog != null and is_instance_valid(active_dialog):
			if active_dialog.has_meta("input_handler"):
				print("[MainUI] Calling dialog's input handler")
				var handler = active_dialog.get_meta("input_handler")
				handler.call(event)
				get_viewport().set_input_as_handled()
				accept_event()
				return

	# Populate upgrades list
	_populate_upgrades_list()

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		var key_char = char(event.unicode) if event.unicode > 0 else "?"
		print("[MainUI] _input called, keycode: %d (%s), active_dialog: %s, buttons: %d" % [event.keycode, key_char, active_dialog != null, active_dialog_buttons.size()])

		# CRITICAL: If dialog is active, handle letter shortcuts FIRST with HIGHEST priority
		if active_dialog != null and is_instance_valid(active_dialog):
			print("[MainUI] Dialog is active and valid!")
			var dialog_keys = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]
			var key_index = dialog_keys.find(event.keycode)
			print("[MainUI] Looking for keycode %d in dialog_keys, found at index: %d" % [event.keycode, key_index])

			if key_index >= 0 and key_index < active_dialog_buttons.size():
				print("[MainUI] Key index %d is valid (buttons count: %d)" % [key_index, active_dialog_buttons.size()])
				var btn = active_dialog_buttons[key_index]
				print("[MainUI] Button at index: %s, valid: %s, disabled: %s" % [btn != null, is_instance_valid(btn) if btn != null else false, btn.disabled if btn != null else "N/A"])
				if btn != null and is_instance_valid(btn) and not btn.disabled:
					print("[MainUI] *** TRIGGERING DIALOG BUTTON: %s ***" % btn.text)
					btn.pressed.emit()
					get_viewport().set_input_as_handled()
					return
				else:
					print("[MainUI] Button not triggerable (null, invalid, or disabled)")
			else:
				print("[MainUI] Key index %d out of range or not found" % key_index)

		# If dialog is active, handle dialog shortcuts FIRST (before buttons consume them)
		if active_dialog != null and is_instance_valid(active_dialog):
			print("[MainUI] Dialog is active, buttons count: %d" % active_dialog_buttons.size())

			# Letter keys for dialog options (Q/W/E/R/A/S/D/F/Z)
			var dialog_keys = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]
			var key_index = dialog_keys.find(event.keycode)

			if key_index >= 0:
				print("[MainUI] Dialog letter key pressed, index: %d, buttons: %d" % [key_index, active_dialog_buttons.size()])
				if key_index < active_dialog_buttons.size():
					var btn = active_dialog_buttons[key_index]
					if btn != null and is_instance_valid(btn) and not btn.disabled:
						print("[MainUI] Triggering dialog button: %s" % btn.text)
						btn.pressed.emit()
						get_viewport().set_input_as_handled()
						return

			# Escape to close dialog
			elif event.keycode == KEY_ESCAPE:
				active_dialog.queue_free()
				active_dialog = null
				active_dialog_buttons = []
				get_viewport().set_input_as_handled()
				return

		# Main game shortcuts (when no dialog is active)
		# Number keys 1-9 for action shortcuts
		if event.keycode >= KEY_1 and event.keycode <= KEY_9:
			var action_index = event.keycode - KEY_1  # 0-indexed
			_trigger_action_by_index(action_index)
			get_viewport().set_input_as_handled()

		# Clear queue (C key by default, configurable via KeybindManager)
		elif KeybindManager.is_action_pressed(event, "clear_queue"):
			if not clear_queue_button.disabled:
				_on_clear_queue_button_pressed()
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

func _unhandled_input(event: InputEvent):
	"""Handle keyboard shortcuts that weren't handled by UI elements"""
	if event is InputEventKey and event.pressed and not event.echo:
		print("[MainUI] _unhandled_input called, keycode: %d, active_dialog: %s" % [event.keycode, active_dialog != null])
		# If dialog is active, handle dialog shortcuts with LETTERS (Q/W/E/R/A/S/D/F/Z)
		if active_dialog != null and is_instance_valid(active_dialog):
			# Letter keys for dialog options (Q/W/E/R/A/S/D/F/Z = 9 options)
			var dialog_keys = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]
			var key_index = dialog_keys.find(event.keycode)

			if key_index >= 0:
				print("[MainUI] Dialog letter key pressed, index: %d, buttons: %d" % [key_index, active_dialog_buttons.size()])
				if key_index < active_dialog_buttons.size():
					var btn = active_dialog_buttons[key_index]
					if btn != null and is_instance_valid(btn) and not btn.disabled:
						print("[MainUI] Triggering dialog button: %s" % btn.text)
						btn.pressed.emit()
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

func _on_reserve_ap_button_pressed():
	"""Reserve 1 AP for event responses"""
	log_message("[color=cyan]Reserving 1 AP for events...[/color]")
	game_manager.reserve_ap(1)

func _on_clear_queue_button_pressed():
	"""Clear all queued actions and refund AP"""
	if queued_actions.size() == 0:
		return

	# Call GameManager to clear queue (refunds AP)
	game_manager.clear_action_queue()

	# Update local display
	queued_actions.clear()
	update_queued_actions_display()

	log_message("[color=yellow]Action queue cleared - AP refunded[/color]")

func _remove_queued_action(action_id: String, action_name: String):
	"""Remove a specific action from the queue"""
	print("[MainUI] Removing queued action: %s (id: %s)" % [action_name, action_id])

	# Find and remove from local queue
	var removed_index = -1
	for i in range(queued_actions.size()):
		if queued_actions[i].get("id") == action_id:
			removed_index = i
			break

	if removed_index >= 0:
		queued_actions.remove_at(removed_index)

		# Tell GameManager to remove and refund AP
		game_manager.remove_queued_action(action_id)

		# Get AP cost for logging
		var action_def = _get_action_by_id(action_id)
		var ap_cost = action_def.get("costs", {}).get("action_points", 0)

		log_message("[color=yellow]Removed: %s (+%d AP)[/color]" % [action_name, ap_cost])
		update_queued_actions_display()
	else:
		print("[MainUI] ERROR: Could not find action to remove: %s" % action_id)

func _on_end_turn_button_pressed():
	if queued_actions.size() == 0:
		log_message("[color=red]ERROR: No actions queued! Press C to clear queue or select actions.[/color]")
		return

	# Check for danger zones and warn player
	var current_state = game_manager.state
	var warnings = []

	# High doom warning
	if current_state.doom >= 80:
		warnings.append("[color=red]⚠️ CRITICAL: Doom at %.1f%% - Very close to game over![/color]" % current_state.doom)
	elif current_state.doom >= 70:
		warnings.append("[color=yellow]⚠️ WARNING: Doom at %.1f%% - Approaching danger zone![/color]" % current_state.doom)

	# Low reputation warning
	if current_state.reputation <= 20:
		warnings.append("[color=red]⚠️ CRITICAL: Reputation at %.0f - May lose funding![/color]" % current_state.reputation)
	elif current_state.reputation <= 30:
		warnings.append("[color=yellow]⚠️ WARNING: Low reputation (%.0f) - Watch funding![/color]" % current_state.reputation)

	# Low money warning
	if current_state.money <= 20000:
		warnings.append("[color=red]⚠️ CRITICAL: Low funds ($%.0f) - Can't afford much![/color]" % current_state.money)

	# Show warnings if any
	if warnings.size() > 0:
		for warning in warnings:
			log_message(warning)
		log_message("[color=gray]Press Space/Enter again to confirm, or C to revise queue[/color]")
		# Note: Simplified version - in full implementation, would require double-confirm

	log_message("[color=cyan]Committing %d actions...[/color]" % queued_actions.size())

	# Clear queued actions (will be repopulated after turn processes)
	queued_actions.clear()
	update_queued_actions_display()

	game_manager.end_turn()

func _on_game_state_updated(state: Dictionary):
	print("[MainUI] State updated: ", state)

	# Update resource displays
	turn_label.text = "Turn: %d" % state.get("turn", 0)
	money_label.text = "Money: $%s" % _format_money(state.get("money", 0))
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

	# Show AP split with remaining AP tracking
	var total_ap = state.get("action_points", 0)
	var committed_ap = state.get("committed_ap", 0)
	var reserved_ap = state.get("reserved_ap", 0)
	var remaining_ap = total_ap - committed_ap - reserved_ap

	# Color-code based on remaining AP
	var ap_color = Color(0.9, 0.9, 0.9)  # White (default)
	if remaining_ap <= 0:
		ap_color = Color(0.8, 0.2, 0.2)  # Red (depleted)
	elif remaining_ap == 1:
		ap_color = Color(0.9, 0.7, 0.2)  # Yellow (low)
	elif remaining_ap < total_ap:
		ap_color = Color(0.7, 0.9, 0.7)  # Light green (partially committed)

	ap_label.add_theme_color_override("font_color", ap_color)

	if reserved_ap > 0:
		ap_label.text = "AP: %d (%d free, %d reserved)  %s" % [total_ap, remaining_ap, reserved_ap, blob_display]
	elif committed_ap > 0:
		ap_label.text = "AP: %d (%d free, %d queued)  %s" % [total_ap, remaining_ap, committed_ap, blob_display]
	else:
		ap_label.text = "AP: %d  %s" % [total_ap, blob_display]

	# Update doom displays (both text label and visual meter)
	var doom = state.get("doom", 0)
	var doom_momentum = state.get("doom_momentum", 0.0)

	# Text label with color coding
	doom_label.text = "Doom: %.1f%%" % doom
	doom_label.modulate = ThemeManager.get_doom_color(doom)

	# Visual doom meter with momentum indicator
	if doom_meter:
		doom_meter.set_doom(doom, doom_momentum)

	# Show cat panel if adopted
	if state.get("has_cat", false):
		cat_panel.visible = true
	else:
		cat_panel.visible = false

	# Enable controls after first init
	if state.get("turn", 0) >= 0:
		test_action_button.disabled = false
		init_button.disabled = true

		# Enable/disable Reserve AP button based on available AP
		var available = state.get("available_ap", 0)
		reserve_ap_button.disabled = (available < 1)

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
		reserve_ap_button.disabled = true

		# Show game over screen with stats
		if game_over_screen:
			game_over_screen.show_game_over(victory, state)

	# Refresh upgrades list to update affordability
	_populate_upgrades_list()

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
		# Only enable if actions are queued
		end_turn_button.disabled = (queued_actions.size() == 0)
		clear_queue_button.disabled = (queued_actions.size() == 0)
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

	# Define category colors (from issue #436 player feedback)
	var category_colors = {
		"hiring": Color(0.4, 0.7, 1.0),      # Blue - people/staff
		"resources": Color(1.0, 0.8, 0.3),   # Gold - money/resources
		"research": Color(0.6, 1.0, 0.6),    # Green - research/growth
		"management": Color(1.0, 0.6, 0.8),  # Pink - administrative
		"other": Color(0.8, 0.8, 0.8)        # Gray - misc
	}

	# Create sections for each category
	var action_index = 0  # Track index for keyboard shortcuts
	for category_key in category_order:
		if not categories.has(category_key):
			continue

		var category_actions = categories[category_key]
		if category_actions.is_empty():
			continue

		# Create category label
		var category_label = Label.new()
		category_label.text = "-- " + category_names.get(category_key, category_key.capitalize()) + " --"
		var label_color = category_colors.get(category_key, Color(0.7, 0.7, 1.0))
		category_label.add_theme_color_override("font_color", label_color)
		actions_list.add_child(category_label)

		# Create buttons for actions in this category
		for action in category_actions:
			var action_id = action.get("id", "")
			var action_name = action.get("name", "Unknown")
			var action_cost = action.get("costs", {})
			var action_description = action.get("description", "")

			# Build button text with keyboard shortcut and costs
			var button_text = "  " + action_name  # Indent actions under category

			# Add keyboard shortcut hint if index is 0-8 (keys 1-9)
			if action_index < 9:
				button_text = "[%d] %s" % [action_index + 1, action_name]

			# Add cost display (concise format)
			var cost_parts = []
			if action_cost.has("action_points"):
				cost_parts.append("%d AP" % action_cost["action_points"])
			if action_cost.has("money"):
				var money_k = action_cost["money"] / 1000.0
				if money_k >= 1:
					cost_parts.append("$%dk" % int(money_k))
				else:
					cost_parts.append("$%d" % action_cost["money"])
			if action_cost.has("reputation"):
				cost_parts.append("%d Rep" % action_cost["reputation"])
			if action_cost.has("papers"):
				cost_parts.append("%d Paper" % action_cost["papers"])

			if cost_parts.size() > 0:
				button_text += " (" + ", ".join(cost_parts) + ")"

			# Create styled button using ThemeManager
			var button = ThemeManager.create_button(button_text)

			action_index += 1  # Increment for next action

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
			else:
				# Apply subtle category color tint to affordable buttons (issue #436)
				var button_color = category_colors.get(category_key, Color(1.0, 1.0, 1.0))
				# Lighten the color for buttons (70% white + 30% category color for subtle tint)
				button.modulate = Color(0.7, 0.7, 0.7).lerp(button_color, 0.3)

			button.tooltip_text = tooltip

			# Connect button press
			button.pressed.connect(func(): _on_dynamic_action_pressed(action_id, action_name))

			# Connect mouse hover for info bar
			button.mouse_entered.connect(func(): _on_action_hover(action, can_afford, missing_resources))
			button.mouse_exited.connect(func(): _on_action_unhover())

			# Add to list
			actions_list.add_child(button)

	log_message("[color=cyan]Loaded %d available actions in %d categories[/color]" % [actions.size(), categories.size()])

	# Also populate upgrades
	_populate_upgrades()

func _populate_upgrades():
	"""Populate upgrades list"""
	# Clear existing upgrades
	for child in upgrades_list.get_children():
		child.queue_free()

	var current_state = game_manager.get_game_state()
	var all_upgrades = GameUpgrades.get_all_upgrades()

	for upgrade in all_upgrades:
		var upgrade_id = upgrade.get("id", "")
		var upgrade_name = upgrade.get("name", "Unknown")
		var upgrade_desc = upgrade.get("description", "")
		var upgrade_cost = upgrade.get("cost", 0)

		# Check if already purchased
		var is_purchased = current_state.get("purchased_upgrades", []).has(upgrade_id)

		# Create button
		var button = ThemeManager.create_button(upgrade_name)

		# If purchased, show differently
		if is_purchased:
			button.text = "✓ " + upgrade_name
			button.disabled = true
			button.modulate = Color(0.5, 1.0, 0.5)  # Green tint
		else:
			button.text = "%s ($%dk)" % [upgrade_name, upgrade_cost / 1000]

			# Check affordability
			var can_afford = current_state.get("money", 0) >= upgrade_cost
			if not can_afford:
				button.disabled = true
				button.modulate = Color(0.6, 0.6, 0.6)

		# Tooltip
		var tooltip = upgrade_desc + "\n\nCost: $%d" % upgrade_cost
		if is_purchased:
			tooltip += "\n\n[PURCHASED]"
		elif not current_state.get("money", 0) >= upgrade_cost:
			tooltip += "\n\n[CANNOT AFFORD]"
		button.tooltip_text = tooltip

		# Connect button press
		if not is_purchased:
			button.pressed.connect(func(): _on_upgrade_pressed(upgrade_id, upgrade_name))

		# Connect hover
		button.mouse_entered.connect(func(): _on_upgrade_hover(upgrade, is_purchased))
		button.mouse_exited.connect(func(): _on_action_unhover())

		upgrades_list.add_child(button)

	log_message("[color=cyan]Loaded %d upgrades[/color]" % all_upgrades.size())

func _on_upgrade_pressed(upgrade_id: String, upgrade_name: String):
	"""Handle upgrade purchase button press"""
	log_message("[color=cyan]Purchasing upgrade: %s[/color]" % upgrade_name)

	# Purchase via GameManager (will handle state update)
	game_manager.purchase_upgrade(upgrade_id)

func _on_upgrade_hover(upgrade: Dictionary, is_purchased: bool):
	"""Update info bar when hovering over an upgrade"""
	var upgrade_name = upgrade.get("name", "Unknown")
	var upgrade_desc = upgrade.get("description", "")
	var upgrade_cost = upgrade.get("cost", 0)

	# Build enhanced upgrade info
	var info_text = "[b][color=cyan]%s[/color][/b] — %s" % [upgrade_name, upgrade_desc]

	# Show cost
	var money_k = upgrade_cost / 1000.0
	if money_k >= 1:
		info_text += "\n[color=gray]├─[/color] [color=yellow]Cost:[/color] [color=gold]$%dk[/color]" % int(money_k)
	else:
		info_text += "\n[color=gray]├─[/color] [color=yellow]Cost:[/color] [color=gold]$%d[/color]" % upgrade_cost

	# Show status
	info_text += "\n[color=gray]└─[/color] "
	if is_purchased:
		info_text += "[color=green]✓ ALREADY PURCHASED[/color]"
	else:
		var current_state = game_manager.get_game_state()
		if current_state.get("money", 0) >= upgrade_cost:
			info_text += "[color=lime]✓ READY TO PURCHASE[/color]"
		else:
			var needed = upgrade_cost - current_state.get("money", 0)
			var needed_k = needed / 1000.0
			if needed_k >= 1:
				info_text += "[color=red]✗ NEED $%dk MORE[/color]" % int(needed_k)
			else:
				info_text += "[color=red]✗ NEED $%d MORE[/color]" % needed

	info_label.text = info_text

func _on_dynamic_action_pressed(action_id: String, action_name: String):
	"""Handle dynamic action button press"""
	log_message("[color=cyan]Selecting action: %s[/color]" % action_name)

	# Check if this is a submenu action
	var action = _get_action_by_id(action_id)
	if action.get("is_submenu", false):
		# Open appropriate submenu dialog instead of queuing
		if action_id == "hire_staff":
			_show_hiring_submenu()
		elif action_id == "fundraise":
			_show_fundraising_submenu()
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
	"""Show popup dialog with hiring options with keyboard support"""
	print("[MainUI] === HIRING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - simplest approach that doesn't interfere with input!
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(500, 400)
	dialog.size = Vector2(500, 400)
	# Center it manually
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 500) / 2,
		(get_viewport().get_visible_rect().size.y - 400) / 2
	)
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Add title label
	var title_label = Label.new()
	title_label.text = "Hire Staff - Choose a staff member:"
	title_label.add_theme_font_size_override("font_size", 16)
	title_label.add_theme_color_override("font_color", Color.CYAN)
	main_vbox.add_child(title_label)

	# Add spacing
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 15)
	main_vbox.add_child(spacer)

	# Create container for hiring buttons
	var vbox = VBoxContainer.new()
	main_vbox.add_child(vbox)

	# Get hiring options
	var hiring_options = GameActions.get_hiring_options()
	var current_state = game_manager.get_game_state()

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in hiring_options:
		var hire_id = option.get("id", "")
		var hire_name = option.get("name", "")
		var hire_desc = option.get("description", "")
		var hire_costs = option.get("costs", {})

		# Create button for this option with keyboard hint (LETTERS not numbers)
		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE  # Don't grab focus - let MainUI handle keys
		btn.mouse_filter = Control.MOUSE_FILTER_PASS  # Still allow mouse clicks
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		var btn_text = "[%s] %s ($%d, %d AP)" % [key_label, hire_name, hire_costs.get("money", 0), hire_costs.get("action_points", 0)]
		btn.text = btn_text

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
		btn.tooltip_text = hire_desc + "\n\nCosts: $%d, %d AP\n\nPress %d to select" % [hire_costs.get("money", 0), hire_costs.get("action_points", 0), button_index + 1]

		# Connect button
		btn.pressed.connect(func(): _on_hiring_option_selected(hire_id, hire_name, dialog))

		vbox.add_child(btn)
		buttons.append(btn)
		button_index += 1

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Hiring submenu opened, tracked %d buttons" % buttons.size())
	for i in range(buttons.size()):
		print("[MainUI]   Button %d: %s" % [i, buttons[i].text])

	# Add dialog to scene tree and show
	print("[MainUI] Adding dialog to scene tree...")
	add_child(dialog)
	dialog.visible = true
	dialog.z_index = 100  # Ensure it's on top
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === HIRING SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Active dialog: %s, Buttons: %d" % [active_dialog != null, active_dialog_buttons.size()])
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_hiring_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle hiring submenu selection"""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	log_message("[color=cyan]Hiring: %s[/color]" % action_name)

	# Queue the actual hiring action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func _show_fundraising_submenu():
	"""Show popup dialog with fundraising options with keyboard support"""
	print("[MainUI] === FUNDRAISING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - simplest approach that doesn't interfere with input!
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(550, 450)
	dialog.size = Vector2(550, 450)
	# Center it manually
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 550) / 2,
		(get_viewport().get_visible_rect().size.y - 450) / 2
	)
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Add title label
	var title_label = Label.new()
	title_label.text = "Fundraising Options - Choose your funding strategy:"
	title_label.add_theme_font_size_override("font_size", 16)
	title_label.add_theme_color_override("font_color", Color.CYAN)
	main_vbox.add_child(title_label)

	# Add spacing
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 15)
	main_vbox.add_child(spacer)

	# Create container for fundraising buttons
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	main_vbox.add_child(vbox)

	# Get fundraising options
	var funding_options = GameActions.get_fundraising_options()
	var current_state = game_manager.get_game_state()

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in funding_options:
		var fund_id = option.get("id", "")
		var fund_name = option.get("name", "")
		var fund_desc = option.get("description", "")
		var fund_costs = option.get("costs", {})
		var fund_gains = option.get("gains", {})

		# Create button for this option
		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE  # Don't grab focus - let MainUI handle keys
		btn.mouse_filter = Control.MOUSE_FILTER_PASS  # Still allow mouse clicks
		btn.custom_minimum_size = Vector2(500, 50)

		# Format costs
		var cost_text = ""
		if fund_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % fund_costs.get("action_points")
		if fund_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % fund_costs.get("reputation")
		if fund_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % fund_costs.get("papers")

		# Format gains
		var gain_text = ""
		if fund_gains.has("money_min") and fund_gains.has("money_max"):
			gain_text = "$%d-$%d" % [fund_gains.get("money_min"), fund_gains.get("money_max")]
		elif fund_gains.has("money"):
			gain_text = "$%d" % fund_gains.get("money")

		# Add keyboard hint (LETTERS not numbers)
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = "[%s] %s\n(%s → %s)" % [key_label, fund_name, cost_text if cost_text != "" else "Free", gain_text]

		# Check affordability
		var can_afford = true
		for resource in fund_costs.keys():
			if current_state.get(resource, 0) < fund_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.6, 0.6, 0.6)

		# Add tooltip
		btn.tooltip_text = fund_desc + "\n\nCosts: %s\nGains: %s\n\nPress %d to select" % [cost_text if cost_text != "" else "None", gain_text, button_index + 1]

		# Connect button
		btn.pressed.connect(func(): _on_fundraising_option_selected(fund_id, fund_name, dialog))

		vbox.add_child(btn)
		buttons.append(btn)
		button_index += 1

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Fundraising submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to scene tree and show
	print("[MainUI] Adding dialog to scene tree...")
	add_child(dialog)
	dialog.visible = true
	dialog.z_index = 100  # Ensure it's on top
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === FUNDRAISING SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_fundraising_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle fundraising submenu selection"""
	print("[MainUI] Fundraising option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	log_message("[color=cyan]Fundraising: %s[/color]" % action_name)

	# Queue the actual fundraising action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

func update_queued_actions_display():
	"""Update the visual queue display and message log"""
	# Clear existing queue items (except hint label)
	for child in queue_container.get_children():
		if child != queue_hint:
			child.queue_free()

	if queued_actions.size() > 0:
		# Hide hint, show queue items
		queue_hint.visible = false

		# Create visual queue items
		for action in queued_actions:
			var action_name = action.get("name", "Unknown")
			var action_id = action.get("id", "")

			# Create queue item panel
			var item = PanelContainer.new()
			item.custom_minimum_size = Vector2(120, 60)

			var vbox = VBoxContainer.new()
			item.add_child(vbox)

			# Action name label
			var label = Label.new()
			label.text = action_name
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label.autowrap_mode = TextServer.AUTOWRAP_WORD
			label.add_theme_font_size_override("font_size", 11)
			vbox.add_child(label)

			# AP cost indicator
			var action_def = _get_action_by_id(action_id)
			var ap_cost = action_def.get("costs", {}).get("action_points", 0)
			if ap_cost > 0:
				var ap_cost_label = Label.new()
				ap_cost_label.text = "-%d AP" % ap_cost
				ap_cost_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
				ap_cost_label.add_theme_color_override("font_color", Color(0.9, 0.7, 0.2))
				ap_cost_label.add_theme_font_size_override("font_size", 10)
				vbox.add_child(ap_cost_label)

			# Remove button (X)
			var remove_btn = Button.new()
			remove_btn.text = "✕ Remove"
			remove_btn.custom_minimum_size = Vector2(90, 24)
			remove_btn.add_theme_font_size_override("font_size", 9)

			# Capture action_id in closure for the callback
			var captured_id = action_id
			var captured_name = action_name
			remove_btn.pressed.connect(func(): _remove_queued_action(captured_id, captured_name))

			vbox.add_child(remove_btn)

			queue_container.add_child(item)

		# Log message
		var action_names = []
		for action in queued_actions:
			action_names.append(action.get("name", "Unknown"))
		log_message("[color=lime]Queued actions (%d): %s[/color]" % [queued_actions.size(), ", ".join(action_names)])
	else:
		# Show hint, hide items
		queue_hint.visible = true
		log_message("[color=gray]No actions queued[/color]")

	# Update button states based on queue (case-insensitive phase check)
	var phase_upper = current_turn_phase.to_upper()
	if phase_upper == "ACTION_SELECTION":
		var queue_empty = queued_actions.size() == 0
		clear_queue_button.disabled = queue_empty
		end_turn_button.disabled = queue_empty
		print("[MainUI] Updated button states: queue_size=%d, buttons_disabled=%s" % [queued_actions.size(), queue_empty])

func _on_event_triggered(event: Dictionary):
	"""Handle event trigger - show popup dialog"""
	print("[MainUI] === EVENT TRIGGERED: %s ===" % event.get("name", "Unknown"))

	log_message("[color=gold]EVENT: %s[/color]" % event.get("name", "Unknown"))

	# Create event dialog - use Panel for consistent input handling
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(600, 450)
	dialog.size = Vector2(600, 450)
	# Center it manually
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 600) / 2,
		(get_viewport().get_visible_rect().size.y - 450) / 2
	)
	print("[MainUI] Created Panel for event, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Add title
	var title_label = Label.new()
	title_label.text = event.get("name", "Event")
	title_label.add_theme_font_size_override("font_size", 18)
	title_label.add_theme_color_override("font_color", Color.GOLD)
	main_vbox.add_child(title_label)

	# Add description label
	var desc_label = Label.new()
	desc_label.text = event.get("description", "An event has occurred!")
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	desc_label.custom_minimum_size = Vector2(560, 0)
	main_vbox.add_child(desc_label)

	# Add spacing
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 20)
	main_vbox.add_child(spacer)

	# Create container for option buttons
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	main_vbox.add_child(vbox)

	# Add each option as a button
	var options = event.get("options", [])
	var current_state = game_manager.get_game_state()

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in options:
		var choice_id = option.get("id", "")
		var choice_text = option.get("text", "")
		var costs = option.get("costs", {})

		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE  # Don't grab focus - let MainUI handle keys
		btn.mouse_filter = Control.MOUSE_FILTER_PASS  # Still allow mouse clicks

		# Add keyboard hint (LETTERS not numbers)
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = "[%s] %s" % [key_label, choice_text]
		btn.custom_minimum_size = Vector2(500, 45)

		# Check affordability
		var can_afford = true
		var missing_resources = []

		for resource in costs.keys():
			var cost = costs[resource]
			var available = 0

			# Special handling for action_points - use event AP pool
			if resource == "action_points":
				available = current_state.get("event_ap", 0)
			else:
				available = current_state.get(resource, 0)

			if available < cost:
				can_afford = false
				if resource == "action_points":
					missing_resources.append("Event AP (need %s, have %s)" % [cost, available])
				else:
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
				var value_sign = "+" if value >= 0 else ""  # Renamed from 'sign' to avoid shadowing built-in function
				tooltip += "  %s: %s%s\n" % [resource, value_sign, value]

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
		buttons.append(btn)
		button_index += 1

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog for event...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Event dialog opened, tracked %d buttons" % buttons.size())

	# Add dialog to scene tree and show
	print("[MainUI] Adding event dialog to scene tree...")
	add_child(dialog)
	dialog.visible = true
	dialog.z_index = 100  # Ensure it's on top
	print("[MainUI] Event dialog added and made visible: %s" % dialog.visible)

	# Wait one frame
	await get_tree().process_frame
	print("[MainUI] === EVENT DIALOG SETUP COMPLETE ===")
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_event_choice_selected(event: Dictionary, choice_id: String, dialog: Control):
	"""Handle event choice selection"""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	log_message("[color=cyan]Event choice: %s[/color]" % choice_id)

	# Tell game manager to resolve event
	game_manager.resolve_event(event, choice_id)

func _on_action_hover(action: Dictionary, can_afford: bool, missing_resources: Array):
	"""Update info bar when hovering over an action"""
	var action_name = action.get("name", "Unknown")
	var action_desc = action.get("description", "")
	var action_costs = action.get("costs", {})

	# Build info text with enhanced formatting
	var info_text = "[b][color=cyan]%s[/color][/b] — %s" % [action_name, action_desc]

	# Add costs with icons/colors
	if not action_costs.is_empty():
		info_text += "\n[color=gray]├─[/color] [color=yellow]Costs:[/color] "
		var cost_parts = []

		# Format each resource cost with appropriate color
		if action_costs.has("action_points"):
			cost_parts.append("[color=magenta]%d AP[/color]" % action_costs["action_points"])
		if action_costs.has("money"):
			var money_k = action_costs["money"] / 1000.0
			if money_k >= 1:
				cost_parts.append("[color=gold]$%dk[/color]" % int(money_k))
			else:
				cost_parts.append("[color=gold]$%d[/color]" % action_costs["money"])
		if action_costs.has("reputation"):
			cost_parts.append("[color=orange]%d Rep[/color]" % action_costs["reputation"])
		if action_costs.has("papers"):
			cost_parts.append("[color=white]%d Papers[/color]" % action_costs["papers"])
		if action_costs.has("compute"):
			cost_parts.append("[color=blue]%.1f Compute[/color]" % action_costs["compute"])
		if action_costs.has("research"):
			cost_parts.append("[color=purple]%.1f Research[/color]" % action_costs["research"])

		info_text += " • ".join(cost_parts)

	# Show affordability with visual indicator
	info_text += "\n[color=gray]└─[/color] "
	if not can_afford:
		info_text += "[color=red]✗ CANNOT AFFORD[/color]"
		if missing_resources.size() > 0:
			info_text += " [color=gray](%s)[/color]" % missing_resources[0]
	else:
		info_text += "[color=lime]✓ READY TO USE[/color]"

	info_label.text = info_text

func _on_action_unhover():
	"""Reset info bar when mouse leaves action"""
	info_label.text = "[color=gray]Hover over actions to see details...[/color]"

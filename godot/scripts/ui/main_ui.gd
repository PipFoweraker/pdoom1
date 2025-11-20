extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements (TopBar now has all resources in one line)
@onready var turn_label = $TopBar/TurnLabel
@onready var money_label = $TopBar/MoneyLabel
@onready var compute_label = $TopBar/ComputeLabel
@onready var research_label = $TopBar/ResearchLabel
@onready var papers_label = $TopBar/PapersLabel
@onready var reputation_label = $TopBar/ReputationLabel
@onready var ap_label = $TopBar/APLabel
@onready var phase_label = $BottomBar/PhaseLabel
@onready var message_log = $ContentArea/RightPanel/MessageScroll/MessageLog
@onready var actions_list = $ContentArea/LeftPanel/ActionsScroll/ActionsList
@onready var upgrades_list = $ContentArea/RightPanel/UpgradesScroll/UpgradesList
@onready var info_label = $InfoBar/MarginContainer/InfoLabel
@onready var queue_container = $ContentArea/RightPanel/QueuePanel/QueueContainer
@onready var queue_hint = $ContentArea/RightPanel/QueuePanel/QueueContainer/QueueHint

@onready var init_button = $BottomBar/ControlButtons/InitButton
@onready var test_action_button = $BottomBar/ControlButtons/TestActionButton
@onready var reserve_ap_button = $BottomBar/ControlButtons/ReserveAPButton
@onready var clear_queue_button = $BottomBar/ControlButtons/ClearQueueButton
@onready var end_turn_button = $BottomBar/ControlButtons/EndTurnButton
@onready var commit_plan_button = $BottomBar/ControlButtons/CommitPlanButton
@onready var doom_meter = $ContentArea/MiddlePanel/CoreZone/RightZones/DoomMeterZone/DoomMeterPanel/MarginContainer/DoomMeter
@onready var numeric_doom_label = $ContentArea/MiddlePanel/CoreZone/RightZones/NumericDoomZone/NumericDoomLabel
@onready var game_over_screen = $"../GameOverScreen"
@onready var bug_report_panel = $"../BugReportPanel"
@onready var bug_report_button = $BottomBar/BugReportButton
@onready var office_cat = $ContentArea/MiddlePanel/CoreZone/CatZone/OfficeCat
@onready var tab_manager = get_parent()
@onready var roster_container = $ContentArea/MiddlePanel/EmployeeRosterZone/RosterScroll/RosterContainer

# Reference to GameManager
var game_manager: Node

# Track queued actions
var queued_actions: Array = []
var current_turn_phase: String = "NOT_STARTED"

# Active dialog state for keyboard shortcuts
var active_dialog: Control = null
var active_dialog_buttons: Array = []

# Event queue for sequential presentation (FIX: multiple events in same turn)
var event_queue: Array[Dictionary] = []
var is_showing_event: bool = false

func _ready():
	print("[MainUI] Initializing UI...")

	# Get GameManager reference
	game_manager = get_node("../../GameManager")

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
	_populate_upgrades()

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		# E key no longer switches to employee screen - employee info moving to main UI
		# (E key was previously handled by TabManager, now disabled)

		var key_char = char(event.unicode) if event.unicode > 0 else "?"
		print("[MainUI] _input called, keycode: %d (%s), active_dialog: %s, buttons: %d" % [event.keycode, key_char, active_dialog != null, active_dialog_buttons.size()])

		# CRITICAL: If dialog is active, handle ALL dialog inputs FIRST (before any game shortcuts)
		# This prevents ENTER/SPACE from triggering turn advancement while dialog is open
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

			# ESC key: only close submenu dialogs (hiring, fundraising), NOT event dialogs
			# Event dialogs must be completed to prevent soft-lock (issue #452)
			if event.keycode == KEY_ESCAPE:
				# Check if this is an event dialog by looking for "event_dialog" meta flag
				if active_dialog.has_meta("is_event_dialog"):
					# Event dialogs cannot be closed with ESC - player must make a choice
					print("[MainUI] ESC pressed but this is an event dialog - ignoring (must complete event)")
					get_viewport().set_input_as_handled()
					return
				else:
					# Submenu dialogs can be closed with ESC
					print("[MainUI] ESC pressed on submenu dialog - closing")
					active_dialog.queue_free()
					active_dialog = null
					active_dialog_buttons = []
					get_viewport().set_input_as_handled()
					return

			# IMPORTANT: Block ALL other keys when dialog is active to prevent:
			# - ENTER from triggering skip turn
			# - SPACE from triggering end turn
			# - Number keys from selecting actions
			# Only dialog-specific keys (Q/W/E/R/etc and ESC) should work
			print("[MainUI] Dialog active - blocking non-dialog key: %d" % event.keycode)
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

		# Space to end turn (with warnings)
		elif event.keycode == KEY_SPACE:
			if not end_turn_button.disabled:
				_on_end_turn_button_pressed()
				get_viewport().set_input_as_handled()

		# Enter to commit plan (no warnings)
		elif event.keycode == KEY_ENTER:
			if not commit_plan_button.disabled:
				_on_commit_plan_button_pressed()
				get_viewport().set_input_as_handled()

		# Backslash (\) or N key to open bug reporter (global hotkeys)
		elif event.keycode == KEY_BACKSLASH or event.keycode == KEY_N:
			if bug_report_panel:
				bug_report_panel.show_panel()
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
	# Find the VBoxContainer (icon_stack) first
	var icon_stack: VBoxContainer = null
	for child in actions_list.get_children():
		if child is VBoxContainer:
			icon_stack = child
			break

	if not icon_stack:
		return

	# Get buttons directly from stack (single column layout)
	var buttons = icon_stack.get_children()
	if index < buttons.size():
		var button = buttons[index] as Button
		if button and not button.disabled:
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
		warnings.append("[color=red]⚠️ CRITICAL: Low funds (%s) - Can't afford much![/color]" % GameConfig.format_money(current_state.money))

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

func _on_commit_plan_button_pressed():
	"""Commit queued actions AND reserve remaining AP (no warnings)"""
	var current_state = game_manager.get_game_state()
	var available_ap = current_state.get("available_ap", 0)

	# If there are queued actions, commit them + reserve balance
	if queued_actions.size() > 0:
		log_message("[color=cyan]Committing %d queued actions + reserving %d remaining AP...[/color]" % [queued_actions.size(), available_ap])
	else:
		# No queued actions - just reserve all AP (reactive strategy)
		log_message("[color=cyan]Committing plan: Reserving all %d AP for reactive responses...[/color]" % available_ap)

		# Queue a virtual "pass_turn" action to represent reactive strategy
		var reserve_action = {
			"id": "pass_turn",
			"name": "Reserve All AP",
			"description": "No planned actions - keep all AP available for responding to events",
			"ap_cost": 0,
			"money_cost": 0
		}
		queued_actions.append(reserve_action)
		update_queued_actions_display()

		# Directly append to game state queue (bypass select_action validation)
		# pass_turn is a virtual action representing "reserve all AP" strategy
		game_manager.state.queued_actions.append("pass_turn")

	# Clear local queue (will be repopulated after turn processes)
	queued_actions.clear()
	update_queued_actions_display()

	# Commit the plan
	game_manager.end_turn()

func _on_employee_tab_button_pressed():
	"""Switch to employee management screen - DISABLED: employee info moving to main UI"""
	# tab_manager.show_employee_screen()
	pass

func _on_bug_report_button_pressed():
	"""Open bug report panel"""
	if bug_report_panel:
		bug_report_panel.show_panel()

func _on_game_state_updated(state: Dictionary):
	print("[MainUI] State updated: ", state)

	# Update resource displays
	turn_label.text = "Turn: %d" % state.get("turn", 0)
	money_label.text = "Money: %s" % GameConfig.format_money(state.get("money", 0))
	compute_label.text = "Compute: %.1f" % state.get("compute", 0)
	research_label.text = "Research: %.1f" % state.get("research", 0)
	papers_label.text = "Papers: %d" % state.get("papers", 0)
	reputation_label.text = "Rep: %.0f" % state.get("reputation", 0)

	# Add employee blob display to AP label (using BBCode for RichTextLabel)
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)
	var blob_display = ""
	for _i in range(safety):
		blob_display += "[color=green]●[/color]"
	for _i in range(capability):
		blob_display += "[color=red]●[/color]"
	for _i in range(compute_eng):
		blob_display += "[color=dodger_blue]●[/color]"

	# Show AP split with remaining AP tracking
	var total_ap = state.get("action_points", 0)
	var committed_ap = state.get("committed_ap", 0)
	var reserved_ap = state.get("reserved_ap", 0)
	var remaining_ap = total_ap - committed_ap - reserved_ap

	# Color-code AP text based on remaining AP
	var ap_color_name = "white"  # Default
	if remaining_ap <= 0:
		ap_color_name = "red"  # Depleted
	elif remaining_ap == 1:
		ap_color_name = "yellow"  # Low
	elif remaining_ap < total_ap:
		ap_color_name = "lime"  # Partially committed

	# Build BBCode text for RichTextLabel
	var ap_text = ""
	if reserved_ap > 0:
		ap_text = "[color=%s]AP: %d (%d free, %d reserved)[/color]  %s" % [ap_color_name, total_ap, remaining_ap, reserved_ap, blob_display]
	elif committed_ap > 0:
		ap_text = "[color=%s]AP: %d (%d free, %d queued)[/color]  %s" % [ap_color_name, total_ap, remaining_ap, committed_ap, blob_display]
	else:
		ap_text = "[color=%s]AP: %d[/color]  %s" % [ap_color_name, total_ap, blob_display]

	ap_label.text = ap_text

	# Update doom displays (both text label and visual meter)
	var doom = state.get("doom", 0)
	var doom_momentum = state.get("doom_momentum", 0.0)

	# Update numeric doom display
	if numeric_doom_label:
		numeric_doom_label.text = "%.1f%%" % doom
		numeric_doom_label.modulate = ThemeManager.get_doom_color(doom)

	# Visual doom meter with momentum indicator
	if doom_meter:
		doom_meter.set_doom(doom, doom_momentum)

	# Update office cat for doom level and visibility
	if office_cat:
		office_cat.update_doom_level(doom / 100.0)  # Convert percentage to 0.0-1.0
		# Show cat if adopted, hide if not
		office_cat.visible = state.get("has_cat", false)

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
		commit_plan_button.disabled = true
		reserve_ap_button.disabled = true

		# Show game over screen with stats
		if game_over_screen:
			game_over_screen.show_game_over(victory, state)

	# Refresh upgrades list to update affordability
	_populate_upgrades()

	# Update employee roster display
	_update_employee_roster(state)

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
		commit_plan_button.disabled = true
	elif phase_name == "action_selection" or phase_name == "ACTION_SELECTION":
		phase_color = "green"
		phase_display = "ACTION SELECTION (Ready)"
		# End turn requires actions, commit plan is always available
		end_turn_button.disabled = (queued_actions.size() == 0)
		commit_plan_button.disabled = false
		clear_queue_button.disabled = (queued_actions.size() == 0)
	elif phase_name == "turn_end" or phase_name == "TURN_END":
		phase_color = "yellow"
		phase_display = "TURN END (Executing...)"
		end_turn_button.disabled = true
		commit_plan_button.disabled = true

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
	"""Populate action list with icon buttons in a grid layout"""
	print("[MainUI] Populating ", actions.size(), " actions as icon buttons")

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

	# Define category order
	var category_order = ["hiring", "resources", "research", "funding", "management", "influence", "strategic", "other"]

	# Define category colors
	var category_colors = {
		"hiring": ThemeManager.get_category_color("hiring"),
		"resources": ThemeManager.get_category_color("resources"),
		"research": ThemeManager.get_category_color("research"),
		"management": ThemeManager.get_category_color("management"),
		"influence": ThemeManager.get_category_color("influence"),
		"strategic": ThemeManager.get_category_color("strategic"),
		"funding": ThemeManager.get_category_color("funding"),
		"other": Color(0.8, 0.8, 0.8)
	}

	# Create a single-column vertical stack for icons on left edge
	var icon_stack = VBoxContainer.new()
	icon_stack.add_theme_constant_override("separation", 2)
	actions_list.add_child(icon_stack)

	# Create icon buttons - single column layout
	var action_index = 0  # Track index for keyboard shortcuts

	for category_key in category_order:
		if not categories.has(category_key):
			continue

		var category_actions = categories[category_key]
		if category_actions.is_empty():
			continue

		# Create icon buttons for actions in this category
		for action in category_actions:
			var action_id = action.get("id", "")
			var action_name = action.get("name", "Unknown")
			var action_cost = action.get("costs", {})

			# Create icon-only button (square, fills width)
			var icon_button = Button.new()
			icon_button.custom_minimum_size = Vector2(70, 70)  # Larger square icon buttons
			icon_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			icon_button.focus_mode = Control.FOCUS_NONE

			# Get icon texture
			var icon_texture = IconLoader.get_action_icon(action_id)
			if icon_texture:
				icon_button.icon = icon_texture
				icon_button.expand_icon = true
				icon_button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

			# Add keyboard shortcut number in corner (subtle)
			if action_index < 9:
				icon_button.text = str(action_index + 1)
				icon_button.add_theme_font_size_override("font_size", 9)
				icon_button.add_theme_color_override("font_color", Color(1, 1, 1, 0.5))

			action_index += 1

			# Check if player can afford this action
			var can_afford = true
			var missing_resources = []

			for resource in action_cost.keys():
				var cost = action_cost[resource]
				var available = current_state.get(resource, 0)

				if available < cost:
					can_afford = false
					missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

			# Style based on affordability and category
			if not can_afford:
				icon_button.disabled = true
				icon_button.modulate = Color(0.4, 0.4, 0.4)  # Dark gray for unaffordable
			else:
				# Apply category color tint
				var button_color = category_colors.get(category_key, Color(1.0, 1.0, 1.0))
				icon_button.modulate = Color(0.9, 0.9, 0.9).lerp(button_color, 0.4)

			# Simple tooltip for accessibility
			icon_button.tooltip_text = action_name

			# Connect button press
			icon_button.pressed.connect(func(): _on_dynamic_action_pressed(action_id, action_name))

			# Connect mouse hover for info bar
			icon_button.mouse_entered.connect(func(): _on_action_hover(action, can_afford, missing_resources))
			icon_button.mouse_exited.connect(func(): _on_action_unhover())

			# Add to stack
			icon_stack.add_child(icon_button)

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
		# Constrain button width to prevent extending into middle
		button.size_flags_horizontal = Control.SIZE_FILL
		button.custom_minimum_size = Vector2(0, 32)

		# If purchased, show differently
		if is_purchased:
			button.text = "✓ " + upgrade_name
			button.disabled = true
			button.modulate = Color(0.5, 1.0, 0.5)  # Green tint
		else:
			button.text = "%s (%s)" % [upgrade_name, GameConfig.format_money(upgrade_cost)]

			# Check affordability
			var can_afford = current_state.get("money", 0) >= upgrade_cost
			if not can_afford:
				button.disabled = true
				button.modulate = Color(0.6, 0.6, 0.6)

		# Tooltip
		var tooltip = upgrade_desc + "\n\nCost: %s" % GameConfig.format_money(upgrade_cost)
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
	info_text += "\n[color=gray]├─[/color] [color=yellow]Cost:[/color] [color=gold]%s[/color]" % GameConfig.format_money(upgrade_cost)

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
			info_text += "[color=red]✗ NEED %s MORE[/color]" % GameConfig.format_money(needed)

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
		elif action_id == "publicity":
			_show_publicity_submenu()
		elif action_id == "strategic":
			_show_strategic_submenu()
		return

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford action: %s[/color]" % action_name)
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
	"""Show popup dialog with candidate pool - shows actual available candidates"""
	print("[MainUI] === HIRING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(450, 400)
	dialog.size = Vector2(450, 400)
	# Position to the right of the left panel (icon stack)
	dialog.position = Vector2(90, 60)  # Just right of the 80px wide left panel
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 8)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "CANDIDATE POOL"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	main_vbox.add_child(header)

	# Get current state and candidate pool
	var current_state = game_manager.get_game_state()
	var candidate_pool = current_state.get("candidate_pool", [])

	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["1", "2", "3", "4", "5", "6"]

	if candidate_pool.size() == 0:
		# No candidates available
		var empty_label = Label.new()
		empty_label.text = "No candidates available.\nNew candidates arrive each turn."
		empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		empty_label.add_theme_font_size_override("font_size", 12)
		empty_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		main_vbox.add_child(empty_label)
	else:
		# Create scrollable list for candidates
		var scroll = ScrollContainer.new()
		scroll.custom_minimum_size = Vector2(0, 280)
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		main_vbox.add_child(scroll)

		var candidate_list = VBoxContainer.new()
		candidate_list.add_theme_constant_override("separation", 6)
		scroll.add_child(candidate_list)

		# Specialization colors
		var spec_colors = {
			"safety": Color(0.3, 0.8, 0.3),
			"capabilities": Color(0.8, 0.3, 0.3),
			"interpretability": Color(0.7, 0.3, 0.8),
			"alignment": Color(0.3, 0.7, 0.8)
		}

		var button_index = 0
		for candidate in candidate_pool:
			var candidate_panel = PanelContainer.new()
			candidate_panel.custom_minimum_size = Vector2(0, 50)

			var hbox = HBoxContainer.new()
			hbox.add_theme_constant_override("separation", 8)
			candidate_panel.add_child(hbox)

			# Keyboard shortcut indicator
			var key_label = Label.new()
			key_label.text = "[%s]" % dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
			key_label.add_theme_font_size_override("font_size", 10)
			key_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
			key_label.custom_minimum_size = Vector2(25, 0)
			hbox.add_child(key_label)

			# Specialization color indicator
			var spec = candidate.get("specialization", "safety")
			var indicator = Label.new()
			indicator.text = "●"
			indicator.add_theme_color_override("font_color", spec_colors.get(spec, Color.WHITE))
			indicator.add_theme_font_size_override("font_size", 14)
			hbox.add_child(indicator)

			# Candidate info VBox
			var info_vbox = VBoxContainer.new()
			info_vbox.add_theme_constant_override("separation", 2)
			info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			hbox.add_child(info_vbox)

			# Name and specialization
			var name_label = Label.new()
			var spec_name = spec.capitalize()
			name_label.text = "%s - %s" % [candidate.get("name", "Unknown"), spec_name]
			name_label.add_theme_font_size_override("font_size", 11)
			info_vbox.add_child(name_label)

			# Stats line: Skill, Salary, Traits
			var stats_label = Label.new()
			var skill = candidate.get("skill_level", 5)
			var salary = candidate.get("current_salary", 60000)
			var traits = candidate.get("traits", [])
			var trait_text = ""
			if traits.size() > 0:
				var trait_names = []
				for trait_id in traits:
					# Get display name for trait
					if Researcher.POSITIVE_TRAITS.has(trait_id):
						trait_names.append(Researcher.POSITIVE_TRAITS[trait_id]["name"])
					elif Researcher.NEGATIVE_TRAITS.has(trait_id):
						trait_names.append(Researcher.NEGATIVE_TRAITS[trait_id]["name"])
					else:
						trait_names.append(trait_id.capitalize())
				trait_text = " [%s]" % ", ".join(trait_names)

			stats_label.text = "Skill %d | %s/yr%s" % [skill, GameConfig.format_money(salary), trait_text]
			stats_label.add_theme_font_size_override("font_size", 9)
			stats_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
			info_vbox.add_child(stats_label)

			# Hire button
			var hire_btn = Button.new()
			hire_btn.text = "Hire"
			hire_btn.custom_minimum_size = Vector2(50, 30)
			hire_btn.focus_mode = Control.FOCUS_NONE

			# Get standard hiring cost from action definitions
			var action_id = "hire_%s_researcher" % spec
			var hire_cost = 60000  # Default
			var hiring_options = GameActions.get_hiring_options()
			for option in hiring_options:
				if option.get("id") == action_id:
					hire_cost = option.get("costs", {}).get("money", 60000)
					break

			var can_afford = current_state.get("money", 0) >= hire_cost and current_state.get("action_points", 0) >= 1

			if not can_afford:
				hire_btn.disabled = true
				hire_btn.modulate = Color(0.5, 0.5, 0.5)

			hire_btn.tooltip_text = "Hire for %s + 1 AP" % GameConfig.format_money(hire_cost)

			# Store candidate reference for hire action
			var candidate_ref = candidate
			hire_btn.pressed.connect(func(): _on_candidate_hired(candidate_ref, dialog))

			hbox.add_child(hire_btn)
			buttons.append(hire_btn)

			candidate_list.add_child(candidate_panel)
			button_index += 1

	# Pool status
	var status_label = Label.new()
	status_label.text = "Pool: %d/6 candidates | New arrivals each turn" % candidate_pool.size()
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(status_label)

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Hiring submenu opened with %d candidates" % candidate_pool.size())

	# Add dialog to TabManager (parent) so it overlays everything without shifting layout
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === HIRING SUBMENU SETUP COMPLETE ===")

func _on_candidate_hired(candidate: Dictionary, dialog: Control):
	"""Handle hiring a specific candidate from the pool"""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Get the candidate's specialization to determine which hire action to use
	var spec = candidate.get("specialization", "safety")
	var action_id = "hire_%s_researcher" % spec
	var candidate_name = candidate.get("name", "Unknown")

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP to hire: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford to hire: %s[/color]" % candidate_name)
		return

	log_message("[color=cyan]Hiring: %s (%s)[/color]" % [candidate_name, spec.capitalize()])

	# Queue the hiring action
	queued_actions.append({"id": action_id, "name": "Hire " + candidate_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func _on_hiring_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle hiring submenu selection"""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Hiring: %s[/color]" % action_name)

	# Queue the actual hiring action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func _show_fundraising_submenu():
	"""Show popup dialog with fundraising options with keyboard support - icon grid layout"""
	print("[MainUI] === FUNDRAISING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	# Position to the right of the left panel (icon stack) - same as hiring submenu
	dialog.position = Vector2(90, 80)  # Just right of the 80px wide left panel
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

	# Get fundraising options
	var funding_options = GameActions.get_fundraising_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons (same layout as hiring submenu)
	var grid = GridContainer.new()
	grid.columns = 3  # 3 icons per row
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in funding_options:
		var fund_id = option.get("id", "")
		var fund_name = option.get("name", "")
		var fund_desc = option.get("description", "")
		var fund_costs = option.get("costs", {})
		var fund_gains = option.get("gains", {})

		# Create VBox for icon + label (same as hiring submenu)
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(100, 80)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(fund_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
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

		# Format gains for tooltip
		var gain_text = ""
		if fund_gains.has("money_min") and fund_gains.has("money_max"):
			gain_text = "%s-%s" % [GameConfig.format_money(fund_gains.get("money_min")), GameConfig.format_money(fund_gains.get("money_max"))]
		elif fund_gains.has("money"):
			gain_text = GameConfig.format_money(fund_gains.get("money"))

		# Check affordability
		var can_afford = true
		for resource in fund_costs.keys():
			if current_state.get(resource, 0) < fund_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s\nGains: %s" % [fund_name, fund_desc, cost_text if cost_text != "" else "Free", gain_text]

		# Connect button
		btn.pressed.connect(func(): _on_fundraising_option_selected(fund_id, fund_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon (shortened names)
		var name_label = Label.new()
		# Shorten common suffixes for cleaner display
		var short_name = fund_name.replace(" Funding", "").replace("Publish ", "")
		name_label.text = short_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "Costs vary: 0-2 Papers, 0-20 Rep"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Fundraising submenu opened, tracked %d buttons" % buttons.size())
	for i in range(buttons.size()):
		print("[MainUI]   Button %d: %s" % [i, buttons[i].text])

	# Add dialog to TabManager (parent) so it overlays everything without shifting layout
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === FUNDRAISING SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Active dialog: %s, Buttons: %d" % [active_dialog != null, active_dialog_buttons.size()])
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_fundraising_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle fundraising submenu selection"""
	print("[MainUI] Fundraising option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Fundraising: %s[/color]" % action_name)

	# Queue the actual fundraising action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

func _show_publicity_submenu():
	"""Show popup dialog with publicity/influence options with keyboard support - icon grid layout"""
	print("[MainUI] === PUBLICITY SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	# Position to the right of the left panel (icon stack)
	dialog.position = Vector2(90, 80)  # Just right of the 80px wide left panel
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

	# Get publicity options
	var publicity_options = GameActions.get_publicity_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons (same layout as other submenus)
	var grid = GridContainer.new()
	grid.columns = 3  # 3 icons per row
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in publicity_options:
		var pub_id = option.get("id", "")
		var pub_name = option.get("name", "")
		var pub_desc = option.get("description", "")
		var pub_costs = option.get("costs", {})

		# Create VBox for icon + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(100, 80)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(pub_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if pub_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % pub_costs.get("action_points")
		if pub_costs.get("money", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += GameConfig.format_money(pub_costs.get("money"))
		if pub_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % pub_costs.get("reputation")
		if pub_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % pub_costs.get("papers")

		# Check affordability
		var can_afford = true
		for resource in pub_costs.keys():
			if current_state.get(resource, 0) < pub_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [pub_name, pub_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_publicity_option_selected(pub_id, pub_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon (shortened names)
		var name_label = Label.new()
		var short_name = pub_name.replace(" Campaign", "").replace("Open Source ", "")
		name_label.text = short_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "Build influence and public awareness"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state for keyboard handling
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Publicity submenu opened, tracked %d buttons" % buttons.size())
	for i in range(buttons.size()):
		print("[MainUI]   Button %d: %s" % [i, buttons[i].text])

	# Add dialog to TabManager as overlay
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === PUBLICITY SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Active dialog: %s, Buttons: %d" % [active_dialog != null, active_dialog_buttons.size()])
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_publicity_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle publicity submenu selection"""
	print("[MainUI] Publicity option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Publicity: %s[/color]" % action_name)

	# Queue the actual publicity action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

func _show_strategic_submenu():
	"""Show popup dialog with strategic/high-stakes options with keyboard support - icon grid layout"""
	print("[MainUI] === STRATEGIC SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	dialog.position = Vector2(90, 80)
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

	# Get strategic options
	var strategic_options = GameActions.get_strategic_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons
	var grid = GridContainer.new()
	grid.columns = 2  # 2 icons per row for strategic (fewer options, larger display)
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in strategic_options:
		var strat_id = option.get("id", "")
		var strat_name = option.get("name", "")
		var strat_desc = option.get("description", "")
		var strat_costs = option.get("costs", {})

		# Create VBox for icon + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(120, 90)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(strat_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if strat_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % strat_costs.get("action_points")
		if strat_costs.get("money", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += GameConfig.format_money(strat_costs.get("money"))
		if strat_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % strat_costs.get("reputation")
		if strat_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % strat_costs.get("papers")

		# Check affordability
		var can_afford = true
		for resource in strat_costs.keys():
			if current_state.get(resource, 0) < strat_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [strat_name, strat_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_strategic_option_selected(strat_id, strat_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon
		var name_label = Label.new()
		name_label.text = strat_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "High-stakes moves - use wisely!"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.3))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Strategic submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to TabManager as overlay
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

	await get_tree().process_frame
	print("[MainUI] === STRATEGIC SUBMENU SETUP COMPLETE ===")

func _on_strategic_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle strategic submenu selection"""
	print("[MainUI] Strategic option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Strategic: %s[/color]" % action_name)

	# Queue the actual strategic action
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
	"""Handle event trigger - queue event for sequential presentation"""
	print("[MainUI] === EVENT TRIGGERED: %s ===" % event.get("name", "Unknown"))

	# Add to event queue
	event_queue.append(event)
	print("[MainUI] Event queued. Queue size: %d" % event_queue.size())

	# If not currently showing an event, show this one immediately
	if not is_showing_event:
		_show_next_event()
	else:
		print("[MainUI] Event added to queue, will show after current event resolves")

func _show_next_event():
	"""Show the next event in queue (sequential presentation)"""
	if event_queue.is_empty():
		print("[MainUI] Event queue empty, no more events to show")
		is_showing_event = false
		return

	# Mark that we're showing an event
	is_showing_event = true

	# Get next event from queue
	var event = event_queue.pop_front()
	print("[MainUI] === SHOWING EVENT: %s ===" % event.get("name", "Unknown"))
	print("[MainUI] Remaining events in queue: %d" % event_queue.size())

	log_message("[color=gold]EVENT: %s[/color]" % event.get("name", "Unknown"))

	# Blurred blocker behind event dialog panel (Fix Issue #485)
	var click_blocker := ColorRect.new()
	click_blocker.color = Color(0.0, 0.0, 0.0, 0.6)
	click_blocker.mouse_filter = Control.MOUSE_FILTER_STOP
	click_blocker.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tab_manager.add_child(click_blocker)

	# Create event dialog - use Panel for consistent input handling
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(600, 450)
	dialog.size = Vector2(600, 450)
	# Center it manually
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 600) / 2,
		(get_viewport().get_visible_rect().size.y - 450) / 2
	)

	# Add forest green background for better visibility
	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = Color(0.15, 0.25, 0.15, 1.0)  # Dark forest green
	panel_style.border_width_left = 3
	panel_style.border_width_top = 3
	panel_style.border_width_right = 3
	panel_style.border_width_bottom = 3
	panel_style.border_color = Color(0.3, 0.5, 0.3, 1.0)  # Lighter green border
	panel_style.corner_radius_top_left = 8
	panel_style.corner_radius_top_right = 8
	panel_style.corner_radius_bottom_right = 8
	panel_style.corner_radius_bottom_left = 8
	dialog.add_theme_stylebox_override("panel", panel_style)

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

		# Add button border for better definition
		var button_style = StyleBoxFlat.new()
		button_style.bg_color = Color(0.2, 0.2, 0.2, 1.0)  # Dark gray background
		button_style.border_width_left = 2
		button_style.border_width_top = 2
		button_style.border_width_right = 2
		button_style.border_width_bottom = 2
		button_style.border_color = Color(0.15, 0.15, 0.15, 1.0)  # Slightly darker border
		button_style.corner_radius_top_left = 4
		button_style.corner_radius_top_right = 4
		button_style.corner_radius_bottom_right = 4
		button_style.corner_radius_bottom_left = 4
		btn.add_theme_stylebox_override("normal", button_style)

		# Hover state
		var button_style_hover = button_style.duplicate()
		button_style_hover.bg_color = Color(0.3, 0.3, 0.3, 1.0)  # Lighter on hover
		btn.add_theme_stylebox_override("hover", button_style_hover)

		# Check affordability
		var can_afford = true
		var missing_resources = []

		for resource in costs.keys():
			var cost = costs[resource]
			var available = 0

			# Special handling for action_points - use available (uncommitted) AP
			# Events can use any AP that hasn't been committed to actions yet
			if resource == "action_points":
				available = current_state.get("available_ap", 0)
			else:
				available = current_state.get(resource, 0)

			if available < cost:
				can_afford = false
				if resource == "action_points":
					missing_resources.append("AP (need %s, have %s available)" % [cost, available])
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
		btn.pressed.connect(func(): _on_event_choice_selected(event, choice_id, dialog, click_blocker))

		vbox.add_child(btn)
		buttons.append(btn)
		button_index += 1

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog for event...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Event dialog opened, tracked %d buttons" % buttons.size())

	# Mark this as an event dialog to prevent ESC from closing it (issue #452)
	dialog.set_meta("is_event_dialog", true)

	# Add dialog to TabManager (parent) so it overlays everything without shifting layout
	print("[MainUI] Adding event dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[MainUI] Event dialog added and made visible: %s" % dialog.visible)

	# Wait one frame
	await get_tree().process_frame
	print("[MainUI] === EVENT DIALOG SETUP COMPLETE ===")
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_event_choice_selected(event: Dictionary, choice_id: String, dialog: Control, blocker: Control):
	"""Handle event choice selection"""
	dialog.queue_free()
	blocker.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	log_message("[color=cyan]Event choice: %s[/color]" % choice_id)

	# Tell game manager to resolve event
	game_manager.resolve_event(event, choice_id)

	# Show next event in queue if any
	if not event_queue.is_empty():
		print("[MainUI] Event resolved, showing next event in queue...")
		# Wait one frame to ensure dialog is cleaned up before showing next
		await get_tree().process_frame
		_show_next_event()
	else:
		print("[MainUI] Event resolved, queue empty")
		is_showing_event = false

func _on_action_hover(action: Dictionary, can_afford: bool, missing_resources: Array):
	"""Update info bar when hovering over an action and highlight affected resources"""
	var action_name = action.get("name", "Unknown")
	var action_desc = action.get("description", "")
	var action_costs = action.get("costs", {})

	# Build info text with enhanced formatting
	var info_text = "[b][color=cyan]%s[/color][/b] — %s" % [action_name, action_desc]

	# Add costs with icons/colors (always add line for consistent 2-line format)
	info_text += "\n[color=gray]├─[/color] "
	if not action_costs.is_empty():
		info_text += "[color=yellow]Costs:[/color] "
		var cost_parts = []

		# Format each resource cost with appropriate color
		if action_costs.has("action_points"):
			cost_parts.append("[color=magenta]%d AP[/color]" % action_costs["action_points"])
		if action_costs.has("money"):
			cost_parts.append("[color=gold]%s[/color]" % GameConfig.format_money(action_costs["money"]))
		if action_costs.has("reputation"):
			cost_parts.append("[color=orange]%d Rep[/color]" % action_costs["reputation"])
		if action_costs.has("papers"):
			cost_parts.append("[color=white]%d Papers[/color]" % action_costs["papers"])
		if action_costs.has("compute"):
			cost_parts.append("[color=blue]%.1f Compute[/color]" % action_costs["compute"])
		if action_costs.has("research"):
			cost_parts.append("[color=purple]%.1f Research[/color]" % action_costs["research"])

		info_text += " • ".join(cost_parts)
	else:
		info_text += "[color=gray]No costs[/color]"

	# Show affordability with visual indicator
	info_text += "\n[color=gray]└─[/color] "
	if not can_afford:
		info_text += "[color=red]✗ CANNOT AFFORD[/color]"
		if missing_resources.size() > 0:
			info_text += " [color=gray](%s)[/color]" % missing_resources[0]
	else:
		info_text += "[color=lime]✓ READY TO USE[/color]"

	info_label.text = info_text

	# Highlight affected resource labels in top bar
	_highlight_resources(action_costs)

func _on_action_unhover():
	"""Reset info bar when mouse leaves action - maintain 2-line format to prevent flicker (issue #450)"""
	info_label.text = "[color=gray]Hover over actions to see details...\n [/color]"
	# Reset resource highlights
	_reset_resource_highlights()

func _highlight_resources(costs: Dictionary):
	"""Highlight resource labels that will be affected by an action"""
	# Map cost keys to label references (excluding ap_label which is RichTextLabel)
	var resource_label_map = {
		"money": money_label,
		"compute": compute_label,
		"research": research_label,
		"papers": papers_label,
		"reputation": reputation_label
	}

	# Highlight each affected resource with a yellow/gold tint
	for resource in costs.keys():
		if resource_label_map.has(resource):
			var label = resource_label_map[resource]
			if label:
				label.add_theme_color_override("font_color", Color(1.0, 0.9, 0.3))  # Gold highlight

func _reset_resource_highlights():
	"""Reset all resource labels to default color"""
	# Regular labels
	var labels = [money_label, compute_label, research_label, papers_label, reputation_label]
	for label in labels:
		if label:
			label.remove_theme_color_override("font_color")
	# ap_label is RichTextLabel - skip color override reset (it uses BBCode colors)

func _update_employee_roster(state: Dictionary):
	"""Update the employee roster display in the middle panel"""
	if not roster_container:
		return

	# Clear existing roster entries
	for child in roster_container.get_children():
		child.queue_free()

	# Get researchers from state
	var researchers = state.get("researchers", [])

	# If no individual researchers, show legacy counts
	if researchers.is_empty():
		var safety = state.get("safety_researchers", 0)
		var capability = state.get("capability_researchers", 0)
		var compute_eng = state.get("compute_engineers", 0)
		var managers = state.get("managers", 0)

		if safety + capability + compute_eng + managers == 0:
			var empty_label = Label.new()
			empty_label.text = "No staff hired"
			empty_label.add_theme_font_size_override("font_size", 10)
			empty_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
			empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			roster_container.add_child(empty_label)
		else:
			# Show legacy count display
			_add_legacy_staff_display(safety, capability, compute_eng, managers)
		return

	# Show individual researchers
	for researcher_data in researchers:
		var entry = _create_researcher_button(researcher_data)
		roster_container.add_child(entry)

func _add_legacy_staff_display(safety: int, capability: int, compute_eng: int, managers: int):
	"""Show simple staff counts (legacy mode)"""
	var staff_types = [
		{"name": "Safety", "count": safety, "color": Color(0.3, 0.8, 0.3)},
		{"name": "Capability", "count": capability, "color": Color(0.8, 0.3, 0.3)},
		{"name": "Engineers", "count": compute_eng, "color": Color(0.3, 0.5, 0.8)},
		{"name": "Managers", "count": managers, "color": Color(0.7, 0.7, 0.3)}
	]

	for staff_type in staff_types:
		if staff_type["count"] > 0:
			var hbox = HBoxContainer.new()
			hbox.add_theme_constant_override("separation", 4)

			# Color indicator
			var indicator = Label.new()
			indicator.text = "●"
			indicator.add_theme_color_override("font_color", staff_type["color"])
			indicator.add_theme_font_size_override("font_size", 12)
			hbox.add_child(indicator)

			# Count and name
			var name_label = Label.new()
			name_label.text = "%s: %d" % [staff_type["name"], staff_type["count"]]
			name_label.add_theme_font_size_override("font_size", 10)
			name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
			hbox.add_child(name_label)

			roster_container.add_child(hbox)

# Old researcher entry: non-interactive panel item
func _create_researcher_entry(data: Dictionary) -> Control:
	"""Create a roster entry for an individual researcher"""
	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(0, 24)

	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 6)
	panel.add_child(hbox)

	# Specialization color indicator
	var spec_colors = {
		"safety": Color(0.3, 0.8, 0.3),
		"capabilities": Color(0.8, 0.3, 0.3),
		"interpretability": Color(0.7, 0.3, 0.8),
		"alignment": Color(0.3, 0.7, 0.8)
	}

	var spec = data.get("specialization", "safety")
	var indicator = Label.new()
	indicator.text = "●"
	indicator.add_theme_color_override("font_color", spec_colors.get(spec, Color.WHITE))
	indicator.add_theme_font_size_override("font_size", 10)
	hbox.add_child(indicator)

	# Name
	var name_label = Label.new()
	name_label.text = data.get("name", "Unknown")
	name_label.add_theme_font_size_override("font_size", 9)
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(name_label)

	# Productivity indicator (simple bar or percentage)
	var productivity = data.get("base_productivity", 1.0)
	var burnout = data.get("burnout", 0.0)
	var effective_prod = productivity * (1.0 - min(burnout / 200.0, 0.5))

	var prod_label = Label.new()
	prod_label.text = "%.0f%%" % (effective_prod * 100)
	prod_label.add_theme_font_size_override("font_size", 9)

	# Color based on productivity
	if effective_prod >= 1.0:
		prod_label.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	elif effective_prod >= 0.7:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.3))
	else:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))

	hbox.add_child(prod_label)

	# Burnout warning if high
	if burnout >= 60:
		var burnout_icon = Label.new()
		burnout_icon.text = "🔥"
		burnout_icon.add_theme_font_size_override("font_size", 8)
		hbox.add_child(burnout_icon)

	return panel

# New researcher entry: interactive button
func _create_researcher_button(data: Dictionary) -> Control:
	"""Create a roster entry/button for an individual researcher"""
	var btn := Button.new()
	btn.custom_minimum_size = Vector2(0, 32)
	btn.focus_mode = Control.FOCUS_NONE
	btn.size_flags_horizontal = Control.SIZE_FILL
	#btn.clip_contents = false

	# Margin/Padding - ensures text does not render so close to box walls
	var margin := MarginContainer.new()
	#var margin_padding = 8
	#margin.add_theme_constant_override("margin_left", margin_padding)
	#margin.add_theme_constant_override("margin_right", margin_padding)
	btn.add_child(margin)

	# Main Row
	var hbox := HBoxContainer.new()
	var hbox_separation = 8
	hbox.add_theme_constant_override("separation", hbox_separation)
	hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	margin.add_child(hbox)

	# Specialization Colours - should this be global/callable?
	var spec_colors = {
		"safety": Color(0.3, 0.8, 0.3),
		"capabilities": Color(0.8, 0.3, 0.3),
		"interpretability": Color(0.7, 0.3, 0.8),
		"alignment": Color(0.3, 0.7, 0.8)
	}

	# Specialisation Indicator 
	var spec = data.get("specialization", "safety")
	var indicator := Label.new()
	indicator.text = "●"
	indicator.add_theme_color_override("font_color", spec_colors.get(spec, Color.WHITE))
	hbox.add_child(indicator)

	# Name Label
	var name_label := Label.new()
	name_label.text = data.get("name", "Unknown")
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	name_label.add_theme_font_size_override("separation", 8)
	hbox.add_child(name_label)

	# Productivity Indicator (simple bar or percentage)
	var productivity = data.get("base_productivity", 1.0)
	var burnout = data.get("burnout", 0.0)
	var effective_prod = productivity * (1.0 - min(burnout / 200.0, 0.5))

	var prod_label := Label.new()
	prod_label.text = "%.0f%%" % (effective_prod * 100)
	prod_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	# Color logic - based on employee productivity
	if effective_prod >= 1.0:
		prod_label.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	elif effective_prod >= 0.7:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.3))
	else:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))

	hbox.add_child(prod_label)

	# Burnout warning if high
	if burnout >= 60:
		var burnout_icon = Label.new()
		burnout_icon.text = "🔥"
		#burnout_icon.add_theme_font_size_override("font_size", 8)
		hbox.add_child(burnout_icon)

	# When staff button is pressed, show extra detail
	btn.pressed.connect(
		func(): _show_staff_id_card(data)
	)
	
	return btn

func _show_staff_id_card(data: Dictionary):
	"""Create an ID card for an individual researcher"""
	# TODO: Adjust formatting
	# My vision is to either have this look like an employee ID, or something similar to back of a sports trading card
	var card = PopupPanel.new()
	card.name = "StaffCard"
	card.size = Vector2(350,300)
	add_child(card)
	
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	card.add_child(vbox)
	
	var employee_label = Label.new()
	var name_text = data.get("name")
	var spec_text = data.get("specialization")
	
	employee_label.text = "%s | %s" % [name_text, spec_text.capitalize()]
	employee_label.add_theme_font_size_override("font_size", 20)
	vbox.add_child(employee_label)
	
	var trait_label = Label.new()
	var traits = data.get("traits", [])
	if traits.size() > 0:
		var trait_names := [];
		for trait_id in traits:
			if Researcher.POSITIVE_TRAITS.has(trait_id):
				trait_names.append(Researcher.POSITIVE_TRAITS[trait_id]["name"])
			elif Researcher.NEGATIVE_TRAITS.has(trait_id):
				trait_names.append(Researcher.NEGATIVE_TRAITS[trait_id]["name"])
			else:
				trait_names.append(trait_id.capitalize())
		trait_label.text = "HR Notes: %s" % ", ".join(trait_names)
	else:
		trait_label.text = "HR Notes: N/A"
	vbox.add_child(trait_label)
	
	var salary_label = Label.new()
	var salaty_text = data.get("current_salary")
	# maybe this could be per turn? More useful stat for user
	salary_label.text = "Current Salary: %s/yr" % GameConfig.format_money(salaty_text) 
	vbox.add_child(salary_label)
	
	var skill_label = Label.new()
	skill_label.text = "Skill Level: %d / 10" % data.get("skill_level")
	vbox.add_child(skill_label)
	
	var base_prod_label = Label.new()
	base_prod_label.text = "Base Productivity: %d" % data.get("base_productivity")
	vbox.add_child(base_prod_label)
	
	var burn_label = Label.new()
	burn_label.text = "Burnout: %d" % data.get("burnout")
	vbox.add_child(burn_label)
	
	card.popup_centered()

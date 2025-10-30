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

func _ready():
	print("[MainUI] Initializing UI...")

	# Get GameManager reference
	game_manager = get_node("../GameManager")

	# Connect to GameManager signals
	game_manager.game_state_updated.connect(_on_game_state_updated)
	game_manager.turn_phase_changed.connect(_on_turn_phase_changed)
	game_manager.action_executed.connect(_on_action_executed)
	game_manager.error_occurred.connect(_on_error_occurred)

	log_message("[color=yellow]UI Ready. Click 'Init Game' to start.[/color]")

func _on_init_button_pressed():
	log_message("[color=cyan]Initializing game...[/color]")
	init_button.disabled = true
	game_manager.start_new_game("test-seed")

func _on_test_action_button_pressed():
	log_message("[color=cyan]Selecting action: hire_safety_researcher[/color]")
	game_manager.select_action("hire_safety_researcher")

func _on_end_turn_button_pressed():
	log_message("[color=cyan]Ending turn...[/color]")
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
		end_turn_button.disabled = false
		init_button.disabled = true

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
	phase_label.text = "Phase: " + phase_name

	log_message("[color=magenta]Turn Phase: " + phase_name + "[/color]")

	# Handle pending events
	if phase_info.has("pending_events") and phase_info["pending_events"].size() > 0:
		log_message("[color=yellow]Events triggered! (Event UI not implemented yet)[/color]")
		for event in phase_info["pending_events"]:
			log_message("[color=yellow]  - " + str(event.get("name", "Unknown Event")) + "[/color]")

func _on_action_executed(result: Dictionary):
	print("[MainUI] Action executed: ", result)

	var message = result.get("message", "Action completed")
	log_message("[color=lime]" + message + "[/color]")

	# Show any additional messages from action
	if result.has("messages"):
		for msg in result.get("messages", []):
			log_message("[color=white]  " + str(msg) + "[/color]")

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

extends Node
## Pure GDScript game manager - NO Python bridge

signal game_state_updated(state: Dictionary)
signal turn_phase_changed(phase: String)
signal actions_available(actions: Array)
signal action_executed(result: Dictionary)
signal error_occurred(error_msg: String)
signal event_triggered(event: Dictionary)

# Game objects
var state: GameState
var turn_manager: TurnManager
var is_initialized: bool = false

func _ready():
	print("[GameManager] Pure GDScript version ready")

func start_new_game(game_seed: String = ""):
	"""Initialize new game - pure GDScript - FIX #418: Handle initial events"""
	# Get config from GameConfig singleton if seed not provided
	if game_seed.is_empty():
		game_seed = GameConfig.get_display_seed()

	print("[GameManager] Starting new game")
	print("  Player: %s" % GameConfig.player_name)
	print("  Lab: %s" % GameConfig.lab_name)
	print("  Seed: %s" % game_seed)
	print("  Difficulty: %s" % GameConfig.get_difficulty_string())

	state = GameState.new(game_seed)

	# Apply difficulty settings to game state
	_apply_difficulty_settings()

	turn_manager = TurnManager.new(state)
	is_initialized = true

	# Start first turn (may trigger events!)
	var turn_result = turn_manager.start_turn()

	# Emit initial state
	game_state_updated.emit(state.to_dict())

	# Emit phase (might be turn_start if events, or action_selection if not)
	turn_phase_changed.emit(turn_result["phase"])

	# Check for initial events (FIX #418)
	if turn_result.has("triggered_events") and turn_result["triggered_events"].size() > 0:
		print("[GameManager] Initial events triggered!")
		for event in turn_result["triggered_events"]:
			event_triggered.emit(event)
	else:
		# No events, emit available actions
		var actions = turn_manager.get_available_actions()
		actions_available.emit(actions)

	print("[GameManager] Game initialized - Turn %d" % state.turn)

func select_action(action_id: String):
	"""Queue action for execution with immediate AP deduction - FIX #418: Block if events pending"""
	if not is_initialized:
		error_occurred.emit("Game not initialized")
		return

	# BLOCK action selection if events are pending (FIX #418)
	if state.pending_events.size() > 0:
		error_occurred.emit("Resolve pending events before selecting actions!")
		return

	# BLOCK action selection if not in ACTION_SELECTION phase (FIX #418)
	if state.current_phase != GameState.TurnPhase.ACTION_SELECTION:
		error_occurred.emit("Cannot select actions in current phase")
		return

	# Get action details to check AP cost
	var action = _get_action_by_id(action_id)
	if not action:
		error_occurred.emit("Action not found: " + action_id)
		return

	var ap_cost = action.get("costs", {}).get("action_points", 0)

	# Check if player has enough AP
	if state.action_points < ap_cost:
		error_occurred.emit("Not enough AP for " + action.get("name", action_id))
		return

	# Check if player can afford the action
	if not state.can_afford(action.get("costs", {})):
		error_occurred.emit("Cannot afford " + action.get("name", action_id))
		return

	# Deduct AP immediately (like old game)
	state.action_points -= ap_cost

	print("[GameManager] Action queued: %s (AP cost: %d, remaining: %d)" % [action_id, ap_cost, state.action_points])
	state.queued_actions.append(action_id)

	action_executed.emit({
		"success": true,
		"message": "Action queued: " + action.get("name", action_id)
	})

	# Emit updated state to refresh UI
	game_state_updated.emit(state.to_dict())

func _get_action_by_id(action_id: String) -> Dictionary:
	"""Helper to get action by ID"""
	var all_actions = GameActions.get_all_actions()
	for action in all_actions:
		if action.get("id") == action_id:
			return action
	# Check hiring submenu actions
	var hiring_options = GameActions.get_hiring_options()
	for action in hiring_options:
		if action.get("id") == action_id:
			return action
	return {}

func end_turn():
	"""Execute queued actions and process turn"""
	if not is_initialized:
		error_occurred.emit("Game not initialized")
		return

	if state.queued_actions.is_empty():
		error_occurred.emit("No actions queued")
		return

	print("[GameManager] Executing turn...")
	turn_phase_changed.emit("turn_end")

	# Execute all queued actions
	var result = turn_manager.execute_turn()

	# Emit results
	for action_result in result["action_results"]:
		action_executed.emit(action_result)

	# Emit updated state
	game_state_updated.emit(state.to_dict())

	# Check for triggered events
	if result.has("triggered_events"):
		var triggered_events = result["triggered_events"]
		for event in triggered_events:
			event_triggered.emit(event)

	# If game not over, start next turn
	if not state.game_over:
		await get_tree().create_timer(0.5).timeout
		start_next_turn()

func start_next_turn():
	"""Begin next turn - FIX #418: Events before actions"""
	print("[GameManager] Starting turn %d" % (state.turn + 1))

	var turn_result = turn_manager.start_turn()

	# Emit phase (might be "turn_start" if events pending, or "action_selection" if not)
	turn_phase_changed.emit(turn_result["phase"])

	# Emit messages
	for message in turn_result["messages"]:
		action_executed.emit({"success": true, "message": message})

	# Emit updated state
	game_state_updated.emit(state.to_dict())

	# Emit triggered events if any (FIX #418)
	if turn_result.has("triggered_events") and turn_result["triggered_events"].size() > 0:
		print("[GameManager] %d event(s) triggered - blocking action selection" % turn_result["triggered_events"].size())
		for event in turn_result["triggered_events"]:
			event_triggered.emit(event)
	else:
		# No events, emit available actions
		var actions = turn_manager.get_available_actions()
		actions_available.emit(actions)

func get_game_state() -> Dictionary:
	if state:
		return state.to_dict()
	return {}

func resolve_event(event: Dictionary, choice_id: String):
	"""Handle player's event choice - FIX #418: Use TurnManager"""
	if not is_initialized:
		error_occurred.emit("Game not initialized")
		return

	# Use TurnManager's resolve_event which handles phase transitions
	var result = turn_manager.resolve_event(event, choice_id)

	if result["success"]:
		action_executed.emit(result)
		game_state_updated.emit(state.to_dict())

		# If all events resolved, transition to action selection
		if result.get("phase_transitioned", false):
			print("[GameManager] All events resolved - transitioning to action selection")
			turn_phase_changed.emit("action_selection")
			# Now emit available actions
			var actions = turn_manager.get_available_actions()
			actions_available.emit(actions)
	else:
		error_occurred.emit(result.get("error", result.get("message", "Event resolution failed")))

func _apply_difficulty_settings():
	"""Apply difficulty modifiers to game state"""
	match GameConfig.difficulty:
		0:  # Easy
			print("[GameManager] Applying EASY difficulty modifiers")
			state.money *= 1.5  # 50% more starting money
			state.max_action_points = 4  # Extra AP
		1:  # Standard
			print("[GameManager] Applying STANDARD difficulty (default)")
			# No changes
		2:  # Hard
			print("[GameManager] Applying HARD difficulty modifiers")
			state.money *= 0.75  # 25% less starting money
			state.max_action_points = 2  # Less AP

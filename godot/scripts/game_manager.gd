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
	# Validation: Game initialized
	if not is_initialized:
		var err = ErrorHandler.error(
			ErrorHandler.Category.ACTIONS,
			"Cannot select action: Game not initialized",
			{"action_id": action_id}
		)
		error_occurred.emit(err.message)
		return

	# Validation: No pending events (FIX #418)
	if state.pending_events.size() > 0:
		var err = ErrorHandler.warning(
			ErrorHandler.Category.ACTIONS,
			"Cannot select actions while events are pending",
			{"action_id": action_id, "pending_events": state.pending_events.size()}
		)
		error_occurred.emit("Resolve pending events before selecting actions!")
		return

	# Validation: Correct phase (FIX #418)
	if state.current_phase != GameState.TurnPhase.ACTION_SELECTION:
		var phase_name = GameState.TurnPhase.keys()[state.current_phase]
		var err = ErrorHandler.warning(
			ErrorHandler.Category.ACTIONS,
			"Cannot select actions in current phase",
			{"action_id": action_id, "current_phase": phase_name}
		)
		error_occurred.emit("Cannot select actions in %s phase" % phase_name)
		return

	# Get action details to check AP cost
	var action = _get_action_by_id(action_id)
	if not action or action.is_empty():
		var err = ErrorHandler.error(
			ErrorHandler.Category.ACTIONS,
			"Action not found",
			{"action_id": action_id}
		)
		error_occurred.emit("Action not found: " + action_id)
		return

	var ap_cost = action.get("costs", {}).get("action_points", 0)

	# Validation: Sufficient AP (check REMAINING AP, not total - fixes overcommitment bug)
	var available_ap = state.action_points - state.committed_ap
	if available_ap < ap_cost:
		var err = ErrorHandler.warning(
			ErrorHandler.Category.RESOURCES,
			"Insufficient action points",
			{
				"action_id": action_id,
				"action_name": action.get("name", ""),
				"required": ap_cost,
				"available": available_ap,
				"total_ap": state.action_points,
				"committed_ap": state.committed_ap
			}
		)
		error_occurred.emit("Not enough AP: %d needed, %d remaining (of %d total)" % [ap_cost, available_ap, state.action_points])
		return

	# Validation: Can afford costs
	if not state.can_afford(action.get("costs", {})):
		var costs = action.get("costs", {})
		var err = ErrorHandler.warning(
			ErrorHandler.Category.RESOURCES,
			"Cannot afford action",
			{
				"action_id": action_id,
				"action_name": action.get("name", ""),
				"costs": costs,
				"state": {
					"money": state.money,
					"compute": state.compute,
					"research": state.research,
					"papers": state.papers,
					"reputation": state.reputation
				}
			}
		)
		error_occurred.emit("Cannot afford " + action.get("name", action_id))
		return

	# Deduct AP immediately (like old game)
	state.action_points -= ap_cost

	ErrorHandler.info(
		ErrorHandler.Category.ACTIONS,
		"Action queued successfully",
		{
			"action_id": action_id,
			"action_name": action.get("name", ""),
			"ap_cost": ap_cost,
			"remaining_ap": state.action_points
		}
	)

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
	# Check fundraising submenu actions
	var fundraising_options = GameActions.get_fundraising_options()
	for action in fundraising_options:
		if action.get("id") == action_id:
			return action
	return {}

func purchase_upgrade(upgrade_id: String):
	"""Purchase an upgrade - doesn't consume AP"""
	if not is_initialized:
		error_occurred.emit("Cannot purchase upgrade: Game not initialized")
		return

	# Purchase the upgrade
	var result = GameUpgrades.purchase_upgrade(upgrade_id, state)

	if result.get("success", false):
		print("[GameManager] Upgrade purchased: %s" % upgrade_id)
		action_executed.emit(result)

		# Emit updated state (money and upgrades changed)
		game_state_updated.emit(state.to_dict())
	else:
		error_occurred.emit(result.get("message", "Upgrade purchase failed"))

func reserve_ap(amount: int):
	"""Reserve AP for event responses"""
	if not is_initialized:
		error_occurred.emit("Cannot reserve AP: Game not initialized")
		return

	if state.reserve_ap_amount(amount):
		print("[GameManager] Reserved %d AP for events (Available: %d, Reserved: %d)" % [amount, state.get_available_ap(), state.reserved_ap])
		action_executed.emit({"success": true, "message": "Reserved %d AP for events" % amount})

		# Emit updated state
		game_state_updated.emit(state.to_dict())
	else:
		error_occurred.emit("Not enough AP to reserve (need %d, have %d)" % [amount, state.get_available_ap()])

func clear_action_queue():
	"""Clear all queued actions and refund committed AP"""
	if not is_initialized:
		return

	var refunded_ap = state.committed_ap
	state.queued_actions.clear()
	state.committed_ap = 0

	print("[GameManager] Queue cleared, refunded %d AP" % refunded_ap)
	game_state_updated.emit(state.to_dict())

func end_turn():
	"""Execute queued actions and process turn"""
	# Validation: Game initialized
	if not is_initialized:
		var err = ErrorHandler.error(
			ErrorHandler.Category.TURN,
			"Cannot end turn: Game not initialized",
			{}
		)
		error_occurred.emit(err.message)
		return

	# Validation: Actions queued
	if state.queued_actions.is_empty():
		var err = ErrorHandler.warning(
			ErrorHandler.Category.TURN,
			"Cannot end turn: No actions queued",
			{"turn": state.turn, "phase": GameState.TurnPhase.keys()[state.current_phase]}
		)
		error_occurred.emit("No actions queued")
		return

	# Validation: Check phase (should be in ACTION_SELECTION)
	if state.current_phase != GameState.TurnPhase.ACTION_SELECTION:
		var phase_name = GameState.TurnPhase.keys()[state.current_phase]
		ErrorHandler.warning(
			ErrorHandler.Category.TURN,
			"Ending turn in unexpected phase",
			{"turn": state.turn, "phase": phase_name}
		)

	ErrorHandler.info(
		ErrorHandler.Category.TURN,
		"Ending turn",
		{
			"turn": state.turn,
			"queued_actions": state.queued_actions.size(),
			"actions": state.queued_actions
		}
	)

	print("[GameManager] Executing turn...")
	turn_phase_changed.emit("turn_end")

	# Execute all queued actions
	var result = turn_manager.execute_turn()

	# Validate turn execution result
	if not result.has("success") or not result.has("action_results"):
		ErrorHandler.error(
			ErrorHandler.Category.TURN,
			"Invalid turn execution result",
			{"result_keys": result.keys()}
		)

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
	else:
		ErrorHandler.info(
			ErrorHandler.Category.GAME_STATE,
			"Game ended",
			{"victory": state.victory, "final_turn": state.turn}
		)

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

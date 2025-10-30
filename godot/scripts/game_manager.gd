extends Node
## Pure GDScript game manager - NO Python bridge

signal game_state_updated(state: Dictionary)
signal turn_phase_changed(phase: String)
signal actions_available(actions: Array)
signal action_executed(result: Dictionary)
signal error_occurred(error_msg: String)

# Game objects
var state: GameState
var turn_manager: TurnManager
var is_initialized: bool = false

func _ready():
	print("[GameManager] Pure GDScript version ready")

func start_new_game(game_seed: String = ""):
	"""Initialize new game - pure GDScript"""
	print("[GameManager] Starting new game (seed: %s)" % game_seed)

	state = GameState.new(game_seed)
	turn_manager = TurnManager.new(state)
	is_initialized = true

	# Start first turn
	var turn_result = turn_manager.start_turn()

	# Emit initial state
	game_state_updated.emit(state.to_dict())
	turn_phase_changed.emit("action_selection")

	# Emit available actions
	var actions = turn_manager.get_available_actions()
	actions_available.emit(actions)

	print("[GameManager] Game initialized - Turn %d" % state.turn)

func select_action(action_id: String):
	"""Queue action for execution"""
	if not is_initialized:
		error_occurred.emit("Game not initialized")
		return

	print("[GameManager] Action queued: %s" % action_id)
	state.queued_actions.append(action_id)

	action_executed.emit({
		"success": true,
		"message": "Action queued: " + action_id
	})

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

	# If game not over, start next turn
	if not state.game_over:
		await get_tree().create_timer(0.5).timeout
		start_next_turn()

func start_next_turn():
	"""Begin next turn"""
	print("[GameManager] Starting turn %d" % (state.turn + 1))

	var turn_result = turn_manager.start_turn()
	turn_phase_changed.emit("action_selection")

	# Emit messages
	for message in turn_result["messages"]:
		action_executed.emit({"success": true, "message": message})

	# Emit updated state and actions
	game_state_updated.emit(state.to_dict())
	var actions = turn_manager.get_available_actions()
	actions_available.emit(actions)

func get_game_state() -> Dictionary:
	if state:
		return state.to_dict()
	return {}

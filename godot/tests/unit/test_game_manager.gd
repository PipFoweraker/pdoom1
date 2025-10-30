extends GutTest
## Unit tests for GameManager class
## Tests high-level game coordination, signal emissions, and turn flow

var game_manager: GameManager
var signal_watcher: SignalWatcher

func before_each():
	# Create fresh game manager for each test
	game_manager = GameManager.new()
	add_child_autofree(game_manager)

	# Watch all signals
	watch_signals(game_manager)

func after_each():
	# Clean up
	if game_manager:
		game_manager.queue_free()

# === INITIALIZATION TESTS ===

func test_initialization_creates_game_objects():
	# Test that start_new_game initializes state and turn_manager
	game_manager.start_new_game("test_seed")

	assert_not_null(game_manager.state, "GameState should be initialized")
	assert_not_null(game_manager.turn_manager, "TurnManager should be initialized")
	assert_true(game_manager.is_initialized, "is_initialized flag should be true")

func test_initialization_with_seed_sets_seed():
	# Test that provided seed is used
	game_manager.start_new_game("custom_seed_123")

	assert_eq(game_manager.state.seed, "custom_seed_123", "Seed should be set correctly")

func test_initialization_without_seed_generates_seed():
	# Test that empty seed generates time-based seed
	game_manager.start_new_game("")

	assert_ne(game_manager.state.seed, "", "Seed should be generated")

# === SIGNAL EMISSION TESTS ===

func test_start_new_game_emits_game_state_updated():
	# Test that initialization emits game_state_updated signal
	game_manager.start_new_game("test_seed")

	assert_signal_emitted(game_manager, "game_state_updated",
		"Should emit game_state_updated on initialization")

func test_start_new_game_emits_turn_phase_changed():
	# Test that initialization emits turn_phase_changed signal
	game_manager.start_new_game("test_seed")

	assert_signal_emitted(game_manager, "turn_phase_changed",
		"Should emit turn_phase_changed on initialization")

func test_start_new_game_emits_actions_available_when_no_events():
	# Test that actions_available is emitted when no initial events
	game_manager.start_new_game("no_events_seed")

	# If no events triggered, should emit actions_available
	# (Event triggering is deterministic but depends on seed and turn conditions)
	# This test may need adjustment based on actual event logic
	assert_signal_emitted_with_parameters(game_manager, "actions_available", [Array],
		"Should emit actions_available if no initial events")

# === ACTION SELECTION TESTS ===

func test_select_action_queues_action():
	# Test that selecting an action queues it
	game_manager.start_new_game("test_seed")
	var initial_queue_size = game_manager.state.queued_actions.size()

	game_manager.select_action("buy_compute")

	assert_eq(game_manager.state.queued_actions.size(), initial_queue_size + 1,
		"Action should be added to queue")
	assert_eq(game_manager.state.queued_actions[0], "buy_compute",
		"Correct action should be queued")

func test_select_action_deducts_action_points():
	# Test that selecting an action deducts AP immediately
	game_manager.start_new_game("test_seed")
	var initial_ap = game_manager.state.action_points

	game_manager.select_action("buy_compute")  # Costs 0 AP in current impl
	game_manager.select_action("safety_research")  # Costs 1 AP

	assert_lt(game_manager.state.action_points, initial_ap,
		"Action points should decrease after action selection")

func test_select_action_validates_affordability():
	# Test that actions are validated before queueing
	game_manager.start_new_game("test_seed")
	game_manager.state.money = 100  # Set very low money
	var initial_queue_size = game_manager.state.queued_actions.size()

	game_manager.select_action("buy_compute")  # Costs $50k

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error when action is unaffordable")
	assert_eq(game_manager.state.queued_actions.size(), initial_queue_size,
		"Unaffordable action should not be queued")

func test_select_action_before_initialization_emits_error():
	# Test that selecting action before init fails gracefully
	game_manager.select_action("buy_compute")

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error when game not initialized")

func test_select_action_invalid_id_emits_error():
	# Test that invalid action ID fails gracefully
	game_manager.start_new_game("test_seed")

	game_manager.select_action("nonexistent_action_xyz")

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error for invalid action ID")

# === TURN SEQUENCING TESTS (FIX #418) ===

func test_select_action_blocks_during_event_phase():
	# FIX #418: Actions should be blocked when events are pending
	game_manager.start_new_game("test_seed")

	# Manually set pending events to simulate event phase
	game_manager.state.pending_events = [{"id": "test_event"}]
	game_manager.state.current_phase = GameState.TurnPhase.TURN_START

	game_manager.select_action("buy_compute")

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error when events are pending (FIX #418)")

func test_select_action_blocks_in_wrong_phase():
	# FIX #418: Actions should only be selectable in ACTION_SELECTION phase
	game_manager.start_new_game("test_seed")
	game_manager.state.current_phase = GameState.TurnPhase.TURN_PROCESSING

	game_manager.select_action("buy_compute")

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error in wrong phase (FIX #418)")

func test_select_action_allowed_in_action_selection_phase():
	# FIX #418: Actions should be allowed in ACTION_SELECTION phase
	game_manager.start_new_game("test_seed")
	game_manager.state.current_phase = GameState.TurnPhase.ACTION_SELECTION
	game_manager.state.pending_events.clear()

	game_manager.select_action("buy_compute")

	assert_signal_not_emitted(game_manager, "error_occurred",
		"Should not error in ACTION_SELECTION phase")

# === TURN EXECUTION TESTS ===

func test_end_turn_requires_queued_actions():
	# Test that end_turn fails if no actions queued
	game_manager.start_new_game("test_seed")

	game_manager.end_turn()

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error when no actions queued")

func test_end_turn_executes_queued_actions():
	# Test that end_turn processes queued actions
	game_manager.start_new_game("test_seed")
	var initial_compute = game_manager.state.compute

	game_manager.select_action("buy_compute")
	game_manager.end_turn()

	await wait_seconds(0.6)  # Wait for turn processing

	assert_gt(game_manager.state.compute, initial_compute,
		"Queued action should be executed")

func test_end_turn_clears_queued_actions():
	# Test that queued actions are cleared after execution
	game_manager.start_new_game("test_seed")

	game_manager.select_action("buy_compute")
	game_manager.end_turn()

	await wait_seconds(0.6)

	assert_eq(game_manager.state.queued_actions.size(), 0,
		"Queued actions should be cleared after turn execution")

func test_end_turn_emits_turn_phase_changed():
	# Test that end_turn emits phase change signal
	game_manager.start_new_game("test_seed")
	game_manager.select_action("buy_compute")

	game_manager.end_turn()

	assert_signal_emitted(game_manager, "turn_phase_changed",
		"Should emit turn_phase_changed on end_turn")

func test_end_turn_emits_game_state_updated():
	# Test that state updates are emitted
	game_manager.start_new_game("test_seed")
	game_manager.select_action("buy_compute")

	# Clear signal count from initialization
	clear_signal_watcher()

	game_manager.end_turn()

	assert_signal_emitted(game_manager, "game_state_updated",
		"Should emit game_state_updated during turn execution")

# === NEXT TURN TESTS ===

func test_start_next_turn_increments_turn_counter():
	# Test that starting next turn increments turn
	game_manager.start_new_game("test_seed")
	var initial_turn = game_manager.state.turn

	game_manager.select_action("buy_compute")
	game_manager.end_turn()

	await wait_seconds(0.6)

	assert_eq(game_manager.state.turn, initial_turn + 1,
		"Turn should increment after end_turn")

func test_start_next_turn_resets_action_points():
	# Test that AP is reset on new turn
	game_manager.start_new_game("test_seed")
	game_manager.select_action("safety_research")  # Uses 1 AP
	var ap_before_turn_end = game_manager.state.action_points

	game_manager.end_turn()
	await wait_seconds(0.6)

	assert_gt(game_manager.state.action_points, ap_before_turn_end,
		"Action points should be reset on new turn")

func test_start_next_turn_emits_actions_available_when_no_events():
	# FIX #418: Test that actions are available if no events
	game_manager.start_new_game("test_seed")
	game_manager.select_action("buy_compute")

	clear_signal_watcher()
	game_manager.end_turn()

	await wait_seconds(0.6)

	# Should emit actions_available if no events triggered
	# Note: This depends on game state not triggering events
	assert_signal_emitted(game_manager, "actions_available",
		"Should emit actions_available when no events (FIX #418)")

# === EVENT RESOLUTION TESTS (FIX #418) ===

func test_resolve_event_updates_state():
	# Test that event resolution affects game state
	game_manager.start_new_game("test_seed")

	# Create a test event
	var test_event = {
		"id": "test_event",
		"name": "Test Event",
		"options": [
			{
				"id": "test_choice",
				"text": "Test",
				"effects": {"money": 10000},
				"costs": {},
				"message": "Test message"
			}
		]
	}

	var initial_money = game_manager.state.money

	game_manager.resolve_event(test_event, "test_choice")

	assert_gt(game_manager.state.money, initial_money,
		"Event resolution should update state")

func test_resolve_event_emits_game_state_updated():
	# Test that event resolution emits state update
	game_manager.start_new_game("test_seed")

	var test_event = {
		"id": "test_event",
		"options": [{
			"id": "test_choice",
			"effects": {},
			"costs": {},
			"message": "Test"
		}]
	}

	clear_signal_watcher()
	game_manager.resolve_event(test_event, "test_choice")

	assert_signal_emitted(game_manager, "game_state_updated",
		"Should emit game_state_updated after event resolution")

func test_resolve_event_transitions_phase_when_all_resolved():
	# FIX #418: Test phase transition after last event resolved
	game_manager.start_new_game("test_seed")

	# Set up single pending event
	var test_event = {
		"id": "test_event",
		"options": [{
			"id": "test_choice",
			"effects": {},
			"costs": {},
			"message": "Test"
		}]
	}

	game_manager.state.pending_events = [test_event]
	game_manager.state.current_phase = GameState.TurnPhase.TURN_START

	clear_signal_watcher()
	game_manager.resolve_event(test_event, "test_choice")

	assert_signal_emitted(game_manager, "turn_phase_changed",
		"Should emit turn_phase_changed after resolving all events (FIX #418)")

func test_resolve_event_emits_actions_available_after_transition():
	# FIX #418: Test that actions become available after events resolved
	game_manager.start_new_game("test_seed")

	var test_event = {
		"id": "test_event",
		"options": [{
			"id": "test_choice",
			"effects": {},
			"costs": {},
			"message": "Test"
		}]
	}

	game_manager.state.pending_events = [test_event]
	game_manager.state.current_phase = GameState.TurnPhase.TURN_START

	clear_signal_watcher()
	game_manager.resolve_event(test_event, "test_choice")

	assert_signal_emitted(game_manager, "actions_available",
		"Should emit actions_available after events resolved (FIX #418)")

func test_resolve_event_before_initialization_emits_error():
	# Test that event resolution before init fails gracefully
	var test_event = {"id": "test", "options": []}

	game_manager.resolve_event(test_event, "choice")

	assert_signal_emitted(game_manager, "error_occurred",
		"Should emit error when game not initialized")

# === GAME STATE ACCESS TESTS ===

func test_get_game_state_returns_dict():
	# Test that get_game_state returns valid dictionary
	game_manager.start_new_game("test_seed")

	var state_dict = game_manager.get_game_state()

	assert_typeof(state_dict, TYPE_DICTIONARY, "Should return dictionary")
	assert_has(state_dict, "money", "Should include money")
	assert_has(state_dict, "doom", "Should include doom")
	assert_has(state_dict, "turn", "Should include turn")

func test_get_game_state_before_initialization_returns_empty():
	# Test that get_game_state returns empty dict before init
	var state_dict = game_manager.get_game_state()

	assert_eq(state_dict, {}, "Should return empty dict before initialization")

# === INTEGRATION TESTS ===

func test_complete_turn_cycle():
	# Test a complete turn: start → select → end → next
	game_manager.start_new_game("test_seed")
	var initial_turn = game_manager.state.turn

	# Select action
	game_manager.select_action("buy_compute")
	assert_eq(game_manager.state.queued_actions.size(), 1, "Action should be queued")

	# End turn
	game_manager.end_turn()
	await wait_seconds(0.6)

	# Verify turn advanced
	assert_eq(game_manager.state.turn, initial_turn + 1, "Turn should advance")
	assert_eq(game_manager.state.queued_actions.size(), 0, "Queue should be empty")

func test_multiple_actions_single_turn():
	# Test queueing multiple actions in one turn
	game_manager.start_new_game("test_seed")

	game_manager.select_action("buy_compute")
	game_manager.select_action("network")

	assert_eq(game_manager.state.queued_actions.size(), 2,
		"Multiple actions should be queued")

	game_manager.end_turn()
	await wait_seconds(0.6)

	assert_eq(game_manager.state.queued_actions.size(), 0,
		"All actions should be processed")

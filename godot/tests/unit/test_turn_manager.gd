extends GutTest
## Unit tests for TurnManager class

var state: GameState
var turn_manager: TurnManager

func before_each():
	# Create fresh state and turn manager for each test
	state = GameState.new("test_seed")
	turn_manager = TurnManager.new(state)

func test_start_turn_increments_turn_counter():
	# Test that start_turn increases turn number
	assert_eq(state.turn, 0, "Should start at turn 0")

	turn_manager.start_turn()
	assert_eq(state.turn, 1, "Turn should increment to 1")

	turn_manager.start_turn()
	assert_eq(state.turn, 2, "Turn should increment to 2")

func test_start_turn_resets_action_points():
	# Test that start_turn resets AP to base amount
	state.action_points = 0  # Deplete AP

	turn_manager.start_turn()

	assert_eq(state.action_points, 3, "AP should reset to base 3")

func test_start_turn_ap_scales_with_staff():
	# Test that AP increases with staff count (base 3 + 0.5 per employee)
	state.safety_researchers = 2
	state.compute_engineers = 4
	# Total staff = 6, so AP = 3 + int(6 * 0.5) = 3 + 3 = 6

	turn_manager.start_turn()

	assert_eq(state.action_points, 6, "AP should scale: 3 + int(6 * 0.5) = 6")

func test_start_turn_deducts_staff_salaries():
	# Test that staff salaries are deducted ($5k per employee)
	state.safety_researchers = 3
	state.capability_researchers = 2
	# Total staff = 5, salaries = 5 * $5000 = $25,000
	var initial_money = state.money

	turn_manager.start_turn()

	var expected_money = initial_money - 25000
	assert_eq(state.money, expected_money, "Should deduct $25k in salaries")

func test_start_turn_generates_research_from_compute():
	# Test that research is generated from compute
	state.compute = 100.0
	state.compute_engineers = 2
	# Research = 100 * 0.05 * (1.0 + 2 * 0.1) = 100 * 0.05 * 1.2 = 6.0

	turn_manager.start_turn()

	assert_almost_eq(state.research, 6.0, 0.01, "Should generate 6.0 research")

func test_execute_turn_processes_queued_actions():
	# Test that execute_turn runs queued actions
	state.queued_actions = ["buy_compute"]
	state.action_points = 3

	var result = turn_manager.execute_turn()

	assert_true(result["success"], "Execute turn should succeed")
	assert_gt(state.compute, 100.0, "Compute should increase from action")

func test_execute_turn_clears_queued_actions():
	# Test that queued actions are cleared after execution
	state.queued_actions = ["buy_compute", "hire_safety_researcher"]

	turn_manager.execute_turn()

	assert_eq(state.queued_actions.size(), 0, "Queued actions should be cleared")

func test_execute_turn_publishes_papers_at_threshold():
	# Test that papers are published when research >= 100
	state.research = 150.0
	state.queued_actions = ["buy_compute"]  # Need at least one action

	turn_manager.execute_turn()

	assert_eq(state.papers, 1.0, "Should publish 1 paper")
	assert_almost_eq(state.research, 50.0, 0.01, "Research should be 150 - 100 = 50")

func test_execute_turn_increases_doom():
	# Test that environmental doom increases each turn
	var initial_doom = state.doom
	state.capability_researchers = 2
	state.queued_actions = ["buy_compute"]

	# Expected doom increase: base 1.0 + (2 * 0.5) = 2.0
	turn_manager.execute_turn()

	assert_almost_eq(state.doom, initial_doom + 2.0, 0.01, "Doom should increase by 2.0")

func test_execute_turn_checks_events():
	# Test that events are checked during turn execution
	state.queued_actions = ["buy_compute"]

	var result = turn_manager.execute_turn()

	assert_has(result, "triggered_events", "Result should include triggered_events")
	# Events array might be empty, but key should exist

func test_get_available_actions_marks_affordability():
	# Test that get_available_actions marks which actions are affordable
	state.money = 10000  # Very low money

	var actions = turn_manager.get_available_actions()

	# Find buy_compute action (costs $10k)
	var buy_compute = null
	for action in actions:
		if action["id"] == "buy_compute":
			buy_compute = action
			break

	assert_not_null(buy_compute, "buy_compute action should exist")
	assert_true(buy_compute["affordable"], "buy_compute should be affordable with $10k")

func test_get_available_actions_includes_all_actions():
	# Test that all actions are included in available actions
	var actions = turn_manager.get_available_actions()

	var all_actions = GameActions.get_all_actions()
	assert_eq(actions.size(), all_actions.size(), "Should include all actions")

func test_multiple_paper_publications():
	# Test that multiple papers can be published in one turn
	state.research = 250.0
	state.queued_actions = ["buy_compute"]

	turn_manager.execute_turn()

	assert_eq(state.papers, 2.0, "Should publish 2 papers")
	assert_almost_eq(state.research, 50.0, 0.01, "Research should be 250 - 200 = 50")

func test_no_staff_no_salary_deduction():
	# Test that no salaries are deducted when staff = 0
	var initial_money = state.money
	assert_eq(state.get_total_staff(), 0, "Should have no staff")

	turn_manager.start_turn()

	assert_eq(state.money, initial_money, "Money should not decrease with no staff")

func test_turn_sequence_integration():
	# Test a complete turn sequence: start → actions → execute
	var initial_turn = state.turn

	# Start turn
	var start_result = turn_manager.start_turn()
	assert_eq(state.turn, initial_turn + 1, "Turn should increment")
	assert_eq(state.action_points, 3, "AP should be 3")

	# Queue actions
	state.queued_actions = ["buy_compute"]

	# Execute turn
	var exec_result = turn_manager.execute_turn()
	assert_true(exec_result["success"], "Execute should succeed")
	assert_eq(state.queued_actions.size(), 0, "Actions should be cleared")

# === TURN SEQUENCING TESTS (FIX #418) ===

func test_turn_phase_starts_at_action_selection():
	# FIX #418: New games should start in ACTION_SELECTION phase
	assert_eq(state.current_phase, GameState.TurnPhase.ACTION_SELECTION,
		"Should start in ACTION_SELECTION phase (FIX #418)")

func test_start_turn_with_no_events_allows_actions():
	# FIX #418: When no events trigger, actions should be selectable
	state.turn = 5  # Use turn that won't trigger events
	state.money = 100000  # Ensure no funding crisis

	var result = turn_manager.start_turn()

	assert_true(result.get("can_select_actions", false),
		"Should allow action selection when no events (FIX #418)")
	assert_eq(state.current_phase, GameState.TurnPhase.ACTION_SELECTION,
		"Phase should be ACTION_SELECTION when no events (FIX #418)")
	assert_eq(state.pending_events.size(), 0,
		"No pending events should exist (FIX #418)")

func test_start_turn_with_events_blocks_actions():
	# FIX #418: When events trigger, actions should be blocked
	state.turn = 10
	state.money = 40000  # Triggers funding_crisis event

	var result = turn_manager.start_turn()

	assert_false(result.get("can_select_actions", true),
		"Should block action selection when events pending (FIX #418)")
	assert_eq(state.current_phase, GameState.TurnPhase.TURN_START,
		"Phase should remain TURN_START when events pending (FIX #418)")
	assert_gt(state.pending_events.size(), 0,
		"Pending events should be recorded (FIX #418)")

func test_start_turn_sets_pending_events():
	# FIX #418: Triggered events should be stored in pending_events
	state.turn = 10
	state.money = 40000

	turn_manager.start_turn()

	assert_gt(state.pending_events.size(), 0,
		"Pending events array should be populated (FIX #418)")
	assert_has(state.pending_events[0], "id",
		"Pending events should be valid event dictionaries (FIX #418)")

func test_start_turn_sets_can_end_turn_false_when_events():
	# FIX #418: can_end_turn should be false when events pending
	state.turn = 10
	state.money = 40000

	turn_manager.start_turn()

	assert_false(state.can_end_turn,
		"can_end_turn should be false when events pending (FIX #418)")

func test_start_turn_sets_can_end_turn_true_when_no_events():
	# FIX #418: can_end_turn should be true when no events
	state.turn = 5
	state.money = 100000

	turn_manager.start_turn()

	assert_true(state.can_end_turn,
		"can_end_turn should be true when no events (FIX #418)")

func test_resolve_event_removes_from_pending():
	# FIX #418: Resolving an event should remove it from pending
	state.turn = 10
	state.money = 40000

	turn_manager.start_turn()
	var event = state.pending_events[0]
	var initial_pending_count = state.pending_events.size()

	turn_manager.resolve_event(event, "emergency_fundraise")

	assert_lt(state.pending_events.size(), initial_pending_count,
		"Pending events should decrease after resolution (FIX #418)")

func test_resolve_event_transitions_to_action_selection():
	# FIX #418: After all events resolved, should transition to ACTION_SELECTION
	state.turn = 10
	state.money = 40000

	turn_manager.start_turn()
	var event = state.pending_events[0]

	# Resolve all pending events
	turn_manager.resolve_event(event, "emergency_fundraise")

	assert_eq(state.current_phase, GameState.TurnPhase.ACTION_SELECTION,
		"Phase should transition to ACTION_SELECTION after all events resolved (FIX #418)")

func test_resolve_event_sets_can_end_turn_true():
	# FIX #418: After resolving all events, can_end_turn should be true
	state.turn = 10
	state.money = 40000

	turn_manager.start_turn()
	var event = state.pending_events[0]

	turn_manager.resolve_event(event, "emergency_fundraise")

	assert_true(state.can_end_turn,
		"can_end_turn should be true after events resolved (FIX #418)")

func test_resolve_event_blocked_in_wrong_phase():
	# FIX #418: Event resolution should only work in TURN_START phase
	state.current_phase = GameState.TurnPhase.ACTION_SELECTION

	var test_event = {"id": "test", "options": [{"id": "choice", "effects": {}, "costs": {}, "message": "test"}]}
	var result = turn_manager.resolve_event(test_event, "choice")

	assert_false(result["success"],
		"Event resolution should fail in wrong phase (FIX #418)")

func test_phase_transitions_complete_cycle():
	# FIX #418: Test complete phase cycle with event
	state.turn = 10
	state.money = 40000

	# Phase 1: TURN_START (events)
	turn_manager.start_turn()
	assert_eq(state.current_phase, GameState.TurnPhase.TURN_START,
		"Phase 1 should be TURN_START (FIX #418)")

	# Resolve event
	var event = state.pending_events[0]
	turn_manager.resolve_event(event, "emergency_fundraise")

	# Phase 2: ACTION_SELECTION
	assert_eq(state.current_phase, GameState.TurnPhase.ACTION_SELECTION,
		"Phase 2 should be ACTION_SELECTION (FIX #418)")

	# Queue actions and execute
	state.queued_actions = ["buy_compute"]

	# Phase 3: TURN_PROCESSING (happens in execute_turn)
	turn_manager.execute_turn()

	# Turn completes, ready for next cycle

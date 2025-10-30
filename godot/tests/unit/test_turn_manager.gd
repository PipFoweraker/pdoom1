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

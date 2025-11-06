extends GutTest
## Test Phase 5 features: expanded actions, productivity, events, rivals

func test_expanded_actions_exist():
	var actions = GameActions.get_all_actions()
	assert_gt(actions.size(), 15, "Should have 15+ actions")

	# Check new strategic actions exist
	var action_ids = []
	for action in actions:
		action_ids.append(action["id"])

	assert_has(action_ids, "lobby_government")
	assert_has(action_ids, "acquire_startup")
	assert_has(action_ids, "grant_proposal")
	assert_has(action_ids, "hire_ethicist")

func test_manager_system():
	var state = GameState.new("test_managers")

	# No managers, default capacity is 9
	assert_eq(state.get_management_capacity(), 9, "Base capacity should be 9")
	assert_eq(state.get_unmanaged_count(), 0, "No unmanaged initially")

	# Hire 10 employees, exceed capacity
	state.safety_researchers = 10
	assert_eq(state.get_unmanaged_count(), 1, "Should have 1 unmanaged employee")

	# Hire 1 manager
	state.managers = 1
	assert_eq(state.get_management_capacity(), 9, "1 manager handles 9")
	assert_eq(state.get_unmanaged_count(), 1, "Still 1 unmanaged")

	# Hire 2nd manager
	state.managers = 2
	assert_eq(state.get_management_capacity(), 18, "2 managers handle 18")
	assert_eq(state.get_unmanaged_count(), 0, "All managed now")

func test_employee_productivity_system():
	var state = GameState.new("test_productivity")
	var turn_manager = TurnManager.new(state)

	# Hire employees and give them compute
	state.safety_researchers = 3
	state.compute = 100.0
	state.money = 100000.0

	# Start turn - should generate research from productive employees
	var result = turn_manager.start_turn()

	assert_true(result["success"], "Turn should start successfully")
	assert_gt(state.research, 0.0, "Should generate some research from employees")

func test_rival_labs_initialization():
	var rivals = RivalLabs.get_rival_labs()

	assert_eq(rivals.size(), 3, "Should have 3 rival labs")

	var names = []
	for rival in rivals:
		names.append(rival.name)

	assert_has(names, "DeepSafety")
	assert_has(names, "CapabiliCorp")
	assert_has(names, "StealthAI")

func test_rival_actions_affect_doom():
	var state = GameState.new("test_rivals")
	var aggressive_rival = RivalLabs.RivalLab.new("TestRival", 0.9)  # Very aggressive
	aggressive_rival.funding = 500000.0

	var result = RivalLabs.process_rival_turn(aggressive_rival, state, state.rng)

	assert_true(result.has("doom_contribution"), "Should return doom contribution")
	assert_gt(result["actions"].size(), 0, "Should take at least 1 action")

func test_expanded_events_exist():
	var events = GameEvents.get_all_events()
	assert_gt(events.size(), 8, "Should have 8+ events")

	var event_ids = []
	for event in events:
		event_ids.append(event["id"])

	# Check new events
	assert_has(event_ids, "employee_burnout")
	assert_has(event_ids, "rival_poaching")
	assert_has(event_ids, "media_scandal")
	assert_has(event_ids, "government_regulation")
	assert_has(event_ids, "technical_failure")

func test_event_condition_evaluation_with_staff():
	var state = GameState.new("test_conditions")
	state.safety_researchers = 5

	var condition = "safety_researchers >= 5"
	var result = GameEvents.evaluate_condition(condition, state)

	assert_true(result, "Should evaluate staff conditions correctly")

func test_full_turn_with_all_phase5_features():
	var state = GameState.new("test_full_turn")
	var turn_manager = TurnManager.new(state)

	# Setup: hire some staff, give compute
	state.safety_researchers = 2
	state.capability_researchers = 1
	state.compute_engineers = 1
	state.compute = 100.0
	state.money = 200000.0

	# Start turn
	var start_result = turn_manager.start_turn()
	assert_true(start_result["success"], "Turn start should succeed")

	# Queue an action (hire manager)
	state.queued_actions.append("hire_manager")

	# Execute turn
	var exec_result = turn_manager.execute_turn()
	assert_true(exec_result["success"], "Turn execution should succeed")

	# Check manager was hired
	assert_eq(state.managers, 1, "Should have hired 1 manager")

	# Check doom changed (rivals + base + capabilities)
	assert_true(state.doom != 50.0, "Doom should change from starting value")

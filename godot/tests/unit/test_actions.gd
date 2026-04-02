extends GutTest
## Unit tests for GameActions class

var state: GameState

func before_each():
	state = GameState.new("test_seed")

func test_all_actions_have_required_fields():
	# Test that all actions have id, name, category, costs
	var actions = GameActions.get_all_actions()

	for action in actions:
		assert_has(action, "id", "Action should have id")
		assert_has(action, "name", "Action should have name")
		assert_has(action, "category", "Action should have category")
		assert_has(action, "costs", "Action should have costs")

func test_action_count():
	# Test that we have expected number of actions
	var actions = GameActions.get_all_actions()
	assert_eq(actions.size(), 12, "Should have 12 main actions")

func test_hiring_options_exist():
	# Test that hiring submenu has 5 options (safety, capability, compute, manager, ethicist)
	var hiring_options = GameActions.get_hiring_options()
	assert_eq(hiring_options.size(), 5, "Should have 5 hiring options")

func test_buy_compute_execution():
	# Test buy_compute action
	var initial_compute = state.compute
	var initial_money = state.money

	var result = GameActions.execute_action("buy_compute", state)

	assert_gt(state.compute, initial_compute, "Compute should increase")
	assert_lt(state.money, initial_money, "Money should decrease")

func test_hire_safety_researcher_execution():
	# Test hiring safety researcher
	var initial_staff = state.safety_researchers

	var result = GameActions.execute_action("hire_safety_researcher", state)

	assert_eq(state.safety_researchers, initial_staff + 1, "Safety researchers should increase by 1")
	assert_lt(state.money, 245000.0, "Money should decrease from starting 245000")

func test_hire_capability_researcher_execution():
	# Test hiring capability researcher
	var initial_staff = state.capability_researchers

	var result = GameActions.execute_action("hire_capability_researcher", state)

	assert_eq(state.capability_researchers, initial_staff + 1, "Capability researchers should increase by 1")

func test_hire_compute_engineer_execution():
	# Test hiring compute engineer
	var initial_staff = state.compute_engineers

	var result = GameActions.execute_action("hire_compute_engineer", state)

	assert_eq(state.compute_engineers, initial_staff + 1, "Compute engineers should increase by 1")

func test_safety_research_execution():
	# Test safety research action - doom reduction scales with safety_researchers count
	# Need at least 1 safety researcher for any doom reduction
	state.safety_researchers = 1
	state.research = 20.0  # Ensure enough research to pay cost
	var initial_doom = state.doom

	var result = GameActions.execute_action("safety_research", state)

	assert_lt(state.doom, initial_doom, "Doom should decrease when safety researchers > 0")

func test_team_building_execution():
	# Test team building action
	var initial_reputation = state.reputation
	var initial_doom = state.doom

	var result = GameActions.execute_action("team_building", state)

	assert_gt(state.reputation, initial_reputation, "Reputation should increase")
	assert_lt(state.doom, initial_doom, "Doom should decrease")

func test_media_campaign_execution():
	# Test media campaign action
	var initial_reputation = state.reputation

	var result = GameActions.execute_action("media_campaign", state)

	assert_gt(state.reputation, initial_reputation, "Reputation should increase")

func test_action_categories():
	# Test that actions are properly categorized
	var actions = GameActions.get_all_actions()
	var categories = {}

	for action in actions:
		var category = action["category"]
		if not categories.has(category):
			categories[category] = 0
		categories[category] += 1

	assert_has(categories, "hiring", "Should have hiring category")
	assert_has(categories, "resources", "Should have resources category")
	assert_has(categories, "research", "Should have research category")
	assert_has(categories, "management", "Should have management category")

func test_hire_staff_is_submenu():
	# Test that hire_staff action is marked as submenu
	var actions = GameActions.get_all_actions()
	var hire_staff = null

	for action in actions:
		if action["id"] == "hire_staff":
			hire_staff = action
			break

	assert_not_null(hire_staff, "hire_staff action should exist")
	assert_true(hire_staff.get("is_submenu", false), "hire_staff should be marked as submenu")

func test_all_hiring_options_cost_money_and_ap():
	# Test that all hiring options have money and AP costs
	var hiring_options = GameActions.get_hiring_options()

	for option in hiring_options:
		var costs = option["costs"]
		assert_has(costs, "money", "Hiring option should cost money")
		assert_has(costs, "action_points", "Hiring option should cost AP")
		assert_gt(costs["money"], 0, "Money cost should be positive")
		assert_gt(costs["action_points"], 0, "AP cost should be positive")

func test_safety_audit_execution():
	# Test safety audit action - action id is "audit_safety" not "safety_audit"
	var initial_doom = state.doom
	var initial_reputation = state.reputation

	var result = GameActions.execute_action("audit_safety", state)

	# Safety audit should reduce doom and increase reputation
	assert_lt(state.doom, initial_doom, "Doom should decrease")
	assert_gt(state.reputation, initial_reputation, "Reputation should increase")

func test_action_execution_returns_result():
	# Test that action execution returns a result dictionary
	var result = GameActions.execute_action("buy_compute", state)

	assert_typeof(result, TYPE_DICTIONARY, "Result should be a dictionary")

func test_unknown_action_returns_empty_dict():
	# Test that unknown action IDs return a failure result (not empty dict)
	var result = GameActions.execute_action("nonexistent_action", state)

	assert_eq(result["success"], false, "Unknown action should return success=false")
	assert_true(result.has("message"), "Unknown action should include an error message")

## Regression test for issue #449 - verify lobby_government is affordable
func test_lobby_government_affordable_without_reputation():
	# Issue #449: lobby_government should not require reputation as a cost
	state.money = 100000
	state.action_points = 3
	state.reputation = 5  # Low reputation - should NOT block action

	# lobby_government is a submenu item (under publicity), not a top-level action
	var lobby_action = GameActions.get_action_by_id("lobby_government")
	assert_false(lobby_action.is_empty(), "lobby_government should exist")

	var costs = lobby_action["costs"]
	var can_afford = state.can_afford(costs)

	assert_true(can_afford, "Should be affordable with just money and AP (no reputation cost)")
	assert_false(costs.has("reputation"), "Costs should not include reputation")

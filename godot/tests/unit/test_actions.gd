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
	# 13 pre-existing (incl. BL-1 Financing submenu) + 5 hiring-pipeline stage actions
	# (advertise / use_connections / interview_next / hire_best / onboard_next, Phase B).
	var actions = GameActions.get_all_actions()
	assert_eq(actions.size(), 18, "Should have 18 main actions (13 base + 5 hiring-pipeline stages)")

func test_hiring_options_exist():
	# Test that hiring submenu has 7 options (safety, capability, compute, manager, ethicist,
	# interpretability, alignment)
	var hiring_options = GameActions.get_hiring_options()
	assert_eq(hiring_options.size(), 7, "Should have 7 hiring options")

func test_all_spawnable_specs_are_hireable():
	# Regression (#561): every researcher specialization that can spawn in the candidate pool
	# must have a hiring submenu option, or those candidates can never be hired.
	var ids := []
	for opt in GameActions.get_hiring_options():
		ids.append(opt["id"])
	assert_true("hire_safety_researcher" in ids, "safety hireable")
	assert_true("hire_capability_researcher" in ids, "capability hireable")
	assert_true("hire_interpretability_researcher" in ids, "interpretability hireable")
	assert_true("hire_alignment_researcher" in ids, "alignment hireable")

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

func test_hire_interpretability_researcher_execution():
	# Regression (#561): interpretability candidates spawn + engine handles them, but the hire
	# action had no submenu option. Seed a candidate explicitly so the test is seed-independent.
	var c = Researcher.new()
	c.specialization = "interpretability"
	state.add_candidate(c)
	var before = state.get_researcher_count_by_spec("interpretability")
	var result = GameActions.execute_action("hire_interpretability_researcher", state)
	assert_true(result.get("success", false), "Interpretability hire should succeed")
	assert_eq(state.get_researcher_count_by_spec("interpretability"), before + 1, "Interpretability researcher should join")

func test_hire_alignment_researcher_execution():
	# Regression (#561): same gap for alignment specialists.
	var c = Researcher.new()
	c.specialization = "alignment"
	state.add_candidate(c)
	var before = state.get_researcher_count_by_spec("alignment")
	var result = GameActions.execute_action("hire_alignment_researcher", state)
	assert_true(result.get("success", false), "Alignment hire should succeed")
	assert_eq(state.get_researcher_count_by_spec("alignment"), before + 1, "Alignment researcher should join")

func test_safety_research_execution():
	# ADR-0015: no action writes doom. Safety research raises the safety_absorption
	# intermediary (Balance-scaled); the overhang stream converts it on the doom tick.
	state.safety_researchers = 1
	state.research = 20.0  # Ensure enough research to pay cost
	var initial_doom = state.doom
	var initial_absorb = state.safety_absorption

	var result = GameActions.execute_action("safety_research", state)

	assert_eq(state.doom, initial_doom, "No printed doom delta (ADR-0015)")
	assert_almost_eq(state.safety_absorption,
		initial_absorb + 1.0 * Balance.num("doom.streams.action_safety_absorb", 0.0), 0.0001,
		"Safety research raises safety_absorption by the Balance-priced amount")

func test_team_building_execution():
	# Test team building action
	var initial_reputation = state.reputation
	var initial_doom = state.doom

	var result = GameActions.execute_action("team_building", state)

	assert_gt(state.reputation, initial_reputation, "Reputation should increase")
	assert_eq(state.doom, initial_doom, "No printed doom delta (ADR-0015)")

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

	# ADR-0015: the audit raises safety_absorption (Balance-priced), never doom directly
	assert_eq(state.doom, initial_doom, "No printed doom delta (ADR-0015)")
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

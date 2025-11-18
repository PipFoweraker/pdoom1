extends GutTest
## Regression tests for fixed bugs - prevent regressions

var state: GameState

func before_each():
	state = GameState.new("test_seed")

## Issue #449: Lobby Government action affordability
## Previously had reputation in costs, making it unaffordable
func test_lobby_government_no_reputation_cost():
	var actions = GameActions.get_all_actions()
	var lobby_action = null

	for action in actions:
		if action["id"] == "lobby_government":
			lobby_action = action
			break

	assert_not_null(lobby_action, "lobby_government action should exist")

	# Check costs - should NOT have reputation cost
	var costs = lobby_action.get("costs", {})
	assert_false(costs.has("reputation"), "lobby_government should NOT cost reputation (issue #449)")
	assert_true(costs.has("money"), "lobby_government should cost money")
	assert_true(costs.has("action_points"), "lobby_government should cost AP")

func test_lobby_government_applies_reputation_penalty():
	# Test that lobby_government applies -10 reputation as effect, not cost
	var initial_reputation = state.reputation
	state.money = 100000  # Ensure we can afford it
	state.action_points = 3

	var result = GameActions.execute_action("lobby_government", state)

	# Reputation should decrease (penalty applied as effect)
	assert_lt(state.reputation, initial_reputation, "Reputation should decrease after lobbying (issue #449)")
	assert_eq(state.reputation, initial_reputation - 10, "Reputation penalty should be -10")

func test_lobby_government_affordable_with_money_and_ap():
	# Test that action is affordable with just money and AP (no rep requirement)
	state.money = 100000
	state.action_points = 3
	state.reputation = 5  # Low reputation - but shouldn't block action

	var can_afford = state.can_afford({"money": 80000, "action_points": 2})
	assert_true(can_afford, "Should be affordable with money and AP only (issue #449)")

## Issue #447: Difficulty validation
## Previously crashed on invalid difficulty values
func test_difficulty_validation_handles_invalid_int():
	# Test that invalid difficulty values are handled gracefully
	GameConfig.difficulty = 999  # Invalid value

	var game_manager = GameManager.new()
	# This should not crash - will be caught in _apply_difficulty_settings
	game_manager.start_new_game("test")

	# Difficulty should be reset to 1 (Standard)
	assert_eq(GameConfig.difficulty, 1, "Invalid difficulty should default to Standard (issue #447)")

	game_manager.queue_free()

func test_difficulty_validation_handles_negative():
	# Test that negative difficulty is handled
	GameConfig.difficulty = -1

	var game_manager = GameManager.new()
	game_manager.start_new_game("test")

	assert_eq(GameConfig.difficulty, 1, "Negative difficulty should default to Standard (issue #447)")

	game_manager.queue_free()

func test_difficulty_validation_accepts_valid_range():
	# Test that valid difficulties (0, 1, 2) are accepted
	for valid_difficulty in [0, 1, 2]:
		GameConfig.difficulty = valid_difficulty

		var game_manager = GameManager.new()
		game_manager.start_new_game("test")

		assert_eq(GameConfig.difficulty, valid_difficulty, "Valid difficulty %d should be preserved" % valid_difficulty)

		game_manager.queue_free()

## Issue #451: Action categories should use button colors, not text labels
## This is more of a UI test, but we can verify no "-- Category --" text exists
func test_no_hardcoded_category_labels_in_actions():
	# Ensure action definitions don't have category label text
	var actions = GameActions.get_all_actions()

	for action in actions:
		var action_name = action.get("name", "")
		assert_false(action_name.begins_with("--"), "Action names should not be category labels (issue #451)")
		assert_false(action_name.ends_with("--"), "Action names should not be category labels (issue #451)")

## Issue #448: Verify no "hire office cat" action exists
func test_no_hire_office_cat_action():
	var actions = GameActions.get_all_actions()

	for action in actions:
		var action_id = action.get("id", "")
		var action_name = action.get("name", "")

		assert_ne(action_id, "hire_office_cat", "hire_office_cat action should not exist (issue #448)")
		assert_ne(action_id, "hire_cat", "hire_cat action should not exist (issue #448)")
		assert_false(action_name.to_lower().contains("hire") and action_name.to_lower().contains("cat"),
			"No action should be named 'hire cat' (issue #448)")

func test_cat_implemented_as_event():
	# Verify cat is implemented as an event, not an action
	var events = GameEvents.get_all_events()
	var cat_event = null

	for event in events:
		if event.get("id") == "stray_cat":
			cat_event = event
			break

	assert_not_null(cat_event, "Stray cat event should exist (issue #448)")
	assert_eq(cat_event.get("type"), "popup", "Cat should be a popup event")

## General affordability validation tests
func test_all_actions_costs_are_non_negative():
	# Ensure no action has negative costs (which would be confusing)
	var actions = GameActions.get_all_actions()

	for action in actions:
		var costs = action.get("costs", {})
		for resource in costs.keys():
			var cost_value = costs[resource]
			assert_gte(cost_value, 0, "Cost for %s in action %s should be non-negative" % [resource, action.get("id")])

func test_all_actions_have_valid_categories():
	# Ensure all actions have recognized categories
	var valid_categories = ["hiring", "resources", "research", "funding", "management", "influence", "strategic", "other"]
	var actions = GameActions.get_all_actions()

	for action in actions:
		var category = action.get("category", "")
		assert_true(category in valid_categories,
			"Action %s has invalid category: %s" % [action.get("id"), category])

func test_actions_with_reputation_cost_are_intentional():
	# Document actions that legitimately cost reputation
	# This helps catch accidental reputation costs like #449
	var actions = GameActions.get_all_actions()
	var allowed_rep_costs = ["release_warning", "sabotage_competitor"]  # Intentionally unethical actions

	for action in actions:
		var costs = action.get("costs", {})
		if costs.has("reputation"):
			var action_id = action.get("id")
			assert_true(action_id in allowed_rep_costs,
				"Action %s costs reputation - verify this is intentional (see issue #449)" % action_id)

## Validate action execution doesn't crash
func test_all_actions_execute_without_errors():
	# Ensure all actions can be executed without crashing
	# Set up state with sufficient resources
	state.money = 1000000
	state.action_points = 10
	state.reputation = 100
	state.research = 100
	state.compute = 100
	state.papers = 10

	var actions = GameActions.get_all_actions()
	for action in actions:
		var action_id = action.get("id")

		# Skip submenu actions (they don't execute directly)
		if action.get("is_submenu", false):
			continue

		# Try executing the action
		var result = GameActions.execute_action(action_id, state)

		# Should return a dictionary
		assert_typeof(result, TYPE_DICTIONARY,
			"Action %s should return a dictionary result" % action_id)

## Test state validation helpers
func test_can_afford_validates_all_resources():
	# Test that can_afford checks all resource types correctly
	state.money = 50000
	state.action_points = 2
	state.reputation = 30
	state.papers = 5

	# Should afford if all resources are available
	assert_true(state.can_afford({"money": 40000, "action_points": 1}), "Should afford with sufficient resources")

	# Should not afford if any resource is insufficient
	assert_false(state.can_afford({"money": 60000}), "Should not afford with insufficient money")
	assert_false(state.can_afford({"action_points": 5}), "Should not afford with insufficient AP")
	assert_false(state.can_afford({"reputation": 50}), "Should not afford with insufficient reputation")
	assert_false(state.can_afford({"papers": 10}), "Should not afford with insufficient papers")

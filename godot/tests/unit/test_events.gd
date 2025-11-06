extends GutTest
## Unit tests for GameEvents system

var state: GameState

func before_each():
	state = GameState.new("test_seed")
	GameEvents.reset_triggered_events()

func test_all_events_have_required_fields():
	# Test that all events have necessary fields
	var events = GameEvents.get_all_events()

	for event in events:
		assert_has(event, "id", "Event should have id")
		assert_has(event, "name", "Event should have name")
		assert_has(event, "description", "Event should have description")
		assert_has(event, "type", "Event should have type")
		assert_has(event, "trigger_type", "Event should have trigger_type")
		assert_has(event, "options", "Event should have options")

func test_event_count():
	# Test that we have expected number of events
	var events = GameEvents.get_all_events()
	assert_eq(events.size(), 5, "Should have 5 events")

func test_funding_crisis_triggers_correctly():
	# Test funding crisis triggers on turn 10 with low money
	state.turn = 10
	state.money = 40000  # Less than 50000

	var events = GameEvents.check_triggered_events(state, state.rng)

	assert_eq(events.size(), 1, "Should trigger funding crisis")
	assert_eq(events[0]["id"], "funding_crisis", "Should be funding crisis event")

func test_funding_crisis_no_trigger_wrong_turn():
	# Test funding crisis doesn't trigger on wrong turn
	state.turn = 5  # Not turn 10
	state.money = 40000

	var events = GameEvents.check_triggered_events(state, state.rng)

	assert_eq(events.size(), 0, "Should not trigger on wrong turn")

func test_funding_crisis_no_trigger_sufficient_money():
	# Test funding crisis doesn't trigger with sufficient money
	state.turn = 10
	state.money = 60000  # More than 50000

	var events = GameEvents.check_triggered_events(state, state.rng)

	assert_eq(events.size(), 0, "Should not trigger with sufficient money")

func test_funding_windfall_triggers_on_threshold():
	# Test funding windfall triggers with papers + reputation
	state.papers = 3.0
	state.reputation = 40.0

	var events = GameEvents.check_triggered_events(state, state.rng)

	var has_windfall = false
	for event in events:
		if event["id"] == "funding_windfall":
			has_windfall = true

	assert_true(has_windfall, "Should trigger funding windfall")

func test_non_repeatable_event_only_triggers_once():
	# Test that non-repeatable events don't trigger twice
	state.turn = 10
	state.money = 40000

	# First check - should trigger
	var events1 = GameEvents.check_triggered_events(state, state.rng)
	assert_eq(events1.size(), 1, "Should trigger first time")

	# Second check - should not trigger
	var events2 = GameEvents.check_triggered_events(state, state.rng)
	assert_eq(events2.size(), 0, "Should not trigger second time (non-repeatable)")

func test_reset_triggered_events_clears_history():
	# Test that reset clears triggered events history
	state.turn = 10
	state.money = 40000

	GameEvents.check_triggered_events(state, state.rng)
	GameEvents.reset_triggered_events()

	# Should be able to trigger again after reset
	var events = GameEvents.check_triggered_events(state, state.rng)
	assert_eq(events.size(), 1, "Should trigger again after reset")

func test_execute_event_choice_applies_effects():
	# Test that event choices apply their effects
	var events = GameEvents.get_all_events()
	var funding_crisis = events[0]  # First event should be funding crisis

	state.money = 40000
	var initial_money = state.money

	# Choose emergency fundraise option
	var result = GameEvents.execute_event_choice(funding_crisis, "emergency_fundraise", state)

	assert_true(result["success"], "Choice execution should succeed")
	assert_gt(state.money, initial_money, "Money should increase")

func test_execute_event_choice_checks_affordability():
	# Test that event choices check affordability
	var events = GameEvents.get_all_events()
	var ai_breakthrough = null

	for event in events:
		if event["id"] == "ai_breakthrough":
			ai_breakthrough = event
			break

	assert_not_null(ai_breakthrough, "AI breakthrough event should exist")

	state.money = 5000  # Not enough for safety review
	state.action_points = 0  # No AP

	# Try safety review option (costs $20k + 1 AP)
	var result = GameEvents.execute_event_choice(ai_breakthrough, "safety_review", state)

	assert_false(result["success"], "Should fail due to insufficient resources")

func test_random_events_deterministic():
	# Test that random events are deterministic with same seed
	state1 = GameState.new("deterministic_seed")
	state2 = GameState.new("deterministic_seed")

	state1.turn = 10
	state2.turn = 10

	var events1 = GameEvents.check_triggered_events(state1, state1.rng)
	var events2 = GameEvents.check_triggered_events(state2, state2.rng)

	assert_eq(events1.size(), events2.size(), "Same seed should trigger same events")

func test_condition_parser_less_than():
	# Test condition parser handles < operator
	state.money = 30000
	var result = GameEvents.evaluate_condition("money < 50000", state)
	assert_true(result, "Should evaluate money < 50000 as true")

	state.money = 60000
	result = GameEvents.evaluate_condition("money < 50000", state)
	assert_false(result, "Should evaluate money < 50000 as false")

func test_condition_parser_greater_than_or_equal():
	# Test condition parser handles >= operator
	state.papers = 3.0
	state.reputation = 40.0

	var result1 = GameEvents.evaluate_condition("papers >= 3", state)
	var result2 = GameEvents.evaluate_condition("reputation >= 40", state)

	assert_true(result1, "Should evaluate papers >= 3 as true")
	assert_true(result2, "Should evaluate reputation >= 40 as true")

func test_event_options_have_required_fields():
	# Test that all event options have necessary fields
	var events = GameEvents.get_all_events()

	for event in events:
		var options = event["options"]
		assert_gt(options.size(), 0, "Event should have at least one option")

		for option in options:
			assert_has(option, "id", "Option should have id")
			assert_has(option, "text", "Option should have text")
			assert_has(option, "effects", "Option should have effects")
			assert_has(option, "message", "Option should have message")

func test_talent_recruitment_is_repeatable():
	# Test that talent recruitment can trigger multiple times
	state.turn = 10  # Past min_turn

	# We can't guarantee it triggers due to randomness, but we can check it's marked repeatable
	var events = GameEvents.get_all_events()
	var talent_recruitment = null

	for event in events:
		if event["id"] == "talent_recruitment":
			talent_recruitment = event
			break

	assert_not_null(talent_recruitment, "Talent recruitment should exist")
	assert_true(talent_recruitment.get("repeatable", false), "Should be marked as repeatable")

func test_event_choice_modifies_staff_count():
	# Test that hiring through events increases staff
	var events = GameEvents.get_all_events()
	var talent_recruitment = null

	for event in events:
		if event["id"] == "talent_recruitment":
			talent_recruitment = event
			break

	state.money = 50000  # Ensure we can afford it
	var initial_staff = state.safety_researchers

	var result = GameEvents.execute_event_choice(talent_recruitment, "hire_discounted", state)

	assert_true(result["success"], "Hiring should succeed")
	assert_eq(state.safety_researchers, initial_staff + 1, "Staff count should increase")

func test_multi_resource_effects():
	# Test that events can affect multiple resources at once
	var events = GameEvents.get_all_events()
	var ai_breakthrough = null

	for event in events:
		if event["id"] == "ai_breakthrough":
			ai_breakthrough = event
			break

	var initial_doom = state.doom
	var initial_reputation = state.reputation
	var initial_research = state.research

	# Choose publish openly (affects doom, reputation, research)
	var result = GameEvents.execute_event_choice(ai_breakthrough, "publish_open", state)

	assert_true(result["success"], "Choice should succeed")
	assert_ne(state.doom, initial_doom, "Doom should change")
	assert_ne(state.reputation, initial_reputation, "Reputation should change")
	assert_ne(state.research, initial_research, "Research should change")

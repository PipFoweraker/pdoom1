extends GutTest
## Unit tests for GameEvents system

var state: GameState

func before_each():
	# WS-0: the fired-event registry (triggered_events / event_cooldowns) is now
	# per-GameState instance state, so a fresh GameState resets it automatically.
	state = GameState.new("test_seed")

func _find_event_by_id(events: Array, id: String) -> Dictionary:
	"""Helper to find a specific event in an array by id"""
	for event in events:
		if event.get("id", "") == id:
			return event
	return {}

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
	# Test that we have a substantial number of events
	var events = GameEvents.get_all_events()
	assert_gt(events.size(), 10, "Should have more than 10 events")

func test_funding_crisis_exists():
	# Test funding crisis event exists and has correct structure
	var events = GameEvents.get_all_events()
	var crisis = _find_event_by_id(events, "funding_crisis")

	assert_false(crisis.is_empty(), "funding_crisis event should exist")
	assert_eq(crisis["type"], "popup", "Should be a popup type")

func test_funding_crisis_triggers_with_low_money():
	# Test funding crisis triggers on correct turn with low money
	state.turn = 10
	state.money = 40000  # Less than 50000

	var events = GameEvents.check_triggered_events(state, state.rng)

	var has_crisis = not _find_event_by_id(events, "funding_crisis").is_empty()
	assert_true(has_crisis, "Should trigger funding crisis with low money on turn 10")

func test_funding_crisis_no_trigger_wrong_turn():
	# Test funding crisis doesn't trigger on wrong turn
	state.turn = 5  # Not turn 10
	state.money = 40000

	var events = GameEvents.check_triggered_events(state, state.rng)

	var has_crisis = not _find_event_by_id(events, "funding_crisis").is_empty()
	assert_false(has_crisis, "Should not trigger funding crisis on wrong turn")

func test_funding_crisis_no_trigger_sufficient_money():
	# Test funding crisis doesn't trigger with sufficient money
	state.turn = 10
	state.money = 60000  # More than 50000

	var events = GameEvents.check_triggered_events(state, state.rng)

	var has_crisis = not _find_event_by_id(events, "funding_crisis").is_empty()
	assert_false(has_crisis, "Should not trigger funding crisis with sufficient money")

func test_funding_windfall_triggers_on_threshold():
	# Test funding windfall triggers with papers + reputation
	state.turn = 5  # #568: events are suppressed before FIRST_EVENT_TURN
	state.papers = 3.0
	state.reputation = 40.0

	var events = GameEvents.check_triggered_events(state, state.rng)

	var has_windfall = not _find_event_by_id(events, "funding_windfall").is_empty()
	assert_true(has_windfall, "Should trigger funding windfall")

func test_non_repeatable_event_only_triggers_once():
	# Test that non-repeatable events don't trigger twice
	state.turn = 10
	state.money = 40000

	# First check - should trigger funding_crisis
	var events1 = GameEvents.check_triggered_events(state, state.rng)
	var has_crisis_1 = not _find_event_by_id(events1, "funding_crisis").is_empty()
	assert_true(has_crisis_1, "Should trigger funding crisis first time")

	# Second check - funding_crisis should not fire again
	var events2 = GameEvents.check_triggered_events(state, state.rng)
	var has_crisis_2 = not _find_event_by_id(events2, "funding_crisis").is_empty()
	assert_false(has_crisis_2, "Should not trigger funding crisis second time (non-repeatable)")

func test_reset_triggered_events_clears_history():
	# Test that clearing the per-GameState registry clears triggered events history.
	# WS-0: the fired-event registry lives on the GameState instance, so the
	# instance-level reset is clearing state.triggered_events / state.event_cooldowns.
	state.turn = 10
	state.money = 40000
	GameEvents.check_triggered_events(state, state.rng)  # consumes funding_crisis on `state`

	GameEvents.check_triggered_events(state, state.rng)
	state.triggered_events.clear()
	state.event_cooldowns.clear()

	# Should be able to trigger again after reset
	var events = GameEvents.check_triggered_events(state, state.rng)
	var has_crisis = not _find_event_by_id(events, "funding_crisis").is_empty()
	assert_true(has_crisis, "A fresh GameState should have clean event history")

# --- #568 regression: event pacing (no pre-first-turn spawn + per-turn cap) ---

func test_no_events_before_first_turn():
	# #568(a): the player's very first turn (turn 1) must not open with an event,
	# even when a threshold event's condition is already satisfied.
	state.turn = 1
	state.papers = 3.0
	state.reputation = 40.0  # would otherwise satisfy funding_windfall
	var events = GameEvents.check_triggered_events(state, state.rng)
	assert_eq(events.size(), 0, "No event should fire before the first turn is played (#568)")

func test_events_resume_from_first_event_turn():
	# #568(a): once FIRST_EVENT_TURN is reached, qualifying events fire as normal.
	state.turn = GameEvents.FIRST_EVENT_TURN
	state.papers = 3.0
	state.reputation = 40.0
	var events = GameEvents.check_triggered_events(state, state.rng)
	assert_false(_find_event_by_id(events, "funding_windfall").is_empty(),
		"Threshold events should fire from FIRST_EVENT_TURN onward (#568)")

func test_new_events_capped_per_turn():
	# #568(b): a burst of simultaneously-qualifying events must not all fire at once.
	# Inject a flood of always-true scenario events and assert the cap holds.
	state.turn = 5
	var flood: Array[Dictionary] = []
	for i in range(6):
		flood.append({
			"id": "flood_%d" % i,
			"name": "Flood %d" % i,
			"description": "test flood event",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "true",
			"repeatable": false,
			"options": [{"id": "ok", "text": "OK", "effects": {}, "message": "ok"}],
		})
	state.set_meta("scenario_events", flood)

	var events = GameEvents.check_triggered_events(state, state.rng)
	assert_eq(events.size(), GameEvents.MAX_NEW_EVENTS_PER_TURN,
		"At most MAX_NEW_EVENTS_PER_TURN events should fire in one turn (#568)")
	assert_true(events.size() <= 2, "Cap should keep the per-turn burst small (#568)")

func test_capped_events_defer_not_lost():
	# #568(b): events squeezed out by the cap are NOT marked, so they can still fire
	# on a later turn (deferred, not dropped).
	# Isolate from the live historical deck (#534) so only our flood competes for slots.
	var saved_events := []
	if EventService:
		saved_events = EventService.transformed_events.duplicate()
		EventService.transformed_events.clear()

	state.turn = 5
	var flood: Array[Dictionary] = []
	for i in range(6):
		flood.append({
			"id": "flood_%d" % i,
			"name": "Flood %d" % i,
			"description": "test flood event",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "true",
			"repeatable": false,
			"options": [{"id": "ok", "text": "OK", "effects": {}, "message": "ok"}],
		})
	state.set_meta("scenario_events", flood)

	var fired_flood := {}
	# Drain over several turns; every flood event should eventually fire exactly once.
	for _t in range(10):
		var events = GameEvents.check_triggered_events(state, state.rng)
		assert_true(events.size() <= GameEvents.MAX_NEW_EVENTS_PER_TURN,
			"Cap must hold on every turn (#568)")
		for e in events:
			var eid: String = e.get("id", "")
			if eid.begins_with("flood_"):
				fired_flood[eid] = true
		state.turn += 1

	if EventService:
		EventService.transformed_events = saved_events

	assert_eq(fired_flood.size(), 6, "All deferred events should eventually fire, none lost (#568)")

func test_execute_event_choice_applies_effects():
	# Test that event choices apply their effects
	var events = GameEvents.get_all_events()
	var funding_crisis = _find_event_by_id(events, "funding_crisis")

	assert_false(funding_crisis.is_empty(), "Funding crisis should exist")

	state.money = 40000
	var initial_money = state.money

	# Choose emergency fundraise option
	var result = GameEvents.execute_event_choice(funding_crisis, "emergency_fundraise", state)

	assert_true(result["success"], "Choice execution should succeed")
	assert_gt(state.money, initial_money, "Money should increase")

func test_execute_event_choice_checks_affordability():
	# Test that event choices check affordability
	var events = GameEvents.get_all_events()
	var ai_breakthrough = _find_event_by_id(events, "ai_breakthrough")

	assert_false(ai_breakthrough.is_empty(), "AI breakthrough event should exist")

	state.money = 5000  # Not enough for safety review
	state.action_points = 0  # No AP

	# Try safety review option (costs $20k + 1 AP)
	var result = GameEvents.execute_event_choice(ai_breakthrough, "safety_review", state)

	assert_false(result["success"], "Should fail due to insufficient resources")

func test_random_events_deterministic():
	# Test that random events are deterministic with same seed
	var state1 = GameState.new("deterministic_seed")
	var state2 = GameState.new("deterministic_seed")

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
	var talent_recruitment = _find_event_by_id(events, "talent_recruitment")

	assert_false(talent_recruitment.is_empty(), "Talent recruitment should exist")
	assert_true(talent_recruitment.get("repeatable", false), "Should be marked as repeatable")

func test_event_choice_modifies_staff_count():
	# Test that hiring through events increases staff
	var events = GameEvents.get_all_events()
	var talent_recruitment = _find_event_by_id(events, "talent_recruitment")

	state.money = 50000  # Ensure we can afford it
	var initial_staff = state.safety_researchers

	var result = GameEvents.execute_event_choice(talent_recruitment, "hire_discounted", state)

	assert_true(result["success"], "Hiring should succeed")
	assert_eq(state.safety_researchers, initial_staff + 1, "Staff count should increase")

func test_multi_resource_effects():
	# Test that events can affect multiple resources at once
	var events = GameEvents.get_all_events()
	var ai_breakthrough = _find_event_by_id(events, "ai_breakthrough")

	var initial_doom = state.doom
	var initial_reputation = state.reputation
	var initial_research = state.research

	# Choose publish openly (affects doom, reputation, research)
	var result = GameEvents.execute_event_choice(ai_breakthrough, "publish_open", state)

	assert_true(result["success"], "Choice should succeed")
	assert_ne(state.doom, initial_doom, "Doom should change")
	assert_ne(state.reputation, initial_reputation, "Reputation should change")
	assert_ne(state.research, initial_research, "Research should change")

# ---------------------------------------------------------------------------
# #631: poaching outcome correctness + legibility
# ---------------------------------------------------------------------------

func _make_researcher(spec: String, name: String, loyalty: int) -> Researcher:
	"""Deterministic researcher for poaching tests (no RNG, explicit loyalty)."""
	var r := Researcher.new()
	r.specialization = spec
	r.researcher_name = name
	r.loyalty = loyalty
	return r

func test_lose_researcher_removes_exactly_one_least_loyal_and_names_them():
	# researcher_poached / let_them_go uses the `lose_researcher` effect.
	# Loyalty is poaching resistance (researcher.gd:18) -- the LEAST loyal leaves.
	state.add_researcher(_make_researcher("safety", "Loyal Larry", 90))
	state.add_researcher(_make_researcher("safety", "Fickle Fran", 20))
	state.add_researcher(_make_researcher("capabilities", "Steady Sam", 70))
	var before := state.researchers.size()

	var events = GameEvents.get_all_events()
	var poach = _find_event_by_id(events, "researcher_poached")
	assert_false(poach.is_empty(), "researcher_poached event should exist")

	var result = GameEvents.execute_event_choice(poach, "let_them_go", state)

	assert_true(result["success"], "Letting them go should succeed")
	assert_eq(state.researchers.size(), before - 1, "Exactly one researcher removed")
	# The least loyal (Fickle Fran, loyalty 20) is the one poached.
	var names := []
	for r in state.researchers:
		names.append(r.researcher_name)
	assert_does_not_have(names, "Fickle Fran", "Least-loyal researcher was poached")
	assert_has(names, "Loyal Larry", "Loyal researcher retained")
	# Legibility: the log names WHO left.
	assert_true(result.has("messages"), "Result carries staffing notes")
	var joined: String = "\n".join(result["messages"])
	assert_string_contains(joined, "Fickle Fran", "Departure note names the researcher")

func test_let_them_go_decrements_legacy_safety_count():
	# The legacy scalar count must track the removal too (game_state accounting).
	state.add_researcher(_make_researcher("safety", "A", 10))
	state.add_researcher(_make_researcher("safety", "B", 80))
	state.add_researcher(_make_researcher("safety", "C", 80))
	var before_count := state.safety_researchers
	var events = GameEvents.get_all_events()
	var poach = _find_event_by_id(events, "researcher_poached")
	GameEvents.execute_event_choice(poach, "let_them_go", state)
	assert_eq(state.safety_researchers, before_count - 1, "Legacy safety count drops by one")

func test_rival_poaching_let_go_actually_removes_a_researcher():
	# Regression for the #631 no-op: rival_poaching/let_go used safety_researchers:-1,
	# which Resources.add rejects and the old create-loop ran range(-1) == empty,
	# so NOBODY left even though flavor said "Lost researcher".
	state.add_researcher(_make_researcher("safety", "Keeper", 95))
	state.add_researcher(_make_researcher("safety", "Leaver", 15))
	var before := state.researchers.size()
	var before_money := state.money

	var events = GameEvents.get_all_events()
	var rival = _find_event_by_id(events, "rival_poaching")
	assert_false(rival.is_empty(), "rival_poaching event should exist")

	var result = GameEvents.execute_event_choice(rival, "let_go", state)

	assert_true(result["success"], "let_go should succeed")
	assert_eq(state.researchers.size(), before - 1, "One safety researcher actually leaves")
	assert_eq(state.money, before_money + 20000.0, "Saved $20k as flavor states")
	assert_true(result.has("messages"), "Departure is legible")
	var joined: String = "\n".join(result["messages"])
	assert_string_contains(joined, "Leaver", "Least-loyal safety researcher named")

func test_poach_with_no_researchers_is_safe_noop():
	# No researchers -> no crash, no phantom removal, no staffing note.
	assert_eq(state.researchers.size(), 0, "Start empty")
	var events = GameEvents.get_all_events()
	var poach = _find_event_by_id(events, "researcher_poached")
	var result = GameEvents.execute_event_choice(poach, "let_them_go", state)
	assert_true(result["success"], "Still resolves")
	assert_eq(state.researchers.size(), 0, "Nobody removed")
	assert_false(result.has("messages"), "No staffing note when nobody leaves")

# ---------------------------------------------------------------------------
# #631 follow-up: GameEvents.remove_researchers() -- shared staffing-loss helper
# used by both event-driven poaches and risk-pool events (insider_threat).
# ---------------------------------------------------------------------------

func test_remove_researchers_removes_least_loyal_first():
	state.add_researcher(_make_researcher("safety", "Loyal Larry", 90))
	state.add_researcher(_make_researcher("safety", "Fickle Fran", 20))
	var before := state.researchers.size()

	var notes := GameEvents.remove_researchers(state, 1, "", "resigned")

	assert_eq(state.researchers.size(), before - 1, "Exactly one researcher removed")
	var names := []
	for r in state.researchers:
		names.append(r.researcher_name)
	assert_does_not_have(names, "Fickle Fran", "Least-loyal researcher resigned")
	assert_eq(notes.size(), 1, "One departure note returned")
	assert_string_contains(notes[0], "Fickle Fran", "Note names who left")
	assert_string_contains(notes[0], "resigned", "Note uses the supplied reason, not a hardcoded 'poached'")

func test_remove_researchers_respects_spec_filter():
	state.add_researcher(_make_researcher("safety", "Safety Sally", 10))
	state.add_researcher(_make_researcher("capabilities", "Cap Carl", 5))

	GameEvents.remove_researchers(state, 1, "capabilities", "resigned")

	var names := []
	for r in state.researchers:
		names.append(r.researcher_name)
	assert_has(names, "Safety Sally", "Safety researcher untouched by capabilities-filtered removal")
	assert_does_not_have(names, "Cap Carl", "Capabilities researcher removed")

func test_remove_researchers_safe_noop_when_empty():
	assert_eq(state.researchers.size(), 0, "Start empty")
	var notes := GameEvents.remove_researchers(state, 1, "", "resigned")
	assert_eq(notes.size(), 0, "No notes when nobody is available to remove")
	assert_eq(state.researchers.size(), 0, "Still nobody")

# ---------------------------------------------------------------------------
# #631 class-killer property tests: an unrecognized effect/cost key in the event
# data is SILENTLY dropped at apply time (ResourceAccessor.add returns false and
# the match falls through; can_afford ignores unknown cost keys) -- that silent
# fall-through is exactly how the "flavor says X, nothing happens" bug class was
# born (rival_poaching let_go, insider_threat Key Resignation). These tests pin
# the data to the handled vocabulary so a typo'd or unimplemented key fails CI
# instead of shipping as a no-op.
# ---------------------------------------------------------------------------

# Every effect key execute_event_choice actually applies (scalars via
# ResourceAccessor.add + the non-scalar match arms in events.gd).
const HANDLED_EFFECT_KEYS := [
	"money", "compute", "research", "papers", "reputation", "doom",
	"compute_engineers",  # scalar legacy count (ResourceAccessor.add)
	"safety_researchers", "capability_researchers",  # staffing arms
	"has_cat", "lose_researcher",
	"loyalty_hit",  # employee_burnout "Push Through" interim content (WORKSHOP_2_BACKLOG ruling)
]

# Every cost key can_afford/spend_resources actually checks and deducts.
const PAYABLE_COST_KEYS := [
	"money", "compute", "research", "papers", "reputation", "action_points",
]

func test_all_core_event_effect_keys_are_handled():
	for event in GameEvents.get_all_events():
		for option in event.get("options", []):
			for key in option.get("effects", {}).keys():
				assert_true(key in HANDLED_EFFECT_KEYS,
					"%s/%s effect key '%s' is not handled by execute_event_choice -- it would be a silent no-op (#631)" % [
						event.get("id", "?"), option.get("id", "?"), key])

func test_all_core_event_cost_keys_are_payable():
	for event in GameEvents.get_all_events():
		for option in event.get("options", []):
			for key in option.get("costs", {}).keys():
				assert_true(key in PAYABLE_COST_KEYS,
					"%s/%s cost key '%s' is not checked by can_afford/spend_resources -- it would be silently free (#631)" % [
						event.get("id", "?"), option.get("id", "?"), key])

# ---------------------------------------------------------------------------
# employee_burnout / "Push Through" -- interim loyalty-hit content
# (WORKSHOP_2_BACKLOG "Burnout outcome model -- RULED", Pip 2026-07-13, resolves
# the #631/#635 AMBIGUOUS case: flavor said "considering leaving", effect was
# doom-only). Push Through must no longer be toothless-beyond-doom: it now also
# dents loyalty on the least-loyal researchers, named, with NO removal and NO
# efficiency/leave debuff (that's L2 #613's job per the ruling).
# ---------------------------------------------------------------------------

func test_push_through_burnout_docks_loyalty_least_loyal_first_no_removal():
	state.add_researcher(_make_researcher("safety", "Frayed Fiona", 20))
	state.add_researcher(_make_researcher("safety", "Steady Sam", 80))
	state.add_researcher(_make_researcher("capabilities", "Weary Wade", 10))
	var before_count := state.researchers.size()
	var before_doom := state.doom

	var events = GameEvents.get_all_events()
	var burnout = _find_event_by_id(events, "employee_burnout")
	assert_false(burnout.is_empty(), "employee_burnout event should exist")

	var result = GameEvents.execute_event_choice(burnout, "ignore_burnout", state)

	assert_true(result["success"], "Push Through should succeed")
	assert_eq(state.researchers.size(), before_count, "Push Through removes nobody (interim: loyalty-hit only)")
	assert_eq(state.doom, before_doom + 3.0, "Doom still applies as flavor states")

	# The two least-loyal researchers (Weary Wade 10, Frayed Fiona 20) take the hit;
	# the most-loyal (Steady Sam 80) is untouched.
	var by_name := {}
	for r in state.researchers:
		by_name[r.researcher_name] = r
	assert_eq(by_name["Weary Wade"].loyalty, 0, "Least-loyal researcher's loyalty drops (clamped at 0)")
	assert_eq(by_name["Frayed Fiona"].loyalty, 5, "Second least-loyal researcher's loyalty drops by 15")
	assert_eq(by_name["Steady Sam"].loyalty, 80, "Most-loyal, unaffected researcher keeps his loyalty")

	# Legibility: the affected researchers are named in the log (#631 pattern).
	assert_true(result.has("messages"), "Loyalty hit is legible, not a silent stat change")
	var joined: String = "\n".join(result["messages"])
	assert_string_contains(joined, "Weary Wade", "Log names an affected researcher")
	assert_string_contains(joined, "Frayed Fiona", "Log names the other affected researcher")
	assert_does_not_have_string(joined, "Steady Sam", "Unaffected researcher not named")

func test_push_through_burnout_with_no_researchers_is_safe_noop():
	assert_eq(state.researchers.size(), 0, "Start empty")
	var events = GameEvents.get_all_events()
	var burnout = _find_event_by_id(events, "employee_burnout")
	var result = GameEvents.execute_event_choice(burnout, "ignore_burnout", state)
	assert_true(result["success"], "Still resolves with nobody on staff")
	assert_eq(state.researchers.size(), 0, "Nobody to remove or dock")
	assert_false(result.has("messages"), "No loyalty-hit note when nobody was affected")

func assert_does_not_have_string(haystack: String, needle: String, msg: String) -> void:
	assert_false(haystack.contains(needle), msg)

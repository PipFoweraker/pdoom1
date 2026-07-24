extends GutTest
## Regression: choosing a window's own option resolves against the window the dialog
## PRESENTED, not blindly window_queue[0] (playtest 2026-07-24 "Unknown option: build_upon"
## / "acknowledge"). The event_dialog shows queued windows one at a time and advances on
## every press; a prior window left unresolved (a HANDLE that failed for lack of Attention
## stays queued) desynced the queue head from the dialog, so the chosen option_id -- absent
## from the stale head -- threw a bogus "Unknown option". Fix: MonthController.
## resolve_current_window_option(option_id, event) matches the queued window by id.

func _state() -> GameState:
	var s := GameState.new("window-option-routing-seed")
	s.money = 245000.0
	s.reputation = 50.0
	return s


func _research_event() -> Dictionary:
	# Mirrors EventService._generate_options for the "research" category (build_upon / acknowledge).
	return {
		"id": "hist_some_paper", "name": "Some Paper", "type": "popup", "category": "research",
		"options": [
			{"id": "build_upon", "text": "Build", "costs": {"action_points": 1, "money": 10000},
			 "effects": {"research": 15, "doom": 1}, "message": "Advancing."},
			{"id": "acknowledge", "text": "Ack", "costs": {}, "effects": {"research": 2}, "message": "Noted."},
		],
	}


func _policy_event() -> Dictionary:
	return {
		"id": "hist_some_policy", "name": "Some Policy", "type": "popup", "category": "policy",
		"options": [
			{"id": "support", "text": "Support", "costs": {"action_points": 1},
			 "effects": {"reputation": 5, "doom": -3}, "message": "Supported."},
			{"id": "stay_neutral", "text": "Neutral", "costs": {}, "effects": {}, "message": "Neutral."},
		],
	}


func _paused_controller(s: GameState, windows: Array) -> MonthController:
	var mc := MonthController.new(s, null)
	mc.window_queue = windows
	mc.status = MonthController.Status.PAUSED_ON_WINDOW
	return mc


func _exhaust_attention(s: GameState) -> void:
	# No reserve, no free capacity, no WIP to cannibalize -> any HANDLE verb fails.
	s.month_plan.attention_reserved = 0
	s.month_plan.attention_spent = s.month_plan.attention_total
	s.month_plan.queued_strategic = []


func test_head_window_stuck_does_not_misroute_a_later_choice():
	# The exact playtest sequence: the head window's HANDLE fails (no Attention) and stays
	# queued; the dialog advances to the research window; the player picks acknowledge.
	var s := _state()
	_exhaust_attention(s)
	var mc := _paused_controller(s, [_policy_event(), _research_event()])

	var r1 := mc.resolve_current_window_option("support")
	assert_false(r1.get("success", true), "HANDLE fails with no Attention; policy window stays at head")
	assert_eq(mc.window_queue.size(), 2, "the stuck window is NOT popped")

	# acknowledge maps to the zero-cost IGNORE path (no Attention needed).
	var r2 := mc.resolve_current_window_option("acknowledge", _research_event())
	assert_true(r2.get("success", false), "acknowledge resolves against the research window the dialog showed")
	assert_false(String(r2.get("message", "")).contains("Unknown option"),
		"no bogus 'Unknown option' -- the RIGHT window was targeted")
	assert_eq(mc.window_queue.size(), 1, "only the research window was removed; the policy window stays")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hist_some_policy",
		"the still-open policy window is the one left queued")


func test_build_upon_on_a_non_head_window_applies_effects():
	var s := _state()
	s.month_plan.set_reserve(3)  # Attention available for a HANDLE
	var mc := _paused_controller(s, [_policy_event(), _research_event()])
	var money0 := s.money

	var r := mc.resolve_current_window_option("build_upon", _research_event())
	assert_true(r.get("success", false), "build_upon on a non-head window resolves cleanly")
	assert_eq(s.money, money0 - 10000.0, "the chosen option's in-fiction money cost applied")
	assert_eq(float((r.get("deltas", {}) as Dictionary).get("research", 0.0)), 15.0,
		"the option's research effect was applied")
	assert_eq(mc.window_queue.size(), 1, "the research window was removed by id-match, not the head")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hist_some_policy",
		"the head (policy) window is untouched")


func test_head_choice_still_resolves_the_head():
	# The aligned (normal) case is unchanged: no event supplied -> resolve the head.
	var s := _state()
	s.month_plan.set_reserve(3)
	var mc := _paused_controller(s, [_research_event(), _policy_event()])
	var r := mc.resolve_current_window_option("acknowledge")
	assert_true(r.get("success", false), "the head window's option resolves via the legacy head fallback")
	assert_eq(mc.window_queue.size(), 1, "the head was removed")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hist_some_policy",
		"the research head was the one removed")

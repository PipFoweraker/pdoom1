extends GutTest
## L1 (#612 / ADR-0009): day-tick playback within a month — auto-pause-on-window, the
## window demand budget, month-boundary plan reset, and a headless playable-loop smoke.

func _state() -> GameState:
	var s := GameState.new("month-controller-seed")
	s.money = 245000.0
	s.reputation = 50.0
	return s


func _window(id: String, unignorable := false) -> Dictionary:
	return {
		"id": id,
		"type": "popup",
		"delivery_tier": "window",
		"event_class": "deferrable",
		"unignorable": unignorable,
		"options": [
			{"id": "handle", "costs": {}, "effects": {"reputation": 1}, "message": "handled"},
			{"id": "ignore", "costs": {}, "effects": {"reputation": -1}, "message": "ignored"},
		],
		"window": {"attention_cost": 1, "handle_option": "handle", "ignore_option": "ignore"},
	}


func test_demand_budget_downgrades_excess_windows_to_feed():
	var s := _state()
	var mc := MonthController.new(s, null)
	var events := []
	for i in range(6):
		events.append(_window("w%d" % i))
	mc._dispatch(events)  # budget default 3
	assert_eq(mc.window_queue.size(), 3, "only the budget's worth demand a decision")
	assert_true(mc.feed_log.size() >= 3, "the excess windows downgrade to the feed")


func test_feed_items_carry_provenance():
	var s := _state()
	var mc := MonthController.new(s, null)
	mc._dispatch([{"delivery_tier": "feed", "id": "memo", "source_id": "board_chair"}])
	assert_eq(mc.feed_log.size(), 1)
	assert_eq(String(mc.feed_log[0].source_id), "board_chair", "feed item keeps its source")


func test_advance_tick_pauses_on_window_then_resumes():
	var s := _state()
	var mc := MonthController.new(s, null)  # null tm: no sim, drives dispatch/pause only
	s.pending_events.assign([_window("crisis")])
	var r := mc.advance_tick()
	assert_eq(String(r.status), "paused_on_window", "a window auto-pauses playback")
	assert_true(mc.is_paused())
	assert_eq((r.windows as Array).size(), 1)
	var res := mc.resolve_current_window("ignore")
	assert_true(res.success, "resolving the window succeeds")
	assert_false(mc.is_paused(), "playback resumes once the queue empties")


func test_skip_unanswered_window_auto_ignores_with_penalty():
	var s := _state()
	var mc := MonthController.new(s, null)
	s.pending_events.assign([_window("lapsing")])
	mc.advance_tick()
	var rep0 := s.reputation
	var res := mc.skip_current_window()
	assert_true(res.success, "an ignorable window can lapse")
	assert_true(s.reputation < rep0, "auto-ignore applies the list price + mild penalty")


func test_unignorable_window_refuses_skip():
	var s := _state()
	var mc := MonthController.new(s, null)
	s.pending_events.assign([_window("subpoena", true)])
	mc.advance_tick()
	var res := mc.skip_current_window()
	assert_false(res.success, "an unignorable window cannot be skipped")
	assert_true(mc.is_paused(), "it stays open, still demanding a decision")


func test_month_boundary_opens_fresh_plan_phase():
	var s := _state()
	var mc := MonthController.new(s, null)
	s.month_plan.queue_strategic("wip", 8, 2, 0)  # spend 8 Attention this month
	assert_eq(s.month_plan.available(), 12, "8 spent this month")
	# Jump the tick into a later calendar month, then advance: a new plan month opens.
	s.turn = 40
	var r := mc.advance_tick()
	assert_true(r.month_opened, "crossing the calendar month opens a new plan phase")
	assert_eq(s.month_plan.available(), 20, "fresh full Attention grant — reserve evaporated")


func test_headless_playable_month_loop_runs():
	# The acceptance smoke: drive real ticks through TurnManager, answering any window that
	# fires, and confirm the month loop advances without crashing and rolls the plan month.
	var s := _state()
	var tm = TurnManager.new(s)
	var mc := MonthController.new(s, tm)
	var guard := 0
	var ticks := 0
	while ticks < 40 and guard < 500:
		guard += 1
		var r := mc.advance_tick()
		if String(r.status) == "paused_on_window":
			# Answer every open window (ignore is always safe) to resume playback.
			var wguard := 0
			while mc.is_paused() and wguard < 20:
				wguard += 1
				mc.resolve_current_window("ignore")
		else:
			ticks += 1
	assert_true(s.turn >= 30, "the loop advanced many day ticks (turn=%d)" % s.turn)
	assert_true(s.month_plan.month_ordinal >= 1, "at least one plan-month boundary rolled")
	assert_false(s.game_over and s.turn < 5, "did not die instantly / hang")

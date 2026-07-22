extends GutTest
## L1 (#612 / ADR-0009): day-tick playback within a month -- auto-pause-on-window, the
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
	assert_eq(s.month_plan.available(), 20, "fresh full Attention grant -- reserve evaporated")
	# The boundary tick is HELD OPEN as the plan phase (playable path: the next
	# end_month() executes it -- never auto-executed, or consequences would double-run).
	assert_eq(String(r.status), "month_open", "boundary tick reports the plan phase opening")
	assert_true(mc.month_open_pending, "boundary tick held open for planning")
	assert_eq(s.current_phase, GameState.TurnPhase.ACTION_SELECTION, "plan phase is open")
	assert_true(s.can_end_turn, "the player can commit the next month plan")


func test_resolve_window_by_option_pays_reserve_first():
	# The v1 dialog path: the player picks one of the event's own options; a non-ignore
	# option is a HANDLE paid reserve-first (payment source still hits the replay artifact).
	var s := _state()
	var mc := MonthController.new(s, null)
	s.month_plan.set_reserve(3)
	s.pending_events.assign([_window("opt_crisis")])
	mc.advance_tick()
	var res := mc.resolve_current_window_option("handle")
	assert_true(res.success, "choosing the handle option resolves the window")
	assert_eq(String(res.payment_source), "reserve", "paid from the crisp reserve first")
	assert_eq(s.month_plan.reserve_remaining(), 2, "the window's Attention cost (1) was drawn")
	assert_false(mc.is_paused(), "playback resumes")


func test_resolve_window_by_ignore_option_maps_to_ignore():
	var s := _state()
	var mc := MonthController.new(s, null)
	s.month_plan.set_reserve(3)
	s.pending_events.assign([_window("opt_pass")])
	mc.advance_tick()
	var res := mc.resolve_current_window_option("ignore")
	assert_true(res.success, "the window's ignore option resolves as IGNORE")
	assert_eq(String(res.payment_source), "ignore", "recorded as ignore, not handle")
	assert_eq(s.month_plan.reserve_remaining(), 3, "IGNORE draws no Attention")


func test_failed_verb_leaves_window_open_and_resolvable():
	# Regression (balance-sweep finding): the four-verb path popped the window BEFORE the
	# resolver validated payment, so handle_reserve with an empty reserve silently dropped
	# the window -- no effect, no charge, no window. Latent in the v1 dialog (the option
	# path guards correctly) but fatal to the future plan-screen UI.
	var s := _state()
	var mc := MonthController.new(s, null)
	s.month_plan.set_reserve(0)  # nothing held -- handle_reserve must fail
	s.pending_events.assign([_window("underfunded")])
	mc.advance_tick()
	var res := mc.resolve_current_window("handle_reserve")  # window costs 1, reserve 0
	assert_false(res.success, "handle_reserve fails with an empty reserve")
	assert_true(mc.is_paused(), "playback stays paused on the unanswered window")
	assert_eq(mc.window_queue.size(), 1, "the window was NOT silently dropped")
	assert_eq(s.pending_events.size(), 1, "the serialized pause point still holds it")
	var res2 := mc.resolve_current_window("handle_cannibalize")
	assert_true(res2.success, "the same window resolves via another verb")
	assert_false(mc.is_paused(), "playback resumes after the real resolution")


func test_headless_playable_month_loop_runs():
	# The acceptance smoke: drive real ticks through TurnManager, answering any window that
	# fires and committing the plan at each held-open boundary (simulating the End Turn
	# button), and confirm the month loop advances and rolls the plan month.
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
			if mc.month_open_pending:
				tm.execute_turn()  # plan commit for a boundary that paused on a window
			ticks += 1
		elif String(r.status) == "month_open":
			# Boundary tick held open for planning -- commit an (empty) plan and play on,
			# mirroring GameManager.end_month().
			tm.execute_turn()
			ticks += 1
		else:
			ticks += 1
	assert_true(s.turn >= 30, "the loop advanced many day ticks (turn=%d)" % s.turn)
	assert_true(s.month_plan.month_ordinal >= 1, "at least one plan-month boundary rolled")
	assert_false(s.game_over and s.turn < 5, "did not die instantly / hang")

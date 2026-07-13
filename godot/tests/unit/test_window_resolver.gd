extends GutTest
## L1 (#612 / ADR-0009 §3, ADR-0012): response-window resolution — the costed menu
## HANDLE-from-reserve / HANDLE-by-cannibalizing / DEFER / IGNORE, and the auto-IGNORE
## of unanswered windows with a mild reputation penalty.

func _state() -> GameState:
	var s := GameState.new("window-resolver-seed")
	s.money = 245000.0
	s.reputation = 50.0
	return s


func _deferrable_window() -> Dictionary:
	return {
		"id": "vendor_dispute",
		"type": "popup",
		"delivery_tier": "window",
		"event_class": "deferrable",
		"source_id": "legal_counsel",
		"options": [
			{"id": "settle", "costs": {"money": 20000, "action_points": 1}, "effects": {"reputation": 5}, "message": "Settled"},
			{"id": "let_it_ride", "costs": {}, "effects": {"reputation": -3}, "message": "Ignored the notice"},
		],
		"window": {"attention_cost": 2, "handle_option": "settle", "ignore_option": "let_it_ride", "defer": {"factory": "loan", "amount": 20000}},
	}


func test_handle_from_reserve_pays_reserve_and_applies_handle_effect():
	var s := _state()
	s.month_plan.set_reserve(3)
	var money0 := s.money
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "handle_reserve")
	assert_true(r.success, "reserve covers the handle")
	assert_eq(String(r.payment_source), "reserve")
	assert_eq(int(r.attention_paid), 2, "the window's Attention cost is drawn")
	assert_eq(s.month_plan.reserve_remaining(), 1, "reserve consumed by the amount")
	assert_eq(s.money, money0 - 20000.0, "the in-fiction money cost of the handle option applies")
	assert_almost_eq(s.reputation, 55.0, 0.01, "the handle effect (+5 rep) applies")


func test_handle_from_reserve_fails_without_enough_reserve():
	var s := _state()
	s.month_plan.set_reserve(1)  # window costs 2
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "handle_reserve")
	assert_false(r.success, "insufficient reserve cannot handle from reserve")


func test_handle_by_cannibalizing_ignores_legacy_ap():
	var s := _state()
	s.action_points = 0  # prove Attention, not AP, is the window currency (AP stripped)
	s.month_plan.set_reserve(0)  # 20 available
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "handle_cannibalize")
	assert_true(r.success, "cannibalizing free capacity handles the window even with zero AP")
	assert_eq(String(r.payment_source), "cannibalize")
	assert_almost_eq(s.reputation, 55.0, 0.01, "handle effect applied")


func test_defer_mints_a_ledger_entry():
	var s := _state()
	var entries0: int = s.ledger.entries.size()
	var money0 := s.money
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "defer")
	assert_true(r.success, "a deferrable window can be deferred")
	assert_eq(s.ledger.entries.size(), entries0 + 1, "DEFER mints a ledger entry")
	assert_eq(s.money, money0, "deferring pays no money now — that's the point")
	assert_eq(String(r.payment_source), "defer")


func test_defer_refused_on_un_snoozable():
	var s := _state()
	var ev := _deferrable_window()
	ev["event_class"] = "un-snoozable"
	var r := WindowResolver.resolve(s, s.month_plan, ev, "defer")
	assert_false(r.success, "un-snoozable windows do not sell DEFER")
	assert_eq(s.ledger.entries.size(), 0, "no entry minted on a refused defer")


func test_ignore_applies_list_price():
	var s := _state()
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "ignore")
	assert_true(r.success)
	assert_almost_eq(s.reputation, 47.0, 0.01, "IGNORE applies the list-price consequence (-3 rep)")


func test_auto_ignore_adds_mild_rep_penalty():
	var s := _state()
	var r := WindowResolver.resolve(s, s.month_plan, _deferrable_window(), "auto_ignore")
	assert_true(r.success, "an unanswered window auto-resolves")
	# list price -3, plus the default unanswered penalty -2 (Balance events.*) = -5.
	assert_almost_eq(s.reputation, 45.0, 0.01, "auto-IGNORE = list price + mild nonresponse penalty")


func test_auto_ignore_refused_on_unignorable():
	var s := _state()
	var ev := _deferrable_window()
	ev["unignorable"] = true
	var rep0 := s.reputation
	var r := WindowResolver.resolve(s, s.month_plan, ev, "auto_ignore")
	assert_false(r.success, "an unignorable window cannot lapse into auto-ignore")
	assert_almost_eq(s.reputation, rep0, 0.01, "no penalty applied on a refused auto-ignore")

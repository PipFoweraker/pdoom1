extends GutTest
## L1 (#612 / ADR-0009): the month plan layer -- Attention economy, the crisp reserve,
## strategic-action durations, and window payment sources.

func _plan(total: int = 20) -> MonthPlan:
	var p := MonthPlan.new()
	p.begin_month(total, 0)
	return p


func test_begin_month_grants_attention():
	var p := _plan(20)
	assert_eq(p.attention_total, 20, "month opens with the Attention grant")
	assert_eq(p.available(), 20, "all of it is available before anything is committed")
	assert_eq(p.reserve_remaining(), 0, "no reserve held until the player sets it")


func test_queue_spends_available_attention():
	var p := _plan(20)
	assert_true(p.queue_strategic("fundraise", 5, 3, 10), "queue succeeds within budget")
	assert_eq(p.available(), 15, "queuing spends Attention")
	assert_eq(p.queued_strategic.size(), 1, "the item is recorded")


func test_cannot_overspend_available():
	var p := _plan(4)
	assert_false(p.queue_strategic("big", 5, 2, 1), "cannot queue beyond available Attention")
	assert_eq(p.available(), 4, "a rejected queue spends nothing")


func test_strategic_actions_have_duration_and_never_resolve_instantly():
	var p := _plan(20)
	p.queue_strategic("hire_search", 3, 4, 10)  # queued on turn 10, 4-tick duration
	assert_eq(p.take_due_strategic(10).size(), 0, "nothing resolves on the tick it was queued")
	assert_eq(p.take_due_strategic(13).size(), 0, "nor before the duration elapses")
	var due := p.take_due_strategic(14)
	assert_eq(due.size(), 1, "it lands after its duration")
	assert_eq(String(due[0].action_id), "hire_search")
	assert_eq(p.queued_strategic.size(), 0, "resolved items are removed")


func test_zero_duration_coerced_to_one_tick():
	var p := _plan(20)
	p.queue_strategic("instant_attempt", 1, 0, 5)
	assert_eq(p.take_due_strategic(5).size(), 0, "even duration 0 does not resolve same-tick")
	assert_eq(p.take_due_strategic(6).size(), 1, "it resolves on the next tick")


func test_reserve_is_explicit_and_bounded():
	var p := _plan(20)
	assert_true(p.set_reserve(6), "player holds 6 for windows")
	assert_eq(p.reserve_remaining(), 6, "reserve is held")
	assert_eq(p.available(), 14, "reserve is not available for plan work")
	assert_false(p.set_reserve(25), "cannot reserve more than exists")
	assert_eq(p.reserve_remaining(), 6, "a rejected reserve change leaves it untouched")


func test_reserve_and_plan_compete_for_the_same_pool():
	var p := _plan(10)
	p.set_reserve(4)
	assert_false(p.queue_strategic("x", 8, 2, 1), "can't queue into reserved Attention")
	assert_true(p.queue_strategic("x", 6, 2, 1), "can queue up to the un-reserved remainder")


func test_reserve_evaporates_at_month_end_no_banking():
	# ADR-0009 S4: unspent reserve does NOT carry. begin_month resets the pools.
	var p := _plan(20)
	p.set_reserve(10)
	p.pay_from_reserve(2)  # spent 2 of the 10
	assert_eq(p.reserve_remaining(), 8, "8 reserve unspent this month")
	p.begin_month(20, 1)   # next month opens
	assert_eq(p.reserve_remaining(), 0, "the unspent 8 evaporated -- no banking")
	assert_eq(p.available(), 20, "next month is a fresh full grant")
	assert_eq(p.month_ordinal, 1, "ordinal advanced")


func test_pay_from_reserve_draws_only_reserve():
	var p := _plan(20)
	p.set_reserve(3)
	assert_true(p.pay_from_reserve(3), "reserve covers the window")
	assert_eq(p.reserve_remaining(), 0, "reserve consumed")
	assert_false(p.pay_from_reserve(1), "no reserve left to draw")


func test_cannibalize_eats_free_capacity_then_kills_wip():
	var p := _plan(10)
	p.queue_strategic("wip_a", 4, 3, 1)  # spent 4
	p.set_reserve(0)
	# available now 6. A window costing 3 pays from free capacity, no WIP killed.
	var r1 := p.pay_by_cannibalizing(3)
	assert_true(r1.paid, "free capacity covers a small window")
	assert_eq((r1.cancelled as Array).size(), 0, "no WIP sacrificed when free capacity suffices")
	# available now 3, WIP still queued (cost 4). A window costing 5 must kill the WIP.
	var r2 := p.pay_by_cannibalizing(5)
	assert_true(r2.paid, "cannibalizing WIP frees enough Attention")
	assert_true((r2.cancelled as Array).has("wip_a"), "the planned WIP was sacrificed")
	assert_eq(p.queued_strategic.size(), 0, "the killed WIP is gone")


func test_cannibalize_fails_when_even_killing_all_wip_is_short():
	var p := _plan(3)
	var r := p.pay_by_cannibalizing(9)
	assert_false(r.paid, "a window bigger than the whole month cannot be cannibalized")


func test_serialization_round_trips():
	var p := _plan(20)
	p.set_reserve(5)
	p.pay_from_reserve(2)
	p.queue_strategic("workstream", 4, 6, 12)
	var restored := MonthPlan.new()
	# JSON hop to mimic the real save path (untyped floats/arrays come back).
	var json_str := JSON.stringify(p.to_dict())
	restored.from_dict(JSON.parse_string(json_str))
	assert_eq(restored.attention_total, p.attention_total)
	assert_eq(restored.attention_spent, p.attention_spent)
	assert_eq(restored.attention_reserved, p.attention_reserved)
	assert_eq(restored.reserve_used, p.reserve_used)
	assert_eq(restored.available(), p.available(), "available Attention survives the round trip")
	assert_eq(restored.reserve_remaining(), p.reserve_remaining(), "reserve survives")
	assert_eq(restored.queued_strategic.size(), 1, "in-flight WIP survives")
	assert_eq(int(restored.queued_strategic[0].resolves_on_turn), 18, "duration timing preserved")

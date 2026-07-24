extends GutTest
## L3 per-tick action resolution (PER_TICK_RESOLUTION_DESIGN.md). Queued cards resolve on their
## scheduled day-ticks -- interleaved with playout -- debiting COMMITTED Attention as each lands,
## instead of the pre-L3 batch execute at commit. An unresolved card can be DIVERTED
## (cannibalized) to fund a response window. These lock the new epoch's accounting + ordering.


func _plan() -> MonthPlan:
	var p := MonthPlan.new()
	p.begin_month(20, 0)
	return p


func test_commit_holds_then_resolution_debits():
	# Queue time COMMITS (holds against the budget); resolution DEBITS (committed -> spent).
	var p := _plan()
	assert_true(p.commit_attention(3), "queue-time commit holds 3 Attention")
	assert_eq(p.attention_committed, 3, "held as committed")
	assert_eq(p.attention_spent, 0, "nothing debited at queue time")
	assert_eq(p.available(), 17, "committed reduces what can still be queued")
	p.resolve_committed(3)
	assert_eq(p.attention_committed, 0, "commitment cleared when the card resolves")
	assert_eq(p.attention_spent, 3, "debited exactly at resolution")
	assert_eq(p.available(), 17, "available is stable across the commit->spent move")


func test_cards_resolve_one_per_day_in_order_not_batched():
	# The core spread: three cards scheduled on consecutive ticks resolve one per day, in queue
	# order -- NOT all at commit.
	var p := _plan()
	p.commit_attention(1)
	p.commit_attention(1)
	p.commit_attention(1)
	p.enqueue_committed_card("a", 1, 11, 10)
	p.enqueue_committed_card("b", 1, 12, 10)
	p.enqueue_committed_card("c", 1, 13, 10)
	assert_eq(p.take_due_strategic(10).size(), 0, "nothing resolves on the commit tick")
	var d11 := p.take_due_strategic(11)
	assert_eq(d11.size(), 1, "exactly one card resolves on day 11")
	assert_eq(String(d11[0].action_id), "a", "in queue order -- 'a' first")
	assert_eq(String(p.take_due_strategic(12)[0].action_id), "b", "'b' on day 12")
	assert_eq(String(p.take_due_strategic(13)[0].action_id), "c", "'c' on day 13")
	assert_eq(p.queued_strategic.size(), 0, "the whole plan resolved across the month")


func test_unresolved_card_diverted_to_fund_a_window():
	# The feature this lane unlocks: an opportunity arrives mid-month; the player cannibalizes a
	# queued-but-unresolved card to pay for it. The card's committed Attention frees up and it
	# never resolves.
	var p := _plan()
	p.commit_attention(5)
	p.enqueue_committed_card("workstream", 5, 15, 10)
	# Mirror production: the implicit reserve claims all uncommitted slack (reserve =
	# total - committed = 15), so available() is 0 and the window CANNOT be paid from free
	# capacity -- it must divert the queued workstream.
	p.set_reserve(15)
	assert_eq(p.available(), 0, "reserve claims the uncommitted slack; nothing free")
	var pay := p.pay_by_cannibalizing(4)
	assert_true(pay.paid, "diverting the workstream funds the 4-cost window")
	assert_true((pay.cancelled as Array).has("workstream"), "the unresolved card was sacrificed")
	assert_eq(p.queued_strategic.size(), 0, "a diverted card will never resolve")
	assert_eq(p.attention_committed, 0, "its commitment was released")
	assert_eq(p.attention_spent, 4, "the window consumed 4 of the freed Attention")


func test_controller_releases_scheduled_cards_over_ticks():
	# Integration: the MonthController plays scheduled cards out over day-ticks (proves the seam
	# is wired end to end, not just the accounting). A card scheduled for a later tick surfaces
	# in last_released_strategic on that tick and leaves the WIP queue.
	var s := GameState.new("per-tick-ctrl-seed")
	s.money = 1000000.0
	var tm = TurnManager.new(s)
	var mc := MonthController.new(s, tm)
	var t0: int = s.turn
	s.month_plan.enqueue_committed_card("pass", 0, t0 + 1, t0)  # 'pass' = deterministic no-op
	var released_ids: Array = []
	for _i in range(6):
		if s.game_over:
			break
		mc.advance_tick()
		for c in mc.last_released_strategic:
			released_ids.append(String(c.get("action_id", "")))
		var g := 0
		while mc.is_paused() and g < 12:
			g += 1
			mc.resolve_current_window("ignore")
	assert_true(released_ids.has("pass"), "the scheduled card resolved on a later tick, not at commit")
	assert_eq(s.month_plan.queued_strategic.size(), 0, "it left the WIP queue once resolved")

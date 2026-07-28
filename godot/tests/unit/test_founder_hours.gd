extends GutTest
## T2 (ADR-0011 amendment (a)+(c)): the AP pool is dead and founder Attention is typed
## 2-way into PLANNING vs OPERATING hours. This file pins BOTH halves.
##
## The 2-way split is the T3-rung FLOOR. The 4-way refinement (doors / approvals / audits /
## reserve) subdivides these two later; these tests are written against the two-type API
## (MonthPlan.HOUR_*) so that subdivision extends them rather than rewriting them.
##
## Load-bearing invariants pinned here:
##   1. sum(hours_total) == attention_total and sum(hours_spent) == attention_spent -- the
##      typed pools are ADDITIVE accounting over an AUTHORITATIVE scalar (the N2 typed-rep
##      shape). If this drifts, the HUD and the affordability gate disagree.
##   2. Overflow is ASYMMETRIC: operating may eat planning, planning may never eat
##      operating. This is the whole mechanical point of the split.
##   3. There is no `action_points` anywhere -- no field, no cost key, no per-turn grant.


func _plan(total: int = 20, planning_share: float = 0.5) -> MonthPlan:
	var mp := MonthPlan.new()
	mp.begin_month(total, 0, planning_share)
	return mp


func _sum(d: Dictionary) -> int:
	return int(d.get(MonthPlan.HOUR_PLANNING, 0)) + int(d.get(MonthPlan.HOUR_OPERATING, 0))


# --- Invariant 1: typed pools are additive over the authoritative scalar ------------------

func test_begin_month_splits_grant_without_losing_hours():
	var mp := _plan(20, 0.5)
	assert_eq(mp.hours_total[MonthPlan.HOUR_PLANNING], 10, "half the grant is planning")
	assert_eq(mp.hours_total[MonthPlan.HOUR_OPERATING], 10, "half the grant is operating")
	assert_eq(_sum(mp.hours_total), mp.attention_total, "typed hours must sum to the grant")


func test_odd_grant_remainder_goes_to_operating():
	# floor() on the planning side means an odd hour must land somewhere, not vanish.
	var mp := _plan(21, 0.5)
	assert_eq(mp.hours_total[MonthPlan.HOUR_PLANNING], 10, "planning takes the floor")
	assert_eq(mp.hours_total[MonthPlan.HOUR_OPERATING], 11, "the remainder goes to operating")
	assert_eq(_sum(mp.hours_total), 21, "no hour is lost to integer division")


func test_spend_keeps_typed_and_scalar_in_step():
	var mp := _plan()
	assert_true(mp.spend_attention(3, MonthPlan.HOUR_PLANNING), "planning spend fits")
	assert_true(mp.spend_attention(2, MonthPlan.HOUR_OPERATING), "operating spend fits")
	assert_eq(mp.attention_spent, 5, "scalar tracks the total")
	assert_eq(_sum(mp.hours_spent), mp.attention_spent, "typed spend sums to the scalar")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 3, "planning booked correctly")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 2, "operating booked correctly")


func test_refund_keeps_typed_and_scalar_in_step():
	var mp := _plan()
	mp.spend_attention(4, MonthPlan.HOUR_PLANNING)
	mp.refund_attention(3, MonthPlan.HOUR_PLANNING)
	assert_eq(mp.attention_spent, 1, "scalar refunded")
	assert_eq(_sum(mp.hours_spent), 1, "typed refunded in step")


func test_refund_cannot_mint_attention():
	var mp := _plan()
	mp.spend_attention(1, MonthPlan.HOUR_OPERATING)
	mp.refund_attention(99, MonthPlan.HOUR_OPERATING)
	assert_eq(mp.attention_spent, 0, "clamped at zero")
	assert_eq(_sum(mp.hours_spent), 0, "typed pools clamped too")


# --- Invariant 2: the overflow asymmetry --------------------------------------------------

func test_operating_may_overflow_into_planning():
	# A crisis costs you the time you meant to spend thinking. 10 operating hours exist;
	# spending 13 operating must succeed by eating 3 planning hours.
	var mp := _plan(20, 0.5)
	assert_true(mp.spend_attention(13, MonthPlan.HOUR_OPERATING), "operating overflows")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 10, "operating pool drained first")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 3, "the spill ate planning hours")
	assert_eq(_sum(mp.hours_spent), 13, "invariant holds through an overflow")


func test_planning_may_not_overflow_into_operating():
	# You cannot retroactively have been in the room: running out of planner hours BLOCKS
	# further strategic queuing even while operating hours sit unused.
	var mp := _plan(20, 0.5)
	assert_true(mp.spend_attention(10, MonthPlan.HOUR_PLANNING), "the planning pool is spendable")
	assert_eq(mp.available(), 10, "aggregate Attention remains")
	assert_false(mp.can_spend_hours(1, MonthPlan.HOUR_PLANNING), "but planner mind is exhausted")
	assert_false(mp.spend_attention(1, MonthPlan.HOUR_PLANNING), "and the spend is refused")
	assert_true(mp.can_spend_hours(1, MonthPlan.HOUR_OPERATING), "operating work still possible")


func test_queue_strategic_bills_planning_hours():
	var mp := _plan(20, 0.5)
	assert_true(mp.queue_strategic("some_action", 4, 2, 0), "queues")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 4, "queuing is planner mind")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 0, "and costs no presence")


func test_queue_strategic_refused_when_planner_mind_is_gone():
	var mp := _plan(20, 0.5)
	mp.spend_attention(10, MonthPlan.HOUR_PLANNING)
	assert_false(mp.queue_strategic("late_idea", 1, 2, 0), "no planning hours -> no new strategy")
	assert_eq(mp.queued_strategic.size(), 0, "and nothing was queued")


func test_cannibalizing_a_window_converts_planning_into_operating():
	# The designed pain: the crisis you handled is the strategy month you did not get.
	var mp := _plan(20, 0.5)
	mp.queue_strategic("big_bet", 8, 3, 0)
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 8, "planning committed to the bet")
	# 14 exceeds the 12 un-committed Attention, so the queued bet MUST be sacrificed first.
	var pay: Dictionary = mp.pay_by_cannibalizing(14)
	assert_true(pay.get("paid", false), "the window is paid")
	assert_eq(pay.get("cancelled", []).size(), 1, "the queued bet was sacrificed")
	assert_eq(mp.attention_spent, 14, "scalar reflects the window only (the bet was refunded)")
	assert_eq(_sum(mp.hours_spent), 14, "invariant survives the cancel-then-spend path")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 10, "operating drained first")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 4, "the rest came out of planning")


func test_reserve_is_deliberately_untyped():
	# DESIGN CALL (see MonthPlan.set_reserve): the crisp reserve is NOT capped at the
	# operating pool. The reserve is the emergency channel, and an emergency is exactly
	# where the type wall is allowed to break (operating already overflows into planning).
	# Capping the pre-declared reserve would forbid at plan time what the overflow rule
	# permits at crisis time. This test exists so that call cannot be reverted silently.
	var mp := _plan(20, 0.5)
	assert_true(mp.set_reserve(14), "reserving past the operating pool is legal")
	assert_eq(mp.available(), 6, "the reserve still competes with plan-speed work")
	assert_eq(_sum(mp.hours_spent), mp.attention_spent, "reserving books no typed hours")


func test_grant_hours_buys_presence_not_planner_mind():
	# ADR-0011 point 6: ops/admin staff reduce the founder-price of routine work. They do
	# NOT top up the founder's capacity to think (point 1: the pool illusion is dead).
	var mp := _plan(20, 0.5)
	mp.grant_hours(2, MonthPlan.HOUR_OPERATING)
	assert_eq(mp.hours_total[MonthPlan.HOUR_OPERATING], 12, "operating capacity bought")
	assert_eq(mp.hours_total[MonthPlan.HOUR_PLANNING], 10, "planner mind untouched")
	assert_eq(_sum(mp.hours_total), mp.attention_total, "invariant holds after a grant")


func test_begin_month_evaporates_typed_hours_too():
	# ADR-0009 S4: no banking, ever. A new month must not inherit last month's leftovers.
	var mp := _plan(20, 0.5)
	mp.spend_attention(6, MonthPlan.HOUR_OPERATING)
	mp.begin_month(20, 1, 0.5)
	assert_eq(mp.attention_spent, 0, "scalar reset")
	assert_eq(_sum(mp.hours_spent), 0, "typed pools reset")
	assert_eq(mp.hours_total[MonthPlan.HOUR_OPERATING], 10, "fresh operating grant")


# --- Serialization ------------------------------------------------------------------------

func test_typed_hours_survive_a_roundtrip():
	var mp := _plan(20, 0.5)
	mp.spend_attention(3, MonthPlan.HOUR_PLANNING)
	mp.spend_attention(2, MonthPlan.HOUR_OPERATING)
	var clone := MonthPlan.new()
	clone.from_dict(mp.to_dict())
	assert_eq(clone.hours_total, mp.hours_total, "grants survive")
	assert_eq(clone.hours_spent, mp.hours_spent, "typed spend survives")
	assert_eq(clone.available(), mp.available(), "aggregate survives")


func test_pre_t2_save_without_typed_hours_loads_into_a_legal_state():
	# A save written before this migration has neither hours key. It must reconstruct a
	# split and book the already-spent Attention as OPERATING -- not zero the pools, which
	# would silently block every further spend.
	var legacy := {
		"attention_total": 20,
		"attention_spent": 5,
		"attention_reserved": 0,
		"reserve_used": 0,
		"month_ordinal": 2,
		"queued_strategic": [],
	}
	var mp := MonthPlan.new()
	mp.from_dict(legacy)
	assert_eq(_sum(mp.hours_total), 20, "a split was reconstructed from the grant")
	assert_eq(_sum(mp.hours_spent), 5, "the legacy spend was booked, not lost")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 5, "booked as un-typed = operating")
	assert_eq(mp.available(), 15, "and the plan is spendable")


# --- Invariant 3: AP is gone ---------------------------------------------------------------

func test_game_state_has_no_action_point_field():
	var state := GameState.new("t2_seed")
	assert_false("action_points" in state, "the AP pool field is deleted")
	assert_false("max_action_points" in state, "the AP cap field is deleted")
	assert_false("committed_ap" in state, "the AP reserve trio is deleted")


func test_state_dict_reports_attention_not_ap():
	var state := GameState.new("t2_seed")
	var d: Dictionary = state.to_dict()
	assert_false(d.has("action_points"), "no AP in the serialized state")
	assert_true(d.has("attention"), "Attention is the founder currency in the state dict")
	assert_true(d.has("planning_hours_left"), "typed hours are surfaced for the HUD")
	assert_true(d.has("operating_hours_left"), "typed hours are surfaced for the HUD")


func test_no_action_definition_still_prices_in_ap():
	# The data migration must be complete: if ANY action def still carries action_points,
	# it is silently un-gated content. attention_cost() would still read it via the legacy
	# alias, which is exactly why this has to be pinned rather than trusted.
	var offenders: Array[String] = []
	for action in GameActions.get_all_actions():
		if action.get("costs", {}).has("action_points"):
			offenders.append(String(action.get("id", "?")))
	assert_eq(offenders, [] as Array[String], "no action def may price in action_points")

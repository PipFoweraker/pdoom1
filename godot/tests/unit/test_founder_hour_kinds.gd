extends GutTest
## Ballot 4 (2026-07-27, REVIEW-BY 2026-08-31): founder hours subdivide 4 ways into
## doors / approvals / audits / reserve. This file pins the KIND layer; test_founder_hours.gd
## still pins the 2-way FAMILY layer underneath it, unchanged and unrewritten -- which is
## itself the evidence that the subdivision extends rather than replaces.
##
## Load-bearing invariants pinned here:
##   1. kinds ACCOUNT, families GATE. There are no per-kind budgets; admissibility is
##      decided entirely by family_of() + the asymmetric overflow rule.
##   2. kind_spent[doors] + [approvals] + [audits] == attention_spent, and
##      kind_spent[reserve] == reserve_used. The reserve is LABELLED by the kind layer but
##      still ACCOUNTED separately -- T2's judgment call 2 (crisp reserve untyped/un-gated)
##      was upheld by this lane, not overruled.
##   3. doors and audits are OPERATING; approvals is PLANNING. That mapping is what makes
##      #980 fall out with no change to conference_trip: draining the operating family kills
##      exactly the presence kinds and leaves next month's direction decidable.


func _plan(total: int = 20, planning_share: float = 0.5) -> MonthPlan:
	var mp := MonthPlan.new()
	mp.begin_month(total, 0, planning_share)
	return mp


func _work_sum(mp: MonthPlan) -> int:
	return mp.kind_spend(MonthPlan.KIND_DOORS) + mp.kind_spend(MonthPlan.KIND_APPROVALS) \
		+ mp.kind_spend(MonthPlan.KIND_AUDITS)


# --- Invariant 3: the kind -> family mapping ---------------------------------------------

func test_presence_kinds_are_operating_and_approvals_is_planning():
	assert_eq(MonthPlan.family_of(MonthPlan.KIND_DOORS), MonthPlan.HOUR_OPERATING, "doors are presence")
	assert_eq(MonthPlan.family_of(MonthPlan.KIND_AUDITS), MonthPlan.HOUR_OPERATING, "you cannot audit from a hotel")
	assert_eq(MonthPlan.family_of(MonthPlan.KIND_RESERVE), MonthPlan.HOUR_OPERATING, "firefighting is presence")
	assert_eq(MonthPlan.family_of(MonthPlan.KIND_APPROVALS), MonthPlan.HOUR_PLANNING, "rulings are planner mind")


func test_family_tokens_still_resolve_so_2way_callers_keep_working():
	assert_eq(MonthPlan.family_of(MonthPlan.HOUR_PLANNING), MonthPlan.HOUR_PLANNING, "family passes through")
	assert_eq(MonthPlan.family_of(MonthPlan.HOUR_OPERATING), MonthPlan.HOUR_OPERATING, "family passes through")
	assert_eq(MonthPlan.family_of("nonsense"), MonthPlan.HOUR_OPERATING, "unknown falls to presence, never to planner mind")


func test_family_tokens_book_their_default_kind():
	assert_eq(MonthPlan.kind_of(MonthPlan.HOUR_PLANNING), MonthPlan.KIND_APPROVALS, "un-subdivided planning is a ruling")
	assert_eq(MonthPlan.kind_of(MonthPlan.HOUR_OPERATING), MonthPlan.KIND_DOORS, "un-subdivided presence is face-time")
	assert_eq(MonthPlan.kind_of(MonthPlan.KIND_AUDITS), MonthPlan.KIND_AUDITS, "a kind is itself")


# --- Invariant 1: kinds account, families gate -------------------------------------------

func test_a_kind_spend_debits_its_family_pool():
	var mp := _plan(20, 0.5)
	assert_true(mp.spend_attention(3, MonthPlan.KIND_AUDITS), "audits fit in the operating pool")
	assert_eq(mp.kind_spend(MonthPlan.KIND_AUDITS), 3, "booked as audits")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 3, "and charged to the operating family")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 0, "planner mind untouched")


func test_there_are_no_per_kind_budgets_only_family_gates():
	var mp := _plan(20, 0.5)  # 10 planning / 10 operating
	# Ten straight audit hours would blow any plausible per-kind cap; the family is the only
	# gate, so all ten are admissible.
	assert_true(mp.spend_attention(10, MonthPlan.KIND_AUDITS), "the whole operating pool may be audits")
	assert_eq(mp.kind_spend(MonthPlan.KIND_AUDITS), 10, "all ten booked to one kind")
	assert_eq(mp.hours_available(MonthPlan.KIND_DOORS), 0, "doors read the same drained family pool")


func test_kind_survives_a_family_overflow():
	var mp := _plan(20, 0.5)
	# 13 audit hours against a 10-hour operating pool: 3 spill into planning capacity.
	assert_true(mp.spend_attention(13, MonthPlan.KIND_AUDITS), "operating kinds may overflow")
	assert_eq(mp.kind_spend(MonthPlan.KIND_AUDITS), 13, "the kind books whole -- it was all auditing")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 10, "operating drained first")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_PLANNING], 3, "the spill records where the time came from")
	assert_eq(_work_sum(mp), mp.attention_spent, "kind invariant survives an overflow")


func test_approvals_may_not_borrow_presence():
	var mp := _plan(20, 0.5)
	assert_true(mp.spend_attention(10, MonthPlan.KIND_APPROVALS), "the planning pool is spendable as approvals")
	assert_false(mp.can_spend_hours(1, MonthPlan.KIND_APPROVALS), "planner mind is exhausted")
	assert_true(mp.can_spend_hours(1, MonthPlan.KIND_DOORS), "presence work still possible")


func test_queuing_strategic_books_approvals():
	var mp := _plan(20, 0.5)
	assert_true(mp.queue_strategic("bet", 4, 2, 0), "queued")
	assert_eq(mp.kind_spend(MonthPlan.KIND_APPROVALS), 4, "queuing is a direction ruling")
	assert_eq(_work_sum(mp), mp.attention_spent, "kind invariant holds")


func test_refund_unbooks_the_kind():
	var mp := _plan(20, 0.5)
	mp.spend_attention(4, MonthPlan.KIND_DOORS)
	mp.refund_attention(3, MonthPlan.KIND_DOORS)
	assert_eq(mp.kind_spend(MonthPlan.KIND_DOORS), 1, "kind refunded in step")
	assert_eq(_work_sum(mp), mp.attention_spent, "kind invariant holds through a refund")


# --- Invariant 2: the reserve is labelled but still accounted separately -----------------

func test_reserve_kind_mirrors_reserve_used_without_booking_hours():
	var mp := _plan(20, 0.5)
	assert_true(mp.set_reserve(6), "reserve is NOT gated at the operating pool (T2 call 2 upheld)")
	assert_eq(mp.kind_spend(MonthPlan.KIND_RESERVE), 0, "declaring a reserve spends nothing yet")
	assert_true(mp.pay_from_reserve(4), "a window draws on it")
	assert_eq(mp.kind_spend(MonthPlan.KIND_RESERVE), 4, "the reserve kind mirrors reserve_used")
	assert_eq(mp.reserve_used, 4, "and reserve_used is still the authority")
	assert_eq(mp.hours_spent[MonthPlan.HOUR_OPERATING], 0, "the reserve books no typed family hours")
	assert_eq(_work_sum(mp), mp.attention_spent, "work kinds still sum to the scalar")


func test_reserve_bigger_than_the_operating_pool_is_still_legal():
	var mp := _plan(20, 0.5)  # only 10 operating hours exist
	assert_true(mp.set_reserve(15), "an emergency is where the type wall is allowed to break")


# --- Save round-trip + legacy save -------------------------------------------------------

func test_kind_spend_round_trips():
	var mp := _plan(20, 0.5)
	mp.spend_attention(2, MonthPlan.KIND_AUDITS)
	mp.spend_attention(3, MonthPlan.KIND_APPROVALS)
	mp.set_reserve(4)
	mp.pay_from_reserve(1)
	var clone := MonthPlan.new()
	clone.from_dict(mp.to_dict())
	assert_eq(clone.kind_spent, mp.kind_spent, "kind labels survive a save")
	assert_eq(clone.hours_spent, mp.hours_spent, "family pools survive a save")


func test_pre_ballot4_save_rebuilds_kinds_from_the_family_pools():
	# A save written by T2: hours_* present, kind_spent absent. It must load into a legal
	# state (the invariant satisfied) rather than reading zero and forking the books.
	var mp := MonthPlan.new()
	mp.from_dict({
		"attention_total": 20,
		"attention_spent": 7,
		"attention_reserved": 0,
		"reserve_used": 0,
		"month_ordinal": 0,
		"hours_total": {MonthPlan.HOUR_PLANNING: 10, MonthPlan.HOUR_OPERATING: 10},
		"hours_spent": {MonthPlan.HOUR_PLANNING: 4, MonthPlan.HOUR_OPERATING: 3},
	})
	assert_eq(mp.kind_spend(MonthPlan.KIND_APPROVALS), 4, "planning hours label as approvals")
	assert_eq(mp.kind_spend(MonthPlan.KIND_DOORS), 3, "operating hours label as doors")
	assert_eq(_work_sum(mp), 7, "the legacy spend was labelled, not lost")


func test_begin_month_resets_the_kind_labels():
	var mp := _plan(20, 0.5)
	mp.spend_attention(5, MonthPlan.KIND_AUDITS)
	mp.begin_month(20, 1, 0.5)
	assert_eq(_work_sum(mp), 0, "kinds reset with everything else -- no banking")
	assert_eq(mp.kind_spend(MonthPlan.KIND_RESERVE), 0, "the reserve label resets too")


# --- Data typing: the presence pass ------------------------------------------------------

func test_action_data_declares_its_kind_at_the_TOP_LEVEL_not_inside_costs():
	# The 4-way lane moved action-def typing out of `costs`: an hour type is a property of the
	# action, not a resource price. Living inside `costs` broke every site that iterates cost
	# pairs numerically (the fresh-game render + the non-negative-costs sweep both blew up).
	var doors := {"costs": {"attention": 1}, "hour_type": MonthPlan.KIND_DOORS}
	assert_eq(GameActions.hour_type(doors), MonthPlan.KIND_DOORS, "a declared kind is returned verbatim")
	var audits := {"costs": {"attention": 1}, "hour_type": MonthPlan.KIND_AUDITS}
	assert_eq(GameActions.hour_type(audits), MonthPlan.KIND_AUDITS, "audits type survives the read")


func test_no_action_data_hides_a_type_tag_inside_its_cost_dict():
	# Regression pin: a String in `costs` is a landmine for every numeric cost consumer.
	var pools: Array = _all_priced_pools()
	for a in pools:
		assert_false(a.get("costs", {}).has("hour_type"),
			"action %s must declare hour_type at the top level, not in costs" % [a.get("id", "?")])


func test_bare_cost_dicts_may_still_carry_the_tag():
	# The code-side channel: a subsystem charge with no action def has nowhere else to put it.
	var s := GameState.new("bare-cost")
	s.month_plan = MonthPlan.new()
	s.month_plan.begin_month(20, 0, 0.5)
	assert_eq(s._cost_hour_type({"attention": 1, "hour_type": MonthPlan.KIND_AUDITS}),
		MonthPlan.KIND_AUDITS, "a bare cost dict may name a kind")
	assert_eq(s._cost_hour_type({"attention": 1}), MonthPlan.HOUR_OPERATING,
		"and an un-typed one is presence -- T2 judgment call 4, upheld")


func test_undeclared_action_still_defaults_to_planning():
	# T2 judgment call 4, KEPT by this lane: a queued action defaults to PLANNING while a
	# bare cost dict defaults to OPERATING. Pinned so the asymmetry cannot drift unnoticed.
	assert_eq(GameActions.hour_type({"costs": {"attention": 1}}), MonthPlan.HOUR_PLANNING,
		"queuing is deciding")


func test_the_audit_action_is_typed_audits_in_data():
	var act: Dictionary = {}
	for a in GameActions.get_operations_options():
		if String(a.get("id", "")) == "audit_self_directed":
			act = a
	assert_false(act.is_empty(), "the audit action exists in data")
	assert_eq(GameActions.hour_type(act), MonthPlan.KIND_AUDITS, "and it bills the audits kind")


func test_every_priced_action_declares_its_hour_type():
	# The presence pass (PR #996 judgment call 5's inheritance): every action that costs
	# Attention was read once and asked "thinking, or showing up?". A new priced action with
	# no declared type silently inherits PLANNING, which is the trap this pins shut.
	var undeclared: Array = []
	for a in _all_priced_pools():
		if int(a.get("costs", {}).get("attention", 0)) > 0 and not a.has("hour_type"):
			undeclared.append(String(a.get("id", "?")))
	assert_eq(undeclared, [], "priced actions missing an hour_type: %s" % [undeclared])


func _all_priced_pools() -> Array:
	var pools: Array = []
	pools.append_array(GameActions.get_all_actions())
	pools.append_array(GameActions.get_hiring_options())
	pools.append_array(GameActions.get_fundraising_options())
	pools.append_array(GameActions.get_publicity_options())
	pools.append_array(GameActions.get_strategic_options())
	pools.append_array(GameActions.get_travel_options())
	pools.append_array(GameActions.get_operations_options())
	return pools


# --- The audit verb: the consumer for T1's reported-vs-actual seam ------------------------

func _state_with_a_liar() -> GameState:
	var s := GameState.new("audit-seed")
	s.turn = 1
	s.month_plan = MonthPlan.new()
	s.month_plan.begin_month(20, 0, 0.5)
	s.record_self_directed("interpretability", 4.0, 7.0)  # claimed 7, did 4
	s.record_self_directed("alignment", 3.0, 3.5)         # a smaller fib
	return s


func test_an_audit_hour_ground_truths_the_biggest_gap():
	var s := _state_with_a_liar()
	var result: Dictionary = s.audit_self_directed()
	assert_true(bool(result.get("ok", false)), "the audit ran")
	assert_eq(String(result.get("topic", "")), "interpretability", "it went where the gap was biggest")
	assert_almost_eq(float(result.get("gap", 0.0)), 3.0, 0.01, "and reported the overstatement")
	var bucket: Dictionary = s.self_directed_progress["interpretability"]
	assert_almost_eq(float(bucket["reported"]), 4.0, 0.01, "the books now say what actually happened")
	assert_almost_eq(float(bucket["actual"]), 4.0, 0.01, "truth is never edited by an audit")
	assert_almost_eq(float(s.self_directed_progress["alignment"]["reported"]), 3.5, 0.01,
		"an audit ground-truths ONE topic, not the whole org")


func test_an_audit_bills_an_audits_hour():
	var s := _state_with_a_liar()
	s.audit_self_directed()
	assert_eq(s.month_plan.kind_spend(MonthPlan.KIND_AUDITS), 1, "one audit hour spent")
	assert_eq(s.month_plan.hours_spent[MonthPlan.HOUR_OPERATING], 1, "charged to presence")


func test_an_audit_is_impossible_with_no_presence_left():
	# The #980 shape: travel drains the operating family, so it kills auditing outright.
	var s := _state_with_a_liar()
	s.month_plan.spend_attention(20, MonthPlan.KIND_DOORS)  # every hour gone
	var result: Dictionary = s.audit_self_directed()
	assert_false(bool(result.get("ok", false)), "no hours, no ground-truthing")
	assert_almost_eq(float(s.self_directed_progress["interpretability"]["reported"]), 7.0, 0.01,
		"and the inflated claim stands uncorrected")


func test_auditing_nothing_is_refused_and_free():
	var s := GameState.new("audit-empty")
	s.month_plan = MonthPlan.new()
	s.month_plan.begin_month(20, 0, 0.5)
	var result: Dictionary = s.audit_self_directed()
	assert_false(bool(result.get("ok", false)), "nobody is self-directing")
	assert_eq(s.month_plan.kind_spend(MonthPlan.KIND_AUDITS), 0, "and no hour was burned finding that out")

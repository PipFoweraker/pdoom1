extends GutTest
## EE-9 · Unit tests for the reactive-policy framework (ReactivePolicy / SweepPolicies) and a fast
## smoke of the shared month runner. Runs in the CI quick gate (tests/unit). The heavy sweeps live
## in tests/manual and are excluded from CI.

const RP = preload("res://tests/manual/reactive_policy.gd")
const SweepPoliciesC = preload("res://tests/manual/sweep_policies.gd")
const Driver = preload("res://tests/manual/l1_month_driver.gd")
const Adapter = preload("res://tests/manual/reactive_adapter.gd")


func _state() -> GameState:
	return GameState.new("reactive-policy-seed")


# --- features() reads game state into the decision snapshot ---

func test_features_snapshot_reads_state() -> void:
	var s := _state()
	s.money = 120000.0
	s.doom = 42.0
	var f := RP.features(s)
	assert_eq(f.cash, 120000.0, "cash mirrors money")
	assert_eq(f.doom, 42.0, "doom mirrors doom")
	assert_eq(f.runway_months, RP.RUNWAY_UNKNOWN, "no staff -> effectively infinite runway")
	# With staff, runway = cash / (staff * annual/12).
	s.safety_researchers = 2
	var f2 := RP.features(s)
	assert_lt(f2.runway_months, RP.RUNWAY_UNKNOWN, "staff creates a finite runway estimate")
	assert_gt(f2.runway_months, 0.0, "positive runway with positive cash")


# --- rules evaluate in order; conditions gate; actions concatenate ---

func test_plan_priority_evaluates_rules_in_order() -> void:
	var pol := RP.make("t", {}, [
		RP.rule(func(f): return f.doom > 50.0, ["a"], "high doom"),
		RP.rule(func(_f): return true, ["b", "c"], "always"),
		RP.rule(func(f): return f.cash < 0.0, ["never"], "impossible"),
	])
	var hi := RP.plan_priority(pol, {"doom": 60.0, "cash": 100.0})
	assert_eq(hi, ["a", "b", "c"], "matching rules concatenate in order")
	var lo := RP.plan_priority(pol, {"doom": 10.0, "cash": 100.0})
	assert_eq(lo, ["b", "c"], "unmatched leading rule is skipped")


func test_parameters_change_behaviour() -> void:
	# Same rule shape, different threshold parameter -> different decision.
	var strict := _threshold_policy(2.0)
	var loose := _threshold_policy(10.0)
	var f := {"runway_months": 5.0}
	assert_eq(RP.plan_priority(strict, f), [], "runway 5 > strict threshold 2 -> no loan")
	assert_eq(RP.plan_priority(loose, f), ["take_loan"], "runway 5 < loose threshold 10 -> loan")


func _threshold_policy(thresh: float) -> Dictionary:
	return RP.make("thr", {"loan_runway_months": thresh}, [
		RP.rule(func(f): return f.runway_months < thresh, ["take_loan"], "loan when short"),
	])


# --- window rules: first match wins; default fallback ---

func test_window_verb_first_match_and_default() -> void:
	var pol := RP.make("w", {}, [], [
		RP.wrule(func(f, _w): return f.doom < 40.0, "ignore", "quiet -> lapse"),
		RP.wrule(func(_f, _w): return true, "handle_reserve", "else engage"),
	])
	assert_eq(RP.window_verb(pol, {"doom": 20.0}, {}), "ignore", "first matching rule wins")
	assert_eq(RP.window_verb(pol, {"doom": 80.0}, {}), "handle_reserve", "later rule when first fails")
	var empty := RP.make("e", {}, [], [])
	assert_eq(RP.window_verb(empty, {}, {}, "defer"), "defer", "no rules -> caller default")


func test_repeat_helper() -> void:
	assert_eq(RP.repeat("x", 3), ["x", "x", "x"], "repeat emits n copies")
	assert_eq(RP.repeat("x", 0), [], "repeat 0 is empty")


# --- Carried-baseline parity: the reactive re-expression must reproduce the exploit sweep's
#     _choose_actions priority (the "keep existing policies working" regression link, #638). ---

func test_baseline_reexpression_matches_exploit_sweep_priority() -> void:
	var s := _state()  # fresh lab: 0 staff, so safety<3 and capability<4 both hold
	var f := RP.features(s)

	# passive -> empty priority (do-nothing baseline)
	assert_eq(RP.plan_priority(SweepPoliciesC.passive(), f), [], "passive queues nothing")

	# safety_lean: hire below 3, then publish every 3rd else safety_research (x12)
	assert_eq(RP.plan_priority(SweepPoliciesC.safety_lean(), f), _old_safety_lean(int(s.safety_researchers)),
		"safety_lean reactive priority == exploit-sweep _choose_actions")

	# capability_rush: hire below 4, buy_compute, then capability_research (x12)
	assert_eq(RP.plan_priority(SweepPoliciesC.capability_rush(), f), _old_capability_rush(int(s.capability_researchers)),
		"capability_rush reactive priority == exploit-sweep _choose_actions")

	# desperation_spam: 6 levers + 6 loans
	assert_eq(RP.plan_priority(SweepPoliciesC.desperation_spam(), f), _old_desperation_spam(),
		"desperation_spam reactive priority == exploit-sweep _choose_actions")

	# loan_hoard: 12 loans
	assert_eq(RP.plan_priority(SweepPoliciesC.loan_hoard(), f), _old_loan_hoard(),
		"loan_hoard reactive priority == exploit-sweep _choose_actions")


# Verbatim re-implementations of test_exploit_sweep._choose_actions branches (the reference).
func _old_safety_lean(safety_researchers: int) -> Array:
	var priority := []
	if safety_researchers < 3:
		priority.append("hire_safety_researcher")
	for i in range(12):
		priority.append("publish_paper" if i % 3 == 0 else "safety_research")
	return priority

func _old_capability_rush(capability_researchers: int) -> Array:
	var priority := []
	if capability_researchers < 4:
		priority.append("hire_capability_researcher")
	priority.append("buy_compute")
	for i in range(12):
		priority.append("capability_research")
	return priority

func _old_desperation_spam() -> Array:
	var priority := []
	for i in range(6):
		priority.append("desperation_lever")
	for i in range(6):
		priority.append("take_loan")
	return priority

func _old_loan_hoard() -> Array:
	var priority := []
	for i in range(12):
		priority.append("take_loan")
	return priority


# --- Standard lines are well-formed and parameterized ---

func test_standard_lines_present_and_parameterized() -> void:
	var names := []
	for p in SweepPoliciesC.all():
		names.append(p.name)
	for want in ["fundraise_first", "balanced_operator", "scout_heavy", "loan_desperation_reactive"]:
		assert_true(want in names, "%s is registered" % want)
	# fundraise_first exposes its documented dials.
	var ff := SweepPoliciesC.fundraise_first()
	assert_true(ff.params.has("loan_runway_months"), "fundraise_first exposes loan_runway_months")
	assert_true(ff.params.has("comfortable_runway_months"), "fundraise_first exposes comfortable_runway_months")


func test_fundraise_first_borrows_only_when_runway_low() -> void:
	# The emergency-borrow path is the L5 raise-as-campaign flow (#641): seek_financing ->
	# accept_financing_offer, replacing the raw take_loan fallback.
	var ff := SweepPoliciesC.fundraise_first()
	var flush := {"runway_months": 12.0, "reputation": 50.0, "ledger_outstanding": 0.0}
	assert_false("seek_financing" in RP.plan_priority(ff, flush), "flush cash -> no borrowing")
	var broke := {"runway_months": 1.0, "reputation": 50.0, "ledger_outstanding": 0.0}
	var broke_pri := RP.plan_priority(ff, broke)
	assert_true("seek_financing" in broke_pri, "cash below loan runway -> seek the offer menu")
	assert_true("accept_financing_offer" in broke_pri, "and accept the best live offer")
	var low_not_broke := {"runway_months": 3.0, "reputation": 50.0, "ledger_outstanding": 0.0}
	var pri := RP.plan_priority(ff, low_not_broke)
	assert_true("fundraise_small" in pri, "low-but-not-broke -> fundraise, not borrow")
	assert_false("seek_financing" in pri, "low-but-not-broke -> no borrowing")
	# Debt service: flush + open bills -> pay_bills (#566).
	var flush_with_debt := {"runway_months": 12.0, "reputation": 50.0, "ledger_outstanding": 60000.0}
	assert_true("pay_bills" in RP.plan_priority(ff, flush_with_debt), "flush + open ledger -> retire the soonest bill")


# --- Fast smoke of the SHARED month driver via the reactive adapter (CI coverage) ---
# The driver is l1_month_driver.gd — the calibration harness's extracted run loop
# (harness unification, PR #642): one driver serves the calibrator AND the EE-9/EE-10
# instruments. This smoke proves the reactive adapter drives it end to end.

func test_shared_driver_smoke_completes() -> void:
	var res: Dictionary = Driver.run("smoke-seed", Adapter.new(SweepPoliciesC.fundraise_first()), {"max_months": 3})
	assert_true(res.has("months"), "driver returns the calibrator result shape")
	assert_true(int(res.death_turn) >= 1, "driver advanced at least one tick")
	assert_true(int(res.months) >= 1 or bool(res.game_over), "planned a month or died trying")
	assert_true(String(res.root_cause) in ["ledger", "doom", "rep", "win", "other", "none"], "attribution classified")


func test_adapter_opening_override_and_features() -> void:
	# EE-10 seam: the first N plan-months come from the override; features are recorded.
	var seen_months := []
	var override := func(_state, m: int):
		seen_months.append(m)
		return ["publish_paper"]
	var adapter = Adapter.new(SweepPoliciesC.fundraise_first(),
		{"plan_override": override, "override_months": 2, "record_features": true})
	var res: Dictionary = Driver.run("smoke-seed", adapter, {"max_months": 3})
	assert_true(res.has("months"), "run completed")
	assert_true(seen_months.size() >= 1 and int(seen_months[0]) == 0, "override drove month 0")
	assert_true(adapter.month_features.size() >= 1, "per-month features recorded")
	assert_true(adapter.month_features[0].has("cash"), "feature snapshot carries cash")

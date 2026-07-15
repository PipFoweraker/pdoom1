class_name SweepPolicies
extends RefCounted
## EE-9 · Named reactive policies for the L1 month sweep (built on ReactivePolicy).
##
## Two groups:
##   STANDARD LINES (new, EE-9) — theorized human play, expressed as reactive (condition -> action)
##   rules with named parameters:
##     fundraise_first   — Pip's expected-player pattern: fundraise by default, loan ONLY when cash
##                         runs below N months of runway. The new "standard finance" bot (replaces
##                         naive loan_desperation as the reference finance line).
##     balanced_operator — safety work + a held reserve + a fundraise cadence.
##     scout_heavy       — grow the board (hire + network + publish). PROXY: the DQ-18 scouting
##                         mechanic is unbuilt, so this stands in via the "hires become your scouts"
##                         reading — hiring + visibility. Revisit when scouting actions exist.
##     loan_desperation_reactive — naive foil KEPT for comparison: always reach for loans (never
##                         fundraise), pull the desperation lever when doom alarms. The pattern
##                         fundraise_first replaces. Named `_reactive` to avoid colliding with the
##                         CALIBRATOR's `loan_desperation` (test_l1_month_sweep.gd) — a different,
##                         fixed-order policy whose numbers anchor the calibration memo.
##
##   CARRIED BASELINES (continuity with tests/manual/test_exploit_sweep.gd's five dispositions) —
##   re-expressed as reactive policies so their PLAN PRIORITY matches the hardcoded _choose_actions
##   (unit-tested in test_reactive_policy.gd). Lets the month sweep report alongside the turn-grain
##   exploit sweep for comparability. NOTE: outcomes differ across the two harnesses by design — the
##   exploit sweep resolves EVERY event; the month sweep applies only windows within the demand
##   budget (the #630 fix). The shared thing is the policy, not the number.

const RP = preload("res://tests/manual/reactive_policy.gd")


# --- Carried-baseline priority patterns (kept byte-identical to test_exploit_sweep._choose_actions) ---

static func _safety_lean_tail() -> Array:
	# for i in 12: publish_paper if i%3==0 else safety_research  (exploit sweep parity)
	var out: Array = []
	for i in range(12):
		out.append("publish_paper" if i % 3 == 0 else "safety_research")
	return out


# --- The registry ---

static func all() -> Array:
	"""The ordered policy set the month sweep runs. Standard lines first, then carried baselines."""
	return [
		fundraise_first(),
		balanced_operator(),
		scout_heavy(),
		loan_desperation_reactive(),
		# Carried baselines (comparability with the exploit sweep):
		passive(),
		safety_lean(),
		capability_rush(),
		desperation_spam(),
		loan_hoard(),
	]


# ============================================================================
# STANDARD LINES (EE-9)
# ============================================================================

static func fundraise_first() -> Dictionary:
	"""Fundraise by default; borrow ONLY when runway falls below loan_runway_months (Pip's spec).
	The emergency-borrow path uses the L5 raise-as-campaign flow (PR #641): seek_financing quotes
	a priced offer menu, accept_financing_offer takes the best live one — the real player flow,
	replacing the raw take_loan fallback. Services debt (pay_bills) when cash is comfortable.
	Fills leftover capacity with safety work. The reference finance line."""
	var p := {
		"loan_runway_months": 2.0,        # below this many months of runway -> emergency raise
		"comfortable_runway_months": 4.0, # below this -> raise money (fundraise, not borrow)
		"big_round_rep": 60.0,            # reputation at/above which a big round is worth the rep cost
		"pay_bills_above_runway": 5.0,    # runway above this + open ledger -> retire soonest bill early
		"safety_fill": 8,                 # leftover-AP safety_research copies
	}
	return RP.make("fundraise_first", p, [
		RP.rule(func(f): return f.runway_months < p.loan_runway_months,
			["seek_financing", "accept_financing_offer"],
			"cash < loan_runway_months of runway -> emergency raise via the L5 offer menu (#641)"),
		RP.rule(func(f): return f.runway_months < p.comfortable_runway_months and f.reputation >= p.big_round_rep,
			["fundraise_big"], "cash low AND rep strong -> major round"),
		RP.rule(func(f): return f.runway_months < p.comfortable_runway_months,
			["fundraise_small"], "cash low -> modest round (default finance = fundraise)"),
		RP.rule(func(f): return f.runway_months > p.pay_bills_above_runway and f.ledger_outstanding > 0.0,
			["pay_bills"], "flush + open bills -> retire the soonest balloon early (#566)"),
		RP.rule(func(_f): return true,
			RP.repeat("safety_research", p.safety_fill) + RP.repeat("publish_paper", 2),
			"spend the rest on safety work"),
	])


static func balanced_operator() -> Dictionary:
	"""Safety work + a held reserve + a fundraise cadence; hires safety staff toward a target and
	audits when doom alarms."""
	var p := {
		"loan_runway_months": 2.0,
		"comfortable_runway_months": 5.0,
		"target_safety_staff": 3,
		"doom_alarm": 60.0,
		"reserve": 8,  # Attention explicitly held for windows (documents intent; harness honours full reserve v1)
	}
	return RP.make("balanced_operator", p, [
		RP.rule(func(f): return f.runway_months < p.loan_runway_months, ["take_loan"], "emergency loan"),
		RP.rule(func(f): return f.runway_months < p.comfortable_runway_months, ["fundraise_small"], "fundraise cadence"),
		RP.rule(func(f): return f.safety_researchers < p.target_safety_staff, ["hire_safety_researcher"], "grow safety bench to target"),
		RP.rule(func(f): return f.doom > p.doom_alarm, ["audit_safety"], "doom alarm -> safety audit"),
		RP.rule(func(_f): return true, ["safety_research", "publish_paper", "safety_research"], "steady safety work"),
	], [
		# Window rule demo: hold engagement, but let low-stakes windows lapse when doom is quiet.
		RP.wrule(func(f, _w): return f.doom < 40.0, "ignore", "quiet times -> conserve, let it lapse"),
		RP.wrule(func(_f, _w): return true, "handle_reserve", "otherwise engage from reserve"),
	])


static func scout_heavy() -> Dictionary:
	"""Grow the board: hire + network + publish. PROXY for DQ-18 scouting (unbuilt) — hiring stands
	in for 'hires become your scouts', networking/publishing for visibility. Light direct research."""
	var p := {
		"loan_runway_months": 2.0,
		"comfortable_runway_months": 5.0,
		"note": "proxy_pending_scouting_actions",
	}
	return RP.make("scout_heavy", p, [
		RP.rule(func(f): return f.runway_months < p.loan_runway_months, ["take_loan"], "emergency loan"),
		RP.rule(func(f): return f.runway_months < p.comfortable_runway_months, ["fundraise_small"], "fundraise when short"),
		RP.rule(func(_f): return true,
			["hire_safety_researcher", "network", "publish_paper", "hire_capability_researcher", "network"],
			"populate the board: hire + network + publish"),
	])


static func loan_desperation_reactive() -> Dictionary:
	"""Naive finance foil KEPT for comparison (fundraise_first replaces it as the standard line):
	always reach for loans instead of fundraising; pull the desperation lever when doom alarms."""
	var p := {
		"comfortable_runway_months": 5.0,
		"doom_alarm": 60.0,
	}
	return RP.make("loan_desperation_reactive", p, [
		RP.rule(func(f): return f.runway_months < p.comfortable_runway_months, RP.repeat("take_loan", 2), "short -> loans (never fundraise)"),
		RP.rule(func(f): return f.doom > p.doom_alarm, ["desperation_lever"], "doom alarm -> desperation lever"),
		RP.rule(func(_f): return true, RP.repeat("safety_research", 6), "leftover -> safety"),
	])


# ============================================================================
# CARRIED BASELINES — reactive re-expression of the exploit sweep's five dispositions.
# plan_priority(policy, features) must equal the old _choose_actions priority (see unit test).
# ============================================================================

static func passive() -> Dictionary:
	# Empty plan + IGNORE every window: matches the calibrator's do_nothing baseline shape
	# (empty plans, ignore verb), so `passive` here is directly comparable to the memo's
	# do_nothing median (14 months on the calibrated constants).
	return RP.make("passive", {}, [], [
		RP.wrule(func(_f, _w): return true, "ignore", "do nothing: let every window lapse at list price"),
	])


static func safety_lean() -> Dictionary:
	return RP.make("safety_lean", {"hire_below": 3}, [
		RP.rule(func(f): return f.safety_researchers < 3, ["hire_safety_researcher"], "hire safety below 3"),
		RP.rule(func(_f): return true, _safety_lean_tail(), "publish every 3rd, else safety_research (x12)"),
	])


static func capability_rush() -> Dictionary:
	return RP.make("capability_rush", {"hire_below": 4}, [
		RP.rule(func(f): return f.capability_researchers < 4, ["hire_capability_researcher"], "hire capability below 4"),
		RP.rule(func(_f): return true, ["buy_compute"] + RP.repeat("capability_research", 12), "buy compute, then capability_research (x12)"),
	])


static func desperation_spam() -> Dictionary:
	return RP.make("desperation_spam", {}, [
		RP.rule(func(_f): return true, RP.repeat("desperation_lever", 6) + RP.repeat("take_loan", 6), "6 levers then 6 loans"),
	])


static func loan_hoard() -> Dictionary:
	return RP.make("loan_hoard", {}, [
		RP.rule(func(_f): return true, RP.repeat("take_loan", 12), "12 loans"),
	])

class_name ReactivePolicyAdapter
extends RefCounted
## EE-9 · Adapter handing a REACTIVE policy (ReactivePolicy dict) to the shared month driver
## (l1_month_driver.gd — the calibration harness's extracted run loop). This replaced the
## lane's earlier parallel MonthRunner: one driver, many policy front-ends.
##
##   plan()         — snapshot features, walk the policy's plan_rules into an ordered action
##                    priority, fill the month's AP/affordability budget against it
##                    (Driver.try_queue — same gate as the calibrator's policies).
##   window_prefs() — the policy's window rules name ONE preferred verb; the driver's
##                    legality check + fallback ladder guarantees the pause clears.
##
## Extras for the instruments built on top:
##   - params.reserve (optional): burn Attention on strategic WIP so the implicit reserve
##     lands at `reserve` (WIP has no gameplay effect in v1 — the L2 seam — so this is purely
##     the reserve-scarcity lever, same trick as the calibrator's greedy_overcommit).
##   - plan_override/override_months (EE-10): replace the first N plan-months' priority with
##     a caller-supplied Callable(state, month_ordinal) -> Array — the opening prefix.
##   - record_features: per-month features snapshots (miner feature vectors), read-only.
##
## Determinism: conditions draw no randomness; this adapter makes NO brng draws (an override
## Callable may carry its own seeded RNG). Engine randomness stays on the seeded state.rng.

const RP = preload("res://tests/manual/reactive_policy.gd")
const Driver = preload("res://tests/manual/l1_month_driver.gd")

var policy: Dictionary
var plan_override = null          # Callable(state, month_ordinal) -> Array, or null
var override_months: int = 0
var record_features: bool = false
var month_features: Array = []    # [{month, cash, doom, ...}] when record_features


func _init(p: Dictionary, cfg: Dictionary = {}) -> void:
	policy = p
	plan_override = cfg.get("plan_override", null)
	override_months = int(cfg.get("override_months", 0))
	record_features = bool(cfg.get("record_features", false))


func name() -> String:
	return String(policy.get("name", "?"))


func plan(state, _brng: RandomNumberGenerator, month_ordinal: int) -> void:
	var f: Dictionary = RP.features(state)
	if record_features:
		var snap := {"month": month_ordinal, "turn": f.turn, "cash": f.cash,
			"runway_months": f.runway_months, "doom": f.doom, "reputation": f.reputation,
			"staff": f.staff, "papers": f.papers, "ledger_outstanding": f.ledger_outstanding}
		month_features.append(snap)

	var priority: Array
	if plan_override != null and month_ordinal < override_months:
		priority = (plan_override as Callable).call(state, month_ordinal)
	else:
		priority = RP.plan_priority(policy, f)

	# L2 (ADR-0011): fill the month's ATTENTION budget (month_plan), not the retired per-turn AP pool.
	var attn_left: int = state.month_plan.available() if state.month_plan != null else 0
	for id in priority:
		if attn_left <= 0:
			break
		attn_left = Driver.try_queue(state, id, attn_left)

	# Optional reserve dial: burn (total - reserve) Attention as WIP so the implicit reserve
	# (total - spent) lands at params.reserve. v1: WIP has no effect — pure scarcity lever.
	var params: Dictionary = policy.get("params", {})
	if params.has("reserve") and state.month_plan != null:
		var burn: int = clampi(state.month_plan.attention_total - int(params["reserve"]),
			0, state.month_plan.available())
		if burn > 0:
			state.month_plan.queue_strategic("__policy_reserve_dial__", burn, 5, state.turn)


func window_prefs(state, _brng: RandomNumberGenerator, window: Dictionary) -> Array:
	var f: Dictionary = RP.features(state)
	return [RP.window_verb(policy, f, window)]

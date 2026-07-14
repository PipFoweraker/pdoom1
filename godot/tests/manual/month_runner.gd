class_name MonthRunner
extends RefCounted
## EE-9/EE-10 · Deterministic headless driver for the L1 month loop (ADR-0009), shared by the
## month sweep, the desperation solver, and the opening-book miner.
##
## Mirrors GameManager's real playable path WITHOUT a SceneTree or timers (advance_tick is
## synchronous): open plan phase -> commit the plan turn -> day-tick playback with auto-pause on
## response windows -> month boundary holds open the next plan phase. A reactive policy
## (ReactivePolicy) decides the plan-phase action priority and every window verb. Bots draw no
## randomness of their own; all randomness is the seeded state.rng, so every (seed, policy[, opening])
## run is deterministic and replayable.
##
## TOOLING ONLY (tests/manual/lib): no gameplay code is touched. The one modelling choice worth
## stating: the plan phase queues LEGACY actions (state.queued_actions -> execute_turn), because in
## current main the strategic-Attention path is not yet wired to effects (the L2 seam). That is the
## real action economy today; when L2 lands, swap _fill's target here — one place.

const RP = preload("res://tests/manual/reactive_policy.gd")

const DEFAULT_MAX_MONTHS := 24
const TICKS_PER_MONTH_CAP := 400   # safety cap on ticks within one month's playback
const WINDOW_ANSWER_CAP := 30      # safety cap on windows answered per pause


static func _ap_cost(id: String) -> int:
	return int(GameActions.get_action_by_id(id).get("costs", {}).get("action_points", 1))


static func _money_cost(id: String) -> float:
	return float(GameActions.get_action_by_id(id).get("costs", {}).get("money", 0.0))


static func _fill(state, priority: Array) -> Array:
	"""Fill this month's action budget against an ordered priority list, gated by available AP and
	money (same rule as test_exploit_sweep._fill). Returns the queued action ids."""
	var acts: Array = []
	var ap: int = state.action_points
	for id in priority:
		if ap <= 0:
			break
		var apc: int = _ap_cost(id)
		if ap >= apc and state.money >= _money_cost(id):
			acts.append(id)
			ap -= apc
	return acts


static func _outcome(state) -> String:
	"""How the run ended (surface counter). Mirrors test_exploit_sweep._outcome."""
	if state.victory:
		return "win"
	if state.doom >= 99.9:
		return "doom_loss"
	if state.ledger != null and (state.ledger.death_attribution as Array).size() > 0:
		return "ledger_death"
	if not state.game_over:
		return "survived"   # reached the month cap alive
	return "other_loss"


static func _snapshot(state, f: Dictionary, month_ordinal: int) -> Dictionary:
	"""Per-month feature snapshot (EE-10 miner input) — taken at the plan phase, before the plan
	commits. Captures the decision context and the outcome-so-far."""
	return {
		"month": month_ordinal,
		"turn": state.turn,
		"cash": f.cash,
		"runway_months": f.runway_months,
		"doom": f.doom,
		"reputation": f.reputation,
		"governance": f.governance,
		"staff": f.staff,
		"papers": f.papers,
		"ledger_outstanding": f.ledger_outstanding,
	}


static func _answer_windows(mc, policy: Dictionary, state) -> void:
	"""Answer every open window with the policy's window verb, with a legality + payment fallback
	chain that guarantees the pause clears (handle_reserve -> cannibalize -> skip/auto_ignore)."""
	var wguard := 0
	while mc.is_paused() and wguard < WINDOW_ANSWER_CAP:
		wguard += 1
		var w: Dictionary = mc.window_queue[0]
		var f := RP.features(state)
		var verb := RP.window_verb(policy, f, w)
		if verb == "ignore" and EventTiers.is_unignorable(w):
			verb = "handle_reserve"
		if verb == "defer" and not EventTiers.defer_allowed(w):
			verb = "handle_reserve"
		var res: Dictionary = mc.resolve_current_window(verb)
		if res.get("success", false):
			continue
		# Fallback: guarantee forward progress so playback can never hang on an unpayable verb.
		if mc.resolve_current_window("handle_cannibalize").get("success", false):
			continue
		if not EventTiers.is_unignorable(w):
			mc.skip_current_window()
		else:
			break  # unignorable and unpayable (should not happen with a funded reserve)


static func run(seed_str: String, policy: Dictionary, cfg: Dictionary = {}) -> Dictionary:
	"""Drive one (seed, policy) run through the month loop. cfg keys (all optional):
	  max_months           int   — plan-months to play before stopping a survivor (default 24)
	  turn_cap             int   — hard day-tick ceiling (safety)
	  record_month_features bool  — collect per-month snapshots (EE-10 miner)
	  plan_override        Callable(state, month_ordinal) -> Array  — override plan priority...
	  override_months      int   — ...for the first this-many months (EE-10 opening prefix)
	Returns a result dict: {policy, seed, turns, months, outcome, doom, cash, reputation,
	root_cause, surface, chain, month_features}."""
	var max_months: int = int(cfg.get("max_months", DEFAULT_MAX_MONTHS))
	var turn_cap: int = int(cfg.get("turn_cap", max_months * 40 + 60))
	var record: bool = bool(cfg.get("record_month_features", false))
	var plan_override = cfg.get("plan_override", null)
	var override_months: int = int(cfg.get("override_months", 0))

	var state = GameState.new(seed_str)
	var tm = TurnManager.new(state)
	var mc = MonthController.new(state, tm)
	var month_features: Array = []

	tm.start_turn()  # open the month-0 plan phase (turn 1) — mirrors GameManager.start_new_game

	var months_planned := 0
	var loop_guard := 0
	while months_planned < max_months and not state.game_over and state.turn < turn_cap:
		loop_guard += 1
		if loop_guard > max_months + turn_cap + 100:
			break
		# ---- PLAN PHASE (turn open, ACTION_SELECTION) ----
		var f := RP.features(state)
		if record:
			month_features.append(_snapshot(state, f, months_planned))
		var priority: Array
		if plan_override != null and months_planned < override_months:
			priority = (plan_override as Callable).call(state, months_planned)
		else:
			priority = RP.plan_priority(policy, f)
		for a in _fill(state, priority):
			state.queued_actions.append(a)
		if state.queued_actions.is_empty():
			state.queued_actions.append("pass")  # an empty month still commits (a real idle month)
		# Implicit reserve (GameManager.end_month parity): everything not spent on strategic
		# Attention guards this month's windows.
		if state.month_plan != null:
			state.month_plan.set_reserve(state.month_plan.attention_total - state.month_plan.attention_spent)
		# ---- COMMIT the open plan turn ----
		tm.execute_turn()
		months_planned += 1
		if state.game_over:
			break
		# ---- PLAYBACK to the next month boundary (held open as the next plan phase) ----
		var reached_boundary := false
		var tickguard := 0
		while not reached_boundary and not state.game_over and state.turn < turn_cap and tickguard < TICKS_PER_MONTH_CAP:
			tickguard += 1
			var r: Dictionary = mc.advance_tick()
			match String(r.get("status", "")):
				"paused_on_window":
					_answer_windows(mc, policy, state)
					if mc.month_open_pending:
						reached_boundary = true
				"month_open":
					reached_boundary = true
				# "ready" -> keep ticking

	var attribution: Dictionary = DeathAttribution.classify(state)
	return {
		"policy": String(policy.get("name", "?")),
		"seed": seed_str,
		"turns": state.turn,
		"months": months_planned,
		"outcome": _outcome(state),
		"doom": state.doom,
		"cash": state.money,
		"reputation": state.reputation,
		"root_cause": String(attribution.get("root_cause", "other")),
		"surface": String(attribution.get("surface", "other")),
		"chain": attribution.get("chain", []),
		"month_features": month_features,
	}

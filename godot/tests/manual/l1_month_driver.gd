class_name L1MonthDriver
extends RefCounted
## THE shared L1 month-cycle run driver (harness unification, PR #642 correction round).
##
## Extracted VERBATIM from test_l1_month_sweep.gd's `_run`/`_answer_windows` (the G1
## calibration harness whose 72-run CSV is the calibration reference -- see
## docs/balance/L1_CALIBRATION_2026-07-14.md) so that every balance instrument drives the
## SAME month loop: the calibrator's sweep, the EE-9 reactive-policy sweep, the desperation
## solver-bot, and the EE-10 opening-book miner. Two month-runners was a maintenance smell;
## this is the one. Extraction verified outcome-neutral by diffing the calibrator's
## regenerated docs/balance/L1_sweep_runs.csv against the tracked copy (byte-stable).
##
## The driver reimplements GameManager.end_month + _run_month_playback SYNCHRONOUSLY (no
## SceneTree timers): plan commit -> day-tick playback (MonthController.advance_tick) ->
## auto-pause-on-window -> month boundary -> new plan phase. It does NOT clamp doom -- a
## balance instrument must let runs die.
##
## Policy decisions are delegated to an ADAPTER object providing:
##   name() -> String                              -- stamps bot_seed = hash("seed|name")
##   plan(state, brng, month_ordinal) -> void      -- queue actions / strategic WIP for the
##                                                   open plan turn (AP/affordability-gated
##                                                   by the adapter via try_queue below)
##   window_prefs(state, brng, window) -> Array    -- preference-ordered response verbs; the
##                                                   driver applies legality + a fallback
##                                                   ladder so the pause always clears
## Determinism contract: the engine RNG is seeded by the game seed; the bot's own draws come
## from `brng` (seeded hash(seed|name)) -- an adapter must make identical brng draws in
## identical order for a given (seed, policy) to keep runs replayable.

const MAX_TICKS_PER_MONTH := 60  # wiring guard: a calendar month is ~16 workday ticks
const MAX_WINDOWS_PER_PAUSE := 40
const DEFAULT_MAX_MONTHS := 420  # ADR-0002 mortality guard: > the 400-month hard limit


# ============================================================================
# COST / AFFORDABILITY HELPERS (shared by adapters)
# ============================================================================

static func ap_cost(id: String) -> int:
	# L2 (ADR-0011): the action's legacy action_points cost IS its Attention cost.
	return int(GameActions.get_action_by_id(id).get("costs", {}).get("action_points", 1))


static func non_ap_costs(id: String) -> Dictionary:
	var c: Dictionary = GameActions.get_action_by_id(id).get("costs", {}).duplicate()
	c.erase("action_points")
	return c


static func affordable(state, id: String, attn_left: int) -> bool:
	if ap_cost(id) > attn_left:
		return false
	return state.can_afford(non_ap_costs(id))


static func try_queue(state, id: String, attn_left: int) -> int:
	"""Queue `id` if its Attention cost fits `attn_left` and non-Attention costs are
	affordable. Spends the Attention from month_plan (mirrors GameManager.select_action) so
	the driver's implicit reserve (attention_total - attention_spent) stays correct. Returns
	the remaining Attention budget either way."""
	if affordable(state, id, attn_left):
		state.queued_actions.append(id)
		if state.month_plan != null:
			state.month_plan.attention_spent += ap_cost(id)
		return attn_left - ap_cost(id)
	return attn_left


# ============================================================================
# WINDOW RESPONSE PHASE (verbatim from the calibration harness)
# ============================================================================

static func _answer_windows(adapter, state, mc, brng: RandomNumberGenerator, wstats: Dictionary, wiring_notes: Array) -> void:
	var guard := 0
	while mc.is_paused() and not state.game_over and guard < MAX_WINDOWS_PER_PAUSE:
		guard += 1
		var window: Dictionary = mc.window_queue[0]
		var legal: Array = EventTiers.legal_responses(window)
		var prefs: Array = adapter.window_prefs(state, brng, window)
		var chosen := ""
		for p in prefs:
			if p in legal:
				chosen = p
				break
		if chosen == "":
			chosen = String(legal[0]) if legal.size() > 0 else "handle_reserve"

		wstats["offered"] += 1
		var res: Dictionary = mc.resolve_current_window(chosen)
		if not bool(res.get("success", false)):
			# Fallback ladder so an empty reserve / non-deferrable window still resolves and
			# the pause always clears (else an unignorable window would hang the run).
			for fb in ["handle_reserve", "handle_cannibalize", "ignore", "auto_ignore"]:
				if fb == chosen:
					continue
				res = mc.resolve_current_window(fb)
				if bool(res.get("success", false)):
					chosen = fb
					break
		if not bool(res.get("success", false)):
			wiring_notes.append("window '%s' (class %s) could not be resolved by any verb (seed run)" % [
				String(window.get("id", "?")), EventTiers.class_of(window)])
			# Force-drop to avoid an infinite pause (documented wiring workaround).
			if mc.window_queue.size() > 0:
				mc.window_queue.pop_front()
				if mc.window_queue.is_empty():
					mc.status = MonthController.Status.READY
					mc._finish_paused_tick()
			continue

		# Tally by the resolved verb / payment source.
		match chosen:
			"handle_reserve":
				wstats["handled_reserve"] += 1
			"handle_cannibalize":
				wstats["handled_cannibalize"] += 1
			"defer":
				wstats["deferred"] += 1
			"ignore":
				wstats["ignored"] += 1
			"auto_ignore":
				wstats["auto_ignored"] += 1


# ============================================================================
# THE MONTH DRIVER -- synchronous reimplementation of end_month + playback
# ============================================================================

static func run(seed: String, adapter, cfg: Dictionary = {}) -> Dictionary:
	"""Drive one (seed, adapter-policy) run. cfg: {max_months:int}. Returns the calibration
	harness's result dict (months, death_turn, surface, root_cause, doom trajectory/telemetry,
	window stats, ledger + money/rep finals) plus `wiring_notes`."""
	var max_months: int = int(cfg.get("max_months", DEFAULT_MAX_MONTHS))
	var wiring_notes: Array = []

	var brng := RandomNumberGenerator.new()
	var bot_seed: int = ("%s|%s" % [seed, adapter.name()]).hash()
	brng.seed = bot_seed

	var state = GameState.new(seed, [])
	var tm = TurnManager.new(state)
	var mc = MonthController.new(state, tm)  # current_month_index stamped at turn 0 (mirrors GameManager)
	tm.start_turn()                          # opens turn 1 = month-0 plan phase (mirrors start_new_game)
	# Game-start events are emitted on the legacy plan-phase path before the month loop owns
	# the tick; drop them (they never reach the window system). Documented harness simplification.
	state.pending_events.clear()

	var wstats := {"offered": 0, "handled_reserve": 0, "handled_cannibalize": 0,
		"deferred": 0, "ignored": 0, "auto_ignored": 0}
	var doom_traj: Array = [snappedf(state.doom, 0.1)]  # doom at each month boundary (index 0 = start)
	var attn_spent_by_month: Array = []
	var reserve_by_month: Array = []
	var months := 0

	while not state.game_over and months < max_months:
		# ---- PLAN + COMMIT (mirror GameManager.end_month) ----
		adapter.plan(state, brng, months)
		if state.queued_actions.is_empty():
			state.queued_actions.append(GameActions.PASS_ACTION_ID)
		# Implicit reserve v1: everything not spent on strategic guards the windows.
		if state.month_plan != null:
			state.month_plan.set_reserve(state.month_plan.attention_total - state.month_plan.attention_spent)
		attn_spent_by_month.append(state.month_plan.attention_spent)
		reserve_by_month.append(state.month_plan.attention_reserved)
		tm.execute_turn()  # execute the OPEN plan turn
		if state.game_over:
			break

		# ---- DAY-TICK PLAYBACK until the month boundary or death ----
		var boundary := false
		var tick_guard := 0
		while not state.game_over and not boundary and tick_guard < MAX_TICKS_PER_MONTH:
			tick_guard += 1
			var r: Dictionary = mc.advance_tick()
			match String(r.get("status", "")):
				"paused_on_window":
					_answer_windows(adapter, state, mc, brng, wstats, wiring_notes)
					if mc.month_open_pending:
						boundary = true
				"month_open":
					boundary = true
				_:
					pass
		if tick_guard >= MAX_TICKS_PER_MONTH and not boundary and not state.game_over:
			wiring_notes.append("month %d for policy %s exceeded %d ticks without a boundary" % [
				months, adapter.name(), MAX_TICKS_PER_MONTH])
			break
		if state.game_over:
			break
		# Boundary reached: the boundary tick is held open as the next plan phase.
		months += 1
		doom_traj.append(snappedf(state.doom, 0.1))

	var attribution: Dictionary = DeathAttribution.classify(state)
	var ledger_billed := 0
	for c in state.cause_log:
		if str(c.get("kind", "")) in DeathAttribution.LEDGER_KINDS:
			ledger_billed += 1

	# Per-tick doom curve (record_doom_history appends one entry per resolution tick).
	var doom_hist: Array = []
	for v in state.doom_history:
		doom_hist.append(snappedf(float(v), 0.1))
	# Last tick's doom-source breakdown (which pressure delivered the killing doom).
	var doom_src := {}
	if state.doom_system:
		for k in state.doom_system.doom_sources:
			var val: float = float(state.doom_system.doom_sources[k])
			if abs(val) > 0.05:
				doom_src[k] = snappedf(val, 0.1)

	var out := {
		"seed": seed, "policy": adapter.name(), "bot_seed": bot_seed,
		"months": months, "death_turn": state.turn,
		"death_date": Clock.month_label(state.turn, state.start_year, state.start_month, state.start_day),
		"game_over": state.game_over, "victory": state.victory,
		"surface": str(attribution.surface), "root_cause": str(attribution.root_cause),
		"chain": attribution.chain,
		"doom_traj": doom_traj,
		"doom_hist": doom_hist,
		"doom_src_at_death": doom_src,
		"doom_final": snappedf(state.doom, 0.1),
		"attn_spent_by_month": attn_spent_by_month,
		"reserve_by_month": reserve_by_month,
		"windows": wstats.duplicate(),
		"ledger_entries": state.ledger.entries.size() if state.ledger else 0,
		"ledger_billed": ledger_billed,
		"money_final": int(round(state.money)),
		"rep_final": snappedf(state.reputation, 0.1),
		"wiring_notes": wiring_notes,
	}
	# Free the Node-derived sim objects so bulk runs don't flood the log with orphan dumps.
	if is_instance_valid(state.doom_system):
		state.doom_system.free()
	if state.get("risk_system") != null and is_instance_valid(state.risk_system):
		state.risk_system.free()
	state.free()
	return out

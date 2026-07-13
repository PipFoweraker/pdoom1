extends GutTest
## Headless L1 MONTH-CYCLE BALANCE SWEEP (G1 lane, feeds docs/balance/L1_SWEEP_2026-07-13.md).
##
## The exploit sweep (tests/manual/test_exploit_sweep.gd) drives the pre-L1 single-day turn
## loop. This one drives the NEW month cycle (ADR-0009 / PR #636): plan commit -> day-tick
## playback (MonthController.advance_tick) -> auto-pause-on-window -> month boundary -> new
## plan phase. It measures; it changes NO balance constants.
##
## It reimplements GameManager.end_month + _run_month_playback SYNCHRONOUSLY (no SceneTree
## timers) so 70+ runs stay deterministic and fast — the same object-level driving the
## exploit sweep uses (GameState + TurnManager, plus the MonthController layer). Crucially it
## does NOT clamp doom (test_month_button_path.gd clamps to keep its WIRING smoke alive; a
## balance sweep must let runs die).
##
## Policies (per the G1 brief):
##   random_walk x30   — random affordable actions, random attention split, random window verb
##   do_nothing x10    — empty plans, IGNORE every window (the exploit sweep's "shame" baseline)
##   safety_lean x8    — queue safety-ish actions, keep the full implicit reserve
##   greedy_overcommit x8 — spend ALL attention on strategic WIP (zero reserve), HANDLE by cannibalizing
##   reserve_heavy x8  — >=50% reserve, HANDLE-from-reserve every window
##   loan_desperation x8 — money levers aggressively, DEFER windows to mint ledger entries
##
## Each run is deterministic in (game seed, policy): the engine RNG is seeded by the game
## seed; the bot's own choices draw from a SEPARATE RNG seeded by hash(seed|policy), recorded
## per run for repro. Invoke:
##   "/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot \
##     -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_l1_month_sweep.gd -glog=1 -gexit

const MAX_MONTHS := 60           # safety cap (a run to 2040 is ~270 months; nothing gets close pre-rebalance)
const MAX_TICKS_PER_MONTH := 60  # wiring guard: a calendar month is ~16 workday ticks
const MAX_WINDOWS_PER_PAUSE := 40
const RUNS_CSV := "res://../docs/balance/L1_sweep_runs.csv"

# Leaf actions only (submenu openers like hire_staff/fundraise have no effect — excluded).
const SAFE_ACTIONS := ["hire_safety_researcher", "safety_research", "publish_paper", "audit_safety"]
const CAP_ACTIONS := ["hire_capability_researcher", "capability_research", "buy_compute"]
const MONEY_LEVERS := ["take_loan", "desperation_lever", "funding_strings", "staff_rider"]
const RANDOM_POOL := [
	"safety_research", "capability_research", "publish_paper", "buy_compute", "team_building",
	"audit_safety", "hire_safety_researcher", "hire_capability_researcher", "hire_compute_engineer",
	"hire_manager", "take_loan", "desperation_lever", "funding_strings", "staff_rider",
	"fundraise_small", "fundraise_big", "apply_grant", "network", "media_campaign",
	"order_supplies", "office_maintenance",
]

# (policy_name, seed_count)
const POLICY_PLAN := [
	["random_walk", 30],
	["do_nothing", 10],
	["safety_lean", 8],
	["greedy_overcommit", 8],
	["reserve_heavy", 8],
	["loan_desperation", 8],
]

var _wiring_notes: Array = []


# ============================================================================
# COST / AFFORDABILITY HELPERS
# ============================================================================

func _ap_cost(id: String) -> int:
	return int(GameActions.get_action_by_id(id).get("costs", {}).get("action_points", 1))


func _non_ap_costs(id: String) -> Dictionary:
	var c: Dictionary = GameActions.get_action_by_id(id).get("costs", {}).duplicate()
	c.erase("action_points")
	return c


func _affordable(state, id: String, ap_left: int) -> bool:
	if _ap_cost(id) > ap_left:
		return false
	return state.can_afford(_non_ap_costs(id))


# ============================================================================
# PLAN PHASE — queue legacy actions (AP-gated) + strategic WIP (the reserve lever)
#
# In v1 the meaningful game effects come from state.queued_actions (executed once at
# end_month). Strategic WIP (MonthPlan.queued_strategic) has NO gameplay effect yet (L2
# seam) — so spending Attention on it is a pure reserve-reduction lever: end_month sets
# reserve = attention_total - attention_spent, so reserve = 20 - strategic_spend.
# ============================================================================

func _plan(policy: String, state, brng: RandomNumberGenerator) -> void:
	var ap_left: int = state.action_points
	var strategic_spend := 0  # attention units to burn on WIP (lowers the implicit reserve)

	match policy:
		"do_nothing":
			pass  # empty plan -> pass action; full 20 reserve
		"safety_lean":
			var order := ["hire_safety_researcher", "safety_research", "publish_paper", "audit_safety", "safety_research"]
			for id in order:
				ap_left = _try_queue(state, id, ap_left)
			# keep the full implicit reserve (no strategic spend)
		"greedy_overcommit":
			# spend everything: attention AND action points; zero reserve.
			strategic_spend = state.month_plan.attention_total  # burn all 20 -> reserve 0
			var greedy := ["buy_compute", "hire_capability_researcher", "capability_research",
				"capability_research", "hire_compute_engineer", "team_building"]
			for id in greedy:
				ap_left = _try_queue(state, id, ap_left)
		"reserve_heavy":
			strategic_spend = int(state.month_plan.attention_total / 2)  # >=50% held in reserve
			for id in ["hire_safety_researcher", "safety_research", "network"]:
				ap_left = _try_queue(state, id, ap_left)
		"loan_desperation":
			for id in ["take_loan", "desperation_lever", "funding_strings", "take_loan", "staff_rider"]:
				ap_left = _try_queue(state, id, ap_left)
		"random_walk":
			strategic_spend = brng.randi_range(0, state.month_plan.attention_total)  # random reserve
			var picks := brng.randi_range(0, 5)
			for _i in range(picks):
				var id: String = RANDOM_POOL[brng.randi_range(0, RANDOM_POOL.size() - 1)]
				ap_left = _try_queue(state, id, ap_left)
		_:
			pass

	# Burn strategic attention as durationed WIP (no effect in v1; sets the reserve).
	if strategic_spend > 0:
		state.month_plan.queue_strategic("__sweep_wip__", strategic_spend, 5, state.turn)


func _try_queue(state, id: String, ap_left: int) -> int:
	if _affordable(state, id, ap_left):
		state.queued_actions.append(id)
		return ap_left - _ap_cost(id)
	return ap_left


# ============================================================================
# WINDOW RESPONSE PHASE
# ============================================================================

func _window_prefs(policy: String, brng: RandomNumberGenerator) -> Array:
	match policy:
		"do_nothing":
			return ["ignore"]
		"safety_lean":
			return ["handle_reserve", "handle_cannibalize"]
		"greedy_overcommit":
			return ["handle_cannibalize", "handle_reserve"]
		"reserve_heavy":
			return ["handle_reserve", "handle_cannibalize"]
		"loan_desperation":
			return ["defer", "ignore", "handle_cannibalize"]
		"random_walk":
			return _shuffle_det(["handle_reserve", "handle_cannibalize", "defer", "ignore"], brng)
		_:
			return ["ignore", "handle_reserve"]


func _shuffle_det(arr: Array, brng: RandomNumberGenerator) -> Array:
	var a := arr.duplicate()
	for i in range(a.size() - 1, 0, -1):
		var j := brng.randi_range(0, i)
		var tmp = a[i]; a[i] = a[j]; a[j] = tmp
	return a


func _answer_windows(policy: String, state, mc, brng: RandomNumberGenerator, wstats: Dictionary) -> void:
	var guard := 0
	while mc.is_paused() and not state.game_over and guard < MAX_WINDOWS_PER_PAUSE:
		guard += 1
		var window: Dictionary = mc.window_queue[0]
		var legal: Array = EventTiers.legal_responses(window)
		var prefs: Array = _window_prefs(policy, brng)
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
			_wiring_notes.append("window '%s' (class %s) could not be resolved by any verb (seed run)" % [
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
# THE MONTH DRIVER — synchronous reimplementation of end_month + playback
# ============================================================================

func _run(seed: String, policy: String) -> Dictionary:
	var brng := RandomNumberGenerator.new()
	var bot_seed: int = ("%s|%s" % [seed, policy]).hash()
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

	while not state.game_over and months < MAX_MONTHS:
		# ---- PLAN + COMMIT (mirror GameManager.end_month) ----
		_plan(policy, state, brng)
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
					_answer_windows(policy, state, mc, brng, wstats)
					if mc.month_open_pending:
						boundary = true
				"month_open":
					boundary = true
				_:
					pass
		if tick_guard >= MAX_TICKS_PER_MONTH and not boundary and not state.game_over:
			_wiring_notes.append("month %d for policy %s exceeded %d ticks without a boundary" % [
				months, policy, MAX_TICKS_PER_MONTH])
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

	# Per-tick doom curve (record_doom_history appends one entry per resolution tick) —
	# the trajectory instrument the month boundaries can't provide because no run reaches one.
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
		"seed": seed, "policy": policy, "bot_seed": bot_seed,
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
	}
	# Free the Node-derived sim objects so 72 runs don't flood the log with orphan dumps.
	if is_instance_valid(state.doom_system):
		state.doom_system.free()
	if state.get("risk_system") != null and is_instance_valid(state.risk_system):
		state.risk_system.free()
	state.free()
	return out


# ============================================================================
# STATS
# ============================================================================

func _median(sorted_vals: Array) -> float:
	var n := sorted_vals.size()
	if n == 0:
		return 0.0
	if n % 2 == 1:
		return float(sorted_vals[n / 2])
	return (float(sorted_vals[n / 2 - 1]) + float(sorted_vals[n / 2])) / 2.0


func _mean(vals: Array) -> float:
	if vals.is_empty():
		return 0.0
	var s := 0.0
	for v in vals:
		s += float(v)
	return s / vals.size()


func _slope(traj: Array, month: int) -> Variant:
	# doom delta over calendar-month `month` (1-based): traj[month] - traj[month-1]. null if unreached.
	if traj.size() > month:
		return float(traj[month]) - float(traj[month - 1])
	return null


# ============================================================================
# THE SWEEP
# ============================================================================

func _calendar_month_lengths(n: int) -> Array:
	# Pure Clock arithmetic (no sim): how many workday ticks each of the first n plan-months
	# spans. Turn 1 opens plan-month 0; a boundary is the tick whose calendar month differs
	# from the previous tick. Contrasts "ticks in a month" against "ticks to die".
	var lengths: Array = []
	var probe = GameState.new("__calprobe__", [])
	var sy: int = probe.start_year; var sm: int = probe.start_month; var sd: int = probe.start_day
	probe.free()
	var boundaries: Array = []
	var t := 1
	while boundaries.size() < n + 1 and t < 400:
		if Clock.is_month_boundary(t, sy, sm, sd):
			boundaries.append(t)
		t += 1
	for i in range(1, boundaries.size()):
		lengths.append(int(boundaries[i]) - int(boundaries[i - 1]))
	return lengths


func test_l1_month_sweep() -> void:
	var month_lengths := _calendar_month_lengths(4)

	var by_policy := {}
	var all_runs: Array = []
	var t0 := Time.get_ticks_msec()
	for entry in POLICY_PLAN:
		var pname: String = entry[0]
		var count: int = entry[1]
		by_policy[pname] = []
		for i in range(count):
			var seed := "l1sweep-%s-%02d" % [pname, i]
			var run := _run(seed, pname)
			by_policy[pname].append(run)
			all_runs.append(run)
	var elapsed := (Time.get_ticks_msec() - t0) / 1000.0

	# ---- Per-run CSV (determinism + full data for the memo/repro appendix) ----
	var csv: Array = []
	csv.append("seed,policy,bot_seed,months,death_turn,death_date,surface,root_cause,victory," +
		"doom_start,doom_m1,doom_m2,doom_m3,doom_final," +
		"win_offered,win_reserve,win_cannib,win_defer,win_ignore,win_autoignore," +
		"ledger_entries,ledger_billed,money_final,rep_final")
	for r in all_runs:
		var traj: Array = r["doom_traj"]
		var w: Dictionary = r["windows"]
		csv.append("%s,%s,%d,%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%.1f,%d,%d,%d,%d,%d,%d,%d,%d,%d,%.1f" % [
			r["seed"], r["policy"], r["bot_seed"], r["months"], r["death_turn"], r["death_date"],
			r["surface"], r["root_cause"], str(r["victory"]),
			str(traj[0]), _traj_at(traj, 1), _traj_at(traj, 2), _traj_at(traj, 3), r["doom_final"],
			w["offered"], w["handled_reserve"], w["handled_cannibalize"], w["deferred"],
			w["ignored"], w["auto_ignored"],
			r["ledger_entries"], r["ledger_billed"], r["money_final"], r["rep_final"]])
	var csv_text := "\n".join(csv) + "\n"
	var f = FileAccess.open(RUNS_CSV, FileAccess.WRITE)
	if f:
		f.store_string(csv_text)
		f.close()

	print("\n===L1_SWEEP_CSV_BEGIN===")
	print(csv_text)
	print("===L1_SWEEP_CSV_END===")

	# ---- Aggregate summary per policy ----
	print("\n===L1_SWEEP_SUMMARY_BEGIN===")
	print("policy | n | median_months | min | max | median_death_turn | mean_m1_slope | mean_m2_slope | mean_m3_slope | deaths(doom/rep/ledger/other/win/immortal)")
	for entry in POLICY_PLAN:
		var pname: String = entry[0]
		var rows: Array = by_policy[pname]
		var months_arr: Array = []
		var turns_arr: Array = []
		var m1: Array = []; var m2: Array = []; var m3: Array = []
		var dc := {"doom": 0, "rep": 0, "ledger": 0, "other": 0, "win": 0, "immortal": 0}
		for r in rows:
			months_arr.append(r["months"])
			turns_arr.append(r["death_turn"])
			var s1 = _slope(r["doom_traj"], 1); if s1 != null: m1.append(s1)
			var s2 = _slope(r["doom_traj"], 2); if s2 != null: m2.append(s2)
			var s3 = _slope(r["doom_traj"], 3); if s3 != null: m3.append(s3)
			if r["victory"]:
				dc["win"] += 1
			elif not r["game_over"]:
				dc["immortal"] += 1
			else:
				var root: String = r["root_cause"]
				if dc.has(root):
					dc[root] += 1
				else:
					dc["other"] += 1
		months_arr.sort()
		turns_arr.sort()
		print("%s | %d | %.1f | %d | %d | %.0f | %s | %s | %s | %d/%d/%d/%d/%d/%d" % [
			pname, rows.size(), _median(months_arr), months_arr[0], months_arr[months_arr.size() - 1],
			_median(turns_arr), _fmt(_mean(m1)), _fmt(_mean(m2)), _fmt(_mean(m3)),
			dc["doom"], dc["rep"], dc["ledger"], dc["other"], dc["win"], dc["immortal"]])
	print("===L1_SWEEP_SUMMARY_END===")

	# ---- Narrative candidates: representative runs, full trajectory + chain ----
	print("\n===L1_SWEEP_NARRATIVES_BEGIN===")
	for pick in [_representative(by_policy["reserve_heavy"]), _representative(by_policy["greedy_overcommit"]),
			_representative(by_policy["random_walk"]), _representative(by_policy["do_nothing"]),
			_representative(by_policy["loan_desperation"])]:
		if pick.is_empty():
			continue
		print("--- %s / seed %s (bot_seed %d) ---" % [pick["policy"], pick["seed"], pick["bot_seed"]])
		print("  months=%d death_turn=%d date=%s surface=%s root=%s victory=%s" % [
			pick["months"], pick["death_turn"], pick["death_date"], pick["surface"], pick["root_cause"], str(pick["victory"])])
		print("  doom_traj=%s doom_final=%.1f" % [str(pick["doom_traj"]), pick["doom_final"]])
		print("  attn_spent_by_month=%s reserve_by_month=%s" % [str(pick["attn_spent_by_month"]), str(pick["reserve_by_month"])])
		print("  windows=%s ledger_entries=%d ledger_billed=%d money_final=%d rep_final=%.1f" % [
			str(pick["windows"]), pick["ledger_entries"], pick["ledger_billed"], pick["money_final"], pick["rep_final"]])
		print("  doom_per_tick=%s" % str(pick["doom_hist"]))
		print("  doom_sources_at_death=%s" % str(pick["doom_src_at_death"]))
		var chain: Array = pick["chain"]
		print("  chain=%s" % ("(none)" if chain.is_empty() else " -> ".join(chain)))
	print("===L1_SWEEP_NARRATIVES_END===")

	print("\n===L1_SWEEP_CALENDAR_BEGIN===")
	print("workday-ticks per plan-month (first 4, pure Clock, no sim): %s" % str(month_lengths))
	print("===L1_SWEEP_CALENDAR_END===")

	# ---- Wiring notes ----
	print("\n===L1_SWEEP_WIRING_BEGIN===")
	if _wiring_notes.is_empty():
		print("no wiring anomalies observed")
	else:
		for n in _wiring_notes:
			print("WIRING: %s" % n)
	print("===L1_SWEEP_WIRING_END===")

	print("\nSweep ran %d runs in %.1fs." % [all_runs.size(), elapsed])
	assert_eq(all_runs.size(), 72, "ran all planned runs")


func _traj_at(traj: Array, month: int) -> String:
	return "%.1f" % float(traj[month]) if traj.size() > month else ""


func _fmt(v: float) -> String:
	return "%.2f" % v


func _representative(rows: Array) -> Dictionary:
	# Pick the run whose months-survived is the median (the typical lived experience).
	if rows.is_empty():
		return {}
	var sorted_rows := rows.duplicate()
	sorted_rows.sort_custom(func(a, b): return int(a["months"]) < int(b["months"]))
	return sorted_rows[sorted_rows.size() / 2]

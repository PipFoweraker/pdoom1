extends GutTest
## Headless L1 MONTH-CYCLE BALANCE SWEEP (G1 lane, feeds docs/balance/L1_SWEEP_2026-07-13.md).
##
## The exploit sweep (tests/manual/test_exploit_sweep.gd) drives the pre-L1 single-day turn
## loop. This one drives the NEW month cycle (ADR-0009 / PR #636): plan commit -> day-tick
## playback (MonthController.advance_tick) -> auto-pause-on-window -> month boundary -> new
## plan phase. It measures; it changes NO balance constants.
##
## It reimplements GameManager.end_month + _run_month_playback SYNCHRONOUSLY (no SceneTree
## timers) so 70+ runs stay deterministic and fast -- the same object-level driving the
## exploit sweep uses (GameState + TurnManager, plus the MonthController layer). Crucially it
## does NOT clamp doom (test_month_button_path.gd clamps to keep its WIRING smoke alive; a
## balance sweep must let runs die).
##
## Policies (per the G1 brief):
##   random_walk x30   -- random affordable actions, random attention split, random window verb
##   do_nothing x10    -- empty plans, IGNORE every window (the exploit sweep's "shame" baseline)
##   safety_lean x8    -- queue safety-ish actions, keep the full implicit reserve
##   greedy_overcommit x8 -- spend ALL attention on strategic WIP (zero reserve), HANDLE by cannibalizing
##   reserve_heavy x8  -- >=50% reserve, HANDLE-from-reserve every window
##   loan_desperation x8 -- money levers aggressively, DEFER windows to mint ledger entries
##
## Each run is deterministic in (game seed, policy): the engine RNG is seeded by the game
## seed; the bot's own choices draw from a SEPARATE RNG seeded by hash(seed|policy), recorded
## per run for repro. Invoke:
##   "/c/Program Files/Godot/Godot_v4.5.1-stable_win64_console.exe" --headless --path godot \
##     -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_l1_month_sweep.gd -glog=1 -gexit

const MAX_MONTHS := 420          # ADR-0002 mortality check: a run reaching this cap FAILS the
                                 # iteration (no immortal runs). 420 > the 400-month hard limit
                                 # so a runaway-survival policy is detectable, not silently capped.
const MAX_TICKS_PER_MONTH := 60  # wiring guard: a calendar month is ~16 workday ticks
const MAX_WINDOWS_PER_PAUSE := 40
const RUNS_CSV := "res://../docs/balance/L1_sweep_runs.csv"

# Leaf actions only (submenu openers like hire_staff/fundraise have no effect -- excluded).
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

# Harness unification (PR #642): the month-cycle run driver -- plan commit -> day-tick
# playback -> window auto-pause -> boundary, plus all telemetry -- was extracted VERBATIM
# into l1_month_driver.gd so the EE-9/EE-10 instruments drive the SAME loop as this
# calibrator. This file keeps ONLY the policy definitions (_plan/_window_prefs) and the
# reporting. Extraction verified outcome-neutral: the regenerated L1_sweep_runs.csv is
# byte-stable against the tracked calibration copy.
const Driver = preload("res://tests/manual/l1_month_driver.gd")


## Adapter handing this file's string-keyed policies to the shared driver. brng draw order
## is identical to the pre-extraction code, so (seed, policy) runs stay bit-reproducible.
class LegacyPolicyAdapter:
	var host  # the test script instance (owns _plan/_window_prefs)
	var policy: String

	func _init(h, p: String) -> void:
		host = h
		policy = p

	func name() -> String:
		return policy

	func plan(state, brng: RandomNumberGenerator, _month_ordinal: int) -> void:
		host._plan(policy, state, brng)

	func window_prefs(state, brng: RandomNumberGenerator, _window: Dictionary) -> Array:
		return host._window_prefs(policy, brng)


# ============================================================================
# PLAN PHASE -- queue legacy actions (now ATTENTION-gated) + strategic WIP (reserve lever)
#
# L2 (ADR-0011): the founder spends the MONTHLY ATTENTION budget (~20), not a per-turn AP
# pool. Per-action costs are UNCHANGED (Pip's one-variable ruling: swap the budget/currency
# only, don't rescale costs) -- so a plan of the existing cheap actions leaves lots of
# Attention unspent; that action-sparsity is accepted here (richness is a later content
# wave). Strategic WIP (MonthPlan.queued_strategic) still has NO gameplay effect (L2 seam),
# so burning Attention on it is a pure reserve-reduction lever: the driver sets
# reserve = attention_total - attention_spent, so unspent Attention = reserve.
# ============================================================================

func _plan(policy: String, state, brng: RandomNumberGenerator) -> void:
	var attn_left: int = state.month_plan.available()  # the fresh monthly Attention budget

	match policy:
		"do_nothing":
			pass  # empty plan -> pass action; full reserve
		"safety_lean":
			var order := ["hire_safety_researcher", "safety_research", "publish_paper", "audit_safety", "safety_research"]
			for id in order:
				attn_left = _try_queue(state, id, attn_left)
			# keep the full implicit reserve (no strategic spend)
		"greedy_overcommit":
			var greedy := ["buy_compute", "hire_capability_researcher", "capability_research",
				"capability_research", "hire_compute_engineer", "team_building"]
			for id in greedy:
				attn_left = _try_queue(state, id, attn_left)
			# burn ALL remaining Attention on WIP -> reserve 0 (zero-reserve gamble)
			var rem: int = state.month_plan.available()
			if rem > 0:
				state.month_plan.queue_strategic("__sweep_wip__", rem, 5, state.turn)
		"reserve_heavy":
			# hold >=50% in reserve: cap founder spend at half the monthly budget
			var cap := int(state.month_plan.attention_total / 2)
			for id in ["hire_safety_researcher", "safety_research", "network"]:
				if state.month_plan.attention_spent >= cap:
					break
				attn_left = _try_queue(state, id, attn_left)
		"loan_desperation":
			for id in ["take_loan", "desperation_lever", "funding_strings", "take_loan", "staff_rider"]:
				attn_left = _try_queue(state, id, attn_left)
		"random_walk":
			var picks := brng.randi_range(0, 5)
			for _i in range(picks):
				var id: String = RANDOM_POOL[brng.randi_range(0, RANDOM_POOL.size() - 1)]
				attn_left = _try_queue(state, id, attn_left)
			# random extra WIP burn -> random reserve level
			var rem: int = state.month_plan.available()
			if rem > 0:
				var burn := brng.randi_range(0, rem)
				if burn > 0:
					state.month_plan.queue_strategic("__sweep_wip__", burn, 5, state.turn)
		_:
			pass


func _try_queue(state, id: String, attn_left: int) -> int:
	return Driver.try_queue(state, id, attn_left)


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


# ============================================================================
# THE MONTH DRIVER -- extracted to l1_month_driver.gd (shared with EE-9/EE-10)
# ============================================================================

func _run(seed: String, policy: String) -> Dictionary:
	var out: Dictionary = Driver.run(seed, LegacyPolicyAdapter.new(self, policy), {"max_months": MAX_MONTHS})
	for n in out.get("wiring_notes", []):
		_wiring_notes.append(n)
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
		"doom_start,doom_m1,doom_m2,doom_m3,doom_m4,doom_m5,doom_m6,doom_final," +
		"win_offered,win_reserve,win_cannib,win_defer,win_ignore,win_autoignore," +
		"ledger_entries,ledger_billed,money_final,rep_final")
	for r in all_runs:
		var traj: Array = r["doom_traj"]
		var w: Dictionary = r["windows"]
		csv.append("%s,%s,%d,%d,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%.1f,%d,%d,%d,%d,%d,%d,%d,%d,%d,%.1f" % [
			r["seed"], r["policy"], r["bot_seed"], r["months"], r["death_turn"], r["death_date"],
			r["surface"], r["root_cause"], str(r["victory"]),
			str(traj[0]), _traj_at(traj, 1), _traj_at(traj, 2), _traj_at(traj, 3),
			_traj_at(traj, 4), _traj_at(traj, 5), _traj_at(traj, 6), r["doom_final"],
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
	print("policy | n | median_months | min | max | median_death_turn | m1..m6 mean doom-slope | deaths(doom/rep/ledger/other/win/immortal)")
	var overall_max_months := 0
	var immortal_total := 0
	for entry in POLICY_PLAN:
		var pname: String = entry[0]
		var rows: Array = by_policy[pname]
		var months_arr: Array = []
		var turns_arr: Array = []
		var ms: Array = [[], [], [], [], [], []]  # m1..m6 slope samples
		var dc := {"doom": 0, "rep": 0, "ledger": 0, "other": 0, "win": 0, "immortal": 0}
		for r in rows:
			months_arr.append(r["months"])
			turns_arr.append(r["death_turn"])
			for mi in range(1, 7):
				var s = _slope(r["doom_traj"], mi)
				if s != null:
					ms[mi - 1].append(s)
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
		overall_max_months = max(overall_max_months, int(months_arr[months_arr.size() - 1]))
		immortal_total += dc["immortal"]
		var slope_str := ""
		for mi in range(6):
			slope_str += ("%s " % _fmt(_mean(ms[mi])))
		print("%s | %d | %.1f | %d | %d | %.0f | %s| %d/%d/%d/%d/%d/%d" % [
			pname, rows.size(), _median(months_arr), months_arr[0], months_arr[months_arr.size() - 1],
			_median(turns_arr), slope_str,
			dc["doom"], dc["rep"], dc["ledger"], dc["other"], dc["win"], dc["immortal"]])
	# ADR-0002 mortality guarantee: every policy must die, and no run may exceed 400 months.
	var mortality_ok := (overall_max_months < 400) and (immortal_total == 0)
	print("MORTALITY_CHECK: max_months=%d immortal_runs=%d -> %s" % [
		overall_max_months, immortal_total, ("PASS" if mortality_ok else "FAIL (ADR-0002 violated)")])
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

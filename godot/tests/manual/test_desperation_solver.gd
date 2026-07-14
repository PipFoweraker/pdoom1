extends GutTest
## EE-9 · SOLVER-BOT — desperation levers (DQ-25, Pip's open-Q1).
##
## Systematically varies usage of ONE mechanic — the desperation lever (financing.json:
## desperation_lever: -10 doom now, plants a SECRET compounding governance liability, fuse 3
## turns) — against a FIXED baseline policy, and reports the survival / death-cause deltas.
## Answers Pip's question: does the lever ever PAY, or does the ledger backlash kill you faster
## than the doom it buys down?
##
## Method (the established "isolate-one-variable" solver technique): baseline = fundraise_first
## with NO lever; variants = the same policy + a single injected rule "pull the lever when doom
## >= threshold", swept across thresholds. Everything else is held identical, so the survival
## delta is attributable to the lever alone. Generic — point `MECHANIC`/`_variant` at another
## action to solve a different mechanic.
##
## tests/manual (excluded from CI/quick). Invoke:
##   "$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_desperation_solver.gd -gexit

const RP = preload("res://tests/manual/reactive_policy.gd")
const MonthRunnerC = preload("res://tests/manual/month_runner.gd")
const SweepPoliciesC = preload("res://tests/manual/sweep_policies.gd")

const NUM_SEEDS := 12
const MAX_MONTHS := 24
const MECHANIC := "desperation_lever"
const THRESHOLDS := [60.0, 70.0, 80.0, 90.0]  # pull the lever when doom crosses this
const REPORT_PATH := "res://../docs/balance/DESPERATION_SOLVER.md"


func _seeds() -> Array:
	var a := []
	for i in range(NUM_SEEDS):
		a.append("sweep-%02d" % i)
	return a


func _variant(threshold: float) -> Dictionary:
	"""fundraise_first with a single lever rule prepended: pull one lever when doom >= threshold."""
	var base: Dictionary = SweepPoliciesC.fundraise_first()
	var rules: Array = [
		RP.rule(func(f): return f.doom >= threshold, [MECHANIC], "solver: %s at doom>=%.0f" % [MECHANIC, threshold]),
	]
	rules.append_array(base.plan_rules)
	return RP.make("lever@%.0f" % threshold, {"lever_doom_threshold": threshold}, rules, base.window_rules)


func _median(v: Array) -> float:
	var s := v.duplicate()
	s.sort()
	var n := s.size()
	if n == 0:
		return 0.0
	if n % 2 == 1:
		return float(s[n / 2])
	return (float(s[n / 2 - 1]) + float(s[n / 2])) / 2.0


func _stats(rows: Array) -> Dictionary:
	var turns := []
	var lever_deaths := 0  # root-cause ledger (the lever's secret liability biting)
	var doom_deaths := 0
	for r in rows:
		turns.append(r.turns)
		if String(r.root_cause) == "ledger":
			lever_deaths += 1
		elif String(r.surface) == "doom":
			doom_deaths += 1
	return {"median_turns": _median(turns), "min_turns": turns.min(), "max_turns": turns.max(),
		"ledger_root": lever_deaths, "doom_surface": doom_deaths, "mean_turns": _mean(turns)}


func _mean(v: Array) -> float:
	if v.is_empty():
		return 0.0
	var s := 0.0
	for x in v:
		s += float(x)
	return s / v.size()


func test_desperation_solver() -> void:
	var variants: Array = [
		{"name": "baseline (no lever)", "policy": SweepPoliciesC.fundraise_first()},
		# Unconditional: pull the lever at EVERY plan phase (fires at month 0, so it actually
		# exercises the mechanic even when death is sub-month).
		{"name": "lever@always", "policy": _variant(0.0)},
	]
	for t in THRESHOLDS:
		variants.append({"name": "lever@%.0f" % t, "policy": _variant(t)})

	var results := {}
	for v in variants:
		var rows := []
		for seed in _seeds():
			rows.append(MonthRunnerC.run(seed, v.policy, {"max_months": MAX_MONTHS}))
		results[v.name] = rows

	var baseline_stats: Dictionary = _stats(results["baseline (no lever)"])

	print("\n===SOLVER_RUNS_BEGIN===")
	print("variant,seed,turns,outcome,doom,root_cause")
	for v in variants:
		for r in results[v.name]:
			print("%s,%s,%d,%s,%.2f,%s" % [v.name, r.seed, r.turns, r.outcome, r.doom, r.root_cause])
	print("===SOLVER_RUNS_END===")

	var lines := []
	lines.append("# Desperation-Lever Solver — does the lever ever pay?")
	lines.append("")
	lines.append("> **CAVEAT — regenerate post-migration.** Balance constants predate the nine-stream doom")
	lines.append("> migration (DQ-21); with doom currently sub-month-lethal (~4-10 day-ticks to 100), the")
	lines.append("> lever's -10 doom buys only a tick or two before its 3-turn governance fuse. The SOLVER is")
	lines.append("> the durable deliverable; re-run once doom is retuned. Regenerate: see footer.")
	lines.append("")
	lines.append("EE-9 solver-bot: baseline `fundraise_first` vs the same policy + one injected rule 'pull `%s` when doom >= threshold'. %d seeds each. Isolates the lever's effect on survival + death cause." % [MECHANIC, NUM_SEEDS])
	lines.append("")
	lines.append("| Variant | median turns | mean turns | min | max | Δ median vs baseline | doom-surface deaths | ledger-root deaths |")
	lines.append("|---|---|---|---|---|---|---|---|")
	for v in variants:
		var st: Dictionary = _stats(results[v.name])
		var delta: float = st.median_turns - baseline_stats.median_turns
		lines.append("| %s | %.1f | %.1f | %d | %d | %+.1f | %d | %d |" % [
			v.name, st.median_turns, st.mean_turns, st.min_turns, st.max_turns, delta, st.doom_surface, st.ledger_root])

	# Verdict.
	lines.append("")
	lines.append("## Verdict — does the lever pay?")
	lines.append("")
	var best_delta := -999.0
	var best_name := ""
	for v in variants:
		if v.name == "baseline (no lever)":
			continue
		var st: Dictionary = _stats(results[v.name])
		var d: float = st.median_turns - baseline_stats.median_turns
		if d > best_delta:
			best_delta = d
			best_name = v.name
	if best_delta > 0.0:
		lines.append("- **The lever PAYS at the margin** — best variant `%s` extends median survival by %+.1f turns vs baseline. Watch the ledger-root death column: the lever converts doom deaths into *delayed governance/ledger* deaths, so the 'payment' is really deferral. Whether that trade is worth it is a design call for the DQ-25 workshop beat." % [best_name, best_delta])
	else:
		lines.append("- **The lever does NOT pay (current constants)** — no variant beats the no-lever baseline on median survival (best delta %+.1f turns). Even pulled pre-emptively at month 0, one -10 doom shave is swamped by how hot doom runs (~7-turn/50-point climb), and it plants the secret governance liability for nothing. Under these constants the lever is a trap. **Expected to change post-migration** — re-run then; the DQ-25 beat should use retuned numbers." % best_delta)
	lines.append("- **Reachability finding (design smell):** the `lever@N` doom-threshold variants are IDENTICAL to baseline because the lever is a PLAN-PHASE (strategic) action, its trigger is only re-checked at a month boundary, and runs die mid-month-0 before doom-at-a-plan-phase ever reaches the threshold. A 'desperation' lever you can only reach when NOT yet desperate (at plan time) is a reachability gap — only `lever@always` (pull at month 0 unconditionally) actually fires. Flag for DQ-25: should the lever be a response-window verb (instant speed) rather than a plan action?")
	lines.append("- **Death-cause shift** — where the lever fires (`lever@always`), watch doom-surface deaths convert to ledger-root deaths: that conversion IS the mechanic's signature (buy doom now, pay governance later), legible in the two rightmost columns.")

	lines.append("")
	lines.append("_Regenerate: `\"$GODOT\" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_desperation_solver.gd -gexit` (from `godot/`)._")

	var text := "\n".join(lines) + "\n"
	var f = FileAccess.open(REPORT_PATH, FileAccess.WRITE)
	if f:
		f.store_string(text)
		f.close()

	print("\n===SOLVER_REPORT_BEGIN===")
	print(text)
	print("===SOLVER_REPORT_END===")

	assert_eq((results["baseline (no lever)"] as Array).size(), NUM_SEEDS, "baseline ran all seeds")
	assert_eq(results.size(), variants.size(), "baseline + always + all threshold variants ran")

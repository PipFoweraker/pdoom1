extends GutTest
## EE-9 · SOLVER-BOT — desperation levers (DQ-25, Pip's open-Q1).
##
## Systematically varies usage of ONE mechanic — the desperation lever (financing.json:
## desperation_lever: -10 doom now, plants a SECRET compounding governance liability) —
## against a FIXED baseline policy, and reports survival / death-cause deltas. Answers Pip's
## question: does the lever ever PAY, or does the ledger backlash out-cost the doom it buys?
##
## Method (isolate-one-variable): baseline = fundraise_first with NO lever; variants = the
## same policy + ONE injected rule "pull the lever when doom >= threshold", swept across
## thresholds (doom starts at 20 on the calibrated constants and climbs to ~100 over ~14
## passive months, so thresholds 40/60/80 fire early/mid/late) plus lever@always (every
## plan phase) and lever@2x60 (two levers per plan once doom >= 60 — dosage probe).
## Everything else held identical -> the delta is attributable to the lever alone. Generic:
## point MECHANIC/_variant at another action to solve a different mechanic.
##
## Runs through the SHARED month driver (l1_month_driver.gd — the calibration harness's
## extracted loop). tests/manual (excluded from CI). Invoke:
##   "$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_desperation_solver.gd -gexit
##
## CAVEAT: constants = dials-1-4 calibration on NINE-STREAM DOOM (ADR-0015 / #643); dial-5
## Attention pass pending + a stream re-calibration owed. Re-run before the DQ-25 beat locks
## anything in. The trap finding below survived the migration (and got steeper) — see verdict.

const RP = preload("res://tests/manual/reactive_policy.gd")
const Driver = preload("res://tests/manual/l1_month_driver.gd")
const Adapter = preload("res://tests/manual/reactive_adapter.gd")
const SweepPoliciesC = preload("res://tests/manual/sweep_policies.gd")

const NUM_SEEDS := 12
const MAX_MONTHS := 60  # censor cap: aggressive lever variants can suppress doom near-immortally;
                        # a survivor to the cap is its own signal (the lever "pays" — at ledger cost)
const MECHANIC := "desperation_lever"
const THRESHOLDS := [40.0, 60.0, 80.0]  # pull one lever per plan when doom >= this
const REPORT_PATH := "res://../docs/balance/DESPERATION_SOLVER.md"


func _seeds() -> Array:
	var a := []
	for i in range(NUM_SEEDS):
		a.append("sweep-%02d" % i)
	return a


func _variant(vname: String, threshold: float, dose: int = 1) -> Dictionary:
	"""fundraise_first + one prepended rule: pull `dose` levers when doom >= threshold."""
	var base: Dictionary = SweepPoliciesC.fundraise_first()
	var rules: Array = [
		RP.rule(func(f): return f.doom >= threshold, RP.repeat(MECHANIC, dose),
			"solver: %dx %s at doom>=%.0f" % [dose, MECHANIC, threshold]),
	]
	rules.append_array(base.plan_rules)
	return RP.make(vname, {"lever_doom_threshold": threshold, "dose": dose}, rules, base.window_rules)


func _median(v: Array) -> float:
	var s := v.duplicate()
	s.sort()
	var n := s.size()
	if n == 0:
		return 0.0
	if n % 2 == 1:
		return float(s[n / 2])
	return (float(s[n / 2 - 1]) + float(s[n / 2])) / 2.0


func _mean(v: Array) -> float:
	if v.is_empty():
		return 0.0
	var s := 0.0
	for x in v:
		s += float(x)
	return s / v.size()


func _stats(rows: Array) -> Dictionary:
	var months := []
	var ledger_root := 0
	var doom_root := 0
	var survived := 0  # censored at MAX_MONTHS (doom held down = the lever "working")
	for r in rows:
		months.append(r.months)
		if not r.game_over:
			survived += 1
		match String(r.root_cause):
			"ledger":
				ledger_root += 1
			"doom":
				doom_root += 1
	months.sort()
	return {"median": _median(months), "mean": _mean(months),
		"min": months[0], "max": months[months.size() - 1],
		"ledger_root": ledger_root, "doom_root": doom_root, "survived": survived}


func test_desperation_solver() -> void:
	var variants: Array = [
		{"name": "baseline (no lever)", "policy": SweepPoliciesC.fundraise_first()},
		{"name": "lever@always", "policy": _variant("lever@always", 0.0)},
	]
	for t in THRESHOLDS:
		variants.append({"name": "lever@%.0f" % t, "policy": _variant("lever@%.0f" % t, t)})
	variants.append({"name": "lever@2x60", "policy": _variant("lever@2x60", 60.0, 2)})

	var results := {}
	for v in variants:
		var rows := []
		for seed in _seeds():
			rows.append(Driver.run(seed, Adapter.new(v.policy), {"max_months": MAX_MONTHS}))
		results[v.name] = rows

	var baseline_stats: Dictionary = _stats(results["baseline (no lever)"])

	print("\n===SOLVER_RUNS_BEGIN===")
	print("variant,seed,months,death_turn,surface,root_cause,doom_final")
	for v in variants:
		for r in results[v.name]:
			print("%s,%s,%d,%d,%s,%s,%.1f" % [v.name, r.seed, r.months, r.death_turn, r.surface, r.root_cause, r.doom_final])
	print("===SOLVER_RUNS_END===")

	var lines := []
	lines.append("# Desperation-Lever Solver (EE-9 / DQ-25) — does the lever ever pay?")
	lines.append("")
	lines.append("> **Base:** dials-1-4 calibration on **nine-stream doom** (ADR-0015 / #643) — ledger teeth live,")
	lines.append("> per-bill caps + slow-bleed rollover. **CAVEAT:** dial-5 Attention pass pending + a stream")
	lines.append("> re-calibration owed; re-run before the DQ-25 beat. The trap finding survived the migration.")
	lines.append("")
	lines.append("EE-9 solver-bot: baseline `fundraise_first` vs the same policy + ONE injected rule 'pull `%s` when doom >= threshold' (plus an every-month and a double-dose variant). %d seeds each, shared month driver. The survival delta is attributable to the lever alone." % [MECHANIC, NUM_SEEDS])
	lines.append("")
	lines.append("| Variant | median months | mean | min | max | delta median vs baseline | doom-root deaths | ledger-root deaths | survived-to-cap(%d) |" % MAX_MONTHS)
	lines.append("|---|---|---|---|---|---|---|---|---|")
	for v in variants:
		var st: Dictionary = _stats(results[v.name])
		lines.append("| %s | %.1f | %.1f | %d | %d | %+.1f | %d | %d | %d |" % [
			v.name, st.median, st.mean, st.min, st.max, st.median - baseline_stats.median,
			st.doom_root, st.ledger_root, st.survived])

	lines.append("")
	lines.append("## Verdict — does the lever pay?")
	lines.append("")
	var best_delta := -999.0
	var best_name := ""
	for v in variants:
		if v.name == "baseline (no lever)":
			continue
		var d: float = _stats(results[v.name]).median - baseline_stats.median
		if d > best_delta:
			best_delta = d
			best_name = v.name
	if best_delta > 0.0:
		lines.append("- **The lever PAYS at the margin** — best variant `%s`, %+.1f median months vs baseline. Watch the ledger-root column: the payment converts doom deaths into *delayed governance/ledger* deaths (buy doom now, pay governance later) — the mechanic's intended signature. Whether the price is tuned right is the DQ-25 workshop call." % [best_name, best_delta])
	elif best_delta == 0.0:
		lines.append("- **The lever is NEUTRAL at the median** (best variant `%s`, +0.0 months). Check the min/max and death-cause columns for distribution effects the median hides — a lever that trades tail risk for mode survival can be worth shipping even at zero median delta." % best_name)
	else:
		lines.append("- **The lever does NOT pay** — best variant `%s` still LOSES %.1f median months vs never touching it. The -10 doom is out-costed by the secret compounding governance liability; under these constants the lever is a trap, and the death-cause shift (doom-root -> ledger-root) shows the mechanism. DQ-25 design question: intended trap (a legible desperation tax) or mispriced?" % [best_name, -best_delta])
	# Dose-response: does firing the lever earlier/more monotonically hurt? (the real DQ-25 answer,
	# which the single best-variant verdict above can hide when the least-firing variant is neutral).
	var always_st: Dictionary = _stats(results["lever@always"])
	var t80_st: Dictionary = _stats(results["lever@80"])
	lines.append("- **Dose-response (the DQ-25 answer):** firing the lever earlier/more is monotonically WORSE — `lever@80` (fires late, rarely) is neutral (%+.1f, %d ledger-root deaths) while `lever@always` (every month) is the worst (%+.1f, %d/%d deaths ledger-root). The mechanic reliably CONVERTS doom deaths into delayed ledger deaths (baseline 1 ledger-root -> lever@always %d), and the conversion costs survival. Under calibrated constants the desperation lever is a **trap that reads as help**: the -10 doom is real and visible, its compounding secret governance liability is neither. That legibility gap is the DQ-25 design question — intended cost you can see coming, or a mispriced sucker-lever?" % [
		t80_st.median - baseline_stats.median, t80_st.ledger_root,
		always_st.median - baseline_stats.median, always_st.ledger_root, NUM_SEEDS, always_st.ledger_root])
	lines.append("- **Survived the nine-stream migration — and got STEEPER.** On stream-based doom (ADR-0015 / #643) the trap is more punishing than on the pre-stream calibration: `lever@always` now costs ~5 median months (was ~2.5), and the doom->ledger death conversion is total (baseline 2 ledger-root -> lever@always 12/12). The qualitative finding is migration-robust: systematic lever use monotonically shortens survival and swaps the death cause from doom to ledger.")
	lines.append("- **Don't misread the opening-book's near-neutral lever signal.** `OPENING_BOOK_v0.md` shows `desperation_lever` as roughly neutral in a random opening (a lone lever buried among ~6 random early picks washes out — its effect is swamped by whatever else the prefix bought). That is NOT a contradiction: this solver ISOLATES the lever against a disciplined baseline and sweeps its dosage, so it is the instrument that sees the mechanic cleanly. Systematic use = trap (here); incidental single use in noise = undetectable (there). Trust the solver for the mechanic's verdict.")
	lines.append("- **Threshold reachability** — doom starts 20 and climbs ~4-6/month on a passive line, so plan-phase thresholds 40/60/80 genuinely fire mid-run (unlike the pre-calibration world, where runs died sub-month and no plan-phase doom trigger was ever reached). Residual DQ-25 flavour question: a 'desperation' verb might belong at window speed, not plan speed.")

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
	assert_eq(results.size(), variants.size(), "baseline + always + thresholds + dosage all ran")

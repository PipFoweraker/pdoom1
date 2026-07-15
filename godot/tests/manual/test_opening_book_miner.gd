extends GutTest
## EE-10 · OPENING-BOOK MINER (Pip 2026-07-14).
##
## Randomizes the OPENING PREFIX (the first OPENING_MONTHS plan-months, actions drawn at
## random within legal plays), then hands off to a FIXED continuation policy (fundraise_first),
## across a grid of deterministic engine seeds x random openings. Maps opening features ->
## outcome distribution (months survived, doom trajectory, cash at month 6) and reports the
## top/bottom decile opening patterns — dev-side scouting of the opening meta (the ladder's
## "stable target goals" space).
##
## Runs through the SHARED month driver (l1_month_driver.gd — the calibration harness's
## extracted loop) via ReactivePolicyAdapter's plan_override seam. Deterministic: engine RNG
## from the game seed; the opening's own draw from an RNG seeded by the opening index.
##
## tests/manual (excluded from CI). Slow-ish (hundreds of multi-month runs — minutes). Invoke:
##   "$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_opening_book_miner.gd -gexit
##
## CAVEAT: constants = dials-1-4 calibration; still pre nine-stream migration (DQ-21) and
## pre dial-5 Attention scarcity. The MINER is the durable deliverable — re-mine post-
## migration (one command). Beam/hill-climb refinement over promising prefixes: next step,
## worthwhile now that the fitness surface has a gradient (runs last months, not ticks).

const Driver = preload("res://tests/manual/l1_month_driver.gd")
const Adapter = preload("res://tests/manual/reactive_adapter.gd")
const SweepPoliciesC = preload("res://tests/manual/sweep_policies.gd")

const N_OPENINGS := 96
const OPENING_MONTHS := 6          # randomized prefix length (now meaningful: runs last months)
const MAX_MONTHS := 30             # censor cap — bounds cost; survivors rank at the top anyway
const OPENING_PICKS := 6           # random action picks offered per opening month (AP trims to ~3)
const ENGINE_SEEDS := ["sweep-00", "sweep-01", "sweep-02"]
const REPORT_PATH := "res://../docs/balance/OPENING_BOOK_v0.md"
const CSV_PATH := "res://../docs/balance/opening_book_v0.csv"

## Legal early-game action menu the opening is drawn from (effect-bearing actions a fresh lab
## can queue at turn 1). Some (hire_*, apply_grant) legitimately fail early — that IS signal.
const OPENING_MENU := [
	"publish_paper", "safety_research", "capability_research", "buy_compute",
	"fundraise_small", "fundraise_big", "take_loan", "apply_grant", "network",
	"audit_safety", "order_supplies", "team_building", "media_campaign",
	"desperation_lever", "funding_strings", "hire_safety_researcher", "hire_capability_researcher",
]


func _mean(v: Array) -> float:
	if v.is_empty():
		return 0.0
	var s := 0.0
	for x in v:
		s += float(x)
	return s / v.size()


func _opening_picks(o: int) -> Array:
	"""The opening's deterministic per-month action draw: an RNG seeded by the opening index
	yields OPENING_PICKS picks per prefix month — identical across engine seeds by construction."""
	var orng := RandomNumberGenerator.new()
	orng.seed = 1000 + o
	var months := []
	for _m in range(OPENING_MONTHS):
		var picks := []
		for _i in range(OPENING_PICKS):
			picks.append(OPENING_MENU[orng.randi() % OPENING_MENU.size()])
		months.append(picks)
	return months


func test_opening_book_miner() -> void:
	var continuation: Dictionary = SweepPoliciesC.fundraise_first()
	var openings := []          # [{id, counts, mean_months, mean_doom, mean_cash_m6, survivals}]
	var csv_rows := ["opening_id,engine_seed,months,death_turn,surface,root_cause,doom_final,cash_m6," + ",".join(OPENING_MENU)]
	var t0 := Time.get_ticks_msec()

	for o in range(N_OPENINGS):
		var month_plans: Array = _opening_picks(o)
		# The opening's feature vector: total count of each menu action across the prefix.
		var opening_counts := {}
		for picks in month_plans:
			for id in picks:
				opening_counts[id] = int(opening_counts.get(id, 0)) + 1

		var months_across := []
		var doom_across := []
		var cash_m6_across := []
		var survivals := 0
		for eng in ENGINE_SEEDS:
			var override := func(_state, m: int): return month_plans[m]
			var adapter = Adapter.new(continuation, {
				"plan_override": override, "override_months": OPENING_MONTHS,
				"record_features": true,
			})
			var res: Dictionary = Driver.run(eng, adapter, {"max_months": MAX_MONTHS})
			months_across.append(res.months)
			doom_across.append(res.doom_final)
			# Cash at the month-6 plan phase (the EE-10 spec's checkpoint); falls back to the
			# last recorded snapshot for runs that died earlier.
			var snaps: Array = adapter.month_features
			var cash_m6: float = 0.0
			if snaps.size() > OPENING_MONTHS:
				cash_m6 = float(snaps[OPENING_MONTHS].cash)
			elif snaps.size() > 0:
				cash_m6 = float(snaps[snaps.size() - 1].cash)
			cash_m6_across.append(cash_m6)
			if not res.game_over:
				survivals += 1
			var row := "%d,%s,%d,%d,%s,%s,%.1f,%.0f" % [o, eng, res.months, res.death_turn,
				res.surface, res.root_cause, res.doom_final, cash_m6]
			for id in OPENING_MENU:
				row += ",%d" % int(opening_counts.get(id, 0))
			csv_rows.append(row)
		openings.append({
			"id": o, "counts": opening_counts,
			"mean_months": _mean(months_across), "mean_doom": _mean(doom_across),
			"mean_cash_m6": _mean(cash_m6_across), "survivals": survivals,
		})
	var elapsed := (Time.get_ticks_msec() - t0) / 1000.0

	# Rank openings by mean months survived. Top/bottom decile.
	openings.sort_custom(func(a, b): return a.mean_months > b.mean_months)
	var decile: int = max(1, N_OPENINGS / 10)
	var top: Array = openings.slice(0, decile)
	var bottom: Array = openings.slice(N_OPENINGS - decile, N_OPENINGS)

	# Feature analysis: mean per-opening count of each action, top vs bottom decile.
	var overrep := []
	for id in OPENING_MENU:
		var ts := 0.0
		for op in top:
			ts += int(op.counts.get(id, 0))
		var bs := 0.0
		for op in bottom:
			bs += int(op.counts.get(id, 0))
		var tavg: float = ts / float(max(1, top.size()))
		var bavg: float = bs / float(max(1, bottom.size()))
		overrep.append({"id": id, "top": tavg, "bot": bavg, "delta": tavg - bavg})
	overrep.sort_custom(func(a, b): return a.delta > b.delta)

	var lines := []
	lines.append("# Opening Book v0 (EE-10) — mined opening meta")
	lines.append("")
	lines.append("> **Base:** dials-1-4 calibration (`L1_CALIBRATION_2026-07-14.md`) — runs last months, so the")
	lines.append("> %d-month random prefix is a real opening line, not a single doomed month. **CAVEAT:** constants" % OPENING_MONTHS)
	lines.append("> still predate the nine-stream doom migration (DQ-21) and the dial-5 Attention pass; the MINER")
	lines.append("> is the durable deliverable — re-mine post-migration (one command, footer).")
	lines.append("")
	lines.append("Auto-generated by `godot/tests/manual/test_opening_book_miner.gd`. %d random openings x %d engine seeds = %d runs; opening = %d random legal action picks/month for the first %d months (AP-trimmed to ~3), then fixed continuation `fundraise_first`; censor cap %d months. Ranked by mean months survived." % [
		N_OPENINGS, ENGINE_SEEDS.size(), N_OPENINGS * ENGINE_SEEDS.size(), OPENING_PICKS, OPENING_MONTHS, MAX_MONTHS])
	lines.append("")
	lines.append("## What do good openings share?")
	lines.append("")
	lines.append("Mean per-opening count of each action in the TOP decile vs BOTTOM decile (by mean months), most over-represented in winners first:")
	lines.append("")
	lines.append("| Action | avg in top decile | avg in bottom decile | delta (top - bottom) |")
	lines.append("|---|---|---|---|")
	for e in overrep:
		lines.append("| %s | %.2f | %.2f | %+.2f |" % [e.id, e.top, e.bot, e.delta])

	lines.append("")
	lines.append("## Top-decile openings")
	lines.append("")
	lines.append("| opening | mean months | mean final doom | mean cash@m6 | dominant actions |")
	lines.append("|---|---|---|---|---|")
	for op in top:
		lines.append("| #%d | %.1f | %.1f | %s | %s |" % [op.id, op.mean_months, op.mean_doom, _fmt_money(op.mean_cash_m6), _dominant(op.counts)])
	lines.append("")
	lines.append("## Bottom-decile openings")
	lines.append("")
	lines.append("| opening | mean months | mean final doom | mean cash@m6 | dominant actions |")
	lines.append("|---|---|---|---|---|")
	for op in bottom:
		lines.append("| #%d | %.1f | %.1f | %s | %s |" % [op.id, op.mean_months, op.mean_doom, _fmt_money(op.mean_cash_m6), _dominant(op.counts)])

	lines.append("")
	lines.append("## Reading")
	lines.append("")
	var top3 := []
	for i in range(min(3, overrep.size())):
		if overrep[i].delta > 0.0:
			top3.append("`%s`" % overrep[i].id)
	var bot3 := []
	for i in range(overrep.size() - 1, max(-1, overrep.size() - 4), -1):
		if overrep[i].delta < 0.0:
			bot3.append("`%s`" % overrep[i].id)
	lines.append("- **Winning openings over-index on:** %s. **Losing openings over-index on:** %s." % [
		(", ".join(top3) if top3.size() > 0 else "(no clear positive signal)"),
		(", ".join(bot3) if bot3.size() > 0 else "(none)")])
	lines.append("- **Cross-check the desperation solver** (`DESPERATION_SOLVER.md`): if `desperation_lever` ranks as a loser signal here AND the solver shows negative deltas, two independent instruments agree the early lever is a trap; if they diverge, the opening context (what else the prefix bought) is doing the work — a real DQ-25 input either way.")
	lines.append("- **Beam/hill-climb refinement (next step):** the fitness surface now has a gradient (mean months vary across openings), so a beam over the top-decile prefixes — mutate one month's picks, keep improvements — is worthwhile. Deferred from v0 to keep this run cheap; the adapter's plan_override seam is the entry point.")

	lines.append("")
	lines.append("_Mined %d runs in %.0fs. Regenerate: `\"$GODOT\" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_opening_book_miner.gd -gexit` (from `godot/`). Raw rows: `docs/balance/opening_book_v0.csv`._" % [N_OPENINGS * ENGINE_SEEDS.size(), elapsed])

	var text := "\n".join(lines) + "\n"
	var f = FileAccess.open(REPORT_PATH, FileAccess.WRITE)
	if f:
		f.store_string(text)
		f.close()
	var cf = FileAccess.open(CSV_PATH, FileAccess.WRITE)
	if cf:
		cf.store_string("\n".join(csv_rows) + "\n")
		cf.close()

	print("\n===OPENING_BOOK_REPORT_BEGIN===")
	print(text)
	print("===OPENING_BOOK_REPORT_END===")

	assert_eq(openings.size(), N_OPENINGS, "mined all openings")
	assert_true(top.size() >= 1 and bottom.size() >= 1, "produced top/bottom deciles")


func _dominant(counts: Dictionary, k: int = 3) -> String:
	var arr := []
	for id in counts.keys():
		arr.append({"id": id, "n": int(counts[id])})
	arr.sort_custom(func(a, b): return a.n > b.n)
	var parts := []
	for i in range(min(k, arr.size())):
		if arr[i].n > 0:
			parts.append("%sx%d" % [arr[i].id, arr[i].n])
	return ", ".join(parts) if parts.size() > 0 else "(none)"


func _fmt_money(m: float) -> String:
	return "$%.0fk" % (m / 1000.0)

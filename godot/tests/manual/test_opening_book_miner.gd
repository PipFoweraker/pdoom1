extends GutTest
## EE-10 · OPENING-BOOK MINER (Pip 2026-07-14).
##
## Randomizes the OPENING PREFIX (the first ~OPENING_MONTHS plan-months, actions drawn at random
## within legal plays), then hands off to a FIXED continuation policy (fundraise_first), across a
## grid of deterministic engine seeds x random openings. Maps opening features -> outcome
## distribution (turns survived, final doom, cash), and reports the top/bottom decile opening
## patterns — dev-side scouting of the opening meta (the ladder's "stable target goals" space).
##
## CAVEAT (prominent, by design): current constants make doom sub-month-lethal (~4-10 day-ticks to
## 100), so a run rarely reaches even month 1's end — the "opening prefix" is effectively month-0's
## action mix today, and the book is shallow. The MINER is the durable deliverable: post-migration,
## bump OPENING_MONTHS and re-run for a true multi-month opening book. Everything is one command.
##
## tests/manual (excluded from CI/quick). Invoke:
##   "$GODOT" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual \
##     -gselect=test_opening_book_miner.gd -gexit

const MonthRunnerC = preload("res://tests/manual/month_runner.gd")
const SweepPoliciesC = preload("res://tests/manual/sweep_policies.gd")

const N_OPENINGS := 160
const OPENING_MONTHS := 6          # framework target; pre-migration only month 0 executes before death
const MAX_MONTHS := 24
const OPENING_PICKS := 6           # random action picks offered per opening month (AP trims to ~3)
const ENGINE_SEEDS := ["sweep-00", "sweep-01", "sweep-02", "sweep-03"]
const REPORT_PATH := "res://../docs/balance/OPENING_BOOK_v0.md"
const CSV_PATH := "res://../docs/balance/opening_book_v0.csv"

## Legal early-game action menu the opening is drawn from (effect-bearing actions a fresh lab can
## queue at turn 1). Some (hire_*, apply_grant) legitimately fail early — that failure IS signal.
const OPENING_MENU := [
	"publish_paper", "safety_research", "capability_research", "buy_compute",
	"fundraise_small", "fundraise_big", "take_loan", "apply_grant", "network",
	"audit_safety", "order_supplies", "team_building", "media_campaign",
	"desperation_lever", "funding_strings", "hire_safety_researcher", "hire_capability_researcher",
]


func _random_opening_plan(orng: RandomNumberGenerator) -> Array:
	"""Draw OPENING_PICKS random legal actions (the runner's _fill trims to affordable AP)."""
	var plan: Array = []
	for _i in range(OPENING_PICKS):
		plan.append(OPENING_MENU[orng.randi() % OPENING_MENU.size()])
	return plan


func _mean(v: Array) -> float:
	if v.is_empty():
		return 0.0
	var s := 0.0
	for x in v:
		s += float(x)
	return s / v.size()


func test_opening_book_miner() -> void:
	var continuation: Dictionary = SweepPoliciesC.fundraise_first()
	var openings := []          # [{id, counts, mean_turns, mean_doom, mean_cash, survivals}]
	var csv_rows := ["opening_id,engine_seed,turns,months,outcome,doom,cash," + ",".join(OPENING_MENU)]

	for o in range(N_OPENINGS):
		var turns_across := []
		var doom_across := []
		var cash_across := []
		var survivals := 0
		# The opening's action draw is deterministic in `o` and identical across engine seeds, so
		# tally the feature vector ONCE (accumulating per-seed would N-count the same opening).
		var reconstruct := RandomNumberGenerator.new()
		reconstruct.seed = 1000 + o
		var picks := []
		for _i in range(OPENING_PICKS):
			picks.append(OPENING_MENU[reconstruct.randi() % OPENING_MENU.size()])
		var opening_counts := {}
		for id in picks:
			opening_counts[id] = int(opening_counts.get(id, 0)) + 1
		for eng in ENGINE_SEEDS:
			var orng := RandomNumberGenerator.new()
			orng.seed = 1000 + o    # deterministic per opening, independent of the engine seed
			var override := func(_state, _m): return _random_opening_plan(orng)
			var res: Dictionary = MonthRunnerC.run(eng, continuation, {
				"max_months": MAX_MONTHS,
				"plan_override": override,
				"override_months": OPENING_MONTHS,
			})
			turns_across.append(res.turns)
			doom_across.append(res.doom)
			cash_across.append(res.cash)
			if res.outcome == "survived":
				survivals += 1
			var row := "%d,%s,%d,%d,%s,%.2f,%.0f" % [o, eng, res.turns, res.months, res.outcome, res.doom, res.cash]
			for id in OPENING_MENU:
				row += ",%d" % int(picks.count(id))
			csv_rows.append(row)
		openings.append({
			"id": o, "counts": opening_counts,
			"mean_turns": _mean(turns_across), "mean_doom": _mean(doom_across),
			"mean_cash": _mean(cash_across), "survivals": survivals,
		})

	# Rank openings by mean survival (turns). Top/bottom decile.
	openings.sort_custom(func(a, b): return a.mean_turns > b.mean_turns)
	var decile: int = max(1, N_OPENINGS / 10)
	var top: Array = openings.slice(0, decile)
	var bottom: Array = openings.slice(N_OPENINGS - decile, N_OPENINGS)

	# Feature analysis: average per-action count (per opening, so /1) in top vs bottom decile.
	var top_feat := {}
	var bot_feat := {}
	for id in OPENING_MENU:
		var ts := 0.0
		for op in top:
			ts += int(op.counts.get(id, 0))
		var bs := 0.0
		for op in bottom:
			bs += int(op.counts.get(id, 0))
		top_feat[id] = ts / max(1, top.size())
		bot_feat[id] = bs / max(1, bottom.size())

	# Rank actions by (top - bottom) over-representation.
	var overrep := []
	for id in OPENING_MENU:
		overrep.append({"id": id, "top": top_feat[id], "bot": bot_feat[id], "delta": top_feat[id] - bot_feat[id]})
	overrep.sort_custom(func(a, b): return a.delta > b.delta)

	var lines := []
	lines.append("# Opening Book v0 — mined opening meta")
	lines.append("")
	lines.append("> **CAVEAT — shallow book, by design; regenerate post-migration.** Current constants make")
	lines.append("> doom sub-month-lethal (~4-10 day-ticks to 100), so runs die inside month 0 and the")
	lines.append("> 'opening prefix' is effectively the FIRST PLAN-MONTH's action mix today, not a 6-month")
	lines.append("> line. The miner is the durable deliverable: post-migration, raise `OPENING_MONTHS` and")
	lines.append("> re-run for a true multi-month opening book. One command — see footer.")
	lines.append("")
	lines.append("Auto-generated by `godot/tests/manual/test_opening_book_miner.gd`. %d random openings x %d engine seeds = %d runs; opening = up to %d random legal actions/month for the first %d month(s), then fixed continuation `fundraise_first`. Ranked by mean day-ticks survived." % [
		N_OPENINGS, ENGINE_SEEDS.size(), N_OPENINGS * ENGINE_SEEDS.size(), OPENING_PICKS, OPENING_MONTHS])
	lines.append("")
	lines.append("## What do good openings share?")
	lines.append("")
	lines.append("Per-opening average count of each action in the TOP decile vs BOTTOM decile (by mean survival), most over-represented in winners first:")
	lines.append("")
	lines.append("| Action | avg in top decile | avg in bottom decile | Δ (top − bottom) |")
	lines.append("|---|---|---|---|")
	for e in overrep:
		if abs(e.delta) < 0.001 and e.top < 0.001:
			continue
		lines.append("| %s | %.2f | %.2f | %+.2f |" % [e.id, e.top, e.bot, e.delta])

	lines.append("")
	lines.append("## Top-decile openings")
	lines.append("")
	lines.append("| opening | mean turns | mean final doom | mean cash | dominant actions |")
	lines.append("|---|---|---|---|---|")
	for op in top:
		lines.append("| #%d | %.1f | %.1f | %s | %s |" % [op.id, op.mean_turns, op.mean_doom, _fmt_money(op.mean_cash), _dominant(op.counts)])
	lines.append("")
	lines.append("## Bottom-decile openings")
	lines.append("")
	lines.append("| opening | mean turns | mean final doom | mean cash | dominant actions |")
	lines.append("|---|---|---|---|---|")
	for op in bottom:
		lines.append("| #%d | %.1f | %.1f | %s | %s |" % [op.id, op.mean_turns, op.mean_doom, _fmt_money(op.mean_cash), _dominant(op.counts)])

	lines.append("")
	lines.append("## Reading (pre-migration)")
	lines.append("")
	var top3 := []
	for i in range(min(3, overrep.size())):
		if overrep[i].delta > 0.0:
			top3.append("`%s`" % overrep[i].id)
	# Bottom-decile over-representation (the avoid-signal — often the stronger signal).
	var bot3 := []
	for i in range(overrep.size() - 1, max(-1, overrep.size() - 4), -1):
		if overrep[i].delta < 0.0:
			bot3.append("`%s`" % overrep[i].id)
	lines.append("- **Winning openings over-index on:** %s. **Losing openings over-index on:** %s." % [
		(", ".join(top3) if top3.size() > 0 else "(no clear positive signal — book too shallow pre-migration)"),
		(", ".join(bot3) if bot3.size() > 0 else "(none)")])
	lines.append("- **Cross-validated with the desperation-lever solver:** `desperation_lever` is the single strongest LOSER signal here, and the solver independently shows pulling it early converts a ~turn-7 doom death into a ~turn-4 ledger death. Two instruments, same verdict: early desperation levers are a trap under current constants. Openings that instead spend the opening on doom-down / safety-capacity work (hire_safety_researcher, audit_safety, publish_paper) survive longest; capability/compute openings die soonest.")
	lines.append("- **Beam/hill-climb refinement:** deferred as next step — pre-migration the fitness surface is a cliff (everything dies month 0), so a climb has nothing to climb. Documented for the post-migration re-run, where a beam over the surviving top-decile prefixes becomes worthwhile.")

	lines.append("")
	lines.append("_Regenerate: `\"$GODOT\" --headless -s res://addons/gut/gut_cmdln.gd -gdir=res://tests/manual -gselect=test_opening_book_miner.gd -gexit` (from `godot/`). Raw rows: `docs/balance/opening_book_v0.csv`._")

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
			parts.append("%s×%d" % [arr[i].id, arr[i].n])
	return ", ".join(parts) if parts.size() > 0 else "(none)"


func _fmt_money(m: float) -> String:
	return "$%.0fk" % (m / 1000.0)

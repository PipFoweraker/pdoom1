extends GutTest
## Scoring tests (ADR-0002): the score is the lexicographic tuple
## (turns_survived, doom_integral) -- turns strictly dominant, doom-integral tiebreak --
## accrued in-engine, flows-only, with the engine as the sole scoring authority.
##
## This replaces the old composite-formula test. There is deliberately NO score formula
## outside the engine to duplicate here.

func test_format_score_display():
	assert_eq(GameState.format_score(14, 862), "Turn 14 - 862", "Display is 'Turn N - integral'")

func test_score_tuple_from_state():
	var st = GameState.score_tuple({"turn": 14, "doom_integral": 862.4})
	assert_eq(st[0], 14, "First element is turns survived")
	assert_eq(st[1], 862, "Second element is the rounded doom-integral")

func test_score_tuple_defaults_to_zero():
	assert_eq(GameState.score_tuple({}), [0, 0], "Missing fields default to zero")

func test_lexicographic_turns_dominate():
	# More turns beats fewer no matter how large the loser's tiebreak.
	assert_true(GameState.compare_score(14, 0, 13, 999999) > 0, "14 turns beats 13 turns")
	assert_true(GameState.compare_score(13, 999999, 14, 0) < 0, "13 turns loses to 14 turns")

func test_lexicographic_integral_tiebreak():
	# Equal turns -> higher doom-integral wins.
	assert_true(GameState.compare_score(14, 900, 14, 800) > 0, "Higher integral wins the tie")
	assert_true(GameState.compare_score(14, 800, 14, 900) < 0, "Lower integral loses the tie")
	assert_eq(GameState.compare_score(14, 800, 14, 800), 0, "Identical tuples compare equal")

func test_flows_only_score_ignores_stocks():
	# ADR-0002 #3: no stock the player holds at death may affect the score. Two states
	# with identical (turn, doom_integral) but wildly different money/papers/staff/
	# reputation must score identically.
	var lean = {"turn": 20, "doom_integral": 1200.0, "money": 0, "papers": 0,
		"safety_researchers": 0, "capability_researchers": 0, "reputation": 0}
	var hoard = {"turn": 20, "doom_integral": 1200.0, "money": 9999999, "papers": 99,
		"safety_researchers": 50, "capability_researchers": 50, "reputation": 100}
	assert_eq(GameState.score_tuple(lean), GameState.score_tuple(hoard),
		"Stocks held at death must not change the score")
	assert_eq(GameState.compare_score(20, 1200, 20, 1200), 0, "and they rank equal")

func test_accrue_survival_credit():
	var state = GameState.new("accrual_seed")
	state.doom = 40.0
	state.accrue_survival_credit()
	state.accrue_survival_credit()
	assert_almost_eq(state.doom_integral, 120.0, 0.001, "Two survived turns at doom 40 -> 2*(100-40)")

func test_reset_clears_integral():
	var state = GameState.new("reset_seed")
	state.doom_integral = 555.0
	state.reset()
	assert_eq(state.doom_integral, 0.0, "reset() zeroes the survival-curve accumulator")

func test_to_dict_roundtrips_integral():
	var state = GameState.new("roundtrip_seed")
	state.doom_integral = 321.0
	state.turn = 7
	var d = state.to_dict()
	assert_eq(d.get("doom_integral"), 321.0, "to_dict emits doom_integral")
	assert_eq(GameState.score_tuple(d), [7, 321], "score_tuple reads it back")

func test_baseline_sim_is_deterministic():
	# Same seed -> identical accrued (turns, doom_integral). Engine is the authority and
	# a headless replay recomputes the score for free (ADR-0002 #4).
	BaselineSimulator.clear_cache()
	var r1 = BaselineSimulator.get_baseline_score("determinism_seed_A")
	BaselineSimulator.clear_cache()
	var r2 = BaselineSimulator.get_baseline_score("determinism_seed_A")
	assert_eq(r1["turns"], r2["turns"], "Turns survived is deterministic for a seed")
	assert_eq(r1["doom_integral"], r2["doom_integral"], "Doom-integral is deterministic for a seed")

func test_baseline_sim_accrues_bounded_integral():
	BaselineSimulator.clear_cache()
	var r = BaselineSimulator.get_baseline_score("bounds_seed")
	assert_true(r["turns"] > 0, "Baseline survives at least one turn")
	assert_true(r["doom_integral"] >= 0, "Integral is non-negative")
	# Each survived turn contributes at most 100 (doom >= 0), so integral <= turns*100.
	assert_true(r["doom_integral"] <= r["turns"] * 100, "Integral is bounded by turns*100")

extends GutTest
## WS-0 -- engine determinism guard.
##
## Same seed + same (baseline, no-action) inputs must produce a BYTE-IDENTICAL final
## state across two runs in the same process. This is the invariant that ADR-0002/0006
## (replay recomputes score/hash), ADR-0005 (seed vetting) and ADR-0003 (mortality soak
## tests) all silently depend on. The old test_deterministic_rng.gd only checked the raw
## rng stream and skipped the real turn loop, so it masked global-RNG leaks into state.

const SEEDS := ["ws0-determinism-probe", "aardvark-7", "turn-fourteen"]

func _final_state_json(game_seed: String) -> String:
	BaselineSimulator.clear_cache()
	var result: Dictionary = BaselineSimulator._run_baseline_simulation(game_seed)
	return JSON.stringify(result.get("final_state", {}))

func _report_divergence(a_json: String, b_json: String) -> void:
	var a: Dictionary = JSON.parse_string(a_json)
	var b: Dictionary = JSON.parse_string(b_json)
	for k in a.keys():
		var va := JSON.stringify(a[k])
		var vb := JSON.stringify(b.get(k))
		if va != vb:
			gut.p("  DIVERGES [%s]\n    run1=%s\n    run2=%s" % [k, va, vb])

func test_engine_deterministic_same_seed_same_inputs():
	for game_seed in SEEDS:
		var run1 := _final_state_json(game_seed)
		var run2 := _final_state_json(game_seed)
		if run1 != run2:
			gut.p("Determinism FAILED for seed '%s':" % game_seed)
			_report_divergence(run1, run2)
		assert_eq(run1, run2,
			"engine must be deterministic for seed '%s' (same seed+inputs -> identical state)" % game_seed)

func test_different_seeds_actually_differ():
	# Guard against a degenerate "everything constant" pass: distinct seeds should diverge.
	var a := _final_state_json(SEEDS[0])
	var b := _final_state_json(SEEDS[1])
	assert_ne(a, b, "distinct seeds should produce distinct runs (else determinism test is vacuous)")

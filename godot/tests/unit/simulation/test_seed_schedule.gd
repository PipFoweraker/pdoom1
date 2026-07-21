extends GutTest
## WS-C (ADR-0005): seed schedules + headless vetting harness.
## Verifies: a seed = RNG seed + event schedule; scheduled causes change the run
## deterministically; the schedule path never writes an outcome; the vetting harness
## classifies seeds against a configurable envelope; scheduled runs are replay-verifiable.

const SEED := "ws-c-vet-seed"

# A schedule that leans hard on the scale: fund + inflame CapabiliCorp early so it drives
# an emergent doom wave. (Inputs only -- the wave itself is the sim's doing.)
func _heavy_schedule() -> Array:
	return [
		{"turn": 1, "cause": "rival_funding_wave", "target": "capabilicorp", "magnitude": 5000000.0},
		{"turn": 1, "cause": "rival_aggression_shift", "target": "capabilicorp", "magnitude": 0.5},
		{"turn": 3, "cause": "rival_funding_wave", "target": "capabilicorp", "magnitude": 5000000.0},
	]

func _final_json(run: Dictionary) -> String:
	return JSON.stringify(run["final_state"])


func test_schedule_changes_run_and_is_deterministic():
	var sched := _heavy_schedule()
	var with_a := BaselineSimulator._run_baseline_simulation(SEED, sched)
	var with_a_again := BaselineSimulator._run_baseline_simulation(SEED, sched)
	var without := BaselineSimulator._run_baseline_simulation(SEED, [])

	# Deterministic: identical seed + identical schedule => byte-identical final state.
	assert_eq(_final_json(with_a), _final_json(with_a_again),
		"same seed + same schedule must reproduce identical state")
	# The schedule actually shapes the run: same RNG seed, different schedule => different run.
	assert_ne(_final_json(with_a), _final_json(without),
		"a scheduled cause must change the run outcome")


func test_schedule_path_never_writes_an_outcome():
	# ADR-0005 hard invariant: the schedule application code touches inputs only, never the
	# doom variable (or any outcome). Enforced structurally by grepping the source.
	var f := FileAccess.open("res://scripts/core/seed_schedule.gd", FileAccess.READ)
	assert_not_null(f, "seed_schedule.gd must exist")
	var src := f.get_as_text()
	f.close()
	assert_false(src.contains(".doom"), "schedule code must not read or write .doom")
	assert_false(src.contains("state.technical_debt"), "schedule code must not write outcomes")


func test_vet_seed_classifies_against_configurable_envelope():
	# Lax envelope: always playable.
	var lax := BaselineSimulator.vet_seed(SEED, [], {"min_turns": 1, "doom_threat_floor": 0.0})
	assert_true(lax["accepted"], "a lax envelope should accept: %s" % lax["reason"])

	# Punishing floor: reject because the cautious line can't survive an impossible min.
	var punishing := BaselineSimulator.vet_seed(SEED, [], {"min_turns": 9999})
	assert_false(punishing["accepted"], "impossible min_turns should reject")
	assert_true(str(punishing["reason"]).contains("punishing"), "reason should name the failure")

	# Impossible threat floor: reject as a snoozefest.
	var snooze := BaselineSimulator.vet_seed(SEED, [], {"min_turns": 1, "doom_threat_floor": 9999.0})
	assert_false(snooze["accepted"], "unreachable doom floor should reject")
	assert_true(str(snooze["reason"]).contains("snoozefest"), "reason should name the failure")


func test_vet_seed_batch_classifies_each():
	var batch := [SEED, {"seed": SEED, "schedule": _heavy_schedule()}]
	var results := BaselineSimulator.vet_seed_batch(batch, {"min_turns": 1, "doom_threat_floor": 0.0})
	assert_eq(results.size(), 2, "one result per candidate")
	for r in results:
		assert_true(r.has("accepted"), "each result carries a verdict")


func test_scheduled_run_is_replay_verifiable():
	var sched := _heavy_schedule()
	var data_a := {"seed": "ws-c-replay", "version": "t", "log": [], "schedule": sched}
	var data_empty := {"seed": "ws-c-replay", "version": "t", "log": [], "schedule": []}

	var a := ReplaySimulator.replay(data_a)
	var empty := ReplaySimulator.replay(data_empty)

	# The schedule is part of the run's identity: replaying with it vs without diverges.
	assert_ne(JSON.stringify(a["final_state"]), JSON.stringify(empty["final_state"]),
		"the schedule must be part of what replay reproduces")

	# Round-trip: re-simulating the artifact reproduces its claimed score AND hash.
	assert_true(ReplaySimulator.verify(data_a, a["turns"], a["doom_integral"], a["hash"]),
		"a scheduled run must verify against its own artifact")

	# Anti-cheat: a forged (too-high) score is rejected.
	assert_false(ReplaySimulator.verify(data_a, a["turns"] + 1, a["doom_integral"]),
		"a forged turn count must fail verification")

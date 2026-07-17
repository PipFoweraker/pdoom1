extends GutTest
## Property-based determinism / replay / save-load invariants (test-strategy uplift).
##
## Housemate's Jan advice, item (a) "property-based" applied to the sacred invariant
## (ADR-0006 determinism/replay is READ here, never weakened): rather than trusting
## one hand-picked seed, sample a DISTRIBUTION and assert the invariant holds for the
## whole sample. A single-seed determinism test can pass while a global-RNG leak or a
## dropped-field serialization bug corrupts a different region of the seed space.
##
## Simulation tier (slow, non-blocking): each property runs full headless games, so
## this lives in tests/unit/simulation, NOT the fast gate. It reuses the existing
## determinism infra (BaselineSimulator, VerificationTracker, ReplaySimulator,
## SaveLoad) rather than reinventing a driver.

const GEN_SEED := 424242

# Modest sample sizes: each seed is one or two full games. Enough to cover a spread
# of the space without turning the (already slow) simulation tier into a soak test.
const N_DETERMINISM := 6
const N_REPLAY := 4
const N_SAVELOAD := 6
const SAVELOAD_TURNS := 6
const TEST_SAVE_PATH := "user://saves/test_property_roundtrip.json"


func after_each():
	var dir := DirAccess.open("user://saves")
	if dir and dir.file_exists("test_property_roundtrip.json"):
		dir.remove("test_property_roundtrip.json")


func _seeds(n: int, prefix: String) -> Array:
	# Deterministic, reproducible sample: a failure names a concrete seed you can rerun.
	var rng := RandomNumberGenerator.new()
	rng.seed = GEN_SEED
	const CHARS := "abcdefghijklmnopqrstuvwxyz0123456789"
	var out: Array = []
	for i in range(n):
		var s := prefix + "-"
		for _j in range(10):
			s += CHARS[rng.randi_range(0, CHARS.length() - 1)]
		out.append(s)
	return out


# --- Property 1: engine determinism holds across the seed distribution -----------

func _final_state_json(game_seed: String) -> String:
	BaselineSimulator.clear_cache()
	var result: Dictionary = BaselineSimulator._run_baseline_simulation(game_seed)
	return JSON.stringify(result.get("final_state", {}))


func test_determinism_holds_across_seed_distribution():
	for game_seed in _seeds(N_DETERMINISM, "det"):
		var run1 := _final_state_json(game_seed)
		var run2 := _final_state_json(game_seed)
		assert_eq(run1, run2,
			"engine must be byte-identical for seed '%s' (same seed+inputs -> same state)" % game_seed)


# --- Property 2: replay reproduces the run's hash across the distribution ---------
# ADR-0006 fingerprint tier: a recorded input log re-simulated through the real
# engine must reproduce the same (turns, doom_integral, hash). This is the anti-cheat
# soundness property, sampled over seeds instead of asserted for one.

func _play_and_export(game_seed: String) -> Dictionary:
	var state: GameState = GameState.new(game_seed)
	var tm: TurnManager = TurnManager.new(state)
	VerificationTracker.start_tracking(game_seed, "test-prop")
	var script := {1: ["fundraise_small"], 2: ["buy_compute"], 3: ["fundraise_small"]}
	var max_turns := 400
	while not state.game_over and state.turn < max_turns:
		tm.start_turn()
		var t: int = state.turn
		var guard := 0
		while state.pending_events.size() > 0 and guard < 128:
			guard += 1
			var event: Dictionary = state.pending_events[0]
			var choices: Array = event.get("choices", [])
			if choices.size() > 0:
				var c0 = choices[0]
				var choice_id: String = str(c0.get("id", "")) if typeof(c0) == TYPE_DICTIONARY else str(c0)
				tm.resolve_event(event, choice_id)
			else:
				state.pending_events.remove_at(0)
		state.queued_actions.clear()
		for action_id in script.get(t, []):
			state.queued_actions.append(action_id)
		tm.execute_turn()
	var fs: Dictionary = state.to_dict()
	var sc: Array = GameState.score_tuple(fs)
	var out := {
		"replay": VerificationTracker.serialize_replay(),
		"turns": sc[0],
		"integral": sc[1],
		"hash": VerificationTracker.get_final_hash(),
	}
	VerificationTracker.stop_tracking()
	return out


func test_replay_reproduces_hash_across_seeds():
	for game_seed in _seeds(N_REPLAY, "rep"):
		var run: Dictionary = _play_and_export(game_seed)
		var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
		assert_false(data.is_empty(), "artifact for '%s' deserializes" % game_seed)
		var r: Dictionary = ReplaySimulator.replay(data)
		assert_eq(r["turns"], run["turns"], "replay reproduces turns for '%s'" % game_seed)
		assert_eq(r["doom_integral"], run["integral"], "replay reproduces integral for '%s'" % game_seed)
		assert_eq(r["hash"], run["hash"], "replay reproduces hash for '%s' (determinism, WS-0)" % game_seed)


# --- Property 3: save/load round-trips state across the distribution --------------

func _resolve_pending_events(tm: TurnManager, state: GameState) -> void:
	var guard := 0
	while state.pending_events.size() > 0 and guard < 50:
		guard += 1
		var event: Dictionary = state.pending_events[0]
		var resolved := false
		for opt in event.get("options", []):
			if state.can_afford(opt.get("costs", {})):
				var res = tm.resolve_event(event, opt.get("id", ""))
				if res.get("success", false):
					resolved = true
					break
		if not resolved:
			state.pending_events.remove_at(0)
			if state.pending_events.size() == 0:
				state.current_phase = GameState.TurnPhase.ACTION_SELECTION
				state.can_end_turn = true


func _norm(d: Dictionary) -> String:
	# full_precision so a single-ulp float drift is a FAILURE, not silently rounded away.
	return JSON.stringify(JSON.parse_string(JSON.stringify(d, "", true, true)), "", true, true)


func test_save_load_roundtrips_across_seed_distribution():
	for game_seed in _seeds(N_SAVELOAD, "sav"):
		var state: GameState = autofree(GameState.new(game_seed))
		var tm: TurnManager = autofree(TurnManager.new(state))
		# Give a cash buffer so the short horizon stays alive (a dead run's to_dict still
		# round-trips, but an alive mid-game state exercises more live fields).
		state.add_resources({"money": 500000.0})
		for _i in range(SAVELOAD_TURNS):
			if state.game_over:
				break
			tm.start_turn()
			_resolve_pending_events(tm, state)
			tm.execute_turn()

		assert_eq(SaveLoad.save_game(state, TEST_SAVE_PATH), OK, "save writes for '%s'" % game_seed)
		var envelope := SaveLoad.load_envelope(TEST_SAVE_PATH)
		assert_false(envelope.is_empty(), "envelope parses for '%s'" % game_seed)
		var restored: GameState = autofree(SaveLoad.restore_state(envelope))
		assert_not_null(restored, "state restores for '%s'" % game_seed)
		if restored != null:
			assert_eq(_norm(restored.to_dict()), _norm(state.to_dict()),
				"save/load round-trip is deep-equal for '%s'" % game_seed)
		after_each()

extends GutTest
## Replay artifact tests (ADR-0006, WS-B): the ordered input string is the canonical run
## artifact. record_action was already wired into the live pipeline
## (turn_manager.execute_turn); these tests exercise that wiring plus the new serialize /
## replay / verify path.
##
## VERIFICATION TIERS (ADR-0006): the SCORE (turns, doom_integral) is the sound anti-cheat
## property -- you cannot claim a score your inputs do not produce. The verification HASH is
## the cheap fingerprint tier, now asserted too: the engine determinism fix (WS-0) means an
## identical seed+input replay reproduces an identical hash, so a mismatch = tamper/forgery.

# Drive a real game headless with a per-turn action script, recording via the live
# VerificationTracker wiring. Returns the exported artifact + the run's score.
# max_turns must exceed a real death (post-#638 recalibration a passive-ish run dies
# ~t300-320) -- the score contract (ADR-0006) is defined at game_over, so the run must
# actually END or live-vs-replay compare different stopping rules.
func _play_scripted(seed: String, script: Dictionary, max_turns: int = 500, schedule: Array = []) -> Dictionary:
	var state: GameState = GameState.new(seed, schedule)
	var tm: TurnManager = TurnManager.new(state)
	VerificationTracker.start_tracking(seed, "test-vB", schedule)

	while not state.game_over and state.turn < max_turns:
		tm.start_turn()
		var t: int = state.turn
		var guard: int = 0
		while state.pending_events.size() > 0 and guard < 128:
			guard += 1
			var event: Dictionary = state.pending_events[0]
			var choices: Array = event.get("choices", [])
			if choices.size() > 0:
				var choice_id: String = str(choices[0].get("id", "")) if typeof(choices[0]) == TYPE_DICTIONARY else str(choices[0])
				tm.resolve_event(event, choice_id)
			else:
				state.pending_events.remove_at(0)
		state.queued_actions.clear()
		for action_id in script.get(t, []):
			state.queued_actions.append(action_id)
		tm.execute_turn()

	var fs: Dictionary = state.to_dict()
	var sc: Array = GameState.score_tuple(fs)
	var out: Dictionary = {
		"replay": VerificationTracker.serialize_replay(),
		"export": VerificationTracker.export_for_submission(fs),
		"turns": sc[0],
		"integral": sc[1],
		"hash": VerificationTracker.get_final_hash()
	}
	VerificationTracker.stop_tracking()
	return out


func test_live_pipeline_records_inputs_into_log():
	# The queued action must show up in the artifact -- proof record_action is wired live.
	var run: Dictionary = _play_scripted("replay_seed_W", {1: ["buy_compute"]})
	var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
	var found: bool = false
	for entry in data.get("log", []):
		if str(entry.get("k", "")) == "a" and str(entry.get("id", "")) == "buy_compute":
			found = true
	assert_true(found, "the live turn pipeline recorded the queued action into the replay log")


func test_export_carries_replay_artifact():
	var run: Dictionary = _play_scripted("replay_seed_E", {1: ["fundraise_small"]})
	assert_true(run["export"].has("replay"), "game-over export carries the replay artifact")
	var data: Dictionary = VerificationTracker.deserialize_replay(run["export"]["replay"])
	assert_eq(data.get("seed", ""), "replay_seed_E", "artifact records its seed")
	assert_eq(data.get("format", ""), "pdoom1-replay-v1", "artifact is tagged with its format version")
	assert_true((data.get("log", []) as Array).size() > 0, "artifact records a non-empty input log")


func test_replay_reproduces_score():
	# Re-simulating the recorded input sequence reproduces the run's score.
	var run: Dictionary = _play_scripted("replay_seed_A", {1: ["fundraise_small"], 2: ["buy_compute"], 3: ["publish_paper"]})
	var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
	assert_false(data.is_empty(), "artifact deserializes")

	var r: Dictionary = ReplaySimulator.replay(data)
	assert_eq(r["turns"], run["turns"], "replay reproduces turns survived")
	assert_eq(r["doom_integral"], run["integral"], "replay reproduces the doom-integral score")
	assert_eq(r["hash"], run["hash"], "replay reproduces the verification hash (deterministic engine, WS-0)")


func test_replay_is_deterministic():
	# Replaying the SAME artifact twice yields the same result (the harness itself is stable).
	var run: Dictionary = _play_scripted("replay_seed_D", {1: ["buy_compute"], 2: ["fundraise_small"]})
	var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
	var r1: Dictionary = ReplaySimulator.replay(data)
	var r2: Dictionary = ReplaySimulator.replay(data)
	assert_eq(r1["turns"], r2["turns"], "same artifact replays to same turns")
	assert_eq(r1["doom_integral"], r2["doom_integral"], "same artifact replays to same integral")
	assert_eq(r1["hash"], r2["hash"], "same artifact replays to same hash (replay path is internally stable)")


func test_verify_accepts_true_score_and_rejects_inflated_claim():
	# The sound anti-cheat property: you cannot claim a score your inputs do not produce.
	var run: Dictionary = _play_scripted("replay_seed_V", {1: ["fundraise_small"], 2: ["buy_compute"]})
	var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
	assert_true(ReplaySimulator.verify(data, run["turns"], run["integral"]),
		"an artifact verifies against the score it actually produces")
	assert_false(ReplaySimulator.verify(data, run["turns"] + 5, run["integral"]),
		"a claim of more turns than the inputs produce is rejected")
	assert_false(ReplaySimulator.verify(data, run["turns"], run["integral"] + 10000),
		"a claim of a higher doom-integral than the inputs produce is rejected")
	# Fingerprint tier (ADR-0006), now that WS-0 made the engine deterministic:
	assert_true(ReplaySimulator.verify(data, run["turns"], run["integral"], run["hash"]),
		"an artifact verifies against the score AND hash it actually produces")
	assert_false(ReplaySimulator.verify(data, run["turns"], run["integral"], "deadbeef_not_the_real_hash"),
		"a forged verification hash is rejected even when the score matches")


func test_artifact_carries_schedule_and_scheduled_run_verifies():
	# DQ-6 / #620 item 4: a seed = RNG seed + event schedule (ADR-0005), but the producer
	# never emitted the `schedule` key the verifier reads (replay_simulator.gd) -- so a
	# scheduled run's artifact re-simulated WITHOUT its schedule and failed to reproduce.
	var schedule: Array = [
		{"turn": 1, "cause": "rival_funding_wave", "target": "capabilicorp", "magnitude": 5000000.0},
		{"turn": 2, "cause": "rival_aggression_shift", "target": "capabilicorp", "magnitude": 0.5},
	]
	var run: Dictionary = _play_scripted("replay_seed_S", {1: ["fundraise_small"], 2: ["buy_compute"]}, 500, schedule)
	var data: Dictionary = VerificationTracker.deserialize_replay(run["replay"])
	assert_true(data.has("schedule"), "artifact emits the schedule key the verifier reads (DQ-6)")
	assert_eq((data.get("schedule", []) as Array).size(), schedule.size(),
		"artifact carries the full event schedule")
	assert_true(ReplaySimulator.verify(data, run["turns"], run["integral"], run["hash"]),
		"a SCHEDULED run's artifact re-simulates to the same score and hash")


func test_malformed_artifact_deserializes_to_empty():
	assert_true(VerificationTracker.deserialize_replay("not json {{{").is_empty(),
		"malformed replay text yields an empty dict, not a crash")
	assert_true(VerificationTracker.deserialize_replay("[1,2,3]").is_empty(),
		"a non-object JSON payload is rejected")


func test_replay_does_not_disturb_live_tracker():
	# A live game is mid-flight; replaying a different run must leave the live hash intact.
	VerificationTracker.start_tracking("live_seed", "test-vB")
	VerificationTracker.record_action("buy_compute", GameState.new("live_seed"))
	var live_hash: String = VerificationTracker.get_final_hash()
	var live_log_size: int = VerificationTracker.replay_log.size()

	var other: Dictionary = _play_scripted("other_seed", {1: ["fundraise_small"]})
	VerificationTracker.start_tracking("live_seed", "test-vB")  # restore the live context
	VerificationTracker.record_action("buy_compute", GameState.new("live_seed"))

	ReplaySimulator.replay(VerificationTracker.deserialize_replay(other["replay"]))
	assert_eq(VerificationTracker.get_final_hash(), live_hash, "replay restored the live hash")
	assert_eq(VerificationTracker.replay_log.size(), live_log_size, "replay restored the live input log")
	VerificationTracker.stop_tracking()

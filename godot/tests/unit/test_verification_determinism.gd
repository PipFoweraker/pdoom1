extends GutTest
## Test suite for cumulative hash verification determinism
##
## Ensures that:
## 1. Same seed + same actions = same hash (determinism)
## 2. Different actions = different hash (sensitivity)
## 3. RNG outcomes are properly tracked
## 4. Hash chain is tamper-evident
##
## History: this file previously `extends Node` with a `_ready()` runner and
## print-based pseudo-assertions, so GUT silently skipped it (wrong base class)
## and it contributed ZERO real coverage. Converted to GutTest under #629/#590.

var test_state: GameState


func test_identical_games_same_hash():
	# Two identical playthroughs must produce the same hash (determinism).
	var seed_str = "test-determinism-seed-001"

	var hash1 = _play_test_game(seed_str, [
		"buy_compute",
		"hire_safety_researcher_0",
		"publish_paper"
	])
	var hash2 = _play_test_game(seed_str, [
		"buy_compute",
		"hire_safety_researcher_0",
		"publish_paper"
	])

	assert_eq(hash1, hash2, "Identical games should produce identical hashes")


func test_different_actions_different_hash():
	# Different actions must produce different hashes (sensitivity).
	var seed_str = "test-determinism-seed-002"

	var hash1 = _play_test_game(seed_str, [
		"buy_compute",
		"hire_safety_researcher_0"
	])
	var hash2 = _play_test_game(seed_str, [
		"buy_compute",
		"publish_paper"
	])

	assert_ne(hash1, hash2, "Different actions should produce different hashes")


func test_rng_tracking_consistency():
	# RNG outcomes are deterministic from the seed, so repeated runs match.
	var seed_str = "test-rng-tracking-001"

	var hash1 = _play_test_game(seed_str, ["fundraise_small"])
	var hash2 = _play_test_game(seed_str, ["fundraise_small"])

	assert_eq(hash1, hash2, "RNG outcomes should be tracked consistently")


func test_action_order_matters():
	# Action order must affect the hash (prevents reordering attacks).
	var seed_str = "test-order-matters-001"

	var hash1 = _play_test_game(seed_str, [
		"buy_compute",
		"publish_paper"
	])
	var hash2 = _play_test_game(seed_str, [
		"publish_paper",
		"buy_compute"
	])

	assert_ne(hash1, hash2, "Action order should affect the hash")


func test_event_tracking():
	# A tracked game must yield a non-empty final hash.
	var seed_str = "test-event-tracking-001"

	# No enable_debug() here any more (#1193): the assertion is about the hash, and the
	# verbose log is opt-in. test_debug_mode_does_not_change_hash covers debug on/off.
	var hash1 = _play_test_game(seed_str, ["buy_compute", "hire_safety_researcher_0"], 10)

	assert_ne(hash1, "", "A tracked game should produce a non-empty final hash")


func _exercise_every_recorder(seed_str: String) -> String:
	## Drive every record_* entry point once per turn; return the final hash.
	test_state = GameState.new()
	test_state.rng.seed = hash(seed_str)
	VerificationTracker.start_tracking(seed_str, "test-v1.0", [], "2026-01", "L0")
	for turn in range(1, 6):
		test_state.turn = turn
		GameActions.execute_action("buy_compute", test_state)
		VerificationTracker.record_action("buy_compute", test_state)
		VerificationTracker.record_event("evt_%d" % turn, "funding", turn)
		VerificationTracker.record_event_response("evt_%d" % turn, "accept", turn)
		VerificationTracker.record_window_response("win_%d" % turn, "pay", "reserve", turn)
		VerificationTracker.record_rng_outcome("event_trigger", 0.123456 * turn, turn)
		VerificationTracker.record_turn_end(turn, test_state)
	var final_hash = VerificationTracker.get_final_hash()
	VerificationTracker.stop_tracking()
	return final_hash


func test_debug_mode_does_not_change_hash():
	# #1193: debug_mode is logging only. The fingerprint must be byte-identical with
	# the verbose log on or off, or making it opt-in would fork every board.
	var was_debug: bool = VerificationTracker.debug_mode
	VerificationTracker.disable_debug()
	var hash_off := _exercise_every_recorder("test-debug-neutral-001")
	VerificationTracker.enable_debug()
	var hash_on := _exercise_every_recorder("test-debug-neutral-001")
	VerificationTracker.debug_mode = was_debug

	assert_ne(hash_off, "", "the exercised game must produce a hash")
	assert_eq(hash_on, hash_off, "debug_mode must not feed the verification hash")


func test_debug_logging_is_opt_in():
	# #1193: default OFF; only the user arg or the env var turns it on.
	assert_false(VerificationTracker.debug_requested(PackedStringArray(), ""), "no arg, no env -> off")
	assert_false(VerificationTracker.debug_requested(PackedStringArray(["--other"]), "0"), "unrelated arg, env 0 -> off")
	assert_true(VerificationTracker.debug_requested(PackedStringArray(["--verify-debug"]), ""), "user arg -> on")
	assert_true(VerificationTracker.debug_requested(PackedStringArray(), "1"), "env 1 -> on")
	assert_true(VerificationTracker.debug_requested(PackedStringArray(), " TRUE "), "env true -> on")


func test_new_game_does_not_force_debug_on():
	# #1193 regression pin: GameManager used to call enable_debug() for every game.
	var src := FileAccess.get_file_as_string("res://scripts/game_manager.gd")
	assert_false(src.contains("VerificationTracker.enable_debug()"),
		"GameManager must not force tracker debug logging on (opt-in via --verify-debug)")


func _play_test_game(seed_str: String, actions: Array, turns: int = 3) -> String:
	## Simulate a game with the given seed and actions; return the final hash.
	# Create fresh game state
	test_state = GameState.new()
	test_state.rng.seed = hash(seed_str)

	# Start verification tracking
	VerificationTracker.start_tracking(seed_str, "test-v1.0")

	# Simulate turns
	for turn in range(turns):
		test_state.turn = turn + 1

		# Execute actions for this turn
		var actions_this_turn = min(actions.size() - turn, 1)
		for i in range(actions_this_turn):
			var action_id = actions[turn] if turn < actions.size() else "do_nothing"
			GameActions.execute_action(action_id, test_state)
			VerificationTracker.record_action(action_id, test_state)

		# Record turn end
		VerificationTracker.record_turn_end(test_state.turn, test_state)

	var final_hash = VerificationTracker.get_final_hash()
	VerificationTracker.stop_tracking()

	return final_hash

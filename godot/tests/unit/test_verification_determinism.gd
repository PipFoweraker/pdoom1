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

	VerificationTracker.enable_debug()
	var hash1 = _play_test_game(seed_str, ["buy_compute", "hire_safety_researcher_0"], 10)
	VerificationTracker.disable_debug()

	assert_ne(hash1, "", "A tracked game should produce a non-empty final hash")


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

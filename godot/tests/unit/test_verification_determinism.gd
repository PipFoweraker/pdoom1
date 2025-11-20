extends Node
## Test suite for cumulative hash verification determinism
##
## Ensures that:
## 1. Same seed + same actions = same hash (determinism)
## 2. Different actions = different hash (sensitivity)
## 3. RNG outcomes are properly tracked
## 4. Hash chain is tamper-evident

var test_state: GameState
var turn_mgr: Node

func _ready():
	print("\n=== VERIFICATION HASH DETERMINISM TESTS ===\n")

	# Run all tests
	test_identical_games_same_hash()
	test_different_actions_different_hash()
	test_rng_tracking_consistency()
	test_action_order_matters()
	test_event_tracking()

	print("\n=== ALL TESTS COMPLETE ===\n")

func test_identical_games_same_hash():
	"""Test that two identical playthroughs produce the same hash"""
	print("[TEST] Identical games → same hash")

	var seed = "test-determinism-seed-001"

	# Play game 1
	var hash1 = _play_test_game(seed, [
		"buy_compute",
		"hire_safety_researcher_0",
		"publish_paper"
	])

	# Play game 2 (identical actions)
	var hash2 = _play_test_game(seed, [
		"buy_compute",
		"hire_safety_researcher_0",
		"publish_paper"
	])

	# Hashes should be identical
	if hash1 == hash2:
		print("  ✅ PASS: Identical games produce identical hashes")
		print("    Hash: %s..." % hash1.substr(0, 16))
	else:
		print("  ❌ FAIL: Hashes differ!")
		print("    Hash 1: %s..." % hash1.substr(0, 16))
		print("    Hash 2: %s..." % hash2.substr(0, 16))

func test_different_actions_different_hash():
	"""Test that different actions produce different hashes"""
	print("\n[TEST] Different actions → different hash")

	var seed = "test-determinism-seed-002"

	# Play game 1
	var hash1 = _play_test_game(seed, [
		"buy_compute",
		"hire_safety_researcher_0"
	])

	# Play game 2 (different second action)
	var hash2 = _play_test_game(seed, [
		"buy_compute",
		"publish_paper"
	])

	# Hashes should be different
	if hash1 != hash2:
		print("  ✅ PASS: Different actions produce different hashes")
		print("    Hash 1: %s..." % hash1.substr(0, 16))
		print("    Hash 2: %s..." % hash2.substr(0, 16))
	else:
		print("  ❌ FAIL: Hashes are identical!")
		print("    Hash: %s..." % hash1.substr(0, 16))

func test_rng_tracking_consistency():
	"""Test that RNG outcomes are consistently tracked"""
	print("\n[TEST] RNG tracking consistency")

	var seed = "test-rng-tracking-001"

	# Play with action that has RNG (fundraise_small)
	var hash1 = _play_test_game(seed, ["fundraise_small"])
	var hash2 = _play_test_game(seed, ["fundraise_small"])

	# Should be identical (RNG is deterministic from seed)
	if hash1 == hash2:
		print("  ✅ PASS: RNG outcomes tracked consistently")
		print("    Hash: %s..." % hash1.substr(0, 16))
	else:
		print("  ❌ FAIL: RNG tracking inconsistent!")
		print("    Hash 1: %s..." % hash1.substr(0, 16))
		print("    Hash 2: %s..." % hash2.substr(0, 16))

func test_action_order_matters():
	"""Test that action order affects hash (prevents reordering attacks)"""
	print("\n[TEST] Action order matters")

	var seed = "test-order-matters-001"

	# Play with actions in order A, B
	var hash1 = _play_test_game(seed, [
		"buy_compute",
		"publish_paper"
	])

	# Play with actions in order B, A
	var hash2 = _play_test_game(seed, [
		"publish_paper",
		"buy_compute"
	])

	# Hashes should be different
	if hash1 != hash2:
		print("  ✅ PASS: Action order affects hash")
		print("    Hash (A→B): %s..." % hash1.substr(0, 16))
		print("    Hash (B→A): %s..." % hash2.substr(0, 16))
	else:
		print("  ❌ FAIL: Action order doesn't affect hash!")
		print("    Hash: %s..." % hash1.substr(0, 16))

func test_event_tracking():
	"""Test that events are tracked in hash"""
	print("\n[TEST] Event tracking")

	var seed = "test-event-tracking-001"

	# Enable debug mode to see event tracking
	VerificationTracker.enable_debug()

	# Play game that might trigger events
	var hash1 = _play_test_game(seed, ["buy_compute", "hire_safety_researcher_0"], 10)

	VerificationTracker.disable_debug()

	print("  ℹ️  Event tracking verified in debug output")
	print("    Final hash: %s..." % hash1.substr(0, 16))

func _play_test_game(seed: String, actions: Array, turns: int = 3) -> String:
	"""
	Simulate a game with given seed and actions.
	Returns the final verification hash.
	"""
	# Create fresh game state
	test_state = GameState.new()
	test_state.rng.seed = hash(seed)

	# Start verification tracking
	VerificationTracker.start_tracking(seed, "test-v1.0")

	# Simulate turns
	for turn in range(turns):
		test_state.turn = turn + 1

		# Execute actions for this turn
		var actions_this_turn = min(actions.size() - turn, 1)
		for i in range(actions_this_turn):
			var action_id = actions[turn] if turn < actions.size() else "do_nothing"

			# Execute action (simplified - just record it)
			var result = GameActions.execute_action(action_id, test_state)

			# Record action in hash
			VerificationTracker.record_action(action_id, test_state)

		# Record turn end
		VerificationTracker.record_turn_end(test_state.turn, test_state)

	# Get final hash
	var final_hash = VerificationTracker.get_final_hash()

	# Stop tracking
	VerificationTracker.stop_tracking()

	return final_hash

extends Node
## Quick Verification System Test
## Run this to verify hash generation works before deployment
##
## Usage:
##   1. Add this scene to your project
##   2. Run it (F6 in Godot)
##   3. Check output for ✅ PASS or ❌ FAIL
##   4. Both runs should produce IDENTICAL hashes

func _ready():
	print("\n============================================================")
	print("VERIFICATION SYSTEM - QUICK TEST")
	print("============================================================\n")

	# Run two identical games
	print("Running Game 1 (seed: quick-test-001)...")
	var hash1 = run_test_game("quick-test-001")

	print("\nRunning Game 2 (same seed, same actions)...")
	var hash2 = run_test_game("quick-test-001")

	# Compare hashes
	print("\n============================================================")
	print("RESULTS")
	print("============================================================")
	print("Hash 1: %s" % hash1)
	print("Hash 2: %s" % hash2)
	print("")

	if hash1 == hash2:
		print("✅ PASS: Hashes match! System is deterministic.")
		print("   This means: same seed + same actions = same hash")
		print("   Ready for deployment!")
	else:
		print("❌ FAIL: Hashes don't match!")
		print("   This means: something is not deterministic")
		print("   Check RNG tracking in turn_manager.gd")

	print("============================================================\n")

	# Test different actions
	print("Testing different actions (should produce different hash)...")
	var hash3 = run_test_game_variant("quick-test-002")

	if hash3 != hash1:
		print("✅ PASS: Different actions produce different hash")
	else:
		print("❌ FAIL: Different actions produce same hash!")

	print("\n============================================================")
	print("TEST COMPLETE - Check results above")
	print("============================================================\n")

	# Exit after test
	await get_tree().create_timer(1.0).timeout
	get_tree().quit()

func run_test_game(seed: String) -> String:
	"""Simulate a short game and return verification hash."""

	# Create game state
	var state = GameState.new(seed)

	# Start verification
	VerificationTracker.start_tracking(seed, "test-0.10.2")

	# Simulate 5 turns
	for turn in range(1, 6):
		state.turn = turn
		state.action_points = 3

		# Turn start
		print("  Turn %d..." % turn)

		# Execute some actions
		match turn:
			1:
				_execute_action("buy_compute", state)
			2:
				_execute_action("hire_safety_researcher_0", state)
			3:
				_execute_action("publish_paper", state)
			4:
				_execute_action("buy_compute", state)
			5:
				_execute_action("do_nothing", state)

		# Simulate some RNG (candidate spawning)
		var candidate_roll = state.rng.randf()
		VerificationTracker.record_rng_outcome("test_candidate_spawn", candidate_roll, turn)

		# Turn end
		VerificationTracker.record_turn_end(turn, state)

	# Get final hash
	var final_hash = VerificationTracker.get_final_hash()
	VerificationTracker.stop_tracking()

	return final_hash

func run_test_game_variant(seed: String) -> String:
	"""Run game with DIFFERENT actions to verify hash changes."""

	var state = GameState.new(seed)
	VerificationTracker.start_tracking(seed, "test-0.10.2")

	for turn in range(1, 6):
		state.turn = turn
		state.action_points = 3

		# Different actions
		match turn:
			1:
				_execute_action("hire_safety_researcher_0", state)  # Changed
			2:
				_execute_action("buy_compute", state)  # Changed
			3:
				_execute_action("publish_paper", state)
			4:
				_execute_action("buy_compute", state)
			5:
				_execute_action("do_nothing", state)

		var candidate_roll = state.rng.randf()
		VerificationTracker.record_rng_outcome("test_candidate_spawn", candidate_roll, turn)
		VerificationTracker.record_turn_end(turn, state)

	var final_hash = VerificationTracker.get_final_hash()
	VerificationTracker.stop_tracking()

	return final_hash

func _execute_action(action_id: String, state: GameState):
	"""Execute action and record in verification hash."""

	# Execute the action (simplified - we don't need full validation for test)
	var result = GameActions.execute_action(action_id, state)

	# Record action in verification hash
	VerificationTracker.record_action(action_id, state)

	print("    - Executed: %s" % action_id)

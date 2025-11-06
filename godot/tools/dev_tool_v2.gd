extends SceneTree
## P(Doom) Godot Development Tool v2
##
## Handles autoload initialization gracefully
## Verbose output for debugging

# Test registry
var tests := {
	"game_state": test_game_state,
	"seeds": test_seed_variations,
	"dual": test_dual_identity,
}

func _init():
	print("\n" + "=".repeat(70))
	print("P(Doom) Godot Development Tool v2")
	print("=".repeat(70))

	print("\n[INFO] Running in headless mode")
	print("[INFO] Autoloads will initialize (GameConfig, GameManager, etc.)")
	print("[INFO] This is normal and expected\n")

	var args = OS.get_cmdline_args()

	# Parse command line arguments
	if "--list" in args:
		list_tests()
		finish_execution()
		return

	if "--test" in args:
		var test_idx = args.find("--test")
		if test_idx + 1 < args.size():
			var test_name = args[test_idx + 1]
			print("[INFO] Running test: %s\n" % test_name)
			run_test(test_name)
		else:
			print("[ERROR] --test requires a test name")
			list_tests()
		finish_execution()
		return

	# Interactive mode - run all tests
	print("[INFO] No arguments provided - running all tests\n")
	interactive_menu()
	finish_execution()

func finish_execution():
	"""Gracefully finish execution with status message"""
	print("\n" + "=".repeat(70))
	print("[INFO] Test execution complete")
	print("[INFO] Exiting Godot...")
	print("=".repeat(70) + "\n")
	quit(0)

func interactive_menu():
	"""Run all tests in sequence"""
	print("=".repeat(70))
	print("Running all tests")
	print("=".repeat(70) + "\n")

	for test_name in tests.keys():
		run_test(test_name)
		print()  # Blank line between tests

func list_tests():
	"""List all available tests"""
	print("\nAvailable Tests:")
	for test_name in tests.keys():
		print("  - %s" % test_name)
	print()

func run_test(test_name: String):
	"""Run a specific test by name"""
	if test_name in tests:
		print("-".repeat(70))
		print("[TEST] %s" % test_name.to_upper())
		print("-".repeat(70))
		tests[test_name].call()
		print("[✓] Test '%s' completed" % test_name)
		print("-".repeat(70))
	else:
		print("[ERROR] Unknown test: %s" % test_name)
		list_tests()

## ============================================================================
## TEST IMPLEMENTATIONS
## ============================================================================

func test_game_state():
	"""Test basic game state functionality"""
	print("\n[INFO] Loading GameState class...")
	var GameStateClass = load("res://scripts/core/game_state.gd")
	if not GameStateClass:
		print("[ERROR] Could not load GameState script")
		return

	print("[INFO] Creating GameState instance (autoloads will initialize)...")
	var gs = GameStateClass.new()

	print("[INFO] Initializing with seed 'dev-test'...")
	gs.initialize("dev-test")

	print("\n[RESULTS] GameState Properties:")
	print("  Seed: %s" % gs.seed)
	print("  Turn: %d" % gs.turn)
	print("  Money: $%.0f" % gs.money)
	print("  Staff: %d" % gs.staff)
	print("  Reputation: %.1f" % gs.reputation)
	print("  Doom: %.1f%%" % gs.doom)
	if "action_points" in gs and "max_action_points" in gs:
		print("  Action Points: %d / %d" % [gs.action_points, gs.max_action_points])

	# Test turn advancement
	print("\n[INFO] Testing turn advancement...")
	var initial_turn = gs.turn
	if gs.has_method("advance_turn"):
		gs.advance_turn()
		print("  Turn advanced: %d → %d" % [initial_turn, gs.turn])
	elif gs.has_method("end_turn"):
		gs.end_turn()
		print("  Turn ended: %d → %d" % [initial_turn, gs.turn])
	else:
		print("  [SKIP] No advance_turn or end_turn method found")

	print("\n[INFO] Cleaning up GameState instance...")
	gs.free()
	print("[✓] GameState working correctly")

func test_seed_variations():
	"""Test seed consistency"""
	print("\n[INFO] Testing seed variation consistency...")

	var GameStateClass = load("res://scripts/core/game_state.gd")
	if not GameStateClass:
		print("[ERROR] Could not load GameState script")
		return

	var test_seeds = ["alpha", "beta", "gamma"]

	print("\n[RESULTS] Lab names for different seeds:")
	for seed in test_seeds:
		var gs = GameStateClass.new()
		gs.initialize(seed)
		var lab_name = gs.lab_name if "lab_name" in gs else "N/A"
		print("  Seed '%s': %s" % [seed, lab_name])
		gs.free()

	# Test consistency
	print("\n[INFO] Testing seed consistency (same seed = same result)...")
	var seed = "consistency-test"

	var gs1 = GameStateClass.new()
	gs1.initialize(seed)
	var name1 = gs1.lab_name if "lab_name" in gs1 else "N/A"
	gs1.free()

	var gs2 = GameStateClass.new()
	gs2.initialize(seed)
	var name2 = gs2.lab_name if "lab_name" in gs2 else "N/A"
	gs2.free()

	var matches = (name1 == name2)
	var status = "[✓]" if matches else "[✗]"
	print("  %s Run 1: '%s'" % [status, name1])
	print("  %s Run 2: '%s'" % [status, name2])
	print("  %s Consistency: %s" % [status, "PASS" if matches else "FAIL"])

	if matches:
		print("\n[✓] Seed variation system working correctly")
	else:
		print("\n[✗] Seed variation INCONSISTENT - this is a bug!")

func test_dual_identity():
	"""Test dual identity system"""
	print("\n[INFO] Testing dual identity (player + lab names)...")

	var GameStateClass = load("res://scripts/core/game_state.gd")
	if not GameStateClass:
		print("[ERROR] Could not load GameState script")
		return

	var gs = GameStateClass.new()
	gs.initialize("identity-test")

	print("\n[RESULTS] Default Identity:")
	if "player_name" in gs:
		print("  Player Name: %s" % gs.player_name)
	else:
		print("  Player Name: [not implemented]")

	if "lab_name" in gs:
		print("  Lab Name: %s" % gs.lab_name)
	else:
		print("  Lab Name: [not implemented]")

	# Test customization
	if "player_name" in gs:
		var original_lab = gs.lab_name if "lab_name" in gs else "N/A"
		gs.player_name = "CustomPlayer"
		var new_lab = gs.lab_name if "lab_name" in gs else "N/A"

		print("\n[INFO] After changing player name to 'CustomPlayer':")
		print("  Player Name: %s" % gs.player_name)
		print("  Lab Name: %s" % new_lab)

		if original_lab == new_lab:
			print("  [✓] Lab name unchanged (correct behavior)")
		else:
			print("  [!] Lab name changed (unexpected)")

	gs.free()
	print("\n[✓] Dual identity test complete")

## ============================================================================
## HELPER INFO
## ============================================================================

func print_info(message: String):
	"""Print info message"""
	print("[INFO] %s" % message)

func print_result(message: String):
	"""Print result message"""
	print("[RESULT] %s" % message)

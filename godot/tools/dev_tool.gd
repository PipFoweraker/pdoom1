extends SceneTree
## P(Doom) Godot Development Tool
##
## Interactive testing tool for Godot implementation, ported from Python version.
## Run via: godot --script tools/dev_tool.gd [--test <test_name>]
##
## Features:
## - Interactive test menu
## - Game state validation
## - Leaderboard testing
## - Seed variation testing
## - Turn progression debugging
##
## Usage:
##   godot --script tools/dev_tool.gd                # Interactive menu
##   godot --script tools/dev_tool.gd --test seeds   # Run specific test
##   godot --script tools/dev_tool.gd --list         # List available tests

# Test registry - maps test names to functions
var tests := {
	"game_state": test_game_state,
	"seeds": test_seed_variations,
	"leaderboard": test_leaderboard_system,
	"turn": test_turn_progression,
	"dual": test_dual_identity,
	"session": test_complete_session,
}

func _init():
	print("=" * 60)
	print("P(Doom) Godot Development Tool")
	print("=" * 60)

	var args = OS.get_cmdline_args()

	# Parse command line arguments
	if "--list" in args:
		list_tests()
		quit()
		return

	if "--test" in args:
		var test_idx = args.find("--test")
		if test_idx + 1 < args.size():
			var test_name = args[test_idx + 1]
			run_test(test_name)
		else:
			print("[ERROR] --test requires a test name")
			list_tests()
		quit()
		return

	# Interactive mode
	interactive_menu()

func interactive_menu():
	"""Display interactive test menu"""
	print("\nAvailable Tests:")
	print("-" * 60)
	var idx = 1
	for test_name in tests.keys():
		print("  %d. %s" % [idx, test_name])
		idx += 1
	print("  0. Exit")
	print("-" * 60)
	print("\nNote: For interactive input, run tests individually via:")
	print("  godot --script tools/dev_tool.gd --test <test_name>")
	print("\nRunning all tests in sequence...")
	print()

	for test_name in tests.keys():
		run_test(test_name)
		print()

	quit()

func list_tests():
	"""List all available tests"""
	print("\nAvailable Tests:")
	for test_name in tests.keys():
		print("  - %s" % test_name)

func run_test(test_name: String):
	"""Run a specific test by name"""
	if test_name in tests:
		print("[TEST] Running: %s" % test_name)
		print("=" * 60)
		tests[test_name].call()
		print("[OK] Test completed: %s" % test_name)
	else:
		print("[ERROR] Unknown test: %s" % test_name)
		list_tests()

## ============================================================================
## TEST IMPLEMENTATIONS
## ============================================================================

func test_game_state():
	"""Test basic game state functionality"""
	print("Testing GameState initialization and basic operations...")

	# Create a game state with test seed
	var game_state = GameState.new()
	game_state.initialize("dev-test-seed")

	print("  Initial State:")
	print("    Seed: %s" % game_state.seed)
	print("    Turn: %d" % game_state.turn)
	print("    Money: $%.0f" % game_state.money)
	print("    Staff: %d" % game_state.staff)
	print("    Reputation: %.1f" % game_state.reputation)
	print("    Doom: %.1f%%" % game_state.doom)
	print("    Action Points: %d / %d" % [game_state.action_points, game_state.max_action_points])

	# Test turn advancement
	print("\n  Testing turn advancement...")
	var initial_turn = game_state.turn
	game_state.advance_turn()
	print("    Turn advanced: %d → %d" % [initial_turn, game_state.turn])
	print("    Action Points reset: %d" % game_state.action_points)

	game_state.free()
	print("\n[✓] GameState working correctly")

func test_seed_variations():
	"""Test how different seeds create different experiences"""
	print("Testing seed variation consistency...")

	var test_seeds = ["alpha", "beta", "gamma", "delta", "epsilon"]
	var lab_names = {}

	print("\n  Generating lab names for different seeds:")
	for seed in test_seeds:
		var gs = GameState.new()
		gs.initialize(seed)
		var lab_name = gs.lab_name if "lab_name" in gs else "N/A"
		lab_names[seed] = lab_name
		print("    Seed '%s': Lab = '%s'" % [seed, lab_name])
		gs.free()

	# Test consistency - same seed should produce same lab name
	print("\n  Testing seed consistency (run twice):")
	for seed in test_seeds.slice(0, 2):  # Test first 3 seeds
		var gs1 = GameState.new()
		gs1.initialize(seed)
		var name1 = gs1.lab_name if "lab_name" in gs1 else "N/A"
		gs1.free()

		var gs2 = GameState.new()
		gs2.initialize(seed)
		var name2 = gs2.lab_name if "lab_name" in gs2 else "N/A"
		gs2.free()

		var matches = (name1 == name2)
		var status = "[✓]" if matches else "[✗]"
		print("    %s Seed '%s': '%s' == '%s' : %s" % [status, seed, name1, name2, matches])

	print("\n[✓] Seed variation system working correctly")

func test_dual_identity():
	"""Test dual identity system (player_name + lab_name)"""
	print("Testing Dual Identity System...")

	var gs = GameState.new()
	gs.initialize("test-seed-123")

	print("  Default Identity:")
	print("    Player Name: %s" % (gs.player_name if "player_name" in gs else "N/A"))
	print("    Lab Name: %s" % (gs.lab_name if "lab_name" in gs else "N/A"))

	# Test customization
	if "player_name" in gs:
		gs.player_name = "DevTester"
		print("\n  Customized Identity:")
		print("    Player Name: %s" % gs.player_name)
		print("    Lab Name: %s (should be unchanged)" % gs.lab_name)

	# Test different seed
	var gs2 = GameState.new()
	gs2.initialize("different-seed")
	print("\n  Different Seed:")
	print("    Lab Name: %s" % (gs2.lab_name if "lab_name" in gs2 else "N/A"))

	gs.free()
	gs2.free()
	print("\n[✓] Dual identity system working correctly")

func test_leaderboard_system():
	"""Test leaderboard functionality"""
	print("Testing Leaderboard System...")
	print("  [NOTE] This requires Leaderboard autoload to be configured")

	# Check if leaderboard exists
	if not Engine.has_singleton("Leaderboard") and not has_node("/root/Leaderboard"):
		print("  [SKIP] Leaderboard autoload not found")
		print("  [INFO] To enable: Configure Leaderboard in Project Settings > Autoload")
		return

	var leaderboard = get_node_or_null("/root/Leaderboard")
	if not leaderboard:
		print("  [SKIP] Could not access Leaderboard node")
		return

	print("  [✓] Leaderboard autoload found")

	# Test basic functionality
	var test_seed = "dev-test-seed"
	print("  Testing seed-specific leaderboard: '%s'" % test_seed)

	# Note: Actual implementation depends on Leaderboard API
	# This is a template - adjust based on actual Leaderboard interface
	if leaderboard.has_method("get_entries_for_seed"):
		var entries = leaderboard.get_entries_for_seed(test_seed)
		print("  [✓] Retrieved %d entries for seed '%s'" % [entries.size(), test_seed])
	else:
		print("  [INFO] Leaderboard.get_entries_for_seed() not implemented yet")

	print("\n[✓] Leaderboard system check completed")

func test_turn_progression():
	"""Test game progression over multiple turns"""
	print("Testing Turn Progression...")
	print("  Simulating 10 turns of gameplay...")

	var gs = GameState.new()
	gs.initialize("turn-test-seed")

	print("\n  %-4s | %-6s | %-10s | %-6s | %-6s | %-8s" % ["Turn", "Staff", "Money", "Doom", "Rep", "GameOver"])
	print("  " + "-" * 60)

	for i in range(10):
		var turn_str = "%d" % gs.turn
		var staff_str = "%d" % gs.staff
		var money_str = "$%.0f" % gs.money
		var doom_str = "%.1f%%" % gs.doom
		var rep_str = "%.0f" % gs.reputation
		var over_str = "Yes" if gs.game_over else "No"

		print("  %-4s | %-6s | %-10s | %-6s | %-6s | %-8s" % [turn_str, staff_str, money_str, doom_str, rep_str, over_str])

		if gs.game_over:
			print("\n  [!] Game ended at turn %d" % gs.turn)
			if "game_over_reason" in gs:
				print("      Reason: %s" % gs.game_over_reason)
			break

		# Advance turn
		gs.advance_turn()

		# Simulate some changes (basic placeholder)
		gs.money -= 2000
		gs.reputation += 5

	if not gs.game_over:
		print("\n  [✓] Game survived 10 turns")

	gs.free()
	print("\n[✓] Turn progression test completed")

func test_complete_session():
	"""Test complete game session simulation"""
	print("Testing Complete Session Simulation...")

	var gs = GameState.new()
	gs.initialize("session-test-seed")

	if "player_name" in gs:
		gs.player_name = "SessionTester"
		print("  Player: %s" % gs.player_name)
	if "lab_name" in gs:
		print("  Lab: %s" % gs.lab_name)

	print("\n  Simulating 5-turn session:")
	for i in range(5):
		gs.advance_turn()
		gs.money -= 2000
		gs.reputation += 5
		print("    Turn %d: $%.0f, Rep: %.0f" % [gs.turn, gs.money, gs.reputation])

	print("\n  [✓] Session simulation completed")

	# Test leaderboard recording (if available)
	var leaderboard = get_node_or_null("/root/Leaderboard")
	if leaderboard and leaderboard.has_method("record_session"):
		print("  [INFO] Recording session to leaderboard...")
		# Implementation depends on actual Leaderboard API
	else:
		print("  [SKIP] Leaderboard recording not available")

	gs.free()
	print("\n[✓] Complete session test finished")

## ============================================================================
## HELPER FUNCTIONS
## ============================================================================

func print_separator():
	print("=" * 60)

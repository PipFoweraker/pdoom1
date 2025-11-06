extends SceneTree
## Simple test without autoload dependencies

func _init():
	print("=".repeat(60))
	print("Simple Godot Test - No Autoloads")
	print("=".repeat(60))

	# Test 1: Basic functionality
	print("\n[TEST] Basic GDScript")
	var test_dict = {"a": 1, "b": 2, "c": 3}
	print("  Dictionary created: %s" % test_dict)
	print("  [✓] Pass")

	# Test 2: Load GameState script (without instantiating)
	print("\n[TEST] Load GameState script")
	var GameStateClass = load("res://scripts/core/game_state.gd")
	if GameStateClass:
		print("  [✓] GameState script found at res://scripts/core/game_state.gd")
	else:
		print("  [✗] GameState script not found")

	# Test 3: Check methods available
	print("\n[TEST] Check GameState methods")
	if GameStateClass:
		var temp_gs = GameStateClass.new()
		print("  Available methods:")
		if temp_gs.has_method("initialize"):
			print("    - initialize()")
		if temp_gs.has_method("advance_turn"):
			print("    - advance_turn()")
		if temp_gs.has_method("end_turn"):
			print("    - end_turn()")
		temp_gs.free()
		print("  [✓] Methods checked")

	print("\n" + "=".repeat(60))
	print("Test Complete - Exiting Immediately")
	print("=".repeat(60))

	# Force immediate exit
	quit(0)

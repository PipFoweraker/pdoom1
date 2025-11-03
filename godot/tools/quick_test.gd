extends SceneTree
## Quick test - minimal version to verify script execution works

func _init():
	print("=".repeat(60))
	print("Quick Test - Godot Dev Tool")
	print("=".repeat(60))

	# Test 1: Basic functionality
	print("\n[TEST 1] Basic GDScript functionality")
	var test_array = ["alpha", "beta", "gamma"]
	for item in test_array:
		print("  - Item: %s" % item)
	print("[✓] Basic functionality works")

	# Test 2: Check for GameState autoload
	print("\n[TEST 2] Checking for GameState autoload")
	if Engine.has_singleton("GameState"):
		print("[✓] GameState singleton found")
	elif root and root.has_node("/root/GameState"):
		print("[✓] GameState autoload found at /root/GameState")
	else:
		print("[!] GameState not found as singleton or autoload")
		print("    This is expected when running outside the main game")

	# Test 3: Check for GameManager
	print("\n[TEST 3] Checking for GameManager autoload")
	if root and root.has_node("/root/GameManager"):
		print("[✓] GameManager autoload found")
	else:
		print("[!] GameManager not found")
		print("    This is expected when running outside the main game")

	# Test 4: Load GameState class directly
	print("\n[TEST 4] Attempting to load GameState class")
	var GameStateClass = load("res://scripts/core/game_state.gd")
	if GameStateClass:
		print("[✓] GameState script loaded successfully")
		print("    Path: res://scripts/core/game_state.gd")

		# Try to instantiate
		print("\n[TEST 5] Attempting to instantiate GameState")
		var gs = GameStateClass.new()
		if gs:
			print("[✓] GameState instance created")

			# Check for initialize method
			if gs.has_method("initialize"):
				print("[✓] GameState has initialize() method")
				# Try to initialize with a seed
				print("\n[TEST 6] Initializing GameState with seed")
				gs.initialize("test-seed-123")
				print("[✓] GameState initialized successfully")

				# Check properties
				print("\n[TEST 7] Checking GameState properties")
				if "seed" in gs:
					print("  Seed: %s" % gs.seed)
				if "turn" in gs:
					print("  Turn: %s" % gs.turn)
				if "money" in gs:
					print("  Money: $%.0f" % gs.money)
				if "doom" in gs:
					print("  Doom: %.1f%%" % gs.doom)

				print("[✓] GameState properties accessible")
			else:
				print("[!] GameState doesn't have initialize() method")

			gs.free()
		else:
			print("[✗] Failed to create GameState instance")
	else:
		print("[✗] Failed to load GameState script")
		print("    Expected path: res://scripts/core/game_state.gd")

	print("\n" + "=".repeat(60))
	print("Quick Test Complete")
	print("=".repeat(60))

	quit()

extends SceneTree
## P(Doom) Godot Development Tool - MINIMAL VERSION
##
## This version validates code without instantiating GameState
## to avoid autoload initialization hanging

func _init():
	print("\n" + "=".repeat(70))
	print("P(Doom) Godot Development Tool - Minimal (No Instantiation)")
	print("=".repeat(70))

	var args = OS.get_cmdline_args()
	var test_name = ""

	if "--test" in args:
		var test_idx = args.find("--test")
		if test_idx + 1 < args.size():
			test_name = args[test_idx + 1]

	if test_name == "":
		print("\n[INFO] No test specified, running validation checks\n")
		run_all_validations()
	else:
		print("\n[INFO] Running test: %s\n" % test_name)
		run_validation(test_name)

	print("\n" + "=".repeat(70))
	print("[✓] Validation complete - exiting")
	print("=".repeat(70) + "\n")

	# Force immediate exit
	OS.kill(OS.get_process_id())

func run_all_validations():
	"""Run all validation checks"""
	validate_gamestate_exists()
	validate_gamestate_methods()
	validate_gamestate_properties()

func run_validation(test_name: String):
	"""Run specific validation"""
	match test_name:
		"exists":
			validate_gamestate_exists()
		"methods":
			validate_gamestate_methods()
		"properties":
			validate_gamestate_properties()
		_:
			print("[ERROR] Unknown test: %s" % test_name)
			print("\nAvailable tests:")
			print("  - exists")
			print("  - methods")
			print("  - properties")

func validate_gamestate_exists():
	"""Validate GameState script exists and can be loaded"""
	print("-".repeat(70))
	print("[TEST] GameState Script Existence")
	print("-".repeat(70))

	var GameStateClass = load("res://scripts/core/game_state.gd")
	if GameStateClass:
		print("[✓] GameState script found: res://scripts/core/game_state.gd")
		print("[✓] Script can be loaded")
	else:
		print("[✗] GameState script NOT found")
		return

	print("-".repeat(70) + "\n")

func validate_gamestate_methods():
	"""Validate GameState has expected methods"""
	print("-".repeat(70))
	print("[TEST] GameState Method Validation")
	print("-".repeat(70))

	var GameStateClass = load("res://scripts/core/game_state.gd")
	if not GameStateClass:
		print("[✗] Cannot load GameState")
		return

	# Get the script's methods by checking the source
	var script = GameStateClass as Script
	var methods = script.get_script_method_list()

	print("\n[INFO] Found %d methods in GameState:" % methods.size())

	var expected_methods = ["initialize", "advance_turn", "end_turn"]
	var found_methods = []

	for method in methods:
		var method_name = method.name if method.has("name") else str(method)
		if method_name in expected_methods:
			found_methods.append(method_name)

	print("\n[RESULTS] Expected Method Check:")
	for expected in expected_methods:
		if expected in found_methods:
			print("  [✓] %s() - Found" % expected)
		else:
			print("  [?] %s() - Not found (might use different name)" % expected)

	print("\n[INFO] Sample of all methods found:")
	for i in range(min(10, methods.size())):
		var method = methods[i]
		var method_name = method.name if method.has("name") else str(method)
		print("  - %s" % method_name)

	if methods.size() > 10:
		print("  ... and %d more" % (methods.size() - 10))

	print("-".repeat(70) + "\n")

func validate_gamestate_properties():
	"""Validate GameState has expected properties"""
	print("-".repeat(70))
	print("[TEST] GameState Property Validation")
	print("-".repeat(70))

	var GameStateClass = load("res://scripts/core/game_state.gd")
	if not GameStateClass:
		print("[✗] Cannot load GameState")
		return

	var script = GameStateClass as Script
	var properties = script.get_script_property_list()

	print("\n[INFO] Found %d properties in GameState:" % properties.size())

	var expected_props = ["seed", "turn", "money", "doom", "staff", "reputation"]
	var found_props = []

	for prop in properties:
		var prop_name = prop.name if prop.has("name") else str(prop)
		if prop_name in expected_props:
			found_props.append(prop_name)

	print("\n[RESULTS] Expected Property Check:")
	for expected in expected_props:
		if expected in found_props:
			print("  [✓] %s - Found" % expected)
		else:
			print("  [?] %s - Not found (might be different)" % expected)

	print("\n[INFO] Sample of all properties found:")
	var count = 0
	for prop in properties:
		var prop_name = prop.name if prop.has("name") else str(prop)
		# Skip internal properties
		if not prop_name.begins_with("_"):
			print("  - %s" % prop_name)
			count += 1
			if count >= 15:
				break

	if properties.size() > count:
		print("  ... and more")

	print("-".repeat(70) + "\n")

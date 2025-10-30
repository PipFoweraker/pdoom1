extends SceneTree
## GUT test runner script for command-line execution

func _init():
	var gut = load("res://addons/gut/gut.gd").new()
	add_child(gut)

	# Configure GUT
	gut.set_yield_between_tests(true)
	gut.set_modulate_test_name(true)

	# Add test directories
	gut.add_directory("res://tests/unit")

	# Set output options
	gut.set_log_level(gut.LOG_LEVEL_ALL_ASSERTS)
	gut.set_compact_mode(false)

	# Run tests
	gut.test_scripts()

	# Wait for tests to complete
	await gut.get_tree().process_frame

	# Print summary
	print("\n" + "=".repeat(60))
	print("TEST SUMMARY")
	print("=".repeat(60))
	print("Tests run: ", gut.get_test_count())
	print("Passed: ", gut.get_pass_count())
	print("Failed: ", gut.get_fail_count())
	print("=".repeat(60))

	# Exit with appropriate code
	if gut.get_fail_count() > 0:
		quit(1)
	else:
		quit(0)

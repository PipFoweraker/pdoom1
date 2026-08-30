extends GutTest
## Regression (#1341): opening the pause menu must actually stop the month.
##
## Found by Pip on the SHIPPED v0.14.4 build, 2026-08-30. He opened the pause menu
## to change the music volume; six day-ticks and a month boundary ran while it was
## open, and the Month Review dialog then appeared over a still-open, still
## click-eating, invisible menu.
##
## Root cause was one argument. SceneTree.create_timer(time_sec, process_always,
## ...) DEFAULTS process_always to TRUE, so the timer ignores SceneTree.paused --
## and game_manager's month-playback and turn-advance awaits both used the default.
## pause_menu.gd was never at fault: it sets get_tree().paused = true correctly and
## the loops did not observe it.
##
## This test asserts the invariant in BOTH directions, because a pause test that
## only checks "nothing happened" passes just as well when the game is broken and
## nothing was ever going to happen.

var _gm = null


func after_each() -> void:
	# NEVER leave the tree paused. A failed assertion between the pause and the
	# unpause below would otherwise hand every later test in the run a frozen tree,
	# and the suite would report a cascade of failures with one real cause.
	get_tree().paused = false
	_gm = null


func _boot_game():
	"""Boot the real scene exactly as the game does (same idiom as #664's test)."""
	var scene: PackedScene = load("res://scenes/main.tscn")
	assert_not_null(scene, "main.tscn must load")
	var root: Node = scene.instantiate()
	add_child_autofree(root)
	var main_ui: Node = root.find_child("MainUI", true, false)
	assert_not_null(main_ui, "MainUI node must exist under the scene root")
	await get_tree().process_frame
	for _i in range(10):
		await get_tree().process_frame
	return main_ui.game_manager


func _wait_real_seconds(seconds: float) -> void:
	"""Wait in WALL-CLOCK time, including while the tree is paused.

	This deliberately uses create_timer's process_always DEFAULT (true) -- the very
	behaviour that caused #1341 -- because the test has to keep running through the
	pause it is testing. Do not "fix" this one to false.
	"""
	await get_tree().create_timer(seconds, true).timeout


func test_paused_tree_stops_day_ticks_and_unpausing_resumes_them() -> void:
	_gm = await _boot_game()
	assert_not_null(_gm, "MainUI must have created a GameManager")
	assert_true(_gm.is_initialized, "GameManager must be initialized")

	# Presentation pacing only -- day_tick_seconds is not a sim input, so shortening
	# it changes nothing but how long this test takes.
	_gm.day_tick_seconds = 0.05

	# Commit the month with no queued actions: end_month() routes an empty plan
	# through the canonical PASS, so playback starts without any setup.
	_gm.end_month()
	await get_tree().process_frame
	assert_true(
		_gm.month_playback_active,
		"end_month() must start month playback, or this test proves nothing"
	)

	# --- direction 1: PAUSED means STOPPED -------------------------------------
	get_tree().paused = true
	var turn_at_pause: int = _gm.state.turn
	# Long enough for many ticks at 0.05s. Before the fix this window swallowed six
	# real ticks and a month boundary.
	await _wait_real_seconds(0.6)
	var turn_after_pause: int = _gm.state.turn

	assert_eq(
		turn_after_pause,
		turn_at_pause,
		(
			"The month advanced while the tree was PAUSED (#1341). "
			+ "turn %d -> %d over 0.6s at day_tick_seconds=0.05. "
			+ "Check that game_manager's create_timer calls pass process_always=false."
		) % [turn_at_pause, turn_after_pause]
	)

	# --- direction 2: UNPAUSED means RUNNING -----------------------------------
	# Without this half, the assertion above would also pass on a game that had
	# simply stopped working -- which is the failure mode #1023 spent a month in.
	get_tree().paused = false
	await _wait_real_seconds(0.6)
	var turn_after_resume: int = _gm.state.turn

	gut.p(
		(
			"turn at pause=%d, after 0.6s paused=%d, after 0.6s resumed=%d"
			% [turn_at_pause, turn_after_pause, turn_after_resume]
		)
	)
	assert_gt(
		turn_after_resume,
		turn_after_pause,
		(
			"The month did NOT resume after unpausing, so the 'paused means stopped' "
			+ "assertion above proves nothing -- the playback loop is simply dead."
		)
	)

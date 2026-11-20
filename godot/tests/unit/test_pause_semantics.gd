extends GutTest
## Pins docs/design/PAUSE_SEMANTICS.md (#1343) at the sites where a wrong answer is
## expensive. Sibling of test_pause_stops_month_playback.gd (#1341), which pins the
## simulation half; this file pins navigation, diagnostics and messages.
##
## Every behavioural test here asserts BOTH directions, because a pause test that only
## checks "nothing happened" passes just as well on a game where nothing was ever going
## to happen. Where the interesting direction is "keeps running while paused", the
## other direction is a CONTROL: a plain pausable node in the same paused tree, proving
## the tree really was paused and the passing site is genuinely exempt.

var _saved_fade_duration: float = 0.3


func before_each() -> void:
	_saved_fade_duration = SceneTransition.fade_duration


func after_each() -> void:
	# NEVER leave the tree paused -- a failed assertion mid-test would otherwise freeze
	# every later test in the run and report a cascade with one real cause.
	get_tree().paused = false
	SceneTransition.fade_duration = _saved_fade_duration
	SceneTransition.fade_rect.modulate.a = 0.0


func _wait_real_seconds(seconds: float) -> void:
	"""Wall-clock wait that keeps running through the pause under test. Uses
	process_always=TRUE on purpose -- the test must outlive its own pause."""
	await get_tree().create_timer(seconds, true).timeout


# --- navigation: #1034 ----------------------------------------------------------

var _fade_done: bool = false


func _run_fade_out() -> void:
	await SceneTransition.fade_out()
	_fade_done = true


var _control_done: bool = false


func _run_control_tween(node: Node) -> void:
	var tw := node.create_tween()
	tw.tween_property(node, "position:x", 10.0, 0.05)
	await tw.finished
	_control_done = true


func test_scene_transition_fade_completes_while_paused() -> void:
	# #1034: the fade awaits a Tween bound to SceneTransition. Under the inherited
	# PAUSABLE mode it never finished while paused, so is_transitioning stuck true and
	# ALL later navigation was dropped. The fix is process_mode ALWAYS on the router.
	SceneTransition.fade_duration = 0.05
	var control := Node2D.new()
	add_child_autofree(control)

	_fade_done = false
	_control_done = false
	get_tree().paused = true
	_run_fade_out()
	_run_control_tween(control)
	await _wait_real_seconds(0.5)

	assert_false(
		_control_done,
		"CONTROL: a tween on an ordinary pausable node must NOT finish while paused -- "
		+ "if it did, the tree was not really paused and this test proves nothing."
	)
	assert_true(
		_fade_done,
		"SceneTransition.fade_out() did not finish while the tree was paused (#1034): "
		+ "every later go_to()/reload() would be dropped. Check its process_mode."
	)


func test_navigation_releases_a_pause() -> void:
	# A scene entered paused has no pause menu to unpause it (only main.tscn hosts one).
	get_tree().paused = true
	assert_true(SceneTransition._release_pause(), "must report that it released a pause")
	assert_false(get_tree().paused, "navigation must leave the tree unpaused")
	# Other direction: an unpaused tree is left alone and reported as such.
	assert_false(SceneTransition._release_pause(), "nothing to release when not paused")
	assert_false(get_tree().paused)


# --- diagnostics: #1028 ---------------------------------------------------------


func _key(keycode: int) -> InputEventKey:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.pressed = true
	return ev


func test_diagnostic_hotkeys_still_dispatch_while_paused() -> void:
	# #1028: every global diagnostic bind lives in KeybindManager._input. Inheriting
	# PAUSABLE killed screenshot / log export / F3 / flight recorder the moment the
	# pause menu opened -- exactly when a player is trying to capture something odd.
	var vp := KeybindManager.get_viewport()
	if vp.gui_get_focus_owner():
		vp.gui_get_focus_owner().release_focus()
	var f3: int = KeybindManager.keybinds["debug_overlay"]["key"]
	watch_signals(KeybindManager)

	get_tree().paused = true
	assert_true(
		KeybindManager.can_process(),
		"KeybindManager must keep processing while the tree is paused (#1028)"
	)
	vp.push_input(_key(f3))
	assert_signal_emit_count(
		KeybindManager,
		"debug_overlay_toggled",
		1,
		"the debug-overlay bind must still dispatch while paused (#1028)"
	)

	# Other direction: the gameplay surface beside it really is paused. MainUI and
	# everything else that is not explicitly exempt answers false here.
	var gameplay := Control.new()
	add_child_autofree(gameplay)
	assert_false(
		gameplay.can_process(),
		"CONTROL: an ordinary node must NOT process while paused -- gameplay input stops"
	)
	get_tree().paused = false
	# Toggled once above; toggle back so no listener is left in a flipped state.
	vp.push_input(_key(f3))


# --- messages freeze ------------------------------------------------------------


func test_toast_lifetime_does_not_run_down_behind_the_pause_menu() -> void:
	var nm = get_node_or_null("/root/NotificationManager")
	assert_not_null(nm, "NotificationManager autoload should exist")
	if nm.active_notifications.size() >= nm.MAX_NOTIFICATIONS:
		pending("toast slots already full from an earlier test; cannot measure")
		return

	get_tree().paused = true
	nm.show_notification("pause-semantics probe", nm.NotificationType.INFO, 1.0)
	await get_tree().process_frame
	var panel: Control = nm.active_notifications.back()
	assert_not_null(panel, "the toast must have been created")

	# Paused for longer than the toast's whole lifetime. Before #1343 the lifetime
	# clock ignored the pause, so on unpause the toast slid straight back out
	# (gone within SLIDE_DURATION) -- a message the player never saw.
	await _wait_real_seconds(1.3)
	get_tree().paused = false
	await _wait_real_seconds(nm.SLIDE_DURATION + 0.25)
	assert_true(
		is_instance_valid(panel) and nm.active_notifications.has(panel),
		(
			"The toast expired while the tree was PAUSED (#1343): it vanished %.2fs "
			+ "after unpausing despite a 1.0s lifetime. Check the create_timer in "
			+ "notification_manager.gd passes process_always=false."
		) % (nm.SLIDE_DURATION + 0.25)
	)

	# Other direction: once unpaused, the lifetime DOES run and the toast goes away.
	await _wait_real_seconds(1.0 + nm.SLIDE_DURATION + 0.4)
	assert_false(
		is_instance_valid(panel) and nm.active_notifications.has(panel),
		"the toast never expired after unpausing -- the lifetime clock is dead"
	)

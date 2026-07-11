extends GutTest
## Regression tests: global keybinds must yield to focused text fields (#575, #567).
##
## KeybindManager.is_text_input_focused() is the shared gate used by the autoload's
## own _input and by MainUI's shortcut handling. When a LineEdit/TextEdit owns focus
## (e.g. the bug-report form), pressing a bound key must NOT fire the global shortcut,
## so the character reaches the field instead.

var line_edit: LineEdit

func after_each():
	# Release any focus we grabbed so tests don't leak state into each other.
	var vp = KeybindManager.get_viewport()
	if vp and vp.gui_get_focus_owner():
		vp.gui_get_focus_owner().release_focus()
	if is_instance_valid(line_edit):
		line_edit.queue_free()
	line_edit = null

func _make_key_event(keycode: int) -> InputEventKey:
	var ev = InputEventKey.new()
	ev.keycode = keycode
	ev.pressed = true
	return ev

func _clear_focus():
	var vp = KeybindManager.get_viewport()
	if vp and vp.gui_get_focus_owner():
		vp.gui_get_focus_owner().release_focus()

func test_gate_true_when_line_edit_focused():
	line_edit = LineEdit.new()
	add_child_autofree(line_edit)
	line_edit.grab_focus()
	await get_tree().process_frame
	assert_true(KeybindManager.is_text_input_focused(),
		"Gate should report text focus while a LineEdit owns focus")

func test_gate_false_when_nothing_focused():
	_clear_focus()
	await get_tree().process_frame
	assert_false(KeybindManager.is_text_input_focused(),
		"Gate should be false when no text field is focused")

# Use the admin_mode bind for behavioural checks: admin_mode_toggled has no autoload
# listener, so emitting it in a headless test has no side effects (unlike
# screenshot_requested, which drives a real save_png on a null headless viewport).
func test_keybind_not_consumed_while_text_focused():
	# With a text field focused, a bound global key must NOT fire — the gate yields
	# the key to the field (#575).
	line_edit = LineEdit.new()
	add_child_autofree(line_edit)
	line_edit.grab_focus()
	await get_tree().process_frame

	var admin_key = KeybindManager.keybinds["admin_mode"]["key"]
	watch_signals(KeybindManager)
	KeybindManager._input(_make_key_event(admin_key))
	assert_signal_not_emitted(KeybindManager, "admin_mode_toggled",
		"Global keybind must yield to a focused text field (#575)")

func test_keybind_fires_when_no_text_focus():
	# Sanity check the other direction: same key DOES fire when nothing is focused,
	# so the gate isn't just disabling the shortcut outright.
	_clear_focus()
	await get_tree().process_frame

	var admin_key = KeybindManager.keybinds["admin_mode"]["key"]
	watch_signals(KeybindManager)
	KeybindManager._input(_make_key_event(admin_key))
	assert_signal_emitted(KeybindManager, "admin_mode_toggled",
		"Global keybind should fire normally when no text field is focused")

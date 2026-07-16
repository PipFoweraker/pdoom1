extends GutTest
## Lane 1 / Phase A: the PLAN<->WATCH mode controller (scripts/ui/screen_mode.gd).
## The month LOOP itself is covered by test_month_button_path.gd; this guards the UI
## SEAM — that committing flips plan-only panels off / watch-only panels on, and back.

var ctrl: ScreenModeController
var plan_panel: Control
var watch_panel: Control


func before_each():
	ctrl = ScreenModeController.new()
	add_child_autofree(ctrl)
	plan_panel = Control.new()
	watch_panel = Control.new()
	add_child_autofree(plan_panel)
	add_child_autofree(watch_panel)
	ctrl.register_plan_only(plan_panel)
	ctrl.register_watch_only(watch_panel)


func test_starts_showing_plan_hiding_watch():
	ctrl.enter_plan()
	assert_eq(ctrl.current_mode, ScreenModeController.Mode.PLAN, "in PLAN mode")
	assert_true(plan_panel.visible, "plan-only panel visible in PLAN")
	assert_false(watch_panel.visible, "watch-only panel hidden in PLAN")


func test_commit_transitions_to_watch():
	"""COMMIT THE MONTH: PLAN -> WATCH hides the plan hand, reveals the watch strip."""
	ctrl.enter_plan()
	ctrl.enter_watch()
	assert_eq(ctrl.current_mode, ScreenModeController.Mode.WATCH, "in WATCH mode")
	assert_false(plan_panel.visible, "plan-only panel hidden in WATCH")
	assert_true(watch_panel.visible, "watch-only panel visible in WATCH")


func test_review_returns_to_plan():
	"""Month review closes back into PLAN — the loop is closed."""
	ctrl.enter_watch()
	ctrl.enter_plan()
	assert_true(plan_panel.visible, "plan panel back on return to PLAN")
	assert_false(watch_panel.visible, "watch strip hidden back in PLAN")


func test_mode_changed_signal_fires():
	watch_signals(ctrl)
	ctrl.enter_watch()
	assert_signal_emitted(ctrl, "mode_changed")


func test_speed_dial_emits_speed_changed():
	"""The WATCH speed dial drives day_tick_seconds via speed_changed (a REAL control)."""
	var bar := ctrl.build_watch_bar()
	add_child_autofree(bar)
	watch_signals(ctrl)
	# Find a speed button ("2x") in the built strip and press it.
	var pressed_any := false
	for b in _all_buttons(bar):
		if b.text == "2x":
			b.emit_signal("pressed")
			pressed_any = true
			break
	assert_true(pressed_any, "found the 2x speed button in the watch strip")
	assert_signal_emitted(ctrl, "speed_changed")


func test_watch_readout_updates_from_state():
	ctrl.build_watch_bar()
	var state := {
		"calendar": {"year": 2034, "month": 3, "day": 12},
		"month_plan": {"attention_total": 20, "attention_spent": 6, "attention_reserved": 0},
	}
	# Should not error and should reflect the day; assert via no crash + label text.
	ctrl.update_from_state(state)
	assert_string_contains(ctrl._day_label.text, "day 12", "day readout reflects the calendar")
	assert_string_contains(ctrl._reserve_label.text, "reserve", "reserve readout present")


func _all_buttons(n: Node) -> Array:
	var out: Array = []
	if n is Button:
		out.append(n)
	for c in n.get_children():
		out.append_array(_all_buttons(c))
	return out

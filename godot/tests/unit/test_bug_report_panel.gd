extends GutTest
## Regression tests for the bug-report panel Submit button state (#603).
##
## After submitting, the panel flashes a "thanks" state; the Submit button must be
## disabled there so it can't be clicked again, and re-enabled when the panel is reused.

func _make_panel():
	var scene = load("res://scenes/ui/bug_report_panel.tscn")
	var panel = scene.instantiate()
	add_child_autofree(panel)  # triggers _ready(), binding @onready node refs
	return panel

func test_submit_enabled_by_default():
	var panel = _make_panel()
	assert_false(panel.submit_button.disabled, "Submit should start enabled")

func test_submit_disabled_in_thanks_state():
	# _on_report_saved is a coroutine (it awaits a reset timer); the synchronous prefix
	# disables the button, which is what we assert. The node is freed at teardown, so the
	# pending timer resume is dropped rather than touching a freed instance.
	var panel = _make_panel()
	panel._on_report_saved("user://dummy_report.json")
	assert_true(panel.submit_button.disabled,
		"Submit should be disabled in the thanks/submitted state (#603)")

func test_reset_form_reenables_submit():
	var panel = _make_panel()
	panel.submit_button.disabled = true  # simulate the post-submit state
	panel.reset_form()
	assert_false(panel.submit_button.disabled,
		"reset_form should re-enable Submit so the panel is reusable (#603)")

extends GutTest
## Regression tests for the F3 debug overlay (#600).
##
## Bug: the Errors tab rendered `error.to_string()` inside a `[color=...]` BBCode tag on a plain
## Label. ErrorHandler.GameError (an inner class extending RefCounted) has no `_to_string()`, so
## `to_string()` returned "<RefCounted#...>" and the Label showed the BBCode literally -- every
## entry read like "color white refcounted ...". The fix renders `format_message()` with a real
## font-colour override. These tests lock that in.

const DEBUG_OVERLAY := preload("res://scenes/debug_overlay.tscn")


func _fresh_overlay():
	var overlay = DEBUG_OVERLAY.instantiate()
	add_child_autofree(overlay)
	return overlay


func test_error_list_shows_readable_messages_not_refcounted():
	ErrorHandler.clear_history()
	ErrorHandler.report_err(ErrorHandler.Category.TURN, "regression_probe_boom", {"n": 1})

	var overlay = _fresh_overlay()
	overlay.update_errors()

	var errors_list = overlay.errors_list
	var found := false
	for child in errors_list.get_children():
		if child is Label:
			var t: String = child.text
			assert_false(t.contains("RefCounted"),
				"#600: error rows must not render as '<RefCounted#...>'")
			assert_false(t.begins_with("[color="),
				"#600: plain Labels must not carry literal BBCode color tags")
			if t.contains("regression_probe_boom"):
				found = true
	assert_true(found, "the logged error's readable message must appear in the Errors tab")


func test_error_stats_header_has_no_literal_bbcode():
	ErrorHandler.clear_history()
	ErrorHandler.report_err(ErrorHandler.Category.TURN, "probe", {})

	var overlay = _fresh_overlay()
	overlay.update_errors()

	for child in overlay.errors_list.get_children():
		if child is Label:
			assert_false(child.text.contains("[b]"),
				"stats header must not show literal [b] tags on a plain Label")

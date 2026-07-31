extends GutTest
## Regression tests for the achievement toast presentation (the v0.13.2
## "giant unstyled purple rectangle" bug).
##
## Shipped failure: the ACHIEVEMENT toast rendered as a flat violet panel
## ~400x950 covering the right third of the screen. Mechanism: the autowrap
## message Label measured at ~zero width on the first layout pass (one glyph
## per line -> ~950px minimum height), the PanelContainer inflated to fit,
## and -- being a ROOT-level Control with no parent container -- nothing ever
## re-laid it out when the minimum collapsed a frame later. These tests pin
## both halves of the fix plus the palette swap away from debug purple.

var _nm = null


func before_each():
	_nm = get_node_or_null("/root/NotificationManager")


func _build_achievement_panel() -> PanelContainer:
	return _nm._build_notification_panel({
		"message": "Achievement -- Personnel File Opened",
		"type": _nm.NotificationType.ACHIEVEMENT,
	})


func test_settle_collapses_inflated_toast():
	# The persistence half of the bug: a root-level Control keeps a bogus
	# inflated size forever unless something resets it. Simulate the shipped
	# degenerate first pass, then assert _settle_toast_size collapses it.
	assert_not_null(_nm, "NotificationManager autoload should exist")
	var panel := _build_achievement_panel()
	get_tree().root.add_child(panel)
	panel.size = Vector2(400, 950)  # what v0.13.2 actually rendered
	await _nm._settle_toast_size(panel)
	assert_lte(panel.size.y, 120.0,
		"toast must settle back to content height, not keep the inflated 950px")
	assert_lte(panel.size.x, 410.0, "toast width should stay ~400px")
	panel.queue_free()


func test_achievement_toast_minimum_is_compact():
	# The measurement half: with the wrap width pinned, the real shipped
	# message must never report a near-screen-height minimum.
	assert_not_null(_nm, "NotificationManager autoload should exist")
	var panel := _build_achievement_panel()
	get_tree().root.add_child(panel)
	await get_tree().process_frame
	await get_tree().process_frame
	var min_size: Vector2 = panel.get_combined_minimum_size()
	assert_lte(min_size.y, 120.0,
		"a one-line achievement toast should be ~70px tall, not screen-height")
	panel.queue_free()


func test_achievement_palette_is_amber_leather_not_debug_purple():
	# Presentation contract: achievement chrome uses the warm ledger register
	# (dark leather bg, amber border), not the retired violet placeholder.
	assert_not_null(_nm, "NotificationManager autoload should exist")
	var bg: Color = _nm._get_notification_color(_nm.NotificationType.ACHIEVEMENT)
	var border: Color = _nm._get_notification_border_color(_nm.NotificationType.ACHIEVEMENT)
	assert_gt(bg.r, bg.b,
		"achievement background should read warm (r > b), not violet (was r 0.5 < b 0.8)")
	assert_lt(bg.get_luminance(), 0.25, "achievement background should stay dark")
	assert_gt(border.r, border.b, "achievement border should be amber, not lilac")


func test_toast_click_requests_early_dismiss():
	assert_not_null(_nm, "NotificationManager autoload should exist")
	var panel := _build_achievement_panel()
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	_nm._on_toast_gui_input(click, panel)
	assert_true(bool(panel.get_meta("dismiss_early", false)),
		"a mouse press on the toast should flag it for early dismissal")
	panel.free()

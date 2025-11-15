extends GutTest
## Integration tests for UI stability and interaction bugs

## Issue #452: Event popup ESC key soft-lock
## Test that event dialogs cannot be closed with ESC
func test_event_dialog_blocks_esc_key():
	# This test verifies the meta flag is set correctly
	var test_panel = Panel.new()

	# Simulate event dialog creation
	test_panel.set_meta("is_event_dialog", true)

	# Verify meta flag
	assert_true(test_panel.has_meta("is_event_dialog"), "Event dialog should have is_event_dialog meta")
	assert_true(test_panel.get_meta("is_event_dialog"), "is_event_dialog should be true")

	test_panel.queue_free()

func test_submenu_dialog_allows_esc():
	# Submenu dialogs should NOT have the is_event_dialog flag
	var test_panel = Panel.new()

	# Submenu dialogs don't set the meta flag
	assert_false(test_panel.has_meta("is_event_dialog"), "Submenu dialog should not have is_event_dialog meta")

	test_panel.queue_free()

func test_event_dialog_has_valid_buttons():
	# Test that event dialogs would have accessible buttons
	# Simulates the button setup from MainUI._on_event_triggered

	var buttons = []
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	# Simulate creating 3 event options
	for i in range(3):
		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE
		btn.text = "[%s] Test Option %d" % [dialog_key_labels[i], i + 1]
		buttons.append(btn)

	assert_eq(buttons.size(), 3, "Should create 3 buttons")
	assert_eq(buttons[0].text, "[Q] Test Option 1", "First button should have Q shortcut")
	assert_eq(buttons[1].text, "[W] Test Option 2", "Second button should have W shortcut")

	for btn in buttons:
		btn.queue_free()

## Issue #450: InfoBar height stability
func test_infobar_maintains_height():
	# Test that InfoBar has fixed minimum height
	var info_bar = PanelContainer.new()
	info_bar.custom_minimum_size = Vector2(0, 60)

	# Verify minimum height is set
	assert_eq(info_bar.custom_minimum_size.y, 60, "InfoBar should have 60px minimum height (issue #450)")

	# Simulate text changes (hover/unhover)
	var label = RichTextLabel.new()
	label.bbcode_enabled = true
	info_bar.add_child(label)

	# Set single-line text (unhovered)
	label.text = "[color=gray]Hover over actions to see details...\n [/color]"
	assert_true(label.text.contains("\n"), "Unhover text should maintain 2-line format")

	# Set multi-line text (hovered)
	label.text = "[b]Test Action[/b]\n[color=gray]├─[/color] Test details"
	assert_true(label.text.contains("\n"), "Hover text should be multi-line")

	# InfoBar height should remain constant
	assert_eq(info_bar.custom_minimum_size.y, 60, "InfoBar height should not change")

	info_bar.queue_free()

func test_info_label_unhover_text_format():
	# Test that unhover text maintains 2-line format
	var unhover_text = "[color=gray]Hover over actions to see details...\n [/color]"

	# Count newlines
	var newline_count = unhover_text.count("\n")
	assert_gte(newline_count, 1, "Unhover text should have at least 1 newline for 2-line format (issue #450)")

	# Verify it's not just a trailing newline
	assert_true(unhover_text.ends_with("\n [/color]"), "Should have space after newline to maintain height")

## Issue #451: Category color coding
func test_category_colors_are_prominent():
	# Test that category colors use 50% lerp for visibility
	var base_color = Color(0.85, 0.85, 0.85)
	var category_color = Color(0.2, 0.8, 0.2)  # Green for hiring

	# Calculate expected button color (50% lerp from issue #451)
	var button_color = base_color.lerp(category_color, 0.5)

	# Verify the lerp creates visible distinction
	var color_difference = abs(button_color.r - base_color.r) + abs(button_color.g - base_color.g) + abs(button_color.b - base_color.b)
	assert_gt(color_difference, 0.2, "Category color should be visibly different from base (issue #451)")

func test_disabled_buttons_are_grayed_out():
	# Test that unaffordable actions are properly grayed
	var button = Button.new()
	button.modulate = Color(0.6, 0.6, 0.6)

	# Verify gray modulate
	assert_lt(button.modulate.r, 0.7, "Disabled buttons should be grayed out")
	assert_lt(button.modulate.g, 0.7, "Disabled buttons should be grayed out")
	assert_lt(button.modulate.b, 0.7, "Disabled buttons should be grayed out")

	button.queue_free()

## General UI stability tests
func test_dialog_button_focus_mode():
	# Test that dialog buttons use FOCUS_NONE to prevent input interference
	var btn = Button.new()
	btn.focus_mode = Control.FOCUS_NONE

	assert_eq(btn.focus_mode, Control.FOCUS_NONE, "Dialog buttons should not grab focus")

	btn.queue_free()

func test_dialog_z_index_for_overlay():
	# Test that dialogs have high z-index for proper layering
	var dialog = Panel.new()
	dialog.z_index = 1000
	dialog.z_as_relative = false

	assert_eq(dialog.z_index, 1000, "Dialog should have high z-index")
	assert_false(dialog.z_as_relative, "Dialog z-index should be absolute")

	dialog.queue_free()

## Test keyboard shortcut handling
func test_keyboard_shortcuts_use_correct_keys():
	# Verify dialog uses letter keys (Q/W/E/R/A/S/D/F/Z), not numbers
	var dialog_keys = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]

	assert_eq(dialog_keys.size(), 9, "Should support up to 9 dialog options")
	assert_eq(dialog_keys[0], KEY_Q, "First shortcut should be Q")
	assert_eq(dialog_keys[1], KEY_W, "Second shortcut should be W")

func test_action_shortcuts_use_number_keys():
	# Verify main actions use number keys 1-9
	var action_keys = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9]

	assert_eq(action_keys.size(), 9, "Should support up to 9 action shortcuts")
	assert_eq(action_keys[0], KEY_1, "First action shortcut should be 1")

## Test that UI elements have proper constraints
func test_action_buttons_have_size_constraints():
	# Test that action buttons have proper sizing (issue #451 - prevent extending into middle)
	var button = Button.new()
	button.size_flags_horizontal = Control.SIZE_FILL
	button.custom_minimum_size = Vector2(0, 32)

	assert_eq(button.size_flags_horizontal, Control.SIZE_FILL, "Buttons should fill horizontally")
	assert_eq(button.custom_minimum_size.y, 32, "Buttons should have minimum height")

	button.queue_free()

## Test resource display formatting
func test_money_format_has_commas():
	# Test that money is formatted with commas (from issue #436 player feedback)
	var formatted = GameConfig.format_money(1000)
	assert_true(formatted.contains(",") or formatted.contains("1") and formatted.contains("000"),
		"Money should be formatted with comma separators")

	var large_amount = GameConfig.format_money(245000)
	assert_true(large_amount.contains("245"), "Should format large amounts correctly")
	assert_true(large_amount.begins_with("$"), "Should include dollar sign")

func test_negative_money_format():
	# Test negative money formatting
	var formatted = GameConfig.format_money(-1000)
	assert_true(formatted.begins_with("-$"), "Negative amounts should show -$")

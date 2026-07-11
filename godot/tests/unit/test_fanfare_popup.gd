extends GutTest
## Tests for the FanfarePopup reveal component (#578) and Travel discoverability (#565).

func test_fanfare_scene_loads_and_instantiates():
	var scene = load("res://scenes/ui/fanfare_popup.tscn")
	assert_not_null(scene, "fanfare_popup.tscn should load as a PackedScene")
	var popup = scene.instantiate()
	assert_not_null(popup, "fanfare_popup.tscn should instantiate")
	assert_true(popup is FanfarePopup, "scene root should carry the FanfarePopup script")
	popup.free()

func test_fanfare_present_text_only():
	# The image slot is optional; text-only must work (hero banners land later).
	var popup = FanfarePopup.new()
	add_child_autofree(popup)
	await popup.present("Test Title", "Test body text", "")
	assert_eq(popup._title_label.text, "Test Title", "title should be set")
	assert_eq(popup._body_label.text, "Test body text", "body should be set")
	assert_false(popup._image.visible, "image slot hidden when no path is given")

func test_fanfare_present_ignores_missing_image_path():
	var popup = FanfarePopup.new()
	add_child_autofree(popup)
	await popup.present("T", "B", "res://does/not/exist.png")
	assert_false(popup._image.visible, "non-existent image path should leave the slot hidden")

func test_travel_action_visible_without_papers():
	# #565: Travel must be discoverable in the action list from turn 1, not hotkey-only.
	var state = autofree(GameState.new("test_seed"))
	var travel = GameActions.get_action_by_id("travel")
	assert_eq(travel.get("id", ""), "travel", "travel action should exist")
	assert_true(
		GameActions.is_action_unlocked(travel, state.to_dict()),
		"travel should be unlocked with 0 papers so its action-list button is visible")

extends GutTest
## Rival-intel feed filter (PR #726 review request): the "rivals" feed channel must be
## player-filterable, with the preference persisted (GameConfig / user://config.cfg pattern),
## display-only (no effect on the underlying log content or simulation).
##
## Covers the WATCH-screen toggle wiring (reflects + emits) and the GameConfig round-trip.
## The filter predicate itself (main_ui._feed_passes_filter) is exercised in-game; here we
## pin the persisted preference and the toggle contract that drives it.

const WATCH_SCENE := "res://scenes/ui/watch_screen.tscn"


func _instance(path: String) -> Node:
	var scene: PackedScene = load(path)
	assert_not_null(scene, "scene %s should load" % path)
	var node: Node = scene.instantiate()
	add_child_autofree(node)
	return node


func test_watch_screen_exposes_rivals_filter_toggle():
	var watch = _instance(WATCH_SCENE)
	await get_tree().process_frame
	assert_not_null(watch.rivals_filter_button, "WatchScreen exposes the rival-intel toggle")
	assert_true(watch.has_signal("rivals_filter_changed"), "WatchScreen emits rivals_filter_changed")


func test_rivals_toggle_reflects_persisted_preference():
	var prev: bool = GameConfig.show_rivals_feed
	# show ON -> the "Hide rival intel" toggle is unpressed.
	GameConfig.show_rivals_feed = true
	var w_on = _instance(WATCH_SCENE)
	await get_tree().process_frame
	assert_false(w_on.rivals_filter_button.button_pressed,
		"show_rivals_feed ON -> Hide toggle starts unpressed")
	# show OFF -> the toggle starts pressed (rivals hidden).
	GameConfig.show_rivals_feed = false
	var w_off = _instance(WATCH_SCENE)
	await get_tree().process_frame
	assert_true(w_off.rivals_filter_button.button_pressed,
		"show_rivals_feed OFF -> Hide toggle starts pressed")
	GameConfig.show_rivals_feed = prev


func test_rivals_toggle_emits_on_flip():
	var watch = _instance(WATCH_SCENE)
	await get_tree().process_frame
	watch_signals(watch)
	var before: bool = watch.rivals_filter_button.button_pressed
	watch.rivals_filter_button.button_pressed = not before  # user flips the toggle
	assert_signal_emitted(watch, "rivals_filter_changed",
		"Flipping the toggle emits rivals_filter_changed")


func test_show_rivals_feed_persists_across_save_load():
	var prev: bool = GameConfig.show_rivals_feed
	# Persist OFF, clobber in memory, reload -> the persisted OFF wins.
	GameConfig.show_rivals_feed = false
	GameConfig.save_config()
	GameConfig.show_rivals_feed = true
	GameConfig.load_config()
	assert_false(GameConfig.show_rivals_feed,
		"show_rivals_feed survives save -> load (persisted preference)")
	# Restore the original value on disk so the test is net-neutral.
	GameConfig.show_rivals_feed = prev
	GameConfig.save_config()

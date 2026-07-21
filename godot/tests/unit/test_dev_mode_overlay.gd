extends GutTest
## Tests for the DEV MODE overlay (backslash) -- keybind registration + the pure readout builder.
##
## Covers: the dev_mode action is registered on backslash and the old backslash conflicts were
## moved off it; pressing backslash fires dev_mode_toggled; and DevModeReadout.build_sections()
## produces non-empty, titled sections from a sample GameState. The actual on-screen
## layout/toggle needs a human eye (noted in the PR).


func _make_key_event(keycode: int) -> InputEventKey:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.pressed = true
	return ev


func test_dev_mode_keybind_registered_on_backslash():
	assert_true(KeybindManager.keybinds.has("dev_mode"),
		"dev_mode action must be registered as a named keybind")
	assert_eq(KeybindManager.keybinds["dev_mode"]["key"], KEY_BACKSLASH,
		"dev_mode should default to the backslash key (owner request)")


func test_backslash_conflicts_moved_off():
	# The two prior backslash users were reclaimed so backslash is unambiguously DEV MODE.
	assert_ne(KeybindManager.keybinds["export_log"]["key"], KEY_BACKSLASH,
		"export_log must no longer sit on backslash")
	assert_ne(KeybindManager.keybinds["bug_reporter"]["key"], KEY_BACKSLASH,
		"bug_reporter must no longer sit on backslash")
	assert_eq(KeybindManager.keybinds["bug_reporter"]["key"], KEY_N,
		"bug_reporter should move to N (already opened it)")


func test_backslash_emits_dev_mode_toggled():
	watch_signals(KeybindManager)
	KeybindManager._input(_make_key_event(KEY_BACKSLASH))
	assert_signal_emitted(KeybindManager, "dev_mode_toggled",
		"Pressing backslash should fire dev_mode_toggled")


func test_readout_sections_non_empty_from_sample_state():
	var state := GameState.new()  # _init + reset() give working doom/risk/rival subsystems
	var sections := DevModeReadout.build_sections(state)
	assert_gt(sections.size(), 0, "Readout must produce at least one section")
	for section in sections:
		assert_true(section.has("title"), "each section has a title")
		assert_true(section.has("lines"), "each section has lines")
		assert_gt(section["lines"].size(), 0,
			"section '%s' should have content" % section.get("title", "?"))
	state.free()


func test_readout_covers_key_domains():
	var state := GameState.new()
	var titles: Array = []
	for section in DevModeReadout.build_sections(state):
		titles.append(str(section["title"]))
	var joined := " | ".join(PackedStringArray(titles))
	assert_string_contains(joined, "Resources", "readout must include resources")
	assert_string_contains(joined, "Doom", "readout must include doom")
	assert_string_contains(joined, "Risk", "readout must include risk pools")
	assert_string_contains(joined, "Rival", "readout must include rival labs")
	assert_string_contains(joined, "Ledger", "readout must include ledger")
	state.free()


func test_readout_handles_null_state():
	var sections := DevModeReadout.build_sections(null)
	assert_gt(sections.size(), 0, "null state must degrade to a placeholder section, not crash")


# --- #600: the overlay must read the LIVE GameState MainUI holds, not the dead autoload ------
#
# main.tscn instances a scene-local GameManager node that MainUI drives; the bareword
# `GameManager` autoload is a different instance whose `state` stays null. These stubs stand in
# for "MainUI holding the live manager" so we can assert the overlay resolves it.

class _FakeGM extends Node:
	signal game_state_updated(state)
	var state
	var turn_manager
	var is_initialized := true

class _FakeMainUI extends Node:
	var game_manager


func test_overlay_resolves_live_manager_from_main_ui():
	var overlay = DevModeOverlay.new()
	var gm = _FakeGM.new()
	var mui = _FakeMainUI.new()
	mui.game_manager = gm
	overlay.main_ui = mui
	assert_eq(overlay._live_gm(), gm,
		"#600: overlay must resolve the live game_manager MainUI holds, not the autoload")
	overlay.free()
	gm.free()
	mui.free()


func test_render_populates_sections_from_live_state():
	# Reproduces #600: with a live-shaped GameState reachable via main_ui.game_manager, the
	# readout must build the full multi-section dump -- not the single "No active game" placeholder.
	var overlay = DevModeOverlay.new()
	var gm = _FakeGM.new()
	gm.state = GameState.new()  # _init + reset() give working doom/risk/rival subsystems
	var mui = _FakeMainUI.new()
	mui.game_manager = gm
	overlay.main_ui = mui
	overlay._info_vbox = VBoxContainer.new()

	overlay._render()

	# Null state -> 1 section -> 3 nodes (head + body + separator). A live state renders ~7
	# sections. Anything well above 3 proves the live path populated, not the placeholder.
	assert_gt(overlay._info_vbox.get_child_count(), 6,
		"live state must render multiple populated sections, not the null placeholder")

	overlay._info_vbox.free()
	gm.state.free()
	overlay.free()
	gm.free()
	mui.free()


func test_backslash_toggle_opens_then_closes():
	# #600: backslash must CLOSE the overlay, not only open it. _on_toggle flips _root.visible;
	# this locks in that a second press hides it. (Live keypress routing still needs a human eye.)
	var overlay = DevModeOverlay.new()
	overlay._built = true
	overlay._root = Control.new()
	overlay._root.visible = false

	overlay._on_toggle()
	assert_true(overlay._root.visible, "first backslash opens dev mode")
	overlay._on_toggle()
	assert_false(overlay._root.visible, "second backslash closes dev mode")

	overlay._root.free()
	overlay.free()

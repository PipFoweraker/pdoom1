extends GutTest
## Tests for the DEV MODE overlay (backslash) — keybind registration + the pure readout builder.
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

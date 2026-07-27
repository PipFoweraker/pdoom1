extends GutTest
## Tests for the UI evolution capture rail (F7) -- Pip's "it went from this...
## to this..." ask (2026-07-27). Covers keybind registration and the pure
## filename/manifest helpers; the actual screenshot (get_viewport().get_texture())
## needs a live rendered viewport, same caveat as test_flight_recorder.gd.


func test_ui_evolution_shot_keybind_registered_on_f7():
	assert_true(KeybindManager.keybinds.has("ui_evolution_shot"),
		"ui_evolution_shot action must be registered as a named keybind")
	assert_eq(KeybindManager.keybinds["ui_evolution_shot"]["key"], KEY_F7,
		"ui_evolution_shot should default to F7")


func test_f7_emits_ui_evolution_shot_requested():
	var ev := InputEventKey.new()
	ev.keycode = KEY_F7
	ev.pressed = true
	watch_signals(KeybindManager)
	KeybindManager._input(ev)
	assert_signal_emitted(KeybindManager, "ui_evolution_shot_requested",
		"Pressing F7 should fire ui_evolution_shot_requested")


# ---------------------------------------------------------------------------
# Pure helpers -- filenames, session dir, manifest entry shape.
# ---------------------------------------------------------------------------

func test_session_dir_is_scoped_by_version():
	assert_eq(UIEvolutionRecorder.session_dir("0.13.1"), "user://ui_evolution/0.13.1")


func test_shot_filename_is_zero_padded_and_sortable():
	var ts := {"year": 2026, "month": 7, "day": 27, "hour": 9, "minute": 5, "second": 3}
	var name1 := UIEvolutionRecorder.shot_filename(1, ts)
	assert_eq(name1, "0001_20260727_090503.png")

	var name10 := UIEvolutionRecorder.shot_filename(10, ts)
	assert_true(name1 < name10, "Shot 0001 sorts before shot 0010 (zero-padded)")


func test_iso_timestamp_format():
	var ts := {"year": 2026, "month": 7, "day": 27, "hour": 9, "minute": 5, "second": 3}
	assert_eq(UIEvolutionRecorder.iso_timestamp(ts), "2026-07-27 09:05:03")


func test_manifest_entry_shape():
	var ts := {"year": 2026, "month": 7, "day": 27, "hour": 9, "minute": 5, "second": 3}
	var entry := UIEvolutionRecorder.manifest_entry(3, ts, "0.13.1", "MainUI", 5, "0003_20260727_090503.png")

	assert_eq(entry["index"], 3)
	assert_eq(entry["timestamp"], "2026-07-27 09:05:03")
	assert_eq(entry["version"], "0.13.1")
	assert_eq(entry["scene"], "MainUI")
	assert_eq(entry["turn"], 5)
	assert_eq(entry["screenshot"], "0003_20260727_090503.png")


func test_manifest_entry_is_json_round_trippable():
	var ts := {"year": 2026, "month": 7, "day": 27, "hour": 9, "minute": 5, "second": 3}
	var entry := UIEvolutionRecorder.manifest_entry(1, ts, "0.13.1", "MainUI", -1, "0001_x.png")
	var text := JSON.stringify(entry)
	var parsed = JSON.parse_string(text)
	assert_true(parsed is Dictionary, "Manifest entry round-trips through JSON as a Dictionary")
	assert_eq(int(parsed.get("index", -1)), 1)

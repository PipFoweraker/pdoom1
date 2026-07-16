extends GutTest
## Tests for the playtest flight recorder (F6) — WORKSHOP_2_BACKLOG "Playtest
## deep-dive protocol". Covers the keybind registration and the pure snapshot/
## manifest helpers; the actual screenshot (get_viewport().get_texture()) needs a
## live rendered viewport and a human eye, per the task spec — not unit-tested here.


func test_flight_recorder_keybind_registered_on_f6():
	assert_true(KeybindManager.keybinds.has("flight_recorder"),
		"flight_recorder action must be registered as a named keybind")
	assert_eq(KeybindManager.keybinds["flight_recorder"]["key"], KEY_F6,
		"flight_recorder should default to F6 (rebound off F9 — Nvidia overlay collision)")


func test_f6_emits_flight_recorder_requested():
	var ev := InputEventKey.new()
	ev.keycode = KEY_F6
	ev.pressed = true
	watch_signals(KeybindManager)
	KeybindManager._input(ev)
	assert_signal_emitted(KeybindManager, "flight_recorder_requested",
		"Pressing F6 should fire flight_recorder_requested")


# ---------------------------------------------------------------------------
# Snapshot serialization — reuses GameState.to_dict() (the save/load path),
# NOT a parallel serializer. This is the piece the task asks to unit-test.
# ---------------------------------------------------------------------------

func test_build_state_snapshot_reuses_to_dict():
	var state := GameState.new("flight_recorder_test_seed")
	var snapshot := FlightRecorder.build_state_snapshot(state)
	var direct := state.to_dict()
	assert_eq(snapshot.hash(), direct.hash(),
		"build_state_snapshot must be exactly state.to_dict() — no parallel serializer")
	assert_true(snapshot.has("turn"), "Snapshot carries the turn field")
	assert_true(snapshot.has("money"), "Snapshot carries scalar resources")
	assert_true(snapshot.has("researchers"), "Snapshot carries the researcher roster")
	state.free()


func test_build_state_snapshot_handles_null_state():
	var snapshot := FlightRecorder.build_state_snapshot(null)
	assert_eq(snapshot, {}, "Null state degrades to an empty dict, not a crash")


func test_build_state_snapshot_is_json_round_trippable():
	# The snapshot must survive JSON.stringify/parse_string (what actually gets
	# written to the *_state.json file) without losing its shape.
	var state := GameState.new("flight_recorder_json_seed")
	state.turn = 7
	var snapshot := FlightRecorder.build_state_snapshot(state)
	var text := JSON.stringify(snapshot, "\t")
	var parsed = JSON.parse_string(text)
	assert_true(parsed is Dictionary, "Snapshot round-trips through JSON as a Dictionary")
	assert_eq(int(parsed.get("turn", -1)), 7, "Turn value survives the JSON round trip")
	state.free()


# ---------------------------------------------------------------------------
# File naming — screenshot/state/note for one press must sort adjacently.
# ---------------------------------------------------------------------------

func test_marker_prefix_is_zero_padded_and_sortable():
	var ts := {"year": 2026, "month": 7, "day": 14, "hour": 9, "minute": 5, "second": 3}
	var prefix := FlightRecorder.marker_prefix(1, ts)
	assert_eq(prefix, "0001_20260714_090503")

	var prefix10 := FlightRecorder.marker_prefix(10, ts)
	assert_true(prefix < prefix10, "Marker 0001 sorts before marker 0010 (zero-padded)")


func test_session_dir_name_format():
	var ts := {"year": 2026, "month": 7, "day": 14, "hour": 9, "minute": 5, "second": 3}
	assert_eq(FlightRecorder.session_dir_name(ts), "session_20260714_090503")


func test_manifest_entry_files_share_marker_prefix_and_sort_adjacently():
	var state := GameState.new("flight_recorder_manifest_seed")
	state.turn = 3
	var entry := FlightRecorder.build_manifest_entry(2, "specimen note", state, "0002_20260714_090503")

	assert_eq(entry["marker_id"], 2)
	assert_eq(entry["turn"], 3)
	assert_eq(entry["note"], "specimen note")

	var files: Dictionary = entry["files"]
	var names: Array = files.values()
	names.sort()
	# All three filenames share the "0002_20260714_090503" prefix, so sorting
	# them alphabetically keeps them adjacent regardless of key order.
	for n in names:
		assert_string_starts_with(String(n), "0002_20260714_090503",
			"Each captured file for one press shares the marker prefix")
	state.free()


func test_manifest_entry_handles_null_state():
	var entry := FlightRecorder.build_manifest_entry(5, "", null, "0005_x")
	assert_eq(entry["turn"], -1, "Null state degrades to turn -1, not a crash")

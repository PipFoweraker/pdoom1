extends GutTest
## ASSERTION GUARD (#1134): no debug/dev surface may WRITE into state.pending_events.
##
## The defect: debug_overlay's "Trigger Random Event" button appended a raw event dict
## straight onto `gm.state.pending_events` behind nothing but `if gm and gm.state`. No
## phase guard. Injected while the run sat in a phase that never drains the queue, the
## queue never emptied -- and TurnManager gates `can_select_actions` on
## `pending_events.size() == 0`, so the run was permanently unplayable. Pip reproduced
## the hard lock repeatably in a release build (2026-08-06) and ruled the feature out:
## "triggering random events doesn't seem so useful for debugging at this point, just
## creating bugs lol."
##
## The fix was DELETION, not a phase guard -- so the guard that keeps it deleted is a
## ban on the whole write path, not a check on one caller. Reading pending_events from
## a debug surface stays legal (the F3 readout prints the queue); touching it does not.
##
## The overlay is instanced unconditionally in main.tscn and its keybind is bound with
## no build check, so this surface is reachable by any player in a shipped build. That
## is why the ban is asserted in the fast gate rather than left to review.

const DEBUG_SCRIPT_DIR := "res://scripts/debug"
const DEBUG_OVERLAY_SCENE := "res://scenes/debug_overlay.tscn"

## Retired entry points. If any of these names comes back in scripts/debug, the feature
## has been resurrected under its old shape.
const RETIRED_SYMBOLS := [
	"_on_trigger_event_button_pressed",
	"_show_event_selection_popup",
	"_trigger_specific_event",
	"_queue_event",
	"_queue_selected_event",
	"_trigger_random_event",
	"_populate_event_dropdown",
]

## Mutating uses of pending_events. Plain reads (.size(), .is_empty(), indexing, `for`)
## are deliberately absent -- looking is free, touching is not.
const MUTATION_PATTERN := "pending_events\\s*(=[^=]|\\+=|\\.\\s*(append|append_array|push_back|push_front|insert|assign|clear|remove_at|erase|resize|pop_front|pop_back|pop_at|fill|reverse|sort|sort_custom|shuffle))"


func _gd_files(dir_path: String, out: Array) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var entry := d.get_next()
	while entry != "":
		if not entry.begins_with("."):
			var full := dir_path.path_join(entry)
			if d.current_is_dir():
				_gd_files(full, out)
			elif entry.get_extension() == "gd":
				out.append(full)
		entry = d.get_next()
	d.list_dir_end()


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var text := f.get_as_text()
	f.close()
	return text


## Drop comments so a tombstone comment naming the banned call does not fail the guard.
## Heuristic: a `#` with an even number of double quotes before it on the line starts a
## comment. Good enough for GDScript that does not embed `#` inside a string literal.
func _strip_comments(source: String) -> String:
	var kept: Array[String] = []
	for line in source.split("\n"):
		var quotes := 0
		var cut := -1
		for i in line.length():
			var ch := line[i]
			if ch == "\"":
				quotes += 1
			elif ch == "#" and quotes % 2 == 0:
				cut = i
				break
		kept.append(line if cut < 0 else line.substr(0, cut))
	return "\n".join(kept)


func test_debug_dir_is_scanned_at_all():
	# Backstop against a silently-empty scan (the #640 lesson: a guard that inspects
	# nothing passes forever).
	var files: Array = []
	_gd_files(DEBUG_SCRIPT_DIR, files)
	assert_gt(files.size(), 2,
		"expected several .gd files under %s -- an empty scan makes this guard hollow" % DEBUG_SCRIPT_DIR)


func test_no_debug_surface_writes_into_pending_events():
	var re := RegEx.new()
	assert_eq(re.compile(MUTATION_PATTERN), OK, "mutation regex must compile")

	var files: Array = []
	_gd_files(DEBUG_SCRIPT_DIR, files)
	var offenders: Array[String] = []
	for path in files:
		var code := _strip_comments(_read(path))
		var line_no := 0
		for line in code.split("\n"):
			line_no += 1
			if re.search(line) != null:
				offenders.append("%s:%d: %s" % [path, line_no, line.strip_edges()])

	assert_eq(offenders.size(), 0,
		"no debug/dev surface may enqueue or edit state.pending_events (#1134 -- the F3 " +
		"event-trigger permalock). Offenders:\n" + "\n".join(offenders))


func test_retired_event_trigger_symbols_are_gone():
	var files: Array = []
	_gd_files(DEBUG_SCRIPT_DIR, files)
	var offenders: Array[String] = []
	for path in files:
		var code := _strip_comments(_read(path))
		for symbol in RETIRED_SYMBOLS:
			if code.contains(symbol):
				offenders.append("%s defines/calls retired symbol %s" % [path, symbol])

	assert_eq(offenders.size(), 0,
		"the debug event-trigger feature was RETIRED by #1134 -- do not reintroduce it. " +
		"Offenders:\n" + "\n".join(offenders))


func test_debug_overlay_scene_has_no_event_trigger_control():
	var scene_text := _read(DEBUG_OVERLAY_SCENE)
	assert_gt(scene_text.length(), 0, "debug_overlay.tscn must be readable")
	assert_false(scene_text.contains("TriggerEventButton"),
		"debug_overlay.tscn still carries the retired Trigger Event button (#1134)")
	assert_false(scene_text.contains("_on_trigger_event_button_pressed"),
		"debug_overlay.tscn still connects a signal to the retired trigger-event handler (#1134)")

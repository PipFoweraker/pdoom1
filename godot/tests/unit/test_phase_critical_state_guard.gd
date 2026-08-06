extends GutTest
## Phase-critical state guard -- the CLASS behind #1134, not the instance.
##
## #1134 was a silent PERMALOCK: debug_overlay appended to `state.pending_events` from a
## phase whose drain path refuses, so `GameManager.select_action` hard-refused every action
## forever and the event modal (PRIORITY_MUST_ANSWER, ESC-proof, closes only on SUCCESS)
## could never be satisfied. No error, no crash, run dead.
##
## PR #1143 retired the offending feature. This file guards the SPECIES: a caller mutating
## state that the phase machine depends on, without knowing which phase it is in.
##
## The audit that produced the allowlists below (enumerated state, writer classification,
## reachability calls) is docs/design/PHASE_GUARD_AUDIT_2026-08-06.md. If a test here fails,
## read that document BEFORE widening an allowlist -- the allowlist is the conclusion of a
## reachability argument, not a convenience list.
##
## Scope note: this is a SOURCE SCAN, not a runtime assertion. It cannot prove a writer is
## phase-safe; it can only prove that no NEW file started writing phase-critical state
## without a human re-running the reachability argument. That blind spot is stated in the
## audit doc under "what each mechanism misses".

const SCAN_ROOTS := ["res://scripts", "res://autoload"]

# Mutating operations on an Array/enum field. Reads (.size(), .is_empty(), indexing) are
# deliberately legal -- looking is free, touching is not.
const MUTATORS := "append|clear|erase|remove_at|insert|assign|resize|push_back|push_front|pop_back|pop_front|append_array|sort|shuffle|reverse|fill"

# Phase-critical state: every variable whose VALUE gates a phase transition or gates the
# player's ability to act. Value = list of files permitted to mutate it through a
# `state`-rooted receiver (`state.X`, `gm.state.X`, `game_manager.state.X`).
#
# PENDING_REMOVAL_1143: the two scripts/debug entries exist only because PR #1143 (which
# deletes both writers) had not merged when this guard landed. The allowlist is PERMISSIVE
# -- an entry that no longer writes is fine -- so #1143 merges green, and the entries should
# then be deleted from this list. Do not add to that pair.
const ALLOWED := {
	"pending_events": [
		"res://scripts/core/baseline_simulator.gd",
		"res://scripts/core/game_state.gd",
		"res://scripts/core/month_controller.gd",
		"res://scripts/core/replay_simulator.gd",
		"res://scripts/core/seed_schedule.gd",
		"res://scripts/core/turn_manager.gd",
		"res://scripts/debug/debug_overlay.gd",      # PENDING_REMOVAL_1143
		"res://scripts/debug/dev_mode_overlay.gd",   # PENDING_REMOVAL_1143
	],
	"current_phase": [
		"res://scripts/core/game_state.gd",
		"res://scripts/core/month_controller.gd",
		"res://scripts/core/turn_manager.gd",
	],
	"can_end_turn": [
		"res://scripts/core/game_state.gd",
		"res://scripts/core/month_controller.gd",
		"res://scripts/core/turn_manager.gd",
	],
	"queued_actions": [
		"res://scripts/core/conference_trip.gd",
		"res://scripts/core/game_state.gd",
		"res://scripts/core/replay_simulator.gd",
		"res://scripts/core/turn_manager.gd",
		"res://scripts/game_manager.gd",
		"res://scripts/ui/plan_controller.gd",  # append_reserve_all: audited, UNLOCK-direction only
	],
	"game_over": [
		"res://scripts/core/game_state.gd",
	],
}

# `event_triggered` raises the ESC-proof MUST_ANSWER modal. Emitting it from a phase whose
# resolution path refuses is the #1134 permalock in its purest form, so the emitter set is
# closed to the one file whose emit sites were each checked against a drain path.
const EVENT_TRIGGERED_EMITTERS := [
	"res://scripts/game_manager.gd",
	"res://scripts/debug/debug_overlay.gd",  # PENDING_REMOVAL_1143
]

var _sources: Dictionary = {}  # path -> comment-stripped source


func before_all() -> void:
	for root in SCAN_ROOTS:
		_collect(root)


func _collect(dir_path: String) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		var full := dir_path.path_join(name)
		if dir.current_is_dir():
			_collect(full)
		elif name.ends_with(".gd"):
			var f := FileAccess.open(full, FileAccess.READ)
			if f != null:
				_sources[full] = _strip_comments(f.get_as_text())
				f.close()
		name = dir.get_next()
	dir.list_dir_end()


func _strip_comments(src: String) -> String:
	# Line-level comment strip. A '#' inside a string literal would be over-stripped, which
	# can only ever HIDE a match -- so the failure mode is a missed violation, never a false
	# alarm. Stated rather than solved: a false alarm would erode trust in the guard, a miss
	# is caught by the next reader.
	var out := PackedStringArray()
	for line in src.split("\n"):
		var idx := line.find("#")
		out.append(line if idx < 0 else line.substr(0, idx))
	return "\n".join(out)


func _mutation_regex(varname: String) -> RegEx:
	var re := RegEx.new()
	# Receiver must END in the token `state`, which catches `state.`, `gm.state.`,
	# `game_manager.state.` and rejects PlanController's own local `queued_actions`.
	# NOTE: a preceding '.' must be ALLOWED (that is exactly `gm.state.`). An earlier draft
	# excluded it and silently matched nothing in the two files that carried the live #1134
	# defect -- a hollow guard that passed for the wrong reason. Kept as a comment because
	# "the guard compiled and went green" is not evidence; test_scanner_finds_the_known_
	# offender_shape below pins the shape this regex must catch.
	var err := re.compile("(^|[^A-Za-z0-9_])state\\.%s\\s*(=[^=]|\\.\\s*(%s)\\s*\\()" % [varname, MUTATORS])
	assert_eq(err, OK, "regex for %s must compile" % varname)
	return re


func _hits(varname: String) -> Array:
	"""Every `<something>state.<varname>` MUTATION site, as {path, line, text}."""
	var re := _mutation_regex(varname)
	var found: Array = []
	for path in _sources:
		var lines: PackedStringArray = _sources[path].split("\n")
		for i in lines.size():
			if re.search(lines[i]) != null:
				found.append({"path": path, "line": i + 1, "text": lines[i].strip_edges()})
	return found


# ---- 0: backstop. A guard that scans nothing is worse than no guard (#640). -------------

func test_scan_actually_reads_the_source_tree():
	assert_gt(_sources.size(), 100,
		"scan found only %d .gd files under %s -- a hollow guard passes vacuously" % [
			_sources.size(), ", ".join(SCAN_ROOTS)])
	assert_true(_sources.has("res://scripts/core/turn_manager.gd"),
		"turn_manager.gd must be in the scan: it OWNS the phase machine")
	assert_true(_sources.has("res://scripts/game_manager.gd"),
		"game_manager.gd must be in the scan: it owns the select_action gate")


func test_scanner_finds_the_known_core_writers():
	# Second backstop: the regex must actually match real code. If TurnManager's writes stop
	# being found, the regex has rotted and every other test here is passing vacuously.
	var pending: Array = _hits("pending_events")
	var tm_hits := 0
	for h in pending:
		if String(h["path"]) == "res://scripts/core/turn_manager.gd":
			tm_hits += 1
	assert_gt(tm_hits, 0,
		"scanner found ZERO pending_events mutations in turn_manager.gd -- regex has rotted")
	assert_gt(_hits("current_phase").size(), 0, "scanner must find current_phase writers")
	assert_gt(_hits("queued_actions").size(), 0, "scanner must find queued_actions writers")


func test_scanner_finds_the_known_offender_shape():
	# THIRD backstop, and the one that matters most. The first draft of the regex excluded a
	# preceding '.', so it matched ZERO of `gm.state.pending_events.append(...)` -- precisely
	# the line that permalocked Pip's run in #1134. It went green for the wrong reason. These
	# literals pin the shapes the scanner must catch and the ones it must not.
	var re := _mutation_regex("pending_events")
	var must_catch := [
		"	gm.state.pending_events.append(event)",                      # #1134, debug_overlay
		"	game_manager.state.pending_events.append({\"id\": x})",       # deeper receiver chain
		"	state.pending_events.clear()",                               # bare receiver
		"	state.pending_events = triggered_events",                    # whole-array replace
	]
	for line in must_catch:
		assert_ne(re.search(line), null, "scanner MUST catch: %s" % line.strip_edges())
	var must_ignore := [
		"	if state.pending_events.size() > 0:",       # reads stay legal -- looking is free
		"	for e in state.pending_events:",
		"	if state.pending_events == other:",         # comparison, not assignment
		"	queued_pending_events.append(x)",           # unrelated local with a similar name
	]
	for line in must_ignore:
		assert_eq(re.search(line), null, "scanner must NOT flag: %s" % line.strip_edges())


# ---- 1: the allowlists ------------------------------------------------------------------

func test_only_audited_files_mutate_phase_critical_state():
	var violations: Array = []
	for varname in ALLOWED:
		var allowed: Array = ALLOWED[varname]
		for h in _hits(varname):
			if not allowed.has(String(h["path"])):
				violations.append("%s:%d mutates state.%s -- %s" % [
					h["path"], h["line"], varname, h["text"]])
	assert_eq(violations.size(), 0,
		("NEW writer(s) of phase-critical state, unaudited:\n  %s\n\n"
		+ "This is the #1134 species: a caller mutating state the phase machine depends on "
		+ "without knowing which phase it is in. Before widening ALLOWED, run the "
		+ "reachability argument in docs/design/PHASE_GUARD_AUDIT_2026-08-06.md: can this "
		+ "line execute in a phase where the drain path refuses? If yes, it is a silent "
		+ "permalock, not a style issue.") % "\n  ".join(violations))


# ---- 2: the MUST_ANSWER modal ------------------------------------------------------------

func test_event_triggered_is_emitted_only_from_audited_files():
	var re := RegEx.new()
	assert_eq(re.compile("event_triggered\\s*\\.\\s*emit\\s*\\(|emit_signal\\s*\\(\\s*[\"']event_triggered[\"']"), OK)
	var violations: Array = []
	var total := 0
	for path in _sources:
		var lines: PackedStringArray = _sources[path].split("\n")
		for i in lines.size():
			if re.search(lines[i]) == null:
				continue
			total += 1
			if not EVENT_TRIGGERED_EMITTERS.has(path):
				violations.append("%s:%d -- %s" % [path, i + 1, lines[i].strip_edges()])
	assert_gt(total, 0, "scanner found ZERO event_triggered emit sites -- regex has rotted")
	assert_eq(violations.size(), 0,
		("event_triggered raised from an unaudited file:\n  %s\n\n"
		+ "event_triggered opens the PRIORITY_MUST_ANSWER modal. It is ESC-proof (#452) and "
		+ "closes ONLY on a successful resolve. TurnManager.resolve_event refuses unless "
		+ "current_phase == TURN_START, and MonthController only answers while is_paused(). "
		+ "Emitting outside those two conditions is an unanswerable modal = permalock.") % "\n  ".join(violations))


# ---- 3: the drain-path invariant is still where the audit says it is ---------------------

func test_resolve_event_still_refuses_outside_turn_start():
	# The whole audit rests on this refusal existing. If someone relaxes it, the allowlists
	# above are guarding a rule that no longer holds -- fail loudly rather than silently
	# guard the wrong invariant.
	var src: String = _sources.get("res://scripts/core/turn_manager.gd", "")
	assert_ne(src, "", "turn_manager.gd source must be readable")
	var re := RegEx.new()
	assert_eq(re.compile("state\\.current_phase\\s*!=\\s*GameState\\.TurnPhase\\.TURN_START"), OK)
	assert_ne(re.search(src), null,
		"TurnManager.resolve_event no longer refuses outside TURN_START. That refusal is the "
		+ "reason an out-of-phase pending event is unanswerable -- if the drain path changed, "
		+ "re-run docs/design/PHASE_GUARD_AUDIT_2026-08-06.md before trusting this file.")


func test_select_action_still_refuses_on_pending_events():
	var src: String = _sources.get("res://scripts/game_manager.gd", "")
	assert_ne(src, "", "game_manager.gd source must be readable")
	var re := RegEx.new()
	assert_eq(re.compile("state\\.pending_events\\.size\\(\\)\\s*>\\s*0"), OK)
	assert_ne(re.search(src), null,
		"GameManager.select_action no longer gates on pending_events. That gate is what turns "
		+ "a stray pending event into a permalock -- the audit's severity ranking depends on it.")

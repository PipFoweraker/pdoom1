extends GutTest
## Tests for PerfLog -- the dev-mode turn-timing + anomaly tripwire logger.
##
## Covers the load-bearing contract:
##   - timing records land in the rolling log (begin/end AND the Stopwatch helper),
##   - the wall-time threshold WARNING fires when a section runs over,
##   - the loop-iteration tripwire fires past a sane bound and stays quiet under it,
##   - the dev gate suppresses ALL recording/warnings when inactive (release cut).
##
## Hermetic: file logging is disabled and the override forces the gate, so the suite does
## not depend on the DEV_BUILD const nor write to user://.
##
## #976: PerfLog is a shared autoload singleton with NO test gating of its own callers --
## turn_manager.gd/office_floor.gd/event_service.gd call it unconditionally, so across a
## full-suite run they write real lines to the real LOG_PATH the entire time (DEV_BUILD is a
## hardcoded true const). reset_for_tests() below resets every piece of shared state
## (including the _thresholds map, which before_each/after_each never used to touch) so
## nothing this file sets can leak into another test file, in either direction.

var _anomaly_count := 0


func before_each() -> void:
	PerfLog.reset_for_tests()
	PerfLog.set_file_logging(false)
	PerfLog.set_enabled_override(true)  # force-active regardless of DEV_BUILD
	_anomaly_count = 0


func after_each() -> void:
	PerfLog.reset_for_tests()


func _on_anomaly(_msg: String) -> void:
	_anomaly_count += 1


# --- Timing records --------------------------------------------------------

func test_begin_end_records_a_timing_entry():
	PerfLog.begin("unit_section", {"turn": 7})
	var ms := PerfLog.end("unit_section")
	assert_gte(ms, 0.0, "elapsed should be a non-negative millisecond count")
	var entries := PerfLog.get_entries()
	assert_eq(entries.size(), 1, "one begin/end pair should record exactly one entry")
	assert_eq(entries[0]["section"], "unit_section", "entry should carry the section name")
	assert_eq(entries[0]["ctx"]["turn"], 7, "entry should carry the caller context")
	assert_false(entries[0]["over"], "a fast section under the default threshold is not flagged")


func test_end_without_begin_is_a_noop():
	var ms := PerfLog.end("never_started")
	assert_eq(ms, 0.0, "ending an unopened section returns 0 and records nothing")
	assert_eq(PerfLog.get_entries().size(), 0, "no entry from an unmatched end()")


func test_stopwatch_helper_records_a_timing_entry():
	var sw := PerfLog.time_section("sw_section")
	var ms := sw.stop()
	assert_gte(ms, 0.0, "stopwatch elapsed should be non-negative")
	assert_eq(PerfLog.get_entries().size(), 1, "stopwatch stop() should record one entry")
	assert_eq(PerfLog.get_last_entry()["section"], "sw_section")


func test_stopwatch_stop_is_idempotent():
	var sw := PerfLog.time_section("sw_once")
	sw.stop()
	sw.stop()  # second stop must not double-record
	assert_eq(PerfLog.get_entries().size(), 1, "a stopwatch records at most once")


# --- Threshold warning -----------------------------------------------------

func test_threshold_warning_fires_when_section_runs_over():
	PerfLog.anomaly_flagged.connect(_on_anomaly)
	# Negative threshold: any non-negative elapsed exceeds it, so the tripwire is deterministic.
	PerfLog.set_threshold("slow_section", -1.0)
	PerfLog.begin("slow_section")
	PerfLog.end("slow_section")
	PerfLog.anomaly_flagged.disconnect(_on_anomaly)

	assert_eq(_anomaly_count, 1, "an over-threshold section should emit anomaly_flagged once")
	assert_eq(PerfLog.get_warnings().size(), 1, "the warning should land in the rolling warning log")
	assert_true(PerfLog.get_last_entry()["over"], "the recorded entry should be marked over-threshold")
	assert_string_contains(PerfLog.get_warnings()[0], "SLOW", "the warning line should name it a SLOW section")


func test_fast_section_under_threshold_does_not_warn():
	PerfLog.set_threshold("fast_section", 1000000.0)  # 1000s -- nothing here comes close
	PerfLog.begin("fast_section")
	PerfLog.end("fast_section")
	assert_eq(PerfLog.get_warnings().size(), 0, "a section under threshold must not warn")


# --- Iteration tripwire ----------------------------------------------------

func test_iteration_tripwire_fires_past_bound():
	PerfLog.anomaly_flagged.connect(_on_anomaly)
	var tripped := PerfLog.check_iterations("runaway_loop", 401, 400)
	PerfLog.anomaly_flagged.disconnect(_on_anomaly)

	assert_true(tripped, "count over the sane bound should trip the wire")
	assert_eq(_anomaly_count, 1, "tripping should emit anomaly_flagged")
	assert_string_contains(PerfLog.get_warnings()[0], "RUNAWAY", "the warning should read as a runaway loop")


func test_iteration_tripwire_quiet_under_bound():
	var tripped := PerfLog.check_iterations("normal_loop", 30, 400)
	assert_false(tripped, "count within the sane bound must not trip")
	assert_eq(PerfLog.get_warnings().size(), 0, "no warning under the bound")


# --- Dev gate --------------------------------------------------------------

func test_inactive_gate_suppresses_all_recording():
	PerfLog.set_enabled_override(false)  # simulate a release cut (DEV_BUILD=false)
	PerfLog.anomaly_flagged.connect(_on_anomaly)

	PerfLog.begin("gated_section")
	var ms := PerfLog.end("gated_section")
	var tripped := PerfLog.check_iterations("gated_loop", 99999, 400)

	PerfLog.anomaly_flagged.disconnect(_on_anomaly)
	assert_eq(ms, 0.0, "timing returns 0 when the logger is inactive")
	assert_false(tripped, "the tripwire stays down when inactive")
	assert_eq(PerfLog.get_entries().size(), 0, "no entries recorded while inactive")
	assert_eq(PerfLog.get_warnings().size(), 0, "no warnings recorded while inactive")
	assert_eq(_anomaly_count, 0, "no anomaly signal while inactive -- players see nothing")


func test_is_active_follows_override():
	PerfLog.set_enabled_override(true)
	assert_true(PerfLog.is_active(), "override true forces the logger active")
	PerfLog.set_enabled_override(false)
	assert_false(PerfLog.is_active(), "override false forces it inactive")


# --- Rolling buffer --------------------------------------------------------

func test_entries_ring_buffer_is_bounded():
	# Record well past the cap and confirm the buffer never exceeds MAX_ENTRIES.
	var over_cap := PerfLog.MAX_ENTRIES + 50
	for i in range(over_cap):
		PerfLog.begin("ring_%d" % i)
		PerfLog.end("ring_%d" % i)
	assert_eq(PerfLog.get_entries().size(), PerfLog.MAX_ENTRIES,
		"the rolling log must cap at MAX_ENTRIES (oldest dropped)")


# --- mark() / gauge() -------------------------------------------------------

func test_mark_records_an_entry_with_label_and_ctx():
	PerfLog.mark("scene_ready", {"scene": "watch"})
	var entries := PerfLog.get_entries()
	assert_eq(entries.size(), 1, "mark() should record exactly one entry")
	assert_eq(entries[0]["kind"], "mark", "entry should be tagged kind=mark")
	assert_eq(entries[0]["label"], "scene_ready", "entry should carry the mark label")
	assert_eq(entries[0]["ctx"]["scene"], "watch", "entry should carry the caller context")


func test_mark_is_noop_when_inactive():
	PerfLog.set_enabled_override(false)
	PerfLog.mark("gated_mark")
	assert_eq(PerfLog.get_entries().size(), 0, "mark() must no-op while the gate is off")


func test_gauge_records_an_entry_with_name_and_value():
	PerfLog.gauge("office_sprites", 12, {"turn": 3})
	var entries := PerfLog.get_entries()
	assert_eq(entries.size(), 1, "gauge() should record exactly one entry")
	assert_eq(entries[0]["kind"], "gauge", "entry should be tagged kind=gauge")
	assert_eq(entries[0]["name"], "office_sprites", "entry should carry the gauge name")
	assert_eq(entries[0]["value"], 12, "entry should carry the gauge value")
	assert_eq(entries[0]["ctx"]["turn"], 3, "entry should carry the caller context")


func test_gauge_is_noop_when_inactive():
	PerfLog.set_enabled_override(false)
	PerfLog.gauge("gated_gauge", 1)
	assert_eq(PerfLog.get_entries().size(), 0, "gauge() must no-op while the gate is off")


# --- Rotation ----------------------------------------------------------------

func test_should_rotate_true_past_threshold():
	assert_true(PerfLog.should_rotate(PerfLog.MAX_LOG_BYTES, PerfLog.MAX_LOG_BYTES),
		"a log exactly at the threshold should rotate")
	assert_true(PerfLog.should_rotate(PerfLog.MAX_LOG_BYTES + 1, PerfLog.MAX_LOG_BYTES),
		"a log past the threshold should rotate")


func test_should_rotate_false_under_threshold():
	assert_false(PerfLog.should_rotate(100, PerfLog.MAX_LOG_BYTES),
		"a small log should not rotate")


# --- File line shape ---------------------------------------------------------
# Enables real file logging briefly to check the written line shape, then removes the file
# and restores hermetic settings -- the only test in this suite that touches user://.
#
# #976: writes to a private log_path_override rather than the real PerfLog.LOG_PATH.
# turn_manager.gd/office_floor.gd/event_service.gd write real, unguarded lines to the real
# LOG_PATH throughout a full-suite run (nothing gates their PerfLog calls), so sharing that
# path here raced this test's delete-then-4-writes-then-read against that outside traffic --
# an order-dependent flake that passed 18/18 in isolation and failed intermittently in the
# full fast gate. A path nothing else ever touches makes that race structurally impossible.
const _TEST_LOG_PATH := "user://logs/perf_log_line_shape_test.log"

func test_written_line_has_timestamp_and_type_fields():
	var re := RegEx.new()
	re.compile("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z (BEGIN|END|MARK|GAUGE|WARN|ITER) ")

	PerfLog.set_log_path_override(_TEST_LOG_PATH)
	PerfLog.set_file_logging(true)
	if FileAccess.file_exists(_TEST_LOG_PATH):
		DirAccess.remove_absolute(_TEST_LOG_PATH)
	PerfLog.begin("line_shape_section", {"turn": 1})
	PerfLog.end("line_shape_section")
	PerfLog.mark("line_shape_mark")
	PerfLog.gauge("line_shape_gauge", 5)
	PerfLog.set_file_logging(false)

	var f := FileAccess.open(_TEST_LOG_PATH, FileAccess.READ)
	assert_not_null(f, "perf log should exist after a real write")
	if f == null:
		PerfLog.set_log_path_override(null)
		return
	var lines: Array = []
	while not f.eof_reached():
		var line := f.get_line()
		if not line.is_empty():
			lines.append(line)
	f.close()
	DirAccess.remove_absolute(_TEST_LOG_PATH)
	PerfLog.set_log_path_override(null)

	assert_gte(lines.size(), 4, "begin+end+mark+gauge should write at least 4 lines")
	for line in lines:
		assert_not_null(re.search(line), "line should start with an ISO-8601 timestamp + TYPE field: %s" % line)

extends Node
## PerfLog -- dev-mode performance logger for the load-bearing turn/month loop.
##
## OBSERVABILITY ONLY. It reads a monotonic clock (Time.get_ticks_usec) and, at most,
## display-only values a caller hands it (turn number, counts, labels). It NEVER touches
## game state, RNG, or scoring, so it has ZERO gameplay/determinism effect (ladder stays L2).
## Every public method early-returns
## a no-op unless BuildInfo.is_dev_build() is true, so a clean release cut (DEV_BUILD=false)
## makes normal players see nothing -- no file writes, no console spam.
##
## Why this exists: a runaway turn, an accidental infinite loop ("infi-glitch"), or a
## divide-by-one blow-up should be OBSERVABLE before it bites. Two cheap tripwires:
##   1. Wall-time: a timed section exceeding a threshold (default 1000 ms for a turn).
##   2. Iteration count: a loop blowing past a sane bound -- the divide-by-one /
##      infinite-accrual tripwire.
##
## API (all no-ops in a release cut):
##   PerfLog.begin("turn_resolution", {"turn": t}); ...; PerfLog.end("turn_resolution")
##   var sw := PerfLog.time_section("turn_resolution"); ...; sw.stop()   # stopwatch helper
##   PerfLog.check_iterations("month_playback", i, 400)                  # loop tripwire
##   PerfLog.mark("scene_ready", {"scene": "watch"})                     # one-line stamped event
##   PerfLog.gauge("office_sprites", 12)                                 # point-in-time count
##
## Callers must treat the tripwire returns as OBSERVATION ONLY -- never break/branch game
## logic on them, or the logger would fork behavior. It watches; it does not steer.
##
## FILE FORMAT (2026-07-27 tightening, for later story-mining/parsing): every line written
## to perf.log leads with an ISO-8601 UTC wall-clock timestamp and a fixed TYPE field
## (BEGIN/END/MARK/GAUGE/WARN/ITER), then the existing free-text body, so a later parser can
## split reliably on the first two whitespace-delimited fields. ASCII only; ctx renders as
## trailing key=value pairs, stable field order.

## Default wall-time threshold (ms) above which a timed section is flagged. A whole turn
## resolving in >1s is well past anything the current sim should need -- picked as a loud
## "something is wrong", not a tight budget.
const DEFAULT_WARN_MS := 1000.0

## Rolling in-memory ring-buffer caps. Turns are user-paced (seconds+ apart), so these hold
## a long trail without unbounded growth.
const MAX_ENTRIES := 512
const MAX_WARNINGS := 128

## Dev log trail. Append-only; created lazily under user://logs (same dir as LogExporter).
const LOG_PATH := "user://logs/perf.log"
const LOG_DIR := "user://logs"
const ROTATED_LOG_NAME := "perf.log.1"

## Size-based rotation: once perf.log reaches this many bytes, the NEXT write rotates it to
## perf.log.1 (overwriting any prior rotation) and starts a fresh perf.log. Keeps a session's
## worth of story-mineable trail without unbounded growth across a long dev session.
const MAX_LOG_BYTES := 5 * 1024 * 1024

signal anomaly_flagged(message: String)

## Rolling records. Each entry: {section, ms, over, ctx}. Warnings mirror the anomaly lines.
var _entries: Array = []
var _warnings: Array = []
## Section name -> {start_usec, ctx} for begin()/end() pairs.
var _open: Dictionary = {}
## Optional per-section threshold overrides (ms).
var _thresholds: Dictionary = {}
## Test/override hook: null => follow BuildInfo.is_dev_build(); true/false => forced.
var _enabled_override = null
## File logging can be disabled (e.g. by tests) to stay hermetic; on by default in dev.
var _file_logging := true
## Test hook: null => write to LOG_PATH; non-null => redirect writes to this path instead.
var _log_path_override = null


## Manual stopwatch for scoped timing without matching begin/end names. Cheap RefCounted;
## stop() records once and is idempotent. In a release cut _record() is a no-op, so a bare
## `PerfLog.time_section(x).stop()` is safe (never null, never touches state).
class Stopwatch:
	extends RefCounted
	var _perf: Node
	var _section: String
	var _start_usec: int
	var _ctx: Dictionary
	var _stopped := false

	func _init(perf: Node, section: String, start_usec: int, ctx: Dictionary) -> void:
		_perf = perf
		_section = section
		_start_usec = start_usec
		_ctx = ctx

	## Stop and record. Returns elapsed ms (0.0 if already stopped or logging inactive).
	func stop() -> float:
		if _stopped or _perf == null:
			return 0.0
		_stopped = true
		return _perf._record(_section, _start_usec, _ctx)


func _ready() -> void:
	# Nothing to build; the logger is passive. Announce only in dev so release stays silent.
	if is_active():
		print("[PerfLog] Ready (dev). Perf trail: %s" % (OS.get_user_data_dir() + "/logs/perf.log"))


## True while the logger should observe/emit. Follows the dev-build gate unless a test forces it.
func is_active() -> bool:
	if _enabled_override != null:
		return bool(_enabled_override)
	return BuildInfo.is_dev_build()


## --- Timing API ------------------------------------------------------------

## Start a named section. Pairs with end(section). ctx (e.g. {"turn": n}) rides into the record.
func begin(section: String, ctx: Dictionary = {}) -> void:
	if not is_active():
		return
	_open[section] = {"start_usec": Time.get_ticks_usec(), "ctx": ctx}
	_write_line("BEGIN", "section=%s%s" % [section, _kv_suffix(ctx)])


## End a named section started with begin(). Returns elapsed ms (0.0 if unmatched/inactive).
func end(section: String) -> float:
	if not is_active():
		return 0.0
	if not _open.has(section):
		return 0.0
	var open: Dictionary = _open[section]
	_open.erase(section)
	return _record(section, int(open["start_usec"]), open["ctx"])


## Stopwatch helper: returns a Stopwatch you stop() when the scope ends. Handy when a section
## has multiple return paths and a begin/end pair would be easy to leak.
func time_section(section: String, ctx: Dictionary = {}) -> Stopwatch:
	return Stopwatch.new(self, section, Time.get_ticks_usec(), ctx)


## --- One-line events ---------------------------------------------------------

## Stamp a single unpaired event -- no begin/end matching, just "this happened, here's when
## and with what context". No-op when inactive; feeds the same ring buffer + file trail as
## timed sections. ctx is display-only (e.g. {"scene": "watch"}) -- never branch on it.
func mark(label: String, ctx: Dictionary = {}) -> void:
	if not is_active():
		return
	_push(_entries, {"kind": "mark", "label": label, "ctx": ctx}, MAX_ENTRIES)
	_write_line("MARK", "label=%s%s" % [label, _kv_suffix(ctx)])


## Record a point-in-time count/value (e.g. gauge("office_sprites", 12)). No-op when
## inactive; feeds the same ring buffer + file trail as timed sections.
func gauge(name: String, value, ctx: Dictionary = {}) -> void:
	if not is_active():
		return
	_push(_entries, {"kind": "gauge", "name": name, "value": value, "ctx": ctx}, MAX_ENTRIES)
	_write_line("GAUGE", "name=%s value=%s%s" % [name, str(value), _kv_suffix(ctx)])


## --- Iteration tripwire ----------------------------------------------------

## Flag a WARNING if a loop's iteration count blows past a sane bound -- the cheap
## divide-by-one / infinite-accrual detector. OBSERVATION ONLY: returns whether it tripped
## (for tests), but callers must NOT branch game logic on it. Returns false when inactive.
func check_iterations(loop_name: String, count: int, sane_bound: int, ctx: Dictionary = {}) -> bool:
	if not is_active():
		return false
	if count <= sane_bound:
		return false
	_flag("RUNAWAY loop '%s' hit %d iterations (sane bound %d)" % [loop_name, count, sane_bound], ctx, "ITER")
	return true


## --- Configuration ---------------------------------------------------------

## Override the wall-time threshold (ms) for one section. Absent sections use DEFAULT_WARN_MS.
func set_threshold(section: String, warn_ms: float) -> void:
	_thresholds[section] = warn_ms


## Test hook: force the active gate (true/false) or restore the dev-build default (null).
func set_enabled_override(value) -> void:
	_enabled_override = value


## Test hook: silence the file trail so unit runs stay hermetic.
func set_file_logging(enabled: bool) -> void:
	_file_logging = enabled


## Test hook: redirect file writes to a private path (null => the real LOG_PATH).
## Exists because turn_manager.gd/office_floor.gd/event_service.gd call PerfLog with NO
## test gating of their own (by design -- they're production call sites), so whenever a test
## suite run exercises them the real LOG_PATH gets real writes for the whole suite. A test
## that wants to inspect the actual written-line shape needs a path nothing else touches,
## rather than fighting that shared, suite-wide traffic (issue #976).
func set_log_path_override(path) -> void:
	_log_path_override = path


## Effective file-trail path: the override when a test set one, else the real LOG_PATH.
func get_log_path() -> String:
	return _log_path_override if _log_path_override != null else LOG_PATH


## Test-only: reset ALL shared singleton state in one call (dev/test hook, unused in a
## release cut). Covers what before_each/after_each need so a test can't leak ring-buffer
## entries, warnings, open sections, threshold overrides, the enabled/file-logging gates, or
## a log-path override into the next test -- see issue #976.
func reset_for_tests() -> void:
	_entries.clear()
	_warnings.clear()
	_open.clear()
	_thresholds.clear()
	_enabled_override = null
	_file_logging = true
	_log_path_override = null


## --- Introspection (for the dev overlay / tests) ---------------------------

func get_entries() -> Array:
	return _entries.duplicate()


func get_warnings() -> Array:
	return _warnings.duplicate()


func get_last_entry() -> Dictionary:
	return _entries.back() if not _entries.is_empty() else {}


func clear() -> void:
	_entries.clear()
	_warnings.clear()
	_open.clear()


## --- Internals -------------------------------------------------------------

func _record(section: String, start_usec: int, ctx: Dictionary) -> float:
	if not is_active():
		return 0.0
	var elapsed_ms := float(Time.get_ticks_usec() - start_usec) / 1000.0
	var threshold: float = float(_thresholds.get(section, DEFAULT_WARN_MS))
	var over := elapsed_ms > threshold
	var entry := {"section": section, "ms": elapsed_ms, "over": over, "ctx": ctx}
	_push(_entries, entry, MAX_ENTRIES)
	var body := "section=%s ms=%.2f" % [section, elapsed_ms]
	if over:
		body += " over=true"
	body += _kv_suffix(ctx)
	_write_line("END", body)
	if over:
		_flag("SLOW section '%s' took %.1f ms (threshold %.0f ms)" % [section, elapsed_ms, threshold], ctx)
	return elapsed_ms


## type is the file TYPE field for this warning ("WARN" for a slow section, "ITER" for a
## runaway-loop trip). The in-memory _warnings line keeps the legacy "[WARN]" tag regardless
## of type -- callers/tests match on the message text (SLOW/RUNAWAY), not that tag.
func _flag(message: String, ctx: Dictionary, type: String = "WARN") -> void:
	var line := "[PerfLog][WARN] " + message + _ctx_suffix(ctx)
	_push(_warnings, line, MAX_WARNINGS)
	# print (not push_warning): in a dev checkout these are expected dev signals, and
	# push_warning can be mis-counted as an engine fault by strict test tooling.
	print(line)
	_write_line(type, message + _kv_suffix(ctx))
	anomaly_flagged.emit(message)


## Legacy in-memory suffix (Dictionary.to_string() shape) -- kept for the _warnings buffer's
## text, which existing callers/tests match by substring only. File lines use _kv_suffix().
func _ctx_suffix(ctx: Dictionary) -> String:
	return ("  " + str(ctx)) if not ctx.is_empty() else ""


## Stable key=value ctx rendering for the file trail (a later parser splits on TYPE, then
## reads trailing key=value pairs). Insertion order; "" when ctx is empty.
func _kv_suffix(ctx: Dictionary) -> String:
	if ctx.is_empty():
		return ""
	var parts: Array = []
	for k in ctx.keys():
		parts.append("%s=%s" % [k, str(ctx[k])])
	return " " + " ".join(parts)


func _push(buf: Array, item, cap: int) -> void:
	buf.append(item)
	while buf.size() > cap:
		buf.pop_front()


## Compose and append one line: "<ISO-8601 UTC timestamp>Z <TYPE> <body>". TYPE is one of
## BEGIN/END/MARK/GAUGE/WARN/ITER (see the file-format doc at the top of this file).
func _write_line(type: String, body: String) -> void:
	if not _file_logging or not is_active():
		return
	var dir := DirAccess.open("user://")
	if dir != null and not dir.dir_exists("logs"):
		dir.make_dir("logs")
	var log_path := get_log_path()
	_rotate_if_needed(log_path)
	var line := "%s %s %s" % [_timestamp(), type, body]
	var f: FileAccess
	if FileAccess.file_exists(log_path):
		f = FileAccess.open(log_path, FileAccess.READ_WRITE)
		if f != null:
			f.seek_end()
	else:
		f = FileAccess.open(log_path, FileAccess.WRITE)
	if f != null:
		f.store_line(line)
		f.close()


## Current wall-clock as an ISO-8601 UTC string, e.g. "2026-07-27T13:45:01Z".
func _timestamp() -> String:
	return "%sZ" % Time.get_datetime_string_from_system(true)


## Pure size-vs-threshold decision, split out so tests can exercise it without touching
## user://. True means the CURRENT perf.log has grown past the rotation threshold.
static func should_rotate(current_size_bytes: int, threshold_bytes: int = MAX_LOG_BYTES) -> bool:
	return current_size_bytes >= threshold_bytes


## Size-based rotation: when perf.log has reached MAX_LOG_BYTES, move it to perf.log.1
## (clobbering any prior rotation) so the next write starts a fresh perf.log. Runs at the
## top of every file write; a no-op on a small/missing log (the common case). Rotation is
## defined only for the real LOG_PATH -- a test-only log_path_override (issue #976) never
## rotates, since it is a throwaway path a single test owns.
func _rotate_if_needed(log_path: String = LOG_PATH) -> void:
	if log_path != LOG_PATH:
		return
	if not FileAccess.file_exists(LOG_PATH):
		return
	var f := FileAccess.open(LOG_PATH, FileAccess.READ)
	if f == null:
		return
	var size := f.get_length()
	f.close()
	if not should_rotate(size):
		return
	var dir := DirAccess.open(LOG_DIR)
	if dir == null:
		return
	if dir.file_exists(ROTATED_LOG_NAME):
		dir.remove(ROTATED_LOG_NAME)
	dir.rename("perf.log", ROTATED_LOG_NAME)

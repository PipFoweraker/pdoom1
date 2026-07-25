extends Node
## PerfLog -- dev-mode performance logger for the load-bearing turn/month loop.
##
## OBSERVABILITY ONLY. It reads a monotonic clock (Time.get_ticks_usec) and, at most,
## the turn number a caller hands it. It NEVER touches game state, RNG, or scoring, so it
## has ZERO gameplay/determinism effect (ladder stays L2). Every public method early-returns
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
##
## Callers must treat the tripwire returns as OBSERVATION ONLY -- never break/branch game
## logic on them, or the logger would fork behavior. It watches; it does not steer.

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


## --- Iteration tripwire ----------------------------------------------------

## Flag a WARNING if a loop's iteration count blows past a sane bound -- the cheap
## divide-by-one / infinite-accrual detector. OBSERVATION ONLY: returns whether it tripped
## (for tests), but callers must NOT branch game logic on it. Returns false when inactive.
func check_iterations(loop_name: String, count: int, sane_bound: int, ctx: Dictionary = {}) -> bool:
	if not is_active():
		return false
	if count <= sane_bound:
		return false
	_flag("RUNAWAY loop '%s' hit %d iterations (sane bound %d)" % [loop_name, count, sane_bound], ctx)
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
	_write_line("[PerfLog] %-22s %8.2f ms%s%s" % [
		section, elapsed_ms, ("  <<< OVER" if over else ""), _ctx_suffix(ctx)])
	if over:
		_flag("SLOW section '%s' took %.1f ms (threshold %.0f ms)" % [section, elapsed_ms, threshold], ctx)
	return elapsed_ms


func _flag(message: String, ctx: Dictionary) -> void:
	var line := "[PerfLog][WARN] " + message + _ctx_suffix(ctx)
	_push(_warnings, line, MAX_WARNINGS)
	# print (not push_warning): in a dev checkout these are expected dev signals, and
	# push_warning can be mis-counted as an engine fault by strict test tooling.
	print(line)
	_write_line(line)
	anomaly_flagged.emit(message)


func _ctx_suffix(ctx: Dictionary) -> String:
	return ("  " + str(ctx)) if not ctx.is_empty() else ""


func _push(buf: Array, item, cap: int) -> void:
	buf.append(item)
	while buf.size() > cap:
		buf.pop_front()


func _write_line(line: String) -> void:
	if not _file_logging or not is_active():
		return
	var dir := DirAccess.open("user://")
	if dir != null and not dir.dir_exists("logs"):
		dir.make_dir("logs")
	var f: FileAccess
	if FileAccess.file_exists(LOG_PATH):
		f = FileAccess.open(LOG_PATH, FileAccess.READ_WRITE)
		if f != null:
			f.seek_end()
	else:
		f = FileAccess.open(LOG_PATH, FileAccess.WRITE)
	if f != null:
		f.store_line(line)
		f.close()

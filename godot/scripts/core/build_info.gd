extends RefCounted
class_name BuildInfo
## Dev-build identification: version + a per-commit build stamp so a playtester can
## confirm *exactly* which build he is running (playtester couldn't tell builds apart).
##
## The stamp is produced out-of-band by tools/write_build_stamp.py, which writes
## res://build_stamp.txt (key=value lines) from `git rev-parse --short HEAD` + the
## build date. We read that file here at startup. Chosen for reliability over
## cleverness: the date always resolves, the commit is best-effort, and if the file
## is missing (fresh checkout, never stamped) we degrade to "unstamped" rather than
## crash. Re-run the tool before packaging to refresh the commit.
##
## The pure readers here are unit-tested (test_dev_build_indicator.gd); the on-screen
## badge (dev_build_badge.gd) still needs a human eye.

## Master switch for the DEV BUILD indicators. On by default in dev; flip to false
## for a clean release cut (or gate on OS.is_debug_build() via is_dev_build()).
const DEV_BUILD := true

## res:// text file written by tools/write_build_stamp.py. Not a Godot resource, so
## it produces no .import churn; read via FileAccess.
const STAMP_PATH := "res://build_stamp.txt"

## Parse the stamp file into a Dictionary of {key: value}. Empty dict if absent.
static func _read_stamp() -> Dictionary:
	var out: Dictionary = {}
	if not FileAccess.file_exists(STAMP_PATH):
		return out
	var f := FileAccess.open(STAMP_PATH, FileAccess.READ)
	if f == null:
		return out
	while not f.eof_reached():
		var line := f.get_line().strip_edges()
		if line.is_empty() or not line.contains("="):
			continue
		var parts := line.split("=", false, 1)
		if parts.size() == 2:
			out[parts[0].strip_edges()] = parts[1].strip_edges()
	f.close()
	return out

## Short git commit hash the build came from, or "" if not stamped.
static func get_commit() -> String:
	return String(_read_stamp().get("commit", ""))

## Build date (ISO) recorded at stamp time, or "" if not stamped.
static func get_build_date() -> String:
	return String(_read_stamp().get("date", ""))

## True while this build should show the DEV BUILD indicators.
static func is_dev_build() -> bool:
	return DEV_BUILD

## Compact commit+date stamp, e.g. "fd60eb6 · 2026-07-11". Always non-empty:
## falls back to the date, then to "unstamped", so the overlay never shows blank.
static func get_stamp() -> String:
	var commit := get_commit()
	var date := get_build_date()
	if not commit.is_empty() and not date.is_empty():
		return "%s · %s" % [commit, date]
	if not commit.is_empty():
		return commit
	if not date.is_empty():
		return date
	return "unstamped"

## One-line badge text for the corner indicator, e.g.
## "DEV BUILD  v0.11.0  ·  fd60eb6 · 2026-07-11". Always non-empty.
static func get_badge_text() -> String:
	return "DEV BUILD  v%s  ·  %s" % [GameConfig.CURRENT_VERSION, get_stamp()]

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

# --- Live git identity (L1 follow-up: the stamp went stale and cost a playtest) --------
#
# The baked stamp is written at package time and silently rots in a dev checkout (it read
# "fd60eb6 · 2026-07-11" on every branch for two days). Dev builds now read the REAL HEAD
# from git at runtime; the baked stamp is only the fallback for exported builds (no .git,
# no git binary) and is explicitly marked "(stamp)" so it can never pass as live.
# Acceptance: two different checkouts can never show the same badge silently — live HEAD
# differs per checkout, and a stamped badge visibly says it is a stamp.

## Cache: "" = not probed yet; "-" = probed, git unavailable (don't re-shell every frame).
static var _live_git_cache: String = ""


## Live "branch@shortsha" read from git at runtime, or "" when this is not a git checkout
## (exported build) or git is not installed. Cached after the first probe. Also emits a
## LOUD stale-stamp warning when the baked stamp disagrees with the live HEAD.
static func get_live_git_stamp() -> String:
	if _live_git_cache != "":
		return "" if _live_git_cache == "-" else _live_git_cache
	_live_git_cache = "-"

	# Only shell out when this looks like a git checkout: the repo root is one level above
	# the godot project dir; .git is a dir in a normal clone and a FILE in a git worktree.
	var root := ProjectSettings.globalize_path("res://").path_join("..")
	var dotgit := root.path_join(".git")
	if not (DirAccess.dir_exists_absolute(dotgit) or FileAccess.file_exists(dotgit)):
		return ""

	var out: Array = []
	if OS.execute("git", ["-C", root, "rev-parse", "--short", "HEAD"], out) != 0 or out.is_empty():
		return ""
	var sha := String(out[0]).strip_edges()
	if sha.is_empty():
		return ""

	var branch := ""
	var bout: Array = []
	if OS.execute("git", ["-C", root, "rev-parse", "--abbrev-ref", "HEAD"], bout) == 0 and not bout.is_empty():
		branch = String(bout[0]).strip_edges()
		if branch == "HEAD":
			branch = "detached"
	_live_git_cache = ("%s@%s" % [branch, sha]) if not branch.is_empty() else sha

	# The baked stamp exists AND disagrees with reality -> say so in the console. The badge
	# shows live git regardless, so a stale stamp can never be mistaken for the build
	# identity. (print, not push_warning: in a dev checkout the stamp is stale after every
	# commit by construction — GUT/CI must not count that as an engine error.)
	var stamped := get_commit()
	if not stamped.is_empty() and not sha.begins_with(stamped) and not stamped.begins_with(sha):
		print("[BuildInfo] NOTE: build_stamp.txt is stale (stamp %s vs live HEAD %s) — badge uses live git" % [stamped, sha])

	return _live_git_cache


## Compact build-identity stamp. Dev checkouts: live git, e.g.
## "l1-month-turn-engine@a1b2c3d · live". Exported/no-git: the baked stamp explicitly
## marked "(stamp)", e.g. "fd60eb6 · 2026-07-11 (stamp)". Always non-empty: degrades to
## the date, then "unstamped", so the overlay never shows blank.
static func get_stamp() -> String:
	var live := get_live_git_stamp()
	if not live.is_empty():
		return "%s · live" % live
	var commit := get_commit()
	var date := get_build_date()
	if not commit.is_empty() and not date.is_empty():
		return "%s · %s (stamp)" % [commit, date]
	if not commit.is_empty():
		return "%s (stamp)" % commit
	if not date.is_empty():
		return "%s (stamp)" % date
	return "unstamped"

## One-line badge text for the corner indicator, e.g.
## "DEV BUILD  v0.11.0  ·  fd60eb6 · 2026-07-11". Always non-empty.
static func get_badge_text() -> String:
	return "DEV BUILD  v%s  ·  %s" % [GameConfig.CURRENT_VERSION, get_stamp()]

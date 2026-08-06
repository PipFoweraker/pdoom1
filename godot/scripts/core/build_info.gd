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

## Manual kill-switch for the DEV BUILD indicators. Leave true: the real gate is
## is_dev_build() below, which ALSO requires a debug run, so a release-template
## export is never a "dev build" no matter what this const says. Flip false only
## to force the indicators off even in a dev checkout.
const DEV_BUILD := true

## Alpha-tools era switch (#1079 fallout, ruled 2026-08-05). While this is true the ALPHA
## TOOLS overlay (backslash) is reachable in an EXPORTED RELEASE build too -- see
## are_alpha_tools_available() below for the full reasoning. Flip false at 1.0, when the
## tools stop being a promise the name already makes ("alpha" says they do not survive to
## the finished game).
const ALPHA_TOOLS_ERA := true

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

## Test hook: null => follow OS.is_debug_build(); true/false => forced. Exists so the
## GATE SPLIT below can be asserted under simulated RELEASE conditions -- a headless GUT
## run is always a debug run, so without this hook the release branch of every gate is
## untestable and can only be discovered at a friend's house (2026-08-05).
static var _debug_run_override = null


## True when this process is a debug run (editor or debug-template export).
static func is_debug_run() -> bool:
	if _debug_run_override != null:
		return bool(_debug_run_override)
	return OS.is_debug_build()


## True while this run should show the BUILD-GATED dev features: the DEV BUILD badge,
## the flight recorder (F6), the UI evolution recorder (F7) and the perf log.
##
## Discriminator: OS.is_debug_build() (same signal as OS.has_feature("debug")) is
## true in the editor AND in a debug-template export, and false ONLY in a
## release-template export -- exactly the set of builds players download.
## OS.has_feature("editor") is deliberately NOT used: it is false in an exported
## debug build, which would misclassify tester debug exports as public releases.
## Before this gate existed the const above shipped as-is, so the public v0.13.2
## release showed the amber DEV BUILD banner on every screen (issue #1067).
##
## NOTE (2026-08-05): this is NO LONGER the gate for the ALPHA TOOLS overlay. See
## are_alpha_tools_available().
static func is_dev_build() -> bool:
	return DEV_BUILD and is_debug_run()


## THE GATE SPLIT (2026-08-05). PR #1079 correctly stopped a public release wearing the
## amber DEV BUILD banner -- but the overlay, both recorders and the perf log all hung off
## the SAME is_dev_build(), so they silently switched off in release exports as a side
## effect. Pip lost backslash mid-playtest on a shipped build ("I wasn't able to bump
## doom"). That consequence was flagged when #1079 merged and never ruled on; this is the
## ruling.
##
## Which side each feature landed on, and why:
##   BADGE            -> is_dev_build().             A release must not look like a dev cut.
##   ALPHA TOOLS      -> are_alpha_tools_available(). Reachable in release.
##   FLIGHT RECORDER  -> is_dev_build().             Writes a SCREENSHOT + the full
##                       GameState JSON to the player's disk. Explicit F6, yes, but the
##                       artefact is a picture of someone's screen; nobody asked for it in
##                       a shipped build. Privacy posture, not convenience.
##   UI EVOLUTION REC -> is_dev_build().             Same, and it is a SILENT screenshot
##                       (no popup, no confirmation). Strictly worse than F6 to ship.
##   PERF LOG         -> is_dev_build().             Writes user://logs/perf.log
##                       continuously, unprompted, rotating at 5MB. The textbook
##                       "invisible recorder on a player's disk". Stays off.
##
## Why the overlay is safe to un-gate and the recorders are not: PR #1104's Alpha Tools
## made every state-MUTATING dev power set a STICKY, ONE-WAY unranked flag on the run,
## carried through the save envelope, warned at first use and again at game over
## (docs/decision-cards/2026-08-01_dev-powers-nomenclature.html). That system exists
## PRECISELY so dev powers can ship without polluting the board -- so build-gating the
## overlay is now both redundant and in tension with that ruling. The recorders have no
## such protection because their risk is not the leaderboard, it is the disk.
static func are_alpha_tools_available() -> bool:
	return DEV_BUILD and ALPHA_TOOLS_ERA

# --- Live git identity (L1 follow-up: the stamp went stale and cost a playtest) --------
#
# The baked stamp is written at package time and silently rots in a dev checkout (it read
# "fd60eb6 - 2026-07-11" on every branch for two days). Dev builds now read the REAL HEAD
# from git at runtime; the baked stamp is only the fallback for exported builds (no .git,
# no git binary) and is explicitly marked "(stamp)" so it can never pass as live.
# Acceptance: two different checkouts can never show the same badge silently -- live HEAD
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
	# commit by construction -- GUT/CI must not count that as an engine error.)
	var stamped := get_commit()
	if not stamped.is_empty() and not sha.begins_with(stamped) and not stamped.begins_with(sha):
		print("[BuildInfo] NOTE: build_stamp.txt is stale (stamp %s vs live HEAD %s) -- badge uses live git" % [stamped, sha])

	return _live_git_cache


## Compact build-identity stamp. Dev checkouts: live git, e.g.
## "l1-month-turn-engine@a1b2c3d - live". Exported/no-git: the baked stamp explicitly
## marked "(stamp)", e.g. "fd60eb6 - 2026-07-11 (stamp)". Always non-empty: degrades to
## the date, then "unstamped", so the overlay never shows blank.
static func get_stamp() -> String:
	var live := get_live_git_stamp()
	if not live.is_empty():
		return "%s - live" % live
	var commit := get_commit()
	var date := get_build_date()
	if not commit.is_empty() and not date.is_empty():
		return "%s - %s (stamp)" % [commit, date]
	if not commit.is_empty():
		return "%s (stamp)" % commit
	if not date.is_empty():
		return "%s (stamp)" % date
	return "unstamped"

## One-line badge text for the corner indicator. Dev/debug runs get the loud form
## with the full stamp; exported release builds get a dignified version-only form
## (players read "DEV BUILD" on a downloaded release as "I have the wrong file" --
## issue #1067). Always non-empty either way.
static func get_badge_text() -> String:
	return get_dev_badge_text() if is_dev_build() else get_release_badge_text()

## Dev form, e.g. "DEV BUILD  v0.11.0  -  fd60eb6 - 2026-07-11 (stamp)".
static func get_dev_badge_text() -> String:
	return "DEV BUILD  v%s  -  %s" % [GameConfig.CURRENT_VERSION, get_stamp()]

## Release form: just the version, e.g. "v0.13.2". Keeps the support value ("which
## build are you running?") without the scary label or the git plumbing.
static func get_release_badge_text() -> String:
	return "v%s" % GameConfig.CURRENT_VERSION

## Build identity for the ALPHA TOOLS overlay header. Unlike get_badge_text() this does
## NOT change shape by build type: the overlay now opens in release builds too, and
## "which build is this?" is the single most useful thing on it when Pip is standing in
## someone else's lounge room. Always version + stamp.
static func get_tools_stamp_text() -> String:
	return "v%s  -  %s" % [GameConfig.CURRENT_VERSION, get_stamp()]

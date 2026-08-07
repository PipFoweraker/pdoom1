extends GutTest
## CONTAINMENT GUARD (2026-08-07). The test suite was writing into the DEVELOPER'S
## LIVE PLAYER PROFILE, and it cost real data.
##
## Measured: Godot derives `user://` from `config/name` in project.godot ("P(Doom)"),
## NOT from the checkout path. Every one of the 33 worktrees on this machine therefore
## resolves `user://` to the SAME directory, `%APPDATA%/Godot/app_userdata/P(Doom)/`.
## scripts/run_godot_tests.py called subprocess.run() with no `env=`, so each headless
## run inherited the developer's APPDATA. On 2026-08-07 that took Pip's 2026-07-31
## league board from 50 entries to 0 and rewrote his config.cfg / keybinds.cfg /
## theme.cfg mid-session.
##
## Two separate things had to be true for that damage, and this file pins BOTH:
##   1. The tests ran against the real profile   -> test_user_dir_is_not_the_real_profile
##   2. The tests left ~1,300 files behind        -> test_property_boards_are_cleaned_up
## Isolation alone would only move the mess somewhere else. The litter guard is what
## makes a future regression visible instead of merely relocated.
##
## HOW THIS FAILS: run the suite with a bare `godot --headless` (no APPDATA override)
## and case 1 goes red naming the real Roaming path. That is exactly how it was proven
## before the runner fix landed.
##
## NOTE ON WHAT THIS CANNOT PROVE: it cannot stop a developer who invokes Godot by hand
## from writing to their own profile. It only guarantees the SUPPORTED entry point
## (scripts/run_godot_tests.py) is safe, and that a run which somehow is not gets caught
## rather than silently eating a board.

const LEADERBOARD_DIR := "user://leaderboards"

func _normalised_user_dir() -> String:
	return OS.get_user_data_dir().replace("\\", "/").to_lower()

func test_user_dir_is_not_the_real_profile():
	# The literal path that was damaged. Named explicitly rather than checked
	# generically, so the failure message points at the actual casualty.
	var dir := _normalised_user_dir()
	assert_false(dir.contains("appdata/roaming"),
		("tests are writing to the developer's LIVE profile at %s -- " +
		 "run via scripts/run_godot_tests.py, which sets an isolated APPDATA " +
		 "(XDG_DATA_HOME has NO effect on Windows; that was tried)") % OS.get_user_data_dir())

func test_runner_supplied_a_sandbox():
	# Belt and braces for the case above: when the supported runner is used it exports
	# PDOOM1_USERDATA_SANDBOX, and user:// must actually resolve inside it. A run
	# without the var (a hand-rolled `godot --headless`) skips this rather than
	# failing, because case 1 already covers the dangerous half.
	var sandbox := OS.get_environment("PDOOM1_USERDATA_SANDBOX")
	if sandbox == "":
		pass_test("not launched via run_godot_tests.py -- case 1 above is the real gate")
		return
	assert_true(_normalised_user_dir().begins_with(sandbox.replace("\\", "/").to_lower()),
		"the runner declared a sandbox at %s but user:// resolved to %s" % [sandbox, OS.get_user_data_dir()])

func test_property_boards_are_cleaned_up():
	# test_leaderboard_properties.gd creates one board file per property iteration and
	# used to delete none of them: 1,302 files in a five-second burst, all named
	# leaderboard_test_prop_<n>_<usec>__test.json. GUT runs suites in filename order,
	# so by the time this file runs those boards have already been created -- and, once
	# that suite cleans up after itself, already removed.
	var dir := DirAccess.open(LEADERBOARD_DIR)
	if dir == null:
		pass_test("no leaderboards dir in this profile -- nothing could have been littered")
		return
	var leftovers: Array = []
	dir.list_dir_begin()
	var f := dir.get_next()
	while f != "":
		if f.begins_with("leaderboard_test_prop_"):
			leftovers.append(f)
		f = dir.get_next()
	dir.list_dir_end()
	assert_eq(leftovers.size(), 0,
		"%d property-test board files were left behind (e.g. %s) -- a test that creates a board must delete it" % [
			leftovers.size(), str(leftovers.slice(0, 3))])

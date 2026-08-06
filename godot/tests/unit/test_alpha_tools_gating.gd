extends GutTest
## THE GATE SPLIT (2026-08-05) -- the regression that cost a playtest, pinned.
##
## PR #1079 made the DEV BUILD badge conditional on OS.is_debug_build(). Correct for the
## badge. But the ALPHA TOOLS overlay, the flight recorder, the UI evolution recorder and
## the perf log all hung off the SAME BuildInfo.is_dev_build(), so they silently switched
## off in release exports too -- and Pip discovered it at a friend's house when backslash
## stopped working ("I wasn't able to bump doom").
##
## These tests assert the SPLIT, both directions, under SIMULATED release conditions
## (BuildInfo._debug_run_override -- a headless GUT run is always a debug run, so without
## that hook the release branch of every gate is untestable and can only be found in the
## field). Limit, stated plainly: this simulates the DISCRIMINATOR, not an actual exported
## release build. A real release-template export still needs a human press of backslash.

var _saved_debug_override
var _saved_perf_override

func before_each():
	_saved_debug_override = BuildInfo._debug_run_override
	_saved_perf_override = PerfLog._enabled_override
	PerfLog._enabled_override = null  # follow the build gate, not a leftover test forcing

func after_each():
	BuildInfo._debug_run_override = _saved_debug_override
	PerfLog._enabled_override = _saved_perf_override


# --- The split itself -------------------------------------------------------------

func test_release_build_hides_the_badge_but_keeps_alpha_tools():
	BuildInfo._debug_run_override = false
	assert_false(BuildInfo.is_dev_build(),
		"a release-template export is not a dev build")
	assert_eq(BuildInfo.get_badge_text(), BuildInfo.get_release_badge_text(),
		"#1067: a public release must NOT wear the amber DEV BUILD banner")
	assert_true(BuildInfo.are_alpha_tools_available(),
		"but the ALPHA TOOLS overlay must still be reachable -- #1104's sticky unranked "
		+ "flag, not the build type, is what protects the board")

func test_dev_build_gets_both():
	BuildInfo._debug_run_override = true
	assert_true(BuildInfo.is_dev_build(), "a debug run is a dev build")
	assert_true(BuildInfo.are_alpha_tools_available(), "and has the tools")

func test_alpha_tools_gate_is_independent_of_the_build_type():
	# The whole point: the two gates must not be the same expression again.
	BuildInfo._debug_run_override = false
	var release_tools := BuildInfo.are_alpha_tools_available()
	BuildInfo._debug_run_override = true
	assert_eq(release_tools, BuildInfo.are_alpha_tools_available(),
		"are_alpha_tools_available() must not depend on OS.is_debug_build()")


# --- The overlay actually builds under release conditions ---------------------------

func test_overlay_builds_under_release_conditions():
	# The direct proof of Pip's bug. Before the split this overlay early-returned with
	# _built == false in a release build, so backslash did nothing.
	BuildInfo._debug_run_override = false
	var overlay := DevModeOverlay.new()
	add_child_autofree(overlay)
	assert_true(overlay._built,
		"backslash overlay must build in a release build (this is the #1079 regression)")
	assert_not_null(overlay._root, "and have a togglable root control")

func test_overlay_toggles_under_release_conditions():
	BuildInfo._debug_run_override = false
	var overlay := DevModeOverlay.new()
	add_child_autofree(overlay)
	overlay._on_toggle()
	assert_true(overlay._root.visible, "first backslash opens it in a release build")
	overlay._on_toggle()
	assert_false(overlay._root.visible, "second backslash closes it")

func test_overlay_header_shows_the_build_identity_in_release_too():
	BuildInfo._debug_run_override = false
	var stamp := BuildInfo.get_tools_stamp_text()
	assert_string_contains(stamp, GameConfig.CURRENT_VERSION,
		"'which build is this?' must be answerable from the overlay in someone else's lounge")
	assert_ne(stamp.strip_edges(), "", "never blank")


# --- The recorders and the perf log deliberately STAY build-gated --------------------
#
# Ruling (build_info.gd carries the full reasoning): these three write to a player's disk.
# F6 dumps a screenshot plus the whole GameState; F7 is a SILENT screenshot with no
# confirmation at all; the perf log writes continuously and unprompted, rotating at 5MB.
# The overlay's risk was the leaderboard, and #1104 solved that. Their risk is the disk,
# and nothing solves that except not running them. No one asked for them in a shipped build.

func test_flight_recorder_stays_off_in_a_release_build():
	BuildInfo._debug_run_override = false
	var fr := FlightRecorder.new()
	add_child_autofree(fr)
	assert_false(fr._built,
		"F6 writes a screenshot + full state dump to disk -- not in a shipped build")

func test_ui_evolution_recorder_stays_off_in_a_release_build():
	BuildInfo._debug_run_override = false
	var rec := UIEvolutionRecorder.new()
	add_child_autofree(rec)
	assert_false(rec._built,
		"F7 is a SILENT screenshot -- strictly worse than F6 to ship")

func test_perf_log_stays_off_in_a_release_build():
	BuildInfo._debug_run_override = false
	assert_false(PerfLog.is_active(),
		"perf.log writes unprompted and continuously -- the invisible-recorder case")

func test_all_three_come_back_in_a_dev_build():
	BuildInfo._debug_run_override = true
	assert_true(PerfLog.is_active(), "perf log runs in dev")
	var fr := FlightRecorder.new()
	add_child_autofree(fr)
	assert_true(fr._built, "F6 runs in dev")
	var rec := UIEvolutionRecorder.new()
	add_child_autofree(rec)
	assert_true(rec._built, "F7 runs in dev")

extends GutTest
## Tests for the DEV BUILD indicator + open-ledger keybind.
##
## Covers the pure readers: BuildInfo.get_stamp()/get_badge_text() must always return a
## non-empty string (never a blank overlay), and the open_ledger keybind action must be
## registered on L. The actual on-screen badge/leather look still needs a human eye.

func test_build_stamp_reader_returns_non_empty():
	# Even with no stamp file, the reader degrades to "unstamped" rather than blank.
	assert_ne(BuildInfo.get_stamp(), "", "Build stamp must never be empty")

func test_dev_badge_text_includes_version_and_dev_marker():
	var text := BuildInfo.get_dev_badge_text()
	assert_ne(text, "", "Badge text must never be empty")
	assert_string_contains(text, "DEV BUILD", "Dev badge must read as a dev build")
	assert_string_contains(text, GameConfig.CURRENT_VERSION,
		"Badge must show the current version so the tester can confirm the build")

func test_release_badge_text_is_version_only():
	# Issue #1067: the public v0.13.2 release showed "DEV BUILD" on every screen and
	# players read it as "I downloaded the wrong file". The release form must carry
	# the version (support value) and nothing scary.
	var text := BuildInfo.get_release_badge_text()
	assert_string_contains(text, GameConfig.CURRENT_VERSION,
		"Release badge still identifies the version")
	assert_false(text.contains("DEV BUILD"),
		"Release badge must never read as a dev build")

func test_badge_text_matches_run_kind():
	# get_badge_text() must pick the form that matches this run's is_dev_build().
	if BuildInfo.is_dev_build():
		assert_eq(BuildInfo.get_badge_text(), BuildInfo.get_dev_badge_text(),
			"Dev runs get the loud DEV BUILD form")
	else:
		assert_eq(BuildInfo.get_badge_text(), BuildInfo.get_release_badge_text(),
			"Release builds get the quiet version-only form")

func test_is_dev_build_returns_bool():
	assert_typeof(BuildInfo.is_dev_build(), TYPE_BOOL, "is_dev_build() should return a bool")

func test_is_dev_build_requires_debug_run():
	# The load-bearing formula (issue #1067): a release-template export, where
	# OS.is_debug_build() is false, can NEVER be a dev build regardless of the
	# DEV_BUILD const. In this test environment (editor/debug) both sides are true.
	assert_eq(BuildInfo.is_dev_build(), BuildInfo.DEV_BUILD and OS.is_debug_build(),
		"is_dev_build() must AND the manual switch with the debug-run discriminator")

func test_open_ledger_keybind_registered_on_L():
	assert_true(KeybindManager.keybinds.has("open_ledger"),
		"open_ledger action must be registered as a named keybind")
	assert_eq(KeybindManager.keybinds["open_ledger"]["key"], KEY_L,
		"open_ledger should default to the L key")

func test_open_ledger_keybind_has_readable_name():
	assert_eq(KeybindManager.get_key_name("open_ledger"), "L",
		"open_ledger should surface a human-readable key name")

# --- Honest badge (L1 follow-up: a stale baked stamp cost a playtest session) ---------

func test_live_git_stamp_reflects_this_checkout():
	# This suite runs inside a git checkout (clone or worktree), so the live probe must
	# find HEAD -- the dev badge can therefore never be a silently stale baked stamp.
	var live := BuildInfo.get_live_git_stamp()
	if live.is_empty():
		pending("git unavailable here -- exported-build fallback path (stamp marked '(stamp)')")
		return
	assert_string_contains(live, "@", "live identity carries branch@sha")
	assert_string_contains(BuildInfo.get_stamp(), "live",
		"a dev checkout's badge is marked live, not a baked stamp")

func test_stamped_fallback_is_visibly_a_stamp_never_live():
	# The fallback format must self-identify: when the badge is NOT live git, it says
	# "(stamp)" (or "unstamped") -- two checkouts can never show the same badge silently.
	var stamp := BuildInfo.get_stamp()
	assert_true(stamp.contains("live") or stamp.contains("(stamp)") or stamp == "unstamped",
		"every badge form declares its provenance (live / stamp / unstamped), got: %s" % stamp)

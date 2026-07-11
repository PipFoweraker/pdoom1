extends GutTest
## Tests for the DEV BUILD indicator + open-ledger keybind.
##
## Covers the pure readers: BuildInfo.get_stamp()/get_badge_text() must always return a
## non-empty string (never a blank overlay), and the open_ledger keybind action must be
## registered on L. The actual on-screen badge/leather look still needs a human eye.

func test_build_stamp_reader_returns_non_empty():
	# Even with no stamp file, the reader degrades to "unstamped" rather than blank.
	assert_ne(BuildInfo.get_stamp(), "", "Build stamp must never be empty")

func test_badge_text_includes_version_and_dev_marker():
	var text := BuildInfo.get_badge_text()
	assert_ne(text, "", "Badge text must never be empty")
	assert_string_contains(text, "DEV BUILD", "Badge must read as a dev build")
	assert_string_contains(text, GameConfig.CURRENT_VERSION,
		"Badge must show the current version so the tester can confirm the build")

func test_is_dev_build_returns_bool():
	assert_typeof(BuildInfo.is_dev_build(), TYPE_BOOL, "is_dev_build() should return a bool")

func test_open_ledger_keybind_registered_on_L():
	assert_true(KeybindManager.keybinds.has("open_ledger"),
		"open_ledger action must be registered as a named keybind")
	assert_eq(KeybindManager.keybinds["open_ledger"]["key"], KEY_L,
		"open_ledger should default to the L key")

func test_open_ledger_keybind_has_readable_name():
	assert_eq(KeybindManager.get_key_name("open_ledger"), "L",
		"open_ledger should surface a human-readable key name")

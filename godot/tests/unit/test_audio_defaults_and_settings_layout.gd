extends GutTest
## Guards three defects Pip reported out loud in the 2026-08-01 playtest, plus
## the one he fixed by hand on 2026-07-31 without reporting it at all.
##
## 1. Music default too loud. He turned the slider to 13% by hand on 07-31
##    ("I hate this fucking music. Escape. Music way down.") and asked for 15%
##    on 08-01 at 11:38. The default is now 15.
## 2. The startup bed was the wrong track (11:06, 11:30). Tier 0 -- the bed a
##    player hears for most of an early run -- is now checkpoint_saved.ogg.
## 3. "Graphics Settings" rendered as a header with nothing under it. The rows
##    existed and were wired the whole time; they were simply below the fold of
##    a ScrollContainer that had been given half the vertical space it needed.
##
## HONEST LIMITATION -- READ BEFORE TRUSTING A GREEN RUN. Not one assertion here
## hears anything. These tests prove which file is referenced, what number is
## declared, and what rectangle encloses what. Whether checkpoint_saved.ogg is
## actually the calmer bed Pip meant, and whether -22.5 dBFS is actually a
## comfortable listening level in his room, can only be settled by Pip pressing
## play. Likewise the layout assertions prove a row is inside the viewport, not
## that the screen looks good.

const GAME_CONFIG_SCRIPT := "res://autoload/game_config.gd"
const SETTINGS_MENU_SCENE := "res://scenes/settings_menu.tscn"
const SETTINGS_MENU_SCRIPT := "res://scripts/ui/settings_menu.gd"
const CALM_BED := "res://assets/audio/music/checkpoint_saved.ogg"

# The value Pip asked for at 11:38. Pinned as a literal so a future edit that
# drifts the default has to argue with a named human request.
const EXPECTED_MUSIC_DEFAULT := 15

## ---- 1. Audio defaults ----

func _fresh_config() -> Object:
	# A bare script instance, NOT the /root/GameConfig autoload. The autoload has
	# already run load_config() against this machine's real user://config.cfg, so
	# its live music_volume is whatever Pip last chose -- useless for asserting on
	# the DEFAULT. A never-readied instance still carries the declared values.
	return load(GAME_CONFIG_SCRIPT).new()

func test_default_music_volume_is_fifteen_percent():
	var cfg = _fresh_config()
	assert_eq(cfg.music_volume, EXPECTED_MUSIC_DEFAULT,
		"Fresh-install music default (Pip 2026-08-01 11:38: 'set the default volume down at like 15%')")
	cfg.free()

func test_music_bus_routes_through_master_so_gains_multiply():
	# The loudness claim in the commit message -- master 50% x music 15% = 0.075
	# linear -- is only true if the Music bus SENDS to Master. Check it rather
	# than assume it: a bus layout edit that reroutes Music straight to the
	# output would silently make the shipped default 15% instead of 7.5%.
	if AudioServer.get_bus_count() <= MusicManager.MUSIC_BUS_INDEX:
		# Headless with a dummy driver can come up with the stock 1-bus layout.
		# Say so out loud rather than passing vacuously.
		pass_test("no Music bus in this audio driver; routing not checked")
		return
	var music_bus := AudioServer.get_bus_index("Music")
	assert_eq(music_bus, MusicManager.MUSIC_BUS_INDEX,
		"MusicManager.MUSIC_BUS_INDEX must match the real bus layout")
	assert_eq(str(AudioServer.get_bus_send(music_bus)), "Master",
		"Music must send to Master for master_volume to attenuate music")

func test_default_effective_music_loudness_is_quiet_but_audible():
	var cfg = _fresh_config()
	var effective: float = (float(cfg.master_volume) / 100.0) * (float(cfg.music_volume) / 100.0)
	var effective_db: float = linear_to_db(effective)
	cfg.free()
	# 0.50 x 0.15 = 0.075 -> -22.5 dBFS. Beds are normalised to ~-16 LUFS, so
	# the program sits near -38.5 LUFS at the output.
	assert_almost_eq(effective, 0.075, 0.0005, "master x music linear gain")
	assert_between(effective_db, -23.5, -21.5, "effective music gain in dBFS")

func test_saved_preference_still_wins_over_the_new_default():
	# The requirement was "change the DEFAULT only". load_config() must pass the
	# in-memory value as ConfigFile's fallback, which is what makes a stored
	# preference survive a default change. Asserted at the source, because the
	# behavioural version would have to write this machine's real config.cfg.
	var src := FileAccess.get_file_as_string(GAME_CONFIG_SCRIPT)
	assert_string_contains(src,
		'music_volume = config.get_value("audio", "music_volume", music_volume)',
		"load_config must fall back to the declared default, never overwrite a stored one")

## ---- 2. The startup bed ----

func test_tier_zero_bed_is_the_calm_track():
	var tier0: Array = MusicManager.MUSIC_TIER_STEMS[0]
	assert_eq(tier0.size(), 1, "tier 0 is a single bed until stems are commissioned")
	assert_eq(tier0[0]["path"], CALM_BED,
		"Tier 0 is the bed heard most; Pip 11:30 asked for the slower gentler one")

func test_gameplay_fallback_playlist_starts_on_the_same_bed():
	# The legacy playlist only runs if the adaptive build fails, but when it does
	# it must not resurrect the track Pip asked to retire from the start slot.
	var playlist: Array = MusicManager.music_library[MusicManager.MusicContext.GAMEPLAY]
	assert_eq(playlist[0], CALM_BED, "fallback playlist head must track MUSIC_TIER_STEMS[0]")

func test_every_tier_bed_still_resolves():
	# A swap that typos a path degrades silently: _build_adaptive_stream() skips
	# the missing stem and inherits a neighbour's, so the game still plays music
	# and nothing looks wrong.
	for tier in range(MusicManager.MUSIC_TIER_STEMS.size()):
		for stem in MusicManager.MUSIC_TIER_STEMS[tier]:
			assert_true(ResourceLoader.exists(stem["path"]),
				"tier %d stem missing: %s" % [tier, stem["path"]])

## ---- 3. The settings screen ----
##
## Rebuilt 2026-08-02 per Pip's ruling (#1096): Direction 5 front card (the five
## first-five-minutes controls) + Direction 1 operations board behind the
## ">> ALL PROTOCOLS" door. The old single scrolling column is gone, so the old
## fold-geometry assertions are restated against the new structure: the INTENT
## each test guards is unchanged and named in its comment.

func _build_settings_menu() -> Control:
	var menu: Control = load(SETTINGS_MENU_SCENE).instantiate()
	add_child_autofree(menu)
	return menu

func test_front_card_is_the_default_view():
	# Direction 5's bet: a drive-by adjuster lands on five controls, not a wall.
	var menu := _build_settings_menu()
	await get_tree().process_frame
	assert_true((menu.get_node("FrontCard") as Control).visible,
		"the front card is the default view")
	assert_false((menu.get_node("Board") as Control).visible,
		"the operations board opens only through the ALL PROTOCOLS door")

func test_nothing_can_hide_below_a_fold():
	# THE ORIGINAL DEFECT, restated. Six shipped sections spent weeks invisible
	# below the fold of a half-starved ScrollContainer. The rebuild's answer is
	# structural: no scroll region exists anywhere in the scene, so there is no
	# fold for a control to hide behind.
	var menu := _build_settings_menu()
	assert_null(_find_scroll(menu),
		"no ScrollContainer in settings -- nothing scrolls, nothing hides")

func _find_scroll(node: Node) -> Node:
	if node is ScrollContainer:
		return node
	for child in node.get_children():
		var hit := _find_scroll(child)
		if hit != null:
			return hit
	return null

func test_front_card_serves_the_five_first_minute_intents():
	# Volume, music, fullscreen, hints, colorblind: the five intents nearly every
	# early settings visit is one of (SETTINGS_MENU_OPTIONS.md, Direction 5).
	var menu := _build_settings_menu()
	var card := "FrontCard/Card/Margin/CardVBox"
	for row in ["VolumeRow", "MusicRow", "FullscreenRow", "HintsRow", "ColorblindRow"]:
		assert_not_null(menu.get_node_or_null(card + "/" + row),
			"front card must carry %s" % row)
	assert_not_null(menu.get_node_or_null(card + "/AllProtocolsButton"),
		"the one door to everything else must exist")

func test_board_carries_the_full_inventory():
	# Direction 1's promise: EVERY remaining control visible at once on the board,
	# so a privacy sweep or a settings audit is one glance, zero navigation.
	var menu := _build_settings_menu()
	var expectations := {
		"Board/BoardVBox/Columns/Col1/MasterSlider": "master volume",
		"Board/BoardVBox/Columns/Col1/SFXSlider": "sfx volume",
		"Board/BoardVBox/Columns/Col1/MusicSlider": "music volume",
		"Board/BoardVBox/Columns/Col1/FullscreenRow": "fullscreen",
		"Board/BoardVBox/Columns/Col2/IntrosRow": "story intros",
		"Board/BoardVBox/Columns/Col2/HintsRow": "gameplay hints",
		"Board/BoardVBox/Columns/Col2/RivalsRow": "rival intel feed (new: was WATCH-screen-only)",
		"Board/BoardVBox/Columns/Col2/DifficultyRow": "research intensity (write path owned by #1084)",
		"Board/BoardVBox/Columns/Col2/ThemeRow": "visual theme",
		"Board/BoardVBox/Columns/Col2/UILayoutRow": "UI layout A/B",
		"Board/BoardVBox/Columns/Col2/ColorblindRow": "colorblind mode",
		"Board/BoardVBox/Columns/Col3/LeaderboardRow": "leaderboard identity consent",
		"Board/BoardVBox/Columns/Col3/LaunchPingRow": "anonymous launch ping",
		"Board/BoardVBox/Columns/Col3/KeybindingsButton": "keybindings jump-off",
	}
	for path in expectations:
		assert_not_null(menu.get_node_or_null(path),
			"board must show %s (%s)" % [expectations[path], path])

func test_board_fits_the_frame_without_overflow():
	# The no-scroll bet only holds if the board actually FITS. Geometry check at
	# the design viewport; smaller test windows can't judge this fairly, so they
	# skip loudly instead of passing vacuously.
	var menu := _build_settings_menu()
	menu.call("_show_board")
	await get_tree().process_frame
	await get_tree().process_frame

	var vp := menu.get_viewport_rect()
	if vp.size.x < 1280 or vp.size.y < 720:
		pass_test("viewport %s too small to judge the 1080p board layout" % vp.size)
		return

	var board: Control = menu.get_node("Board")
	for path in ["Board/BoardVBox/Columns/Col1/FullscreenRow",
			"Board/BoardVBox/Columns/Col3/KeybindingsButton",
			"Board/BoardVBox/FooterRow"]:
		var row: Control = menu.get_node(path)
		assert_true(board.get_global_rect().encloses(row.get_global_rect()),
			"%s must sit inside the board frame (board=%s row=%s)" % [
				path, board.get_global_rect(), row.get_global_rect()])

func test_no_dead_graphics_quality_control():
	# GameConfig.graphics_quality is still declared and still persists, but
	# apply_graphics_settings() carries a TODO and does nothing with it. A
	# Low/Medium/High dropdown wired to that is a control that lies. Guard both
	# halves: no such row anywhere in either view, and no handler to feed one.
	var menu := _build_settings_menu()
	assert_null(menu.find_child("QualityRow", true, false),
		"do not re-add a quality dropdown until apply_graphics_settings() honours it")
	assert_false(menu.has_method("_on_graphics_quality_changed"),
		"handler for a control that does nothing must not linger")

func test_apply_button_is_dead_and_autosave_replaces_it():
	# The old model applied every change live but persisted only on Apply, so
	# Back-without-Apply silently reverted on next launch -- settings that "worked"
	# until the player restarted. The rebuild's rule: no Apply button anywhere,
	# a debounced save on change, and a flush on every exit path.
	var menu := _build_settings_menu()
	await get_tree().process_frame
	assert_null(menu.find_child("ApplyButton", true, false),
		"there is no Apply button; saving is not the player's job")
	assert_false(menu.has_method("_on_apply_pressed"), "Apply handler must be gone")

	var src := FileAccess.get_file_as_string(SETTINGS_MENU_SCRIPT)
	assert_string_contains(src, "func _exit_tree():",
		"an exit backstop must exist so navigation can never discard changes")
	assert_string_contains(src, "_flush_save()",
		"exits must flush the debounced save")

	# Mechanism check without touching any real setting value: scheduling arms
	# the timer and marks dirty; disarm afterwards so autofree cannot write the
	# machine's real user://config.cfg from a test.
	menu.call("_schedule_save")
	assert_true(bool(menu.get("_dirty")), "a change must mark the config dirty")
	var timer: Timer = menu.get("_save_timer")
	assert_false(timer.is_stopped(), "a change must arm the debounced save timer")
	timer.stop()
	menu.set("_dirty", false)

func test_stale_shortcuts_grid_is_gone():
	# The static grid advertised [F5] Quick save / [F9] Quick load; no F5 binding
	# exists and F9 is a debug-only layout flip. Stale text posing as documentation
	# -- the silent-wrongness flavour league week taught us to fear. The real,
	# self-maintaining keybind screen is linked from BOTH views instead.
	var menu := _build_settings_menu()
	assert_null(menu.find_child("ShortcutsGrid", true, false),
		"the hand-maintained shortcuts grid must stay dead (it drifted from reality)")
	assert_null(menu.find_child("KeyboardShortcuts", true, false),
		"no static keyboard-reference section; the keybind screen is the truth")
	assert_not_null(menu.get_node_or_null("FrontCard/Card/Margin/CardVBox/KeybindingsButton"),
		"front card must link the real keybind screen")
	assert_not_null(menu.get_node_or_null("Board/BoardVBox/Columns/Col3/KeybindingsButton"),
		"board must link the real keybind screen")

func test_fullscreen_toggle_is_wired_to_something_real():
	# The row that survived has to actually work. GameConfig.apply_graphics_settings()
	# is the only thing standing between the checkbox and the window mode.
	var src := FileAccess.get_file_as_string(GAME_CONFIG_SCRIPT)
	assert_string_contains(src, "DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)",
		"fullscreen must reach DisplayServer")
	var ui_src := FileAccess.get_file_as_string(SETTINGS_MENU_SCRIPT)
	assert_string_contains(ui_src, 'GameConfig.set_setting("fullscreen", pressed, false)',
		"the checkbox must write the setting that apply_graphics_settings() reads")

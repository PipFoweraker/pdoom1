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

func _build_settings_menu() -> Control:
	var menu: Control = load(SETTINGS_MENU_SCENE).instantiate()
	add_child_autofree(menu)
	return menu

func test_graphics_section_rows_are_visible_without_scrolling():
	# THE DEFECT. VBox is anchor-centred with fixed +-400/+-300 offsets, so it is
	# 800x600 at any window size and this measurement is screen-independent.
	# Scroll and Spacer both carried size_flags_vertical = 3, so they split the
	# leftover height evenly and the scroll viewport came out near 179 px -- just
	# enough for the three audio sliders and the "Graphics Settings" header, and
	# nothing else. Collapsing the (unused) Spacer hands that space back.
	var menu := _build_settings_menu()
	await get_tree().process_frame
	await get_tree().process_frame

	var scroll: ScrollContainer = menu.get_node("VBox/Scroll")
	var section := "VBox/Scroll/SettingsContainer/GraphicsSettings"
	var header: Node = menu.get_node(section)
	assert_not_null(header, "Graphics section must exist")

	var row: Control = menu.get_node(section + "/FullscreenRow")
	assert_true(scroll.get_global_rect().encloses(row.get_global_rect()),
		"Fullscreen row must be inside the scroll viewport (scroll=%s row=%s)" % [
			scroll.get_global_rect(), row.get_global_rect()])

func test_graphics_section_is_not_an_empty_header():
	# Stated separately from the geometry so the intent survives a future
	# relayout: whatever the rects end up being, the section must have content.
	var menu := _build_settings_menu()
	await get_tree().process_frame
	var section: Node = menu.get_node("VBox/Scroll/SettingsContainer/GraphicsSettings")
	var rows := 0
	for child in section.get_children():
		if child is HBoxContainer:
			rows += 1
	assert_gt(rows, 0, "a section header with no rows under it is worse than no section")

func test_scrollbar_is_always_visible():
	# The list is longer than the viewport even after the fix, and it always will
	# be. SHOW_ALWAYS (2) is the affordance that says so; on AUTO the dark-theme
	# bar is easy to miss, which is half of why the cut-off section read as empty.
	var menu := _build_settings_menu()
	var scroll: ScrollContainer = menu.get_node("VBox/Scroll")
	assert_eq(scroll.vertical_scroll_mode, ScrollContainer.SCROLL_MODE_SHOW_ALWAYS,
		"settings list must advertise that it scrolls")

func test_no_dead_graphics_quality_control():
	# GameConfig.graphics_quality is still declared and still persists, but
	# apply_graphics_settings() carries a TODO and does nothing with it. A
	# Low/Medium/High dropdown wired to that is a control that lies. Guard both
	# halves: the row is gone, and the handler that fed it is gone.
	var menu := _build_settings_menu()
	assert_null(menu.get_node_or_null("VBox/Scroll/SettingsContainer/GraphicsSettings/QualityRow"),
		"do not re-add a quality dropdown until apply_graphics_settings() honours it")
	assert_false(menu.has_method("_on_graphics_quality_changed"),
		"handler for a control that does nothing must not linger")

func test_fullscreen_toggle_is_wired_to_something_real():
	# The row that survived has to actually work. GameConfig.apply_graphics_settings()
	# is the only thing standing between the checkbox and the window mode.
	var src := FileAccess.get_file_as_string(GAME_CONFIG_SCRIPT)
	assert_string_contains(src, "DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)",
		"fullscreen must reach DisplayServer")
	var ui_src := FileAccess.get_file_as_string(SETTINGS_MENU_SCRIPT)
	assert_string_contains(ui_src, 'GameConfig.set_setting("fullscreen", pressed, false)',
		"the checkbox must write the setting that apply_graphics_settings() reads")

extends GutTest
## Adaptive doom-band music (docs/audio/MUSIC_DESIGN.md).
## Covers the pure doom->tier mapping, the placeholder stream builder, and the
## read-only wiring. Audio is a pure view-layer side-effect (ADR-0006): these
## tests also pin that the music system only LISTENS to game state.

var _saved_tier: int = 0

func before_each():
	_saved_tier = MusicManager._current_music_tier
	MusicManager._tier_override = -1  # never let an audition override leak between tests

func after_each():
	MusicManager._current_music_tier = _saved_tier
	MusicManager._tier_override = -1

func test_tier_mapping_tracks_canonical_bands():
	# One probe per canonical ThemeManager band (below: 15/37/52/67/80/92/101),
	# against the documented band->tier collapse [0,1,1,2,2,3,4].
	assert_eq(MusicManager.music_tier_for_doom(0.0), 0, "NOMINAL -> cosy")
	assert_eq(MusicManager.music_tier_for_doom(10.0), 0, "NOMINAL -> cosy")
	assert_eq(MusicManager.music_tier_for_doom(20.0), 1, "ELEVATED -> uneasy")
	assert_eq(MusicManager.music_tier_for_doom(40.0), 1, "HIGH -> uneasy")
	assert_eq(MusicManager.music_tier_for_doom(60.0), 2, "SEVERE -> spooky")
	assert_eq(MusicManager.music_tier_for_doom(75.0), 2, "EXTREME -> spooky")
	assert_eq(MusicManager.music_tier_for_doom(85.0), 3, "CATASTROPHIC -> eldritch")
	assert_eq(MusicManager.music_tier_for_doom(95.0), 4, "TERMINAL -> terminal")
	assert_eq(MusicManager.music_tier_for_doom(100.0), 4, "TERMINAL -> terminal")

func test_tier_mapping_is_monotonic():
	# Rising doom must never lower the music tier (the ratchet direction).
	var previous := -1
	for doom in range(0, 101):
		var tier: int = MusicManager.music_tier_for_doom(float(doom))
		assert_true(tier >= previous, "Tier dropped at doom %d" % doom)
		assert_between(tier, 0, MusicManager.MUSIC_TIER_NAMES.size() - 1,
			"Tier out of range at doom %d" % doom)
		previous = tier

func test_tier_config_shapes_agree():
	# The band->tier table must cover all 7 canonical bands and only name
	# tiers that exist in both the name list and the stem config.
	assert_eq(MusicManager.MUSIC_TIER_BY_BAND.size(), 7,
		"One entry per canonical doom band")
	assert_eq(MusicManager.MUSIC_TIER_STEMS.size(),
		MusicManager.MUSIC_TIER_NAMES.size(),
		"Stem config and tier names must align")
	for tier in MusicManager.MUSIC_TIER_BY_BAND:
		assert_between(tier, 0, MusicManager.MUSIC_TIER_NAMES.size() - 1,
			"Band maps to a nonexistent tier")

func test_set_doom_level_updates_tier_without_audio():
	# Nothing is playing in headless tests; set_doom_level must still track
	# the tier and never crash (never-block-on-missing-audio constraint).
	MusicManager.set_doom_level(95.0)
	assert_eq(MusicManager._current_music_tier, 4, "Terminal doom -> tier 4")
	MusicManager.set_doom_level(0.0)
	assert_eq(MusicManager._current_music_tier, 0, "Doom relief -> tier 0")

func test_build_adaptive_stream_has_one_clip_per_tier():
	var stream = MusicManager._build_adaptive_stream()
	if stream == null:
		# Audio assets absent (e.g. stripped CI checkout): graceful null is
		# the contract, not a failure.
		pass_test("No stems available; builder degraded gracefully to null")
		return
	assert_eq(stream.clip_count, MusicManager.MUSIC_TIER_NAMES.size(),
		"One clip per music tier")
	for tier in range(stream.clip_count):
		assert_eq(String(stream.get_clip_name(tier)),
			MusicManager.MUSIC_TIER_NAMES[tier], "Clip name matches tier name")
		assert_not_null(stream.get_clip_stream(tier),
			"Every tier has a stream (gap-filled from neighbours)")

func test_gameplay_context_goes_adaptive_and_takes_tier_switches():
	# End-to-end through the public surface: entering GAMEPLAY builds and
	# starts the interactive stream (dummy audio driver in headless is fine),
	# and doom updates route to it without error.
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	if MusicManager._adaptive_stream == null:
		_silence_music()
		pass_test("No audio assets in this checkout; degraded to playlist as designed")
		return
	assert_true(MusicManager._adaptive_active, "GAMEPLAY should engage adaptive mode")
	assert_not_null(MusicManager._adaptive_playback(),
		"Interactive playback should be live on a player")
	MusicManager.set_doom_level(95.0)
	assert_eq(MusicManager._current_music_tier, 4, "Doom 95 -> terminal tier")
	assert_not_null(MusicManager._adaptive_playback(),
		"Playback survives a tier switch")
	MusicManager.set_doom_level(5.0)
	assert_eq(MusicManager._current_music_tier, 0, "Doom 5 -> cosy tier")
	_silence_music()

## Synchronous cleanup so later tests never see leftover playback.
func _silence_music():
	MusicManager._adaptive_active = false
	MusicManager.current_context = MusicManager.MusicContext.MENU
	for player in [MusicManager.player_a, MusicManager.player_b]:
		if player != null:
			player.stop()
			player.stream = null

func test_doom_signal_wiring_is_listen_only():
	# MusicManager subscribes to game_state_updated (read-only). It must not
	# be connected to anything that WRITES game state; the only game-facing
	# coupling is this one listener.
	assert_true(
		GameManager.game_state_updated.is_connected(MusicManager._on_game_state_for_music),
		"MusicManager listens to game_state_updated")
	# And the handler tolerates a minimal/malformed state dict.
	MusicManager._on_game_state_for_music({})
	assert_eq(MusicManager._current_music_tier, 0, "Missing doom key reads as 0")


# === Audition override -- the ALPHA TOOLS music player (Pip 2026-08-05) ==============
#
# The point of the feature is that a track can be HELD against live game state, so the
# thing to pin is exactly that: doom keeps moving and does NOT take the tier back.

func test_override_holds_the_tier_against_live_doom():
	MusicManager.set_doom_level(0.0)
	MusicManager.set_tier_override(4)
	assert_true(MusicManager.is_tier_overridden(), "override is engaged")
	assert_eq(MusicManager.get_current_music_tier(), 4, "the held tier is what plays")
	MusicManager.set_doom_level(10.0)   # automatic would be 0
	MusicManager.set_doom_level(60.0)   # automatic would be 2
	assert_eq(MusicManager.get_current_music_tier(), 4,
		"doom must NOT reclaim the tier while a human is auditioning")
	assert_eq(MusicManager.get_auto_music_tier(), 2,
		"automatic tier is still tracked underneath, for the readout and the release")

func test_release_snaps_to_where_doom_is_now_not_where_it_was():
	MusicManager.set_doom_level(0.0)
	MusicManager.set_tier_override(4)
	MusicManager.set_doom_level(95.0)
	MusicManager.clear_tier_override()
	assert_false(MusicManager.is_tier_overridden(), "override released")
	assert_eq(MusicManager.get_current_music_tier(), 4,
		"release follows doom NOW (95 -> tier 4), not the tier doom had at override time")
	MusicManager.set_doom_level(0.0)
	assert_eq(MusicManager.get_current_music_tier(), 0, "and doom drives again afterwards")

func test_override_releases_itself_at_the_run_boundary():
	# The stated safety property: an override cannot silently ride into a scored run.
	# Every start-run / return-to-menu / game-over transition calls play_context().
	MusicManager.set_tier_override(3)
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	assert_false(MusicManager.is_tier_overridden(),
		"entering a run must hand the tier back to doom")
	_silence_music()

func test_audition_is_not_an_alpha_tool():
	# Auditioning writes nothing toward game state or scoring, so it must NOT set the
	# sticky unranked flag the mutating pokes set (decision card 2026-08-01).
	GameConfig.reset_alpha_tools_flag()
	MusicManager.set_tier_override(4)
	MusicManager.clear_tier_override()
	assert_false(GameConfig.alpha_tools_used,
		"playing a different track is not a state mutation and must not unrank the run")
	assert_true(GameConfig.is_ranked_run(), "run stays ranked after an audition")

func test_catalogue_lists_every_tier_once_and_dedupes_shared_beds():
	var cat := MusicManager.audition_catalogue()
	var tiers: Array = []
	var paths: Array = []
	for entry in cat:
		assert_true(entry.has("label") and entry.has("kind") and entry.has("path"),
			"catalogue entries carry label/kind/path")
		if str(entry["kind"]) == "tier":
			tiers.append(int(entry["tier"]))
		assert_false(paths.has(str(entry["path"])),
			"no bed listed twice (checkpoint_saved.ogg is both MENU and tier 0)")
		paths.append(str(entry["path"]))
	assert_eq(tiers.size(), MusicManager.MUSIC_TIER_NAMES.size(),
		"every music tier is auditionable")
	assert_gt(cat.size(), MusicManager.MUSIC_TIER_NAMES.size(),
		"the standalone victory/defeat beds are auditionable too")

func test_status_line_says_what_is_playing_and_why():
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	assert_string_contains(MusicManager.audition_status_line(), "AUTO",
		"unoverridden playback reports as automatic")
	MusicManager.set_tier_override(4)
	var line := MusicManager.audition_status_line()
	assert_string_contains(line, "OVERRIDE", "an override says so")
	assert_string_contains(line, "terminal", "and names the tier being heard")
	assert_string_contains(line, "cosy", "and names the tier doom would have chosen")
	_silence_music()

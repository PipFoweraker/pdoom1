extends Node
## Music Manager - Background music playback with crossfade support
##
## GAMEPLAY is doom-band ADAPTIVE (docs/audio/MUSIC_DESIGN.md): an
## AudioStreamInteractive whose clips are the five music tiers of the
## doom-intensity spec, switched by a READ-ONLY doom value arriving via
## GameManager.game_state_updated. Audio is a pure view-layer side-effect
## (ADR-0006): this node never writes game state, never touches the seeded
## RNG or the turn loop, and degrades to the legacy playlist (or silence)
## when audio assets are missing.

enum MusicContext {
	MENU,      # Welcome screen, settings, etc.
	GAMEPLAY,  # Active game session
	VICTORY,   # Win screen
	DEFEAT     # Loss screen
}

const CROSSFADE_DURATION = 2.0
const MUSIC_BUS_INDEX = 2  # Music bus in default_bus_layout.tres

## ---- Adaptive doom-band music (docs/audio/MUSIC_DESIGN.md) ----
## The canonical 7 doom status bands (ThemeManager.DOOM_STATUS_BANDS,
## NOMINAL..TERMINAL) collapse onto 5 MUSIC TIERS, named after the 5
## doom-intensity bands in docs/art/PALETTE_AND_DOOM_INTENSITY.md.
const MUSIC_TIER_NAMES := ["cosy", "uneasy", "spooky", "eldritch", "terminal"]
## Band index (0..6) -> music tier (0..4):
## NOMINAL->cosy, ELEVATED/HIGH->uneasy, SEVERE/EXTREME->spooky,
## CATASTROPHIC->eldritch, TERMINAL->terminal.
const MUSIC_TIER_BY_BAND := [0, 1, 1, 2, 2, 3, 4]

## Composed tier beds (Fable tier-set v0.3, tools/music/jukebox.html --
## Pip-judged over two listening rounds; GM-placeholder timbres, real
## composition). Each is a whole-track bed cut to an exact bar-boundary
## loop at ~-16 LUFS; when per-layer stems are recorded (COMMISSION_LIST),
## each tier grows to a multi-stem AudioStreamSynchronized group
## (BASE / PULSE / WEIRD / FIRE) and nothing else has to change.
## M0-M2 share C @ 104 (one room souring); M3-M4 are D dorian @ 96.
const MUSIC_TIER_STEMS := [
	[{"path": "res://assets/audio/music/unit_tests_passing.ogg", "volume_db": 0.0}],
	[{"path": "res://assets/audio/music/distribution_shift.ogg", "volume_db": 0.0}],
	[{"path": "res://assets/audio/music/proxy_gaming.ogg", "volume_db": 0.0}],
	[{"path": "res://assets/audio/music/mesa_optimizer.ogg", "volume_db": 0.0}],
	[{"path": "res://assets/audio/music/treacherous_turn.ogg", "volume_db": 0.0}],
]

## The placeholder tracks carry no BPM metadata, so clips are stamped with a
## nominal BPM to give AudioStreamInteractive a time base for beat-measured
## crossfades: 8 beats at 120 BPM = a 4 s tier crossfade.
const ADAPTIVE_BPM := 120.0
const ADAPTIVE_FADE_BEATS := 8.0

var adaptive_enabled: bool = true
var _adaptive_stream: AudioStreamInteractive = null
var _adaptive_build_attempted: bool = false
var _adaptive_active: bool = false
var _current_music_tier: int = 0

# Music tracks organized by context
var music_library = {
	MusicContext.MENU: [
		# "Checkpoint saved" -- the respite cue (round-2 commission).
		# Composed-audio only now; the last placeholder (PDOOMN ST1) and the
		# 0.7 s beeyoowee UI blip are both out of the music rotation.
		"res://assets/audio/music/checkpoint_saved.ogg"
	],
	MusicContext.GAMEPLAY: [
		# Legacy-playlist fallback (used only if the adaptive build fails):
		# same composed beds, in tier order.
		"res://assets/audio/music/unit_tests_passing.ogg",
		"res://assets/audio/music/distribution_shift.ogg",
		"res://assets/audio/music/proxy_gaming.ogg",
		"res://assets/audio/music/mesa_optimizer.ogg",
		"res://assets/audio/music/treacherous_turn.ogg"
	],
	MusicContext.VICTORY: [
		# "The off switch worked (quiet dawn)" -- victory confirmed round 2.
		"res://assets/audio/music/the_off_switch_worked.ogg"
	],
	MusicContext.DEFEAT: [
		# The papers-please trudge (Pip: "I love the dirge").
		"res://assets/audio/music/out_of_distribution_trudge.ogg"
	]
}

# Audio players for crossfading
var player_a: AudioStreamPlayer
var player_b: AudioStreamPlayer
var active_player: AudioStreamPlayer
var inactive_player: AudioStreamPlayer

# Current state
var current_context: MusicContext = MusicContext.MENU
var current_track_index: int = 0
var is_crossfading: bool = false
var music_enabled: bool = true

# The in-flight crossfade tween, tracked so it can be killed on stop/shutdown. Left
# untracked, a tween still running at quit leaks (ObjectDB warning at exit).
var _crossfade_tween: Tween = null

func _ready():
	print("[MusicManager] Initializing music system...")

	# Create two audio stream players for crossfading
	player_a = AudioStreamPlayer.new()
	player_a.bus = "Music"
	player_a.name = "MusicPlayerA"
	add_child(player_a)

	player_b = AudioStreamPlayer.new()
	player_b.bus = "Music"
	player_b.name = "MusicPlayerB"
	add_child(player_b)

	# Start with player_a as active
	active_player = player_a
	inactive_player = player_b

	# Connect finished signals for continuous playback
	player_a.finished.connect(_on_track_finished)
	player_b.finished.connect(_on_track_finished)

	# Apply volume from GameConfig
	_apply_volume()

	# GameManager is declared after MusicManager in the autoload list, so the
	# doom-signal hookup is deferred until the tree is fully assembled.
	call_deferred("_connect_doom_signal")

	print("[MusicManager] Music system ready")

## Subscribe (read-only) to game-state broadcasts to track the doom band.
## Listening to a signal never writes game state -- ADR-0006 safe.
func _connect_doom_signal():
	var game_manager = get_node_or_null("/root/GameManager")
	if game_manager == null or not game_manager.has_signal("game_state_updated"):
		print("[MusicManager] GameManager not available; adaptive music will idle at tier 0")
		return
	if not game_manager.game_state_updated.is_connected(_on_game_state_for_music):
		game_manager.game_state_updated.connect(_on_game_state_for_music)
		print("[MusicManager] Doom-band signal connected (read-only)")

func _on_game_state_for_music(state: Dictionary):
	set_doom_level(float(state.get("doom", 0.0)))

## Apply music volume from GameConfig
func _apply_volume():
	# Get GameConfig autoload
	var game_config = get_node_or_null("/root/GameConfig")
	if not game_config:
		print("[MusicManager] GameConfig not ready, using default volume")
		return

	var volume_percent = game_config.music_volume
	var volume_db = linear_to_db(volume_percent / 100.0)
	AudioServer.set_bus_volume_db(MUSIC_BUS_INDEX, volume_db)
	print("[MusicManager] Volume set to %d%% (%.1f dB)" % [volume_percent, volume_db])

## Set music volume (0-100)
func set_volume(volume_percent: int):
	var volume_db = linear_to_db(volume_percent / 100.0)
	AudioServer.set_bus_volume_db(MUSIC_BUS_INDEX, volume_db)
	print("[MusicManager] Volume changed to %d%% (%.1f dB)" % [volume_percent, volume_db])

## Play music for a specific context
func play_context(context: MusicContext, shuffle: bool = true):
	print("[MusicManager] Switching to context: ", MusicContext.keys()[context])

	current_context = context

	# GAMEPLAY prefers the doom-adaptive stream; anything else (or a failed
	# adaptive build) falls back to the legacy per-context playlist.
	if context == MusicContext.GAMEPLAY and adaptive_enabled:
		if _play_adaptive():
			return
	_adaptive_active = false

	var tracks = music_library[context]

	if tracks.is_empty():
		print("[MusicManager] No tracks available for context: ", MusicContext.keys()[context])
		stop_music()
		return

	# Select track (shuffle or sequential)
	if shuffle:
		current_track_index = randi() % tracks.size()
	else:
		current_track_index = 0

	play_track(tracks[current_track_index])

## Play a specific track with crossfade
func play_track(track_path: String):
	if not music_enabled:
		print("[MusicManager] Music disabled, skipping playback")
		return

	# Check if track exists
	if not ResourceLoader.exists(track_path):
		print("[MusicManager] ERROR: Track not found: ", track_path)
		return

	# Load the audio stream
	var stream = load(track_path)
	if not stream:
		print("[MusicManager] ERROR: Failed to load track: ", track_path)
		return

	print("[MusicManager] Loading track: ", track_path.get_file())
	_adaptive_active = false
	_play_stream(stream)

## Start (or crossfade to) an already-loaded stream. Shared by the legacy
## playlist path and the adaptive gameplay stream.
func _play_stream(stream: AudioStream):
	# If nothing is playing, start immediately
	if not active_player.playing:
		active_player.stream = stream
		active_player.volume_db = 0
		active_player.play()
		print("[MusicManager] Started playing: ", _stream_display_name(stream))
	else:
		# Crossfade to new track
		_crossfade_to_track(stream)

func _stream_display_name(stream: AudioStream) -> String:
	if stream == null:
		return "None"
	if stream is AudioStreamInteractive:
		return "adaptive doom stream"
	if stream.resource_path != "":
		return stream.resource_path.get_file()
	return "unnamed stream"

## Crossfade from active player to inactive player with new track
func _crossfade_to_track(new_stream: AudioStream):
	if is_crossfading:
		print("[MusicManager] Already crossfading, ignoring request")
		return

	is_crossfading = true
	print("[MusicManager] Crossfading to new track...")

	# Set up inactive player with new stream
	inactive_player.stream = new_stream
	inactive_player.volume_db = -80  # Start silent
	inactive_player.play()

	# Crossfade animation
	var tween = create_tween()
	_crossfade_tween = tween
	tween.set_parallel(true)
	tween.tween_property(active_player, "volume_db", -80, CROSSFADE_DURATION)
	tween.tween_property(inactive_player, "volume_db", 0, CROSSFADE_DURATION)

	await tween.finished
	_crossfade_tween = null

	# Stop old player and swap
	active_player.stop()
	var temp = active_player
	active_player = inactive_player
	inactive_player = temp

	is_crossfading = false
	print("[MusicManager] Crossfade complete")

## Called when a track finishes playing
func _on_track_finished():
	if is_crossfading:
		return  # Don't advance during crossfade

	# Adaptive clips loop internally; if the interactive stream somehow ends
	# (e.g. a stem that refused to loop), restart it rather than advancing
	# the legacy playlist.
	if _adaptive_active:
		if music_enabled and active_player.stream == _adaptive_stream:
			active_player.play()
		return

	# Get current context tracks
	var tracks = music_library[current_context]
	if tracks.is_empty():
		return

	# Advance to next track (loop within context)
	current_track_index = (current_track_index + 1) % tracks.size()
	play_track(tracks[current_track_index])

## Stop all music
func stop_music():
	print("[MusicManager] Stopping music")

	if is_crossfading:
		# Kill the actual in-flight crossfade tween. The old code created a fresh tween and
		# killed that instead -- a no-op that left the real crossfade running.
		if _crossfade_tween != null and _crossfade_tween.is_valid():
			_crossfade_tween.kill()
		_crossfade_tween = null
		is_crossfading = false

	var tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(player_a, "volume_db", -80, 1.0)
	tween.tween_property(player_b, "volume_db", -80, 1.0)

	await tween.finished

	player_a.stop()
	player_b.stop()

## Pause music
func pause_music():
	active_player.stream_paused = true
	if inactive_player.playing:
		inactive_player.stream_paused = true

## Resume music
func resume_music():
	active_player.stream_paused = false
	if inactive_player.playing:
		inactive_player.stream_paused = false

## Enable/disable music
func set_music_enabled(enabled: bool):
	music_enabled = enabled
	if not enabled:
		stop_music()
	else:
		# Resume current context
		play_context(current_context)

## Get current track name
func get_current_track_name() -> String:
	if active_player.stream:
		return active_player.stream.resource_path.get_file().get_basename()
	return "None"

## Shutdown cleanup. Autoloads are freed during SceneTree teardown at quit; without this
## the running crossfade Tween plus the playing AudioStreamPlayback/AudioStream objects are
## still live when the engine's leak check runs, producing the "ObjectDB instances leaked"
## warning and "resources still in use at exit" error. Killing the tween and clearing both
## players' streams releases those references before the check.
func _exit_tree() -> void:
	if _crossfade_tween != null and _crossfade_tween.is_valid():
		_crossfade_tween.kill()
	_crossfade_tween = null
	if is_instance_valid(player_a):
		player_a.stop()
		player_a.stream = null
	if is_instance_valid(player_b):
		player_b.stop()
		player_b.stream = null
	_adaptive_active = false
	_adaptive_stream = null

## ---- Adaptive doom-band music ----

## Map a doom percentage (0-100) to a music tier (0-4) via the canonical
## band API. Pure read; safe to call from anywhere.
func music_tier_for_doom(doom_percent: float) -> int:
	var band: int = 0
	var theme_manager = get_node_or_null("/root/ThemeManager")
	if theme_manager != null:
		band = theme_manager.get_doom_band_index(doom_percent)
	band = clampi(band, 0, MUSIC_TIER_BY_BAND.size() - 1)
	return MUSIC_TIER_BY_BAND[band]

## READ-ONLY doom input. The single entry point for game -> music flow:
## stores the tier and, if the adaptive stream is live, switches clips.
## Never writes anything back toward game state.
func set_doom_level(doom_percent: float):
	var tier: int = music_tier_for_doom(doom_percent)
	if tier == _current_music_tier:
		return
	print("[MusicManager] Doom %.1f%% -> music tier %d (%s)" % [
		doom_percent, tier, MUSIC_TIER_NAMES[tier]])
	_current_music_tier = tier
	_switch_adaptive_tier(tier)

## Debug hook: force a music tier directly (dev overlay / manual testing).
func debug_force_tier(tier: int):
	tier = clampi(tier, 0, MUSIC_TIER_NAMES.size() - 1)
	_current_music_tier = tier
	_switch_adaptive_tier(tier)

## Start the adaptive gameplay stream. Returns false if it cannot be built
## (missing module or missing audio) so the caller can fall back.
func _play_adaptive() -> bool:
	if not music_enabled:
		print("[MusicManager] Music disabled, skipping adaptive playback")
		return true  # Handled: stay silent, do not fall through to playlist
	if _adaptive_stream == null and not _adaptive_build_attempted:
		_adaptive_build_attempted = true
		_adaptive_stream = _build_adaptive_stream()
	if _adaptive_stream == null:
		return false
	if _adaptive_active and active_player.stream == _adaptive_stream and active_player.playing:
		# Already live (e.g. restart-game re-entry): just re-sync the tier.
		_switch_adaptive_tier(_current_music_tier)
		return true
	_adaptive_active = true
	_adaptive_stream.initial_clip = clampi(_current_music_tier, 0, _adaptive_stream.clip_count - 1)
	print("[MusicManager] Starting adaptive gameplay stream at tier %d (%s)" % [
		_current_music_tier, MUSIC_TIER_NAMES[_current_music_tier]])
	_play_stream(_adaptive_stream)
	return true

## Switch the live interactive playback to the clip for `tier`. No-op when
## the adaptive stream is not currently audible (menu, defeat, disabled).
func _switch_adaptive_tier(tier: int):
	if not _adaptive_active or _adaptive_stream == null:
		return
	var playback := _adaptive_playback()
	if playback == null:
		return
	var clip: int = clampi(tier, 0, _adaptive_stream.clip_count - 1)
	if playback.get_current_clip_index() == clip:
		return
	playback.switch_to_clip(clip)

## Find the live interactive playback, on whichever player carries the
## adaptive stream (it may sit on either side of a crossfade).
func _adaptive_playback() -> AudioStreamPlaybackInteractive:
	for player in [player_a, player_b]:
		if player != null and player.playing and player.stream == _adaptive_stream:
			var playback = player.get_stream_playback()
			if playback is AudioStreamPlaybackInteractive:
				return playback
	return null

## Build the AudioStreamInteractive: one clip per music tier, each clip a
## looped stem (or an AudioStreamSynchronized stem group), plus a single
## any-to-any crossfade transition rule. Missing stems degrade: a tier with
## no loadable stems inherits its neighbour's stream; if NOTHING loads the
## whole build returns null and the legacy playlist takes over.
func _build_adaptive_stream() -> AudioStreamInteractive:
	var tier_streams: Array = []
	var loaded_any := false
	for tier in range(MUSIC_TIER_STEMS.size()):
		var stems: Array = []
		var volumes: Array = []
		for stem in MUSIC_TIER_STEMS[tier]:
			var path: String = stem["path"]
			if not ResourceLoader.exists(path):
				print("[MusicManager] Adaptive stem missing, skipping: ", path)
				continue
			var stream = load(path)
			if stream == null:
				print("[MusicManager] Adaptive stem failed to load, skipping: ", path)
				continue
			stems.append(_prepare_stem(stream))
			volumes.append(stem.get("volume_db", 0.0))
		if stems.is_empty():
			tier_streams.append(null)  # Filled from a neighbour below
			continue
		loaded_any = true
		if stems.size() == 1:
			tier_streams.append(stems[0])
		else:
			var synced := AudioStreamSynchronized.new()
			synced.stream_count = stems.size()
			for i in range(stems.size()):
				synced.set_sync_stream(i, stems[i])
				synced.set_sync_stream_volume(i, volumes[i])
			tier_streams.append(synced)
	if not loaded_any:
		print("[MusicManager] No adaptive stems available; falling back to playlist")
		return null

	# Fill gaps: forward from lower tiers, then backward for leading gaps.
	for tier in range(tier_streams.size()):
		if tier_streams[tier] == null and tier > 0:
			tier_streams[tier] = tier_streams[tier - 1]
	for tier in range(tier_streams.size() - 1, -1, -1):
		if tier_streams[tier] == null and tier < tier_streams.size() - 1:
			tier_streams[tier] = tier_streams[tier + 1]

	var interactive := AudioStreamInteractive.new()
	interactive.clip_count = tier_streams.size()
	for tier in range(tier_streams.size()):
		interactive.set_clip_name(tier, StringName(MUSIC_TIER_NAMES[tier]))
		interactive.set_clip_stream(tier, tier_streams[tier])
		interactive.set_clip_auto_advance(tier, AudioStreamInteractive.AUTO_ADVANCE_DISABLED)
	interactive.initial_clip = 0
	interactive.add_transition(
		AudioStreamInteractive.CLIP_ANY, AudioStreamInteractive.CLIP_ANY,
		AudioStreamInteractive.TRANSITION_FROM_TIME_IMMEDIATE,
		AudioStreamInteractive.TRANSITION_TO_TIME_START,
		AudioStreamInteractive.FADE_CROSS, ADAPTIVE_FADE_BEATS)
	print("[MusicManager] Adaptive stream built: %d tiers" % tier_streams.size())
	return interactive

## Duplicate a loaded stream (so loop/BPM tweaks never leak into the shared
## resource cache the legacy playlist also uses), force it to loop, and stamp
## the nominal BPM used for beat-measured crossfades.
func _prepare_stem(stream: AudioStream) -> AudioStream:
	var stem: AudioStream = stream.duplicate()
	if stem is AudioStreamMP3 or stem is AudioStreamOggVorbis:
		stem.loop = true
		stem.bpm = ADAPTIVE_BPM
	else:
		# WAV stems should be authored/imported with loop points; a stem that
		# does not loop just goes quiet at clip end (finished-signal restarts).
		print("[MusicManager] Adaptive stem is not mp3/ogg; relying on import loop settings: ",
			stream.resource_path)
	return stem

## Debug: Print music library
func print_library():
	print("[MusicManager] === Music Library ===")
	for context in music_library:
		print("  ", MusicContext.keys()[context], ":")
		for track in music_library[context]:
			print("    - ", track.get_file())
	print("====================================")

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
## TIER 0 IS THE TRACK A PLAYER (and Pip, on loop, for hours) HEARS MOST.
## It was unit_tests_passing.ogg ("M0 cosy"); Pip 2026-08-01 11:06/11:30:
## "that creeping one needs a bit of work ... the current theme is a little bit
## intense, and I think the slower gentler one actually might just be more chill
## -- especially when it's majority me listening to it". checkpoint_saved.ogg is
## the first of the three swaps he named ("whatever that song was in the settings
## menu") and the only candidate with a recorded positive verdict from him
## (tools/music/jukebox_notes2.json, "menu": "Transitioning to something like
## this is exceptional ... the attention-demands are diminished"). It is already
## wired, imported and shipping as tier 0, so this costs no new asset.
##
## SUPERSEDED IN PART, 2026-08-21. This block used to end: "CONSEQUENCE,
## deliberate: menu and calm-gameplay now share a bed, so launching a run no
## longer changes the music." That is no longer true and the sentence is
## replaced rather than deleted, because the 08-01 reasoning above still governs
## TIER 0 and only the MENU half was reversed.
## Pip, 2026-08-21: "let's make Out of Distribution the default track at main
## menu and main menus, so people will notice it switching to the game tune when
## they start" / "it's the one i like the most". The inaudible-launch property
## was the cost of sharing a bed; he now wants the launch audible, so MENU moved
## to out_of_distribution_trudge.ogg (see music_library) and tier 0 stayed put.
## The run's musical arc is unchanged -- doom still escalates through M1..M4 --
## and the calm floor is still checkpoint_saved.ogg.
## unit_tests_passing.ogg stays in the repo for the rework; restoring it is this
## one line.
const MUSIC_TIER_STEMS := [
	[{"path": "res://assets/audio/music/checkpoint_saved.ogg", "volume_db": 0.0}],
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

## Human titles for the beds, keyed by resource path. The dev overlay is happy with
## "M3 eldritch (mesa_optimizer)"; a player is not. These are the names the tracks were
## COMPOSED under (tools/music/jukebox.html track list), so the credits, the jukebox and
## the in-game picker all say the same words. Anything missing falls back to a
## prettified filename rather than going blank.
const TRACK_TITLES := {
	"res://assets/audio/music/checkpoint_saved.ogg": "Checkpoint saved",
	"res://assets/audio/music/distribution_shift.ogg": "Distribution shift",
	"res://assets/audio/music/proxy_gaming.ogg": "Proxy gaming",
	"res://assets/audio/music/mesa_optimizer.ogg": "Mesa optimizer",
	"res://assets/audio/music/treacherous_turn.ogg": "Treacherous turn",
	"res://assets/audio/music/the_off_switch_worked.ogg": "The off switch worked",
	"res://assets/audio/music/out_of_distribution_trudge.ogg": "Out of distribution",
	"res://assets/audio/music/unit_tests_passing.ogg": "Unit tests passing",
}

## Plain-language name for each music tier, for the player-facing picker and status line.
## MUSIC_TIER_NAMES are the internal spec words (cosy..terminal); these say what the tier
## MEANS to someone who has never read docs/audio/MUSIC_DESIGN.md.
const MUSIC_TIER_MOODS := ["Calm", "Uneasy", "Tense", "Dire", "Terminal"]

var adaptive_enabled: bool = true
var _adaptive_stream: AudioStreamInteractive = null
var _adaptive_build_attempted: bool = false
var _adaptive_active: bool = false
var _current_music_tier: int = 0

## ---- Audition override (ALPHA TOOLS music player, 2026-08-05) ----
## -1 == automatic (doom drives the tier). >= 0 == a human is holding the tier open so a
## track can be heard against the actual game state it plays under -- Pip's ask now that a
## musician is interested in the game.
##
## NOT an Alpha Tool, deliberately: this writes NOTHING toward game state, RNG or scoring
## (music is already a pure view-layer side-effect, ADR-0006), so it does not set the
## sticky unranked flag. Playing a different track is not "add $50k".
## RUN BOUNDARY: cleared by play_context(), which fires on every start-run /
## return-to-menu / game-over transition -- so an override can never silently ride into a
## scored run.
var _tier_override: int = -1
## The tier automatic selection WOULD be on right now. Kept up to date even while
## overridden, so the overlay can say "you are hearing 4, the game is at 1" and so
## releasing the override snaps back to the truth instead of to a stale value.
var _auto_music_tier: int = 0
## Path of a standalone bed a HUMAN chose (as opposed to one the game chose for a
## context, or the legacy playlist running because the adaptive build failed). Only
## used to word the status line honestly; nothing reads it for behaviour.
var _manual_pick_path: String = ""

## ---- "Nudging the conductor" (#1249, Pip 2026-08-21) ----------------------
## Pip: "I would probably like the game to tell me it's switching tracks if I
## select another one and it doesn't start within, like, half a second. Make it
## diegetic -- 'nudging the conductor....'"
##
## TWO causes produced one symptom, and only one of them was cosmetic:
##
##  1. CROSSFADE_DURATION is 2.0s and the incoming player starts at -80 dB, so a
##     pick is inaudible for roughly the first half-second BY DESIGN. Nothing is
##     broken; the player just cannot tell "working on it" from "my click did
##     nothing".
##  2. A pick made DURING an in-flight crossfade was DISCARDED, with a print()
##     as its only trace. Crossfades last 2s, so any second pick inside that
##     window was silently lost. That is the silent-wrongness failure this
##     codebase hunts everywhere else -- player_status_line() even carries a
##     comment about not blaming the player for a state they did not cause.
##
## Fixing only (1) would be worse than nothing: the nudge line would appear and
## then resolve to the WRONG track. So the queue below fixes (2) as well.
const CONDUCTOR_NUDGE_DELAY := 0.5
## True once a pick has been waiting longer than CONDUCTOR_NUDGE_DELAY without
## becoming audible. A FLAG, not a clock: player_status_line() stays a pure map
## from state to string, and a test can set this directly.
var _conductor_nudging: bool = false
## Set the moment a pick is requested, cleared when it lands. Distinct from
## _conductor_nudging, which only turns on after the delay -- a switch that
## completes in 300ms should say nothing at all.
var _switch_pending: bool = false
## A stream requested while a crossfade was already running. Applied when that
## crossfade finishes rather than dropped. Only the LAST one is kept: a player
## clicking four tracks in two seconds wants the fourth, not a queue of four.
var _queued_stream: AudioStream = null

# Music tracks organized by context
var music_library = {
	MusicContext.MENU: [
		# "Out of distribution" -- the papers-please trudge. Pip 2026-08-21:
		# "let's make Out of Distribution the default track at main menu and
		# main menus, so people will notice it switching to the game tune when
		# they start" / "it's the one i like the most".
		# This DELIBERATELY re-separates menu from gameplay: see the CONSEQUENCE
		# note above MUSIC_TIER_STEMS. Starting a run is audible again.
		# It is also the DEFEAT bed, so menu and game-over now share a track --
		# accepted, because there is no spare composed bed to move DEFEAT to.
		"res://assets/audio/music/out_of_distribution_trudge.ogg"
	],
	MusicContext.GAMEPLAY: [
		# Legacy-playlist fallback (used only if the adaptive build fails):
		# same composed beds, in tier order -- kept in lockstep with
		# MUSIC_TIER_STEMS so a fallback run starts as calm as the real one.
		"res://assets/audio/music/checkpoint_saved.ogg",
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

	# Keep processing while the tree is paused. The pause menu sets
	# get_tree().paused = true, and a Tween created by create_tween() is bound to the
	# node that made it -- so with the default (inherited, PAUSABLE) process mode a
	# crossfade started from the pause menu's music picker would freeze half-done:
	# both players audible, `is_crossfading` stuck true, and every later switch
	# ignored ("Already crossfading"). Music is a view-layer side-effect (ADR-0006)
	# with no game state to freeze, so ALWAYS is also the honest process mode for it.
	process_mode = Node.PROCESS_MODE_ALWAYS

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

	# Run boundary for the audition override: every caller of play_context() is a
	# start-run / return-to-menu / game-over transition, so this is exactly where a
	# hand-held tier must be let go of. Cleared silently (no re-switch) because the
	# context change is about to choose a stream anyway.
	_tier_override = -1
	_manual_pick_path = ""

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
	_begin_switch()
	_play_stream(stream)


## #1249: mark a requested switch, and raise the diegetic nudge if it has not
## become audible within CONDUCTOR_NUDGE_DELAY.
##
## A one-shot timer sets a FLAG rather than player_status_line() reading a clock.
## That function is documented as a "pure string build, unit-tested", and it stays
## that way: a test sets _conductor_nudging directly and asserts the wording,
## without waiting half a second or stubbing time.
func _begin_switch() -> void:
	_switch_pending = true
	_conductor_nudging = false
	var tree := get_tree()
	if tree == null:
		return  # headless/teardown: no timer to hang the nudge on, and nothing to show it
	await tree.create_timer(CONDUCTOR_NUDGE_DELAY).timeout
	# Still waiting after the delay -> say so. If the switch already landed,
	# _switch_pending is false and the player never sees a flicker for a fast one.
	if _switch_pending:
		_conductor_nudging = true

## Start (or crossfade to) an already-loaded stream. Shared by the legacy
## playlist path and the adaptive gameplay stream.
func _play_stream(stream: AudioStream):
	# If nothing is playing, start immediately
	if not active_player.playing:
		active_player.stream = stream
		active_player.volume_db = 0
		active_player.play()
		# Audible immediately -- nothing to nudge the conductor about (#1249).
		_switch_pending = false
		_conductor_nudging = false
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
		# #1249: QUEUE, do not drop. This used to return here with only a print()
		# to show for it, so any pick made inside the 2s crossfade window vanished
		# and the player was left believing they had not clicked. Keeping only the
		# newest request is deliberate -- four clicks in two seconds means "play
		# the fourth", not "play all four in order".
		_queued_stream = new_stream
		print("[MusicManager] Crossfade in flight; queued %s" % _stream_display_name(new_stream))
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

	# #1249: a pick made mid-crossfade waited here rather than being dropped.
	# Apply it now. The pending/nudge flags stay set across this hop, because from
	# the player's point of view their pick still has not been honoured.
	if _queued_stream != null:
		var queued := _queued_stream
		_queued_stream = null
		_crossfade_to_track(queued)
		return

	_switch_pending = false
	_conductor_nudging = false

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
	_auto_music_tier = tier
	if _tier_override >= 0:
		return  # a human is holding the tier; remember where automatic would be
	if tier == _current_music_tier:
		return
	print("[MusicManager] Doom %.1f%% -> music tier %d (%s)" % [
		doom_percent, tier, MUSIC_TIER_NAMES[tier]])
	_current_music_tier = tier
	_switch_adaptive_tier(tier)


## ---- Audition API (ALPHA TOOLS music player) ----

## Hold `tier` open regardless of doom, so it can be heard against the live game state.
func set_tier_override(tier: int) -> void:
	_tier_override = clampi(tier, 0, MUSIC_TIER_NAMES.size() - 1)
	_current_music_tier = _tier_override
	print("[MusicManager] Tier OVERRIDE -> %d (%s); automatic would be %d (%s)" % [
		_tier_override, MUSIC_TIER_NAMES[_tier_override],
		_auto_music_tier, MUSIC_TIER_NAMES[_auto_music_tier]])
	_switch_adaptive_tier(_tier_override)


## Give the tier back to doom. Snaps straight to wherever automatic is NOW, so releasing
## never leaves the player hearing a tier the game left behind ten turns ago.
func clear_tier_override() -> void:
	if _tier_override < 0:
		return
	_tier_override = -1
	print("[MusicManager] Tier override released -> automatic tier %d (%s)" % [
		_auto_music_tier, MUSIC_TIER_NAMES[_auto_music_tier]])
	if _auto_music_tier != _current_music_tier:
		_current_music_tier = _auto_music_tier
		_switch_adaptive_tier(_auto_music_tier)


func is_tier_overridden() -> bool:
	return _tier_override >= 0


## True while the doom-adaptive interactive stream is the thing being heard (as opposed
## to a standalone bed, e.g. after auditioning the victory track).
func is_adaptive_active() -> bool:
	return _adaptive_active


func get_current_music_tier() -> int:
	return _current_music_tier


func get_auto_music_tier() -> int:
	return _auto_music_tier


## Legacy debug hook, kept for callers/tests: same thing as set_tier_override().
func debug_force_tier(tier: int):
	set_tier_override(tier)


## Flat catalogue of every bed the game can play, for the overlay's one dropdown.
## Entries: {"label": String, "kind": "tier"|"track", "tier": int, "path": String}.
## Tiers come first (they are the adaptive score); the standalone context beds follow,
## deduplicated -- a bed used by two contexts would otherwise read as two different
## tracks. Since 2026-08-21 the duplicate pair is MENU and DEFEAT (both
## out_of_distribution_trudge.ogg); before that it was MENU and tier 0. The dedup is
## generic, so which pair collides does not matter to this function.
func audition_catalogue() -> Array:
	var out: Array = []
	var seen: Dictionary = {}
	for tier in range(MUSIC_TIER_NAMES.size()):
		var path := ""
		if tier < MUSIC_TIER_STEMS.size() and not MUSIC_TIER_STEMS[tier].is_empty():
			path = String(MUSIC_TIER_STEMS[tier][0]["path"])
			seen[path] = true
		out.append({
			"label": "M%d %s  (%s)" % [tier, MUSIC_TIER_NAMES[tier], path.get_file().get_basename()],
			"title": track_title(path),
			"kind": "tier", "tier": tier, "path": path,
		})
	for context in [MusicContext.MENU, MusicContext.VICTORY, MusicContext.DEFEAT]:
		for track in music_library[context]:
			var p := String(track)
			if seen.has(p):
				continue
			seen[p] = true
			out.append({
				"label": "%s  (%s)" % [MusicContext.keys()[context], p.get_file().get_basename()],
				"title": track_title(p),
				"kind": "track", "tier": -1, "path": p,
			})
	return out


## Human title for a bed. Unknown paths degrade to a prettified filename rather than an
## empty string, so a newly added track is ugly in the picker but never invisible.
func track_title(path: String) -> String:
	if path == "":
		return "Unknown track"
	if TRACK_TITLES.has(path):
		return String(TRACK_TITLES[path])
	return path.get_file().get_basename().replace("_", " ").capitalize()


## ---- PLAYER-FACING music picker (pause menu, 2026-08-06) ----------------------------
##
## Same machinery as the dev audition tool, different words. Pip's ruling that promoted
## it: "if people want to listen to their favourite tracks, they can do so and if they
## miss out on doom indicators etc, so be it, that's their choice." That is only safe
## because a pick writes NOTHING toward GameState, the seeded RNG or scoring -- see the
## _tier_override comment above and test_music_player_controls.gd, which snapshots the
## whole state dict across a full picker session and asserts it is byte-identical.

## The picker's list: "Automatic" first (the default and the designed experience),
## then every bed by human title. Entries carry the same kind/tier/path contract as
## audition_catalogue(), plus kind "auto".
func player_catalogue() -> Array:
	var out: Array = [{
		"label": "Automatic -- follows the situation",
		"title": "Automatic", "kind": "auto", "tier": -1, "path": "",
	}]
	for entry in audition_catalogue():
		var e: Dictionary = entry.duplicate()
		if String(e.get("kind", "")) == "tier":
			var tier: int = int(e.get("tier", 0))
			e["label"] = "%s -- %s" % [
				String(e.get("title", "")), MUSIC_TIER_MOODS[clampi(tier, 0, MUSIC_TIER_MOODS.size() - 1)]]
		else:
			e["label"] = String(e.get("title", ""))
		out.append(e)
	return out


## Apply a catalogue entry. ONE code path for the pause menu and the dev overlay, so
## "what a pick does" cannot drift between the two surfaces. Returns nothing and
## touches nothing outside this node.
func apply_catalogue_entry(entry: Dictionary) -> void:
	if entry.is_empty():
		return
	match String(entry.get("kind", "")):
		"auto":
			return_to_automatic()
		"tier":
			_manual_pick_path = ""
			set_tier_override(int(entry.get("tier", 0)))
		_:
			_manual_pick_path = String(entry.get("path", ""))
			play_track(_manual_pick_path)


## Hand the music back to the game. Releases a held tier AND, if a standalone bed
## replaced the adaptive stream entirely, restarts the current context so the
## doom-following score comes back rather than the player being left on a dead bed.
func return_to_automatic() -> void:
	clear_tier_override()
	if not is_adaptive_active():
		play_context(current_context)


## Index into player_catalogue() of the entry currently being heard, so the picker can
## open showing the truth instead of resetting to item 0. -1 means "not in the list".
func player_catalogue_index() -> int:
	var cat := player_catalogue()
	if not is_tier_overridden() and _adaptive_active:
		return 0  # Automatic
	if is_tier_overridden():
		for i in range(cat.size()):
			if String(cat[i].get("kind", "")) == "tier" and int(cat[i].get("tier", -1)) == _current_music_tier:
				return i
		return 0
	# A standalone bed is playing (or nothing is): match on what the player is hearing.
	var playing_path := ""
	if active_player != null and active_player.stream != null:
		playing_path = active_player.stream.resource_path
	for i in range(cat.size()):
		if String(cat[i].get("path", "")) == playing_path and playing_path != "":
			return i
	return 0


## The player-facing counterpart of audition_status_line(). Plainer words, and it answers
## the question the dev line answers in jargon: what am I hearing, and what does the game
## want to play instead? Pure string build, unit-tested.
func player_status_line() -> String:
	# #1249. Takes precedence over everything below: while a switch is in flight the
	# honest answer to "what am I hearing" is "not yet what you asked for". Reporting
	# the OLD track as "now playing" during a crossfade is how the player concludes
	# their click did nothing.
	if _conductor_nudging:
		return "Nudging the conductor...."
	if not _adaptive_active:
		# Two very different situations look the same from here: the player picked a
		# standalone bed, or the adaptive stream could not be built (missing audio, and
		# the legacy playlist took over). Only the first is "your pick" -- blaming the
		# player for the second would be the silent-wrongness failure mode in words.
		if _manual_pick_path != "":
			return ("Now playing: %s -- your pick. The music that follows the situation "
				+ "is paused until you choose Automatic.") % get_current_track_name_pretty()
		return "Now playing: %s." % get_current_track_name_pretty()
	var tier := clampi(_current_music_tier, 0, MUSIC_TIER_MOODS.size() - 1)
	var auto := clampi(_auto_music_tier, 0, MUSIC_TIER_MOODS.size() - 1)
	var heard := "%s (%s)" % [track_title(_tier_path(tier)), MUSIC_TIER_MOODS[tier]]
	if _tier_override < 0:
		return "Now playing: %s -- following the situation." % heard
	if tier == auto:
		return "Now playing: %s -- your pick. It is what the game would play anyway." % heard
	return ("Now playing: %s -- your pick. The game would switch to %s (%s); it will not "
		+ "while your pick is held.") % [heard, track_title(_tier_path(auto)), MUSIC_TIER_MOODS[auto]]


func _tier_path(tier: int) -> String:
	if tier < 0 or tier >= MUSIC_TIER_STEMS.size() or MUSIC_TIER_STEMS[tier].is_empty():
		return ""
	return String(MUSIC_TIER_STEMS[tier][0]["path"])


## Title-cased current track, for player-facing text (get_current_track_name() returns
## the raw basename, which is fine for the dev line and wrong in front of a player).
func get_current_track_name_pretty() -> String:
	if active_player != null and active_player.stream != null:
		return track_title(active_player.stream.resource_path)
	return "Nothing"


## One line for the overlay: what is playing, and WHY. Pure string build, unit-tested.
func audition_status_line() -> String:
	if not _adaptive_active:
		return "Playing: %s  [standalone bed -- adaptive score is not running]" % get_current_track_name()
	var tier := clampi(_current_music_tier, 0, MUSIC_TIER_NAMES.size() - 1)
	var auto := clampi(_auto_music_tier, 0, MUSIC_TIER_NAMES.size() - 1)
	if _tier_override >= 0:
		return "Playing: M%d %s  [OVERRIDE -- doom says M%d %s]" % [
			tier, MUSIC_TIER_NAMES[tier], auto, MUSIC_TIER_NAMES[auto]]
	return "Playing: M%d %s  [AUTO -- following doom]" % [tier, MUSIC_TIER_NAMES[tier]]

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

extends Node
## Music Manager - Background music playback with crossfade support

enum MusicContext {
	MENU,      # Welcome screen, settings, etc.
	GAMEPLAY,  # Active game session
	VICTORY,   # Win screen
	DEFEAT     # Loss screen
}

const CROSSFADE_DURATION = 2.0
const MUSIC_BUS_INDEX = 2  # Music bus in default_bus_layout.tres

# Music tracks organized by context
var music_library = {
	MusicContext.MENU: [
		"res://assets/audio/music/PDoom1 seleciton beeyoowee.wav",
		"res://assets/audio/music/PDOOMN ST1 (safe).mp3"
	],
	MusicContext.GAMEPLAY: [
		"res://assets/audio/music/PDoom1 Descent gradient.mp3",
		"res://assets/audio/music/PDoom1 Local maxima.mp3",
		"res://assets/audio/music/PDoom1 Power spike.mp3",
		"res://assets/audio/music/PDoom1 Undetected sandbagging.mp3"
	],
	MusicContext.VICTORY: [],  # Reserved for future victory music
	MusicContext.DEFEAT: [
		"res://assets/audio/music/PDoom Out_of_distribution.mp3"
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

	print("[MusicManager] Music system ready")

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

	# If nothing is playing, start immediately
	if not active_player.playing:
		active_player.stream = stream
		active_player.volume_db = 0
		active_player.play()
		print("[MusicManager] Started playing: ", track_path.get_file())
	else:
		# Crossfade to new track
		_crossfade_to_track(stream)

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
	tween.set_parallel(true)
	tween.tween_property(active_player, "volume_db", -80, CROSSFADE_DURATION)
	tween.tween_property(inactive_player, "volume_db", 0, CROSSFADE_DURATION)

	await tween.finished

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
		get_tree().create_tween().kill()
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

## Debug: Print music library
func print_library():
	print("[MusicManager] === Music Library ===")
	for context in music_library:
		print("  ", MusicContext.keys()[context], ":")
		for track in music_library[context]:
			print("    - ", track.get_file())
	print("====================================")

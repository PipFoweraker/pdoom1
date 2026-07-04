extends Node
# leaderboard.gd
# Local leaderboard system for P(Doom) - JSON-based storage
# Ported from pygame/src/scores/local_store.py

class_name Leaderboard

# Score entry data structure
class ScoreEntry:
	# ADR-0002: the score is the tuple (score, doom_integral) where `score` is
	# turns-survived (primary, dominant metric) and `doom_integral` is the
	# area-under-the-survival-curve tiebreak. `score` is named for back-compat with
	# the UI, which already treats it as turns.
	var score: int  # Turns survived (primary metric)
	var doom_integral: int  # Doom-integral tiebreak (ADR-0002)
	var player_name: String  # Lab name
	var date: String  # ISO timestamp
	var level_reached: int  # Final turn number (== score; kept for back-compat)
	var game_mode: String  # Game version, e.g. "v0.11.0"
	var duration_seconds: float  # Game duration
	var entry_uuid: String  # Unique identifier
	var baseline_score: int  # Baseline (no-action) turns survived for comparison (Issue #372)
	var baseline_doom_integral: int  # Baseline doom-integral tiebreak

	func _init(p_score: int, p_player_name: String, p_level: int, p_mode: String, p_duration: float, p_baseline: int = 0, p_doom_integral: int = 0, p_baseline_integral: int = 0):
		score = p_score
		doom_integral = p_doom_integral
		player_name = p_player_name
		date = Time.get_datetime_string_from_system()
		level_reached = p_level
		game_mode = p_mode
		duration_seconds = p_duration
		entry_uuid = generate_uuid()
		baseline_score = p_baseline
		baseline_doom_integral = p_baseline_integral

	func to_dict() -> Dictionary:
		return {
			"score": score,
			"doom_integral": doom_integral,
			"player_name": player_name,
			"date": date,
			"level_reached": level_reached,
			"game_mode": game_mode,
			"duration_seconds": duration_seconds,
			"entry_uuid": entry_uuid,
			"baseline_score": baseline_score,
			"baseline_doom_integral": baseline_doom_integral
		}

	static func from_dict(data: Dictionary) -> ScoreEntry:
		var entry = ScoreEntry.new(
			data.get("score", 0),
			data.get("player_name", "Unknown Lab"),
			data.get("level_reached", 0),
			data.get("game_mode", "Unknown"),
			data.get("duration_seconds", 0.0),
			data.get("baseline_score", 0),  # Issue #372
			data.get("doom_integral", 0),
			data.get("baseline_doom_integral", 0)
		)
		entry.date = data.get("date", "")
		entry.entry_uuid = data.get("entry_uuid", "")
		return entry

	func generate_uuid() -> String:
		# Simple UUID generation
		var uuid = ""
		for i in range(32):
			uuid += str(randi() % 16)
			if i == 7 or i == 11 or i == 15 or i == 19:
				uuid += "-"
		return uuid

# Main leaderboard class
var version: String = "1.0.0"
var max_entries: int = 50
var entries: Array[ScoreEntry] = []
var game_seed: String = ""  # Renamed from 'seed' to avoid shadowing built-in function
var game_version: String = ""  # ADR-0002 #5: boards are keyed by (seed, game_version)
var leaderboard_dir: String = "user://leaderboards"
var file_path: String = ""

func _init(p_seed: String = "default", p_version: String = ""):
	game_seed = p_seed
	game_version = p_version
	# ADR-0002 #5: version-scope the board so balance patches rotate the meta and old
	# scores never rank against the current game. Legacy callers (no version) keep the
	# old per-seed filename. Delimiter is '__' to survive hyphens/underscores in seeds.
	if game_version != "":
		file_path = "%s/leaderboard_%s__%s.json" % [leaderboard_dir, game_seed, game_version]
	else:
		file_path = "%s/leaderboard_%s.json" % [leaderboard_dir, game_seed]
	_ensure_directory_exists()
	_load_leaderboard()

func _ensure_directory_exists():
	var dir = DirAccess.open("user://")
	if not dir.dir_exists("leaderboards"):
		dir.make_dir("leaderboards")
		print("Created leaderboards directory")

func add_score(entry: ScoreEntry) -> Dictionary:
	"""
	Add a score to the leaderboard.
	Returns: {added: bool, rank: int}
	"""
	print("Adding score: ", entry.score, " for ", entry.player_name)

	# Add entry
	entries.append(entry)

	# Sort lexicographically (ADR-0002): turns dominant, doom-integral tiebreak.
	entries.sort_custom(func(a, b): return GameState.compare_score(a.score, a.doom_integral, b.score, b.doom_integral) > 0)

	# Find rank (1-based)
	var rank = 0
	for i in range(entries.size()):
		if entries[i].entry_uuid == entry.entry_uuid:
			rank = i + 1
			break

	# Trim to max entries
	if entries.size() > max_entries:
		entries = entries.slice(0, max_entries)

	# Save
	_save_leaderboard()

	var was_added = rank > 0 and rank <= max_entries
	print("Score added: ", was_added, " at rank ", rank)

	return {"added": was_added, "rank": rank}

func get_top_scores(count: int = 10) -> Array[ScoreEntry]:
	"""Get top N scores from leaderboard"""
	var top_count = min(count, entries.size())
	return entries.slice(0, top_count)

func is_high_score(score: int) -> bool:
	"""Check if a score would make the leaderboard"""
	if entries.size() < max_entries:
		return true

	# Check if better than worst score
	if entries.size() > 0:
		return score > entries[entries.size() - 1].score

	return true

func get_rank_for_score(score: int) -> int:
	"""Get what rank a score would achieve (0 = not on leaderboard)"""
	for i in range(entries.size()):
		if score > entries[i].score:
			return i + 1

	if entries.size() < max_entries:
		return entries.size() + 1

	return 0

func _save_leaderboard():
	"""Save leaderboard to JSON file (atomic write)"""
	var data = {
		"version": version,
		"created": Time.get_datetime_string_from_system(),
		"max_entries": max_entries,
		"seed": game_seed,
		"game_version": game_version,  # ADR-0002 #5
		"entries": []
	}

	for entry in entries:
		data["entries"].append(entry.to_dict())

	var json_string = JSON.stringify(data, "\t")
	var file = FileAccess.open(file_path, FileAccess.WRITE)
	if file:
		file.store_string(json_string)
		file.close()
		print("Leaderboard saved to: ", file_path)
	else:
		push_error("Failed to save leaderboard to: " + file_path)

func _load_leaderboard():
	"""Load leaderboard from JSON file"""
	if not FileAccess.file_exists(file_path):
		print("No leaderboard file found, creating new: ", file_path)
		return

	var file = FileAccess.open(file_path, FileAccess.READ)
	if not file:
		push_error("Failed to open leaderboard file: " + file_path)
		return

	var json_string = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(json_string)

	if parse_result != OK:
		push_error("Failed to parse leaderboard JSON")
		return

	var data = json.data
	version = data.get("version", "1.0.0")
	max_entries = data.get("max_entries", 50)

	entries.clear()
	for entry_data in data.get("entries", []):
		entries.append(ScoreEntry.from_dict(entry_data))

	print("Loaded ", entries.size(), " leaderboard entries from ", file_path)

func clear():
	"""Clear all entries (for testing)"""
	entries.clear()
	_save_leaderboard()

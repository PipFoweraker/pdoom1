extends Node
# leaderboard.gd
# Local leaderboard system for P(Doom) - JSON-based storage
# Ported from pygame/src/scores/local_store.py

class_name Leaderboard

# Score entry data structure
class ScoreEntry:
	var score: int  # Turns survived (primary metric)
	var player_name: String  # Lab name
	var date: String  # ISO timestamp
	var level_reached: int  # Final turn number
	var game_mode: String  # e.g., "Bootstrap_v0.4.1"
	var duration_seconds: float  # Game duration
	var entry_uuid: String  # Unique identifier
	var baseline_score: int  # Baseline (no-action) score for comparison (Issue #372)

	func _init(p_score: int, p_player_name: String, p_level: int, p_mode: String, p_duration: float, p_baseline: int = 0):
		score = p_score
		player_name = p_player_name
		date = Time.get_datetime_string_from_system()
		level_reached = p_level
		game_mode = p_mode
		duration_seconds = p_duration
		entry_uuid = generate_uuid()
		baseline_score = p_baseline

	func to_dict() -> Dictionary:
		return {
			"score": score,
			"player_name": player_name,
			"date": date,
			"level_reached": level_reached,
			"game_mode": game_mode,
			"duration_seconds": duration_seconds,
			"entry_uuid": entry_uuid,
			"baseline_score": baseline_score
		}

	static func from_dict(data: Dictionary) -> ScoreEntry:
		var entry = ScoreEntry.new(
			data.get("score", 0),
			data.get("player_name", "Unknown Lab"),
			data.get("level_reached", 0),
			data.get("game_mode", "Unknown"),
			data.get("duration_seconds", 0.0),
			data.get("baseline_score", 0)  # Issue #372
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
var leaderboard_dir: String = "user://leaderboards"
var file_path: String = ""

func _init(p_seed: String = "default"):
	game_seed = p_seed
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

	# Sort by score (highest first)
	entries.sort_custom(func(a, b): return a.score > b.score)

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

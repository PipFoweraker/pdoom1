extends Node
# leaderboard.gd
# Local leaderboard system for P(Doom) - JSON-based storage
# Ported from pygame/src/scores/local_store.py

class_name Leaderboard

# --- Remote board name budget (MEASURED, not assumed) -------------------------
# The remote score API stores at most this many BYTES of a submitted name and
# cuts the rest with a byte-wise substr. Measured on 2026-08-08 by reading the
# live (weekly-2026-w32, L4) board: Pip's lab went up as the 41-byte
# "GRIM (Global Risk Intervention Mechanism)" and came back as the 40-byte
# "GRIM (Global Risk Intervention Mechanism" -- amputated mid-word, closing
# bracket eaten, on the public board.
#
# BYTES rather than characters on purpose: a byte-wise server cut can also split
# a multi-byte UTF-8 codepoint and store an invalid string. The client fits the
# value itself (see fit_board_name) so the server's cut never fires at all.
#
# score_api.php lives on the server and is in no repo here, so raising this
# limit or adding a field is a server change -- routed through coordination,
# not decided here.
const BOARD_NAME_MAX_BYTES := 40
const BOARD_NAME_CUT_MARK := "..."

static func fit_board_name(raw: String) -> String:
	"""Fit a name inside the remote board's byte budget, LEGIBLY.

	The server cuts at a byte offset and says nothing, which is how
	"GRIM (Global Risk Intervention Mechanism)" became
	"GRIM (Global Risk Intervention Mechanism" on the public board -- a name
	that reads as a typo rather than as a truncation. Three rules:

	  1. a name that fits is returned untouched (a cut mark on an uncut name is
	     its own small lie);
	  2. a cut name ends in a visible mark, so the player can SEE it was cut;
	  3. the cut prefers a word boundary, so whole words are dropped rather than
	     words being sliced -- unless the boundary is so early that most of the
	     name would vanish, in which case a hard cut keeps more identity.

	Pure and static: no state, no I/O, unit-tested directly."""
	if raw.to_utf8_buffer().size() <= BOARD_NAME_MAX_BYTES:
		return raw
	var budget: int = BOARD_NAME_MAX_BYTES - BOARD_NAME_CUT_MARK.to_utf8_buffer().size()
	# Shrink by CHARACTERS while measuring in BYTES, so a multi-byte codepoint is
	# dropped whole and the result is always valid UTF-8 (the server's byte-wise
	# substr is exactly what can split one, and this stops it ever running).
	var cut := raw
	while cut.length() > 0 and cut.to_utf8_buffer().size() > budget:
		cut = cut.substr(0, cut.length() - 1)
	var space := cut.rfind(" ")
	if space >= int(budget * 0.5):
		cut = cut.substr(0, space)
	return cut.strip_edges() + BOARD_NAME_CUT_MARK

# Score entry data structure
class ScoreEntry:
	# ADR-0002: the score is the tuple (score, doom_integral) where `score` is
	# turns-survived (primary, dominant metric) and `doom_integral` is the
	# area-under-the-survival-curve tiebreak. `score` is named for back-compat with
	# the UI, which already treats it as turns.
	var score: int  # Turns survived (primary metric)
	var doom_integral: int  # Doom-integral tiebreak (ADR-0002)
	# TWO identity values, never conflated (Pip's ruling 2026-08-08). Generated
	# lab names COLLIDE -- that is why the #1133 generator exists at all -- so a
	# lab name alone cannot identify a person; and one player running several
	# labs over several months is a feature, which a single conflated field
	# would destroy permanently.
	var lab_name: String  # The org the player runs. What the frozen wire key `player_name` has always carried.
	var operator_name: String  # The human (GameConfig.player_name, "Operator:" in the prompt). Local-only so far.
	var date: String  # ISO timestamp
	var level_reached: int  # Final turn number (== score; kept for back-compat)
	var game_mode: String  # Game version, e.g. "v0.11.0"
	var duration_seconds: float  # Game duration
	var entry_uuid: String  # Unique identifier
	var baseline_score: int  # Baseline (no-action) turns survived for comparison (Issue #372)
	var baseline_doom_integral: int  # Baseline doom-integral tiebreak

	# p_operator_name is appended LAST and optional so every existing positional
	# caller (from_dict, tests, dev tools) keeps working unchanged.
	func _init(p_score: int, p_lab_name: String, p_level: int, p_mode: String, p_duration: float, p_baseline: int = 0, p_doom_integral: int = 0, p_baseline_integral: int = 0, p_operator_name: String = ""):
		score = p_score
		doom_integral = p_doom_integral
		lab_name = p_lab_name
		operator_name = p_operator_name
		date = Time.get_datetime_string_from_system()
		level_reached = p_level
		game_mode = p_mode
		duration_seconds = p_duration
		entry_uuid = generate_uuid()
		baseline_score = p_baseline
		baseline_doom_integral = p_baseline_integral

	func to_dict() -> Dictionary:
		"""LOCAL persistence shape. Carries BOTH names.

		`player_name` stays the key for the lab because every local board file
		already on disk uses it -- renaming the key would orphan existing rows.
		The GDScript field is now honestly named; the KEY is the frozen contract.
		Full, unfitted values: the local board is the complete record, and the
		remote budget is a remote problem (see to_wire_dict)."""
		return {
			"score": score,
			"doom_integral": doom_integral,
			"player_name": lab_name,  # frozen key; holds the LAB (see to_wire_dict)
			"operator_name": operator_name,
			"date": date,
			"level_reached": level_reached,
			"game_mode": game_mode,
			"duration_seconds": duration_seconds,
			"entry_uuid": entry_uuid,
			"baseline_score": baseline_score,
			"baseline_doom_integral": baseline_doom_integral
		}

	func to_wire_dict() -> Dictionary:
		"""REMOTE submission shape: exactly the frozen server contract, nothing else.

		Two deliberate differences from to_dict():
		  1. the lab name is pre-fitted to the board's measured byte budget, so
		     the server's own substr never fires and never amputates mid-word;
		  2. `operator_name` is NOT sent. score_api.php is server-side and in no
		     repo here, so its tolerance for unknown keys is unmeasured -- and a
		     rejected POST loses a score. Carrying the operator to the server is
		     a coordination item, not a client change."""
		var body := to_dict()
		body["player_name"] = Leaderboard.fit_board_name(lab_name)
		body.erase("operator_name")
		return body

	static func from_dict(data: Dictionary) -> ScoreEntry:
		var entry = ScoreEntry.new(
			data.get("score", 0),
			data.get("player_name", "Unknown Lab"),
			data.get("level_reached", 0),
			data.get("game_mode", "Unknown"),
			data.get("duration_seconds", 0.0),
			data.get("baseline_score", 0),  # Issue #372
			data.get("doom_integral", 0),
			data.get("baseline_doom_integral", 0),
			# Absent on every pre-existing row (local files AND the live board).
			# Defaults EMPTY on purpose: a legacy row genuinely has no operator,
			# and back-filling the lab into it would fabricate an identity.
			data.get("operator_name", "")
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
# ADR-0002 #5: boards are keyed by (seed, game_version). Post build-vs-ladder split
# this value is the LADDER EPOCH ("L1") passed by callers via
# GameConfig.get_board_version(), NOT the build string -- legacy pre-split files
# carry the old "v0.11.0"-style value and remain readable (spec DECISION B1).
var game_version: String = ""
var leaderboard_dir: String = "user://leaderboards"
var file_path: String = ""

func _init(p_seed: String = "default", p_version: String = ""):
	game_seed = p_seed
	game_version = p_version
	# ADR-0002 #5: version-scope the board so balance patches rotate the meta and old
	# scores never rank against the current game. Post build-vs-ladder split the scope
	# is the ladder EPOCH (filename "...__L1.json"), so cosmetic build bumps do NOT
	# rotate the board -- only gameplay-rule bumps do. Legacy callers (no version) keep
	# the old per-seed filename. Delimiter is '__' to survive hyphens/underscores in seeds.
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
	print("Adding score: ", entry.score, " for ", entry.lab_name)

	# #700: dedupe by entry_uuid, mirroring the remote endpoint (score_api.php
	# refuses a re-POST with duplicate:true). Without this a re-add appended a
	# duplicate row, and at the cap a duplicate could evict a distinct
	# legitimate entry. Return the existing entry's rank; do not double-count.
	if entry.entry_uuid != "":
		for i in range(entries.size()):
			if entries[i].entry_uuid == entry.entry_uuid:
				print("Duplicate entry_uuid -- not re-adding (rank ", i + 1, ")")
				return {"added": false, "rank": i + 1, "duplicate": true}

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

func rename_entry(uuid: String, new_name: String) -> bool:
	"""Rename one entry's displayed lab name in place (found by entry_uuid).

	Exists for the game-over default-identity prompt (Pip 2026-08-06): the local
	save runs FIRST (isolation contract rule 2 -- durable before any dialog), so
	a player who claims a name at the prompt has already saved the score under
	the old default. This retrofits the just-saved LOCAL row so the player can
	recognise their run on their own board too. Name-only: score, rank order,
	uuid and every other field are untouched, so this can never move a row."""
	var name := new_name.strip_edges()
	if uuid == "" or name == "":
		return false
	for entry in entries:
		if entry.entry_uuid == uuid:
			entry.lab_name = name
			_save_leaderboard()
			return true
	return false

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

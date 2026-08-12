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

# Separator between the lab and the operator in the single board field. ASCII
# double-hyphen per the house rule (issue #744), and NOT parentheses: the one
# real lab name we have -- "GRIM (Global Risk Intervention Mechanism)" --
# already contains brackets, so "LAB (OPERATOR)" would nest them.
const BOARD_NAME_SEPARATOR := " -- "

static func compose_board_name(lab: String, operator_name: String) -> String:
	"""Both names inside the ONE field the server actually stores.

	Measured 2026-08-10 against the deployed API: an unknown extra key is
	accepted (HTTP 200) and then silently dropped by $ALLOWED_FIELDS. So an
	`operator_name` key delivers nothing, and the only route to a public board
	is composition inside `player_name`.

	Format: `LAB -- OPERATOR`. Three reasons, each a real constraint:
	  1. LAB FIRST, because the rows already on the board hold a bare lab in
	     this column. Leading with the operator would change what the column
	     means halfway down the page.
	  2. `--`, not parentheses. The one real lab name we have,
	     "GRIM (Global Risk Intervention Mechanism)", already contains
	     brackets, so `LAB (OPERATOR)` nests them.
	  3. NEITHER half may erase the other. The operator exists to break lab-name
	     collisions -- Pip 2026-08-10, "we're going to get a LOT of colliding
	     labs" -- so it cannot be the half that silently vanishes; and a board
	     row with no lab is not what the column is for. The operator is capped
	     at half the composable budget and the lab takes the remainder, so a
	     long name shortens itself rather than the other one.

	Fitting is CLIENT-SIDE and mandatory, not cosmetic. Measured the same day:
	a submission whose byte-wise cut at 40 splits a UTF-8 codepoint takes the
	ENTIRE board to zero rows while the server answers ok:true -- PHP
	json_encode() returns false on malformed UTF-8, so the board file is
	truncated and rewritten with nothing. Composition is what first puts
	PLAYER-TYPED text into that byte-cut field, so this is the guard that keeps
	an accented operator name from destroying a public board."""
	var lab_clean := _collapse_separator(lab.strip_edges())
	var op_clean := _collapse_separator(operator_name.strip_edges())
	# No operator -> byte-identical to what this client already submits. Every
	# legacy row and every anonymous player is unaffected.
	if op_clean == "":
		return fit_board_name(lab_clean)
	if lab_clean == "":
		return fit_board_name(op_clean)
	var composable: int = BOARD_NAME_MAX_BYTES - BOARD_NAME_SEPARATOR.to_utf8_buffer().size()
	var op_fitted := fit_board_name(op_clean, int(composable / 2))
	var lab_fitted := fit_board_name(lab_clean, composable - op_fitted.to_utf8_buffer().size())
	return lab_fitted + BOARD_NAME_SEPARATOR + op_fitted

static func _collapse_separator(s: String) -> String:
	"""Keep the separator unambiguous: a name containing ' -- ' would otherwise
	make the composed string un-splittable back into two names by anyone reading
	the board."""
	var out := s
	while out.contains(BOARD_NAME_SEPARATOR):
		out = out.replace(BOARD_NAME_SEPARATOR, " - ")
	return out

static func fit_board_name(raw: String, max_bytes: int = BOARD_NAME_MAX_BYTES) -> String:
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

	`max_bytes` defaults to the whole board budget. compose_board_name passes a
	SHARE of it, so the same fitting rules apply to each half of a composed name.

	Pure and static: no state, no I/O, unit-tested directly."""
	if raw.to_utf8_buffer().size() <= max_bytes:
		return raw
	var budget: int = max_bytes - BOARD_NAME_CUT_MARK.to_utf8_buffer().size()
	if budget <= 0:
		# No room for even the cut mark. Shrink by CHARACTERS so the result is
		# still valid UTF-8, and drop the mark rather than return only a mark.
		var bare := raw
		while bare.length() > 0 and bare.to_utf8_buffer().size() > max_bytes:
			bare = bare.substr(0, bare.length() - 1)
		return bare
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
		  2. `operator_name` is NOT sent as its own key. MEASURED 2026-08-10
		     against the deployed API on a throwaway board: an unknown key is
		     accepted (HTTP 200) and then SILENTLY DROPPED by the server's
		     $ALLOWED_FIELDS whitelist. Not rejected -- but not stored either,
		     so a separate key delivers nothing. Until the server whitelists it,
		     both names travel COMPOSED inside the one frozen field."""
		var body := to_dict()
		body["player_name"] = Leaderboard.compose_board_name(lab_name, operator_name)
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

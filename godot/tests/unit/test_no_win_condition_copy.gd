extends GutTest
## ASSERTION GUARD, not an enumeration (fresh-eyes teardown 2026-08-06, finding 2).
##
## ADR-0002 (design series, docs/game-design/decisions/) deleted the victory bonus and
## ruled: "There is no victory condition." The score is turns survived with a
## doom-integral tiebreak. The engine agrees -- `GameState.victory` is initialised false
## and is never assigned true anywhere (check_win_lose sets it false on BOTH death
## routes; test_game_state.test_check_win_lose_doom_zero_no_victory pins doom<=0 as a
## non-ending).
##
## The COPY did not agree. On 2026-08-06 four player-facing surfaces still promised a
## win the game cannot award: the doom instrument tooltip ("Win by solving alignment
## (0%) or finishing below the league baseline"), the Player Guide ("REDUCE TO ZERO TO
## WIN!"), the game-over headline ("VICTORY!"), and the feed line ("VICTORY! You
## survived!") -- while the main menu subtitle said "You can't win. You can only buy
## time." Enumeration is the failure mode (#1050 enumerated nine AP strings and missed
## six). This test asserts the ABSENCE of the win claim across every player-facing
## surface, so the next one fails the fast gate instead of waiting for a playtest.
##
## Structure deliberately mirrors test_no_stale_ap_vocabulary.gd (#1073/#1116).
##
## NOT in scope: code comments and docstrings (this file's own tombstone comments SHOULD
## say "there is no victory condition"), internal identifiers such as the `victory`
## field and `is_victory` parameter, dev-only overlays, and the historical release
## record in data/patch_notes.json.
##
## The colliding docs/adr/0002 ("rare apex victory") is issue #809 and is NOT settled
## here; this guard encodes what the game currently IMPLEMENTS and what the menu tells
## the player first. If #809 rules the other way, this test is the thing to change.

const SCAN_DIRS := {
	"res://scenes": "tscn",
	"res://data": "json",
	"res://scripts/ui": "gd",
	"res://autoload": "gd",
}

## Dev-only / historical-record surfaces. Substring match on the res:// path.
const EXCLUDED_PATHS := [
	"debug_overlay",
	"dev_mode",
	"scripts/debug/",
	"data/patch_notes.json",
	"data/historical_events.json",  # verbatim arXiv abstract dumps, not authored copy
	"office_floor/",                # sandbox/dev tooling, not the played screen
]

const PLAYER_FACING_JSON_KEYS := [
	"name", "description", "text", "title", "message", "label", "summary",
	"detailed_description", "tooltip", "hint", "body", "subtitle", "flavor",
]

## A string that DENIES the win condition is the copy we want, not an offence. The menu
## subtitle and the resign tooltip both use the word "win" to say there isn't one.
## Checked case-insensitively against the whole string, before any offence matching.
const DENIALS := [
	"cannot win",
	"can not win",
	"can't win",
	"cant win",
	"no way to win",
	"never win",
	"no win condition",
	"no victory",
	"not a victory",
	"unwinnable",
]


func _is_excluded(path: String) -> bool:
	for frag in EXCLUDED_PATHS:
		if path.contains(frag):
			return true
	return false


func _walk(dir_path: String, ext: String, out: Array) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var name := d.get_next()
	while name != "":
		if name.begins_with("."):
			name = d.get_next()
			continue
		var full := dir_path.path_join(name)
		if d.current_is_dir():
			_walk(full, ext, out)
		elif name.get_extension() == ext and not _is_excluded(full):
			out.append(full)
		name = d.get_next()
	d.list_dir_end()


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var t := f.get_as_text()
	f.close()
	return t


## The offence patterns.
##   - `victory` / `victorious` in a player-facing string always announces the thing
##     ADR-0002 deleted.
##   - `win` / `wins` / `winnable` as a standalone word, UNLESS the same string denies
##     it. Deliberately NOT matching `won`: "won't show again" is a real, innocent
##     string and \bwon\b matches it, so the false-positive cost outweighs catching a
##     hypothetical "you have won".
## Plumbing, not prose: a bare lowercase token with no spaces is a dict key, a res://
## path, a signal name or a node name -- `state.get("victory", false)` is the engine
## FIELD, which ADR-0002 kept (initialised false, never assigned true). Same carve-out
## the AP guard makes for internal keys such as `ap_cost`. A player-facing sentence
## always has a space or a capital in it.
func _is_internal_identifier(text: String) -> bool:
	return RegEx.create_from_string("^[a-z0-9_./:%-]+$").search(text) != null


func _offences(text: String) -> Array:
	var found: Array = []
	if _is_internal_identifier(text):
		return found
	var lower := text.to_lower()
	for denial in DENIALS:
		if lower.contains(denial):
			return found
	if RegEx.create_from_string("(?i)\\b(victory|victorious|victories)\\b").search(text) != null:
		found.append("victory")
	if RegEx.create_from_string("(?i)\\b(win|wins|winnable)\\b").search(text) != null:
		found.append("win")
	return found


# --- .tscn: only the properties that render as words on screen -----------------------

func _tscn_player_strings(src: String) -> Array:
	var out: Array = []
	var re := RegEx.create_from_string(
		"(?m)^(text|tooltip_text|placeholder_text|hint_tooltip)\\s*=\\s*\"((?:[^\"\\\\]|\\\\.)*)\"")
	for m in re.search_all(src):
		out.append(m.get_string(2))
	return out


# --- .gd: string literals only, with comments and docstrings removed -----------------

func _gd_string_literals(src: String) -> Array:
	var stripped := RegEx.create_from_string("(?s)\"\"\".*?\"\"\"").sub(src, "", true)
	stripped = RegEx.create_from_string("(?m)#.*$").sub(stripped, "", true)
	var out: Array = []
	for m in RegEx.create_from_string("\"((?:[^\"\\\\\\n]|\\\\.)*)\"").search_all(stripped):
		out.append(m.get_string(1))
	return out


# --- .json: values of player-facing keys, at any nesting depth ------------------------

func _json_player_strings(value, out: Array) -> void:
	if value is Dictionary:
		for k in value.keys():
			var v = value[k]
			if v is String and String(k) in PLAYER_FACING_JSON_KEYS:
				out.append(v)
			else:
				_json_player_strings(v, out)
	elif value is Array:
		for item in value:
			_json_player_strings(item, out)


func _player_strings_for(path: String, ext: String) -> Array:
	var src := _read(path)
	if src.is_empty():
		return []
	match ext:
		"tscn":
			return _tscn_player_strings(src)
		"gd":
			return _gd_string_literals(src)
		"json":
			var json := JSON.new()
			if json.parse(src) != OK:
				return []
			var out: Array = []
			_json_player_strings(json.data, out)
			return out
	return []


func collect_offences() -> Array:
	var offences: Array = []
	for dir_path in SCAN_DIRS.keys():
		var ext: String = SCAN_DIRS[dir_path]
		var files: Array = []
		_walk(dir_path, ext, files)
		for path in files:
			for s in _player_strings_for(path, ext):
				for hit in _offences(s):
					offences.append("%s -- '%s' in: %s" % [path, hit, s.substr(0, 120)])
	return offences


func test_no_player_facing_surface_claims_a_win_condition():
	var offences := collect_offences()
	assert_eq(offences.size(), 0,
		"ADR-0002: there is no victory condition and the engine never sets victory=true. "
		+ "These player-facing strings still promise one:\n  - %s" % "\n  - ".join(offences))


func test_the_engine_never_awards_a_victory():
	# The copy guard is only honest if the mechanic really is absent. Both death routes
	# in check_win_lose set victory=false; doom<=0 is not an ending at all.
	var state = GameState.new("test_seed")
	state.doom = 100.0
	if state.doom_system:
		state.doom_system.current_doom = 100.0
	state.check_win_lose()
	assert_true(state.game_over, "doom 100 must end the run")
	assert_false(state.victory, "a doom death is not a victory (ADR-0002)")

	var state2 = GameState.new("test_seed")
	state2.reputation = 0.0
	state2.check_win_lose()
	assert_true(state2.game_over, "reputation collapse must end the run")
	assert_false(state2.victory, "a reputation death is not a victory (ADR-0002)")


func test_the_scan_actually_reaches_the_files_it_claims_to():
	# A guard that scans nothing passes forever.
	for dir_path in SCAN_DIRS.keys():
		var files: Array = []
		_walk(dir_path, SCAN_DIRS[dir_path], files)
		assert_gt(files.size(), 0, "scan found no .%s files under %s" % [SCAN_DIRS[dir_path], dir_path])


func test_the_offence_detector_is_not_vacuous():
	# Proves the matcher goes red on the exact strings that shipped on 2026-08-06 --
	# the cheap standing half of "reintroduce a string and watch it fail".
	assert_gt(_offences("Win by solving alignment (0%) or finishing below the league baseline.").size(), 0,
		"the main.tscn doom tooltip that shipped must be detected")
	assert_gt(_offences("The probability of AI catastrophe - REDUCE TO ZERO TO WIN!").size(), 0,
		"the player-guide line that shipped must be detected")
	assert_gt(_offences("VICTORY!").size(), 0,
		"the game-over headline that shipped must be detected")
	assert_gt(_offences("VICTORY! You survived!").size(), 0,
		"the main_ui feed line that shipped must be detected")
	# Known limit, stated rather than hidden: "Humanity Survived the AI Revolution" is a
	# victory claim with no win-word in it. Word matching cannot catch that class; it was
	# removed by hand, and it only ever appeared attached to the "VICTORY!" title which
	# this guard DOES catch.

	# The denials must NOT trip: the design's own voice uses "win" to negate it.
	assert_eq(_offences("You can't win. You can only buy time.").size(), 0,
		"the menu subtitle is the SOURCE of truth, not an offence")
	assert_eq(_offences("There is no way to win P(Doom); you are only ever buying time.").size(), 0,
		"the resign tooltip states the ruling and must not false-positive")
	assert_eq(_offences("There is no victory screen and no finish line.").size(), 0,
		"the rewritten guide denies the win condition and must not false-positive")
	assert_eq(_offences("Dismiss (won't show again for this version)").size(), 0,
		"'won't' must not trip -- this is why \\bwon\\b is deliberately not a pattern")
	assert_eq(_offences("Open the settings window").size(), 0,
		"'window' must not trip the word boundary")

	# The identifier carve-out must be narrow: it may swallow dict keys, never sentences.
	assert_eq(_offences("victory").size(), 0,
		"the bare `victory` dict key in state.get(\"victory\", false) is plumbing")
	assert_eq(_offences("res://scenes/ui/victory_screen.tscn").size(), 0,
		"a res:// path is plumbing")
	assert_gt(_offences("Victory").size(), 0,
		"a capitalised word is authored copy, not a dict key")
	assert_gt(_offences("you win").size(), 0,
		"a lowercase SENTENCE (it has a space) is still copy")

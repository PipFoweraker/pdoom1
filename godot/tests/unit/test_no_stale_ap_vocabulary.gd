extends GutTest
## ASSERTION GUARD, not an enumeration (#1073).
##
## The per-turn Action Point pool was DELETED by ADR-0011 amendment (a) and its code
## death landed in T2 (game_state.gd: "There is no `action_points` field, no per-turn
## grant, no AP in any cost dict"). PR #1050 was titled "finish killing player-facing
## AP" and it did NOT: it enumerated nine strings and shipped, leaving a main.tscn
## tooltip teaching a FORMULA for the dead mechanic ("Base 3 + 0.5 per staff"), two
## player-guide lines, an action description pricing a reward in the dead currency,
## and two historical-timeline option labels.
##
## Enumeration is the failure mode. This test asserts the ABSENCE of the vocabulary
## across every player-facing surface, so the next stale string fails the fast gate
## instead of waiting for a playtest.
##
## Scope -- surfaces a player can read:
##   - godot/scenes/**.tscn      `text` / `tooltip_text` / `placeholder_text` values
##   - godot/data/**.json        values of player-facing keys (name/description/text/...)
##   - godot/scripts/ui/**.gd    string literals (comments + docstrings stripped)
##   - godot/autoload/**.gd      string literals (keybind descriptions live here)
##
## Deliberately NOT in scope: code comments (game_state.gd's tombstone comment SHOULD
## say "the AP pool is DELETED"), internal dict keys such as `ap_cost`, dev-only
## surfaces (debug_overlay legitimately offers "Add 5 Action Points"), and
## data/patch_notes.json (a historical release record -- v0.2.x really did ship an
## "AP Double-Spend Bug" fix; rewriting history there would be the dishonest move).

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

## JSON keys whose values a player reads. Anything else in a data file is plumbing.
const PLAYER_FACING_JSON_KEYS := [
	"name", "description", "text", "title", "message", "label", "summary",
	"detailed_description", "tooltip", "hint", "body", "subtitle", "flavor",
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


## The offence patterns. "action point" in any casing is always the dead currency.
## Bare uppercase `AP` as a standalone word is the abbreviation -- inside a
## player-facing string there is no other thing it means.
func _offences(text: String) -> Array:
	var found: Array = []
	if text.to_lower().contains("action point"):
		found.append("action point")
	var re := RegEx.create_from_string("\\bAP\\b")
	if re.search(text) != null:
		found.append("AP")
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
	# Strip triple-quoted docstrings first (GDScript's comment-by-convention), then
	# line comments, then harvest what is left inside double quotes.
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


## Collect every offence in scope. Shared by the guard test and the meta-test that
## proves the guard can actually go red.
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


func test_no_player_facing_surface_teaches_the_retired_ap_currency():
	var offences := collect_offences()
	assert_eq(offences.size(), 0,
		"ADR-0011 deleted the AP pool. These player-facing strings still teach it:\n  - %s"
		% "\n  - ".join(offences))


func test_the_scan_actually_reaches_the_files_it_claims_to():
	# A guard that scans nothing passes forever. #1050 failed by enumerating; this
	# test fails if the walk silently stops finding files (renamed dirs, res:// change).
	for dir_path in SCAN_DIRS.keys():
		var files: Array = []
		_walk(dir_path, SCAN_DIRS[dir_path], files)
		assert_gt(files.size(), 0, "scan found no .%s files under %s" % [SCAN_DIRS[dir_path], dir_path])


func test_the_offence_detector_is_not_vacuous():
	# Proves the matcher itself goes red on the exact strings this issue is about --
	# the cheap standing half of "reintroduce a string and watch it fail".
	assert_eq(_offences("Action Points. Limits actions per turn. Base 3 + 0.5 per staff.").size(), 1,
		"the main.tscn tooltip that shipped must be detected")
	assert_gt(_offences("Use all your AP each turn - wasted AP = wasted time").size(), 0,
		"bare 'AP' in a player-facing string must be detected")
	assert_gt(_offences("+2 action points now").size(), 0,
		"a data-file description pricing a reward in AP must be detected")
	assert_eq(_offences("Attention -- the founder's month. Grant 20/month.").size(), 0,
		"the CURRENT vocabulary must not false-positive")
	assert_eq(_offences("Apply the patch").size(), 0,
		"'Apply' must not trip the bare-AP word boundary")

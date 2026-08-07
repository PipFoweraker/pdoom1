class_name CreditsData
extends RefCounted
## Read-only accessor for res://data/credits.json.
##
## That JSON is GENERATED from CREDITS.md by scripts/generate_credits.py and a
## pre-commit --check blocks a stale copy. Nothing in the game should hand-write
## a credit string: two copies of a contributor's name is how one of them ends
## up wrong and nobody notices (the decisions/README.md failure mode).
##
## Two callers today: credits_screen.gd (the whole surface) and office_cat.gd
## (the in-run "who is this cat" tooltip). Both go through here so the cat ->
## person mapping exists exactly once.

const CREDITS_PATH := "res://data/credits.json"

static var _cache: Dictionary = {}
static var _loaded: bool = false


## Parsed credits document. Returns an empty-but-shaped dictionary if the file
## is missing or malformed -- a credits screen with nothing on it is a bad day,
## a crash on the way to the main menu is a worse one.
static func data() -> Dictionary:
	if _loaded:
		return _cache
	_loaded = true
	_cache = {"cats": [], "sections": []}

	# ResourceLoader/FileAccess note: unlike an imported .jpg, a .json in
	# res://data IS shipped verbatim in the .pck, so FileAccess is correct here
	# (this is the opposite of the #796 texture trap in office_cat.gd).
	if not FileAccess.file_exists(CREDITS_PATH):
		push_warning("[CreditsData] missing " + CREDITS_PATH)
		return _cache
	var file := FileAccess.open(CREDITS_PATH, FileAccess.READ)
	if file == null:
		push_warning("[CreditsData] could not open " + CREDITS_PATH)
		return _cache
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_warning("[CreditsData] " + CREDITS_PATH + " did not parse as an object")
		return _cache
	var doc: Dictionary = parsed
	_cache = {
		"cats": doc.get("cats", []),
		"sections": doc.get("sections", []),
	}
	return _cache


## Every contributed cat: [{name, credited_to, asset}]. `credited_to` is "" when
## the preferred credit form is still unconfirmed in CREDITS.md -- callers must
## render the cat WITHOUT a credit line rather than printing a placeholder.
static func cats() -> Array:
	return data().get("cats", [])


static func sections() -> Array:
	return data().get("sections", [])


## Credit line for one cat asset file name (e.g. "web-luna.jpg"), or "" if the
## asset is unknown or its credit form is unconfirmed.
static func credit_for_asset(asset: String) -> String:
	for entry in cats():
		if typeof(entry) == TYPE_DICTIONARY and str(entry.get("asset", "")) == asset:
			return str(entry.get("credited_to", ""))
	return ""


## Test hook: drop the cache so a test can re-read after touching the file.
static func reset_cache() -> void:
	_cache = {}
	_loaded = false

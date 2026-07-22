extends Node
## Balance -- the central gameplay-tunables surface (L9, issue #621).
##
## JSON-backed, mirroring the proven ScenarioLoader/EventService load pattern:
## shipped defaults live in res://data/balance/defaults.json; an optional
## user://balance_overrides.json deep-merges on top so sweeps/tuning swap a file
## instead of editing code (DQ-8 / ADR-0013 numbers become file-swaps).
##
## BEHAVIOR-PRESERVATION CONTRACT: every consumer passes its pre-L9 inline
## literal as the fallback default, and defaults.json ships those exact values.
## A missing or broken file therefore degrades to exactly the shipped behavior
## (with a push_error so the packaging bug is visible).
##
## Usage:
##   Balance.num("ledger.loan.interest_rate", 0.25)
##   Balance.inum("events.max_new_events_per_turn", 2)
##   Balance.table("difficulty.easy")

const DEFAULTS_PATH := "res://data/balance/defaults.json"
const USER_OVERRIDES_PATH := "user://balance_overrides.json"

var _data: Dictionary = {}
var _cache: Dictionary = {}  # dotted path -> resolved value (null = known-missing)


func _ready() -> void:
	reload()


func reload() -> void:
	"""(Re)load defaults + user overrides. Safe to call at runtime (sweeps/tests)."""
	_cache.clear()
	_data = _load_json(DEFAULTS_PATH)
	if _data.is_empty():
		push_error("[Balance] Missing or invalid %s -- falling back to call-site defaults" % DEFAULTS_PATH)

	var overrides := _load_json(USER_OVERRIDES_PATH, true)
	if not overrides.is_empty():
		_deep_merge(_data, overrides)
		print("[Balance] Applied user balance overrides (%d top-level keys)" % overrides.size())


func num(path: String, default_value: float) -> float:
	"""Numeric tunable at dotted path; default_value is the pre-L9 literal."""
	var v = _lookup(path)
	if v is float or v is int:
		return float(v)
	return default_value


func inum(path: String, default_value: int) -> int:
	"""Integer tunable at dotted path; default_value is the pre-L9 literal."""
	var v = _lookup(path)
	if v is float or v is int:
		return int(v)
	return default_value


func table(path: String, default_value: Dictionary = {}) -> Dictionary:
	"""Dictionary subtree at dotted path (e.g. a difficulty level's modifiers)."""
	var v = _lookup(path)
	if v is Dictionary:
		return v
	return default_value


func _lookup(path: String):
	if _cache.has(path):
		return _cache[path]
	var node = _data
	for part in path.split("."):
		if node is Dictionary and node.has(part):
			node = node[part]
		else:
			_cache[path] = null
			return null
	_cache[path] = node
	return node


func _load_json(path: String, optional: bool = false) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		if not optional:
			push_error("[Balance] Failed to open %s" % path)
		return {}
	var json := JSON.new()
	var err := json.parse(file.get_as_text())
	file.close()
	if err != OK:
		push_error("[Balance] Failed to parse %s: %s" % [path, json.get_error_message()])
		return {}
	var data = json.get_data()
	if not data is Dictionary:
		push_error("[Balance] %s is not a JSON object" % path)
		return {}
	return data


func _deep_merge(base: Dictionary, extra: Dictionary) -> void:
	for key in extra.keys():
		if key.begins_with("_"):
			continue  # metadata keys (_description, _reason)
		if extra[key] is Dictionary and base.has(key) and base[key] is Dictionary:
			_deep_merge(base[key], extra[key])
		else:
			base[key] = extra[key]

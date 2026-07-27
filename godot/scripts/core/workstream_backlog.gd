extends RefCounted
class_name WorkstreamBacklog
## The standing backlog of directed work (ADR-0011 s3: "idle staff don't exist"). Loads
## res://data/workstreams/backlog.json once and exposes a read-only API GameState uses to
## mint Workstream objects. Same shape as QuirkCatalogue -- data over hardcoding.
##
## DETERMINISM (ADR-0006): entries() returns the list SORTED BY ID, never in JSON/parse
## order, so any code that indexes or iterates the backlog is order-stable across
## platforms and reloads. There is no rng here: which workstream starts is player input.

const Definitions = preload("res://scripts/data/definition_loader.gd")
const BACKLOG_PATH := "res://data/workstreams/backlog.json"

static var _loaded: bool = false
static var _entries: Array[Dictionary] = []
static var _by_id: Dictionary = {}


static func _ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	var data := Definitions.load_object(BACKLOG_PATH, "WorkstreamBacklog")
	var raw = data.get("workstreams", [])
	var collected: Array[Dictionary] = []
	if raw is Array:
		for e in raw:
			if e is Dictionary and String(e.get("id", "")) != "":
				collected.append((e as Dictionary).duplicate(true))
	collected.sort_custom(func(a, b): return String(a.get("id", "")) < String(b.get("id", "")))
	_entries = collected
	_by_id = {}
	for e in _entries:
		_by_id[String(e.get("id", ""))] = e
	if _entries.is_empty():
		push_error("[WorkstreamBacklog] No workstreams loaded from %s" % BACKLOG_PATH)


static func reload() -> void:
	"""Force a re-read (tests + the balance reload path)."""
	_loaded = false
	_entries = []
	_by_id = {}
	_ensure_loaded()


static func entries() -> Array[Dictionary]:
	"""All backlog entries, id-sorted. Copies out -- callers must not mutate the cache."""
	_ensure_loaded()
	var out: Array[Dictionary] = []
	for e in _entries:
		out.append(e.duplicate(true))
	return out


static func size() -> int:
	_ensure_loaded()
	return _entries.size()


static func has(entry_id: String) -> bool:
	_ensure_loaded()
	return _by_id.has(entry_id)


static func get_entry(entry_id: String) -> Dictionary:
	"""One backlog entry by id, or {} if unknown."""
	_ensure_loaded()
	var e = _by_id.get(entry_id, {})
	return (e as Dictionary).duplicate(true) if e is Dictionary else {}


static func ids() -> Array[String]:
	_ensure_loaded()
	var out: Array[String] = []
	for e in _entries:
		out.append(String(e.get("id", "")))
	return out


static func entries_for_topic(topic_key: String) -> Array[Dictionary]:
	"""Backlog entries on one topic (id-sorted, like entries())."""
	var out: Array[Dictionary] = []
	for e in entries():
		if String(e.get("topic", "")) == topic_key:
			out.append(e)
	return out

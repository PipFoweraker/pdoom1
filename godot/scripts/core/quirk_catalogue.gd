extends RefCounted
class_name QuirkCatalogue
## Data-driven researcher QUIRK catalogue (replaces the retired hardcoded trait system and
## the placeholder QUIRK_POOL). Loads res://data/researchers/quirks.json once and exposes a
## small read-only API the sim reads through Researcher.quirk_effect().
##
## DETERMINISM (ADR-0006): pick_id() indexes a SORTED id list, so the draw is a pure function
## of the seeded rng and is independent of JSON key / Dictionary iteration order. Definitions
## are hidden-but-TRUE: a quirk's effect is live from creation; play only REVEALS it.
## Design + rationale: docs/game-design/RESEARCHER_QUIRKS.md.

const Definitions = preload("res://scripts/data/definition_loader.gd")
const QUIRKS_PATH := "res://data/researchers/quirks.json"

static var _loaded: bool = false
static var _defs: Dictionary = {}
static var _ids: Array[String] = []

static func _ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	var data := Definitions.load_object(QUIRKS_PATH, "QuirkCatalogue")
	_defs = data.get("quirks", {})
	if _defs.is_empty():
		push_error("[QuirkCatalogue] No quirks loaded from %s" % QUIRKS_PATH)
	_ids = []
	for k in _defs.keys():
		_ids.append(String(k))
	# Sort so pick_id indexing is deterministic regardless of parse/dict order (ADR-0006).
	_ids.sort()

static func ids() -> Array[String]:
	_ensure_loaded()
	return _ids.duplicate()

static func size() -> int:
	_ensure_loaded()
	return _ids.size()

static func has(id: String) -> bool:
	_ensure_loaded()
	return _defs.has(id)

static func get_def(id: String) -> Dictionary:
	_ensure_loaded()
	return _defs.get(id, {})

static func effect(id: String, key: String, default_value):
	"""Return quirk `id`'s effect-channel `key`, or default_value if the quirk (or key) is
	absent. The only channels the sim honours are listed in RESEARCHER_QUIRKS.md."""
	_ensure_loaded()
	var eff: Dictionary = _defs.get(id, {}).get("effects", {})
	return eff.get(key, default_value)

static func reveal_after_turns(id: String, default_value: int = 6) -> int:
	"""Deterministic tenure fallback: the turn count at/after which employment surfaces the
	quirk even absent a bespoke incident. Guarantees every quirk reveals in play."""
	_ensure_loaded()
	var rv: Dictionary = _defs.get(id, {}).get("reveal", {})
	return int(rv.get("after_turns", default_value))

static func reveal_via(id: String) -> String:
	"""Narrative trigger tag ('tenure' | 'incident' | 'leak'). Telemetry / flavour only; the
	deterministic reveal is driven by reveal_after_turns (+ leak self-surfacing)."""
	_ensure_loaded()
	var rv: Dictionary = _defs.get(id, {}).get("reveal", {})
	return String(rv.get("via", "tenure"))

static func display_name(id: String) -> String:
	_ensure_loaded()
	if id == "":
		return "none"
	return String(_defs.get(id, {}).get("name", id.capitalize()))

static func flavour(id: String) -> String:
	_ensure_loaded()
	return String(_defs.get(id, {}).get("flavour", ""))

static func pick_id(rng: RandomNumberGenerator) -> String:
	"""Deterministically draw a quirk id from the seeded rng (sorted-index, ADR-0006)."""
	_ensure_loaded()
	if _ids.is_empty():
		return ""
	return _ids[rng.randi() % _ids.size()]

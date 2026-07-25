extends RefCounted
class_name PropCatalogue
## Data-driven office-prop metadata catalogue. Loads res://data/office/props_manifest.json
## once (static/lazy, same pattern as quirk_catalogue.gd) and exposes a small read-only API:
## per-prop footprint, feet anchor, height, and style-family tags.
##
## PURPOSE: replace the renderer's one-size-fits-all PROP_TARGET_H force-scale (every prop
## squashed to 46 display px, feet-anchored) with per-asset metadata. This lane ships DATA +
## LOADER + TESTS only; office_floor.gd / office_sandbox.gd integration is a documented
## follow-up AFTER the in-flight scale lane merges (see docs/art/PROP_MANIFEST.md).
##
## DETERMINISM: ids() and style_ids() return SORTED id lists, so any seeded-rng draw over
## them is independent of JSON key / Dictionary iteration order (same rule as ADR-0006).
##
## FALLBACK: every accessor answers sanely for an unmanifested id (push_warning ONCE per id)
## so a new prop PNG dropped in without a manifest entry renders like today instead of
## crashing: height matches the legacy PROP_TARGET_H behaviour, footprint is 1x1, anchor is
## the ANCHOR_UNSET sentinel (caller should fall back to texture bottom-centre).

const Definitions = preload("res://scripts/data/definition_loader.gd")
const MANIFEST_PATH := "res://data/office/props_manifest.json"

## Legacy renderer behaviour being replaced: office_floor.gd::PROP_TARGET_H scales every
## prop to 46 px tall at the 64 px DISPLAY tile (floor art is 32 px drawn 2x). The fallback
## height reproduces that: 46/64 of a tile, whatever tile_px the caller passes.
const FALLBACK_TARGET_H := 46.0
const DISPLAY_TILE_PX := 64.0

## Sentinel returned by anchor() for unmanifested ids: "no anchor data, use the texture's
## bottom-centre" (a real anchor always has x >= 0 and y > 0).
const ANCHOR_UNSET := Vector2(-1, -1)

static var _loaded: bool = false
static var _defs: Dictionary = {}
static var _ids: Array[String] = []
static var _warned: Dictionary = {}


static func _ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	var data := Definitions.load_object(MANIFEST_PATH, "PropCatalogue")
	_defs = data.get("props", {})
	if _defs.is_empty():
		push_error("[PropCatalogue] No props loaded from %s" % MANIFEST_PATH)
	_ids = []
	for k in _defs.keys():
		_ids.append(String(k))
	# Sorted so index-based seeded draws are deterministic regardless of parse order.
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


static func get_entry(id: String) -> Dictionary:
	"""Full manifest entry for `id`, or {} for unmanifested ids (warns once)."""
	_ensure_loaded()
	if not _defs.has(id):
		_warn_once(id)
		return {}
	return _defs[id]


static func height_px(id: String, tile_px: float = DISPLAY_TILE_PX) -> float:
	"""Rendered subject height in px when a floor tile renders at `tile_px`.
	Manifested: height_tiles * tile_px. Fallback: the legacy PROP_TARGET_H
	force-scale (46 px at the 64 px display tile), scaled to `tile_px`."""
	_ensure_loaded()
	if not _defs.has(id):
		_warn_once(id)
		return FALLBACK_TARGET_H * tile_px / DISPLAY_TILE_PX
	return float(_defs[id].get("height_tiles", FALLBACK_TARGET_H / DISPLAY_TILE_PX)) * tile_px


static func anchor(id: String) -> Vector2:
	"""Feet anchor in CANVAS px (bottom-centre of the opaque subject). Returns
	ANCHOR_UNSET for unmanifested ids -- caller falls back to texture bottom-centre."""
	_ensure_loaded()
	if not _defs.has(id):
		_warn_once(id)
		return ANCHOR_UNSET
	var a: Array = _defs[id].get("anchor_px", [])
	if a.size() != 2:
		return ANCHOR_UNSET
	return Vector2(float(a[0]), float(a[1]))


static func footprint(id: String) -> Vector2i:
	"""Floor tiles occupied [w, h] at the 32 px art-tile scale. Fallback: 1x1."""
	_ensure_loaded()
	if not _defs.has(id):
		_warn_once(id)
		return Vector2i(1, 1)
	var f: Array = _defs[id].get("footprint_tiles", [])
	if f.size() != 2:
		return Vector2i(1, 1)
	return Vector2i(int(f[0]), int(f[1]))


static func art_path(id: String) -> String:
	"""res:// path of the prop texture, or "" for unmanifested ids."""
	_ensure_loaded()
	if not _defs.has(id):
		_warn_once(id)
		return ""
	return String(_defs[id].get("art", ""))


static func style_tags(id: String) -> Array[String]:
	"""Office-state families ("scummy"/"decent") this prop belongs to. Empty for
	unmanifested ids."""
	_ensure_loaded()
	var out: Array[String] = []
	if not _defs.has(id):
		_warn_once(id)
		return out
	for t in _defs[id].get("style_tags", []):
		out.append(String(t))
	return out


static func style_ids(tag: String) -> Array[String]:
	"""All prop ids carrying style tag `tag`, SORTED (deterministic for seeded draws)."""
	_ensure_loaded()
	var out: Array[String] = []
	for id in _ids:
		if _defs[id].get("style_tags", []).has(tag):
			out.append(id)
	return out  # _ids already sorted


static func _warn_once(id: String) -> void:
	if _warned.has(id):
		return
	_warned[id] = true
	push_warning(
		"[PropCatalogue] '%s' has no manifest entry -- using legacy PROP_TARGET_H fallback. "
		% id
		+ "Add it to %s (see docs/art/PROP_MANIFEST.md)." % MANIFEST_PATH
	)

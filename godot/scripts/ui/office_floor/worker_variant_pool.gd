extends RefCounted
class_name WorkerVariantPool
## Data-driven worker APPEARANCE variant registry (#793 mechanism half).
##
## Loads res://data/office/worker_variants.json once (static/lazy, same pattern
## as PropCatalogue) and maps an employee's appearance_id to a SpriteFrames
## resource. ART-AGNOSTIC: today the manifest lists ONE variant -- the current
## shared office_worker.tres -- so every worker resolves to the same art and
## behaviour is byte-for-byte unchanged. When the round-2 worker sheets are
## triaged in (Pip), new variants are ADDED to the JSON list; no code changes.
##
## DETERMINISM / STABILITY: variant_index_for() is a pure function of the
## appearance_id and the variant count (posmod of an int id, or of the stable
## String hash) -- the same appearance_id always lands on the same variant for a
## fixed variant list, independent of roster order or size. Note the boundary:
## CHANGING the variant count remaps assignments (documented tradeoff; the
## per-run mapping is what matters for a cosmetic pure view, ADR-0006).
##
## FALLBACK: a variant whose frames path is missing/unloadable resolves to null
## (warn once); the caller (OfficeFloor) then falls back to its shared frames.

const Definitions = preload("res://scripts/data/definition_loader.gd")
const MANIFEST_PATH := "res://data/office/worker_variants.json"

static var _loaded: bool = false
static var _variants: Array = []           # [{id, frames, ...}] in manifest order
static var _frames_cache: Dictionary = {}  # frames path -> SpriteFrames or null
static var _warned: Dictionary = {}


static func _ensure_loaded() -> void:
	if _loaded:
		return
	_loaded = true
	var data := Definitions.load_object(MANIFEST_PATH, "WorkerVariantPool")
	_variants = []
	for v in data.get("variants", []):
		if v is Dictionary:
			_variants.append(v)
	if _variants.is_empty():
		push_warning("[WorkerVariantPool] no variants in %s -- floors fall back to shared frames" % MANIFEST_PATH)


static func count() -> int:
	_ensure_loaded()
	return _variants.size()


static func variant_id_at(index: int) -> String:
	_ensure_loaded()
	if index < 0 or index >= _variants.size():
		return ""
	return String(_variants[index].get("id", ""))


## Pure, stable appearance -> variant-index mapping. Accepts an int (used
## directly) or anything else (stable String hash). Returns -1 when the pool is
## empty (caller falls back). Exposed with an explicit `cnt` so tests can pin it.
static func variant_index_for(appearance_id, cnt: int) -> int:
	if cnt <= 0:
		return -1
	var n: int
	match typeof(appearance_id):
		TYPE_INT:
			n = appearance_id
		TYPE_FLOAT:
			n = int(appearance_id)
		_:
			n = String(appearance_id).hash()
	return posmod(n, cnt)


## SpriteFrames for this appearance, or null when the pool is empty or the
## mapped variant's art fails to load (graceful fallback path).
static func frames_for(appearance_id) -> SpriteFrames:
	_ensure_loaded()
	var idx := variant_index_for(appearance_id, _variants.size())
	if idx < 0:
		return null
	return _load_frames(String(_variants[idx].get("frames", "")))


static func _load_frames(path: String) -> SpriteFrames:
	if path == "":
		return null
	if not _frames_cache.has(path):
		var res: Resource = null
		if ResourceLoader.exists(path):
			res = load(path)
		if res is SpriteFrames:
			_frames_cache[path] = res
		else:
			_frames_cache[path] = null
			if not _warned.has(path):
				_warned[path] = true
				# print, not push_warning: this is the DESIGNED degrade path (missing
				# variant art -> shared frames) and unit tests exercise it on purpose.
				print("[WorkerVariantPool] variant frames missing/invalid: %s -- falling back to shared frames" % path)
	return _frames_cache[path]


# --- test seams (unit tests only; static state persists across a GUT run) ----
static func _override_variants_for_test(variants: Array) -> void:
	_loaded = true
	_variants = variants.duplicate(true)
	_frames_cache.clear()
	_warned.clear()


static func _reset_for_test() -> void:
	_loaded = false
	_variants = []
	_frames_cache.clear()
	_warned.clear()

extends RefCounted
class_name PortraitLibrary
## Deterministic portrait picker for candidate/employee cards (DQ-15 / #758).
##
## The staged dossier portraits (godot/assets/portraits/, see README.md there) are five
## archetype images with no name/identity mapping yet -- this picks one PER PERSON,
## stably, from their existing seeded `appearance_id` ("body_NN", NN 0..IDENTITY_POOL_SIZE-1
## per researcher.gd). It does NOT claim to match the archetype semantically; it just makes
## the art visible (Pip 2026-07-24: "demonstrate portraits even if they don't match names").
## Swap _index_for()'s mapping for a real archetype->portrait rule later without touching
## callers.

const PORTRAIT_DIR := "res://assets/portraits/"
const PORTRAIT_SIZE := 256

## File stems in the staged set (README.md table order). Kept small/explicit rather than a
## directory scan: deterministic across platforms, and a missing file just no-ops (see
## get_portrait) instead of shifting every other person's assignment.
const PORTRAIT_STEMS := [
	"dossier_people_pleaser",
	"dossier_authoritarian_pessimist",
	"dossier_moral_crusader",
	"dossier_capabilities_optimist",
	"dossier_burned_out_senior",
]

# stem -> Texture2D or null (load failed / missing). Loaded once, reused for every card.
static var _cache: Dictionary = {}

## Texture2D for this appearance_id, or null if nothing is staged for it (callers must
## fall back to text-only -- never crash on missing art). Accepts Variant: appearance_id
## is a String in researcher.gd but some snapshot dicts (office_floor.gd) carry a bare int.
static func get_portrait(appearance_id) -> Texture2D:
	var stem: String = PORTRAIT_STEMS[_index_for(appearance_id)]
	if _cache.has(stem):
		return _cache[stem]
	var path := "%s%s_%d.png" % [PORTRAIT_DIR, stem, PORTRAIT_SIZE]
	var tex: Texture2D = null
	if ResourceLoader.exists(path):
		var loaded = load(path)
		if loaded is Texture2D:
			tex = loaded
	_cache[stem] = tex
	return tex

## Ready-to-add TextureRect for `appearance_id`, sized for a card thumbnail, or null if no
## portrait is available (caller stays text-only).
static func make_texture_rect(appearance_id, thumb_size: int = 48) -> TextureRect:
	var tex := get_portrait(appearance_id)
	if tex == null:
		return null
	var rect := TextureRect.new()
	rect.texture = tex
	rect.custom_minimum_size = Vector2(thumb_size, thumb_size)
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	return rect

## Stable index into PORTRAIT_STEMS for a given appearance_id. Deliberately NOT archetype-
## aware (identity is uncorrelated with ability per researcher.gd) -- just deterministic per
## person so the same candidate always shows the same face across re-renders/reloads.
static func _index_for(appearance_id) -> int:
	if appearance_id == null or appearance_id == "":
		return 0
	if appearance_id is String and appearance_id.begins_with("body_"):
		var num_str: String = appearance_id.substr(5)
		if num_str.is_valid_int():
			return int(num_str) % PORTRAIT_STEMS.size()
	if appearance_id is int or appearance_id is float:
		return absi(int(appearance_id)) % PORTRAIT_STEMS.size()
	# Non-standard id (e.g. test fixtures): hash it instead of crashing or always
	# picking index 0.
	return absi(hash(str(appearance_id))) % PORTRAIT_STEMS.size()

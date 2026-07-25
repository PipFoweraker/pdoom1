extends Control
## OFFICE SANDBOX v2 -- a standalone DEV TOY for the office-floor view (Pip: open
## this in the evening and play). Spawn walking people, cycle their skin, add/remove
## cats, change the room's mood, AND (v2) load the PROMOTED art assets from
## art_source, drop props onto a tile grid, flip the office STATE (scummy/decent) to
## preview "office reflects game state", and leave IN-CONTEXT feedback that persists.
##
## This is the prototyping ground for the future runtime "office reflects game state"
## asset system (see docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md). It is a
## DEV TOOL and NEVER ships to players.
##
## MECHANICS-SAFE / W3-SAFE (by construction): PURE COMPOSITION. It instantiates the
## existing OfficeFloor view (res://scenes/ui/office_floor/office_floor.tscn) and
## drives it through its EXISTING public API only, plus two ADDITIVE cosmetic dev
## hooks added in this PR (OfficeFloor.set_floor_tile_texture / set_wall_strip_texture,
## both backward-compatible no-ops for the live WATCH integration). There is NO game
## state, no economy, no win/lose, no touching of employee_fsm/employee_sprite/
## watch_screen/main_ui/GameState. Just a toy + an art review loop.
##
## PROMOTED-ASSET LOADING (v2): the promoted assets live in art_source/ which is
## OUTSIDE the Godot project (NOT res://). We compute the art_source dir from
## ProjectSettings.globalize_path("res://") + "/../art_source", read the promote list
## art_source/promote_list.txt (newline paths grouped by "# category/subtype"
## headers, each path relative to art_source), and load each PNG by ABSOLUTE
## filesystem path via Image.load() -> ImageTexture. If promote_list.txt is absent we
## fall back to art_source/pixellab_verdicts.json (keys whose tag array contains
## "promote"). BOTH files are UNTRACKED (they live only in Pip's working copy), so in
## a fresh checkout the loader finds nothing and degrades cleanly to placeholders --
## the toy still runs, it just has an empty prop pool until run from the working copy.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")
# Real pixellab.ai art-loop SpriteFrames (idle/walking/working/stressed + directional walks).
const RealSpriteFrames := preload("res://assets/office_floor/artloop_char/office_worker.tres")
# Reused ONLY for its static _build_placeholder_frames() colour-skin generator (no instances).
const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")

const HAT := Color(0.14, 0.14, 0.18)
const MAX_PEOPLE := 24
const MAX_CATS := 8
const MAX_PLACED := 64

# Tile grid props snap to (matches the 32px source tile scale; feels like desks-on-a-grid).
const GRID := 32.0
# Target on-floor height a placed prop is scaled to (aspect kept), matching OfficeFloor props.
const PROP_TARGET_H := 46.0
# Region of a 4x4 Wang tileset atlas holding the all-lower base tile (same crop OfficeFloor
# uses). Applied to promoted floor/wall tilesets before handing them to the dev hooks.
const WANG_BASE_REGION := Rect2i(64, 32, 32, 32)
const TILE_UPSCALE := 2

# Skins the sandbox rotates through. "art" = real pixellab frames; "color" = a generated
# animated placeholder tinted body+hat (Tier 1); "blob" = Tier 0 procedural blob+hat.
var _skins: Array = [
	{"name": "Pixellab worker (real art)", "kind": "art"},
	{"name": "Green / safety",             "kind": "color", "body": Color(0.35, 0.75, 0.45)},
	{"name": "Orange / capabilities",      "kind": "color", "body": Color(0.85, 0.45, 0.30)},
	{"name": "Blue / interpretability",    "kind": "color", "body": Color(0.55, 0.55, 0.90)},
	{"name": "Teal / alignment",           "kind": "color", "body": Color(0.40, 0.75, 0.80)},
	{"name": "Gold / manager",             "kind": "color", "body": Color(0.80, 0.75, 0.40)},
	{"name": "Blobs (Tier 0)",             "kind": "blob"},
]

# Room mood/lighting -- a whole-floor tint via modulate (cats inherit it as children).
var _moods: Array = [
	{"name": "Day",   "tint": Color(1.00, 1.00, 1.00)},
	{"name": "Warm",  "tint": Color(1.10, 0.96, 0.82)},
	{"name": "Cool",  "tint": Color(0.84, 0.92, 1.12)},
	{"name": "Night", "tint": Color(0.58, 0.60, 0.82)},
	{"name": "Sepia", "tint": Color(1.08, 0.94, 0.72)},
]

# Coarse office STATE -- the prototype "reflects game state" query. Each state biases
# which promoted props are offered (by keyword match on the asset id) and picks a
# promoted floor/wall tileset (matched by filename substring) to swap in. The real
# runtime hook later reads this from GameState instead of a keypress. "neutral" props
# (matching NO state keyword) are offered in every state.
var _states: Array = [
	{"name": "scummy", "floor_key": "floor_lino",     "wall_key": "wall_scummy", "bias": ["scummy"]},
	{"name": "decent", "floor_key": "floor_concrete", "wall_key": "wall_decent", "bias": ["decent", "clean", "mega"]},
]
# Union of every state's bias keywords -- a prop matching none of these is "neutral".
const _STATE_KEYWORDS := ["scummy", "decent", "clean", "mega"]

# Cat coat colours cycled as cats are added.
var _cat_palette: Array = [
	Color(0.16, 0.16, 0.18),   # black
	Color(0.85, 0.55, 0.25),   # ginger tabby
	Color(0.62, 0.62, 0.66),   # grey
	Color(0.94, 0.94, 0.95),   # white
]

const _NAME_POOL := [
	"Sage", "Riley", "Quinn", "Morgan", "Parker", "Lane", "Avery", "Kai",
	"Rowan", "Emerson", "Devon", "Skyler", "Marlowe", "Reese", "Sasha", "Nico",
]
const _SPEC_POOL := ["safety", "capabilities", "interpretability", "alignment", "manager"]

# Feedback tags leaveable on the focused prop (written to sandbox_feedback.json).
const _TAG_KEYS := {
	KEY_L: "like", KEY_J: "dislike", KEY_F: "favour",
	KEY_G: "disfavour", KEY_M: "promote", KEY_N: "note",
}

var _floor: OfficeFloor
var _legend: Label
var _status: Label
var _asset_status: Label
var _roster: Array = []
var _cats: Array = []
var _next_id: int = 0
var _skin_idx: int = 0
var _mood_idx: int = 0
var _state_idx: int = 0
var _cat_color_idx: int = 0
var _rng := RandomNumberGenerator.new()

# --- v2 promoted-asset + feedback state -------------------------------------
var _art_root: String = ""                 # absolute, normalised path to art_source/
var _promoted: Dictionary = {}             # category -> Array of asset dicts
var _load_report: String = ""              # human-readable "found N props, M tilesets"
var _prop_pool: Array = []                 # state-filtered subset of promoted props
var _prop_idx: int = 0
var _placed_props: Array = []              # Sprite2D children of _floor
var _ghost: Sprite2D = null                # translucent placement preview following the mouse
var _feedback: Dictionary = {}             # asset_id -> {"tags":[...], "notes":[...]}

func _ready() -> void:
	_rng.randomize()
	set_anchors_preset(Control.PRESET_FULL_RECT)

	_floor = OfficeFloorScene.instantiate()
	_floor.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_floor)

	# Load promoted assets + any existing feedback BEFORE the overlay so the legend/
	# status can report counts. Both degrade to empty if the source files are absent.
	_art_root = _compute_art_root()
	_load_feedback()
	_load_promoted()
	_rebuild_prop_pool()

	_build_overlay()
	_build_ghost()

	# Start with the real-art skin and a few people so it's alive on open.
	_apply_skin(0)
	_apply_mood(0)
	_apply_state(0)
	for _i in range(5):
		_spawn_person()
	_add_cat()
	_update_status()

func _build_overlay() -> void:
	var panel := PanelContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.position = Vector2(8, 8)
	add_child(panel)

	var vb := VBoxContainer.new()
	vb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(vb)

	_legend = Label.new()
	_legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_legend.add_theme_font_size_override("font_size", 13)
	_legend.text = "OFFICE SANDBOX v2  --  dev toy (no game state)\n" \
		+ "[1]/[2] spawn/despawn person   [S] cycle skin   [B] mood/light\n" \
		+ "[C]/[X] add/remove cat   [R] randomize   [0] clear all   [ESC] quit\n" \
		+ "[T] office STATE (scummy/decent -> props bias + floor/wall swap)\n" \
		+ "[P] cycle prop   [LMB] place on grid   [RMB] remove nearest   [K] clear props\n" \
		+ "feedback on current prop:  [L]ike  [J] dislike  [F]avour  [G] disfavour  [M] promote  [N] note"
	vb.add_child(_legend)

	_status = Label.new()
	_status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_status.add_theme_font_size_override("font_size", 12)
	vb.add_child(_status)

	_asset_status = Label.new()
	_asset_status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_asset_status.add_theme_font_size_override("font_size", 12)
	vb.add_child(_asset_status)

func _build_ghost() -> void:
	_ghost = Sprite2D.new()
	_ghost.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_ghost.modulate = Color(1, 1, 1, 0.45)
	_ghost.z_index = 3
	_ghost.visible = false
	_floor.add_child(_ghost)
	_refresh_ghost_texture()

func _process(_delta: float) -> void:
	# Ghost preview snaps to the tile grid under the mouse so the drop cell is obvious.
	if _ghost == null:
		return
	if _prop_pool.is_empty():
		_ghost.visible = false
		return
	_ghost.visible = true
	_ghost.position = _snap_to_grid(_floor.get_local_mouse_position())

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if not mb.pressed:
			return
		match mb.button_index:
			MOUSE_BUTTON_LEFT:
				_place_prop()
			MOUSE_BUTTON_RIGHT:
				_remove_nearest_prop(_floor.get_local_mouse_position())
			_:
				return
		_update_status()
		return
	if not (event is InputEventKey):
		return
	var ke := event as InputEventKey
	if not ke.pressed or ke.echo:
		return
	if _TAG_KEYS.has(ke.keycode):
		_tag_current(_TAG_KEYS[ke.keycode])
		_update_status()
		return
	match ke.keycode:
		KEY_1, KEY_KP_1:
			_spawn_person()
		KEY_2, KEY_KP_2:
			_despawn_person()
		KEY_S:
			_cycle_skin()
		KEY_C:
			_add_cat()
		KEY_X:
			_remove_cat()
		KEY_B:
			_cycle_mood()
		KEY_T:
			_cycle_state()
		KEY_P:
			_cycle_prop()
		KEY_K:
			_clear_props()
		KEY_R:
			_randomize()
		KEY_0, KEY_KP_0, KEY_BACKSPACE, KEY_DELETE:
			_clear_all()
		KEY_ESCAPE:
			get_tree().quit()
		_:
			return
	_update_status()

# --- People -----------------------------------------------------------------
func _spawn_person() -> void:
	if _roster.size() >= MAX_PEOPLE:
		return
	_roster.append(_make_person(_next_id))
	_next_id += 1
	_push_roster()

# Build one employee snapshot dict with a randomised mood so the roster shows a
# mix of FSM states (working / walking-drift / idle-disengaged / stressed).
func _make_person(id: int) -> Dictionary:
	var d := {
		"id": id,
		"name": _NAME_POOL[id % _NAME_POOL.size()],
		"specialization": _SPEC_POOL[_rng.randi() % _SPEC_POOL.size()],
		"burnout": 12.0,
		"loyalty": 65,
		"assigned": true,
		"unmanaged": false,
	}
	match _rng.randi() % 4:
		0:
			pass                                  # working
		1:
			d["unmanaged"] = true                 # walking / drifting
		2:
			d["loyalty"] = 8                       # idle / disengaged
		_:
			d["burnout"] = 92.0                    # stressed
	return d

func _despawn_person() -> void:
	if _roster.is_empty():
		return
	_roster.pop_back()
	_push_roster()

func _push_roster() -> void:
	_floor.set_roster(_roster)

# --- Skins ------------------------------------------------------------------
func _cycle_skin() -> void:
	_skin_idx = (_skin_idx + 1) % _skins.size()
	_apply_skin(_skin_idx)

func _apply_skin(idx: int) -> void:
	_skin_idx = idx
	var s: Dictionary = _skins[idx]
	match String(s.get("kind", "")):
		"art":
			_floor.set_sprite_frames(RealSpriteFrames)
			_floor.set_tier(1)
		"color":
			var frames: SpriteFrames = EmployeeSpriteScript._build_placeholder_frames(s["body"], HAT)
			_floor.set_sprite_frames(frames)
			_floor.set_tier(1)
		_:
			_floor.set_tier(0)                     # "blob"

# --- Mood / lighting --------------------------------------------------------
func _cycle_mood() -> void:
	_mood_idx = (_mood_idx + 1) % _moods.size()
	_apply_mood(_mood_idx)

func _apply_mood(idx: int) -> void:
	_mood_idx = idx
	_floor.modulate = _moods[idx]["tint"]

# --- Office STATE (prototype "reflects game state") -------------------------
func _cycle_state() -> void:
	_apply_state((_state_idx + 1) % _states.size())

func _apply_state(idx: int) -> void:
	_state_idx = idx
	var st: Dictionary = _states[idx]
	# 1) bias the prop pool toward this state (neutral props always kept).
	_rebuild_prop_pool()
	# 2) swap floor + wall tilesets to the matching promoted tileset, if we have one.
	var floor_tex := _tileset_tile_for(String(st.get("floor_key", "")))
	var wall_tex := _tileset_tile_for(String(st.get("wall_key", "")))
	# Additive dev hooks (default null restores built-in look for the live integration).
	_floor.set_floor_tile_texture(floor_tex)
	_floor.set_wall_strip_texture(wall_tex)

# Find a promoted tileset whose id contains `key`, crop its Wang base tile, upscale,
# and return a tileable texture. Returns null if no promoted tileset matched.
func _tileset_tile_for(key: String) -> Texture2D:
	if key == "":
		return null
	for a in _promoted.get("tilesets", []):
		if String(a.get("id", "")).findn(key) != -1:
			return _wang_base_tile(a.get("tex", null))
	return null

func _wang_base_tile(tex: Texture2D) -> Texture2D:
	if tex == null:
		return null
	var img: Image = tex.get_image()
	if img == null:
		return null
	var r := WANG_BASE_REGION
	if r.position.x + r.size.x <= img.get_width() and r.position.y + r.size.y <= img.get_height():
		img = img.get_region(r)
	# else: atlas smaller than expected -- just tile the whole (small) image.
	img.resize(img.get_width() * TILE_UPSCALE, img.get_height() * TILE_UPSCALE, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(img)

# --- Props (placeable, grid-snapped) ----------------------------------------
# Rebuild the offered prop pool for the current state: props whose id matches the
# state's bias keywords PLUS state-neutral props (matching no state keyword at all).
func _rebuild_prop_pool() -> void:
	var st: Dictionary = _states[_state_idx]
	var bias: Array = st.get("bias", [])
	_prop_pool.clear()
	for a in _promoted.get("props", []):
		var id_l := String(a.get("id", "")).to_lower()
		var neutral := true
		var matches_state := false
		for kw in _STATE_KEYWORDS:
			if id_l.find(kw) != -1:
				neutral = false
				if kw in bias:
					matches_state = true
		if neutral or matches_state:
			_prop_pool.append(a)
	if _prop_idx >= _prop_pool.size():
		_prop_idx = 0
	_refresh_ghost_texture()

func _cycle_prop() -> void:
	if _prop_pool.is_empty():
		return
	_prop_idx = (_prop_idx + 1) % _prop_pool.size()
	_refresh_ghost_texture()

func _current_prop() -> Dictionary:
	if _prop_pool.is_empty() or _prop_idx >= _prop_pool.size():
		return {}
	return _prop_pool[_prop_idx]

func _refresh_ghost_texture() -> void:
	if _ghost == null:
		return
	var p := _current_prop()
	_ghost.texture = p.get("tex", null) if not p.is_empty() else null
	if _ghost.texture != null:
		_ghost.scale = _prop_scale(_ghost.texture)

func _prop_scale(tex: Texture2D) -> Vector2:
	var h := tex.get_size().y
	var s := (PROP_TARGET_H / h) if h > 0.0 else 1.0
	return Vector2(s, s)

func _place_prop() -> void:
	var p := _current_prop()
	if p.is_empty() or _placed_props.size() >= MAX_PLACED:
		return
	var tex: Texture2D = p.get("tex", null)
	if tex == null:
		return
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	spr.scale = _prop_scale(tex)
	spr.position = _snap_to_grid(_floor.get_local_mouse_position())
	spr.z_index = 2
	spr.set_meta("asset_id", String(p.get("id", "")))
	_floor.add_child(spr)
	_placed_props.append(spr)

func _remove_nearest_prop(at: Vector2) -> void:
	if _placed_props.is_empty():
		return
	var best := -1
	var best_d := INF
	for i in range(_placed_props.size()):
		var spr = _placed_props[i]
		if not is_instance_valid(spr):
			continue
		var d: float = spr.position.distance_to(at)
		if d < best_d:
			best_d = d
			best = i
	if best >= 0:
		var spr = _placed_props[best]
		if is_instance_valid(spr):
			spr.queue_free()
		_placed_props.remove_at(best)

func _clear_props() -> void:
	for spr in _placed_props:
		if is_instance_valid(spr):
			spr.queue_free()
	_placed_props.clear()

func _snap_to_grid(pos: Vector2) -> Vector2:
	return Vector2(
		floor(pos.x / GRID) * GRID + GRID * 0.5,
		floor(pos.y / GRID) * GRID + GRID * 0.5)

# --- In-context feedback ----------------------------------------------------
# Tag the CURRENT (focused) prop and persist to <art_source>/sandbox_feedback.json.
# Tags accumulate as a set; "note" appends a timestamped marker to a notes array
# (free-text notes would need a focus-stealing LineEdit -- deferred, see PR notes).
func _tag_current(tag: String) -> void:
	var p := _current_prop()
	if p.is_empty():
		return
	var id := String(p.get("id", ""))
	if not _feedback.has(id):
		_feedback[id] = {"tags": [], "notes": []}
	var rec: Dictionary = _feedback[id]
	if tag == "note":
		var notes: Array = rec.get("notes", [])
		notes.append("noted " + Time.get_datetime_string_from_system())
		rec["notes"] = notes
	else:
		var tags: Array = rec.get("tags", [])
		if not (tag in tags):
			tags.append(tag)
		rec["tags"] = tags
	rec["updated"] = Time.get_datetime_string_from_system()
	_feedback[id] = rec
	_save_feedback()

func _tags_for(id: String) -> String:
	if not _feedback.has(id):
		return "-"
	var rec: Dictionary = _feedback[id]
	var parts: Array = []
	for t in rec.get("tags", []):
		parts.append(String(t))
	var n: int = rec.get("notes", []).size()
	if n > 0:
		parts.append("%dx note" % n)
	return "-" if parts.is_empty() else ", ".join(parts)

# --- Cats -------------------------------------------------------------------
func _add_cat() -> void:
	if _cats.size() >= MAX_CATS:
		return
	var cat := SandboxCat.new()
	cat.color = _cat_palette[_cat_color_idx % _cat_palette.size()]
	_cat_color_idx += 1
	var b := _floor_bounds()
	cat.position = Vector2(
		_rng.randf_range(b.position.x, b.end.x),
		_rng.randf_range(b.position.y, b.end.y))
	_floor.add_child(cat)
	_cats.append(cat)

func _remove_cat() -> void:
	if _cats.is_empty():
		return
	var cat = _cats.pop_back()
	if is_instance_valid(cat):
		cat.queue_free()

func _floor_bounds() -> Rect2:
	var s := _floor.size
	if s.x < 40.0 or s.y < 40.0:
		s = Vector2(360, 260)
	return Rect2(Vector2(16, 16), s - Vector2(32, 32))

# --- Bulk toys --------------------------------------------------------------
func _randomize() -> void:
	_clear_all()
	_apply_skin(_rng.randi() % _skins.size())
	_apply_mood(_rng.randi() % _moods.size())
	_apply_state(_rng.randi() % _states.size())
	var n := _rng.randi_range(4, 9)
	for _i in range(n):
		_spawn_person()
	var c := _rng.randi_range(1, 3)
	for _j in range(c):
		_add_cat()

func _clear_all() -> void:
	_roster.clear()
	_push_roster()
	for cat in _cats:
		if is_instance_valid(cat):
			cat.queue_free()
	_cats.clear()
	_clear_props()

func _update_status() -> void:
	if _status == null:
		return
	_status.text = "skin: %s   |   people: %d   |   cats: %d   |   mood: %s" % [
		_skins[_skin_idx]["name"], _roster.size(), _cats.size(), _moods[_mood_idx]["name"]]
	if _asset_status == null:
		return
	var cur := _current_prop()
	var cur_line: String
	if cur.is_empty():
		cur_line = "current prop: (none -- %s)" % _load_report
	else:
		var id := String(cur.get("id", ""))
		cur_line = "current prop: %s  [%s]" % [id.get_file(), _tags_for(id)]
	_asset_status.text = "state: %s   |   props offered: %d   |   placed: %d\n%s\nloaded: %s" % [
		_states[_state_idx]["name"], _prop_pool.size(), _placed_props.size(), cur_line, _load_report]

# ===========================================================================
# PROMOTED-ASSET LOADER (from art_source, OUTSIDE res://; absolute-path I/O).
# ===========================================================================

# art_source sits one level ABOVE the Godot project dir. globalize_path("res://")
# returns the absolute project dir; simplify_path resolves the ".." segment.
func _compute_art_root() -> String:
	var res_abs := ProjectSettings.globalize_path("res://")
	return (res_abs + "/../art_source").simplify_path()

# Populate _promoted (category -> Array of {id, abs, tex}). Primary source is
# promote_list.txt; fallback is pixellab_verdicts.json; either absent -> empty pool.
func _load_promoted() -> void:
	_promoted = {}
	var counts := {}          # category -> [found, loaded]
	if not DirAccess.dir_exists_absolute(_art_root):
		_load_report = "art_source not found at %s" % _art_root
		push_warning("[office_sandbox] " + _load_report)
		return
	var entries: Array = _read_promote_list()          # [{rel, category, subtype}, ...]
	var source := "promote_list.txt"
	if entries.is_empty():
		entries = _read_verdicts_promoted()
		source = "pixellab_verdicts.json"
	if entries.is_empty():
		_load_report = "no promoted assets found (place promote_list.txt / pixellab_verdicts.json in art_source)"
		push_warning("[office_sandbox] " + _load_report)
		return
	for e in entries:
		var rel := String(e.get("rel", ""))
		if rel == "":
			continue
		var cat := String(e.get("category", "misc")).to_lower()
		if not counts.has(cat):
			counts[cat] = [0, 0]
		counts[cat][0] += 1
		var abs_path := (_art_root + "/" + rel).simplify_path()
		var tex := _load_texture(abs_path)
		if tex == null:
			continue                                    # missing/unreadable file -> skip + count
		counts[cat][1] += 1
		if not _promoted.has(cat):
			_promoted[cat] = []
		_promoted[cat].append({
			"id": rel, "abs": abs_path, "tex": tex,
			"subtype": String(e.get("subtype", "")),
		})
	# Build the human-readable report ("props 18/20, tilesets 5/5") from source X.
	var bits: Array = []
	for cat in counts.keys():
		bits.append("%s %d/%d" % [cat, counts[cat][1], counts[cat][0]])
	_load_report = ("via %s: " % source) + (", ".join(bits) if not bits.is_empty() else "0")
	print("[office_sandbox] promoted assets ", _load_report)

func _load_texture(abs_path: String) -> Texture2D:
	if not FileAccess.file_exists(abs_path):
		return null
	var img := Image.new()
	if img.load(abs_path) != OK:
		return null
	return ImageTexture.create_from_image(img)

# Parse promote_list.txt: lines are either "# category/subtype" headers or a path
# relative to art_source. Blank lines ignored. Returns [] if the file is absent.
func _read_promote_list() -> Array:
	var path := _art_root + "/promote_list.txt"
	if not FileAccess.file_exists(path):
		return []
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return []
	var text := f.get_as_text()
	f.close()
	var out: Array = []
	var cat := "misc"
	var sub := ""
	for raw in text.split("\n"):
		var line := raw.strip_edges()
		if line == "":
			continue
		if line.begins_with("#"):
			var hdr := line.substr(1).strip_edges()
			var parts := hdr.split("/", false)
			cat = parts[0].strip_edges() if parts.size() > 0 else "misc"
			sub = parts[1].strip_edges() if parts.size() > 1 else ""
			continue
		out.append({"rel": line, "category": cat, "subtype": sub})
	return out

# Fallback: pixellab_verdicts.json. Accepts either {key: [tags...]} or
# {key: {"tags": [...]}}; keeps keys whose tag array contains "promote". Category is
# inferred from the path (props/tilesets/misc) since the verdicts file has no headers.
func _read_verdicts_promoted() -> Array:
	var path := _art_root + "/pixellab_verdicts.json"
	if not FileAccess.file_exists(path):
		return []
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return []
	var text := f.get_as_text()
	f.close()
	var data = JSON.parse_string(text)
	if not (data is Dictionary):
		return []
	var out: Array = []
	for key in data.keys():
		var v = data[key]
		var tags: Array = []
		if v is Array:
			tags = v
		elif v is Dictionary:
			tags = v.get("tags", [])
		if "promote" in tags:
			out.append({"rel": String(key), "category": _infer_category(String(key)), "subtype": ""})
	return out

func _infer_category(rel: String) -> String:
	var low := rel.to_lower()
	if low.find("tileset") != -1 or low.find("floor") != -1 or low.find("wall") != -1:
		return "tilesets"
	if low.find("prop") != -1:
		return "props"
	return "misc"

# ===========================================================================
# FEEDBACK PERSISTENCE (<art_source>/sandbox_feedback.json; merges on load).
# ===========================================================================
func _feedback_path() -> String:
	return _art_root + "/sandbox_feedback.json"

func _load_feedback() -> void:
	_feedback = {}
	var path := _feedback_path()
	if not FileAccess.file_exists(path):
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	if data is Dictionary:
		_feedback = data

func _save_feedback() -> void:
	if not DirAccess.dir_exists_absolute(_art_root):
		push_warning("[office_sandbox] cannot save feedback: art_source missing")
		return
	var f := FileAccess.open(_feedback_path(), FileAccess.WRITE)
	if f == null:
		push_warning("[office_sandbox] cannot open sandbox_feedback.json for write")
		return
	f.store_string(JSON.stringify(_feedback, "  "))
	f.close()

# ---------------------------------------------------------------------------
# Self-contained procedural cat. Wanders inside its parent's bounds and draws a
# small pixel-ish cat in _draw(). Cosmetic-only, private RNG; touches no game
# state. Kept an inner class so the toy needs no new shared files or cat art
# import (the pixellab pixel-cats live only in art_source -- see the PR notes).
# ---------------------------------------------------------------------------
class SandboxCat extends Node2D:
	var color: Color = Color(0.2, 0.2, 0.2)
	var speed: float = 30.0
	var _target: Vector2 = Vector2.ZERO
	var _bounds: Rect2 = Rect2(0, 0, 320, 220)
	var _pause: float = 0.0
	var _rng := RandomNumberGenerator.new()

	func _ready() -> void:
		_rng.randomize()
		_target = position
		z_index = 5
		texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST

	func _process(delta: float) -> void:
		var p := get_parent()
		if p is Control:
			_bounds = Rect2(Vector2(16, 16), (p as Control).size - Vector2(32, 32))
		if _pause > 0.0:
			_pause -= delta
		elif position.distance_to(_target) <= 4.0:
			_pick_target()
			_pause = _rng.randf_range(0.5, 2.5)
		else:
			position = position.move_toward(_target, speed * delta)
		position.x = clampf(position.x, _bounds.position.x, _bounds.end.x)
		position.y = clampf(position.y, _bounds.position.y, _bounds.end.y)
		queue_redraw()

	func _pick_target() -> void:
		_target = Vector2(
			_rng.randf_range(_bounds.position.x, _bounds.end.x),
			_rng.randf_range(_bounds.position.y, _bounds.end.y))

	func _draw() -> void:
		var dark := color.darkened(0.35)
		draw_line(Vector2(-8, 0), Vector2(-13, -6), dark, 2.0)                       # tail
		draw_circle(Vector2(0, 0), 7.0, color)                                       # body
		draw_circle(Vector2(6, -4), 4.5, color)                                      # head
		draw_colored_polygon(PackedVector2Array([                                     # left ear
			Vector2(3.0, -8.0), Vector2(4.5, -11.0), Vector2(6.5, -8.0)]), dark)
		draw_colored_polygon(PackedVector2Array([                                     # right ear
			Vector2(7.0, -8.0), Vector2(9.0, -11.0), Vector2(10.0, -8.0)]), dark)
		draw_circle(Vector2(5.0, -4.5), 0.9, Color(0.15, 0.9, 0.4))                   # eyes
		draw_circle(Vector2(8.0, -4.5), 0.9, Color(0.15, 0.9, 0.4))

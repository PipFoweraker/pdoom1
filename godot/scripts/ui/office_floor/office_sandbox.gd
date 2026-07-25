extends Control
## OFFICE SANDBOX v3 -- a standalone DEV TOY for the office-floor view (Pip: open
## this in the evening and play). v3 adds SCALING, a POPULATE-UP sequence with simple
## space/placement logic, REAL cat walk-cycles loaded from art_source, and two dev-only
## prototypes: doom-glow on cats + a transparent-overlay (poster-on-wall) compositing POC.
##
## Everything v2 shipped still works: promoted-asset loader, prop placement, skin/mood
## cycling, scummy/decent office STATE, and in-context feedback.
##
## This is the prototyping ground for the future runtime "office reflects game state"
## asset system (see docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md). It is a
## DEV TOOL and NEVER ships to players.
##
## MECHANICS-SAFE / W3-SAFE (by construction): PURE COMPOSITION. It instantiates the
## existing OfficeFloor view (res://scenes/ui/office_floor/office_floor.tscn) and drives
## it through its EXISTING public API only, plus the two ADDITIVE cosmetic dev hooks that
## v2 added (OfficeFloor.set_floor_tile_texture / set_wall_strip_texture -- both
## backward-compatible no-ops for the live WATCH integration). v3 adds NO new hooks to
## OfficeFloor or EmployeeSprite: all scaling / doom-glow / overlays are applied by the
## sandbox onto nodes it owns or onto sprite NODE transforms (never touching the sprites'
## internal art scale, movement, or game state). There is NO game state, no economy, no
## win/lose, no touching of employee_fsm/employee_sprite/watch_screen/main_ui/GameState.
##
## PROMOTED-ASSET + CAT-WALK LOADING: art_source/ lives OUTSIDE the Godot project (NOT
## res://). Props come from art_source/promote_list.txt (v2). Cat walk-cycles are loaded
## DIRECTLY from known art_source cat-walk dirs by ABSOLUTE path via Image.load() -- they
## are git-tracked, so they resolve in any checkout; if art_source is absent the loader
## degrades cleanly (empty prop pool + procedural cats) and the toy still runs.

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

# --- v3 tuning --------------------------------------------------------------
# Global OCCUPANT scale default. The v2 sprites drew at EmployeeSprite.SPRITE_SCALE (2.0);
# on a small floor that reads too big ("spawn one person, it's relatively huge"). 0.65 makes
# a spawned worker a sane fraction of the floor. Tunable live with [-]/[=]. Applied as a NODE
# transform scale onto occupants (people/cats/props) -- never touches the sprites' art scale.
const OCCUPANT_SCALE_DEFAULT := 0.65
const OCCUPANT_SCALE_MIN := 0.2
const OCCUPANT_SCALE_MAX := 3.0
const OCCUPANT_SCALE_STEP := 1.12       # multiplicative per keypress
const PER_SPRITE_STEP := 1.1            # per-selected-sprite scale step
const PER_SPRITE_MIN := 0.25
const PER_SPRITE_MAX := 4.0

# POPULATE-UP sequence: cumulative TARGET totals per press (level 1..10). Level 0 = empty.
# Each press advances one stage (people via set_roster, cats wandering, furniture on walls).
const _POP_STAGES := [
	{"people": 1,  "cats": 0, "furn": 2},
	{"people": 3,  "cats": 1, "furn": 4},
	{"people": 5,  "cats": 1, "furn": 6},
	{"people": 7,  "cats": 2, "furn": 8},
	{"people": 9,  "cats": 2, "furn": 10},
	{"people": 12, "cats": 3, "furn": 13},
	{"people": 15, "cats": 3, "furn": 16},
	{"people": 18, "cats": 4, "furn": 19},
	{"people": 21, "cats": 5, "furn": 22},
	{"people": 24, "cats": 6, "furn": 26},
]

# Cat walk-cycle source dirs (relative to art_source). Each holds walk_<dir>_<n>.png for
# dir in {south,east,north,west}. These are git-tracked so they resolve in any checkout.
const _CAT_WALK_DIRS: Array[String] = [
	"pixellab_2026-07-16/cat_walk_cat1",
	"pixellab_2026-07-16/cat_walk_cat2",
]
# Cat art sets that exist as rotation-only (static) frames and STILL NEED walk-cycles
# generated (pixellab) before they can become real walkers. Reported on-screen/stdout.
const _CAT_SETS_NEEDING_WALKS := ["cat_black", "cat_tabby", "cat_eldritch(x4)", "cat_purple(x4)"]

const DOOM_STEP := 0.1

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

# Cat coat colours cycled as procedural cats are added (fallback only; real cats use art).
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

# Placeholder furniture kinds (procedural; used by POPULATE so the placement logic is
# demonstrable even in a fresh checkout with no promoted props). {id: [w,h, color]}.
const _FURN_KINDS := {
	"desk":    [44, 22, Color(0.42, 0.30, 0.20)],
	"cabinet": [24, 38, Color(0.55, 0.56, 0.60)],
	"plant":   [22, 30, Color(0.24, 0.55, 0.30)],
	"server":  [26, 40, Color(0.18, 0.20, 0.24)],
	"printer": [30, 24, Color(0.70, 0.70, 0.72)],
}

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
var _placed_props: Array = []              # Sprite2D children of _floor (manual placement)
var _ghost: Sprite2D = null                # translucent placement preview following the mouse
var _feedback: Dictionary = {}             # asset_id -> {"tags":[...], "notes":[...]}

# --- v3 state ---------------------------------------------------------------
var _occupant_scale: float = OCCUPANT_SCALE_DEFAULT
var _pop_level: int = 0
var _furniture: Array = []                 # Sprite2D furniture placed by POPULATE (wall-affinity)
var _occupied_cells: Dictionary = {}       # str(cell centre) -> true (furniture no-overlap)
var _cat_frame_sets: Array = []            # [{name, frames}] real walk-cycle SpriteFrames
var _cat_walk_report: String = ""
var _doom_level: float = 0.0
var _overlay_mode: bool = false            # false = prop placement, true = poster overlay
var _overlays: Array = []                  # Sprite2D transparent wall overlays (stackable)
var _poster_texs: Array = []               # placeholder/promoted poster textures
var _poster_idx: int = 0
var _marker: SandboxMarker = null          # highlights the per-sprite / overlay selection target

func _ready() -> void:
	_rng.randomize()
	set_anchors_preset(Control.PRESET_FULL_RECT)

	_floor = OfficeFloorScene.instantiate()
	_floor.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_floor)

	# Load promoted assets + cat walk-cycles + any existing feedback BEFORE the overlay so
	# the legend/status can report counts. All degrade to empty if the source files absent.
	_art_root = _compute_art_root()
	_load_feedback()
	_load_promoted()
	_load_cat_walks()
	_build_poster_pool()
	_rebuild_prop_pool()

	_build_overlay()
	_build_ghost()
	_build_marker()

	# Start with the real-art skin and a few people so it's alive on open.
	_apply_skin(0)
	_apply_mood(0)
	_apply_state(0)
	for _i in range(5):
		_spawn_person()
	_add_cat()
	_apply_occupant_scale()
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
	_legend.text = "OFFICE SANDBOX v3  --  dev toy (no game state)\n" \
		+ "[1]/[2] spawn/despawn person   [S] skin   [B] mood   [C]/[X] add/remove cat   [R] randomize   [0] clear   [ESC] quit\n" \
		+ "SCALE:  [-]/[=] all occupants   [,]/[.] the sprite under the cursor   |   POPULATE:  [U] up a stage   [I] down a stage\n" \
		+ "[T] office STATE (scummy/decent)   [P] cycle prop/poster   [LMB] place   [RMB] remove nearest   [K] clear props\n" \
		+ "DOOM-GLOW on cats:  [ [ ] decrease   [ ] ] increase   |   OVERLAY POC:  [V] toggle poster-on-wall mode   [;]/['] selected overlay opacity\n" \
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

func _build_marker() -> void:
	_marker = SandboxMarker.new()
	_marker.z_index = 6
	_marker.visible = false
	_floor.add_child(_marker)

func _process(_delta: float) -> void:
	# Ghost preview: in prop mode it snaps to the tile grid; in overlay mode it snaps to the
	# nearest wall so the poster drop target reads. Marker highlights the selection target for
	# the per-sprite scale ([,]/[.]) or the overlay opacity ([;]/[']) keys.
	var mouse := _floor.get_local_mouse_position()
	if _ghost != null:
		if _overlay_mode:
			_ghost.visible = _ghost.texture != null
			_ghost.position = _snap_to_wall(mouse)
		elif _prop_pool.is_empty():
			_ghost.visible = false
		else:
			_ghost.visible = true
			_ghost.position = _snap_to_grid(mouse)
	if _marker != null:
		if _overlay_mode:
			var ov := _nearest_overlay(mouse)
			_marker.visible = ov != null
			if ov != null:
				_marker.position = ov.position
				_marker.radius = 26.0
		else:
			var sp := _nearest_person(mouse)
			_marker.visible = sp != null
			if sp != null:
				_marker.position = sp.position
				_marker.radius = 18.0

func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if not mb.pressed:
			return
		match mb.button_index:
			MOUSE_BUTTON_LEFT:
				if _overlay_mode:
					_place_overlay()
				else:
					_place_prop()
			MOUSE_BUTTON_RIGHT:
				if _overlay_mode:
					_remove_nearest_overlay(_floor.get_local_mouse_position())
				else:
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
		KEY_U:
			_populate_up()
		KEY_I:
			_populate_down()
		KEY_MINUS, KEY_KP_SUBTRACT:
			_nudge_occupant_scale(1.0 / OCCUPANT_SCALE_STEP)
		KEY_EQUAL, KEY_KP_ADD:
			_nudge_occupant_scale(OCCUPANT_SCALE_STEP)
		KEY_COMMA:
			_scale_nearest_person(1.0 / PER_SPRITE_STEP)
		KEY_PERIOD:
			_scale_nearest_person(PER_SPRITE_STEP)
		KEY_BRACKETLEFT:
			_nudge_doom(-DOOM_STEP)
		KEY_BRACKETRIGHT:
			_nudge_doom(DOOM_STEP)
		KEY_V:
			_toggle_overlay_mode()
		KEY_SEMICOLON:
			_nudge_overlay_opacity(-0.1)
		KEY_APOSTROPHE:
			_nudge_overlay_opacity(0.1)
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
	_apply_occupant_scale()

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
	_apply_occupant_scale()

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
	if _overlay_mode:
		_cycle_poster()
		return
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
	if _overlay_mode:
		_ghost.texture = _current_poster()
		_ghost.scale = Vector2.ONE
		return
	var p := _current_prop()
	_ghost.texture = p.get("tex", null) if not p.is_empty() else null
	if _ghost.texture != null:
		_ghost.scale = _prop_scale(_ghost.texture) * _occupant_scale

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
	var base := _prop_scale(tex)
	spr.set_meta("base_scale", base)
	spr.scale = base * _occupant_scale
	# Wall-affinity assist: if the drop point is near a wall, snap flush to it; else free grid.
	spr.position = _grid_or_wall(_floor.get_local_mouse_position())
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

# Grid-snap, but if the point is within one grid cell of a wall, snap flush to that wall
# (furniture wall-affinity for manual placement; the POPULATE placer uses walls exclusively).
func _grid_or_wall(pos: Vector2) -> Vector2:
	var b := _floor_bounds()
	var snapped := _snap_to_grid(pos)
	if pos.x - b.position.x < GRID:
		snapped.x = b.position.x + GRID * 0.5
	elif b.end.x - pos.x < GRID:
		snapped.x = b.end.x - GRID * 0.5
	if pos.y - b.position.y < GRID:
		snapped.y = b.position.y + GRID * 0.5
	elif b.end.y - pos.y < GRID:
		snapped.y = b.end.y - GRID * 0.5
	return snapped

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
# Spawn a cat. Uses a REAL loaded walk-cycle (cycling the available sets) when any exist;
# otherwise falls back to the procedural drawn cat. Both honour doom-glow + occupant scale.
func _add_cat() -> void:
	if _cats.size() >= MAX_CATS:
		return
	var cat: SandboxCatBase
	if not _cat_frame_sets.is_empty():
		var rc := RealCat.new()
		rc.setup(_cat_frame_sets[_cat_color_idx % _cat_frame_sets.size()]["frames"])
		cat = rc
	else:
		var sc := SandboxCat.new()
		sc.color = _cat_palette[_cat_color_idx % _cat_palette.size()]
		cat = sc
	_cat_color_idx += 1
	var b := _floor_bounds()
	cat.position = Vector2(
		_rng.randf_range(b.position.x, b.end.x),
		_rng.randf_range(b.position.y, b.end.y))
	_floor.add_child(cat)
	cat.scale = Vector2(_occupant_scale, _occupant_scale)
	cat.set_doom(_doom_level)
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

# --- v3: SCALING ------------------------------------------------------------
# Apply the global occupant scale (times any per-sprite multiplier held in node meta) to
# every occupant the sandbox owns: employee sprites (NODE transform only -- never the art
# scale the live view sets), cats, populate-furniture, and manually-placed props.
func _apply_occupant_scale() -> void:
	for c in _floor.get_children():
		if c is OfficeEmployeeSprite:
			var m := float((c as Node).get_meta("sb_scale_mult", 1.0))
			(c as Node2D).scale = Vector2(_occupant_scale * m, _occupant_scale * m)
	for cat in _cats:
		if is_instance_valid(cat):
			cat.scale = Vector2(_occupant_scale, _occupant_scale)
	for f in _furniture:
		if is_instance_valid(f):
			var base: Vector2 = f.get_meta("base_scale", Vector2.ONE)
			f.scale = base * _occupant_scale
	for spr in _placed_props:
		if is_instance_valid(spr):
			var base2: Vector2 = spr.get_meta("base_scale", Vector2.ONE)
			spr.scale = base2 * _occupant_scale
	_refresh_ghost_texture()

func _nudge_occupant_scale(mult: float) -> void:
	_occupant_scale = clampf(_occupant_scale * mult, OCCUPANT_SCALE_MIN, OCCUPANT_SCALE_MAX)
	_apply_occupant_scale()

func _scale_nearest_person(mult: float) -> void:
	var sp := _nearest_person(_floor.get_local_mouse_position())
	if sp == null:
		return
	var m := float(sp.get_meta("sb_scale_mult", 1.0))
	m = clampf(m * mult, PER_SPRITE_MIN, PER_SPRITE_MAX)
	sp.set_meta("sb_scale_mult", m)
	_apply_occupant_scale()

func _nearest_person(at: Vector2) -> Node2D:
	var best: Node2D = null
	var best_d := INF
	for c in _floor.get_children():
		if c is OfficeEmployeeSprite:
			var d: float = (c as Node2D).position.distance_to(at)
			if d < best_d:
				best_d = d
				best = c
	return best

# --- v3: POPULATE-UP sequence + placement logic -----------------------------
func _populate_up() -> void:
	if _pop_level >= _POP_STAGES.size():
		return
	_pop_level += 1
	_apply_pop_stage()

func _populate_down() -> void:
	if _pop_level <= 0:
		return
	_pop_level -= 1
	_apply_pop_stage()

func _apply_pop_stage() -> void:
	var want_people := 0
	var want_cats := 0
	var want_furn := 0
	if _pop_level > 0:
		var st: Dictionary = _POP_STAGES[_pop_level - 1]
		want_people = int(st["people"])
		want_cats = int(st["cats"])
		want_furn = int(st["furn"])
	# People (spread around the desks by OfficeFloor's own layout -- sane, non-overlapping).
	while _roster.size() < want_people and _roster.size() < MAX_PEOPLE:
		_roster.append(_make_person(_next_id))
		_next_id += 1
	while _roster.size() > want_people:
		_roster.pop_back()
	_push_roster()
	# Cats (wander freely).
	while _cats.size() < want_cats and _cats.size() < MAX_CATS:
		_add_cat()
	while _cats.size() > want_cats:
		_remove_cat()
	# Furniture (wall-affinity, no-overlap).
	while _furniture.size() < want_furn:
		if not _spawn_furniture():
			break
	while _furniture.size() > want_furn:
		_remove_furniture()
	_apply_occupant_scale()

# Place one furniture piece on a free perimeter (wall) grid cell. Returns false if the
# floor is full. Demonstrates the first "space logic" slice: furniture hugs walls, does
# not overlap other furniture.
func _spawn_furniture() -> bool:
	var cell := _pick_wall_cell()
	if cell == Vector2.INF:
		return false
	var kinds := _FURN_KINDS.keys()
	var kind := String(kinds[_rng.randi() % kinds.size()])
	var tex := _furniture_tex(kind)
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var base := _prop_scale(tex)
	spr.set_meta("base_scale", base)
	spr.scale = base * _occupant_scale
	spr.position = cell
	spr.z_index = 2
	spr.set_meta("cell_key", str(cell))
	_floor.add_child(spr)
	_furniture.append(spr)
	_occupied_cells[str(cell)] = true
	return true

func _remove_furniture() -> void:
	if _furniture.is_empty():
		return
	var spr = _furniture.pop_back()
	if is_instance_valid(spr):
		_occupied_cells.erase(String(spr.get_meta("cell_key", "")))
		spr.queue_free()

# Return a random unoccupied grid cell centre on the floor PERIMETER (wall-affinity). Falls
# back to any interior cell if the perimeter is full. Returns Vector2.INF if nothing free.
func _pick_wall_cell() -> Vector2:
	var b := _floor_bounds()
	var cols := int(b.size.x / GRID)
	var rows := int(b.size.y / GRID)
	if cols < 2 or rows < 2:
		return Vector2.INF
	var edge: Array = []
	var inner: Array = []
	for r in range(rows):
		for c in range(cols):
			var centre := Vector2(
				b.position.x + c * GRID + GRID * 0.5,
				b.position.y + r * GRID + GRID * 0.5)
			if _occupied_cells.has(str(centre)):
				continue
			if c == 0 or c == cols - 1 or r == 0 or r == rows - 1:
				edge.append(centre)
			else:
				inner.append(centre)
	var pool: Array = edge if not edge.is_empty() else inner
	if pool.is_empty():
		return Vector2.INF
	var chosen: Vector2 = pool[_rng.randi() % pool.size()]
	return chosen

func _furniture_tex(kind: String) -> Texture2D:
	var spec: Array = _FURN_KINDS[kind]
	var w := int(spec[0])
	var h := int(spec[1])
	var col: Color = spec[2]
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	img.fill(col)
	# simple top highlight + dark base so it reads as a solid object, not a flat rect
	img.fill_rect(Rect2i(0, 0, w, max(1, int(h * 0.18))), col.lightened(0.25))
	img.fill_rect(Rect2i(0, h - max(1, int(h * 0.14)), w, max(1, int(h * 0.14))), col.darkened(0.35))
	# 1px border
	for x in range(w):
		img.set_pixel(x, 0, col.darkened(0.5))
		img.set_pixel(x, h - 1, col.darkened(0.5))
	for y in range(h):
		img.set_pixel(0, y, col.darkened(0.5))
		img.set_pixel(w - 1, y, col.darkened(0.5))
	return ImageTexture.create_from_image(img)

# --- v3: DOOM-GLOW on cats (prototype) --------------------------------------
func _nudge_doom(d: float) -> void:
	_doom_level = clampf(_doom_level + d, 0.0, 1.0)
	for cat in _cats:
		if is_instance_valid(cat):
			cat.set_doom(_doom_level)

# --- v3: transparent OVERLAY (poster-on-wall) POC ---------------------------
# Builds the offered poster texture pool. Prefers promoted assets whose id reads like a
# poster / wall-art / decal; otherwise generates translucent placeholder posters so the
# compositing demo works with no art. Posters are placed with wall-affinity, stack on top of
# each other, and each has an independently adjustable opacity -- proving transparent-layer
# compositing (the incremental foundation a weather-through-windows feature builds on later).
func _build_poster_pool() -> void:
	_poster_texs.clear()
	for a in _promoted.get("props", []):
		var id_l := String(a.get("id", "")).to_lower()
		if id_l.find("poster") != -1 or id_l.find("wall_art") != -1 or id_l.find("decal") != -1 or id_l.find("art") != -1:
			var tex = a.get("tex", null)
			if tex != null:
				_poster_texs.append(tex)
	if _poster_texs.is_empty():
		var hues: Array[Color] = [Color(0.85, 0.30, 0.35), Color(0.30, 0.55, 0.85), Color(0.35, 0.75, 0.45), Color(0.80, 0.70, 0.30)]
		for hue in hues:
			_poster_texs.append(_make_poster_tex(hue))

func _make_poster_tex(hue: Color) -> Texture2D:
	var w := 40
	var h := 56
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	img.fill(hue.lightened(0.1))
	# frame border
	var border := hue.darkened(0.5)
	for x in range(w):
		img.set_pixel(x, 0, border)
		img.set_pixel(x, 1, border)
		img.set_pixel(x, h - 1, border)
		img.set_pixel(x, h - 2, border)
	for y in range(h):
		img.set_pixel(0, y, border)
		img.set_pixel(1, y, border)
		img.set_pixel(w - 1, y, border)
		img.set_pixel(w - 2, y, border)
	# a diagonal + a band so overlap/transparency is legible when stacked
	for i in range(min(w, h)):
		img.set_pixel(clampi(i, 0, w - 1), clampi(i, 0, h - 1), hue.darkened(0.25))
	img.fill_rect(Rect2i(4, int(h * 0.6), w - 8, 4), hue.darkened(0.3))
	return ImageTexture.create_from_image(img)

func _current_poster() -> Texture2D:
	if _poster_texs.is_empty():
		return null
	return _poster_texs[_poster_idx % _poster_texs.size()]

func _cycle_poster() -> void:
	if _poster_texs.is_empty():
		return
	_poster_idx = (_poster_idx + 1) % _poster_texs.size()
	_refresh_ghost_texture()

func _toggle_overlay_mode() -> void:
	_overlay_mode = not _overlay_mode
	_refresh_ghost_texture()

func _place_overlay() -> void:
	var tex := _current_poster()
	if tex == null:
		return
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	spr.position = _snap_to_wall(_floor.get_local_mouse_position())
	# z_index 1 = on the wall, behind the people (z 0) that stand lower on the floor. Later
	# overlays get a higher z so a stack composites front-to-back visibly.
	spr.z_index = 1 + (_overlays.size() % 4)
	var op := 0.7
	spr.modulate = Color(1, 1, 1, op)
	spr.set_meta("opacity", op)
	_floor.add_child(spr)
	_overlays.append(spr)

func _remove_nearest_overlay(at: Vector2) -> void:
	var ov := _nearest_overlay(at)
	if ov == null:
		return
	_overlays.erase(ov)
	ov.queue_free()

func _nearest_overlay(at: Vector2) -> Sprite2D:
	var best: Sprite2D = null
	var best_d := INF
	for spr in _overlays:
		if not is_instance_valid(spr):
			continue
		var d: float = spr.position.distance_to(at)
		if d < best_d:
			best_d = d
			best = spr
	return best

func _nudge_overlay_opacity(d: float) -> void:
	var ov := _nearest_overlay(_floor.get_local_mouse_position())
	if ov == null:
		return
	var op := clampf(float(ov.get_meta("opacity", 0.7)) + d, 0.05, 1.0)
	ov.set_meta("opacity", op)
	ov.modulate = Color(1, 1, 1, op)

# Snap a point to the nearest wall of the floor bounds (poster wall-affinity). Posters sit
# just inside the wall so they read as mounted on it.
func _snap_to_wall(p: Vector2) -> Vector2:
	var b := _floor_bounds()
	var inset := 20.0
	var dl := p.x - b.position.x
	var dr := b.end.x - p.x
	var dt := p.y - b.position.y
	var db := b.end.y - p.y
	var m := minf(minf(dl, dr), minf(dt, db))
	if m == dt:
		return Vector2(clampf(p.x, b.position.x + inset, b.end.x - inset), b.position.y + inset)
	elif m == db:
		return Vector2(clampf(p.x, b.position.x + inset, b.end.x - inset), b.end.y - inset)
	elif m == dl:
		return Vector2(b.position.x + inset, clampf(p.y, b.position.y + inset, b.end.y - inset))
	return Vector2(b.end.x - inset, clampf(p.y, b.position.y + inset, b.end.y - inset))

func _clear_overlays() -> void:
	for spr in _overlays:
		if is_instance_valid(spr):
			spr.queue_free()
	_overlays.clear()

func _clear_furniture() -> void:
	for spr in _furniture:
		if is_instance_valid(spr):
			spr.queue_free()
	_furniture.clear()
	_occupied_cells.clear()

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
	_apply_occupant_scale()

func _clear_all() -> void:
	_roster.clear()
	_push_roster()
	for cat in _cats:
		if is_instance_valid(cat):
			cat.queue_free()
	_cats.clear()
	_clear_props()
	_clear_furniture()
	_clear_overlays()
	_pop_level = 0

func _update_status() -> void:
	if _status == null:
		return
	_status.text = "skin: %s   |   people: %d   |   cats: %d   |   mood: %s   |   scale: %d%%   |   populate: %d/%d" % [
		_skins[_skin_idx]["name"], _roster.size(), _cats.size(), _moods[_mood_idx]["name"],
		int(round(_occupant_scale * 100.0)), _pop_level, _POP_STAGES.size()]
	if _asset_status == null:
		return
	var mode_line := "MODE: %s   |   doom-glow: %d%%   |   overlays: %d" % [
		("OVERLAY (poster on wall)" if _overlay_mode else "prop placement"),
		int(round(_doom_level * 100.0)), _overlays.size()]
	var cur := _current_prop()
	var cur_line: String
	if _overlay_mode:
		cur_line = "current poster: %d/%d (%s)" % [
			(_poster_idx % max(1, _poster_texs.size())) + 1, _poster_texs.size(),
			"promoted" if _has_promoted_posters() else "placeholder"]
	elif cur.is_empty():
		cur_line = "current prop: (none -- %s)" % _load_report
	else:
		var id := String(cur.get("id", ""))
		cur_line = "current prop: %s  [%s]" % [id.get_file(), _tags_for(id)]
	_asset_status.text = "state: %s   |   props offered: %d   |   placed: %d   |   furniture: %d\n%s\n%s\ncats: %s\nloaded: %s" % [
		_states[_state_idx]["name"], _prop_pool.size(), _placed_props.size(), _furniture.size(),
		mode_line, cur_line, _cat_walk_report, _load_report]

func _has_promoted_posters() -> bool:
	for a in _promoted.get("props", []):
		var id_l := String(a.get("id", "")).to_lower()
		if id_l.find("poster") != -1 or id_l.find("wall_art") != -1 or id_l.find("decal") != -1:
			return true
	return false

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
		# Expected on a fresh checkout run outside Pip's working copy -- degrade cleanly.
		_load_report = "art_source not found at %s" % _art_root
		print("[office_sandbox] " + _load_report)
		return
	var entries: Array = _read_promote_list()          # [{rel, category, subtype}, ...]
	var source := "promote_list.txt"
	if entries.is_empty():
		entries = _read_verdicts_promoted()
		source = "pixellab_verdicts.json"
	if entries.is_empty():
		# Expected when promote_list.txt / pixellab_verdicts.json are absent (they are
		# untracked, so live only in Pip's working copy) -- degrade to an empty prop pool.
		_load_report = "no promoted assets found (place promote_list.txt / pixellab_verdicts.json in art_source)"
		print("[office_sandbox] " + _load_report)
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
# CAT WALK-CYCLE LOADER (real pixellab frames from art_source; absolute-path I/O).
# ===========================================================================
# For each known cat-walk dir, assemble a SpriteFrames with walk_<dir> clips (+ an idle
# frame). Cats spawned afterwards use these; sets without walk frames stay procedural and
# are flagged. Degrades cleanly (empty -> all procedural) when art_source is absent.
func _load_cat_walks() -> void:
	_cat_frame_sets.clear()
	var loaded: Array = []
	if DirAccess.dir_exists_absolute(_art_root):
		for rel in _CAT_WALK_DIRS:
			var d := (_art_root + "/" + rel).simplify_path()
			if not DirAccess.dir_exists_absolute(d):
				continue
			var sf := _build_cat_frames(d)
			if sf != null:
				_cat_frame_sets.append({"name": rel.get_file(), "frames": sf})
				loaded.append(rel.get_file())
	if loaded.is_empty():
		_cat_walk_report = "REAL cat walkers: none (art_source absent) -- using procedural cats. Generate walk frames (pixellab) for: " + ", ".join(_CAT_SETS_NEEDING_WALKS)
	else:
		_cat_walk_report = "REAL cat walkers: %s   |   still NEED walk-frames (pixellab): %s" % [
			", ".join(loaded), ", ".join(_CAT_SETS_NEEDING_WALKS)]
	print("[office_sandbox] ", _cat_walk_report)

# Assemble a walk-cycle SpriteFrames from <dir>/walk_<facing>_<n>.png sequences.
# Clips: walk_south / walk_east / walk_north / walk_west (looping) + idle (south frame 0).
# Returns null if no frames were found.
func _build_cat_frames(dir_abs: String) -> SpriteFrames:
	var sf := SpriteFrames.new()
	var first := true
	var made_any := false
	for facing: String in ["south", "east", "north", "west"]:
		var clip := "walk_" + facing
		var i := 0
		var added := 0
		while true:
			var p := "%s/walk_%s_%d.png" % [dir_abs, facing, i]
			if not FileAccess.file_exists(p):
				break
			var tex := _load_texture(p)
			if tex == null:
				break
			if first:
				sf.rename_animation("default", clip)
				first = false
			elif not sf.has_animation(clip):
				sf.add_animation(clip)
			sf.set_animation_loop(clip, true)
			sf.set_animation_speed(clip, 10.0)
			sf.add_frame(clip, tex)
			added += 1
			i += 1
		if added > 0:
			made_any = true
	if not made_any:
		return null
	var south0 := _load_texture(dir_abs + "/walk_south_0.png")
	if south0 != null:
		if not sf.has_animation("idle"):
			sf.add_animation("idle")
		sf.set_animation_loop("idle", true)
		sf.set_animation_speed("idle", 1.0)
		sf.add_frame("idle", south0)
	return sf

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

# ===========================================================================
# CATS. Base wander + doom-glow shared by the procedural cat (SandboxCat, drawn) and the
# real walk-cycle cat (RealCat, AnimatedSprite2D). Cosmetic-only, private RNG; touches no
# game state. Inner classes so the toy needs no new shared files.
# ===========================================================================
class SandboxCatBase extends Node2D:
	var color: Color = Color(0.2, 0.2, 0.2)
	var speed: float = 30.0
	var _target: Vector2 = Vector2.ZERO
	var _bounds: Rect2 = Rect2(0, 0, 320, 220)
	var _pause: float = 0.0
	var _doom: float = 0.0
	var _t: float = 0.0
	var _rng := RandomNumberGenerator.new()
	var _glow: Sprite2D = null
	static var _glow_tex: Texture2D = null

	func _ready() -> void:
		_rng.randomize()
		_target = position
		z_index = 5
		texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_glow = Sprite2D.new()
		_glow.texture = _get_glow_tex()
		var mat := CanvasItemMaterial.new()
		mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		_glow.material = mat
		_glow.z_index = -1                # behind the cat body
		_glow.modulate = Color(1.0, 0.25, 0.15, 0.0)
		add_child(_glow)
		_build_visual()
		_update_glow()

	func _get_glow_tex() -> Texture2D:
		if _glow_tex == null:
			_glow_tex = _make_radial()
		return _glow_tex

	static func _make_radial() -> Texture2D:
		var s := 96
		var img := Image.create(s, s, false, Image.FORMAT_RGBA8)
		var c := Vector2(s / 2.0, s / 2.0)
		for y in range(s):
			for x in range(s):
				var dist := Vector2(x, y).distance_to(c) / (s / 2.0)
				var a := clampf(1.0 - dist, 0.0, 1.0)
				a = a * a
				img.set_pixel(x, y, Color(1, 1, 1, a))
		return ImageTexture.create_from_image(img)

	func _process(delta: float) -> void:
		_t += delta
		var p := get_parent()
		if p is Control:
			_bounds = Rect2(Vector2(16, 16), (p as Control).size - Vector2(32, 32))
		var dirv := Vector2.ZERO
		var moving := false
		if _pause > 0.0:
			_pause -= delta
		elif position.distance_to(_target) <= 4.0:
			_pick_target()
			_pause = _rng.randf_range(0.5, 2.5)
		else:
			var before := position
			position = position.move_toward(_target, speed * delta)
			dirv = position - before
			moving = dirv.length_squared() > 0.0001
		position.x = clampf(position.x, _bounds.position.x, _bounds.end.x)
		position.y = clampf(position.y, _bounds.position.y, _bounds.end.y)
		_update_glow()
		_on_tick(dirv, moving, delta)

	func _update_glow() -> void:
		if _glow == null:
			return
		var pulse := 0.75 + 0.25 * sin(_t * 4.0)
		_glow.modulate = Color(1.0, 0.25, 0.15, _doom * pulse)
		var sc := 0.6 + _doom * 0.9
		_glow.scale = Vector2(sc, sc)

	func set_doom(level: float) -> void:
		_doom = clampf(level, 0.0, 1.0)
		_update_glow()
		_on_doom()

	func _pick_target() -> void:
		_target = Vector2(
			_rng.randf_range(_bounds.position.x, _bounds.end.x),
			_rng.randf_range(_bounds.position.y, _bounds.end.y))

	# virtuals
	func _build_visual() -> void:
		pass
	func _on_tick(_dirv: Vector2, _moving: bool, _delta: float) -> void:
		pass
	func _on_doom() -> void:
		pass

# Procedural drawn cat (fallback when no real walk-cycle art is available).
class SandboxCat extends SandboxCatBase:
	func _on_tick(_dirv: Vector2, _moving: bool, _delta: float) -> void:
		queue_redraw()

	func _on_doom() -> void:
		queue_redraw()

	func _draw() -> void:
		var body := color.lerp(Color(0.85, 0.12, 0.10), _doom * 0.6)
		var dark := body.darkened(0.35)
		draw_line(Vector2(-8, 0), Vector2(-13, -6), dark, 2.0)                       # tail
		draw_circle(Vector2(0, 0), 7.0, body)                                        # body
		draw_circle(Vector2(6, -4), 4.5, body)                                       # head
		draw_colored_polygon(PackedVector2Array([                                     # left ear
			Vector2(3.0, -8.0), Vector2(4.5, -11.0), Vector2(6.5, -8.0)]), dark)
		draw_colored_polygon(PackedVector2Array([                                     # right ear
			Vector2(7.0, -8.0), Vector2(9.0, -11.0), Vector2(10.0, -8.0)]), dark)
		var eye := Color(0.15, 0.9, 0.4).lerp(Color(1.0, 0.85, 0.1), _doom)           # eyes redden->amber with doom
		draw_circle(Vector2(5.0, -4.5), 0.9 + _doom * 0.6, eye)
		draw_circle(Vector2(8.0, -4.5), 0.9 + _doom * 0.6, eye)

# Real walk-cycle cat (AnimatedSprite2D playing loaded pixellab frames).
class RealCat extends SandboxCatBase:
	const ART_SCALE := 0.45                    # 68px source -> ~30px on floor
	var _frames: SpriteFrames = null
	var _anim: AnimatedSprite2D = null

	func setup(frames: SpriteFrames) -> void:
		_frames = frames

	func _build_visual() -> void:
		_anim = AnimatedSprite2D.new()
		_anim.sprite_frames = _frames
		_anim.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_anim.scale = Vector2(ART_SCALE, ART_SCALE)
		add_child(_anim)
		if _frames != null and _frames.has_animation("idle"):
			_anim.play("idle")
		elif _frames != null and _frames.get_animation_names().size() > 0:
			_anim.play(_frames.get_animation_names()[0])

	func _on_tick(dirv: Vector2, moving: bool, _delta: float) -> void:
		if _anim == null or _frames == null:
			return
		if not moving:
			if _frames.has_animation("idle") and _anim.animation != "idle":
				_anim.play("idle")
			return
		var clip := "walk_" + _dir_name(dirv)
		if _frames.has_animation(clip):
			if _anim.animation != clip:
				_anim.play(clip)

	func _on_doom() -> void:
		if _anim != null:
			_anim.self_modulate = Color(1, 1, 1, 1).lerp(Color(1.0, 0.35, 0.28, 1.0), _doom * 0.7)

	func _dir_name(v: Vector2) -> String:
		if absf(v.x) >= absf(v.y):
			return "east" if v.x > 0.0 else "west"
		return "south" if v.y > 0.0 else "north"

# ===========================================================================
# Selection highlight ring (marks the per-sprite-scale / overlay-opacity target).
# ===========================================================================
class SandboxMarker extends Node2D:
	var radius: float = 18.0

	func _process(_delta: float) -> void:
		queue_redraw()

	func _draw() -> void:
		draw_arc(Vector2.ZERO, radius, 0.0, TAU, 28, Color(1.0, 0.9, 0.2, 0.85), 1.5)
		draw_arc(Vector2.ZERO, radius + 2.0, 0.0, TAU, 28, Color(0.1, 0.1, 0.1, 0.5), 1.0)

extends Control
## OFFICE SANDBOX v4 -- a standalone DEV TOY for the office-floor view (Pip: open
## this in the evening and play). v3 added SCALING, a POPULATE-UP sequence with simple
## space/placement logic, REAL cat walk-cycles loaded from art_source, and two dev-only
## prototypes: doom-glow on cats + a transparent-overlay (poster-on-wall) compositing POC.
##
## v4 (Pip's 2026-07-26 review feedback):
##   - COMPARE (side-by-side small vs large office) is now the DEFAULT view on open;
##     [V] toggles back to the single-floor view.
##   - BOTH floors are editable: spawn/populate/prop/poster/cat actions target the floor
##     UNDER THE MOUSE CURSOR; the status line names the active floor.
##   - Quality-tier mapping (canonical ladder: scummy / decent / premium): in compare
##     view the SMALL office renders the SCUMMY tier, the LARGE office DECENT. Where
##     tier-variant art is missing an asset falls back to the decent art unchanged.
##   - Props with a manifest entry (PropCatalogue, #907) place at their authored
##     scale + feet anchor and occupy their footprint_tiles cells.
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
# LEGACY fallback prop height for assets WITHOUT a manifest entry (#907 integration:
# manifested props scale via PropCatalogue.height_px instead of this force-scale).
const PROP_TARGET_H := 46.0
# One floor tile on screen (32px art displayed 2x; = OfficeEmployeeSprite.TILE_PX).
const DISPLAY_TILE_PX := 64.0
# Region of a 4x4 Wang tileset atlas holding the all-lower base tile (same crop OfficeFloor
# uses). Applied to promoted floor/wall tilesets before handing them to the dev hooks.
const WANG_BASE_REGION := Rect2i(64, 32, 32, 32)
const TILE_UPSCALE := 2

# --- v3 tuning --------------------------------------------------------------
# Global OCCUPANT scale default. Since the #899 scale pass fixed the BASE art scale
# (EmployeeSprite.SPRITE_SCALE now lands a worker at ~128px = 2 floor tiles), the sandbox
# default multiplier is NEUTRAL: 1.0 shows the real in-game scale. (The old 0.65 existed
# only to compensate for the oversized 2.0 base scale.) Tunable live with [-]/[=]. Applied
# as a NODE transform scale onto occupants -- never touches the sprites' art scale.
const OCCUPANT_SCALE_DEFAULT := 1.0
const OCCUPANT_SCALE_MIN := 0.2
const OCCUPANT_SCALE_MAX := 3.0
const OCCUPANT_SCALE_STEP := 1.12       # multiplicative per keypress
# #899: per-sprite step raised 1.1 -> 1.25. A 10% step was easy to read as "the keys are
# dead" on art that overflowed the room; 25% per press is unambiguous.
const PER_SPRITE_STEP := 1.25           # per-selected-sprite scale step
const PER_SPRITE_MIN := 0.25
const PER_SPRITE_MAX := 4.0
# #899: max cursor->sprite distance for the per-sprite pick ([,]/[.] and the marker ring).
# Previously _nearest_person had NO pick radius, so the keys silently retargeted whichever
# sprite happened to be nearest anywhere on the floor between presses.
const PICK_RADIUS := 64.0

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
const _CAT_SETS_NEEDING_WALKS := ["cat_eldritch(x4)"]

const DOOM_STEP := 0.1

# --- Anchor Sockets V2 demo (#894): doom-glow attached to sprite PARTS -------
# Anchored cat sets are built from res://data/office/anchor_sockets.json (the
# SSOT lists each promoted clip's frames dir), so the walkers and the anchors
# can never drift apart. Glow art = the closest hue variants of the existing
# doom overlay families (art_source/pixellab_2026-07-26_doom_overlays) per
# Pip's interim colour mapping (2026-07-26, W3 circle-back may override):
# blue = technical weirdness, purple = eldritch, red = conventional
# catastrophe. INTENSITY carries the doom level; subtle at nominal.
const _GLOW_FLAVOURS := [
	{"name": "purple (eldritch)", "rel": "pixellab_2026-07-26_doom_overlays/aura/glowdisc"},
	{"name": "red (catastrophe)", "rel": "pixellab_2026-07-26_doom_overlays/states/aura_red"},
	{"name": "blue (weirdness)", "rel": "pixellab_2026-07-26_doom_overlays/arc/radialweb"},
]

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

# Office quality TIERS -- the prototype "reflects game state" query. Canonical ladder
# (ruled 2026-07-26, see docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md):
# scummy / decent / premium. Only scummy + decent have art today; premium joins this
# array when its tilesets/props exist. Each tier biases which promoted props are offered
# (manifest style_tags when available, else keyword match on the asset id) and picks a
# promoted floor/wall tileset (matched by filename substring) to swap in. The real
# runtime hook later reads the tier from GameState instead of a keypress. Props tagged
# for NO tier count as decent art and are offered in every tier (decent fallback --
# where tier-variant art is missing the decent art shows unchanged, no tinting).
var _states: Array = [
	{"name": "scummy", "floor_key": "floor_lino",     "wall_key": "wall_scummy", "bias": ["scummy"]},
	{"name": "decent", "floor_key": "floor_concrete", "wall_key": "wall_decent", "bias": ["decent", "clean", "mega"]},
]
# Union of every tier's bias keywords -- a prop matching none of these is decent-fallback art.
const _STATE_KEYWORDS := ["scummy", "decent", "clean", "mega"]
# The tier whose art stands in when a tier-variant is missing (ruled 2026-07-26).
const FALLBACK_TIER := "decent"
# COMPARE view pins tiers per floor: the small starter office renders SCUMMY, the
# large complex office DECENT (Pip's 2026-07-26 ruling).
const COMPARE_TIER_SMALL := "scummy"
const COMPARE_TIER_LARGE := "decent"

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
var _pop_level_b: int = 0                  # v4: the small floor has its own populate level
var _furniture: Array = []                 # Sprite2D furniture placed by POPULATE (wall-affinity)
var _occupied_cells: Dictionary = {}       # str(cell centre) -> true (furniture no-overlap)
var _cat_frame_sets: Array = []            # [{name, frames, anchored_set?}] real walk-cycle SpriteFrames
var _cat_walk_report: String = ""
# Anchor Sockets V2 demo state: glow toggle + doom-flavour hue selection.
var _anchor_glow_on: bool = true
var _glow_flavour_idx: int = 0
var _glow_flavour_frames: Array = []       # SpriteFrames per _GLOW_FLAVOURS entry (null = missing art)
var _doom_level: float = 0.0
var _overlay_mode: bool = false            # false = prop placement, true = poster overlay
var _overlays: Array = []                  # Sprite2D transparent wall overlays (stackable)
var _poster_texs: Array = []               # placeholder/promoted poster textures
var _poster_idx: int = 0
var _marker: SandboxMarker = null          # highlights the per-sprite / overlay selection target
var _last_msg: String = ""                 # #899: transient feedback line shown in the status

# --- compare view (side-by-side scale check) ---------------------------------
# v4: compare is the DEFAULT view on open ("a more useful view" -- Pip 2026-07-26);
# [V] toggles back to single-floor. It renders TWO OfficeFloor instances at once:
# LEFT a small starter room (2-3 staff, sparse props, SCUMMY tier), RIGHT the main
# floor as a larger complex office (6+ staff, cats, dense props, DECENT tier). Same
# rendering path + the same shared scale constants on both -- the point is
# compare-and-contrast of one scale ruling in two room sizes. BOTH floors are
# editable: actions target the floor under the mouse cursor (_active_floor).
# Dev-only, pure composition, zero game-state writes.
var _compare_mode := false
var _floor_b: OfficeFloor = null           # LEFT starter office
var _hover_is_b := false                   # cached "cursor over the small floor" (v4)
var _roster_b: Array = []
var _furniture_b: Array = []               # starter-floor placeholder props
var _caption_a: Label = null
var _caption_b: Label = null

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
	_load_glow_flavours()
	_build_poster_pool()
	_rebuild_prop_pool()

	_build_overlay()
	_build_ghost()
	_build_marker()

	# Start with the real-art skin and a few people so it's alive on open.
	_apply_skin(0)
	_apply_mood(0)
	_apply_state(1)   # single-view tier defaults to decent (index 1)
	for _i in range(5):
		_spawn_person_on(_floor)
	_add_cat(_floor)
	# v4: COMPARE (small scummy office vs large decent office) is the DEFAULT view.
	_toggle_compare()
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
	_legend.text = "OFFICE SANDBOX v4  --  dev toy (no game state)   |   actions hit the floor UNDER THE CURSOR\n" \
		+ "[1]/[2] spawn/despawn person   [S] skin   [B] mood   [C]/[X] add/remove cat   [R] randomize   [0] clear   [ESC] quit\n" \
		+ "SCALE:  [-]/[=] all occupants   [,]/[.] the sprite under the cursor (within 64px)   |   POPULATE (cursor floor):  [U] up a stage   [I] down a stage\n" \
		+ "[V] toggle COMPARE (DEFAULT ON): small=SCUMMY vs large=DECENT office\n" \
		+ "[T] office TIER (scummy/decent; pinned per floor while compare is on)   [P] cycle prop/poster   [LMB] place   [RMB] remove nearest   [K] clear props\n" \
		+ "DOOM-GLOW on cats:  [ [ ] decrease   [ ] ] increase   |   OVERLAY POC:  [O] toggle poster-on-wall mode   [;]/['] selected overlay opacity\n" \
		+ "ANCHOR SOCKETS V2:  [A] toggle part-anchored glow (eyes; butt on rear walks + butt-flash)   [D] doom flavour hue (purple/red/blue)\n" \
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

# v4: the floor the mouse cursor is over -- ALL spawn/populate/placement actions target
# this floor, so the small starter office is just as editable as the large one.
func _active_floor() -> OfficeFloor:
	if _compare_mode and _floor_b != null and is_instance_valid(_floor_b) \
			and _floor_b.get_global_rect().has_point(get_global_mouse_position()):
		return _floor_b
	return _floor

# Human-readable name + pinned tier of a floor, for the status line.
func _floor_label(f: OfficeFloor) -> String:
	if not _compare_mode:
		return "single (%s)" % String(_states[_state_idx]["name"])
	return ("SMALL/%s" % COMPARE_TIER_SMALL) if f == _floor_b else ("LARGE/%s" % COMPARE_TIER_LARGE)

# The tier whose props should be OFFERED right now (compare: the hovered floor's tier).
func _pool_tier() -> String:
	if _compare_mode:
		return COMPARE_TIER_SMALL if _hover_is_b else COMPARE_TIER_LARGE
	return String(_states[_state_idx]["name"])

# Ghost + marker live under whichever floor is active so their local coords track it.
func _reparent_cursor_nodes(af: OfficeFloor) -> void:
	for n in [_ghost, _marker]:
		if n != null and is_instance_valid(n) and n.get_parent() != af:
			n.get_parent().remove_child(n)
			af.add_child(n)

func _process(_delta: float) -> void:
	# Active-floor tracking: when the cursor crosses floors, retarget the ghost/marker and
	# re-bias the offered prop pool to that floor's tier.
	var af := _active_floor()
	var over_b := af == _floor_b and _floor_b != null
	if over_b != _hover_is_b:
		_hover_is_b = over_b
		_reparent_cursor_nodes(af)
		_rebuild_prop_pool()
		_update_status()
	# Ghost preview: in prop mode it snaps to the tile grid; in overlay mode it snaps to the
	# nearest wall so the poster drop target reads. Marker highlights the selection target for
	# the per-sprite scale ([,]/[.]) or the overlay opacity ([;]/[']) keys.
	var mouse := af.get_local_mouse_position()
	if _ghost != null:
		if _overlay_mode:
			_ghost.visible = _ghost.texture != null
			_ghost.position = _snap_to_wall(mouse, _bounds_of(af))
		elif _prop_pool.is_empty():
			_ghost.visible = false
		else:
			_ghost.visible = true
			_ghost.position = _snap_to_grid(mouse)
	if _marker != null:
		if _overlay_mode:
			var ov := _nearest_overlay(mouse, af)
			_marker.visible = ov != null
			if ov != null:
				_marker.position = ov.position
				_marker.radius = 26.0
		else:
			var sp := _nearest_person(mouse, PICK_RADIUS, af)
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
					_remove_nearest_overlay(_active_floor().get_local_mouse_position())
				else:
					_remove_nearest_prop(_active_floor().get_local_mouse_position())
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
		KEY_A:
			_toggle_anchor_glow()
		KEY_D:
			_cycle_glow_flavour()
		KEY_V:
			_toggle_compare()
		KEY_O:
			_toggle_overlay_mode()   # was [V]; V now toggles the compare view
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
# v4: rosters are per-floor; keyboard actions route to the floor under the cursor.
func _roster_of(f: OfficeFloor) -> Array:
	return _roster_b if f == _floor_b and _floor_b != null else _roster

func _spawn_person() -> void:
	_spawn_person_on(_active_floor())

func _spawn_person_on(f: OfficeFloor) -> void:
	var r := _roster_of(f)
	if r.size() >= MAX_PEOPLE:
		return
	r.append(_make_person(_next_id))
	_next_id += 1
	f.set_roster(r)
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
	var f := _active_floor()
	var r := _roster_of(f)
	if r.is_empty():
		return
	r.pop_back()
	f.set_roster(r)

func _push_roster() -> void:
	_floor.set_roster(_roster)

# --- Skins ------------------------------------------------------------------
func _cycle_skin() -> void:
	_skin_idx = (_skin_idx + 1) % _skins.size()
	_apply_skin(_skin_idx)

func _apply_skin(idx: int) -> void:
	_skin_idx = idx
	_apply_skin_to_floor(_floor)
	if _floor_b != null and is_instance_valid(_floor_b):
		_apply_skin_to_floor(_floor_b)   # compare view mirrors the skin (same render path)
	_apply_occupant_scale()

func _apply_skin_to_floor(f: OfficeFloor) -> void:
	var s: Dictionary = _skins[_skin_idx]
	match String(s.get("kind", "")):
		"art":
			# Real art goes through the variant pool (variant 0 == this same asset,
			# so the render is unchanged until new worker variants are triaged in).
			f.set_use_variant_pool(true)
			f.set_sprite_frames(RealSpriteFrames)
			f.set_tier(1)
		"color":
			# Colour-skin preview must apply UNIFORMLY -> bypass the variant pool.
			f.set_use_variant_pool(false)
			var frames: SpriteFrames = EmployeeSpriteScript._build_placeholder_frames(s["body"], HAT)
			f.set_sprite_frames(frames)
			f.set_tier(1)
		_:
			f.set_tier(0)                     # "blob"

# --- Mood / lighting --------------------------------------------------------
func _cycle_mood() -> void:
	_mood_idx = (_mood_idx + 1) % _moods.size()
	_apply_mood(_mood_idx)

func _apply_mood(idx: int) -> void:
	_mood_idx = idx
	_floor.modulate = _moods[idx]["tint"]
	if _floor_b != null and is_instance_valid(_floor_b):
		_floor_b.modulate = _moods[idx]["tint"]

# --- Office TIER (prototype "reflects game state"; ladder scummy/decent/premium) ----
func _cycle_state() -> void:
	if _compare_mode:
		# Tiers are PINNED per floor while comparing (small=scummy, large=decent).
		_last_msg = "compare view pins tiers: small=%s, large=%s ([V] for single view to cycle)" % [
			COMPARE_TIER_SMALL, COMPARE_TIER_LARGE]
		return
	_apply_state((_state_idx + 1) % _states.size())

func _apply_state(idx: int) -> void:
	_state_idx = idx
	# 1) bias the prop pool toward the active tier (decent-fallback art always kept).
	_rebuild_prop_pool()
	# 2) dress each floor for its tier (compare pins small=scummy / large=decent).
	_apply_floor_styles()

func _state_named(tier: String) -> Dictionary:
	for st in _states:
		if String(st.get("name", "")) == tier:
			return st
	return _states[_state_idx]

func _apply_floor_styles() -> void:
	if _compare_mode and _floor_b != null and is_instance_valid(_floor_b):
		_style_floor(_floor, COMPARE_TIER_LARGE)
		_style_floor(_floor_b, COMPARE_TIER_SMALL)
	else:
		_style_floor(_floor, String(_states[_state_idx]["name"]))

# Dress one floor for a tier: swap in the tier's promoted floor/wall tilesets (additive
# dev hooks; null restores the built-in look) and tell the floor its quality tier so its
# landmark props can pick tier-variant art (missing variants fall back to decent art).
func _style_floor(f: OfficeFloor, tier: String) -> void:
	if f == null or not is_instance_valid(f):
		return
	var st := _state_named(tier)
	f.set_floor_tile_texture(_tileset_tile_for(String(st.get("floor_key", ""))))
	f.set_wall_strip_texture(_tileset_tile_for(String(st.get("wall_key", ""))))
	f.set_office_style(tier)

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
# Rebuild the offered prop pool for the ACTIVE tier (compare: the hovered floor's tier):
# props serving the tier PLUS decent-fallback art. Manifested assets (PropCatalogue) are
# judged by their style_tags (#907); unmanifested promoted art falls back to keyword
# inference on the asset id. A decent-tagged asset with NO tier-variant art is still
# offered in other tiers (the fall-back-to-decent-unchanged rule, 2026-07-26).
func _rebuild_prop_pool() -> void:
	var tier := _pool_tier()
	var bias: Array = _state_named(tier).get("bias", [])
	_prop_pool.clear()
	for a in _promoted.get("props", []):
		if _prop_serves_tier(a, tier, bias):
			_prop_pool.append(a)
	if _prop_idx >= _prop_pool.size():
		_prop_idx = 0
	_refresh_ghost_texture()

func _prop_serves_tier(a: Dictionary, tier: String, bias: Array) -> bool:
	var id := String(a.get("id", ""))
	var base := id.get_file().get_basename()
	if PropCatalogue.has(base):
		var tags := PropCatalogue.style_tags(base)
		if tier in tags:
			return true
		# Decent art stands in wherever its tier-variant is missing (no tinting hacks).
		return FALLBACK_TIER in tags and not PropCatalogue.has("%s_%s" % [base, tier])
	# Unmanifested: keyword inference on the id (legacy path).
	var id_l := id.to_lower()
	var untiered := true
	var matches_tier := false
	for kw in _STATE_KEYWORDS:
		if id_l.find(kw) != -1:
			untiered = false
			if kw in bias:
				matches_tier = true
	return untiered or matches_tier

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
		_ghost.centered = true
		_ghost.offset = Vector2.ZERO
		return
	var p := _current_prop()
	_ghost.texture = p.get("tex", null) if not p.is_empty() else null
	if _ghost.texture != null:
		var id := String(p.get("id", ""))
		_ghost.scale = _prop_scale(_ghost.texture, id) * _occupant_scale
		_apply_prop_anchor(_ghost, _ghost.texture, id)

# Manifest id for a promoted asset: the file basename (matches props_manifest.json keys).
# Only trusted when the loaded texture's size equals the manifest canvas_px -- an
# art_source master at another resolution is exactly the "missing metadata" case Pip
# picks up in his review sweep, so it degrades to the legacy path.
func _manifest_id_for(tex: Texture2D, asset_id: String) -> String:
	if tex == null or asset_id == "":
		return ""
	var base := asset_id.get_file().get_basename()
	if not PropCatalogue.has(base):
		return ""
	var canvas: Array = PropCatalogue.get_entry(base).get("canvas_px", [])
	if canvas.size() != 2 or Vector2(float(canvas[0]), float(canvas[1])) != tex.get_size():
		return ""
	return base

# #907 integration: manifested props scale so the opaque subject spans
# height_px(id, DISPLAY_TILE_PX); everything else keeps the legacy PROP_TARGET_H
# force-scale (PropCatalogue's fallback reproduces the same 46px for unknown ids).
func _prop_scale(tex: Texture2D, asset_id: String = "") -> Vector2:
	var mid := _manifest_id_for(tex, asset_id)
	if mid != "":
		var subj: Array = PropCatalogue.get_entry(mid).get("subject_px", [])
		if subj.size() == 2 and float(subj[1]) > 0.0:
			var sm := PropCatalogue.height_px(mid, DISPLAY_TILE_PX) / float(subj[1])
			return Vector2(sm, sm)
	var h := tex.get_size().y
	var s := (PROP_TARGET_H / h) if h > 0.0 else 1.0
	return Vector2(s, s)

# Feet-anchor a sprite at the manifest anchor_px (subject feet) instead of the texture
# centre, so padding-heavy art sits on the floor where it is dropped.
func _apply_prop_anchor(spr: Sprite2D, tex: Texture2D, asset_id: String) -> void:
	var mid := _manifest_id_for(tex, asset_id)
	var anchor := PropCatalogue.anchor(mid) if mid != "" else PropCatalogue.ANCHOR_UNSET
	if anchor != PropCatalogue.ANCHOR_UNSET:
		spr.centered = false
		spr.offset = -anchor
	else:
		spr.centered = true
		spr.offset = Vector2.ZERO

func _place_prop() -> void:
	var p := _current_prop()
	if p.is_empty() or _placed_props.size() >= MAX_PLACED:
		return
	var tex: Texture2D = p.get("tex", null)
	if tex == null:
		return
	var af := _active_floor()
	var id := String(p.get("id", ""))
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var base := _prop_scale(tex, id)
	spr.set_meta("base_scale", base)
	spr.scale = base * _occupant_scale
	_apply_prop_anchor(spr, tex, id)
	# Wall-affinity assist: if the drop point is near a wall, snap flush to it; else free grid.
	spr.position = _grid_or_wall(af.get_local_mouse_position(), _bounds_of(af))
	spr.z_index = 2
	spr.set_meta("asset_id", id)
	af.add_child(spr)
	_placed_props.append(spr)
	_occupy_prop_footprint(spr, af, id)
	_sync_blocked_rects()

# #907: a manifested prop OCCUPIES its footprint_tiles cells (display tiles are 64px =
# 2x2 sandbox grid cells each) so POPULATE furniture will not overlap it. Unmanifested
# props keep the old behaviour (no occupancy -- the renderer used to just guess).
func _occupy_prop_footprint(spr: Sprite2D, f: OfficeFloor, asset_id: String) -> void:
	var mid := _manifest_id_for(spr.texture, asset_id)
	if mid == "":
		return
	var fp := PropCatalogue.footprint(mid)
	var w_px := fp.x * DISPLAY_TILE_PX
	var d_px := fp.y * DISPLAY_TILE_PX
	var keys: Array = []
	# Feet-anchored: footprint extends up from the feet row, centred horizontally.
	var y0 := spr.position.y - d_px + GRID * 0.5
	var x0 := spr.position.x - w_px * 0.5 + GRID * 0.5
	var cols := int(ceil(w_px / GRID))
	var rows := int(ceil(d_px / GRID))
	for r in range(rows):
		for c in range(cols):
			var cell := _cell_of(f, Vector2(x0 + c * GRID, y0 + r * GRID))
			var key := _cell_key(f, cell)
			if not _occupied_cells.has(key):
				_occupied_cells[key] = true
				keys.append(key)
	spr.set_meta("occupied_keys", keys)

func _release_prop_footprint(spr: Sprite2D) -> void:
	for key in spr.get_meta("occupied_keys", []):
		_occupied_cells.erase(String(key))

# --- Tier-1 collision: feed prop/furniture footprints to the floors ----------
# Walkers must never STAND inside furniture. Each floor gets the no-stand rects
# of the props parented to it via OfficeFloor.set_extra_blocked_rects (additive
# dev hook; the floor adds its own landmark-prop footprints itself).
func _blocked_rect_for(spr: Sprite2D) -> Rect2:
	var mid := _manifest_id_for(spr.texture, String(spr.get_meta("asset_id", "")))
	if mid != "":
		# Manifested: authored footprint, feet-anchored (extends up from the feet).
		var fp := PropCatalogue.footprint(mid)
		var w := fp.x * DISPLAY_TILE_PX
		var d := fp.y * DISPLAY_TILE_PX
		return Rect2(spr.position - Vector2(w * 0.5, d), Vector2(w, d))
	# Unmanifested (placeholder furniture / legacy props): the drawn sprite rect.
	var base: Vector2 = spr.get_meta("base_scale", Vector2.ONE)
	var sz: Vector2 = spr.texture.get_size() * base if spr.texture != null else Vector2(GRID, GRID)
	if spr.centered:
		return Rect2(spr.position - sz * 0.5, sz)
	return Rect2(spr.position + spr.offset * base, sz)

func _sync_blocked_rects() -> void:
	var rects_a: Array = []
	var rects_b: Array = []
	for spr in _placed_props + _furniture + _furniture_b:
		if not is_instance_valid(spr):
			continue
		var r: Rect2 = _blocked_rect_for(spr)
		if _floor_b != null and is_instance_valid(_floor_b) and spr.get_parent() == _floor_b:
			rects_b.append(r)
		elif spr.get_parent() == _floor:
			rects_a.append(r)
	_floor.set_extra_blocked_rects(rects_a)
	if _floor_b != null and is_instance_valid(_floor_b):
		_floor_b.set_extra_blocked_rects(rects_b)

func _remove_nearest_prop(at: Vector2) -> void:
	if _placed_props.is_empty():
		return
	var af := _active_floor()
	var best := -1
	var best_d := INF
	for i in range(_placed_props.size()):
		var spr = _placed_props[i]
		if not is_instance_valid(spr) or spr.get_parent() != af:
			continue
		var d: float = spr.position.distance_to(at)
		if d < best_d:
			best_d = d
			best = i
	if best >= 0:
		var spr = _placed_props[best]
		if is_instance_valid(spr):
			_release_prop_footprint(spr)
			spr.queue_free()
		_placed_props.remove_at(best)
		_sync_blocked_rects()

func _clear_props() -> void:
	for spr in _placed_props:
		if is_instance_valid(spr):
			_release_prop_footprint(spr)
			spr.queue_free()
	_placed_props.clear()
	_sync_blocked_rects()

func _snap_to_grid(pos: Vector2) -> Vector2:
	return Vector2(
		floor(pos.x / GRID) * GRID + GRID * 0.5,
		floor(pos.y / GRID) * GRID + GRID * 0.5)

# Occupancy key for a grid cell of a specific floor (cells are floor-local, so the two
# compare floors would otherwise collide on identical coordinates).
func _cell_key(f: OfficeFloor, cell: Vector2) -> String:
	return ("b|" if f == _floor_b and _floor_b != null else "a|") + str(cell)

# Resolve a floor-local point to its occupancy cell CENTRE on the floor's bounds lattice
# (the same lattice _pick_wall_cell enumerates, so occupancy from placed props and
# populate furniture actually collide instead of living on offset grids).
func _cell_of(f: OfficeFloor, pos: Vector2) -> Vector2:
	var b := _bounds_of(f)
	var c := floorf((pos.x - b.position.x) / GRID)
	var r := floorf((pos.y - b.position.y) / GRID)
	return Vector2(
		b.position.x + c * GRID + GRID * 0.5,
		b.position.y + r * GRID + GRID * 0.5)

# Grid-snap, but if the point is within one grid cell of a wall, snap flush to that wall
# (furniture wall-affinity for manual placement; the POPULATE placer uses walls exclusively).
func _grid_or_wall(pos: Vector2, b: Rect2) -> Vector2:
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
# Spawn a cat on `target` (default: the floor under the cursor). Uses a REAL loaded
# walk-cycle (cycling the available sets) when any exist; otherwise falls back to the
# procedural drawn cat. Both honour doom-glow + occupant scale.
func _add_cat(target: OfficeFloor = null) -> void:
	if _cats.size() >= MAX_CATS:
		return
	var af := target if target != null else _active_floor()
	var cat: SandboxCatBase
	if not _cat_frame_sets.is_empty():
		var rc := RealCat.new()
		# Stable per-cat id phase-offsets the deterministic alt-clip splice (#913).
		var set_info: Dictionary = _cat_frame_sets[_cat_color_idx % _cat_frame_sets.size()]
		rc.setup(set_info["frames"], "cat_%d" % _cat_color_idx)
		# Anchor Sockets V2: sets built from anchor_sockets.json get part-anchored
		# doom glow (eyes everywhere; butt on rear walks + butt-flash splices).
		var aset := String(set_info.get("anchored_set", ""))
		if aset != "":
			rc.configure_anchor_glow(aset, _current_glow_frames(), _anchor_glow_on)
		cat = rc
	else:
		var sc := SandboxCat.new()
		sc.color = _cat_palette[_cat_color_idx % _cat_palette.size()]
		cat = sc
	_cat_color_idx += 1
	var b := _bounds_of(af)
	cat.position = Vector2(
		_rng.randf_range(b.position.x, b.end.x),
		_rng.randf_range(b.position.y, b.end.y))
	af.add_child(cat)
	cat.scale = Vector2(_occupant_scale, _occupant_scale)
	cat.set_doom(_doom_level)
	_cats.append(cat)

func _cats_on(f: OfficeFloor) -> int:
	var n := 0
	for cat in _cats:
		if is_instance_valid(cat) and cat.get_parent() == f:
			n += 1
	return n

# Remove the newest cat on `target` (default: the floor under the cursor); falls back to
# the newest cat anywhere so [X] never silently no-ops while cats remain.
func _remove_cat(target: OfficeFloor = null) -> void:
	if _cats.is_empty():
		return
	var af := target if target != null else _active_floor()
	var idx := _cats.size() - 1
	for i in range(_cats.size() - 1, -1, -1):
		if is_instance_valid(_cats[i]) and _cats[i].get_parent() == af:
			idx = i
			break
	var cat = _cats[idx]
	_cats.remove_at(idx)
	if is_instance_valid(cat):
		cat.queue_free()

func _floor_bounds() -> Rect2:
	return _bounds_of(_floor)

func _bounds_of(f: Control) -> Rect2:
	var s := f.size
	if s.x < 40.0 or s.y < 40.0:
		s = Vector2(360, 260)
	return Rect2(Vector2(16, 16), s - Vector2(32, 32))

# --- v3: SCALING ------------------------------------------------------------
# Apply the global occupant scale (times any per-sprite multiplier held in node meta) to
# every occupant the sandbox owns: employee sprites (NODE transform only -- never the art
# scale the live view sets), cats, populate-furniture, and manually-placed props.
func _apply_occupant_scale() -> void:
	_scale_people_on(_floor)
	if _floor_b != null and is_instance_valid(_floor_b):
		_scale_people_on(_floor_b)   # compare view: SAME scale constants both sides
	for cat in _cats:
		if is_instance_valid(cat):
			cat.scale = Vector2(_occupant_scale, _occupant_scale)
	for f in _furniture:
		if is_instance_valid(f):
			var base: Vector2 = f.get_meta("base_scale", Vector2.ONE)
			f.scale = base * _occupant_scale
	for f2 in _furniture_b:
		if is_instance_valid(f2):
			var base_b: Vector2 = f2.get_meta("base_scale", Vector2.ONE)
			f2.scale = base_b * _occupant_scale
	for spr in _placed_props:
		if is_instance_valid(spr):
			var base2: Vector2 = spr.get_meta("base_scale", Vector2.ONE)
			spr.scale = base2 * _occupant_scale
	_refresh_ghost_texture()

func _scale_people_on(f: OfficeFloor) -> void:
	for c in f.get_children():
		if c is OfficeEmployeeSprite:
			var m := float((c as Node).get_meta("sb_scale_mult", 1.0))
			(c as Node2D).scale = Vector2(_occupant_scale * m, _occupant_scale * m)

func _nudge_occupant_scale(mult: float) -> void:
	_occupant_scale = clampf(_occupant_scale * mult, OCCUPANT_SCALE_MIN, OCCUPANT_SCALE_MAX)
	_apply_occupant_scale()

func _scale_nearest_person(mult: float) -> void:
	var af := _active_floor()
	var sp := _nearest_person(af.get_local_mouse_position(), PICK_RADIUS, af)
	if sp == null:
		# #899: previously this silently no-opped (or silently retargeted a far-away
		# sprite) -- now the status line says why nothing visibly changed.
		_last_msg = "per-sprite scale: no sprite within %dpx of the cursor" % int(PICK_RADIUS)
		return
	var m := float(sp.get_meta("sb_scale_mult", 1.0))
	m = clampf(m * mult, PER_SPRITE_MIN, PER_SPRITE_MAX)
	sp.set_meta("sb_scale_mult", m)
	var nm := "sprite"
	if sp is OfficeEmployeeSprite:
		nm = (sp as OfficeEmployeeSprite).emp_name
	_last_msg = "per-sprite scale: %s -> x%.2f" % [nm, m]
	_apply_occupant_scale()

# #899: picks the nearest employee sprite WITHIN max_dist of `at` (was unbounded,
# which made [,]/[.] retarget invisibly-distant sprites between presses).
# v4: searches floor `f` (default main) -- `at` is in that floor's local coords.
func _nearest_person(at: Vector2, max_dist: float = PICK_RADIUS, f: OfficeFloor = null) -> Node2D:
	var af := f if f != null else _floor
	var best: Node2D = null
	var best_d := INF
	for c in af.get_children():
		if c is OfficeEmployeeSprite:
			var d: float = (c as Node2D).position.distance_to(at)
			if d < best_d:
				best_d = d
				best = c
	return best if best_d <= max_dist else null

# --- v3: POPULATE-UP sequence + placement logic -----------------------------
# v4: each floor keeps its own populate level; [U]/[I] drive the floor under the cursor.
func _furn_of(f: OfficeFloor) -> Array:
	return _furniture_b if f == _floor_b and _floor_b != null else _furniture

func _populate_up() -> void:
	var af := _active_floor()
	if af == _floor_b and _floor_b != null:
		if _pop_level_b >= _POP_STAGES.size():
			return
		_pop_level_b += 1
	else:
		if _pop_level >= _POP_STAGES.size():
			return
		_pop_level += 1
	_apply_pop_stage(af)

func _populate_down() -> void:
	var af := _active_floor()
	if af == _floor_b and _floor_b != null:
		if _pop_level_b <= 0:
			return
		_pop_level_b -= 1
	else:
		if _pop_level <= 0:
			return
		_pop_level -= 1
	_apply_pop_stage(af)

func _apply_pop_stage(f: OfficeFloor = null) -> void:
	var af := f if f != null else _floor
	var on_b := af == _floor_b and _floor_b != null
	var level := _pop_level_b if on_b else _pop_level
	var want_people := 0
	var want_cats := 0
	var want_furn := 0
	if level > 0:
		var st: Dictionary = _POP_STAGES[level - 1]
		want_people = int(st["people"])
		want_cats = int(st["cats"])
		want_furn = int(st["furn"])
	# People (spread around the desks by OfficeFloor's own layout -- sane, non-overlapping).
	var roster := _roster_of(af)
	while roster.size() < want_people and roster.size() < MAX_PEOPLE:
		roster.append(_make_person(_next_id))
		_next_id += 1
	while roster.size() > want_people:
		roster.pop_back()
	af.set_roster(roster)
	# Cats (wander freely, parented to this floor).
	while _cats_on(af) < want_cats and _cats.size() < MAX_CATS:
		_add_cat(af)
	while _cats_on(af) > want_cats:
		_remove_cat(af)
	# Furniture (wall-affinity, no-overlap).
	var furn := _furn_of(af)
	while furn.size() < want_furn:
		if not _spawn_furniture(af):
			break
	while furn.size() > want_furn:
		_remove_furniture(af)
	_apply_occupant_scale()
	_sync_blocked_rects()

# Place one furniture piece on a free perimeter (wall) grid cell of floor `f`. Returns
# false if the floor is full. Demonstrates the first "space logic" slice: furniture hugs
# walls, does not overlap other furniture.
func _spawn_furniture(f: OfficeFloor = null) -> bool:
	var af := f if f != null else _floor
	var cell := _pick_wall_cell(af)
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
	var key := _cell_key(af, cell)
	spr.set_meta("cell_key", key)
	af.add_child(spr)
	_furn_of(af).append(spr)
	_occupied_cells[key] = true
	return true

func _remove_furniture(f: OfficeFloor = null) -> void:
	var furn := _furn_of(f if f != null else _floor)
	if furn.is_empty():
		return
	var spr = furn.pop_back()
	if is_instance_valid(spr):
		_occupied_cells.erase(String(spr.get_meta("cell_key", "")))
		spr.queue_free()

# Return a random unoccupied grid cell centre on the floor PERIMETER (wall-affinity). Falls
# back to any interior cell if the perimeter is full. Returns Vector2.INF if nothing free.
func _pick_wall_cell(f: OfficeFloor = null) -> Vector2:
	var af := f if f != null else _floor
	var b := _bounds_of(af)
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
			if _occupied_cells.has(_cell_key(af, centre)):
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

# --- COMPARE VIEW: side-by-side starter vs complex office (#899 / #793) ------
# [V] splits the sandbox into TWO OfficeFloor instances rendered through the
# IDENTICAL path with the IDENTICAL scale constants:
#   LEFT  = small starter environment: small bounds, 3 staff, sparse props.
#   RIGHT = the main sandbox floor, topped up to a larger complex office:
#           7+ staff, 2 cats, 8+ wall furniture (plus whatever was placed).
# Purpose: visually judge one scale ruling (worker ~2 tiles, cat ~0.5 tile) in
# two room sizes at once. Pure composition; no game-state writes.
func _toggle_compare() -> void:
	_compare_mode = not _compare_mode
	if _compare_mode:
		_enter_compare()
	else:
		_exit_compare()

func _enter_compare() -> void:
	# LEFT starter floor: same scene, same skin/mood, its own small roster; renders the
	# SCUMMY tier (the large floor renders DECENT -- Pip's 2026-07-26 quality-tier ruling).
	_floor_b = OfficeFloorScene.instantiate()
	add_child(_floor_b)
	move_child(_floor_b, _floor.get_index() + 1)   # keep the legend/status panel on top
	_apply_skin_to_floor(_floor_b)
	_floor_b.modulate = _moods[_mood_idx]["tint"]
	_roster_b = []
	for _i in range(3):
		_roster_b.append(_make_person(_next_id))
		_next_id += 1
	_floor_b.set_roster(_roster_b)
	# RIGHT complex floor: top up the EXISTING sandbox population (reuses the
	# normal spawn machinery; never shrinks anything Pip already placed).
	while _roster.size() < 7 and _roster.size() < MAX_PEOPLE:
		_roster.append(_make_person(_next_id))
		_next_id += 1
	_push_roster()
	while _cats_on(_floor) < 2 and _cats.size() < MAX_CATS:
		_add_cat(_floor)
	_apply_floor_styles()   # small=scummy / large=decent tilesets + prop variants
	_rebuild_prop_pool()
	_layout_floors()
	_caption_a = _make_caption(_floor, "LARGE office -- DECENT tier")
	_caption_b = _make_caption(_floor_b, "SMALL office -- SCUMMY tier")
	# Furniture spawns DEFERRED (both floors): wall-affinity derives from the floors'
	# real bounds, which do not exist until the layout pass after the anchor change
	# (spawning now would hug the walls of a stale rect).
	call_deferred("_spawn_starter_props")
	call_deferred("_spawn_compare_furniture")
	_apply_occupant_scale()
	_last_msg = "compare ON (default): both floors editable -- actions hit the floor under the cursor"

func _exit_compare() -> void:
	if _caption_a != null and is_instance_valid(_caption_a):
		_caption_a.queue_free()
	_caption_a = null
	_caption_b = null                      # child of _floor_b; freed with it
	# Ghost/marker may be parented to the departing floor; cats/props on it die with it.
	_reparent_cursor_nodes(_floor)
	_hover_is_b = false
	if _floor_b != null and is_instance_valid(_floor_b):
		for i in range(_cats.size() - 1, -1, -1):
			if not is_instance_valid(_cats[i]) or _cats[i].get_parent() == _floor_b:
				_cats.remove_at(i)
		for i in range(_placed_props.size() - 1, -1, -1):
			var spr = _placed_props[i]
			if not is_instance_valid(spr) or spr.get_parent() == _floor_b:
				if is_instance_valid(spr):
					_release_prop_footprint(spr)
				_placed_props.remove_at(i)
		for i in range(_overlays.size() - 1, -1, -1):
			if not is_instance_valid(_overlays[i]) or _overlays[i].get_parent() == _floor_b:
				_overlays.remove_at(i)
		_floor_b.queue_free()
	_floor_b = null
	_roster_b.clear()
	for spr in _furniture_b:
		if is_instance_valid(spr):
			_occupied_cells.erase(String(spr.get_meta("cell_key", "")))
	_furniture_b.clear()
	# Drop any remaining small-floor occupancy records.
	for key in _occupied_cells.keys():
		if String(key).begins_with("b|"):
			_occupied_cells.erase(key)
	_pop_level_b = 0
	_apply_floor_styles()   # restore the single-view tier
	_rebuild_prop_pool()
	_layout_floors()
	_sync_blocked_rects()
	_last_msg = "compare OFF (single floor; [V] to bring it back)"

func _layout_floors() -> void:
	if _compare_mode:
		# LEFT starter: deliberately small room. RIGHT complex: the wide remainder.
		_set_floor_anchors(_floor_b, 0.02, 0.32, 0.36, 0.96)
		_set_floor_anchors(_floor, 0.40, 0.04, 0.99, 0.98)
	else:
		_floor.set_anchors_preset(Control.PRESET_FULL_RECT)

func _set_floor_anchors(f: Control, l: float, t: float, r: float, b: float) -> void:
	if f == null or not is_instance_valid(f):
		return
	f.anchor_left = l
	f.anchor_top = t
	f.anchor_right = r
	f.anchor_bottom = b
	f.offset_left = 0.0
	f.offset_top = 0.0
	f.offset_right = 0.0
	f.offset_bottom = 0.0

func _make_caption(parent_floor: Control, text: String) -> Label:
	var cap := Label.new()
	cap.text = text
	cap.add_theme_font_size_override("font_size", 12)
	cap.modulate = Color(1.0, 0.9, 0.4)
	cap.position = Vector2(12, 12)
	cap.z_index = 4
	parent_floor.add_child(cap)
	return cap

# Deferred main-floor furniture top-up for compare entry (see _enter_compare: the
# wall cells need the post-layout bounds). Never shrinks anything Pip already placed.
func _spawn_compare_furniture() -> void:
	if not _compare_mode:
		return
	while _furniture.size() < 8:
		if not _spawn_furniture(_floor):
			break
	_apply_occupant_scale()
	_sync_blocked_rects()

# Sparse starter furnishing: a desk / plant / cabinet against the left floor's
# walls, via the same placeholder _furniture_tex path POPULATE uses. Registers each
# spot's occupancy so populate-up on the small floor will not stack furniture on it.
func _spawn_starter_props() -> void:
	if _floor_b == null or not is_instance_valid(_floor_b):
		return
	var b := _bounds_of(_floor_b)
	var spots: Array = [
		Vector2(b.position.x + GRID * 0.5, b.position.y + GRID * 0.5),
		Vector2(b.end.x - GRID * 0.5, b.position.y + GRID * 0.5),
		Vector2(b.position.x + GRID * 0.5, b.end.y - GRID * 0.5),
	]
	var kinds: Array = ["desk", "plant", "cabinet"]
	for i in range(spots.size()):
		var tex := _furniture_tex(String(kinds[i]))
		var spr := Sprite2D.new()
		spr.texture = tex
		spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		var base := _prop_scale(tex)
		spr.set_meta("base_scale", base)
		spr.scale = base * _occupant_scale
		spr.position = spots[i]
		spr.z_index = 2
		var key := _cell_key(_floor_b, _cell_of(_floor_b, spots[i]))
		spr.set_meta("cell_key", key)
		_occupied_cells[key] = true
		_floor_b.add_child(spr)
		_furniture_b.append(spr)
	_sync_blocked_rects()

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
	var af := _active_floor()
	var spr := Sprite2D.new()
	spr.texture = tex
	spr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	spr.position = _snap_to_wall(af.get_local_mouse_position(), _bounds_of(af))
	# z_index 1 = on the wall, behind the people (z 0) that stand lower on the floor. Later
	# overlays get a higher z so a stack composites front-to-back visibly.
	spr.z_index = 1 + (_overlays.size() % 4)
	var op := 0.7
	spr.modulate = Color(1, 1, 1, op)
	spr.set_meta("opacity", op)
	af.add_child(spr)
	_overlays.append(spr)

func _remove_nearest_overlay(at: Vector2) -> void:
	var ov := _nearest_overlay(at, _active_floor())
	if ov == null:
		return
	_overlays.erase(ov)
	ov.queue_free()

# Nearest overlay ON floor `f` (default: any floor -- `at` must then be main-floor-local).
func _nearest_overlay(at: Vector2, f: OfficeFloor = null) -> Sprite2D:
	var best: Sprite2D = null
	var best_d := INF
	for spr in _overlays:
		if not is_instance_valid(spr):
			continue
		if f != null and spr.get_parent() != f:
			continue
		var d: float = spr.position.distance_to(at)
		if d < best_d:
			best_d = d
			best = spr
	return best

func _nudge_overlay_opacity(d: float) -> void:
	var af := _active_floor()
	var ov := _nearest_overlay(af.get_local_mouse_position(), af)
	if ov == null:
		return
	var op := clampf(float(ov.get_meta("opacity", 0.7)) + d, 0.05, 1.0)
	ov.set_meta("opacity", op)
	ov.modulate = Color(1, 1, 1, op)

# Snap a point to the nearest wall of the given floor bounds (poster wall-affinity).
# Posters sit just inside the wall so they read as mounted on it.
func _snap_to_wall(p: Vector2, b: Rect2) -> Vector2:
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
	for spr in _furniture_b:
		if is_instance_valid(spr):
			spr.queue_free()
	_furniture_b.clear()
	_occupied_cells.clear()
	_sync_blocked_rects()

# --- Bulk toys --------------------------------------------------------------
func _randomize() -> void:
	_clear_all()
	_apply_skin(_rng.randi() % _skins.size())
	_apply_mood(_rng.randi() % _moods.size())
	if not _compare_mode:
		_apply_state(_rng.randi() % _states.size())
	var n := _rng.randi_range(4, 9)
	for _i in range(n):
		_spawn_person_on(_floor)
	var c := _rng.randi_range(1, 3)
	for _j in range(c):
		_add_cat(_floor)
	_apply_occupant_scale()

# v4: [0] clears CONTENTS but keeps the current view layout (compare stays compare --
# it is the default view now, so clearing must not silently collapse to single-floor).
func _clear_all() -> void:
	_roster.clear()
	_push_roster()
	_roster_b.clear()
	if _floor_b != null and is_instance_valid(_floor_b):
		_floor_b.set_roster(_roster_b)
	for cat in _cats:
		if is_instance_valid(cat):
			cat.queue_free()
	_cats.clear()
	_clear_props()
	_clear_furniture()
	_clear_overlays()
	_pop_level = 0
	_pop_level_b = 0

func _update_status() -> void:
	if _status == null:
		return
	# #899: surface the SELECTED sprite's per-sprite multiplier so [,]/[.] have
	# visible feedback (the old status only printed the GLOBAL scale, so a
	# working per-sprite nudge looked like dead keys).
	var af := _active_floor()
	var sel := _nearest_person(af.get_local_mouse_position(), PICK_RADIUS, af)
	var sel_txt := "none in range"
	if sel != null:
		sel_txt = "x%.2f" % float(sel.get_meta("sb_scale_mult", 1.0))
	var pop_txt := "%d/%d" % [_pop_level, _POP_STAGES.size()]
	if _compare_mode:
		pop_txt = "large %d/%d, small %d/%d" % [
			_pop_level, _POP_STAGES.size(), _pop_level_b, _POP_STAGES.size()]
	_status.text = "skin: %s   |   people: %d+%d   |   cats: %d   |   mood: %s   |   scale: %d%%   |   sel sprite: %s   |   populate: %s%s" % [
		_skins[_skin_idx]["name"], _roster.size(), _roster_b.size(), _cats.size(),
		_moods[_mood_idx]["name"],
		int(round(_occupant_scale * 100.0)), sel_txt, pop_txt,
		("" if _last_msg == "" else "\n>> " + _last_msg)]
	if _asset_status == null:
		return
	var mode_line := "ACTIVE FLOOR (under cursor): %s   |   MODE: %s   |   compare: %s   |   doom-glow: %d%%   |   anchor glow: %s @ %s   |   overlays: %d" % [
		_floor_label(af),
		("OVERLAY (poster on wall)" if _overlay_mode else "prop placement"),
		("ON" if _compare_mode else "off"),
		int(round(_doom_level * 100.0)),
		("ON" if _anchor_glow_on else "off"),
		String(_GLOW_FLAVOURS[_glow_flavour_idx % _GLOW_FLAVOURS.size()]["name"]),
		_overlays.size()]
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
	_asset_status.text = "tier: %s   |   props offered: %d   |   placed: %d   |   furniture: %d+%d\n%s\n%s\ncats: %s\nloaded: %s" % [
		_pool_tier(), _prop_pool.size(), _placed_props.size(),
		_furniture.size(), _furniture_b.size(),
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
	# Anchor Sockets V2 sets FIRST (so the first spawned cats demo the anchors),
	# then the legacy 2026-07-16 walkers.
	for aset in AnchoredOverlay.sprite_sets():
		var asf := _build_anchored_cat_frames(String(aset))
		if asf != null:
			_cat_frame_sets.append({"name": String(aset), "frames": asf, "anchored_set": String(aset)})
			loaded.append(String(aset) + "*")
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
		_cat_walk_report = "REAL cat walkers: %s (* = anchor-socket set)   |   still NEED walk-frames (pixellab): %s" % [
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
		# #913 splice seam: optional alternate loop frames (walk_<facing>_alt_<n>.png,
		# e.g. the butt-flash strut) load into "walk_<facing>_alt"; RealCat splices
		# them in deterministically when present. No files -> no clip -> hook dormant.
		var alt_clip := clip + "_alt"
		var ai := 0
		while true:
			var ap := "%s/walk_%s_alt_%d.png" % [dir_abs, facing, ai]
			if not FileAccess.file_exists(ap):
				break
			var atex := _load_texture(ap)
			if atex == null:
				break
			if not sf.has_animation(alt_clip):
				sf.add_animation(alt_clip)
				sf.set_animation_loop(alt_clip, true)
				sf.set_animation_speed(alt_clip, 10.0)
			sf.add_frame(alt_clip, atex)
			ai += 1
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
# ANCHOR SOCKETS V2 (#894): promoted-clip walkers + part-anchored doom glow.
# ===========================================================================
# Build a walker SpriteFrames for one anchor_sockets.json sprite set. The JSON
# is the SSOT for WHERE each promoted clip's frames live (source_dir, repo-root
# relative) and which frame range is used (butt-flash splices 2..8), so the
# walker and its anchors cannot drift apart. Returns null when the art is
# absent (fresh checkout without art_source) -- degrades like the legacy path.
func _build_anchored_cat_frames(sprite_set: String) -> SpriteFrames:
	var repo_root := (_art_root + "/..").simplify_path()
	var clips: Dictionary = AnchoredOverlay.sprite_entry(sprite_set).get("clips", {})
	if clips.is_empty():
		return null
	var sf := SpriteFrames.new()
	var made_any := false
	var first := true
	for clip in clips.keys():
		var entry: Dictionary = clips[clip]
		var dir_abs := (repo_root + "/" + String(entry.get("source_dir", ""))).simplify_path()
		var lo := 0
		var hi := 9999
		var rng: Array = entry.get("frames", [])
		if rng.size() == 2:
			lo = int(rng[0])
			hi = int(rng[1])
		var added := 0
		for i in range(lo, hi + 1):
			var p := "%s/frame_%03d.png" % [dir_abs, i]
			if not FileAccess.file_exists(p):
				break
			var tex := _load_texture(p)
			if tex == null:
				break
			if first:
				sf.rename_animation("default", String(clip))
				first = false
			elif not sf.has_animation(String(clip)):
				sf.add_animation(String(clip))
			sf.set_animation_loop(String(clip), true)
			# 8 fps = the cat-sweep review-sheet playback convention.
			sf.set_animation_speed(String(clip), 8.0 if String(clip) != "idle" else 1.0)
			sf.add_frame(String(clip), tex)
			added += 1
		if added > 0:
			made_any = true
	return sf if made_any else null

# Load one looping SpriteFrames per glow flavour (Pip's interim colour mapping
# 2026-07-26). Missing art -> null slot; the demo skips it.
func _load_glow_flavours() -> void:
	_glow_flavour_frames.clear()
	for fl in _GLOW_FLAVOURS:
		_glow_flavour_frames.append(_build_overlay_frames(
			(_art_root + "/" + String(fl["rel"])).simplify_path()))

# Overlay loop dir -> SpriteFrames ("glow" anim; loop/frame_*.png, idle.png
# fallback for loop-less variants).
func _build_overlay_frames(dir_abs: String) -> SpriteFrames:
	var sf := SpriteFrames.new()
	sf.rename_animation("default", "glow")
	sf.set_animation_loop("glow", true)
	sf.set_animation_speed("glow", 8.0)
	var i := 0
	while true:
		var p := "%s/loop/frame_%03d.png" % [dir_abs, i]
		if not FileAccess.file_exists(p):
			break
		var tex := _load_texture(p)
		if tex == null:
			break
		sf.add_frame("glow", tex)
		i += 1
	if sf.get_frame_count("glow") == 0:
		var idle_tex := _load_texture(dir_abs + "/idle.png")
		if idle_tex == null:
			return null
		sf.add_frame("glow", idle_tex)
	return sf

func _current_glow_frames() -> SpriteFrames:
	if _glow_flavour_frames.is_empty():
		return null
	return _glow_flavour_frames[_glow_flavour_idx % _glow_flavour_frames.size()]

func _toggle_anchor_glow() -> void:
	_anchor_glow_on = not _anchor_glow_on
	for cat in _cats:
		if is_instance_valid(cat) and cat is RealCat:
			(cat as RealCat).set_anchor_glow_enabled(_anchor_glow_on)
	_last_msg = "anchor-socket glow %s" % ("ON" if _anchor_glow_on else "off")

func _cycle_glow_flavour() -> void:
	if _GLOW_FLAVOURS.is_empty():
		return
	_glow_flavour_idx = (_glow_flavour_idx + 1) % _GLOW_FLAVOURS.size()
	var frames := _current_glow_frames()
	for cat in _cats:
		if is_instance_valid(cat) and cat is RealCat:
			(cat as RealCat).set_glow_frames(frames)
	_last_msg = "doom glow flavour: %s%s" % [
		String(_GLOW_FLAVOURS[_glow_flavour_idx]["name"]),
		"" if frames != null else " (art missing -- glow hidden)"]

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
		# Pass 3 cat-worker avoidance: registering in the floor's cat group opts
		# this cat into OfficeFloor's deterministic separation pass (workers
		# barely deflect for cats; cats yield more -- see office_floor.gd).
		add_to_group(OfficeFloor.CAT_GROUP)
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
	# #899 scale unification: cat and human sizes derive from the SAME on-screen
	# tile unit (OfficeEmployeeSprite.TILE_PX = 64px; humans target CHAR_TARGET_H
	# = 2 tiles = 128px). Cat art: 68x68 canvas, opaque subject ~34px tall.
	# Target height comes from the SHARED cat ratio (#913 sneaky 1.1x: 0.5 ->
	# 0.55 tile via OfficeEmployeeSprite.CAT_TILE_RATIO -- one constant, all cats).
	const CAT_SUBJECT_H := 34.0
	const CAT_TARGET_H := OfficeEmployeeSprite.TILE_PX * OfficeEmployeeSprite.CAT_TILE_RATIO
	const ART_SCALE := CAT_TARGET_H / CAT_SUBJECT_H
	var cat_id: String = "cat"           # stable id seeding the alt-clip splice hash
	var _frames: SpriteFrames = null
	var _anim: AnimatedSprite2D = null
	# Anchor Sockets V2 (#894): part-anchored doom glow. Intensity carries the
	# doom level (Pip interim colour ruling 2026-07-26): SUBTLE at nominal.
	const EYE_GLOW_MIN := 0.14
	const EYE_GLOW_MAX := 0.85
	const BUTT_GLOW_MIN := 0.22
	const BUTT_GLOW_MAX := 0.95
	const EYE_GLOW_SCALE := 0.20         # overlay is a 64px canvas; ~13px over the eyes
	const BUTT_GLOW_SCALE := 0.40
	var anchored_set: String = ""
	var _glow_frames: SpriteFrames = null
	var _glow_enabled := true
	var _eye_ov: AnchoredOverlay = null
	var _butt_ov: AnchoredOverlay = null
	# #913 alt-clip splice (cat contract: "walk_<dir>_alt", e.g. walk_north_alt --
	# the butt-flash loop). Same deterministic 1-in-N mechanism as the workers
	# (OfficeEmployeeSprite.should_play_alt); art arrives from the cat sweep later.
	var _loops := 0
	var _alt_active := false
	var _alt_base := ""

	func setup(frames: SpriteFrames, id: String = "cat") -> void:
		_frames = frames
		cat_id = id

	## Anchor Sockets V2: opt this cat into part-anchored glow (call before the
	## cat enters the tree; overlays are built in _build_visual).
	func configure_anchor_glow(set_id: String, glow_frames: SpriteFrames, enabled: bool) -> void:
		anchored_set = set_id
		_glow_frames = glow_frames
		_glow_enabled = enabled

	func set_anchor_glow_enabled(on: bool) -> void:
		_glow_enabled = on
		for ov in [_eye_ov, _butt_ov]:
			if ov != null:
				ov.set_enabled(on)

	## Swap the glow hue flavour (Pip interim colour mapping) live.
	func set_glow_frames(glow_frames: SpriteFrames) -> void:
		_glow_frames = glow_frames
		for ov in [_eye_ov, _butt_ov]:
			if ov != null:
				ov.set_overlay_frames(glow_frames)

	func _build_visual() -> void:
		_anim = AnimatedSprite2D.new()
		_anim.sprite_frames = _frames
		_anim.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_anim.scale = Vector2(ART_SCALE, ART_SCALE)
		_anim.animation_looped.connect(_on_anim_looped)
		_anim.animation_finished.connect(_on_anim_finished)
		add_child(_anim)
		if _frames != null and _frames.has_animation("idle"):
			_anim.play("idle")
		elif _frames != null and _frames.get_animation_names().size() > 0:
			_anim.play(_frames.get_animation_names()[0])
		# Anchor Sockets V2 overlays: eyes on every clip with an 'eyes' socket;
		# butt auto-appears ONLY on clips carrying a 'butt' socket (rear-facing
		# walks + butt-flash splices) -- AnchoredOverlay hides itself otherwise.
		if anchored_set != "" and _glow_frames != null:
			_eye_ov = AnchoredOverlay.new()
			_eye_ov.attach(_anim, anchored_set, "eyes", _glow_frames,
				{"scale": EYE_GLOW_SCALE, "opacity": EYE_GLOW_MIN, "blend": "add",
				"pulse": true, "z_offset": 1})
			_butt_ov = AnchoredOverlay.new()
			_butt_ov.attach(_anim, anchored_set, "butt", _glow_frames,
				{"scale": BUTT_GLOW_SCALE, "opacity": BUTT_GLOW_MIN, "blend": "add",
				"pulse": true, "z_offset": 1})
			set_anchor_glow_enabled(_glow_enabled)
			_apply_glow_doom()

	func _apply_glow_doom() -> void:
		if _eye_ov != null:
			_eye_ov.set_base_opacity(lerpf(EYE_GLOW_MIN, EYE_GLOW_MAX, _doom))
		if _butt_ov != null:
			_butt_ov.set_base_opacity(lerpf(BUTT_GLOW_MIN, BUTT_GLOW_MAX, _doom))

	func _on_tick(dirv: Vector2, moving: bool, _delta: float) -> void:
		if _anim == null or _frames == null:
			return
		var wanted := ""
		if not moving:
			if _frames.has_animation("idle"):
				wanted = "idle"
		else:
			var clip := "walk_" + _dir_name(dirv)
			if _frames.has_animation(clip):
				wanted = clip
		if wanted == "":
			return
		if _alt_active:
			if wanted == _alt_base:
				return               # let the spliced alt play its one pass
			_alt_active = false      # direction/idle change cancels the splice
			_alt_base = ""
		if _anim.animation != wanted:
			_anim.play(wanted)

	# #913 splice: on each completed base loop, deterministically (hash of cat id
	# + loop count, ~1-in-6) play "<clip>_alt" once, then return to the base clip.
	func _on_anim_looped() -> void:
		if _alt_active:
			_end_alt()
			return
		_loops += 1
		var base := String(_anim.animation)
		if base.ends_with(OfficeEmployeeSprite.ALT_CLIP_SUFFIX):
			return
		var alt := base + OfficeEmployeeSprite.ALT_CLIP_SUFFIX
		if _frames != null and _frames.has_animation(alt) \
				and OfficeEmployeeSprite.should_play_alt(cat_id, _loops):
			_alt_active = true
			_alt_base = base
			_anim.play(alt)

	func _on_anim_finished() -> void:
		if _alt_active:
			_end_alt()

	func _end_alt() -> void:
		_alt_active = false
		var back := _alt_base
		_alt_base = ""
		if _frames != null and _frames.has_animation(back):
			_anim.play(back)

	func _on_doom() -> void:
		if _anim != null:
			_anim.self_modulate = Color(1, 1, 1, 1).lerp(Color(1.0, 0.35, 0.28, 1.0), _doom * 0.7)
		_apply_glow_doom()

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

extends Control
class_name OfficeFloor
## Standalone, reusable office-floor VIEW for the WATCH screen.
##
## PURE VIEW (ADR-0006, non-negotiable): it READS a roster SNAPSHOT (an Array of
## plain Dictionaries -- copied values, never a live GameState reference) and
## renders milling employees. It NEVER writes game state and nothing it does
## feeds back into the sim, so it is determinism-safe by construction: replay
## replays inputs->state, and a cosmetic view cannot alter a verified run. Sprite
## wander randomness is cosmetic and deliberately does NOT use the seeded game RNG.
##
## PUBLIC API
##   set_roster(snapshot: Array)   # array of employee dicts; adds/updates/removes sprites
##   set_tier(t: int)              # 0 = placeholder blobs+hats, 1 = AnimatedSprite2D FSM
##   tier                          # property (get/set)
##   set_sprite_frames(frames)     # optional: real pixellab.ai art for Tier 1
##   OfficeFloor.snapshot_from_state(state) -> Array   # static, read-only GameState adapter
##
## Employee snapshot dict fields (ALL optional; unknown fields ignored; see
## EmployeeFSM for the state mapping and graceful-degrade rules):
##   id:String/int, name:String, specialization:String,
##   burnout:float(0-100), loyalty:int(0-100), unmanaged:bool, assigned:bool
##
## Scaling note: designed for 1..~12 sprites (Startup/Entity phases). For the
## Titan phase (hundreds of staff) the intended approach is NOT one sprite each --
## aggregate into division "pods"/heatmap tiles fed the same snapshot. That
## aggregation is deliberately NOT built here (see build brief Tier 2/phase-scaling).

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")

# Promoted pixellab.ai art (2026-07-21 re-roll sweep) for the WATCH office backdrop.
# The floor is a top-down Wang tileset atlas; we tile its all-"lower" base tile. Props are
# top-down map objects drawn feet-anchored at the cosmetic landmark zones. PURELY cosmetic
# (ADR-0006): drawing them reads nothing from and writes nothing to game state.
const FLOOR_ATLAS := preload("res://assets/office_floor/tilesets/floor_concrete.png")
const PROP_WATER_COOLER := preload("res://assets/office_floor/props/water_cooler.png")
const PROP_FILING_CABINET := preload("res://assets/office_floor/props/filing_cabinet.png")
const PROP_SERVER := preload("res://assets/office_floor/props/server_cluster.png")
# Region of the 4x4 Wang atlas holding the all-lower base floor tile (wang_0; bounding_box
# per the source tileset metadata in art_source/pixellab_2026-07-21-rerolls/tilesets/).
# Cropped once into a standalone tileable texture.
const FLOOR_BASE_REGION := Rect2i(64, 32, 32, 32)
const PROP_TARGET_H := 30.0                    # draw props scaled to this pixel height (art varies)
const FLOOR_DIM := Color(0.62, 0.63, 0.66)     # tint floor/props muted so sprites + UI read over them

@export var tier: int = 0: set = set_tier
# Deferred seams (build brief "Deferred to later waves"): office aesthetic tier and
# moral skew. Declared cheaply now so later art/logic has an anchor; currently unused.
@export var office_tier: int = 0
@export var moral_skew: float = 0.0

# Specialization -> body colour (readout of role on the floor).
const SPEC_COLORS := {
	"safety":           Color(0.35, 0.75, 0.45),
	"capabilities":     Color(0.85, 0.45, 0.30),
	"interpretability": Color(0.55, 0.55, 0.9),
	"alignment":        Color(0.4, 0.75, 0.8),
	"manager":          Color(0.8, 0.75, 0.4),
}
const DEFAULT_BODY_COLOR := Color(0.6, 0.6, 0.65)
const HAT_COLOR := Color(0.14, 0.14, 0.18)

const COLLAB_CHECK_RANGE := Vector2(2.5, 5.0)   # seconds between collaboration attempts
const COLLAB_START_CHANCE := 0.5                # chance to actually pair when eligible

var _sprites: Dictionary = {}   # id -> OfficeEmployeeSprite
var _shared_frames: SpriteFrames = null   # optional real art shared across sprites
var _rng := RandomNumberGenerator.new()   # cosmetic-only (collaboration timing); NOT the game RNG
var _collab_timer := 0.0
var _floor_tile: Texture2D = null   # base concrete tile cropped from the Wang atlas (cosmetic)

func _ready() -> void:
	custom_minimum_size = Vector2(360, 260)
	_floor_tile = _build_floor_tile()
	_rng.randomize()
	_collab_timer = _rng.randf_range(COLLAB_CHECK_RANGE.x, COLLAB_CHECK_RANGE.y)
	resized.connect(_on_resized)
	queue_redraw()

# Collaboration is orchestrated HERE because the floor knows who else is working.
# Pure view: it only sends a cosmetic pair-up target to a sprite; no game state.
func _process(delta: float) -> void:
	_collab_timer -= delta
	if _collab_timer <= 0.0:
		_collab_timer = _rng.randf_range(COLLAB_CHECK_RANGE.x, COLLAB_CHECK_RANGE.y)
		_maybe_start_collaboration()

func _maybe_start_collaboration() -> void:
	var available: Array = []
	for id in _sprites:
		var s: OfficeEmployeeSprite = _sprites[id]
		if s.is_at_desk():
			available.append(s)
	if available.size() < 2 or _rng.randf() >= COLLAB_START_CHANCE:
		return
	var a: OfficeEmployeeSprite = available[_rng.randi() % available.size()]
	var b: OfficeEmployeeSprite = available[_rng.randi() % available.size()]
	if a != b:
		a.try_start_collaboration(b.desk_pos)

func _on_resized() -> void:
	# Keep everyone inside the new bounds.
	var b := _bounds()
	for id in _sprites:
		var spr: OfficeEmployeeSprite = _sprites[id]
		spr.bounds = b
	_relayout_desks()
	queue_redraw()

func _bounds() -> Rect2:
	var s := size
	if s.x < 40.0 or s.y < 40.0:
		s = custom_minimum_size
	return Rect2(Vector2(8, 8), s - Vector2(16, 16))

## Replace/refresh the rendered roster from a snapshot (read-only; copies values).
func set_roster(snapshot: Array) -> void:
	var b := _bounds()
	var z := _zones(b)
	var seen: Dictionary = {}
	var total := snapshot.size()
	for i in range(total):
		var emp = snapshot[i]
		if not (emp is Dictionary):
			continue
		var id = emp.get("id", emp.get("name", str(i)))
		seen[id] = true
		var state := EmployeeFSM.map_state(emp)
		var spec := String(emp.get("specialization", ""))
		var body: Color = SPEC_COLORS.get(spec, DEFAULT_BODY_COLOR)
		var desk := _desk_for_index(i, total, b)
		var cfg := {
			"state": state, "name": String(emp.get("name", str(id))),
			"body_color": body, "hat_color": HAT_COLOR, "desk_pos": desk,
			"fridge_pos": z["fridge_pos"], "water_pos": z["water_pos"],
			"cat_pos": z["cat_pos"], "window_pos": z["window_pos"],
		}
		if _sprites.has(id):
			var spr: OfficeEmployeeSprite = _sprites[id]
			spr.bounds = b
			spr.configure(cfg)
		else:
			var spr2: OfficeEmployeeSprite = EmployeeSpriteScript.new()
			spr2.tier = tier
			spr2.bounds = b
			spr2.position = desk
			add_child(spr2)
			spr2.configure(cfg)
			if _shared_frames != null:
				spr2.set_sprite_frames(_shared_frames)
			_sprites[id] = spr2
	# Remove sprites for employees no longer present.
	for id in _sprites.keys():
		if not seen.has(id):
			_sprites[id].queue_free()
			_sprites.erase(id)
	queue_redraw()

## Number of employee sprites currently on the floor (the walker count). Read-only;
## the WATCH integration + its guard test assert this tracks the live staff count.
func sprite_count() -> int:
	return _sprites.size()

func set_tier(t: int) -> void:
	tier = t
	for id in _sprites:
		_sprites[id].set_tier(t)
	queue_redraw()

## Supply a real Tier-1 SpriteFrames (animations: idle/walking/working/stressed).
func set_sprite_frames(frames: SpriteFrames) -> void:
	_shared_frames = frames
	for id in _sprites:
		_sprites[id].set_sprite_frames(frames)

func _relayout_desks() -> void:
	var b := _bounds()
	var z := _zones(b)
	var ids := _sprites.keys()
	var total := ids.size()
	for i in range(total):
		var spr: OfficeEmployeeSprite = _sprites[ids[i]]
		spr.desk_pos = _desk_for_index(i, total, b)
		spr.fridge_pos = z["fridge_pos"]
		spr.water_pos = z["water_pos"]
		spr.cat_pos = z["cat_pos"]
		spr.window_pos = z["window_pos"]

# Cosmetic destination LANDMARKS derived from the floor bounds -- placed at distinct
# spots so a walking employee's destination reads at a glance (Tier-1 named points,
# not a navmesh). window along the top wall; three corners: cat / water cooler /
# fridge. Desks cluster around tables in the central band (see _table_centers).
func _zones(b: Rect2) -> Dictionary:
	var inset := Vector2(b.size.x * 0.10, b.size.y * 0.12)
	return {
		"window_pos": b.position + Vector2(b.size.x * 0.5, b.size.y * 0.07),
		"cat_pos":    b.position + Vector2(inset.x, b.size.y - inset.y),                 # bottom-left
		"water_pos":  b.position + Vector2(b.size.x - inset.x, inset.y),                 # top-right
		"fridge_pos": b.position + Vector2(b.size.x - inset.x, b.size.y - inset.y),      # bottom-right
	}

# A couple of table centres in the central band (kept clear of the corner landmarks).
func _table_centers(b: Rect2) -> Array:
	var cy := b.position.y + b.size.y * 0.48
	return [
		b.position + Vector2(b.size.x * 0.36, cy - b.position.y),
		b.position + Vector2(b.size.x * 0.64, cy - b.position.y),
	]

# Desks semi-clustered around the tables (NOT a grid): employee i joins table
# i % num_tables and sits at a ring slot around it. Stable per index.
func _desk_for_index(i: int, _total: int, b: Rect2) -> Vector2:
	var tables := _table_centers(b)
	var t := i % tables.size()
	var slot := i / tables.size()
	var radius: float = min(b.size.x, b.size.y) * 0.16
	var angle := float(slot) * (TAU / 3.0) + float(t) * 0.6   # offset the two rings so they don't mirror
	return tables[t] + Vector2(cos(angle), sin(angle) * 0.7) * radius

# Crop the all-lower base floor tile out of the Wang atlas into a standalone tileable
# texture (runs once, cosmetic). Returns null on failure -> _draw falls back to a flat fill.
func _build_floor_tile() -> Texture2D:
	if FLOOR_ATLAS == null:
		return null
	var atlas_img := FLOOR_ATLAS.get_image()
	if atlas_img == null:
		return null
	var r := FLOOR_BASE_REGION
	if r.position.x + r.size.x > atlas_img.get_width() or r.position.y + r.size.y > atlas_img.get_height():
		return null
	return ImageTexture.create_from_image(atlas_img.get_region(r))

# Draw a promoted prop texture centred horizontally on `at`, feet-anchored (bottom edge at
# `at`) so it sits on the floor, scaled to PROP_TARGET_H (aspect kept) and dimmed to match.
func _draw_prop(tex: Texture2D, at: Vector2) -> void:
	if tex == null:
		return
	var src := tex.get_size()
	if src.y <= 0.0:
		return
	var scl := PROP_TARGET_H / src.y
	var w := src.x * scl
	var rect := Rect2(at - Vector2(w * 0.5, PROP_TARGET_H), Vector2(w, PROP_TARGET_H))
	draw_texture_rect(tex, rect, false, FLOOR_DIM)

# --- Floor background (tier-agnostic; sprites draw on top) ------------------
func _draw() -> void:
	var b := _bounds()
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.09, 0.10, 0.11))       # room
	# Floor: tile the promoted concrete Wang base tile if available, else a flat fill.
	if _floor_tile != null:
		draw_texture_rect(_floor_tile, b, true, FLOOR_DIM)               # tiled concrete
		draw_rect(b, Color(0.05, 0.06, 0.07, 0.34))                     # dim veil so UI/sprites read
	else:
		draw_rect(b, Color(0.13, 0.15, 0.16))                          # procedural fallback floor
	draw_rect(b, Color(0.3, 0.5, 0.35, 0.5), false, 1.5)              # bounds outline
	# tables (desks cluster around these)
	for c in _table_centers(b):
		var r: float = min(b.size.x, b.size.y) * 0.10
		draw_circle(c, r, Color(0.2, 0.22, 0.24, 0.7))
		draw_arc(c, r, 0.0, TAU, 20, Color(0.3, 0.33, 0.36, 0.8), 1.5)
	# faint desk markers around the tables
	var total := _sprites.size()
	for i in range(total):
		var d := _desk_for_index(i, total, b)
		draw_rect(Rect2(d + Vector2(-13, 5), Vector2(26, 5)), Color(0.25, 0.27, 0.29, 0.6))
	# cosmetic landmark markers (window / cat / water cooler / fridge). Promoted pixellab
	# props stand in for the water/fridge markers + add a server-cluster decor piece; the
	# window strip + cat corner stay procedural (cat art deferred to the #758 identity pass).
	var z := _zones(b)
	draw_rect(Rect2(Vector2(b.position.x + 6, b.position.y + 2), Vector2(b.size.x - 12, 5)), Color(0.45, 0.6, 0.75, 0.45))  # window strip (top wall)
	draw_circle(z["cat_pos"], 9.0, Color(0.9, 0.5, 0.7, 0.4))            # cat corner (pink)
	_draw_prop(PROP_WATER_COOLER, z["water_pos"])                       # water cooler (top-right)
	_draw_prop(PROP_FILING_CABINET, z["fridge_pos"])                    # filing cabinet appliance (bottom-right)
	_draw_prop(PROP_SERVER, b.position + Vector2(b.size.x * 0.12, b.size.y * 0.18))  # server cluster decor (top-left)

# ---------------------------------------------------------------------------
# READ-ONLY GameState adapter. Static so callers can build a snapshot without
# an OfficeFloor instance. Reads only; writes nothing. The integration lane
# calls this each day-tick and hands the result to set_roster().
# ---------------------------------------------------------------------------
static func snapshot_from_state(state) -> Array:
	var out: Array = []
	if state == null:
		return out
	var researchers: Array = state.researchers if "researchers" in state else []
	var total := researchers.size()
	# get_unmanaged_count() reports how many exceed management capacity; we mark
	# the trailing N as the drifting/unmanaged ones (view heuristic -- order-only).
	var unmanaged_n := 0
	if state.has_method("get_unmanaged_count"):
		unmanaged_n = state.get_unmanaged_count()
	for i in range(total):
		var r = researchers[i]
		out.append({
			"id": i,
			"name": r.researcher_name if "researcher_name" in r else str(i),
			"specialization": r.specialization if "specialization" in r else "",
			"burnout": float(r.burnout) if "burnout" in r else 0.0,
			"loyalty": int(r.loyalty) if "loyalty" in r else 50,
			"unmanaged": i >= (total - unmanaged_n),
			"assigned": true,   # employed researchers are working their specialization
		})
	return out

# ---------------------------------------------------------------------------
# READ-ONLY adapter for the SERIALIZED game-state Dictionary (GameState.to_dict()) --
# the shape delivered by GameManager.game_state_updated -> main_ui -> WatchScreen. Same
# output contract as snapshot_from_state() but reads plain dict fields ("researchers" is an
# Array of Researcher.to_dict() dicts). Copies values only; writes nothing; determinism-safe.
# appearance_id is carried through untouched so the Friday identity / portrait-variant-pool
# mapping (#758) can consume it later with no signature change here.
# ---------------------------------------------------------------------------
static func snapshot_from_state_dict(state: Dictionary) -> Array:
	var out: Array = []
	if not state.has("researchers"):
		return out
	var researchers = state.get("researchers", [])
	if not (researchers is Array):
		return out
	var total: int = researchers.size()
	var unmanaged_n := int(state.get("unmanaged_count", 0))
	for i in range(total):
		var r = researchers[i]
		if not (r is Dictionary):
			continue
		out.append({
			"id": i,
			"name": String(r.get("name", str(i))),
			"specialization": String(r.get("specialization", "")),
			"burnout": float(r.get("burnout", 0.0)),
			"loyalty": int(r.get("loyalty", 50)),
			"unmanaged": i >= (total - unmanaged_n),
			"assigned": true,
			"appearance_id": r.get("appearance_id", i),   # seam for #758 identity mapping
		})
	return out

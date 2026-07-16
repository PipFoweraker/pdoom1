extends Control
class_name OfficeFloor
## Standalone, reusable office-floor VIEW for the WATCH screen.
##
## PURE VIEW (ADR-0006, non-negotiable): it READS a roster SNAPSHOT (an Array of
## plain Dictionaries — copied values, never a live GameState reference) and
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
## Titan phase (hundreds of staff) the intended approach is NOT one sprite each —
## aggregate into division "pods"/heatmap tiles fed the same snapshot. That
## aggregation is deliberately NOT built here (see build brief Tier 2/phase-scaling).

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")

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

var _sprites: Dictionary = {}   # id -> OfficeEmployeeSprite
var _shared_frames: SpriteFrames = null   # optional real art shared across sprites

func _ready() -> void:
	custom_minimum_size = Vector2(360, 260)
	resized.connect(_on_resized)
	queue_redraw()

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
		if _sprites.has(id):
			var spr: OfficeEmployeeSprite = _sprites[id]
			spr.bounds = b
			spr.configure({
				"state": state, "name": String(emp.get("name", str(id))),
				"body_color": body, "hat_color": HAT_COLOR, "desk_pos": desk,
			})
		else:
			var spr2: OfficeEmployeeSprite = EmployeeSpriteScript.new()
			spr2.tier = tier
			spr2.bounds = b
			spr2.position = desk
			add_child(spr2)
			spr2.configure({
				"state": state, "name": String(emp.get("name", str(id))),
				"body_color": body, "hat_color": HAT_COLOR, "desk_pos": desk,
			})
			if _shared_frames != null:
				spr2.set_sprite_frames(_shared_frames)
			_sprites[id] = spr2
	# Remove sprites for employees no longer present.
	for id in _sprites.keys():
		if not seen.has(id):
			_sprites[id].queue_free()
			_sprites.erase(id)
	queue_redraw()

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
	var ids := _sprites.keys()
	var total := ids.size()
	for i in range(total):
		_sprites[ids[i]].desk_pos = _desk_for_index(i, total, b)

# Simple stable grid of desks across the floor interior.
func _desk_for_index(i: int, total: int, b: Rect2) -> Vector2:
	var n := maxi(total, 1)
	var cols := int(ceil(sqrt(float(n))))
	var rows := int(ceil(float(n) / float(cols)))
	var col := i % cols
	var row := i / cols
	var cell := Vector2(b.size.x / float(cols), b.size.y / float(rows))
	return b.position + Vector2((col + 0.5) * cell.x, (row + 0.5) * cell.y)

# --- Floor background (tier-agnostic; sprites draw on top) ------------------
func _draw() -> void:
	var b := _bounds()
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.09, 0.10, 0.11))       # room
	draw_rect(b, Color(0.13, 0.15, 0.16))                              # floor
	draw_rect(b, Color(0.3, 0.5, 0.35, 0.5), false, 1.5)              # bounds outline
	# faint desk markers
	var total := _sprites.size()
	for i in range(total):
		var d := _desk_for_index(i, total, b)
		draw_rect(Rect2(d + Vector2(-14, 6), Vector2(28, 6)), Color(0.25, 0.27, 0.29, 0.6))

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
	# the trailing N as the drifting/unmanaged ones (view heuristic — order-only).
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

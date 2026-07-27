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
##   set_sprite_frames(frames)     # optional: FALLBACK shared art for Tier 1
##   set_use_variant_pool(on)      # per-worker appearance variants (WorkerVariantPool); default ON
##   set_extra_blocked_rects(a)    # additive dev hook: extra no-stand prop footprints (sandbox)
##   approach_point_for(landmark, requester_id) -> Vector2  # pass 3: free approach slot, or landmark unchanged
##   OfficeFloor.snapshot_from_state(state) -> Array   # static, read-only GameState adapter
##
## Cats (pass 3): any Node2D child in group CAT_GROUP ("office_floor_cats")
## joins the separation pass -- cats and workers avoid each other with the
## asymmetric weights below. The sandbox cats register themselves; a future
## live cat only needs add_to_group(OfficeFloor.CAT_GROUP).
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
# #770: integer nearest-neighbor upscale of the base floor tile so the concrete reads
# at a sensible scale in the WATCH strip (the atlas tiles are 32px, which tiled tiny).
const FLOOR_TILE_SCALE := 2
# LEGACY fallback only (#907 integration): props with a manifest entry render at their
# authored proportions via PropCatalogue; PROP_TARGET_H remains the force-scale for any
# texture drawn WITHOUT a manifest id (PropCatalogue's own fallback reproduces it too).
const PROP_TARGET_H := 46.0                    # #770: props drawn larger (was 30) to match the bigger floor
# One floor tile on screen: 32 px art displayed at FLOOR_TILE_SCALE (matches
# OfficeEmployeeSprite.TILE_PX = 64). PropCatalogue heights are in tiles of this size.
const DISPLAY_TILE_PX := 32.0 * FLOOR_TILE_SCALE
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

# --- Pass 3: cat-worker mutual avoidance -------------------------------------
# Cats and workers repel each other through the SAME deterministic separation
# pass as worker-worker (positions only, order-independent snapshot, no RNG).
# Cats participate by group membership: any Node2D child of the floor in
# CAT_GROUP is steered directly by the floor each frame.
# ASYMMETRIC weights (a weight scales how hard THAT neighbour pushes THIS mover):
#   WORKER_FOR_CAT 0.25 -- a worker barely deflects for a cat: max push
#     0.25 * SEPARATION_STRENGTH(40) = 10 px/s vs walk speed 42 -- a visible
#     shoulder-turn that can never stall an arrival.
#   CAT_FOR_WORKER 1.6 -- a cat yields readily: 1.6 * 40 = 64 px/s exceeds the
#     cat wander speed (30), so the worker's personal space wins and the cat
#     detours around instead of clipping through.
#   CAT_FOR_CAT 1.0 -- cats keep out of each other at the plain worker weight.
const CAT_GROUP := "office_floor_cats"
const SEP_WEIGHT_WORKER_FOR_CAT := 0.25
const SEP_WEIGHT_CAT_FOR_WORKER := 1.6
const SEP_WEIGHT_CAT_FOR_CAT := 1.0

# #913 water-cooler bubbles -> pass-3 ORGANIC bursts (Pip 2026-07-26: "make
# them way more intermittent and seemingly-random -- if you have 2 firing on
# slightly off-kilter timers, it seems organic."). Bubble EVENTS are sparse:
# each of TWO independent emitters fires one short BUBBLE_FRAMES-frame rise per
# period, then stays quiet.
# NO-COMMON-MULTIPLE PRINCIPLE (copy this pattern for future ambient juice):
# the two base periods 7.3 s and 11.9 s are incommensurate -- they share no
# short common multiple (the joint pattern realigns only every
# 7.3 * 11.9 ~= 86.9 s), so the combined burst rhythm never visibly repeats
# inside a sitting. Each emitter also gets a DETERMINISTIC per-prop phase
# offset hashed from the prop's position (ADR-0006: cosmetic yet reproducible,
# no RNG draws), so two coolers on screen would not fire in sync either.
const BUBBLE_FRAMES := 3
const BUBBLE_FRAME_TIME := 0.35                 # burst = 3 * 0.35 ~= 1 s of rise
const BUBBLE_EMITTER_PERIODS: Array[float] = [7.3, 11.9]
const BUBBLE_COLOR := Color(0.85, 0.95, 1.0, 0.38)

# Pass 3 approach slots (prop manifest v1.2 `approach_px`): a slot is taken
# when another sprite stands within this radius of it (or is navigating to it).
const APPROACH_SLOT_CLAIM_RADIUS := 10.0

var _sprites: Dictionary = {}   # id -> OfficeEmployeeSprite
var _shared_frames: SpriteFrames = null   # FALLBACK art shared across sprites
# Worker appearance variants (#793 mechanism half): when ON (default), each
# sprite's SpriteFrames comes from WorkerVariantPool keyed by the snapshot's
# appearance_id; any unresolved variant falls back to _shared_frames. Variant 0
# is wired to the current shared asset, so behaviour is unchanged until new
# worker art is triaged in. The sandbox turns this OFF for colour-skin previews.
var _use_variant_pool := true
var _appearance: Dictionary = {}          # sprite id -> appearance_id (for reapplies)
# Tier-1 collision: floor-local no-stand rects built from landmark-prop
# footprints (PropCatalogue) + any extra rects a host supplies (sandbox props).
var _blocked_rects: Array = []
var _extra_blocked_rects: Array = []
# Landmark props on this floor: [{id, feet}] -- rebuilt with the blocked rects;
# feeds the pass-3 approach-slot resolution (approach_point_for).
var _landmark_props: Array = []
# Pass-3 organic bubbles: one monotonic clock; per-emitter last-drawn frame so
# _tick_bubbles only redraws on an actual frame transition.
var _bubble_clock := 0.0
var _bubble_frames_drawn: Array = [-1, -1]
var _rng := RandomNumberGenerator.new()   # cosmetic-only (collaboration timing); NOT the game RNG
var _collab_timer := 0.0
var _floor_tile: Texture2D = null   # base concrete tile cropped from the Wang atlas (cosmetic)
var _wall_strip_tex: Texture2D = null   # ADDITIVE dev-hook override for the top wall strip (cosmetic)
# Office quality tier (canonical ladder: scummy / decent / premium -- see
# docs/game-design/SEED_ASSET_REGISTRY_AND_VERDICTS.md). "" or "decent" = the shipped
# default art. ADDITIVE dev hook like the tile overrides: the live WATCH integration
# never sets it, so its behaviour is unchanged. Cosmetic only (ADR-0006).
var _office_style: String = ""
var _style_tex_cache: Dictionary = {}   # variant manifest id -> Texture2D (loaded once)

func _ready() -> void:
	custom_minimum_size = Vector2(360, 260)
	# #770: nearest-neighbor so the upscaled floor tile + props stay crisp pixel art
	# (sprites already force NEAREST per-node; this covers the floor/prop draws here).
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_floor_tile = _build_floor_tile()
	_rng.randomize()
	_collab_timer = _rng.randf_range(COLLAB_CHECK_RANGE.x, COLLAB_CHECK_RANGE.y)
	resized.connect(_on_resized)
	_rebuild_blocked_rects()
	queue_redraw()

# Collaboration is orchestrated HERE because the floor knows who else is working.
# Pure view: it only sends a cosmetic pair-up target to a sprite; no game state.
func _process(delta: float) -> void:
	_collab_timer -= delta
	if _collab_timer <= 0.0:
		_collab_timer = _rng.randf_range(COLLAB_CHECK_RANGE.x, COLLAB_CHECK_RANGE.y)
		_maybe_start_collaboration()
	_apply_separation(delta)
	_tick_bubbles(delta)

# Tier-1 collision: one separation pass per frame over workers AND cats
# (pass 3). Positions are SNAPSHOTTED before anything moves, so the result is
# independent of iteration order -- fully deterministic from positions alone
# (no RNG; see EmployeeSprite). Workers get the full damped treatment
# (apply_separation); cats -- plain Node2D wanderers with no floor-known nav
# target -- are displaced directly and clamped into the bounds. O(n^2) is fine
# at the 1..24-walker + few-cats scale this floor is scoped to.
func _apply_separation(delta: float) -> void:
	var ids := _sprites.keys()
	var cats := _cat_nodes()
	var n := ids.size() + cats.size()
	if n < 2:
		return
	# Snapshot: workers first (roster order), then cats (child order).
	var pts: Array = []
	var is_cat: Array = []
	for id in ids:
		pts.append((_sprites[id] as Node2D).position)
		is_cat.append(false)
	for c in cats:
		pts.append((c as Node2D).position)
		is_cat.append(true)
	for i in range(n):
		var others: Array = []
		var weights: Array = []
		for j in range(n):
			if j == i:
				continue
			others.append(pts[j])
			if is_cat[i]:
				weights.append(SEP_WEIGHT_CAT_FOR_CAT if is_cat[j] else SEP_WEIGHT_CAT_FOR_WORKER)
			else:
				weights.append(SEP_WEIGHT_WORKER_FOR_CAT if is_cat[j] else 1.0)
		if is_cat[i]:
			var cat := cats[i - ids.size()] as Node2D
			var sep := OfficeEmployeeSprite.separation_vector(
				pts[i], others, OfficeEmployeeSprite.SEPARATION_RADIUS, weights)
			if sep != Vector2.ZERO:
				var b := _bounds()
				cat.position = (cat.position
					+ sep * OfficeEmployeeSprite.SEPARATION_STRENGTH * delta).clamp(b.position, b.end)
		else:
			(_sprites[ids[i]] as OfficeEmployeeSprite).apply_separation(others, delta, weights)

## Node2D children registered as cats (CAT_GROUP). Child order -- deterministic.
func _cat_nodes() -> Array:
	var out: Array = []
	for c in get_children():
		if c is Node2D and (c as Node).is_in_group(CAT_GROUP):
			out.append(c)
	return out

# Pass-3 organic bubbles: advance the emitter clock; redraw only when an
# emitter's burst frame actually changes (sparse events, not a constant loop).
func _tick_bubbles(delta: float) -> void:
	_bubble_clock += delta
	var feet: Vector2 = _zones(_bounds())["water_pos"]
	var changed := false
	for i in range(BUBBLE_EMITTER_PERIODS.size()):
		var f := bubble_frame_at(_bubble_clock, BUBBLE_EMITTER_PERIODS[i],
			bubble_phase_for(feet, BUBBLE_EMITTER_PERIODS[i], i))
		if f != int(_bubble_frames_drawn[i]):
			_bubble_frames_drawn[i] = f
			changed = true
	if changed:
		queue_redraw()

## Deterministic per-prop phase for bubble emitter `emitter_idx` at prop feet
## `pos`: a pure hash of the (whole-pixel) position -- NO RNG draws (ADR-0006).
## The same cooler in the same spot always fires on the same schedule; a second
## cooler elsewhere desyncs automatically. Result is in [0, period).
static func bubble_phase_for(pos: Vector2, period: float, emitter_idx: int = 0) -> float:
	var h := ("bubbles|%d|%.0f,%.0f" % [emitter_idx, pos.x, pos.y]).hash()
	return float(posmod(h, 1000)) / 1000.0 * period

## Pure emitter clock -> burst frame. Returns -1 while the emitter is quiet, or
## 0..BUBBLE_FRAMES-1 during the one short rise it fires per period. A pure
## function of time (no state, no RNG) -- deterministic and unit-testable.
static func bubble_frame_at(t: float, period: float, phase: float) -> int:
	if period <= 0.0:
		return -1
	var local := fposmod(t + phase, period)
	var idx := int(local / BUBBLE_FRAME_TIME)
	return idx if idx < BUBBLE_FRAMES else -1

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
	# Keep everyone inside the new bounds; landmark footprints move with them.
	var b := _bounds()
	_rebuild_blocked_rects()
	for id in _sprites:
		var spr: OfficeEmployeeSprite = _sprites[id]
		spr.bounds = b
		spr.blocked_rects = _blocked_rects
	_relayout_desks()
	queue_redraw()

func _bounds() -> Rect2:
	var s := size
	if s.x < 40.0 or s.y < 40.0:
		s = custom_minimum_size
	return Rect2(Vector2(8, 8), s - Vector2(16, 16))

## Observability only (see godot/autoload/perf_log.gd): the Titan-phase scaling cliff this
## class's own doc comment flags above (hundreds of staff, one-sprite-each not viable) makes
## the roster rebuild the thing worth watching first. A tighter threshold than the 1000 ms
## default (still cosmetic, never touches game state/RNG/scoring, never branched on).
const ROSTER_REBUILD_WARN_MS := 50.0
var _roster_threshold_set := false

## Replace/refresh the rendered roster from a snapshot (read-only; copies values).
func set_roster(snapshot: Array) -> void:
	if not _roster_threshold_set:
		PerfLog.set_threshold("office_roster_rebuild", ROSTER_REBUILD_WARN_MS)
		_roster_threshold_set = true
	var sw := PerfLog.time_section("office_roster_rebuild", {"count": snapshot.size()})
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
		# Appearance seam (#758/#793): appearance_id keys the worker's variant art;
		# absent -> the roster id (stable), so assignment never shuffles on re-set.
		_appearance[id] = emp.get("appearance_id", id)
		var state := EmployeeFSM.map_state(emp)
		var spec := String(emp.get("specialization", ""))
		var body: Color = SPEC_COLORS.get(spec, DEFAULT_BODY_COLOR)
		var desk := _desk_for_index(i, total, b)
		var cfg := {
			"state": state, "name": String(emp.get("name", str(id))),
			"entity_id": str(id),
			"body_color": body, "hat_color": HAT_COLOR, "desk_pos": desk,
			"fridge_pos": z["fridge_pos"], "water_pos": z["water_pos"],
			"cat_pos": z["cat_pos"], "window_pos": z["window_pos"],
		}
		if _sprites.has(id):
			var spr: OfficeEmployeeSprite = _sprites[id]
			spr.bounds = b
			spr.blocked_rects = _blocked_rects
			spr.configure(cfg)
		else:
			var spr2: OfficeEmployeeSprite = EmployeeSpriteScript.new()
			spr2.tier = tier
			spr2.bounds = b
			spr2.blocked_rects = _blocked_rects
			spr2.position = desk
			add_child(spr2)
			spr2.configure(cfg)
			var fr := _resolved_frames(_appearance[id])
			if fr != null:
				spr2.set_sprite_frames(fr)
			_sprites[id] = spr2
	# Remove sprites for employees no longer present.
	for id in _sprites.keys():
		if not seen.has(id):
			_sprites[id].queue_free()
			_sprites.erase(id)
			_appearance.erase(id)
	queue_redraw()
	PerfLog.gauge("office_sprites", _sprites.size())
	sw.stop()

## Number of employee sprites currently on the floor (the walker count). Read-only;
## the WATCH integration + its guard test assert this tracks the live staff count.
func sprite_count() -> int:
	return _sprites.size()

func set_tier(t: int) -> void:
	tier = t
	for id in _sprites:
		_sprites[id].set_tier(t)
	queue_redraw()

## Supply the FALLBACK Tier-1 SpriteFrames (animations: idle/walking/working/
## stressed). With the variant pool ON (default) each sprite still prefers its
## appearance-mapped variant; today variant 0 IS this same shared asset, so the
## two paths render identically until new worker art is triaged in.
func set_sprite_frames(frames: SpriteFrames) -> void:
	_shared_frames = frames
	_reapply_frames()

## Toggle per-worker appearance variants (WorkerVariantPool). The sandbox turns
## this OFF so its colour-skin preview frames apply uniformly; the live WATCH
## integration leaves it ON.
func set_use_variant_pool(enabled: bool) -> void:
	if _use_variant_pool == enabled:
		return
	_use_variant_pool = enabled
	_reapply_frames()

## Frames for one worker: appearance-mapped variant when the pool is on and the
## variant's art resolves; otherwise the shared fallback (graceful degrade).
func _resolved_frames(appearance_id) -> SpriteFrames:
	if _use_variant_pool:
		var f := WorkerVariantPool.frames_for(appearance_id)
		if f != null:
			return f
	return _shared_frames

func _reapply_frames() -> void:
	for id in _sprites:
		var f := _resolved_frames(_appearance.get(id, id))
		if f != null:
			_sprites[id].set_sprite_frames(f)

# ---------------------------------------------------------------------------
# ADDITIVE DEV HOOKS (office sandbox v2). PURELY COSMETIC + backward-compatible:
# they only override the private floor/wall tile textures consumed by _draw().
# Passing null restores the built-in look. The LIVE WATCH integration
# (watch_screen.gd / main_ui.gd) NEVER calls these, so its behaviour is byte-for-
# byte unchanged. They read nothing and write no game state (ADR-0006 pure view).
# Used by office_sandbox.gd to preview promoted tilesets loaded from art_source at
# dev time. Callers supply an already-tileable tile texture (crop/scale is theirs).
# ---------------------------------------------------------------------------
## Override the tiled floor texture. Pass null to restore the built-in concrete tile.
func set_floor_tile_texture(tex: Texture2D) -> void:
	_floor_tile = tex if tex != null else _build_floor_tile()
	queue_redraw()

## Override the top wall strip with a (tileable) texture. Pass null to restore the
## flat procedural strip drawn by _draw().
func set_wall_strip_texture(tex: Texture2D) -> void:
	_wall_strip_tex = tex
	queue_redraw()

## ADDITIVE dev hook: set the office quality tier (canonical ladder scummy/decent/premium).
## Landmark props then prefer a manifest variant "<id>_<style>" whose style_tags carry the
## tier; where that variant art is missing the prop falls back to the decent art UNCHANGED
## (no tinting hacks -- ruled 2026-07-26). "" or "decent" = shipped default art.
func set_office_style(style: String) -> void:
	_office_style = style
	queue_redraw()

## ADDITIVE dev hook (tier-1 collision): extra no-stand rects in floor-local
## coords -- the sandbox feeds its placed-prop/furniture footprints through here.
## The live WATCH integration never calls this (backward-compatible no-op).
func set_extra_blocked_rects(rects: Array) -> void:
	_extra_blocked_rects = rects.duplicate()
	_rebuild_blocked_rects()
	for id in _sprites:
		_sprites[id].blocked_rects = _blocked_rects

## Read-only: the current no-stand rects (own landmarks + extras). For tests.
func blocked_rects() -> Array:
	return _blocked_rects.duplicate()

# Landmark props whose PropCatalogue footprints become no-stand rects. The cat
# corner and window strip stay procedural (no prop, nothing to block). Also
# records the id+feet of each landmark prop for approach-slot resolution.
func _rebuild_blocked_rects() -> void:
	_blocked_rects = []
	_landmark_props = []
	var b := _bounds()
	var z := _zones(b)
	_add_landmark_prop("water_cooler", z["water_pos"])
	_add_landmark_prop("filing_cabinet", z["fridge_pos"])
	_add_landmark_prop("server_cluster",
		b.position + Vector2(b.size.x * 0.12, b.size.y * 0.18))
	_blocked_rects.append_array(_extra_blocked_rects)

func _add_landmark_prop(id: String, feet: Vector2) -> void:
	_blocked_rects.append(_footprint_rect(id, feet))
	_landmark_props.append({"id": id, "feet": feet})

# --- Pass 3: prop approach slots ---------------------------------------------
# Prop manifest v1.2: a prop may declare `approach_px` -- preferred standing
# spots as offsets from its feet anchor, in SOURCE px. Landmark destinations
# resolve to the first FREE slot, so walkers stand at the water cooler's SIDES
# instead of stacking "slightly in front" of it (Pip, 2026-07-26). Props
# without slots keep the pass-2 behaviour EXACTLY: the raw landmark point,
# which the sprite's nearest-outside-footprint clamp then resolves.

## Resolve a landmark feet-point into a standing spot for `requester_id`.
## Deterministic: slots are tried in authored (manifest) order; a slot is free
## when no OTHER sprite stands within APPROACH_SLOT_CLAIM_RADIUS of it or is
## currently navigating to it. All busy -> the first slot (walkers share).
## Landmarks without slot data return unchanged (fallback identical to pass 2).
func approach_point_for(landmark: Vector2, requester_id: String = "") -> Vector2:
	var slots := _approach_slots_at(landmark)
	if slots.is_empty():
		return landmark
	for s in slots:
		if _slot_free(s, requester_id):
			return s
	return slots[0]

# Display-space approach slots of the landmark prop whose feet sit at
# `landmark` (empty when no prop is there or it declares none). Offsets scale
# by the same subject-height factor _draw_prop renders with, so the slots
# track the drawn art.
func _approach_slots_at(landmark: Vector2) -> Array:
	for lp in _landmark_props:
		if (lp["feet"] as Vector2).distance_to(landmark) > 0.5:
			continue
		var id := String(lp["id"])
		var offs := PropCatalogue.approach_points(id)
		if offs.is_empty():
			return []
		var subj: Array = PropCatalogue.get_entry(id).get("subject_px", [])
		var subject_h := float(subj[1]) if subj.size() == 2 else 0.0
		if subject_h <= 0.0:
			return []
		var scl := PropCatalogue.height_px(id, DISPLAY_TILE_PX) / subject_h
		var out: Array = []
		for o in offs:
			out.append(landmark + (o as Vector2) * scl)
		return out
	return []

func _slot_free(slot: Vector2, requester_id: String) -> bool:
	for id in _sprites:
		if str(id) == requester_id:
			continue
		var spr: OfficeEmployeeSprite = _sprites[id]
		if spr.position.distance_to(slot) < APPROACH_SLOT_CLAIM_RADIUS:
			return false
		var dest = spr.current_destination()
		if dest != null and (dest as Vector2).distance_to(slot) < 1.0:
			return false
	return true

# Floor area a feet-anchored prop occupies: footprint_tiles wide, extending UP
# from the feet point (same convention as the sandbox occupancy pass, #907).
func _footprint_rect(id: String, feet: Vector2) -> Rect2:
	var fp := PropCatalogue.footprint(id)
	var w := fp.x * DISPLAY_TILE_PX
	var d := fp.y * DISPLAY_TILE_PX
	return Rect2(feet - Vector2(w * 0.5, d), Vector2(w, d))

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
		spr.blocked_rects = _blocked_rects

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
	var tile_img := atlas_img.get_region(r)
	# #770: integer nearest-neighbor upscale so the tiled concrete reads larger/crisper
	# in the WATCH strip instead of as a fine 32px grid.
	tile_img.resize(r.size.x * FLOOR_TILE_SCALE, r.size.y * FLOOR_TILE_SCALE, Image.INTERPOLATE_NEAREST)
	return ImageTexture.create_from_image(tile_img)

# Draw a prop texture with its feet anchor at `at`, dimmed to match the floor.
# #907 integration: when `id` has a manifest entry (PropCatalogue) the prop keeps its
# AUTHORED proportions -- scaled so the opaque subject spans height_px(id, DISPLAY_TILE_PX)
# and anchored at the manifest anchor_px (subject feet) instead of the texture's
# bottom-centre (which drifted with transparent padding). Without an id / entry it falls
# back to the legacy PROP_TARGET_H force-scale, so unknown textures render like before.
func _draw_prop(tex: Texture2D, at: Vector2, id: String = "") -> void:
	if tex == null:
		return
	var src := tex.get_size()
	if src.y <= 0.0:
		return
	if id != "" and PropCatalogue.has(id):
		var e := PropCatalogue.get_entry(id)
		var subj: Array = e.get("subject_px", [])
		var subject_h := float(subj[1]) if subj.size() == 2 else src.y
		if subject_h <= 0.0:
			subject_h = src.y
		var scl_m := PropCatalogue.height_px(id, DISPLAY_TILE_PX) / subject_h
		var anchor := PropCatalogue.anchor(id)
		if anchor == PropCatalogue.ANCHOR_UNSET:
			anchor = Vector2(src.x * 0.5, src.y)   # no anchor data -> texture bottom-centre
		draw_texture_rect(tex, Rect2(at - anchor * scl_m, src * scl_m), false, FLOOR_DIM)
		return
	var scl := PROP_TARGET_H / src.y
	var w := src.x * scl
	var rect := Rect2(at - Vector2(w * 0.5, PROP_TARGET_H), Vector2(w, PROP_TARGET_H))
	draw_texture_rect(tex, rect, false, FLOOR_DIM)

# Resolve the texture + manifest id a landmark prop should draw with under the current
# office style. Honours the manifest's style_tags: a "<id>_<style>" variant is used only
# if manifested AND tagged for the style; otherwise the decent art draws unchanged.
func _styled_prop(id: String, default_tex: Texture2D) -> Array:
	if _office_style == "" or _office_style == "decent":
		return [default_tex, id]
	var variant := "%s_%s" % [id, _office_style]
	if not PropCatalogue.has(variant) or not (_office_style in PropCatalogue.style_tags(variant)):
		return [default_tex, id]   # variant art missing -> decent art unchanged
	if not _style_tex_cache.has(variant):
		var path := PropCatalogue.art_path(variant)
		var tex := load(path) if path != "" and ResourceLoader.exists(path) else null
		_style_tex_cache[variant] = tex if tex != null else default_tex
	return [_style_tex_cache[variant], variant]

func _draw_landmark_prop(id: String, default_tex: Texture2D, at: Vector2) -> void:
	var resolved := _styled_prop(id, default_tex)
	_draw_prop(resolved[0], at, resolved[1])

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
	# window strip (top wall). Dev-hook: if a promoted wall texture was supplied via
	# set_wall_strip_texture() it tiles across a slightly taller strip; default (null)
	# draws the original flat blue rect unchanged.
	if _wall_strip_tex != null:
		draw_texture_rect(_wall_strip_tex, Rect2(Vector2(b.position.x + 6, b.position.y + 2), Vector2(b.size.x - 12, 12)), true, FLOOR_DIM)
	else:
		draw_rect(Rect2(Vector2(b.position.x + 6, b.position.y + 2), Vector2(b.size.x - 12, 5)), Color(0.45, 0.6, 0.75, 0.45))
	draw_circle(z["cat_pos"], 9.0, Color(0.9, 0.5, 0.7, 0.4))            # cat corner (pink)
	# #907: landmark props render manifest-scaled/anchored, style-variant-aware.
	_draw_landmark_prop("water_cooler", PROP_WATER_COOLER, z["water_pos"])          # top-right
	_draw_water_bubbles(z["water_pos"])                                             # #913 juice
	_draw_landmark_prop("filing_cabinet", PROP_FILING_CABINET, z["fridge_pos"])     # bottom-right
	_draw_landmark_prop("server_cluster", PROP_SERVER,
		b.position + Vector2(b.size.x * 0.12, b.size.y * 0.18))                     # top-left decor

# Pass-3 organic bubbles (#913 evolved): draw whichever emitters are mid-burst
# right now. Two emitters on incommensurate timers (constants above) each rise
# one bubble through the jug (the top ~third of the manifest-scaled prop) over
# a short 3-frame burst; between bursts the jug is still. Pure function of the
# emitter clock -- sparse, never visibly repeating, no RNG.
func _draw_water_bubbles(feet: Vector2) -> void:
	var h := PropCatalogue.height_px("water_cooler", DISPLAY_TILE_PX)
	if h <= 0.0:
		return
	var rise := h * 0.05                                   # px climbed per frame
	var base_y := feet.y - h * 0.72                        # bottom of the jug water line
	# Emitter 0 sits slightly left and larger; emitter 1 right and smaller.
	var xs: Array = [feet.x - h * 0.02, feet.x + h * 0.025]
	var radii: Array = [1.6, 1.1]
	for i in range(BUBBLE_EMITTER_PERIODS.size()):
		var f := bubble_frame_at(_bubble_clock, BUBBLE_EMITTER_PERIODS[i],
			bubble_phase_for(feet, BUBBLE_EMITTER_PERIODS[i], i))
		if f < 0:
			continue
		draw_circle(Vector2(float(xs[i]), base_y - float(f) * rise), float(radii[i]), BUBBLE_COLOR)

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

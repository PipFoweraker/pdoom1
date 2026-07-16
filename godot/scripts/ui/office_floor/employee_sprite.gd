extends Node2D
class_name OfficeEmployeeSprite
## One employee rendered on the OfficeFloor. PURE VIEW: it only draws and moves
## cosmetically. It never touches game state; its wander/behavior RNG is a private,
## cosmetic RNG (NOT the seeded game RNG — ADR-0006).
##
## Tier 0: a colored blob + a hat, drawn with _draw() (OG-pdoom1 parity).
## Tier 1: an AnimatedSprite2D playing the FSM animation (idle/walking/working/
##         stressed). Placeholder SpriteFrames are generated in code; assigning a
##         real pixellab.ai SpriteFrames (with those 4 clip names) swaps the art
##         with no code change.
##
## Within a state, sprites run cheap cosmetic MICRO-BEHAVIORS (all private-RNG):
##   working  -> occasionally leaves the desk for a food run (fridge / water
##               cooler) or to pat the cat, then returns; and occasionally walks
##               to a peer's desk to collaborate (started by OfficeFloor, which
##               knows who else is working) then returns. All still the "working"
##               state — human flavor, never a state change and never a bonus.
##   walking  -> "aimless" isn't just drift: picks drift / window-gaze (a long
##               stare out the window) / spin-on-the-spot, so disengagement reads.

const BODY_RADIUS := 11.0
const ARRIVE_EPS := 4.0

# Micro-behavior tuning (seconds / per-second chances; all cosmetic).
const BREAK_CHANCE_PER_SEC := 0.14      # once off cooldown, chance/sec to start a break
const BREAK_COOLDOWN_RANGE := Vector2(5.0, 12.0)
const BREAK_DWELL_RANGE := Vector2(1.5, 3.5)
const WINDOW_GAZE_RANGE := Vector2(4.0, 9.0)
const SPIN_RANGE := Vector2(2.0, 4.5)
const DRIFT_RANGE := Vector2(2.0, 5.0)
const SPIN_STEP_INTERVAL := 0.22         # seconds per quarter-turn while "spinning"

# --- Directional facing --------------------------------------------------
## Facing is a discrete compass direction (NOT a node rotation). Movement picks
## a facing from the dominant axis of the movement vector; "spin" cycles this
## same facing string S->E->N->W (or reverse) instead of tipping the sprite
## over on its Z axis. Tier 1 shows the real 4 rotation-reference frames when
## facing != south; south keeps using the animated FSM-state clip (that's the
## only direction pixellab has full walk/idle/working/stressed loops for today).
const FACING_SOUTH := "south"
const FACING_EAST := "east"
const FACING_NORTH := "north"
const FACING_WEST := "west"
const _SPIN_ORDER := [FACING_SOUTH, FACING_EAST, FACING_NORTH, FACING_WEST]

# Static per-direction reference art (committed alongside the animated clips).
# FUTURE SEAM: once directional walk/working/stressed CLIPS exist, name them
# "<state>_<facing>" (e.g. "walking_east") in the shared SpriteFrames and
# _update_facing_visual() below will prefer them automatically -- no code
# change needed here, only art + clip names.
const ROTATION_SOUTH := preload("res://assets/office_floor/artloop_char/rotation_south.png")
const ROTATION_EAST := preload("res://assets/office_floor/artloop_char/rotation_east.png")
const ROTATION_NORTH := preload("res://assets/office_floor/artloop_char/rotation_north.png")
const ROTATION_WEST := preload("res://assets/office_floor/artloop_char/rotation_west.png")
const DEFAULT_FACING_TEXTURES := {
	FACING_SOUTH: ROTATION_SOUTH,
	FACING_EAST: ROTATION_EAST,
	FACING_NORTH: ROTATION_NORTH,
	FACING_WEST: ROTATION_WEST,
}
# Screen-space unit vectors per facing (+x = east, +y = south/down). Used by
# the tier-0 blob's "nose" cue.
const _FACING_VECTORS := {
	FACING_SOUTH: Vector2(0, 1),
	FACING_EAST: Vector2(1, 0),
	FACING_NORTH: Vector2(0, -1),
	FACING_WEST: Vector2(-1, 0),
}

var tier: int = 0
var sprite_state: String = EmployeeFSM.STATE_IDLE
var emp_name: String = ""
var body_color: Color = Color(0.6, 0.6, 0.65)
var hat_color: Color = Color(0.15, 0.15, 0.18)

var bounds: Rect2 = Rect2(0, 0, 400, 300)
var desk_pos: Vector2 = Vector2.ZERO      # workstation used by the "working" state
# Cosmetic destination landmarks on the floor (set by OfficeFloor from its bounds).
var fridge_pos: Vector2 = Vector2.ZERO    # food run
var water_pos: Vector2 = Vector2.ZERO     # water cooler
var cat_pos: Vector2 = Vector2.ZERO       # pat the cat
var window_pos: Vector2 = Vector2.ZERO    # window-gaze
var speed: float = 42.0

var _target: Vector2 = Vector2.ZERO
var _rng := RandomNumberGenerator.new()   # cosmetic-only; deliberately un-seeded from the game
var _anim: AnimatedSprite2D
var _facing_sprite: Sprite2D             # static directional reference art (tier 1 only)
var _label: Label

# working micro-behavior
var _work_sub := "desk"                   # desk | to_break | on_break | to_collab | collaborating | returning
var _break_cooldown := 0.0
var _break_target := Vector2.ZERO
var _break_kind := ""                     # "fridge" | "water" | "cat" | "collab" (legibility cue only)
var _collab_target := Vector2.ZERO        # peer desk, set by OfficeFloor.try_start_collaboration()
# aimless micro-behavior
var _aimless := "drift"                   # drift | window | spin
var _aimless_timer := 0.0
var _spin_dir := 1.0
var _spin_step_timer := 0.0

# facing (compass direction the sprite should visually face; NOT a node rotation)
var _facing: String = FACING_SOUTH
var _facing_active: bool = false          # true while translating or spinning-in-place
var _facing_textures: Dictionary = DEFAULT_FACING_TEXTURES

func _ready() -> void:
	_rng.randomize()
	_target = position
	_anim = AnimatedSprite2D.new()
	_anim.visible = false
	# Crisp pixel art, no blur, regardless of per-file .import filter settings.
	_anim.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_anim)
	_facing_sprite = Sprite2D.new()
	_facing_sprite.visible = false
	_facing_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_facing_sprite)
	_label = Label.new()
	_label.add_theme_font_size_override("font_size", 10)
	_label.position = Vector2(-BODY_RADIUS - 2.0, BODY_RADIUS + 2.0)
	_label.text = emp_name
	add_child(_label)
	_apply_tier()

func configure(data: Dictionary) -> void:
	## data: {state, name, body_color, hat_color, desk_pos, snack_pos, cat_pos, window_pos}
	var prev_state := sprite_state
	sprite_state = data.get("state", EmployeeFSM.STATE_IDLE)
	emp_name = data.get("name", "")
	body_color = data.get("body_color", body_color)
	hat_color = data.get("hat_color", hat_color)
	desk_pos = data.get("desk_pos", desk_pos)
	fridge_pos = data.get("fridge_pos", fridge_pos)
	water_pos = data.get("water_pos", water_pos)
	cat_pos = data.get("cat_pos", cat_pos)
	window_pos = data.get("window_pos", window_pos)
	if _label:
		_label.text = emp_name
	if sprite_state != prev_state:
		_enter_state_behavior()
	_refresh_visual()

func set_state(new_state: String) -> void:
	if new_state == sprite_state:
		return
	sprite_state = new_state
	_enter_state_behavior()
	_refresh_visual()

func set_tier(t: int) -> void:
	if t == tier:
		return
	tier = t
	_apply_tier()

## Assign a real (or shared placeholder) SpriteFrames. Must contain animations
## named idle / walking / working / stressed.
func set_sprite_frames(frames: SpriteFrames) -> void:
	if _anim:
		_anim.sprite_frames = frames
		_refresh_visual()

func _apply_tier() -> void:
	if _anim == null:
		return
	if tier == 1:
		if _anim.sprite_frames == null:
			_anim.sprite_frames = _build_placeholder_frames(body_color, hat_color)
	else:
		_anim.visible = false
		if _facing_sprite:
			_facing_sprite.visible = false
	_refresh_visual()
	queue_redraw()

## Optional: override the static per-direction reference art (default: the
## committed rotation_{south,east,north,west}.png). Same seam shape as
## set_sprite_frames() so a future art swap needs no OfficeFloor code change.
func set_facing_textures(textures: Dictionary) -> void:
	_facing_textures = textures
	_refresh_visual()

func _refresh_visual() -> void:
	_update_facing_visual()
	queue_redraw()

## Pick what tier-1 art to show this frame: the animated FSM-state clip while
## facing south (or not actively facing anything in particular), a directional
## CLIP if one exists for "<state>_<facing>" (future per-direction walk art
## drops in here with zero code change), otherwise the static rotation frame
## for the current facing.
func _update_facing_visual() -> void:
	if tier != 1 or _anim == null:
		return
	var want_facing := _facing if _facing_active else FACING_SOUTH
	if want_facing == FACING_SOUTH:
		_show_animated_clip(sprite_state)
		return
	var directional_clip := "%s_%s" % [sprite_state, want_facing]
	if _anim.sprite_frames and _anim.sprite_frames.has_animation(directional_clip):
		_show_animated_clip(directional_clip)
	else:
		_show_static_facing(want_facing)

func _show_animated_clip(clip_name: String) -> void:
	if _facing_sprite:
		_facing_sprite.visible = false
	_anim.visible = true
	if _anim.sprite_frames and _anim.sprite_frames.has_animation(clip_name):
		_anim.play(clip_name)

func _show_static_facing(facing: String) -> void:
	if _facing_sprite == null:
		return
	var tex: Texture2D = _facing_textures.get(facing, null)
	if tex == null:
		_show_animated_clip(sprite_state)
		return
	_anim.visible = false
	_facing_sprite.texture = tex
	_facing_sprite.visible = true

## Pure facing-selection: given a movement vector, pick the compass direction
## the sprite should face (dominant axis wins; ties favour horizontal). Screen
## space: +x = east, +y = south (down). Static/testable with no scene tree.
static func facing_from_vector(v: Vector2) -> String:
	if absf(v.x) < 0.0001 and absf(v.y) < 0.0001:
		return FACING_SOUTH
	if absf(v.x) >= absf(v.y):
		return FACING_EAST if v.x > 0.0 else FACING_WEST
	return FACING_SOUTH if v.y > 0.0 else FACING_NORTH

func _set_facing(f: String) -> void:
	_facing = f

## Move toward target and face the direction actually travelled this frame.
## Marks _facing_active so the directional art (rather than the south-only
## animated clip) is shown while translating.
func _move_toward_and_face(target: Vector2, delta: float) -> void:
	_facing_active = true
	var before := position
	position = position.move_toward(target, speed * delta)
	var moved := position - before
	if moved.length_squared() > 0.0001:
		_set_facing(facing_from_vector(moved))

# Initialise the micro-behavior when a state is (re)entered.
func _enter_state_behavior() -> void:
	match sprite_state:
		EmployeeFSM.STATE_WORKING:
			_work_sub = "desk"
			_break_kind = ""
			_break_cooldown = _rng.randf_range(BREAK_COOLDOWN_RANGE.x, BREAK_COOLDOWN_RANGE.y)
		EmployeeFSM.STATE_WALKING:
			_pick_aimless()
		_:
			pass

func _process(delta: float) -> void:
	_facing_active = false
	match sprite_state:
		EmployeeFSM.STATE_WORKING:
			_process_working(delta)
		EmployeeFSM.STATE_WALKING:
			_process_aimless(delta)
		_:
			# idle / stressed hold position (heads-down / head-in-hands)
			pass
	_clamp_to_bounds()
	_refresh_visual()
	if tier == 0:
		queue_redraw()

# working: productive-normal at the desk, with occasional human breaks + collabs.
func _process_working(delta: float) -> void:
	match _work_sub:
		"desk":
			_move_toward_and_face(desk_pos, delta)
			if position.distance_to(desk_pos) <= ARRIVE_EPS:
				_break_cooldown -= delta
				if _break_cooldown <= 0.0 and _rng.randf() < BREAK_CHANCE_PER_SEC * delta:
					_start_break()
		"to_break":
			_move_toward_and_face(_break_target, delta)
			if position.distance_to(_break_target) <= ARRIVE_EPS:
				_work_sub = "on_break"
				_aimless_timer = _rng.randf_range(BREAK_DWELL_RANGE.x, BREAK_DWELL_RANGE.y)
		"on_break":
			_aimless_timer -= delta
			if _aimless_timer <= 0.0:
				_work_sub = "returning"
		"to_collab":
			# stand just beside the peer's desk, not on top of it
			var beside := _collab_target + Vector2(BODY_RADIUS * 1.6, 0.0)
			_move_toward_and_face(beside, delta)
			if position.distance_to(beside) <= ARRIVE_EPS:
				_work_sub = "collaborating"
				_aimless_timer = _rng.randf_range(BREAK_DWELL_RANGE.x, BREAK_DWELL_RANGE.y)
		"collaborating":
			_aimless_timer -= delta
			if _aimless_timer <= 0.0:
				_work_sub = "returning"
		"returning":
			_move_toward_and_face(desk_pos, delta)
			if position.distance_to(desk_pos) <= ARRIVE_EPS:
				_work_sub = "desk"
				_break_kind = ""
				_break_cooldown = _rng.randf_range(BREAK_COOLDOWN_RANGE.x, BREAK_COOLDOWN_RANGE.y)

func _start_break() -> void:
	# get-food -> fridge or water cooler; or pat the cat.
	match _rng.randi() % 3:
		0:
			_break_kind = "fridge"
			_break_target = fridge_pos
		1:
			_break_kind = "water"
			_break_target = water_pos
		_:
			_break_kind = "cat"
			_break_target = cat_pos
	_work_sub = "to_break"

## True when this employee is working AND parked at its own desk (available to
## be pulled into a collaboration). Read-only.
func is_at_desk() -> bool:
	return sprite_state == EmployeeFSM.STATE_WORKING and _work_sub == "desk"

## OfficeFloor pulls this employee over to a peer's desk to collaborate. Only
## accepted while parked at own desk. Purely cosmetic: returns false if busy.
func try_start_collaboration(peer_desk: Vector2) -> bool:
	if not is_at_desk():
		return false
	_collab_target = peer_desk
	_break_kind = "collab"
	_work_sub = "to_collab"
	return true

# aimless (unmanaged/drifting): visibly disengaged, not just moving.
func _process_aimless(delta: float) -> void:
	_aimless_timer -= delta
	match _aimless:
		"drift":
			if position.distance_to(_target) <= ARRIVE_EPS:
				_pick_wander_target()
			_move_toward_and_face(_target, delta)
			if _aimless_timer <= 0.0:
				_pick_aimless()
		"window":
			if position.distance_to(window_pos) > ARRIVE_EPS:
				_move_toward_and_face(window_pos, delta)
				_aimless_timer += delta   # don't burn gaze time until we've arrived
			elif _aimless_timer <= 0.0:
				_pick_aimless()
		"spin":
			# Stand still and turn the BODY to face S -> E -> N -> W (or reverse) --
			# a person spinning on the spot, not the sprite image tipping over.
			_facing_active = true
			_spin_step_timer -= delta
			if _spin_step_timer <= 0.0:
				_spin_step_timer = SPIN_STEP_INTERVAL
				_advance_spin_facing()
			if _aimless_timer <= 0.0:
				_pick_aimless()

func _advance_spin_facing() -> void:
	var idx := _SPIN_ORDER.find(_facing)
	if idx < 0:
		idx = 0
	var step := 1 if _spin_dir > 0.0 else -1
	idx = posmod(idx + step, _SPIN_ORDER.size())
	_facing = _SPIN_ORDER[idx]

func _pick_aimless() -> void:
	match _rng.randi() % 3:
		0:
			_aimless = "drift"
			_pick_wander_target()
			_aimless_timer = _rng.randf_range(DRIFT_RANGE.x, DRIFT_RANGE.y)
		1:
			_aimless = "window"
			_aimless_timer = _rng.randf_range(WINDOW_GAZE_RANGE.x, WINDOW_GAZE_RANGE.y)
		_:
			_aimless = "spin"
			_aimless_timer = _rng.randf_range(SPIN_RANGE.x, SPIN_RANGE.y)
			_spin_dir = 1.0 if _rng.randf() < 0.5 else -1.0
			_spin_step_timer = 0.0   # turn immediately on entering spin

func _pick_wander_target() -> void:
	_target = Vector2(
		_rng.randf_range(bounds.position.x + BODY_RADIUS, bounds.end.x - BODY_RADIUS),
		_rng.randf_range(bounds.position.y + BODY_RADIUS, bounds.end.y - BODY_RADIUS)
	)

func _clamp_to_bounds() -> void:
	position.x = clampf(position.x, bounds.position.x + BODY_RADIUS, bounds.end.x - BODY_RADIUS)
	position.y = clampf(position.y, bounds.position.y + BODY_RADIUS, bounds.end.y - BODY_RADIUS)

# --- Tier 0 rendering: blob + hat ------------------------------------------
func _draw() -> void:
	if tier != 0:
		return
	var draw_body := body_color
	var draw_hat := hat_color
	# The floor doubles as a dashboard: tint by state so a problem reads at a glance.
	match sprite_state:
		EmployeeFSM.STATE_STRESSED:
			draw_body = body_color.lerp(Color(0.85, 0.2, 0.2), 0.55)  # reddening
		EmployeeFSM.STATE_WALKING:
			draw_body = body_color.lerp(Color(0.85, 0.7, 0.2), 0.35)  # aimless amber
		_:
			pass
	# body
	draw_circle(Vector2.ZERO, BODY_RADIUS, draw_body)
	draw_arc(Vector2.ZERO, BODY_RADIUS, 0.0, TAU, 24, Color(0, 0, 0, 0.4), 1.5)
	# hat: brim + crown sitting on top of the blob
	var brim := Rect2(-BODY_RADIUS, -BODY_RADIUS - 2.0, BODY_RADIUS * 2.0, 3.0)
	draw_rect(brim, draw_hat)
	var crown := Rect2(-BODY_RADIUS * 0.55, -BODY_RADIUS - 8.0, BODY_RADIUS * 1.1, 6.0)
	draw_rect(crown, draw_hat)
	# stressed: little "!" hands-on-head cue
	if sprite_state == EmployeeFSM.STATE_STRESSED:
		draw_line(Vector2(0, -BODY_RADIUS - 12.0), Vector2(0, -BODY_RADIUS - 16.0), Color(0.9, 0.2, 0.2), 2.0)
	# facing cue (tier 0 stand-in for the tier-1 directional sprite): a small
	# dark "nose" dot on the edge of the blob toward the current facing.
	var nose_dir: Vector2 = _FACING_VECTORS.get(_facing, Vector2(0, 1))
	draw_circle(nose_dir * (BODY_RADIUS - 3.0), 2.0, Color(0, 0, 0, 0.5))
	# off-desk cue: small dot coloured by errand so the flavor reads on the floor
	# (fridge/water=cyan-blue, cat=pink, collaborate=green).
	if sprite_state == EmployeeFSM.STATE_WORKING and _work_sub != "desk":
		var cue := Color(0.5, 0.75, 0.9)  # food (fridge/water)
		match _break_kind:
			"cat":
				cue = Color(0.9, 0.5, 0.7)
			"collab":
				cue = Color(0.4, 0.85, 0.5)
		draw_circle(Vector2(BODY_RADIUS - 1.0, -BODY_RADIUS - 4.0), 2.5, cue)

# --- Tier 1 placeholder frame generation -----------------------------------
# Builds a tiny 4-animation SpriteFrames of solid-colour "characters" with a hat,
# a 1px bob between the two frames of moving states so motion reads. Real art
# drops in via set_sprite_frames(); nothing here is load-bearing for behavior.
static func _build_placeholder_frames(body: Color, hat: Color) -> SpriteFrames:
	var sf := SpriteFrames.new()
	var specs := {
		EmployeeFSM.STATE_IDLE:     {"tint": body, "bob": 0, "fps": 2.0},
		EmployeeFSM.STATE_WALKING:  {"tint": body.lerp(Color(0.85, 0.7, 0.2), 0.35), "bob": 2, "fps": 6.0},
		EmployeeFSM.STATE_WORKING:  {"tint": body, "bob": 1, "fps": 4.0},
		EmployeeFSM.STATE_STRESSED: {"tint": body.lerp(Color(0.85, 0.2, 0.2), 0.55), "bob": 1, "fps": 5.0},
	}
	# SpriteFrames ships with a "default" animation; reuse it as idle to avoid a stray clip.
	var first := true
	for state in specs.keys():
		var anim_name: String = state
		if first:
			sf.rename_animation("default", anim_name)
			first = false
		elif not sf.has_animation(anim_name):
			sf.add_animation(anim_name)
		sf.set_animation_loop(anim_name, true)
		sf.set_animation_speed(anim_name, specs[state]["fps"])
		var bob: int = specs[state]["bob"]
		sf.add_frame(anim_name, _make_char_texture(specs[state]["tint"], hat, 0))
		sf.add_frame(anim_name, _make_char_texture(specs[state]["tint"], hat, bob))
	return sf

static func _make_char_texture(body: Color, hat: Color, bob: int) -> ImageTexture:
	var w := 24
	var h := 32
	var img := Image.create(w, h, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var oy := clampi(bob, 0, 4)
	# body block
	img.fill_rect(Rect2i(6, 12 + oy, 12, 16), body)
	# head
	img.fill_rect(Rect2i(8, 6 + oy, 8, 7), body.lerp(Color(1, 1, 1), 0.15))
	# hat
	img.fill_rect(Rect2i(6, 3 + oy, 12, 3), hat)
	img.fill_rect(Rect2i(9, 0 + oy, 6, 3), hat)
	return ImageTexture.create_from_image(img)

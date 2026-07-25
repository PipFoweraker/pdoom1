extends Control
## OFFICE SANDBOX -- a standalone DEV TOY for the office-floor view (Pip: open this
## in the evening and play). Spawn walking people, cycle their skin, add/remove cats,
## and change the room's mood/lighting. Watch them wander, work, drift, and pat the cat.
##
## MECHANICS-SAFE / W3-SAFE (by construction): this scene is PURE COMPOSITION. It
## instantiates the existing OfficeFloor view (res://scenes/ui/office_floor/office_floor.tscn)
## and drives it through its EXISTING public API only (set_roster / set_tier /
## set_sprite_frames). It reuses OfficeEmployeeSprite's placeholder-frame generator for
## colour skins and the committed pixellab SpriteFrames for the real-art skin. The cats
## are a self-contained inner class (SandboxCat) drawn procedurally. The "mood/light"
## control uses the built-in CanvasItem.modulate property. NOTHING here modifies
## office_floor.gd / employee_fsm.gd / employee_sprite.gd, the WATCH integration, game
## state, the economy, or actions. There is no game state, no win/lose -- just a toy.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")
# Real pixellab.ai art-loop SpriteFrames (idle/walking/working/stressed + directional walks).
const RealSpriteFrames := preload("res://assets/office_floor/artloop_char/office_worker.tres")
# Reused ONLY for its static _build_placeholder_frames() colour-skin generator (no instances).
const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")

const HAT := Color(0.14, 0.14, 0.18)
const MAX_PEOPLE := 24
const MAX_CATS := 8

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

var _floor: OfficeFloor
var _status: Label
var _roster: Array = []
var _cats: Array = []
var _next_id: int = 0
var _skin_idx: int = 0
var _mood_idx: int = 0
var _cat_color_idx: int = 0
var _rng := RandomNumberGenerator.new()

func _ready() -> void:
	_rng.randomize()
	set_anchors_preset(Control.PRESET_FULL_RECT)

	_floor = OfficeFloorScene.instantiate()
	_floor.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_floor)

	_build_overlay()

	# Start with the real-art skin and a few people so it's alive on open.
	_apply_skin(0)
	_apply_mood(0)
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

	var legend := Label.new()
	legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	legend.add_theme_font_size_override("font_size", 13)
	legend.text = "OFFICE SANDBOX  --  dev toy (no game state)\n" \
		+ "[1] spawn person    [2] despawn person    [S] cycle skin\n" \
		+ "[C] add cat    [X] remove cat    [B] cycle mood / light\n" \
		+ "[R] randomize    [0] clear all    [ESC] quit"
	vb.add_child(legend)

	_status = Label.new()
	_status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_status.add_theme_font_size_override("font_size", 12)
	vb.add_child(_status)

func _input(event: InputEvent) -> void:
	if not (event is InputEventKey):
		return
	var ke := event as InputEventKey
	if not ke.pressed or ke.echo:
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

func _update_status() -> void:
	if _status == null:
		return
	_status.text = "skin: %s   |   people: %d   |   cats: %d   |   mood: %s" % [
		_skins[_skin_idx]["name"], _roster.size(), _cats.size(), _moods[_mood_idx]["name"]]

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

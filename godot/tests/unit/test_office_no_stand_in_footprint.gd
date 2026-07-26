extends GutTest
## Tier-1 collision, part 2: no-walk zones from prop footprints. Walkers may
## still CROSS a prop transiently mid-walk (accepted tier-1 boundary; real
## pathing is tier 2, awaiting the tile-grid ruling / WS-3) but must never
## STAND/IDLE inside one: stationary poses are pushed out, wander targets
## re-roll, and destinations inside a prop resolve to the nearest point just
## outside it (so the water-cooler landmark stays reachable). Pure view.

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")
const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")

const WALK := Rect2(11, 11, 378, 278)   # tier-0 feet rect of Rect2(0,0,400,300) bounds
const PROP := Rect2(150, 150, 64, 64)   # a 1x1-display-tile footprint mid-floor


func _make_sprite() -> OfficeEmployeeSprite:
	var spr: OfficeEmployeeSprite = EmployeeSpriteScript.new()
	add_child_autofree(spr)
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.blocked_rects = [PROP]
	return spr


# --- pure helpers ------------------------------------------------------------

func test_point_outside_passes_through_unchanged():
	var p := Vector2(50, 50)
	assert_eq(OfficeEmployeeSprite.push_out_of_rects(p, [PROP], WALK), p)


func test_point_inside_is_pushed_just_outside():
	var out := OfficeEmployeeSprite.push_out_of_rects(Vector2(160, 180), [PROP], WALK)
	assert_false(PROP.has_point(out), "pushed point is outside the footprint")


func test_push_exits_through_the_nearest_edge():
	# 5px from the left edge, far from the others -> exits left.
	var out := OfficeEmployeeSprite.push_out_of_rects(Vector2(155, 180), [PROP], WALK)
	assert_lt(out.x, PROP.position.x, "exited through the near (left) edge")
	assert_eq(out.y, 180.0, "push is a straight slide, no drift")


func test_push_prefers_an_exit_inside_the_walkable_rect():
	# Prop flush against the bottom of the walkable rect: a point near its bottom
	# edge must NOT be pushed below the floor -- it takes an in-bounds exit instead.
	var wall_prop := Rect2(200, WALK.end.y - 64.0, 64, 64)
	var inside := Vector2(232, WALK.end.y - 4.0)
	var out := OfficeEmployeeSprite.push_out_of_rects(inside, [wall_prop], WALK)
	assert_false(wall_prop.has_point(out), "outside the prop")
	assert_true(WALK.has_point(out), "exit stays on the walkable floor, not inside the wall")


func test_inside_any_rect():
	assert_true(OfficeEmployeeSprite.inside_any_rect(Vector2(160, 160), [PROP]))
	assert_false(OfficeEmployeeSprite.inside_any_rect(Vector2(10, 10), [PROP]))


# --- sprite behaviour --------------------------------------------------------

func test_idle_walker_inside_a_footprint_is_pushed_out():
	var spr := _make_sprite()
	spr.sprite_state = EmployeeFSM.STATE_IDLE
	spr.position = Vector2(170, 170)          # standing inside the prop
	spr._process(0.05)
	assert_false(PROP.has_point(spr.position), "idle pose never renders inside furniture")


func test_stressed_walker_inside_a_footprint_is_pushed_out():
	var spr := _make_sprite()
	spr.sprite_state = EmployeeFSM.STATE_STRESSED
	spr.position = Vector2(180, 200)
	spr._process(0.05)
	assert_false(PROP.has_point(spr.position), "stressed pose never renders inside furniture")


func test_destination_inside_a_prop_resolves_to_its_edge():
	# The water-cooler landmark IS the prop's feet point: the clamped target must
	# sit just outside the footprint so arrival triggers at the standing spot.
	var spr := _make_sprite()
	var target := Vector2(180, 180)           # inside PROP
	var clamped := spr._clamp_target(target)
	assert_false(PROP.has_point(clamped), "nav targets resolve outside footprints")
	assert_true(spr._feet_rect().has_point(clamped), "resolved target stays walkable")


func test_wander_targets_avoid_footprints():
	var spr := _make_sprite()
	spr._rng.seed = 12345                     # cosmetic RNG; seeded for a stable sweep
	for _i in range(40):
		spr._pick_wander_target()
		assert_false(PROP.has_point(spr._target), "wander target rerolled out of the footprint")


func test_worker_idling_on_break_never_parks_inside_prop():
	# A break dwell at a target inside the prop: the walker walks to the clamped
	# edge point, dwells there, and is never left standing inside the footprint.
	var spr := _make_sprite()
	spr.sprite_state = EmployeeFSM.STATE_WORKING
	spr._work_sub = "to_break"
	spr._break_target = Vector2(182, 182)     # inside PROP
	spr.position = Vector2(60, 180)
	for _i in range(400):
		spr._process(0.05)
		if spr._work_sub == "on_break":
			break
	assert_eq(spr._work_sub, "on_break", "break dwell reached (arrival check agrees with the clamp)")
	assert_false(PROP.has_point(spr.position), "dwelling happens at the prop's edge, not inside it")


# --- OfficeFloor wiring ------------------------------------------------------

func test_floor_builds_landmark_footprint_rects():
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	await get_tree().process_frame
	assert_eq(f.blocked_rects().size(), 3,
		"water cooler + filing cabinet + server cluster footprints are no-stand rects")


func test_floor_hands_blocked_rects_to_sprites_and_extras_propagate():
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	await get_tree().process_frame
	f.set_roster([{"id": 0, "name": "A", "assigned": true}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	assert_eq(spr.blocked_rects.size(), 3, "sprites receive the floor's no-stand rects")
	f.set_extra_blocked_rects([Rect2(10, 10, 20, 20)])
	assert_eq(f.blocked_rects().size(), 4, "sandbox extras are additive")
	assert_eq(spr.blocked_rects.size(), 4, "existing sprites are re-armed with the extras")


# --- Pass 3: approach slots (prop manifest v1.2 approach_px) ------------------

func _make_floor() -> OfficeFloor:
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	return f


func test_water_cooler_landmark_resolves_to_a_side_slot():
	var f := _make_floor()
	var z: Dictionary = f._zones(f._bounds())
	var water: Vector2 = z["water_pos"]
	var p: Vector2 = f.approach_point_for(water, "w1")
	assert_ne(p, water, "water cooler declares approach_px -> not the raw landmark point")
	assert_gt(absf(p.x - water.x), 30.0, "slot stands to the SIDE of the cooler, not in front")
	assert_false(OfficeEmployeeSprite.inside_any_rect(p, f.blocked_rects()),
		"slot is a legal standing spot, outside every footprint")


func test_second_walker_gets_the_other_free_slot():
	var f := _make_floor()
	var z: Dictionary = f._zones(f._bounds())
	var water: Vector2 = z["water_pos"]
	var slot1: Vector2 = f.approach_point_for(water, "nobody")
	# Park a walker ON the first slot; the next requester must get the other one.
	f.set_roster([{"id": 0, "name": "A", "loyalty": 8}])   # loyalty 8 -> idle, holds position
	var spr: OfficeEmployeeSprite = f._sprites[0]
	spr.position = slot1
	var slot2: Vector2 = f.approach_point_for(water, "someone_else")
	assert_ne(slot2, slot1, "occupied slot skipped -> the free side slot is handed out")
	assert_ne(slot2, water, "still a slot, not the raw landmark")
	# The occupant itself keeps its own slot (requester is never its own blocker).
	assert_eq(f.approach_point_for(water, "0"), slot1, "occupant re-resolves to its own slot")


func test_all_slots_busy_falls_back_to_first_slot():
	var f := _make_floor()
	var z: Dictionary = f._zones(f._bounds())
	var water: Vector2 = z["water_pos"]
	var slot1: Vector2 = f.approach_point_for(water, "nobody")
	f.set_roster([
		{"id": 0, "name": "A", "loyalty": 8},
		{"id": 1, "name": "B", "loyalty": 8},
	])
	f._sprites[0].position = slot1
	f._sprites[1].position = f.approach_point_for(water, "y")   # the remaining free slot
	var occupied: Vector2 = f.approach_point_for(water, "late_arrival")
	assert_eq(occupied, slot1, "all slots taken -> deterministic first slot (walkers share)")


func test_props_without_slots_fall_back_unchanged():
	var f := _make_floor()
	var z: Dictionary = f._zones(f._bounds())
	assert_eq(f.approach_point_for(z["fridge_pos"], "x"), Vector2(z["fridge_pos"]),
		"filing cabinet declares no approach_px -> landmark unchanged (pass-2 path)")
	assert_eq(f.approach_point_for(Vector2(50, 50), "x"), Vector2(50, 50),
		"a non-landmark point passes through untouched")


func test_sprite_break_target_routes_through_floor_slots():
	var f := _make_floor()
	var z: Dictionary = f._zones(f._bounds())
	f.set_roster([{"id": 0, "name": "A", "assigned": true}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	var t: Vector2 = spr._landmark_break_target(z["water_pos"])
	assert_ne(t, Vector2(z["water_pos"]), "sprite's water-break target is an approach slot")
	assert_eq(t, f.approach_point_for(z["water_pos"], "0"),
		"sprite resolves via its owning floor with its own entity id")
	# Detached sprite (no floor parent): raw landmark, exactly the pass-2 path.
	var lone: OfficeEmployeeSprite = EmployeeSpriteScript.new()
	add_child_autofree(lone)
	assert_eq(lone._landmark_break_target(Vector2(70, 80)), Vector2(70, 80),
		"no floor above the sprite -> landmark unchanged")

extends GutTest
## OfficeFloor sprite facing: two playtest bug fixes.
##   1. A moving sprite must FACE the direction it's moving (south/east/north/
##      west), picked from the dominant axis of the movement vector.
##   2. "spin" (the disengaged aimless behavior) must CYCLE the facing string
##      S -> E -> N -> W (or reverse) instead of tweening the sprite Node2D's
##      rotation/rotation_degrees -- no clock-hand tipping.
## Pure-view, no GameState: same guarantee as the rest of OfficeFloor (ADR-0006).

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")


func _make_sprite() -> OfficeEmployeeSprite:
	var spr: OfficeEmployeeSprite = EmployeeSpriteScript.new()
	add_child_autofree(spr)
	return spr


# --- facing_from_vector: pure function, no scene tree needed ---------------

func test_facing_from_vector_cardinal_directions():
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(10, 0)), "east")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(-10, 0)), "west")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(0, 10)), "south")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(0, -10)), "north")


func test_facing_from_vector_diagonal_picks_dominant_axis():
	# Mostly-horizontal diagonal -> east/west; mostly-vertical -> south/north.
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(10, 3)), "east")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(-10, -3)), "west")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(3, 10)), "south")
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(-3, -10)), "north")


func test_facing_from_vector_tie_favours_horizontal():
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2(5, 5)), "east")


func test_facing_from_vector_zero_vector_defaults_south():
	assert_eq(OfficeEmployeeSprite.facing_from_vector(Vector2.ZERO), "south")


# --- movement drives the live sprite's facing -------------------------------

func test_drift_movement_updates_facing_east():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(50, 50)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._aimless = "drift"
	spr._aimless_timer = 100.0
	spr._target = Vector2(350, 50)   # straight east
	spr._process(0.1)
	assert_eq(spr._facing, "east")
	assert_true(spr._facing_active)


func test_drift_movement_updates_facing_north():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(50, 250)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._aimless = "drift"
	spr._aimless_timer = 100.0
	spr._target = Vector2(50, 10)    # straight north (screen-up)
	spr._process(0.1)
	assert_eq(spr._facing, "north")


func test_working_desk_approach_updates_facing():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(50, 50)
	spr.desk_pos = Vector2(50, 250)   # straight south
	spr.sprite_state = EmployeeFSM.STATE_WORKING
	spr._work_sub = "desk"
	spr._process(0.1)
	assert_eq(spr._facing, "south")


# --- spin: cycles facing, never rotates the node ----------------------------

func test_spin_never_rotates_the_node():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(100, 100)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._aimless = "spin"
	spr._aimless_timer = 100.0
	spr._spin_dir = 1.0
	spr._spin_step_timer = 0.0
	for i in range(40):
		spr._process(0.05)
		assert_eq(spr.rotation, 0.0, "node rotation must stay 0 during spin (step %d)" % i)
		assert_eq(spr.rotation_degrees, 0.0, "node rotation_degrees must stay 0 during spin (step %d)" % i)


func test_spin_cycles_facing_through_all_four_directions():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(100, 100)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._aimless = "spin"
	spr._aimless_timer = 100.0
	spr._spin_dir = 1.0
	spr._spin_step_timer = 0.0
	var seen := {}
	# SPIN_STEP_INTERVAL is 0.22s; step well past a full S->E->N->W->S cycle.
	for i in range(60):
		spr._process(0.05)
		seen[spr._facing] = true
	assert_true(seen.has("south"), "spin should pass through south")
	assert_true(seen.has("east"), "spin should pass through east")
	assert_true(seen.has("north"), "spin should pass through north")
	assert_true(seen.has("west"), "spin should pass through west")


func test_spin_marks_facing_active_so_directional_art_shows():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.position = Vector2(100, 100)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._aimless = "spin"
	spr._aimless_timer = 100.0
	spr._spin_dir = 1.0
	spr._spin_step_timer = 0.0
	spr._process(0.05)
	assert_true(spr._facing_active)


# --- stationary states default to south, no lingering rotation -------------

func test_idle_state_has_zero_rotation():
	var spr := _make_sprite()
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.sprite_state = EmployeeFSM.STATE_IDLE
	spr._process(0.1)
	assert_eq(spr.rotation, 0.0)

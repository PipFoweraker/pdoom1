extends GutTest
## Tier-1 collision, part 1: separation steering (boids-lite). Walkers softly
## repel walkers so they stop rendering inside each other -- DETERMINISTIC (a
## pure function of positions; no RNG in the separation path) -- while desk ring
## slots stay intentional convergence points (the push fades to zero inside
## SEPARATION_DAMP_RADIUS of the walker's current nav target, and STRENGTH is
## deliberately below walk speed so separation can never block an arrival).
## Pure view (ADR-0006): no game state anywhere.

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")
const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")

const DT := 0.05
const OPEN_FLOOR_MIN_DIST := 20.0   # "not inside each other" floor for the open-floor case


func _make_sprite() -> OfficeEmployeeSprite:
	var spr: OfficeEmployeeSprite = EmployeeSpriteScript.new()
	add_child_autofree(spr)
	spr.bounds = Rect2(0, 0, 400, 300)
	return spr


# --- separation_vector: pure, deterministic ---------------------------------

func test_no_neighbours_no_push():
	assert_eq(OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [], 30.0), Vector2.ZERO)


func test_far_neighbour_no_push():
	var v := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(200, 50)], 30.0)
	assert_eq(v, Vector2.ZERO, "neighbour outside the radius must not repel")


func test_near_neighbour_pushes_away():
	# Neighbour to the east -> push west (negative x), no vertical component.
	var v := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(60, 50)], 30.0)
	assert_lt(v.x, 0.0, "push points away from the neighbour")
	assert_almost_eq(v.y, 0.0, 0.0001)


func test_closer_neighbour_pushes_harder():
	var near := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(55, 50)], 30.0)
	var far := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(75, 50)], 30.0)
	assert_gt(near.length(), far.length(), "repulsion weight grows as distance shrinks")


func test_magnitude_capped_at_one():
	var crowd := [Vector2(51, 50), Vector2(52, 50), Vector2(50, 51), Vector2(50, 52), Vector2(49, 50)]
	var v := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), crowd, 30.0)
	assert_true(v.length() <= 1.0001, "summed push is normalised, never explosive")


func test_exactly_coincident_neighbour_contributes_nothing():
	# No direction is derivable from positions alone; the intentional case
	# (shared desk slots) is handled by arrival damping instead.
	var v := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(50, 50)], 30.0)
	assert_eq(v, Vector2.ZERO)


func test_separation_vector_is_deterministic():
	var neighbors := [Vector2(60, 55), Vector2(45, 40)]
	var a := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), neighbors, 30.0)
	var b := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), neighbors, 30.0)
	assert_eq(a, b, "pure function of positions -- same inputs, same push")


# --- open floor: overlapping walkers separate to a minimum distance ----------

func test_open_floor_overlapping_idlers_separate():
	var a := _make_sprite()
	var b := _make_sprite()
	a.sprite_state = EmployeeFSM.STATE_IDLE   # holding position: full separation applies
	b.sprite_state = EmployeeFSM.STATE_IDLE
	a.position = Vector2(200, 150)
	b.position = Vector2(206, 150)            # rendering inside each other
	for _i in range(200):
		# Mirror OfficeFloor._apply_separation: snapshot positions FIRST so the
		# result is independent of update order.
		var pa := a.position
		var pb := b.position
		a.apply_separation([pb], DT)
		b.apply_separation([pa], DT)
	assert_gt(a.position.distance_to(b.position), OPEN_FLOOR_MIN_DIST,
		"idle walkers pushed apart to a readable min distance")


func test_open_floor_separation_is_deterministic():
	var results: Array = []
	for _run in range(2):
		var a := _make_sprite()
		var b := _make_sprite()
		a.sprite_state = EmployeeFSM.STATE_IDLE
		b.sprite_state = EmployeeFSM.STATE_IDLE
		a.position = Vector2(200, 150)
		b.position = Vector2(210, 152)
		for _i in range(100):
			var pa := a.position
			var pb := b.position
			a.apply_separation([pb], DT)
			b.apply_separation([pa], DT)
		results.append([a.position, b.position])
	assert_eq(results[0][0], results[1][0], "same start -> same end (no RNG in separation)")
	assert_eq(results[0][1], results[1][1], "same start -> same end (no RNG in separation)")


# --- separation must NOT fight arrival ---------------------------------------

func test_worker_still_reaches_desk_past_a_neighbour():
	var a := _make_sprite()
	a.sprite_state = EmployeeFSM.STATE_WORKING
	a._work_sub = "desk"
	a._break_cooldown = 100000.0              # keep the break RNG out of this test
	a.position = Vector2(100, 150)
	a.desk_pos = Vector2(260, 150)
	var blocker := Vector2(240, 150)          # parked walker near the approach
	for _i in range(600):
		a._process(DT)
		a.apply_separation([blocker], DT)
		a._break_cooldown = 100000.0
	assert_true(a.is_at_desk(), "separation (strength < speed, damped near target) never blocks desk arrival")


func test_ring_slot_neighbours_both_hold_their_desks():
	# Two desks closer together than SEPARATION_RADIUS: the damp ramp (zero at
	# the walker's own nav target) must let BOTH sit their slots without jitter.
	var a := _make_sprite()
	var b := _make_sprite()
	a.sprite_state = EmployeeFSM.STATE_WORKING
	b.sprite_state = EmployeeFSM.STATE_WORKING
	a._work_sub = "desk"
	b._work_sub = "desk"
	a._break_cooldown = 100000.0
	b._break_cooldown = 100000.0
	a.desk_pos = Vector2(200, 150)
	b.desk_pos = Vector2(212, 150)            # 12px apart < SEPARATION_RADIUS 30
	a.position = Vector2(120, 140)
	b.position = Vector2(300, 160)
	for _i in range(600):
		var pa := a.position
		var pb := b.position
		a._process(DT)
		b._process(DT)
		a.apply_separation([pb], DT)
		b.apply_separation([pa], DT)
		a._break_cooldown = 100000.0
		b._break_cooldown = 100000.0
	assert_true(a.is_at_desk(), "walker A seated at its ring slot")
	assert_true(b.is_at_desk(), "walker B seated at the adjacent ring slot")
	assert_true(a.position.distance_to(a.desk_pos) <= a.ARRIVE_EPS + 0.001,
		"A parked ON its desk slot -- separation damped to zero at the target")
	assert_true(b.position.distance_to(b.desk_pos) <= b.ARRIVE_EPS + 0.001,
		"B parked ON its desk slot -- separation damped to zero at the target")


# --- Pass 3: cat-worker mutual avoidance (asymmetric weights) -----------------

func test_weights_scale_the_push():
	var full := OfficeEmployeeSprite.separation_vector(Vector2(50, 50), [Vector2(60, 50)], 30.0)
	var quarter := OfficeEmployeeSprite.separation_vector(
		Vector2(50, 50), [Vector2(60, 50)], 30.0, [0.25])
	assert_almost_eq(quarter.length(), full.length() * 0.25, 0.0001,
		"a 0.25 weight scales that neighbour's push to a quarter")


func test_missing_weight_entries_default_to_one():
	var plain := OfficeEmployeeSprite.separation_vector(
		Vector2(50, 50), [Vector2(60, 50), Vector2(50, 60)], 30.0)
	var partial := OfficeEmployeeSprite.separation_vector(
		Vector2(50, 50), [Vector2(60, 50), Vector2(50, 60)], 30.0, [1.0])
	assert_eq(plain, partial, "weights shorter than neighbours pad with 1.0")


func _make_floor_with_idle_worker_and_cat() -> Array:
	# One idle worker (loyalty 8 -> holds position) plus a bare Node2D cat
	# registered in the floor's cat group -- the minimum mutual-avoidance pair.
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	f.set_roster([{"id": 0, "name": "A", "loyalty": 8}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	spr.position = Vector2(180, 150)
	var cat := Node2D.new()
	cat.add_to_group(OfficeFloor.CAT_GROUP)
	f.add_child(cat)
	cat.position = Vector2(186, 150)          # rendering inside the worker
	return [f, spr, cat]


func test_cat_and_worker_separate_and_cat_yields_more():
	var trio := _make_floor_with_idle_worker_and_cat()
	var f: OfficeFloor = trio[0]
	var spr: OfficeEmployeeSprite = trio[1]
	var cat: Node2D = trio[2]
	var w0: Vector2 = spr.position
	var c0: Vector2 = cat.position
	for _i in range(200):
		f._apply_separation(DT)
	assert_gt(spr.position.distance_to(cat.position), OPEN_FLOOR_MIN_DIST,
		"cat and worker separate to a readable min distance")
	assert_gt(c0.distance_to(cat.position), w0.distance_to(spr.position) * 2.0,
		"ASYMMETRY: the cat (weight 1.6) yields far more than the worker deflects (0.25)")


func test_cat_worker_separation_is_deterministic():
	var results: Array = []
	for _run in range(2):
		var trio := _make_floor_with_idle_worker_and_cat()
		var f: OfficeFloor = trio[0]
		for _i in range(100):
			f._apply_separation(DT)
		results.append([(trio[1] as Node2D).position, (trio[2] as Node2D).position])
	assert_eq(results[0][0], results[1][0], "worker path identical run-to-run (no RNG)")
	assert_eq(results[0][1], results[1][1], "cat path identical run-to-run (no RNG)")


func test_unregistered_node_does_not_join_separation():
	# A plain child NOT in the cat group must be ignored by the pass entirely.
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	f.set_roster([{"id": 0, "name": "A", "loyalty": 8}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	spr.position = Vector2(180, 150)
	var bystander := Node2D.new()
	f.add_child(bystander)
	bystander.position = Vector2(186, 150)
	var w0: Vector2 = spr.position
	for _i in range(50):
		f._apply_separation(DT)
	assert_eq(spr.position, w0, "one worker + non-cat node -> no separation applied")
	assert_eq(bystander.position, Vector2(186, 150), "non-cat node never displaced")

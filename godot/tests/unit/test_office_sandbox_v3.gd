extends GutTest
## Robustness / inferential guard for the OFFICE SANDBOX v3 dev toy. The sandbox never
## ships to players, but it is a live prototyping surface, so this locks the invariants
## that a UI-preview tool must not violate: it INSTANTIATES clean, its state machines are
## bounded (populate / scale / doom / overlay opacity all CLAMP, never overrun or crash),
## destructive calls on empty collections are no-ops, the first "space logic" slice holds
## (furniture hugs walls + never shares a cell), and the real cat WALK-CYCLE data a spawned
## cat would preview is assembled with the expected clips (the pixels still need a human's
## eyes -- see the PR "UX QA" note -- but the DATA behind the preview is machine-checkable).
##
## PURE VIEW / mechanics-safe: no GameState, no seeded RNG, no writes. Art loading degrades
## gracefully when art_source is absent, so the cat-walk assertions are guarded.

const SandboxScene := preload("res://scenes/ui/office_floor/office_sandbox.tscn")


func _sandbox() -> Control:
	var s: Control = SandboxScene.instantiate()
	add_child_autofree(s)
	return s


func test_instantiates_clean_with_a_floor():
	var s := _sandbox()
	await get_tree().process_frame
	assert_not_null(s._floor, "sandbox built its OfficeFloor child")
	assert_true(s._roster.size() > 0, "opens alive with some people")


func test_populate_up_is_bounded_and_sequenced():
	var s := _sandbox()
	await get_tree().process_frame
	# Drive the full sequence, then push PAST the last stage -- must not overrun or crash.
	for _i in range(20):
		s._populate_up()
	var last: Dictionary = s._POP_STAGES[s._POP_STAGES.size() - 1]
	assert_eq(s._pop_level, s._POP_STAGES.size(), "populate level clamps at the last stage")
	assert_eq(s._roster.size(), int(last["people"]), "final stage people count reached")
	assert_eq(s._cats.size(), int(last["cats"]), "final stage cat count reached")
	assert_eq(s._furniture.size(), int(last["furn"]), "final stage furniture count reached")


func test_populate_down_past_zero_is_a_noop_not_a_crash():
	var s := _sandbox()
	await get_tree().process_frame
	s._populate_up()
	s._populate_up()
	for _i in range(10):
		s._populate_down()   # more downs than ups
	assert_eq(s._pop_level, 0, "populate level floors at 0")
	assert_eq(s._roster.size(), 0, "everyone gone at level 0")
	assert_eq(s._cats.size(), 0, "no cats at level 0")
	assert_eq(s._furniture.size(), 0, "no furniture at level 0")


func test_furniture_hugs_walls_and_never_shares_a_cell():
	var s := _sandbox()
	await get_tree().process_frame
	for _i in range(6):
		s._populate_up()
	assert_true(s._furniture.size() > 0, "furniture was placed")
	# no-overlap: one occupied-cell record per furniture piece
	assert_eq(s._occupied_cells.size(), s._furniture.size(), "no two furniture share a grid cell")
	# wall-affinity: every piece sits within one grid cell of a wall
	var b: Rect2 = s._floor_bounds()
	for spr in s._furniture:
		var p: Vector2 = spr.position
		var cell: float = s.GRID
		var near_wall: bool = (p.x - b.position.x <= cell) or (b.end.x - p.x <= cell) \
			or (p.y - b.position.y <= cell) or (b.end.y - p.y <= cell)
		assert_true(near_wall, "furniture piece hugs a wall (pos=%s bounds=%s)" % [p, b])


func test_occupant_scale_clamps_and_applies_to_sprites():
	var s := _sandbox()
	await get_tree().process_frame
	# Hammer the bounds.
	for _i in range(40):
		s._nudge_occupant_scale(1.0 / s.OCCUPANT_SCALE_STEP)
	assert_almost_eq(s._occupant_scale, s.OCCUPANT_SCALE_MIN, 0.001, "scale floors at MIN")
	for _i in range(40):
		s._nudge_occupant_scale(s.OCCUPANT_SCALE_STEP)
	assert_almost_eq(s._occupant_scale, s.OCCUPANT_SCALE_MAX, 0.001, "scale ceils at MAX")
	# The scale is actually applied to the employee sprite NODE transform (the P0 fix for
	# "spawn one person, it's relatively huge" -- occupant size is now controllable).
	var found := false
	for c in s._floor.get_children():
		if c is OfficeEmployeeSprite:
			assert_almost_eq((c as Node2D).scale.x, s._occupant_scale, 0.01, "sprite node scale follows occupant scale")
			found = true
			break
	assert_true(found, "at least one employee sprite present to scale")


func test_doom_level_clamps_zero_to_one():
	var s := _sandbox()
	await get_tree().process_frame
	for _i in range(30):
		s._nudge_doom(0.1)
	assert_almost_eq(s._doom_level, 1.0, 0.0001, "doom ceils at 1.0")
	for _i in range(30):
		s._nudge_doom(-0.1)
	assert_almost_eq(s._doom_level, 0.0, 0.0001, "doom floors at 0.0")


func test_overlay_stack_places_and_opacity_clamps():
	var s := _sandbox()
	await get_tree().process_frame
	s._toggle_overlay_mode()
	assert_true(s._overlay_mode, "overlay mode on")
	for _i in range(3):
		s._place_overlay()
	assert_eq(s._overlays.size(), 3, "three transparent overlays stacked")
	# opacity of the selected (nearest) overlay clamps within (0, 1]
	for _i in range(30):
		s._nudge_overlay_opacity(0.1)
	var top_op := float(s._overlays[0].get_meta("opacity", -1.0))
	assert_lt(top_op, 1.0001, "opacity ceils at 1.0")
	for _i in range(30):
		s._nudge_overlay_opacity(-0.1)
	var low_op := float(s._overlays[0].get_meta("opacity", -1.0))
	assert_gt(low_op, 0.0, "opacity stays above 0 (still a visible layer)")


func test_destructive_calls_on_empty_are_noops():
	var s := _sandbox()
	await get_tree().process_frame
	s._clear_all()
	# All of these should be safe no-ops on empty collections (no crash, no negative counts).
	s._despawn_person()
	s._remove_cat()
	s._remove_furniture()
	s._remove_nearest_prop(Vector2.ZERO)
	s._remove_nearest_overlay(Vector2.ZERO)
	assert_eq(s._roster.size(), 0, "roster still empty")
	assert_eq(s._cats.size(), 0, "cats still empty")
	assert_eq(s._furniture.size(), 0, "furniture still empty")
	assert_eq(s._placed_props.size(), 0, "props still empty")
	assert_eq(s._overlays.size(), 0, "overlays still empty")
	pass_test("destructive-on-empty did not crash")


func test_cat_walk_cycle_preview_data_is_well_formed():
	# The walk-cycle PREVIEW pixels need a human's eyes; the DATA behind it does not.
	# When art_source is present (git-tracked cat_walk_cat1/2), assert the SpriteFrames a
	# spawned cat previews has the four directional walk clips + an idle, each with frames.
	var s := _sandbox()
	await get_tree().process_frame
	assert_ne(s._cat_walk_report, "", "cat-walk loader produced a status line")
	if s._cat_frame_sets.is_empty():
		pass_test("art_source absent in this checkout -- procedural cats + generation flag (guarded)")
		return
	var frames: SpriteFrames = s._cat_frame_sets[0]["frames"]
	for facing: String in ["south", "east", "north", "west"]:
		var clip := "walk_" + facing
		assert_true(frames.has_animation(clip), "real cat has %s clip" % clip)
		assert_true(frames.get_frame_count(clip) > 0, "%s has frames" % clip)
		assert_true(frames.get_animation_loop(clip), "%s loops" % clip)
	assert_true(frames.has_animation("idle"), "real cat has an idle frame for pauses")

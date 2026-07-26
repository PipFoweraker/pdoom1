extends GutTest
## Robustness / inferential guard for the OFFICE SANDBOX dev toy (v3 mechanics + the v4
## polish pass: compare-by-default, per-floor editing, quality-tier pinning, and the
## #907 prop-manifest renderer integration). The sandbox never
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


func test_compare_is_the_default_view_with_pinned_tiers():
	# v4 (Pip 2026-07-26): side-by-side compare is the DEFAULT on open ("a more
	# useful view"), and the tier mapping is pinned: small=SCUMMY, large=DECENT.
	var s := _sandbox()
	await get_tree().process_frame
	assert_true(s._compare_mode, "compare view is ON by default")
	assert_not_null(s._floor_b, "small starter floor exists on open")
	assert_eq(s._floor._office_style, "decent", "large office renders the DECENT tier")
	assert_eq(s._floor_b._office_style, "scummy", "small office renders the SCUMMY tier")
	# [T] must not silently re-dress the pinned floors while comparing.
	s._cycle_state()
	assert_eq(s._floor._office_style, "decent", "tier stays pinned under [T] in compare")
	assert_eq(s._floor_b._office_style, "scummy", "tier stays pinned under [T] in compare")


func test_small_floor_is_editable():
	# v4: "couldn't add anything to the small office" -- spawn/populate/cat actions
	# now target a specific floor; drive the small floor directly and assert it fills.
	var s := _sandbox()
	await get_tree().process_frame
	var before_b: int = s._roster_b.size()
	s._spawn_person_on(s._floor_b)
	assert_eq(s._roster_b.size(), before_b + 1, "person spawned onto the SMALL floor roster")
	assert_eq(s._floor_b.sprite_count(), s._roster_b.size(), "small floor renders its own roster")
	var main_roster: int = s._roster.size()
	s._add_cat(s._floor_b)
	assert_eq(s._cats_on(s._floor_b), 1, "cat spawned onto the small floor")
	s._remove_cat(s._floor_b)
	assert_eq(s._cats_on(s._floor_b), 0, "cat removed from the small floor")
	# Populate the small floor to stage 2 without disturbing the large floor.
	s._pop_level_b = 2
	s._apply_pop_stage(s._floor_b)
	var stage: Dictionary = s._POP_STAGES[1]
	assert_eq(s._roster_b.size(), int(stage["people"]), "small floor populated to stage 2 people")
	assert_eq(s._roster.size(), main_roster, "large floor roster untouched by small-floor populate")


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
	# no-overlap: every piece owns a distinct registered cell (the occupancy dict also
	# holds small-floor starter cells + manifested-prop footprints, so compare per-piece).
	var seen := {}
	for spr in s._furniture:
		var key := String(spr.get_meta("cell_key", ""))
		assert_ne(key, "", "furniture piece carries its occupancy cell key")
		assert_false(seen.has(key), "no two furniture share a grid cell (%s)" % key)
		assert_true(s._occupied_cells.has(key), "furniture cell registered occupied")
		seen[key] = true
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


func test_compare_view_toggles_and_builds_second_floor():
	# #899/#793 scale-compare view, v4 default-ON: the sandbox OPENS comparing --
	# starter floor built, complex floor topped up. [V] tears the starter floor down
	# to the single-floor view; [V] again rebuilds it.
	var s := _sandbox()
	await get_tree().process_frame
	assert_true(s._compare_mode, "compare mode on by default")
	assert_not_null(s._floor_b, "starter (left) floor exists")
	assert_eq(s._roster_b.size(), 3, "starter floor has 3 staff")
	assert_true(s._roster.size() >= 7, "complex floor topped up to 7+ staff")
	assert_true(s._cats.size() >= 2, "complex floor has cats")
	await get_tree().process_frame   # furniture spawns deferred (needs a layout pass)
	assert_true(s._furniture_b.size() > 0, "starter floor got sparse props")
	assert_true(s._furniture.size() > 0, "complex floor got wall furniture")
	s._toggle_compare()
	assert_false(s._compare_mode, "compare mode off after [V]")
	assert_null(s._floor_b, "starter floor torn down")
	assert_eq(s._pop_level_b, 0, "small-floor populate level reset on teardown")
	s._toggle_compare()
	await get_tree().process_frame
	assert_true(s._compare_mode, "compare mode back on")
	assert_not_null(s._floor_b, "starter floor rebuilt")


func test_nearest_person_pick_radius_bounds_selection():
	# #899: the per-sprite scale keys must NOT silently retarget a far-away sprite.
	var s := _sandbox()
	await get_tree().process_frame
	assert_null(s._nearest_person(Vector2(-10000.0, -10000.0)),
		"no sprite picked outside PICK_RADIUS")


func _fake_tex(w: int, h: int) -> Texture2D:
	return ImageTexture.create_from_image(Image.create(w, h, false, Image.FORMAT_RGBA8))


func test_prop_scale_and_anchor_honour_the_manifest():
	# #907 integration: a promoted asset whose basename is manifested AND whose texture
	# matches the manifest canvas renders at authored proportions (height_px/subject_h)
	# and feet-anchors at anchor_px; anything else keeps the legacy 46px force-scale.
	var s := _sandbox()
	await get_tree().process_frame
	var cooler := _fake_tex(64, 120)              # matches water_cooler canvas_px
	assert_eq(s._manifest_id_for(cooler, "props/water_cooler.png"), "water_cooler",
		"basename resolves to the manifest id when the canvas matches")
	var scl: Vector2 = s._prop_scale(cooler, "props/water_cooler.png")
	assert_almost_eq(scl.x, (3.5 * 64.0) / 109.0, 0.001,
		"manifested prop scales subject to height_px, not PROP_TARGET_H")
	var spr: Sprite2D = autofree(Sprite2D.new())
	spr.texture = cooler
	s._apply_prop_anchor(spr, cooler, "props/water_cooler.png")
	assert_false(spr.centered, "manifested prop is feet-anchored (not centred)")
	assert_eq(spr.offset, Vector2(-31.5, -114.0), "offset puts anchor_px on the node origin")
	# Canvas mismatch (an off-resolution art_source master) degrades to the legacy path.
	var master := _fake_tex(128, 240)
	assert_eq(s._manifest_id_for(master, "props/water_cooler.png"), "",
		"canvas mismatch -> not trusted as the manifested asset")
	var legacy: Vector2 = s._prop_scale(master, "props/water_cooler.png")
	assert_almost_eq(legacy.x, s.PROP_TARGET_H / 240.0, 0.001, "legacy force-scale kept")
	s._apply_prop_anchor(spr, master, "props/water_cooler.png")
	assert_true(spr.centered, "unmanifested texture restores centred placement")


func test_prop_pool_tier_selection_honours_style_tags_with_decent_fallback():
	# Canonical ladder scummy/decent/premium (2026-07-26): manifested decent art is
	# OFFERED in the scummy tier while its scummy variant art is missing (fallback
	# unchanged, no tinting); unmanifested art keeps keyword inference.
	var s := _sandbox()
	await get_tree().process_frame
	var scummy_bias: Array = s._state_named("scummy").get("bias", [])
	var decent_bias: Array = s._state_named("decent").get("bias", [])
	var manifested := {"id": "props/water_cooler.png"}
	assert_true(s._prop_serves_tier(manifested, "decent", decent_bias),
		"decent-tagged manifested art serves the decent tier")
	assert_true(s._prop_serves_tier(manifested, "scummy", scummy_bias),
		"decent-tagged manifested art stands in for the missing scummy variant")
	var kw_scummy := {"id": "props/lamp_scummy.png"}   # unmanifested, keyword-tiered
	assert_true(s._prop_serves_tier(kw_scummy, "scummy", scummy_bias),
		"scummy-keyword art serves the scummy tier")
	assert_false(s._prop_serves_tier(kw_scummy, "decent", decent_bias),
		"scummy-keyword art is not offered in the decent tier")
	var untiered := {"id": "props/beanbag.png"}
	assert_true(s._prop_serves_tier(untiered, "scummy", scummy_bias),
		"untiered art counts as decent-fallback and is offered everywhere")
	assert_true(s._prop_serves_tier(untiered, "decent", decent_bias),
		"untiered art counts as decent-fallback and is offered everywhere")


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

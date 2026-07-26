extends GutTest
## #913 alt-clip splice hook ("butt-flash"): when a SpriteFrames carries
## "<clip>_alt" (workers: "walking_north_alt"; cats: "walk_north_alt"), the
## walker occasionally plays the alt loop ONCE, then returns to the base clip.
## DETERMINISTIC: the splice decision is a pure hash of entity id + loop count
## (should_play_alt, ~1-in-6 loops) -- no RNG, reproducible, phase-offset per
## entity. Art arrives later from the cat sweep; these tests use synthetic
## frames, proving the hook is art-agnostic.

const EmployeeSpriteScript := preload("res://scripts/ui/office_floor/employee_sprite.gd")

const PERIOD := OfficeEmployeeSprite.ALT_CLIP_PERIOD


func _make_frames(clips: Array) -> SpriteFrames:
	var sf := SpriteFrames.new()
	var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	img.fill(Color.WHITE)
	var tex := ImageTexture.create_from_image(img)
	var first := true
	for c in clips:
		var clip := String(c)
		if first:
			sf.rename_animation("default", clip)
			first = false
		elif not sf.has_animation(clip):
			sf.add_animation(clip)
		sf.set_animation_loop(clip, true)
		sf.set_animation_speed(clip, 6.0)
		sf.add_frame(clip, tex)
		sf.add_frame(clip, tex)
	return sf


func _make_sprite(clips: Array, id: String) -> OfficeEmployeeSprite:
	var spr: OfficeEmployeeSprite = EmployeeSpriteScript.new()
	add_child_autofree(spr)
	spr.bounds = Rect2(0, 0, 400, 300)
	spr.tier = 1
	spr.entity_id = id
	spr.set_sprite_frames(_make_frames(clips))
	return spr


func _first_trigger_loop(id: String) -> int:
	for l in range(1, PERIOD + 1):
		if OfficeEmployeeSprite.should_play_alt(id, l):
			return l
	return -1


# --- should_play_alt: pure + deterministic -----------------------------------

func test_exactly_one_splice_per_period_window():
	for id in ["worker_0", "worker_1", "cat_2", "zz"]:
		var triggers := 0
		for l in range(1, PERIOD + 1):
			if OfficeEmployeeSprite.should_play_alt(String(id), l):
				triggers += 1
		assert_eq(triggers, 1, "%s: exactly 1 splice in any %d consecutive loops" % [id, PERIOD])


func test_should_play_alt_is_deterministic():
	for l in range(0, 24):
		assert_eq(
			OfficeEmployeeSprite.should_play_alt("stable_id", l),
			OfficeEmployeeSprite.should_play_alt("stable_id", l),
			"same id + loop -> same decision, every time (loop %d)" % l)


func test_trigger_loops_are_periodic_per_entity():
	var first := _first_trigger_loop("periodic_id")
	assert_gt(first, 0, "a trigger exists inside the first window")
	assert_true(OfficeEmployeeSprite.should_play_alt("periodic_id", first + PERIOD),
		"triggers repeat every ALT_CLIP_PERIOD loops")
	assert_false(OfficeEmployeeSprite.should_play_alt("periodic_id", first + 1),
		"the loop right after a trigger does not re-trigger")


func test_non_positive_period_never_triggers():
	assert_false(OfficeEmployeeSprite.should_play_alt("x", 3, 0))
	assert_false(OfficeEmployeeSprite.should_play_alt("x", 3, -2))


# --- worker sprite: splice in, one pass, splice out --------------------------

func test_worker_splices_alt_once_then_returns_to_base():
	var id := "splicer"
	var spr := _make_sprite(["walking", "walking_alt"], id)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._refresh_visual()
	assert_eq(String(spr._anim.animation), "walking", "base clip playing")
	var trigger := _first_trigger_loop(id)
	assert_gt(trigger, 0)
	for l in range(1, trigger):
		spr._on_animation_looped()
		assert_eq(String(spr._anim.animation), "walking", "no splice before the trigger loop (loop %d)" % l)
	spr._on_animation_looped()   # the trigger loop
	assert_eq(String(spr._anim.animation), "walking_alt", "alt clip spliced in on the deterministic loop")
	assert_true(spr._alt_active)
	spr._on_animation_looped()   # the alt loop completes its single pass
	assert_eq(String(spr._anim.animation), "walking", "back to the base clip after ONE alt pass")
	assert_false(spr._alt_active)


func test_directional_alt_clip_contract():
	# The documented contract name: "walking_north_alt" splices over "walking_north".
	var id := "north_walker"
	var spr := _make_sprite(["walking", "walking_north", "walking_north_alt"], id)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._facing = OfficeEmployeeSprite.FACING_NORTH
	spr._facing_active = true
	spr._update_facing_visual()
	assert_eq(String(spr._anim.animation), "walking_north", "directional base clip playing")
	var trigger := _first_trigger_loop(id)
	for _l in range(1, trigger):
		spr._on_animation_looped()
	spr._on_animation_looped()
	assert_eq(String(spr._anim.animation), "walking_north_alt", "walking_north_alt spliced in")


func test_no_alt_clip_means_hook_stays_dormant():
	var spr := _make_sprite(["walking"], "dormant")
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._refresh_visual()
	for _l in range(PERIOD * 3):
		spr._on_animation_looped()
		assert_eq(String(spr._anim.animation), "walking", "no *_alt clip -> nothing ever splices")
	assert_false(spr._alt_active)


func test_state_change_cancels_an_active_splice():
	var id := "cancelled"
	var spr := _make_sprite(["walking", "walking_alt", "working"], id)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._refresh_visual()
	var trigger := _first_trigger_loop(id)
	for _l in range(trigger):
		spr._on_animation_looped()
	assert_true(spr._alt_active, "alt is mid-splice")
	spr._show_animated_clip("working")
	assert_false(spr._alt_active, "wanting a different clip cancels the splice")
	assert_eq(String(spr._anim.animation), "working")


func test_non_looping_alt_ends_via_animation_finished():
	var id := "oneshot"
	var spr := _make_sprite(["walking", "walking_alt"], id)
	spr._anim.sprite_frames.set_animation_loop("walking_alt", false)
	spr.sprite_state = EmployeeFSM.STATE_WALKING
	spr._refresh_visual()
	var trigger := _first_trigger_loop(id)
	for _l in range(trigger):
		spr._on_animation_looped()
	assert_true(spr._alt_active)
	spr._on_animation_finished()
	assert_false(spr._alt_active)
	assert_eq(String(spr._anim.animation), "walking", "non-looping alt returns to base on finish")


# --- shared cat scale ruling (#913 sneaky 1.1x) ------------------------------

func test_cat_tile_ratio_is_the_1_1x_bump():
	assert_almost_eq(OfficeEmployeeSprite.CAT_TILE_RATIO, 0.55, 0.0001,
		"cats read 0.55 tile (0.5 * 1.1 sneaky bump, Pip-approved 2026-07-26)")

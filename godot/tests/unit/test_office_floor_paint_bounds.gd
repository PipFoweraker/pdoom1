extends GutTest
## #793 (layering + scale): locks the two invariants that the v0.13.2 league recording
## broke at 00:54 -- the office-floor server rack painting ON TOP of the feed text, and
## a worker sprite drawn nearly as tall as the room was deep.
##
## WHAT THIS CAN AND CANNOT PROVE. These are ARITHMETIC assertions over the rects the
## renderer computes, not pixel checks: a headless test cannot see a frame. They prove
## the drawn geometry stays inside the control and that the person/room ratio is sane.
## They CANNOT prove the result looks right. That still needs a human looking at it.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")

# The size WatchScreen actually gives the floor (watch_screen.gd sets height 260 and
# EXPAND_FILL for the width; 360 is the floor's own custom_minimum_size width).
const LIVE_SIZE := Vector2(360, 260)

var _floor: OfficeFloor


func before_each() -> void:
	_floor = _sized_floor(LIVE_SIZE)


## A floor pinned to an exact pixel size. The scene root is anchored full-rect, so a
## bare instance adopts the VIEWPORT size when parented outside a container -- pinning
## the anchors top-left is what makes `size` actually stick.
func _sized_floor(px: Vector2) -> OfficeFloor:
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	f.set_anchors_preset(Control.PRESET_TOP_LEFT)
	f.custom_minimum_size = Vector2.ZERO
	f.size = px
	return f


func test_floor_clips_its_own_painting() -> void:
	# The structural guarantee. A Control does NOT clip its own _draw() by default, and
	# the floor is the LAST sibling in the WATCH VBox, so anything it paints above its
	# own rect lands on the feed panel. clip_contents makes the rect authoritative
	# whatever a future art/anchor/scale change does.
	assert_true(_floor.clip_contents,
		"OfficeFloor must clip_contents so it can never paint over the feed above it")


func test_floor_reserves_headroom_above_the_walkable_floor() -> void:
	# Feet-anchored props extend UPWARD. If the walkable floor's top edge is the
	# control's top edge, a prop at the back wall must paint outside the control --
	# that is the defect, expressed as geometry.
	var b: Rect2 = _floor._bounds()
	assert_gt(b.position.y, 8.0,
		"walkable floor must start below a back-wall headroom band, not at the control top")
	assert_lt(b.size.y, LIVE_SIZE.y,
		"the walkable floor is a subset of the control, not the whole of it")


func test_every_landmark_prop_paints_inside_the_control() -> void:
	# The actual regression: server_cluster is 3.5 authored tiles tall and stands at
	# 18% depth. At the old 64px subject tile that was 224px of art rising out of a
	# 260px control, ~178px of it above the top edge and over the feed.
	var b: Rect2 = _floor._bounds()
	var z: Dictionary = _floor._zones(b)
	var placements := {
		"water_cooler": z["water_pos"],
		"filing_cabinet": z["fridge_pos"],
		"server_cluster": _floor._server_decor_pos(b),
	}
	var control := Rect2(Vector2.ZERO, LIVE_SIZE)
	for id in placements.keys():
		var rect: Rect2 = _prop_draw_rect(String(id), placements[id])
		assert_true(control.encloses(rect),
			"%s draw rect %s must fit inside the control %s" % [id, rect, control])


func test_worker_is_a_person_in_a_room_not_a_giant() -> void:
	# The scale half of #793. The recording showed a worker about as tall as the floor
	# was deep. A person should read as a modest fraction of the room's depth.
	var depth: float = _floor._bounds().size.y
	var h: float = _floor.char_target_height()
	assert_gt(h, 0.0, "worker target height must be positive")
	var ratio := h / depth
	assert_lt(ratio, 0.40, "a worker must be well under half the room's depth (was ~0.52)")
	assert_gt(ratio, 0.15, "...but still big enough to read as a person, not a speck")


func test_worker_sprites_receive_the_room_proportionate_height() -> void:
	# The floor must PUSH its derived height into the sprites; a sprite left on the
	# 128px reference default is the bug back again.
	_floor.set_tier(1)
	_floor.set_roster([
		{"id": "a", "name": "Ellis Wilson", "specialization": "safety"},
		{"id": "b", "name": "Second Person", "specialization": "capabilities"},
	])
	var found := 0
	for child in _floor.get_children():
		if child is OfficeEmployeeSprite:
			found += 1
			assert_almost_eq(child.char_target_h, _floor.char_target_height(), 0.01,
				"each sprite is sized against the room, not the 64px reference tile")
	assert_eq(found, 2, "both roster members rendered a sprite")


func test_subject_scale_tracks_the_room_size() -> void:
	# Responsiveness: halve the strip, the subjects halve too, so the proportion
	# survives any layout Pip lands on.
	var tall: float = _floor.char_target_height()
	var short: float = _sized_floor(Vector2(360, 130)).char_target_height()
	assert_lt(short, tall, "a shorter strip yields shorter people")


## Reproduce _draw_prop's manifest branch: the rect the renderer will actually paint.
func _prop_draw_rect(id: String, feet: Vector2) -> Rect2:
	var e: Dictionary = PropCatalogue.get_entry(id)
	assert_false(e.is_empty(), "%s must be manifested for this test to mean anything" % id)
	var subj: Array = e.get("subject_px", [])
	var canvas: Array = e.get("canvas_px", [])
	var src := Vector2(float(canvas[0]), float(canvas[1]))
	var scl: float = PropCatalogue.height_px(id, _floor._subject_tile_px()) / float(subj[1])
	var anchor: Vector2 = PropCatalogue.anchor(id)
	if anchor == PropCatalogue.ANCHOR_UNSET:
		anchor = Vector2(src.x * 0.5, src.y)
	return Rect2(feet - anchor * scl, src * scl)

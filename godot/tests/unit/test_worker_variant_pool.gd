extends GutTest
## Worker appearance variant pool (#793 mechanism half). Art-agnostic registry:
## data/office/worker_variants.json lists variant id -> SpriteFrames path;
## appearance_id maps to a variant via a pure, stable function (posmod of int
## id / stable String hash); a missing variant degrades to the floor's shared
## fallback frames. Variant 0 is wired to the CURRENT shared asset, so today's
## render is unchanged -- these tests lock the mechanism, not the art.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")
const SharedWorkerFrames := preload("res://assets/office_floor/artloop_char/office_worker.tres")


func after_each():
	WorkerVariantPool._reset_for_test()


# --- the shipped manifest ----------------------------------------------------

func test_manifest_loads_with_variant_zero_as_the_shared_asset():
	assert_gt(WorkerVariantPool.count(), 0, "worker_variants.json lists at least one variant")
	var f := WorkerVariantPool.frames_for(0)
	assert_not_null(f, "variant 0 resolves")
	assert_eq(f, SharedWorkerFrames,
		"variant 0 IS the current shared office_worker.tres -- behaviour unchanged until new art is triaged in")
	assert_true(f.has_animation("walking"), "resolved frames honour the clip contract")


# --- pure, stable assignment -------------------------------------------------

func test_int_appearance_ids_map_by_posmod():
	assert_eq(WorkerVariantPool.variant_index_for(0, 3), 0)
	assert_eq(WorkerVariantPool.variant_index_for(7, 3), 1)
	assert_eq(WorkerVariantPool.variant_index_for(-1, 3), 2, "negative ids still land in range")


func test_string_appearance_ids_are_stable_and_in_range():
	for id in ["alice", "bob", "r_129", ""]:
		var a := WorkerVariantPool.variant_index_for(String(id), 5)
		var b := WorkerVariantPool.variant_index_for(String(id), 5)
		assert_eq(a, b, "'%s': same appearance -> same variant, every call" % id)
		assert_between(a, 0, 4, "'%s': index in range" % id)


func test_empty_pool_returns_sentinel():
	assert_eq(WorkerVariantPool.variant_index_for(3, 0), -1)


func test_assignment_ignores_roster_order_and_size():
	# The mapping depends ONLY on appearance_id + variant count -- re-querying in
	# any order, interleaved with other ids, never changes an answer.
	var expected := WorkerVariantPool.variant_index_for(11, 4)
	for other in [99, 2, 57, 11, 0]:
		WorkerVariantPool.variant_index_for(int(other), 4)
	assert_eq(WorkerVariantPool.variant_index_for(11, 4), expected)


# --- graceful fallback -------------------------------------------------------

func test_missing_variant_art_resolves_null():
	WorkerVariantPool._override_variants_for_test([
		{"id": "ghost", "frames": "res://assets/does_not_exist.tres"},
	])
	assert_null(WorkerVariantPool.frames_for(0), "unloadable variant art -> null (caller falls back)")


func test_floor_falls_back_to_shared_frames_when_variant_missing():
	WorkerVariantPool._override_variants_for_test([
		{"id": "ghost", "frames": "res://assets/does_not_exist.tres"},
	])
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	await get_tree().process_frame
	f.set_tier(1)
	f.set_sprite_frames(SharedWorkerFrames)
	f.set_roster([{"id": 0, "name": "A", "assigned": true, "appearance_id": 0}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	assert_eq(spr._anim.sprite_frames, SharedWorkerFrames,
		"variant unresolved -> the shared fallback frames render")


# --- OfficeFloor wiring ------------------------------------------------------

func test_floor_applies_variant_frames_by_appearance_id():
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	await get_tree().process_frame
	f.set_tier(1)
	f.set_roster([{"id": 0, "name": "A", "assigned": true, "appearance_id": 3}])
	var spr: OfficeEmployeeSprite = f._sprites[0]
	assert_eq(spr._anim.sprite_frames, SharedWorkerFrames,
		"pool ON by default: appearance maps to variant 0 == the shared asset (unchanged render)")


func test_pool_off_applies_shared_frames_uniformly():
	# The sandbox colour-skin path: bypassing the pool must let an explicit
	# set_sprite_frames() win for every sprite, new and existing.
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	await get_tree().process_frame
	f.set_tier(1)
	f.set_roster([{"id": 0, "name": "A", "assigned": true, "appearance_id": 1}])
	f.set_use_variant_pool(false)
	var custom := SpriteFrames.new()
	custom.add_animation("walking")
	f.set_sprite_frames(custom)
	var spr: OfficeEmployeeSprite = f._sprites[0]
	assert_eq(spr._anim.sprite_frames, custom, "pool OFF -> the explicit shared frames apply")
	f.set_roster([
		{"id": 0, "name": "A", "assigned": true, "appearance_id": 1},
		{"id": 1, "name": "B", "assigned": true, "appearance_id": 2},
	])
	var spr_b: OfficeEmployeeSprite = f._sprites[1]
	assert_eq(spr_b._anim.sprite_frames, custom, "new sprites also get the shared frames while the pool is OFF")

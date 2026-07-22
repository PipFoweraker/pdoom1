extends GutTest
## Guards the office-floor WATCH integration (step 1): the walker COUNT tracks the staff
## count -- walkers spawn when staff are hired and despawn when staff leave -- and the
## read-only state-dict adapter maps the serialized GameState shape correctly. PURE VIEW
## (ADR-0006): no GameManager, no seeded RNG, no writes; instantiated standalone so the
## guard stays fast and deterministic.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")


func _floor() -> OfficeFloor:
	var f: OfficeFloor = OfficeFloorScene.instantiate()
	add_child_autofree(f)
	return f


func _roster(n: int) -> Array:
	var out: Array = []
	for i in range(n):
		out.append({"id": i, "name": "R%d" % i, "specialization": "safety", "assigned": true})
	return out


func test_walker_count_matches_roster():
	var f := _floor()
	await get_tree().process_frame
	f.set_roster(_roster(3))
	assert_eq(f.sprite_count(), 3, "3 staff -> 3 walkers")


func test_walker_spawns_when_staff_hired():
	var f := _floor()
	await get_tree().process_frame
	f.set_roster(_roster(2))
	assert_eq(f.sprite_count(), 2, "baseline 2 walkers")
	f.set_roster(_roster(4))
	assert_eq(f.sprite_count(), 4, "hiring 2 more -> 2 new walkers appear")


func test_walker_despawns_when_staff_leaves():
	var f := _floor()
	await get_tree().process_frame
	f.set_roster(_roster(5))
	assert_eq(f.sprite_count(), 5, "baseline 5 walkers")
	f.set_roster(_roster(2))
	assert_eq(f.sprite_count(), 2, "losing 3 staff -> 3 walkers leave")


func test_empty_roster_clears_floor():
	var f := _floor()
	await get_tree().process_frame
	f.set_roster(_roster(3))
	f.set_roster([])
	assert_eq(f.sprite_count(), 0, "no staff -> empty floor")


func test_snapshot_from_state_dict_counts_and_flags():
	# GameState.to_dict() shape: "researchers" is an Array of Researcher.to_dict() dicts.
	var state := {
		"researchers": [
			{"name": "A", "specialization": "safety", "burnout": 5.0, "loyalty": 70, "appearance_id": 11},
			{"name": "B", "specialization": "capabilities", "burnout": 90.0, "loyalty": 60, "appearance_id": 22},
			{"name": "C", "specialization": "alignment", "burnout": 10.0, "loyalty": 50, "appearance_id": 33},
		],
		"unmanaged_count": 1,
	}
	var snap := OfficeFloor.snapshot_from_state_dict(state)
	assert_eq(snap.size(), 3, "3 researchers -> 3 snapshot entries")
	assert_eq(String(snap[0]["name"]), "A", "name mapped from dict")
	assert_false(bool(snap[0]["unmanaged"]), "first researcher is managed")
	assert_true(bool(snap[2]["unmanaged"]), "trailing researcher flagged unmanaged (count=1)")
	assert_eq(int(snap[1]["appearance_id"]), 22, "appearance_id carried through (identity seam #758)")


func test_snapshot_from_state_dict_degrades_on_missing():
	assert_eq(OfficeFloor.snapshot_from_state_dict({}).size(), 0, "no researchers key -> empty")
	assert_eq(OfficeFloor.snapshot_from_state_dict({"researchers": 5}).size(), 0, "non-array -> empty")


func test_snapshot_drives_floor_count():
	# End-to-end of the read path: state dict -> adapter -> set_roster -> walker count.
	var f := _floor()
	await get_tree().process_frame
	var state := {"researchers": [{"name": "A"}, {"name": "B"}], "unmanaged_count": 0}
	f.set_roster(OfficeFloor.snapshot_from_state_dict(state))
	assert_eq(f.sprite_count(), 2, "adapter + set_roster -> walker count tracks staff")

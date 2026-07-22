extends GutTest
## Unit tests for EmployeeFSM -- the pure state-mapping logic behind the OfficeFloor
## Tier-1 sprites. Tests the mapping (mechanical state -> sprite state) ONLY, never
## rendering. This is the readout contract: the floor is the dashboard.

func test_working_when_assigned_and_healthy():
	var emp := {"assigned": true, "burnout": 10.0, "loyalty": 70, "unmanaged": false}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_WORKING, "Assigned + healthy -> working")

func test_stressed_when_burnt_out():
	# >= 80 matches Researcher.is_burned_out()
	var emp := {"assigned": true, "burnout": 80.0, "loyalty": 70, "unmanaged": false}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_STRESSED, "Burnout>=80 -> stressed")

func test_stressed_dominates_unmanaged():
	# Burnout is the most salient problem; wins over drift.
	var emp := {"assigned": true, "burnout": 95.0, "unmanaged": true}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_STRESSED, "Stressed outranks drifting")

func test_walking_when_unmanaged():
	var emp := {"assigned": true, "burnout": 20.0, "loyalty": 60, "unmanaged": true}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_WALKING, "Unmanaged (not burnt) -> walking/drift")

func test_idle_when_disengaged_low_loyalty():
	var emp := {"assigned": true, "burnout": 10.0, "loyalty": 5, "unmanaged": false}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_IDLE, "Very low loyalty -> idle (checked out)")

func test_just_below_burnout_threshold_not_stressed():
	var emp := {"assigned": true, "burnout": 79.9, "loyalty": 60, "unmanaged": false}
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_WORKING, "Below 80 burnout is not stressed")

# --- graceful degradation: absent fields default to idle/wander, never a false working ---
func test_empty_dict_degrades_to_idle():
	assert_eq(EmployeeFSM.map_state({}), EmployeeFSM.STATE_IDLE, "No data -> idle (graceful)")

func test_missing_assigned_is_idle_not_working():
	var emp := {"burnout": 10.0, "loyalty": 70}  # no 'assigned', not unmanaged
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_IDLE, "Absent 'assigned' must not fake working")

func test_missing_loyalty_does_not_force_idle():
	var emp := {"assigned": true, "burnout": 10.0}  # no loyalty field
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_WORKING, "Absent loyalty -> not treated as disengaged")

func test_unmanaged_without_assigned_still_walks():
	var emp := {"unmanaged": true}  # minimal
	assert_eq(EmployeeFSM.map_state(emp), EmployeeFSM.STATE_WALKING, "Unmanaged flag alone -> walking")

# --- roster-level mapping ---
func test_map_roster_index_aligned():
	var roster := [
		{"assigned": true, "burnout": 5.0},                 # working
		{"assigned": true, "burnout": 90.0},                # stressed
		{"assigned": true, "unmanaged": true},              # walking
		{},                                                 # idle
	]
	var states := EmployeeFSM.map_roster(roster)
	assert_eq(states.size(), 4, "One state per employee")
	assert_eq(states[0], EmployeeFSM.STATE_WORKING)
	assert_eq(states[1], EmployeeFSM.STATE_STRESSED)
	assert_eq(states[2], EmployeeFSM.STATE_WALKING)
	assert_eq(states[3], EmployeeFSM.STATE_IDLE)

func test_map_roster_skips_non_dict_entries():
	var roster := [{"assigned": true, "burnout": 5.0}, "garbage", 42]
	var states := EmployeeFSM.map_roster(roster)
	assert_eq(states.size(), 1, "Non-dict entries are skipped")

func test_all_states_are_distinct_and_named():
	assert_eq(EmployeeFSM.ALL_STATES.size(), 4, "Four sprite states")
	var uniq := {}
	for s in EmployeeFSM.ALL_STATES:
		uniq[s] = true
	assert_eq(uniq.size(), 4, "All state names distinct")

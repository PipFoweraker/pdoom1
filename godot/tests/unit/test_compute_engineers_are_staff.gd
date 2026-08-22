extends GutTest
## #1247: compute engineers are PEOPLE, not an integer.
##
## Found by Pip playing the v0.14.2 release build, 2026-08-21: "When I acquire a
## startup, my employee screen tells me I have 2 engineers but they don't load
## into the sim." The Employee Management screen showed, in one frame:
##
##     Team Size: 1 employees
##     * Safety Researchers: 1
##     * Compute Engineers: 2
##
## Ruled by Pip 2026-08-22: "real STAFF, but they might not eg produce as much
## research?" So they get Researcher objects AND their own output profile.

func _state(seed_str: String):
	var s = GameState.new(seed_str)
	s.money = 500000.0
	return s

func test_headcount_and_role_counts_agree():
	# The exact contradiction from the screenshot: object model vs counter model.
	var s = _state("i1247_agree")
	GameActions._acquire_staff(s, "safety", 1)
	GameActions._acquire_staff(s, "compute_engineer", 2)
	assert_eq(s.get_total_staff(), 3, "three people, three staff")
	assert_eq(s.safety_researchers + s.capability_researchers + s.compute_engineers,
		s.get_total_staff() - s.managers,
		"the role counters sum to the headcount -- they are one model now")

func test_acquired_staff_are_real_researcher_objects():
	var s = _state("i1247_objects")
	GameActions._acquire_staff(s, "compute_engineer", 2)
	assert_eq(s.researchers.size(), 2, "acquisition creates people, not integers")
	for r in s.researchers:
		assert_eq(r.specialization, "compute_engineer", "lane survives generate_random")
		assert_ne(r.researcher_name, "", "a person has a name")
		assert_gt(r.base_productivity, 0.0, "and a productivity the sim can read")

func test_acquired_staff_occupy_desks():
	# The sharpest consequence: desks_free derives from get_total_staff(), so staff
	# that did not count occupied no desks and acquisition was a route around the
	# office cap that #791's early economy treats as a real constraint.
	var s = _state("i1247_desks")
	var before := s.get_total_staff()
	GameActions._acquire_staff(s, "compute_engineer", 2)
	assert_eq(s.get_total_staff(), before + 2, "acquired staff consume headcount")

func test_compute_engineers_produce_less_research_than_safety():
	var ce: float = Researcher.SPECIALIZATIONS["compute_engineer"]["research_speed_modifier"]
	assert_lt(ce, 1.0, "Pip's ruling: real staff, but not as much research")
	assert_gt(ce, 0.0, "and NOT zero -- before #1247 they produced nothing at all")

func test_compute_engineer_has_a_full_role_profile():
	var spec: Dictionary = Researcher.SPECIALIZATIONS.get("compute_engineer", {})
	assert_true(spec.has("name"), "shows a human-readable role")
	assert_true(spec.has("base_cost"), "and costs a salary like any other hire")

func test_removing_one_keeps_both_models_in_step():
	var s = _state("i1247_remove")
	GameActions._acquire_staff(s, "compute_engineer", 2)
	var victim = s.researchers[0]
	s.remove_researcher(victim)
	assert_eq(s.compute_engineers, 1, "the counter follows the person out")
	assert_eq(s.get_total_staff(), 1, "and so does the headcount")

func test_total_staff_no_longer_switches_models():
	# The root cause. With ZERO researchers the old code fell back to the counter
	# sum; with one it switched to the object list and silently stopped counting
	# anybody who was only ever an integer.
	var s = _state("i1247_noswitch")
	assert_eq(s.get_total_staff(), 0, "empty lab counts zero either way")
	GameActions._acquire_staff(s, "safety", 1)
	assert_eq(s.get_total_staff(), 1, "one person, one staff -- no model switch")

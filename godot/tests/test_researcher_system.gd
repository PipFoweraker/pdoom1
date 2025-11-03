extends GutTest
## Test researcher specialization system

func test_researcher_initialization():
	var researcher = Researcher.new("safety", "Test Researcher")
	assert_eq(researcher.specialization, "safety")
	assert_eq(researcher.researcher_name, "Test Researcher")
	assert_between(researcher.skill_level, 3, 7, "New hire skill should be 3-7")
	assert_between(researcher.loyalty, 40, 70, "New hire loyalty should be 40-70")

func test_researcher_auto_name_generation():
	var researcher = Researcher.new("capabilities")
	assert_ne(researcher.researcher_name, "", "Should generate a name")
	assert_true(researcher.researcher_name.contains(" "), "Should have first and last name")

func test_specialization_costs():
	var safety = Researcher.new("safety")
	assert_eq(safety.salary_expectation, 60000.0)

	var interp = Researcher.new("interpretability")
	assert_eq(interp.salary_expectation, 70000.0)

	var align = Researcher.new("alignment")
	assert_eq(align.salary_expectation, 65000.0)

func test_productivity_calculation():
	var researcher = Researcher.new("safety")
	researcher.skill_level = 5
	researcher.base_productivity = 1.0
	researcher.burnout = 0.0

	var productivity = researcher.get_effective_productivity()
	assert_almost_eq(productivity, 1.0, 0.1)

func test_burnout_reduces_productivity():
	var researcher = Researcher.new("safety")
	researcher.base_productivity = 1.0
	researcher.burnout = 50.0  # 50% burned out

	var productivity = researcher.get_effective_productivity()
	assert_lt(productivity, 1.0, "Burnout should reduce productivity")
	assert_almost_eq(productivity, 0.75, 0.1, "50 burnout = 25% reduction")

func test_burnout_accumulation():
	var researcher = Researcher.new("safety")
	researcher.burnout = 0.0

	researcher.accumulate_burnout(10.0)
	assert_eq(researcher.burnout, 10.0)

	researcher.accumulate_burnout(5.0)
	assert_eq(researcher.burnout, 15.0)

func test_burnout_clamping():
	var researcher = Researcher.new("safety")
	researcher.burnout = 95.0

	researcher.accumulate_burnout(20.0)
	assert_eq(researcher.burnout, 100.0, "Burnout should cap at 100")

func test_workaholic_trait_productivity():
	var researcher = Researcher.new("safety")
	researcher.base_productivity = 1.0
	researcher.burnout = 0.0
	researcher.add_trait("workaholic")

	var productivity = researcher.get_effective_productivity()
	assert_almost_eq(productivity, 1.2, 0.05, "Workaholic = +20% productivity")

func test_workaholic_burnout_rate():
	var researcher = Researcher.new("safety")
	researcher.add_trait("workaholic")
	researcher.burnout = 0.0

	researcher.accumulate_burnout(1.0)
	# Base 1.0 + workaholic 2.0 = 3.0 total
	assert_eq(researcher.burnout, 3.0, "Workaholic accumulates extra burnout")

func test_prima_donna_salary_penalty():
	var researcher = Researcher.new("safety")
	researcher.add_trait("prima_donna")
	researcher.base_productivity = 1.0
	researcher.burnout = 0.0
	researcher.salary_expectation = 60000.0

	# Paid well - no penalty
	researcher.current_salary = 60000.0
	assert_almost_eq(researcher.get_effective_productivity(), 1.0, 0.05)

	# Underpaid - productivity penalty
	researcher.current_salary = 50000.0  # < 90% of expectation
	var productivity = researcher.get_effective_productivity()
	assert_lt(productivity, 1.0, "Prima donna should lose productivity when underpaid")
	assert_almost_eq(productivity, 0.8, 0.05, "Should be 20% penalty")

func test_safety_conscious_trait_doom_modifier():
	var researcher = Researcher.new("safety")
	researcher.add_trait("safety_conscious")

	var modifier = researcher.get_doom_modifier()
	assert_lt(modifier, 0.0, "Safety conscious should reduce doom")
	assert_almost_eq(modifier, -0.10, 0.01, "Should be -10%")

func test_safety_specialization_doom_modifier():
	var safety_researcher = Researcher.new("safety")
	var modifier = safety_researcher.get_doom_modifier()
	assert_lt(modifier, 0.0, "Safety spec should reduce doom")

	var cap_researcher = Researcher.new("capabilities")
	var cap_modifier = cap_researcher.get_doom_modifier()
	assert_gt(cap_modifier, 0.0, "Capabilities spec should increase doom")

func test_researcher_turn_processing():
	var researcher = Researcher.new("safety")
	researcher.burnout = 0.0
	researcher.turns_employed = 0

	researcher.process_turn()

	assert_eq(researcher.turns_employed, 1)
	assert_gt(researcher.burnout, 0.0, "Should accumulate some burnout each turn")

func test_skill_growth_over_time():
	var researcher = Researcher.new("safety")
	researcher.skill_level = 5

	# Run many turns to trigger skill growth (5% chance per turn)
	var grew = false
	for i in range(100):
		var before = researcher.skill_level
		researcher.process_turn()
		if researcher.skill_level > before:
			grew = true
			break

	assert_true(grew, "Should eventually grow skill over 100 turns")

func test_loyalty_changes_with_salary():
	var researcher = Researcher.new("safety")
	researcher.salary_expectation = 60000.0
	researcher.loyalty = 50

	# Paid well - loyalty increases
	researcher.current_salary = 60000.0
	researcher.process_turn()
	assert_gte(researcher.loyalty, 50, "Good salary should maintain/increase loyalty")

	# Underpaid - loyalty decreases
	researcher.loyalty = 50
	researcher.current_salary = 40000.0  # < 80%
	researcher.process_turn()
	assert_lte(researcher.loyalty, 50, "Low salary should decrease loyalty")

func test_game_state_add_researcher():
	var state = GameState.new("test_add")
	var researcher = Researcher.new("safety")

	state.add_researcher(researcher)

	assert_eq(state.researchers.size(), 1)
	assert_eq(state.safety_researchers, 1, "Should update legacy count")

func test_game_state_multiple_researchers():
	var state = GameState.new("test_multi")

	var safety1 = Researcher.new("safety")
	var safety2 = Researcher.new("safety")
	var cap1 = Researcher.new("capabilities")

	state.add_researcher(safety1)
	state.add_researcher(safety2)
	state.add_researcher(cap1)

	assert_eq(state.researchers.size(), 3)
	assert_eq(state.get_researcher_count_by_spec("safety"), 2)
	assert_eq(state.get_researcher_count_by_spec("capabilities"), 1)

func test_game_state_remove_researcher():
	var state = GameState.new("test_remove")
	var researcher = Researcher.new("safety")

	state.add_researcher(researcher)
	assert_eq(state.researchers.size(), 1)

	state.remove_researcher(researcher)
	assert_eq(state.researchers.size(), 0)
	assert_eq(state.safety_researchers, 0, "Should update legacy count")

func test_doom_system_with_researchers():
	var state = GameState.new("test_doom_researchers")
	var doom_sys = state.doom_system

	# Hire 2 safety researchers
	var safety1 = Researcher.new("safety")
	var safety2 = Researcher.new("safety")
	state.add_researcher(safety1)
	state.add_researcher(safety2)

	# Give them compute and management
	state.compute = 100.0
	state.managers = 1

	var result = doom_sys.calculate_doom_change(state)

	# Should have negative doom from safety researchers
	assert_lt(result["sources"]["safety"], 0.0, "Safety researchers should reduce doom")

func test_doom_system_specialization_bonus():
	var state = GameState.new("test_spec_bonus")
	var doom_sys = state.doom_system

	# Safety specialist with high productivity
	var researcher = Researcher.new("safety")
	researcher.base_productivity = 1.0
	researcher.burnout = 0.0
	state.add_researcher(researcher)
	state.compute = 100.0
	state.managers = 1

	var result = doom_sys.calculate_doom_change(state)

	# Safety spec bonus should make doom reduction stronger
	var safety_doom = result["sources"]["safety"]
	# Base -3.5, plus 15% bonus = -4.025
	assert_lt(safety_doom, -3.5, "Safety spec should have bonus reduction")

func test_capability_researcher_doom_penalty():
	var state = GameState.new("test_cap_penalty")
	var doom_sys = state.doom_system

	var cap_researcher = Researcher.new("capabilities")
	state.add_researcher(cap_researcher)
	state.compute = 100.0
	state.managers = 1

	var result = doom_sys.calculate_doom_change(state)

	# Capabilities should add doom with penalty
	assert_gt(result["sources"]["capabilities"], 3.0, "Should have 5% doom penalty")

func test_researcher_serialization():
	var researcher = Researcher.new("safety", "Test Name")
	researcher.skill_level = 7
	researcher.burnout = 25.0
	researcher.add_trait("workaholic")

	var data = researcher.to_dict()

	var researcher2 = Researcher.new()
	researcher2.from_dict(data)

	assert_eq(researcher2.researcher_name, "Test Name")
	assert_eq(researcher2.specialization, "safety")
	assert_eq(researcher2.skill_level, 7)
	assert_eq(researcher2.burnout, 25.0)
	assert_true(researcher2.has_trait("workaholic"))

func test_hiring_action_creates_researcher():
	var state = GameState.new("test_hiring")
	var action_result = GameActions.execute_action("hire_safety_researcher", state)

	assert_true(action_result["success"])
	assert_eq(state.researchers.size(), 1, "Should have hired 1 researcher")
	assert_eq(state.researchers[0].specialization, "safety")

func test_hiring_all_specializations():
	var state = GameState.new("test_all_specs")
	state.money = 500000.0  # Enough for all hires
	state.action_points = 10

	GameActions.execute_action("hire_safety_researcher", state)
	GameActions.execute_action("hire_capability_researcher", state)
	GameActions.execute_action("hire_interpretability_researcher", state)
	GameActions.execute_action("hire_alignment_researcher", state)

	assert_eq(state.researchers.size(), 4)
	assert_eq(state.get_researcher_count_by_spec("safety"), 1)
	assert_eq(state.get_researcher_count_by_spec("capabilities"), 1)
	assert_eq(state.get_researcher_count_by_spec("interpretability"), 1)
	assert_eq(state.get_researcher_count_by_spec("alignment"), 1)

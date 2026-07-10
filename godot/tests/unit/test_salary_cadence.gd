extends GutTest
## Salary cadence + low-cash warning regression (#573).
## The bug: annual salary (current_salary, ~$60k) was billed as annual/12 (a MONTH's pay)
## every day-turn ("Day 1/5"), craterng cash by ~turn 7 with no warning. Fixed to per-workday
## (annual/260) + a bankruptcy warning before a cash defeat.

func test_salary_per_turn_is_small_fraction_of_annual():
	var state = GameState.new("salary_cadence_seed")
	var r = Researcher.new()
	r.current_salary = 60000.0
	r.specialization = "safety"
	state.researchers.append(r)
	var money_before: float = state.money
	var tm = TurnManager.new(state)
	tm.start_turn()
	var per_turn_cost: float = money_before - state.money
	# Old bug: annual/12 ~= $5000 billed every day. Fixed: annual/260 ~= $231/workday.
	assert_gt(per_turn_cost, 0.0, "Salary should still be charged each turn")
	assert_lt(per_turn_cost, 500.0, "Per-turn salary must be a small fraction of annual (regression guard vs the /12 crash)")
	assert_almost_eq(per_turn_cost, 60000.0 / 260.0, 60.0, "Per-turn salary ~= annual/260 (per workday)")

func test_low_cash_warning_fires_before_cash_defeat():
	var state = GameState.new("low_cash_seed")
	var r = Researcher.new()
	r.current_salary = 60000.0
	state.researchers.append(r)
	state.money = 100.0  # cannot cover next turn's payroll
	var tm = TurnManager.new(state)
	var result: Dictionary = tm.start_turn()
	var joined: String = "\n".join(result.get("messages", []))
	assert_true(
		joined.contains("CRITICAL") or joined.contains("Low cash") or joined.contains("bankruptcy"),
		"A low-cash/bankruptcy warning must surface when cash can't cover the next turn's bills"
	)

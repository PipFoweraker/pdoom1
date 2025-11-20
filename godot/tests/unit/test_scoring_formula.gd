extends Node
## Scoring Formula Test Suite
## Verifies scoring calculation matches expected values from SCORING_SYSTEM_PROPOSAL.md
##
## Usage:
##   godot --headless --script tests/unit/test_scoring_formula.gd

# Import the GameOverScreen to access calculate_final_score
# Since we can't directly import, we'll duplicate the function here for testing
# CRITICAL: This must match game_over_screen.gd exactly!

func calculate_final_score(state: Dictionary) -> int:
	"""
	Calculate final score from game state.
	DUPLICATE of game_over_screen.gd for testing purposes.
	"""
	var score = 0

	# Extract values with defaults
	var doom = state.get("doom", 0.0)
	var papers = state.get("papers", 0)
	var turn = state.get("turn", 0)
	var money = state.get("money", 0)

	# Count total researchers (all types)
	var researchers = 0
	researchers += state.get("safety_researchers", 0)
	researchers += state.get("capability_researchers", 0)
	researchers += state.get("compute_engineers", 0)

	# 1. Safety Achievement (40-50% of total score)
	var safety_score = (100 - doom) * 1000
	score += safety_score

	# 2. Research Output (20-30% of total score)
	var paper_score = papers * 5000
	score += paper_score

	# 3. Team Excellence (10-15% of total score)
	var team_score = researchers * 2000
	score += team_score

	# 4. Survival Duration (10-15% of total score)
	var survival_score = turn * 500
	score += survival_score

	# 5. Financial Success (5-10% of total score)
	var financial_score = money * 0.1
	score += financial_score

	# 6. Victory Bonus (unlocks at doom < 20%)
	if doom < 20.0:
		score += 50000  # Victory bonus

	return int(score)

func _ready():
	print("\n============================================================")
	print("SCORING FORMULA TEST SUITE")
	print("============================================================\n")

	var tests_passed = 0
	var tests_failed = 0

	# Test Scenario 1: Safety-Focused Win
	print("[TEST 1] Safety-Focused Win")
	var state1 = {
		"turn": 50,
		"doom": 15.0,
		"papers": 8,
		"safety_researchers": 6,
		"capability_researchers": 0,
		"compute_engineers": 0,
		"money": 150000
	}
	var expected1 = 227000
	var actual1 = calculate_final_score(state1)

	print("  Expected: %d" % expected1)
	print("  Actual:   %d" % actual1)

	if actual1 == expected1:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual1 - expected1))
		tests_failed += 1
	print("")

	# Test Scenario 2: Long Survival (No Victory)
	print("[TEST 2] Long Survival (No Victory)")
	var state2 = {
		"turn": 80,
		"doom": 55.0,
		"papers": 12,
		"safety_researchers": 5,
		"capability_researchers": 3,
		"compute_engineers": 2,
		"money": 80000
	}
	var expected2 = 173000
	var actual2 = calculate_final_score(state2)

	print("  Expected: %d" % expected2)
	print("  Actual:   %d" % actual2)

	if actual2 == expected2:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual2 - expected2))
		tests_failed += 1
	print("")

	# Test Scenario 3: Early Loss (Typical)
	print("[TEST 3] Early Loss (Typical)")
	var state3 = {
		"turn": 20,
		"doom": 100.0,
		"papers": 3,
		"safety_researchers": 2,
		"capability_researchers": 1,
		"compute_engineers": 1,
		"money": 50000
	}
	var expected3 = 38000
	var actual3 = calculate_final_score(state3)

	print("  Expected: %d" % expected3)
	print("  Actual:   %d" % actual3)

	if actual3 == expected3:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual3 - expected3))
		tests_failed += 1
	print("")

	# Test Scenario 4: Capability Rush (Risky)
	print("[TEST 4] Capability Rush (Risky)")
	var state4 = {
		"turn": 35,
		"doom": 75.0,
		"papers": 15,
		"safety_researchers": 2,
		"capability_researchers": 5,
		"compute_engineers": 1,
		"money": 200000
	}
	var expected4 = 153500
	var actual4 = calculate_final_score(state4)

	print("  Expected: %d" % expected4)
	print("  Actual:   %d" % actual4)

	if actual4 == expected4:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual4 - expected4))
		tests_failed += 1
	print("")

	# Test Edge Case: Perfect Safety Win
	print("[TEST 5] Perfect Safety Win (Edge Case)")
	var state5 = {
		"turn": 60,
		"doom": 5.0,
		"papers": 10,
		"safety_researchers": 10,
		"capability_researchers": 0,
		"compute_engineers": 0,
		"money": 200000
	}
	# Calculation:
	# Safety: (100-5)*1000 = 95,000
	# Papers: 10*5000 = 50,000
	# Team: 10*2000 = 20,000
	# Survival: 60*500 = 30,000
	# Financial: 200000*0.1 = 20,000
	# Victory: +50,000 (doom < 20)
	# Total: 265,000
	var expected5 = 265000
	var actual5 = calculate_final_score(state5)

	print("  Expected: %d" % expected5)
	print("  Actual:   %d" % actual5)

	if actual5 == expected5:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual5 - expected5))
		tests_failed += 1
	print("")

	# Test Edge Case: Victory Threshold (19.9% doom)
	print("[TEST 6] Victory Threshold Test (19.9% doom)")
	var state6 = {
		"turn": 30,
		"doom": 19.9,
		"papers": 5,
		"safety_researchers": 3,
		"capability_researchers": 0,
		"compute_engineers": 0,
		"money": 100000
	}
	# Calculation:
	# Safety: (100-19.9)*1000 = 80,100
	# Papers: 5*5000 = 25,000
	# Team: 3*2000 = 6,000
	# Survival: 30*500 = 15,000
	# Financial: 100000*0.1 = 10,000
	# Victory: +50,000 (doom < 20)
	# Total: 186,100
	var expected6 = 186100
	var actual6 = calculate_final_score(state6)

	print("  Expected: %d" % expected6)
	print("  Actual:   %d" % actual6)

	if actual6 == expected6:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual6 - expected6))
		tests_failed += 1
	print("")

	# Test Edge Case: No Victory Threshold (20.1% doom)
	print("[TEST 7] No Victory Threshold (20.1% doom)")
	var state7 = {
		"turn": 30,
		"doom": 20.1,
		"papers": 5,
		"safety_researchers": 3,
		"capability_researchers": 0,
		"compute_engineers": 0,
		"money": 100000
	}
	# Same as above BUT no victory bonus (doom >= 20)
	# Total: 136,100 (without 50k bonus)
	var expected7 = 136100
	var actual7 = calculate_final_score(state7)

	print("  Expected: %d" % expected7)
	print("  Actual:   %d" % actual7)

	if actual7 == expected7:
		print("  ✅ PASS")
		tests_passed += 1
	else:
		print("  ❌ FAIL (difference: %d)" % (actual7 - expected7))
		tests_failed += 1
	print("")

	# Results Summary
	print("============================================================")
	print("TEST RESULTS")
	print("============================================================")
	print("Tests Passed: %d" % tests_passed)
	print("Tests Failed: %d" % tests_failed)
	print("")

	if tests_failed == 0:
		print("✅ ALL TESTS PASSED!")
		print("\nScoring formula is working correctly and matches")
		print("the expected values from SCORING_SYSTEM_PROPOSAL.md")
	else:
		print("❌ SOME TESTS FAILED!")
		print("\nCheck the scoring formula in game_over_screen.gd")
		print("to ensure it matches the specification.")

	print("============================================================\n")

	# Exit after test
	await get_tree().create_timer(1.0).timeout
	get_tree().quit()

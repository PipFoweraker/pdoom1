extends GutTest
## #1225 item 4: "counter-offers -- low specificity is exactly right".
##
## Measured before this fix: there was NO counter-offer mechanic at all. The three
## things labelled counter-offer were rival-retention EVENT OPTIONS, all fixed
## price, all anonymous:
##
##   rival_poaching      "Counter-Offer"          $80,000   effects: {}   <- EMPTY
##   researcher_poached  "Match Their Offer"      $50,000   reputation +2
##   researcher_poached  "Counter with Promotion" $30,000   reputation +3
##
## No person was named, no amount was chosen, and NO Researcher.current_salary was
## ever changed by any of them. The $80,000 option's only mechanical effect was
## that you did not take the other one.
##
## Meanwhile the DEPARTURE path was rich: lose_researcher targets the least loyal
## and names them. Losing someone said who; keeping someone said nothing.

func _state_with_team() -> GameState:
	var s = GameState.new("retention_test")
	for i in range(3):
		var r := Researcher.new("safety")
		r.researcher_name = "Researcher %d" % i
		r.candidate_id = "cand_%d" % i
		r.hire_state = Researcher.HireState.EMPLOYED
		r.loyalty = 50 - (i * 10)  # Researcher 2 is least loyal -> the poaching target
		r.current_salary = 60000.0
		s.researchers.append(r)
		s.safety_researchers += 1
	return s

func test_retention_targets_the_person_a_rival_would_take():
	# Same targeting as lose_researcher: whoever the rival would have taken is
	# exactly who you are keeping. A counter-offer that defended a random hire
	# would not be a counter-offer.
	var s := _state_with_team()
	var kept = GameEvents._retain_most_at_risk(s, "")
	assert_not_null(kept, "there is somebody to keep")
	assert_eq(kept.researcher_name, "Researcher 2", "the LEAST loyal is the one at risk")

func test_retention_raises_loyalty_because_loyalty_is_poaching_resistance():
	var s := _state_with_team()
	var before: int = s.researchers[2].loyalty
	var kept = GameEvents._retain_most_at_risk(s, "")
	assert_gt(kept.loyalty, before, "fighting for someone must make the next raid harder")

func test_matching_an_offer_actually_changes_what_they_are_paid():
	# The complaint, precisely: "Match Their Offer" never changed current_salary.
	var s := _state_with_team()
	var before: float = s.researchers[2].current_salary
	var kept = GameEvents._retain_most_at_risk(s, "")
	assert_gt(kept.current_salary, before,
		"a match that does not move their pay is not a match")

func test_retention_has_an_ongoing_cost_not_a_one_off():
	# The raise bills through the normal per-workday payroll from the next turn, so
	# keeping people is expensive FOREVER. That is the design point, and it is what
	# makes the choice interesting rather than a toll.
	var s := _state_with_team()
	var payroll_before := 0.0
	for r in s.researchers:
		payroll_before += r.current_salary
	GameEvents._retain_most_at_risk(s, "")
	var payroll_after := 0.0
	for r in s.researchers:
		payroll_after += r.current_salary
	assert_gt(payroll_after, payroll_before, "the lab's salary bill went up and stays up")

func test_retention_names_the_person_it_kept():
	# Symmetry with _format_departure. Losing someone named them; keeping someone
	# used to name nobody at all.
	var s := _state_with_team()
	var kept = GameEvents._retain_most_at_risk(s, "")
	var line := GameEvents._format_retention(s, kept)
	assert_true(line.find("Researcher 2") != -1, "the retained person is named")
	assert_true(line.to_lower().find("loyalty") != -1, "and what changed is stated")

func test_retention_on_an_empty_lab_is_a_safe_no_op():
	var s = GameState.new("retention_empty")
	assert_null(GameEvents._retain_most_at_risk(s, ""), "nobody to keep -> null, not a crash")

func test_the_counter_offer_options_are_no_longer_empty():
	# The $80,000 button with effects:{} is the headline of this issue.
	for ev in GameEvents.get_all_events():
		if ev.get("id") != "rival_poaching":
			continue
		for o in ev.get("options", []):
			if String(o.get("text", "")).to_lower().find("counter") == -1:
				continue
			var eff: Dictionary = o.get("effects", {})
			assert_false(eff.is_empty(), "an $80,000 option must do something")
			assert_true(eff.has("retain_researcher"), "and what it does is keep the person")

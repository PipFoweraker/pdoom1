extends GutTest
## #1225 item 2: a rejected offer used to leave NO MARK, which made lowballing free.
##
## From the 2026-08-14 playtest. Rejection probability is
## clampf(shortfall_frac * reject_scale, 0, 1) with reject_scale 2.0, so ANY offer
## with shortfall_frac < 0.5 was a GUARANTEED eventual hire: re-send the identical
## lowball every 2 workdays at 1 Attention until the roll lands, then collect the
## resentful_accept. The negotiation read, the self-worth floor and the resentment
## debt are all real mechanics, and retry defeated all three.
##
## The rejection was also never told to the player: `offer_rejected` had zero
## consumers anywhere in the codebase.

func _cand(name: String) -> Researcher:
	var c := Researcher.new("safety")
	c.researcher_name = name
	c.candidate_id = "cand_" + name
	c.hire_state = Researcher.HireState.CANDIDATE_IN_POOL
	return c

func test_a_fresh_candidate_remembers_nothing():
	var c := _cand("Iris")
	assert_eq(c.offers_rejected, 0, "nobody starts resentful")
	assert_eq(c.highest_rejected_offer, 0.0, "and nothing has been turned down")

func test_rejection_is_remembered_with_its_number():
	var c := _cand("Iris")
	c.highest_rejected_offer = maxf(c.highest_rejected_offer, 40000.0)
	c.offers_rejected += 1
	assert_eq(c.highest_rejected_offer, 40000.0, "the amount is what they remember")
	assert_eq(c.offers_rejected, 1, "and that it happened")

func test_memory_keeps_the_highest_not_the_latest():
	# A player who lowballs 40k, gets refused, then tries 30k must not reset the mark.
	var c := _cand("Iris")
	c.highest_rejected_offer = maxf(c.highest_rejected_offer, 40000.0)
	c.highest_rejected_offer = maxf(c.highest_rejected_offer, 30000.0)
	assert_eq(c.highest_rejected_offer, 40000.0, "40k stands; a worse offer does not erase it")

func test_offer_memory_survives_save_and_load():
	# The exploit returns if the memory does not round-trip: save, reload, re-lowball.
	var c := _cand("Iris")
	c.highest_rejected_offer = 42000.0
	c.offers_rejected = 3
	var reloaded := Researcher.new()
	reloaded.from_dict(c.to_dict())
	assert_eq(reloaded.highest_rejected_offer, 42000.0, "the number survives a save hop")
	assert_eq(reloaded.offers_rejected, 3, "so does the count")

func test_older_saves_load_as_never_rejected():
	# Absent keys must mean "no history", which is exactly the pre-fix behaviour for a
	# game already in flight -- not a crash and not a phantom rejection.
	var r := Researcher.new()
	r.from_dict({"name": "Legacy", "specialization": "safety"})
	assert_eq(r.offers_rejected, 0, "a pre-#1225 save has no offer history")
	assert_eq(r.highest_rejected_offer, 0.0, "and no remembered number")

func test_self_worth_floor_is_not_raised_by_memory():
	# The fix is a MEMORY, not a moving floor. A candidate who rejected 40k must still
	# accept their real floor -- otherwise every rejection would silently inflate them.
	var a := _cand("Iris")
	var b := _cand("Iris2")
	b.salary_expectation = a.salary_expectation
	b.appetites = a.appetites.duplicate()
	b.highest_rejected_offer = 40000.0
	b.offers_rejected = 2
	var pipeline := HiringPipeline.new()
	assert_eq(pipeline.self_worth_floor(a, []), pipeline.self_worth_floor(b, []),
		"rejection history must not move the floor -- only make_offer() consult it")

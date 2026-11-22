extends GutTest
## #1225 item 5: the Attention was previewed, the money was not.
##
## From the 2026-08-14 playtest. Pip wants a checklist of what a hire will require
## BEFORE committing. #789 item 1 already asked for onboarding to be "predictable
## AP sinks you can plan for when you make the offer". The Attention half shipped;
## the cash half did not.
##
## hard_checklist_money() existed and was called from build_onboard_prompt,
## _provision_hard_checklist, _resolve_job and the tests -- from everywhere EXCEPT
## the one screen where the player is still deciding. The number first appeared on
## the "<name> said yes" card, AFTER commitment.

func _pipeline() -> HiringPipeline:
	return HiringPipeline.new()

func _cand(needs_visa: bool) -> Researcher:
	var c := Researcher.new("safety")
	c.researcher_name = "Iris"
	c.candidate_id = "cand_1"
	c.needs_visa = needs_visa
	c.onboarded = false
	return c

func test_a_domestic_hire_projects_the_laptop_money():
	var p := _pipeline()
	var money := p.hard_checklist_money(_cand(false))
	assert_gt(money, 0.0, "a hire costs real cash to onboard, and the dialog must be able to say so")

func test_a_visa_hire_costs_strictly_more():
	# One hire in four (serial % 4 == 0) carries a visa: +$5,000 and +2 Attention. On the
	# old dialog a $8,000 hire was indistinguishable from a $3,000 one except by reading
	# "~5" instead of "~3".
	var p := _pipeline()
	var domestic := p.hard_checklist_money(_cand(false))
	var foreign := p.hard_checklist_money(_cand(true))
	assert_gt(foreign, domestic, "the visa is real money and must be projectable before the offer")
	assert_almost_eq(foreign - domestic, p.item_money("visa"), 0.01,
		"the difference IS the visa line item")

func test_visa_attention_is_projectable_too():
	var p := _pipeline()
	assert_gt(p.hard_checklist_attention(_cand(true)), p.hard_checklist_attention(_cand(false)),
		"a visa hire also costs more founder time")

func test_mentoring_prompt_says_dismissal_means_skip():
	# THE TRAP. _resolve_hiring_window treats a lapsed/dismissed card as mentoring_skipped,
	# arming a PERMANENT output debuff and a monthly quit roll. A player who closes a popup
	# had made a permanent decision and was never told.
	var p := _pipeline()
	var prompt := p.build_mentoring_prompt(_cand(false))
	var desc := String(prompt.get("description", ""))
	assert_true(desc.to_lower().find("counts as skipping") != -1,
		"the card must say that closing it IS a choice")
	assert_true(desc.to_lower().find("permanent") != -1,
		"and that the consequence is permanent")

func test_mentoring_prompt_names_the_numbers():
	# "a lasting output debuff and an early-quit risk" is true and unactionable.
	var p := _pipeline()
	var desc := String(p.build_mentoring_prompt(_cand(false)).get("description", ""))
	assert_true(desc.find("%") != -1, "the attrition chance is a number the player can weigh")
	assert_true(desc.to_lower().find("later") != -1,
		"and it must say the decision is recoverable from the hiring screen")

func test_an_already_mentored_hire_gets_no_prompt():
	var p := _pipeline()
	var c := _cand(false)
	c.mentoring_done = true
	assert_true(p.build_mentoring_prompt(c).is_empty(), "no card once the choice is made")

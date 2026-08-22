extends GutTest
## #1225 item 3: an ad campaign must be legible from launch to close.
##
## The defect: `advertise` cost $8,000 + 3 Attention and then said nothing until a
## candidate happened to arrive. `_surface_hiring_notifications` returned early when
## `ad_hits <= 0`, so a zero-yield month emitted NOTHING -- indistinguishable from the
## campaign having quietly ended. Expected yield is 0-6 over three months (mean 3) with
## a 1-in-27 chance of paying $8,000 for literally nobody, and that worst case was the
## most silent case of all.
##
## RULING: 2026-08-22 -- a mechanic that charges the player and does nothing observable gets an unsubtle placeholder consequence NOW rather than waiting for a balanced one; players need to suffer, and balance comes later -- flavour: mechanical-inertness -- mechanism: this test file, and the fix-by dates on the inertness issues
##
## Pip's words, on the class of defect this file addresses: "we need to give the
## mechanical inertness a definitee fix-by date. and I'd rather have a bad thing in
## there now, unsubtle, rather than no thing, and we can balance it later. suggest?
## players need to suffer." So a dead month says it is dead, and the closing line names
## the money. Declared here because this is the first place the doctrine was applied and
## nothing else had recorded it -- it was governing the work while existing only in
## conversation.
##
## These pin the MESSAGE, not the balance. The yield numbers are Balance-driven and are
## expected to move; the requirement that every month reports itself is not.

const MC = preload("res://scripts/core/month_controller.gd")


func _m(added: int, discarded: int, rem: int, ended: bool, total: int, spent: float) -> Dictionary:
	return {
		"kind": "advertise_month",
		"added": added,
		"discarded": discarded,
		"months_remaining": rem,
		"ended": ended,
		"total_added": total,
		"spent": spent,
	}


# --- the branch that did not exist before -------------------------------------

func test_zero_yield_month_says_nobody_applied():
	var msg := MC.ad_campaign_message(_m(0, 0, 2, false, 0, 8000.0))
	assert_true(msg.contains("nobody applied"),
		"A month that produced nobody must SAY so -- silence reads as 'no campaign'. Got: " + msg)


func test_zero_yield_month_still_reports_months_remaining():
	var msg := MC.ad_campaign_message(_m(0, 0, 2, false, 0, 8000.0))
	assert_true(msg.contains("2 months"),
		"A dead month must still prove the campaign is alive. Got: " + msg)


# --- the 1-in-27: paid everything, got nobody ---------------------------------

func test_campaign_that_produced_nobody_names_the_money():
	var msg := MC.ad_campaign_message(_m(0, 0, 0, true, 0, 8000.0))
	assert_true(msg.contains("produced nobody"), "The worst case must be stated. Got: " + msg)
	assert_true(msg.contains("$8,000"),
		"The closing line must name what it cost -- that is the part that stings. Got: " + msg)


func test_money_is_formatted_with_thousands_separators():
	var msg := MC.ad_campaign_message(_m(0, 0, 0, true, 0, 12500.0))
	assert_true(msg.contains("$12,500"), "Money reads as money, not a bare float. Got: " + msg)


# --- the ordinary branches still read correctly -------------------------------

func test_single_applicant_is_singular():
	var msg := MC.ad_campaign_message(_m(1, 0, 2, false, 1, 8000.0))
	assert_true(msg.contains("An applicant responded"), "Got: " + msg)
	assert_false(msg.contains("1 applicants"), "No '1 applicants'. Got: " + msg)


func test_several_applicants_are_counted():
	var msg := MC.ad_campaign_message(_m(3, 0, 1, false, 4, 8000.0))
	assert_true(msg.contains("3 applicants responded"), "Got: " + msg)


func test_last_month_is_singular():
	var msg := MC.ad_campaign_message(_m(1, 0, 1, false, 1, 8000.0))
	assert_true(msg.contains("One month of the campaign remains"), "Got: " + msg)


func test_successful_close_reports_the_total_and_the_cost():
	var msg := MC.ad_campaign_message(_m(1, 0, 0, true, 4, 8000.0))
	assert_true(msg.contains("4 people came of it"), "Got: " + msg)
	assert_true(msg.contains("$8,000"), "Got: " + msg)


func test_close_with_exactly_one_hire_is_singular():
	var msg := MC.ad_campaign_message(_m(0, 0, 0, true, 1, 8000.0))
	assert_true(msg.contains("One person came of it"), "Got: " + msg)


# --- the at-cap discard (#961 rules this must never be silent) -----------------

func test_at_cap_discard_is_reported():
	var msg := MC.ad_campaign_message(_m(0, 2, 2, false, 0, 8000.0))
	assert_true(msg.contains("2 more were turned away"),
		"#961: what happens at cap must NEVER be silent. Got: " + msg)
	assert_true(msg.contains("shortlist is full"), "Got: " + msg)


func test_single_at_cap_discard_is_singular():
	var msg := MC.ad_campaign_message(_m(1, 1, 2, false, 1, 8000.0))
	assert_true(msg.contains("One more was turned away"), "Got: " + msg)


func test_no_discard_line_when_nothing_was_discarded():
	var msg := MC.ad_campaign_message(_m(2, 0, 1, false, 2, 8000.0))
	assert_false(msg.contains("turned away"),
		"Do not mention the cap when the cap was not hit. Got: " + msg)


# --- every branch produces SOMETHING ------------------------------------------

func test_no_branch_returns_an_empty_message():
	## The original defect was an early `return` producing no line at all. Nothing in
	## this function may reintroduce a silent path.
	for added in [0, 1, 3]:
		for discarded in [0, 1, 2]:
			for ended in [true, false]:
				var msg := MC.ad_campaign_message(_m(added, discarded, 1, ended, added, 8000.0))
				assert_true(msg.strip_edges().length() > 0,
					"empty message for added=%d discarded=%d ended=%s" % [added, discarded, ended])

extends GutTest
## #1223: the Action Queue and the Attention header contradicted each other in one
## frame, and "ticks" was a word the game never defined for a player.
##
## Pip's 2026-08-14 playtest, one screen:
##
##   Top bar        Attention: 20 (12 free, 8 queued)   <- month_plan.attention_spent
##   Action Queue   No actions queued yet               <- PlanController mirror
##   IN-FLIGHT      Offer: Iris Wilson 0/2 ticks        <- HiringPipeline.jobs
##
## Three sources, one column, no arbitration. All three were right about their own
## number. These tests pin the two halves fixed here: the header stops claiming the
## queue holds something it does not, and the clock says "days" like the rest of
## the game.

const MAIN_UI := "res://scripts/ui/main_ui.gd"
const HIRING_PANEL := "res://scripts/ui/hiring_panel_controller.gd"
const FINANCE := "res://scripts/core/finance_engine.gd"

func _source(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	assert_not_null(f, "could not open %s" % path)
	if f == null:
		return ""
	var s := f.get_as_text()
	f.close()
	return s

func test_header_does_not_call_committed_attention_queued():
	# The exact contradiction. attention_spent has two disjoint writer sets and only
	# GameManager.select_action() mints a queue tile; MonthPlan.spend_attention()
	# deliberately mints nothing, and every hiring action uses that one.
	var src := _source(MAIN_UI)
	assert_eq(src.find("%d free, %d queued"), -1,
		"the header must not call committed Attention 'queued' -- the queue widget disagrees")
	assert_true(src.find("%d free, %d committed") != -1,
		"it says 'committed', which is true before AND after the plan commits")

func test_in_flight_hiring_reports_days_not_ticks():
	var src := _source(HIRING_PANEL)
	assert_eq(src.find('"unit": "ticks"'), -1,
		"'ticks' is defined nowhere a player can reach -- PLAYERGUIDE.md has zero hits")
	assert_true(src.find('"unit": "days"') != -1,
		"a tick IS a workday (clock.gd: 'One turn = one WORKDAY')")

func test_onboarding_still_says_steps_not_days():
	# Deliberate asymmetry: onboarding rows are CHECKLIST items, not time. Printing
	# both as days would make a checklist look like a clock, which is the confusion
	# the issue flagged when 3/4 steps sat beside 0/2 ticks under one header.
	var src := _source(HIRING_PANEL)
	assert_true(src.find('"unit": "steps"') != -1,
		"onboarding keeps 'steps' -- it is a checklist, not a duration")

func test_loan_fuse_reports_days():
	var src := _source(FINANCE)
	assert_eq(src.find("bills in %d ticks"), -1, "the loan fuse spoke in ticks too")
	assert_true(src.find("bills in %d days") != -1, "one word, one vocabulary")

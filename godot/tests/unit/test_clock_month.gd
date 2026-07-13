extends GutTest
## L1 (#612 / ADR-0009): Clock month-plan helpers + the L0 leap-day fix (#620 note 2).

# --- Leap-day infinite-loop fix -------------------------------------------------
# The old date_for_turn compared `day` against the NON-leap DAYS_IN_MONTH[1]=28 in the
# while-condition while the body used a leap-adjusted 29, so a date landing exactly on
# Feb 29 entered the loop but never decremented — an infinite hang. If this regresses,
# these two calls hang the whole suite (a hard, if blunt, guard).

func test_date_landing_exactly_on_feb29_does_not_hang():
	# start 2020-02-01 (leap), turn 20 -> total_days 28 -> day 29, month 2. This is the
	# EXACT condition that hung the old loop (29 > 28 true, 29 > 29 false -> no progress).
	var d := Clock.date_for_turn(20, 2020, 2, 1)
	assert_eq(int(d.month), 2, "lands in February")
	assert_eq(int(d.day), 29, "lands exactly on the leap day without hanging")


func test_date_rolls_past_feb29_into_march():
	var d := Clock.date_for_turn(21, 2020, 2, 1)  # one workday past -> March 1
	assert_eq(int(d.month), 3, "rolls over the leap February")
	assert_eq(int(d.day), 1, "into March 1")


func test_all_dates_valid_across_the_fiction_window():
	# Sweep the whole 2017->2040 window at the day grain; every date must be well-formed.
	for turn in range(0, 3000, 7):
		var d := Clock.date_for_turn(turn, 2017, 7, 3)
		var m := int(d.month)
		assert_between(m, 1, 12, "month in range at turn %d" % turn)
		var month_len: int = Clock.DAYS_IN_MONTH[m - 1]
		if m == 2 and Clock.is_leap_year(int(d.year)):
			month_len = 29
		assert_between(int(d.day), 1, month_len, "day within month length at turn %d" % turn)


# --- Month plan-layer helpers ---------------------------------------------------

func test_month_index_is_monotonic_and_detects_boundaries():
	var prev := Clock.month_index(0, 2017, 7, 3)
	var boundaries := 0
	for turn in range(1, 400):
		var idx := Clock.month_index(turn, 2017, 7, 3)
		assert_true(idx >= prev, "month index never decreases (turn %d)" % turn)
		if idx != prev:
			boundaries += 1
			assert_true(Clock.is_month_boundary(turn, 2017, 7, 3),
				"a change in month index IS a month boundary (turn %d)" % turn)
		prev = idx
	assert_true(boundaries >= 10, "several month boundaries occur over 400 workday ticks")


func test_turn_zero_is_a_boundary():
	assert_true(Clock.is_month_boundary(0, 2017, 7, 3), "turn 0 opens the first plan phase")


func test_month_ordinal_counts_plan_months_from_start():
	assert_eq(Clock.month_ordinal_since_start(0, 2017, 7, 3), 0, "run starts at plan-month 0")
	# A turn a couple of calendar months in should read ordinal >= 1.
	var later := Clock.month_ordinal_since_start(60, 2017, 7, 3)
	assert_true(later >= 1, "ordinal advances with calendar months")


func test_month_label_is_the_badge_date():
	var label := Clock.month_label(0, 2017, 7, 3)
	assert_string_contains(label, "July", "badge names the plan month")
	assert_string_contains(label, "2017", "badge carries the year")


func test_annual_to_per_month_is_twelfth():
	assert_almost_eq(Clock.annual_to_per_month(120000.0), 10000.0, 0.01, "annual/12 per month")

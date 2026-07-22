class_name Clock
extends RefCounted
## The single time authority (L0, #620 item 2).
##
## One turn = one WORKDAY (values unchanged by L0 -- only the seam moved here).
## Three time conventions used to live in three places: the day-calendar
## (game_state), the annual/260 salary denominator (turn_manager), and
## get_months_per_turn (game_state). Every turn<->calendar conversion now routes
## through this one object so the L1 month re-denomination (ADR-0009) flips ONE
## seam -- and L9's Balance surface has a single place to read pacing from.
## See docs/design/TWO_ACT_STRUCTURE.md for the variable game-length plan.

const TURNS_PER_WEEK: int = 5        # work days per week (turn = 1 workday)
const DAYS_PER_WEEK: int = 7         # calendar days per week (weekends pass between weeks)
const WORKDAYS_PER_YEAR: float = 260.0  # salary denominator: annual/260 per turn (#573)

const WEEKDAY_NAMES := ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
const DAYS_IN_MONTH := [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


static func weeks_to_turns(weeks: int) -> int:
	"""Convert a duration in weeks to turns (paper review periods, deadlines)."""
	return weeks * TURNS_PER_WEEK


static func months_per_turn() -> float:
	"""Calendar months represented by one turn. Fixed at 1.0 until the variable
	game-length system lands (see docs/design/TWO_ACT_STRUCTURE.md).

	L1/ADR-0009 note: the resolution tick stays day-grained (turn = 1 workday);
	the MONTH is the PLAN cadence, a layer above the tick (MonthPlan / Clock month
	helpers below). Badge = calendar date, days-survived scoring stays fine-grained
	(ADR-0009 S6). This value is unchanged so risk/doom calibration and recorded
	replays are untouched by the month plan layer."""
	return 1.0


static func annual_to_per_turn(annual_amount: float) -> float:
	"""Convert an annual money magnitude (e.g. salary) to one turn's bill.
	Turn = 1 workday, ~260 workdays/yr (#573: was /12, a month billed every day).
	Billed per workday-turn, ~21.7 workdays/month, so a full month of billing already
	sums to ~annual/12 -- monthly payroll emerges from the tick grain (ADR-0009
	re-denomination is behaviour-neutral here; see MonthPlan doc)."""
	return annual_amount / WORKDAYS_PER_YEAR


static func week_number(turn: int) -> int:
	"""Current week number (1-indexed)."""
	@warning_ignore("integer_division")
	return (turn / TURNS_PER_WEEK) + 1


static func day_of_week(turn: int) -> int:
	"""Day within the current week (1-5 for Mon-Fri)."""
	return (turn % TURNS_PER_WEEK) + 1


static func weekday_name(turn: int) -> String:
	"""Name of the current weekday."""
	return WEEKDAY_NAMES[turn % TURNS_PER_WEEK]


static func date_for_turn(turn: int, start_year: int, start_month: int, start_day: int) -> Dictionary:
	"""Calculate the calendar date for a turn (moved verbatim from GameState, #472).
	Returns: {year, month, day, weekday, week_number, day_of_week, quarter}"""
	# Each turn = 1 weekday, so we need to account for weekends
	@warning_ignore("integer_division")
	var weeks_elapsed = turn / TURNS_PER_WEEK
	var days_into_week = turn % TURNS_PER_WEEK

	# Total calendar days = weeks * 7 + days into current week
	var total_days = weeks_elapsed * DAYS_PER_WEEK + days_into_week

	# Calculate date from start date (using configurable values)
	var year = start_year
	var month = start_month
	var day = start_day + total_days

	# Roll over months and years.
	# L0 leap-day fix (#620 note 2): the old loop condition compared `day` against the
	# NON-leap DAYS_IN_MONTH[1]=28 while the body used a leap-adjusted month_days=29, so a
	# date landing exactly on Feb 29 satisfied the while-condition (29>28) but never
	# decremented (29>29 is false) -- an infinite hang. The month-turn fiction window
	# (2017-2040) crosses six Feb-29 dates, so this was latent->live. Compute the
	# leap-adjusted length ONCE and use it in both the test and the decrement.
	while true:
		var month_days = DAYS_IN_MONTH[month - 1]
		if month == 2 and is_leap_year(year):
			month_days = 29
		if day <= month_days:
			break
		day -= month_days
		month += 1
		if month > 12:
			month = 1
			year += 1

	@warning_ignore("integer_division")
	var quarter = ((month - 1) / 3) + 1

	return {
		"year": year,
		"month": month,
		"day": day,
		"weekday": weekday_name(turn),
		"week_number": week_number(turn),
		"day_of_week": day_of_week(turn),
		"quarter": quarter
	}


static func is_leap_year(year: int) -> bool:
	return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


# ============================================================================
# MONTH PLAN LAYER (L1 / ADR-0009)
#
# The MONTH is the plan cadence; the day-turn is the resolution tick beneath it.
# These helpers let the engine detect month boundaries (when a fresh plan phase
# opens and reserve evaporates) and label the badge without any consumer needing
# calendar arithmetic. All derive from date_for_turn -- one source of truth.
# ============================================================================

const MONTH_NAMES := ["January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December"]
const MONTH_ABBR := ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
	"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

const MONTHS_PER_YEAR: int = 12


static func month_index(turn: int, start_year: int, start_month: int, start_day: int) -> int:
	"""Absolute month ordinal (year*12 + month-1) for the turn's calendar date.
	Monotonic across year rollover, so `month_index(turn) != month_index(turn-1)`
	is the month-boundary test. This is the plan-turn counter (ADR-0009: ~114-270
	of these to the loss anchors)."""
	var d := date_for_turn(turn, start_year, start_month, start_day)
	return int(d.year) * MONTHS_PER_YEAR + (int(d.month) - 1)


static func is_month_boundary(turn: int, start_year: int, start_month: int, start_day: int) -> bool:
	"""True when `turn` opens a new calendar month relative to `turn - 1` (a fresh
	plan phase / reserve evaporation point). Turn 0 is treated as a boundary (the
	first plan phase). Days are physics; the boundary is where routine decisions live."""
	if turn <= 0:
		return true
	return month_index(turn, start_year, start_month, start_day) \
		!= month_index(turn - 1, start_year, start_month, start_day)


static func month_ordinal_since_start(turn: int, start_year: int, start_month: int, start_day: int) -> int:
	"""0-based count of plan-months elapsed since the run's start month. This is the
	league/month plan-turn number that stamps the replay artifact (ADR-0016)."""
	var start_idx := start_year * MONTHS_PER_YEAR + (start_month - 1)
	return month_index(turn, start_year, start_month, start_day) - start_idx


static func month_name(turn: int, start_year: int, start_month: int, start_day: int) -> String:
	var d := date_for_turn(turn, start_year, start_month, start_day)
	return MONTH_NAMES[int(d.month) - 1]


static func month_label(turn: int, start_year: int, start_month: int, start_day: int) -> String:
	"""Badge label -- the exact plan month, e.g. 'March 2034' (ADR-0009 S6)."""
	var d := date_for_turn(turn, start_year, start_month, start_day)
	return "%s %d" % [MONTH_NAMES[int(d.month) - 1], int(d.year)]


static func annual_to_per_month(annual_amount: float) -> float:
	"""Convert an annual magnitude to a single month's bill (annual/12). Provided for
	consumers that bill once per plan-month; the per-workday payroll path already sums
	to this over a month (see annual_to_per_turn)."""
	return annual_amount / float(MONTHS_PER_YEAR)

class_name Clock
extends RefCounted
## The single time authority (L0, #620 item 2).
##
## One turn = one WORKDAY (values unchanged by L0 — only the seam moved here).
## Three time conventions used to live in three places: the day-calendar
## (game_state), the annual/260 salary denominator (turn_manager), and
## get_months_per_turn (game_state). Every turn<->calendar conversion now routes
## through this one object so the L1 month re-denomination (ADR-0009) flips ONE
## seam — and L9's Balance surface has a single place to read pacing from.
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
	game-length system lands (see docs/design/TWO_ACT_STRUCTURE.md)."""
	return 1.0


static func annual_to_per_turn(annual_amount: float) -> float:
	"""Convert an annual money magnitude (e.g. salary) to one turn's bill.
	Turn = 1 workday, ~260 workdays/yr (#573: was /12, a month billed every day)."""
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

	# Roll over months and years
	while day > DAYS_IN_MONTH[month - 1]:
		# Check for leap year February
		var feb_days = 28
		if month == 2 and is_leap_year(year):
			feb_days = 29

		var month_days = DAYS_IN_MONTH[month - 1] if month != 2 else feb_days

		if day > month_days:
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

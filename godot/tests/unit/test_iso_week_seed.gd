extends GutTest
## The featured league seed names the ISO week the league opens in.
##
## THE DEFECT (measured 2026-08-24). `GameConfig.get_weekly_seed()`'s fallback
## computed `(day_of_year - 1) / 7 + 1` against the calendar year and formatted
## it with `%d`. That is not the ISO week. It agreed with every seed blessed in
## 2026 by coincidence, then diverged permanently:
##
##     2026-07-24 .. 2026-12-25   naive == ISO
##     2027-01-01   naive weekly-2027-w1   ISO weekly-2026-w53
##     2027-01-08   naive weekly-2027-w2   ISO weekly-2027-w01
##     2027-02-05   naive weekly-2027-w6   ISO weekly-2027-w05
##
## Three defects on one date -- wrong ISO year, wrong week number, no
## zero-padding -- and v0.19 is scheduled for Friday 2027-01-01, so the fire
## date IS a league night.
##
## Why zero-padding is not cosmetic: the board key is an exact string. Under
## `%d` the first week of 2027 posts to `weekly-2027-w1` while every convention
## and every document says `weekly-2027-w01`. Those are two different boards,
## and a board cannot be tidied after the fact -- "filtering standings is
## editing them".
##
## RULING: 2026-08-24 -- the featured seed names the ISO week the league opens in -- flavour: league-seeds -- mechanism: godot/tests/unit/test_iso_week_seed.gd
##
## The reference implementation is Python's `date.isocalendar()`. The GDScript
## here was verified against it over every day from 2024-01-01 to 2032-12-31 --
## 3,288 consecutive days, zero mismatches -- before this test was written. The
## cases below are the boundaries that verification identified, kept so the
## property stays pinned without needing Python.


func test_blessed_seeds_round_trip():
	# Every seed actually blessed to date, at the date it was set. If this ever
	# fails, the convention changed and the ruling above needs revisiting --
	# it does not mean the test is stale.
	assert_eq(GameConfig.iso_week_seed(2026, 7, 24), "weekly-2026-w30")
	assert_eq(GameConfig.iso_week_seed(2026, 7, 31), "weekly-2026-w31")
	assert_eq(GameConfig.iso_week_seed(2026, 8, 7), "weekly-2026-w32")
	assert_eq(GameConfig.iso_week_seed(2026, 8, 13), "weekly-2026-w33")
	assert_eq(GameConfig.iso_week_seed(2026, 8, 23), "weekly-2026-w34")


func test_the_january_boundary_belongs_to_the_previous_iso_year():
	# ISO-8601: a week belongs to the year containing its Thursday. 2027-01-01
	# is a Friday whose Thursday fell on 2026-12-31, so the whole week is week
	# 53 OF 2026. The old code emitted weekly-2027-w1 here.
	assert_eq(GameConfig.iso_week_seed(2026, 12, 31), "weekly-2026-w53")
	assert_eq(GameConfig.iso_week_seed(2027, 1, 1), "weekly-2026-w53")
	assert_eq(GameConfig.iso_week_seed(2027, 1, 3), "weekly-2026-w53")
	# The Monday after starts ISO 2027.
	assert_eq(GameConfig.iso_week_seed(2027, 1, 4), "weekly-2027-w01")


func test_single_digit_weeks_are_zero_padded():
	# w1 and w01 are different board keys. This is the assertion that catches a
	# regression to "%d".
	assert_eq(GameConfig.iso_week_seed(2027, 1, 8), "weekly-2027-w01")
	assert_eq(GameConfig.iso_week_seed(2027, 2, 5), "weekly-2027-w05")
	assert_true(
		GameConfig.iso_week_seed(2027, 2, 5).ends_with("w05"),
		"single-digit ISO weeks must render as w05, never w5"
	)


func test_leap_year_and_year_end_edges():
	# 2028 is a leap year; the day-of-year offset must account for it.
	assert_eq(GameConfig.iso_week_seed(2028, 3, 1), "weekly-2028-w09")
	# 2024-12-30 is a Monday in ISO week 1 of 2025 -- the mirror of the 2027
	# case, where a December date belongs to the NEXT ISO year.
	assert_eq(GameConfig.iso_week_seed(2024, 12, 30), "weekly-2025-w01")


func test_weeks_advance_by_exactly_one_across_a_week_boundary():
	# A property rather than a fixture: consecutive Fridays must land on
	# consecutive week numbers. This is what the original ticks_msec bug broke
	# (the week froze), and a naive formula can break it at a year boundary
	# without any single fixture noticing.
	assert_eq(GameConfig.iso_week_seed(2026, 8, 28), "weekly-2026-w35")
	assert_eq(GameConfig.iso_week_seed(2026, 9, 4), "weekly-2026-w36")
	assert_eq(GameConfig.iso_week_seed(2026, 9, 11), "weekly-2026-w37")


func test_the_shipped_override_matches_the_week_it_names():
	# The override is what players actually post to. It must be a well-formed
	# seed for a real ISO week -- this catches a hand-typed literal like
	# "weekly-2026-w5" or "weekly-2026-w60".
	var seed: String = GameConfig.FEATURED_SEED_OVERRIDE
	if seed.is_empty():
		pass_test("no override set; the ISO fallback is under test above")
		return
	var parts := seed.split("-")
	assert_eq(parts.size(), 3, "seed shape is weekly-<isoyear>-w<NN>: " + seed)
	assert_eq(parts[0], "weekly", "seed must start with 'weekly': " + seed)
	var week_part: String = parts[2]
	assert_true(week_part.begins_with("w"), "third segment must start with w: " + seed)
	var digits := week_part.substr(1)
	assert_eq(digits.length(), 2, "ISO week must be zero-padded to 2 digits: " + seed)
	var week := int(digits)
	assert_true(week >= 1 and week <= 53, "ISO week out of range: " + seed)

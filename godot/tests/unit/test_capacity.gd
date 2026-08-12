extends GutTest
## Unit tests for Capacity -- the single derivation point for the monthly Attention budget.
##
## These exist to pin the two promises the 2026-08-12 ruling makes, both of which fail
## SILENTLY if broken:
##   1. ZERO BEHAVIOUR CHANGE while balance is being developed -- the value is the grant,
##      for every seed and every month. If this ever goes red, the ladder epoch must bump.
##   2. ANY variability is SEED-derived, never runtime RNG -- deriving must not advance
##      GameState.rng, or every recorded input-replay forks (ADR-0006).

const SEEDS := ["alpha", "bravo", "charlie", "2017-opening", "", "a much longer seed string"]

# 2017-01 through 2036-12 in Clock.month_index form (year * 12 + month - 1): twenty years,
# comfortably longer than any run the ladder will see.
const FIRST_MONTH := 2017 * 12
const LAST_MONTH := 2036 * 12 + 11


# --- Promise 1: the value is locked -------------------------------------------------

func test_balance_dial_is_still_twenty():
	# The ruling's number, pinned at its source. If someone retunes the dial this test is
	# the first thing that says so.
	assert_eq(Balance.inum("attention.per_month", 20), 20, "Balance attention.per_month is the ruling's 20")


func test_value_is_the_grant_for_every_seed_and_every_month():
	var grant: int = 20
	var mismatches: int = 0
	for game_seed in SEEDS:
		for mi in range(FIRST_MONTH, LAST_MONTH + 1):
			var got: Dictionary = Capacity.derive(game_seed, mi, {Capacity.MOD_GRANT: grant})
			if int(got["value"]) != grant:
				mismatches += 1
	assert_eq(mismatches, 0, "value == grant for all %d seed/month pairs" % (SEEDS.size() * (LAST_MONTH - FIRST_MONTH + 1)))


func test_value_falls_back_to_the_balance_dial_without_a_modifier():
	var got: Dictionary = Capacity.derive("alpha", FIRST_MONTH)
	assert_eq(int(got["value"]), Balance.inum("attention.per_month", 20), "no modifier set -> the Balance grant")


func test_value_honours_the_difficulty_and_scenario_grants():
	# Difficulty (easy 24 / standard 20 / hard 16) and scenario packs (sandbox 40) already
	# move the grant today. The derivation must pass them through untouched -- this is the
	# half of "zero behaviour change" that a hardcoded 20 would have quietly broken.
	for grant in [16, 20, 24, 40, 0]:
		var got: Dictionary = Capacity.derive("alpha", FIRST_MONTH + 6, {Capacity.MOD_GRANT: grant})
		assert_eq(int(got["value"]), grant, "grant %d passes through the derivation unchanged" % grant)


func test_derive_returns_both_fields():
	var got: Dictionary = Capacity.derive("alpha", FIRST_MONTH, {Capacity.MOD_GRANT: 20})
	assert_true(got.has("value"), "derive returns a value")
	assert_true(got.has("reason"), "derive returns a reason")
	assert_true(got["value"] is int, "value is an int")
	assert_true(got["reason"] is String, "reason is a String")


# --- Promise 2: seed-derived, never runtime RNG -------------------------------------

func test_reason_is_stable_for_the_same_seed_and_month():
	# Two runs on one board key must read the same sentence in the same month.
	for game_seed in SEEDS:
		for mi in [FIRST_MONTH, FIRST_MONTH + 6, FIRST_MONTH + 77, LAST_MONTH]:
			var first: String = Capacity.reason_for(game_seed, mi)
			for _repeat in range(5):
				assert_eq(Capacity.reason_for(game_seed, mi), first,
					"reason stable for seed '%s' month %d" % [game_seed, mi])


func test_deriving_does_not_advance_the_run_rng():
	# The failure this guards is the nastiest one available: a run that still completes and
	# still posts a score, from a stream that no longer matches its replay.
	var state := GameState.new("determinism_seed")
	var seed_before: int = state.rng.seed
	var state_before: int = state.rng.state
	for mi in range(FIRST_MONTH, FIRST_MONTH + 120):
		var _ignored: Dictionary = state.capacity_for_month(mi)
	assert_eq(state.rng.seed, seed_before, "capacity_for_month leaves rng.seed untouched")
	assert_eq(state.rng.state, state_before, "capacity_for_month leaves rng.state untouched")


func test_two_states_on_one_seed_read_the_same_reasons():
	var a := GameState.new("board_key_seed")
	var b := GameState.new("board_key_seed")
	for mi in range(FIRST_MONTH, FIRST_MONTH + 60):
		assert_eq(str(a.capacity_for_month(mi)["reason"]), str(b.capacity_for_month(mi)["reason"]),
			"same seed, same month, same sentence (month %d)" % mi)


func test_reasons_differ_across_seeds_somewhere():
	# Not every seed/month pair must differ (the pools are small), but the selection must
	# actually READ the seed. If this goes green with a constant reason, the salt is dead.
	var differing: int = 0
	for mi in range(FIRST_MONTH, FIRST_MONTH + 60):
		if Capacity.reason_for("alpha", mi) != Capacity.reason_for("bravo", mi):
			differing += 1
	assert_true(differing > 0, "the reason varies by seed (%d of 60 months differ)" % differing)


func test_reasons_differ_across_months_within_a_seed():
	var seen := {}
	for mi in range(FIRST_MONTH, FIRST_MONTH + 24):
		seen[Capacity.reason_for("alpha", mi)] = true
	assert_true(seen.size() > 1, "the reason varies by month (%d distinct over 24 months)" % seen.size())


# --- The reason itself ----------------------------------------------------------------

func test_every_calendar_month_has_a_reason_pool():
	assert_eq(Capacity.MONTH_REASONS.size(), 12, "one pool per calendar month")
	for m in range(12):
		var pool: Array = Capacity.MONTH_REASONS[m]
		assert_true(pool.size() > 0, "%s pool is not empty" % Clock.MONTH_NAMES[m])


func test_reason_names_its_calendar_month():
	# The contract reason_for() documents: the sentence opens with the month it explains,
	# so July reads as July in every run regardless of which run-year it falls in.
	for mi in range(FIRST_MONTH, FIRST_MONTH + 36):
		var month_name: String = Clock.MONTH_NAMES[posmod(mi, 12)]
		var reason: String = Capacity.reason_for("alpha", mi)
		assert_true(reason.begins_with(month_name + "."),
			"month %d reason opens with '%s.' -- got '%s'" % [mi, month_name, reason])


func test_july_reads_as_july_and_the_ruling_sentence_is_in_the_pool():
	assert_true(Capacity.MONTH_REASONS[6].has("July. Two researchers away, the university is shut, nobody answers email."),
		"the ruling's worked example is one of July's reasons")


func test_reason_is_never_empty_over_a_long_run():
	var empties: int = 0
	for mi in range(FIRST_MONTH, LAST_MONTH + 1):
		if Capacity.reason_for("alpha", mi).length() == 0:
			empties += 1
	assert_eq(empties, 0, "every month of a 20-year run has a reason")


func test_reason_pools_are_ascii_only():
	# scripts/check_no_emoji.py is a blocking pre-commit gate on godot/**/*.gd. This is the
	# same rule asserted at runtime so a bad paste is caught by the suite too.
	var offenders: Array = []
	for m in range(12):
		for reason in Capacity.MONTH_REASONS[m]:
			var text := String(reason)
			for i in range(text.length()):
				if text.unicode_at(i) >= 128:
					offenders.append(text)
					break
	assert_eq(offenders.size(), 0, "ASCII only -- non-ASCII in: %s" % str(offenders))


func test_reason_pools_never_name_a_number():
	# The sentences must stay true when the value unlocks, so they explain the month, not
	# the size of the budget.
	for m in range(12):
		for reason in Capacity.MONTH_REASONS[m]:
			var digits: int = 0
			for i in range(String(reason).length()):
				var c: int = String(reason).unicode_at(i)
				if c >= 48 and c <= 57:
					digits += 1
			assert_eq(digits, 0, "no digits in '%s'" % reason)


# --- Wiring: the call sites really do read the derivation -----------------------------

func test_game_state_opens_its_first_month_from_the_derivation():
	var state := GameState.new("boot_seed")
	var expected: Dictionary = state.capacity_for_month(
		Clock.month_index(0, state.start_year, state.start_month, state.start_day))
	assert_eq(state.month_plan.attention_total, int(expected["value"]),
		"reset() opened month 0 with the derived value")
	assert_eq(state.month_plan.attention_total, state.attention_per_month,
		"and it equals the stored grant -- zero behaviour change")


func test_capacity_for_month_reads_the_stored_grant_as_its_modifier():
	var state := GameState.new("modifier_seed")
	state.attention_per_month = 16
	assert_eq(int(state.capacity_for_month(FIRST_MONTH)["value"]), 16,
		"the field is the modifier the derivation reads back out")


func test_current_month_index_matches_the_clock():
	var state := GameState.new("clock_seed")
	assert_eq(state.current_month_index(),
		Clock.month_index(state.turn, state.start_year, state.start_month, state.start_day),
		"current_month_index is Clock.month_index for the current turn")

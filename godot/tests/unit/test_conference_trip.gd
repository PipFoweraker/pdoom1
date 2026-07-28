extends GutTest
## ConferenceTrip -- the ADR-0014 rhythm-break shell (Pip rulings 2026-07-27).
##
## The two properties this lane must not lose:
##   1. an away window auto-resolves DETERMINISTICALLY (model A skip-turns rides the existing
##      seeded stream through MonthController.advance_tick -- no new RNG source), so a
##      recorded replay re-simulates the blackout window identically;
##   2. everything that fired while the founder was away lands in the return BACKLOG rather
##      than vanishing or ambushing the player as a stack of modals.

var state: GameState
var turn_manager: TurnManager
var controller: MonthController
var _saved_historical_events := []


func before_each():
	# Test isolation (#534): unit tests must NOT load the live ~1194-event historical timeline
	# into pending_events -- it hangs the headless suite. Same guard as test_turn_manager.gd.
	if EventService:
		_saved_historical_events = EventService.transformed_events.duplicate()
		EventService.transformed_events.clear()
	ConferenceTrip.reload_catalogue()
	state = GameState.new("conference-trip-seed")
	turn_manager = TurnManager.new(state)
	controller = MonthController.new(state, turn_manager)
	turn_manager.start_turn()  # open turn 1, matching the plan phase GameManager boots into


func after_each():
	if EventService:
		EventService.transformed_events = _saved_historical_events


func _fresh_run(game_seed: String) -> Dictionary:
	"""Stand up an independent run on `game_seed` and take the same trip on it."""
	var s := GameState.new(game_seed)
	var tm := TurnManager.new(s)
	var mc := MonthController.new(s, tm)
	tm.start_turn()
	var trip: Dictionary = ConferenceTrip.run_trip(s, mc, "safety_retreat")
	return {"state": s, "trip": trip}


func _fingerprint(s: GameState, trip: Dictionary) -> String:
	"""Everything an away window is allowed to move, plus the backlog it produced. Compared as
	one JSON blob so a divergence anywhere shows up as a failed string equality."""
	return JSON.stringify({
		"turn": s.turn,
		"money": s.money,
		"reputation": s.reputation,
		"doom": s.doom,
		"rng_state": str(s.rng.state),
		"attended": s.attended_conferences,
		"backlog": trip.get("backlog", []),
		"memento": trip.get("memento", {}),
		"ticks_resolved": trip.get("ticks_resolved", 0),
		"attention_consumed": trip.get("attention_consumed", 0),
		"cut_short": trip.get("cut_short", false),
	})


# ---------------------------------------------------------------------------
# Catalogue + the away-window arithmetic (Pip's travel ruling)
# ---------------------------------------------------------------------------
func test_catalogue_loads_the_shell_entries():
	var all: Array = ConferenceTrip.catalogue()
	assert_gt(all.size(), 0, "conferences.json loaded at least one entry")
	assert_between(all.size(), 2, 4, "the shell catalogue stays tiny (2-3 entries by design)")
	for conf in all:
		assert_true(conf.has("id"), "every entry has an id")
		assert_gt(int(conf.get("duration_turns", 0)), 0, "every entry has a positive duration")


func test_away_window_includes_travel_on_both_sides():
	# Pip 2026-07-27 1555: attending consumes the away window PLUS roughly a day either side
	# for travel -- travel days are exposed time, not free.
	var conf := {"duration_turns": 3, "travel_days": 1}
	assert_eq(ConferenceTrip.away_ticks(conf), 5, "3 days away + 1 travel day each side")
	var big := {"duration_turns": 5, "travel_days": 2}
	assert_eq(ConferenceTrip.away_ticks(big), 9, "5 days away + 2 travel days each side")


# ---------------------------------------------------------------------------
# Determinism -- the load-bearing property
# ---------------------------------------------------------------------------
func test_away_window_resolves_deterministically():
	var a := _fresh_run("conference-determinism-probe")
	var b := _fresh_run("conference-determinism-probe")
	assert_true(bool(a["trip"].get("success", false)), "run A committed")
	assert_true(bool(b["trip"].get("success", false)), "run B committed")
	var fa := _fingerprint(a["state"], a["trip"])
	var fb := _fingerprint(b["state"], b["trip"])
	if fa != fb:
		gut.p("[conference-determinism] A: " + fa)
		gut.p("[conference-determinism] B: " + fb)
	assert_eq(fa, fb, "the same seed must resolve the same away window, backlog included")


func test_away_window_advances_exactly_the_expected_ticks():
	# Non-vacuity guard for the determinism test above: the window must actually run turns.
	var start := state.turn
	var trip: Dictionary = ConferenceTrip.run_trip(state, controller, "safety_retreat")
	assert_true(bool(trip.get("success", false)), "committed to the retreat")
	var expected: int = ConferenceTrip.away_ticks(ConferenceTrip.by_id("safety_retreat"))
	if not bool(trip.get("cut_short", false)):
		assert_eq(int(trip.get("ticks_resolved", 0)), expected, "resolved the whole away window")
		assert_eq(state.turn - start, expected, "state.turn advanced by exactly the away window")
	assert_gt(int(trip.get("ticks_resolved", 0)), 0, "the trip is not a no-op")


# ---------------------------------------------------------------------------
# The backlog captures what fired while away
# ---------------------------------------------------------------------------
func test_backlog_captures_fired_feed_events():
	# Against a synthetic advance_tick() result, so the assertion is about the collector's
	# contract rather than about whichever events a given seed happens to roll.
	var backlog: Array = []
	ConferenceTrip.collect_tick(backlog, 12, {
		"status": "ready",
		"month_opened": false,
		"feed": [
			{"source_id": "rivals", "event": {"id": "rival_move", "name": "A rival moved", "channel": "rivals"}},
			{"source_id": "hiring", "event": {"id": "advertise_hit", "name": "Applicant responded"}},
		],
		"released": [],
	})
	assert_eq(backlog.size(), 2, "both fired feed events landed in the backlog")
	assert_eq(String(backlog[0].get("kind", "")), "feed", "captured as feed items")
	assert_eq(int(backlog[0].get("turn", 0)), 12, "stamped with the turn they fired on")
	assert_eq(String(backlog[0].get("name", "")), "A rival moved", "keeps the event's own name")
	assert_eq(String(backlog[0].get("channel", "")), "rivals", "carries the feed channel through")


func test_backlog_captures_month_boundaries_and_released_work():
	var backlog: Array = []
	ConferenceTrip.collect_tick(backlog, 30, {
		"status": "month_open",
		"month_opened": true,
		"feed": [],
		"released": [{"action_id": "research_basic", "attention_cost": 2}],
	})
	var kinds: Array = []
	for entry in backlog:
		kinds.append(String(entry.get("kind", "")))
	assert_has(kinds, "month_opened", "a month opening with nobody home is reported")
	assert_has(kinds, "strategic_released", "strategic WIP that landed while away is reported")


func test_real_away_window_produces_a_readable_backlog():
	var trip: Dictionary = ConferenceTrip.run_trip(state, controller, "neurips")
	if not bool(trip.get("success", false)):
		# Not affordable on this seed's opening cash -- the gate is itself the behaviour.
		assert_string_contains(String(trip.get("message", "")), "afford", "refused for an honest reason")
		return
	var backlog: Array = trip.get("backlog", [])
	for entry in backlog:
		assert_true(entry is Dictionary, "backlog entries are plain data")
		assert_true(entry.has("kind"), "every entry declares its kind")
		assert_true(entry.has("turn"), "every entry is stamped with when it happened")


# ---------------------------------------------------------------------------
# The costs that keep this from being a free button
# ---------------------------------------------------------------------------
func test_trip_consumes_all_remaining_operating_hours():
	# Pip ruling 2026-07-27 1555 ("attending consumes the founder's remaining capacity"),
	# REFINED by his #980 noticing and cashed out by T2's 2-way founder hours: being away is
	# a loss of OPERATOR PRESENCE, not of PLANNER MIND. So the trip must drain the operating
	# pool to nothing, and must NOT touch planning hours -- next month's direction is still
	# decidable from a hotel room. The anti-free-button property is preserved: every form of
	# presence work (windows, hiring, interviews, travel) is dead for the rest of the month.
	var before_operating: int = state.month_plan.hours_available(MonthPlan.HOUR_OPERATING)
	var before_planning: int = state.month_plan.hours_available(MonthPlan.HOUR_PLANNING)
	assert_gt(before_operating, 0, "the founder starts the month with presence to lose")
	var trip: Dictionary = ConferenceTrip.run_trip(state, controller, "safety_retreat")
	assert_true(bool(trip.get("success", false)), "committed")
	assert_eq(state.month_plan.hours_available(MonthPlan.HOUR_OPERATING), 0,
		"no operating hours are left -- the founder is not in the building")
	assert_eq(state.month_plan.hours_available(MonthPlan.HOUR_PLANNING), before_planning,
		"planner mind survives the trip (#980)")
	assert_gt(int(trip.get("attention_consumed", 0)), 0, "the cost is reported back to the player")


func test_travel_cash_leaves_up_front():
	var conf := ConferenceTrip.by_id("safety_retreat")
	var cost: int = int(conf.get("travel_cost", 0))
	assert_gt(cost, 0, "the retreat costs real travel cash")
	var money_before: float = state.money
	var trip: Dictionary = ConferenceTrip.run_trip(state, controller, "safety_retreat")
	assert_true(bool(trip.get("success", false)), "committed")
	# Salaries and the ledger also bill during the away window, so cash must be at least the
	# travel cost lower -- the point is that the travel cash is not free.
	assert_lt(state.money, money_before - float(cost) + 1.0, "travel cash left the account")


func test_cannot_attend_the_same_conference_twice_in_a_year():
	var first: Dictionary = ConferenceTrip.run_trip(state, controller, "safety_retreat")
	assert_true(bool(first.get("success", false)), "first trip committed")
	var gate: Dictionary = ConferenceTrip.can_commit(state, "safety_retreat")
	assert_false(bool(gate.get("ok", true)), "a second trip this year is refused")
	assert_string_contains(String(gate.get("reason", "")), "Already attended", "with a legible reason")


func test_unknown_conference_is_refused_cleanly():
	var trip: Dictionary = ConferenceTrip.run_trip(state, controller, "not_a_conference")
	assert_false(bool(trip.get("success", true)), "refused")
	assert_eq((trip.get("backlog", []) as Array).size(), 0, "and produces no backlog")

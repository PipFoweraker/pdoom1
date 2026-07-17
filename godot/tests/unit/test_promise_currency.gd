extends GutTest
## fix/promise-currency (Option B): appetite promises cost a FUTURE OBLIGATION IN THEIR OWN
## DOMAIN, never raw reputation.
##
## THE BUG (confirmed from a real playtest death, turn 14): the old appetite_promise minted a
## REPUTATION-currency principal (~2000) while reputation STARTS AT 50 and death fires at
## reputation <= 0 (game_state.gd check_win_lose). A single promise's bill zeroed the whole
## reputation bar -> instant death. The headline negotiation mechanic was a mis-scaled
## instant-death trap.
##
## THE FIX: re-home each promise's cost onto the thing it actually promises --
##   first_authorship -> a paper / first-author slot OWED (currency "papers")
##   compute_budget   -> compute committed to the hire (currency "compute")
##   mission_charter / mentorship -> a standing governance/mission obligation (currency "governance")
## Magnitudes are small + survivable; NONE bill reputation. The discount-to-self_worth_floor
## negotiation currency (ADR-0011) is unchanged -- only the COST side moved.
##
## DESIGN GUARDRAIL (Pip): a new player must NOT be able to LOSE within the first ~6 turns via
## promises used as intended. Reputation must not be instantly zeroable by a single promise.


func _new_state(seed_str: String = "promise_currency") -> GameState:
	var s := GameState.new(seed_str)
	s.turn = 1
	return s


func _make_candidate(state: GameState, spec: String, skill: int, expectation: float, appetites: Dictionary = {}) -> Researcher:
	var c := Researcher.new(spec)
	c.skill_level = skill
	c.base_productivity = 0.5 + skill * 0.1
	c.salary_expectation = expectation
	c.current_salary = expectation
	for k in Researcher.APPETITE_KEYS:
		c.appetites[k] = float(appetites.get(k, 0.0))
	state.candidate_pool.clear()
	state.add_candidate(c)
	return c


func _advance_and_tick(state: GameState, ticks: int) -> void:
	for i in range(ticks):
		state.turn += 1
		state.hiring.on_tick(state)


# --- The rep-bomb is gone -------------------------------------------------------

func test_no_promise_mints_a_reputation_currency_entry():
	# Every promise id (incl. mentorship) must bill in its OWN domain, never reputation.
	for pid in Ledger.PROMISE_SPEC:
		var e: Ledger.Entry = Ledger.appetite_promise("Alice", pid)
		assert_ne(e.currency, "reputation",
			"promise '%s' must NOT be a reputation-currency entry (the old rep-bomb)" % pid)
		assert_eq(e.currency, String(Ledger.PROMISE_SPEC[pid]["currency"]),
			"promise '%s' bills in its domain currency" % pid)
		assert_true(String(e.source).begins_with("promise:%s:" % pid),
			"source keeps the promise:<id>:<name> tag for attribution")


func test_promise_bill_does_not_zero_reputation():
	# Billing a promise (even at its full principal) leaves reputation untouched -- the exact
	# failure the fix targets. Bill the first-authorship promise directly.
	var s := _new_state("rep_untouched")
	var rep0: float = s.reputation
	var e: Ledger.Entry = Ledger.appetite_promise("Alice", "first_authorship")
	e.fuse = 0  # due now
	s.ledger.add(e)
	s.ledger.tick_and_bill(s)
	s.check_win_lose()
	assert_almost_eq(s.reputation, rep0, 0.001, "a promise bill leaves reputation unchanged")
	assert_false(s.game_over, "no death from a promise bill")


func test_promise_bills_in_its_domain_resource():
	# first_authorship draws a paper; compute_budget draws compute; mission_charter draws
	# governance -- all survivable, none touching reputation.
	var s := _new_state("domain_bill")
	s.papers = 3.0
	var compute0: float = s.compute
	var gov0: float = s.governance
	for pid in ["first_authorship", "compute_budget", "mission_charter", "mentorship"]:
		var e: Ledger.Entry = Ledger.appetite_promise("Alice", pid)
		e.fuse = 0
		s.ledger.add(e)
	s.ledger.tick_and_bill(s)
	assert_lt(s.papers, 3.0, "first_authorship consumed a paper slot")
	assert_lt(s.compute, compute0, "compute_budget drew committed compute")
	assert_lt(s.governance, gov0, "mission/mentorship charged governance (a standing obligation)")


# --- Guardrail: promises cannot lose the game in the first 6 turns --------------

func test_promise_heavy_hire_cannot_lose_within_6_turns():
	# A promise-hungry candidate hired on ALL promises (as intended), then six turns of ledger
	# billing. The player must survive -- reputation must not be zeroable by promises.
	var s := _new_state("six_turn_safety")
	var c := _make_candidate(s, "safety", 7, 80000.0, {
		"prestige": 1.0, "compute": 1.0, "mission_purity": 1.0, "mentees": 1.0, "money": 0.0,
	})
	var all_promises := ["first_authorship", "compute_budget", "mission_charter", "mentorship"]
	var promised_floor: float = s.hiring.self_worth_floor(c, all_promises)
	s.hiring.make_offer(s, c.candidate_id, promised_floor + 500.0, all_promises)
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	assert_eq(c.hire_state, Researcher.HireState.EMPLOYED, "the promise-heavy offer was accepted")
	# Confirm the promises minted domain obligations (not reputation).
	var promise_entries := 0
	for e in s.ledger.entries:
		if String(e.source).begins_with("promise:"):
			promise_entries += 1
			assert_ne(e.currency, "reputation", "no minted promise is a reputation entry")
	assert_eq(promise_entries, all_promises.size(), "each promise minted its obligation")

	# Six turns of ledger billing from turn 1. The player must not lose.
	var start_turn: int = s.turn
	for t in range(6):
		s.turn += 1
		s.ledger.tick_and_bill(s)
		s.check_win_lose()
		assert_false(s.game_over,
			"promises used as intended must not cause a loss by turn %d" % (s.turn - start_turn))
	assert_gt(s.reputation, 0.0, "reputation is never zeroed by hiring promises")


func test_worst_case_all_promises_bill_immediately_is_survivable():
	# Stress: force EVERY promise to bill on turn 1 (fuse 0) from fresh starting resources.
	# Even this worst case must be survivable (defends the guardrail against future fuse tuning).
	var s := _new_state("worst_case")
	for pid in Ledger.PROMISE_SPEC:
		var e: Ledger.Entry = Ledger.appetite_promise("Alice", pid)
		e.fuse = 0
		s.ledger.add(e)
	s.ledger.tick_and_bill(s)
	s.check_win_lose()
	assert_false(s.game_over, "all promises billing at once is survivable")
	assert_gt(s.reputation, 0.0, "reputation survives a full promise barrage")


# --- Serialization round-trip ---------------------------------------------------

func test_promise_obligations_serialize_round_trip():
	var s := _new_state("promise_saveload")
	for pid in Ledger.PROMISE_SPEC:
		s.ledger.add(Ledger.appetite_promise("Alice", pid))
	var before := []
	for e in s.ledger.entries:
		before.append({"source": e.source, "currency": e.currency, "principal": e.principal, "fuse": e.fuse})

	var blob := JSON.stringify(s.to_dict())
	var parsed = JSON.parse_string(blob)
	assert_not_null(parsed, "state with promise obligations serializes to JSON")

	var s2 := GameState.new("promise_reload")
	s2.from_dict(parsed)
	assert_eq(s2.ledger.entries.size(), s.ledger.entries.size(), "all promise entries round-trip")
	for i in range(before.size()):
		var e2: Ledger.Entry = s2.ledger.entries[i]
		assert_eq(e2.source, before[i]["source"], "source round-trips")
		assert_eq(e2.currency, before[i]["currency"], "domain currency round-trips")
		assert_almost_eq(e2.principal, before[i]["principal"], 0.001, "principal round-trips exactly")
		assert_eq(e2.fuse, before[i]["fuse"], "fuse round-trips")


# --- Legibility: the cost is surfaced before commit -----------------------------

func test_each_promise_exposes_a_cost_line():
	# The offer flow (main_ui.gd) reads this to show the obligation BEFORE the player commits.
	for pid in Ledger.PROMISE_SPEC:
		var text := Ledger.appetite_promise_cost_text(pid)
		assert_true(text.length() > 0, "promise '%s' exposes a human cost line" % pid)
		assert_true(text.contains("owes"), "the cost line names the obligation for '%s'" % pid)

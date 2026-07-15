extends GutTest
## WS-1 (ADR-0003): the Liability Ledger.
## Verifies entry lifecycle (fuse / compounding interest / billing), the bankruptcy
## escalation that gives debt teeth, secret exposure -> blackmail chaining, and — the
## definition-of-done — the ADR-0002 mortality guarantee via a headless soak: a
## desperation bot buys time then dies of its own ledger (death is attributable);
## a lean bot dies sooner but clean (no ledger attribution). Both runs are finite.

func _fresh_state(seed_str: String):
	var s = GameState.new(seed_str)
	s.doom = 50.0
	s.money = 245000.0
	s.governance = 50.0
	s.reputation = 50.0
	# ADR-0015: these tests exercise the LEDGER's own conversion contract in isolation
	# (synchronous doom arithmetic, controlled soak). With a doom_system attached the
	# ledger routes doom as a buffered STREAM INPUT (applied on the next doom tick) —
	# correct in the real loop, but it would decouple the soak's hand-rolled doom math.
	# Detach the authority so Ledger._add_doom takes its documented lightweight-double
	# fallback (state.doom +=). Stream routing is covered by test_doom_system + the sweep.
	if s.doom_system:
		s.doom_system.free()
		s.doom_system = null
	return s


func test_fuse_ticks_and_interest_compounds_before_due():
	var state = _fresh_state("ledger-lifecycle")
	var e = Ledger.loan(100000.0, 3, 0.25)  # principal 120k, fuse 3, +25%/turn
	state.ledger.add(e)
	var start_money: float = state.money

	state.ledger.tick_and_bill(state)  # compound 120k->150k, fuse 3->2, not due
	assert_eq(e.fuse, 2, "fuse decrements each turn")
	assert_almost_eq(e.principal, 150000.0, 1.0, "principal compounds by interest rate")
	assert_eq(state.money, start_money, "nothing billed before the fuse burns down")
	assert_false(e.settled, "live entry is not settled")


func test_due_entry_bills_its_currency():
	var state = _fresh_state("ledger-bill")
	state.ledger.add(Ledger.Entry.new("loan", "money", 50000.0, 0, 0.0))  # due now, no interest
	var start_money: float = state.money
	state.ledger.tick_and_bill(state)
	assert_eq(state.money, start_money - 50000.0, "a due money entry bills in money")
	assert_eq(state.ledger.entries[0].settled, true, "billed entry settles")


func test_unpayable_bill_escalates_to_doom_and_is_attributed():
	var state = _fresh_state("ledger-bankruptcy")
	state.money = 5000.0
	var doom0: float = state.doom
	state.ledger.add(Ledger.Entry.new("loan", "money", 100000.0, 0, 0.0))
	state.ledger.tick_and_bill(state)
	assert_eq(state.money, 0.0, "money floors at zero on an unpayable bill")
	assert_gt(state.doom, doom0, "the unpayable shortfall escalates into doom (the teeth)")
	assert_gt(state.ledger.death_attribution.size(), 0, "the killing bill is attributed to its entry")


func test_secret_exposure_offers_a_blackmail_entry():
	var state = _fresh_state("ledger-expose")
	var secret = Ledger.desperation_payroll(state.rng)  # secret governance liability
	state.ledger.add(secret)
	assert_true(secret.secret, "the payroll coinflip plants a secret liability")
	var before: int = state.ledger.entries.size()
	state.ledger.expose(secret, state)
	assert_false(secret.secret, "exposure burns the secrecy flag")
	assert_gt(state.ledger.entries.size(), before, "exposure offers a new blackmail entry (the chain continues)")


# ---- Mortality-guarantee soak (the DoD) ----
# A controlled structural soak of the ledger mechanic: doom rises each turn; spending
# money suppresses it. The lean bot spends only clean money; the desperation bot also
# takes loans to keep suppressing after clean money runs out. (Full-pipeline soak
# through TurnManager's real doom/rival balance is a follow-up seam — see PR.)
const _DOOM_RISE := 6.0
const _SUPPRESS := 8.0
const _COST := 45000.0

func _soak(desperation: bool) -> Dictionary:
	var state = _fresh_state("soak-%s" % ("desperation" if desperation else "lean"))
	var turn := 0
	while state.doom < 100.0 and turn < 300:
		turn += 1
		state.ledger.tick_and_bill(state)          # ledger bills first (may spike doom)
		if state.doom >= 100.0:
			break
		state.doom += _DOOM_RISE
		var suppressed := false
		if state.money >= _COST:
			state.money -= _COST
			suppressed = true
		elif desperation:
			# Desperation lever: borrow to fund another suppression — buys time now,
			# plants a compounding liability that bills later.
			state.money += 70000.0
			state.ledger.add(Ledger.loan(70000.0, 12, 0.10))
			state.money -= _COST
			suppressed = true
		if suppressed:
			state.doom -= _SUPPRESS
		state.doom = clamp(state.doom, 0.0, 300.0)
	return {
		"turns": turn,
		"attributed": state.ledger.death_attribution.size(),
		"final_doom": state.doom,
	}


func test_mortality_guarantee_no_immortal_runs():
	# Compounding payables guarantee termination: even the doom-suppressing desperation
	# bot cannot outrun its ledger.
	var desp := _soak(true)
	assert_lt(desp["turns"], 300, "a debt-fuelled run must still terminate (no immortal runs)")
	assert_gt(desp["attributed"], 0, "the desperation death is attributable to ledger entries")


func test_desperation_buys_time_then_dies_of_its_own_ledger():
	var lean := _soak(false)
	var desp := _soak(true)
	# Desperation buys time — it survives strictly longer than the clean-hands run...
	assert_gt(desp["turns"], lean["turns"], "desperation levers buy time (more turns survived)")
	# ...but at the cost of a spectacular, self-inflicted death.
	assert_gt(desp["attributed"], 0, "desperation dies of its own ledger (attributed)")
	assert_eq(lean["attributed"], 0, "the lean run dies clean — no ledger attribution")

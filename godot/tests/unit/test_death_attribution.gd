extends GutTest
## EE-8 (ADR-0012): root-cause death attribution.
## Verifies the contributing-cause trail (turn-stamped ledger defaults/exposures,
## rep-collapse watermark) and the DeathAttribution classifier: a rep/doom death
## downstream of ledger damage is a LEDGER death; clean deaths stay themselves;
## stale immaterial scratches don't claim a death. Recording must never mutate
## outcomes — classify() is read-only over a finished state.

func _fresh_state(seed_str: String):
	var s = GameState.new(seed_str)
	s.doom = 50.0
	s.money = 245000.0
	s.governance = 50.0
	s.reputation = 50.0
	return s


func test_ledger_default_writes_turn_stamped_causes():
	var state = _fresh_state("attr-default")
	state.turn = 7
	state.money = 5000.0
	state.ledger.add(Ledger.Entry.new("loan", "money", 100000.0, 0, 0.0))
	state.ledger.tick_and_bill(state)
	assert_gt(state.cause_log.size(), 0, "an unpayable bill writes a contributing cause")
	var c: Dictionary = state.cause_log[0]
	assert_eq(str(c.kind), "ledger_default", "the cause kind names the default")
	assert_eq(int(c.turn), 7, "the cause is turn-stamped")
	assert_true(c.effects.has("doom"), "the cause records the doom conversion")
	assert_true(float(c.effects.reputation) < 0.0, "the cause records the rep damage")
	assert_eq(int(state.ledger.death_attribution[0].get("turn", -1)), 7,
		"death_attribution rows gain the turn stamp too")


func test_exposure_records_applied_not_intended_rep_damage():
	var state = _fresh_state("attr-expose")
	state.reputation = 10.0
	var secret = Ledger.desperation_payroll(state.rng)  # intended rep hit is 32-56
	state.ledger.add(secret)
	state.ledger.expose(secret, state)
	var c = null
	for x in state.cause_log:
		if str(x.kind) == "ledger_exposure":
			c = x
	assert_not_null(c, "exposure writes a contributing cause")
	assert_almost_eq(float(c.effects.reputation), -10.0, 0.01,
		"APPLIED rep damage is recorded (clamped at the zero floor), not the intended magnitude")


func test_rep_death_downstream_of_exposure_is_ledger_rooted():
	var state = _fresh_state("attr-rep-death")
	state.turn = 5
	state.reputation = 30.0  # below the minimum 32-rep exposure hit -> guaranteed collapse
	var secret = Ledger.desperation_payroll(state.rng)
	state.ledger.add(secret)
	state.ledger.expose(secret, state)
	state.check_win_lose()
	assert_true(state.game_over, "rep hit zero -> run over")
	var r: Dictionary = DeathAttribution.classify(state)
	assert_eq(str(r.surface), "rep", "the surface counter is reputation")
	assert_eq(str(r.root_cause), "ledger",
		"a rep death downstream of a ledger exposure is a LEDGER death (ADR-0012 cascade)")
	assert_gt((r.chain as Array).size(), 0, "the chain names the causal trail")
	assert_true(str(r.chain[0]).begins_with("t"), "chain entries are turn-stamped")


func test_doom_death_without_ledger_causes_stays_doom_rooted():
	var state = _fresh_state("attr-doom-clean")
	state.doom_system.current_doom = 100.0
	state.check_win_lose()
	var r: Dictionary = DeathAttribution.classify(state)
	assert_eq(str(r.surface), "doom")
	assert_eq(str(r.root_cause), "doom", "a clean doom death is not stolen by the ledger")


func test_stale_immaterial_scratch_does_not_claim_a_doom_death():
	var state = _fresh_state("attr-stale")
	state.turn = 3
	state.note_cause("ledger_default", "loan", {"doom": 0.5, "reputation": -0.2})
	state.turn = 40  # far outside RECENT_WINDOW
	state.doom_system.current_doom = 100.0
	state.check_win_lose()
	var r: Dictionary = DeathAttribution.classify(state)
	assert_eq(str(r.root_cause), "doom",
		"a tiny default 37 turns before death is history, not root cause (materiality + recency guards)")


func test_rep_collapse_watermark_recorded_once():
	var state = _fresh_state("attr-collapse")
	state.reputation = 8.0  # below REP_COLLAPSE_THRESHOLD but above zero
	state.check_win_lose()
	state.check_win_lose()
	var n := 0
	for c in state.cause_log:
		if str(c.kind) == "rep_collapse":
			n += 1
	assert_eq(n, 1, "the first crossing marks the chain exactly once")
	assert_false(state.game_over, "a collapse watermark is not itself a death")


func test_live_run_classifies_as_none():
	var state = _fresh_state("attr-alive")
	var r: Dictionary = DeathAttribution.classify(state)
	assert_eq(str(r.surface), "none")
	assert_eq(str(r.root_cause), "none")

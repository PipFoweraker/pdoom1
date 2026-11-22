extends GutTest
## EE-8 (ADR-0012): root-cause death attribution.
## Verifies the contributing-cause trail (turn-stamped ledger defaults/exposures,
## rep-collapse watermark) and the DeathAttribution classifier: a rep/doom death
## downstream of ledger damage is a LEDGER death; clean deaths stay themselves;
## stale immaterial scratches don't claim a death. Recording must never mutate
## outcomes -- classify() is read-only over a finished state.

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
	# Start rep below the minimum possible exposure hit (post-L1 desperation severity ~1200-2000
	# * expose.rep_per_1000/1000 ~ 3.0-5.0) so the applied damage is guaranteed to clamp at the
	# zero floor -- the point of the test is that the CLAMPED value is recorded, not the intended.
	state.reputation = 1.0
	var secret = Ledger.desperation_payroll(state.rng)
	state.ledger.add(secret)
	state.ledger.expose(secret, state)
	var c = null
	for x in state.cause_log:
		if str(x.kind) == "ledger_exposure":
			c = x
	assert_not_null(c, "exposure writes a contributing cause")
	assert_almost_eq(float(c.effects.reputation), -1.0, 0.01,
		"APPLIED rep damage is recorded (clamped at the zero floor), not the intended magnitude")


func test_rep_death_downstream_of_exposure_is_ledger_rooted():
	var state = _fresh_state("attr-rep-death")
	state.turn = 5
	# A materially large secret liability (governance principal 12000 -> exposure rep hit 30 at
	# expose.rep_per_1000=2.5), so the applied damage clears BOTH the classifier's REP_MATERIALITY
	# floor and the starting rep -- a guaranteed, ledger-rooted rep collapse. (Post-T9 the default
	# desperation_payroll exposure ~3-5 rep sits under the materiality edge; this test isolates
	# the cascade classification, not the factory magnitude.)
	state.reputation = 20.0
	var secret = Ledger.Entry.new("payroll_coinflip", "governance", 12000.0, 0, 0.0, true)
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

## ---- #1248: the panel must not blame a crisis the player survived ----------
##
## Reproduces the run Pip played on 2026-08-21 exactly: died on turn 130, with
## funding_starvation logged at t80 and rep_collapse at t87, and $1,189,765 in the
## bank at the end. The old panel printed both under CAUSE OF DEATH.

func _run_that_recovered():
	var s = _fresh_state("issue_1248_recovered")
	s.turn = 130
	s.game_over = true
	s.reputation = 0.0
	s.money = 1189765.0
	s.cause_log.append({
		"turn": 80, "kind": "funding_starvation", "source": "payroll",
		"effects": {"cash_level": 248.0, "bills_due": 670.3},
	})
	s.cause_log.append({
		"turn": 87, "kind": "rep_collapse", "source": "reputation",
		"effects": {"reputation_level": 5.0},
	})
	return s

func test_causes_older_than_the_window_are_history_not_cause():
	var s = _run_that_recovered()
	var split: Dictionary = DeathAttribution.chain_split(s)
	assert_eq(split["proximate"].size(), 0,
		"t80 and t87 are 50 and 43 turns before a t130 death -- neither is proximate")
	assert_eq(split["earlier"].size(), 2,
		"both are kept as history; nothing is dropped")

func test_panel_does_not_print_survived_crises_as_cause_of_death():
	var s = _run_that_recovered()
	var result := DeathAttribution.classify(s)
	var bbcode := GameOverScreen.build_attribution_bbcode(
		result.get("chain_proximate", []), "", result.get("chain_earlier", []))
	var cause_half := bbcode.substr(0, bbcode.find("EARLIER IN THE RUN"))
	assert_eq(cause_half.find("funding_starvation"), -1,
		"a cash crisis survived 50 turns earlier must not sit under CAUSE OF DEATH")
	assert_true(bbcode.find("EARLIER IN THE RUN") != -1,
		"it is still shown, under an honest heading")
	assert_true(bbcode.find("funding_starvation") != -1,
		"and it is not thrown away -- the trail is the interesting part")

func test_recent_causes_still_reach_the_cause_panel():
	# The control: the same shapes, logged just before death, MUST be blamed.
	var s = _fresh_state("issue_1248_proximate")
	s.turn = 130
	s.game_over = true
	s.reputation = 0.0
	s.cause_log.append({
		"turn": 128, "kind": "ledger_default", "source": "payroll",
		"effects": {"doom": 2.0, "reputation": -8.0},
	})
	var split: Dictionary = DeathAttribution.chain_split(s)
	assert_eq(split["proximate"].size(), 1, "t128 vs a t130 death is proximate")
	assert_eq(split["earlier"].size(), 0, "and nothing is demoted to history")

func test_unstamped_cause_is_treated_as_proximate():
	# A cause with no turn cannot be SHOWN to be old. Demoting it would hide a
	# real one; the filter must fail toward blaming, not toward silence.
	var s = _fresh_state("issue_1248_unstamped")
	s.turn = 130
	s.game_over = true
	s.cause_log.append({"kind": "ledger_default", "source": "payroll", "effects": {}})
	var split: Dictionary = DeathAttribution.chain_split(s)
	assert_eq(split["proximate"].size(), 1, "an unstamped cause stays in the cause panel")

func test_full_chain_is_unchanged_for_the_sweep_drivers():
	# tests/manual/ analyse whole runs and read `chain`. Splitting the panel must
	# not quietly shorten what they see.
	var s = _run_that_recovered()
	var result := DeathAttribution.classify(s)
	assert_eq((result.get("chain", []) as Array).size(), 2,
		"`chain` stays the UNFILTERED trail")

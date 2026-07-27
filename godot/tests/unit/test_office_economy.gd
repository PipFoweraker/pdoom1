extends GutTest
## Early-game office economy (#791, #811 item 1): the tier-0 hire cap, the 3-option lease
## menu as a FinanceEngine instrument family, sign-and-lock-in, rent on the payroll rail,
## the render/sim boundary (ADR-0018), and the scouting action stubs.

var _created: Array = []

func _fresh_state(seed_str: String = "office-test") -> GameState:
	var s := GameState.new(seed_str)
	s.reset()
	s.money = 245000.0
	s.action_points = 6
	_created.append(s)
	return s

func after_each() -> void:
	# GameState is a Node that spawns doom_system/risk_system Nodes -- free them so the fast
	# gate doesn't accumulate orphans (same cleanup as test_finance_engine).
	for s in _created:
		if not is_instance_valid(s):
			continue
		if s.doom_system != null and is_instance_valid(s.doom_system):
			s.doom_system.free()
		if ("risk_system" in s) and s.risk_system != null and is_instance_valid(s.risk_system):
			s.risk_system.free()
		s.free()
	_created.clear()

func _rng(seed_str: String = "office-test") -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = seed_str.hash()
	return r

func _ctx(state) -> Dictionary:
	return FinanceEngine.context_from_state(state)

func _fill_desks(state: GameState, n: int) -> void:
	for i in range(n):
		var r := Researcher.new("safety")
		r.generate_random(state.rng)
		state.add_researcher(r)

# ---- Content + the render/sim boundary (ADR-0018) --------------------------------

func test_offices_data_defines_a_start_and_exactly_three_lease_options() -> void:
	assert_false(Office.start_office().is_empty(), "offices.json must define the tier-0 start")
	assert_eq(Office.lease_options().size(), 3,
		"Pip's ruling: THREE offices to choose from at the first-lease decision")

func test_every_lease_option_is_tier_one_not_a_separate_tier_ladder() -> void:
	for opt in Office.lease_options():
		assert_eq(int(opt["tier"]), 1,
			"3 OPTIONS at the tier-1 decision, not 3 tiers total (R3A_CRIB disambiguation)")

func test_lease_options_differ_in_floorplan_size_rent_and_cap() -> void:
	var caps := {}
	var rents := {}
	var sizes := {}
	for opt in Office.lease_options():
		caps[int(opt["hire_cap"])] = true
		rents[float(opt["rent_per_month"])] = true
		sizes[String(opt["floorplan"]["size_label"])] = true
	assert_eq(caps.size(), 3, "each office offers a different number of desks")
	assert_eq(rents.size(), 3, "each office charges a different rent")
	assert_eq(sizes.size(), 3, "each office has a different floorplan size")

func test_floorplan_is_render_only_and_desk_slots_mirror_hire_cap() -> void:
	# ADR-0018: the render layer reads sim counts; the sim never reads cells. desk_slots is
	# authored to match hire_cap as a courtesy -- the SIM path (Office.hire_cap) reads the
	# state field, so mangling desk_slots must not move the cap.
	for opt in Office.lease_options():
		assert_eq(int(opt["floorplan"]["desk_slots"]), int(opt["hire_cap"]),
			"desk_slots is authored to mirror hire_cap")
	var s := _fresh_state()
	s.office_hire_cap = 5
	assert_eq(Office.hire_cap(s), 5, "the sim cap comes from state, never from floorplan")

# ---- The tier-0 start + the hard hire cap ---------------------------------------

func test_run_starts_in_the_bedroom_unleased() -> void:
	var s := _fresh_state()
	assert_eq(s.office_tier, 0, "every run starts at tier 0 (#791 bedroom/basement)")
	assert_false(s.office_locked, "no lease signed at start")
	assert_eq(s.office_rent_per_month, 0.0, "tier 0 is free")
	assert_eq(s.office_hire_cap, int(Office.start_office()["hire_cap"]),
		"the starting cap comes from offices.json, not a literal")

func test_tier_zero_cap_binds_before_a_working_team_exists() -> void:
	var s := _fresh_state()
	assert_true(Office.has_desk_space(s), "an empty bedroom has room")
	_fill_desks(s, s.office_hire_cap)
	assert_false(Office.has_desk_space(s), "the bedroom cap binds -- this is what forces the lease")

func test_hire_action_refuses_crisply_when_there_is_no_desk() -> void:
	var s := _fresh_state()
	_fill_desks(s, s.office_hire_cap)
	var before := s.get_total_staff()
	var money_before := s.money
	var r := GameActions.execute_action("hire_safety_researcher", s)
	assert_false(bool(r["success"]), "hiring is refused with no desk")
	assert_true(String(r["message"]).begins_with("No desk"),
		"crisp refusal, not a soft debuff (OFFICE_ECONOMY_PROPOSAL 2b)")
	assert_eq(s.get_total_staff(), before, "the refused hire changed no headcount")
	assert_eq(s.money, money_before, "the refused hire spent nothing")

func test_pipeline_offer_stage_refuses_when_there_is_no_desk() -> void:
	var s := _fresh_state()
	_fill_desks(s, s.office_hire_cap)
	var cand := Researcher.new("safety")
	cand.generate_random(s.rng)
	s.hiring.stamp_candidate(cand)
	s.candidate_pool.append(cand)
	var attention_before: int = s.month_plan.attention_spent
	var r: Dictionary = s.hiring.make_offer(s, cand.candidate_id, 100000.0)
	assert_false(bool(r["success"]), "no offer goes out for a desk you do not have")
	assert_eq(s.month_plan.attention_spent, attention_before, "the refusal spends no Attention")

func test_signing_a_lease_raises_the_cap_and_reopens_hiring() -> void:
	var s := _fresh_state()
	_fill_desks(s, s.office_hire_cap)
	assert_false(Office.has_desk_space(s), "capped before the lease")
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	FinanceEngine.accept_offer(offers[1], s)  # the walk-up
	assert_true(Office.has_desk_space(s), "the lease unlocks more hires (#791 small-now)")

# ---- The lease as a FinanceEngine instrument family ------------------------------

func test_lease_menu_is_always_three_and_carries_offer_shape() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	assert_eq(offers.size(), 3, "the first-lease decision is a fixed 3-way choice")
	for o in offers:
		assert_eq(String(o["factory"]), "lease", "lease is its own instrument family")
		assert_true(o.has("expiry_turn"), "standing-offer expiry, same as financing (ADR-0012)")
		assert_true(FinanceEngine.offer_live(o, 0), "a fresh quote is live at the turn it was minted")
		assert_eq(float(o["principal"]), 0.0, "a lease hands you no cash")

func test_lease_offers_are_deterministic_for_a_seed() -> void:
	var s := _fresh_state()
	var a: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng("same"))
	var b: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng("same"))
	for i in range(a.size()):
		assert_eq(float(a[i]["deposit"]), float(b[i]["deposit"]), "same seed -> same terms (WS-0)")

func test_better_finance_reputation_relieves_the_deposit() -> void:
	var s := _fresh_state()
	var lo: Array = FinanceEngine.generate_lease_offers(
		FinanceEngine.context_from_state(s).merged({"finance_rep": 5.0}, true), _rng())
	var hi: Array = FinanceEngine.generate_lease_offers(
		FinanceEngine.context_from_state(s).merged({"finance_rep": 95.0}, true), _rng())
	assert_lt(float(hi[0]["deposit"]), float(lo[0]["deposit"]),
		"a landlord who trusts you asks for less up front (same rep-relief thesis as price())")

func test_signing_charges_deposit_plus_fitout_and_sets_the_office() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	var offer: Dictionary = offers[0]
	var expected: float = float(offer["deposit"]) + float(offer["fitout"])
	var before := s.money
	var r: Dictionary = FinanceEngine.accept_offer(offer, s)
	assert_true(bool(r["success"]), "the sign succeeds when affordable")
	assert_almost_eq(s.money, before - expected, 0.01, "deposit + fitout is the forced early spend (#791)")
	assert_eq(s.office_id, String(offer["option_id"]), "the signed office is the one chosen")
	assert_eq(s.office_hire_cap, int(offer["hire_cap"]), "the quoted cap is the cap you get")
	assert_eq(s.office_rent_per_month, float(offer["rent_per_month"]), "the quoted rent is the rent you owe")

func test_signing_is_refused_when_the_upfront_is_unaffordable() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	s.money = 10.0
	var r: Dictionary = FinanceEngine.accept_offer(offers[2], s)
	assert_false(bool(r["success"]), "cannot sign what you cannot pay for")
	assert_false(s.office_locked, "a refused sign leaves you in the bedroom")

# ---- Lock-in (v1 has no moving mechanic) ----------------------------------------

func test_signing_locks_the_choice_in() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	FinanceEngine.accept_offer(offers[0], s)
	assert_true(s.office_locked, "signing locks the office (Pip: players locked in for now)")
	var second: Dictionary = FinanceEngine.accept_offer(offers[1], s)
	assert_false(bool(second["success"]), "no second lease -- moving is not possible yet")
	assert_eq(s.office_id, String(offers[0]["option_id"]), "the first choice still stands")

func test_the_action_path_tours_then_signs_and_then_refuses() -> void:
	var s := _fresh_state()
	var early: Dictionary = GameActions.execute_action("sign_lease_walkup_office", s)
	assert_false(bool(early["success"]), "you cannot sign an office you never priced")
	var tour: Dictionary = GameActions.execute_action("tour_offices", s)
	assert_true(bool(tour["success"]), "touring mints the quotes")
	assert_eq(s.lease_offers.size(), 3, "three standing quotes")
	var signed: Dictionary = GameActions.execute_action("sign_lease_walkup_office", s)
	assert_true(bool(signed["success"]), "the chosen office signs")
	assert_eq(s.office_id, "walkup_office", "the action id selects WHICH office")
	assert_eq(s.lease_offers.size(), 0, "signing one retires the whole menu")
	var again: Dictionary = GameActions.execute_action("tour_offices", s)
	assert_false(bool(again["success"]), "no re-touring once locked in")

func test_office_upgrades_is_an_additive_seam_that_ships_empty() -> void:
	var s := _fresh_state()
	assert_eq(s.office_upgrades.size(), 0, "no upgrades authored in v1 -- the array is the seam")
	var r: Dictionary = Office.apply_upgrade(s, "standing_desks")
	assert_false(bool(r["success"]), "the hook refuses honestly rather than fabricating an effect")
	assert_eq(s.office_upgrades.size(), 0, "a refused upgrade adds nothing")

# ---- Rent on the payroll rail ----------------------------------------------------

func test_rent_is_a_noop_before_any_lease_is_signed() -> void:
	var s := _fresh_state()
	var before := s.money
	assert_eq(Office.charge_rent(s), 0.0, "the bedroom is free")
	assert_eq(s.money, before, "an unsigned run is economically unchanged by #791")

func test_rent_deducts_cash_directly_and_mints_no_ledger_entry() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	FinanceEngine.accept_offer(offers[1], s)
	var payables_before: int = s.ledger.entries.size()
	var before := s.money
	var charged: float = Office.charge_rent(s)
	assert_eq(charged, s.office_rent_per_month, "one month of the quoted rent")
	assert_almost_eq(s.money, before - charged, 0.01, "payroll rail: a direct deduction")
	assert_eq(s.ledger.entries.size(), payables_before,
		"rent is NOT a ledger payable -- predictable and non-compounding (rail decision)")

func test_rent_is_attributed_when_it_pushes_the_org_under() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	FinanceEngine.accept_offer(offers[1], s)
	s.money = 10.0
	Office.charge_rent(s)
	var found := false
	for c in s.cause_log:
		if String(c.get("kind", "")) == "office_rent":
			found = true
	assert_true(found, "EE-8: a rent charge that sinks you is on the attribution trail")

# ---- Save/load round-trip --------------------------------------------------------

func test_office_state_round_trips_through_save() -> void:
	var s := _fresh_state()
	var offers: Array = FinanceEngine.generate_lease_offers(_ctx(s), _rng())
	FinanceEngine.accept_offer(offers[2], s)
	var restored := _fresh_state("restore-target")
	restored.from_dict(s.to_dict())
	assert_eq(restored.office_id, s.office_id, "the signed office survives save/load")
	assert_eq(restored.office_hire_cap, s.office_hire_cap, "so does the cap")
	assert_eq(restored.office_rent_per_month, s.office_rent_per_month, "and the rent")
	assert_true(restored.office_locked, "and the lock-in")

func test_a_pre_office_save_loads_into_the_bedroom() -> void:
	var s := _fresh_state()
	s.from_dict({"money": 1000.0})  # a save with no office keys at all
	assert_eq(s.office_tier, 0, "old saves land at tier 0 rather than in an undefined office")
	assert_false(s.office_locked, "and unlocked")

# ---- Scouting stubs --------------------------------------------------------------

func test_all_three_scouting_actions_are_real_selectable_actions() -> void:
	for id in ["scout_read", "scout_meetups", "scout_shitpost"]:
		assert_false(GameActions.get_action_by_id(id).is_empty(),
			"%s resolves through the normal action lookup" % id)

func test_scout_read_moves_research_only() -> void:
	var s := _fresh_state()
	var rep_before := s.reputation
	var research_before := s.research
	var r := GameActions.execute_action("scout_read", s)
	assert_true(bool(r["success"]), "reading executes")
	assert_gt(s.research, research_before, "reading advances the work")
	assert_eq(s.reputation, rep_before, "nobody noticed -- reading is invisible")

func test_scout_meetups_raises_standing_and_can_surface_one_lead() -> void:
	var s := _fresh_state()
	var rep_before := s.reputation
	var pool_before := s.candidate_pool.size()
	var r := GameActions.execute_action("scout_meetups", s)
	assert_true(bool(r["success"]), "meetups execute")
	assert_gt(s.reputation, rep_before, "people remember you")
	if s.candidate_pool.size() > pool_before:
		assert_true(String(r["message"]).contains("candidate pool"),
			"the message names the lead ONLY when a lead actually landed")

func test_scout_shitpost_trades_reputation_for_hype() -> void:
	var s := _fresh_state()
	var rep_before := s.reputation
	var hype_before := s.hype
	GameActions.execute_action("scout_shitpost", s)
	assert_gt(s.hype, hype_before, "hype is a real field the finance engine already prices")
	assert_lt(s.reputation, rep_before, "loud costs you standing with careful people")

func test_hype_feeds_the_finance_engine_pricing_context() -> void:
	var s := _fresh_state()
	GameActions.execute_action("scout_shitpost", s)
	assert_eq(float(FinanceEngine.context_from_state(s)["hype"]), s.hype,
		"the shitpost writes into the same hype the instrument availability gates read")

# ---- The onboarding -> scouting handoff ------------------------------------------

func test_cold_open_handoff_points_at_an_active_scouting_choice() -> void:
	var scene := load("res://scripts/ui/cold_open_sequence.gd")
	assert_eq(scene.HANDOFF_ACTION_ID, "scouting",
		"the cold-open's final beat hands over a scouting choice, not a narrative line (#811)")
	assert_false(GameActions.get_action_by_id(scene.HANDOFF_ACTION_ID).is_empty(),
		"and the thing it hands over is a REAL action the player can select")

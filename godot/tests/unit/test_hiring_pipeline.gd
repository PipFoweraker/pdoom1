extends GutTest
## Phase B hiring pipeline: source -> interview -> offer -> onboard (the fishing-line).
## Spec: docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md "Phase B". Every stage is an
## Attention-gated, duration-bearing action (ADR-0009); the whole thing is deterministic
## (WS-0) and round-trips through save/load (L7).

const AdvertiseFloor := 8000.0


func _new_state(seed_str: String = "phaseB") -> GameState:
	var s := GameState.new(seed_str)
	# GameState.new -> reset() opens the first month with the full Attention grant, so
	# month_plan.available() is the per-month budget (20). Plenty for the pipeline stages.
	s.turn = 1
	return s


func _make_candidate(state: GameState, spec: String, skill: int, expectation: float, appetites: Dictionary = {}) -> Researcher:
	"""A hand-built candidate placed in the pool (id stamped by add_candidate)."""
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
	"""Simulate `ticks` resolution ticks passing, resolving due pipeline jobs each tick
	(mirrors what MonthController.advance_tick does for the live game)."""
	for i in range(ticks):
		state.turn += 1
		state.hiring.on_tick(state)


# --- SOURCE ------------------------------------------------------------------

func test_advertise_launches_a_campaign_and_spends_money_and_attention():
	var s := _new_state()
	var money0: float = s.money
	var att0: int = s.month_plan.available()
	var r := s.hiring.advertise(s)
	assert_true(r.get("success", false), "advertise succeeds with funds + attention")
	assert_eq(s.hiring.campaigns.size(), 1, "a campaign is created")
	assert_lt(s.money, money0, "money was spent on the ad")
	assert_lt(s.month_plan.available(), att0, "attention was spent on the ad")


func test_advertise_trickles_candidates_over_months():
	# The trickle MECHANISM: inject a guaranteed campaign (per_month_min=1) so the assertion
	# is seed-independent, then run its boundaries. Each boundary spawns >=1 candidate (until
	# the pool caps) and the campaign expires after months_remaining.
	var s := _new_state("advertise_trickle")
	s.candidate_pool.clear()
	s.hiring.campaigns.append({"months_remaining": 2, "per_month_min": 1, "per_month_max": 2})
	var total_hits := 0
	for m in range(3):
		var ev := s.hiring.on_month_boundary(s)
		for e in ev:
			if String(e.get("kind", "")) == "advertise_hit":
				total_hits += 1
	assert_gt(total_hits, 0, "the campaign trickled candidates into the pool over its run")
	assert_gt(s.candidate_pool.size(), 0, "candidates actually landed in the pool")
	assert_eq(s.hiring.campaigns.size(), 0, "the campaign expired after months_remaining")


func test_advertise_action_configures_a_balance_driven_campaign():
	# The public advertise() wires the campaign from the Balance surface.
	var s := _new_state("advertise_cfg")
	s.hiring.advertise(s)
	assert_eq(s.hiring.campaigns.size(), 1, "advertise created a campaign")
	assert_eq(int(s.hiring.campaigns[0]["months_remaining"]), Balance.inum("hiring.advertise.campaign_months", 3),
		"campaign length comes from Balance")


func test_connections_costs_reputation_and_yields_prevetted_on_success():
	var s := _new_state("connections_seed")
	s.reputation = 1000.0  # ample standing: success chance sits at the cap (0.95)
	s.candidate_pool.clear()
	var rep0: float = s.reputation
	# Launch several attempts so at least one lands (0.05^N miss is negligible; deterministic
	# for the fixed seed). Each spends its own reputation + attention.
	var launched := 0
	for i in range(6):
		if s.hiring.use_connections(s).get("success", false):
			launched += 1
	assert_gt(launched, 0, "connections launches with standing + attention")
	assert_lt(s.reputation, rep0, "each favor cost reputation")
	# Resolve the short connections jobs.
	_advance_and_tick(s, 3)
	assert_gt(s.candidate_pool.size(), 0, "at least one pre-vetted lead surfaced")
	# Every connections lead is pre-vetted (skill + comp already known).
	for c in s.candidate_pool:
		assert_eq(c.reveal_level, Researcher.REVEAL_SKILL,
			"connections lead is pre-vetted (reveal = SKILL)")


func test_two_sourcing_channels_are_mechanically_distinct():
	# Advertise spends MONEY and leaves an unvetted (reveal 0) trickle; connections spends
	# REPUTATION for a pre-vetted (reveal 1) lead. Assert the cost sources differ.
	var s := _new_state("channels")
	var money0: float = s.money
	var rep0: float = s.reputation
	s.hiring.advertise(s)
	assert_lt(s.money, money0, "advertise spends money")
	assert_almost_eq(s.reputation, rep0 + Balance.num("hiring.advertise.reputation_gain", 1.0), 0.001,
		"advertise nudges reputation UP (discovery), not down")
	var rep1: float = s.reputation
	s.hiring.use_connections(s)
	assert_lt(s.reputation, rep1, "connections spends reputation (a favor)")


# --- INTERVIEW ---------------------------------------------------------------

func test_interview_raises_reveal_after_its_duration():
	var s := _new_state("interview")
	var c := _make_candidate(s, "safety", 6, 60000.0)
	assert_eq(c.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "starts uninterviewed")
	var r := s.hiring.launch_interview(s, c.candidate_id)
	assert_true(r.get("success", false), "interview scheduled")
	# Not resolved yet (duration): reveal unchanged mid-flight.
	assert_eq(c.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "reveal unchanged before the duration elapses")
	_advance_and_tick(s, Balance.inum("hiring.interview.duration_ticks", 3))
	assert_eq(c.reveal_level, Researcher.REVEAL_SKILL, "interview revealed the next layer")


func test_interview_requires_attention():
	var s := _new_state("interview_att")
	var c := _make_candidate(s, "safety", 6, 60000.0)
	# Drain all attention.
	s.month_plan.spend_attention(s.month_plan.available())
	var r := s.hiring.launch_interview(s, c.candidate_id)
	assert_false(r.get("success", false), "no attention -> interview fails")


# --- OFFER + NEGOTIATE -------------------------------------------------------

func test_offer_in_range_is_accepted_and_employs():
	var s := _new_state("offer_accept")
	var c := _make_candidate(s, "safety", 6, 60000.0, {"money": 0.5})
	var floor: float = s.hiring.self_worth_floor(c, [])
	var r := s.hiring.make_offer(s, c.candidate_id, floor + 1000.0, [])
	assert_true(r.get("success", false), "offer goes out")
	assert_eq(c.hire_state, Researcher.HireState.OFFERED, "candidate is now OFFERED")
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	assert_eq(c.hire_state, Researcher.HireState.EMPLOYED, "in-range offer accepted -> employed")
	assert_true(s.researchers.has(c), "hire joined the team")
	assert_false(s.candidate_pool.has(c), "and left the pool")
	assert_false(c.onboarded, "a pipeline hire starts un-onboarded (not yet productive)")


func test_offer_below_floor_risks_rejection_or_resentment():
	# A hard lowball never cleanly accepts: it either bounces back to the pool or is taken
	# resentfully (a loyalty debt). Assert the outcome is one of those two.
	var s := _new_state("offer_lowball")
	var c := _make_candidate(s, "safety", 6, 60000.0, {"money": 0.9})
	var floor: float = s.hiring.self_worth_floor(c, [])
	s.hiring.make_offer(s, c.candidate_id, floor * 0.4, [])  # well below the floor
	var ledger0: int = s.ledger.entries.size()
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	var events: Array = s.hiring.last_events
	var outcome := ""
	for e in events:
		if String(e.get("kind", "")).begins_with("offer_"):
			outcome = String(e.get("kind", ""))
	assert_true(outcome == "offer_rejected" or outcome == "offer_resentful_accept",
		"lowball resolves as rejection or resentful accept (got '%s')" % outcome)
	if outcome == "offer_rejected":
		assert_eq(c.hire_state, Researcher.HireState.CANDIDATE_IN_POOL, "declined -> back in the pool")
	else:
		assert_eq(c.hire_state, Researcher.HireState.EMPLOYED, "resentful accept -> employed")
		assert_gt(s.ledger.entries.size(), ledger0, "resentment minted a loyalty-debt ledger entry")


func test_first_authorship_promise_buys_the_floor_down_and_mints_a_ledger_entry():
	# A prestige-hungry candidate takes less cash for a first-authorship promise; the promise
	# mints a ledger obligation (ADR-0003).
	var s := _new_state("promise")
	var c := _make_candidate(s, "safety", 7, 80000.0, {"prestige": 1.0, "money": 0.0})
	var bare_floor: float = s.hiring.self_worth_floor(c, [])
	var promised_floor: float = s.hiring.self_worth_floor(c, ["first_authorship"])
	assert_lt(promised_floor, bare_floor, "the promise lowers the acceptance floor")
	# Offer BELOW the bare floor but at/above the promised floor -> only the promise makes it land.
	var cash: float = promised_floor + 500.0
	assert_lt(cash, bare_floor, "the cash alone would not have sufficed")
	var ledger0: int = s.ledger.entries.size()
	s.hiring.make_offer(s, c.candidate_id, cash, ["first_authorship"])
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	assert_eq(c.hire_state, Researcher.HireState.EMPLOYED, "promise carried the offer to acceptance")
	assert_gt(s.ledger.entries.size(), ledger0, "the promise minted a ledger entry")
	var found_promise := false
	for e in s.ledger.entries:
		if String(e.source).begins_with("promise:first_authorship"):
			found_promise = true
	assert_true(found_promise, "the minted entry is the first-authorship promise")


func test_negotiation_read_narrows_with_a_recruiter():
	var s := _new_state("read")
	var c := _make_candidate(s, "safety", 6, 60000.0)
	var no_read := s.hiring.negotiation_read(s, c, [])
	assert_false(no_read.get("has_recruiter", true), "solo founder gets only a wide guess")
	# Add a senior, onboarded employee to act as the recruiter.
	var recruiter := Researcher.new("safety")
	recruiter.skill_level = 8
	recruiter.onboarded = true
	s.add_researcher(recruiter)
	var read := s.hiring.negotiation_read(s, c, [])
	assert_true(read.get("has_recruiter", false), "a recruiter sharpens the read")
	var wide: float = float(no_read["high"]) - float(no_read["low"])
	var tight: float = float(read["high"]) - float(read["low"])
	assert_lt(tight, wide, "the recruiter read is a narrower band")


# --- ONBOARD -----------------------------------------------------------------

func test_onboarding_checklist_gates_productivity():
	var s := _new_state("onboard")
	var c := _make_candidate(s, "safety", 6, 60000.0, {"money": 0.3})
	# Employ via an in-range offer.
	var floor: float = s.hiring.self_worth_floor(c, [])
	s.hiring.make_offer(s, c.candidate_id, floor + 2000.0, [])
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	assert_false(c.onboarded, "starts un-onboarded")
	var prod_before: float = c.get_effective_productivity()
	# Work the hard checklist (laptop + visa if needed).
	for item in s.hiring.onboarding_required(c):
		var res := s.hiring.onboard_step(s, c.candidate_id, item)
		assert_true(res.get("success", false), "onboard step '%s' applied" % item)
	assert_true(c.onboarded, "hard checklist cleared -> onboarded")
	var prod_after: float = c.get_effective_productivity()
	assert_gt(prod_after, prod_before, "onboarding restored productivity")


func test_skipping_mentoring_debuffs_and_arms_attrition():
	var s := _new_state("skimp")
	var c := _make_candidate(s, "safety", 6, 60000.0)
	var floor: float = s.hiring.self_worth_floor(c, [])
	s.hiring.make_offer(s, c.candidate_id, floor + 2000.0, [])
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	s.hiring.onboard_step(s, c.candidate_id, "laptop")
	if c.needs_visa:
		s.hiring.onboard_step(s, c.candidate_id, "visa")
	assert_true(c.onboarded, "productive after the hard checklist")
	var full_prod: float = c.get_effective_productivity()
	s.hiring.skip_mentoring(s, c.candidate_id)
	assert_true(c.mentoring_skipped, "mentoring marked skipped")
	assert_lt(c.get_effective_productivity(), full_prod, "skimping mentoring is a lasting debuff")


# --- DETERMINISM + SAVE/LOAD -------------------------------------------------

func test_pipeline_is_deterministic():
	var a := _run_scripted(_new_state("determinism_x"))
	var b := _run_scripted(_new_state("determinism_x"))
	assert_eq(a, b, "same seed + same pipeline script -> identical outcome")


func _run_scripted(s: GameState) -> String:
	# A fixed script exercising each channel; the resulting pool/team signature is the fingerprint.
	s.candidate_pool.clear()
	s.hiring.advertise(s)
	s.hiring.use_connections(s)
	for m in range(3):
		s.hiring.on_month_boundary(s)
		_advance_and_tick(s, 3)
	var names: Array = []
	for c in s.candidate_pool:
		names.append(c.researcher_name)
	names.sort()
	return "%d|%s" % [s.hiring.next_serial, ",".join(names)]


## Integration: drive the pipeline through the REAL month loop (action-id -> execute_turn ->
## MonthController tick hooks), synchronously via advance_tick (the same call the async
## playback wraps). Proves the wiring, not just the direct HiringPipeline API.
func test_pipeline_runs_through_the_real_month_loop():
	var GameManagerScript = load("res://scripts/game_manager.gd")
	var gm = GameManagerScript.new()
	add_child_autofree(gm)
	gm.start_new_game("hiring-integration")
	var st = gm.state
	# A known candidate to interview.
	var c := Researcher.new("safety")
	c.skill_level = 6
	st.candidate_pool.clear()
	st.add_candidate(c)
	var cid: String = c.candidate_id

	# Queue the SOURCE + INTERVIEW stage actions as this month's plan; execute the open plan
	# turn (what end_month does first) -> the action-ids route to state.hiring.
	st.queued_actions.append("advertise")
	st.queued_actions.append("interview_next")
	gm.turn_manager.execute_turn()
	assert_eq(st.hiring.campaigns.size(), 1, "advertise ran through the action path")
	assert_gt(st.hiring.jobs.size(), 0, "interview_next scheduled a job through the action path")
	assert_eq(c.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "interview hasn't resolved yet (duration)")

	# Play the month out tick-by-tick (advance_tick is synchronous; the async loop just paces
	# it). Clamp doom so the short run survives, and auto-skip any response windows.
	var guard := 0
	while guard < 30:
		guard += 1
		st.doom = 5.0
		if st.doom_system != null:
			st.doom_system.current_doom = 5.0
		if gm.month_controller.is_paused():
			gm.month_controller.skip_current_window()
			continue
		var r: Dictionary = gm.month_controller.advance_tick()
		if String(r.get("status", "")) == "month_open":
			break
		if st.game_over:
			break
	# The interview job resolved via the MonthController on_tick hook.
	assert_gt(c.reveal_level, Researcher.REVEAL_UNINTERVIEWED,
		"the interview resolved through the real month loop (reveal rose)")


func test_save_load_round_trips_pipeline_state():
	var s := _new_state("saveload")
	# Seed some durable pipeline state: a live campaign, an in-flight interview job, and an
	# employed-but-onboarding hire.
	s.hiring.advertise(s)
	var c := _make_candidate(s, "safety", 6, 60000.0)
	s.hiring.launch_interview(s, c.candidate_id)
	var floor: float = s.hiring.self_worth_floor(c, [])
	# Employ a second candidate mid-onboard.
	var h := Researcher.new("alignment")
	h.skill_level = 5
	s.add_candidate(h)
	s.hiring.make_offer(s, h.candidate_id, s.hiring.self_worth_floor(h, []) + 1000.0, [])
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	s.hiring.onboard_step(s, h.candidate_id, "laptop")

	var blob := JSON.stringify(s.to_dict())
	var parsed = JSON.parse_string(blob)
	assert_not_null(parsed, "state serializes to JSON")

	var s2 := GameState.new("saveload_reload")
	s2.from_dict(parsed)
	assert_eq(s2.hiring.next_serial, s.hiring.next_serial, "id serial round-trips")
	assert_eq(s2.hiring.campaigns.size(), s.hiring.campaigns.size(), "campaigns round-trip")
	assert_eq(s2.hiring.jobs.size(), s.hiring.jobs.size(), "in-flight jobs round-trip")
	# The onboarding hire's flags survived.
	var h2: Researcher = null
	for r in s2.researchers:
		if r.candidate_id == h.candidate_id:
			h2 = r
	assert_not_null(h2, "the onboarding hire round-tripped")
	if h2 != null:
		assert_eq(h2.laptop_done, h.laptop_done, "laptop_done round-trips")
		assert_eq(h2.onboarded, h.onboarded, "onboarded flag round-trips")
		assert_eq(h2.needs_visa, h.needs_visa, "needs_visa round-trips")

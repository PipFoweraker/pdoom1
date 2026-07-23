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


func test_ad_campaign_response_surfaces_a_player_feed_notification():
	# The ad trickle used to be SILENT. It now emits a player-facing FEED notification (the
	# established readable/no-decision channel) via the MonthController when a campaign sources
	# a candidate at a month boundary. Drive the real boundary path (MonthController), not the
	# pipeline in isolation, to prove the wiring.
	var s := _new_state("ad_feed_seed")
	var mc := MonthController.new(s, null)  # null tm: exercise the boundary/dispatch path only
	s.candidate_pool.clear()
	# A guaranteed campaign (per_month_min=1) so the boundary sources >=1 candidate seed-independently.
	s.hiring.campaigns.append({"months_remaining": 2, "per_month_min": 1, "per_month_max": 2})
	var feed0: int = mc.feed_log.size()
	s.turn = 40  # jump into a later calendar month so advance_tick crosses a boundary
	mc.advance_tick()
	assert_gt(mc.feed_log.size(), feed0, "the ad campaign response surfaced a feed notification")
	var found := false
	for item in mc.feed_log:
		var ev: Dictionary = item.get("event", {})
		if String(ev.get("id", "")) == "hiring_ad_response":
			found = true
			assert_eq(EventTiers.tier_of(ev), EventTiers.TIER_FEED, "the notification is a feed-tier item")
			assert_true(String(ev.get("message", "")).to_lower().contains("ad campaign"),
				"the message tells the player their ad campaign paid off")
	assert_true(found, "an ad-response feed notification was emitted when the campaign sourced a candidate")
	# And no notification fires on a boundary with no campaign activity (stays silent).
	var mc2 := MonthController.new(GameState.new("ad_feed_quiet"), null)
	mc2.state.candidate_pool.clear()
	mc2.state.hiring.campaigns.clear()
	var quiet0: int = mc2.feed_log.size()
	mc2.state.turn = 40
	mc2.advance_tick()
	for item in mc2.feed_log:
		assert_ne(String((item.get("event", {}) as Dictionary).get("id", "")), "hiring_ad_response",
			"no ad-response notification without a live campaign")
	assert_eq(mc2.feed_log.size(), quiet0, "a quiet boundary stays silent")


func test_ad_campaign_response_batches_multiple_arrivals():
	# Several candidates landing the same month collapse into ONE pluralized feed line.
	var s := _new_state("ad_feed_batch")
	var mc := MonthController.new(s, null)
	s.candidate_pool.clear()
	# per_month_min == per_month_max == 3 -> exactly three arrivals this boundary.
	s.hiring.campaigns.append({"months_remaining": 1, "per_month_min": 3, "per_month_max": 3})
	s.turn = 40
	mc.advance_tick()
	var ad_items := 0
	var count_field := 0
	for item in mc.feed_log:
		var ev: Dictionary = item.get("event", {})
		if String(ev.get("id", "")) == "hiring_ad_response":
			ad_items += 1
			count_field = int(ev.get("count", 0))
	assert_eq(ad_items, 1, "multiple arrivals batch into a single feed line")
	assert_eq(count_field, 3, "the batched line reports all three arrivals")


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
	# #789: the hard checklist grew (laptop -> [visa ->] systems -> meet people).
	for item in s.hiring.onboarding_required(c):
		s.hiring.onboard_step(s, c.candidate_id, item)
	assert_true(c.onboarded, "productive after the hard checklist")
	var full_prod: float = c.get_effective_productivity()
	s.hiring.skip_mentoring(s, c.candidate_id)
	assert_true(c.mentoring_skipped, "mentoring marked skipped")
	assert_lt(c.get_effective_productivity(), full_prod, "skimping mentoring is a lasting debuff")


# --- #789 THE HIRING STITCH --------------------------------------------------
# Accept-prompt cards (hard-pause windows, FIFO), explicit reserve-vs-cannibalize
# source choice, interview schedule->happen surfacing. Spec:
# docs/game-design/BUILD_BRIEF_789_HIRING_STITCH.md + Pip's rulings on issue #789.


func _employ_pipeline_hire(s: GameState) -> Researcher:
	"""Employ one deterministic pipeline hire (clean accept, no visa) via an in-range
	offer resolved through on_tick. Leaves the accept event in s.hiring.last_events."""
	var c := _make_candidate(s, "safety", 6, 60000.0, {"money": 0.5})
	c.needs_visa = false  # deterministic checklist for the assertions
	c.visa_done = true
	var floor: float = s.hiring.self_worth_floor(c, [])
	s.hiring.make_offer(s, c.candidate_id, floor + 2000.0, [])
	_advance_and_tick(s, Balance.inum("hiring.offer.duration_ticks", 2))
	return c


func _paused_on_accept(s: GameState, mc: MonthController) -> Researcher:
	"""Drive an offer to acceptance through the REAL MonthController tick so the #789
	prompt cards queue and playback pauses. Returns the hire."""
	var c := _make_candidate(s, "safety", 6, 60000.0, {"money": 0.5})
	c.needs_visa = false
	c.visa_done = true
	var floor: float = s.hiring.self_worth_floor(c, [])
	s.hiring.make_offer(s, c.candidate_id, floor + 2000.0, [])
	s.turn = 5  # past resolves_on_turn, still inside the first calendar month
	mc.advance_tick()
	return c


func test_accept_event_carries_onboard_projection():
	# The offer_accepted event now carries candidate_id + the onboarding projection, so
	# the accept-prompt can be built without re-deriving pipeline state.
	var s := _new_state("stitch_accept")
	var c := _employ_pipeline_hire(s)
	var ev := {}
	for e in s.hiring.last_events:
		if String(e.get("kind", "")) == "offer_accepted":
			ev = e
	assert_false(ev.is_empty(), "an offer_accepted event was emitted on resolution")
	assert_eq(String(ev.get("candidate_id", "")), c.candidate_id, "the event names the candidate id")
	assert_eq(int(ev.get("onboard_attention", -1)), s.hiring.hard_checklist_attention(c),
		"the event carries the hard-checklist Attention projection")


func test_hard_checklist_attention_sums_steps_and_excludes_mentoring():
	var s := _new_state("stitch_sum")
	var c := _employ_pipeline_hire(s)
	var h = s.hiring
	var expected: int = h.item_attention("laptop") + h.item_attention("systems") + h.item_attention("meet_people")
	assert_eq(h.hard_checklist_attention(c), expected,
		"hard checklist = laptop + systems + meet_people when no visa is needed")
	assert_false(h.remaining_hard_items(c).has("mentoring"), "mentoring is never a hard item")
	c.needs_visa = true
	c.visa_done = false
	assert_eq(h.hard_checklist_attention(c), expected + h.item_attention("visa"),
		"a needed visa adds its Attention to the projection")


func test_systems_step_requires_the_laptop_first():
	var s := _new_state("stitch_systems")
	var c := _employ_pipeline_hire(s)
	var r := s.hiring.onboard_step(s, c.candidate_id, "systems")
	assert_false(r.get("success", true), "systems onboarding refused before the laptop exists")
	s.hiring.onboard_step(s, c.candidate_id, "laptop")
	assert_true(s.hiring.onboard_step(s, c.candidate_id, "systems").get("success", false),
		"systems onboarding lands once the laptop is issued")


func test_accept_queues_prompt_cards_and_pauses_outside_the_demand_budget():
	var s := _new_state("stitch_cards")
	var mc := MonthController.new(s, null)
	_paused_on_accept(s, mc)
	assert_true(mc.is_paused(), "an accepted offer pauses playback on the prompt cards")
	assert_eq(mc.window_queue.size(), 2, "two cards queue: provision, then optional mentoring (FIFO)")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("kind", "")), "hiring_onboard_prompt",
		"card 1 is the provision prompt")
	assert_eq(String((mc.window_queue[1] as Dictionary).get("kind", "")), "hiring_mentoring_prompt",
		"card 2 is the optional mentoring prompt")
	assert_eq(mc.windows_surfaced_this_month, 0,
		"the player's own follow-up cards do NOT consume the window demand budget")


func test_provision_from_reserve_draws_reserve_and_onboards():
	var s := _new_state("stitch_reserve")
	var mc := MonthController.new(s, null)
	var c := _paused_on_accept(s, mc)
	var hard_att: int = s.hiring.hard_checklist_attention(c)
	var hard_money: float = s.hiring.hard_checklist_money(c)
	s.month_plan.set_reserve(10)
	var money0: float = s.money
	var res := mc.resolve_current_window_option("provision_reserve")
	assert_true(res.get("success", false), "provision_reserve resolves the card")
	assert_eq(String(res.get("payment_source", "")), "reserve", "the Attention came from the crisp reserve")
	assert_true(c.onboarded, "one HANDLE completed the whole hard checklist")
	assert_eq(s.month_plan.reserve_used, hard_att, "reserve drawn = the projected hard-checklist Attention")
	assert_almost_eq(s.money, money0 - hard_money, 0.01, "the money cost was charged exactly once")
	# The mentoring card is next in the FIFO queue.
	assert_true(mc.is_paused(), "the optional mentoring card still awaits its decision")
	var res2 := mc.resolve_current_window_option("mentor_reserve")
	assert_true(res2.get("success", false), "mentoring from reserve resolves")
	assert_true(c.mentoring_done, "mentoring done via the prompt chain")
	assert_eq(s.month_plan.reserve_used, hard_att + s.hiring.item_attention("mentoring"),
		"mentoring drew its own Attention from reserve")
	assert_false(mc.is_paused(), "queue empty -> playback resumes")


func test_provision_by_cannibalizing_then_skip_mentoring():
	var s := _new_state("stitch_cannibal")
	var mc := MonthController.new(s, null)
	var c := _paused_on_accept(s, mc)
	var hard_att: int = s.hiring.hard_checklist_attention(c)
	var spent0: int = s.month_plan.attention_spent
	var res := mc.resolve_current_window_option("provision_cannibalize")
	assert_true(res.get("success", false), "provision_cannibalize resolves with an empty reserve")
	assert_eq(String(res.get("payment_source", "")), "cannibalize", "explicit source choice honored")
	assert_eq(s.month_plan.attention_spent, spent0 + hard_att, "cannibalizing ate available capacity")
	assert_true(c.onboarded, "hire onboarded")
	var res2 := mc.resolve_current_window_option("skip_mentoring")
	assert_true(res2.get("success", false), "skip is a legal, costless choice")
	assert_true(c.mentoring_skipped, "dismissing the mentoring card arms the explicit skip lever")
	assert_false(c.mentoring_done, "skipped, not done")
	assert_false(mc.is_paused(), "playback resumes")


func test_defer_leaves_hire_unonboarded_and_costs_nothing():
	var s := _new_state("stitch_defer")
	var mc := MonthController.new(s, null)
	var c := _paused_on_accept(s, mc)
	var rng_state = s.rng.state
	var res := mc.resolve_current_window_option("defer")
	assert_true(res.get("success", false), "deferring is legal (settle-in-slowly path)")
	assert_false(c.onboarded, "the hire stays un-onboarded (reduced output) until worked from the hiring screen")
	assert_eq(s.month_plan.reserve_used, 0, "no Attention drawn for a defer")
	var res2 := mc.resolve_current_window_option("skip_mentoring")
	assert_true(res2.get("success", false))
	assert_eq(s.rng.state, rng_state, "resolving the prompt cards consumes NO RNG (replay-safe)")
	assert_false(bool(s.hiring.onboarding_status(c)["onboarded"]), "tray query still reports them onboarding")


func test_provision_money_short_keeps_card_open_and_reserve_intact():
	var s := _new_state("stitch_broke")
	var mc := MonthController.new(s, null)
	var c := _paused_on_accept(s, mc)
	s.money = 0.0
	s.month_plan.set_reserve(10)
	var res := mc.resolve_current_window_option("provision_reserve")
	assert_false(res.get("success", true), "the money pre-check fails the choice")
	assert_eq(s.month_plan.reserve_used, 0, "the failed choice did NOT consume any reserve")
	assert_true(mc.is_paused(), "the card stays open, resolvable via another option")
	assert_false(c.onboarded, "no flags flipped")
	var res2 := mc.resolve_current_window_option("defer")
	assert_true(res2.get("success", false), "defer remains available")


func test_interview_resolution_surfaces_feed_item_with_toast():
	# #789 seam 3: interview = schedule -> HAPPEN. The resolution used to be silent; it
	# now lands in the feed (persistent) tagged toast=true (transient notification hint).
	var s := _new_state("stitch_interview")
	var mc := MonthController.new(s, null)
	var c := _make_candidate(s, "safety", 6, 60000.0)
	s.hiring.launch_interview(s, c.candidate_id)
	s.turn = 6  # past the interview duration, same calendar month
	var r := mc.advance_tick()
	var found := false
	for item in mc.feed_log:
		var ev: Dictionary = item.get("event", {})
		if String(ev.get("id", "")) == "hiring_interview_done":
			found = true
			assert_eq(EventTiers.tier_of(ev), EventTiers.TIER_FEED, "surfaced on the feed tier")
			assert_true(bool(ev.get("toast", false)), "tagged for a toast notification")
			assert_true(String(ev.get("message", "")).contains(c.researcher_name), "names the candidate")
	assert_true(found, "the resolved interview surfaced a feed item")
	var in_result := false
	for item in r.get("feed", []):
		if String((item.get("event", {}) as Dictionary).get("id", "")) == "hiring_interview_done":
			in_result = true
	assert_true(in_result, "advance_tick returns the item so the UI layer can toast it")


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


func test_end_month_executes_before_setting_the_implicit_reserve():
	# REGRESSION (#664): end_month() must EXECUTE the plan turn BEFORE it sets the implicit
	# Attention reserve. The reserve is `attention_total - attention_spent`; if it is set
	# first, month_plan.available() is driven to 0 and every execution-time self-charging
	# pipeline action (which spends via month_plan.spend_attention) fails "not enough
	# Attention" despite a full budget. The sibling test above calls execute_turn() DIRECTLY,
	# so it never runs end_month's reserve block and cannot catch this ordering bug.
	var GameManagerScript = load("res://scripts/game_manager.gd")
	var gm = GameManagerScript.new()
	add_child_autofree(gm)
	gm.start_new_game("hiring-reserve-order")
	var st = gm.state
	var full_attention: int = st.month_plan.attention_total
	assert_gt(full_attention, 0, "the month opened with a real Attention budget")

	# Queue a SOURCE action that self-charges Attention at EXECUTION time, then drive the
	# real End-Turn path (end_month), not execute_turn directly.
	st.queued_actions.append("advertise")
	gm.end_month()

	# If the reserve were set before execution, advertise would have been starved and no
	# campaign created. Post-fix: it runs, and the reserve banks only what execution left.
	assert_eq(st.hiring.campaigns.size(), 1,
		"advertise executed through end_month (reserve did NOT starve its Attention)")
	var adv_cost: int = Balance.inum("hiring.advertise.cost_attention", 3)
	assert_eq(st.month_plan.attention_spent, adv_cost,
		"execution charged advertise's Attention exactly once (no double / no starve)")
	assert_eq(st.month_plan.attention_reserved, full_attention - adv_cost,
		"the implicit reserve banked the post-execution remainder")


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

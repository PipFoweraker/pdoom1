extends GutTest
## feat/quirk-skeleton (WS-3 prototype): the quirk layer becomes the LIVE system.
##
## Covers the three sim changes of the skeleton:
##  1. UNIVERSAL QUIRK DOOM -- the quirk doom_mod_add channel routes through the DoomSystem
##     'quirk' stream summed over the WHOLE productive roster (was: one log-only call inside
##     the capabilities arm, so a safety-lane secret_successionist had zero effect).
##     ADR-0015 (stream, not a direct doom write) + ADR-0006 (deterministic sum, no rng).
##  2. APPETITE SATISFACTION -- appetites were priced into offers then never read post-hire.
##     process_turn(rng, lab_context) now runs a deterministic per-turn check (strong hungers
##     vs lab-state proxies) that nudges loyalty. No new rng draws.
##  3. PROMISE KEPT/BROKEN -- ledger promise bills branch on covered vs shortfall and move
##     the NAMED promisee's loyalty (was: unconditional bill, silent lapse).
## Plus the skill-up / tenure-reveal turn-feed surfacing.


func _new_state(seed_str: String) -> GameState:
	var s := GameState.new(seed_str)
	s.turn = 1
	return s


func _employ(state: GameState, spec: String, name: String, skill: int = 5, quirk_id: String = "") -> Researcher:
	var r := Researcher.new(spec, name)
	r.researcher_name = name
	r.skill_level = skill
	r.base_productivity = 0.5 + skill * 0.1
	r.quirk = quirk_id
	r.quirk_known = false
	state.add_researcher(r)
	return r


# ============================================================================
# 1. Universal quirk doom stream
# ============================================================================

func test_quirk_stream_zero_without_quirks():
	var s := _new_state("quirk_stream_zero")
	_employ(s, "safety", "Plain Person")
	var result: Dictionary = s.doom_system.calculate_doom_change(s)
	assert_almost_eq(float(result["sources"].get("quirk", 0.0)), 0.0, 0.000001,
		"a quirk-free roster contributes nothing to the quirk stream")


func test_safety_lane_quirk_carrier_feeds_the_stream():
	# THE fix: a SAFETY researcher's doom quirk now matters. Pre-skeleton, doom_mod_add was
	# only read inside the capabilities-specialization arm (log-only), so this carrier's
	# +0.04 was completely dead.
	var s := _new_state("quirk_stream_safety")
	_employ(s, "safety", "Quiet Successionist", 5, "secret_successionist")
	var expected: float = Balance.num("doom.streams.W_quirk_doom", 0.5) \
		* float(QuirkCatalogue.effect("secret_successionist", "doom_mod_add", 0.0))
	var result: Dictionary = s.doom_system.calculate_doom_change(s)
	assert_almost_eq(float(result["sources"]["quirk"]), expected, 0.000001,
		"a productive safety-lane carrier's doom_mod_add lands in the quirk stream")
	assert_gt(float(result["sources"]["quirk"]), 0.0, "secret_successionist raises the rate")


func test_doom_lowering_quirk_is_negative_relief():
	# The stream is natively SIGNED (like alarm): a true_believer's conviction is genuine
	# relief, exempt from the R2-Q9 v1 hazard clamp.
	var s := _new_state("quirk_stream_relief")
	_employ(s, "capabilities", "Devoted One", 5, "true_believer")
	var result: Dictionary = s.doom_system.calculate_doom_change(s)
	assert_lt(float(result["sources"]["quirk"]), 0.0,
		"true_believer (doom_mod_add -0.04) shows as a negative stream contribution")


func test_quirk_stream_sums_over_whole_roster():
	var s := _new_state("quirk_stream_sum")
	_employ(s, "safety", "A", 5, "secret_successionist")   # +0.04
	_employ(s, "interpretability", "B", 5, "true_believer") # -0.04
	_employ(s, "capabilities", "C", 5, "e_acc_sympathizer") # +0.05
	var w: float = Balance.num("doom.streams.W_quirk_doom", 0.5)
	var expected: float = w * (0.04 - 0.04 + 0.05)
	var result: Dictionary = s.doom_system.calculate_doom_change(s)
	assert_almost_eq(float(result["sources"]["quirk"]), expected, 0.000001,
		"the stream is the deterministic SUM over every productive researcher")


func test_quirk_stream_effect_live_while_hidden():
	# Hidden-but-TRUE (ADR-0004): the stream reads the channel regardless of quirk_known.
	var s := _new_state("quirk_stream_hidden")
	var r := _employ(s, "safety", "Sleeper", 5, "e_acc_sympathizer")
	assert_false(r.quirk_known, "the quirk starts hidden")
	var result: Dictionary = s.doom_system.calculate_doom_change(s)
	assert_gt(float(result["sources"]["quirk"]), 0.0, "the effect is live before the reveal")


# ============================================================================
# 2. Appetite satisfaction (deterministic, gated on a non-empty context)
# ============================================================================

func _hungry(researcher: Researcher, key: String) -> void:
	researcher.appetites[key] = 1.0


func test_empty_context_skips_appetites_entirely():
	# Legacy callers (and every pre-existing test) pass no context -> byte-identical
	# behaviour to the pre-skeleton process_turn.
	var a := Researcher.new("safety", "Control")
	var b := Researcher.new("safety", "Probe")
	for r in [a, b]:
		_hungry(r, "money")
		r.current_salary = r.salary_expectation * 0.5  # starving the money appetite
	a.process_turn(null)
	b.process_turn(null, {})
	assert_eq(a.loyalty, b.loyalty, "empty context == legacy path (no appetite drift)")


func test_starved_money_appetite_bleeds_loyalty():
	var fed := Researcher.new("safety", "Paid Well")
	var starved := Researcher.new("safety", "Paid Badly")
	for r in [fed, starved]:
		_hungry(r, "money")
	starved.current_salary = starved.salary_expectation * 0.9  # below expectation, above the 0.8 base-drift floor
	var ctx := {"compute_per_researcher": 10.0, "papers": 0.0, "reputation": 50.0,
		"roster_size": 1, "junior_count": 0, "doom_rate": 1.0}
	fed.process_turn(null, ctx)
	starved.process_turn(null, ctx)
	assert_lt(starved.loyalty, fed.loyalty,
		"a hungry-for-money hire paid under expectation drifts out vs one paid at rate")


func test_fed_appetites_credit_loyalty_and_net_is_capped():
	var r := Researcher.new("safety", "Well Fed")
	for key in Researcher.APPETITE_KEYS:
		_hungry(r, key)  # all five hungers strong
	# Everything fed: pay at expectation, slack compute, papers, juniors, doom falling.
	var ctx := {"compute_per_researcher": 10.0, "papers": 3.0, "reputation": 70.0,
		"roster_size": 4, "junior_count": 2, "doom_rate": -0.5}
	var before: int = r.loyalty
	var summary: Dictionary = r.process_turn(null, ctx)
	assert_eq(int(summary["appetite_loyalty_delta"]), Researcher.APPETITE_NET_CAP,
		"five fed hungers clamp to the net cap (gentle drift, never a cliff)")
	assert_eq(summary["appetite_starved"].size(), 0, "nothing starved in a flush lab")
	# +1 base salary drift + capped appetite credit
	assert_eq(r.loyalty, before + 1 + Researcher.APPETITE_NET_CAP, "loyalty moved by base + capped appetite drift")


func test_weak_appetites_never_move_loyalty():
	var r := Researcher.new("safety", "Even Keeled")
	for key in Researcher.APPETITE_KEYS:
		r.appetites[key] = Researcher.APPETITE_HUNGRY_THRESHOLD - 0.05  # all below threshold
	var ctx := {"compute_per_researcher": 0.0, "papers": 0.0, "reputation": 0.0,
		"roster_size": 1, "junior_count": 0, "doom_rate": 5.0}  # a maximally starving lab
	var summary: Dictionary = r.process_turn(null, ctx)
	assert_eq(int(summary["appetite_loyalty_delta"]), 0,
		"appetites under the hunger threshold are inert (only STRONG hungers bite)")


func test_mentee_hunger_reads_seniority():
	# A mentee-hungry SENIOR needs juniors; the same hunger on a junior just needs peers.
	var senior := Researcher.new("safety", "Prof")
	senior.skill_level = Researcher.SENIOR_SKILL_LEVEL
	_hungry(senior, "mentees")
	var no_juniors := {"compute_per_researcher": 0.0, "papers": 0.0, "reputation": 0.0,
		"roster_size": 3, "junior_count": 0, "doom_rate": 1.0}
	var summary: Dictionary = senior.process_turn(null, no_juniors)
	assert_has(summary["appetite_starved"], "mentees", "a senior with no juniors is starved")
	var with_juniors := no_juniors.duplicate()
	with_juniors["junior_count"] = 1
	summary = senior.process_turn(null, with_juniors)
	assert_has(summary["appetite_fed"], "mentees", "give them a junior and the hunger feeds")


func test_appetite_check_is_deterministic_and_rng_free():
	# Same inputs -> same outputs, twice; and the check consumes NO rng (ADR-0006): a
	# seeded rng handed to two identical researchers advances identically with or without
	# a context.
	var rng1 := RandomNumberGenerator.new()
	rng1.seed = 12345
	var rng2 := RandomNumberGenerator.new()
	rng2.seed = 12345
	var ctx := {"compute_per_researcher": 10.0, "papers": 1.0, "reputation": 60.0,
		"roster_size": 2, "junior_count": 1, "doom_rate": -0.1}
	var a := Researcher.new("safety", "Twin A")
	var b := Researcher.new("safety", "Twin B")
	_hungry(a, "prestige")
	_hungry(b, "prestige")
	a.process_turn(rng1, ctx)
	b.process_turn(rng2)  # no context
	assert_eq(rng1.state, rng2.state,
		"the appetite check draws NOTHING from the rng stream (replay-safe)")


# ============================================================================
# 3. Promise kept / broken (ledger settlement semantics)
# ============================================================================

func test_kept_paper_promise_credits_the_promisee():
	var s := _new_state("promise_kept_papers")
	var r := _employ(s, "safety", "Alice Chen")
	s.papers = 3.0  # obligation covered
	var e: Ledger.Entry = Ledger.appetite_promise("Alice Chen", "first_authorship")
	e.fuse = 0
	s.ledger.add(e)
	var before: int = r.loyalty
	s.ledger.tick_and_bill(s)
	var credit: int = Balance.inum("ledger.promise.kept_loyalty_credit", 3)
	assert_eq(r.loyalty, before + credit, "a covered promise credits the named promisee")
	assert_true(_has_cause(s, "ledger_promise_kept"), "a promise_kept cause is recorded")
	assert_almost_eq(s.papers, 2.0, 0.001, "money-settlement rules unchanged: the paper is still drawn")


func test_broken_paper_promise_hits_the_promisee():
	var s := _new_state("promise_broken_papers")
	var r := _employ(s, "safety", "Alice Chen")
	s.papers = 0.0  # shortfall -- the first-authorship never materializes
	var e: Ledger.Entry = Ledger.appetite_promise("Alice Chen", "first_authorship")
	e.fuse = 0
	s.ledger.add(e)
	var before: int = r.loyalty
	s.ledger.tick_and_bill(s)
	var hit: int = Balance.inum("ledger.promise.broken_loyalty_hit", 8)
	assert_eq(r.loyalty, before - hit, "the silent lapse is gone -- the promisee takes the hit")
	assert_true(_has_cause(s, "ledger_promise_broken"), "a promise_broken cause is recorded")


func test_governance_promise_kept_and_broken():
	# mission_charter bills governance (principal 6): covered at the start-of-game 50,
	# broken when governance is nearly drained.
	var s := _new_state("promise_gov")
	var r := _employ(s, "alignment", "Bob Kumar")
	var e: Ledger.Entry = Ledger.appetite_promise("Bob Kumar", "mission_charter")
	e.fuse = 0
	s.ledger.add(e)
	var before: int = r.loyalty
	s.ledger.tick_and_bill(s)
	assert_gt(r.loyalty, before, "governance promise covered -> loyalty credit")

	var s2 := _new_state("promise_gov_short")
	var r2 := _employ(s2, "alignment", "Cara Diaz")
	s2.governance = 1.0  # cannot cover the 6-point charter
	var e2: Ledger.Entry = Ledger.appetite_promise("Cara Diaz", "mission_charter")
	e2.fuse = 0
	s2.ledger.add(e2)
	var before2: int = r2.loyalty
	s2.ledger.tick_and_bill(s2)
	assert_lt(r2.loyalty, before2, "governance shortfall -> the promisee's loyalty takes the hit")


func test_promise_to_departed_researcher_is_a_noop():
	# The promisee left before the bill landed: nothing to move, no crash, still settles.
	var s := _new_state("promise_departed")
	s.papers = 3.0
	var e: Ledger.Entry = Ledger.appetite_promise("Ghost Person", "first_authorship")
	e.fuse = 0
	s.ledger.add(e)
	s.ledger.tick_and_bill(s)
	assert_true(e.settled, "the bill settles normally")
	assert_false(_has_cause(s, "ledger_promise_kept"), "no loyalty event for a departed promisee")


func test_non_promise_governance_bills_untouched():
	# The kept/broken branch keys on the promise: source prefix -- ordinary governance
	# entries (staff riders, coinflips) never move roster loyalty.
	var s := _new_state("promise_only")
	var r := _employ(s, "safety", "Dana Ellis")
	var e := Ledger.staff_rider("Dana Ellis")
	e.fuse = 0
	s.ledger.add(e)
	var before: int = r.loyalty
	s.ledger.tick_and_bill(s)
	assert_eq(r.loyalty, before, "a non-promise bill leaves loyalty alone")


func _has_cause(state: GameState, kind: String) -> bool:
	for c in state.cause_log:
		if str(c.kind) == kind:
			return true
	return false


# ============================================================================
# Turn-feed surfacing (skill-ups + tenure quirk reveals)
# ============================================================================

func test_lifecycle_notes_surface_skill_ups_and_reveals():
	# The 5%/turn skill roll used to fire SILENTLY (researcher.gd); now the lifecycle step
	# returns feed notes. Deterministic given the seed: iterate the lifecycle step until
	# both a skill-up and the sponge's tenure reveal (after_turns 10) have narrated.
	var s := _new_state("lifecycle_notes")
	var r := _employ(s, "safety", "Sam Sponge", 3, "sponge")  # skill_growth_mult 2.5 -> 12.5%/turn
	var tm := TurnManager.new(s)
	var saw_skill_up := false
	var saw_reveal := false
	for i in range(120):
		var notes: Array = tm._step_process_researcher_lifecycles()
		for note in notes:
			if String(note).contains("levels up"):
				saw_skill_up = true
			if String(note).contains("Quirk surfaced"):
				saw_reveal = true
		if saw_skill_up and saw_reveal:
			break
	assert_true(saw_skill_up, "a skill-up produces a turn-feed note (no more silent levelling)")
	assert_true(saw_reveal, "the tenure reveal narrates with the catalogue hint")
	assert_true(r.quirk_known, "the sponge quirk is exposed by tenure")
	assert_gt(r.skill_level, 3, "the skill actually grew")
	tm.free()

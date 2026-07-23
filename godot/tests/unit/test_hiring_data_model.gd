extends GutTest
## Phase A hiring data model: hidden-ability layer, reveal-level gating, hire-state
## transitions, appetites, quirk exposure, and save/load round-trip of the new fields.
## Spec: docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md "Phase A".

func _make_seeded() -> Researcher:
	# Deterministic candidate via a seeded RNG (WS-0: no global RNG).
	var rng := RandomNumberGenerator.new()
	rng.seed = 12345
	var r := Researcher.new("safety")
	r.generate_random(rng)
	return r

# --- Appetites --------------------------------------------------------------

func test_default_appetites_are_neutral_and_complete():
	var r := Researcher.new("safety")
	assert_eq(r.appetites.size(), Researcher.APPETITE_KEYS.size(), "All 5 appetite keys present by default")
	for k in Researcher.APPETITE_KEYS:
		assert_true(r.appetites.has(k), "Appetite key present: %s" % k)
		assert_eq(float(r.appetites[k]), 0.0, "Default appetite neutral: %s" % k)

func test_generate_random_populates_appetites_in_range():
	var r := _make_seeded()
	assert_eq(r.appetites.size(), Researcher.APPETITE_KEYS.size())
	for k in Researcher.APPETITE_KEYS:
		var v: float = float(r.appetites[k])
		assert_between(v, 0.0, 1.0, "Appetite %s in [0,1]" % k)
	assert_between(r.loyalty_risk, 0.0, 1.0, "loyalty_risk in [0,1]")

func test_generation_is_deterministic():
	var a := _make_seeded()
	var b := _make_seeded()
	assert_eq(a.appearance_id, b.appearance_id, "Same seed -> same identity")
	assert_eq(a.appetites, b.appetites, "Same seed -> same appetites")
	assert_eq(a.loyalty_risk, b.loyalty_risk, "Same seed -> same loyalty_risk")
	assert_eq(a.quirk, b.quirk, "Same seed -> same quirk")

func test_identity_assigned_and_from_known_pool():
	var r := _make_seeded()
	assert_ne(r.appearance_id, "", "Identity assigned")
	assert_true(r.appearance_id.begins_with("body_"), "Identity from combinatorial pool")

# --- Reveal-level gating ----------------------------------------------------

func test_uninterviewed_hides_skill_appetites_loyalty():
	var r := _make_seeded()
	assert_eq(r.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "Fresh candidate uninterviewed")
	var card := r.get_card_data()
	# Identity + lane + seniority always shown.
	assert_eq(card["name"], r.researcher_name)
	assert_ne(card["seniority_band"], Researcher.HIDDEN_PLACEHOLDER, "Rough seniority shown at reveal 0")
	# Hidden layer masked.
	assert_eq(card["skill_level"], Researcher.HIDDEN_PLACEHOLDER, "Skill hidden at reveal 0")
	assert_eq(card["appetites"], Researcher.HIDDEN_PLACEHOLDER, "Appetites hidden at reveal 0")
	assert_eq(card["loyalty_risk"], Researcher.HIDDEN_PLACEHOLDER, "Loyalty-risk hidden at reveal 0")

func test_reveal_more_progressively_unhides():
	var r := _make_seeded()
	r.reveal_more(1)  # REVEAL_SKILL
	var c1 := r.get_card_data()
	assert_eq(c1["skill_level"], r.skill_level, "Skill revealed at level 1")
	assert_eq(c1["appetites"], Researcher.HIDDEN_PLACEHOLDER, "Appetites still hidden at level 1")

	r.reveal_more(1)  # REVEAL_APPETITES
	var c2 := r.get_card_data()
	assert_true(c2["appetites"] is Dictionary, "Appetites revealed at level 2")
	assert_eq(c2["loyalty_risk"], Researcher.HIDDEN_PLACEHOLDER, "Loyalty-risk still hidden at level 2")

	r.reveal_more(1)  # REVEAL_DEEP
	var c3 := r.get_card_data()
	assert_eq(float(c3["loyalty_risk"]), r.loyalty_risk, "Loyalty-risk revealed at level 3")

func test_reveal_more_clamps_at_max():
	var r := _make_seeded()
	r.reveal_more(99)
	assert_eq(r.reveal_level, Researcher.MAX_REVEAL, "Reveal clamps to MAX_REVEAL")
	assert_eq(r.reveal_more(5), Researcher.MAX_REVEAL, "Cannot exceed MAX_REVEAL")

func test_is_field_revealed_unknown_field_never():
	var r := _make_seeded()
	r.set_reveal_level(Researcher.MAX_REVEAL)
	assert_false(r.is_field_revealed("no_such_field"), "Unknown fields never reveal")

# --- Quirk exposure (independent of interview ladder, A2) --------------------

func test_quirk_hidden_even_when_fully_interviewed():
	var r := Researcher.new("safety")
	r.quirk = "secret_successionist"
	r.set_reveal_level(Researcher.MAX_REVEAL)
	var card := r.get_card_data()
	assert_eq(card["quirk"], Researcher.HIDDEN_PLACEHOLDER, "Quirk stays hidden until exposure, even fully interviewed")

func test_expose_quirk_reveals_it():
	var r := Researcher.new("safety")
	r.quirk = "doom_absolutist"
	r.expose_quirk()
	var card := r.get_card_data()
	assert_eq(card["quirk"], "doom_absolutist", "Exposure event surfaces the quirk")

func test_exposed_absent_quirk_reads_none():
	var r := Researcher.new("safety")  # no quirk
	r.expose_quirk()
	var card := r.get_card_data()
	assert_eq(card["quirk"], "none", "Checked absence reads 'none', not the placeholder")

# --- Hire-state transitions -------------------------------------------------

func test_valid_hire_state_flow():
	var r := Researcher.new("safety")
	assert_eq(r.hire_state, Researcher.HireState.CANDIDATE_IN_POOL, "Starts in pool")
	assert_true(r.transition_hire_state(Researcher.HireState.OFFERED), "pool -> offered ok")
	assert_true(r.transition_hire_state(Researcher.HireState.EMPLOYED), "offered -> employed ok")
	assert_true(r.transition_hire_state(Researcher.HireState.DEPARTED), "employed -> departed ok")

func test_invalid_hire_state_transitions_rejected():
	var r := Researcher.new("safety")
	assert_false(r.transition_hire_state(Researcher.HireState.EMPLOYED), "pool -> employed skips offer")
	assert_eq(r.hire_state, Researcher.HireState.CANDIDATE_IN_POOL, "Rejected transition is a no-op")

func test_departed_is_terminal():
	var r := Researcher.new("safety")
	r.transition_hire_state(Researcher.HireState.OFFERED)
	r.transition_hire_state(Researcher.HireState.EMPLOYED)
	r.transition_hire_state(Researcher.HireState.DEPARTED)
	assert_false(r.transition_hire_state(Researcher.HireState.EMPLOYED), "No resurrection from departed")
	assert_false(r.transition_hire_state(Researcher.HireState.CANDIDATE_IN_POOL), "Departed is terminal")

func test_offer_can_return_to_pool():
	var r := Researcher.new("safety")
	r.transition_hire_state(Researcher.HireState.OFFERED)
	assert_true(r.transition_hire_state(Researcher.HireState.CANDIDATE_IN_POOL), "Declined offer -> back to pool")

# --- Hiring marks employed + fully revealed (backward compat) ----------------

func test_add_researcher_marks_employed_and_revealed():
	var state := GameState.new("test_hire_reveal")
	var r := _make_seeded()
	state.add_researcher(r)
	assert_eq(r.hire_state, Researcher.HireState.EMPLOYED, "Hired -> employed")
	assert_eq(r.reveal_level, Researcher.MAX_REVEAL, "Employed staff fully revealed")
	assert_false(r.quirk_known, "But quirk still hidden until exposure")

func test_starting_candidates_are_uninterviewed():
	var state := GameState.new("test_pool")
	assert_gt(state.candidate_pool.size(), 0, "Pool seeded with candidates")
	for cand in state.candidate_pool:
		assert_eq(cand.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "Pool candidates uninterviewed")
		assert_eq(cand.hire_state, Researcher.HireState.CANDIDATE_IN_POOL, "Pool candidates in pool state")
		assert_ne(cand.appearance_id, "", "Candidate carries an identity")

# --- Turn-0 founding team: exactly four starters, each with a GUARANTEED hidden rider --------

func _starter_has_strong_appetite(cand: Researcher) -> bool:
	for k in Researcher.APPETITE_KEYS:
		if float(cand.appetites.get(k, 0.0)) >= GameState.STARTER_STRONG_APPETITE:
			return true
	return false

func test_starter_pool_is_exactly_four():
	# Pip ruling: the founding team is EXACTLY four "starter pokemon".
	var state := GameState.new("starter_count_seed")
	assert_eq(state.candidate_pool.size(), 4, "the turn-0 founding team is exactly four starters")

func test_each_starter_carries_a_hidden_rider():
	var state := GameState.new("starter_riders_seed")
	assert_eq(state.candidate_pool.size(), 4, "four starters")
	for cand in state.candidate_pool:
		# Rider present: a rare quirk OR a strong appetite.
		assert_true(cand.has_quirk() or _starter_has_strong_appetite(cand),
			"each starter is GUARANTEED a rider (a quirk or a strong appetite)")
		# ...but it starts HIDDEN.
		assert_false(cand.quirk_known, "the quirk rider starts hidden (quirk_known false)")
		assert_eq(cand.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "starter starts at reveal 0")

func test_starter_riders_are_deterministic_from_seed():
	# Same seed -> byte-identical founding team (replay-safe, ADR-0006).
	var a := GameState.new("starter_determinism_seed")
	var b := GameState.new("starter_determinism_seed")
	assert_eq(a.candidate_pool.size(), b.candidate_pool.size(), "same seed -> same starter count")
	for i in range(a.candidate_pool.size()):
		assert_eq(a.candidate_pool[i].quirk, b.candidate_pool[i].quirk, "same seed -> same rider quirk")
		assert_eq(a.candidate_pool[i].appetites, b.candidate_pool[i].appetites, "same seed -> same appetites")
		assert_eq(a.candidate_pool[i].researcher_name, b.candidate_pool[i].researcher_name, "same seed -> same names")

# --- Save / load round-trip of the new fields -------------------------------

func test_researcher_new_fields_round_trip():
	var r := _make_seeded()
	r.reveal_more(2)
	r.quirk = "empire_builder"
	r.quirk_known = true
	r.transition_hire_state(Researcher.HireState.OFFERED)

	# Full JSON hop, mirroring the save/load path (numbers come back as float).
	var json_str := JSON.stringify(r.to_dict())
	var parsed = JSON.parse_string(json_str)
	assert_not_null(parsed, "Round-trips through JSON")

	var r2 := Researcher.new()
	r2.from_dict(parsed)
	assert_eq(r2.appearance_id, r.appearance_id, "appearance_id round-trips")
	assert_eq(r2.reveal_level, r.reveal_level, "reveal_level round-trips")
	assert_eq(r2.hire_state, r.hire_state, "hire_state round-trips")
	assert_eq(r2.quirk, r.quirk, "quirk round-trips")
	assert_eq(r2.quirk_known, r.quirk_known, "quirk_known round-trips")
	assert_almost_eq(r2.loyalty_risk, r.loyalty_risk, 0.0001, "loyalty_risk round-trips")
	for k in Researcher.APPETITE_KEYS:
		assert_almost_eq(float(r2.appetites[k]), float(r.appetites[k]), 0.0001, "appetite %s round-trips" % k)

func test_pre_phase_a_save_loads_with_defaults():
	# A researcher dict WITHOUT the new keys (old save) must load cleanly.
	var legacy := {"name": "Old Hand", "specialization": "safety", "skill_level": 6}
	var r := Researcher.new()
	r.from_dict(legacy)
	assert_eq(r.reveal_level, Researcher.REVEAL_UNINTERVIEWED, "Missing reveal_level -> default")
	assert_eq(r.hire_state, Researcher.HireState.CANDIDATE_IN_POOL, "Missing hire_state -> default")
	assert_eq(r.appetites.size(), Researcher.APPETITE_KEYS.size(), "Missing appetites -> neutral set")

# --- #789 onboarding-chain steps (systems / meet_people + the tunable const) --

func test_789_step_flags_round_trip():
	var r := _make_seeded()
	r.systems_done = true
	r.meet_people_done = true
	var parsed = JSON.parse_string(JSON.stringify(r.to_dict()))
	assert_not_null(parsed, "round-trips through JSON")
	var r2 := Researcher.new()
	r2.from_dict(parsed)
	assert_true(r2.systems_done, "systems_done round-trips")
	assert_true(r2.meet_people_done, "meet_people_done round-trips")

func test_pre_789_save_defaults_new_steps_false():
	# A pre-#789 save (no systems/meet_people keys) loads with the steps still owed.
	var legacy := {"name": "Old Hand", "specialization": "safety", "laptop_done": true}
	var r := Researcher.new()
	r.from_dict(legacy)
	assert_false(r.systems_done, "missing systems_done -> false (step still owed)")
	assert_false(r.meet_people_done, "missing meet_people_done -> false (step still owed)")

func test_789_onboard_attention_const_shape():
	# Guard the tunable const's SHAPE (a renamed key would silently break the
	# item_attention lookups and the hard-checklist projection).
	for k in ["laptop", "systems", "meet_people", "mentoring"]:
		assert_true(HiringPipeline.ONBOARD_ATTENTION.has(k), "ONBOARD_ATTENTION carries '%s'" % k)
		assert_gt(int(HiringPipeline.ONBOARD_ATTENTION[k]), 0, "step '%s' costs real Attention" % k)

func test_789_hard_checklist_includes_new_steps():
	var pipeline := HiringPipeline.new()
	var r := _make_seeded()
	r.needs_visa = false
	var required: Array = pipeline.onboarding_required(r)
	for item in ["laptop", "systems", "meet_people"]:
		assert_true(required.has(item), "hard checklist includes '%s'" % item)
	assert_false(required.has("mentoring"), "mentoring stays optional (soft item)")
	assert_false(required.has("visa"), "no visa for a domestic hire")
	r.needs_visa = true
	assert_true(pipeline.onboarding_required(r).has("visa"), "visa appears for a foreign hire")

# --- Card view --------------------------------------------------------------

func test_card_view_renders_hidden_and_revealed():
	var r := _make_seeded()
	var card := CandidateCard.new()
	add_child_autofree(card)
	card.set_researcher(r)
	# Uninterviewed: card text shows the placeholder for skill.
	assert_true(card._body.text.contains(Researcher.HIDDEN_PLACEHOLDER), "Hidden fields shown as placeholder")
	r.set_reveal_level(Researcher.MAX_REVEAL)
	card.set_researcher(r)
	assert_true(card._body.text.contains("Skill: %d" % r.skill_level), "Revealed skill shown after interview")

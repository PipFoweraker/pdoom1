extends GutTest
## Data-driven researcher QUIRK catalogue (retires the legacy trait system).
## Covers: catalogue loads + is well-formed; deterministic assignment from a seed; the
## effect accessor; tenure/exposure reveal flipping quirk_known; save/load round-trip; and
## that the four founding starters draw their quirk from the catalogue.
## Design: docs/game-design/RESEARCHER_QUIRKS.md. Determinism contract: ADR-0006.

# --- Catalogue loads + shape ------------------------------------------------

func test_catalogue_loads_expected_size():
	var ids := QuirkCatalogue.ids()
	assert_gte(ids.size(), 12, "catalogue has ~12-16 quirks")
	assert_true(QuirkCatalogue.has("runs_hot"), "runs_hot present (reframed workaholic)")
	assert_true(QuirkCatalogue.has("secret_successionist"), "canonical reference quirk present")
	assert_false(QuirkCatalogue.has("workaholic"), "legacy trait id is NOT a quirk")

func test_every_quirk_is_well_formed():
	for id in QuirkCatalogue.ids():
		var d := QuirkCatalogue.get_def(id)
		assert_true(d.has("name") and String(d["name"]) != "", "%s has a name" % id)
		assert_true(d.has("flavour") and String(d["flavour"]) != "", "%s has flavour" % id)
		assert_true(d.get("effects", {}) is Dictionary, "%s has an effects dict" % id)
		assert_false(d.get("effects", {}).is_empty(), "%s has at least one effect channel" % id)
		# reveal fallback must be a positive turn count (guarantees it surfaces in play)
		assert_gt(QuirkCatalogue.reveal_after_turns(id), 0, "%s has a tenure reveal fallback" % id)

func test_effect_accessor_returns_value_or_default():
	# runs_hot self_productivity_mult is 1.20 in the data.
	assert_almost_eq(float(QuirkCatalogue.effect("runs_hot", "self_productivity_mult", 1.0)), 1.20, 0.001)
	# A channel the quirk does not touch falls back to the default.
	assert_eq(QuirkCatalogue.effect("runs_hot", "leak_chance", 0.0), 0.0, "untouched channel -> default")
	# An unknown quirk id -> default.
	assert_eq(QuirkCatalogue.effect("no_such_quirk", "self_productivity_mult", 1.0), 1.0)

# --- Deterministic assignment -----------------------------------------------

func test_pick_id_is_deterministic_from_seed():
	var a := RandomNumberGenerator.new(); a.seed = 4242
	var b := RandomNumberGenerator.new(); b.seed = 4242
	for i in range(20):
		assert_eq(QuirkCatalogue.pick_id(a), QuirkCatalogue.pick_id(b), "same seed -> same pick")

func test_pick_id_always_in_catalogue():
	var rng := RandomNumberGenerator.new(); rng.seed = 99
	for i in range(50):
		assert_true(QuirkCatalogue.has(QuirkCatalogue.pick_id(rng)), "pick_id yields a real quirk id")

func test_generated_quirk_is_catalogue_member_and_deterministic():
	# Same seed -> same quirk on the researcher (hidden-layer child rng, ADR-0006).
	var r1 := Researcher.new("safety")
	var r2 := Researcher.new("safety")
	var rng1 := RandomNumberGenerator.new(); rng1.seed = 31337
	var rng2 := RandomNumberGenerator.new(); rng2.seed = 31337
	r1.generate_random(rng1)
	r2.generate_random(rng2)
	assert_eq(r1.quirk, r2.quirk, "same seed -> same quirk")
	if r1.quirk != "":
		assert_true(QuirkCatalogue.has(r1.quirk), "assigned quirk is a catalogue id")

# --- Effect wiring on the researcher ----------------------------------------

func test_researcher_quirk_effect_reads_catalogue():
	var r := Researcher.new("safety")
	assert_eq(float(r.quirk_effect("self_productivity_mult", 1.0)), 1.0, "no quirk -> default")
	r.quirk = "runs_hot"
	assert_almost_eq(float(r.quirk_effect("self_productivity_mult", 1.0)), 1.20, 0.001, "quirk -> catalogue value")

# --- Reveal flips quirk_known -----------------------------------------------

func test_tenure_reveal_flips_quirk_known_at_threshold():
	var r := Researcher.new("safety")
	r.quirk = "cat_whisperer"  # after_turns = 4 in the data
	r.quirk_known = false
	var threshold := QuirkCatalogue.reveal_after_turns("cat_whisperer")

	r.turns_employed = threshold - 1
	assert_false(r.maybe_reveal_quirk_by_tenure(), "not yet at threshold")
	assert_false(r.quirk_known, "still hidden before threshold")

	r.turns_employed = threshold
	assert_true(r.maybe_reveal_quirk_by_tenure(), "reveals at threshold")
	assert_true(r.quirk_known, "quirk_known flipped true")

func test_expose_quirk_event_path_flips_known():
	var r := Researcher.new("safety")
	r.quirk = "doom_absolutist"
	assert_false(r.quirk_known)
	r.expose_quirk()
	assert_true(r.quirk_known, "exposure event surfaces the quirk")

func test_no_quirk_never_reveals_by_tenure():
	var r := Researcher.new("safety")  # quirk == ""
	r.turns_employed = 999
	assert_false(r.maybe_reveal_quirk_by_tenure(), "no quirk -> nothing to reveal")

# --- Save / load round-trip of a catalogue quirk ----------------------------

func test_catalogue_quirk_round_trips_through_json():
	var r := Researcher.new("safety")
	r.quirk = "empire_builder"
	r.quirk_known = true
	var parsed = JSON.parse_string(JSON.stringify(r.to_dict()))
	assert_not_null(parsed, "serializes to JSON")
	var r2 := Researcher.new()
	r2.from_dict(parsed)
	assert_eq(r2.quirk, "empire_builder", "quirk id round-trips")
	assert_true(r2.quirk_known, "quirk_known round-trips")
	# And the effect is still live after the hop.
	assert_almost_eq(float(r2.quirk_effect("team_productivity_add", 0.0)), 0.04, 0.001)

# --- Starters draw their quirk from the catalogue ---------------------------

func test_starter_quirks_are_catalogue_members():
	var state := GameState.new("quirk_starter_seed")
	assert_eq(state.candidate_pool.size(), 4, "four founding starters")
	for cand in state.candidate_pool:
		if cand.quirk != "":
			assert_true(QuirkCatalogue.has(cand.quirk),
				"starter quirk '%s' is drawn from the catalogue" % cand.quirk)

func test_starter_quirk_riders_exist_across_seeds():
	# Across a spread of seeds, guaranteed riders that land on the quirk branch must all be
	# catalogue members (the appetite-branch starters simply carry no quirk).
	var seen_a_quirk := false
	for s in ["seedA", "seedB", "seedC", "seedD", "seedE", "seedF"]:
		var state := GameState.new(s)
		for cand in state.candidate_pool:
			if cand.quirk != "":
				seen_a_quirk = true
				assert_true(QuirkCatalogue.has(cand.quirk), "%s: catalogue quirk" % s)
	assert_true(seen_a_quirk, "at least one starter across seeds took the quirk branch")

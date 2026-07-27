extends GutTest
## ADR-0010 B7/B8/B9: typed reputation (org / operator / employee) + the
## governance-body roster.
##
## The load-bearing invariant under test is the AUTHORITY RULE: the legacy
## `reputation` scalar stays authoritative and untouched, and the typed dims are
## a purely ADDITIVE layer. A future refactor that turns the scalar into a
## derived sum of the dims breaks ~20 write sites (spend_resources, media_system,
## the ledger's currency:"reputation" entries) -- test_scalar_stays_authoritative
## and test_billing_does_not_touch_scalar exist to catch exactly that.
##
## The cost-routing rule is Pip's, 2026-07-27: reputation COSTS bill the ORG by
## default; the FOUNDER (operator) pays only when the event/action explicitly
## names the founder.

func _fresh_state(seed_str: String):
	var s = GameState.new(seed_str)
	s.reputation = 50.0
	return s


# ---------------------------------------------------------------------------
# rep_for(kind, who)
# ---------------------------------------------------------------------------

func test_typed_dims_start_at_zero():
	var state = _fresh_state("rep-zero")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), 0.0, "org safety starts at zero")
	assert_eq(state.rep_for("capability", GameState.REP_WHO_ORG), 0.0, "org capability starts at zero")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_OPERATOR), 0.0, "operator safety starts at zero")
	assert_eq(state.reputation, 50.0, "the authoritative scalar is untouched by typing")


func test_rep_for_defaults_to_org():
	var state = _fresh_state("rep-default-who")
	state.add_rep("safety", 4.0, GameState.REP_WHO_ORG)
	assert_eq(state.rep_for("safety"), 4.0, "omitting `who` reads the org bearer")


func test_org_and_operator_are_separate_pockets():
	var state = _fresh_state("rep-split")
	state.add_rep("safety", 6.0, GameState.REP_WHO_ORG)
	state.add_rep("safety", -2.0, GameState.REP_WHO_OPERATOR)
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), 6.0, "org dim moved")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_OPERATOR), -2.0, "operator dim moved independently")
	assert_eq(state.rep_for("capability", GameState.REP_WHO_ORG), 0.0, "the other kind is untouched")


func test_unknown_kind_and_unknown_bearer_read_zero():
	# ResourceAccessor.read's convention: an unknown name reads 0.0, never errors.
	var state = _fresh_state("rep-unknown")
	state.add_rep("safety", 5.0, GameState.REP_WHO_ORG)
	assert_eq(state.rep_for("charisma", GameState.REP_WHO_ORG), 0.0, "unknown kind reads zero")
	assert_eq(state.rep_for("safety", "nobody_by_that_name"), 0.0, "unknown bearer reads zero")
	assert_eq(state.rep_for("safety", ""), 0.0, "empty bearer reads zero")
	assert_false(state.has_rep_bearer("nobody_by_that_name"), "unknown bearer is not claimed as known")
	assert_true(state.has_rep_bearer(GameState.REP_WHO_ORG), "org is a known bearer")
	assert_true(state.has_rep_bearer(GameState.REP_WHO_OPERATOR), "operator is a known bearer")


func test_unknown_kind_write_is_a_no_op():
	var state = _fresh_state("rep-unknown-write")
	state.add_rep("charisma", 9.0, GameState.REP_WHO_ORG)
	assert_false(state.rep_org.has("charisma"), "an unknown kind never creates a dim")


func test_rep_dims_returns_a_detached_copy():
	var state = _fresh_state("rep-copy")
	state.add_rep("safety", 3.0, GameState.REP_WHO_ORG)
	var dims: Dictionary = state.rep_dims(GameState.REP_WHO_ORG)
	dims["safety"] = 999.0
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), 3.0,
		"mutating the returned dict must not write through to state")


# ---------------------------------------------------------------------------
# Employee bearer (B8 per-person)
# ---------------------------------------------------------------------------

func _employ(state, person_name: String, candidate_id: String):
	var r = Researcher.new()
	r.researcher_name = person_name
	r.candidate_id = candidate_id
	state.researchers.append(r)
	return r


func test_employee_rep_resolves_by_name_and_by_candidate_id():
	var state = _fresh_state("rep-person")
	var r = _employ(state, "Ada Okonkwo", "cand_7")
	r.add_rep("safety", 8.0)
	assert_eq(state.rep_for("safety", "Ada Okonkwo"), 8.0, "a researcher resolves by display name")
	assert_eq(state.rep_for("safety", "cand_7"), 8.0, "a researcher resolves by candidate_id")
	assert_true(state.has_rep_bearer("cand_7"), "an employed researcher is a known bearer")


func test_employee_rep_is_independent_of_org_rep():
	var state = _fresh_state("rep-person-independent")
	_employ(state, "Ada Okonkwo", "cand_7")
	state.add_rep("safety", 5.0, "cand_7")
	assert_eq(state.rep_for("safety", "cand_7"), 5.0, "the person's dim moved")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), 0.0, "the org's dim did not")
	assert_eq(state.reputation, 50.0, "the scalar did not")


func test_researcher_rep_dims_is_a_detached_copy():
	var r = Researcher.new()
	r.add_rep("capability", 2.0)
	var dims: Dictionary = r.rep_dims()
	dims["capability"] = 42.0
	assert_eq(r.rep_for("capability"), 2.0, "the live researcher dict is not handed out")
	assert_eq(r.rep_for("nonsense"), 0.0, "unknown kind reads zero on a person too")


# ---------------------------------------------------------------------------
# COST ROUTING RULE (Pip 2026-07-27)
# ---------------------------------------------------------------------------

func test_rep_cost_bearer_defaults_to_org():
	assert_eq(GameState.rep_cost_bearer({}), GameState.REP_WHO_ORG, "an empty spec bills the org")
	assert_eq(GameState.rep_cost_bearer({"id": "bad_press"}), GameState.REP_WHO_ORG,
		"a spec that says nothing about the founder bills the org")
	assert_eq(GameState.REP_COST_DEFAULT_BEARER, GameState.REP_WHO_ORG,
		"the named default constant is the org")


func test_rep_cost_bearer_routes_to_founder_only_when_named():
	assert_eq(GameState.rep_cost_bearer({"targets_founder": true}), GameState.REP_WHO_OPERATOR,
		"the explicit founder flag bills the founder")
	assert_eq(GameState.rep_cost_bearer({"rep_bearer": "operator"}), GameState.REP_WHO_OPERATOR,
		"an explicit operator bearer bills the founder")
	assert_eq(GameState.rep_cost_bearer({"rep_bearer": "founder"}), GameState.REP_WHO_OPERATOR,
		"'founder' is accepted as an alias for the operator pocket")
	assert_eq(GameState.rep_cost_bearer({"targets_founder": false}), GameState.REP_WHO_ORG,
		"an explicitly false flag falls back to the org")
	assert_eq(GameState.rep_cost_bearer({"rep_bearer": "org", "targets_founder": true}),
		GameState.REP_WHO_ORG, "an explicit org bearer wins over the flag")


func test_billing_charges_the_routed_pocket():
	var state = _fresh_state("rep-bill")
	var bearer_a := state.bill_reputation("safety", 3.0, {})
	assert_eq(bearer_a, GameState.REP_WHO_ORG, "the default bill returns the org bearer")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), -3.0, "the org pocket paid")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_OPERATOR), 0.0, "the founder pocket did not")

	var bearer_b := state.bill_reputation("safety", 2.0, {"targets_founder": true})
	assert_eq(bearer_b, GameState.REP_WHO_OPERATOR, "a founder-named bill returns the operator bearer")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_OPERATOR), -2.0, "the founder pocket paid")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), -3.0, "the org pocket is unchanged")


func test_billing_does_not_touch_scalar():
	var state = _fresh_state("rep-bill-scalar")
	state.bill_reputation("safety", 10.0, {"targets_founder": true})
	assert_eq(state.reputation, 50.0,
		"typed billing is additive-only -- the authoritative scalar is still spend_resources' job")


func test_scalar_stays_authoritative_under_spend():
	# The legacy path must keep working untouched: spend_resources deducts the
	# scalar and the typed dims stay out of it.
	var state = _fresh_state("rep-scalar-authority")
	state.add_rep("safety", 7.0, GameState.REP_WHO_ORG)
	state.spend_resources({"reputation": 5.0})
	assert_eq(state.reputation, 45.0, "the scalar is the thing spend_resources deducts")
	assert_eq(state.rep_for("safety", GameState.REP_WHO_ORG), 7.0, "typed dims are not decomposed from it")


# ---------------------------------------------------------------------------
# Serialization: additive keys, round-trip, backwards compatibility
# ---------------------------------------------------------------------------

func test_typed_rep_round_trips_through_save():
	var state = _fresh_state("rep-save")
	state.add_rep("safety", 4.5, GameState.REP_WHO_ORG)
	state.add_rep("capability", -1.25, GameState.REP_WHO_OPERATOR)
	var restored = _fresh_state("rep-save")
	restored.from_dict(state.to_dict())
	assert_eq(restored.rep_for("safety", GameState.REP_WHO_ORG), 4.5, "org dim survives the round trip")
	assert_eq(restored.rep_for("capability", GameState.REP_WHO_OPERATOR), -1.25,
		"operator dim survives the round trip")
	assert_eq(restored.reputation, state.reputation, "the scalar round-trips as it always did")


func test_save_keys_are_additive_not_a_restructure():
	var state = _fresh_state("rep-keys")
	var d: Dictionary = state.to_dict()
	assert_true(d.has("reputation"), "the pre-existing scalar key is still there, unmoved")
	assert_true(d["reputation"] is float, "the scalar key is still a plain float, not a dict")
	assert_true(d.has("rep_org"), "the typed org dim is a NEW key")
	assert_true(d.has("rep_operator"), "the typed operator dim is a NEW key")


func test_pre_typing_save_loads_at_zero():
	var state = _fresh_state("rep-legacy-save")
	var legacy: Dictionary = state.to_dict()
	legacy.erase("rep_org")
	legacy.erase("rep_operator")
	var restored = _fresh_state("rep-legacy-save")
	restored.add_rep("safety", 99.0, GameState.REP_WHO_ORG)  # dirty it first
	restored.from_dict(legacy)
	assert_eq(restored.rep_for("safety", GameState.REP_WHO_ORG), 0.0,
		"a save with no typed keys loads as scalar-only, not as stale dims")


func test_researcher_rep_round_trips_and_defaults():
	var r = Researcher.new()
	r.researcher_name = "Ada Okonkwo"
	r.add_rep("safety", 3.5)
	var d: Dictionary = r.to_dict()
	assert_true(d.has("rep"), "per-person rep is a new serialized key")
	var restored = Researcher.new()
	restored.from_dict(d)
	assert_eq(restored.rep_for("safety"), 3.5, "per-person rep survives the round trip")

	var legacy: Dictionary = r.to_dict()
	legacy.erase("rep")
	var from_legacy = Researcher.new()
	from_legacy.add_rep("safety", 12.0)
	from_legacy.from_dict(legacy)
	assert_eq(from_legacy.rep_for("safety"), 0.0, "a pre-typing researcher loads at zero standing")


func test_paper_standing_round_trips_and_defaults():
	var paper = PaperSubmissions.PaperSubmission.new()
	paper.title = "On Not Doing That"
	assert_eq(paper.standing, 0.0, "a fresh paper carries no standing")
	paper.add_standing(2.0)
	paper.add_standing(-5.0)
	assert_eq(paper.standing, 0.0, "standing floors at zero in v1 (adoption only adds)")
	paper.add_standing(1.5)
	var d: Dictionary = paper.to_dict()
	assert_true(d.has("standing"), "paper standing is a new serialized key")
	var restored = PaperSubmissions.PaperSubmission.from_dict(d)
	assert_eq(restored.standing, 1.5, "paper standing survives the round trip")

	var legacy: Dictionary = paper.to_dict()
	legacy.erase("standing")
	assert_eq(PaperSubmissions.PaperSubmission.from_dict(legacy).standing, 0.0,
		"a pre-typing paper loads with no standing")


# ---------------------------------------------------------------------------
# Governance-body roster (B4) -- loading only; no consumer logic yet.
# ---------------------------------------------------------------------------

func test_bodies_roster_loads():
	var bodies: Array = RivalLabs.load_governance_bodies()
	assert_between(bodies.size(), 2, 5,
		"the roster carries 2-5 governance bodies (small by design in v1)")


func test_every_body_has_the_fields_the_adoption_reader_will_want():
	var seen_ids: Array = []
	for body in RivalLabs.load_governance_bodies():
		assert_true(body is Dictionary, "each body is a plain dict (no new class -- B4)")
		assert_ne(String(body.get("id", "")), "", "each body has an id")
		assert_ne(String(body.get("name", "")), "", "each body has a name")
		assert_ne(String(body.get("focus", "")), "", "each body has a focus")
		assert_false(String(body.get("id")) in seen_ids, "body ids are unique")
		seen_ids.append(String(body.get("id")))
		var weight := float(body.get("weight", -1.0))
		assert_between(weight, 0.0, 1.0, "adoption weight is a 0..1 clout fraction")


func test_body_focus_shares_the_rival_lab_vocabulary():
	# So one receptivity reader can walk labs and bodies together (B4/B5).
	var lab_focuses := ["safety", "capabilities", "governance", "balanced"]
	for body in RivalLabs.load_governance_bodies():
		assert_true(String(body.get("focus")) in lab_focuses,
			"body focus '%s' is drawn from the RivalLab focus vocabulary" % String(body.get("focus")))

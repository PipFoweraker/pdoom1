extends GutTest
## Researcher PERSONA catalogue validation (issue #1225 section 1: 24 identity slots on
## 5 wired faces via a bare modulo -- Pip asked for 'a systematic run of personas').
## The catalogue (res://data/researchers/personas.json) is DATA-ONLY for now: no runtime
## system consumes it yet (the identity lane wires the draw + portrait mapping). These
## tests pin the contract that makes that wiring safe: every mechanical key maps 1:1 onto
## Researcher.from_dict keys, every quirk id is a QuirkCatalogue member, the pool is deep
## enough to break the modulo (> 2x IDENTITY_POOL_SIZE) with even lane coverage, and the
## whole file survives a Researcher hydration round-trip.

const Definitions = preload("res://scripts/data/definition_loader.gd")
const PERSONAS_PATH := "res://data/researchers/personas.json"

const APPETITE_KEYS := ["compute", "prestige", "mentees", "money", "mission_purity"]

var _data: Dictionary = {}
var _personas: Dictionary = {}

func before_all():
	_data = Definitions.load_object(PERSONAS_PATH, "PersonaTest")
	_personas = _data.get("personas", {})

# --- Catalogue loads + depth -------------------------------------------------

func test_catalogue_loads():
	assert_false(_data.is_empty(), "personas.json loads as a JSON object")
	assert_eq(int(_data.get("version", 0)), 1, "version 1")
	assert_false(_personas.is_empty(), "personas dict is non-empty")

func test_pool_breaks_the_identity_modulo():
	# #1225: 24 identity slots % 5 wired faces guarantees duplicate faces in a full
	# 6-candidate pool. The persona pool must exceed 2x the identity slot count so a
	# hiring-heavy long run (~40-50 sourced candidates) never repeats a person.
	assert_gt(_personas.size(), Researcher.IDENTITY_POOL_SIZE * 2,
		"persona pool exceeds 2x IDENTITY_POOL_SIZE (%d)" % Researcher.IDENTITY_POOL_SIZE)
	assert_gte(_personas.size(), 48, "at least 48 personas (12 per lane)")

func test_every_lane_has_depth():
	# Candidate specialization is drawn uniformly over SPEC_POOL (hiring_pipeline.gd:170),
	# so per-lane depth is what prevents repeats, not the total.
	var counts := {}
	for id in _personas.keys():
		var spec := String(_personas[id].get("specialization", ""))
		counts[spec] = int(counts.get(spec, 0)) + 1
	for spec in ["safety", "capabilities", "interpretability", "alignment"]:
		assert_gte(int(counts.get(spec, 0)), 12, "%s lane has at least 12 personas" % spec)

# --- Per-persona shape (keys map 1:1 onto Researcher.from_dict) --------------

func test_every_persona_is_well_formed():
	for id in _personas.keys():
		var p: Dictionary = _personas[id]
		var pname := String(p.get("name", ""))
		assert_true(pname.length() > 0, "%s has a name" % id)
		assert_true(pname.contains(" "), "%s name has at least two words" % id)
		assert_true(Researcher.SPECIALIZATIONS.has(String(p.get("specialization", ""))),
			"%s specialization is a Researcher lane" % id)
		assert_true(String(p.get("flavour", "")).length() >= 80,
			"%s flavour is substantial (no stat blocks)" % id)
		var skill := int(p.get("skill_level", 0))
		assert_between(skill, 1, 10, "%s skill_level in 1..10" % id)
		var salary := float(p.get("salary_expectation", 0.0))
		assert_between(salary, 30000.0, 200000.0, "%s salary_expectation plausible" % id)
		var lr := float(p.get("loyalty_risk", -1.0))
		assert_between(lr, 0.0, 1.0, "%s loyalty_risk in 0..1" % id)
		assert_true(p.get("needs_visa", null) is bool, "%s needs_visa is a bool" % id)

func test_appetites_are_the_five_adr0011_keys():
	for id in _personas.keys():
		var app: Dictionary = _personas[id].get("appetites", {})
		assert_eq(app.keys().size(), APPETITE_KEYS.size(), "%s has exactly five appetites" % id)
		for k in APPETITE_KEYS:
			assert_true(app.has(k), "%s has appetite '%s'" % [id, k])
			var v := float(app.get(k, -1.0))
			assert_between(v, 0.0, 1.0, "%s appetite %s in 0..1" % [id, k])

func test_quirk_ids_are_catalogue_members():
	var seen_quirk := false
	for id in _personas.keys():
		var q := String(_personas[id].get("quirk", ""))
		if q != "":
			seen_quirk = true
			assert_true(QuirkCatalogue.has(q), "%s quirk '%s' is in quirks.json" % [id, q])
	assert_true(seen_quirk, "at least one persona carries a quirk rider")

func test_names_are_unique():
	var seen := {}
	for id in _personas.keys():
		var lower := String(_personas[id].get("name", "")).to_lower()
		assert_false(seen.has(lower), "duplicate persona name: %s" % lower)
		seen[lower] = true

func test_ascii_only():
	# Repo hard rule (#744): godot/data/**/*.json is ASCII-only (blocking pre-commit
	# gate). Pinned here too so a hand-edit fails fast in the test tier.
	for id in _personas.keys():
		var s := "%s%s%s" % [id, _personas[id].get("name", ""), _personas[id].get("flavour", "")]
		for i in range(s.length()):
			if s.unicode_at(i) > 126:
				fail_test("%s contains non-ASCII at index %d" % [id, i])
				return
	pass_test("all persona ids, names and flavour are ASCII")

# --- Hydration: the schema really is Researcher's serialization schema -------

func test_every_persona_hydrates_a_researcher():
	# from_dict reads exactly these keys ('flavour' is ignored by design), so a future
	# PersonaCatalogue can hydrate a candidate with no translation layer.
	for id in _personas.keys():
		var p: Dictionary = _personas[id]
		var r := Researcher.new()
		r.from_dict(p)
		assert_eq(r.researcher_name, String(p["name"]), "%s name hydrates" % id)
		assert_eq(r.specialization, String(p["specialization"]), "%s lane hydrates" % id)
		assert_eq(r.skill_level, int(p["skill_level"]), "%s skill hydrates" % id)
		assert_almost_eq(r.salary_expectation, float(p["salary_expectation"]), 0.01,
			"%s salary hydrates" % id)
		assert_eq(r.quirk, String(p.get("quirk", "")), "%s quirk hydrates" % id)
		assert_eq(r.needs_visa, bool(p["needs_visa"]), "%s needs_visa hydrates" % id)
		assert_almost_eq(r.loyalty_risk, float(p["loyalty_risk"]), 0.002,
			"%s loyalty_risk hydrates (snapped to SAVE_QUANTUM)" % id)
		for k in APPETITE_KEYS:
			assert_almost_eq(float(r.appetites[k]), float(p["appetites"][k]), 0.002,
				"%s appetite %s hydrates (snapped)" % [id, k])

func test_hydrated_persona_round_trips_through_save():
	# A persona-backed hire must survive the save/load JSON hop like any researcher.
	var ids := _personas.keys()
	ids.sort()
	var p: Dictionary = _personas[ids[0]]
	var r := Researcher.new()
	r.from_dict(p)
	var parsed = JSON.parse_string(JSON.stringify(r.to_dict()))
	assert_not_null(parsed, "serializes to JSON")
	var r2 := Researcher.new()
	r2.from_dict(parsed)
	assert_eq(r2.researcher_name, r.researcher_name, "name survives the hop")
	assert_eq(r2.quirk, r.quirk, "quirk survives the hop")
	for k in APPETITE_KEYS:
		assert_almost_eq(float(r2.appetites[k]), float(r.appetites[k]), 0.0001,
			"appetite %s stable across the hop (snap is idempotent)" % k)

func test_quirked_personas_have_live_effects():
	# The rider is hidden-but-TRUE (ADR-0004): effects are live from creation.
	for id in _personas.keys():
		var q := String(_personas[id].get("quirk", ""))
		if q == "":
			continue
		var r := Researcher.new()
		r.from_dict(_personas[id])
		var eff: Dictionary = QuirkCatalogue.get_def(q).get("effects", {})
		assert_false(eff.is_empty(), "%s quirk '%s' has effect channels" % [id, q])
		var channel := String(eff.keys()[0])
		assert_eq(r.quirk_effect(channel, null), eff[channel],
			"%s quirk effect '%s' is live through the researcher" % [id, channel])

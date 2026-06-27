extends GutTest
## Unit tests for Research Quality System (Issue #500)
## Speed multipliers, per-month->per-turn risk scaling, serialization.

func _state() -> GameState:
	return GameState.new("rq_test_seed")

func test_default_mode_is_standard():
	assert_eq(_state().research_quality_mode, "standard", "Default quality should be standard")

func test_research_multipliers():
	var s = _state()
	s.set_research_quality("rushed");   assert_eq(s.get_research_multiplier(), 2.0, "Rushed = 2.0x")
	s.set_research_quality("thorough"); assert_eq(s.get_research_multiplier(), 0.5, "Thorough = 0.5x")
	s.set_research_quality("standard"); assert_eq(s.get_research_multiplier(), 1.0, "Standard = 1.0x")

func test_set_invalid_mode_is_ignored():
	var s = _state()
	s.set_research_quality("nonsense")
	assert_eq(s.research_quality_mode, "standard", "Invalid mode ignored")

func test_rushed_adds_integrity_and_overhang_risk():
	var s = _state()
	s.research_quality_mode = "rushed"
	s.apply_research_quality_risk(1)
	assert_almost_eq(s.risk_system.pools["research_integrity"], 6.0, 0.001, "Rushed +6 integrity (per-month x 1.0)")
	assert_almost_eq(s.risk_system.pools["capability_overhang"], 2.0, 0.001, "Rushed +2 overhang")

func test_thorough_reduces_seeded_risk():
	var s = _state()
	s.risk_system.add_risk("research_integrity", 20.0, "seed", 0)
	s.risk_system.add_risk("capability_overhang", 20.0, "seed", 0)
	s.research_quality_mode = "thorough"
	s.apply_research_quality_risk(1)
	assert_almost_eq(s.risk_system.pools["research_integrity"], 17.0, 0.001, "Thorough -3 integrity")
	assert_almost_eq(s.risk_system.pools["capability_overhang"], 17.0, 0.001, "Thorough -3 overhang")

func test_standard_is_risk_neutral():
	var s = _state()
	s.risk_system.add_risk("research_integrity", 10.0, "seed", 0)
	s.research_quality_mode = "standard"
	s.apply_research_quality_risk(1)
	assert_almost_eq(s.risk_system.pools["research_integrity"], 10.0, 0.001, "Standard changes no risk")

func test_quality_mode_survives_serialization():
	var s = _state(); s.set_research_quality("rushed")
	var s2 = _state(); s2.from_dict(s.to_dict())
	assert_eq(s2.research_quality_mode, "rushed", "Mode survives save/load")

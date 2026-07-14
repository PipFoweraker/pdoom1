extends GutTest
## Unit tests for DoomSystem class

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

func _create_doom_system() -> DoomSystem:
	"""Create a fresh DoomSystem for testing"""
	var doom_system = DoomSystem.new()
	return doom_system

func _create_minimal_game_state() -> GameState:
	"""Create a minimal GameState for doom calculations"""
	var state = GameState.new("test_seed")
	return state

# ============================================================================
# DOOM CLAMPING TESTS (Issue #488)
# ============================================================================

func test_doom_clamped_to_upper_bound():
	# Test that doom is clamped to 100 maximum
	var doom_system = _create_doom_system()

	doom_system.current_doom = 95.0
	doom_system.add_event_doom(20.0, "test_event")

	assert_eq(doom_system.current_doom, 100.0, "Doom should be clamped to 100")

func test_doom_clamped_to_lower_bound():
	# Test that doom is clamped to 0 minimum
	var doom_system = _create_doom_system()

	doom_system.current_doom = 5.0
	doom_system.add_event_doom(-20.0, "test_reduction")

	assert_eq(doom_system.current_doom, 0.0, "Doom should be clamped to 0")

func test_doom_clamping_in_calculate_doom_change():
	# Test that calculate_doom_change also clamps doom
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	# Set up state to generate doom that pushes past the ceiling (magnitudes are Balance-driven
	# post-L1 re-denomination, so start near the cap and let any positive change clamp).
	doom_system.current_doom = 99.9
	state.capability_researchers = 10  # any positive per-researcher doom now tips it over 100

	var result = doom_system.calculate_doom_change(state)

	assert_eq(doom_system.current_doom, 100.0, "Doom should be clamped to 100 after calculation")
	assert_eq(result["new_doom"], 100.0, "Result should report clamped doom value")

# ============================================================================
# CALCULATE_DOOM_CHANGE TESTS (Issue #488)
# ============================================================================

func test_calculate_doom_change_returns_expected_structure():
	# Test that calculate_doom_change returns all expected keys
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	var result = doom_system.calculate_doom_change(state)

	assert_has(result, "total_change", "Result should have total_change")
	assert_has(result, "raw_change", "Result should have raw_change")
	assert_has(result, "momentum", "Result should have momentum")
	assert_has(result, "velocity", "Result should have velocity")
	assert_has(result, "sources", "Result should have sources")
	assert_has(result, "new_doom", "Result should have new_doom")
	assert_has(result, "trend", "Result should have trend")

func test_calculate_doom_change_base_doom():
	# Base doom equals the Balance coefficient (L1 re-denominated it off the strategic-turn
	# magnitude; assert the wiring, not a frozen literal).
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	var result = doom_system.calculate_doom_change(state)

	assert_almost_eq(result["sources"]["base"], Balance.num("doom.base_per_turn", 0.06), 0.0001, "Base doom matches Balance base_per_turn")

func test_calculate_doom_change_capability_researchers():
	# Capability researchers add per-researcher doom (Balance-driven magnitude).
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	state.capability_researchers = 2  # 2 * per-researcher coefficient

	var result = doom_system.calculate_doom_change(state)

	assert_almost_eq(result["sources"]["capabilities"], 2.0 * Balance.num("doom.legacy_capability_per_researcher", 0.15), 0.0001, "Capabilities doom = 2 x per-researcher coefficient")

# ============================================================================
# APPLY_DOOM_MODIFIER TESTS (Issue #488)
# ============================================================================

func test_apply_doom_modifier_adds_to_existing():
	# Test that apply_doom_modifier accumulates modifiers
	var doom_system = _create_doom_system()

	doom_system.apply_doom_modifier("capabilities", -0.5)
	assert_eq(doom_system.doom_modifiers["capabilities"], -0.5, "First modifier should be applied")

	doom_system.apply_doom_modifier("capabilities", -0.3)
	assert_eq(doom_system.doom_modifiers["capabilities"], -0.8, "Modifiers should accumulate")

func test_apply_doom_modifier_ignores_invalid_source():
	# Test that apply_doom_modifier ignores invalid sources
	var doom_system = _create_doom_system()

	var original_mods = doom_system.doom_modifiers.duplicate()
	doom_system.apply_doom_modifier("invalid_source", 5.0)

	assert_eq(doom_system.doom_modifiers, original_mods, "Invalid source should not modify anything")

func test_set_doom_multiplier():
	# Test that set_doom_multiplier sets the value correctly
	var doom_system = _create_doom_system()

	doom_system.set_doom_multiplier("rivals", 0.7)
	assert_eq(doom_system.doom_multipliers["rivals"], 0.7, "Multiplier should be set to 0.7")

	doom_system.set_doom_multiplier("rivals", 1.5)
	assert_eq(doom_system.doom_multipliers["rivals"], 1.5, "Multiplier should be replaced with 1.5")

# ============================================================================
# MOMENTUM SYSTEM TESTS
# ============================================================================

func test_momentum_capped_positive():
	# Test that momentum is capped at momentum_cap
	var doom_system = _create_doom_system()

	# Force high momentum by directly setting it
	doom_system.doom_momentum = 10.0  # Above cap

	# Calculate momentum to apply capping
	doom_system._calculate_momentum(5.0)

	assert_true(doom_system.doom_momentum <= doom_system.momentum_cap, "Momentum should be capped at momentum_cap")

func test_momentum_capped_negative():
	# Test that negative momentum is also capped
	var doom_system = _create_doom_system()

	doom_system.doom_momentum = -10.0  # Below negative cap

	doom_system._calculate_momentum(-5.0)

	assert_true(doom_system.doom_momentum >= -doom_system.momentum_cap, "Negative momentum should be capped")

# ============================================================================
# STATUS AND TREND TESTS
# ============================================================================

# L6 unification: doom statuses are ThemeManager's canonical bands, lowercased
# (nominal/elevated/high/severe/extreme/catastrophic/terminal at 15/37/52/67/80/92).
# The former 25/50/70/90 safe/warning/danger/critical/catastrophic copy is gone.

func test_get_doom_status_nominal():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 10.0
	assert_eq(doom_system.get_doom_status(), "nominal", "Doom < 15 should be 'nominal'")

func test_get_doom_status_elevated():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 20.0
	assert_eq(doom_system.get_doom_status(), "elevated", "Doom 15-36 should be 'elevated'")

func test_get_doom_status_high():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 40.0
	assert_eq(doom_system.get_doom_status(), "high", "Doom 37-51 should be 'high'")

func test_get_doom_status_severe():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 60.0
	assert_eq(doom_system.get_doom_status(), "severe", "Doom 52-66 should be 'severe'")

func test_get_doom_status_extreme():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 70.0
	assert_eq(doom_system.get_doom_status(), "extreme", "Doom 67-79 should be 'extreme'")

func test_get_doom_status_catastrophic():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 80.0
	assert_eq(doom_system.get_doom_status(), "catastrophic", "Doom 80-91 should be 'catastrophic'")

func test_get_doom_status_terminal():
	var doom_system = _create_doom_system()

	doom_system.current_doom = 95.0
	assert_eq(doom_system.get_doom_status(), "terminal", "Doom >= 92 should be 'terminal'")

# ============================================================================
# ADD_EVENT_DOOM TESTS
# ============================================================================

func test_add_event_doom_increases_doom():
	# Test that add_event_doom adds to current doom
	var doom_system = _create_doom_system()

	doom_system.current_doom = 50.0
	doom_system.add_event_doom(10.0, "test_event")

	assert_eq(doom_system.current_doom, 60.0, "Doom should increase by event amount")

func test_add_event_doom_tracks_source():
	# Test that add_event_doom updates the events source
	var doom_system = _create_doom_system()

	doom_system.add_event_doom(5.0, "event1")
	doom_system.add_event_doom(3.0, "event2")

	assert_eq(doom_system.doom_sources["events"], 8.0, "Event doom should accumulate")

# ============================================================================
# SERIALIZATION TESTS
# ============================================================================

func test_to_dict_serialization():
	# Test that to_dict properly serializes state
	var doom_system = _create_doom_system()

	doom_system.current_doom = 75.0
	doom_system.doom_velocity = 2.5
	doom_system.doom_momentum = 3.0

	var dict = doom_system.to_dict()

	assert_eq(dict["current_doom"], 75.0, "Serialized doom should match")
	assert_eq(dict["doom_velocity"], 2.5, "Serialized velocity should match")
	assert_eq(dict["doom_momentum"], 3.0, "Serialized momentum should match")
	assert_has(dict, "doom_sources", "Should include doom_sources")
	assert_has(dict, "doom_multipliers", "Should include doom_multipliers")
	assert_has(dict, "doom_modifiers", "Should include doom_modifiers")

func test_from_dict_deserialization():
	# Test that from_dict properly deserializes state
	var doom_system = _create_doom_system()

	var data = {
		"current_doom": 65.0,
		"doom_velocity": -1.5,
		"doom_momentum": -2.0,
		"doom_sources": {"base": 1.0, "events": 5.0},
		"doom_multipliers": {"capabilities": 1.2},
		"doom_modifiers": {"safety": 0.5}
	}

	doom_system.from_dict(data)

	assert_eq(doom_system.current_doom, 65.0, "Deserialized doom should match")
	assert_eq(doom_system.doom_velocity, -1.5, "Deserialized velocity should match")
	assert_eq(doom_system.doom_momentum, -2.0, "Deserialized momentum should match")

func test_from_dict_handles_missing_keys():
	# Test that from_dict handles partial data gracefully
	var doom_system = _create_doom_system()

	var data = {
		"current_doom": 40.0
	}

	doom_system.from_dict(data)

	assert_eq(doom_system.current_doom, 40.0, "Should set current_doom from partial data")
	assert_eq(doom_system.doom_velocity, 0.0, "Should use default for missing velocity")
	assert_eq(doom_system.doom_momentum, 0.0, "Should use default for missing momentum")

# ============================================================================
# DOOM TREND TESTS
# ============================================================================

func test_get_doom_trend_stable():
	# Test doom trend when velocity is near zero
	var doom_system = _create_doom_system()

	doom_system.doom_velocity = 0.0
	assert_eq(doom_system._get_doom_trend(), "stable", "Near-zero velocity should be 'stable'")

func test_get_doom_trend_increasing():
	# Test doom trend when velocity is moderately positive
	var doom_system = _create_doom_system()

	doom_system.doom_velocity = 1.0
	assert_eq(doom_system._get_doom_trend(), "increasing", "Positive velocity should be 'increasing'")

func test_get_doom_trend_strongly_increasing():
	# Test doom trend when velocity is highly positive
	var doom_system = _create_doom_system()

	doom_system.doom_velocity = 3.0
	assert_eq(doom_system._get_doom_trend(), "strongly_increasing", "High velocity should be 'strongly_increasing'")

func test_get_doom_trend_decreasing():
	# Test doom trend when velocity is moderately negative
	var doom_system = _create_doom_system()

	doom_system.doom_velocity = -1.0
	assert_eq(doom_system._get_doom_trend(), "decreasing", "Negative velocity should be 'decreasing'")

func test_get_doom_trend_strongly_decreasing():
	# Test doom trend when velocity is highly negative
	var doom_system = _create_doom_system()

	doom_system.doom_velocity = -3.0
	assert_eq(doom_system._get_doom_trend(), "strongly_decreasing", "High negative velocity should be 'strongly_decreasing'")

# ============================================================================
# UNPRODUCTIVE DOOM TESTS (Issue #424)
# ============================================================================

func test_unproductive_doom_no_staff():
	# Test that no staff means no unproductive doom
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	doom_system._calculate_unproductive_doom(state)

	assert_eq(doom_system.doom_sources["unproductive"], 0.0, "No staff should mean no unproductive doom")

func test_unproductive_doom_all_productive():
	# Test that fully productive staff generates no unproductive doom
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	# Add 5 researchers (under management capacity of 9, compute is 100)
	state.safety_researchers = 5

	doom_system._calculate_unproductive_doom(state)

	assert_eq(doom_system.doom_sources["unproductive"], 0.0, "All productive staff should mean no unproductive doom")

func test_unproductive_doom_unmanaged():
	# Test that unmanaged employees contribute to doom (Issue #424 fix)
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	# Add 12 researchers with 0 managers (capacity = 9, so 3 unmanaged)
	state.safety_researchers = 12
	state.managers = 0

	doom_system._calculate_unproductive_doom(state)

	# 3 unmanaged * per-staff coefficient (Balance-driven)
	assert_almost_eq(doom_system.doom_sources["unproductive"], 3.0 * Balance.num("doom.unproductive_per_staff", 0.025), 0.0001, "Unmanaged employees each contribute the per-staff coefficient")

func test_unproductive_doom_no_compute():
	# Test that employees without compute are unproductive
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	# 5 researchers, but only 2 compute available
	state.safety_researchers = 5
	state.compute = 2.0

	doom_system._calculate_unproductive_doom(state)

	# 3 without compute * per-staff coefficient (Balance-driven)
	assert_almost_eq(doom_system.doom_sources["unproductive"], 3.0 * Balance.num("doom.unproductive_per_staff", 0.025), 0.0001, "Employees without compute contribute the per-staff coefficient")

func test_unproductive_doom_no_double_counting():
	# Test that unmanaged employees are not double-counted (Issue #424 fix)
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()

	# 15 researchers with 0 managers (capacity = 9)
	# 6 unmanaged, 9 managed
	# With 100 compute, all 9 managed can work
	state.safety_researchers = 15
	state.managers = 0
	state.compute = 100.0

	doom_system._calculate_unproductive_doom(state)

	# Only 6 unproductive (not 6 + 6 from double counting) * per-staff coefficient (Balance-driven)
	assert_almost_eq(doom_system.doom_sources["unproductive"], 6.0 * Balance.num("doom.unproductive_per_staff", 0.025), 0.0001, "Unmanaged should not be double-counted")

# ============================================================================
# RIVAL DOOM CONTRIBUTION TESTS (Issue #562)
# ============================================================================

func test_rival_doom_survives_source_reset():
	# Regression: turn_manager sets rival doom BEFORE calculate_doom_change(), whose
	# _reset_doom_sources() used to wipe it to 0 before the sum.
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()
	doom_system.set_rival_doom_contribution(7.0)
	var result = doom_system.calculate_doom_change(state)
	assert_eq(result["sources"]["rivals"], 7.0, "Rival doom must survive the per-turn source reset (issue #562)")

func test_rival_doom_zero_when_unset():
	var doom_system = _create_doom_system()
	var state = _create_minimal_game_state()
	var result = doom_system.calculate_doom_change(state)
	assert_eq(result["sources"]["rivals"], 0.0, "Rival doom is 0 when no contribution set")

func test_rival_capability_overhang_scales_with_progress():
	# The passive overhang term grows with accumulated capability_progress, so an advanced
	# rival applies strictly more doom than an identical low-progress one (same rng seed).
	var low = RivalLabs.RivalLab.new("LowLab", 0.9)
	low.capability_progress = 0.0
	var high = RivalLabs.RivalLab.new("HighLab", 0.9)
	high.capability_progress = 200.0
	var state = _create_minimal_game_state()
	var rng_low = RandomNumberGenerator.new()
	rng_low.seed = 12345
	var rng_high = RandomNumberGenerator.new()
	rng_high.seed = 12345
	var low_result = RivalLabs.process_rival_turn(low, state, rng_low)
	var high_result = RivalLabs.process_rival_turn(high, state, rng_high)
	# Overhang coefficient is Balance-driven (L1 re-denominated it); read it, don't freeze it.
	var expected_delta = 200.0 * Balance.num("rivals.capability_overhang_doom_per_progress", RivalLabs.CAPABILITY_OVERHANG_DOOM_PER_PROGRESS)
	assert_almost_eq(high_result["doom_contribution"] - low_result["doom_contribution"], expected_delta, 0.001, "Overhang doom scales with capability_progress")
	assert_gt(high_result["doom_contribution"], low_result["doom_contribution"], "Higher-capability rival contributes more doom")

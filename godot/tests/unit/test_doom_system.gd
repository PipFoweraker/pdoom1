extends GutTest
## Unit tests for DoomSystem -- ADR-0015 nine-stream accumulating-rate model.
## doom_rate = sum of NAMED STREAMS read from the DQ-21 world-state intermediaries; no
## action/event writes doom directly (ledger/risk arrive as routed STREAM INPUTS).

# ============================================================================
# HELPERS
# ============================================================================

func _create_doom_system() -> DoomSystem:
	return DoomSystem.new()

func _create_minimal_game_state() -> GameState:
	return GameState.new("test_seed")

# ============================================================================
# DOOM CLAMPING (Issue #488) -- via calculate_doom_change (the single authority)
# ============================================================================

func test_doom_clamped_to_upper_bound():
	# A routed stream input that would push past 100 clamps on the next tick.
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.current_doom = 95.0
	ds.add_stream_input("ledger", 20.0)
	ds.calculate_doom_change(state)
	assert_eq(ds.current_doom, 100.0, "Doom level clamps to 100")

func test_doom_clamped_to_lower_bound():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.current_doom = 5.0
	ds.add_stream_input("ledger", -20.0)
	ds.calculate_doom_change(state)
	assert_eq(ds.current_doom, 0.0, "Doom level clamps to 0")

func test_doom_clamping_in_calculate_doom_change():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.current_doom = 99.9
	# A large frontier makes the overhang stream tip it over 100.
	state.frontier_capability = {"player": 1000000.0}
	var result = ds.calculate_doom_change(state)
	assert_eq(ds.current_doom, 100.0, "Doom clamps to 100 after calculation")
	assert_eq(result["new_doom"], 100.0, "Result reports clamped value")

# ============================================================================
# CALCULATE_DOOM_CHANGE STRUCTURE + STREAMS
# ============================================================================

func test_calculate_doom_change_returns_expected_structure():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	var result = ds.calculate_doom_change(state)
	for key in ["total_change", "raw_change", "momentum", "velocity", "sources", "streams", "new_doom", "rate", "level", "trend"]:
		assert_has(result, key, "Result should have %s" % key)

func test_baseline_stream_equals_ambient_risk():
	# The baseline stream reads the ambient_risk intermediary (seeded from doom.base_per_turn).
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	var result = ds.calculate_doom_change(state)
	assert_almost_eq(result["sources"]["baseline"], Balance.num("doom.base_per_turn", 0.06), 0.0001, "baseline stream == ambient_risk")

func test_overhang_stream_grows_with_frontier():
	# Overhang converts accumulated frontier (minus absorption) into hazard.
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	state.frontier_capability = {"player": 5000.0}
	state.safety_absorption = 0.0
	var result = ds.calculate_doom_change(state)
	assert_gt(result["sources"]["overhang"], 0.0, "overhang > 0 when frontier exceeds absorption")

func test_safety_absorption_reduces_overhang():
	# Absorption offsets frontier in the overhang gap (and clamps the stream at 0).
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	state.frontier_capability = {"rivalX": 3000.0}
	state.safety_absorption = 100000.0  # absorption exceeds frontier -> clamped to 0
	var result = ds.calculate_doom_change(state)
	assert_eq(result["sources"]["overhang"], 0.0, "overhang clamps at 0 when absorption exceeds frontier (v1 R2-Q9)")

func test_alarm_stream_is_negative_relief():
	# global_alarm produces a small NEGATIVE stream (the natively-negative component).
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	state.global_alarm = 50.0
	var result = ds.calculate_doom_change(state)
	assert_lt(result["sources"]["alarm"], 0.0, "alarm stream is a negative relief")

# ============================================================================
# STREAM INPUTS (ledger/risk routed, not parallel-written) -- ADR-0015 / #638
# ============================================================================

func test_stream_input_is_buffered_not_written_directly():
	var ds = _create_doom_system()
	ds.current_doom = 50.0
	ds.add_stream_input("ledger", 10.0)
	assert_eq(ds.current_doom, 50.0, "stream input does NOT write the level directly")

func test_stream_input_lands_on_next_tick():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.current_doom = 50.0
	ds.add_stream_input("ledger", 10.0)
	var result = ds.calculate_doom_change(state)
	assert_almost_eq(result["sources"]["ledger"], 10.0, 0.01, "ledger input appears in its named stream")
	assert_gt(ds.current_doom, 59.0, "level integrated the ledger input")

func test_add_event_doom_routes_risk_to_panic():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.add_event_doom(5.0, "risk_capability")
	var result = ds.calculate_doom_change(state)
	assert_almost_eq(result["sources"]["panic"], 5.0, 0.01, "risk shocks route to the panic stream")

func test_set_rival_doom_contribution_is_retired_noop():
	# Rivals no longer emit direct doom; the shim is a no-op sink.
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.set_rival_doom_contribution(7.0)
	var result = ds.calculate_doom_change(state)
	assert_false(result["sources"].has("rivals"), "there is no 'rivals' doom stream anymore")

# ============================================================================
# MOMENTUM (gated trend modifier)
# ============================================================================

func test_momentum_capped_positive():
	var ds = _create_doom_system()
	ds.doom_momentum = 10.0
	ds._calculate_momentum(5.0)
	assert_true(ds.doom_momentum <= ds.momentum_cap, "Momentum capped at momentum_cap")

func test_momentum_capped_negative():
	var ds = _create_doom_system()
	ds.doom_momentum = -10.0
	ds._calculate_momentum(-5.0)
	assert_true(ds.doom_momentum >= -ds.momentum_cap, "Negative momentum capped")

# ============================================================================
# STATUS BANDS (ThemeManager canonical bands)
# ============================================================================

func test_get_doom_status_nominal():
	var ds = _create_doom_system(); ds.current_doom = 10.0
	assert_eq(ds.get_doom_status(), "nominal", "Doom < 15 is 'nominal'")

func test_get_doom_status_elevated():
	var ds = _create_doom_system(); ds.current_doom = 20.0
	assert_eq(ds.get_doom_status(), "elevated", "Doom 15-36 is 'elevated'")

func test_get_doom_status_terminal():
	var ds = _create_doom_system(); ds.current_doom = 95.0
	assert_eq(ds.get_doom_status(), "terminal", "Doom >= 92 is 'terminal'")

# ============================================================================
# PER-STREAM API (F3 overlay data + two instruments, DQ-21)
# ============================================================================

func test_two_instrument_readouts():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	ds.calculate_doom_change(state)
	assert_eq(ds.get_doom_level(), ds.current_doom, "get_doom_level == accumulated level")
	assert_eq(ds.get_doom_rate(), ds.doom_rate, "get_doom_rate == most recent rate")

func test_stream_contributions_and_dominant():
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	state.frontier_capability = {"player": 50000.0}  # make overhang the dominant stream
	ds.calculate_doom_change(state)
	var contribs = ds.get_stream_contributions()
	assert_has(contribs, "overhang", "stream contributions include overhang")
	assert_eq(ds.get_dominant_stream(), "overhang", "overhang dominates with a large frontier")

# ============================================================================
# TREND TELEMETRY INVARIANT (N=6) -- instrumentation, never a clamp
# ============================================================================

func test_trend_invariant_never_clamps_negative_rate():
	# A sustained negative rate is LEGAL (the engine never forces the sum positive).
	var ds = _create_doom_system()
	var state = _create_minimal_game_state()
	state.global_alarm = 10000.0  # a big alarm relief -> negative rate
	var result = ds.calculate_doom_change(state)
	assert_lt(result["rate"], 0.0, "negative rate is permitted (no clamp)")

# ============================================================================
# TREND READOUT
# ============================================================================

func test_get_doom_trend_stable():
	var ds = _create_doom_system(); ds.doom_velocity = 0.0
	assert_eq(ds._get_doom_trend(), "stable", "Near-zero velocity is 'stable'")

func test_get_doom_trend_increasing():
	var ds = _create_doom_system(); ds.doom_velocity = 1.0
	assert_eq(ds._get_doom_trend(), "increasing", "Positive velocity is 'increasing'")

func test_get_doom_trend_strongly_decreasing():
	var ds = _create_doom_system(); ds.doom_velocity = -3.0
	assert_eq(ds._get_doom_trend(), "strongly_decreasing", "High negative velocity is 'strongly_decreasing'")

# ============================================================================
# SERIALIZATION
# ============================================================================

func test_to_dict_serialization():
	var ds = _create_doom_system()
	ds.current_doom = 75.0
	ds.doom_velocity = 2.5
	ds.doom_momentum = 3.0
	var dict = ds.to_dict()
	assert_eq(dict["current_doom"], 75.0, "Serialized doom matches")
	assert_eq(dict["doom_velocity"], 2.5, "Serialized velocity matches")
	assert_eq(dict["doom_momentum"], 3.0, "Serialized momentum matches")
	assert_has(dict, "doom_sources", "Includes doom_sources (streams)")
	assert_has(dict, "rate_history", "Includes rate_history")

func test_from_dict_deserialization():
	var ds = _create_doom_system()
	var data = {
		"current_doom": 65.0,
		"doom_velocity": -1.5,
		"doom_momentum": -2.0,
		"doom_sources": {"baseline": 0.06, "ledger": 5.0},
		"rate_history": [1.0, 2.0],
	}
	ds.from_dict(data)
	assert_eq(ds.current_doom, 65.0, "Deserialized doom matches")
	assert_eq(ds.doom_velocity, -1.5, "Deserialized velocity matches")
	assert_eq(ds.doom_momentum, -2.0, "Deserialized momentum matches")

func test_from_dict_handles_missing_keys():
	var ds = _create_doom_system()
	ds.from_dict({"current_doom": 40.0})
	assert_eq(ds.current_doom, 40.0, "Sets current_doom from partial data")
	assert_eq(ds.doom_velocity, 0.0, "Default for missing velocity")
	assert_eq(ds.doom_momentum, 0.0, "Default for missing momentum")

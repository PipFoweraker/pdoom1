extends GutTest
## Test the modular doom momentum system

func test_doom_system_initialization():
	var doom_sys = DoomSystem.new()
	assert_eq(doom_sys.current_doom, 50.0, "Should start at 50 doom")
	assert_eq(doom_sys.doom_momentum, 0.0, "Should start with 0 momentum")
	assert_eq(doom_sys.doom_velocity, 0.0, "Should start with 0 velocity")

func test_basic_doom_calculation_no_momentum():
	var state = GameState.new("test_doom_basic")
	var doom_sys = state.doom_system

	# Minimal setup - no staff, no rivals
	var result = doom_sys.calculate_doom_change(state)

	# Should have base doom only (+1.0)
	assert_almost_eq(result["raw_change"], 1.0, 0.1, "Should have +1 base doom")
	assert_gt(result["new_doom"], 50.0, "Doom should increase")

func test_momentum_accumulation():
	var state = GameState.new("test_momentum")
	var doom_sys = state.doom_system

	# Hire capability researchers to generate consistent doom increase
	state.capability_researchers = 2

	# Turn 1: Initial doom increase
	var result1 = doom_sys.calculate_doom_change(state)
	var doom_after_turn1 = result1["new_doom"]

	# Turn 2: Momentum should accumulate
	var result2 = doom_sys.calculate_doom_change(state)
	var doom_after_turn2 = result2["new_doom"]

	# Turn 3: More momentum
	var result3 = doom_sys.calculate_doom_change(state)

	# Momentum should be accumulating (positive momentum)
	assert_gt(doom_sys.doom_momentum, 0.0, "Should have positive momentum after 3 turns of doom increase")
	assert_gt(result3["total_change"], result1["total_change"], "Turn 3 change should be larger due to momentum")

func test_momentum_decay():
	var doom_sys = DoomSystem.new()

	# Manually set high momentum
	doom_sys.doom_momentum = 5.0

	# Calculate doom with neutral changes
	var state = GameState.new("test_decay")
	state.doom_system = doom_sys

	# Turn 1
	doom_sys.calculate_doom_change(state)
	var momentum_turn1 = doom_sys.doom_momentum

	# Turn 2
	doom_sys.calculate_doom_change(state)
	var momentum_turn2 = doom_sys.doom_momentum

	# Momentum should decay over time
	assert_lt(momentum_turn2, momentum_turn1, "Momentum should decay without sustained doom changes")

func test_safety_researchers_reduce_doom():
	var state = GameState.new("test_safety")
	var doom_sys = state.doom_system

	# Hire safety researchers + give them compute + manager
	state.safety_researchers = 3
	state.compute = 100.0
	state.managers = 1

	var result = doom_sys.calculate_doom_change(state)

	# Safety researchers should produce negative doom
	assert_lt(result["sources"]["safety"], 0.0, "Safety should reduce doom")
	# Expected: 3 researchers * 3.5 = -10.5 doom

func test_capability_researchers_increase_doom():
	var state = GameState.new("test_caps")
	var doom_sys = state.doom_system

	state.capability_researchers = 2

	var result = doom_sys.calculate_doom_change(state)

	# Capability research should increase doom
	assert_gt(result["sources"]["capabilities"], 0.0, "Capabilities should increase doom")
	# Expected: 2 * 3.0 = 6.0 doom

func test_doom_spiral_scenario():
	"""Test that risky play creates doom spiral via momentum"""
	var state = GameState.new("test_spiral")
	var doom_sys = state.doom_system

	# Risky setup: 5 capability researchers, 0 safety
	state.capability_researchers = 5

	# Run 5 turns
	var changes = []
	for i in range(5):
		var result = doom_sys.calculate_doom_change(state)
		changes.append(result["total_change"])

	# Doom changes should be increasing due to momentum
	assert_gt(changes[4], changes[0], "Turn 5 doom change should be larger than turn 1 (spiral)")
	assert_gt(doom_sys.doom_momentum, 1.0, "Should have significant positive momentum")

func test_safety_flywheel_scenario():
	"""Test that safety-focused play creates negative momentum"""
	var state = GameState.new("test_flywheel")
	var doom_sys = state.doom_system

	# Safety-focused setup: 4 safety researchers, 0 capability
	state.safety_researchers = 4
	state.compute = 100.0
	state.managers = 1

	# Run 5 turns
	var changes = []
	for i in range(5):
		var result = doom_sys.calculate_doom_change(state)
		changes.append(result["total_change"])

	# Doom should be decreasing consistently
	assert_lt(changes[0], 0.0, "Should have negative doom change")
	assert_lt(doom_sys.doom_momentum, 0.0, "Should have negative momentum (safety flywheel)")

func test_doom_source_tracking():
	var state = GameState.new("test_sources")
	var doom_sys = state.doom_system

	state.safety_researchers = 2
	state.capability_researchers = 1
	state.compute = 100.0
	state.managers = 1

	var result = doom_sys.calculate_doom_change(state)

	# Check all sources are tracked
	assert_has(result["sources"], "base")
	assert_has(result["sources"], "capabilities")
	assert_has(result["sources"], "safety")
	assert_has(result["sources"], "momentum")

	# Verify values
	assert_eq(result["sources"]["base"], 1.0, "Base doom should be 1.0")
	assert_almost_eq(result["sources"]["capabilities"], 3.0, 0.1, "Caps doom should be 3.0")
	assert_lt(result["sources"]["safety"], 0.0, "Safety should be negative")

func test_momentum_cap():
	"""Test that momentum doesn't grow infinitely"""
	var doom_sys = DoomSystem.new()
	var state = GameState.new("test_cap")
	state.doom_system = doom_sys

	# Create extreme doom increase
	state.capability_researchers = 10

	# Run many turns to try to build extreme momentum
	for i in range(20):
		doom_sys.calculate_doom_change(state)

	# Momentum should be capped
	assert_lte(abs(doom_sys.doom_momentum), doom_sys.momentum_cap, "Momentum should be capped at %s" % doom_sys.momentum_cap)

func test_doom_trend_detection():
	var doom_sys = DoomSystem.new()

	# Test strongly increasing
	doom_sys.doom_velocity = 3.0
	assert_eq(doom_sys._get_doom_trend(), "strongly_increasing")

	# Test increasing
	doom_sys.doom_velocity = 1.0
	assert_eq(doom_sys._get_doom_trend(), "increasing")

	# Test stable
	doom_sys.doom_velocity = 0.0
	assert_eq(doom_sys._get_doom_trend(), "stable")

	# Test decreasing
	doom_sys.doom_velocity = -1.0
	assert_eq(doom_sys._get_doom_trend(), "decreasing")

	# Test strongly decreasing
	doom_sys.doom_velocity = -3.0
	assert_eq(doom_sys._get_doom_trend(), "strongly_decreasing")

func test_doom_status_thresholds():
	var doom_sys = DoomSystem.new()

	doom_sys.current_doom = 20.0
	assert_eq(doom_sys.get_doom_status(), "safe")

	doom_sys.current_doom = 40.0
	assert_eq(doom_sys.get_doom_status(), "warning")

	doom_sys.current_doom = 60.0
	assert_eq(doom_sys.get_doom_status(), "danger")

	doom_sys.current_doom = 80.0
	assert_eq(doom_sys.get_doom_status(), "critical")

	doom_sys.current_doom = 95.0
	assert_eq(doom_sys.get_doom_status(), "catastrophic")

func test_integration_with_game_state():
	"""Test that doom system integrates with game state properly"""
	var state = GameState.new("test_integration")

	# Initial doom should sync
	assert_eq(state.doom, 50.0)
	assert_eq(state.doom_system.current_doom, 50.0)

	# Hire staff and run turn
	state.safety_researchers = 2
	state.compute = 100.0
	state.managers = 1

	var turn_mgr = TurnManager.new(state)
	var result = turn_mgr.execute_turn()

	# Doom should be synced after turn
	assert_eq(state.doom, state.doom_system.current_doom, "Doom should sync between systems")

func test_doom_serialization():
	"""Test that doom system can save/load"""
	var doom_sys = DoomSystem.new()
	doom_sys.current_doom = 60.0
	doom_sys.doom_momentum = 2.5
	doom_sys.doom_velocity = 1.8

	# Serialize
	var data = doom_sys.to_dict()

	# Create new system and deserialize
	var doom_sys2 = DoomSystem.new()
	doom_sys2.from_dict(data)

	# Verify
	assert_eq(doom_sys2.current_doom, 60.0)
	assert_eq(doom_sys2.doom_momentum, 2.5)
	assert_eq(doom_sys2.doom_velocity, 1.8)

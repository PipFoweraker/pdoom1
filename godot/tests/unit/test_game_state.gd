extends GutTest
## Unit tests for GameState class

func test_game_state_initialization_defaults():
	# Test that GameState initializes with correct default values
	var state = GameState.new("test_seed")

	assert_eq(state.money, 245000.0, "Should start with $245,000")
	assert_eq(state.compute, 100.0, "Should start with 100 compute")
	assert_eq(state.research, 0.0, "Should start with 0 research")
	assert_eq(state.papers, 0.0, "Should start with 0 papers")
	assert_eq(state.reputation, 50.0, "Should start with 50 reputation")
	# Start doom is Balance-driven (dial 2, #638: the 2017 spawn starts LOW -- 20, was 50).
	assert_eq(state.doom, Balance.num("starting_resources.doom", 20.0), "Start doom matches Balance starting_resources.doom")
	# T2: no AP pool. The founder starts a fresh PLAN MONTH with the Balance grant.
	assert_eq(state.attention_per_month, Balance.inum("attention.per_month", 20), "Attention grant matches Balance")
	assert_eq(state.get_available_attention(), state.attention_per_month, "Full month's Attention available at boot")
	assert_eq(state.turn, 0, "Should start at turn 0")
	assert_false(state.game_over, "Game should not be over initially")
	assert_false(state.victory, "Should not be victorious initially")

func test_game_state_seed_is_set():
	# Test that seed is stored correctly
	var state = GameState.new("custom_seed_123")

	assert_eq(state.game_seed_str, "custom_seed_123", "Seed should be stored")

func test_game_state_staff_initialization():
	# Test that staff counts start at zero
	var state = GameState.new("test_seed")

	assert_eq(state.safety_researchers, 0, "Should start with 0 safety researchers")
	assert_eq(state.capability_researchers, 0, "Should start with 0 capability researchers")
	assert_eq(state.compute_engineers, 0, "Should start with 0 compute engineers")
	assert_eq(state.get_total_staff(), 0, "Total staff should be 0")

func test_can_afford_sufficient_resources():
	# Test can_afford returns true when resources are sufficient
	var state = GameState.new("test_seed")

	assert_true(state.can_afford({"money": 50000}), "Should afford $50k")
	assert_true(state.can_afford({"compute": 50}), "Should afford 50 compute")
	assert_true(state.can_afford({"attention": 2}), "Should afford 2 Attention")
	assert_true(state.can_afford({"money": 50000, "attention": 1}), "Should afford combo")

func test_can_afford_insufficient_resources():
	# Test can_afford returns false when resources are insufficient
	var state = GameState.new("test_seed")

	assert_false(state.can_afford({"money": 300000}), "Should not afford $300k")
	assert_false(state.can_afford({"compute": 500}), "Should not afford 500 compute")
	assert_false(state.can_afford({"attention": 999}), "Should not afford 999 Attention")
	assert_false(state.can_afford({"money": 50000, "compute": 500}), "Should not afford if one resource insufficient")

func test_spend_resources_deducts_correctly():
	# Test spend_resources deducts the correct amounts
	var state = GameState.new("test_seed")

	state.spend_resources({"money": 10000})
	assert_eq(state.money, 235000.0, "Money should decrease by $10k")

	var attention_before := state.get_available_attention()
	state.spend_resources({"compute": 20, "attention": 1})
	assert_eq(state.compute, 80.0, "Compute should decrease by 20")
	assert_eq(state.get_available_attention(), attention_before - 1, "Attention should decrease by 1")

func test_add_resources_increases_correctly():
	# Test add_resources increases the correct amounts
	var state = GameState.new("test_seed")

	state.add_resources({"money": 50000})
	assert_eq(state.money, 295000.0, "Money should increase by $50k")

	state.add_resources({"research": 25, "papers": 3})
	assert_eq(state.research, 25.0, "Research should increase by 25")
	assert_eq(state.papers, 3.0, "Papers should increase by 3")

func test_add_resources_clamps_doom():
	# Test that doom is clamped to [0, 100]
	var state = GameState.new("test_seed")

	# Test upper bound (start doom is Balance-driven, so pin it explicitly first)
	state.doom = 50.0
	state.add_resources({"doom": 60})
	assert_eq(state.doom, 100.0, "Doom should be clamped to 100")

	# Test lower bound
	state.doom = 10.0
	state.add_resources({"doom": -20})
	assert_eq(state.doom, 0.0, "Doom should be clamped to 0")

func test_add_resources_doom_write_is_clobbered_by_the_doom_engine():
	## ADR-0015 S-ticket CLOBBER GUARD (#967 Parent 1).
	## `add_resources({"doom": N})` still moves `state.doom` in a direct-state context (the
	## test above depends on that), which is exactly why the bug was invisible for so long:
	## turn resolution REASSIGNS `state.doom = doom_system.current_doom`
	## (turn_manager.gd _step_resolve_doom), so the parallel write never survives a real turn.
	## This test PINS the clobber. It must stay red-if-removed, because the wrong fix is to
	## make the parallel write stick -- the doom LEVEL is single-authority (DoomSystem), and
	## content that wants to move it writes a world-state INTERMEDIARY instead
	## (events.gd effect loop -> add_event_doom / global_alarm / safety_absorption / ...).
	var state = GameState.new("clobber_guard_seed")
	assert_not_null(state.doom_system, "GameState owns a DoomSystem")
	state.doom_system.current_doom = 42.0
	state.doom = 42.0

	state.add_resources({"doom": 25.0})
	assert_eq(state.doom, 67.0, "the raw sink does move state.doom before resolution")

	var tm: TurnManager = autofree(TurnManager.new(state))
	tm.execute_turn()

	assert_eq(state.doom, state.doom_system.current_doom,
		"after resolution the doom level is whatever DoomSystem says -- single authority")
	assert_lt(state.doom, 67.0,
		"the +25 parallel write was discarded, not coincidentally preserved")

func test_get_total_staff_counts_all_types():
	# Test get_total_staff sums all staff types
	var state = GameState.new("test_seed")

	state.safety_researchers = 3
	state.capability_researchers = 2
	state.compute_engineers = 4

	assert_eq(state.get_total_staff(), 9, "Total staff should be 9")

func test_check_win_lose_doom_zero_no_victory():
	# DQ-1 / ADR-0002: there is NO victory condition. doom<=0 must NOT end the game.
	var state = GameState.new("test_seed")
	state.doom = 0.0
	# Must also set doom_system since check_win_lose syncs from it
	if state.doom_system:
		state.doom_system.current_doom = 0.0

	state.check_win_lose()

	assert_false(state.game_over, "doom<=0 must not end the game (no victory condition)")
	assert_false(state.victory, "There is no victory condition (ADR-0002)")

func test_check_win_lose_doom_defeat():
	# Test defeat when doom reaches 100
	var state = GameState.new("test_seed")
	state.doom = 100.0
	if state.doom_system:
		state.doom_system.current_doom = 100.0

	state.check_win_lose()

	assert_true(state.game_over, "Game should be over")
	assert_false(state.victory, "Should not be victorious")

func test_check_win_lose_reputation_defeat():
	# Test defeat when reputation reaches 0
	var state = GameState.new("test_seed")
	state.reputation = 0.0

	state.check_win_lose()

	assert_true(state.game_over, "Game should be over")
	assert_false(state.victory, "Should not be victorious")

func test_to_dict_serialization():
	# Test that to_dict properly serializes state
	var state = GameState.new("test_seed")
	state.money = 75000
	state.safety_researchers = 2
	state.turn = 5

	var dict = state.to_dict()

	assert_eq(dict["money"], 75000, "Serialized money should match")
	assert_eq(dict["safety_researchers"], 2, "Serialized staff should match")
	assert_eq(dict["turn"], 5, "Serialized turn should match")
	assert_has(dict, "doom", "Should include doom")
	assert_has(dict, "reputation", "Should include reputation")
	assert_has(dict, "attention", "Should include Attention")
	assert_has(dict, "planning_hours_left", "Should include planning hours")
	assert_has(dict, "operating_hours_left", "Should include operating hours")

func test_queued_actions_initialization():
	# Test that queued_actions starts empty
	var state = GameState.new("test_seed")

	assert_eq(state.queued_actions.size(), 0, "Queued actions should start empty")

func test_rng_initialization():
	# Test that RNG is initialized from seed
	var state = GameState.new("test_seed")

	assert_not_null(state.rng, "RNG should be initialized")

	# Test determinism: same seed should give same random values
	var state2 = GameState.new("test_seed")

	var val1 = state.rng.randf()
	var val2 = state2.rng.randf()

	assert_eq(val1, val2, "Same seed should produce same random values")

# FIX #407: Action validation tests for reputation costs
func test_can_afford_reputation_sufficient():
	# Test can_afford returns true when reputation is sufficient (FIX #407)
	var state = GameState.new("test_seed")

	assert_true(state.can_afford({"reputation": 5}), "Should afford 5 reputation")
	assert_true(state.can_afford({"reputation": 50}), "Should afford 50 reputation (exact match)")
	assert_true(state.can_afford({"reputation": 10, "attention": 1}), "Should afford combo with reputation")

func test_can_afford_reputation_insufficient():
	# Test can_afford returns false when reputation is insufficient (FIX #407)
	var state = GameState.new("test_seed")

	assert_false(state.can_afford({"reputation": 100}), "Should not afford 100 reputation")
	assert_false(state.can_afford({"reputation": 51}), "Should not afford 51 reputation")
	assert_false(state.can_afford({"money": 10000, "reputation": 60}), "Should not afford if reputation insufficient")

func test_spend_resources_reputation_deduction():
	# Test spend_resources deducts reputation correctly (FIX #407)
	var state = GameState.new("test_seed")

	state.spend_resources({"reputation": 10})
	assert_eq(state.reputation, 40.0, "Reputation should decrease by 10")

	var att_before := state.get_available_attention()
	state.spend_resources({"reputation": 5, "attention": 1})
	assert_eq(state.reputation, 35.0, "Reputation should decrease by another 5")
	assert_eq(state.get_available_attention(), att_before - 1, "Attention should also decrease")

func test_spend_resources_reputation_clamped_to_zero():
	# Test that reputation is clamped to 0 when spending
	# Note: spend_resources validates can_afford first, so this bypasses validation
	var state = GameState.new("test_seed")
	state.reputation = 10.0

	# Spend exactly what we have (should work)
	state.spend_resources({"reputation": 10})
	assert_eq(state.reputation, 0.0, "Reputation should reach 0")

func test_action_validation_fundraise_with_insufficient_reputation():
	# Test that fundraise_big action is correctly blocked without enough reputation (FIX #407)
	# fundraise_big costs 2 AP + 8 reputation
	var state = GameState.new("test_seed")
	state.reputation = 5.0  # Below 8 required

	var fundraise_action = GameActions.get_action_by_id("fundraise_big")
	assert_false(fundraise_action.is_empty(), "fundraise_big action should exist")
	assert_false(state.can_afford(fundraise_action["costs"]), "Should not afford fundraise_big with only 5 reputation")

func test_action_validation_fundraise_with_sufficient_reputation():
	# Test that fundraise_big action is allowed with enough reputation (FIX #407)
	# fundraise_big costs 2 Attention + 8 reputation
	var state = GameState.new("test_seed")
	state.reputation = 50.0  # Default starting value (well above 8)

	var fundraise_action = GameActions.get_action_by_id("fundraise_big")
	assert_true(state.can_afford(fundraise_action["costs"]), "Should afford fundraise_big with 50 reputation and a fresh Attention month")

# FIX #424: Unmanaged employee productivity tests
func test_get_unmanaged_count_legacy():
	# Test get_unmanaged_count with legacy staff counts
	var state = GameState.new("test_seed")

	# 12 researchers with 0 managers (base capacity = 9)
	state.safety_researchers = 8
	state.capability_researchers = 4
	state.managers = 0

	assert_eq(state.get_unmanaged_count(), 3, "Should have 3 unmanaged (12 - 9 capacity)")

func test_get_unmanaged_count_with_manager():
	# Test get_unmanaged_count when managers increase capacity
	# With 1 manager, capacity = 1*9 = 9 (managers > 0 uses managers*9 formula)
	var state = GameState.new("test_seed")

	state.safety_researchers = 8
	state.managers = 1  # Capacity = 9

	assert_eq(state.get_unmanaged_count(), 0, "Should have 0 unmanaged with 8 staff and 1 manager")

func test_get_unmanaged_count_uses_researchers_array():
	# Test that get_unmanaged_count uses researchers array when populated (FIX #424)
	var state = GameState.new("test_seed")

	# Add 12 researchers via the new system
	for i in range(12):
		var researcher = Researcher.new()
		researcher.generate_random(state.rng)
		state.add_researcher(researcher)

	state.managers = 0  # Base capacity = 9

	# Should use researchers array (12), not legacy counts
	assert_eq(state.get_unmanaged_count(), 3, "Should use researchers array size for unmanaged count")

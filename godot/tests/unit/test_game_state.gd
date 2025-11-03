extends GutTest
## Unit tests for GameState class

func test_game_state_initialization_defaults():
	# Test that GameState initializes with correct default values
	var state = GameState.new("test_seed")

	assert_eq(state.money, 100000.0, "Should start with $100,000")
	assert_eq(state.compute, 100.0, "Should start with 100 compute")
	assert_eq(state.research, 0.0, "Should start with 0 research")
	assert_eq(state.papers, 0.0, "Should start with 0 papers")
	assert_eq(state.reputation, 50.0, "Should start with 50 reputation")
	assert_eq(state.doom, 50.0, "Should start with 50 doom")
	assert_eq(state.action_points, 3, "Should start with 3 AP")
	assert_eq(state.turn, 0, "Should start at turn 0")
	assert_false(state.game_over, "Game should not be over initially")
	assert_false(state.victory, "Should not be victorious initially")

func test_game_state_seed_is_set():
	# Test that seed is stored correctly
	var state = GameState.new("custom_seed_123")

	assert_eq(state.seed, "custom_seed_123", "Seed should be stored")

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
	assert_true(state.can_afford({"action_points": 2}), "Should afford 2 AP")
	assert_true(state.can_afford({"money": 50000, "action_points": 1}), "Should afford combo")

func test_can_afford_insufficient_resources():
	# Test can_afford returns false when resources are insufficient
	var state = GameState.new("test_seed")

	assert_false(state.can_afford({"money": 200000}), "Should not afford $200k")
	assert_false(state.can_afford({"compute": 500}), "Should not afford 500 compute")
	assert_false(state.can_afford({"action_points": 5}), "Should not afford 5 AP")
	assert_false(state.can_afford({"money": 50000, "compute": 500}), "Should not afford if one resource insufficient")

func test_spend_resources_deducts_correctly():
	# Test spend_resources deducts the correct amounts
	var state = GameState.new("test_seed")

	state.spend_resources({"money": 10000})
	assert_eq(state.money, 90000.0, "Money should decrease by $10k")

	state.spend_resources({"compute": 20, "action_points": 1})
	assert_eq(state.compute, 80.0, "Compute should decrease by 20")
	assert_eq(state.action_points, 2, "AP should decrease by 1")

func test_add_resources_increases_correctly():
	# Test add_resources increases the correct amounts
	var state = GameState.new("test_seed")

	state.add_resources({"money": 50000})
	assert_eq(state.money, 150000.0, "Money should increase by $50k")

	state.add_resources({"research": 25, "papers": 3})
	assert_eq(state.research, 25.0, "Research should increase by 25")
	assert_eq(state.papers, 3.0, "Papers should increase by 3")

func test_add_resources_clamps_doom():
	# Test that doom is clamped to [0, 100]
	var state = GameState.new("test_seed")

	# Test upper bound
	state.add_resources({"doom": 60})
	assert_eq(state.doom, 100.0, "Doom should be clamped to 100")

	# Test lower bound
	state.doom = 10.0
	state.add_resources({"doom": -20})
	assert_eq(state.doom, 0.0, "Doom should be clamped to 0")

func test_get_total_staff_counts_all_types():
	# Test get_total_staff sums all staff types
	var state = GameState.new("test_seed")

	state.safety_researchers = 3
	state.capability_researchers = 2
	state.compute_engineers = 4

	assert_eq(state.get_total_staff(), 9, "Total staff should be 9")

func test_check_win_lose_doom_victory():
	# Test victory when doom reaches 0
	var state = GameState.new("test_seed")
	state.doom = 0.0

	state.check_win_lose()

	assert_true(state.game_over, "Game should be over")
	assert_true(state.victory, "Should be victorious")

func test_check_win_lose_doom_defeat():
	# Test defeat when doom reaches 100
	var state = GameState.new("test_seed")
	state.doom = 100.0

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
	assert_eq(dict["total_staff"], 2, "Serialized total staff should match")
	assert_has(dict, "doom", "Should include doom")
	assert_has(dict, "reputation", "Should include reputation")
	assert_has(dict, "action_points", "Should include AP")

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
	assert_true(state.can_afford({"reputation": 10, "action_points": 1}), "Should afford combo with reputation")

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

	state.spend_resources({"reputation": 5, "action_points": 1})
	assert_eq(state.reputation, 35.0, "Reputation should decrease by another 5")
	assert_eq(state.action_points, 2, "AP should also decrease")

func test_spend_resources_reputation_clamped_to_zero():
	# Test that reputation is clamped to 0 when spending (FIX #407)
	var state = GameState.new("test_seed")
	state.reputation = 10.0

	# Spend more than available (shouldn't happen with validation, but test clamping)
	state.spend_resources({"reputation": 15})
	assert_eq(state.reputation, 0.0, "Reputation should be clamped to 0, not negative")

func test_action_validation_fundraise_with_insufficient_reputation():
	# Test that fundraise action is correctly blocked without enough reputation (FIX #407)
	var state = GameState.new("test_seed")
	state.reputation = 3.0  # Fundraise costs 5 reputation

	var fundraise_action = GameActions.get_action_by_id("fundraise")
	assert_false(fundraise_action.is_empty(), "Fundraise action should exist")
	assert_false(state.can_afford(fundraise_action["costs"]), "Should not afford fundraise with only 3 reputation")

func test_action_validation_fundraise_with_sufficient_reputation():
	# Test that fundraise action is allowed with enough reputation (FIX #407)
	var state = GameState.new("test_seed")
	state.reputation = 50.0  # Default starting value
	state.action_points = 3

	var fundraise_action = GameActions.get_action_by_id("fundraise")
	assert_true(state.can_afford(fundraise_action["costs"]), "Should afford fundraise with 50 reputation and 3 AP")

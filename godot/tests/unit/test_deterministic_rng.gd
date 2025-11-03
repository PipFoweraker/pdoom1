extends GutTest
## Unit tests for deterministic RNG functionality

func test_same_seed_produces_same_sequence():
	# Test that same seed produces identical random sequences
	var state1 = GameState.new("test_seed_123")
	var state2 = GameState.new("test_seed_123")

	var sequence1 = []
	var sequence2 = []

	for i in range(10):
		sequence1.append(state1.rng.randf())
		sequence2.append(state2.rng.randf())

	assert_eq(sequence1, sequence2, "Same seed should produce identical sequences")

func test_different_seeds_produce_different_sequences():
	# Test that different seeds produce different sequences
	var state1 = GameState.new("seed_a")
	var state2 = GameState.new("seed_b")

	var sequence1 = []
	var sequence2 = []

	for i in range(10):
		sequence1.append(state1.rng.randf())
		sequence2.append(state2.rng.randf())

	assert_ne(sequence1, sequence2, "Different seeds should produce different sequences")

func test_rng_state_persists_across_calls():
	# Test that RNG state advances correctly
	var state = GameState.new("test_seed")

	var val1 = state.rng.randf()
	var val2 = state.rng.randf()
	var val3 = state.rng.randf()

	# Values should all be different (extremely unlikely to be same)
	assert_ne(val1, val2, "Sequential RNG calls should produce different values")
	assert_ne(val2, val3, "Sequential RNG calls should produce different values")
	assert_ne(val1, val3, "Sequential RNG calls should produce different values")

func test_rng_reproducibility_after_reset():
	# Test that resetting with same seed reproduces sequence
	var state = GameState.new("test_seed")
	var first_sequence = []

	for i in range(5):
		first_sequence.append(state.rng.randf())

	# Create new state with same seed
	state = GameState.new("test_seed")
	var second_sequence = []

	for i in range(5):
		second_sequence.append(state.rng.randf())

	assert_eq(first_sequence, second_sequence, "Same seed should reproduce exact sequence after reset")

func test_rng_integer_generation():
	# Test that randi() also works deterministically
	var state1 = GameState.new("test_seed")
	var state2 = GameState.new("test_seed")

	var ints1 = []
	var ints2 = []

	for i in range(10):
		ints1.append(state1.rng.randi())
		ints2.append(state2.rng.randi())

	assert_eq(ints1, ints2, "Integer RNG should also be deterministic")

func test_rng_range_generation():
	# Test that randi_range() works deterministically
	var state1 = GameState.new("test_seed")
	var state2 = GameState.new("test_seed")

	var ranges1 = []
	var ranges2 = []

	for i in range(10):
		ranges1.append(state1.rng.randi_range(1, 100))
		ranges2.append(state2.rng.randi_range(1, 100))

	assert_eq(ranges1, ranges2, "Ranged integer RNG should be deterministic")

func test_seed_hash_consistency():
	# Test that hash() function produces consistent results
	var seed = "test_seed"

	var state1 = GameState.new(seed)
	var state2 = GameState.new(seed)

	# Both should use hash(seed), verify they produce same sequence
	var val1 = state1.rng.randf()
	var val2 = state2.rng.randf()

	assert_eq(val1, val2, "Hash function should be consistent for same seed")

func test_empty_seed_generates_time_based_seed():
	# Test that empty seed generates different seeds (time-based)
	var state1 = GameState.new("")
	var state2 = GameState.new("")

	# Seeds should be different (time-based)
	assert_ne(state1.seed, state2.seed, "Empty seed should generate unique time-based seeds")

	# But each should still be deterministic with its own seed
	var saved_seed = state1.seed
	var state_copy = GameState.new(saved_seed)

	var val1 = state1.rng.randf()
	var val_copy = state_copy.rng.randf()

	assert_eq(val1, val_copy, "Even time-based seeds should be reproducible")

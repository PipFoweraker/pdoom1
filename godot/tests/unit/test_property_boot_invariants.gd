extends GutTest
## Property-based boot invariants (test-strategy uplift).
##
## Housemate's Jan advice, item (a): "some unit tests should be property-based."
## Instead of asserting one hand-picked seed boots correctly, this generates a
## DISTRIBUTION of seeds (deterministically, so the run is reproducible) plus
## deliberately awkward edge seeds, and asserts the SAME invariant holds for every
## one: a fresh GameState boots to an ACTIONABLE state.
##
## "Actionable" is the real contract a player depends on turn 0: the run is alive,
## resources are finite and sane, and at least one action is affordable. A
## single-case test can pass while a whole region of the seed space boots into an
## unplayable/game-over state; sampling the space catches that class.
##
## Fast tier: this only constructs GameState/TurnManager (no turn simulation), so
## hundreds of samples cost milliseconds -- cheap enough for the required gate.

const NUM_SAMPLES := 64
const GEN_SEED := 20260717  # fixed so a failure reproduces exactly

# Deliberately awkward inputs a fuzzer would find but a single example never covers.
# NOTE: built at runtime (see _generate_seeds) rather than as a const, because a const
# array must be a constant expression -- String.repeat() is a method call and is not.
func _edge_seeds() -> Array:
	return [
		"",                       # empty -> engine must synthesize a seed (see GameState._init)
		" ",                      # whitespace only
		"0",                      # numeric-looking
		"-1",                     # negative-looking
		"seed with spaces",       # spaces
		"UPPER/lower.mix-99",     # punctuation the hash must tolerate
		"a".repeat(4096),         # pathologically long
		"the-quick-brown-fox",    # ordinary
	]


func _generate_seeds() -> Array:
	# Deterministic pseudo-random seed strings from a fixed generator, so the sample
	# set is identical every run (a property test must be reproducible to be useful).
	var rng := RandomNumberGenerator.new()
	rng.seed = GEN_SEED
	const CHARS := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
	var seeds: Array = []
	for i in range(NUM_SAMPLES):
		var length := rng.randi_range(1, 24)
		var s := ""
		for _j in range(length):
			s += CHARS[rng.randi_range(0, CHARS.length() - 1)]
		seeds.append(s)
	seeds.append_array(_edge_seeds())
	return seeds


func _assert_actionable(game_seed: String, label: String) -> void:
	var state: GameState = autofree(GameState.new(game_seed))

	# Alive and at the start of the run.
	assert_false(state.game_over, "[%s] fresh game must not be game_over" % label)
	assert_eq(state.turn, 0, "[%s] fresh game starts at turn 0" % label)

	# Resources finite and sane (a NaN/inf here would silently poison every downstream
	# comparison, including the determinism hash).
	assert_true(is_finite(state.money), "[%s] money finite" % label)
	assert_gt(state.money, 0.0, "[%s] starts with positive money" % label)
	assert_true(is_finite(state.doom), "[%s] doom finite" % label)
	assert_between(state.doom, 0.0, 100.0, "[%s] doom within [0,100] and not yet lost" % label)
	assert_gt(state.action_points, 0, "[%s] has action points to spend" % label)

	# The core "actionable" claim: at least one action is affordable at boot. A run
	# that boots with nothing affordable is soft-locked from move one.
	var tm: TurnManager = autofree(TurnManager.new(state))
	var actions := tm.get_available_actions()
	assert_gt(actions.size(), 0, "[%s] action list is non-empty" % label)
	var any_affordable := false
	for a in actions:
		if a.get("affordable", false):
			any_affordable = true
			break
	assert_true(any_affordable, "[%s] at least one action affordable at boot (not soft-locked)" % label)


func test_any_seed_boots_to_actionable_state():
	for game_seed in _generate_seeds():
		var label: String = game_seed.substr(0, 24) if game_seed.length() > 0 else "<empty>"
		_assert_actionable(game_seed, label)


func test_distinct_seeds_produce_distinct_rng_streams():
	# Guards against a degenerate pass: if every seed collapsed to the same RNG state
	# the boot-invariant sweep above would be vacuously satisfied by one hidden case.
	var streams := {}
	var seeds := _generate_seeds()
	for game_seed in seeds:
		if game_seed == "":
			continue  # empty deliberately randomizes; not comparable
		var state: GameState = autofree(GameState.new(game_seed))
		streams[state.rng.seed] = true
	# Distinct textual seeds should overwhelmingly map to distinct rng seeds.
	assert_gt(streams.size(), int((seeds.size() - 1) * 0.9),
		"distinct seeds should yield distinct rng streams (else the sweep is near-vacuous)")

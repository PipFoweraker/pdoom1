extends GutTest
## LabNameGenerator tests (Pip 2026-08-06: "fix improving the random lab name
## generation mechanisms a bit" -- the old single-shape generator made every
## roll sound like the same beige institute).
##
## Pinned properties:
##   - deterministic under a seed (same seeded rng -> same sequence)
##   - real variety across draws (shape + word variety, not one shape)
##   - never malformed: non-empty, ASCII-only (house rule #744), no doubled
##     spaces, no leading/trailing space, no duplicate-adjacent words,
##     board-friendly length
##   - RNG isolation is structural: the generator draws ONLY from the rng the
##     caller passes, so the seeded run RNG (GameState.rng) cannot be touched
##     unless a caller hands it in -- and no caller does (UI-only usage).

const DRAWS := 500

func _batch(seed_value: int, count: int) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_value
	var out: Array = []
	for _i in range(count):
		out.append(LabNameGenerator.generate(rng))
	return out


func test_deterministic_under_a_seed():
	# Same seed -> identical sequence; different seed -> (overwhelmingly) not.
	var a := _batch(1234, 50)
	var b := _batch(1234, 50)
	assert_eq(a, b, "same seeded rng must reproduce the same name sequence")
	var c := _batch(99999, 50)
	assert_ne(a, c, "a different seed should produce a different sequence")


func test_variety_not_one_beige_institute():
	var names := _batch(42, DRAWS)
	var distinct := {}
	for n in names:
		distinct[n] = true
	assert_gt(distinct.size(), 100,
		"%d draws produced only %d distinct names -- pools/shapes too small" % [DRAWS, distinct.size()])

	# Every structural shape must actually be reachable: the acronym form
	# (contains a parenthesised expansion), the surname firm (contains " & "),
	# and the plain-word forms. 500 draws at the smallest weight (10%) miss a
	# shape with probability ~(0.9)^500 -- effectively never.
	var saw_acronym := false
	var saw_firm := false
	var saw_plain := false
	for n in names:
		if n.contains("("):
			saw_acronym = true
		elif n.contains(" & "):
			saw_firm = true
		else:
			saw_plain = true
	assert_true(saw_acronym, "acronym shape never rolled in %d draws" % DRAWS)
	assert_true(saw_firm, "surname-firm shape never rolled in %d draws" % DRAWS)
	assert_true(saw_plain, "institute/corporate/gallows shapes never rolled in %d draws" % DRAWS)


func test_never_malformed():
	var names := _batch(7, DRAWS)
	for n in names:
		var s: String = n
		assert_ne(s.strip_edges(), "", "empty name rolled")
		assert_eq(s, s.strip_edges(), "leading/trailing whitespace: '%s'" % s)
		assert_false(s.contains("  "), "doubled space in '%s'" % s)
		assert_lt(s.length(), 61, "board-unfriendly length (%d): '%s'" % [s.length(), s])
		for i in range(s.length()):
			assert_lt(s.unicode_at(i), 128, "non-ASCII char in '%s' (house rule #744)" % s)
		assert_false(LabNameGenerator._has_adjacent_duplicate(s),
			"duplicate adjacent words in '%s'" % s)


func test_adjacent_duplicate_guard_detects():
	# The guard itself must actually catch the failure it exists for --
	# otherwise test_never_malformed's last assertion is vacuously green.
	assert_true(LabNameGenerator._has_adjacent_duplicate("AI Safety Safety Research"))
	assert_true(LabNameGenerator._has_adjacent_duplicate("AI Safety safety Research"),
		"guard must be case-insensitive")
	assert_false(LabNameGenerator._has_adjacent_duplicate("AI Safety Research"))
	assert_false(LabNameGenerator._has_adjacent_duplicate("Voss & Okafor Containment"))

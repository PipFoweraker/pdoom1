extends GutTest
## Property-based invariant tests for Leaderboard (godot/scripts/leaderboard.gd)
## and the ADR-0002 comparator GameState.compare_score.
##
## Approach: a DETERMINISTIC seeded RandomNumberGenerator generates many (>=200)
## random ScoreEntry inputs per property, and we assert the invariant holds across
## all of them. Fixed seeds keep failures reproducible.
##
## Hermeticity: every board is constructed with a unique test-only seed string so
## its JSON filename never collides with a real leaderboard file, and we clear()
## it up front. Boards are Nodes -> autofree() so nothing leaks between cases.
##
## IMPORTANT BEHAVIOURAL NOTE (read before trusting the P2 test name):
## add_score() does NOT deduplicate by entry_uuid -- it unconditionally does
## entries.append(entry). The only entry_uuid logic is the rank-lookup loop. So the
## real, provable invariant is rank stability of the first occurrence on re-add;
## the "board size does not grow" half of naive idempotency is FALSE in production
## and is asserted here as characterization (documenting the no-dedup gap).

const CAP := 50  # Leaderboard.max_entries default; asserted in test_cap_matches_assumption.

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

var _board_counter := 0

func _fresh_board() -> Leaderboard:
	# Unique seed per board => unique user:// filename => no clobbering real files.
	_board_counter += 1
	var lb: Leaderboard = Leaderboard.new("test_prop_%d_%d" % [_board_counter, Time.get_ticks_usec()], "test")
	lb.clear()  # start empty and hermetic
	autofree(lb)
	return lb

func _rng(seed_val: int) -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = seed_val
	return r

func _make_entry(score: int, doom_integral: int) -> Leaderboard.ScoreEntry:
	# ScoreEntry.new(score, player_name, level, mode, duration, baseline, doom_integral, baseline_integral)
	return Leaderboard.ScoreEntry.new(score, "Lab", score, "test", 1.0, 0, doom_integral, 0)

func _cmp(a: Leaderboard.ScoreEntry, b: Leaderboard.ScoreEntry) -> int:
	return GameState.compare_score(a.score, a.doom_integral, b.score, b.doom_integral)

# ---------------------------------------------------------------------------
# sanity: the cap value this suite assumes
# ---------------------------------------------------------------------------

func test_cap_matches_assumption():
	var lb := _fresh_board()
	assert_eq(lb.max_entries, CAP, "suite assumes a cap of %d; leaderboard.gd changed it" % CAP)

# ---------------------------------------------------------------------------
# P1 ordering: get_top_scores(N) is sorted descending by the ADR-0002 comparator.
# ---------------------------------------------------------------------------

func test_property_ordering_sorted_descending():
	var total := 0
	for seed_val in [1, 2, 3]:
		var rng := _rng(seed_val)
		var lb := _fresh_board()
		for i in range(100):  # 3 seeds x 100 = 300 random inputs
			lb.add_score(_make_entry(rng.randi_range(0, 40), rng.randi_range(0, 40)))
			total += 1
		var top: Array = lb.get_top_scores(1000)
		assert_gt(top.size(), 0, "board should be non-empty after adds")
		for i in range(top.size() - 1):
			var prev: Leaderboard.ScoreEntry = top[i]
			var next: Leaderboard.ScoreEntry = top[i + 1]
			var c: int = GameState.compare_score(prev.score, prev.doom_integral, next.score, next.doom_integral)
			assert_true(c >= 0,
				"ordering violated at %d: compare(prev=(%d,%d), next=(%d,%d))=%d must be >=0"
				% [i, prev.score, prev.doom_integral, next.score, next.doom_integral, c])
	assert_true(total >= 200, "expected >=200 generated inputs, got %d" % total)

# ---------------------------------------------------------------------------
# P2 re-entry rank stability (the TRUE invariant; see behavioural note above).
# Re-adding an already-present entry object leaves the first occurrence's rank
# unchanged. Also characterizes the actual no-dedup behaviour (size grows).
# ---------------------------------------------------------------------------

func test_property_reentry_rank_stable():
	var checks := 0
	for seed_val in [11, 22, 33, 44, 55, 66]:
		var rng := _rng(seed_val)
		var lb := _fresh_board()
		# UNDER the cap (40 < 50) so the no-dedup growth is observable (not trimmed).
		# DISTINCT scores => compare_score never ties => ranks are fully stable
		# (Godot sort_custom is not guaranteed stable, so equal keys would flake).
		var scores: Array[int] = []
		for i in range(40):
			scores.append(i)
		# deterministic Fisher-Yates shuffle
		for i in range(scores.size() - 1, 0, -1):
			var j := rng.randi_range(0, i)
			var tmp := scores[i]
			scores[i] = scores[j]
			scores[j] = tmp
		var made: Array[Leaderboard.ScoreEntry] = []
		for s in scores:
			var e := _make_entry(s, rng.randi_range(0, 1000))
			made.append(e)
			lb.add_score(e)
			checks += 1
		# pick an entry currently sitting at rank > 1 so a broken uuid-match loop bites.
		var target: Leaderboard.ScoreEntry = null
		var rank_before := -1
		for i in range(1, lb.entries.size()):  # skip index 0 (rank 1)
			target = lb.entries[i]
			rank_before = i + 1
			break
		assert_not_null(target, "need a rank>1 entry to test")
		var size_before := lb.entries.size()
		var res: Dictionary = lb.add_score(target)  # re-add the SAME object (same entry_uuid)
		assert_eq(res["rank"], rank_before,
			"re-adding an existing entry must return its unchanged first-occurrence rank")
		# characterization of ACTUAL production behaviour: NO dedup -> board grew by 1.
		assert_eq(lb.entries.size(), size_before + 1,
			"documenting no-dedup: re-add appends a duplicate (board grows by 1)")
	assert_true(checks >= 200, "expected >=200 generated inputs, got %d" % checks)

# ---------------------------------------------------------------------------
# P3 cap: board never exceeds the cap, and the retained set is the top-cap
# (no dropped entry outranks the worst retained entry).
# ---------------------------------------------------------------------------

func test_property_cap_retains_top():
	for seed_val in [7, 8]:
		var rng := _rng(seed_val)
		var lb := _fresh_board()
		var all_entries: Array[Leaderboard.ScoreEntry] = []
		for i in range(300):  # >> cap; 2 seeds x 300 = 600 inputs
			var e := _make_entry(rng.randi_range(0, 500), rng.randi_range(0, 500))
			all_entries.append(e)
			lb.add_score(e)
			assert_true(lb.entries.size() <= CAP,
				"cap violated mid-add: size=%d > cap=%d" % [lb.entries.size(), CAP])
		assert_eq(lb.entries.size(), CAP, "board should be full at exactly the cap")
		# worst retained = last element (sorted descending).
		var worst_retained: Leaderboard.ScoreEntry = lb.entries[lb.entries.size() - 1]
		# every entry that did NOT survive must not outrank the worst retained.
		for e in all_entries:
			if lb.entries.has(e):
				continue
			var c: int = GameState.compare_score(worst_retained.score, worst_retained.doom_integral, e.score, e.doom_integral)
			assert_true(c >= 0,
				"dropped entry (%d,%d) outranks worst retained (%d,%d): compare=%d must be >=0"
				% [e.score, e.doom_integral, worst_retained.score, worst_retained.doom_integral, c])

# ---------------------------------------------------------------------------
# P4 rank monotonicity: a higher score never gets a worse (numerically larger)
# rank than a lower score via get_rank_for_score. Rank 0 = "not on board" = worst,
# mapped to a large sentinel so the comparison is total.
# ---------------------------------------------------------------------------

func _effective_rank(lb: Leaderboard, score: int) -> int:
	var r: int = lb.get_rank_for_score(score)
	return 0x7FFFFFFF if r == 0 else r  # 0 (off-board) is the worst possible rank

func test_property_rank_monotonic():
	var rng := _rng(99)
	var lb := _fresh_board()
	# under-cap board so get_rank_for_score exercises the full range of outcomes.
	for i in range(40):
		lb.add_score(_make_entry(rng.randi_range(0, 100), rng.randi_range(0, 100)))
	var checks := 0
	for i in range(250):  # 250 random score pairs
		var sa := rng.randi_range(0, 120)
		var sb := rng.randi_range(0, 120)
		var lo: int = min(sa, sb)
		var hi: int = max(sa, sb)
		var rank_hi := _effective_rank(lb, hi)
		var rank_lo := _effective_rank(lb, lo)
		assert_true(rank_hi <= rank_lo,
			"rank monotonicity violated: score %d rank %d worse than lower score %d rank %d"
			% [hi, rank_hi, lo, rank_lo])
		checks += 1
	assert_true(checks >= 200, "expected >=200 generated inputs, got %d" % checks)

# ---------------------------------------------------------------------------
# P5 comparator soundness: sign(compare(a,b)) == -sign(compare(b,a)), and score
# strictly dominates doom_integral (a strictly higher score always compares > 0
# regardless of either doom value).
# ---------------------------------------------------------------------------

func _sign(x: int) -> int:
	return 0 if x == 0 else (1 if x > 0 else -1)

func test_property_comparator_sound():
	var rng := _rng(1234)
	var checks := 0
	for i in range(250):  # 250 random (score,doom) pairs
		var sa := rng.randi_range(0, 50)
		var da := rng.randi_range(0, 50)
		var sb := rng.randi_range(0, 50)
		var db := rng.randi_range(0, 50)
		var ab: int = GameState.compare_score(sa, da, sb, db)
		var ba: int = GameState.compare_score(sb, db, sa, da)
		assert_eq(_sign(ab), -_sign(ba),
			"antisymmetry violated: compare(a,b)=%d compare(b,a)=%d" % [ab, ba])
		# score strictly dominates doom_integral.
		if sa > sb:
			assert_eq(ab, 1,
				"score dominance violated: score %d>%d must give compare==1 regardless of doom (%d vs %d), got %d"
				% [sa, sb, da, db, ab])
		elif sa < sb:
			assert_eq(ab, -1,
				"score dominance violated: score %d<%d must give compare==-1 regardless of doom (%d vs %d), got %d"
				% [sa, sb, da, db, ab])
		checks += 1
	assert_true(checks >= 200, "expected >=200 generated inputs, got %d" % checks)

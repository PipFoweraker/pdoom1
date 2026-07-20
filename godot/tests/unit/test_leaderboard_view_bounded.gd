extends GutTest
## Bounded-view / memory regression tests for the leaderboard screen
## (godot/scripts/ui/leaderboard_screen.gd).
##
## Context: opening the leaderboard on a huge accumulated population spiked memory
## and segfaulted the RELEASE build. The DATA is a deliberate substrate and must NOT
## be reduced; only the VIEW is bounded. These tests pin the two invariants that
## keep runtime memory bounded while every stored byte is preserved:
##
##  1. RENDER is page-bounded: no matter how large the population (5000 here), only
##     ~entries_per_page ROW NODES are ever instantiated -- never one node per entry.
##  2. LOAD does not leak: Leaderboard `extends Node` (NOT RefCounted), so the screen
##     must not RETAIN those Node instances. It now stores plain entry arrays and
##     frees the transient board Nodes, so loading leaves no orphan Nodes behind and
##     re-opening does not accumulate memory.

const SCREEN := preload("res://scenes/leaderboard_screen.tscn")

# ScoreEntry.new(score, player_name, level, mode, duration, baseline, doom_integral, baseline_integral)
func _make_entry(score: int) -> Leaderboard.ScoreEntry:
	return Leaderboard.ScoreEntry.new(score, "Lab %d" % score, score, "test", 1.0, 0, score % 7, 0)

func _make_screen():
	var screen = SCREEN.instantiate()
	add_child_autofree(screen)  # triggers _ready -> loads real user:// boards (may be empty in CI)
	return screen

func _huge_population(n: int) -> Array:
	# Already sorted descending (matches the screen's sort order) so page bounds are obvious.
	var entries: Array = []
	for i in range(n):
		entries.append(_make_entry(n - i))
	return entries

# --- Invariant 1: render is page-bounded even for a 5000-entry population ------

func test_render_is_page_bounded_for_huge_population():
	var screen = _make_screen()
	screen.filtered_entries = _huge_population(5000)
	screen.current_seed = "all"
	screen.current_page = 1
	screen._display_current_page()

	var count: int = screen.entries_container.get_child_count()
	assert_eq(count, screen.entries_per_page,
		"page 1 must instantiate exactly entries_per_page rows, got %d for a 5000-entry board" % count)
	# The whole point: memory is bounded -- we did NOT build a node per entry.
	assert_lt(count, 5000,
		"render must NOT instantiate a node per entry (that is the unbounded-memory bug)")

func test_paging_frees_prior_rows_and_stays_bounded():
	var screen = _make_screen()
	screen.filtered_entries = _huge_population(5000)
	screen.current_seed = "all"
	screen.current_page = 1
	screen._display_current_page()
	var after_page1: int = screen.entries_container.get_child_count()

	# Page forward several times: 5000/20 = 250 pages, so these are all full pages.
	for _p in range(5):
		screen._on_next_button_pressed()
	var after_paging: int = screen.entries_container.get_child_count()

	assert_eq(after_page1, screen.entries_per_page, "page 1 bounded to entries_per_page")
	assert_eq(after_paging, screen.entries_per_page,
		"paging must FREE the previous page's rows (bounded, not accumulating): got %d" % after_paging)

func test_last_partial_page_is_bounded():
	var screen = _make_screen()
	# 45 entries, 20/page -> page 3 holds the remaining 5 (still <= entries_per_page).
	screen.filtered_entries = _huge_population(45)
	screen.current_seed = "all"
	screen.current_page = 3
	screen._display_current_page()
	var count: int = screen.entries_container.get_child_count()
	assert_lte(count, screen.entries_per_page,
		"a partial last page never exceeds entries_per_page rows, got %d" % count)
	assert_eq(count, 5, "page 3 of a 45-entry board shows the trailing 5 entries")

# --- Invariant 2: loading does not retain / leak Leaderboard Nodes ------------

func test_load_stores_arrays_not_nodes_and_leaves_no_orphans():
	var screen = _make_screen()

	# Seed a few synthetic boards on disk with unique test-only seeds (no '__' in the
	# seed itself so filename parsing is unambiguous).
	var seeds: Array = []
	for i in range(3):
		var s := "zzzViewBounded%dx%d" % [i, Time.get_ticks_usec()]
		seeds.append(s)
		var lb := Leaderboard.new(s, "test")
		lb.clear()
		for j in range(5):
			lb.add_score(_make_entry(j))  # writes the file
		lb.free()

	var orphans_before: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	screen._load_all_leaderboards()
	var orphans_after: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)

	# Boards must be stored as PLAIN ARRAYS -- never retained Leaderboard Nodes.
	for s in seeds:
		var key := "%s (test)" % s
		assert_true(screen.all_leaderboards.has(key), "seeded board %s should be loaded" % key)
		var val = screen.all_leaderboards[key]
		assert_true(val is Array, "board must be stored as a plain Array (not a Node)")
		assert_false(val is Node, "board must NOT be a retained Leaderboard Node (that is the leak)")

	# Parsing every board must leave NO orphan Nodes -- each transient board is freed.
	assert_true(orphans_after <= orphans_before,
		"_load_all_leaderboards leaked %d orphan Node(s)" % (orphans_after - orphans_before))

	# Cleanup: remove the synthetic files so we don't pollute user://leaderboards.
	var dir := DirAccess.open("user://leaderboards")
	if dir:
		for s in seeds:
			dir.remove("leaderboard_%s__test.json" % s)

## --- Invariant 3: the DEFAULT open is lazy (does NOT parse every seed file) --------
## Opening the screen used to parse every leaderboard_*.json on every open (~5-7s with
## many boards). The fix: discover files cheaply (a dir listing, no parse) and parse only
## the current/most-relevant single board on open; the full all-seeds population is parsed
## lazily only when the user picks "All Seeds". This pins that the common open stays bounded.
func test_default_open_parses_at_most_one_board():
	# Seed several distinct boards on disk BEFORE opening the screen.
	var seeds: Array = []
	for i in range(4):
		var s := "zzzLazyOpen%dx%d" % [i, Time.get_ticks_usec()]
		seeds.append(s)
		var lb := Leaderboard.new(s, "test")
		lb.clear()
		lb.add_score(_make_entry(i + 1))  # writes the file
		lb.free()

	# Instantiating triggers _ready -> the cheap default open.
	var screen = _make_screen()

	# Discovery is cheap and COMPLETE: every file is known without being parsed.
	var known := 0
	for s in seeds:
		if screen._board_files.has("%s (test)" % s):
			known += 1
	assert_eq(known, seeds.size(), "discovery must list every board file (cheap, no parse)")

	# The open must have PARSED at most one board (the default), never the whole set,
	# and must NOT have built the full all-seeds aggregate.
	assert_lte(screen.all_leaderboards.size(), 1,
		"default open must parse <=1 board, but parsed %d" % screen.all_leaderboards.size())
	assert_false(screen._aggregate_loaded,
		"default open must NOT eagerly build the all-seeds aggregate")

	# Selecting "All Seeds" is what triggers the full (cached) parse -- and it is complete.
	screen.current_seed = "all"
	screen._filter_and_display()
	assert_true(screen._aggregate_loaded, "picking All Seeds loads the full aggregate")
	for s in seeds:
		assert_true(screen.all_leaderboards.has("%s (test)" % s),
			"all-seeds view must include every board (no data dropped)")

	# Cleanup: remove the synthetic files so we don't pollute user://leaderboards.
	var dir := DirAccess.open("user://leaderboards")
	if dir:
		for s in seeds:
			dir.remove("leaderboard_%s__test.json" % s)

func test_reload_does_not_accumulate_orphans():
	var screen = _make_screen()
	# Repeated loads (as happens on Refresh / re-open) must not grow orphan Nodes.
	screen._load_all_leaderboards()
	var baseline: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	for _i in range(3):
		screen._load_all_leaderboards()
	var after: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)
	assert_true(after <= baseline,
		"repeated loads leaked %d orphan Node(s) (re-open would accumulate memory)" % (after - baseline))

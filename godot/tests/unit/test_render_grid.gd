extends GutTest
## Guards RenderGrid (scripts/ui/office_floor/render_grid.gd), the a(3)-lite
## render-layer grid approved by the ADR-0018 amendment (2026-07-27).
##
## What is actually at risk here, and so what these tests pin:
##   - conversion ROUND-TRIPS: cell_at(cell_centre(c)) == c and
##     cell_at(cell_origin(c)) == c, for positive AND negative cells;
##   - NEGATIVE coordinates: the old hack used floor() on a screen-origin
##     lattice; integer truncation would fold -1..+1 into column 0, so the
##     floor-division behaviour is pinned explicitly;
##   - SNAP EDGES: a point exactly on a cell boundary belongs to the cell it
##     starts, not the one it ends -- half-open cells are what stops two
##     edge-to-edge props claiming the same cell;
##   - FOOTPRINT occupancy: claims skip (never steal) already-held cells, and
##     release() frees exactly what an owner held;
##   - row-major ENUMERATION order, which the sandbox's seeded furniture draw
##     depends on for determinism (ADR-0006 discipline).
##
## Headless by construction: RenderGrid has no scene tree, no autoload, and no
## sim dependency (the ADR-0018 arrow rule), so it needs no doubles.

const CELL := 32.0


func _grid(cell: Variant = CELL, origin: Vector2 = Vector2.ZERO) -> RenderGrid:
	return RenderGrid.new(cell, origin)


# --- Conversion round-trips ---------------------------------------------------
func test_centre_and_origin_round_trip_through_cell_at() -> void:
	var g := _grid()
	for c in [Vector2i(0, 0), Vector2i(1, 0), Vector2i(7, 3), Vector2i(120, 45)]:
		assert_eq(g.cell_at(g.cell_centre(c)), c, "centre round-trip for %s" % c)
		assert_eq(g.cell_at(g.cell_origin(c)), c, "origin round-trip for %s" % c)


func test_round_trip_holds_for_negative_cells() -> void:
	var g := _grid()
	for c in [Vector2i(-1, -1), Vector2i(-4, 2), Vector2i(3, -9), Vector2i(-31, -31)]:
		assert_eq(g.cell_at(g.cell_centre(c)), c, "centre round-trip for %s" % c)
		assert_eq(g.cell_at(g.cell_origin(c)), c, "origin round-trip for %s" % c)


func test_round_trip_holds_with_a_shifted_origin() -> void:
	# The sandbox anchors each floor's lattice at its inner bounds (16, 16).
	var g := _grid(CELL, Vector2(16, 16))
	assert_eq(g.cell_at(Vector2(16, 16)), Vector2i(0, 0))
	assert_eq(g.cell_at(Vector2(15.9, 16)), Vector2i(-1, 0))
	assert_eq(g.cell_centre(Vector2i(0, 0)), Vector2(32, 32))
	for c in [Vector2i(0, 0), Vector2i(2, 5), Vector2i(-3, -1)]:
		assert_eq(g.cell_at(g.cell_centre(c)), c, "shifted-origin round-trip %s" % c)


func test_non_square_cells_convert_per_axis() -> void:
	var g := _grid(Vector2(64, 16))
	assert_eq(g.cell_at(Vector2(65, 17)), Vector2i(1, 1))
	assert_eq(g.cell_centre(Vector2i(0, 0)), Vector2(32, 8))
	assert_eq(g.cell_rect(Vector2i(1, 2)), Rect2(Vector2(64, 32), Vector2(64, 16)))


func test_degenerate_cell_size_is_clamped_not_divided_by_zero() -> void:
	var g := _grid(0.0)
	assert_gt(g.cell_size.x, 0.0, "zero cell size must clamp, not divide by zero")
	assert_eq(g.cell_at(Vector2(0, 0)), Vector2i(0, 0))


# --- Negative coordinates -----------------------------------------------------
func test_negative_world_points_use_floor_division_not_truncation() -> void:
	var g := _grid()
	# Truncation would put all four of these in column/row 0.
	assert_eq(g.cell_at(Vector2(-1, -1)), Vector2i(-1, -1))
	assert_eq(g.cell_at(Vector2(-0.001, -0.001)), Vector2i(-1, -1))
	assert_eq(g.cell_at(Vector2(-32, -32)), Vector2i(-1, -1))
	assert_eq(g.cell_at(Vector2(-33, -33)), Vector2i(-2, -2))
	assert_eq(g.cell_at(Vector2(0, 0)), Vector2i(0, 0))


func test_snap_is_continuous_across_the_origin() -> void:
	var g := _grid()
	assert_eq(g.snap(Vector2(-1, -1)), Vector2(-16, -16))
	assert_eq(g.snap(Vector2(1, 1)), Vector2(16, 16))
	assert_eq(g.snap(Vector2(-33, 5)), Vector2(-48, 16))


# --- Snap edges ---------------------------------------------------------------
func test_snap_edges_are_half_open() -> void:
	var g := _grid()
	# Exactly on a boundary belongs to the cell STARTING there.
	assert_eq(g.cell_at(Vector2(32, 32)), Vector2i(1, 1))
	assert_eq(g.cell_at(Vector2(31.999, 31.999)), Vector2i(0, 0))
	assert_eq(g.snap(Vector2(32, 32)), Vector2(48, 48))
	assert_eq(g.snap(Vector2(31.999, 0)), Vector2(16, 16))
	# Both ends of a cell snap to the same centre.
	assert_eq(g.snap(Vector2(0, 0)), g.snap(Vector2(31.5, 31.5)))


func test_snap_to_corner_returns_the_cell_origin() -> void:
	var g := _grid(CELL, Vector2(16, 16))
	assert_eq(g.snap_to_corner(Vector2(50, 50)), Vector2(48, 48))
	assert_eq(g.snap_to_corner(Vector2(16, 16)), Vector2(16, 16))


# --- Footprints ---------------------------------------------------------------
func test_footprint_cells_is_row_major_and_clamps_to_at_least_one_cell() -> void:
	var g := _grid()
	var cells := g.footprint_cells(Vector2i(2, 3), Vector2i(3, 2))
	assert_eq(cells.size(), 6)
	assert_eq(cells[0], Vector2i(2, 3))
	assert_eq(cells[2], Vector2i(4, 3))
	assert_eq(cells[3], Vector2i(2, 4), "row-major: 4th entry starts the next row")
	assert_eq(cells[5], Vector2i(4, 4))
	assert_eq(g.footprint_cells(Vector2i(0, 0), Vector2i(0, -5)).size(), 1,
		"a non-positive footprint still occupies its own cell")


func test_cells_in_rect_covers_touched_cells_without_bleeding_past_a_flush_edge() -> void:
	var g := _grid()
	assert_eq(g.cells_in_rect(Rect2(Vector2(0, 0), Vector2(32, 32))).size(), 1,
		"a rect exactly one cell wide occupies one cell")
	assert_eq(g.cells_in_rect(Rect2(Vector2(0, 0), Vector2(64, 32))).size(), 2)
	assert_eq(g.cells_in_rect(Rect2(Vector2(16, 16), Vector2(32, 32))).size(), 4,
		"a straddling rect touches four cells")
	assert_eq(g.cells_in_rect(Rect2(Vector2(5, 5), Vector2.ZERO)),
		[Vector2i(0, 0)] as Array[Vector2i], "a zero-size rect is one cell")
	# Edge-to-edge rects must not overlap.
	var a := g.cells_in_rect(Rect2(Vector2(0, 0), Vector2(32, 32)))
	var b := g.cells_in_rect(Rect2(Vector2(32, 0), Vector2(32, 32)))
	assert_false(a.has(b[0]), "flush neighbours claim disjoint cells")


func test_cells_in_rect_handles_negative_space() -> void:
	var g := _grid()
	# -40 .. +8 spans cells -2, -1 and 0 on both axes.
	var cells := g.cells_in_rect(Rect2(Vector2(-40, -40), Vector2(48, 48)))
	assert_eq(cells.size(), 9)
	assert_eq(cells[0], Vector2i(-2, -2), "row-major starts at the top-left cell")
	assert_true(cells.has(Vector2i(-1, -1)))
	assert_true(cells.has(Vector2i(0, 0)), "the far edge reaches 8px into cell 0")
	assert_false(cells.has(Vector2i(1, 0)), "and stops there")


# --- Occupancy ----------------------------------------------------------------
func test_occupancy_claim_and_release_round_trip() -> void:
	var g := _grid()
	var cells := g.footprint_cells(Vector2i(1, 1), Vector2i(2, 2))
	assert_eq(g.occupy(cells, "desk").size(), 4)
	assert_true(g.is_occupied(Vector2i(2, 2)))
	assert_eq(g.owner_of(Vector2i(2, 2)), "desk")
	assert_eq(g.occupied_count(), 4)
	assert_eq(g.cells_of("desk").size(), 4)
	assert_eq(g.release("desk"), 4)
	assert_eq(g.occupied_count(), 0)
	assert_false(g.is_occupied(Vector2i(2, 2)))
	assert_null(g.owner_of(Vector2i(2, 2)), "a free cell has no owner")


func test_claims_skip_occupied_cells_instead_of_stealing_them() -> void:
	var g := _grid()
	g.occupy_cell(Vector2i(1, 1), "desk")
	var claimed := g.occupy(g.footprint_cells(Vector2i(1, 1), Vector2i(2, 1)), "plant")
	assert_eq(claimed, [Vector2i(2, 1)] as Array[Vector2i], "only the free cell is claimed")
	assert_eq(g.owner_of(Vector2i(1, 1)), "desk", "an existing claim is never stolen")
	# Releasing the loser must not free the winner's cell.
	g.release("plant")
	assert_true(g.is_occupied(Vector2i(1, 1)))
	assert_false(g.is_occupied(Vector2i(2, 1)))


func test_release_of_an_unknown_owner_is_a_no_op() -> void:
	var g := _grid()
	g.occupy_cell(Vector2i(0, 0), 7)
	assert_eq(g.release(999), 0, "defensive teardown releases must be harmless")
	assert_eq(g.occupied_count(), 1)


func test_release_cell_drops_the_owner_when_its_last_cell_goes() -> void:
	var g := _grid()
	g.occupy(g.footprint_cells(Vector2i(0, 0), Vector2i(2, 1)), "server")
	g.release_cell(Vector2i(0, 0))
	assert_eq(g.cells_of("server"), [Vector2i(1, 0)] as Array[Vector2i])
	g.release_cell(Vector2i(1, 0))
	assert_eq(g.cells_of("server").size(), 0)
	assert_eq(g.occupied_count(), 0)


func test_clear_wipes_every_claim() -> void:
	var g := _grid()
	g.occupy_cell(Vector2i(0, 0), "a")
	g.occupy_cell(Vector2i(9, 9), "b")
	g.clear()
	assert_eq(g.occupied_count(), 0)
	assert_eq(g.cells_of("a").size(), 0)


func test_two_grids_do_not_share_occupancy() -> void:
	# This is the whole point of retiring the "a|"/"b|" string-key prefix: the two
	# compare-view floors used to collide on identical local coordinates.
	var a := _grid()
	var b := _grid()
	a.occupy_cell(Vector2i(3, 3), "desk")
	assert_false(b.is_occupied(Vector2i(3, 3)), "grids are independent lattices")


# --- Bounds, neighbours, enumeration ------------------------------------------
func test_set_bounds_anchors_the_origin_and_counts_whole_cells_only() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2(16, 16), Vector2(200, 100)))
	assert_eq(g.origin, Vector2(16, 16))
	assert_eq(g.cols(), 6, "200/32 = 6 whole columns, the trailing 8px is unaddressable")
	assert_eq(g.rows(), 3)
	assert_true(g.has_bounds())
	assert_eq(g.bounds_rect(), Rect2(Vector2(16, 16), Vector2(192, 96)))
	assert_eq(g.cell_at(Vector2(16, 16)), Vector2i(0, 0))


func test_unbounded_grid_contains_everything_and_enumerates_nothing() -> void:
	var g := _grid()
	assert_false(g.has_bounds())
	assert_true(g.contains(Vector2i(-500, 900)), "an unbounded lattice is infinite")
	assert_false(g.is_edge_cell(Vector2i(0, 0)), "no bounds means no perimeter")
	assert_eq(g.all_cells().size(), 0, "enumerating an infinite lattice returns nothing")


func test_containment_and_edge_detection_on_a_bounded_grid() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))   # 4 x 3
	assert_true(g.contains(Vector2i(3, 2)))
	assert_false(g.contains(Vector2i(4, 2)))
	assert_false(g.contains(Vector2i(-1, 0)))
	assert_true(g.is_edge_cell(Vector2i(0, 1)))
	assert_true(g.is_edge_cell(Vector2i(3, 1)))
	assert_false(g.is_edge_cell(Vector2i(1, 1)), "the only interior cells are (1,1) and (2,1)")


func test_enumeration_is_row_major_and_partitions_edge_from_interior() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))   # 4 x 3 = 12 cells
	var all := g.all_cells()
	assert_eq(all.size(), 12)
	assert_eq(all[0], Vector2i(0, 0))
	assert_eq(all[3], Vector2i(3, 0))
	assert_eq(all[4], Vector2i(0, 1), "row-major wrap")
	assert_eq(g.edge_cells().size(), 10)
	assert_eq(g.interior_cells(), [Vector2i(1, 1), Vector2i(2, 1)] as Array[Vector2i])
	assert_eq(g.edge_cells().size() + g.interior_cells().size(), all.size(),
		"edge and interior partition the grid")


func test_free_filters_drop_occupied_cells() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))
	g.occupy_cell(Vector2i(0, 0), "desk")
	g.occupy_cell(Vector2i(1, 1), "plant")
	assert_eq(g.free_cells().size(), 10)
	assert_eq(g.edge_cells(true).size(), 9)
	assert_eq(g.interior_cells(true), [Vector2i(2, 1)] as Array[Vector2i])


func test_neighbours_are_clipped_to_bounds_and_ordered() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))
	assert_eq(g.neighbours4(Vector2i(1, 1)),
		[Vector2i(1, 0), Vector2i(0, 1), Vector2i(2, 1), Vector2i(1, 2)] as Array[Vector2i])
	assert_eq(g.neighbours4(Vector2i(0, 0)),
		[Vector2i(1, 0), Vector2i(0, 1)] as Array[Vector2i], "corner drops out-of-bounds")
	assert_eq(g.neighbours8(Vector2i(1, 1)).size(), 8)
	assert_eq(g.neighbours8(Vector2i(0, 0)).size(), 3)


func test_unbounded_neighbours_keep_negative_cells() -> void:
	var g := _grid()
	assert_eq(g.neighbours4(Vector2i(0, 0)).size(), 4)
	assert_true(g.neighbours4(Vector2i(0, 0)).has(Vector2i(-1, 0)))


func test_free_neighbours_skip_claimed_cells() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))
	g.occupy_cell(Vector2i(1, 0), "desk")
	var free := g.free_neighbours4(Vector2i(1, 1))
	assert_false(free.has(Vector2i(1, 0)))
	assert_eq(free.size(), 3)


func test_no_cell_sentinel_cannot_collide_with_a_real_cell() -> void:
	var g := _grid()
	g.set_bounds(Rect2(Vector2.ZERO, Vector2(128, 96)))
	assert_false(g.contains(RenderGrid.NO_CELL))
	assert_ne(g.cell_at(Vector2(-1e6, -1e6)), RenderGrid.NO_CELL,
		"the sentinel must sit outside any plausible lattice")

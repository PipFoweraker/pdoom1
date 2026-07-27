extends RefCounted
class_name RenderGrid
## First-class RENDER-LAYER grid: Vector2i col/row addressing, world<->cell
## conversion, snap, footprint occupancy, neighbour + enumeration queries.
##
## AUTHORITY: ADR-0018 (render-only office doctrine), a(3)-lite amendment
## 2026-07-27. Quoting the ruling: a first-class integer grid type "is approved
## as RENDER-LAYER INFRASTRUCTURE. Its consumers are prop placement, decorating
## render, walk theatre, and click-targets." And the scope guard, verbatim:
## "this grid is explicitly NOT a pathfinding or simulation grid; nothing
## sim-side may read cell state".
##
## THE ARROW RULE (non-negotiable, enforced by review not by the compiler):
##   The sim owns counts and quantities; the render owns coordinates.
## Consequences for this file, permanently:
##   - NO import of / reference to GameState, TurnManager, or anything in
##     scripts/core that models the simulation. This script has ZERO project
##     dependencies by design (it only uses engine built-ins), which is also
##     why it is headless-unit-testable with no scene tree.
##   - NO signals out of here into core. It is a passive value/utility object.
##   - Nothing here is serialized into a save, a replay, or a leaderboard
##     payload. Cell coordinates are a frame-local rendering detail; ADR-0006
##     replays record (action, entity_id), never positions.
##
## SEAM NOTE -- decorating render (Wednesday's W2 block):
##   W2's decorating system is the next consumer of this type: it will ask the
##   grid which cells a decor prop occupies, which cells are free, and where a
##   prop snaps. That is legitimate -- placement is EXPRESSION.
##   The line W2 must not cross, restating ADR-0018: DECOR VALUE KEYS OFF
##   OWNERSHIP + TIER + SPEND (sim-side counts), NEVER OFF PLACEMENT. The moment
##   a decor bonus is priced by WHERE a prop sits -- which cell, which room,
##   adjacency to another prop -- a spatial fact has become a gameplay input and
##   the doctrine is breached through the back door. Occupancy queries here
##   exist to stop props overlapping and to keep walkers out of furniture, i.e.
##   to make the picture correct. They are not an economy input, and no
##   sim-side caller may read them.
##
## RETIRES: office_sandbox.gd's ad hoc string-keyed 32px snap-hack
## (`_snap_to_grid` / `_cell_of` / `_cell_key` + a `String -> true`
## `_occupied_cells` dictionary keyed by stringified cell CENTRES, with an
## "a|"/"b|" prefix to stop the two compare floors colliding). That debt is
## replaced here by real Vector2i keys and per-floor grid instances.
##
## DETERMINISM: every enumeration accessor (all_cells / free_cells /
## edge_cells / interior_cells) returns ROW-MAJOR order, so a seeded-RNG draw
## over the result is independent of Dictionary iteration order -- the same rule
## PropCatalogue.ids() follows for ADR-0006.

## Sentinel "no such cell" return (pick/query misses). A real cell can be
## negative, so the sentinel has to sit outside any plausible lattice.
const NO_CELL := Vector2i(-2147483647, -2147483647)

## Smallest legal cell edge in world units. A zero/negative cell size would make
## every conversion a division by zero, so it is clamped with a warning instead.
const MIN_CELL_PX := 1.0

## World-unit size of one cell. Non-square grids are supported (isometric /
## letterboxed tiles); the office uses a square 32. Assign through
## set_cell_size(), which clamps to MIN_CELL_PX -- a zero edge would make every
## conversion a division by zero.
var cell_size: Vector2 = Vector2(32.0, 32.0)

## World position of cell (0, 0)'s top-left corner. Callers anchoring to a
## Control's inner rect pass that rect's position (see set_bounds).
var origin: Vector2 = Vector2.ZERO

var _cols: int = 0            # 0 = unbounded (no enumeration, no containment test)
var _rows: int = 0
var _occupied: Dictionary = {}      # Vector2i -> owner (Variant)
var _owner_cells: Dictionary = {}   # owner -> Array[Vector2i]


## `p_cell_size` accepts a float (square cells) or a Vector2 (non-square).
func _init(p_cell_size: Variant = 32.0, p_origin: Vector2 = Vector2.ZERO) -> void:
	set_cell_size(p_cell_size)
	origin = p_origin


func set_cell_size(v: Variant) -> void:
	var s := cell_size
	if v is Vector2:
		s = v
	elif v is Vector2i:
		s = Vector2(v)
	elif v is float or v is int:
		s = Vector2(float(v), float(v))
	else:
		push_warning("RenderGrid.set_cell_size: unsupported type, keeping %s" % cell_size)
		return
	cell_size = Vector2(maxf(s.x, MIN_CELL_PX), maxf(s.y, MIN_CELL_PX))


# --- Bounds -------------------------------------------------------------------
## Anchor the lattice to a world-space rect: origin becomes the rect's top-left
## and the grid gains a finite col/row extent (whole cells only -- a trailing
## partial cell is not addressable, matching the sandbox's `int(size / GRID)`).
## Re-calling this after a layout change is cheap and is how a resizable floor
## keeps its lattice aligned.
func set_bounds(rect: Rect2) -> void:
	origin = rect.position
	_cols = maxi(0, floori(rect.size.x / cell_size.x))
	_rows = maxi(0, floori(rect.size.y / cell_size.y))


func clear_bounds() -> void:
	_cols = 0
	_rows = 0


func has_bounds() -> bool:
	return _cols > 0 and _rows > 0


func cols() -> int:
	return _cols


func rows() -> int:
	return _rows


## World rect the bounded lattice covers (whole cells only). Rect2() if unbounded.
func bounds_rect() -> Rect2:
	if not has_bounds():
		return Rect2()
	return Rect2(origin, Vector2(_cols * cell_size.x, _rows * cell_size.y))


## True when `cell` is inside the bounded extent. An UNBOUNDED grid contains
## every cell (including negative ones) -- it is an infinite lattice by design.
func contains(cell: Vector2i) -> bool:
	if not has_bounds():
		return true
	return cell.x >= 0 and cell.y >= 0 and cell.x < _cols and cell.y < _rows


## Perimeter test. Always false on an unbounded grid (no perimeter exists).
func is_edge_cell(cell: Vector2i) -> bool:
	if not has_bounds() or not contains(cell):
		return false
	return cell.x == 0 or cell.y == 0 or cell.x == _cols - 1 or cell.y == _rows - 1


# --- World <-> cell conversion ------------------------------------------------
## The cell containing `world`. Floor division, so it is correct for NEGATIVE
## coordinates too: a point one pixel left of the origin lands in col -1, not 0
## (integer truncation would wrongly fold -1..+1 into the same column).
func cell_at(world: Vector2) -> Vector2i:
	return Vector2i(
		floori((world.x - origin.x) / cell_size.x),
		floori((world.y - origin.y) / cell_size.y))


## Top-left world corner of `cell`. Round-trip guarantee:
## cell_at(cell_origin(c)) == c for every c.
func cell_origin(cell: Vector2i) -> Vector2:
	return origin + Vector2(cell.x * cell_size.x, cell.y * cell_size.y)


## World centre of `cell`. Round-trip guarantee:
## cell_at(cell_centre(c)) == c for every c.
func cell_centre(cell: Vector2i) -> Vector2:
	return cell_origin(cell) + cell_size * 0.5


func cell_rect(cell: Vector2i) -> Rect2:
	return Rect2(cell_origin(cell), cell_size)


## Snap a world point to its cell CENTRE (the sandbox's placement snap).
func snap(world: Vector2) -> Vector2:
	return cell_centre(cell_at(world))


## Snap a world point to its cell's top-left CORNER (tile-aligned blits).
func snap_to_corner(world: Vector2) -> Vector2:
	return cell_origin(cell_at(world))


# --- Footprints ---------------------------------------------------------------
## The `size.x` x `size.y` block of cells whose top-left is `anchor`, row-major.
## A non-positive size is clamped to 1 (a prop always occupies at least itself).
func footprint_cells(anchor: Vector2i, size: Vector2i) -> Array[Vector2i]:
	var w := maxi(1, size.x)
	var h := maxi(1, size.y)
	var out: Array[Vector2i] = []
	for r in range(h):
		for c in range(w):
			out.append(Vector2i(anchor.x + c, anchor.y + r))
	return out


## Every cell a world-space rect touches, row-major. A zero-size rect yields the
## single cell containing its position; a rect flush to a cell boundary does NOT
## pick up the next cell along (half-open on the far edge), so two rects laid
## edge-to-edge occupy disjoint cell sets.
func cells_in_rect(rect: Rect2) -> Array[Vector2i]:
	var r := rect.abs()
	var first := cell_at(r.position)
	var far := r.position + r.size
	var last := Vector2i(
		ceili((far.x - origin.x) / cell_size.x) - 1,
		ceili((far.y - origin.y) / cell_size.y) - 1)
	last = Vector2i(maxi(last.x, first.x), maxi(last.y, first.y))
	return footprint_cells(first, Vector2i(last.x - first.x + 1, last.y - first.y + 1))


# --- Occupancy ----------------------------------------------------------------
## Claim one cell for `owner`. Returns false if the cell was ALREADY claimed
## (by anyone, including `owner`) -- claims never silently steal.
func occupy_cell(cell: Vector2i, owner: Variant) -> bool:
	if _occupied.has(cell):
		return false
	_occupied[cell] = owner
	var held: Array = _owner_cells.get(owner, [])
	held.append(cell)
	_owner_cells[owner] = held
	return true


## Claim every free cell in `cells` for `owner`; already-claimed cells are
## SKIPPED, not stolen. Returns the cells actually claimed (row-major, i.e. the
## input's order filtered). Partial claims are deliberate: it reproduces the
## sandbox's prior behaviour where a prop footprint overlapping existing
## furniture recorded only the cells it genuinely took.
func occupy(cells: Array, owner: Variant) -> Array[Vector2i]:
	var claimed: Array[Vector2i] = []
	for c in cells:
		if c is Vector2i and occupy_cell(c, owner):
			claimed.append(c)
	return claimed


func is_occupied(cell: Vector2i) -> bool:
	return _occupied.has(cell)


## The owner holding `cell`, or null when free.
func owner_of(cell: Vector2i) -> Variant:
	return _occupied.get(cell, null)


## Cells currently held by `owner` (row-major within each occupy() call).
func cells_of(owner: Variant) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in _owner_cells.get(owner, []):
		out.append(c)
	return out


## Free everything `owner` holds. Returns how many cells were released; 0 is a
## normal answer (callers release defensively on teardown).
func release(owner: Variant) -> int:
	var held: Array = _owner_cells.get(owner, [])
	for c in held:
		if _occupied.get(c, null) == owner:
			_occupied.erase(c)
	_owner_cells.erase(owner)
	return held.size()


## Free one cell regardless of who holds it.
func release_cell(cell: Vector2i) -> void:
	if not _occupied.has(cell):
		return
	var owner: Variant = _occupied[cell]
	_occupied.erase(cell)
	var held: Array = _owner_cells.get(owner, [])
	held.erase(cell)
	if held.is_empty():
		_owner_cells.erase(owner)
	else:
		_owner_cells[owner] = held


func occupied_count() -> int:
	return _occupied.size()


func clear() -> void:
	_occupied.clear()
	_owner_cells.clear()


# --- Neighbours ---------------------------------------------------------------
## 4-neighbourhood in a fixed order (N, W, E, S) so callers are deterministic.
## Out-of-bounds neighbours are dropped on a BOUNDED grid and kept on an
## unbounded one.
func neighbours4(cell: Vector2i) -> Array[Vector2i]:
	return _filter_contained([
		cell + Vector2i(0, -1), cell + Vector2i(-1, 0),
		cell + Vector2i(1, 0), cell + Vector2i(0, 1)])


## 8-neighbourhood, row-major (NW, N, NE, W, E, SW, S, SE).
func neighbours8(cell: Vector2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for dy in [-1, 0, 1]:
		for dx in [-1, 0, 1]:
			if dx == 0 and dy == 0:
				continue
			out.append(cell + Vector2i(dx, dy))
	return _filter_contained(out)


## Neighbours that are in-bounds AND unoccupied.
func free_neighbours4(cell: Vector2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in neighbours4(cell):
		if not is_occupied(c):
			out.append(c)
	return out


func _filter_contained(cells: Array) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in cells:
		if contains(c):
			out.append(c)
	return out


# --- Enumeration (bounded grids only) -----------------------------------------
## Every cell in the bounded extent, ROW-MAJOR. Empty on an unbounded grid --
## enumerating an infinite lattice is a caller bug, not a thing to guess at.
func all_cells() -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for r in range(_rows):
		for c in range(_cols):
			out.append(Vector2i(c, r))
	return out


func free_cells() -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in all_cells():
		if not is_occupied(c):
			out.append(c)
	return out


## Perimeter cells, row-major. `only_free` drops occupied ones.
func edge_cells(only_free: bool = false) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in all_cells():
		if is_edge_cell(c) and not (only_free and is_occupied(c)):
			out.append(c)
	return out


## Non-perimeter cells, row-major. `only_free` drops occupied ones.
func interior_cells(only_free: bool = false) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	for c in all_cells():
		if not is_edge_cell(c) and not (only_free and is_occupied(c)):
			out.append(c)
	return out

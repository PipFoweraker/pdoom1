extends GutTest
## Guard for the 2026-08-05 playtest failure: 2 of 2 external players could not find
## Fundraising. Root cause was geometry, not comprehension -- the turn-1 hand rendered as a
## single 70px-wide VBox column of 15 tiles (~1,065px tall) inside an ActionsScroll viewport
## of ~550px at 1080p, and the scrollbar sat at the FAR RIGHT edge of the ~573px panel,
## ~470px away from the 70px tile column it scrolls -- an invisible affordance. Fundraising
## was tile 10 (y ~639px), below the fold. (#1043 item 1: "no scrolling at the opening
## view"; #798: action grouping.)
##
## Guards:
##   1. the REAL turn-1 hand (GameActions defs, fresh-run state) rendered into a plan panel
##      sized like the 1080p layout fits entirely above the fold, with a floor on the count.
##      The fixed panel size matters: GUT's headless window is larger than 1080p, so only a
##      pinned panel reproduces the geometry playtesters actually saw.
##   2. the Fundraising tile is the FIRST tile (money is the enabling resource);
##   3. in the real booted scene: every tile inside the live ActionsScroll viewport, and
##      upgrade rows are uniform full-width list rows (replacing the ragged, content-sized
##      right-aligned float -- 200..283px buttons, measured -- that read as clutter).
##
## HONESTY NOTE: these prove geometry -- tiles inside the fold, fundraise first, uniform
## rows. No test proves the screen READS well; that stays a human playtest call.

# The plan panel at the default 1920x1080 canvas: ContentArea gives the Plan column
# 0.3/(0.3+0.3+0.4) of ~1910px = ~573px wide; the column's vertical budget after the
# reserve gauge / hint / upgrades label / command zone rows is ~808px, split 0.8:0.65
# with UpgradesScroll = ~445px for the action hand. Conservative vs the GUT window.
const PLAN_PANEL_1080P := Vector2(573, 445)
const MIN_VISIBLE_ACTIONS := 12  # floor: the whole turn-1 hand (15 tiles today) stays visible

# Fresh-run state (mirrors the #1043 F6 capture: turn 1, $245k, nobody hired yet).
const FRESH_STATE := {
	"money": 245000, "turn": 1, "total_staff": 0, "reputation": 0.0,
	"papers": 0, "research": 0.0, "purchased_upgrades": [],
}


# --- Fixed-size harness (same FakeHost pattern as test_action_bar_renderer) ----------------

class FakeGameManager:
	extends RefCounted
	var _state: Dictionary
	func _init(state: Dictionary) -> void:
		_state = state
	func get_game_state() -> Dictionary:
		return _state

class FakeHost:
	extends Node
	var actions_list: Control
	var game_manager
	var _ui_layout: String = "classic"
	func _populate_upgrades() -> void: pass
	func _apply_first_lever_nudge() -> void: pass
	func _show_strategic_unlock_fanfare() -> void: pass
	func _on_dynamic_action_pressed(_id: String, _name: String) -> void: pass
	func _on_action_hover(_a: Dictionary, _c: bool, _m: Array) -> void: pass
	func _on_action_unhover() -> void: pass


var _harness_scroll: ScrollContainer = null


func _render_real_hand_in_1080p_panel() -> Array:
	"""Render the REAL action defs with a fresh-run state into a plan panel pinned to the
	1080p geometry. Returns the tile buttons in visual order."""
	var host := FakeHost.new()
	host.game_manager = FakeGameManager.new(FRESH_STATE)
	add_child_autofree(host)

	var panel := Control.new()
	panel.custom_minimum_size = PLAN_PANEL_1080P
	panel.size = PLAN_PANEL_1080P
	host.add_child(panel)

	_harness_scroll = ScrollContainer.new()
	_harness_scroll.set_anchors_preset(Control.PRESET_FULL_RECT)
	panel.add_child(_harness_scroll)

	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_harness_scroll.add_child(list)
	host.actions_list = list

	var renderer = ActionBarRenderer.new(host)
	renderer.render(GameActions.get_all_actions())
	await get_tree().process_frame
	await get_tree().process_frame
	return _tiles_in(list)


func _tiles_in(actions_list: Control) -> Array:
	"""All action tiles in the hand, in visual order (buttons tagged with action_id meta,
	inside whatever container the active layout mounted under actions_list)."""
	var out: Array = []
	if actions_list == null:
		return out
	for stack in actions_list.get_children():
		if stack is Container:
			for b in stack.get_children():
				if b is Button and String(b.get_meta("action_id", "")) != "":
					out.append(b)
	return out


func _clipped_tiles(tiles: Array, fold: Rect2) -> Array:
	var clipped: Array = []
	for t in tiles:
		var r: Rect2 = t.get_global_rect()
		if not fold.encloses(r):
			clipped.append("%s at y=%.0f..%.0f (fold bottom %.0f)" % [
				String(t.get_meta("action_id")), r.position.y, r.end.y, fold.end.y])
	return clipped


func test_turn1_hand_fits_above_the_fold_at_1080p() -> void:
	var tiles: Array = await _render_real_hand_in_1080p_panel()
	assert_true(tiles.size() >= MIN_VISIBLE_ACTIONS,
		"turn-1 hand should render at least %d tiles (got %d)" % [MIN_VISIBLE_ACTIONS, tiles.size()])
	var fold: Rect2 = _harness_scroll.get_global_rect()
	var clipped: Array = _clipped_tiles(tiles, fold)
	assert_eq(clipped.size(), 0,
		"every turn-1 action must be visible without scrolling in the %s plan panel; %d of %d tiles are outside the fold: %s" % [
			str(PLAN_PANEL_1080P), clipped.size(), tiles.size(), ", ".join(clipped)])


func test_fundraise_is_the_first_tile() -> void:
	var tiles: Array = await _render_real_hand_in_1080p_panel()
	var ids: Array = []
	for t in tiles:
		ids.append(String(t.get_meta("action_id")))
	assert_true(ids.has("fundraise"),
		"the fundraise action must be in the turn-1 hand (got: %s)" % [ids])
	if ids.is_empty():
		return
	assert_eq(ids[0], "fundraise",
		"money is the enabling resource -- Fundraising must be tile 1 (keyboard [1]); hand order: %s" % [ids])


# --- Real booted scene: live fold containment + upgrade-row uniformity ---------------------

func test_real_scene_hand_fits_and_upgrade_rows_are_uniform() -> void:
	# Boot main.tscn exactly as the game does (same pattern as test_game_start_actionable).
	var scene: PackedScene = load("res://scenes/main.tscn")
	assert_not_null(scene, "main.tscn must load")
	if scene == null:
		return
	var root: Node = scene.instantiate()
	add_child_autofree(root)
	var main_ui: Node = root.find_child("MainUI", true, false)
	assert_not_null(main_ui, "MainUI node must exist under the scene root")
	if main_ui == null:
		return
	var plan = main_ui.get("plan_screen")

	# _ready awaits one frame then auto-boots; poll until the hand has rendered tiles.
	for _i in range(60):
		await get_tree().process_frame
		if plan != null and not _tiles_in(plan.actions_list).is_empty():
			break
	# Deterministic register: measure the CLASSIC flat hand even if a local pref persisted
	# the proposed layout on this machine.
	if main_ui.get("_ui_layout") != "classic":
		main_ui._apply_ui_layout("classic")
		for _i in range(3):
			await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame

	var tiles: Array = _tiles_in(plan.actions_list)
	assert_false(tiles.is_empty(), "turn-1 action hand must render tiles in the booted scene")

	# 1. Live fold containment at whatever size the headless window gives (weaker than the
	# pinned-panel guard above, but it exercises the REAL scene tree and ratios).
	var fold: Rect2 = plan.actions_scroll.get_global_rect()
	assert_gt(fold.size.y, 200.0, "ActionsScroll viewport should be a real panel (got %s)" % fold.size)
	var clipped: Array = _clipped_tiles(tiles, fold)
	assert_eq(clipped.size(), 0,
		"booted scene: %d of %d tiles are outside the live %s fold: %s" % [
			clipped.size(), tiles.size(), str(fold.size), ", ".join(clipped)])

	# 2. Upgrade rows: one uniform full-width column, not a ragged right-aligned float.
	var rows: Array = []
	for c in plan.upgrades_list.get_children():
		if c is Button:
			rows.append(c)
	assert_gt(rows.size(), 0, "upgrades list must render rows")
	var list_width: float = plan.upgrades_list.size.x
	for r in rows:
		assert_eq(r.size_flags_horizontal, Control.SIZE_EXPAND_FILL,
			"upgrade row '%s' must fill the column (uniform list rows, not a ragged float)" % r.text)
		assert_almost_eq(r.size.x, list_width, 1.0,
			"upgrade row '%s' width %.0f should span the %.0f column" % [r.text, r.size.x, list_width])

extends GutTest
## CARVE 5 (docs/MAIN_UI_SEAM_MAP.md, seam R1): characterization + regression lock for the ACTION-BAR
## RENDERING extracted out of main_ui.gd into ActionBarRenderer. This is the surface the player touches
## every turn, so the pin is deliberately STRUCTURAL: it constructs the renderer against a fake host and
## asserts the produced button grid (category sections, button count, costs -> grey-out flags, coming-soon
## badges) is exactly what the pre-carve inline renderer produced. If a later edit forks the on-screen bar,
## these assertions break.
##
## NON-FORKING refactor: every render statement is a VERBATIM move; only host-owned members/handlers were
## re-routed through `host.` (actions_list, game_manager, _ui_layout, the press/hover/upgrades/nudge/fanfare
## callbacks). Input (_on_dynamic_action_pressed), hover, and the GameActions/SubmenuChrome delegates stay
## in the view. No gameplay/RNG/scoring change; ladder stays L2.

const RENDERER_PATH := "res://scripts/ui/action_bar_renderer.gd"

# The rendering surface that moved out of the view. Every one must live on the renderer now.
const RENDER_METHODS := [
	"render",            # single entry point (was _on_actions_available's body)
	"_render_flat",      # classic single-column icon grid
	"_render_grouped",   # P9 grouped collapsible sections (was _render_actions_grouped)
	"_build_action_tile",  # VARIANT PLUG POINT: one classic tile
	"_build_action_row",   # VARIANT PLUG POINT: one grouped row
]

# A minimal game-state stand-in: render() only ever calls get_game_state() on it.
class FakeGameManager:
	extends RefCounted
	var _state: Dictionary
	func _init(state: Dictionary) -> void:
		_state = state
	func get_game_state() -> Dictionary:
		return _state

# A minimal MainUI stand-in exposing exactly the surface render() composes. The callbacks are
# no-ops -- construction + a single render pass exercises the whole grid build headlessly.
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


func _sample_actions() -> Array:
	# hiring has TWO actions (one affordable, one coming-soon); resources has ONE unaffordable action.
	# No unlock_conditions -> all unlocked (GameActions.is_action_unlocked returns true).
	return [
		{"id": "hire_staff", "name": "Hire Staff", "category": "hiring", "costs": {"money": 100}},
		{"id": "advertise", "name": "Advertise", "category": "hiring", "costs": {"money": 50}},
		{"id": "buy_compute", "name": "Buy Compute", "category": "resources", "costs": {"money": 100000}},
	]


func _make_host(layout: String) -> FakeHost:
	var host := FakeHost.new()
	host.game_manager = FakeGameManager.new({"money": 1000})
	host._ui_layout = layout
	add_child_autofree(host)
	host.actions_list = VBoxContainer.new()
	host.add_child(host.actions_list)
	return host


# --- Structural: the surface moved, and the view kept only a shim -------------------------

func test_renderer_is_a_refcounted_view_module_taking_a_host():
	var r = ActionBarRenderer.new(null)
	assert_not_null(r, "ActionBarRenderer constructs with a host reference")
	assert_true(r is RefCounted, "it is a RefCounted view module (same pattern as the other carves)")


func test_renderer_declares_the_whole_render_surface():
	var r = ActionBarRenderer.new(null)
	for m in RENDER_METHODS:
		assert_true(r.has_method(m), "ActionBarRenderer owns %s (moved from the view)" % m)


func test_render_left_the_view_but_the_signal_shim_stays():
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	# The grouped renderer moved wholesale -- the view must not re-declare it.
	assert_false(src.contains("func _render_actions_grouped"),
		"_render_actions_grouped moved into ActionBarRenderer; the view must not re-declare it")
	# The view keeps a thin _on_actions_available shim that forwards to the renderer.
	assert_true(src.contains("func _on_actions_available"), "the view keeps the actions_available signal shim")
	assert_true(src.contains("action_bar.render(actions)"), "the shim forwards the payload to the renderer")
	# The render-only config moved with the code that used it.
	assert_false(src.contains("const HIDDEN_FROM_ACTION_BAR_IDS"),
		"HIDDEN_FROM_ACTION_BAR_IDS moved into the renderer")
	assert_false(src.contains("const CATEGORY_HEADER_ICONS"),
		"CATEGORY_HEADER_ICONS moved into the renderer")


func test_input_and_hover_stayed_in_the_view():
	# The carve is render-only: queueing input and the shared InfoBar hover must NOT have moved.
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	assert_true(src.contains("func _on_dynamic_action_pressed"), "input (press->PlanController/SubmenuController) stays in the view")
	assert_true(src.contains("func _on_action_hover"), "hover (shared InfoBar) stays in the view")


# --- Behavioural pin: the GROUPED grid the renderer builds ---------------------------------

func test_grouped_render_pins_category_sections_and_buttons():
	var host := _make_host("proposed")
	var renderer = ActionBarRenderer.new(host)
	renderer.render(_sample_actions())

	# One top-level stack holds the whole grouped hand.
	var top := host.actions_list.get_children()
	assert_eq(top.size(), 1, "grouped hand mounts a single stack under actions_list")
	var stack: Node = top[0]
	assert_true(stack is VBoxContainer, "the stack is a VBoxContainer")

	# Two categories present (hiring, resources) -> header+blist each -> 4 children, hiring first.
	var sections := stack.get_children()
	assert_eq(sections.size(), 4, "two categories -> two [header, blist] pairs")

	var hiring_header: Button = sections[0]
	var hiring_blist: Node = sections[1]
	var resources_header: Button = sections[2]
	var resources_blist: Node = sections[3]

	assert_true(hiring_header is Button and hiring_header.toggle_mode, "hiring header is a collapsible toggle Button")
	assert_eq(hiring_header.text, "v Hiring (2)", "hiring header shows the display name + action count")
	assert_eq(resources_header.text, "v Resources (1)", "resources header shows the display name + count")

	# hiring rows: hire_staff (affordable) then advertise (coming-soon), in payload order.
	var hiring_rows := hiring_blist.get_children()
	assert_eq(hiring_rows.size(), 2, "hiring lists both of its actions")

	var hire_row: Button = hiring_rows[0]
	assert_eq(hire_row.text, "  Hire Staff", "affordable row shows the plain indented name")
	assert_false(hire_row.disabled, "affordable action row is enabled")

	var advertise_row: Button = hiring_rows[1]
	assert_eq(advertise_row.text, "  Advertise [SOON]", "coming-soon row is badged [SOON]")
	assert_true(advertise_row.disabled, "coming-soon row is greyed out (disabled)")
	assert_eq(advertise_row.modulate, Color(0.35, 0.35, 0.35), "coming-soon grey-out modulate is pinned")

	# resources row: buy_compute costs 100000 but host has 1000 -> unaffordable grey-out.
	var resources_rows := resources_blist.get_children()
	assert_eq(resources_rows.size(), 1, "resources lists its one action")
	var compute_row: Button = resources_rows[0]
	assert_eq(compute_row.text, "  Buy Compute", "unaffordable row keeps its plain name")
	assert_true(compute_row.disabled, "unaffordable action row is greyed out (disabled)")
	assert_eq(compute_row.modulate, Color(0.4, 0.4, 0.4), "unaffordable grey-out modulate is pinned")


# --- Behavioural pin: the classic FLAT grid, same affordability/coming-soon rules ----------

func test_flat_render_pins_tiles_and_greyout():
	var host := _make_host("classic")
	var renderer = ActionBarRenderer.new(host)
	renderer.render(_sample_actions())

	# Flat layout mounts a single icon_stack; all three actions become tiles in it.
	var top := host.actions_list.get_children()
	assert_eq(top.size(), 1, "flat hand mounts a single icon_stack under actions_list")
	var tiles := top[0].get_children()
	assert_eq(tiles.size(), 3, "all three actions render as flat icon tiles")

	# tiles are in category_order then payload order: hire_staff, advertise, buy_compute.
	var hire_tile: Button = tiles[0]
	assert_false(hire_tile.disabled, "affordable tile is enabled")
	assert_eq(hire_tile.text, "1", "first affordable tile carries its keyboard badge")

	var advertise_tile: Button = tiles[1]
	assert_true(advertise_tile.disabled, "coming-soon tile is disabled")
	assert_eq(advertise_tile.text, "SOON", "coming-soon tile is badged SOON instead of a number")
	assert_eq(advertise_tile.modulate, Color(0.35, 0.35, 0.35), "coming-soon tile grey-out is pinned")

	var compute_tile: Button = tiles[2]
	assert_true(compute_tile.disabled, "unaffordable tile is disabled")
	assert_eq(compute_tile.modulate, Color(0.4, 0.4, 0.4), "unaffordable tile grey-out is pinned")

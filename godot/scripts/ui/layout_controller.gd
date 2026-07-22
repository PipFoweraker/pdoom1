class_name LayoutController
extends Node
## A/B layout controller (UI_PROPOSALS_2026-07-22 section 4). Sibling to ScreenModeController,
## same proven move: it does NOT duplicate scenes and does NOT rebuild the widget tree -- it
## REGISTERS the existing container nodes and flips a handful of their layout properties from a
## persisted flag (GameConfig.ui_layout). "classic" restores the captured scene defaults so it
## stays pixel-identical to today; "proposed" applies the P6/P9/P10/P11 container deltas.
##
## Every A/B difference this node owns lives in _apply_proposed / _restore_classic so the two
## arrangements are legible side by side and easy to tune. apply_layout() is idempotent: it
## always restores classic first, then layers proposed on top, so flip->flip->flip never drifts.
##
## VIEW-ONLY (ADR-0006): container properties only -- zero writes to game state, zero RNG, no
## turn-logic. P9 (grouped action submenus) and P10 (the committed-queue gantt) need game-data
## population hooks, so main_ui gates those on is_proposed(); this node owns the pure reflow:
##   P6  -- clamp the OfficeCat so it can't dominate the PLAN centre.
##   P11 -- rebalance the three column stretch ratios (reclaim the instrument dead-zone, give
##          the WATCH office-floor more of the right side) + dock the orphaned upgrades list.

signal layout_changed(name: String)

var current: String = "classic"

# Registered reflow targets (set by main_ui via register_targets()).
var _plan_col: Control
var _instrument_col: Control
var _watch_col: Control
var _office_cat: Control
var _plan_screen: Control            # VBox that parents the upgrades label + scroll
var _upgrades_label: Control
var _upgrades_scroll: Control

# Captured scene defaults (so "classic" restores byte-for-byte). Captured once, before any flip.
var _captured := false
var _orig_plan_ratio: float = 0.3
var _orig_instrument_ratio: float = 0.3
var _orig_watch_ratio: float = 0.4
var _orig_cat_min: Vector2 = Vector2.ZERO
var _orig_cat_hflags: int = 0
var _orig_upgrades_scroll_min: Vector2 = Vector2.ZERO

# The proposed-mode upgrades dock (a framed panel built on demand; freed on restore).
var _dock_panel: PanelContainer = null

# Proposed column split: tighten the instrument column (D5/D6 dead-zone) and hand the reclaimed
# width to WATCH so the office floor breathes (P11). PLAN holds so the hand doesn't reflow.
const _PROPOSED_PLAN_RATIO := 0.30
const _PROPOSED_INSTRUMENT_RATIO := 0.24
const _PROPOSED_WATCH_RATIO := 0.46


func register_targets(plan_col: Control, instrument_col: Control, watch_col: Control,
		office_cat: Control, plan_screen: Control, upgrades_label: Control,
		upgrades_scroll: Control) -> void:
	"""Hand the controller the existing nodes it reflows. Captures their scene-default values
	on first call so classic can always restore them exactly."""
	_plan_col = plan_col
	_instrument_col = instrument_col
	_watch_col = watch_col
	_office_cat = office_cat
	_plan_screen = plan_screen
	_upgrades_label = upgrades_label
	_upgrades_scroll = upgrades_scroll
	_capture_defaults()


func _capture_defaults() -> void:
	if _captured:
		return
	if _plan_col != null:
		_orig_plan_ratio = _plan_col.size_flags_stretch_ratio
	if _instrument_col != null:
		_orig_instrument_ratio = _instrument_col.size_flags_stretch_ratio
	if _watch_col != null:
		_orig_watch_ratio = _watch_col.size_flags_stretch_ratio
	if _office_cat != null:
		_orig_cat_min = _office_cat.custom_minimum_size
		_orig_cat_hflags = _office_cat.size_flags_horizontal
	if _upgrades_scroll != null:
		_orig_upgrades_scroll_min = _upgrades_scroll.custom_minimum_size
	_captured = true


func is_proposed() -> bool:
	return current == "proposed"


func apply_layout(name: String) -> void:
	"""Set the arrangement. Idempotent: restore classic, then (for proposed) layer the deltas.
	Unknown names coerce to classic so a bad flag can never leave the UI half-reflowed."""
	var target := name if name == "proposed" else "classic"
	_restore_classic()
	if target == "proposed":
		_apply_proposed()
	current = target
	layout_changed.emit(current)


func toggle() -> String:
	"""Flip between the two arrangements and return the new one (for the dev hotkey)."""
	apply_layout("classic" if current == "proposed" else "proposed")
	return current


# --- classic (restore captured scene defaults) --------------------------------------------

func _restore_classic() -> void:
	if not _captured:
		return
	if _plan_col != null:
		_plan_col.size_flags_stretch_ratio = _orig_plan_ratio
	if _instrument_col != null:
		_instrument_col.size_flags_stretch_ratio = _orig_instrument_ratio
	if _watch_col != null:
		_watch_col.size_flags_stretch_ratio = _orig_watch_ratio
	if _office_cat != null:
		_office_cat.custom_minimum_size = _orig_cat_min
		_office_cat.size_flags_horizontal = _orig_cat_hflags
	_undock_upgrades()


# --- proposed (P6 + P11 container deltas) --------------------------------------------------

func _apply_proposed() -> void:
	# P11: rebalance the columns -- reclaim the instrument dead-zone for the WATCH office floor.
	if _plan_col != null:
		_plan_col.size_flags_stretch_ratio = _PROPOSED_PLAN_RATIO
	if _instrument_col != null:
		_instrument_col.size_flags_stretch_ratio = _PROPOSED_INSTRUMENT_RATIO
	if _watch_col != null:
		_watch_col.size_flags_stretch_ratio = _PROPOSED_WATCH_RATIO
	# P6: clamp the cat so it can't dominate the PLAN centre (no-op while it is hidden in the
	# scene; the clamp bites the moment the ambient-office lane un-hides it).
	if _office_cat != null:
		_office_cat.custom_minimum_size = Vector2(0, 0)
		_office_cat.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	# P11: dock the orphaned upgrades list into a framed panel (D6 -- stops it reading as
	# floating below the hand).
	_dock_upgrades()


func _dock_upgrades() -> void:
	"""Wrap the upgrades label + scroll in a titled PanelContainer. This is the ONE reparent in
	the harness (a single leaf subtree, exactly the doc-endorsed move): the object references
	main_ui/plan_screen hold to upgrades_list stay valid because reparent moves nodes, not refs.
	Fully reversible -- _undock_upgrades puts them back at the same index for pixel-identical
	classic."""
	if _dock_panel != null or _plan_screen == null or _upgrades_label == null or _upgrades_scroll == null:
		return
	var idx := _upgrades_label.get_index()
	_dock_panel = PanelContainer.new()
	_dock_panel.name = "UpgradesDock"
	_dock_panel.size_flags_vertical = Control.SIZE_SHRINK_END
	TerminalTheme.style_panel(_dock_panel, TerminalTheme.AMBER_DIM, TerminalTheme.PANEL_BG_DEEP)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 2)
	_dock_panel.add_child(vb)
	_plan_screen.add_child(_dock_panel)
	_plan_screen.move_child(_dock_panel, idx)
	_upgrades_label.reparent(vb)
	_upgrades_scroll.reparent(vb)
	# Bound the scroll so a long upgrades list can't stretch back into the reclaimed dead-zone.
	_upgrades_scroll.custom_minimum_size = Vector2(0, 132)


func _undock_upgrades() -> void:
	if _dock_panel == null:
		return
	var idx := _dock_panel.get_index()
	if _upgrades_label != null and _plan_screen != null:
		_upgrades_label.reparent(_plan_screen)
		_plan_screen.move_child(_upgrades_label, idx)
	if _upgrades_scroll != null and _plan_screen != null:
		_upgrades_scroll.reparent(_plan_screen)
		_plan_screen.move_child(_upgrades_scroll, idx + 1)
		_upgrades_scroll.custom_minimum_size = _orig_upgrades_scroll_min
	_dock_panel.queue_free()
	_dock_panel = null

extends RefCounted
class_name SubmenuChrome
## Shared submenu dialog chrome -- extracted from main_ui.gd (#622, build lane L10).
##
## The #510 polish set: solid panel styling, the clickable [X] + "[ESC] close" hint,
## alignment of a submenu to the action button that opened it, and the button lookup.
## Pure static helpers: the host keeps ownership of active_dialog state and passes a
## close callback in, so any screen (current submenus, future L2/L3 scenes) can reuse
## the same chrome without inheriting MainUI's dialog bookkeeping.

static func find_action_button(actions_list: Control, action_id: String) -> Button:
	"""Locate the left-panel icon button that opened a submenu, by action_id meta."""
	if actions_list == null:
		return null
	for child in actions_list.get_children():
		if child is VBoxContainer:
			for b in child.get_children():
				if b is Button and b.get_meta("action_id", "") == action_id:
					return b
	return null

static func style_panel(dialog: Control) -> void:
	"""Near-opaque panel + border so submenus read as solid panels, not see-through
	overlays on the action icons (playtest feedback: screen5)."""
	# Palette-sourced (#743): deep-aubergine dread ground + dimmed cozy-amber frame,
	# matching the menu_theme.tres modal register instead of the old gray-green tone.
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.09, 0.04, 0.11, 0.97)
	style.set_border_width_all(2)
	style.border_color = Color(0.91, 0.64, 0.24, 0.6)
	style.set_corner_radius_all(6)
	dialog.add_theme_stylebox_override("panel", style)

static func add_close_affordance(dialog: Control, on_close: Callable) -> void:
	"""Solid panel styling + clickable [X] top-right + '[ESC] close' hint bottom-right (#510).
	Skips panel styling if the caller already set a bespoke 'panel' stylebox (e.g. the trend
	expand panel or the leather ledger), so we don't clobber it. on_close is the host's
	close routine (it owns the active_dialog state)."""
	if not dialog.has_theme_stylebox_override("panel"):
		style_panel(dialog)

	var close_btn := Button.new()
	close_btn.text = "X"
	close_btn.focus_mode = Control.FOCUS_NONE
	close_btn.custom_minimum_size = Vector2(24, 24)
	close_btn.size = Vector2(24, 24)
	close_btn.position = Vector2(dialog.size.x - 30, 6)
	close_btn.add_theme_font_size_override("font_size", 12)
	close_btn.tooltip_text = "Close (ESC)"
	var x_style := StyleBoxFlat.new()
	x_style.bg_color = Color(0.30, 0.18, 0.18, 0.95)
	x_style.set_corner_radius_all(4)
	close_btn.add_theme_stylebox_override("normal", x_style)
	var x_hover := x_style.duplicate()
	x_hover.bg_color = Color(0.55, 0.22, 0.22, 1.0)
	close_btn.add_theme_stylebox_override("hover", x_hover)
	close_btn.pressed.connect(on_close)
	dialog.add_child(close_btn)

	# Footer hint, bottom-RIGHT (clear of centered footer labels like "Pool: 3/6")
	var hint := Label.new()
	hint.text = "[ESC] close"
	hint.add_theme_font_size_override("font_size", 10)
	hint.add_theme_color_override("font_color", Color(0.65, 0.7, 0.65))
	hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	hint.size = Vector2(110, 16)
	hint.position = Vector2(dialog.size.x - 122, dialog.size.y - 20)
	dialog.add_child(hint)

	# Universal escape contract (fix/ui-no-dead-ends): make the panel honor ui_cancel
	# (Esc) on its OWN via a helper node, so it is escapable even without a host input
	# router. In-game MainUI._input still consumes Esc first (this never double-fires);
	# this is the intrinsic fallback that stops the panel ever becoming a dead-end.
	EscToClose.attach(dialog, on_close)

static func align_to_button(dialog: Control, button: Button) -> void:
	"""Position a submenu just to the RIGHT of the action button that opened it and
	top-aligned to it, so it clearly expands from that row rather than over it
	(#510 + playtest feedback). Clamped to the viewport. The dialog must already be
	in the tree (every _show_*_submenu builder adds it before decorating)."""
	var parent := dialog.get_parent()
	if parent == null:
		return
	var viewport := dialog.get_viewport()
	if viewport == null:
		return
	var gap: float = 10.0
	var view := viewport.get_visible_rect().size
	var target_x: float = button.global_position.x + button.size.x + gap - parent.global_position.x
	var target_y: float = button.global_position.y - parent.global_position.y
	var max_x: float = maxf(40.0, view.x - dialog.size.x - 10.0)
	var max_y: float = maxf(40.0, view.y - dialog.size.y - 10.0)
	dialog.position = Vector2(clampf(target_x, 40.0, max_x), clampf(target_y, 40.0, max_y))

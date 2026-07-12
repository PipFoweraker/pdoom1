extends CanvasLayer
class_name DevModeOverlay
## DEV MODE overlay — the owner's old pre-Godot dev mode, rebuilt richer.
##
## Press backslash (the `dev_mode` keybind) to toggle. Left column mirrors the verbose
## PowerShell logs on-screen (full live game state, refreshed each turn / state change);
## right column gives dev "pokes" to set up test situations. Gated on BuildInfo.DEV_BUILD
## so it never ships in a clean release cut.
##
## Built entirely in code (no .tscn) following dev_build_badge.gd, and added at runtime via
## `main_ui.gd`. The readout content comes from the pure, unit-tested DevModeReadout builder;
## this file is the renderer + control wiring. The on-screen layout/toggle needs a human eye.

## Above the F3 debug overlay (128), below the DEV BUILD badge (200) so the badge stays visible.
const OVERLAY_LAYER := 150

# Dev nudge step sizes — coarse enough to set up test situations fast.
const MONEY_STEP := 10000.0
const COMPUTE_STEP := 10.0
const REP_STEP := 5.0
const DOOM_STEP := 5.0

## Reference to the MainUI node so jump buttons can drive its in-place screens
## (ledger / travel / employee). Set by whoever instantiates this overlay.
var main_ui: Node = null

var _root: Control = null
var _info_vbox: VBoxContainer = null
var _event_dropdown: OptionButton = null
var _built := false


## Resolve the *live* GameManager that MainUI actually drives (#600).
## main.tscn instances a scene-local `GameManager` node that MainUI holds as `game_manager`;
## that node — NOT the bareword `GameManager` autoload singleton — owns the live `state`.
## The autoload's `state` is never populated, which is why every readout previously showed
## "No active game". Prefer MainUI's instance; fall back to the autoload only when unwired.
func _live_gm() -> Node:
	if main_ui != null:
		var gm = main_ui.get("game_manager")
		if gm != null:
			return gm
	return GameManager


func _ready() -> void:
	layer = OVERLAY_LAYER
	# Gate on dev build: in a release cut this overlay builds nothing and stays inert.
	if not BuildInfo.is_dev_build():
		visible = false
		return
	_build_ui()
	_built = true
	if is_instance_valid(KeybindManager):
		KeybindManager.dev_mode_toggled.connect(_on_toggle)
	# Track the live manager MainUI drives, so nudges / turns refresh the readout (#600).
	var gm := _live_gm()
	if gm != null and gm.has_signal("game_state_updated") \
			and not gm.game_state_updated.is_connected(_on_state_updated):
		gm.game_state_updated.connect(_on_state_updated)


func _on_toggle() -> void:
	if not _built or _root == null:
		return
	_root.visible = not _root.visible
	if _root.visible:
		_render()


func _on_state_updated(_state: Dictionary) -> void:
	# Live-update while open, so the readout tracks each turn / nudge without a re-toggle.
	if _root != null and _root.visible:
		_render()


# --- UI construction -------------------------------------------------------

func _build_ui() -> void:
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE  # let clicks through outside the panel
	_root.visible = false
	add_child(_root)

	# Panel pinned to the left ~ half of the screen, so the game stays visible/clickable at right.
	var panel := PanelContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_LEFT_WIDE)
	panel.custom_minimum_size = Vector2(760, 0)
	panel.offset_right = 760
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.05, 0.05, 0.08, 0.94)
	style.border_color = Color(0.9, 0.6, 0.1)
	style.set_border_width_all(2)
	style.set_content_margin_all(10)
	panel.add_theme_stylebox_override("panel", style)
	_root.add_child(panel)

	var outer := VBoxContainer.new()
	panel.add_child(outer)

	# Header
	var header := HBoxContainer.new()
	outer.add_child(header)
	var title := Label.new()
	title.text = "🛠  DEV MODE"
	title.add_theme_font_size_override("font_size", 22)
	title.add_theme_color_override("font_color", Color(1.0, 0.75, 0.2))
	header.add_child(title)
	var stamp := Label.new()
	stamp.text = "   " + BuildInfo.get_badge_text()
	stamp.add_theme_font_size_override("font_size", 11)
	stamp.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	stamp.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	stamp.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	header.add_child(stamp)
	var close_btn := Button.new()
	close_btn.text = "✕"
	close_btn.focus_mode = Control.FOCUS_NONE
	close_btn.pressed.connect(func(): _root.visible = false)
	header.add_child(close_btn)

	var hint := Label.new()
	hint.text = "Backslash toggles · dev build only · not shipped in release"
	hint.add_theme_font_size_override("font_size", 10)
	hint.add_theme_color_override("font_color", Color(0.55, 0.55, 0.6))
	outer.add_child(hint)

	var sep := HSeparator.new()
	outer.add_child(sep)

	# Body: INFO (scroll) on the left, CONTROLS on the right.
	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(body)

	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.custom_minimum_size = Vector2(470, 520)
	body.add_child(scroll)
	_info_vbox = VBoxContainer.new()
	_info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_info_vbox)

	body.add_child(_build_controls())

	_render()


func _build_controls() -> Control:
	var col := VBoxContainer.new()
	col.custom_minimum_size = Vector2(250, 0)

	col.add_child(_section_label("JUMP TO"))
	col.add_child(_action_button("📖 Ledger", _jump_ledger))
	col.add_child(_action_button("✈ Travel", _jump_travel))
	col.add_child(_action_button("🏆 Leaderboard*", _jump_leaderboard))
	col.add_child(_action_button("👥 Employee", _jump_employee))
	col.add_child(_action_button("⚙ Settings*", _jump_settings))
	col.add_child(_action_button("F3 Risk overlay", _jump_f3))
	var jump_note := Label.new()
	jump_note.text = "* full-scene swap: leaves current game"
	jump_note.add_theme_font_size_override("font_size", 9)
	jump_note.add_theme_color_override("font_color", Color(0.55, 0.55, 0.6))
	col.add_child(jump_note)

	col.add_child(HSeparator.new())
	col.add_child(_section_label("NUDGE RESOURCES"))
	col.add_child(_nudge_row("Money", "money", MONEY_STEP))
	col.add_child(_nudge_row("Doom", "doom", DOOM_STEP))
	col.add_child(_nudge_row("Reputation", "reputation", REP_STEP))
	col.add_child(_nudge_row("Compute", "compute", COMPUTE_STEP))

	col.add_child(HSeparator.new())
	col.add_child(_section_label("TRIGGERS"))
	col.add_child(_action_button("⏭ Advance turn (dev)", _advance_turn))
	_event_dropdown = OptionButton.new()
	_event_dropdown.focus_mode = Control.FOCUS_NONE
	_populate_event_dropdown()
	col.add_child(_event_dropdown)
	col.add_child(_action_button("Queue selected event", _queue_selected_event))
	col.add_child(_action_button("🎲 Trigger random event", _trigger_random_event))
	var ev_note := Label.new()
	ev_note.text = "Queued events surface on turn processing."
	ev_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ev_note.custom_minimum_size = Vector2(240, 0)
	ev_note.add_theme_font_size_override("font_size", 9)
	ev_note.add_theme_color_override("font_color", Color(0.55, 0.55, 0.6))
	col.add_child(ev_note)

	return col


func _section_label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", 12)
	l.add_theme_color_override("font_color", Color(1.0, 0.75, 0.2))
	return l


func _action_button(text: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_NONE
	b.pressed.connect(cb)
	return b


func _nudge_row(label: String, field: String, step: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	var l := Label.new()
	l.text = label
	l.custom_minimum_size = Vector2(90, 0)
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(l)
	var minus := Button.new()
	minus.text = "−"
	minus.focus_mode = Control.FOCUS_NONE
	minus.pressed.connect(func(): _nudge(field, -step))
	row.add_child(minus)
	var plus := Button.new()
	plus.text = "+"
	plus.focus_mode = Control.FOCUS_NONE
	plus.pressed.connect(func(): _nudge(field, step))
	row.add_child(plus)
	return row


func _populate_event_dropdown() -> void:
	_event_dropdown.clear()
	for e in GameEvents.get_all_events():
		var label := str(e.get("name", e.get("id", "?")))
		_event_dropdown.add_item(label)
		_event_dropdown.set_item_metadata(_event_dropdown.item_count - 1, str(e.get("id", "")))


# --- Rendering -------------------------------------------------------------

func _render() -> void:
	if _info_vbox == null:
		return
	for c in _info_vbox.get_children():
		_info_vbox.remove_child(c)
		c.queue_free()
	var gm := _live_gm()
	var state = gm.state if gm != null else null
	for section in DevModeReadout.build_sections(state):
		var head := Label.new()
		head.text = "▸ " + str(section["title"])
		head.add_theme_font_size_override("font_size", 14)
		head.add_theme_color_override("font_color", Color(0.5, 0.85, 1.0))
		_info_vbox.add_child(head)
		var body := Label.new()
		body.text = "\n".join(PackedStringArray(section["lines"]))
		body.add_theme_font_size_override("font_size", 12)
		body.add_theme_color_override("font_color", Color(0.85, 0.85, 0.85))
		_info_vbox.add_child(body)
		_info_vbox.add_child(HSeparator.new())


# --- Control handlers ------------------------------------------------------

func _nudge(field: String, delta: float) -> void:
	var gm := _live_gm()
	var s = gm.state if gm != null else null
	if s == null:
		return
	match field:
		"money":
			s.money = max(0.0, s.money + delta)
		"compute":
			s.compute = max(0.0, s.compute + delta)
		"reputation":
			s.reputation = clampf(s.reputation + delta, 0.0, 100.0)
		"doom":
			s.doom = clampf(s.doom + delta, 0.0, 100.0)
			if s.doom_system != null:
				s.doom_system.current_doom = s.doom
	# Emit on the LIVE manager so MainUI's readouts refresh (autoload signal has no listeners).
	if gm.has_signal("game_state_updated"):
		gm.game_state_updated.emit(s.to_dict())
	_render()


func _jump_ledger() -> void:
	if main_ui != null and main_ui.has_method("_show_ledger_screen"):
		main_ui._show_ledger_screen()


func _jump_travel() -> void:
	if main_ui != null and main_ui.has_method("_show_travel_submenu"):
		main_ui._show_travel_submenu()


func _jump_employee() -> void:
	# Employee is an in-place screen owned by TabManager (MainUI's parent). The E-key path
	# is currently disabled in-game, but the dev button still drives it directly.
	var tm := main_ui.get_parent() if main_ui != null else null
	if tm != null and tm.has_method("show_employee_screen"):
		tm.show_employee_screen()


func _jump_leaderboard() -> void:
	get_tree().change_scene_to_file("res://scenes/leaderboard_screen.tscn")


func _jump_settings() -> void:
	get_tree().change_scene_to_file("res://scenes/settings_menu.tscn")


func _jump_f3() -> void:
	if is_instance_valid(KeybindManager):
		KeybindManager.debug_overlay_toggled.emit()


func _advance_turn() -> void:
	# Dev advance: mirror end_turn()'s AP conversion + turn execution, but bypass the
	# "no actions queued" guard so a turn can be forced even with an empty queue.
	var gm := _live_gm()
	if not is_instance_valid(gm) or gm.state == null or gm.turn_manager == null:
		return
	gm.state.action_points -= gm.state.committed_ap
	gm.state.committed_ap = 0
	gm.turn_manager.execute_turn()
	gm.game_state_updated.emit(gm.state.to_dict())
	if not gm.state.game_over:
		gm.start_next_turn()
	_render()


func _queue_event(event_id: String) -> void:
	var gm := _live_gm()
	if not is_instance_valid(gm) or gm.state == null or event_id == "":
		return
	# Inject into the pending queue exactly like SeedSchedule's inject_event cause does.
	gm.state.pending_events.append({"id": event_id, "scheduled": true})
	if is_instance_valid(NotificationManager) and NotificationManager.has_method("info"):
		NotificationManager.info("Dev: queued event '%s' (fires on turn processing)" % event_id)
	_render()


func _queue_selected_event() -> void:
	if _event_dropdown == null or _event_dropdown.item_count == 0:
		return
	var idx := _event_dropdown.selected
	if idx < 0:
		idx = 0
	_queue_event(str(_event_dropdown.get_item_metadata(idx)))


func _trigger_random_event() -> void:
	var all := GameEvents.get_all_events()
	if all.is_empty():
		return
	var gm := _live_gm()
	var idx := 0
	if is_instance_valid(gm) and gm.state != null and gm.state.rng != null:
		idx = gm.state.rng.randi() % all.size()
	else:
		idx = randi() % all.size()
	_queue_event(str(all[idx].get("id", "")))

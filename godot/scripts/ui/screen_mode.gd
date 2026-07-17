class_name ScreenModeController
extends Node
## Plan/Watch two-screen mode controller (BUILD_BRIEF_PLAN_WATCH_UI Lane 1 / Phase A).
##
## The model (ruled): TWO screens with a mode switch between them.
##   PLAN  = strategy — lay out the month before it plays (the hand / queue / team).
##   WATCH = tactics  — the committed month plays out in day-ticks (feed / doom / windows).
##   COMMIT THE MONTH transitions PLAN -> WATCH; month-end review returns to PLAN.
##
## Phase-A scaffold approach: this does NOT reparent the existing widget tree (main_ui.gd
## is heavily coupled to absolute node paths — moving nodes would break it). Instead it
## REGISTERS the existing panels as plan-only / watch-only and toggles their visibility,
## plus owns two NEW pieces of chrome it builds itself: the mode BANNER and the WATCH
## control strip (playback speed + day/reserve readout). Follow-up lanes promote this into
## genuinely separate PlanScreen/WatchScreen scenes once the widget coupling is untangled.

enum Mode { PLAN, WATCH }

signal mode_changed(mode: int)
signal speed_changed(seconds: float)   # WATCH speed dial -> game_manager.day_tick_seconds

var current_mode: int = Mode.PLAN

# NEW chrome this controller owns (built here, mounted by main_ui).
var banner: PanelContainer
var watch_bar: PanelContainer
var _banner_label: RichTextLabel
var _toggle_button: Button       # manual PLAN<->WATCH switch, lives in the banner
var _day_label: Label
var _reserve_label: Label

# Existing panels toggled per mode (registered by main_ui).
var _plan_only: Array[Node] = []
var _watch_only: Array[Node] = []

# Speed presets for the WATCH playback dial (seconds per visible day-tick).
const _SPEEDS := {"1x": 0.20, "2x": 0.10, "4x": 0.05}


func register_plan_only(n: Node) -> void:
	if n != null and not _plan_only.has(n):
		_plan_only.append(n)

func register_watch_only(n: Node) -> void:
	if n != null and not _watch_only.has(n):
		_watch_only.append(n)


func build_banner() -> PanelContainer:
	"""The mode banner — a boxed strip naming the current screen + its verb. Amber in PLAN,
	green in WATCH (the two registers). main_ui inserts the returned node under the TopBar."""
	banner = PanelContainer.new()
	banner.name = "ModeBanner"
	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 8)
	margin.add_theme_constant_override("margin_right", 8)
	margin.add_theme_constant_override("margin_top", 2)
	margin.add_theme_constant_override("margin_bottom", 2)
	banner.add_child(margin)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	margin.add_child(row)
	_banner_label = RichTextLabel.new()
	_banner_label.bbcode_enabled = true
	_banner_label.fit_content = true
	_banner_label.scroll_active = false
	_banner_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_banner_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_banner_label.add_theme_font_override("normal_font", TerminalTheme.mono_font())
	row.add_child(_banner_label)
	# Manual view toggle (quick-win): flip PLAN<->WATCH at will so the player can look
	# things over. Text shows the target view; also bound to V in main_ui. VIEW-only.
	_toggle_button = Button.new()
	_toggle_button.focus_mode = Control.FOCUS_NONE
	_toggle_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_toggle_button.tooltip_text = "Switch between PLAN and WATCH views (V) -- look things over at will."
	_toggle_button.pressed.connect(toggle_mode)
	row.add_child(_toggle_button)
	return banner


func build_watch_bar() -> PanelContainer:
	"""The WATCH-only control strip: playback speed dial + live day / reserve readout
	(brief WATCH header — playback controls + reserve remaining). Play/pause is a clean
	STUB for a follow-up lane; the speed dial is REAL (drives day_tick_seconds)."""
	watch_bar = PanelContainer.new()
	watch_bar.name = "WatchControls"
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	watch_bar.add_child(row)

	var tag := Label.new()
	tag.text = "▶ PLAYBACK"
	tag.add_theme_color_override("font_color", TerminalTheme.GREEN)
	tag.add_theme_font_override("font", TerminalTheme.mono_font())
	row.add_child(tag)

	# Play/pause — STUB (follow-up lane owns real pause; auto-pause on windows already works).
	var pause_stub := Button.new()
	pause_stub.text = "⏸"
	pause_stub.disabled = true
	pause_stub.tooltip_text = "Pause/resume — stub (follow-up lane). Windows already auto-pause playback."
	pause_stub.focus_mode = Control.FOCUS_NONE
	row.add_child(pause_stub)

	# Speed dial — REAL: sets game_manager.day_tick_seconds via speed_changed.
	for key in ["1x", "2x", "4x"]:
		var b := Button.new()
		b.text = key
		b.focus_mode = Control.FOCUS_NONE
		b.tooltip_text = "Playback speed"
		b.pressed.connect(func(): speed_changed.emit(_SPEEDS[key]))
		row.add_child(b)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer)

	_day_label = Label.new()
	_day_label.text = "day —"
	_day_label.add_theme_color_override("font_color", TerminalTheme.TEXT)
	_day_label.add_theme_font_override("font", TerminalTheme.mono_font())
	row.add_child(_day_label)

	var sep := Label.new()
	sep.text = "·"
	sep.add_theme_color_override("font_color", TerminalTheme.RULE_BRIGHT)
	row.add_child(sep)

	_reserve_label = Label.new()
	_reserve_label.text = "reserve —"
	_reserve_label.tooltip_text = "Held Attention — the slack available to spend on mid-month response windows."
	_reserve_label.add_theme_color_override("font_color", TerminalTheme.AMBER)
	_reserve_label.add_theme_font_override("font", TerminalTheme.mono_font())
	row.add_child(_reserve_label)

	return watch_bar


func enter_plan() -> void:
	set_mode(Mode.PLAN)

func enter_watch() -> void:
	set_mode(Mode.WATCH)

func toggle_mode() -> void:
	"""Manual PLAN<->WATCH switch (quick-win). VIEW-only: flips which screen subtree is
	visible so the player can look things over; never touches the turn loop / RNG. The
	game's own phase transitions (COMMIT / month review) still drive the mode as before;
	this just lets the player peek in between."""
	set_mode(Mode.WATCH if current_mode == Mode.PLAN else Mode.PLAN)


func set_mode(m: int) -> void:
	current_mode = m
	var is_plan := m == Mode.PLAN
	for n in _plan_only:
		if is_instance_valid(n):
			(n as CanvasItem).visible = is_plan
	for n in _watch_only:
		if is_instance_valid(n):
			(n as CanvasItem).visible = not is_plan
	_refresh_banner()
	mode_changed.emit(m)


func update_from_state(state: Dictionary) -> void:
	"""Refresh WATCH readouts (day / reserve) from the live game state each tick."""
	var cal: Dictionary = state.get("calendar", {})
	if _day_label != null and not cal.is_empty():
		var months := ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
		var mi: int = int(cal.get("month", 1)) - 1
		var mname: String = months[mi] if mi >= 0 and mi < 12 else "?"
		_day_label.text = "day %d — %s %d" % [int(cal.get("day", 0)), mname, int(cal.get("year", 0))]
	if _reserve_label != null:
		var mp: Dictionary = state.get("month_plan", {})
		var total := int(mp.get("attention_total", 0))
		var spent := int(mp.get("attention_spent", 0))
		var reserved := int(mp.get("attention_reserved", 0))
		# Remaining slack = whatever isn't committed to strategic work this month.
		var remaining: int = max(0, total - spent)
		if reserved > 0:
			remaining = reserved
		_reserve_label.text = "reserve %d" % remaining


func _refresh_banner() -> void:
	if _toggle_button != null:
		# Button shows the view it switches TO.
		_toggle_button.text = "WATCH >" if current_mode == Mode.PLAN else "< PLAN"
	if _banner_label == null:
		return
	if current_mode == Mode.PLAN:
		if banner != null:
			TerminalTheme.style_panel(banner, TerminalTheme.AMBER_DIM, TerminalTheme.PANEL_BG_DEEP)
		_banner_label.text = "[color=#ffb833]▓▓ PLAN[/color]  [color=#a87a28]· strategy · lay out the month, then[/color] [color=#ffb833]COMMIT THE MONTH ▶[/color]"
	else:
		if banner != null:
			TerminalTheme.style_panel(banner, TerminalTheme.GREEN_DIM, TerminalTheme.PANEL_BG_DEEP)
		_banner_label.text = "[color=#5cec78]▓▓ WATCH[/color]  [color=#369048]· tactics · the month plays out — respond to windows as they arrive[/color]"

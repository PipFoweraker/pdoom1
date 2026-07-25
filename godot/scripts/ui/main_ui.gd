extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements (TopBar now has all resources in one line)
# --- Shared top/bottom chrome (resource readouts + control bar; not screen-specific) ---
@onready var turn_label = $TopBar/TurnLabel
@onready var turn_count_label = $TopBar/TurnCountLabel
@onready var money_label = $TopBar/MoneyLabel
@onready var compute_label = $TopBar/ComputeLabel
@onready var research_label = $TopBar/ResearchLabel
@onready var papers_label = $TopBar/PapersLabel
@onready var reputation_label = $TopBar/ReputationLabel
@onready var ap_label = $TopBar/APLabel
@onready var phase_label = $BottomBar/PhaseLabel
@onready var info_label = $InfoBar/MarginContainer/InfoLabel

# --- The three extracted screens (BUILD_BRIEF_PLAN_WATCH_UI Lane 1) ---
# PLAN (strategy) and WATCH (tactics) are real, script-backed screen subtrees; the shared
# InstrumentPanel (doom / roster / committed-month queue) stays visible in both modes.
# main_ui drives game logic against the screens' PUBLIC members rather than reaching through
# absolute $ContentArea/<column>/... node paths -- that coupling is what the split untangles.
@onready var plan_screen: PlanScreen = $ContentArea/PlanScreen
@onready var instruments: InstrumentPanel = $ContentArea/InstrumentColumn
@onready var watch_screen: WatchScreen = $ContentArea/WatchScreen

# Leaf widgets, resolved THROUGH the owning screen. Child _ready runs before the parent's,
# so each screen's own @onready refs are already populated when these evaluate.
@onready var message_log = watch_screen.message_log
@onready var actions_list = plan_screen.actions_list
@onready var upgrades_list = plan_screen.upgrades_list
@onready var getting_started_hint = plan_screen.getting_started_hint
@onready var queue_container = instruments.queue_container
@onready var queue_hint = instruments.queue_hint
@onready var doom_meter = instruments.doom_meter
@onready var numeric_doom_label = instruments.numeric_doom_label
@onready var office_cat = instruments.office_cat
@onready var roster_container = instruments.roster_container

@onready var reserve_ap_button = $BottomBar/ControlButtons/ReserveAPButton
@onready var undo_last_button = $BottomBar/ControlButtons/UndoLastButton
@onready var clear_queue_button = $BottomBar/ControlButtons/ClearQueueButton
@onready var end_turn_button = $BottomBar/ControlButtons/EndTurnButton
@onready var commit_plan_button = $BottomBar/ControlButtons/CommitPlanButton
@onready var game_over_screen = $"../GameOverScreen"
@onready var bug_report_panel = $"../BugReportPanel"
@onready var bug_report_button = $BottomBar/BugReportButton
@onready var tab_manager = get_parent()
@onready var pause_menu = $"../../PauseMenu"

# Reference to GameManager
var game_manager: Node

# CARVE 1 (R4, docs/MAIN_UI_SEAM_MAP.md): the plan/attention/queue LOGIC lives in
# PlanController now. main_ui is the thin view -- it renders plan_controller.queued_actions
# and wires buttons to plan_controller.* calls; it owns no queue/cost/commit math.
var plan_controller: PlanController
# CARVE 2 (R5, docs/MAIN_UI_SEAM_MAP.md): the submenu/dialog orchestration -- one data-driven
# component replaces the seven copy-pasted _show_*_submenu builders. main_ui calls
# submenu_controller.open(action_id); hiring/travel stay bespoke and open() delegates back here.
var submenu_controller: SubmenuController
# CARVE 3 (R1/R5): the hiring candidate-card pipeline (pool panel, candidate + onboarding
# cards, offer dialog, in-flight tracker) lives in its own view module. main_ui keeps only a
# _show_hiring_submenu() shim + the update_inflight_display() HUD call.
var hiring_panel: HiringPanelController
# CARVE 4 (R1/R5): the travel/conferences submenu pipeline (actions grid, paper-status +
# upcoming-conferences sections, submit-paper / attend-conference sub-dialogs) -- the last
# bespoke submenu -- lives in its own view module. main_ui keeps only a _show_travel_submenu() shim.
var travel_panel: TravelPanelController
# CARVE 5 (R1, docs/MAIN_UI_SEAM_MAP.md): the ACTION-BAR RENDERING (the flat icon grid + the P9
# grouped collapsible sections) lives in ActionBarRenderer now -- a variant-ready seam so a
# dev-mode display variant can plug in with minimal surgery. main_ui keeps a thin
# _on_actions_available() shim (stores _last_actions for layout flips) and still owns input
# (_on_dynamic_action_pressed), hover (_on_action_hover), and the shared delegates.
var action_bar: ActionBarRenderer
# CARVE 6 (R6, docs/MAIN_UI_SEAM_MAP.md): the event/result PRESENTATION -- turning an executed
# action's result, an achievement unlock, or an engine error into feed-log lines (+ the PLAN
# error toast) -- lives in EventResultPresenter now. main_ui keeps thin signal shims that forward
# here and still owns the feed MODEL/rendering (log_message) the presenter writes through.
var event_result_presenter: EventResultPresenter
var research_quality_selector  # Issue #500
var doom_trend_graph  # #512 doom trend sparkline (script-instantiated)
var doom_breakdown  # #578 colour-coded per-source doom "blow-by-blow" (script-instantiated)
var event_dialog  # #622 L10: event dialog presenter (script-instantiated child)
var ledger_screen  # #622 L10: Liability Ledger UI (leather palette + summary button + screen builder)
var employee_panel  # #622 L10: employee roster + staff ID card (becomes L2's assignment surface)
var screen_mode: ScreenModeController  # Lane 1 / Phase A: PLAN<->WATCH two-screen mode controller
var layout_controller: LayoutController  # A/B layout harness (classic | proposed); container-reflow only
var queue_gantt: QueueGantt              # P10 committed-queue gantt (proposed layout only; pure view)
var _last_actions: Array = []            # last actions payload, re-rendered when the layout flips
var _ui_layout: String = "classic"       # active A/B layout; gates P9 grouped hand + P10 gantt
var _inflight_hiring_box: VBoxContainer  # in-flight hiring jobs + progress, mounted under the queue (VIEW-only)
# EE-7 (ADR-0012 loss legibility): per-resource "last turn" delta chips beside the
# money/compute/reputation/doom readouts. Snapshot at each turn boundary; a chip shows
# the change over the last completed turn, green=helped red=hurt (doom inverted).
var _delta_labels: Dictionary = {}       # resource key -> Label
var _prev_turn_snapshot: Dictionary = {}
var _last_delta_turn: int = -1
const _DELTA_GOOD := Color(0.35, 0.85, 0.40)
const _DELTA_BAD := Color(0.95, 0.30, 0.25)
# CARVE 5 (R1): the action-bar render config + new-unlock tracking (CATEGORY_HEADER_ICONS,
# COMING_SOON_*, HIDDEN_FROM_ACTION_BAR_IDS, _seen_unlocked_actions, _actions_primed) moved into
# ActionBarRenderer with the rendering that used them. FIRST_LEVER_* stays here -- it drives the
# cold-open nudge (_apply_first_lever_nudge), which is view-owned, not render config.
var current_turn_phase: String = "NOT_STARTED"

# First-lever nudge (#801 cold-open handoff). When GameConfig.show_first_lever_hint is set
# (by the cold-open on completion), pulse the hire button + point the getting-started hint at
# the lever, so a new player learns action->effect. Cleared after the first hire or turn 3.
# Pure presentation -- reads a transient flag, mutates no game state / RNG / score.
const FIRST_LEVER_ACTION_ID := "hire_staff"
const FIRST_LEVER_HINT_TEXT := "Advisor: doom is rising -- hire a researcher to lower it (the glowing button)."
var _first_lever_pulse_tween: Tween

# CARVE 5 (R1): COMING_SOON_ACTION_IDS / COMING_SOON_TOOLTIP_SUFFIX / HIDDEN_FROM_ACTION_BAR_IDS
# moved into ActionBarRenderer (they are action-bar RENDER config -- grey-out + hidden ids -- used
# only by the rendering that now lives there).

# P0 feed filter (playtest 2026-07-17): the arxiv/technical-research flavour deck floods the
# feed. Each logged line is recorded here with its channel; the "flavour" channel is hidden
# by default so real, actionable events aren't crowded out. The toggle flips this.
var _feed_lines: Array = []              # [{text: String, channel: String}, ...]
var _feed_important_only: bool = true    # default view hides the flavour spam
# Rival-intel filter (v0 News feedline / DQ-32): hide the "rivals" channel when the player
# opts out. Mirrors the persisted GameConfig.show_rivals_feed; display-only, determinism-safe.
var _feed_hide_rivals: bool = not GameConfig.show_rivals_feed
const FEED_MAX_LINES: int = 500          # cap the backing model so a long run stays bounded (trim oldest)

# Active dialog state for keyboard shortcuts
var active_dialog: Control = null
var active_dialog_buttons: Array = []

func _ready():
	print("[MainUI] Initializing UI...")

	# HUD tooltips that quote balance numbers are built from Balance here, so they
	# track the mechanic instead of drifting from a hardcoded literal in the scene
	# (#715 / issue like the version single-source). AP is difficulty-dependent, so
	# it is refreshed per-turn in the resource-update path instead.
	_apply_balance_tooltips()

	# Get GameManager reference -- the autoload singleton is the ONE GameManager
	# (L0 #620/#608: the duplicate scene-local node was removed from main.tscn)
	game_manager = GameManager

	# CARVE 1 (R4): stand up the plan/queue/attention controller over the same GameManager.
	plan_controller = PlanController.new(game_manager)

	# CARVE 2 (R5): stand up the submenu orchestration component. It composes this view's
	# shared shell helpers (_present_modal_dialog / _make_cost_label / active_dialog state) and
	# routes option queueing through plan_controller.
	submenu_controller = SubmenuController.new(self, plan_controller)

	# CARVE 3 (R1): stand up the hiring-pipeline view module (candidate cards, onboarding,
	# offer dialog, in-flight tracker). It composes this view's shared shell helpers.
	hiring_panel = HiringPanelController.new(self)

	# CARVE 4 (R1/R5): stand up the travel/conferences view module (actions grid, papers +
	# upcoming-conferences sections, submit-paper / attend-conference sub-dialogs). It composes
	# this view's shared shell + cost helpers.
	travel_panel = TravelPanelController.new(self)

	# CARVE 5 (R1): stand up the action-bar renderer (flat icon grid + P9 grouped sections). It
	# composes this view: reads actions_list / game_manager / _ui_layout, wires each button's press
	# to _on_dynamic_action_pressed and hover to _on_action_hover, and calls back for upgrades /
	# first-lever nudge / strategic-unlock fanfare. Variant-ready: a dev-mode display variant plugs
	# into render()'s layout dispatch (see action_bar_renderer.gd VARIANT PLUG POINT).
	action_bar = ActionBarRenderer.new(self)

	# CARVE 6 (R6): stand up the event/result presenter (executed-action result, achievement
	# unlock, engine error -> feed feedback). It composes this view: it writes through
	# host.log_message() and reaches host.plan_screen for the error toast.
	event_result_presenter = EventResultPresenter.new(self)

	# P0 rage-quit friction (playtest 2026-07-17): during a run, a window-close (X / Alt+F4)
	# should return to the Main Menu instead of quitting straight to desktop. We take over the
	# tree's close handling here and restore the default in _exit_tree so the menu screens
	# (which have their own explicit Quit) still close the app normally. The deliberate
	# quit-to-desktop paths (pause menu, main menu) are untouched.
	get_tree().set_auto_accept_quit(false)

	# Connect to GameManager signals
	game_manager.game_state_updated.connect(_on_game_state_updated)
	game_manager.turn_phase_changed.connect(_on_turn_phase_changed)
	game_manager.action_executed.connect(_on_action_executed)
	game_manager.error_occurred.connect(_on_error_occurred)
	game_manager.actions_available.connect(_on_actions_available)

	# P0 feed filter: the WATCH screen owns the "Hide arxiv flood" toggle; re-render on flip.
	if watch_screen and watch_screen.has_signal("feed_filter_changed"):
		watch_screen.feed_filter_changed.connect(_on_feed_filter_changed)
		_feed_important_only = watch_screen.feed_filter_button.button_pressed

	# Rival-intel filter: reflect the persisted preference and re-render on flip.
	if watch_screen and watch_screen.has_signal("rivals_filter_changed"):
		watch_screen.rivals_filter_changed.connect(_on_rivals_filter_changed)
		_feed_hide_rivals = watch_screen.rivals_filter_button.button_pressed

	# #622 L10: event dialog presenter (script-instantiated child, same mount pattern as
	# the #500 selector). Choices route back through game_manager.resolve_event so the
	# presenter stays reusable for the L1 rewrite's mid-month response windows.
	event_dialog = preload("res://scripts/ui/event_dialog.gd").new()
	event_dialog.state_provider = game_manager.get_game_state
	add_child(event_dialog)
	game_manager.event_triggered.connect(event_dialog.present)
	event_dialog.choice_selected.connect(_on_event_choice_selected)
	event_dialog.dialog_opened.connect(_on_event_dialog_opened)
	event_dialog.dialog_closed.connect(_on_event_dialog_closed)
	event_dialog.message_logged.connect(log_message)

	# L8 (#619): register the scene-local GameManager with the achievements
	# observer (read-only listener; contract in autoload/achievements.gd).
	var achievements = get_node_or_null("/root/Achievements")
	if achievements:
		achievements.watch(game_manager)
		achievements.achievement_unlocked.connect(_on_achievement_unlocked)

	# EE-7: per-resource "last turn" delta chips (money/compute/rep/doom)
	_setup_delta_chips()

	# Issue #500: research quality selector (script-instantiated; reparent in editor if preferred)
	research_quality_selector = preload("res://scripts/ui/research_quality_selector.gd").new()
	research_quality_selector.quality_selected.connect(_on_research_quality_selected)
	plan_screen.add_child(research_quality_selector)
	# Just under PlanScreen's attention gauge (index 0), above the getting-started hint.
	plan_screen.move_child(research_quality_selector, 1)

	# #512: doom trend sparkline, inserted just below the doom gauge in the instrument column
	var right_zones := instruments.right_zones
	var doom_meter_zone := instruments.doom_meter_zone
	doom_trend_graph = preload("res://scripts/ui/doom_trend_graph.gd").new()
	doom_trend_graph.custom_minimum_size = Vector2(0, 92)  # taller -- playtest feedback (screen1)
	doom_trend_graph.window_size = 24  # show more time points (screen6)
	doom_trend_graph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	doom_trend_graph.expand_requested.connect(_show_doom_trend_expanded)
	right_zones.add_child(doom_trend_graph)
	right_zones.move_child(doom_trend_graph, doom_meter_zone.get_index() + 1)

	# #578: doom "blow-by-blow" -- colour-coded per-source breakdown, just below the trend graph.
	doom_breakdown = preload("res://scripts/ui/doom_breakdown.gd").new()
	right_zones.add_child(doom_breakdown)
	right_zones.move_child(doom_breakdown, doom_trend_graph.get_index() + 1)

	# BL-1: compact Liability Ledger summary just below the doom trend. #622 L10: the
	# leather palette, summary button, and full-screen builder now live in LedgerScreen;
	# MainUI keeps the _show_ledger_screen entry point and its dialog bookkeeping.
	ledger_screen = preload("res://scripts/ui/ledger_screen.gd").new()
	ledger_screen.message_logged.connect(log_message)
	add_child(ledger_screen)
	var ledger_summary_btn: Button = ledger_screen.create_summary_button()
	ledger_summary_btn.pressed.connect(_show_ledger_screen)
	right_zones.add_child(ledger_summary_btn)
	right_zones.move_child(ledger_summary_btn, doom_trend_graph.get_index() + 1)

	# #622 L10: employee roster + staff ID card (script-instantiated child; grows into
	# the L2 per-person assignment surface). Renders into the scene's roster container;
	# the ID-card overlay parents to the TabManager so it overlays everything.
	employee_panel = preload("res://scripts/ui/employee_panel.gd").new()
	add_child(employee_panel)
	employee_panel.setup(roster_container, tab_manager)
	employee_panel.dialog_opened.connect(_on_employee_dialog_opened)
	employee_panel.dialog_closed.connect(_on_employee_dialog_closed)
	employee_panel.info_text_changed.connect(_on_employee_info_text)

	# #602: native path to the Employee screen. The E-key shortcut was retired when
	# employee info began moving toward the main UI, which left the full Employee screen
	# with no in-UI affordance to reach it. This visible button restores access; ESC or
	# the screen's own Back button returns to the main view (see _on_open_employee_screen).
	var employee_access_btn := Button.new()
	employee_access_btn.focus_mode = Control.FOCUS_NONE
	employee_access_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	employee_access_btn.custom_minimum_size = Vector2(0, 40)
	employee_access_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	employee_access_btn.add_theme_font_size_override("font_size", 16)
	employee_access_btn.text = " Employees -- roster & morale"
	employee_access_btn.tooltip_text = "Open the Employee management screen  (ESC returns here)"
	employee_access_btn.pressed.connect(_on_open_employee_screen)
	right_zones.add_child(employee_access_btn)
	right_zones.move_child(employee_access_btn, ledger_summary_btn.get_index() + 1)

	# Lane 1 / Phase A: PLAN<->WATCH two-screen scaffold + first terminal-styling pass.
	# Built AFTER all panels exist so it can register them for per-mode visibility.
	_setup_plan_watch_scaffold()

	# In-flight hiring tracker: a lightweight Gantt-ish list mounted just under the
	# committed-month queue in the SHARED instrument column (visible in PLAN and WATCH,
	# since jobs cook during day-tick playback). Populated by
	# hiring_panel.update_inflight_display (CARVE 3); this node stays host-owned.
	_inflight_hiring_box = VBoxContainer.new()
	_inflight_hiring_box.name = "InFlightHiring"
	_inflight_hiring_box.add_theme_constant_override("separation", 2)
	_inflight_hiring_box.visible = false
	instruments.add_child(_inflight_hiring_box)
	instruments.move_child(_inflight_hiring_box, instruments.queue_panel.get_index() + 1)

	# Always-visible DEV BUILD corner badge so a playtester can confirm exactly which
	# build he's running (version + git stamp). Draws on its own CanvasLayer over the UI.
	add_child(DevBuildBadge.new())

	# DEV MODE overlay (backslash) -- full state readout + dev controls, on its own CanvasLayer.
	# Gated on BuildInfo.DEV_BUILD by the overlay; wired to MainUI so its jump buttons can
	# drive the in-place ledger/travel/employee screens.
	var dev_overlay := DevModeOverlay.new()
	dev_overlay.main_ui = self
	add_child(dev_overlay)

	# Playtest flight recorder (F6) -- screenshot + state snapshot + marker note in
	# one press (WORKSHOP_2_BACKLOG "Playtest deep-dive protocol"). Same wiring
	# pattern as the DEV MODE overlay: gated on BuildInfo.DEV_BUILD by the node
	# itself, resolves the live GameManager via main_ui.
	var flight_recorder := FlightRecorder.new()
	flight_recorder.main_ui = self
	add_child(flight_recorder)

	# Enable input processing for keyboard shortcuts
	set_process_input(true)
	set_process_unhandled_input(true)
	set_process_unhandled_key_input(true)  # For dialog shortcuts

	# Auto-initialize game when scene loads
	log_message("[color=cyan]Initializing game...[/color]")
	log_message("[color=gray]Keyboard: 1-9 for actions, Space/Enter to commit[/color]")

	# Boot the game on next frame to ensure everything is ready
	await get_tree().process_frame
	_boot_game()

func _setup_plan_watch_scaffold() -> void:
	"""Lane 1 / Phase A (BUILD_BRIEF_PLAN_WATCH_UI): stand up the two-screen structure over
	the existing single UI -- a mode controller + banner + WATCH control strip, existing
	panels sorted into PLAN vs WATCH, and a first terminal-styling pass. The game stays
	fully playable: COMMIT THE MONTH (the End Turn button) drives PLAN->WATCH; the month
	review returns to PLAN (see _on_turn_phase_changed / _on_end_turn_button_pressed)."""
	# --- background: dark CRT phosphor field on its own layer (no layout disturbance) ---
	var bg_layer := CanvasLayer.new()
	bg_layer.layer = -10
	var bg := ColorRect.new()
	bg.color = TerminalTheme.BG_DARK
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg_layer.add_child(bg)
	add_child(bg_layer)

	# --- mode controller + its owned chrome ---
	screen_mode = ScreenModeController.new()
	add_child(screen_mode)

	# Mode banner just under the TopBar.
	var banner := screen_mode.build_banner()
	add_child(banner)
	move_child(banner, $TopBar.get_index() + 1)

	# WATCH control strip (speed dial + day/reserve readout) just above the content area.
	var watch_bar := screen_mode.build_watch_bar()
	add_child(watch_bar)
	move_child(watch_bar, banner.get_index() + 1)

	# Speed dial -> real playback speed.
	screen_mode.speed_changed.connect(func(secs: float): game_manager.day_tick_seconds = secs)

	# --- register the real screens for mode switching ---
	# The extraction turned scattered per-panel visibility toggles into two real, script-backed
	# screen subtrees: ScreenModeController now shows/hides PlanScreen and WatchScreen as whole
	# units. The shared InstrumentPanel (doom / roster / committed-month queue) is registered to
	# neither, so it stays visible in BOTH modes. Response windows still overlay as dialogs.
	screen_mode.register_plan_only(plan_screen)     # the whole PLAN screen (hand, upgrades, verbs)
	screen_mode.register_watch_only(watch_screen)   # the whole WATCH screen (the feed)
	screen_mode.register_watch_only(watch_bar)      # the playback control strip
	# The plan-time control-bar verbs live in the shared BottomBar; hide them while watching.
	screen_mode.register_plan_only(undo_last_button)
	screen_mode.register_plan_only(clear_queue_button)
	screen_mode.register_plan_only(reserve_ap_button)
	screen_mode.register_plan_only(commit_plan_button)
	screen_mode.register_plan_only(end_turn_button)                        # END TURN == COMMIT THE MONTH

	# The End Turn button is the PLAN->WATCH commit -- relabel it in the plan register.
	end_turn_button.text = "COMMIT THE MONTH >"

	# --- terminal styling that isn't owned by a screen (screens style their own panels) ---
	TerminalTheme.style_panel($InfoBar, TerminalTheme.RULE, TerminalTheme.PANEL_BG_DEEP)
	$TopBar/TitleLabel.add_theme_color_override("font_color", TerminalTheme.AMBER)

	# Start in PLAN (the game opens at the month plan).
	screen_mode.enter_plan()

	# --- A/B layout harness (UI_PROPOSALS_2026-07-22 section 4) --------------------------------
	# Container-reflow sibling to ScreenModeController: registers the existing columns/panels and
	# flips their layout properties from GameConfig.ui_layout. "classic" is captured first so it
	# stays pixel-identical; "proposed" assembles P6/P9/P10/P11. Flip live with the dev hotkey.
	layout_controller = LayoutController.new()
	add_child(layout_controller)
	layout_controller.register_targets(
		plan_screen, instruments, watch_screen,
		instruments.office_cat, plan_screen, plan_screen.upgrades_label, plan_screen.upgrades_scroll)

	# P10 gantt: mount under the shared queue panel in the instrument column (visible only in
	# proposed). Pure view -- driven read-only from state via _refresh_gantt().
	queue_gantt = QueueGantt.new()
	queue_gantt.name = "QueueGantt"
	instruments.add_child(queue_gantt)
	instruments.move_child(queue_gantt, instruments.queue_panel.get_index() + 1)

	# Re-skin the gantt register (amber PLAN / green WATCH + progress fill) on every mode flip.
	screen_mode.mode_changed.connect(func(_m): _refresh_gantt())

	# Apply the persisted layout (classic default -> a no-op restore, so first boot is unchanged).
	_apply_ui_layout(GameConfig.ui_layout)


func _unhandled_key_input(event: InputEvent):
	"""Handle keyboard shortcuts for dialogs (runs after focus but before _unhandled_input)"""
	if event is InputEventKey and event.pressed and not event.echo:
		print("[MainUI] _unhandled_key_input called, keycode: %d, active_dialog: %s" % [event.keycode, active_dialog != null])
		# CRITICAL: Call the dialog's input handler if one is active
		if active_dialog != null and is_instance_valid(active_dialog):
			if active_dialog.has_meta("input_handler"):
				print("[MainUI] Calling dialog's input handler")
				var handler = active_dialog.get_meta("input_handler")
				handler.call(event)
				get_viewport().set_input_as_handled()
				accept_event()
				return

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		# When a full-screen sub-view (e.g. the Employee screen) is up, MainUI is hidden
		# and is NOT the active screen. Don't handle any shortcuts -- and crucially don't
		# open the pause menu -- from here; TabManager owns ESC/back in that state so ESC
		# returns to the main view, not the game menu (#602).
		if not visible:
			return

		# Game/global shortcuts yield to focused text fields so typing works (#575).
		# Bug-report form etc. own a LineEdit/TextEdit; let those keys reach the field.
		# Dialog choice buttons use FOCUS_NONE, so this never blocks dialog keys.
		if KeybindManager.is_text_input_focused():
			return

		# DEBUG: sweep doom for QA (PageUp/PageDown +/-10). Debug builds only -- auto-off in release.
		# TODO: remove before any release/PR if undesired (currently gated, so release-safe).
		if OS.is_debug_build() and (event.keycode == KEY_PAGEUP or event.keycode == KEY_PAGEDOWN):
			_debug_nudge_doom(10.0 if event.keycode == KEY_PAGEUP else -10.0)
			get_viewport().set_input_as_handled()
			return

		# DEBUG: flip the A/B UI layout live (classic<->proposed) for Pip's iteration loop.
		# Debug builds only -- release players use the Settings toggle. Persists the choice.
		if OS.is_debug_build() and event.keycode == KEY_F9:
			_toggle_ui_layout()
			get_viewport().set_input_as_handled()
			return

		# Liability Ledger toggle (L): open when closed, close when the ledger itself is
		# open -- a key that opens a panel should also close it (#601). Respects the
		# text-focus gate above. If a *different* dialog is open (event/submenu), L is
		# consumed but ignored so it never stomps that dialog.
		if KeybindManager.is_action_pressed(event, "open_ledger"):
			if active_dialog != null and is_instance_valid(active_dialog):
				if active_dialog.has_meta("is_ledger"):
					_close_active_submenu()
			else:
				_show_ledger_screen()
			get_viewport().set_input_as_handled()
			return

		# ESC key for pause menu (highest priority - before dialogs)
		if event.keycode == KEY_ESCAPE:
			# If pause menu is visible, it handles ESC itself to close
			# If no active dialog, open pause menu
			if active_dialog == null or not is_instance_valid(active_dialog):
				if pause_menu and not pause_menu.visible:
					pause_menu.show_pause_menu()
					get_viewport().set_input_as_handled()
					return

		# E key no longer switches to employee screen - employee info moving to main UI
		# (E key was previously handled by TabManager, now disabled)

		var key_char = char(event.unicode) if event.unicode > 0 else "?"
		print("[MainUI] _input called, keycode: %d (%s), active_dialog: %s, buttons: %d" % [event.keycode, key_char, active_dialog != null, active_dialog_buttons.size()])

		# CRITICAL: If dialog is active, handle ALL dialog inputs FIRST (before any game shortcuts)
		# This prevents ENTER/SPACE from triggering turn advancement while dialog is open
		if active_dialog != null and is_instance_valid(active_dialog):
			print("[MainUI] Dialog is active and valid!")
			# Map the pressed key to a choice button. Dialogs label buttons with
			# numbers ([1][2][3], e.g. hire pool) or letters ([Q][W][E], e.g. events);
			# accept both so keys always match the shown buttons (#567, #575).
			var key_index = _dialog_button_index_for_key(event.keycode)
			print("[MainUI] Dialog key %d -> button index %d (buttons: %d)" % [event.keycode, key_index, active_dialog_buttons.size()])

			if key_index >= 0 and key_index < active_dialog_buttons.size():
				var btn = active_dialog_buttons[key_index]
				if btn != null and is_instance_valid(btn) and not btn.disabled:
					print("[MainUI] *** TRIGGERING DIALOG BUTTON: %s ***" % btn.text)
					btn.pressed.emit()
					get_viewport().set_input_as_handled()
					return
				else:
					print("[MainUI] Button not triggerable (null, invalid, or disabled)")
			# else: key isn't a choice for this dialog (e.g. R on a 3-option event).
			# Fall through to ESC handling; other keys are blocked below. No scary log.

			# ESC key: only close submenu dialogs (hiring, fundraising), NOT event dialogs
			# Event dialogs must be completed to prevent soft-lock (issue #452)
			if event.keycode == KEY_ESCAPE:
				# Check if this is an event dialog by looking for "event_dialog" meta flag
				if active_dialog.has_meta("is_event_dialog"):
					# Event dialogs cannot be closed with ESC - player must make a choice
					print("[MainUI] ESC pressed but this is an event dialog - ignoring (must complete event)")
					get_viewport().set_input_as_handled()
					return
				else:
					# Submenu dialogs can be closed with ESC
					print("[MainUI] ESC pressed on submenu dialog - closing")
					_close_active_submenu()
					get_viewport().set_input_as_handled()
					return

			# IMPORTANT: Block ALL other keys when dialog is active to prevent:
			# - ENTER from triggering skip turn
			# - SPACE from triggering end turn
			# - Number keys from selecting actions
			# Only dialog-specific keys (Q/W/E/R/etc and ESC) should work
			print("[MainUI] Dialog active - blocking non-dialog key: %d" % event.keycode)
			get_viewport().set_input_as_handled()
			return

		# Manual PLAN<->WATCH view toggle (V). VIEW-only quick-win: lets the player flip
		# screens at will to look things over. Works in any phase; never touches the sim.
		if event.keycode == KEY_V:
			if screen_mode:
				screen_mode.toggle_mode()
				get_viewport().set_input_as_handled()
			return

		# Main game shortcuts (when no dialog is active)
		# Number keys 1-9 for action shortcuts
		if event.keycode >= KEY_1 and event.keycode <= KEY_9:
			var action_index = event.keycode - KEY_1  # 0-indexed
			_trigger_action_by_index(action_index)
			get_viewport().set_input_as_handled()

		# Undo last action (Z key by default, configurable via KeybindManager)
		elif KeybindManager.is_action_pressed(event, "undo_action"):
			if not undo_last_button.disabled:
				_on_undo_last_button_pressed()
				get_viewport().set_input_as_handled()

		# Clear queue (C key by default, configurable via KeybindManager)
		elif KeybindManager.is_action_pressed(event, "clear_queue"):
			if not clear_queue_button.disabled:
				_on_clear_queue_button_pressed()
				get_viewport().set_input_as_handled()

		# Space to end turn (with warnings)
		elif event.keycode == KEY_SPACE:
			if not end_turn_button.disabled:
				_on_end_turn_button_pressed()
				get_viewport().set_input_as_handled()

		# Enter to commit plan (no warnings)
		elif event.keycode == KEY_ENTER:
			if not commit_plan_button.disabled:
				_on_commit_plan_button_pressed()
				get_viewport().set_input_as_handled()

		# N key to open bug reporter (backslash was reclaimed for the DEV MODE overlay)
		elif event.keycode == KEY_N:
			if bug_report_panel:
				bug_report_panel.show_panel()
				get_viewport().set_input_as_handled()

		# Quick menu shortcuts (H, F, R, P, T)
		elif KeybindManager.is_action_pressed(event, "menu_hire"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				submenu_controller.open("hire_staff")
				_decorate_active_submenu(_find_action_button("hire_staff"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_fundraise"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				submenu_controller.open("fundraise")
				_decorate_active_submenu(_find_action_button("fundraise"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_publicity"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				submenu_controller.open("publicity")
				_decorate_active_submenu(_find_action_button("publicity"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_travel"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				submenu_controller.open("travel")
				_decorate_active_submenu(_find_action_button("travel"))
				get_viewport().set_input_as_handled()

func _unhandled_input(event: InputEvent):
	"""Handle keyboard shortcuts that weren't handled by UI elements"""
	if event is InputEventKey and event.pressed and not event.echo:
		print("[MainUI] _unhandled_input called, keycode: %d, active_dialog: %s" % [event.keycode, active_dialog != null])
		# If dialog is active, handle dialog shortcuts with LETTERS (Q/W/E/R/A/S/D/F/Z)
		if active_dialog != null and is_instance_valid(active_dialog):
			# Number or letter keys for dialog options; map to the shown buttons (#567, #575)
			var key_index = _dialog_button_index_for_key(event.keycode)

			if key_index >= 0 and key_index < active_dialog_buttons.size():
				var btn = active_dialog_buttons[key_index]
				if btn != null and is_instance_valid(btn) and not btn.disabled:
					print("[MainUI] Triggering dialog button: %s" % btn.text)
					btn.pressed.emit()
					get_viewport().set_input_as_handled()

func _dialog_button_index_for_key(keycode: int) -> int:
	"""Map a pressed key to a dialog choice-button index, or -1 if unmapped.
	Dialogs label buttons either with numbers ([1][2][3], e.g. the hire candidate
	pool) or letters ([Q][W][E], e.g. event choices). Accept both schemes so the
	keys always match whatever buttons are displayed (issues #567, #575)."""
	if keycode >= KEY_1 and keycode <= KEY_9:
		return keycode - KEY_1
	var letter_keys = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]
	return letter_keys.find(keycode)

func _trigger_action_by_index(index: int):
	"""Trigger action button by its index (for keyboard shortcuts)"""
	# Find the VBoxContainer (icon_stack) first
	var icon_stack: VBoxContainer = null
	for child in actions_list.get_children():
		if child is VBoxContainer:
			icon_stack = child
			break

	if not icon_stack:
		return

	# Get buttons directly from stack (single column layout)
	var buttons = icon_stack.get_children()
	if index < buttons.size():
		var button = buttons[index] as Button
		if button and not button.disabled:
			button.emit_signal("pressed")
			log_message("[color=cyan]Keyboard shortcut: %d[/color]" % (index + 1))

func _apply_ui_layout(name: String) -> void:
	"""Flip the A/B layout (VIEW-only; ADR-0006). LayoutController reflows the containers (P6
	cat clamp + P11 column split + upgrades dock); here we swap the classic one-line queue hint
	for the P10 gantt and re-render the action hand grouped (P9) vs flat. Zero writes to game
	state, zero RNG, no turn-logic -- pure presentation."""
	var target := name if name == "proposed" else "classic"
	_ui_layout = target
	if layout_controller:
		layout_controller.apply_layout(target)
	var proposed := target == "proposed"
	# P10: the gantt stands in for the one-line queue hint panel in proposed.
	if queue_gantt:
		queue_gantt.visible = proposed
	if instruments and instruments.queue_panel:
		instruments.queue_panel.visible = not proposed
	# P9: re-render the hand in the new register (grouped vs flat), if we have a payload.
	if not _last_actions.is_empty():
		_on_actions_available(_last_actions)
	_refresh_gantt()

func _toggle_ui_layout() -> void:
	"""Dev hotkey: flip classic<->proposed live and persist the choice (same iteration loop as
	the debug doom-nudge). Debug-build gated at the call site."""
	var next := "classic" if _ui_layout == "proposed" else "proposed"
	_apply_ui_layout(next)
	GameConfig.set_setting("ui_layout", next, true)  # persist so the choice survives a restart
	log_message("[color=cyan]UI layout -> %s[/color]" % next)

func _refresh_gantt() -> void:
	"""Rebuild the P10 gantt rows from live state (committed strategic WIP + in-flight hiring +
	the plan-time tentative queue). READ-ONLY: snapshots state, writes nothing. No-op in classic."""
	if queue_gantt == null or _ui_layout != "proposed":
		return
	var state: Dictionary = game_manager.get_game_state() if game_manager else {}
	var rows := QueueGantt.rows_from_state(state, plan_controller.queued_actions)
	var watch_mode := screen_mode != null and screen_mode.current_mode == ScreenModeController.Mode.WATCH
	queue_gantt.update_rows(rows, watch_mode)

func _apply_balance_tooltips() -> void:
	"""Rebuild the resource HUD tooltips that quote balance numbers from Balance,
	so the copy can never drift from the mechanic (turn_manager reads the same keys)."""
	var compute_per := int(Balance.num("compute.per_researcher_per_turn", 1.0))
	if compute_label:
		compute_label.tooltip_text = "Processing power for research. Each researcher uses %d per turn." % compute_per
	var per_paper := int(Balance.num("papers.research_per_paper", 100.0))
	if research_label:
		research_label.tooltip_text = "Generated by staff. %d research = 1 auto-published paper." % per_paper
	var rep_per_paper := int(Balance.num("papers.reputation_per_paper", 5.0))
	if papers_label:
		papers_label.tooltip_text = "Publications boost reputation (+%d each) and may have further downstream impact as their findings are adopted." % rep_per_paper

func _boot_game():
	# Was _on_init_button_pressed (wired to a vestigial "Init" button that has been
	# removed, #715); the game auto-boots from _ready. Loads a queued save or starts fresh.
	# L7 (#618): if the welcome screen queued a saved game, boot into it instead
	# of starting a new run. The flag is one-shot.
	if GameConfig.pending_load_path != "":
		var load_path: String = GameConfig.pending_load_path
		GameConfig.pending_load_path = ""
		log_message("[color=cyan]Loading saved game...[/color]")
		if game_manager.load_saved_game(load_path):
			return
		log_message("[color=red]Load failed -- starting a new game instead.[/color]")
	log_message("[color=cyan]Initializing game...[/color]")
	# #617 debt: was hardcoded "test-seed" -- every boot ran the SAME timeline and
	# GameConfig.game_seed was ignored. Empty arg -> GameManager falls back to
	# GameConfig.get_display_seed() (player's configured seed, else the weekly seed).
	game_manager.start_new_game()

func _on_reserve_ap_button_pressed():
	"""Reserve 1 AP for event responses"""
	log_message("[color=cyan]Reserving 1 AP for events...[/color]")
	game_manager.reserve_ap(1)

func _on_undo_last_button_pressed():
	"""Undo (remove) the last queued action"""
	if plan_controller.queued_actions.size() == 0:
		return

	# Get the last action
	var last_action = plan_controller.queued_actions[-1]
	var action_id = last_action.get("id", "")
	var action_name = last_action.get("name", "Unknown")

	# Remove it using existing logic
	_remove_queued_action(action_id, action_name)

func _on_clear_queue_button_pressed():
	"""Clear all queued actions and refund AP. Queue mutation + refund is PlanController's job
	(R4); the view keeps the empty-queue guard, the log line, and the redraw."""
	if not plan_controller.clear_queue():
		return  # already empty -- nothing to clear

	# Update local display
	update_queued_actions_display()

	log_message("[color=yellow]Action queue cleared - AP refunded[/color]")

func _remove_queued_action(action_id: String, action_name: String):
	"""Remove a specific action from the queue. The queue mutation + Attention refund live in
	PlanController (R4); the view keeps the debug/log lines and the redraw."""
	print("[MainUI] Removing queued action: %s (id: %s)" % [action_name, action_id])

	var result := plan_controller.remove_action(action_id)
	if result.get("removed", false):
		var ap_cost: int = result.get("attention_cost", 0)
		log_message("[color=yellow]Removed: %s (+%d AP)[/color]" % [action_name, ap_cost])
		update_queued_actions_display()
	else:
		print("[MainUI] ERROR: Could not find action to remove: %s" % action_id)

func _on_end_turn_button_pressed():
	if plan_controller.needs_pass_fallback():
		# Issue #733 (+ overbook soft-lock): an empty ACCEPTED queue no longer hard-errors --
		# phantom UI tiles could previously suppress this net. PlanController routes the existing
		# pass-action path (identical to the Do Nothing button) so COMMIT THE MONTH always
		# advances. Determinism-safe: no new RNG and no turn-step reordering -- select_action()
		# only queues the canonical pass id, and end_month() below plays it out exactly as a
		# planned month would.
		log_message("[color=gray]Nothing planned -- the month proceeds.[/color]")
		plan_controller.queue_pass_fallback()
		update_queued_actions_display()

	# Check for danger zones and warn player
	var current_state = game_manager.state
	var warnings = []

	# High doom warning
	# Routed through ThemeManager's canonical bands (L6 unification: was hardcoded
	# 80/70; now CATASTROPHIC >=80 critical, EXTREME >=67 warning)
	var doom_band: int = ThemeManager.get_doom_band_index(current_state.doom)
	if doom_band >= 5:
		warnings.append("[color=red][!]CRITICAL: Doom at %.1f%% (%s) - Very close to game over![/color]" % [current_state.doom, ThemeManager.get_doom_status_label(current_state.doom)])
	elif doom_band == 4:
		warnings.append("[color=yellow][!]WARNING: Doom at %.1f%% (%s) - Approaching danger zone![/color]" % [current_state.doom, ThemeManager.get_doom_status_label(current_state.doom)])

	# Low reputation warning
	if current_state.reputation <= 20:
		warnings.append("[color=red][!]CRITICAL: Reputation at %.0f - May lose funding![/color]" % current_state.reputation)
	elif current_state.reputation <= 30:
		warnings.append("[color=yellow][!]WARNING: Low reputation (%.0f) - Watch funding![/color]" % current_state.reputation)

	# Low money warning
	if current_state.money <= 20000:
		warnings.append("[color=red][!]CRITICAL: Low funds (%s) - Can't afford much![/color]" % GameConfig.format_money(current_state.money))

	# Technical debt warning (Issue #416)
	if current_state.technical_debt >= 75:
		warnings.append("[color=red][!]CRITICAL: Technical debt at %.0f%% - High failure risk![/color]" % current_state.technical_debt)
	elif current_state.technical_debt >= 50:
		warnings.append("[color=yellow][!]WARNING: Technical debt at %.0f%% - Consider an audit![/color]" % current_state.technical_debt)

	# Show warnings if any
	if warnings.size() > 0:
		for warning in warnings:
			log_message(warning)
		log_message("[color=gray]Press Space/Enter again to confirm, or C to revise queue[/color]")
		# Note: Simplified version - in full implementation, would require double-confirm

	log_message("[color=cyan]Committing month plan (%d actions) -- playing the month out...[/color]" % plan_controller.queue_size())

	# Clear the UI mirror (NO refund -- the backend queue is consumed by the commit below;
	# repopulated after the turn processes). reset_mirror() is the commit-path clear, distinct
	# from the clear-queue button's refunding path.
	plan_controller.reset_mirror()
	update_queued_actions_display()

	# L1 (ADR-0009): End Turn commits the MONTH plan and hands control to day-tick
	# playback (auto-pause on response windows, month review at the boundary). The old
	# single day-step lives on ONLY behind the DEV MODE overlay ("Day step (dev)").
	plan_controller.commit_month()
	# Phase A: COMMIT THE MONTH is the PLAN->WATCH transition.
	if screen_mode:
		screen_mode.enter_watch()

func _on_commit_plan_button_pressed():
	"""Commit queued actions AND reserve remaining AP (no warnings)"""
	var current_state = game_manager.get_game_state()
	var available_ap = current_state.get("available_ap", 0)

	# If there are queued actions, commit them + reserve balance
	if plan_controller.queue_size() > 0:
		log_message("[color=cyan]Committing %d queued actions + reserving %d remaining AP...[/color]" % [plan_controller.queue_size(), available_ap])
	else:
		# No queued actions - just reserve all AP (reactive strategy). PlanController owns the
		# reserve-all queue mutation (mirror entry + backend pass id); the view just logs + redraws.
		log_message("[color=cyan]Committing plan: Reserving all %d AP for reactive responses...[/color]" % available_ap)
		plan_controller.append_reserve_all()
		update_queued_actions_display()

	# Clear the UI mirror (NO refund -- backend consumed by the commit; repopulated after the
	# turn processes). Commit-path clear, distinct from the clear-queue button's refunding path.
	plan_controller.reset_mirror()
	update_queued_actions_display()

	# Commit the plan -- the L1 month path (see _on_end_turn_button_pressed).
	plan_controller.commit_month()
	# Phase A: committing the plan is the PLAN->WATCH transition.
	if screen_mode:
		screen_mode.enter_watch()

func _on_employee_tab_button_pressed():
	"""Switch to employee management screen - DISABLED: employee info moving to main UI"""
	# tab_manager.show_employee_screen()
	pass

func _on_open_employee_screen() -> void:
	"""#602: open the full Employee screen via the TabManager. ESC (handled by TabManager)
	or the screen's own Back button returns to the main view -- MainUI's ESC-to-pause is
	suppressed while it's hidden, so ESC goes back to the game, not the game menu."""
	if tab_manager and tab_manager.has_method("show_employee_screen"):
		tab_manager.show_employee_screen()

func _on_bug_report_button_pressed():
	"""Open bug report panel"""
	if bug_report_panel:
		bug_report_panel.show_panel()

func _on_research_quality_selected(mode: String):
	game_manager.set_research_quality(mode)

func _on_game_state_updated(state: Dictionary):
	print("[MainUI] State updated: ", state)

	if research_quality_selector:
		research_quality_selector.update_from_state(state)

	# Phase A: keep the WATCH day/reserve readout live during month playback.
	if screen_mode:
		screen_mode.update_from_state(state)

	# Office-floor visual layer (WATCH): walker count mirrors the staff count. PURE VIEW
	# (ADR-0006) -- reads the state snapshot, writes nothing, cannot affect determinism.
	if watch_screen and watch_screen.has_method("update_office_floor"):
		watch_screen.update_office_floor(state)

	# Refresh the PLAN attention gauge (allocated vs reserved pips) from the month plan.
	if plan_screen:
		plan_screen.update_reserve_gauge(state)

	# P10 gantt (proposed layout): rebuild the operations tracker from live state. No-op in classic.
	_refresh_gantt()

	# Turn/time (Pip: "count turns and tell us the date"). ONE tidy element:
	#   "Turn 14  -  Fri 21 Jul 2017"
	# turn = the plan/decision period (count it); the calendar date is the human "when".
	# The old split (month-year badge + separate "Turn N") is folded into this single
	# label and the now-redundant TurnCountLabel is hidden. VIEW-only (ADR-0006).
	turn_label.text = _format_turn_datetime(state)
	turn_count_label.visible = false
	money_label.text = "%s" % GameConfig.format_money(state.get("money", 0))
	compute_label.text = "%.1f" % state.get("compute", 0)
	research_label.text = "%.1f" % state.get("research", 0)
	papers_label.text = "%d" % state.get("papers", 0)
	reputation_label.text = "* %.0f" % state.get("reputation", 0)

	# EE-7: refresh the per-resource "last turn" delta chips at turn boundaries
	_update_delta_chips(state)

	# Surface in-flight hiring durations (interview/offer/networking) + onboarding
	# checklists with progress in the instrument column. VIEW-only (reads state).
	hiring_panel.update_inflight_display(state)

	# Add employee blob display to AP label (using BBCode for RichTextLabel)
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)
	var blob_display = ""
	for _i in range(safety):
		blob_display += "[color=green]*[/color]"
	for _i in range(capability):
		blob_display += "[color=red]*[/color]"
	for _i in range(compute_eng):
		blob_display += "[color=dodger_blue]*[/color]"

	# L2 (ADR-0011): the founder currency is the monthly ATTENTION budget (month_plan), not
	# the retired per-turn AP pool. Read the plan's Attention split so the HUD is honest --
	# "~20 decisions this month" is now the true, spendable number.
	var mp = state.get("month_plan", {})
	var total_ap = int(mp.get("attention_total", 0))
	var committed_ap = int(mp.get("attention_spent", 0))
	var reserved_ap = int(mp.get("attention_reserved", 0))
	var remaining_ap = total_ap - committed_ap - reserved_ap

	# Color-code Attention text based on remaining budget
	var ap_color_name = "white"  # Default
	if remaining_ap <= 0:
		ap_color_name = "red"  # Depleted
	elif remaining_ap == 1:
		ap_color_name = "yellow"  # Low
	elif remaining_ap < total_ap:
		ap_color_name = "lime"  # Partially committed

	# Build BBCode text for RichTextLabel
	var ap_text = ""
	if reserved_ap > 0:
		ap_text = "[color=%s]Attention: %d (%d free, %d reserved)[/color]  %s" % [ap_color_name, total_ap, remaining_ap, reserved_ap, blob_display]
	elif committed_ap > 0:
		ap_text = "[color=%s]Attention: %d (%d free, %d queued)[/color]  %s" % [ap_color_name, total_ap, remaining_ap, committed_ap, blob_display]
	else:
		ap_text = "[color=%s]Attention: %d[/color]  %s" % [ap_color_name, total_ap, blob_display]

	ap_label.text = ap_text
	# AP tooltip: base is difficulty-set (state.max_action_points), per-staff bonus
	# from Balance -- both the real inputs to turn_manager._step_grant_action_points.
	var ap_base := int(state.get("max_action_points", 3))
	var per_staff = Balance.num("action_points.per_staff", 0.5)
	ap_label.tooltip_text = "Action Points. Limits actions per turn. Base %d + %s per staff." % [ap_base, str(per_staff)]

	# Update doom displays (both text label and visual meter)
	var doom = state.get("doom", 0)
	var doom_momentum = state.get("doom_momentum", 0.0)

	# Update numeric doom display
	if numeric_doom_label:
		numeric_doom_label.text = "%.1f%%" % doom
		numeric_doom_label.modulate = ThemeManager.get_doom_stroke_color(doom)

	# Visual doom meter with momentum indicator
	if doom_meter:
		doom_meter.set_doom(doom, doom_momentum)

	# Feed the trend sparkline (#512)
	if doom_trend_graph:
		doom_trend_graph.set_history(state.get("doom_history", []))

	# Feed the per-source doom breakdown (#578)
	if doom_breakdown:
		doom_breakdown.set_sources(
			state.get("doom_system", {}).get("doom_sources", {}),
			state.get("frontier_capability", {}),
			state.get("rival_labs_full", []))

	# BL-1: refresh the compact Liability Ledger summary (#622 L10: lives in LedgerScreen)
	# turn/start_* let the summary show a real calendar due date, not a raw turn count.
	if ledger_screen:
		ledger_screen.update_summary(state.get("ledger", {}), int(state.get("turn", 0)),
			int(state.get("start_year", GameState.DEFAULT_START_YEAR)),
			int(state.get("start_month", GameState.DEFAULT_START_MONTH)),
			int(state.get("start_day", GameState.DEFAULT_START_DAY)))

	# Update office cat for doom level and visibility
	if office_cat:
		office_cat.update_doom_level(doom / 100.0)  # Convert percentage to 0.0-1.0
		# Show cat if adopted, hide if not
		office_cat.visible = state.get("has_cat", false)

	# Hide getting started hint after turn 3 (new player onboarding).
	# Gated on GameConfig.show_hints (issue #720) so the hints toggle suppresses it.
	if getting_started_hint:
		getting_started_hint.visible = GameConfig.show_hints and state.get("turn", 0) < 3

	# #801: retire the first-lever pulse once the onboarding window has passed, even if the
	# player never hired (belt-and-suspenders; the primary clear is on first hire).
	if GameConfig.show_first_lever_hint and state.get("turn", 0) >= 3:
		_clear_first_lever_nudge()

	# Enable controls after first init
	if state.get("turn", 0) >= 0:
		# Enable/disable Reserve AP button based on available AP
		var available = state.get("available_ap", 0)
		reserve_ap_button.disabled = (available < 1)

		# Note: Actions are now included in init_game response
		# No need to call get_available_actions() separately

	# Check game over
	if state.get("game_over", false):
		var victory = state.get("victory", false)
		if victory:
			log_message("[color=gold]VICTORY! You survived![/color]")
		else:
			log_message("[color=red]GAME OVER! The AI destroyed humanity.[/color]")

		# Disable controls
		end_turn_button.disabled = true
		commit_plan_button.disabled = true
		reserve_ap_button.disabled = true

		# Show game over screen with stats
		if game_over_screen:
			game_over_screen.show_game_over(victory, state)

	# Refresh upgrades list to update affordability
	_populate_upgrades()

	# Update employee roster display (#622 L10: lives in EmployeePanel)
	if employee_panel:
		employee_panel.update_roster(state)

# ---- EE-7 (ADR-0012): per-resource per-turn delta chips ----

func _setup_delta_chips() -> void:
	"""Create the small 'last turn' delta labels right after each resource readout.
	Playtest motivation: the one human ledger-death specimen was low-resolution --
	'the feeling that I was losing things badly' with no numbers to point at."""
	var specs := [
		{"key": "money", "after": money_label},
		{"key": "compute", "after": compute_label},
		{"key": "reputation", "after": reputation_label},
		{"key": "doom", "after": numeric_doom_label},
	]
	for spec in specs:
		var anchor = spec["after"]
		if anchor == null:
			continue
		var chip := Label.new()
		chip.name = "DeltaChip_%s" % spec["key"]
		chip.text = ""
		chip.add_theme_font_size_override("font_size", 12)
		chip.tooltip_text = "Change over the last turn"
		var parent = anchor.get_parent()
		parent.add_child(chip)
		parent.move_child(chip, anchor.get_index() + 1)
		_delta_labels[spec["key"]] = chip


func _update_delta_chips(state: Dictionary) -> void:
	"""On each turn boundary, show each resource's change over the last completed turn.
	Mid-turn state updates leave the chips as-is (they describe the LAST turn)."""
	var t: int = int(state.get("turn", 0))
	var now := {
		"money": float(state.get("money", 0.0)),
		"compute": float(state.get("compute", 0.0)),
		"reputation": float(state.get("reputation", 0.0)),
		"doom": float(state.get("doom", 0.0)),
	}
	if t == _last_delta_turn:
		return
	if _last_delta_turn >= 0 and t == _last_delta_turn + 1:
		for key in now.keys():
			_render_delta_chip(str(key), now[key] - float(_prev_turn_snapshot.get(key, now[key])))
	else:
		# New game / load / anything non-consecutive: no meaningful "last turn".
		for key in _delta_labels.keys():
			(_delta_labels[key] as Label).text = ""
	_prev_turn_snapshot = now
	_last_delta_turn = t


func _render_delta_chip(key: String, d: float) -> void:
	var chip: Label = _delta_labels.get(key)
	if chip == null:
		return
	if absf(d) < 0.05:
		chip.text = ""
		return
	var txt: String
	if key == "money":
		txt = ("+" if d > 0.0 else "-") + GameConfig.format_money(absf(d))
	else:
		txt = "%+.1f" % d
	chip.text = "(%s)" % txt
	# Doom rising is bad; every other resource rising is good.
	var good: bool = (d < 0.0) if key == "doom" else (d > 0.0)
	chip.add_theme_color_override("font_color", _DELTA_GOOD if good else _DELTA_BAD)


func _on_turn_phase_changed(phase_name: String):
	print("[MainUI] Phase changed: ", phase_name)

	current_turn_phase = phase_name

	# Update phase label with color coding
	var phase_color = "white"
	var phase_display = phase_name

	if phase_name == "turn_start" or phase_name == "TURN_START":
		phase_color = "red"
		phase_display = "TURN START - Processing events..."
		end_turn_button.disabled = true
		commit_plan_button.disabled = true
	elif phase_name == "action_selection" or phase_name == "ACTION_SELECTION":
		phase_color = "lime"
		phase_display = "SELECT ACTIONS - Click actions or press 1-9"
		# End turn requires actions, commit plan is always available
		end_turn_button.disabled = plan_controller.is_queue_empty()
		commit_plan_button.disabled = false
		undo_last_button.disabled = plan_controller.is_queue_empty()
		clear_queue_button.disabled = plan_controller.is_queue_empty()
		# Phase A: reaching the plan phase (game start / after month review) returns to PLAN.
		# Mid-month window pauses emit "turn_start", not "action_selection", so WATCH is kept.
		if screen_mode:
			screen_mode.enter_plan()
	elif phase_name == "turn_end" or phase_name == "TURN_END":
		phase_color = "yellow"
		phase_display = "EXECUTING - Your actions are running..."
		end_turn_button.disabled = true
		commit_plan_button.disabled = true

	phase_label.text = "[color=%s]Phase: %s[/color]" % [phase_color, phase_display]

	log_message("[color=magenta]Turn Phase: " + phase_name + "[/color]")

func _on_action_executed(result: Dictionary):
	# CARVE 6 (R6): thin view shim. Result -> feed presentation lives in EventResultPresenter now.
	event_result_presenter.present_action_result(result)

func _on_achievement_unlocked(achievement: Dictionary) -> void:
	# CARVE 6 (R6): thin view shim. Unlock -> feed presentation lives in EventResultPresenter now.
	event_result_presenter.present_achievement(achievement)

func _on_error_occurred(error_msg: String):
	# CARVE 6 (R6): thin view shim. Error -> feed + PLAN-toast presentation lives in
	# EventResultPresenter now.
	event_result_presenter.present_error(error_msg)

func _notification(what: int) -> void:
	# P0 rage-quit friction: intercept the window-manager close during a run and route to the
	# Main Menu instead of quitting to desktop. Quit-to-desktop stays available from the pause
	# menu ("Quit to Desktop") and the main menu itself.
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		print("[MainUI] Window close during run -> returning to main menu (rage-quit friction)")
		GameConfig.save_config()
		get_tree().paused = false
		get_tree().set_auto_accept_quit(true)  # menu screen should close the app normally
		SceneTransition.go_to("res://scenes/welcome.tscn")

func _exit_tree() -> void:
	# Restore default close handling when leaving the run (Main Menu / defeat / quit), so the
	# menu screens close the app on X as expected.
	if is_inside_tree() and get_tree() != null:
		get_tree().set_auto_accept_quit(true)

func log_message(text: String, channel: String = "normal"):
	"""Add a message to the log with an in-game date stamp (playtest: real-seconds
	timestamps were meaningless to players -- show the calendar date instead, reusing
	GameState.get_formatted_date(), the same helper the HUD date badge uses).

	P0 feed filter: every line is recorded with its channel so the "Hide arxiv flood"
	toggle can suppress the low-severity `flavour` stream from the default view without
	losing it. Only lines that pass the current filter are appended to the visible log."""
	var date_stamp := "?"
	if game_manager != null and game_manager.state != null:
		date_stamp = game_manager.state.get_formatted_date()
	var line := "[color=gray][%s][/color] %s" % [date_stamp, text]
	_feed_lines.append({"text": line, "channel": channel})
	# Cap the backing model: trim oldest lines so a long run's feed stays bounded (same
	# latent unbounded-growth issue the old message_log had). The arxiv-flood filter still
	# applies within whatever lines remain stored.
	if _feed_lines.size() > FEED_MAX_LINES:
		_feed_lines = _feed_lines.slice(_feed_lines.size() - FEED_MAX_LINES)
	if not _feed_passes_filter(channel):
		return  # recorded but hidden under the current filter
	message_log.text += "\n" + line

	# Auto-scroll to bottom
	await get_tree().process_frame
	var scroll = message_log.get_parent() as ScrollContainer
	if scroll:
		scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _feed_passes_filter(channel: String) -> bool:
	"""A line is visible unless a filter suppresses its channel: the 'important only' filter
	hides flavour spam; the rival-intel filter hides the 'rivals' channel. Display-only --
	suppressed lines stay recorded in _feed_lines, so the underlying content is unchanged."""
	if _feed_important_only and channel == "flavour":
		return false
	if _feed_hide_rivals and channel == "rivals":
		return false
	return true

func _render_feed() -> void:
	"""Rebuild the visible feed from the recorded lines under the current filter (called when
	the player flips the 'Hide arxiv flood' toggle)."""
	var text := ""
	for entry in _feed_lines:
		if _feed_passes_filter(String(entry.get("channel", "normal"))):
			text += "\n" + String(entry.get("text", ""))
	message_log.text = text
	await get_tree().process_frame
	var scroll = message_log.get_parent() as ScrollContainer
	if scroll:
		scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _on_feed_filter_changed(important_only: bool) -> void:
	_feed_important_only = important_only
	_render_feed()

func _on_rivals_filter_changed(hide_rivals: bool) -> void:
	"""Player toggled rival-intel visibility. Persist the preference (GameConfig ->
	user://config.cfg) and re-render; the backing feed lines are untouched."""
	_feed_hide_rivals = hide_rivals
	GameConfig.show_rivals_feed = not hide_rivals
	GameConfig.save_config()
	_render_feed()

func _on_actions_available(actions: Array):
	"""CARVE 5 (R1, docs/MAIN_UI_SEAM_MAP.md): thin view shim. The action-bar RENDERING lives in
	ActionBarRenderer now; the view keeps only _last_actions (so a live A/B layout flip can
	re-render the same payload -- see _apply_ui_layout) and forwards to the renderer. Input
	(_on_dynamic_action_pressed), hover (_on_action_hover), upgrades, the first-lever nudge and the
	strategic-unlock fanfare stay in the view and are called back through host."""
	# Remember the payload so a live layout flip can re-render the hand (P9).
	_last_actions = actions
	action_bar.render(actions)

## #801 cold-open handoff: pulse the hire button and point the hint at the lever.
## Guarded + minimal -- does nothing unless GameConfig.show_first_lever_hint is set.
func _apply_first_lever_nudge() -> void:
	# Kill any prior pulse (its target button was just freed + recreated).
	if _first_lever_pulse_tween != null and _first_lever_pulse_tween.is_valid():
		_first_lever_pulse_tween.kill()
	_first_lever_pulse_tween = null
	if not GameConfig.show_first_lever_hint:
		return
	var btn := _find_action_button(FIRST_LEVER_ACTION_ID)
	if btn == null:
		return
	# Advisor pointer line (names the lever AND its effect).
	if getting_started_hint:
		getting_started_hint.text = FIRST_LEVER_HINT_TEXT
	# Looping alpha pulse to draw the eye to the named lever.
	_first_lever_pulse_tween = create_tween().set_loops()
	_first_lever_pulse_tween.tween_property(btn, "modulate:a", 0.4, 0.6)
	_first_lever_pulse_tween.tween_property(btn, "modulate:a", 1.0, 0.6)

## Stop the first-lever nudge (first hire taken, or onboarding window passed).
func _clear_first_lever_nudge() -> void:
	GameConfig.show_first_lever_hint = false
	if _first_lever_pulse_tween != null and _first_lever_pulse_tween.is_valid():
		_first_lever_pulse_tween.kill()
	_first_lever_pulse_tween = null

func _populate_upgrades():
	"""Populate upgrades list"""
	# Clear existing upgrades
	for child in upgrades_list.get_children():
		child.queue_free()

	var current_state = game_manager.get_game_state()
	var all_upgrades = GameUpgrades.get_all_upgrades()

	for upgrade in all_upgrades:
		var upgrade_id = upgrade.get("id", "")
		var upgrade_name = upgrade.get("name", "Unknown")
		var upgrade_desc = upgrade.get("description", "")
		var upgrade_cost = upgrade.get("cost", 0)

		# Check if already purchased
		var is_purchased = current_state.get("purchased_upgrades", []).has(upgrade_id)

		# Create button
		var button = ThemeManager.create_button(upgrade_name)
		# Blockier tiles (#594): hug content instead of stretching across the wide right
		# panel, and ~20% taller (32 -> 38) so they read as tighter, blockier tiles.
		# Playtest-3: right-align the column to free up central screen space (was
		# SIZE_SHRINK_BEGIN, hugging the left edge instead).
		button.size_flags_horizontal = Control.SIZE_SHRINK_END
		button.custom_minimum_size = Vector2(200, 38)

		# If purchased, show differently
		if is_purchased:
			button.text = "[OK] " + upgrade_name
			button.disabled = true
			button.modulate = Color(0.5, 1.0, 0.5)  # Green tint
		else:
			button.text = "%s (%s)" % [upgrade_name, GameConfig.format_money(upgrade_cost)]

			# Check affordability
			var can_afford = current_state.get("money", 0) >= upgrade_cost
			if not can_afford:
				button.disabled = true
				button.modulate = Color(0.6, 0.6, 0.6)

		# Tooltip
		var tooltip = upgrade_desc + "\n\nCost: %s" % GameConfig.format_money(upgrade_cost)
		if is_purchased:
			tooltip += "\n\n[PURCHASED]"
		elif not current_state.get("money", 0) >= upgrade_cost:
			tooltip += "\n\n[CANNOT AFFORD]"
		button.tooltip_text = tooltip

		# Connect button press
		if not is_purchased:
			button.pressed.connect(func(): _on_upgrade_pressed(upgrade_id, upgrade_name))

		# Connect hover
		button.mouse_entered.connect(func(): _on_upgrade_hover(upgrade, is_purchased))
		button.mouse_exited.connect(func(): _on_action_unhover())

		upgrades_list.add_child(button)

func _on_upgrade_pressed(upgrade_id: String, upgrade_name: String):
	"""Handle upgrade purchase button press"""
	log_message("[color=cyan]Purchasing upgrade: %s[/color]" % upgrade_name)

	# Purchase via GameManager (will handle state update)
	game_manager.purchase_upgrade(upgrade_id)

func _on_upgrade_hover(upgrade: Dictionary, is_purchased: bool):
	"""Update info bar when hovering over an upgrade"""
	var upgrade_name = upgrade.get("name", "Unknown")
	var upgrade_desc = upgrade.get("description", "")
	var upgrade_cost = upgrade.get("cost", 0)

	# Build enhanced upgrade info
	var info_text = "[b][color=cyan]%s[/color][/b] -- %s" % [upgrade_name, upgrade_desc]

	# Show cost
	info_text += "\n[color=gray]|-[/color] [color=yellow]Cost:[/color] [color=gold]%s[/color]" % GameConfig.format_money(upgrade_cost)

	# Show status
	info_text += "\n[color=gray]`-[/color] "
	if is_purchased:
		info_text += "[color=green][OK] ALREADY PURCHASED[/color]"
	else:
		var current_state = game_manager.get_game_state()
		if current_state.get("money", 0) >= upgrade_cost:
			info_text += "[color=lime][OK] READY TO PURCHASE[/color]"
		else:
			var needed = upgrade_cost - current_state.get("money", 0)
			info_text += "[color=red][X] NEED %s MORE[/color]" % GameConfig.format_money(needed)

	info_label.text = info_text

func _on_dynamic_action_pressed(action_id: String, action_name: String):
	"""Handle dynamic action button press"""
	log_message("[color=cyan]Selecting action: %s[/color]" % action_name)

	# #801: the player engaged the taught lever -- retire the first-lever nudge.
	if GameConfig.show_first_lever_hint and action_id == FIRST_LEVER_ACTION_ID:
		_clear_first_lever_nudge()

	# Check if this is a submenu action
	var action = _get_action_by_id(action_id)
	if action.get("is_submenu", false):
		# CARVE 2 (R5): one entry point. SubmenuController dispatches on action_id (grid submenus
		# built from config; hiring/travel delegate back to the bespoke builders here).
		submenu_controller.open(action_id)
		# Align the submenu to the clicked button + add close affordance (#510)
		_decorate_active_submenu(_find_action_button(action_id))
		return

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford action: %s[/color]" % action_name)
		return

	# Track queued action -- #821: only add the UI tile when the backend accepts
	# (select_action returns false on Attention overbook + emits the error), so a
	# rejected action no longer leaves a phantom queue tile.
	if plan_controller.select_action(action_id):
		plan_controller.queue_action(action_id, action_name)
		update_queued_actions_display()

func _get_action_by_id(action_id: String) -> Dictionary:
	"""Helper to find action definition - delegates to GameActions"""
	return GameActions.get_action_by_id(action_id)

# --- Issue #510 UI polish helpers (submenu close affordance + alignment) ---
# #622 L10: the chrome itself (panel styling, [X] + ESC hint, alignment, button lookup)
# lives in SubmenuChrome. These thin wrappers keep MainUI's ownership of the
# active_dialog state and leave every existing dialog-builder call site unchanged.

func _find_action_button(action_id: String) -> Button:
	"""Locate the left-panel icon button that opened a submenu, by action_id meta."""
	return SubmenuChrome.find_action_button(actions_list, action_id)

func _decorate_active_submenu(anchor_button: Button = null) -> void:
	"""Add close affordance (X + ESC hint) to the active submenu and, when an
	anchor button is given, align the submenu vertically to it (#510).
	Safe to call right after a _show_*_submenu() call: those builders set
	active_dialog and add the dialog to the tree before their internal await."""
	if active_dialog == null or not is_instance_valid(active_dialog):
		return
	if active_dialog.has_meta("is_event_dialog"):
		return  # Event dialogs must be completed, not closed (#452)
	SubmenuChrome.add_close_affordance(active_dialog, _close_active_submenu)
	if anchor_button != null and is_instance_valid(anchor_button):
		SubmenuChrome.align_to_button(active_dialog, anchor_button)

func _add_submenu_close_affordance(dialog: Control) -> void:
	"""#622 L10 delegator -- keeps the one-arg call shape the dialog builders use;
	the chrome is SubmenuChrome.add_close_affordance with MainUI's close routine."""
	SubmenuChrome.add_close_affordance(dialog, _close_active_submenu)

func _close_active_submenu() -> void:
	"""Close the active submenu dialog (shared by [X] click and ESC)."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
	active_dialog = null
	active_dialog_buttons = []

func _present_modal_dialog(dialog: Control) -> void:
	"""Mount a modal Panel over the board WITH a full-rect input barrier beneath it
	(#767). Before this, submenu/pipeline/ledger panels were added over the board with
	no blocker, so clicks landing outside the panel still reached the action icons
	behind (e.g. buy compute while the hiring pipeline was open). This mirrors the
	event-dialog blocker pattern (event_dialog.gd): a MOUSE_FILTER_STOP ColorRect that
	swallows every click to the board. The barrier is a sibling added just BEFORE the
	dialog (so the dialog, a later sibling, still receives its own clicks) and is freed
	automatically when the dialog leaves the tree -- via ANY close path (X, ESC, cancel,
	or a replacing dialog's queue_free) -- so no call site needs to manage it."""
	var barrier := ColorRect.new()
	barrier.name = "ModalInputBarrier"
	barrier.color = Color(0.0, 0.0, 0.0, 0.35)   # faint dim so the board reads as "behind"
	barrier.mouse_filter = Control.MOUSE_FILTER_STOP
	tab_manager.add_child(barrier)
	barrier.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	tab_manager.add_child(dialog)   # later sibling -> drawn above the barrier, stays interactive
	# Free the barrier whenever the dialog leaves the tree -- via ANY close path (X, ESC,
	# cancel button, or a replacing dialog's queue_free). No call site manages it.
	dialog.tree_exited.connect(barrier.queue_free)


func _debug_nudge_doom(delta: float) -> void:
	"""DEBUG-only QA helper: bump doom by delta, record a history point so the trend graph
	fills, and refresh the UI. Gated by OS.is_debug_build() at the call site."""
	if game_manager == null or game_manager.state == null:
		return
	var st = game_manager.state
	if st.doom_system:
		st.doom_system.current_doom = clampf(st.doom_system.current_doom + delta, 0.0, 100.0)
		st.doom = st.doom_system.current_doom
	else:
		st.doom = clampf(st.doom + delta, 0.0, 100.0)
	st.record_doom_history()
	_on_game_state_updated(game_manager.get_game_state())
	log_message("[color=gray][debug] doom %+.0f -> %.1f%%[/color]" % [delta, st.doom])

func _show_doom_trend_expanded() -> void:
	"""Expanded full-history doom trend panel (#512), reusing the #510 close affordance."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	var dialog := Panel.new()
	dialog.custom_minimum_size = Vector2(560, 360)
	dialog.size = Vector2(560, 360)
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 560) / 2.0,
		(get_viewport().get_visible_rect().size.y - 360) / 2.0
	)

	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = Color(0.10, 0.12, 0.14, 1.0)
	panel_style.border_width_left = 2
	panel_style.border_width_top = 2
	panel_style.border_width_right = 2
	panel_style.border_width_bottom = 2
	panel_style.border_color = Color(0.30, 0.40, 0.45, 1.0)
	panel_style.corner_radius_top_left = 6
	panel_style.corner_radius_top_right = 6
	panel_style.corner_radius_bottom_right = 6
	panel_style.corner_radius_bottom_left = 6
	dialog.add_theme_stylebox_override("panel", panel_style)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 12)
	margin.add_theme_constant_override("margin_bottom", 20)
	dialog.add_child(margin)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	margin.add_child(vbox)

	var header := Label.new()
	header.text = "DOOM TREND -- FULL HISTORY"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.80, 0.85, 0.90))
	vbox.add_child(header)

	var graph = preload("res://scripts/ui/doom_trend_graph.gd").new()
	graph.window_size = 0       # full history
	graph.clickable = false
	graph.line_width = 2.5
	graph.size_flags_vertical = Control.SIZE_EXPAND_FILL
	graph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(graph)
	var state = game_manager.get_game_state()
	graph.set_history(state.get("doom_history", []))

	_add_submenu_close_affordance(dialog)
	active_dialog = dialog
	_present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

# CARVE 1 (R4): _calculate_queued_costs moved verbatim to
# PlanController.calculate_queued_costs(). The view calls it in update_queued_actions_display.

func _show_hiring_submenu() -> void:
	# CARVE 3 (docs/MAIN_UI_SEAM_MAP.md, seams R1/R5): the hiring candidate-card pipeline
	# (pool panel, candidate + onboarding cards, offer dialog, in-flight tracker) moved verbatim
	# into HiringPanelController. This shim keeps the existing entry point unchanged --
	# SubmenuController.open("hire_staff") calls host._show_hiring_submenu().
	hiring_panel.open()

func _format_costs_inline(costs: Dictionary) -> String:
	"""Shared cost-summary formatter for the icon-grid submenus (fundraising / publicity /
	strategic / travel / operations). Cost-display sweep (2026-07-24, Pip playtest): these
	buttons were only showing cost on hover (tooltip_text) -- this is what now also goes ON
	the button face via a dedicated cost label, so a hidden-AP surprise (e.g. Compute
	Partnership, Intelligence Opportunity) can't happen here. Returns 'Free' for an empty/
	zero-cost dict."""
	var parts: Array[String] = []
	if costs.get("action_points", 0) > 0:
		parts.append("%d AP" % int(costs["action_points"]))
	if costs.get("money", 0) > 0:
		parts.append(GameConfig.format_money(costs["money"]))
	if costs.get("reputation", 0) > 0:
		parts.append("%d Rep" % int(costs["reputation"]))
	if costs.get("papers", 0) > 0:
		parts.append("%d Papers" % int(costs["papers"]))
	if costs.get("research", 0) > 0:
		parts.append("%d Research" % int(costs["research"]))
	if costs.get("compute", 0) > 0:
		parts.append("%d Compute" % int(costs["compute"]))
	if parts.is_empty():
		return "Free"
	return ", ".join(parts)


func _costs_affordable(costs: Dictionary, state: Dictionary) -> bool:
	"""Shared affordability check for the icon-grid submenus. IMPORTANT: action_points must be
	checked against the monthly Attention budget (available_ap), not the raw legacy
	action_points primitive -- get_available_ap() nets out what's already committed/reserved
	this plan month (see GameState.get_available_ap docstring). Using the raw field under-
	reported unaffordable options as affordable (cost-display sweep, #822-adjacent)."""
	for resource in costs.keys():
		var need = costs[resource]
		if need <= 0:
			continue
		var have = state.get("available_ap", 0) if resource == "action_points" else state.get(resource, 0)
		if have < need:
			return false
	return true


func _make_cost_label(cost_text: String, is_free: bool) -> Label:
	"""Small on-face cost line added under an icon-grid submenu button (cost-display sweep).
	Amber for a real cost, muted green for Free -- consistent with the AP-cost-indicator
	color used in update_queued_actions_display()."""
	var lbl := Label.new()
	lbl.text = cost_text
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.add_theme_font_size_override("font_size", 9)
	if is_free:
		lbl.add_theme_color_override("font_color", Color(0.55, 0.8, 0.55))
	else:
		lbl.add_theme_color_override("font_color", Color(0.9, 0.75, 0.35))
	return lbl


func _show_ledger_screen():
	"""BL-1/#601: open the full Liability Ledger screen. #622 L10: the panel itself is
	built by LedgerScreen; this stays the single entry point (L key, summary click,
	financing submenu, dev overlay) and owns the active_dialog bookkeeping."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	var ledger = game_manager.state.ledger if (game_manager and game_manager.state) else null
	# fix/ui-no-dead-ends: build_screen now attaches the close [X] + intrinsic Esc
	# (ui_cancel) affordance itself, wired to our _close_active_submenu so the dialog
	# bookkeeping stays with the host. No separate _decorate_active_submenu() needed --
	# doing both would stack two [X] buttons.
	# turn/start_* let each row show a real calendar due date, not a raw turn count.
	var g_state = game_manager.state if game_manager else null
	var dialog: Panel = ledger_screen.build_screen(ledger, get_viewport().get_visible_rect().size,
		_close_active_submenu,
		g_state.turn if g_state else 0,
		g_state.start_year if g_state else GameState.DEFAULT_START_YEAR,
		g_state.start_month if g_state else GameState.DEFAULT_START_MONTH,
		g_state.start_day if g_state else GameState.DEFAULT_START_DAY)

	active_dialog = dialog
	active_dialog_buttons = []
	_present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _show_strategic_unlock_fanfare() -> void:
	"""#578: Civ-style fade-up reveal when Strategic Moves first unlocks, instead of a button
	silently appearing. Text-only for now; the image slot (arg 3) takes a hero banner from
	art_prompts/hero_banners.yaml once those are generated."""
	log_message("[color=gold]The board convenes: Strategic Moves are now available.[/color]")
	FanfarePopup.show_fanfare(
		"STRATEGIC MOVES UNLOCKED",
		"The council of elders has deemed your standing sufficient. High-stakes plays now open to you -- bold gambits that can bend the odds, each leaving its mark on the ledger of history. Wield them wisely.",
		"",  # hero banner image slot -- art_prompts/hero_banners.yaml drops in here later
		get_tree().root)


# === TRAVEL & CONFERENCES SUBMENU (Issue #468) ===

func _show_travel_submenu():
	# CARVE 4 (docs/MAIN_UI_SEAM_MAP.md, seams R1/R5): the travel/conferences pipeline (actions
	# grid, paper-status + upcoming-conferences sections, submit-paper / attend-conference
	# sub-dialogs) moved verbatim into TravelPanelController -- the last bespoke submenu, parallel
	# to how CARVE 3 lifted hiring. This shim keeps the existing entry point unchanged:
	# SubmenuController.open("travel") and dev_mode_overlay both call host._show_travel_submenu().
	travel_panel.open()

func _format_turn_datetime(state: Dictionary) -> String:
	"""ONE tidy turn/time string: "Turn 14  -  Fri 21 Jul 2017". The turn is the plan
	period (counted); the calendar date is the human "when". Pure formatting off the
	state payload (turn + calendar dict) -- VIEW-only, no sim/clock mutation. ASCII."""
	var turn_n := int(state.get("turn", 0))
	var cal: Dictionary = state.get("calendar", {})
	if cal.is_empty():
		return "Turn %d" % turn_n
	var wd := String(cal.get("weekday", ""))
	var wd_abbr := wd.substr(0, 3) if wd.length() >= 3 else wd
	var day := int(cal.get("day", 0))
	var mi := int(cal.get("month", 1)) - 1
	var mon: String = Clock.MONTH_ABBR[mi] if mi >= 0 and mi < 12 else "?"
	var year := int(cal.get("year", 0))
	return "Turn %d  -  %s %d %s %d" % [turn_n, wd_abbr, day, mon, year]




func update_queued_actions_display():
	"""Update the visual queue display and message log"""
	# Clear existing queue items (except hint label)
	for child in queue_container.get_children():
		if child != queue_hint:
			child.queue_free()

	if plan_controller.queue_size() > 0:
		# Hide hint, show queue items
		queue_hint.visible = false

		# Create visual queue items
		for action in plan_controller.queued_actions:
			var action_name = action.get("name", "Unknown")
			var action_id = action.get("id", "")

			# Create queue item panel
			var item = PanelContainer.new()
			item.custom_minimum_size = Vector2(120, 60)

			var vbox = VBoxContainer.new()
			item.add_child(vbox)

			# Action name label
			var label = Label.new()
			label.text = action_name
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label.autowrap_mode = TextServer.AUTOWRAP_WORD
			label.add_theme_font_size_override("font_size", 11)
			vbox.add_child(label)

			# AP cost indicator
			var action_def = _get_action_by_id(action_id)
			var ap_cost = action_def.get("costs", {}).get("action_points", 0)
			if ap_cost > 0:
				var ap_cost_label = Label.new()
				ap_cost_label.text = "-%d AP" % ap_cost
				ap_cost_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
				ap_cost_label.add_theme_color_override("font_color", Color(0.9, 0.7, 0.2))
				ap_cost_label.add_theme_font_size_override("font_size", 10)
				vbox.add_child(ap_cost_label)

			# Remove button (X)
			var remove_btn = Button.new()
			remove_btn.text = "x Remove"
			remove_btn.custom_minimum_size = Vector2(90, 24)
			remove_btn.add_theme_font_size_override("font_size", 9)

			# Capture action_id in closure for the callback
			var captured_id = action_id
			var captured_name = action_name
			remove_btn.pressed.connect(func(): _remove_queued_action(captured_id, captured_name))

			vbox.add_child(remove_btn)

			queue_container.add_child(item)

		# Calculate and display turn preview (total costs from queued actions -- R4 logic in PlanController)
		var total_costs = plan_controller.calculate_queued_costs()
		if not total_costs.is_empty():
			var preview_panel = PanelContainer.new()
			preview_panel.custom_minimum_size = Vector2(150, 60)

			var preview_vbox = VBoxContainer.new()
			preview_panel.add_child(preview_vbox)

			var preview_title = Label.new()
			preview_title.text = "Turn Preview:"
			preview_title.add_theme_font_size_override("font_size", 10)
			preview_title.add_theme_color_override("font_color", Color(0.7, 0.9, 1.0))
			preview_vbox.add_child(preview_title)

			# Show projected costs
			for resource in total_costs.keys():
				var cost_label = Label.new()
				var cost_value = total_costs[resource]
				var formatted = ""
				if resource == "money":
					formatted = GameConfig.format_money(-cost_value)
				elif resource == "action_points":
					formatted = "-%d AP" % cost_value
				else:
					formatted = "-%d %s" % [cost_value, resource]
				cost_label.text = formatted
				cost_label.add_theme_font_size_override("font_size", 10)
				cost_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.6))
				preview_vbox.add_child(cost_label)

			queue_container.add_child(preview_panel)

		# Log message
		var action_names = []
		for action in plan_controller.queued_actions:
			action_names.append(action.get("name", "Unknown"))
		log_message("[color=lime]Queued actions (%d): %s[/color]" % [plan_controller.queue_size(), ", ".join(action_names)])
	else:
		# Show hint, hide items
		queue_hint.visible = true
		log_message("[color=gray]No actions queued[/color]")

	# Update button states based on queue (case-insensitive phase check)
	var phase_upper = current_turn_phase.to_upper()
	if phase_upper == "ACTION_SELECTION":
		var queue_empty = plan_controller.is_queue_empty()
		undo_last_button.disabled = queue_empty
		clear_queue_button.disabled = queue_empty
		end_turn_button.disabled = queue_empty
		print("[MainUI] Updated button states: queue_size=%d, buttons_disabled=%s" % [plan_controller.queue_size(), queue_empty])

	# P10 gantt: mirror the tentative plan-time queue into the operations tracker. No-op in classic.
	_refresh_gantt()

func _on_event_dialog_opened(dialog: Control, buttons: Array) -> void:
	"""EventDialog put its modal up (#622) -- route MainUI keyboard shortcuts to it.
	The dialog carries the is_event_dialog meta, so ESC handling keeps refusing to
	close it (#452)."""
	# An event can fire while a submenu/ledger is already open. Overwriting active_dialog
	# without freeing the prior panel ORPHANS it (visible with its input barrier, but
	# untracked -> Esc/L/N no longer close it). Free it first so the visible overlay and
	# the tracked slot can never diverge. (Mirrors _on_employee_dialog_opened.)
	if active_dialog != null and is_instance_valid(active_dialog) and active_dialog != dialog:
		active_dialog.queue_free()
	active_dialog = dialog
	active_dialog_buttons = buttons

func _on_event_dialog_closed() -> void:
	"""EventDialog dismissed its modal -- clear the keyboard-routing state (#622)."""
	active_dialog = null
	active_dialog_buttons = []

func _on_event_choice_selected(event: Dictionary, choice_id: String) -> void:
	"""Resolution stays signal-driven through game_manager.resolve_event (#622, L1 reuse).
	Direction-b (playtest 2026-07-24): the dialog no longer closes on press -- it waits for
	the resolution result and only closes/advances on SUCCESS. On a failed affordability check
	the dialog stays OPEN and shows WHY, so a rejected choice never reads as 'order accepted'."""
	var result: Dictionary = game_manager.resolve_event(event, choice_id)
	var ok := true
	var reason := ""
	if result is Dictionary:
		ok = bool(result.get("success", true))
		reason = String(result.get("message", result.get("error", "")))
	event_dialog.report_choice_result(ok, reason)


func _on_action_hover(action: Dictionary, can_afford: bool, missing_resources: Array):
	"""Update info bar when hovering over an action and highlight affected resources"""
	var action_name = action.get("name", "Unknown")
	var action_desc = action.get("description", "")
	var action_costs = action.get("costs", {})

	# Build info text with enhanced formatting
	var info_text = "[b][color=cyan]%s[/color][/b] -- %s" % [action_name, action_desc]

	# Add costs with icons/colors (always add line for consistent 2-line format)
	info_text += "\n[color=gray]|-[/color] "
	if not action_costs.is_empty():
		info_text += "[color=yellow]Costs:[/color] "
		var cost_parts = []

		# Format each resource cost with appropriate color
		if action_costs.has("action_points"):
			cost_parts.append("[color=magenta]%d AP[/color]" % action_costs["action_points"])
		if action_costs.has("money"):
			cost_parts.append("[color=gold]%s[/color]" % GameConfig.format_money(action_costs["money"]))
		if action_costs.has("reputation"):
			cost_parts.append("[color=orange]%d Rep[/color]" % action_costs["reputation"])
		if action_costs.has("papers"):
			cost_parts.append("[color=white]%d Papers[/color]" % action_costs["papers"])
		if action_costs.has("compute"):
			cost_parts.append("[color=blue]%.1f Compute[/color]" % action_costs["compute"])
		if action_costs.has("research"):
			cost_parts.append("[color=purple]%.1f Research[/color]" % action_costs["research"])

		info_text += " - ".join(cost_parts)
	else:
		info_text += "[color=gray]No costs[/color]"

	# Show affordability with visual indicator
	info_text += "\n[color=gray]`-[/color] "
	if not can_afford:
		info_text += "[color=red][X] CANNOT AFFORD[/color]"
		if missing_resources.size() > 0:
			info_text += " [color=gray](%s)[/color]" % missing_resources[0]
	else:
		info_text += "[color=lime][OK] READY TO USE[/color]"

	info_label.text = info_text

	# Highlight affected resource labels in top bar
	_highlight_resources(action_costs)

func _on_action_unhover():
	"""Reset info bar when mouse leaves action - maintain 2-line format to prevent flicker (issue #450)"""
	info_label.text = "[color=gray]Hover over actions to see details...\n [/color]"
	# Reset resource highlights
	_reset_resource_highlights()

func _highlight_resources(costs: Dictionary):
	"""Highlight resource labels that will be affected by an action"""
	# Map cost keys to label references (excluding ap_label which is RichTextLabel)
	var resource_label_map = {
		"money": money_label,
		"compute": compute_label,
		"research": research_label,
		"papers": papers_label,
		"reputation": reputation_label
	}

	# Highlight each affected resource with a yellow/gold tint
	for resource in costs.keys():
		if resource_label_map.has(resource):
			var label = resource_label_map[resource]
			if label:
				label.add_theme_color_override("font_color", Color(1.0, 0.9, 0.3))  # Gold highlight

func _reset_resource_highlights():
	"""Reset all resource labels to default color"""
	# Regular labels
	var labels = [money_label, compute_label, research_label, papers_label, reputation_label]
	for label in labels:
		if label:
			label.remove_theme_color_override("font_color")
	# ap_label is RichTextLabel - skip color override reset (it uses BBCode colors)

func _on_employee_dialog_opened(dialog: Control) -> void:
	"""EmployeePanel put the staff ID card up (#622). Preserves the old behavior:
	any existing dialog is closed first, then the ID card becomes the active dialog
	(the buttons array is left as-is, exactly as before the extraction)."""
	if active_dialog != null and is_instance_valid(active_dialog) and active_dialog != dialog:
		active_dialog.queue_free()
	active_dialog = dialog

func _on_employee_dialog_closed() -> void:
	"""Staff ID card dismissed (blocker click or its own close button)."""
	active_dialog = null

func _on_employee_info_text(text: String) -> void:
	"""Perk hover details from the staff ID card feed the shared info bar."""
	info_label.text = text


# === OPERATIONS SUBMENU ===

# === COMMAND ZONE - PASS ACTION ===

func _on_pass_button_pressed():
	"""Handle the Do Nothing / Pass button in the command zone"""
	print("[MainUI] Pass button pressed (Do Nothing)")

	# Get pass action definition
	var pass_action = GameActions.get_pass_action()
	var action_id = pass_action.get("id", GameActions.PASS_ACTION_ID)
	var action_name = pass_action.get("name", "Do Nothing")

	# Check if we're in action selection phase
	if current_turn_phase.to_upper() != "ACTION_SELECTION":
		log_message("[color=red]Cannot pass - not in action selection phase[/color]")
		return

	# Check AP availability (pass costs 0 AP but still need to verify game state)
	var available_ap = game_manager.state.get_available_ap()
	var ap_cost = pass_action.get("costs", {}).get("action_points", 0)

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	log_message("[color=gray]%s - skipping this action[/color]" % action_name)

	# Queue the pass action -- #821: only add the UI tile when the backend accepts
	# (select_action returns false if e.g. events are pending), so a rejected pass
	# no longer leaves a phantom queue tile. Pass is free, so overbook never blocks it.
	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	if plan_controller.select_action(action_id):
		plan_controller.queue_action(action_id, action_name)
		update_queued_actions_display()

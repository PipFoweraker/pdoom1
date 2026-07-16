extends VBoxContainer
## Main UI controller - connects UI elements to GameManager

# References to UI elements (TopBar now has all resources in one line)
@onready var turn_label = $TopBar/TurnLabel
@onready var turn_count_label = $TopBar/TurnCountLabel
@onready var money_label = $TopBar/MoneyLabel
@onready var compute_label = $TopBar/ComputeLabel
@onready var research_label = $TopBar/ResearchLabel
@onready var papers_label = $TopBar/PapersLabel
@onready var reputation_label = $TopBar/ReputationLabel
@onready var ap_label = $TopBar/APLabel
@onready var phase_label = $BottomBar/PhaseLabel
@onready var message_log = $ContentArea/RightPanel/MessageScroll/MessageLog
@onready var actions_list = $ContentArea/LeftPanel/ActionsScroll/ActionsList
@onready var upgrades_list = $ContentArea/RightPanel/UpgradesScroll/UpgradesList
@onready var info_label = $InfoBar/MarginContainer/InfoLabel
@onready var queue_container = $ContentArea/RightPanel/QueuePanel/QueueContainer
@onready var queue_hint = $ContentArea/RightPanel/QueuePanel/QueueContainer/QueueHint

@onready var init_button = $BottomBar/ControlButtons/InitButton
@onready var test_action_button = $BottomBar/ControlButtons/TestActionButton
@onready var reserve_ap_button = $BottomBar/ControlButtons/ReserveAPButton
@onready var undo_last_button = $BottomBar/ControlButtons/UndoLastButton
@onready var clear_queue_button = $BottomBar/ControlButtons/ClearQueueButton
@onready var end_turn_button = $BottomBar/ControlButtons/EndTurnButton
@onready var commit_plan_button = $BottomBar/ControlButtons/CommitPlanButton
@onready var doom_meter = $ContentArea/MiddlePanel/CoreZone/RightZones/DoomMeterZone/DoomMeterPanel/MarginContainer/DoomMeter
@onready var numeric_doom_label = $ContentArea/MiddlePanel/CoreZone/RightZones/NumericDoomZone/NumericDoomLabel
@onready var game_over_screen = $"../GameOverScreen"
@onready var bug_report_panel = $"../BugReportPanel"
@onready var bug_report_button = $BottomBar/BugReportButton
@onready var office_cat = $ContentArea/MiddlePanel/CoreZone/CatZone/OfficeCat
@onready var tab_manager = get_parent()
@onready var roster_container = $ContentArea/MiddlePanel/EmployeeRosterZone/RosterScroll/RosterContainer
@onready var pause_menu = $"../../PauseMenu"
@onready var getting_started_hint = $ContentArea/LeftPanel/GettingStartedHint

# Reference to GameManager
var game_manager: Node

# Track queued actions
var queued_actions: Array = []
var research_quality_selector  # Issue #500
var doom_trend_graph  # #512 doom trend sparkline (script-instantiated)
var doom_breakdown  # #578 colour-coded per-source doom "blow-by-blow" (script-instantiated)
var event_dialog  # #622 L10: event dialog presenter (script-instantiated child)
var ledger_screen  # #622 L10: Liability Ledger UI (leather palette + summary button + screen builder)
var employee_panel  # #622 L10: employee roster + staff ID card (becomes L2's assignment surface)
# EE-7 (ADR-0012 loss legibility): per-resource "last turn" delta chips beside the
# money/compute/reputation/doom readouts. Snapshot at each turn boundary; a chip shows
# the change over the last completed turn, green=helped red=hurt (doom inverted).
var _delta_labels: Dictionary = {}       # resource key -> Label
var _prev_turn_snapshot: Dictionary = {}
var _last_delta_turn: int = -1
const _DELTA_GOOD := Color(0.35, 0.85, 0.40)
const _DELTA_BAD := Color(0.95, 0.30, 0.25)
var _seen_unlocked_actions: Dictionary = {}  # #578: action ids seen unlocked, to detect NEW unlocks for fanfare
var _actions_primed: bool = false  # skip fanfare on the very first action population (baseline)
var current_turn_phase: String = "NOT_STARTED"

# Active dialog state for keyboard shortcuts
var active_dialog: Control = null
var active_dialog_buttons: Array = []

func _ready():
	print("[MainUI] Initializing UI...")

	# Get GameManager reference — the autoload singleton is the ONE GameManager
	# (L0 #620/#608: the duplicate scene-local node was removed from main.tscn)
	game_manager = GameManager

	# Connect to GameManager signals
	game_manager.game_state_updated.connect(_on_game_state_updated)
	game_manager.turn_phase_changed.connect(_on_turn_phase_changed)
	game_manager.action_executed.connect(_on_action_executed)
	game_manager.error_occurred.connect(_on_error_occurred)
	game_manager.actions_available.connect(_on_actions_available)

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
	$ContentArea/LeftPanel.add_child(research_quality_selector)
	$ContentArea/LeftPanel.move_child(research_quality_selector, 0)

	# #512: doom trend sparkline, inserted just below the doom gauge in RightZones
	var right_zones := $ContentArea/MiddlePanel/CoreZone/RightZones
	var doom_meter_zone := $ContentArea/MiddlePanel/CoreZone/RightZones/DoomMeterZone
	doom_trend_graph = preload("res://scripts/ui/doom_trend_graph.gd").new()
	doom_trend_graph.custom_minimum_size = Vector2(0, 92)  # taller — playtest feedback (screen1)
	doom_trend_graph.window_size = 24  # show more time points (screen6)
	doom_trend_graph.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	doom_trend_graph.expand_requested.connect(_show_doom_trend_expanded)
	right_zones.add_child(doom_trend_graph)
	right_zones.move_child(doom_trend_graph, doom_meter_zone.get_index() + 1)

	# #578: doom "blow-by-blow" — colour-coded per-source breakdown, just below the trend graph.
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
	employee_access_btn.text = "👥  Employees — roster & morale"
	employee_access_btn.tooltip_text = "Open the Employee management screen  (ESC returns here)"
	employee_access_btn.pressed.connect(_on_open_employee_screen)
	right_zones.add_child(employee_access_btn)
	right_zones.move_child(employee_access_btn, ledger_summary_btn.get_index() + 1)

	# Always-visible DEV BUILD corner badge so a playtester can confirm exactly which
	# build he's running (version + git stamp). Draws on its own CanvasLayer over the UI.
	add_child(DevBuildBadge.new())

	# DEV MODE overlay (backslash) — full state readout + dev controls, on its own CanvasLayer.
	# Gated on BuildInfo.DEV_BUILD by the overlay; wired to MainUI so its jump buttons can
	# drive the in-place ledger/travel/employee screens.
	var dev_overlay := DevModeOverlay.new()
	dev_overlay.main_ui = self
	add_child(dev_overlay)

	# Playtest flight recorder (F6) — screenshot + state snapshot + marker note in
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

	# Call init on next frame to ensure everything is ready
	await get_tree().process_frame
	_on_init_button_pressed()

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

	# Populate upgrades list
	_populate_upgrades()

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		# When a full-screen sub-view (e.g. the Employee screen) is up, MainUI is hidden
		# and is NOT the active screen. Don't handle any shortcuts — and crucially don't
		# open the pause menu — from here; TabManager owns ESC/back in that state so ESC
		# returns to the main view, not the game menu (#602).
		if not visible:
			return

		# Game/global shortcuts yield to focused text fields so typing works (#575).
		# Bug-report form etc. own a LineEdit/TextEdit; let those keys reach the field.
		# Dialog choice buttons use FOCUS_NONE, so this never blocks dialog keys.
		if KeybindManager.is_text_input_focused():
			return

		# DEBUG: sweep doom for QA (PageUp/PageDown ±10). Debug builds only — auto-off in release.
		# TODO: remove before any release/PR if undesired (currently gated, so release-safe).
		if OS.is_debug_build() and (event.keycode == KEY_PAGEUP or event.keycode == KEY_PAGEDOWN):
			_debug_nudge_doom(10.0 if event.keycode == KEY_PAGEUP else -10.0)
			get_viewport().set_input_as_handled()
			return

		# Liability Ledger toggle (L): open when closed, close when the ledger itself is
		# open — a key that opens a panel should also close it (#601). Respects the
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
				_show_hiring_submenu()
				_decorate_active_submenu(_find_action_button("hire_staff"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_fundraise"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				_show_fundraising_submenu()
				_decorate_active_submenu(_find_action_button("fundraise"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_publicity"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				_show_publicity_submenu()
				_decorate_active_submenu(_find_action_button("publicity"))
				get_viewport().set_input_as_handled()
		elif KeybindManager.is_action_pressed(event, "menu_travel"):
			if current_turn_phase.to_upper() == "ACTION_SELECTION":
				_show_travel_submenu()
				_decorate_active_submenu(_find_action_button("travel"))
				get_viewport().set_input_as_handled()

		# Escape to init game (if not started)
		elif event.keycode == KEY_ESCAPE:
			if not init_button.disabled:
				_on_init_button_pressed()
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

func _on_init_button_pressed():
	init_button.disabled = true
	# L7 (#618): if the welcome screen queued a saved game, boot into it instead
	# of starting a new run. The flag is one-shot.
	if GameConfig.pending_load_path != "":
		var load_path: String = GameConfig.pending_load_path
		GameConfig.pending_load_path = ""
		log_message("[color=cyan]Loading saved game...[/color]")
		if game_manager.load_saved_game(load_path):
			return
		log_message("[color=red]Load failed — starting a new game instead.[/color]")
	log_message("[color=cyan]Initializing game...[/color]")
	# #617 debt: was hardcoded "test-seed" — every boot ran the SAME timeline and
	# GameConfig.game_seed was ignored. Empty arg -> GameManager falls back to
	# GameConfig.get_display_seed() (player's configured seed, else the weekly seed).
	game_manager.start_new_game()

func _on_test_action_button_pressed():
	log_message("[color=cyan]Selecting action: hire_safety_researcher[/color]")
	game_manager.select_action("hire_safety_researcher")

func _on_reserve_ap_button_pressed():
	"""Reserve 1 AP for event responses"""
	log_message("[color=cyan]Reserving 1 AP for events...[/color]")
	game_manager.reserve_ap(1)

func _on_undo_last_button_pressed():
	"""Undo (remove) the last queued action"""
	if queued_actions.size() == 0:
		return

	# Get the last action
	var last_action = queued_actions[-1]
	var action_id = last_action.get("id", "")
	var action_name = last_action.get("name", "Unknown")

	# Remove it using existing logic
	_remove_queued_action(action_id, action_name)

func _on_clear_queue_button_pressed():
	"""Clear all queued actions and refund AP"""
	if queued_actions.size() == 0:
		return

	# Call GameManager to clear queue (refunds AP)
	game_manager.clear_action_queue()

	# Update local display
	queued_actions.clear()
	update_queued_actions_display()

	log_message("[color=yellow]Action queue cleared - AP refunded[/color]")

func _remove_queued_action(action_id: String, action_name: String):
	"""Remove a specific action from the queue"""
	print("[MainUI] Removing queued action: %s (id: %s)" % [action_name, action_id])

	# Find and remove from local queue
	var removed_index = -1
	for i in range(queued_actions.size()):
		if queued_actions[i].get("id") == action_id:
			removed_index = i
			break

	if removed_index >= 0:
		queued_actions.remove_at(removed_index)

		# Tell GameManager to remove and refund AP
		game_manager.remove_queued_action(action_id)

		# Get AP cost for logging
		var action_def = _get_action_by_id(action_id)
		var ap_cost = action_def.get("costs", {}).get("action_points", 0)

		log_message("[color=yellow]Removed: %s (+%d AP)[/color]" % [action_name, ap_cost])
		update_queued_actions_display()
	else:
		print("[MainUI] ERROR: Could not find action to remove: %s" % action_id)

func _on_end_turn_button_pressed():
	if queued_actions.size() == 0:
		log_message("[color=red]ERROR: No actions queued! Press C to clear queue or select actions.[/color]")
		return

	# Check for danger zones and warn player
	var current_state = game_manager.state
	var warnings = []

	# High doom warning
	# Routed through ThemeManager's canonical bands (L6 unification: was hardcoded
	# 80/70; now CATASTROPHIC >=80 critical, EXTREME >=67 warning)
	var doom_band: int = ThemeManager.get_doom_band_index(current_state.doom)
	if doom_band >= 5:
		warnings.append("[color=red]⚠️ CRITICAL: Doom at %.1f%% (%s) - Very close to game over![/color]" % [current_state.doom, ThemeManager.get_doom_status_label(current_state.doom)])
	elif doom_band == 4:
		warnings.append("[color=yellow]⚠️ WARNING: Doom at %.1f%% (%s) - Approaching danger zone![/color]" % [current_state.doom, ThemeManager.get_doom_status_label(current_state.doom)])

	# Low reputation warning
	if current_state.reputation <= 20:
		warnings.append("[color=red]⚠️ CRITICAL: Reputation at %.0f - May lose funding![/color]" % current_state.reputation)
	elif current_state.reputation <= 30:
		warnings.append("[color=yellow]⚠️ WARNING: Low reputation (%.0f) - Watch funding![/color]" % current_state.reputation)

	# Low money warning
	if current_state.money <= 20000:
		warnings.append("[color=red]⚠️ CRITICAL: Low funds (%s) - Can't afford much![/color]" % GameConfig.format_money(current_state.money))

	# Technical debt warning (Issue #416)
	if current_state.technical_debt >= 75:
		warnings.append("[color=red]⚠️ CRITICAL: Technical debt at %.0f%% - High failure risk![/color]" % current_state.technical_debt)
	elif current_state.technical_debt >= 50:
		warnings.append("[color=yellow]⚠️ WARNING: Technical debt at %.0f%% - Consider an audit![/color]" % current_state.technical_debt)

	# Show warnings if any
	if warnings.size() > 0:
		for warning in warnings:
			log_message(warning)
		log_message("[color=gray]Press Space/Enter again to confirm, or C to revise queue[/color]")
		# Note: Simplified version - in full implementation, would require double-confirm

	log_message("[color=cyan]Committing month plan (%d actions) — playing the month out...[/color]" % queued_actions.size())

	# Clear queued actions (will be repopulated after turn processes)
	queued_actions.clear()
	update_queued_actions_display()

	# L1 (ADR-0009): End Turn commits the MONTH plan and hands control to day-tick
	# playback (auto-pause on response windows, month review at the boundary). The old
	# single day-step lives on ONLY behind the DEV MODE overlay ("Day step (dev)").
	game_manager.end_month()

func _on_commit_plan_button_pressed():
	"""Commit queued actions AND reserve remaining AP (no warnings)"""
	var current_state = game_manager.get_game_state()
	var available_ap = current_state.get("available_ap", 0)

	# If there are queued actions, commit them + reserve balance
	if queued_actions.size() > 0:
		log_message("[color=cyan]Committing %d queued actions + reserving %d remaining AP...[/color]" % [queued_actions.size(), available_ap])
	else:
		# No queued actions - just reserve all AP (reactive strategy)
		log_message("[color=cyan]Committing plan: Reserving all %d AP for reactive responses...[/color]" % available_ap)

		# Queue the pass action to represent reactive strategy (L0 #620: was the
		# twin id "pass_turn"; ONE id now — GameActions.PASS_ACTION_ID)
		var reserve_action = {
			"id": GameActions.PASS_ACTION_ID,
			"name": "Reserve All AP",
			"description": "No planned actions - keep all AP available for responding to events",
			"ap_cost": 0,
			"money_cost": 0
		}
		queued_actions.append(reserve_action)
		update_queued_actions_display()

		# Directly append to game state queue (bypass select_action validation)
		# — a virtual "reserve all AP" entry; pass costs {} so no AP is committed
		game_manager.state.queued_actions.append(GameActions.PASS_ACTION_ID)

	# Clear local queue (will be repopulated after turn processes)
	queued_actions.clear()
	update_queued_actions_display()

	# Commit the plan — the L1 month path (see _on_end_turn_button_pressed).
	game_manager.end_month()

func _on_employee_tab_button_pressed():
	"""Switch to employee management screen - DISABLED: employee info moving to main UI"""
	# tab_manager.show_employee_screen()
	pass

func _on_open_employee_screen() -> void:
	"""#602: open the full Employee screen via the TabManager. ESC (handled by TabManager)
	or the screen's own Back button returns to the main view — MainUI's ESC-to-pause is
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

	# Update resource displays (Issue #472 - enhanced turn display with calendar)
	var turn_display = state.get("turn_display", "")
	if turn_display != "":
		turn_label.text = turn_display
	else:
		turn_label.text = "Turn: %d" % state.get("turn", 0)
	# Playtest (Pip): the month-year/date badge above has no single number to track
	# state by. This is a plain "Turn N" counter next to it (#F6 HUD lane).
	turn_count_label.text = "Turn %d" % state.get("turn", 0)
	money_label.text = "💰 %s" % GameConfig.format_money(state.get("money", 0))
	compute_label.text = "🖥️ %.1f" % state.get("compute", 0)
	research_label.text = "🔬 %.1f" % state.get("research", 0)
	papers_label.text = "📄 %d" % state.get("papers", 0)
	reputation_label.text = "⭐ %.0f" % state.get("reputation", 0)

	# EE-7: refresh the per-resource "last turn" delta chips at turn boundaries
	_update_delta_chips(state)

	# Add employee blob display to AP label (using BBCode for RichTextLabel)
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)
	var blob_display = ""
	for _i in range(safety):
		blob_display += "[color=green]●[/color]"
	for _i in range(capability):
		blob_display += "[color=red]●[/color]"
	for _i in range(compute_eng):
		blob_display += "[color=dodger_blue]●[/color]"

	# L2 (ADR-0011): the founder currency is the monthly ATTENTION budget (month_plan), not
	# the retired per-turn AP pool. Read the plan's Attention split so the HUD is honest —
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
		doom_breakdown.set_sources(state.get("doom_system", {}).get("doom_sources", {}))

	# BL-1: refresh the compact Liability Ledger summary (#622 L10: lives in LedgerScreen)
	if ledger_screen:
		ledger_screen.update_summary(state.get("ledger", {}))

	# Update office cat for doom level and visibility
	if office_cat:
		office_cat.update_doom_level(doom / 100.0)  # Convert percentage to 0.0-1.0
		# Show cat if adopted, hide if not
		office_cat.visible = state.get("has_cat", false)

	# Hide getting started hint after turn 3 (new player onboarding)
	if getting_started_hint:
		getting_started_hint.visible = state.get("turn", 0) < 3

	# Enable controls after first init
	if state.get("turn", 0) >= 0:
		test_action_button.disabled = false
		init_button.disabled = true

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
		test_action_button.disabled = true
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
	Playtest motivation: the one human ledger-death specimen was low-resolution —
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


func _format_deltas(deltas: Dictionary) -> String:
	"""EE-7: BBCode-coloured 'money +$20k, doom +3.0' summary for the message log —
	resource-affecting events state their deltas instead of burying them in prose."""
	var order := ["money", "compute", "research", "papers", "reputation", "doom"]
	var parts := []
	for key in order:
		if not deltas.has(key):
			continue
		var d: float = float(deltas[key])
		var txt: String
		if key == "money":
			txt = ("+" if d > 0.0 else "-") + GameConfig.format_money(absf(d))
		else:
			txt = "%+.1f" % d
		var good: bool = (d < 0.0) if key == "doom" else (d > 0.0)
		parts.append("[color=%s]%s %s[/color]" % ["lime" if good else "red", key, txt])
	return ", ".join(parts)

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
		end_turn_button.disabled = (queued_actions.size() == 0)
		commit_plan_button.disabled = false
		undo_last_button.disabled = (queued_actions.size() == 0)
		clear_queue_button.disabled = (queued_actions.size() == 0)
	elif phase_name == "turn_end" or phase_name == "TURN_END":
		phase_color = "yellow"
		phase_display = "EXECUTING - Your actions are running..."
		end_turn_button.disabled = true
		commit_plan_button.disabled = true

	phase_label.text = "[color=%s]Phase: %s[/color]" % [phase_color, phase_display]

	log_message("[color=magenta]Turn Phase: " + phase_name + "[/color]")

func _on_action_executed(result: Dictionary):
	print("[MainUI] Action executed: ", result)

	var message = result.get("message", "Action completed")
	log_message("[color=lime]" + message + "[/color]")

	# EE-7: resource-affecting events/actions state their applied deltas explicitly
	var deltas: Dictionary = result.get("deltas", {})
	if not deltas.is_empty():
		log_message("[color=gray]  └─ Δ[/color] " + _format_deltas(deltas))

	# Show any additional messages from action
	if result.has("messages"):
		for msg in result.get("messages", []):
			log_message("[color=white]  " + str(msg) + "[/color]")

	# Note: GameManager now handles auto-starting next turn

func _on_achievement_unlocked(achievement: Dictionary) -> void:
	"""L8 (#619): surface unlocks in the message log. Recognition only (ADR-0002)."""
	log_message("[color=gold]★ Achievement — %s:[/color] [color=gray]%s[/color]" % [
		achievement.get("title", "?"), achievement.get("flavor", "")])

func _on_error_occurred(error_msg: String):
	print("[MainUI] Error: ", error_msg)
	log_message("[color=red]ERROR: " + error_msg + "[/color]")

func log_message(text: String):
	"""Add a message to the log with timestamp"""
	var timestamp = Time.get_ticks_msec() / 1000.0
	message_log.text += "\n[color=gray][%.1fs][/color] %s" % [timestamp, text]

	# Auto-scroll to bottom
	await get_tree().process_frame
	var scroll = message_log.get_parent() as ScrollContainer
	if scroll:
		scroll.scroll_vertical = scroll.get_v_scroll_bar().max_value

func _on_actions_available(actions: Array):
	"""Populate action list with icon buttons in a grid layout"""
	print("[MainUI] Populating ", actions.size(), " actions as icon buttons")

	# Clear existing action buttons (except test button for now)
	for child in actions_list.get_children():
		if child.name != "TestActionButton":
			child.queue_free()

	# Get current state for affordability and unlock checking
	var current_state = game_manager.get_game_state()

	# Filter actions by unlock status (Issue #415: Action Discovery)
	var unlocked_count = 0
	var locked_count = 0

	# Group actions by category, filtering out locked actions
	var categories = {}
	var unlocked_ids := {}  # #578: track which ids are unlocked this pass (for new-unlock fanfares)
	for action in actions:
		# Check if action is unlocked based on game state
		if not GameActions.is_action_unlocked(action, current_state):
			locked_count += 1
			continue  # Skip locked actions - they won't be shown

		unlocked_count += 1
		unlocked_ids[action.get("id", "")] = true
		var category = action.get("category", "other")
		if not categories.has(category):
			categories[category] = []
		categories[category].append(action)

	if locked_count > 0:
		print("[MainUI] Action Discovery: %d unlocked, %d locked (hidden)" % [unlocked_count, locked_count])

	# #578: momentous-unlock fanfare. When Strategic Moves first becomes available, fade a
	# Civ-style reveal up over the screen instead of the button just silently appearing.
	# This is the ONE wired proof trigger; the same FanfarePopup API can front other unlocks.
	if _actions_primed and unlocked_ids.has("strategic") and not _seen_unlocked_actions.has("strategic"):
		_show_strategic_unlock_fanfare()
	for id in unlocked_ids:
		_seen_unlocked_actions[id] = true
	_actions_primed = true

	# Define category order
	var category_order = ["hiring", "resources", "research", "funding", "management", "influence", "strategic", "other"]

	# Define category colors
	var category_colors = {
		"hiring": ThemeManager.get_category_color("hiring"),
		"resources": ThemeManager.get_category_color("resources"),
		"research": ThemeManager.get_category_color("research"),
		"management": ThemeManager.get_category_color("management"),
		"influence": ThemeManager.get_category_color("influence"),
		"strategic": ThemeManager.get_category_color("strategic"),
		"funding": ThemeManager.get_category_color("funding"),
		"other": Color(0.8, 0.8, 0.8)
	}

	# Create a single-column vertical stack for icons on left edge
	var icon_stack = VBoxContainer.new()
	icon_stack.add_theme_constant_override("separation", 1)  # #594: tighter vertical packing for 11+ icons
	actions_list.add_child(icon_stack)

	# Create icon buttons - single column layout
	var action_index = 0  # Track index for keyboard shortcuts

	for category_key in category_order:
		if not categories.has(category_key):
			continue

		var category_actions = categories[category_key]
		if category_actions.is_empty():
			continue

		# Create icon buttons for actions in this category
		for action in category_actions:
			var action_id = action.get("id", "")
			var action_name = action.get("name", "Unknown")
			var action_cost = action.get("costs", {})

			# Create icon-only button (square, fills width)
			var icon_button = Button.new()
			icon_button.custom_minimum_size = Vector2(70, 70)  # square icon tiles
			# #594: hug the 70px icon instead of ballooning across the wide left panel — this
			# reclaims the empty padding around each icon (and stops expand_icon distorting them).
			icon_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
			icon_button.focus_mode = Control.FOCUS_NONE

			# Get icon texture
			var icon_texture = IconLoader.get_action_icon(action_id)
			if icon_texture:
				icon_button.icon = icon_texture
				icon_button.expand_icon = true
				icon_button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

			# Add keyboard shortcut number badge (prominent for discoverability)
			if action_index < 9:
				icon_button.text = str(action_index + 1)
				icon_button.add_theme_font_size_override("font_size", 14)  # Increased from 9
				icon_button.add_theme_color_override("font_color", Color(1, 1, 1, 1))  # Full opacity
				icon_button.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
				icon_button.add_theme_constant_override("outline_size", 2)

			action_index += 1

			# Check if player can afford this action
			var can_afford = true
			var missing_resources = []

			for resource in action_cost.keys():
				var cost = action_cost[resource]
				var available = current_state.get(resource, 0)

				if available < cost:
					can_afford = false
					missing_resources.append("%s (need %s, have %s)" % [resource, cost, available])

			# Style based on affordability and category
			if not can_afford:
				icon_button.disabled = true
				icon_button.modulate = Color(0.4, 0.4, 0.4)  # Dark gray for unaffordable
			else:
				# Apply category color tint
				var button_color = category_colors.get(category_key, Color(1.0, 1.0, 1.0))
				icon_button.modulate = Color(0.9, 0.9, 0.9).lerp(button_color, 0.4)

			# Simple tooltip for accessibility
			icon_button.tooltip_text = action_name

			# Tag with action_id so submenus can align to the button that opened them (#510)
			icon_button.set_meta("action_id", action_id)

			# Connect button press
			icon_button.pressed.connect(func(): _on_dynamic_action_pressed(action_id, action_name))

			# Connect mouse hover for info bar
			icon_button.mouse_entered.connect(func(): _on_action_hover(action, can_afford, missing_resources))
			icon_button.mouse_exited.connect(func(): _on_action_unhover())

			# Add to stack
			icon_stack.add_child(icon_button)

	# Also populate upgrades
	_populate_upgrades()

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
		# Blockier tiles (#594): hug content on the left instead of stretching across the
		# wide right panel, and ~20% taller (32 -> 38) so they read as tighter, blockier tiles.
		button.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		button.custom_minimum_size = Vector2(200, 38)

		# If purchased, show differently
		if is_purchased:
			button.text = "✓ " + upgrade_name
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
	var info_text = "[b][color=cyan]%s[/color][/b] — %s" % [upgrade_name, upgrade_desc]

	# Show cost
	info_text += "\n[color=gray]├─[/color] [color=yellow]Cost:[/color] [color=gold]%s[/color]" % GameConfig.format_money(upgrade_cost)

	# Show status
	info_text += "\n[color=gray]└─[/color] "
	if is_purchased:
		info_text += "[color=green]✓ ALREADY PURCHASED[/color]"
	else:
		var current_state = game_manager.get_game_state()
		if current_state.get("money", 0) >= upgrade_cost:
			info_text += "[color=lime]✓ READY TO PURCHASE[/color]"
		else:
			var needed = upgrade_cost - current_state.get("money", 0)
			info_text += "[color=red]✗ NEED %s MORE[/color]" % GameConfig.format_money(needed)

	info_label.text = info_text

func _on_dynamic_action_pressed(action_id: String, action_name: String):
	"""Handle dynamic action button press"""
	log_message("[color=cyan]Selecting action: %s[/color]" % action_name)

	# Check if this is a submenu action
	var action = _get_action_by_id(action_id)
	if action.get("is_submenu", false):
		# Open appropriate submenu dialog instead of queuing
		if action_id == "hire_staff":
			_show_hiring_submenu()
		elif action_id == "fundraise":
			_show_fundraising_submenu()
		elif action_id == "publicity":
			_show_publicity_submenu()
		elif action_id == "strategic":
			_show_strategic_submenu()
		elif action_id == "travel":
			_show_travel_submenu()
		elif action_id == "operations":
			_show_operations_submenu()
		elif action_id == "financing":
			_show_financing_submenu()
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

	# Track queued action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

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
	"""#622 L10 delegator — keeps the one-arg call shape the dialog builders use;
	the chrome is SubmenuChrome.add_close_affordance with MainUI's close routine."""
	SubmenuChrome.add_close_affordance(dialog, _close_active_submenu)

func _close_active_submenu() -> void:
	"""Close the active submenu dialog (shared by [X] click and ESC)."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
	active_dialog = null
	active_dialog_buttons = []


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
	log_message("[color=gray][debug] doom %+.0f → %.1f%%[/color]" % [delta, st.doom])

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
	header.text = "DOOM TREND — FULL HISTORY"
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
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _calculate_queued_costs() -> Dictionary:
	"""Calculate total costs of all queued actions for turn preview"""
	var total_costs: Dictionary = {}

	for queued_action in queued_actions:
		var action_id = queued_action.get("id", "")
		var action_def = _get_action_by_id(action_id)
		var costs = action_def.get("costs", {})

		for resource in costs.keys():
			if resource == "action_points":
				continue  # AP is already tracked separately
			if not total_costs.has(resource):
				total_costs[resource] = 0
			total_costs[resource] += costs[resource]

	return total_costs

func _show_hiring_submenu():
	"""Show popup dialog with candidate pool - shows actual available candidates"""
	print("[MainUI] === HIRING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(450, 400)
	dialog.size = Vector2(450, 400)
	# Position to the right of the left panel (icon stack)
	dialog.position = Vector2(90, 60)  # Just right of the 80px wide left panel
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 8)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "CANDIDATE POOL"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	main_vbox.add_child(header)

	# Get current state and candidate pool
	var current_state = game_manager.get_game_state()
	var candidate_pool = current_state.get("candidate_pool", [])

	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["1", "2", "3", "4", "5", "6"]

	if candidate_pool.size() == 0:
		# No candidates available
		var empty_label = Label.new()
		empty_label.text = "No candidates available.\nNew candidates arrive each turn."
		empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		empty_label.add_theme_font_size_override("font_size", 12)
		empty_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		main_vbox.add_child(empty_label)
	else:
		# Create scrollable list for candidates
		var scroll = ScrollContainer.new()
		scroll.custom_minimum_size = Vector2(0, 280)
		scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		main_vbox.add_child(scroll)

		var candidate_list = VBoxContainer.new()
		candidate_list.add_theme_constant_override("separation", 6)
		scroll.add_child(candidate_list)

		# Specialization colors
		var spec_colors = {
			"safety": Color(0.3, 0.8, 0.3),
			"capabilities": Color(0.8, 0.3, 0.3),
			"interpretability": Color(0.7, 0.3, 0.8),
			"alignment": Color(0.3, 0.7, 0.8)
		}

		var button_index = 0
		for candidate in candidate_pool:
			var candidate_panel = PanelContainer.new()
			candidate_panel.custom_minimum_size = Vector2(0, 50)

			var hbox = HBoxContainer.new()
			hbox.add_theme_constant_override("separation", 8)
			candidate_panel.add_child(hbox)

			# Keyboard shortcut indicator
			var key_label = Label.new()
			key_label.text = "[%s]" % dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
			key_label.add_theme_font_size_override("font_size", 10)
			key_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
			key_label.custom_minimum_size = Vector2(25, 0)
			hbox.add_child(key_label)

			# Specialization color indicator
			var spec = candidate.get("specialization", "safety")
			var indicator = Label.new()
			indicator.text = "●"
			indicator.add_theme_color_override("font_color", spec_colors.get(spec, Color.WHITE))
			indicator.add_theme_font_size_override("font_size", 14)
			hbox.add_child(indicator)

			# Candidate info VBox
			var info_vbox = VBoxContainer.new()
			info_vbox.add_theme_constant_override("separation", 2)
			info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			hbox.add_child(info_vbox)

			# Name and specialization
			var name_label = Label.new()
			var spec_name = spec.capitalize()
			name_label.text = "%s - %s" % [candidate.get("name", "Unknown"), spec_name]
			name_label.add_theme_font_size_override("font_size", 11)
			info_vbox.add_child(name_label)

			# Stats line: Skill, Salary, Traits
			var stats_label = Label.new()
			var skill = candidate.get("skill_level", 5)
			var salary = candidate.get("current_salary", 60000)
			var traits = candidate.get("traits", [])
			var trait_text = ""
			if traits.size() > 0:
				var trait_names = []
				for trait_id in traits:
					# Get display name for trait
					if Researcher.POSITIVE_TRAITS.has(trait_id):
						trait_names.append(Researcher.POSITIVE_TRAITS[trait_id]["name"])
					elif Researcher.NEGATIVE_TRAITS.has(trait_id):
						trait_names.append(Researcher.NEGATIVE_TRAITS[trait_id]["name"])
					else:
						trait_names.append(trait_id.capitalize())
				trait_text = " [%s]" % ", ".join(trait_names)

			stats_label.text = "Skill %d | %s/yr%s" % [skill, GameConfig.format_money(salary), trait_text]
			stats_label.add_theme_font_size_override("font_size", 9)
			stats_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
			info_vbox.add_child(stats_label)

			# Hire button
			var hire_btn = Button.new()
			hire_btn.text = "Hire"
			hire_btn.custom_minimum_size = Vector2(50, 30)
			hire_btn.focus_mode = Control.FOCUS_NONE

			# Get standard hiring cost from action definitions
			var action_id = "hire_%s_researcher" % spec
			var hire_cost = 60000  # Default
			var hiring_options = GameActions.get_hiring_options()
			for option in hiring_options:
				if option.get("id") == action_id:
					hire_cost = option.get("costs", {}).get("money", 60000)
					break

			var can_afford = current_state.get("money", 0) >= hire_cost and current_state.get("action_points", 0) >= 1

			if not can_afford:
				hire_btn.disabled = true
				hire_btn.modulate = Color(0.5, 0.5, 0.5)

			hire_btn.tooltip_text = "Hire for %s + 1 AP" % GameConfig.format_money(hire_cost)

			# Store candidate reference for hire action
			var candidate_ref = candidate
			hire_btn.pressed.connect(func(): _on_candidate_hired(candidate_ref, dialog))

			hbox.add_child(hire_btn)
			buttons.append(hire_btn)

			candidate_list.add_child(candidate_panel)
			button_index += 1

	# Pool status
	var status_label = Label.new()
	status_label.text = "Pool: %d/6 candidates | New arrivals each turn" % candidate_pool.size()
	status_label.add_theme_font_size_override("font_size", 10)
	status_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(status_label)

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Hiring submenu opened with %d candidates" % candidate_pool.size())

	# Add dialog to TabManager (parent) so it overlays everything without shifting layout
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === HIRING SUBMENU SETUP COMPLETE ===")

func _on_candidate_hired(candidate: Dictionary, dialog: Control):
	"""Handle hiring a specific candidate from the pool.
	#622 L10: routed through GameManager.queue_candidate_hire — the engine owns the
	pending_hire_queue/candidate-pool writes and select_action owns affordability
	(its error_occurred signal logs the reason), so the old UI pre-checks are gone."""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Get the candidate's specialization to determine which hire action to use
	var spec = candidate.get("specialization", "safety")
	var action_id = "hire_%s_researcher" % spec
	var candidate_name = candidate.get("name", "Unknown")

	if not game_manager.queue_candidate_hire(candidate_name, spec):
		return  # rejected — error_occurred already logged the reason

	log_message("[color=cyan]Hiring: %s (%s)[/color]" % [candidate_name, spec.capitalize()])

	# Mirror the engine-accepted action in the local queue display
	queued_actions.append({"id": action_id, "name": "Hire " + candidate_name})
	update_queued_actions_display()

func _on_hiring_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle hiring submenu selection"""
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Hiring: %s[/color]" % action_name)

	# Queue the actual hiring action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	game_manager.select_action(action_id)

func _show_fundraising_submenu():
	"""Show popup dialog with fundraising options with keyboard support - icon grid layout"""
	print("[MainUI] === FUNDRAISING SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	# Position to the right of the left panel (icon stack) - same as hiring submenu
	dialog.position = Vector2(90, 80)  # Just right of the 80px wide left panel
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Get fundraising options
	var funding_options = GameActions.get_fundraising_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons (same layout as hiring submenu)
	var grid = GridContainer.new()
	grid.columns = 3  # 3 icons per row
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in funding_options:
		var fund_id = option.get("id", "")
		var fund_name = option.get("name", "")
		var fund_desc = option.get("description", "")
		var fund_costs = option.get("costs", {})
		var fund_gains = option.get("gains", {})

		# Create VBox for icon + label (same as hiring submenu)
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(100, 80)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(fund_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if fund_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % fund_costs.get("action_points")
		if fund_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % fund_costs.get("reputation")
		if fund_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % fund_costs.get("papers")

		# Format gains for tooltip
		var gain_text = ""
		if fund_gains.has("money_min") and fund_gains.has("money_max"):
			gain_text = "%s-%s" % [GameConfig.format_money(fund_gains.get("money_min")), GameConfig.format_money(fund_gains.get("money_max"))]
		elif fund_gains.has("money"):
			gain_text = GameConfig.format_money(fund_gains.get("money"))

		# Check affordability
		var can_afford = true
		for resource in fund_costs.keys():
			if current_state.get(resource, 0) < fund_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s\nGains: %s" % [fund_name, fund_desc, cost_text if cost_text != "" else "Free", gain_text]

		# Connect button
		btn.pressed.connect(func(): _on_fundraising_option_selected(fund_id, fund_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon (shortened names)
		var name_label = Label.new()
		# Shorten common suffixes for cleaner display
		var short_name = fund_name.replace(" Funding", "").replace("Publish ", "")
		name_label.text = short_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "Costs vary: 0-2 Papers, 0-20 Rep"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state for keyboard handling in MainUI._input()
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Fundraising submenu opened, tracked %d buttons" % buttons.size())
	for i in range(buttons.size()):
		print("[MainUI]   Button %d: %s" % [i, buttons[i].text])

	# Add dialog to TabManager (parent) so it overlays everything without shifting layout
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === FUNDRAISING SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Active dialog: %s, Buttons: %d" % [active_dialog != null, active_dialog_buttons.size()])
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_fundraising_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle fundraising submenu selection"""
	print("[MainUI] Fundraising option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Fundraising: %s[/color]" % action_name)

	# Queue the actual fundraising action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

func _show_financing_submenu():
	"""BL-1: the Liability Ledger financing menu (ADR-0003) - lists the ledger trades
	plus a button that opens the full switchable ledger screen."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(440, 330)
	dialog.size = Vector2(440, 330)
	dialog.position = Vector2(90, 80)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 6)
	margin.add_child(main_vbox)

	var title = Label.new()
	title.text = "FINANCING - every fix is a loan"
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", Color(0.85, 0.78, 0.55))
	main_vbox.add_child(title)

	var current_state = game_manager.get_game_state()
	var buttons = []
	var key_labels = ["Q", "W", "E", "R"]
	var idx = 0
	for option in GameActions.get_financing_options():
		var opt_id = option.get("id", "")
		var opt_name = option.get("name", "")
		var opt_costs = option.get("costs", {})
		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE
		btn.custom_minimum_size = Vector2(0, 44)
		var key = key_labels[idx] if idx < key_labels.size() else ""
		var cost_bits = []
		if opt_costs.get("action_points", 0) > 0:
			cost_bits.append("%d AP" % opt_costs["action_points"])
		if opt_costs.get("money", 0) > 0:
			cost_bits.append(GameConfig.format_money(opt_costs["money"]))
		var cost_txt = (" (%s)" % ", ".join(cost_bits)) if cost_bits.size() > 0 else ""
		btn.text = "[%s]  %s%s" % [key, opt_name, cost_txt]
		btn.tooltip_text = option.get("description", "")
		var can_afford = true
		for res in opt_costs.keys():
			if res == "action_points":
				continue
			if current_state.get(res, 0) < opt_costs[res]:
				can_afford = false
		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)
		btn.pressed.connect(func(): _on_financing_option_selected(opt_id, opt_name, dialog))
		main_vbox.add_child(btn)
		buttons.append(btn)
		idx += 1

	var view_btn = Button.new()
	view_btn.focus_mode = Control.FOCUS_NONE
	view_btn.custom_minimum_size = Vector2(0, 34)
	view_btn.text = "View Ledger  >>"
	view_btn.add_theme_color_override("font_color", Color(0.7, 0.85, 0.9))
	view_btn.pressed.connect(func(): _show_ledger_screen())
	main_vbox.add_child(view_btn)

	active_dialog = dialog
	active_dialog_buttons = buttons
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _on_financing_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Queue a ledger trade (mirrors fundraising selection)."""
	dialog.queue_free()
	active_dialog = null
	active_dialog_buttons = []

	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()
	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return
	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return
	log_message("[color=cyan]Financing: %s[/color]" % action_name)
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()
	game_manager.select_action(action_id)

func _show_ledger_screen():
	"""BL-1/#601: open the full Liability Ledger screen. #622 L10: the panel itself is
	built by LedgerScreen; this stays the single entry point (L key, summary click,
	financing submenu, dev overlay) and owns the active_dialog bookkeeping."""
	if active_dialog != null and is_instance_valid(active_dialog):
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	var ledger = game_manager.state.ledger if (game_manager and game_manager.state) else null
	var dialog: Panel = ledger_screen.build_screen(ledger, get_viewport().get_visible_rect().size)

	active_dialog = dialog
	active_dialog_buttons = []
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false
	_decorate_active_submenu()

func _show_publicity_submenu():
	"""Show popup dialog with publicity/influence options with keyboard support - icon grid layout"""
	print("[MainUI] === PUBLICITY SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	# Position to the right of the left panel (icon stack)
	dialog.position = Vector2(90, 80)  # Just right of the 80px wide left panel
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Get publicity options
	var publicity_options = GameActions.get_publicity_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons (same layout as other submenus)
	var grid = GridContainer.new()
	grid.columns = 3  # 3 icons per row
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in publicity_options:
		var pub_id = option.get("id", "")
		var pub_name = option.get("name", "")
		var pub_desc = option.get("description", "")
		var pub_costs = option.get("costs", {})

		# Create VBox for icon + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(100, 80)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(pub_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if pub_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % pub_costs.get("action_points")
		if pub_costs.get("money", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += GameConfig.format_money(pub_costs.get("money"))
		if pub_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % pub_costs.get("reputation")
		if pub_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % pub_costs.get("papers")

		# Check affordability
		var can_afford = true
		for resource in pub_costs.keys():
			if current_state.get(resource, 0) < pub_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [pub_name, pub_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_publicity_option_selected(pub_id, pub_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon (shortened names)
		var name_label = Label.new()
		var short_name = pub_name.replace(" Campaign", "").replace("Open Source ", "")
		name_label.text = short_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "Build influence and public awareness"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state for keyboard handling
	print("[MainUI] Setting active_dialog and active_dialog_buttons...")
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] active_dialog is now: %s" % (active_dialog != null))
	print("[MainUI] Publicity submenu opened, tracked %d buttons" % buttons.size())
	for i in range(buttons.size()):
		print("[MainUI]   Button %d: %s" % [i, buttons[i].text])

	# Add dialog to TabManager as overlay
	print("[MainUI] Adding dialog to TabManager as overlay...")
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false
	print("[MainUI] Dialog added and made visible: %s" % dialog.visible)

	# Wait one frame for dialog to be ready
	print("[MainUI] Waiting one frame...")
	await get_tree().process_frame
	print("[MainUI] Frame passed, dialog still visible: %s" % dialog.visible)
	print("[MainUI] === PUBLICITY SUBMENU SETUP COMPLETE ===")
	print("[MainUI] Active dialog: %s, Buttons: %d" % [active_dialog != null, active_dialog_buttons.size()])
	print("[MainUI] Ready for keyboard input via MainUI._input()")

func _on_publicity_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle publicity submenu selection"""
	print("[MainUI] Publicity option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Publicity: %s[/color]" % action_name)

	# Queue the actual publicity action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

func _show_strategic_unlock_fanfare() -> void:
	"""#578: Civ-style fade-up reveal when Strategic Moves first unlocks, instead of a button
	silently appearing. Text-only for now; the image slot (arg 3) takes a hero banner from
	art_prompts/hero_banners.yaml once those are generated."""
	log_message("[color=gold]The board convenes: Strategic Moves are now available.[/color]")
	FanfarePopup.show_fanfare(
		"STRATEGIC MOVES UNLOCKED",
		"The council of elders has deemed your standing sufficient. High-stakes plays now open to you — bold gambits that can bend the odds, each leaving its mark on the ledger of history. Wield them wisely.",
		"",  # hero banner image slot — art_prompts/hero_banners.yaml drops in here later
		get_tree().root)


func _show_strategic_submenu():
	"""Show popup dialog with strategic/high-stakes options with keyboard support - icon grid layout"""
	print("[MainUI] === STRATEGIC SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(420, 350)
	dialog.size = Vector2(420, 350)
	dialog.position = Vector2(90, 80)
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Get strategic options
	var strategic_options = GameActions.get_strategic_options()
	var current_state = game_manager.get_game_state()

	# Create grid for icon buttons
	var grid = GridContainer.new()
	grid.columns = 2  # 2 icons per row for strategic (fewer options, larger display)
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []
	var dialog_key_labels = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]

	for option in strategic_options:
		var strat_id = option.get("id", "")
		var strat_name = option.get("name", "")
		var strat_desc = option.get("description", "")
		var strat_costs = option.get("costs", {})

		# Create VBox for icon + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create icon button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(120, 90)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(strat_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint as text
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if strat_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % strat_costs.get("action_points")
		if strat_costs.get("money", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += GameConfig.format_money(strat_costs.get("money"))
		if strat_costs.get("reputation", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Rep" % strat_costs.get("reputation")
		if strat_costs.get("papers", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Papers" % strat_costs.get("papers")

		# Check affordability
		var can_afford = true
		for resource in strat_costs.keys():
			if current_state.get(resource, 0) < strat_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip with full details
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [strat_name, strat_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_strategic_option_selected(strat_id, strat_name, dialog))

		item_vbox.add_child(btn)

		# Add label below icon
		var name_label = Label.new()
		name_label.text = strat_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Add summary at bottom
	var summary_label = Label.new()
	summary_label.text = "High-stakes moves - use wisely!"
	summary_label.add_theme_font_size_override("font_size", 11)
	summary_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.3))
	summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	main_vbox.add_child(summary_label)

	# Store dialog state
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Strategic submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to TabManager as overlay
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

	await get_tree().process_frame
	print("[MainUI] === STRATEGIC SUBMENU SETUP COMPLETE ===")

func _on_strategic_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle strategic submenu selection"""
	print("[MainUI] Strategic option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue (#456)
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Strategic: %s[/color]" % action_name)

	# Queue the actual strategic action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

# === TRAVEL & CONFERENCES SUBMENU (Issue #468) ===

func _show_travel_submenu():
	"""Show popup dialog with travel/conference options - Issue #468"""
	print("[MainUI] === TRAVEL SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(500, 450)
	dialog.size = Vector2(500, 450)
	dialog.position = Vector2(90, 60)
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 10)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "TRAVEL & CONFERENCES"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.3, 0.7, 1.0))
	main_vbox.add_child(header)

	# Get current state and data
	var current_state = game_manager.get_game_state()
	var current_date = current_state.get("calendar", {})
	var current_month = current_date.get("month", 7)
	var paper_submissions = current_state.get("paper_submissions", [])

	# --- SECTION 1: Actions ---
	var actions_header = Label.new()
	actions_header.text = "Actions"
	actions_header.add_theme_font_size_override("font_size", 12)
	actions_header.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
	main_vbox.add_child(actions_header)

	var travel_options = GameActions.get_travel_options()
	var button_index = 0
	var buttons = []
	var dialog_key_labels = ["1", "2", "3"]

	var actions_grid = GridContainer.new()
	actions_grid.columns = 3
	actions_grid.add_theme_constant_override("h_separation", 8)
	actions_grid.add_theme_constant_override("v_separation", 8)
	main_vbox.add_child(actions_grid)

	for option in travel_options:
		var travel_id = option.get("id", "")
		var travel_name = option.get("name", "")
		var travel_desc = option.get("description", "")
		var travel_costs = option.get("costs", {})
		var is_stub = option.get("is_stub", false)

		# Create VBox for button + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(140, 70)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon
		var icon_texture = IconLoader.get_action_icon(travel_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if travel_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % travel_costs.get("action_points")
		if travel_costs.get("research", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += "%d Research" % travel_costs.get("research")

		# Check affordability
		var can_afford = true
		if is_stub:
			can_afford = false
		else:
			for resource in travel_costs.keys():
				var current_val = current_state.get(resource, 0)
				if resource == "action_points":
					current_val = current_state.get("available_ap", 0)
				if current_val < travel_costs[resource]:
					can_afford = false
					break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [travel_name, travel_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_travel_option_selected(travel_id, travel_name, dialog))

		item_vbox.add_child(btn)

		# Add label below
		var name_label = Label.new()
		name_label.text = travel_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		actions_grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# --- SECTION 2: Paper Status ---
	var papers_header = Label.new()
	papers_header.text = "Your Papers"
	papers_header.add_theme_font_size_override("font_size", 12)
	papers_header.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
	main_vbox.add_child(papers_header)

	var papers_scroll = ScrollContainer.new()
	papers_scroll.custom_minimum_size = Vector2(0, 100)
	main_vbox.add_child(papers_scroll)

	var papers_vbox = VBoxContainer.new()
	papers_vbox.add_theme_constant_override("separation", 4)
	papers_scroll.add_child(papers_vbox)

	if paper_submissions.size() == 0:
		var no_papers = Label.new()
		no_papers.text = "No papers submitted yet"
		no_papers.add_theme_font_size_override("font_size", 10)
		no_papers.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
		papers_vbox.add_child(no_papers)
	else:
		for paper in paper_submissions:
			var paper_label = RichTextLabel.new()
			paper_label.bbcode_enabled = true
			paper_label.fit_content = true
			paper_label.custom_minimum_size = Vector2(0, 20)
			var status_color = "[color=gray]"
			match paper.get("status", 0):
				1:  # UNDER_REVIEW
					status_color = "[color=yellow]"
				2:  # ACCEPTED
					status_color = "[color=lime]"
				3:  # REJECTED
					status_color = "[color=red]"
				4:  # PRESENTED
					status_color = "[color=cyan]"
			paper_label.text = "%s%s[/color] - %s (%s)" % [
				status_color,
				paper.get("status_text", "Unknown"),
				paper.get("title", "Untitled"),
				paper.get("target_conference_id", "???")
			]
			paper_label.add_theme_font_size_override("normal_font_size", 10)
			papers_vbox.add_child(paper_label)

	# --- SECTION 3: Upcoming Conferences ---
	var conf_header = Label.new()
	conf_header.text = "Upcoming Conferences"
	conf_header.add_theme_font_size_override("font_size", 12)
	conf_header.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
	main_vbox.add_child(conf_header)

	var conf_scroll = ScrollContainer.new()
	conf_scroll.custom_minimum_size = Vector2(0, 80)
	main_vbox.add_child(conf_scroll)

	var conf_vbox = VBoxContainer.new()
	conf_vbox.add_theme_constant_override("separation", 4)
	conf_scroll.add_child(conf_vbox)

	# Show next 3-4 conferences by month
	var all_conferences = Conferences.get_all_conferences()
	var sorted_conferences = []
	for conf in all_conferences:
		if conf.month == 0:  # Rolling admission
			sorted_conferences.append({"conf": conf, "sort_month": 13})  # Show at end
		else:
			var months_until = conf.month - current_month
			if months_until <= 0:
				months_until += 12
			sorted_conferences.append({"conf": conf, "sort_month": months_until})

	sorted_conferences.sort_custom(func(a, b): return a["sort_month"] < b["sort_month"])

	var shown = 0
	for entry in sorted_conferences:
		if shown >= 4:
			break
		var conf = entry["conf"]
		var conf_label = RichTextLabel.new()
		conf_label.bbcode_enabled = true
		conf_label.fit_content = true
		conf_label.scroll_active = false
		var month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		var month_str = month_names[conf.month - 1] if conf.month > 0 else "Rolling"
		var tier_color = "[color=gold]" if conf.tier == 0 else ("[color=silver]" if conf.tier == 1 else "[color=cyan]")
		conf_label.text = "%s%s[/color] (%s) - %s | Prestige: %.0f%%" % [
			tier_color,
			conf.name,
			month_str,
			conf.description.substr(0, 40) + "..." if conf.description.length() > 40 else conf.description,
			conf.prestige * 100
		]
		conf_label.add_theme_font_size_override("normal_font_size", 9)
		conf_vbox.add_child(conf_label)
		shown += 1

	# Store dialog state
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Travel submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to TabManager as overlay
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

	await get_tree().process_frame
	print("[MainUI] === TRAVEL SUBMENU SETUP COMPLETE ===")

func _on_travel_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle travel submenu selection"""
	print("[MainUI] Travel option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Handle stub action
	if action_id == "send_delegation":
		log_message("[color=yellow][Issue #411] Delegation system coming soon![/color]")
		return

	# For submit_paper and attend_conference, show dedicated dialogs
	if action_id == "submit_paper":
		_show_paper_submission_dialog()
		return
	elif action_id == "attend_conference":
		_show_conference_attendance_dialog()
		return

func _show_paper_submission_dialog():
	"""Show dialog for submitting a paper to a conference"""
	print("[MainUI] === PAPER SUBMISSION DIALOG ===")

	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(450, 400)
	dialog.size = Vector2(450, 400)
	dialog.position = Vector2(90, 60)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 10)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "SUBMIT PAPER"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.3, 0.7, 1.0))
	main_vbox.add_child(header)

	var current_state = game_manager.get_game_state()
	var researchers = current_state.get("researchers", [])
	var current_research = current_state.get("research", 0)

	# Conference selection
	var conf_label = Label.new()
	conf_label.text = "Target Conference:"
	main_vbox.add_child(conf_label)

	var conf_dropdown = OptionButton.new()
	var all_conferences = Conferences.get_all_conferences()
	for conf in all_conferences:
		conf_dropdown.add_item("%s (Prestige: %.0f%%)" % [conf.name, conf.prestige * 100])
		conf_dropdown.set_item_metadata(conf_dropdown.item_count - 1, conf.id)
	main_vbox.add_child(conf_dropdown)

	# Topic selection
	var topic_label = Label.new()
	topic_label.text = "Paper Topic:"
	main_vbox.add_child(topic_label)

	var topic_dropdown = OptionButton.new()
	topic_dropdown.add_item("Safety")
	topic_dropdown.add_item("Alignment")
	topic_dropdown.add_item("Interpretability")
	topic_dropdown.add_item("Capabilities")
	topic_dropdown.add_item("Governance")
	main_vbox.add_child(topic_dropdown)

	# Research investment
	var research_label = Label.new()
	research_label.text = "Research to Invest (have %.0f):" % current_research
	main_vbox.add_child(research_label)

	var research_slider = HSlider.new()
	research_slider.min_value = 15
	research_slider.max_value = min(100, current_research) if current_research >= 15 else 15
	research_slider.value = min(30, current_research) if current_research >= 15 else 15
	research_slider.step = 5
	main_vbox.add_child(research_slider)

	var research_value_label = Label.new()
	research_value_label.text = "%.0f research points" % research_slider.value
	main_vbox.add_child(research_value_label)

	research_slider.value_changed.connect(func(val): research_value_label.text = "%.0f research points" % val)

	# Quality preview (updates based on slider)
	var quality_label = Label.new()
	quality_label.text = "Est. Quality: ~%.0f%%" % (research_slider.value / 100.0 * 50)
	main_vbox.add_child(quality_label)

	# Buttons
	var button_hbox = HBoxContainer.new()
	button_hbox.add_theme_constant_override("separation", 10)
	main_vbox.add_child(button_hbox)

	var cancel_btn = Button.new()
	cancel_btn.text = "Cancel"
	cancel_btn.pressed.connect(func(): dialog.queue_free(); active_dialog = null)
	button_hbox.add_child(cancel_btn)

	var submit_btn = Button.new()
	submit_btn.text = "Submit Paper (1 AP)"
	submit_btn.disabled = current_research < 15
	submit_btn.pressed.connect(func():
		var conf_id = conf_dropdown.get_item_metadata(conf_dropdown.selected)
		var topic = topic_dropdown.selected
		var research_amount = research_slider.value
		# Get first researcher as lead (simplified)
		var lead = null
		if researchers.size() > 0:
			lead = Researcher.new()
			lead.researcher_name = researchers[0].get("researcher_name", "Anonymous")
			lead.skill_level = researchers[0].get("skill_level", 3)
		var result = GameActions.submit_paper_to_conference(game_manager.state, conf_id, topic, research_amount, lead)
		log_message("[color=cyan]%s[/color]" % result.get("message", "Paper submitted"))
		dialog.queue_free()
		active_dialog = null
	)
	button_hbox.add_child(submit_btn)

	_add_submenu_close_affordance(dialog)  # X + ESC hint, consistent with action submenus (#510)
	active_dialog = dialog
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _show_conference_attendance_dialog():
	"""Show dialog for attending a conference"""
	print("[MainUI] === CONFERENCE ATTENDANCE DIALOG ===")

	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(450, 350)
	dialog.size = Vector2(450, 350)
	dialog.position = Vector2(90, 60)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 10)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "ATTEND CONFERENCE"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.3, 0.7, 1.0))
	main_vbox.add_child(header)

	var current_state = game_manager.get_game_state()
	var current_money = current_state.get("money", 0)
	var paper_submissions = current_state.get("paper_submissions", [])
	var attended = current_state.get("attended_conferences", [])

	# Conference selection
	var conf_label = Label.new()
	conf_label.text = "Select Conference:"
	main_vbox.add_child(conf_label)

	var conf_dropdown = OptionButton.new()
	var all_conferences = Conferences.get_all_conferences()
	for conf in all_conferences:
		var travel_cost = conf.get_travel_cost()
		var has_paper = false
		for paper in paper_submissions:
			if paper.get("target_conference_id") == conf.id and paper.get("status") == 2:  # ACCEPTED
				has_paper = true
				break
		var already_attended = attended.has(conf.id)
		var status = ""
		if already_attended:
			status = " [ATTENDED]"
		elif has_paper:
			status = " [PAPER ACCEPTED!]"

		conf_dropdown.add_item("%s - %s%s" % [conf.name, GameConfig.format_money(travel_cost.total), status])
		conf_dropdown.set_item_metadata(conf_dropdown.item_count - 1, conf.id)
		if already_attended:
			conf_dropdown.set_item_disabled(conf_dropdown.item_count - 1, true)
	main_vbox.add_child(conf_dropdown)

	# Cost breakdown (updates when selection changes)
	var cost_label = Label.new()
	cost_label.text = "Select a conference to see costs"
	main_vbox.add_child(cost_label)

	conf_dropdown.item_selected.connect(func(idx):
		var conf_id = conf_dropdown.get_item_metadata(idx)
		var conf = Conferences.get_conference_by_id(conf_id)
		if conf:
			var travel = conf.get_travel_cost()
			cost_label.text = "Flights: %s | Hotel: %s | Registration: %s\nTotal: %s + 2 AP" % [
				GameConfig.format_money(travel.flights),
				GameConfig.format_money(travel.accommodation),
				GameConfig.format_money(travel.registration),
				GameConfig.format_money(travel.total)
			]
	)

	# Trigger initial update
	if conf_dropdown.item_count > 0:
		conf_dropdown.emit_signal("item_selected", 0)

	# Buttons
	var button_hbox = HBoxContainer.new()
	button_hbox.add_theme_constant_override("separation", 10)
	main_vbox.add_child(button_hbox)

	var cancel_btn = Button.new()
	cancel_btn.text = "Cancel"
	cancel_btn.pressed.connect(func(): dialog.queue_free(); active_dialog = null)
	button_hbox.add_child(cancel_btn)

	var attend_btn = Button.new()
	attend_btn.text = "Attend (2 AP)"
	attend_btn.pressed.connect(func():
		var conf_id = conf_dropdown.get_item_metadata(conf_dropdown.selected)
		# Issue #469: Apply jet lag to first researcher (economy class default)
		# TODO: Multi-stage booking with traveler/class selection
		var traveler = game_manager.state.researchers[0] if game_manager.state.researchers.size() > 0 else null
		var result = GameActions.attend_conference_action(game_manager.state, conf_id, "economy", traveler)
		if result.get("success", false):
			log_message("[color=lime]%s[/color]" % result.get("message", "Attended conference"))
		else:
			log_message("[color=red]%s[/color]" % result.get("message", "Failed to attend"))
		dialog.queue_free()
		active_dialog = null
	)
	button_hbox.add_child(attend_btn)

	_add_submenu_close_affordance(dialog)  # X + ESC hint, consistent with action submenus (#510)
	active_dialog = dialog
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func update_queued_actions_display():
	"""Update the visual queue display and message log"""
	# Clear existing queue items (except hint label)
	for child in queue_container.get_children():
		if child != queue_hint:
			child.queue_free()

	if queued_actions.size() > 0:
		# Hide hint, show queue items
		queue_hint.visible = false

		# Create visual queue items
		for action in queued_actions:
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
			remove_btn.text = "✕ Remove"
			remove_btn.custom_minimum_size = Vector2(90, 24)
			remove_btn.add_theme_font_size_override("font_size", 9)

			# Capture action_id in closure for the callback
			var captured_id = action_id
			var captured_name = action_name
			remove_btn.pressed.connect(func(): _remove_queued_action(captured_id, captured_name))

			vbox.add_child(remove_btn)

			queue_container.add_child(item)

		# Calculate and display turn preview (total costs from queued actions)
		var total_costs = _calculate_queued_costs()
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
		for action in queued_actions:
			action_names.append(action.get("name", "Unknown"))
		log_message("[color=lime]Queued actions (%d): %s[/color]" % [queued_actions.size(), ", ".join(action_names)])
	else:
		# Show hint, hide items
		queue_hint.visible = true
		log_message("[color=gray]No actions queued[/color]")

	# Update button states based on queue (case-insensitive phase check)
	var phase_upper = current_turn_phase.to_upper()
	if phase_upper == "ACTION_SELECTION":
		var queue_empty = queued_actions.size() == 0
		undo_last_button.disabled = queue_empty
		clear_queue_button.disabled = queue_empty
		end_turn_button.disabled = queue_empty
		print("[MainUI] Updated button states: queue_size=%d, buttons_disabled=%s" % [queued_actions.size(), queue_empty])

func _on_event_dialog_opened(dialog: Control, buttons: Array) -> void:
	"""EventDialog put its modal up (#622) — route MainUI keyboard shortcuts to it.
	The dialog carries the is_event_dialog meta, so ESC handling keeps refusing to
	close it (#452)."""
	active_dialog = dialog
	active_dialog_buttons = buttons

func _on_event_dialog_closed() -> void:
	"""EventDialog dismissed its modal — clear the keyboard-routing state (#622)."""
	active_dialog = null
	active_dialog_buttons = []

func _on_event_choice_selected(event: Dictionary, choice_id: String) -> void:
	"""Resolution stays signal-driven through game_manager.resolve_event (#622, L1 reuse)."""
	game_manager.resolve_event(event, choice_id)


func _on_action_hover(action: Dictionary, can_afford: bool, missing_resources: Array):
	"""Update info bar when hovering over an action and highlight affected resources"""
	var action_name = action.get("name", "Unknown")
	var action_desc = action.get("description", "")
	var action_costs = action.get("costs", {})

	# Build info text with enhanced formatting
	var info_text = "[b][color=cyan]%s[/color][/b] — %s" % [action_name, action_desc]

	# Add costs with icons/colors (always add line for consistent 2-line format)
	info_text += "\n[color=gray]├─[/color] "
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

		info_text += " • ".join(cost_parts)
	else:
		info_text += "[color=gray]No costs[/color]"

	# Show affordability with visual indicator
	info_text += "\n[color=gray]└─[/color] "
	if not can_afford:
		info_text += "[color=red]✗ CANNOT AFFORD[/color]"
		if missing_resources.size() > 0:
			info_text += " [color=gray](%s)[/color]" % missing_resources[0]
	else:
		info_text += "[color=lime]✓ READY TO USE[/color]"

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

func _show_operations_submenu():
	"""Show popup dialog with operations/maintenance options"""
	print("[MainUI] === OPERATIONS SUBMENU STARTING ===")

	# Close any existing dialog first
	if active_dialog != null and is_instance_valid(active_dialog):
		print("[MainUI] Closing existing dialog...")
		active_dialog.queue_free()
		active_dialog = null
		active_dialog_buttons = []

	# Use Panel - position to the right of the left panel buttons
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(350, 250)
	dialog.size = Vector2(350, 250)
	dialog.position = Vector2(90, 80)
	print("[MainUI] Created Panel, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container
	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 10)
	margin.add_child(main_vbox)

	# Header
	var header = Label.new()
	header.text = "OPERATIONS"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 14)
	header.add_theme_color_override("font_color", Color(0.6, 0.8, 0.6))
	main_vbox.add_child(header)

	# Get operations options
	var operations_options = GameActions.get_operations_options()
	var current_state = game_manager.get_game_state()

	# Create grid for option buttons
	var grid = GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	main_vbox.add_child(grid)

	var button_index = 0
	var buttons = []
	var dialog_key_labels = ["Q", "W", "E", "R"]

	for option in operations_options:
		var op_id = option.get("id", "")
		var op_name = option.get("name", "")
		var op_desc = option.get("description", "")
		var op_costs = option.get("costs", {})

		# Create VBox for button + label
		var item_vbox = VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		# Create button
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(140, 70)
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		# Add icon if available
		var icon_texture = IconLoader.get_action_icon(op_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		# Add keyboard hint
		var key_label = dialog_key_labels[button_index] if button_index < dialog_key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Format costs for tooltip
		var cost_text = ""
		if op_costs.get("action_points", 0) > 0:
			cost_text += "%d AP" % op_costs.get("action_points")
		if op_costs.get("money", 0) > 0:
			if cost_text != "":
				cost_text += ", "
			cost_text += GameConfig.format_money(op_costs.get("money"))

		# Check affordability
		var can_afford = true
		for resource in op_costs.keys():
			var current_val = current_state.get(resource, 0)
			if resource == "action_points":
				current_val = current_state.get("available_ap", 0)
			if current_val < op_costs[resource]:
				can_afford = false
				break

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [op_name, op_desc, cost_text if cost_text != "" else "Free"]

		# Connect button
		btn.pressed.connect(func(): _on_operations_option_selected(op_id, op_name, dialog))

		item_vbox.add_child(btn)

		# Add label below
		var name_label = Label.new()
		name_label.text = op_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Store dialog state
	active_dialog = dialog
	active_dialog_buttons = buttons
	print("[MainUI] Operations submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to TabManager as overlay
	tab_manager.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

	await get_tree().process_frame
	print("[MainUI] === OPERATIONS SUBMENU SETUP COMPLETE ===")

func _on_operations_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle operations submenu selection"""
	print("[MainUI] Operations option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	active_dialog = null
	active_dialog_buttons = []

	# Check if action can be afforded before adding to UI queue
	var action_def = _get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = game_manager.state.get_available_ap()

	if available_ap < ap_cost:
		log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return

	if not game_manager.state.can_afford(action_def.get("costs", {})):
		log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return

	log_message("[color=cyan]Operations: %s[/color]" % action_name)

	# Queue the action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

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

	# Queue the pass action
	queued_actions.append({"id": action_id, "name": action_name})
	update_queued_actions_display()

	print("[MainUI] Calling game_manager.select_action(%s)" % action_id)
	game_manager.select_action(action_id)

extends Node
class_name EventDialog
## Event dialog presenter -- extracted from main_ui.gd (#622, build lane L10).
##
## Owns the event queue + modal presentation (click blocker, forest-green panel,
## lettered choice buttons with affordability display). Deliberately signal-driven:
## choices flow OUT through choice_selected and MainUI routes them to
## game_manager.resolve_event, so the L1 turn-engine rewrite can reuse this
## presenter for mid-month response windows without touching MainUI internals.
##
## Keyboard routing stays in MainUI (its _input reads active_dialog /
## active_dialog_buttons, kept in sync via dialog_opened / dialog_closed).

## Player picked a choice; the host routes this to game_manager.resolve_event.
signal choice_selected(event: Dictionary, choice_id: String)
## A modal dialog (with its choice buttons) is now up -- host should route keys to it.
signal dialog_opened(dialog: Control, buttons: Array)
## The modal dialog was dismissed -- host should clear its key-routing state.
signal dialog_closed
## BBCode line for the host's message log.
signal message_logged(text: String)

## Callable returning the current game-state Dictionary (used for the
## affordability display on choice buttons). Set by the host before events arrive.
var state_provider: Callable

# Event queue for sequential presentation (FIX: multiple events in same turn)
var event_queue: Array[Dictionary] = []
var is_showing_event: bool = false

# Direction-b (playtest 2026-07-24): the dialog no longer closes on press. When a choice is
# pressed we keep these references so the host's resolution result (report_choice_result) can
# either close/advance (SUCCESS) or keep THIS dialog open with the reason (a rejected choice
# must never read as 'order accepted'). Only one event dialog shows at a time (is_showing_event
# gate), so single-slot instance state is safe.
var _pending_dialog: Control = null
var _pending_blocker: Control = null
var _pending_event: Dictionary = {}
var _pending_choice_id: String = ""
var _reason_label: Label = null

## #877: the dialog currently on screen. The presenter used to have NO handle on an
## externally-destroyed panel: click_blocker lived at the viewport root and was freed only by
## report_choice_result(success), and is_showing_event was only ever cleared on that same path.
## So a panel torn down any other way (a replacing modal, a scene teardown) stranded a
## full-screen MOUSE_FILTER_STOP blocker AND left is_showing_event stuck true -- every future
## event then queued forever behind a presenter that thought it was still busy. This handle +
## the tree_exited hook below make the teardown self-healing whoever performs it.
var _showing_dialog: Control = null

func present(event: Dictionary) -> void:
	"""Handle event trigger - queue event for sequential presentation"""
	print("[EventDialog] === EVENT TRIGGERED: %s ===" % event.get("name", "Unknown"))

	# Add to event queue
	event_queue.append(event)
	print("[EventDialog] Event queued. Queue size: %d" % event_queue.size())

	# If not currently showing an event, show this one immediately
	if not is_showing_event:
		_show_next_event()
	else:
		print("[EventDialog] Event added to queue, will show after current event resolves")

static func format_cost_summary(costs: Dictionary) -> String:
	"""Compact inline cost string for event option buttons, e.g. ' ($30,000, 2 Attention)' (#510).
	Cost-display sweep (2026-07-24): a costless option (the 'decline'/'ignore'/'acknowledge'
	free-out) now explicitly says ' (Free)' instead of showing nothing -- a blank cost read
	as ambiguous, not obviously safe-to-pick, next to options that DO cost something."""
	var parts: Array[String] = []
	for resource in costs.keys():
		var amount = costs[resource]
		if amount == null or float(amount) <= 0:
			continue  # a zero/negative-cost entry is not a real cost -- don't clutter the face
		if resource == "money":
			parts.append(GameConfig.format_money(amount))
		else:
			parts.append("%s %s" % [
				GameConfig.format_resource_amount(str(resource), amount),
				GameConfig.format_resource_name(str(resource))])
	if parts.is_empty():
		return " (Free)"
	return " (%s)" % ", ".join(parts)


static func window_attention_for_option(event: Dictionary, option: Dictionary) -> int:
	"""Founder Attention this window will charge for THIS option, for display. 0 when nothing
	is owed -- and 0 is also the honest answer whenever we cannot prove otherwise.

	A window levies an Attention price that lives on the EVENT, not on the option's costs
	(WindowResolver.attention_cost). The presenter is handed events from six emit sites and
	only the two window paths carry it, so this reads the display stamp that
	WindowResolver.present_for_dialog() leaves rather than re-deriving resolution policy --
	an un-stamped event (plan-phase legacy popup, the synthetic month review) claims nothing.

	Two options pay nothing and must not be surcharged: the free-out that resolves as IGNORE
	(stamped by the resolver), and an option whose own costs still carry `attention` -- that
	is an UN-stripped legacy event whose declared cost format_cost_summary already prints, so
	adding to it would bill the player twice on the label for one charge."""
	var cost := int(event.get(WindowResolver.DISPLAY_ATTENTION_KEY, 0))
	if cost <= 0:
		return 0
	var costs = option.get("costs", {})
	if costs is Dictionary and costs.has("attention"):
		return 0
	if String(option.get("id", "")) == String(event.get(WindowResolver.DISPLAY_FREE_OPTION_KEY, "")):
		return 0
	return cost


static func costs_with_window_attention(event: Dictionary, option: Dictionary) -> Dictionary:
	"""The option's costs as the player should SEE them: its own declared costs plus the
	window's Attention price folded in. One merged dict feeds both the button face and the
	tooltip, so the two can never disagree.

	Money-then-Attention ordering is preserved by appending: format_cost_summary iterates
	costs.keys() in insertion order, and core_events.json's header pins that order as load-
	bearing for the cost-summary label.

	NOT used for the affordability grey-out, deliberately. Window Attention is paid
	reserve-FIRST (WindowResolver.resolve_chosen_option -> pay_from_reserve, falling back to
	cannibalizing planned work), and the dialog's affordability loop reads state.attention,
	which is get_available_attention() = total - spent - RESERVED. After a month commits,
	GameManager reserves the whole remainder, so available is 0 while the reserve is full --
	gating on it would grey out every window button in the game."""
	var merged: Dictionary = {}
	var costs = option.get("costs", {})
	if costs is Dictionary:
		merged = costs.duplicate()
	var att := window_attention_for_option(event, option)
	if att > 0:
		merged["attention"] = att
	return merged


## Teal of the bottom bar's END TURN button (scenes/main.tscn:378). The month loop's two
## forward doors must look like siblings -- see is_navigation_popup below.
const PRIMARY_TEAL := Color(0.118, 0.765, 0.702, 1.0)


static func is_navigation_popup(event: Dictionary) -> bool:
	"""True when this popup is a DOOR, not a decision: exactly one option, costing nothing.

	B2/B3 (playtest 2026-08-01, [4:55]): the month review is a generic event, so its single
	'Begin planning August 2017' option was wearing crisis-option chrome -- the letter-menu
	prefix `[Q]` (an arbitrary index into dialog_key_labels) and the ` (Free)` cost suffix, a
	price tag on a door that was never for sale. Neither communicates anything when there is
	no choice to weigh, and the dark-gray option styling reads half-disabled next to the teal
	END TURN.

	Free-ness is decided by asking format_cost_summary what it WOULD have printed, so this
	predicate can never disagree with the chrome it suppresses."""
	var options = event.get("options", [])
	if not (options is Array) or options.size() != 1:
		return false
	var only = options[0]
	if not (only is Dictionary):
		return false
	return format_cost_summary(only.get("costs", {})) == " (Free)"

func _show_next_event() -> void:
	"""Show the next event in queue (sequential presentation)"""
	if event_queue.is_empty():
		print("[EventDialog] Event queue empty, no more events to show")
		is_showing_event = false
		return

	# Mark that we're showing an event
	is_showing_event = true

	# Get next event from queue
	var event = event_queue.pop_front()
	print("[EventDialog] === SHOWING EVENT: %s ===" % event.get("name", "Unknown"))
	print("[EventDialog] Remaining events in queue: %d" % event_queue.size())

	message_logged.emit("[color=gold]EVENT: %s[/color]" % event.get("name", "Unknown"))

	# Blurred blocker behind event dialog panel (Fix Issue #458 + #485)
	# Add to root (get_tree().root) to ensure it blocks ALL UI interactions
	var click_blocker := ColorRect.new()
	click_blocker.color = Color(0.0, 0.0, 0.0, 0.6)
	click_blocker.mouse_filter = Control.MOUSE_FILTER_STOP  # Block all mouse events
	click_blocker.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	click_blocker.z_index = 999  # Just below dialog but above all other UI
	click_blocker.z_as_relative = false  # Absolute z-index
	# Add to viewport root to cover entire screen and all UI
	get_tree().root.add_child(click_blocker)

	# Create event dialog - use Panel for consistent input handling
	var dialog = Panel.new()
	dialog.custom_minimum_size = Vector2(600, 450)
	dialog.size = Vector2(600, 450)
	# Center it manually
	dialog.position = Vector2(
		(get_viewport().get_visible_rect().size.x - 600) / 2,
		(get_viewport().get_visible_rect().size.y - 450) / 2
	)

	# Add forest green background for better visibility
	var panel_style = StyleBoxFlat.new()
	panel_style.bg_color = Color(0.15, 0.25, 0.15, 1.0)  # Dark forest green
	panel_style.border_width_left = 3
	panel_style.border_width_top = 3
	panel_style.border_width_right = 3
	panel_style.border_width_bottom = 3
	panel_style.border_color = Color(0.3, 0.5, 0.3, 1.0)  # Lighter green border
	panel_style.corner_radius_top_left = 8
	panel_style.corner_radius_top_right = 8
	panel_style.corner_radius_bottom_right = 8
	panel_style.corner_radius_bottom_left = 8
	dialog.add_theme_stylebox_override("panel", panel_style)

	print("[EventDialog] Created Panel for event, size: %s, position: %s" % [dialog.size, dialog.position])

	# Create main container. #630: anchor it to fill the fixed-size Panel (a Panel is
	# NOT a container, so children default to their content-driven minimum size at
	# (0,0)). Without this, a long title_label forces the VBox min-width past the
	# 600px panel and the wrapped body text spills over the right border. Anchoring
	# clamps the content width to the panel, giving the autowrap labels a real width
	# to wrap within (inner area = 600 - 2*15 = 570px).
	var margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox = VBoxContainer.new()
	margin.add_child(main_vbox)

	# Add title (#630: autowrap so a long event name wraps instead of forcing the
	# content wider than the panel).
	var title_label = Label.new()
	title_label.text = event.get("name", "Event")
	title_label.add_theme_font_size_override("font_size", 18)
	title_label.add_theme_color_override("font_color", Color.GOLD)
	title_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_vbox.add_child(title_label)

	# Add description label. #630: smart word-wrap + fill the container width so long
	# body text wraps to the panel's inner width instead of clipping past the margins.
	var desc_label = Label.new()
	desc_label.text = event.get("description", "An event has occurred!")
	desc_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	desc_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_vbox.add_child(desc_label)

	# Add spacing
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 20)
	main_vbox.add_child(spacer)

	# Create container for option buttons
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	main_vbox.add_child(vbox)

	# Failure-reason line (direction-b, playtest 2026-07-24). Hidden until an attempted choice
	# is REJECTED (e.g. can't afford the HANDLE). Shown in-place -- the dialog stays open so the
	# player can pick a different option (e.g. the free out). Without this the dialog closed on
	# the rejected click, which reads as 'order accepted' in this genre (the legibility bug).
	var reason_label = Label.new()
	reason_label.add_theme_color_override("font_color", Color(1.0, 0.55, 0.4))  # warm amber/red
	reason_label.add_theme_font_size_override("font_size", 14)
	reason_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	reason_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	reason_label.visible = false
	main_vbox.add_child(reason_label)
	_reason_label = reason_label

	# Add each option as a button
	var options = event.get("options", [])
	var current_state: Dictionary = state_provider.call() if state_provider.is_valid() else {}

	var button_index = 0
	var buttons = []  # Store buttons for keyboard access
	# #567: labels come from DialogKeys, the same table MainUI routes with. No local copy.

	# B2/B3: a one-costless-option popup is navigation, not deliberation. Its button drops the
	# letter-menu prefix and the "(Free)" price tag, hints the key the player actually reaches
	# for, and takes primary-action styling. The letter key still WORKS (MainUI's key map is
	# positional) -- it is only unadvertised.
	var is_navigation := is_navigation_popup(event)

	for option in options:
		var choice_id = option.get("id", "")
		var choice_text = option.get("text", "")
		var costs = option.get("costs", {})
		# What the player is SHOWN: the option's own costs plus the window's Attention price,
		# which is charged by WindowResolver and appears in no option's costs dict. `costs`
		# stays raw below -- see costs_with_window_attention on why the grey-out must not use
		# this (window Attention is paid reserve-first; the affordability pool is not).
		var shown_costs := costs_with_window_attention(event, option)

		var btn = Button.new()
		btn.focus_mode = Control.FOCUS_NONE  # Don't grab focus - let MainUI handle keys
		btn.mouse_filter = Control.MOUSE_FILTER_PASS  # Still allow mouse clicks

		# Add keyboard hint (LETTERS not numbers) + inline cost summary (#510)
		if is_navigation:
			btn.text = "%s   [SPACE]" % choice_text
			btn.custom_minimum_size = Vector2(520, 54)
			btn.add_theme_font_size_override("font_size", 16)
			btn.add_theme_color_override("font_color", PRIMARY_TEAL)
			btn.add_theme_color_override("font_hover_color", Color(1, 1, 1, 1))
		else:
			btn.text = "%s%s%s" % [DialogKeys.prefix_for(button_index), choice_text, format_cost_summary(shown_costs)]
			btn.custom_minimum_size = Vector2(500, 45)

		# Add button border for better definition
		var button_style = StyleBoxFlat.new()
		button_style.bg_color = Color(0.2, 0.2, 0.2, 1.0)  # Dark gray background
		button_style.border_width_left = 2
		button_style.border_width_top = 2
		button_style.border_width_right = 2
		button_style.border_width_bottom = 2
		button_style.border_color = Color(0.15, 0.15, 0.15, 1.0)  # Slightly darker border
		button_style.corner_radius_top_left = 4
		button_style.corner_radius_top_right = 4
		button_style.corner_radius_bottom_right = 4
		button_style.corner_radius_bottom_left = 4
		if is_navigation:
			# Primary action: teal-on-dark, teal border. Deliberately NOT a flat teal fill --
			# the label text sits on this panel and a saturated block would out-shout the
			# review it is meant to close.
			button_style.bg_color = Color(0.07, 0.20, 0.19, 1.0)
			button_style.border_color = PRIMARY_TEAL
		btn.add_theme_stylebox_override("normal", button_style)

		# Hover state
		var button_style_hover = button_style.duplicate()
		button_style_hover.bg_color = Color(0.3, 0.3, 0.3, 1.0)  # Lighter on hover
		if is_navigation:
			button_style_hover.bg_color = PRIMARY_TEAL
		btn.add_theme_stylebox_override("hover", button_style_hover)

		# Affordability DISPLAY (grey-out + tooltip). This is player information, not
		# enforcement -- the engine (turn_manager.resolve_event) remains the authority.
		var can_afford = true
		var missing_resources = []

		for resource in costs.keys():
			var cost = costs[resource]
			var available = 0

			# Special handling for attention - read the month plan, not a per-turn pool
			# Must match can_afford() logic in GameState:130
			if resource == "attention":
				available = current_state.get("attention", 0)
			else:
				available = current_state.get(resource, 0)

			if available < cost:
				can_afford = false
				# #1087: `cost`/`available` are Variants straight off the state dict --
				# "%s" printed them as raw floats. Route through the format policy.
				var res_key := str(resource)
				if res_key == "attention":
					missing_resources.append("Attention (need %s, have %s available)" % [
						GameConfig.format_scalar(float(cost)), GameConfig.format_scalar(float(available))])
				else:
					missing_resources.append("%s (need %s, have %s)" % [
						GameConfig.format_resource_name(res_key),
						GameConfig.format_resource_amount(res_key, cost),
						GameConfig.format_resource_amount(res_key, available)])

		# Add tooltip with costs/effects
		# #1087: these two loops used to dump the raw cost/effect dicts
		# ("  money: 3000.0"), leaking an internal key AND a float into a
		# player-facing tooltip. Both now route through the GameConfig
		# number-format policy (docs/NUMBER_FORMATS.md).
		var tooltip = ""
		if not shown_costs.is_empty():
			tooltip += "Costs:\n"
			for resource in shown_costs.keys():
				tooltip += "  %s\n" % GameConfig.format_resource(str(resource), shown_costs[resource])

		var effects = option.get("effects", {})
		if not effects.is_empty():
			tooltip += "\nEffects:\n"
			for resource in effects.keys():
				tooltip += "  %s\n" % GameConfig.format_resource_delta(str(resource), effects[resource])

		if not can_afford:
			tooltip += "\n[CANNOT AFFORD]\n"
			for msg in missing_resources:
				tooltip += "  Missing: " + msg + "\n"
			btn.disabled = true
			btn.modulate = Color(0.6, 0.6, 0.6)

		btn.tooltip_text = tooltip

		# Connect button
		btn.pressed.connect(func(): _on_choice_pressed(event, choice_id, dialog, click_blocker))

		vbox.add_child(btn)
		buttons.append(btn)
		button_index += 1

	# Mark this as an event dialog to prevent ESC from closing it (issue #452)
	dialog.set_meta("is_event_dialog", true)

	# B1 (Pip, [4:55]-[5:03]): "maybe a space bar or something as well -- maybe not enter, if
	# enter is going to be the commit turn thing, we don't want people doing that accidentally."
	# MainUI._input blocks SPACE and ENTER outright while any dialog is up (correct: it stops an
	# accidental end-turn/commit landing on a crisis). This meta is the narrow, opt-in exception:
	# a costless one-option navigation popup declares that SPACE means "go through the door".
	# ENTER carries no such flag anywhere and stays inert by design.
	dialog.set_meta("space_advances", is_navigation)

	# #877: pin the root-level blocker to the panel's lifetime, so ANY teardown path takes the
	# blocker with it -- the same idiom main_ui._present_modal_dialog uses for its barrier.
	_showing_dialog = dialog
	dialog.tree_exited.connect(click_blocker.queue_free)
	dialog.tree_exited.connect(_on_shown_dialog_gone.bind(dialog))

	# Hand the dialog + buttons to the host for keyboard routing (MainUI._input)
	print("[EventDialog] Emitting dialog_opened with %d buttons" % buttons.size())
	dialog_opened.emit(dialog, buttons)

	# Add dialog to viewport root (Fix #458) - ensures it's above blocker and all UI
	print("[EventDialog] Adding event dialog to viewport root as top-level overlay...")
	get_tree().root.add_child(dialog)
	dialog.visible = true
	dialog.z_index = 1000  # Very high z-index to ensure it's on top
	dialog.z_as_relative = false  # Absolute z-index, not relative to parent
	print("[EventDialog] Event dialog added and made visible: %s" % dialog.visible)

	# Wait one frame
	await get_tree().process_frame
	print("[EventDialog] === EVENT DIALOG SETUP COMPLETE ===")
	print("[EventDialog] Ready for keyboard input via MainUI._input()")

func _on_choice_pressed(event: Dictionary, choice_id: String, dialog: Control, blocker: Control) -> void:
	"""Handle an event choice press. Direction-b (playtest 2026-07-24): do NOT close the dialog
	here. Resolution is signal-driven (the host routes choice_selected to game_manager.
	resolve_event); the host then calls report_choice_result() with the outcome. Only a SUCCESS
	closes/advances this dialog -- a rejected (unaffordable) choice keeps it OPEN and shows why,
	so a rejection can never be mistaken for 'order accepted'."""
	# Remember what is in flight so report_choice_result can act on the right dialog.
	_pending_dialog = dialog
	_pending_blocker = blocker
	_pending_event = event
	_pending_choice_id = choice_id

	# Clear any stale rejection reason from a prior attempt before re-trying.
	_clear_reason()

	# Resolution stays signal-driven. NOTE: this emit runs synchronously -- the host resolves
	# and calls report_choice_result() back into us DURING this call, so nothing below the emit
	# may assume the dialog still exists. All close/advance logic lives in report_choice_result.
	choice_selected.emit(event, choice_id)


func report_choice_result(success: bool, message: String) -> void:
	"""Host callback with the resolution outcome (MainUI._on_event_choice_selected).
	SUCCESS -> close this dialog and advance the queue (the old _on_choice_pressed tail).
	FAILURE -> keep the dialog OPEN and surface the reason in-place, so the player can pick a
	different option (e.g. the free out). The failed press consumed nothing (WindowResolver
	pre-checks money before any state change), so a retry is safe."""
	if not is_instance_valid(_pending_dialog):
		return  # defensive: nothing in flight (e.g. a non-dialog resolution path)

	if not success:
		# Prefer a concrete, actionable money shortfall; else fall back to the resolver message
		# (e.g. "Not enough Attention to handle this window").
		var reason := _money_shortfall_reason(_pending_event, _pending_choice_id)
		if reason == "":
			reason = message
		_show_reason(reason)
		return

	# SUCCESS: the choice actually resolved -- close this dialog and move on.
	message_logged.emit("[color=cyan]Event choice: %s[/color]" % _pending_choice_id)
	# #877: hand the teardown off from the tree_exited safety net to this (correct) path, so
	# the net does not double-fire dialog_closed / clobber the next event's presenter state.
	if _showing_dialog == _pending_dialog:
		_showing_dialog = null
	if is_instance_valid(_pending_dialog):
		_pending_dialog.queue_free()
	if is_instance_valid(_pending_blocker):
		_pending_blocker.queue_free()
	_pending_dialog = null
	_pending_blocker = null
	_reason_label = null

	# Tell the host to clear its key-routing state.
	dialog_closed.emit()

	# Show next event in queue if any (playback may have enqueued more during resolution).
	if not event_queue.is_empty():
		print("[EventDialog] Event resolved, showing next event in queue...")
		await get_tree().process_frame
		_show_next_event()
	else:
		print("[EventDialog] Event resolved, queue empty")
		is_showing_event = false


func _on_shown_dialog_gone(dialog: Control) -> void:
	"""#877 safety net: the on-screen event panel left the tree WITHOUT resolving (the success
	path clears _showing_dialog first, so this only runs on an external teardown). Reset the
	presenter instead of leaving it stuck 'busy' forever, and tell the host to clear its
	key-routing slots. If events were waiting behind this one, present the next once the tree
	settles -- an unanswered queue with an idle presenter is the stuck-queue failure."""
	if _showing_dialog != dialog:
		return
	_showing_dialog = null
	_pending_dialog = null
	_pending_blocker = null
	_pending_event = {}
	_pending_choice_id = ""
	_reason_label = null
	is_showing_event = false
	dialog_closed.emit()
	if not event_queue.is_empty():
		call_deferred("_show_next_event")


func _show_reason(message: String) -> void:
	"""Surface a rejection reason inside the still-open dialog (direction-b).

	A STUB refusal (scripts/core/refusal.gd) arrives with the alpha marker already appended.
	Lift it back out and give it its own line instead of leaving it wedged mid-sentence:
	"-- pick another option." belongs with the reason, and the marker is an aside to the
	player about the BUILD, not part of the in-fiction sentence. Purely presentational --
	neither string is reworded, and a message with no marker renders exactly as before."""
	if not is_instance_valid(_reason_label):
		return
	var text := message if message != "" else "That choice was rejected."
	var marker := ""
	if Refusal.is_stub_message(text):
		marker = "\n%s" % Refusal.ALPHA_STUB_MARKER
		text = Refusal.strip_marker(text)
		if text.is_empty():
			text = "That choice was rejected."
	_reason_label.text = "[!] %s -- pick another option.%s" % [text, marker]
	_reason_label.visible = true


func _clear_reason() -> void:
	if is_instance_valid(_reason_label):
		_reason_label.text = ""
		_reason_label.visible = false


func _money_shortfall_reason(event: Dictionary, choice_id: String) -> String:
	"""Concrete money-shortfall string for the chosen option, e.g.
	'Not enough money: need $20,000, have $8,400'. Returns '' when there is no money shortfall
	(so the resolver's own message stands -- e.g. an Attention shortfall, which lives on the
	window, not the option costs). Read-only: derives from the option costs + current state,
	it does NOT re-run resolution."""
	var current_state: Dictionary = state_provider.call() if state_provider.is_valid() else {}
	for option in event.get("options", []):
		if option is Dictionary and String(option.get("id", "")) == choice_id:
			var costs: Dictionary = option.get("costs", {})
			var need = costs.get("money", 0)
			var have = current_state.get("money", 0)
			if need > have:
				return "Not enough money: need %s, have %s" % [GameConfig.format_money(need), GameConfig.format_money(have)]
			return ""
	return ""

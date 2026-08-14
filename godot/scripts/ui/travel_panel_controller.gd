class_name TravelPanelController
extends RefCounted
## CARVE 4 (docs/MAIN_UI_SEAM_MAP.md, seams R1 + R5): the travel/conferences submenu pipeline pulled
## out of the main_ui.gd monolith. This is the LAST bespoke submenu -- CARVE 2 (SubmenuController)
## deliberately left travel special-cased (parallel to how CARVE 3 lifted hiring) because it does not
## generalize into the icon-grid: it carries a paper-status section, an upcoming-conferences section,
## and two sub-dialogs (submit paper / attend conference) with their own Back routing. This is its home now.
##
## NON-FORKING extraction (structure-only): every function body is a VERBATIM move; only host-owned
## members/helpers (active_dialog state, game_manager, log_message, the shared modal shell, and the
## shared cost helpers _format_costs_inline / _costs_affordable / _make_cost_label) are re-routed
## through `host.`, exactly as SubmenuController and HiringPanelController compose them. No
## gameplay/RNG/scoring change; every action still routes through the SAME GameActions delegates
## (submit_paper_to_conference / attend_conference_action) and reads the SAME state payload. Ladder stays L2.
##
## What it owns (was inline in main_ui):
##   * open() -> _show_travel_submenu() -- the TRAVEL & CONFERENCES panel (actions grid + papers +
##     upcoming-conferences sections)
##   * _on_travel_option_selected() -- routes a picked travel option to its sub-dialog (or stub log)
##   * _show_paper_submission_dialog() -- the submit-a-paper-to-a-conference flow
##   * _show_conference_attendance_dialog() -- the attend-a-conference flow (jet-lag on first researcher)
##
## PURE VIEW (ADR-0006): reads the live state payload (paper_submissions / calendar / researchers /
## attended_conferences) and the Conferences catalog; never touches sim/RNG/turn loop. main_ui keeps a
## one-line _show_travel_submenu() shim so SubmenuController.open("travel") and dev_mode_overlay reach
## the panel unchanged.

var host  # MainUI node (untyped: avoids a class_name coupling cycle main_ui <-> controller)


func _init(host_ref) -> void:
	host = host_ref


# --- Single entry point (SubmenuController.open("travel") delegates here via the view shim) ---

func open() -> void:
	_show_travel_submenu()


func _show_travel_submenu():
	"""Show popup dialog with travel/conference options - Issue #468"""
	print("[MainUI] === TRAVEL SUBMENU STARTING ===")

	# #877: the local free-first block moved into ModalStack (via host._present_modal_dialog),
	# so the incumbent is popped top-first -- or this open is refused outright when an
	# unanswered event holds the top, instead of stranding that event's blocker.

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
	var current_state = host.game_manager.get_game_state()
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
	# #567: travel was the one panel advertising NUMBERS while every sibling advertised
	# LETTERS -- and 1-9 already mean "action bar slot" everywhere outside a dialog, so the
	# same key meant two things one keypress apart. Letters now, from the shared table.
	# Numbers still WORK (DialogKeys keeps them as an unadvertised alias), so the old habit
	# is not punished.

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
		btn.text = DialogKeys.label_for(button_index)
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		# Cost summary -- shown ON the button face (cost label below), not hover-only (#822).
		var cost_text = host._format_costs_inline(travel_costs)
		var is_free = cost_text == "Free"

		# Check affordability
		var can_afford = true
		if is_stub:
			can_afford = false
		else:
			can_afford = host._costs_affordable(travel_costs, current_state)

		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip
		btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [travel_name, travel_desc, cost_text]

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

		# On-face cost line (#822 cost-display sweep) -- greyed along with the button when unaffordable.
		var travel_cost_label = host._make_cost_label(cost_text, is_free)
		if not can_afford:
			travel_cost_label.modulate = Color(0.5, 0.5, 0.5)
		item_vbox.add_child(travel_cost_label)

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
	host.active_dialog = dialog
	host.active_dialog_buttons = buttons
	print("[MainUI] Travel submenu opened, tracked %d buttons" % buttons.size())

	# Add dialog to TabManager as overlay
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

	await host.get_tree().process_frame
	print("[MainUI] === TRAVEL SUBMENU SETUP COMPLETE ===")

func _on_travel_option_selected(action_id: String, action_name: String, dialog: Control):
	"""Handle travel submenu selection"""
	print("[MainUI] Travel option selected: %s (id: %s)" % [action_name, action_id])
	dialog.queue_free()

	# Clear active dialog state
	host.active_dialog = null
	host.active_dialog_buttons = []

	# Handle stub action. A click that can never land is the same silent-failure class as a
	# refused one: during PLAN the old bare log_message() went into the hidden feed, so the
	# button read as broken rather than as not-built-yet. report_rejection reaches the toast.
	if action_id == "send_delegation":
		host.report_rejection("Delegation is not built yet (issue #411) - nothing was queued.")
		return

	# For submit_paper and attend_conference, show dedicated dialogs
	if action_id == "submit_paper":
		_show_paper_submission_dialog()
		return
	elif action_id == "attend_conference":
		_show_conference_attendance_dialog()
		return
	elif action_id == "attend_conference_trip":
		_show_conference_trip_dialog()
		return


func _show_conference_trip_dialog() -> void:
	"""The rhythm-break commit surface (ADR-0014 shell; Pip ruling 2026-07-27).

	Deliberately blunt about the cost BEFORE the player commits -- the whole point of the
	tempo break is that it is a legible-cost / fuzzy-payoff call ("is this worth the blackout
	window"). If this dialog ever stops showing the days away, the cash, and the
	all-your-Attention line, the decision degenerates into a free button.

	PURE VIEW: it reads the ConferenceTrip catalogue and the live state payload, then hands
	the whole commit to GameManager.attend_conference_trip(). No sim work happens here."""
	var dialog := Panel.new()
	dialog.custom_minimum_size = Vector2(560, 460)
	dialog.size = Vector2(560, 460)
	dialog.position = Vector2(90, 60)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 18)
	margin.add_theme_constant_override("margin_right", 18)
	margin.add_theme_constant_override("margin_top", 16)
	margin.add_theme_constant_override("margin_bottom", 16)
	dialog.add_child(margin)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	margin.add_child(vbox)

	var header := Label.new()
	header.text = "LEAVE FOR A CONFERENCE"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 15)
	header.add_theme_color_override("font_color", Color(0.85, 0.72, 0.35))
	vbox.add_child(header)

	var warning := Label.new()
	warning.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	warning.text = "You are gone for the whole window, travel days included. The lab runs on " \
		+ "whatever you have already queued -- your remaining Attention goes with you, and " \
		+ "anything that happens while you are away waits for you on your desk."
	warning.add_theme_font_size_override("font_size", 12)
	warning.add_theme_color_override("font_color", Color(0.62, 0.64, 0.66))
	vbox.add_child(warning)

	vbox.add_child(HSeparator.new())

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(scroll)

	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 12)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(list)

	var current_state: Dictionary = host.game_manager.get_game_state()
	var money: float = float(current_state.get("money", 0))

	for conf in ConferenceTrip.catalogue():
		var conf_id := String(conf.get("id", ""))
		var away: int = ConferenceTrip.away_ticks(conf)
		var cost: int = int(conf.get("travel_cost", 0))

		var row := VBoxContainer.new()
		row.add_theme_constant_override("separation", 3)
		list.add_child(row)

		var title := Label.new()
		title.text = "%s -- %d days away (%d travel)" % [
			String(conf.get("name", conf_id)), away, int(conf.get("travel_days", 0)) * 2]
		title.add_theme_font_size_override("font_size", 13)
		row.add_child(title)

		var blurb := Label.new()
		blurb.text = String(conf.get("blurb", ""))
		blurb.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		blurb.add_theme_font_size_override("font_size", 11)
		blurb.add_theme_color_override("font_color", Color(0.55, 0.57, 0.6))
		row.add_child(blurb)

		var gate: Dictionary = ConferenceTrip.can_commit(host.game_manager.state, conf_id)
		var go_btn := Button.new()
		go_btn.text = "Commit -- %s + all remaining Attention" % GameConfig.format_money(cost)
		go_btn.disabled = not bool(gate.get("ok", false)) or money < float(cost)
		if go_btn.disabled:
			go_btn.tooltip_text = String(gate.get("reason", "Unavailable"))
			go_btn.modulate = Color(0.5, 0.5, 0.5)
		go_btn.pressed.connect(_on_conference_trip_committed.bind(conf_id, dialog))
		row.add_child(go_btn)

	var cancel := Button.new()
	cancel.text = "Stay home"
	cancel.pressed.connect(func():
		dialog.queue_free()
		host.active_dialog = null)
	vbox.add_child(cancel)

	# #877: assign BEFORE presenting -- the chokepoint reads the slot and re-asserts it if
	# the open is refused (an unanswered event outranks every other modal).
	host.active_dialog = dialog
	host._present_modal_dialog(dialog)


func _on_conference_trip_committed(conf_id: String, dialog: Control) -> void:
	"""Commit -> resolve the away window -> fade out to the mini-scene.

	Navigation goes through SceneTransition (the v0.11.0 rule); use_fade=true IS the
	fade-out half of the tempo pocket. The fade back in happens on the vignette's exit."""
	dialog.queue_free()
	host.active_dialog = null
	host.active_dialog_buttons = []

	var trip: Dictionary = host.game_manager.attend_conference_trip(conf_id)
	if not bool(trip.get("success", false)):
		# NOT host.report_outcome: GameManager.attend_conference_trip already emits
		# error_occurred on a refusal, which is the SAME door (present_error -> feed + PLAN
		# toast). Reporting again here would raise the toast twice for one click. This line is
		# the feed record only, which is why it is safe as a bare log_message.
		host.log_message("[color=yellow]%s[/color]" % String(trip.get("message", "Cannot attend.")))
		return

	host.log_message("[color=cyan]Leaving for %s...[/color]" % String(
		trip.get("conference", {}).get("name", "a conference")))
	SceneTransition.go_to("res://scenes/ui/conference_vignette.tscn", true)

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

	var current_state = host.game_manager.get_game_state()
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
	cancel_btn.pressed.connect(func(): dialog.queue_free(); host.active_dialog = null)
	button_hbox.add_child(cancel_btn)

	var submit_btn = Button.new()
	submit_btn.text = "Submit Paper (1 Attention)"
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
		var result = GameActions.submit_paper_to_conference(host.game_manager.state, conf_id, topic, research_amount, lead)
		# The delegate refuses on research OR on Attention ("Not enough Attention (1 operating
		# hour required)"), and this used to report EVERY verdict as a cyan success line into
		# the PLAN-hidden feed -- so a refused submission read as an accepted one that vanished.
		host.report_outcome(result, "Paper")
		dialog.queue_free()
		host.active_dialog = null
	)
	button_hbox.add_child(submit_btn)

	host._add_submenu_close_affordance(dialog)  # X + ESC hint, consistent with action submenus (#510)
	host.active_dialog = dialog
	host._present_modal_dialog(dialog)
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

	var current_state = host.game_manager.get_game_state()
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
			cost_label.text = "Flights: %s | Hotel: %s | Registration: %s\nTotal: %s + 2 Attention" % [
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
	cancel_btn.pressed.connect(func(): dialog.queue_free(); host.active_dialog = null)
	button_hbox.add_child(cancel_btn)

	var attend_btn = Button.new()
	attend_btn.text = "Attend (2 Attention)"
	attend_btn.pressed.connect(func():
		var conf_id = conf_dropdown.get_item_metadata(conf_dropdown.selected)
		# Issue #469: Apply jet lag to first researcher (economy class default)
		# TODO: Multi-stage booking with traveler/class selection
		var traveler = host.game_manager.state.researchers[0] if host.game_manager.state.researchers.size() > 0 else null
		var result = GameActions.attend_conference_action(host.game_manager.state, conf_id, "economy", traveler)
		# Same door as hiring: the refusal ("Cannot afford: $X + 2 operating hours required")
		# reached only the PLAN-hidden feed before, so an unaffordable trip was a dead button.
		host.report_outcome(result, "Conference")
		dialog.queue_free()
		host.active_dialog = null
	)
	button_hbox.add_child(attend_btn)

	host._add_submenu_close_affordance(dialog)  # X + ESC hint, consistent with action submenus (#510)
	host.active_dialog = dialog
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

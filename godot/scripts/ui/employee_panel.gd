extends Node
class_name EmployeePanel
## Employee roster + staff ID card -- extracted from main_ui.gd (#622, build lane L10).
##
## Renders the middle-panel roster (individual researchers, or legacy counts) and the
## full staff perks panel ("ID card") overlay. Grows into the L2 per-person assignment
## surface. Host wiring: setup() hands over the roster container and overlay parent;
## dialog_opened/dialog_closed keep MainUI's active_dialog bookkeeping in sync;
## info_text_changed feeds the info bar on perk hover.

## The staff ID card overlay went up -- host should treat it as the active dialog.
signal dialog_opened(dialog: Control)
## The staff ID card overlay was dismissed.
signal dialog_closed
## BBCode text for the host's info bar (perk hover details).
signal info_text_changed(text: String)

var roster_container: Container
var overlay_parent: Node

func setup(roster: Container, overlay: Node) -> void:
	"""Hand over the scene nodes this panel renders into: the roster VBox and the
	node the ID-card overlay is parented to (the TabManager, so it overlays all UI)."""
	roster_container = roster
	overlay_parent = overlay

func update_roster(state: Dictionary) -> void:
	"""Update the employee roster display in the middle panel"""
	if not roster_container:
		return

	# Clear existing roster entries
	for child in roster_container.get_children():
		child.queue_free()

	# Get researchers from state
	var researchers = state.get("researchers", [])

	# If no individual researchers, show legacy counts
	if researchers.is_empty():
		var safety = state.get("safety_researchers", 0)
		var capability = state.get("capability_researchers", 0)
		var compute_eng = state.get("compute_engineers", 0)
		var managers = state.get("managers", 0)

		if safety + capability + compute_eng + managers == 0:
			var empty_label = Label.new()
			empty_label.text = "No staff hired"
			empty_label.add_theme_font_size_override("font_size", 10)
			empty_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))
			empty_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			roster_container.add_child(empty_label)
		else:
			# Show legacy count display
			_add_legacy_staff_display(safety, capability, compute_eng, managers)
		return

	# Show individual researchers
	for researcher_data in researchers:
		var entry = _create_researcher_button(researcher_data)
		roster_container.add_child(entry)

func _add_legacy_staff_display(safety: int, capability: int, compute_eng: int, managers: int) -> void:
	"""Show simple staff counts (legacy mode)"""
	var staff_types = [
		{"name": "Safety", "count": safety, "color": Color(0.3, 0.8, 0.3)},
		{"name": "Capability", "count": capability, "color": Color(0.8, 0.3, 0.3)},
		{"name": "Engineers", "count": compute_eng, "color": Color(0.3, 0.5, 0.8)},
		{"name": "Managers", "count": managers, "color": Color(0.7, 0.7, 0.3)}
	]

	for staff_type in staff_types:
		if staff_type["count"] > 0:
			var hbox = HBoxContainer.new()
			hbox.add_theme_constant_override("separation", 4)

			# Color indicator
			var indicator = Label.new()
			indicator.text = "*"
			indicator.add_theme_color_override("font_color", staff_type["color"])
			indicator.add_theme_font_size_override("font_size", 12)
			hbox.add_child(indicator)

			# Count and name
			var name_label = Label.new()
			name_label.text = "%s: %d" % [staff_type["name"], staff_type["count"]]
			name_label.add_theme_font_size_override("font_size", 10)
			name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
			hbox.add_child(name_label)

			roster_container.add_child(hbox)

func _create_researcher_button(data: Dictionary) -> Control:
	"""Create a roster entry/button for an individual researcher"""
	var btn := Button.new()
	btn.custom_minimum_size = Vector2(0, 32)
	btn.focus_mode = Control.FOCUS_NONE
	btn.size_flags_horizontal = Control.SIZE_FILL
	#btn.clip_contents = false

	# Margin/Padding - ensures text does not render so close to box walls
	var margin := MarginContainer.new()
	#var margin_padding = 8
	#margin.add_theme_constant_override("margin_left", margin_padding)
	#margin.add_theme_constant_override("margin_right", margin_padding)
	btn.add_child(margin)

	# Main Row
	var hbox := HBoxContainer.new()
	var hbox_separation = 8
	hbox.add_theme_constant_override("separation", hbox_separation)
	hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	margin.add_child(hbox)

	# Specialization Colours - should this be global/callable?
	var spec_colors = {
		"safety": Color(0.3, 0.8, 0.3),
		"capabilities": Color(0.8, 0.3, 0.3),
		"interpretability": Color(0.7, 0.3, 0.8),
		"alignment": Color(0.3, 0.7, 0.8)
	}

	# Specialisation Indicator
	var spec = data.get("specialization", "safety")
	var indicator := Label.new()
	indicator.text = "*"
	indicator.add_theme_color_override("font_color", spec_colors.get(spec, Color.WHITE))
	hbox.add_child(indicator)

	# Name Label
	var name_label := Label.new()
	name_label.text = data.get("name", "Unknown")
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	name_label.add_theme_font_size_override("separation", 8)
	hbox.add_child(name_label)

	# Productivity Indicator. feat/quirk-skeleton display fix: the old inline formula
	# (1 - burnout/200) disagreed with the model (researcher.gd get_effective_productivity:
	# burnout/100 * 0.5, plus quirk/jet-lag/onboarding). Rebuild the Researcher and read
	# the ONE formula.
	var model := _researcher_from_data(data)
	var burnout = data.get("burnout", 0.0)
	var effective_prod = model.get_effective_productivity()

	var prod_label := Label.new()
	prod_label.text = "%.0f%%" % (effective_prod * 100)
	prod_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT

	# Color logic - based on employee productivity
	if effective_prod >= 1.0:
		prod_label.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	elif effective_prod >= 0.7:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.3))
	else:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))

	hbox.add_child(prod_label)

	# Burnout warning if high
	if burnout >= 60:
		var burnout_icon = Label.new()
		burnout_icon.text = "[!]"
		burnout_icon.add_theme_color_override("font_color", Color(0.9, 0.6, 0.2))
		hbox.add_child(burnout_icon)

	# Known-quirk marker (feat/quirk-skeleton): a [Q] chip once the quirk surfaced; the
	# tooltip carries the name. Hidden quirks show nothing (A2). Icon art: issue #903.
	if bool(data.get("quirk_known", false)) and str(data.get("quirk", "")) != "":
		var quirk_chip = Label.new()
		quirk_chip.text = "[Q]"
		quirk_chip.add_theme_color_override("font_color", Color(0.78, 0.72, 0.54))
		hbox.add_child(quirk_chip)
		btn.tooltip_text = "Quirk: %s" % QuirkCatalogue.display_name(str(data.get("quirk", "")))

	# When staff button is pressed, show extra detail
	btn.pressed.connect(
		func(): show_staff_id_card(data)
	)

	return btn

func _researcher_from_data(data: Dictionary) -> Researcher:
	"""Rebuild a FULL Researcher from a state dict. from_dict restores every layer --
	including quirk/quirk_known/appetites -- so the ID card shows the real person
	(feat/quirk-skeleton: the old hand-copied field list silently DROPPED the quirk layer)."""
	var r := Researcher.new()
	r.from_dict(data)
	return r

func show_staff_id_card(data: Dictionary) -> void:
	"""Show the staff ID card (dossier) for a researcher"""
	print("[EmployeePanel] Opening staff ID card for: %s" % data.get("name", "Unknown"))

	# Load and instance the dossier panel scene
	var perks_panel_scene = preload("res://scenes/ui/staff_perks_panel.tscn")
	var perks_panel = perks_panel_scene.instantiate()

	# Full-fidelity rebuild -- keeps the quirk/appetite layer the old builder skipped.
	var researcher := _researcher_from_data(data)

	# Add blocker behind panel
	var blocker = ColorRect.new()
	blocker.color = Color(0.0, 0.0, 0.0, 0.5)
	blocker.mouse_filter = Control.MOUSE_FILTER_STOP
	blocker.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	blocker.z_index = 998

	# Click on blocker closes panel
	blocker.gui_input.connect(func(event):
		if event is InputEventMouseButton and event.pressed:
			perks_panel.queue_free()
			blocker.queue_free()
			dialog_closed.emit()
	)

	overlay_parent.add_child(blocker)

	# Add panel
	overlay_parent.add_child(perks_panel)
	# #877: pin the blocker to the CARD's lifetime. Both close lambdas above/below capture
	# perks_panel, so once anything else freed the card (ESC via MainUI, a replacing modal)
	# neither lambda could ever run again and the z=998 MOUSE_FILTER_STOP blocker was
	# stranded over the whole board -- a dead-mouse soft-lock with nothing visible to blame.
	perks_panel.tree_exited.connect(blocker.queue_free)
	perks_panel.z_index = 999
	perks_panel.visible = true

	# Connect signals
	perks_panel.close_requested.connect(func():
		perks_panel.queue_free()
		blocker.queue_free()
		dialog_closed.emit()
	)

	# (Perk hover signals retired with the dead perk grid -- the dossier panel is static.)

	# Set researcher data
	perks_panel.set_researcher(researcher)

	# Track as active dialog (host closes any prior dialog and adopts this one)
	dialog_opened.emit(perks_panel)
	print("[EmployeePanel] Staff ID card opened")

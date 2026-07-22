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

	# Productivity Indicator (simple bar or percentage)
	var productivity = data.get("base_productivity", 1.0)
	var burnout = data.get("burnout", 0.0)
	var effective_prod = productivity * (1.0 - min(burnout / 200.0, 0.5))

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
		burnout_icon.text = ""
		#burnout_icon.add_theme_font_size_override("font_size", 8)
		hbox.add_child(burnout_icon)

	# When staff button is pressed, show extra detail
	btn.pressed.connect(
		func(): show_staff_id_card(data)
	)

	return btn

func show_staff_id_card(data: Dictionary) -> void:
	"""Show the full staff perks panel for a researcher"""
	print("[EmployeePanel] Opening staff perks panel for: %s" % data.get("name", "Unknown"))

	# Load and instance the perks panel scene
	var perks_panel_scene = preload("res://scenes/ui/staff_perks_panel.tscn")
	var perks_panel = perks_panel_scene.instantiate()

	# Create a Researcher object from the dictionary data
	var researcher = Researcher.new(data.get("specialization", "safety"), data.get("name", ""))
	researcher.skill_level = data.get("skill_level", 5)
	researcher.current_salary = data.get("current_salary", 60000)
	researcher.base_productivity = data.get("base_productivity", 1.0)
	researcher.burnout = data.get("burnout", 0.0)
	researcher.loyalty = data.get("loyalty", 50)
	researcher.turns_employed = data.get("turns_employed", 0)
	researcher.jet_lag_turns = data.get("jet_lag_turns", 0)
	researcher.jet_lag_severity = data.get("jet_lag_severity", 0.0)

	# (Legacy traits retired -> the hidden quirk layer is restored via Researcher.from_dict
	# on the real load path; this lightweight card builder just skips it.)

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
	perks_panel.z_index = 999
	perks_panel.visible = true

	# Connect signals
	perks_panel.close_requested.connect(func():
		perks_panel.queue_free()
		blocker.queue_free()
		dialog_closed.emit()
	)

	perks_panel.perk_hovered.connect(func(perk_data):
		var perk_name = perk_data.get("name", "Unknown")
		var perk_desc = perk_data.get("description", "")
		info_text_changed.emit("[b][color=cyan]%s[/color][/b] -- %s\n[color=gray]Perk selection coming in future update[/color]" % [perk_name, perk_desc])
	)

	perks_panel.perk_unhovered.connect(func():
		info_text_changed.emit("[color=gray]Hover over actions to see details...\n [/color]")
	)

	# Set researcher data
	perks_panel.set_researcher(researcher)

	# Track as active dialog (host closes any prior dialog and adopts this one)
	dialog_opened.emit(perks_panel)
	print("[EmployeePanel] Staff perks panel opened")

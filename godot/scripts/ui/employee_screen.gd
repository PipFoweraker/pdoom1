extends VBoxContainer
## Employee Management Screen - Shows detailed employee information and warnings

@onready var stats_text = $ContentArea/LeftPanel/StatsPanel/MarginContainer/StatsText
@onready var warnings_text = $ContentArea/LeftPanel/WarningsPanel/MarginContainer/WarningsText
@onready var employees_list = $ContentArea/RightPanel/EmployeesScroll/EmployeesList

var game_manager: Node

func _ready():
	# Get GameManager reference from parent hierarchy
	game_manager = get_node("/root/Main/GameManager")

	# Connect to GameManager signals
	if game_manager:
		game_manager.game_state_updated.connect(_on_game_state_updated)

func _on_back_button_pressed():
	"""Return to main game screen"""
	get_parent().show_main_screen()

func _on_game_state_updated(state: Dictionary):
	"""Update employee display when game state changes"""
	_update_stats(state)
	_update_warnings(state)
	_update_employee_list(state)

func _update_stats(state: Dictionary):
	"""Update team overview statistics"""
	var total_employees = state.get("staff", 0)
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)

	var stats = "[b]Team Size:[/b] %d employees\n\n" % total_employees
	stats += "[color=green]● Safety Researchers:[/color] %d\n" % safety
	stats += "[color=red]● Capability Researchers:[/color] %d\n" % capability
	stats += "[color=blue]● Compute Engineers:[/color] %d\n\n" % compute_eng

	# Add productivity info
	var employee_blobs = state.get("employee_blobs", [])
	var productive = 0
	var unproductive = 0

	for blob in employee_blobs:
		if blob.get("productivity", 0) > 0:
			productive += 1
		else:
			unproductive += 1

	stats += "[b]Productivity:[/b]\n"
	stats += "[color=lime]✓ Productive:[/color] %d\n" % productive
	if unproductive > 0:
		stats += "[color=red]✗ Unproductive:[/color] %d\n" % unproductive

	stats_text.text = stats

func _update_warnings(state: Dictionary):
	"""Update management warnings based on employee count"""
	var total_employees = state.get("staff", 0)
	var warnings = []

	# Progressive warning system (issue #424 Phase 2)
	if total_employees >= 10:
		warnings.append("[color=red]⚠️ CRITICAL: 10+ employees - Unmanaged staff are unproductive![/color]")
		warnings.append("[color=yellow]→ Action: Hire Admin Staff or promote experienced employees[/color]")
	elif total_employees == 9:
		warnings.append("[color=orange]⚠️ WARNING: At management capacity (9 employees)[/color]")
		warnings.append("[color=gray]→ Next hire will need management support[/color]")
	elif total_employees == 8:
		warnings.append("[color=yellow]ℹ️ INFO: Team growing - Consider hiring management soon[/color]")
		warnings.append("[color=gray]→ Management helps maintain productivity at scale[/color]")

	# Check for compute shortage
	var employee_blobs = state.get("employee_blobs", [])
	var no_compute_count = 0
	for blob in employee_blobs:
		if not blob.get("has_compute", false) and blob.get("type", "") == "employee":
			no_compute_count += 1

	if no_compute_count > 0:
		warnings.append("[color=orange]⚠️ %d employees lack compute resources[/color]" % no_compute_count)
		warnings.append("[color=gray]→ Purchase more compute or optimize allocation[/color]")

	if warnings.size() > 0:
		warnings_text.text = "\n\n".join(warnings)
	else:
		warnings_text.text = "[color=green]✓ No warnings - Team running smoothly![/color]"

func _update_employee_list(state: Dictionary):
	"""Display detailed list of all employees"""
	# Clear existing list
	for child in employees_list.get_children():
		child.queue_free()

	var employee_blobs = state.get("employee_blobs", [])

	if employee_blobs.size() == 0:
		var label = Label.new()
		label.text = "No employees hired yet."
		label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		employees_list.add_child(label)
		return

	# Display each employee
	for i in range(employee_blobs.size()):
		var blob = employee_blobs[i]
		var employee_card = _create_employee_card(blob, i + 1)
		employees_list.add_child(employee_card)

func _create_employee_card(blob: Dictionary, number: int) -> PanelContainer:
	"""Create a card displaying employee information"""
	var card = PanelContainer.new()
	card.custom_minimum_size = Vector2(0, 80)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 10)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_right", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	card.add_child(margin)

	var vbox = VBoxContainer.new()
	margin.add_child(vbox)

	# Employee header (number and type)
	var header = HBoxContainer.new()
	vbox.add_child(header)

	var name_label = Label.new()
	var subtype = blob.get("subtype", "employee")
	var type_display = subtype.replace("_", " ").capitalize()

	# Color code by type
	var type_color = Color.WHITE
	if "safety" in subtype:
		type_color = Color.GREEN
	elif "capability" in subtype:
		type_color = Color.RED
	elif "compute" in subtype:
		type_color = Color.CYAN

	name_label.text = "#%d - %s" % [number, type_display]
	name_label.add_theme_color_override("font_color", type_color)
	name_label.add_theme_font_size_override("font_size", 14)
	header.add_child(name_label)

	var spacer = Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)

	# Status indicator
	var status_label = Label.new()
	var is_productive = blob.get("productivity", 0) > 0
	var has_compute = blob.get("has_compute", false)

	if is_productive and has_compute:
		status_label.text = "✓ Productive"
		status_label.add_theme_color_override("font_color", Color.LIME_GREEN)
	elif not has_compute:
		status_label.text = "⚠ No Compute"
		status_label.add_theme_color_override("font_color", Color.ORANGE)
	else:
		var reason = blob.get("unproductive_reason", "unknown")
		if reason == "no_manager":
			status_label.text = "✗ Needs Management"
		else:
			status_label.text = "✗ Unproductive"
		status_label.add_theme_color_override("font_color", Color.RED)

	header.add_child(status_label)

	# Employee details
	var details = RichTextLabel.new()
	details.bbcode_enabled = true
	details.fit_content = true
	details.scroll_active = false
	details.custom_minimum_size = Vector2(0, 40)

	var details_text = ""

	# Show role
	var employee_type = blob.get("type", "employee")
	if employee_type == "manager":
		details_text += "[color=gold]Role:[/color] Manager\n"
	else:
		details_text += "[color=gray]Role:[/color] Employee\n"

	# Show productivity details
	var productivity = blob.get("productivity", 0)
	var productivity_pct = int(productivity * 100)
	details_text += "[color=gray]Productivity:[/color] %d%%" % productivity_pct

	# Show bonus if active
	var bonus = blob.get("productive_action_bonus", 1.0)
	if bonus != 1.0:
		var bonus_pct = int((bonus - 1.0) * 100)
		if bonus_pct > 0:
			details_text += " [color=lime](+%d%% bonus)[/color]" % bonus_pct
		else:
			details_text += " [color=orange](%d%% penalty)[/color]" % bonus_pct

	details.text = details_text
	vbox.add_child(details)

	return card

func refresh_display():
	"""Refresh employee data when screen becomes visible"""
	if game_manager:
		var state = game_manager.get_game_state()
		_on_game_state_updated(state)

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
	var total_employees = state.get("total_staff", 0)
	var safety = state.get("safety_researchers", 0)
	var capability = state.get("capability_researchers", 0)
	var compute_eng = state.get("compute_engineers", 0)

	var stats = "[b]Team Size:[/b] %d employees\n\n" % total_employees
	stats += "[color=green]● Safety Researchers:[/color] %d\n" % safety
	stats += "[color=red]● Capability Researchers:[/color] %d\n" % capability
	stats += "[color=blue]● Compute Engineers:[/color] %d\n\n" % compute_eng

	# Add productivity info from researchers
	var researchers = state.get("researchers", [])
	var productive = 0
	var unproductive = 0

	for researcher in researchers:
		var productivity = researcher.get("base_productivity", 1.0)
		var burnout = researcher.get("burnout", 0)
		# Consider productive if productivity > 0 and not burned out
		if productivity > 0 and burnout < 90:
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
	var total_employees = state.get("total_staff", 0)
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

	# Check for burnout among researchers
	var researchers = state.get("researchers", [])
	var burnout_count = 0
	for researcher in researchers:
		if researcher.get("burnout", 0) >= 70:
			burnout_count += 1

	if burnout_count > 0:
		warnings.append("[color=orange]⚠️ %d researcher(s) experiencing high burnout[/color]" % burnout_count)
		warnings.append("[color=gray]→ Consider reducing workload or providing breaks[/color]")

	if warnings.size() > 0:
		warnings_text.text = "\n\n".join(warnings)
	else:
		warnings_text.text = "[color=green]✓ No warnings - Team running smoothly![/color]"

func _update_employee_list(state: Dictionary):
	"""Display detailed list of all employees"""
	# Clear existing list
	for child in employees_list.get_children():
		child.queue_free()

	var researchers = state.get("researchers", [])

	if researchers.size() == 0:
		var label = Label.new()
		label.text = "No employees hired yet."
		label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		employees_list.add_child(label)
		return

	# Display each employee
	for i in range(researchers.size()):
		var researcher = researchers[i]
		var employee_card = _create_employee_card(researcher, i + 1)
		employees_list.add_child(employee_card)

func _create_employee_card(researcher: Dictionary, number: int) -> PanelContainer:
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

	# Employee header (number and name)
	var header = HBoxContainer.new()
	vbox.add_child(header)

	var name_label = Label.new()
	var researcher_name = researcher.get("name", "Anonymous Researcher")
	var specialization = researcher.get("specialization", "safety")

	# Color code by specialization
	var type_color = Color.WHITE
	if specialization == "safety" or specialization == "alignment":
		type_color = Color.GREEN
	elif specialization == "capabilities":
		type_color = Color.RED
	elif specialization == "interpretability":
		type_color = Color.CYAN

	name_label.text = "#%d - %s" % [number, researcher_name]
	name_label.add_theme_color_override("font_color", type_color)
	name_label.add_theme_font_size_override("font_size", 14)
	header.add_child(name_label)

	var spacer = Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)

	# Status indicator
	var status_label = Label.new()
	var productivity = researcher.get("base_productivity", 1.0)
	var burnout = researcher.get("burnout", 0)

	if productivity > 0 and burnout < 70:
		status_label.text = "✓ Productive"
		status_label.add_theme_color_override("font_color", Color.LIME_GREEN)
	elif burnout >= 70:
		status_label.text = "⚠ Burned Out"
		status_label.add_theme_color_override("font_color", Color.ORANGE)
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

	# Show specialization
	var spec_name = specialization.capitalize()
	details_text += "[color=gray]Specialization:[/color] %s\n" % spec_name

	# Show skill level
	var skill_level = researcher.get("skill_level", 5)
	details_text += "[color=gray]Skill Level:[/color] %d/10  " % skill_level

	# Show productivity
	var productivity_pct = int(productivity * 100)
	details_text += "[color=gray]Productivity:[/color] %d%%" % productivity_pct

	# Show burnout if significant
	if burnout > 30:
		details_text += "\n[color=orange]Burnout:[/color] %d%%" % int(burnout)

	details.text = details_text
	vbox.add_child(details)

	return card

func refresh_display():
	"""Refresh employee data when screen becomes visible"""
	if game_manager:
		var state = game_manager.get_game_state()
		_on_game_state_updated(state)

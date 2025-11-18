extends VBoxContainer
## Employee Management Screen - Shows detailed employee information and warnings

@onready var stats_text = $ContentArea/LeftPanel/StatsPanel/MarginContainer/StatsText
@onready var warnings_text = $ContentArea/LeftPanel/WarningsPanel/MarginContainer/WarningsText
@onready var employees_list = $ContentArea/RightPanel/EmployeesScroll/EmployeesList

var game_manager: Node

# Fire confirmation dialog
var fire_dialog: ConfirmationDialog
var researcher_to_fire: int = -1  # Index of researcher to fire
var severance_cost: float = 0.0

func _ready():
	# Get GameManager reference from parent hierarchy
	game_manager = get_node("/root/Main/GameManager")

	# Connect to GameManager signals
	if game_manager:
		game_manager.game_state_updated.connect(_on_game_state_updated)

	# Create fire confirmation dialog
	_create_fire_dialog()

func _create_fire_dialog():
	"""Create the confirmation dialog for firing employees"""
	fire_dialog = ConfirmationDialog.new()
	fire_dialog.title = "Confirm Termination"
	fire_dialog.ok_button_text = "Fire"
	fire_dialog.cancel_button_text = "Cancel"
	fire_dialog.size = Vector2(450, 180)
	fire_dialog.confirmed.connect(_on_fire_confirmed)
	add_child(fire_dialog)

func _calculate_severance(researcher: Dictionary) -> float:
	"""Calculate severance package based on tenure and salary"""
	var turns_employed = researcher.get("turns_employed", 0)
	var salary = researcher.get("current_salary", 60000.0)

	# Base severance: 1 month's salary (1/12 of annual)
	var base_severance = salary / 12.0

	# Add 1 week per turn employed (capped at 8 weeks)
	var tenure_bonus = min(turns_employed, 8) * (salary / 52.0)

	return base_severance + tenure_bonus

func _request_fire_employee(researcher_index: int, researcher: Dictionary):
	"""Show confirmation dialog before firing"""
	researcher_to_fire = researcher_index
	severance_cost = _calculate_severance(researcher)

	var researcher_name = researcher.get("name", "Unknown")
	var turns = researcher.get("turns_employed", 0)

	var dialog_text = "Are you sure you want to fire %s?\n\n" % researcher_name
	dialog_text += "Tenure: %d turns\n" % turns
	dialog_text += "Severance cost: %s\n\n" % GameConfig.format_money(severance_cost)

	# Check if player can afford severance
	var state = game_manager.get_game_state() if game_manager else {}
	var current_money = state.get("money", 0)

	if current_money < severance_cost:
		dialog_text += "[color=red]Warning: Insufficient funds for severance![/color]"

	fire_dialog.dialog_text = dialog_text
	fire_dialog.popup_centered()

func _on_fire_confirmed():
	"""Execute the firing after confirmation"""
	if researcher_to_fire < 0 or not game_manager:
		return

	# Check affordability
	var state = game_manager.get_game_state()
	var current_money = state.get("money", 0)

	if current_money < severance_cost:
		# Can't afford - show error in message log
		if game_manager.has_method("add_message"):
			game_manager.add_message("[color=red]Cannot fire: Insufficient funds for severance package![/color]")
		return

	# Fire the researcher
	game_manager.fire_researcher(researcher_to_fire, severance_cost)

	# Reset state
	researcher_to_fire = -1
	severance_cost = 0.0

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
	var compute_engineers = state.get("compute_engineers", 0)
	var managers = state.get("managers", 0)

	var total_employees = researchers.size() + compute_engineers + managers

	if total_employees == 0:
		var label = Label.new()
		label.text = "No employees hired yet."
		label.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		employees_list.add_child(label)
		return

	var employee_number = 1

	# Display researchers
	var researcher_index = 0
	for researcher in researchers:
		var employee_card = _create_employee_card(researcher, employee_number, researcher_index)
		employees_list.add_child(employee_card)
		employee_number += 1
		researcher_index += 1

	# Display compute engineers
	for _i in range(compute_engineers):
		var engineer_card = _create_simple_employee_card("Compute Engineer", "compute", employee_number)
		employees_list.add_child(engineer_card)
		employee_number += 1

	# Display managers
	for _i in range(managers):
		var manager_card = _create_simple_employee_card("Manager", "manager", employee_number)
		employees_list.add_child(manager_card)
		employee_number += 1

func _create_simple_employee_card(role: String, role_type: String, number: int) -> PanelContainer:
	"""Create a card for non-researcher employees (engineers, managers)"""
	var card = PanelContainer.new()
	card.custom_minimum_size = Vector2(0, 60)

	var margin = MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 10)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_right", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	card.add_child(margin)

	var vbox = VBoxContainer.new()
	margin.add_child(vbox)

	# Employee header
	var header = HBoxContainer.new()
	vbox.add_child(header)

	var name_label = Label.new()

	# Color code by role
	var type_color = Color.WHITE
	if role_type == "compute":
		type_color = Color.DODGER_BLUE
	elif role_type == "manager":
		type_color = Color.GOLD

	name_label.text = "#%d - %s" % [number, role]
	name_label.add_theme_color_override("font_color", type_color)
	name_label.add_theme_font_size_override("font_size", 14)
	header.add_child(name_label)

	var spacer = Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(spacer)

	# Status indicator
	var status_label = Label.new()
	status_label.text = "✓ Active"
	status_label.add_theme_color_override("font_color", Color.LIME_GREEN)
	header.add_child(status_label)

	# Role description
	var details = Label.new()
	if role_type == "compute":
		details.text = "Maintains and optimizes compute infrastructure"
	elif role_type == "manager":
		details.text = "Manages up to 9 employees"
	details.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	details.add_theme_font_size_override("font_size", 12)
	vbox.add_child(details)

	return card

func _create_employee_card(researcher: Dictionary, number: int, researcher_index: int = 0) -> PanelContainer:
	"""Create a card displaying employee information with fire button"""
	var card = PanelContainer.new()
	card.custom_minimum_size = Vector2(0, 100)  # Slightly taller for fire button

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

	# Fire button row
	var button_row = HBoxContainer.new()
	vbox.add_child(button_row)

	var button_spacer = Control.new()
	button_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button_row.add_child(button_spacer)

	var fire_button = Button.new()
	fire_button.text = "Fire"
	fire_button.custom_minimum_size = Vector2(60, 24)
	fire_button.add_theme_color_override("font_color", Color.WHITE)
	fire_button.add_theme_color_override("font_hover_color", Color.WHITE)

	# Store researcher data in button metadata for callback
	fire_button.set_meta("researcher_index", researcher_index)
	fire_button.set_meta("researcher_data", researcher)
	fire_button.pressed.connect(_on_fire_button_pressed.bind(fire_button))

	button_row.add_child(fire_button)

	return card

func _on_fire_button_pressed(button: Button):
	"""Handle fire button click"""
	var researcher_index = button.get_meta("researcher_index")
	var researcher_data = button.get_meta("researcher_data")
	_request_fire_employee(researcher_index, researcher_data)

func refresh_display():
	"""Refresh employee data when screen becomes visible"""
	if game_manager:
		var state = game_manager.get_game_state()
		_on_game_state_updated(state)

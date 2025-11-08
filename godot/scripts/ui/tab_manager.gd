extends Control
## Tab Manager - Handles switching between game screens (Civ-style)

@onready var main_ui = $MainUI
@onready var employee_screen = $EmployeeScreen

enum Screen {
	MAIN,
	EMPLOYEES
}

var current_screen: Screen = Screen.MAIN

func _ready():
	# Start with main screen visible
	show_main_screen()

	# Enable input processing for keyboard shortcuts
	set_process_input(true)

func _input(event: InputEvent):
	"""Handle screen switching shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		# E key for Employees screen
		if event.keycode == KEY_E:
			if current_screen == Screen.MAIN:
				show_employee_screen()
			else:
				show_main_screen()
			get_viewport().set_input_as_handled()

		# Escape to return to main screen
		elif event.keycode == KEY_ESCAPE:
			if current_screen != Screen.MAIN:
				show_main_screen()
				get_viewport().set_input_as_handled()

func show_main_screen():
	"""Show the main game screen"""
	current_screen = Screen.MAIN
	main_ui.visible = true
	employee_screen.visible = false
	print("[TabManager] Showing main screen")

func show_employee_screen():
	"""Show the employee management screen"""
	current_screen = Screen.EMPLOYEES
	main_ui.visible = false
	employee_screen.visible = true
	employee_screen.refresh_display()  # Trigger refresh
	print("[TabManager] Showing employee screen")

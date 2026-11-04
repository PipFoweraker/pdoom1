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
		# Employee screen toggle -- the only surface with the Fire button on it (EXPLOIT 001,
		# docs/EXPLOIT_REGISTER.md). Restored from the dead commented block that sat here since #602.
		# Two differences from the version that was commented out: it asks KeybindManager
		# instead of hardcoding a keycode, so a rebind in the keybind screen actually takes
		# (the failure mode documented at keybind_manager.gd's deleted `cancel` bind), and it
		# yields to text fields and open modals so it cannot swallow a keystroke meant for
		# them (#575's defect class).
		if KeybindManager.is_action_pressed(event, "employee_screen") \
				and not KeybindManager.is_text_input_focused() \
				and not _modal_is_open():
			if current_screen == Screen.MAIN:
				show_employee_screen()
			else:
				show_main_screen()
			get_viewport().set_input_as_handled()
			return

		# Escape to return to main screen
		if event.keycode == KEY_ESCAPE:
			if current_screen != Screen.MAIN:
				show_main_screen()
				get_viewport().set_input_as_handled()

func _modal_is_open() -> bool:
	"""True while MainUI has a modal dialog up. TabManager._input runs BEFORE MainUI's
	_unhandled_key_input, so without this the screen toggle would steal a key the dialog was
	waiting for."""
	if main_ui == null or not is_instance_valid(main_ui):
		return false
	return ("active_dialog" in main_ui) and main_ui.active_dialog != null \
		and is_instance_valid(main_ui.active_dialog)


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

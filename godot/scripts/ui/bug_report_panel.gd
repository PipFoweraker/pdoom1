extends Control
## Bug Report Panel UI
##
## Privacy-focused in-game bug reporting interface with clear opt-in messaging
## and contributor recognition support.
##
## Keyboard shortcut: F8 to open (configured in project settings)

# UI References
@onready var title_input: LineEdit = $CenterContainer/PanelContainer/MarginContainer/VBox/Form/TitleInput
@onready var description_input: TextEdit = $CenterContainer/PanelContainer/MarginContainer/VBox/Form/DescriptionInput
@onready var type_option: OptionButton = $CenterContainer/PanelContainer/MarginContainer/VBox/Form/TypeHBox/TypeOption
@onready var screenshot_check: CheckBox = $CenterContainer/PanelContainer/MarginContainer/VBox/Options/ScreenshotCheck
@onready var save_check: CheckBox = $CenterContainer/PanelContainer/MarginContainer/VBox/Options/SaveCheck
@onready var attribution_check: CheckBox = $CenterContainer/PanelContainer/MarginContainer/VBox/Attribution/AttributionCheck
@onready var name_input: LineEdit = $CenterContainer/PanelContainer/MarginContainer/VBox/Attribution/NameInput
@onready var contact_input: LineEdit = $CenterContainer/PanelContainer/MarginContainer/VBox/Attribution/ContactInput
@onready var privacy_label: RichTextLabel = $CenterContainer/PanelContainer/MarginContainer/VBox/PrivacyLabel
@onready var submit_button: Button = $CenterContainer/PanelContainer/MarginContainer/VBox/Buttons/SubmitButton
@onready var cancel_button: Button = $CenterContainer/PanelContainer/MarginContainer/VBox/Buttons/CancelButton
@onready var confirmation_label: Label = $CenterContainer/PanelContainer/MarginContainer/VBox/ConfirmationLabel

var bug_reporter: BugReporter

func _ready():
	# Hide panel by default
	visible = false

	# Initialize bug reporter
	bug_reporter = BugReporter.new()
	add_child(bug_reporter)

	# Connect signals
	bug_reporter.report_saved.connect(_on_report_saved)
	bug_reporter.report_save_failed.connect(_on_report_save_failed)
	submit_button.pressed.connect(_on_submit_pressed)
	cancel_button.pressed.connect(_on_cancel_pressed)
	attribution_check.toggled.connect(_on_attribution_toggled)

	# Populate report type options
	type_option.clear()
	type_option.add_item("Bug Report", BugReporter.ReportType.BUG)
	type_option.add_item("Feature Request", BugReporter.ReportType.FEATURE_REQUEST)
	type_option.add_item("General Feedback", BugReporter.ReportType.FEEDBACK)

	# Set privacy notice
	privacy_label.bbcode_enabled = true
	privacy_label.text = "[center][color=gray]Your privacy is important to us. Reports are saved locally on your device by default. " + \
		"We collect only essential technical information. See [url=https://pdoom.net/privacy]Privacy Policy[/url] for details." + \
		"\n\nBy including your name, you may be recognized in our [url=https://pdoom.net/contributors]Contributors[/url] program![/color][/center]"

	# Initially disable attribution fields
	name_input.editable = false
	contact_input.editable = false

	confirmation_label.visible = false

func _input(event):
	# Only handle input if panel is visible
	if not visible:
		return

	# Handle keyboard shortcuts
	if event is InputEventKey and event.pressed and not event.echo:
		# Backslash (\), N key, or ESC to close bug reporter
		if event.keycode == KEY_BACKSLASH or event.keycode == KEY_N or event.keycode == KEY_ESCAPE:
			hide_panel()
			get_viewport().set_input_as_handled()

## Show the bug report panel
func show_panel():
	visible = true
	# Set mouse filter to stop clicks to prevent background interaction
	mouse_filter = Control.MOUSE_FILTER_STOP
	title_input.grab_focus()

## Hide the bug report panel
func hide_panel():
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	reset_form()

## Toggle panel visibility
func toggle_panel():
	if visible:
		hide_panel()
	else:
		show_panel()

## Reset form to default state
func reset_form():
	title_input.text = ""
	description_input.text = ""
	type_option.selected = 0  # Bug Report
	screenshot_check.button_pressed = true  # Include screenshot by default
	save_check.button_pressed = false
	attribution_check.button_pressed = false
	name_input.text = ""
	contact_input.text = ""
	name_input.editable = false
	contact_input.editable = false
	confirmation_label.visible = false

## Validate form input
func validate_form() -> String:
	if title_input.text.strip_edges() == "":
		return "Please enter a title for your report."

	if description_input.text.strip_edges() == "":
		return "Please enter a description."

	if attribution_check.button_pressed and name_input.text.strip_edges() == "":
		return "Please enter your name if you want attribution, or uncheck the attribution box."

	return ""  # Valid

## Handle submit button press
func _on_submit_pressed():
	var validation_error = validate_form()
	if validation_error != "":
		show_error(validation_error)
		return

	# Capture screenshot if requested
	var screenshot: Image = null
	if screenshot_check.button_pressed:
		screenshot = bug_reporter.capture_screenshot()

	# Get save file path if requested
	var save_path = ""
	if save_check.button_pressed:
		save_path = _get_save_file_path()

	# Create bug report
	var report = bug_reporter.create_bug_report(
		type_option.get_selected_id() as BugReporter.ReportType,
		title_input.text.strip_edges(),
		description_input.text.strip_edges(),
		"",  # steps_to_reproduce (could add another field for this)
		"",  # expected_behavior
		"",  # actual_behavior
		attribution_check.button_pressed,
		name_input.text.strip_edges(),
		contact_input.text.strip_edges(),
		screenshot_check.button_pressed,
		screenshot,
		save_check.button_pressed,
		save_path
	)

	# Save report locally
	var filepath = bug_reporter.save_report_locally(report, screenshot, save_path)

	if filepath != "":
		# Success handled by signal
		pass
	else:
		show_error("Failed to save report. Please try again.")

## Handle cancel button press
func _on_cancel_pressed():
	hide_panel()

## Handle attribution checkbox toggle
func _on_attribution_toggled(toggled_on: bool):
	name_input.editable = toggled_on
	contact_input.editable = toggled_on

	if not toggled_on:
		name_input.text = ""
		contact_input.text = ""

## Handle successful report save
func _on_report_saved(_filepath: String):
	show_confirmation("Thank you! Your report has been saved.\n\nWe'll create a GitHub issue soon. Check back for updates!")

	# Reset form after short delay
	await get_tree().create_timer(3.0).timeout
	if visible:  # Only reset if still visible
		hide_panel()

## Handle report save failure
func _on_report_save_failed(error: String):
	show_error("Failed to save report: " + error)

## Show confirmation message
func show_confirmation(message: String):
	confirmation_label.text = message
	confirmation_label.modulate = Color.GREEN
	confirmation_label.visible = true

## Show error message
func show_error(message: String):
	confirmation_label.text = message
	confirmation_label.modulate = Color.RED
	confirmation_label.visible = true

	# Hide error after 5 seconds
	await get_tree().create_timer(5.0).timeout
	if confirmation_label.modulate == Color.RED:  # Only hide if still showing error
		confirmation_label.visible = false

## Get the current save file path if one exists
## Returns the path to the most recent save file, or "No save file" if none exists
func _get_save_file_path() -> String:
	# Common save file patterns to check
	var save_patterns = [
		"user://savegame.sav",
		"user://quicksave.sav",
		"user://autosave.sav",
		"user://save.dat"
	]

	# Check for any existing save file
	for save_path in save_patterns:
		if FileAccess.file_exists(save_path):
			# Return the global path for user reference
			return ProjectSettings.globalize_path(save_path)

	# Check saves directory for numbered saves (save_001.sav, etc.)
	var saves_dir = "user://saves"
	var dir = DirAccess.open("user://")
	if dir and dir.dir_exists("saves"):
		var saves = DirAccess.open(saves_dir)
		if saves:
			saves.list_dir_begin()
			var newest_save = ""
			var newest_time = 0
			var file_name = saves.get_next()
			while file_name != "":
				if file_name.ends_with(".sav") or file_name.ends_with(".save"):
					var full_path = saves_dir + "/" + file_name
					var mod_time = FileAccess.get_modified_time(full_path)
					if mod_time > newest_time:
						newest_time = mod_time
						newest_save = full_path
				file_name = saves.get_next()
			saves.list_dir_end()
			if newest_save != "":
				return ProjectSettings.globalize_path(newest_save)

	return "No save file"

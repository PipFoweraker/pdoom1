extends Control
## What's New Modal - Shows patch notes for new versions
##
## Displays patch notes on first launch after an update.
## Can also be opened manually from the welcome screen menu.

signal closed

# UI References
@onready var panel_container: PanelContainer = $CenterContainer/PanelContainer
@onready var title_label: Label = $CenterContainer/PanelContainer/MarginContainer/VBox/TitleLabel
@onready var version_label: Label = $CenterContainer/PanelContainer/MarginContainer/VBox/VersionLabel
@onready var content_scroll: ScrollContainer = $CenterContainer/PanelContainer/MarginContainer/VBox/ContentScroll
@onready var content_label: RichTextLabel = $CenterContainer/PanelContainer/MarginContainer/VBox/ContentScroll/ContentLabel
@onready var close_button: Button = $CenterContainer/PanelContainer/MarginContainer/VBox/CloseButton

# Patch notes data
var patch_notes_data: Dictionary = {}
var current_version_data: Dictionary = {}

const PATCH_NOTES_PATH = "res://data/patch_notes.json"

func _ready():
	# Hide by default
	visible = false

	# Connect signals
	close_button.pressed.connect(_on_close_pressed)

	# Load patch notes data
	_load_patch_notes()

func _input(event: InputEvent):
	# Only handle input if modal is visible
	if not visible:
		return

	# Handle keyboard shortcuts to close
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE or event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			_on_close_pressed()
			get_viewport().set_input_as_handled()

## Load patch notes from JSON file
func _load_patch_notes() -> void:
	if not FileAccess.file_exists(PATCH_NOTES_PATH):
		print("[WhatsNewModal] ERROR: Patch notes file not found at %s" % PATCH_NOTES_PATH)
		return

	var file = FileAccess.open(PATCH_NOTES_PATH, FileAccess.READ)
	if not file:
		print("[WhatsNewModal] ERROR: Could not open patch notes file")
		return

	var json_text = file.get_as_text()
	file.close()

	var json = JSON.new()
	var error = json.parse(json_text)
	if error != OK:
		print("[WhatsNewModal] ERROR: Failed to parse patch notes JSON: %s" % json.get_error_message())
		return

	patch_notes_data = json.get_data()
	print("[WhatsNewModal] Loaded patch notes with %d versions" % patch_notes_data.get("versions", []).size())

## Show the modal with patch notes for current version
func show_modal(mark_as_seen: bool = true) -> void:
	if patch_notes_data.is_empty():
		_load_patch_notes()

	# Find current version's patch notes
	var current_version = GameConfig.get_current_version()
	current_version_data = _get_version_data(current_version)

	if current_version_data.is_empty():
		print("[WhatsNewModal] No patch notes found for version %s" % current_version)
		# Still show something
		_display_fallback_notes(current_version)
	else:
		_display_version_notes(current_version_data)

	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.grab_focus()

	if mark_as_seen:
		GameConfig.mark_patch_notes_seen()

## Show the modal with all recent patch notes
func show_all_notes() -> void:
	if patch_notes_data.is_empty():
		_load_patch_notes()

	_display_all_notes()

	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.grab_focus()

## Hide the modal
func hide_modal() -> void:
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	closed.emit()

## Get patch notes data for a specific version
func _get_version_data(version: String) -> Dictionary:
	var versions = patch_notes_data.get("versions", [])
	for v in versions:
		if v.get("version", "") == version:
			return v
	return {}

## Display patch notes for a specific version
func _display_version_notes(version_data: Dictionary) -> void:
	var version = version_data.get("version", "Unknown")
	var title = version_data.get("title", "")
	var date = version_data.get("date", "")

	title_label.text = "What's New"
	version_label.text = "Version %s - %s" % [version, title]
	if not date.is_empty():
		version_label.text += " (%s)" % date

	# Build content
	var content = ""

	# Highlights section
	var highlights = version_data.get("highlights", [])
	if highlights.size() > 0:
		content += "[b][color=#88ccff]Highlights:[/color][/b]\n"
		for highlight in highlights:
			content += "  [color=#aaffaa]*[/color] %s\n" % highlight
		content += "\n"

	# Sections
	var sections = version_data.get("sections", {})

	# Added
	var added = sections.get("added", [])
	if added.size() > 0:
		content += "[b][color=#88ff88]Added:[/color][/b]\n"
		for item in added:
			content += "  [color=#88ff88]+[/color] %s\n" % item
		content += "\n"

	# Fixed
	var fixed = sections.get("fixed", [])
	if fixed.size() > 0:
		content += "[b][color=#ffcc88]Fixed:[/color][/b]\n"
		for item in fixed:
			content += "  [color=#ffcc88]*[/color] %s\n" % item
		content += "\n"

	# Changed
	var changed = sections.get("changed", [])
	if changed.size() > 0:
		content += "[b][color=#ccccff]Changed:[/color][/b]\n"
		for item in changed:
			content += "  [color=#ccccff]~[/color] %s\n" % item
		content += "\n"

	content_label.bbcode_enabled = true
	content_label.text = content

## Display all patch notes
func _display_all_notes() -> void:
	title_label.text = "Patch Notes"
	version_label.text = "Recent Updates"

	var content = ""
	var versions = patch_notes_data.get("versions", [])

	for i in range(mini(versions.size(), 3)):  # Show last 3 versions
		var version_data = versions[i]
		var version = version_data.get("version", "Unknown")
		var title = version_data.get("title", "")
		var date = version_data.get("date", "")

		content += "[b][color=#ffffff]v%s - %s[/color][/b]" % [version, title]
		if not date.is_empty():
			content += " [color=#888888](%s)[/color]" % date
		content += "\n"

		# Highlights only for all notes view
		var highlights = version_data.get("highlights", [])
		for highlight in highlights:
			content += "  [color=#aaffaa]*[/color] %s\n" % highlight

		content += "\n"

	content_label.bbcode_enabled = true
	content_label.text = content

## Display fallback when no patch notes found
func _display_fallback_notes(version: String) -> void:
	title_label.text = "What's New"
	version_label.text = "Version %s" % version

	content_label.bbcode_enabled = true
	content_label.text = "[color=#aaaaaa]No detailed patch notes available for this version.\n\nCheck the CHANGELOG.md file for the latest updates.[/color]"

## Handle close button
func _on_close_pressed() -> void:
	hide_modal()

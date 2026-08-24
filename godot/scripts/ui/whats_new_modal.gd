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

## Why the patch notes are not on screen. Three genuinely different things used to
## collapse into one reassuring sentence -- "No detailed patch notes available for
## this version." -- which is a value meaning "I could not tell" rendered as a value
## meaning "fine" (Pip's ruling, 2026-08-23).
##
##   OK            data loaded; if the modal still shows a fallback it is because
##                 this version genuinely has no entry. That is the ONLY case where
##                 burning the version with mark_patch_notes_seen() is honest.
##   FILE_MISSING  data/patch_notes.json is not in the build at all.
##   OPEN_FAILED   the file is there and FileAccess would not open it.
##   PARSE_FAILED  the file is there and is not valid JSON.
##   BAD_SHAPE     valid JSON, but not the object-with-"versions" the modal reads.
##
## The last four all mean "the build is broken", not "this release was quiet".
enum LoadStatus { NOT_LOADED, OK, FILE_MISSING, OPEN_FAILED, PARSE_FAILED, BAD_SHAPE }

# Patch notes data
var patch_notes_data: Dictionary = {}
var current_version_data: Dictionary = {}
var load_status: int = LoadStatus.NOT_LOADED

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

## Load patch notes from JSON file. Records WHY it failed in load_status.
func _load_patch_notes() -> void:
	if not FileAccess.file_exists(PATCH_NOTES_PATH):
		load_status = LoadStatus.FILE_MISSING
		print("[WhatsNewModal] ERROR: Patch notes file not found at %s" % PATCH_NOTES_PATH)
		return

	var file = FileAccess.open(PATCH_NOTES_PATH, FileAccess.READ)
	if not file:
		load_status = LoadStatus.OPEN_FAILED
		print("[WhatsNewModal] ERROR: Could not open patch notes file at %s (FileAccess error %d)"
			% [PATCH_NOTES_PATH, FileAccess.get_open_error()])
		return

	var json_text = file.get_as_text()
	file.close()

	load_status = ingest_patch_notes_text(json_text)

## Parse patch-notes JSON text and record the outcome. Split out from the file I/O so
## the failure branches are reachable from a test without staging a broken build.
## Returns a LoadStatus and sets patch_notes_data (left empty on any failure).
func ingest_patch_notes_text(json_text: String) -> int:
	var json = JSON.new()
	var error = json.parse(json_text)
	if error != OK:
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Failed to parse patch notes JSON at line %d: %s"
			% [json.get_error_line(), json.get_error_message()])
		return LoadStatus.PARSE_FAILED

	var parsed = json.get_data()
	# Valid JSON is not the same as the shape this modal reads. A bare array or a
	# string parses fine and would then assign into a typed Dictionary and blow up,
	# or silently yield zero versions -- another "could not tell" wearing "fine".
	if typeof(parsed) != TYPE_DICTIONARY or not (parsed.get("versions", null) is Array):
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Patch notes JSON is not an object with a 'versions' array")
		return LoadStatus.BAD_SHAPE

	patch_notes_data = parsed
	print("[WhatsNewModal] Loaded patch notes with %d versions" % patch_notes_data["versions"].size())
	return LoadStatus.OK

## Show the modal with patch notes for current version
func show_modal(mark_as_seen: bool = true) -> void:
	if patch_notes_data.is_empty():
		_load_patch_notes()

	# Find current version's patch notes
	var current_version = GameConfig.get_current_version()
	current_version_data = _get_version_data(current_version)

	var has_entry := not current_version_data.is_empty()
	if has_entry:
		_display_version_notes(current_version_data)
	else:
		if load_status == LoadStatus.OK:
			print("[WhatsNewModal] Patch notes loaded, but no entry for version %s"
				% current_version)
		else:
			print("[WhatsNewModal] ERROR: Cannot show patch notes for version %s -- %s"
				% [current_version, describe_load_status(load_status)])
		_display_fallback_notes(current_version)

	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.grab_focus()

	# Do NOT burn the version when the fallback fired because the DATA was missing or
	# broken. mark_patch_notes_seen() writes last_seen_version = CURRENT_VERSION, and
	# has_unseen_patch_notes() is an inequality against that, so marking here means the
	# player never gets a second chance at the real notes -- not after a repaired
	# build, not ever, for this version. Before 2026-08-24 this ran unconditionally,
	# so a build shipped without data/patch_notes.json silently consumed the player's
	# one showing. Only "loaded fine, this version has no entry" is honest to mark.
	if mark_as_seen and (has_entry or load_status == LoadStatus.OK):
		GameConfig.mark_patch_notes_seen()
	elif mark_as_seen:
		print("[WhatsNewModal] NOT marking %s seen -- %s. The player is owed another look."
			% [current_version, describe_load_status(load_status)])

## Whether seeing the modal should consume this version's one showing.
## has_entry OR "the data loaded and simply has nothing for this version".
static func should_mark_seen(has_entry: bool, status: int) -> bool:
	return has_entry or status == LoadStatus.OK

## Human-readable cause, for logs. Never shown to the player.
static func describe_load_status(status: int) -> String:
	match status:
		LoadStatus.OK:
			return "patch notes loaded"
		LoadStatus.FILE_MISSING:
			return "data/patch_notes.json is missing from this build"
		LoadStatus.OPEN_FAILED:
			return "data/patch_notes.json could not be opened"
		LoadStatus.PARSE_FAILED:
			return "data/patch_notes.json is not valid JSON"
		LoadStatus.BAD_SHAPE:
			return "data/patch_notes.json is not an object with a 'versions' array"
		_:
			return "patch notes were never loaded"

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

## Display fallback when no patch notes are on screen.
##
## The wording is gentle either way -- a player does not need a stack trace -- but it
## must not CLAIM there are no notes when the truth is that the notes could not be
## read. "No detailed patch notes available for this version" told a player the
## release was quiet when the real story was a missing or corrupt data file, and the
## precise cause is in the log next to this (describe_load_status).
func _display_fallback_notes(version: String) -> void:
	title_label.text = "What's New"
	version_label.text = "Version %s" % version

	var body := ""
	if load_status == LoadStatus.OK:
		body = "No detailed patch notes were written for this version."
	else:
		# Deliberately says the notes could not be LOADED, not that none exist.
		body = ("Patch notes could not be loaded for this build.\n"
			+ "This is a problem with the build, not with the release --\n"
			+ "there may well be notes to read.")

	content_label.bbcode_enabled = true
	content_label.text = "[color=#aaaaaa]%s\n\nVisit pdoom1.com for the latest updates.[/color]" % body

## Handle close button
func _on_close_pressed() -> void:
	hide_modal()

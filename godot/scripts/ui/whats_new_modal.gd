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

## Why the patch notes are not on screen.
##
## WHY THIS ENUM EXISTS (Pip's ruling, 2026-08-23): this modal "collapses three
## different failures into one reassuring sentence -- let's do the opposite of
## that." The sentence was "No detailed patch notes available for this version.",
## shown identically whether data/patch_notes.json was absent from the build,
## present but corrupt, or present, valid and simply silent about this release.
## A packaging failure, a corruption and a content gap wearing the same words --
## and only the third of them was the words being true.
##
##   NOT_LOADED    nothing has tried to read the file yet.
##   OK            data loaded; if the modal still shows a fallback it is because
##                 this version genuinely has no entry.
##   FILE_MISSING  data/patch_notes.json is not in the build at all.
##   OPEN_FAILED   the file is there and FileAccess would not open it.
##   PARSE_FAILED  the file is there and is not valid JSON.
##   BAD_SHAPE     valid JSON, but not the object-with-"versions" the modal reads.
##
## OK is the only row that means "this release was quiet". The other five mean
## the BUILD is broken, and they are told apart in status_report() below.
enum LoadStatus { NOT_LOADED, OK, FILE_MISSING, OPEN_FAILED, PARSE_FAILED, BAD_SHAPE }

# Patch notes data
var patch_notes_data: Dictionary = {}
var current_version_data: Dictionary = {}
var load_status: int = LoadStatus.NOT_LOADED

## Built on demand, not declared in the .tscn: it exists only on the paths where
## the player has something worth reporting, so an absent button is itself a
## statement that nothing is wrong.
var report_button: Button = null

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

	if event is InputEventKey and event.pressed and not event.echo:
		# R comes FIRST and consumes the event. The report affordance only exists
		# on a broken-build path, and a keyboard-only player reaching it must not
		# have the modal close out from under them on the same keystroke.
		if event.keycode == KEY_R and report_button != null and report_button.visible:
			_on_report_pressed()
			get_viewport().set_input_as_handled()
			return
		# Handle keyboard shortcuts to close
		if event.keycode == KEY_ESCAPE or event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			_on_close_pressed()
			get_viewport().set_input_as_handled()

# ---------------------------------------------------------------------------
# The table that makes the collapse impossible to reintroduce
# ---------------------------------------------------------------------------

## Everything that differs between the six outcomes, in ONE place: the words the
## player reads, the code they can quote, whether it is a build defect, and the
## developer-facing cause for the log.
##
## RULING: 2026-08-24 -- a player-facing surface must not collapse distinct failures into one reassuring sentence: each cause gets its own words, its own consequence and its own way for the player to report it -- flavour: silent-failure -- mechanism: this table and godot/tests/unit/test_whats_new_states.gd, which fails if any two rows share a body or a code
##
## Keeping them in one match is the point. The original defect was four rows
## sharing one sentence; a state cannot now be added without someone writing its
## own words, its own reference code and its own consequence on the same screen,
## and test_whats_new_states.gd fails if any two rows share a body or a code.
##
## Keys:
##   body      player-facing. No jargon, no file paths, no error numbers. It must
##             say WHICH of the three stories this is, because that is the whole
##             ruling: a player who reads "the notes could not be read" has
##             learned something the old sentence actively hid from them.
##   code      short, stable, quotable. The diagnostic route: this is a shipped
##             build with no console, so the reference code IS the player's only
##             way to tell us which of the five they hit. Empty for OK -- there
##             is nothing to report, and offering a code would invent a defect.
##   is_defect drives BOTH consequences: whether the version is burned (see
##             should_mark_seen) and whether the report affordance appears.
##   cause     developer-facing, for the log only. Never rendered.
static func status_report(status: int) -> Dictionary:
	match status:
		LoadStatus.OK:
			return {
				"code": "",
				"is_defect": false,
				"cause": "patch notes loaded",
				"body": ("No detailed patch notes were written for this version."
					+ "\n\nNothing is broken -- this release simply did not come with"
					+ " a write-up."),
			}
		LoadStatus.FILE_MISSING:
			return {
				"code": "PN-MISSING",
				"is_defect": true,
				"cause": "data/patch_notes.json is missing from this build",
				"body": ("This build did not ship with its patch notes, so there is"
					+ " nothing here to show you."
					+ "\n\nThat is a packaging mistake on our end, not a quiet"
					+ " release. There are very likely notes for this version --"
					+ " they did not make it into the download."),
			}
		LoadStatus.OPEN_FAILED:
			return {
				"code": "PN-LOCKED",
				"is_defect": true,
				"cause": "data/patch_notes.json could not be opened",
				"body": ("The patch notes are in this build, but the game was not"
					+ " able to open them."
					+ "\n\nThat usually means this copy of the game is damaged or"
					+ " its files are locked by something else -- reinstalling"
					+ " normally fixes it."),
			}
		LoadStatus.PARSE_FAILED:
			return {
				"code": "PN-DAMAGED",
				"is_defect": true,
				"cause": "data/patch_notes.json is not valid JSON",
				"body": ("The patch notes in this build are damaged, so they could"
					+ " not be loaded."
					+ "\n\nThe notes for this version do exist -- this copy of them"
					+ " is corrupt."),
			}
		LoadStatus.BAD_SHAPE:
			return {
				"code": "PN-UNEXPECTED",
				"is_defect": true,
				"cause": "data/patch_notes.json is not an object with a 'versions' array",
				"body": ("The patch notes in this build were read, but they are not"
					+ " arranged the way this screen expects, so none of them could"
					+ " be shown."
					+ "\n\nThat is a fault in the build, not an empty release."),
			}
		_:
			return {
				"code": "PN-NOTLOADED",
				"is_defect": true,
				"cause": "patch notes were never loaded",
				"body": ("This screen opened before the patch notes had been read,"
					+ " so it has nothing to show yet."
					+ "\n\nThat is a fault in the build rather than a release with"
					+ " nothing in it."),
			}

## Human-readable cause, for logs. Never shown to the player.
static func describe_load_status(status: int) -> String:
	return String(status_report(status)["cause"])

## Whether seeing the modal should consume this version's one showing.
##
## THE RULE, and it is the subtle part. GameConfig.mark_patch_notes_seen() writes
## last_seen_version = CURRENT_VERSION, and has_unseen_patch_notes() is an
## inequality against that. So marking is IRREVERSIBLE for this version: it is
## not "the player has been shown the notes", it is "the player will never be
## offered the notes for this version again", including from a repaired build.
##
## Mark seen only when the player has actually received everything this version
## has to give:
##   - real notes were rendered (has_entry), or
##   - the data was READABLE and genuinely contains nothing for this version (OK).
## In every other case the game does not KNOW what this version has to say, and
## spending the player's one showing on that ignorance is the expensive mistake:
## a build shipped without data/patch_notes.json used to consume it silently.
##
## Read the second clause as "not a build defect" -- OK is the only non-defect
## row in status_report(), and the two must stay in step.
static func should_mark_seen(has_entry: bool, status: int) -> bool:
	return has_entry or not bool(status_report(status)["is_defect"])

# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

## Load patch notes from the shipped JSON file. Records WHY it failed in load_status.
func _load_patch_notes() -> void:
	load_status = load_from_path(PATCH_NOTES_PATH)

## Read and ingest a patch-notes file, returning a LoadStatus.
##
## Takes the path as an argument purely so a test can reach the FILE_MISSING
## branch without staging a broken build. A failure branch nothing can reach is
## a failure branch nobody has checked.
func load_from_path(path: String) -> int:
	if not FileAccess.file_exists(path):
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Patch notes file not found at %s" % path)
		return LoadStatus.FILE_MISSING

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Could not open patch notes file at %s (FileAccess error %d)"
			% [path, FileAccess.get_open_error()])
		return LoadStatus.OPEN_FAILED

	var json_text := file.get_as_text()
	file.close()
	return ingest_patch_notes_text(json_text)

## Parse patch-notes JSON text and report the outcome. Split out from the file I/O
## so the parse failures are reachable from a test without a corrupt file on disk.
## Sets patch_notes_data (left empty on any failure).
func ingest_patch_notes_text(json_text: String) -> int:
	var json := JSON.new()
	var error := json.parse(json_text)
	if error != OK:
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Failed to parse patch notes JSON at line %d: %s"
			% [json.get_error_line(), json.get_error_message()])
		return LoadStatus.PARSE_FAILED

	var parsed = json.get_data()
	# Valid JSON is not the same as the shape this modal reads. A bare array or a
	# string parses fine and would then either blow up on assignment into a typed
	# Dictionary or silently yield zero versions -- another "could not tell"
	# wearing "fine".
	if typeof(parsed) != TYPE_DICTIONARY or not (parsed.get("versions", null) is Array):
		patch_notes_data = {}
		print("[WhatsNewModal] ERROR: Patch notes JSON is not an object with a 'versions' array")
		return LoadStatus.BAD_SHAPE

	patch_notes_data = parsed
	print("[WhatsNewModal] Loaded patch notes with %d versions" % patch_notes_data["versions"].size())
	return LoadStatus.OK

# ---------------------------------------------------------------------------
# Showing
# ---------------------------------------------------------------------------

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

	if mark_as_seen and should_mark_seen(has_entry, load_status):
		GameConfig.mark_patch_notes_seen()
	elif mark_as_seen:
		print("[WhatsNewModal] NOT marking %s seen -- %s. The player is owed another look."
			% [current_version, describe_load_status(load_status)])

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
	_set_report_affordance_visible(false)

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
	_set_report_affordance_visible(false)

## Display the fallback when no patch notes are on screen.
##
## This is where the ruling lands. There is no shared "nothing to show" sentence
## any more: the body, the reference code and the report affordance all come from
## status_report(load_status), so the three stories reach the player as three
## different screens.
func _display_fallback_notes(version: String) -> void:
	title_label.text = "What's New"
	version_label.text = "Version %s" % version

	var row := status_report(load_status)
	var body := String(row["body"])
	var is_defect := bool(row["is_defect"])

	if is_defect:
		# The diagnostic route, in the player's hands. A shipped build has no
		# console; without a quotable code, "the patch notes screen was blank" is
		# an unactionable report and all five causes look identical again.
		body += ("\n\n[color=#ffcc88]Reference code: %s[/color]"
			+ "\n\nUse Report this build (R) below -- the code and this build's"
			+ " details travel with the report.") % String(row["code"])
	else:
		body += "\n\nVisit pdoom1.com for the latest updates."

	content_label.bbcode_enabled = true
	content_label.text = "[color=#aaaaaa]%s[/color]" % body
	_set_report_affordance_visible(is_defect)

# ---------------------------------------------------------------------------
# The report route
# ---------------------------------------------------------------------------

## Build (once) and show/hide the report button.
func _set_report_affordance_visible(should_show: bool) -> void:
	if report_button == null:
		if not should_show:
			return
		report_button = Button.new()
		report_button.name = "ReportBuildButton"
		report_button.text = "Report this build (R)"
		report_button.tooltip_text = ("Copies the details -- including the reference"
			+ " code -- and opens a pre-filled report in your browser")
		report_button.custom_minimum_size = Vector2(200, 45)
		report_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		report_button.pressed.connect(_on_report_pressed)
		close_button.get_parent().add_child(report_button)
		close_button.get_parent().move_child(report_button, close_button.get_index())
	report_button.visible = should_show

## The report a player sends when this screen could not read its own data.
##
## Pure enough to read in a test: it builds and frees its own BugReporter, touches
## no clipboard and opens no browser. Returns {} for a non-defect status -- there
## is nothing to report when a release was simply quiet, and manufacturing a bug
## report for it would be the same lie in the other direction.
static func build_defect_report(status: int, version: String) -> Dictionary:
	var row := status_report(status)
	if not bool(row["is_defect"]):
		return {}

	var reporter := BugReporter.new()
	var report := reporter.create_bug_report(
		BugReporter.ReportType.BUG,
		"Patch notes would not load: %s" % String(row["code"]),
		("The What's New screen could not show the notes for version %s."
			+ "\n\nReference code: %s"
			+ "\n\nWhat the game recorded: %s (%s)."
			+ "\n\nThis is a build problem rather than a release with no notes,"
			+ " which is why the game is asking for a report rather than shrugging.")
			% [version, String(row["code"]), String(row["cause"]), PATCH_NOTES_PATH],
		"Open What's New (it opens by itself on the first launch after an update).",
		"The patch notes for version %s." % version,
		String(row["body"]).replace("\n\n", " ")
	)
	reporter.free()
	return report

func _on_report_pressed() -> void:
	var report := build_defect_report(load_status, GameConfig.get_current_version())
	if report.is_empty():
		return
	# Clipboard AND browser, the same pairing bug_report_panel.gd uses: GitHub
	# truncates long query strings, and a player whose browser never opens still
	# has the whole thing in hand.
	DisplayServer.clipboard_set(BugReporter.format_for_transport(report))
	OS.shell_open(BugReporter.github_issue_url(report))
	if report_button != null:
		report_button.text = "Details copied -- check your browser"

## Handle close button
func _on_close_pressed() -> void:
	hide_modal()

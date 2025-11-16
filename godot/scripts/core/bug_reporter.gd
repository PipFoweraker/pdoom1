extends Node
## Privacy-focused bug reporting system for P(Doom)
##
## Collects minimal necessary information for debugging while protecting user privacy.
## Offers options for local save with optional attribution for contributor recognition.
##
## @tutorial: See docs/PRIVACY.md for privacy policy details
## @tutorial: See docs/CONTRIBUTOR_REWARDS.md for contributor recognition program

class_name BugReporter

## Emitted when a bug report is saved
signal report_saved(filepath: String)

## Emitted when a bug report save fails
signal report_save_failed(error: String)

const REPORTS_DIR = "user://bug_reports"

## Report types available
enum ReportType {
	BUG,              ## Bug or error in the game
	FEATURE_REQUEST,  ## Suggestion for new feature
	FEEDBACK          ## General feedback or comment
}

func _ready():
	ensure_reports_directory()

## Ensure bug reports directory exists
func ensure_reports_directory() -> void:
	var dir = DirAccess.open("user://")
	if dir:
		if not dir.dir_exists("bug_reports"):
			var err = dir.make_dir("bug_reports")
			if err != OK:
				push_error("Failed to create bug_reports directory: " + error_string(err))
	else:
		push_error("Failed to access user:// directory")

## Collect minimal system information for debugging
## Only collects essential technical details, no personal information
func collect_system_info() -> Dictionary:
	return {
		"os_type": OS.get_name(),  # Windows/Linux/macOS/etc
		"godot_version": Engine.get_version_info().string,
		"game_version": ProjectSettings.get_setting("application/config/version", "unknown"),
		"timestamp": Time.get_datetime_string_from_system(true)  # UTC ISO 8601 format
	}

## Create a structured bug report
##
## @param report_type: Type of report (BUG, FEATURE_REQUEST, or FEEDBACK)
## @param title: Brief summary of the issue
## @param description: Detailed description
## @param steps_to_reproduce: How to reproduce the issue (optional)
## @param expected_behavior: What should happen (optional)
## @param actual_behavior: What actually happens (optional)
## @param include_attribution: Whether to include user's name in report
## @param attribution_name: Name for attribution (if requested)
## @param contact_info: Optional contact information
## @param include_screenshot: Whether to include a screenshot
## @param screenshot_data: Screenshot image data (if included)
## @param include_save: Whether to include save file
## @param save_file_path: Path to save file (if included)
## @returns Dictionary with structured bug report ready for saving
func create_bug_report(
	report_type: ReportType,
	title: String,
	description: String,
	steps_to_reproduce: String = "",
	expected_behavior: String = "",
	actual_behavior: String = "",
	include_attribution: bool = false,
	attribution_name: String = "",
	contact_info: String = "",
	include_screenshot: bool = false,
	_screenshot_data: Image = null,  # Unused - metadata only
	include_save: bool = false,
	_save_file_path: String = ""  # Unused - metadata only
) -> Dictionary:

	var system_info = collect_system_info()

	var report = {
		"report_type": ReportType.keys()[report_type].to_lower(),
		"title": title,
		"description": description,
		"system_info": system_info,
		"created_at": system_info["timestamp"]
	}

	# Optional fields
	if steps_to_reproduce != "":
		report["steps_to_reproduce"] = steps_to_reproduce
	if expected_behavior != "":
		report["expected_behavior"] = expected_behavior
	if actual_behavior != "":
		report["actual_behavior"] = actual_behavior

	# Attribution (optional, for contributor recognition)
	if include_attribution and attribution_name != "":
		report["attribution"] = {
			"name": attribution_name,
			"contact": contact_info if contact_info != "" else null
		}
	else:
		report["attribution"] = null

	# Attachments metadata
	report["attachments"] = {
		"screenshot_included": include_screenshot,
		"save_file_included": include_save
	}

	return report

## Save bug report to local file system
##
## @param report: Bug report dictionary
## @param screenshot: Optional screenshot image to save alongside report
## @param save_file_path: Optional save file to copy alongside report
## @returns String: Path to saved report file, or empty string on error
func save_report_locally(report: Dictionary, screenshot: Image = null, save_file_path: String = "") -> String:
	var timestamp = Time.get_datetime_string_from_system(true).replace(":", "-").replace("T", "_")
	var base_filename = "bug_report_%s" % timestamp
	var report_filename = "%s.json" % base_filename
	var report_filepath = "%s/%s" % [REPORTS_DIR, report_filename]

	# Handle filename collisions by adding a counter
	var counter = 1
	while FileAccess.file_exists(report_filepath):
		report_filename = "%s_%02d.json" % [base_filename, counter]
		report_filepath = "%s/%s" % [REPORTS_DIR, report_filename]
		counter += 1

	# Save main report JSON
	var file = FileAccess.open(report_filepath, FileAccess.WRITE)
	if file == null:
		var err = FileAccess.get_open_error()
		push_error("Failed to open report file for writing: " + error_string(err))
		report_save_failed.emit("Failed to save report: " + error_string(err))
		return ""

	file.store_string(JSON.stringify(report, "\t"))
	file.close()

	# Save screenshot if included
	if screenshot != null and report["attachments"]["screenshot_included"]:
		var screenshot_filename = "%s_screenshot.png" % base_filename
		var screenshot_filepath = "%s/%s" % [REPORTS_DIR, screenshot_filename]
		var save_err = screenshot.save_png(screenshot_filepath)
		if save_err != OK:
			push_warning("Failed to save screenshot: " + error_string(save_err))
		else:
			report["attachments"]["screenshot_filename"] = screenshot_filename

	# Copy save file if included
	if save_file_path != "" and report["attachments"]["save_file_included"]:
		if FileAccess.file_exists(save_file_path):
			var save_filename = "%s_savefile.sav" % base_filename
			var save_filepath = "%s/%s" % [REPORTS_DIR, save_filename]
			var dir = DirAccess.open("user://")
			var copy_err = dir.copy(save_file_path, save_filepath)
			if copy_err != OK:
				push_warning("Failed to copy save file: " + error_string(copy_err))
			else:
				report["attachments"]["save_filename"] = save_filename

	print("Bug report saved: %s" % report_filepath)
	report_saved.emit(report_filepath)
	return report_filepath

## Format bug report for GitHub issue submission
##
## @param report: Bug report dictionary
## @returns Dictionary with 'title' and 'body' formatted for GitHub API
func format_for_github(_report: Dictionary) -> Dictionary:
	# Create GitHub issue title
	var issue_type = _report["report_type"].replace("_", " ").capitalize()
	var title = "[%s] %s" % [issue_type, _report["title"]]

	# Create GitHub issue body
	var body_parts = []

	# Header
	body_parts.append("**Type:** %s" % issue_type)
	body_parts.append("")

	# Description
	body_parts.append("**Description:**")
	body_parts.append(_report["description"])
	body_parts.append("")

	# Optional sections
	if "steps_to_reproduce" in _report and _report["steps_to_reproduce"] != "":
		body_parts.append("**Steps to Reproduce:**")
		body_parts.append(_report["steps_to_reproduce"])
		body_parts.append("")

	if "expected_behavior" in _report and _report["expected_behavior"] != "":
		body_parts.append("**Expected Behavior:**")
		body_parts.append(_report["expected_behavior"])
		body_parts.append("")

	if "actual_behavior" in _report and _report["actual_behavior"] != "":
		body_parts.append("**Actual Behavior:**")
		body_parts.append(_report["actual_behavior"])
		body_parts.append("")

	# System information
	body_parts.append("**System Information:**")
	var system_info = _report["system_info"]
	body_parts.append("- OS: %s" % system_info["os_type"])
	body_parts.append("- Godot: %s" % system_info["godot_version"])
	body_parts.append("- Game Version: %s" % system_info["game_version"])
	body_parts.append("- Reported: %s" % system_info["timestamp"])
	body_parts.append("")

	# Attribution
	if _report.get("attribution") != null:
		var attribution = _report["attribution"]
		body_parts.append("**Reported by:** %s" % attribution["name"])
		if attribution.get("contact") != null:
			body_parts.append("**Contact:** %s" % attribution["contact"])
	else:
		body_parts.append("**Reported by:** Anonymous")

	# Labels suggestion
	body_parts.append("")
	body_parts.append("---")
	body_parts.append("*Submitted via in-game bug reporter*")

	return {
		"title": title,
		"body": "\n".join(body_parts)
	}

## Get list of recent bug reports from local storage
##
## @param limit: Maximum number of reports to return
## @returns Array of report file paths (newest first)
func get_recent_reports(limit: int = 10) -> Array:
	var report_files = []

	var dir = DirAccess.open(REPORTS_DIR)
	if dir == null:
		return []

	dir.list_dir_begin()
	var filename = dir.get_next()
	while filename != "":
		if filename.begins_with("bug_report_") and filename.ends_with(".json"):
			var filepath = "%s/%s" % [REPORTS_DIR, filename]
			var modified_time = FileAccess.get_modified_time(filepath)
			report_files.append({"path": filepath, "time": modified_time})
		filename = dir.get_next()
	dir.list_dir_end()

	# Sort by modification time (newest first)
	report_files.sort_custom(func(a, b): return a["time"] > b["time"])

	# Return just the paths, limited to requested count
	var result = []
	for i in range(min(limit, report_files.size())):
		result.append(report_files[i]["path"])

	return result

## Capture screenshot of current viewport
##
## @returns Image: Screenshot as Image object
func capture_screenshot() -> Image:
	var viewport = get_viewport()
	var texture = viewport.get_texture()
	var image = texture.get_image()
	return image

## Get formatted report type name
##
## @param report_type: ReportType enum value
## @returns String: Human-readable report type name
static func get_report_type_name(report_type: ReportType) -> String:
	match report_type:
		ReportType.BUG:
			return "Bug Report"
		ReportType.FEATURE_REQUEST:
			return "Feature Request"
		ReportType.FEEDBACK:
			return "Feedback"
		_:
			return "Unknown"

## Check if reports directory exists and is writable
func is_reports_directory_ready() -> bool:
	var dir = DirAccess.open(REPORTS_DIR)
	return dir != null

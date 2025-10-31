extends Node
## Screenshot Manager - Captures and saves screenshots

const SCREENSHOT_DIR = "user://screenshots"

var screenshot_count: int = 0

func _ready():
	# Create screenshot directory
	var dir = DirAccess.open("user://")
	if not dir.dir_exists("screenshots"):
		dir.make_dir("screenshots")

	# Count existing screenshots
	_count_existing_screenshots()

	# Connect to keybind signals
	KeybindManager.screenshot_requested.connect(_on_screenshot_requested)

	print("[ScreenshotManager] Ready. Screenshot directory: %s" % OS.get_user_data_dir() + "/screenshots")

func _on_screenshot_requested():
	take_screenshot()

## Count existing screenshots to avoid overwriting
func _count_existing_screenshots():
	var dir = DirAccess.open(SCREENSHOT_DIR)
	if not dir:
		return

	dir.list_dir_begin()
	var file_name = dir.get_next()

	while file_name != "":
		if file_name.ends_with(".png"):
			screenshot_count += 1
		file_name = dir.get_next()

	dir.list_dir_end()

## Take a screenshot
func take_screenshot() -> String:
	var image = get_viewport().get_texture().get_image()

	# Generate filename with timestamp
	var timestamp = Time.get_datetime_dict_from_system()
	var filename = "pdoom_%04d%02d%02d_%02d%02d%02d.png" % [
		timestamp.year,
		timestamp.month,
		timestamp.day,
		timestamp.hour,
		timestamp.minute,
		timestamp.second
	]

	var path = SCREENSHOT_DIR.path_join(filename)

	# Save image
	var err = image.save_png(path)

	if err == OK:
		var full_path = OS.get_user_data_dir().path_join("screenshots").path_join(filename)
		print("[Screenshot] Saved: %s" % full_path)
		screenshot_count += 1

		# Show notification
		NotificationManager.success("Screenshot saved!")

		return full_path
	else:
		push_error("Failed to save screenshot: %s" % err)
		NotificationManager.error("Screenshot failed!")
		return ""


## Open screenshot folder in file explorer
func open_screenshot_folder():
	var path = OS.get_user_data_dir().path_join("screenshots")
	OS.shell_open(path)

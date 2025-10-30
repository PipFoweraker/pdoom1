extends Control
## Settings Menu - Comprehensive settings management

# UI References
@onready var master_volume_slider = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/Slider
@onready var master_volume_label = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/ValueLabel
@onready var sfx_volume_slider = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/Slider
@onready var sfx_volume_label = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/ValueLabel
@onready var graphics_quality_option = $VBox/SettingsContainer/GraphicsSettings/QualityRow/OptionButton
@onready var fullscreen_checkbox = $VBox/SettingsContainer/GraphicsSettings/FullscreenRow/CheckBox
@onready var difficulty_option = $VBox/SettingsContainer/GameplaySettings/DifficultyRow/OptionButton

# Settings data
var settings = {
	"master_volume": 80,
	"sfx_volume": 80,
	"graphics_quality": 1,  # 0=Low, 1=Medium, 2=High
	"fullscreen": false,
	"difficulty": 1  # 0=Easy, 1=Standard, 2=Hard
}

var original_settings = {}

func _ready():
	print("[SettingsMenu] Initializing...")

	# Load current settings
	load_settings()

	# Update UI to reflect current settings
	update_ui_from_settings()

	# Store original settings for cancel functionality
	original_settings = settings.duplicate()

func load_settings():
	"""Load settings from config file or use defaults"""
	# TODO: Load from config file when implemented
	# For now, use defaults
	print("[SettingsMenu] Using default settings")

func save_settings():
	"""Save settings to config file"""
	# TODO: Implement config file saving
	print("[SettingsMenu] Settings saved: ", settings)

	# Apply settings immediately
	apply_settings()

func apply_settings():
	"""Apply current settings to the game"""
	print("[SettingsMenu] Applying settings...")

	# Audio settings
	# TODO: Apply to audio bus when audio system is implemented
	AudioServer.set_bus_volume_db(0, linear_to_db(settings.master_volume / 100.0))

	# Graphics settings
	if settings.fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)

	# Difficulty is applied when starting new game
	# TODO: Store in global config for game manager to access

func update_ui_from_settings():
	"""Update all UI elements to reflect current settings"""
	master_volume_slider.value = settings.master_volume
	master_volume_label.text = "%d%%" % settings.master_volume

	sfx_volume_slider.value = settings.sfx_volume
	sfx_volume_label.text = "%d%%" % settings.sfx_volume

	graphics_quality_option.selected = settings.graphics_quality
	fullscreen_checkbox.button_pressed = settings.fullscreen
	difficulty_option.selected = settings.difficulty

func _on_master_volume_changed(value: float):
	"""Handle master volume slider change"""
	settings.master_volume = int(value)
	master_volume_label.text = "%d%%" % settings.master_volume

	# Apply immediately for preview
	AudioServer.set_bus_volume_db(0, linear_to_db(value / 100.0))

func _on_sfx_volume_changed(value: float):
	"""Handle SFX volume slider change"""
	settings.sfx_volume = int(value)
	sfx_volume_label.text = "%d%%" % settings.sfx_volume

	# TODO: Apply to SFX bus when audio system is implemented

func _on_graphics_quality_changed(index: int):
	"""Handle graphics quality dropdown change"""
	settings.graphics_quality = index
	print("[SettingsMenu] Graphics quality changed to: ", ["Low", "Medium", "High"][index])

func _on_fullscreen_toggled(pressed: bool):
	"""Handle fullscreen checkbox toggle"""
	settings.fullscreen = pressed
	print("[SettingsMenu] Fullscreen: ", pressed)

func _on_difficulty_changed(index: int):
	"""Handle difficulty dropdown change"""
	settings.difficulty = index
	print("[SettingsMenu] Difficulty changed to: ", ["Easy", "Standard", "Hard"][index])

func _on_apply_pressed():
	"""Handle Apply button press"""
	print("[SettingsMenu] Applying and saving settings...")
	save_settings()

	# Show confirmation (TODO: Add visual feedback)
	print("[SettingsMenu] Settings applied successfully!")

func _on_back_pressed():
	"""Handle Back button press"""
	print("[SettingsMenu] Returning to welcome screen...")

	# Restore original settings if not applied
	# (In a real implementation, ask user if they want to save changes)

	# Return to welcome screen
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()

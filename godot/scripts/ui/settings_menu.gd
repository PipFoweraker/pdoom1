extends Control
## Settings Menu - Comprehensive settings management using GameConfig

# UI References
@onready var master_volume_slider = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/Slider
@onready var master_volume_label = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/ValueLabel
@onready var sfx_volume_slider = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/Slider
@onready var sfx_volume_label = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/ValueLabel
@onready var graphics_quality_option = $VBox/SettingsContainer/GraphicsSettings/QualityRow/OptionButton
@onready var fullscreen_checkbox = $VBox/SettingsContainer/GraphicsSettings/FullscreenRow/CheckBox
@onready var difficulty_option = $VBox/SettingsContainer/GameplaySettings/DifficultyRow/OptionButton

func _ready():
	print("[SettingsMenu] Initializing...")

	# Load settings from GameConfig singleton
	update_ui_from_game_config()

func update_ui_from_game_config():
	"""Update all UI elements to reflect GameConfig settings"""
	master_volume_slider.value = GameConfig.master_volume
	master_volume_label.text = "%d%%" % GameConfig.master_volume

	sfx_volume_slider.value = GameConfig.sfx_volume
	sfx_volume_label.text = "%d%%" % GameConfig.sfx_volume

	graphics_quality_option.selected = GameConfig.graphics_quality
	fullscreen_checkbox.button_pressed = GameConfig.fullscreen
	difficulty_option.selected = GameConfig.difficulty

func _on_master_volume_changed(value: float):
	"""Handle master volume slider change"""
	master_volume_label.text = "%d%%" % int(value)
	# Update GameConfig (will apply to audio bus automatically)
	GameConfig.set_setting("master_volume", int(value), false)

func _on_sfx_volume_changed(value: float):
	"""Handle SFX volume slider change"""
	sfx_volume_label.text = "%d%%" % int(value)
	# Update GameConfig (will apply when SFX bus is implemented)
	GameConfig.set_setting("sfx_volume", int(value), false)

func _on_graphics_quality_changed(index: int):
	"""Handle graphics quality dropdown change"""
	print("[SettingsMenu] Graphics quality changed to: ", ["Low", "Medium", "High"][index])
	GameConfig.set_setting("graphics_quality", index, false)

func _on_fullscreen_toggled(pressed: bool):
	"""Handle fullscreen checkbox toggle"""
	print("[SettingsMenu] Fullscreen: ", pressed)
	GameConfig.set_setting("fullscreen", pressed, false)

func _on_difficulty_changed(index: int):
	"""Handle difficulty dropdown change"""
	print("[SettingsMenu] Difficulty changed to: ", ["Easy", "Standard", "Hard"][index])
	GameConfig.set_setting("difficulty", index, false)

func _on_apply_pressed():
	"""Handle Apply button press - save all settings"""
	print("[SettingsMenu] Saving settings to disk...")
	GameConfig.save_config()
	print("[SettingsMenu] Settings saved successfully!")

	# Show confirmation feedback
	_show_confirmation("Settings Saved", "Your settings have been saved successfully!")

func _on_back_pressed():
	"""Handle Back button press"""
	print("[SettingsMenu] Returning to welcome screen...")

	# Ask if user wants to save unsaved changes
	# For now, just return (changes are applied in real-time anyway)

	# Return to welcome screen
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _show_confirmation(title: String, message: String):
	"""Show a confirmation dialog"""
	var dialog = AcceptDialog.new()
	dialog.title = title
	dialog.dialog_text = message
	dialog.size = Vector2(400, 150)
	add_child(dialog)
	dialog.popup_centered()

	# Auto-close after 2 seconds
	await get_tree().create_timer(2.0).timeout
	if is_instance_valid(dialog):
		dialog.queue_free()

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()

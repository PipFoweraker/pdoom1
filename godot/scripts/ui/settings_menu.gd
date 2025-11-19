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
@onready var theme_dropdown = $VBox/SettingsContainer/UISettings/ThemeRow/ThemeDropdown

# Section header labels for icon integration
@onready var audio_label = $VBox/SettingsContainer/AudioSettings/AudioLabel
@onready var graphics_label = $VBox/SettingsContainer/GraphicsSettings/GraphicsLabel
@onready var gameplay_label = $VBox/SettingsContainer/GameplaySettings/GameplayLabel
@onready var ui_label = $VBox/SettingsContainer/UISettings/UILabel

func _ready():
	print("[SettingsMenu] Initializing...")

	# Load settings from GameConfig singleton
	update_ui_from_game_config()

	# Add icons to section headers
	_setup_section_icons()

	# Connect theme dropdown
	theme_dropdown.item_selected.connect(_on_theme_changed)

	# Set current theme
	var themes = ThemeManager.get_available_themes()
	for i in range(themes.size()):
		if themes[i] == ThemeManager.current_theme:
			theme_dropdown.selected = i
			break

func _setup_section_icons():
	"""Add icons to settings section headers"""
	_add_icon_to_label(audio_label, IconLoader.get_settings_icon("audio"))
	_add_icon_to_label(graphics_label, IconLoader.get_settings_icon("graphics"))
	_add_icon_to_label(gameplay_label, IconLoader.get_settings_icon("gameplay"))
	_add_icon_to_label(ui_label, IconLoader.get_settings_icon("theme"))

func _add_icon_to_label(label: Label, icon: Texture2D):
	"""Replace a label with an HBox containing icon + label"""
	if not icon:
		return

	var parent = label.get_parent()
	var index = label.get_index()

	# Create container
	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 8)

	# Create icon
	var icon_rect = TextureRect.new()
	icon_rect.texture = icon
	icon_rect.custom_minimum_size = Vector2(24, 24)
	icon_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	hbox.add_child(icon_rect)

	# Clone label properties to new label
	var new_label = Label.new()
	new_label.text = label.text
	new_label.add_theme_color_override("font_color", label.get_theme_color("font_color"))
	new_label.add_theme_font_size_override("font_size", label.get_theme_font_size("font_size"))
	hbox.add_child(new_label)

	# Replace in parent
	parent.remove_child(label)
	parent.add_child(hbox)
	parent.move_child(hbox, index)
	label.queue_free()

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

func _on_theme_changed(index: int):
	"""Handle theme dropdown change"""
	var themes = ThemeManager.get_available_themes()
	if index < themes.size():
		var theme_name = themes[index]
		print("[SettingsMenu] Theme changed to: ", theme_name)
		ThemeManager.apply_theme(theme_name)
		NotificationManager.info("Theme changed to " + ThemeManager.themes[theme_name].display_name)

func _on_apply_pressed():
	"""Handle Apply button press - save all settings"""
	print("[SettingsMenu] Saving settings to disk...")
	GameConfig.save_config()
	print("[SettingsMenu] Settings saved successfully!")

	# Show confirmation feedback
	NotificationManager.success("Settings saved successfully!")

func _on_back_pressed():
	"""Handle Back button press"""
	print("[SettingsMenu] Returning to welcome screen...")

	# Ask if user wants to save unsaved changes
	# For now, just return (changes are applied in real-time anyway)

	# Return to welcome screen
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()

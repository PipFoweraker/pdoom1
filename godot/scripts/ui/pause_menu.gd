extends Control
## In-Game Pause Menu - Settings and exit options during gameplay

# UI References
@onready var master_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/MasterVolumeRow/Slider
@onready var master_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/MasterVolumeRow/ValueLabel
@onready var sfx_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/SFXVolumeRow/Slider
@onready var sfx_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/SFXVolumeRow/ValueLabel
@onready var music_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/MusicVolumeRow/Slider
@onready var music_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/MusicVolumeRow/ValueLabel

func _ready():
	print("[PauseMenu] Initializing...")
	update_ui_from_game_config()
	hide()  # Start hidden

func update_ui_from_game_config():
	"""Update all UI elements to reflect GameConfig settings"""
	master_volume_slider.value = GameConfig.master_volume
	master_volume_label.text = "%d%%" % GameConfig.master_volume

	sfx_volume_slider.value = GameConfig.sfx_volume
	sfx_volume_label.text = "%d%%" % GameConfig.sfx_volume

	music_volume_slider.value = GameConfig.music_volume
	music_volume_label.text = "%d%%" % GameConfig.music_volume

func _on_master_volume_changed(value: float):
	"""Handle master volume slider change"""
	master_volume_label.text = "%d%%" % int(value)
	GameConfig.set_setting("master_volume", int(value), false)

func _on_sfx_volume_changed(value: float):
	"""Handle SFX volume slider change"""
	sfx_volume_label.text = "%d%%" % int(value)
	GameConfig.set_setting("sfx_volume", int(value), false)

func _on_music_volume_changed(value: float):
	"""Handle Music volume slider change"""
	music_volume_label.text = "%d%%" % int(value)
	GameConfig.set_setting("music_volume", int(value), false)

func _on_resume_pressed():
	"""Resume game"""
	print("[PauseMenu] Resuming game...")
	GameConfig.save_config()  # Save any volume changes
	hide()
	get_tree().paused = false

func _on_main_menu_pressed():
	"""Return to main menu"""
	print("[PauseMenu] Returning to main menu...")
	GameConfig.save_config()
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _on_quit_pressed():
	"""Quit to desktop"""
	print("[PauseMenu] Quitting game...")
	GameConfig.save_config()
	get_tree().quit()

func show_pause_menu():
	"""Show the pause menu and pause the game"""
	print("[PauseMenu] Pausing game...")
	update_ui_from_game_config()
	show()
	get_tree().paused = true

func _input(event: InputEvent):
	"""Handle ESC to close pause menu"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE and visible:
			_on_resume_pressed()
			get_viewport().set_input_as_handled()

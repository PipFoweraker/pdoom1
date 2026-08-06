extends Control
## In-Game Pause Menu - Settings and exit options during gameplay

# UI References
@onready var master_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/MasterVolumeRow/Slider
@onready var master_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/MasterVolumeRow/ValueLabel
@onready var sfx_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/SFXVolumeRow/Slider
@onready var sfx_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/SFXVolumeRow/ValueLabel
@onready var music_volume_slider = $Panel/VBox/SettingsContainer/AudioSettings/MusicVolumeRow/Slider
@onready var music_volume_label = $Panel/VBox/SettingsContainer/AudioSettings/MusicVolumeRow/ValueLabel
## Player-facing track picker (Pip 2026-08-06). Self-contained component -- the pause
## menu only has to tell it when to re-read reality. Volume already lives one row up,
## so nothing is duplicated here.
@onready var music_controls: MusicControls = $Panel/VBox/SettingsContainer/MusicControls

func _ready():
	print("[PauseMenu] Initializing...")
	update_ui_from_game_config()
	# DEPRECATED (v0.11.0): "Save Game" hidden alongside the welcome-screen "Load Game"
	# (single-slot quicksave; see welcome_screen.gd). Dormant, not deleted.
	var save_button := $Panel/VBox/ButtonContainer/SaveButton
	if save_button:
		save_button.visible = false
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

func _on_save_pressed():
	"""L7 (#618): snapshot the current game to the quicksave slot."""
	var save_button: Button = $Panel/VBox/ButtonContainer/SaveButton
	var gm = GameManager  # autoload singleton -- the ONE GameManager (L0 consolidated; the old "../GameManager" scene node was deleted)
	if gm == null or not gm.has_method("save_game"):
		print("[PauseMenu] Save failed: GameManager not found")
		save_button.text = "Save failed"
		return
	if gm.save_game():
		save_button.text = "Saved!"
	else:
		save_button.text = "Save failed"

func _on_resign_pressed():
	"""Accept your fate: end the run and go to the score screen (#959).

	Unpause BEFORE resigning. The game-over screen and the leaderboard
	transition run on a live tree; resigning while paused would fire the
	state update into a frozen scene and leave the player looking at a paused
	game that has quietly ended.
	"""
	print("[PauseMenu] Player accepted their fate -- ending run")
	get_tree().paused = false
	visible = false
	GameManager.resign()


func _on_main_menu_pressed():
	"""Return to main menu"""
	print("[PauseMenu] Returning to main menu...")
	GameConfig.save_config()
	get_tree().paused = false
	SceneTransition.go_to("res://scenes/welcome.tscn")

func _on_quit_pressed():
	"""Quit to desktop"""
	print("[PauseMenu] Quitting game...")
	GameConfig.save_config()
	get_tree().quit()

func show_pause_menu():
	"""Show the pause menu and pause the game"""
	print("[PauseMenu] Pausing game...")
	update_ui_from_game_config()
	# Doom moved while the menu was shut, so the track readout must be re-derived on
	# every open rather than trusted from last time.
	if music_controls != null:
		music_controls.refresh()
	$Panel/VBox/ButtonContainer/SaveButton.text = "Save Game"  # reset any "Saved!" feedback
	show()
	get_tree().paused = true

func _input(event: InputEvent):
	"""Handle ESC to close pause menu"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE and visible:
			_on_resume_pressed()
			get_viewport().set_input_as_handled()

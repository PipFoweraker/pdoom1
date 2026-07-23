extends Control
## Settings Menu - Comprehensive settings management using GameConfig

# UI References
@onready var master_volume_slider = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/Slider
@onready var master_volume_label = $VBox/SettingsContainer/AudioSettings/MasterVolumeRow/ValueLabel
@onready var sfx_volume_slider = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/Slider
@onready var sfx_volume_label = $VBox/SettingsContainer/AudioSettings/SFXVolumeRow/ValueLabel
@onready var music_volume_slider = $VBox/SettingsContainer/AudioSettings/MusicVolumeRow/Slider
@onready var music_volume_label = $VBox/SettingsContainer/AudioSettings/MusicVolumeRow/ValueLabel
@onready var graphics_quality_option = $VBox/SettingsContainer/GraphicsSettings/QualityRow/OptionButton
@onready var fullscreen_checkbox = $VBox/SettingsContainer/GraphicsSettings/FullscreenRow/CheckBox
@onready var difficulty_option = $VBox/SettingsContainer/GameplaySettings/DifficultyRow/OptionButton
@onready var theme_dropdown = $VBox/SettingsContainer/UISettings/ThemeRow/ThemeDropdown
@onready var colorblind_checkbox = $VBox/SettingsContainer/AccessibilitySettings/ColorblindRow/CheckBox

# Built programmatically (no .tscn row): global-leaderboard opt-out (default ON).
var global_leaderboard_checkbox: CheckButton = null

# Built programmatically (no .tscn row): story-intro toggle (#801). The reversible
# ESCAPE HATCH for the "auto-flip on player signal + reversible settings toggle" pattern
# (see GameConfig.play_intros): a hold-to-skip auto-flips play_intros off; this re-enables.
var play_intros_checkbox: CheckButton = null

# Section header labels for icon integration
@onready var audio_label = $VBox/SettingsContainer/AudioSettings/AudioLabel
@onready var graphics_label = $VBox/SettingsContainer/GraphicsSettings/GraphicsLabel
@onready var gameplay_label = $VBox/SettingsContainer/GameplaySettings/GameplayLabel
@onready var ui_label = $VBox/SettingsContainer/UISettings/UILabel
@onready var accessibility_label = $VBox/SettingsContainer/AccessibilitySettings/AccessibilityLabel
@onready var keyboard_label = $VBox/SettingsContainer/KeyboardShortcuts/KeyboardLabel

func _ready():
	print("[SettingsMenu] Initializing...")

	# Load settings from GameConfig singleton
	update_ui_from_game_config()

	# Add icons to section headers
	_setup_section_icons()

	# Add the global-leaderboard opt-out under Gameplay (built in code, not the .tscn)
	_add_global_leaderboard_toggle()

	# Add the story-intro toggle under Gameplay (built in code, not the .tscn)
	_add_play_intros_toggle()
	# Add the "Show gameplay hints" onboarding toggle under Gameplay (issue #720)
	_add_show_hints_toggle()

	# Add the experimental A/B UI layout toggle under UI (built in code, not the .tscn)
	_add_ui_layout_toggle()

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
	_add_icon_to_label(accessibility_label, IconLoader.get_settings_icon("accessibility"))
	_add_icon_to_label(keyboard_label, IconLoader.get_settings_icon("controls"))

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

	music_volume_slider.value = GameConfig.music_volume
	music_volume_label.text = "%d%%" % GameConfig.music_volume

	graphics_quality_option.selected = GameConfig.graphics_quality
	fullscreen_checkbox.button_pressed = GameConfig.fullscreen
	difficulty_option.selected = GameConfig.difficulty
	colorblind_checkbox.button_pressed = GameConfig.colorblind_mode

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

func _on_music_volume_changed(value: float):
	"""Handle Music volume slider change"""
	music_volume_label.text = "%d%%" % int(value)
	# Update GameConfig (will apply to Music bus automatically)
	GameConfig.set_setting("music_volume", int(value), false)

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

func _add_global_leaderboard_toggle():
	"""Append a 'Submit Scores to Global Leaderboard' toggle to the Gameplay section.
	Respects the player's choice (LeaderboardSync.should_submit reads this). Default ON."""
	var gameplay = get_node_or_null("VBox/SettingsContainer/GameplaySettings")
	if gameplay == null:
		return
	var row = HBoxContainer.new()
	var label = Label.new()
	label.text = "Submit Scores to Global Leaderboard"
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	global_leaderboard_checkbox = CheckButton.new()
	global_leaderboard_checkbox.button_pressed = GameConfig.submit_scores_global
	global_leaderboard_checkbox.toggled.connect(_on_global_leaderboard_toggled)
	row.add_child(global_leaderboard_checkbox)
	gameplay.add_child(row)

func _on_global_leaderboard_toggled(pressed: bool):
	"""Handle global-leaderboard opt-out toggle"""
	print("[SettingsMenu] Submit scores to global leaderboard: ", pressed)
	GameConfig.set_setting("submit_scores_global", pressed, false)
	NotificationManager.info("Global leaderboard submission " + ("enabled" if pressed else "disabled"))

func _add_play_intros_toggle():
	"""Append a 'Play story intros' toggle to the Gameplay section (#801). Reversible escape
	hatch: hold-to-skip auto-flips play_intros off; this lets the player turn intros back on."""
	var gameplay = get_node_or_null("VBox/SettingsContainer/GameplaySettings")
	if gameplay == null:
		return
	var row = HBoxContainer.new()
	var label = Label.new()
	label.text = "Play story intros"
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	play_intros_checkbox = CheckButton.new()
	play_intros_checkbox.button_pressed = GameConfig.play_intros
	play_intros_checkbox.toggled.connect(_on_play_intros_toggled)
	row.add_child(play_intros_checkbox)
	gameplay.add_child(row)

func _on_play_intros_toggled(pressed: bool):
	"""Handle story-intro opt-in/out toggle"""
	print("[SettingsMenu] Play story intros: ", pressed)
	GameConfig.set_setting("play_intros", pressed, false)
	NotificationManager.info("Story intros " + ("enabled" if pressed else "disabled"))

var show_hints_checkbox: CheckButton = null

func _add_show_hints_toggle():
	"""Append a 'Show gameplay hints' toggle to the Gameplay section (issue #720).
	Master switch for onboarding help surfaces (getting-started hint + first-launch
	welcome overlay). Respects the player's choice (GameConfig.show_hints). Default ON."""
	var gameplay = get_node_or_null("VBox/SettingsContainer/GameplaySettings")
	if gameplay == null:
		return
	var row = HBoxContainer.new()
	var label = Label.new()
	label.text = "Show gameplay hints"
	label.tooltip_text = "Show onboarding help: the getting-started hint and the first-launch welcome overlay."
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	show_hints_checkbox = CheckButton.new()
	show_hints_checkbox.button_pressed = GameConfig.show_hints
	show_hints_checkbox.toggled.connect(_on_show_hints_toggled)
	row.add_child(show_hints_checkbox)
	gameplay.add_child(row)

func _on_show_hints_toggled(pressed: bool):
	"""Handle the show-gameplay-hints toggle (issue #720)."""
	print("[SettingsMenu] Show gameplay hints: ", pressed)
	GameConfig.set_setting("show_hints", pressed, false)
	NotificationManager.info("Gameplay hints " + ("enabled" if pressed else "disabled"))

var ui_layout_checkbox: CheckButton = null

func _add_ui_layout_toggle():
	"""Append a 'Proposed UI layout (experimental)' toggle to the UI section. A/B scaffolding
	(UI_PROPOSALS_2026-07-22): OFF = classic PLAN/WATCH; ON = the proposed grouped-hand + gantt +
	reclaim assembly. Applies on the next game load; the in-game F9 hotkey flips it live."""
	var ui_section = get_node_or_null("VBox/SettingsContainer/UISettings")
	if ui_section == null:
		return
	var row = HBoxContainer.new()
	var label = Label.new()
	label.text = "Proposed UI layout (experimental)"
	label.tooltip_text = "A/B test: proposed PLAN/WATCH (grouped actions, operations gantt, reclaimed space). Applies on next game load."
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	ui_layout_checkbox = CheckButton.new()
	ui_layout_checkbox.button_pressed = (GameConfig.ui_layout == "proposed")
	ui_layout_checkbox.toggled.connect(_on_ui_layout_toggled)
	row.add_child(ui_layout_checkbox)
	ui_section.add_child(row)

func _on_ui_layout_toggled(pressed: bool):
	"""Handle the proposed-UI-layout toggle."""
	var layout = "proposed" if pressed else "classic"
	print("[SettingsMenu] UI layout: ", layout)
	GameConfig.set_setting("ui_layout", layout, false)
	NotificationManager.info("Proposed UI layout " + ("enabled" if pressed else "disabled") + " (applies on next game load)")

func _on_colorblind_toggled(pressed: bool):
	"""Handle colorblind mode toggle"""
	print("[SettingsMenu] Colorblind mode: ", pressed)
	GameConfig.set_setting("colorblind_mode", pressed, false)
	NotificationManager.info("Colorblind mode " + ("enabled" if pressed else "disabled"))

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
	SceneTransition.go_to("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()

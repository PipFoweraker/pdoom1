extends Control
## Settings -- two views in one scene (Pip's ruling 2026-08-02, memo #1096:
## "settings directions 1 and 5 proceed, diegetic deferred").
##
## FRONT CARD (Direction 5, THE FIRST FIVE MINUTES): the five controls nearly
## every early settings visit is for -- volume, music, fullscreen, hints,
## colorblind -- on one small centered card, plus exactly one door.
##
## OPERATIONS BOARD (Direction 1): behind the ">> ALL PROTOCOLS" door. Every
## remaining control on one dense three-column board, zero navigation, nothing
## scrolls, so nothing can hide below a fold (the old screen buried six shipped
## sections behind a mis-flagged Spacer -- see docs/design/SETTINGS_MENU_OPTIONS.md
## section 0). Columns group by the player's question: my machine / my game /
## my data + my hands.
##
## PERSISTENCE MODEL -- there is no Apply button. Every control applies live
## (unchanged) and now also SAVES via a debounced timer plus a flush on exit.
## The old model applied live but persisted only on Apply, so Back-without-Apply
## silently reverted on next launch -- the exact silent-wrongness flavour league
## week taught us to fear. One honest rule, stated on screen.
##
## The duplicated controls (volume/music/fullscreen/hints/colorblind exist on
## both views) share one handler each and are re-read from GameConfig on every
## view switch, so the two views cannot disagree while visible.

const KEYBIND_SCENE := "res://scenes/keybind_screen.tscn"

# How long after the last change before the config is written. Sliders fire
# value_changed continuously while dragging; this coalesces a drag into one write.
const SAVE_DEBOUNCE_SECONDS := 0.75

# --- Front card (Direction 5) ---
@onready var front_card: Control = $FrontCard
@onready var fc_volume_slider: HSlider = $FrontCard/Card/Margin/CardVBox/VolumeRow/Slider
@onready var fc_volume_label: Label = $FrontCard/Card/Margin/CardVBox/VolumeRow/ValueLabel
@onready var fc_music_slider: HSlider = $FrontCard/Card/Margin/CardVBox/MusicRow/Slider
@onready var fc_music_label: Label = $FrontCard/Card/Margin/CardVBox/MusicRow/ValueLabel
@onready var fc_fullscreen_checkbox: CheckButton = $FrontCard/Card/Margin/CardVBox/FullscreenRow/CheckBox
@onready var fc_hints_checkbox: CheckButton = $FrontCard/Card/Margin/CardVBox/HintsRow/CheckBox
@onready var fc_colorblind_checkbox: CheckButton = $FrontCard/Card/Margin/CardVBox/ColorblindRow/CheckBox
@onready var all_protocols_button: Button = $FrontCard/Card/Margin/CardVBox/AllProtocolsButton
@onready var fc_keybindings_button: Button = $FrontCard/Card/Margin/CardVBox/KeybindingsButton
@onready var back_button: Button = $FrontCard/Card/Margin/CardVBox/FooterRow/BackButton
@onready var fc_saved_label: Label = $FrontCard/Card/Margin/CardVBox/FooterRow/SavedLabel

# --- Operations board (Direction 1) ---
@onready var board: Control = $Board
@onready var version_label: Label = $Board/BoardVBox/HeaderRow/VersionLabel
@onready var board_master_slider: HSlider = $Board/BoardVBox/Columns/Col1/MasterSlider
@onready var board_master_label: Label = $Board/BoardVBox/Columns/Col1/MasterLabelRow/ValueLabel
@onready var board_sfx_slider: HSlider = $Board/BoardVBox/Columns/Col1/SFXSlider
@onready var board_sfx_label: Label = $Board/BoardVBox/Columns/Col1/SFXLabelRow/ValueLabel
@onready var board_music_slider: HSlider = $Board/BoardVBox/Columns/Col1/MusicSlider
@onready var board_music_label: Label = $Board/BoardVBox/Columns/Col1/MusicLabelRow/ValueLabel
@onready var board_fullscreen_checkbox: CheckButton = $Board/BoardVBox/Columns/Col1/FullscreenRow/CheckBox
@onready var board_intros_checkbox: CheckButton = $Board/BoardVBox/Columns/Col2/IntrosRow/CheckBox
@onready var board_hints_checkbox: CheckButton = $Board/BoardVBox/Columns/Col2/HintsRow/CheckBox
@onready var board_rivals_checkbox: CheckButton = $Board/BoardVBox/Columns/Col2/RivalsRow/CheckBox
@onready var difficulty_option: OptionButton = $Board/BoardVBox/Columns/Col2/DifficultyRow/OptionButton
@onready var theme_dropdown: OptionButton = $Board/BoardVBox/Columns/Col2/ThemeRow/ThemeDropdown
@onready var board_ui_layout_checkbox: CheckButton = $Board/BoardVBox/Columns/Col2/UILayoutRow/CheckBox
@onready var board_colorblind_checkbox: CheckButton = $Board/BoardVBox/Columns/Col2/ColorblindRow/CheckBox
@onready var board_leaderboard_checkbox: CheckButton = $Board/BoardVBox/Columns/Col3/LeaderboardRow/CheckBox
@onready var board_launch_ping_checkbox: CheckButton = $Board/BoardVBox/Columns/Col3/LaunchPingRow/CheckBox
@onready var board_keybindings_button: Button = $Board/BoardVBox/Columns/Col3/KeybindingsButton
@onready var front_card_button: Button = $Board/BoardVBox/FooterRow/FrontCardButton
@onready var board_saved_label: Label = $Board/BoardVBox/FooterRow/SavedLabel

# Debounced-save state. _dirty means "applied live but not yet on disk"; the
# window where that is true is at most SAVE_DEBOUNCE_SECONDS + the exit flush.
var _dirty: bool = false
var _save_timer: Timer = null


func _ready():
	print("[SettingsMenu] Initializing (front card + operations board)...")

	_save_timer = Timer.new()
	_save_timer.one_shot = true
	_save_timer.wait_time = SAVE_DEBOUNCE_SECONDS
	_save_timer.timeout.connect(_on_save_timer_timeout)
	add_child(_save_timer)

	version_label.text = "v%s  board %s" % [
		GameConfig.get_current_version(), GameConfig.get_board_version()]

	_refresh_controls()
	_setup_section_icons()
	_connect_signals()

	# Scene-reentry run-killer family (sibling of #979): reached mid-run (dev-overlay jump,
	# or any future nav) with the run still live and unfinished in the GameManager autoload.
	# Relabel Back so it reads honestly -- it resumes the run instead of going to welcome,
	# where Launch Lab / Load Game would silently clobber it.
	if back_button != null and _live_run_active():
		back_button.text = "[BACK TO GAME]"


func _connect_signals():
	# Duplicated controls share one handler each; the hidden view is re-synced by
	# _refresh_controls() on every view switch, never inside a handler.
	fc_volume_slider.value_changed.connect(_on_master_volume_changed)
	board_master_slider.value_changed.connect(_on_master_volume_changed)
	fc_music_slider.value_changed.connect(_on_music_volume_changed)
	board_music_slider.value_changed.connect(_on_music_volume_changed)
	board_sfx_slider.value_changed.connect(_on_sfx_volume_changed)
	fc_fullscreen_checkbox.toggled.connect(_on_fullscreen_toggled)
	board_fullscreen_checkbox.toggled.connect(_on_fullscreen_toggled)
	fc_hints_checkbox.toggled.connect(_on_show_hints_toggled)
	board_hints_checkbox.toggled.connect(_on_show_hints_toggled)
	fc_colorblind_checkbox.toggled.connect(_on_colorblind_toggled)
	board_colorblind_checkbox.toggled.connect(_on_colorblind_toggled)

	board_intros_checkbox.toggled.connect(_on_play_intros_toggled)
	board_rivals_checkbox.toggled.connect(_on_rivals_feed_toggled)
	board_ui_layout_checkbox.toggled.connect(_on_ui_layout_toggled)
	board_leaderboard_checkbox.toggled.connect(_on_global_leaderboard_toggled)
	board_launch_ping_checkbox.toggled.connect(_on_launch_ping_toggled)
	theme_dropdown.item_selected.connect(_on_theme_changed)

	# Research Intensity: issue #1084 owns this row's write path (the #1058 league-lock
	# contradiction). _on_difficulty_changed is kept byte-identical to the pre-rebuild
	# handler on purpose; only the debounced save is attached as a SEPARATE connection
	# so the rebuild does not alter what the handler itself does.
	difficulty_option.item_selected.connect(_on_difficulty_changed)
	difficulty_option.item_selected.connect(func(_index: int): _schedule_save())

	all_protocols_button.pressed.connect(_show_board)
	front_card_button.pressed.connect(_show_front_card)
	fc_keybindings_button.pressed.connect(_open_keybindings)
	board_keybindings_button.pressed.connect(_open_keybindings)
	back_button.pressed.connect(_on_back_pressed)


func _setup_section_icons():
	"""Add icons to the board's section headers (same IconLoader set the old
	single-column screen used; DISCLOSURE has no matching icon and stays bare)."""
	_add_icon_to_label($Board/BoardVBox/Columns/Col1/AudioHeader, IconLoader.get_settings_icon("audio"))
	_add_icon_to_label($Board/BoardVBox/Columns/Col1/DisplayHeader, IconLoader.get_settings_icon("graphics"))
	_add_icon_to_label($Board/BoardVBox/Columns/Col2/OperationsHeader, IconLoader.get_settings_icon("gameplay"))
	_add_icon_to_label($Board/BoardVBox/Columns/Col2/InterfaceHeader, IconLoader.get_settings_icon("theme"))
	_add_icon_to_label($Board/BoardVBox/Columns/Col2/AccessHeader, IconLoader.get_settings_icon("accessibility"))
	_add_icon_to_label($Board/BoardVBox/Columns/Col3/ControlsHeader, IconLoader.get_settings_icon("controls"))


func _add_icon_to_label(label: Label, icon: Texture2D):
	"""Replace a label with an HBox containing icon + label"""
	if not icon:
		return

	var parent = label.get_parent()
	var index = label.get_index()

	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 8)

	var icon_rect = TextureRect.new()
	icon_rect.texture = icon
	icon_rect.custom_minimum_size = Vector2(24, 24)
	icon_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	hbox.add_child(icon_rect)

	var new_label = Label.new()
	new_label.text = label.text
	new_label.add_theme_color_override("font_color", label.get_theme_color("font_color"))
	new_label.add_theme_font_size_override("font_size", label.get_theme_font_size("font_size"))
	hbox.add_child(new_label)

	parent.remove_child(label)
	parent.add_child(hbox)
	parent.move_child(hbox, index)
	label.queue_free()


## Re-read every control from GameConfig / ThemeManager. Uses the no-signal
## setters: this is a display sync, not a player change -- it must not mark the
## config dirty or re-fire handlers.
func _refresh_controls():
	fc_volume_slider.set_value_no_signal(GameConfig.master_volume)
	board_master_slider.set_value_no_signal(GameConfig.master_volume)
	fc_volume_label.text = "%d%%" % GameConfig.master_volume
	board_master_label.text = "%d%%" % GameConfig.master_volume

	board_sfx_slider.set_value_no_signal(GameConfig.sfx_volume)
	board_sfx_label.text = "%d%%" % GameConfig.sfx_volume

	fc_music_slider.set_value_no_signal(GameConfig.music_volume)
	board_music_slider.set_value_no_signal(GameConfig.music_volume)
	fc_music_label.text = "%d%%" % GameConfig.music_volume
	board_music_label.text = "%d%%" % GameConfig.music_volume

	fc_fullscreen_checkbox.set_pressed_no_signal(GameConfig.fullscreen)
	board_fullscreen_checkbox.set_pressed_no_signal(GameConfig.fullscreen)
	fc_hints_checkbox.set_pressed_no_signal(GameConfig.show_hints)
	board_hints_checkbox.set_pressed_no_signal(GameConfig.show_hints)
	fc_colorblind_checkbox.set_pressed_no_signal(GameConfig.colorblind_mode)
	board_colorblind_checkbox.set_pressed_no_signal(GameConfig.colorblind_mode)

	board_intros_checkbox.set_pressed_no_signal(GameConfig.play_intros)
	board_rivals_checkbox.set_pressed_no_signal(GameConfig.show_rivals_feed)
	board_ui_layout_checkbox.set_pressed_no_signal(GameConfig.ui_layout == "proposed")
	# Identity consent renders its EFFECTIVE state: un-consented (never asked) shows
	# OFF even if a legacy config persisted submit_scores_global=true from the old
	# default-ON era (privacy ruling 2026-07-26).
	board_leaderboard_checkbox.set_pressed_no_signal(
		GameConfig.submit_scores_global and GameConfig.leaderboard_consent_asked)
	board_launch_ping_checkbox.set_pressed_no_signal(GameConfig.send_launch_ping)

	# League lock (#1058, #1084). Show the locked value, disabled, with the same
	# tooltip pregame_setup uses -- never silently accept a value the game will not
	# honour. The lock is ENFORCED AT CONSUMPTION (GameConfig.effective_difficulty());
	# this is only the honest reflection of it, so the control cannot lie about a
	# setting the run will ignore. Unlocked, the stored preference shows as-is.
	if GameConfig.is_difficulty_locked():
		difficulty_option.selected = GameConfig.effective_difficulty()
		difficulty_option.disabled = true
		difficulty_option.tooltip_text = GameConfig.DIFFICULTY_LOCK_TOOLTIP
	else:
		difficulty_option.selected = GameConfig.difficulty
		difficulty_option.disabled = false

	var themes = ThemeManager.get_available_themes()
	for i in range(themes.size()):
		if themes[i] == ThemeManager.current_theme:
			theme_dropdown.selected = i
			break


# --- View switching (the Direction 5 door onto the Direction 1 board) ---

func _show_board():
	_refresh_controls()
	front_card.visible = false
	board.visible = true


func _show_front_card():
	_refresh_controls()
	board.visible = false
	front_card.visible = true


# --- Debounced autosave (replaces the Apply button) ---

func _schedule_save():
	_dirty = true
	_set_saved_text("saving...")
	_save_timer.start()  # restarts if already running -- coalesces a slider drag


func _on_save_timer_timeout():
	if not _dirty:
		return
	GameConfig.save_config()
	_dirty = false
	_set_saved_text("[OK] saved")


## Write immediately if anything is pending. Called on every exit path so a
## change can never be lost to navigation -- the failure the Apply button caused.
func _flush_save():
	if not _dirty:
		return
	_save_timer.stop()
	GameConfig.save_config()
	_dirty = false
	_set_saved_text("[OK] saved")


func _exit_tree():
	# Backstop for exits that bypass _on_back_pressed (scene swaps, quit).
	_flush_save()


func _set_saved_text(status_text: String):
	if fc_saved_label != null:
		fc_saved_label.text = status_text
	if board_saved_label != null:
		board_saved_label.text = status_text


# --- Handlers (apply live via GameConfig, then schedule the save) ---

func _on_master_volume_changed(value: float):
	fc_volume_label.text = "%d%%" % int(value)
	board_master_label.text = "%d%%" % int(value)
	GameConfig.set_setting("master_volume", int(value), false)
	_schedule_save()


func _on_sfx_volume_changed(value: float):
	board_sfx_label.text = "%d%%" % int(value)
	GameConfig.set_setting("sfx_volume", int(value), false)
	_schedule_save()


func _on_music_volume_changed(value: float):
	fc_music_label.text = "%d%%" % int(value)
	board_music_label.text = "%d%%" % int(value)
	GameConfig.set_setting("music_volume", int(value), false)
	_schedule_save()


func _on_fullscreen_toggled(pressed: bool):
	print("[SettingsMenu] Fullscreen: ", pressed)
	GameConfig.set_setting("fullscreen", pressed, false)
	_schedule_save()


func _on_difficulty_changed(index: int):
	"""Handle difficulty dropdown change"""
	# Belt-and-braces for #1084: the dropdown is disabled while the league lock
	# holds, but nothing may WRITE a difficulty the game will not honour either.
	# (The real guarantee is at consumption -- GameConfig.effective_difficulty().)
	if GameConfig.is_difficulty_locked():
		return
	print("[SettingsMenu] Difficulty changed to: ", ["Easy", "Standard", "Hard"][index])
	GameConfig.set_setting("difficulty", index, false)


func _on_show_hints_toggled(pressed: bool):
	"""Master switch for onboarding help surfaces (issue #720)."""
	print("[SettingsMenu] Show gameplay hints: ", pressed)
	GameConfig.set_setting("show_hints", pressed, false)
	NotificationManager.info("Gameplay hints " + ("enabled" if pressed else "disabled"))
	_schedule_save()


func _on_colorblind_toggled(pressed: bool):
	print("[SettingsMenu] Colorblind mode: ", pressed)
	GameConfig.set_setting("colorblind_mode", pressed, false)
	NotificationManager.info("Colorblind mode " + ("enabled" if pressed else "disabled"))
	_schedule_save()


func _on_play_intros_toggled(pressed: bool):
	"""Reversible escape hatch (#801): hold-to-skip auto-flips play_intros off;
	this toggle turns intros back on."""
	print("[SettingsMenu] Play story intros: ", pressed)
	GameConfig.set_setting("play_intros", pressed, false)
	NotificationManager.info("Story intros " + ("enabled" if pressed else "disabled"))
	_schedule_save()


func _on_rivals_feed_toggled(pressed: bool):
	"""Rival-intel lines in the WATCH feed. The WATCH screen's own filter button is
	the other UI for the same persisted preference (GameConfig.show_rivals_feed);
	a live run picks a change here up on its next feed rebuild, not instantly."""
	print("[SettingsMenu] Rival intel feed: ", pressed)
	GameConfig.set_setting("show_rivals_feed", pressed, false)
	NotificationManager.info("Rival intel feed " + ("shown" if pressed else "hidden"))
	_schedule_save()


func _on_ui_layout_toggled(pressed: bool):
	"""A/B scaffolding (UI_PROPOSALS_2026-07-22): OFF = classic PLAN/WATCH; ON = the
	proposed grouped-hand + gantt + reclaim assembly. Applies on next game load."""
	var layout = "proposed" if pressed else "classic"
	print("[SettingsMenu] UI layout: ", layout)
	GameConfig.set_setting("ui_layout", layout, false)
	NotificationManager.info("Proposed UI layout " + ("enabled" if pressed else "disabled") + " (applies on next game load)")
	_schedule_save()


func _on_global_leaderboard_toggled(pressed: bool):
	"""Identity-consent toggle (privacy ruling 2026-07-26): flipping it IS the explicit
	one-time choice, so it also marks consent as asked (no game-over prompt afterwards).
	LeaderboardSync.should_submit reads both flags. Reversible any time."""
	print("[SettingsMenu] Submit scores to global leaderboard: ", pressed)
	GameConfig.leaderboard_consent_asked = true
	GameConfig.set_setting("submit_scores_global", pressed, false)
	NotificationManager.info("Global leaderboard submission " + ("enabled" if pressed else "disabled"))
	_schedule_save()


func _on_launch_ping_toggled(pressed: bool):
	"""Anonymous launch-ping opt-out (#799). DECOUPLED from the identity toggle above
	(coordinator ruling 2026-07-26): the ping carries no identity, so only this toggle
	gates it (UpdateCheck.should_send_ping)."""
	print("[SettingsMenu] Anonymous launch ping: ", pressed)
	GameConfig.set_setting("send_launch_ping", pressed, false)
	NotificationManager.info("Anonymous launch ping " + ("enabled" if pressed else "disabled"))
	_schedule_save()


func _on_theme_changed(index: int):
	"""ThemeManager persists to its own cfg file inside apply_theme(), so no
	debounced save is scheduled here -- GameConfig does not own this value."""
	var themes = ThemeManager.get_available_themes()
	if index < themes.size():
		var theme_name = themes[index]
		print("[SettingsMenu] Theme changed to: ", theme_name)
		ThemeManager.apply_theme(theme_name)
		NotificationManager.info("Theme changed to " + ThemeManager.themes[theme_name].display_name)


# --- Navigation ---

func _open_keybindings():
	"""The real keybind editor (profiles + rebinding). Replaces the old static
	shortcuts grid, which advertised [F5] Quick save / [F9] Quick load -- neither
	binding exists; the grid was stale text posing as documentation."""
	_flush_save()
	SceneTransition.go_to(KEYBIND_SCENE)


func _on_back_pressed():
	_flush_save()

	if _live_run_active():
		# Scene-reentry run-killer family (sibling of #979): a live, unfinished run is
		# sitting in the GameManager autoload -- welcome's Launch Lab / Load Game would
		# silently clobber it (main.tscn._boot_game has no idea it exists). Route back
		# to main.tscn with the resume flag set instead, mirroring the conference
		# rhythm-break's own exit (conference_vignette.gd).
		print("[SettingsMenu] Returning to the live game...")
		GameManager.pending_resume = true
		SceneTransition.go_to("res://scenes/main.tscn")
	else:
		print("[SettingsMenu] Returning to welcome screen...")
		SceneTransition.go_to("res://scenes/welcome.tscn")


func _live_run_active() -> bool:
	"""True when a real, unfinished run is sitting live in the GameManager autoload."""
	return GameManager.is_initialized and GameManager.state != null and not GameManager.state.game_over


func _input(event: InputEvent):
	"""ESC walks back out the way the player came in: board -> front card -> leave."""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			if board.visible:
				_show_front_card()
			else:
				_on_back_pressed()

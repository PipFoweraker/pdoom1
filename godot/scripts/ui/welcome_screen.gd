extends Control
## Welcome/Setup Screen - Matches pygame UI style

@onready var title_label = $VBox/Title
@onready var subtitle_label = $VBox/Subtitle
@onready var menu_container = $VBox/MenuContainer
@onready var launch_lab_button = $VBox/MenuContainer/LaunchLabButton
@onready var load_game_button = $VBox/MenuContainer/LoadGameButton
@onready var custom_seed_button = $VBox/MenuContainer/CustomSeedButton
@onready var settings_button = $VBox/MenuContainer/SettingsButton
@onready var guide_button = $VBox/MenuContainer/GuideButton
@onready var keybindings_button = $VBox/MenuContainer/KeybindingsButton
@onready var leaderboard_button = $VBox/MenuContainer/LeaderboardButton
@onready var whats_new_button = $VBox/MenuContainer/WhatsNewButton
@onready var ai_safety_button = $VBox/MenuContainer/AISafetyButton
@onready var exit_button = $VBox/MenuContainer/ExitButton
@onready var version_label = $Version

# What's New modal
var whats_new_modal: Control = null
const WHATS_NEW_SCENE = preload("res://scenes/ui/whats_new_modal.tscn")

# First-launch welcome overlay (issue #720)
var welcome_overlay: Control = null
const WELCOME_OVERLAY_SCENE = preload("res://scenes/ui/welcome_overlay.tscn")

var menu_buttons: Array[Button] = []
var selected_index: int = 0

# Update notice (#799) + patch-cadence notice (#939), built in code near the
# version label. The update notice stays hidden until UpdateCheck reports a
# newer remote version; the cadence label self-retires at
# UpdateCheck.PATCH_CADENCE_SUNSET (delete _setup_launch_notices' label block
# after that date -- it already renders nothing).
var update_notice: HBoxContainer = null
var update_notice_button: Button = null
var patch_cadence_label: Label = null

func _ready():
	print("[WelcomeScreen] Initializing...")

	# Start menu music
	MusicManager.play_context(MusicManager.MusicContext.MENU)

	# Version label derives from the single source of truth (version.txt ->
	# GameConfig.CURRENT_VERSION), not the static text baked into welcome.tscn.
	if version_label:
		version_label.text = "v" + GameConfig.CURRENT_VERSION

	# Collect all menu buttons in order
	menu_buttons = [
		launch_lab_button,
		custom_seed_button,
		settings_button,
		guide_button,
		keybindings_button,
		leaderboard_button,
		whats_new_button,
		ai_safety_button,
		exit_button
	]

	# Connect button signals
	launch_lab_button.pressed.connect(_on_launch_lab_pressed)
	load_game_button.pressed.connect(_on_load_game_pressed)
	custom_seed_button.pressed.connect(_on_custom_seed_pressed)
	settings_button.pressed.connect(_on_settings_pressed)
	guide_button.pressed.connect(_on_guide_pressed)
	keybindings_button.pressed.connect(_on_keybindings_pressed)
	leaderboard_button.pressed.connect(_on_leaderboard_pressed)
	whats_new_button.pressed.connect(_on_whats_new_pressed)
	ai_safety_button.pressed.connect(_on_ai_safety_pressed)
	exit_button.pressed.connect(_on_exit_pressed)

	# DEPRECATED (v0.11.0): the single-slot quicksave "Load Game" is HIDDEN pending a proper
	# design -- a save picker + a "welcome back" context screen + a verification-safe resume.
	# Save-scum as an INTENTIONAL mechanic ("Orb of Regret" / time-travel branching) is an
	# open design question; the counter-argument is that one uninterruptible run per seed
	# keeps the discovery base honest and unhurried. Node + handler (_on_load_game_pressed)
	# and the pause-menu "Save Game" button are kept DORMANT (not deleted) for easy re-enable.
	# Rationale + re-add checklist: docs/game-design/DEPRECATED_SAVE_LOAD.md.
	load_game_button.visible = false
	load_game_button.disabled = true

	# Build-identity corner badge: loud DEV BUILD + git stamp in dev/debug runs, quiet
	# version-only label in exported release builds (issue #1067).
	add_child(DevBuildBadge.new())

	# Quiet launch notices next to the version label (#799 update check, #939
	# patch-cadence). Never blocks, never pops a modal.
	_setup_launch_notices()

	# Initialize the first-launch onboarding overlays (welcome + What's New).
	# The welcome overlay (issue #720) takes priority on a genuine first launch so the
	# two modals never stack; What's New handles returning players after an update.
	_setup_onboarding_overlays()

	# Enable input processing for keyboard navigation
	set_process_input(true)

	# Focus first button
	_update_button_focus()

	# Start menu music
	MusicManager.play_context(MusicManager.MusicContext.MENU)

func _input(event: InputEvent):
	"""Handle keyboard navigation matching pygame behavior"""
	if event is InputEventKey and event.pressed and not event.echo:
		# Arrow keys for navigation
		if event.keycode == KEY_UP or event.keycode == KEY_W:
			selected_index = (selected_index - 1) % menu_buttons.size()
			_update_button_focus()
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		elif event.keycode == KEY_DOWN or event.keycode == KEY_S:
			selected_index = (selected_index + 1) % menu_buttons.size()
			_update_button_focus()
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		# Enter or Space to activate selected button
		elif event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			menu_buttons[selected_index].emit_signal("pressed")
			var viewport = get_viewport()
			if viewport:
				viewport.set_input_as_handled()

		# [U] opens the update page while the update notice is showing (#799)
		elif event.keycode == KEY_U:
			if update_notice and update_notice.visible:
				_on_update_notice_pressed()
				var viewport = get_viewport()
				if viewport:
					viewport.set_input_as_handled()

		# Number keys 1-5 for direct selection
		elif event.keycode >= KEY_1 and event.keycode <= KEY_5:
			var index = event.keycode - KEY_1
			if index < menu_buttons.size():
				selected_index = index
				menu_buttons[selected_index].emit_signal("pressed")
				var viewport = get_viewport()
				if viewport:
					viewport.set_input_as_handled()

func _update_button_focus():
	"""Update visual focus indicator on buttons"""
	for i in range(menu_buttons.size()):
		if i == selected_index:
			menu_buttons[i].grab_focus()
			# Bright blue with white border when selected
			menu_buttons[i].modulate = Color(0.6, 0.8, 1.0)
		else:
			# Dark blue normal state
			menu_buttons[i].modulate = Color(0.3, 0.4, 0.6)

func _on_launch_lab_pressed():
	print("[WelcomeScreen] Launching lab with default seed...")
	# Set default config mode and show confirmation screen
	GameConfig.config_mode = "default"
	GameConfig.game_seed = ""  # Use weekly seed
	GameConfig.difficulty = 1  # Standard difficulty
	SceneTransition.go_to("res://scenes/config_confirmation.tscn")

func _on_load_game_pressed():
	"""L7 (#618): resume the quicksave. MainUI's autostart consumes the flag."""
	if not SaveLoad.has_save():
		return
	print("[WelcomeScreen] Loading saved game...")
	GameConfig.pending_load_path = SaveLoad.QUICKSAVE_PATH
	SceneTransition.go_to("res://scenes/main.tscn")

func _on_custom_seed_pressed():
	print("[WelcomeScreen] Opening pre-game setup...")
	# Show pre-game setup dialog
	SceneTransition.go_to("res://scenes/pregame_setup.tscn")

func _on_settings_pressed():
	print("[WelcomeScreen] Opening settings menu...")
	SceneTransition.go_to("res://scenes/settings_menu.tscn")

func _on_guide_pressed():
	print("[WelcomeScreen] Opening player guide...")
	SceneTransition.go_to("res://scenes/player_guide.tscn")

func _on_keybindings_pressed():
	print("[WelcomeScreen] Opening keybindings...")
	SceneTransition.go_to("res://scenes/keybind_screen.tscn")

func _on_leaderboard_pressed():
	print("[WelcomeScreen] Opening leaderboard...")
	SceneTransition.go_to("res://scenes/leaderboard_screen.tscn")

func _on_ai_safety_pressed():
	print("[WelcomeScreen] Opening AI Safety Info...")
	OS.shell_open("https://aisafety.info/")

func _on_exit_pressed():
	print("[WelcomeScreen] Exiting game...")
	get_tree().quit()

func _on_whats_new_pressed():
	print("[WelcomeScreen] Opening What's New...")
	if whats_new_modal:
		whats_new_modal.show_all_notes()

func _setup_onboarding_overlays():
	"""Instance both first-launch overlays, then auto-show at most ONE.

	Priority: on a genuine first launch (GameConfig.should_show_welcome()) show the
	welcome/help overlay (issue #720) and silently mark patch notes seen -- a brand
	new player does not need a change-log, and this stops the two modals stacking.
	Otherwise fall back to the What's New modal for returning players after an update."""
	# Instance the What's New modal
	whats_new_modal = WHATS_NEW_SCENE.instantiate()
	add_child(whats_new_modal)
	whats_new_modal.closed.connect(_on_whats_new_closed)

	# Instance the welcome overlay
	welcome_overlay = WELCOME_OVERLAY_SCENE.instantiate()
	add_child(welcome_overlay)
	welcome_overlay.closed.connect(_on_whats_new_closed)

	if GameConfig.should_show_welcome():
		print("[WelcomeScreen] First launch detected! Showing welcome overlay...")
		# A brand-new player does not need patch notes; mark them seen so What's New
		# does not also fire (now or on the next launch).
		GameConfig.mark_patch_notes_seen()
		# Delay slightly to ensure UI is ready
		await get_tree().create_timer(0.3).timeout
		welcome_overlay.show_overlay()  # marks welcome_seen (persisted show-once)
	elif GameConfig.has_unseen_patch_notes():
		print("[WelcomeScreen] New version detected! Showing What's New modal...")
		# Delay slightly to ensure UI is ready
		await get_tree().create_timer(0.3).timeout
		whats_new_modal.show_modal(true)  # true = mark as seen

func _setup_launch_notices():
	"""Build the bottom-right notice stack above the version label.

	Two quiet, themed, ASCII-chrome lines (#799 / #939):
	  [!] Patching frequently right now -- updates land often   (until sunset)
	  v0.13.2 available >> [U]pdate page  [x]                   (when newer)
	No modals, no auto-download, no re-nag after dismiss."""
	var stack := VBoxContainer.new()
	stack.name = "LaunchNotices"
	stack.anchor_left = 1.0
	stack.anchor_top = 1.0
	stack.anchor_right = 1.0
	stack.anchor_bottom = 1.0
	stack.offset_left = -560.0
	stack.offset_top = -150.0
	stack.offset_right = -16.0
	stack.offset_bottom = -48.0
	stack.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	stack.grow_vertical = Control.GROW_DIRECTION_BEGIN
	stack.alignment = BoxContainer.ALIGNMENT_END
	add_child(stack)

	# --- #939: patch-cadence notice. Auto-sunsets via the dated constant so
	# removal cannot be forgotten; after the date this whole block renders
	# nothing and SHOULD be deleted.
	if UpdateCheck.is_patch_notice_active(
			Time.get_date_string_from_system(), UpdateCheck.PATCH_CADENCE_SUNSET):
		patch_cadence_label = Label.new()
		patch_cadence_label.text = "[!] Patching frequently right now -- updates land often"
		patch_cadence_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		patch_cadence_label.add_theme_font_size_override("font_size", 16)
		patch_cadence_label.add_theme_color_override("font_color", Color(1.0, 0.78, 0.35, 0.9))
		stack.add_child(patch_cadence_label)

	# --- #799: update-available notice (hidden until UpdateCheck says newer).
	update_notice = HBoxContainer.new()
	update_notice.visible = false
	update_notice.alignment = BoxContainer.ALIGNMENT_END
	update_notice.add_theme_constant_override("separation", 8)
	update_notice_button = Button.new()
	update_notice_button.add_theme_font_size_override("font_size", 16)
	update_notice_button.tooltip_text = "Open the release page in your browser"
	update_notice_button.pressed.connect(_on_update_notice_pressed)
	update_notice.add_child(update_notice_button)
	var dismiss_button := Button.new()
	dismiss_button.text = "[x]"
	dismiss_button.add_theme_font_size_override("font_size", 16)
	dismiss_button.tooltip_text = "Dismiss (won't show again for this version)"
	dismiss_button.pressed.connect(_on_update_notice_dismissed)
	update_notice.add_child(dismiss_button)
	stack.add_child(update_notice)

	# The HTTP response can land before OR after this scene's _ready: read the
	# cached result now, and listen for a late arrival. (Fresh instance per
	# scene load; Godot drops the connection when this node is freed.)
	UpdateCheck.update_available.connect(_on_update_available)
	if UpdateCheck.available_version != "":
		_on_update_available(UpdateCheck.available_version)

func _on_update_available(remote_version: String):
	if update_notice_button == null:
		return
	# Label + epoch flag come from UpdateCheck so the wording is unit-tested;
	# an epoch-forking update must announce itself BEFORE the player clicks.
	update_notice_button.text = UpdateCheck.build_notice_label(
		remote_version, UpdateCheck.available_epoch_change)
	if UpdateCheck.available_highlights != "":
		update_notice_button.tooltip_text = "What changed:\n%s" % UpdateCheck.available_highlights
	else:
		update_notice_button.tooltip_text = "Open the release page in your browser"
	update_notice.visible = true

func _on_update_notice_pressed():
	print("[WelcomeScreen] Opening update page...")
	# Prefix-validated tag page from the manifest when available, else the
	# generic latest-release page (UpdateCheck.get_update_page_url).
	OS.shell_open(UpdateCheck.get_update_page_url())

func _on_update_notice_dismissed():
	print("[WelcomeScreen] Update notice dismissed for v%s" % UpdateCheck.available_version)
	UpdateCheck.dismiss_current_notice()
	if update_notice:
		update_notice.visible = false

func _on_whats_new_closed():
	"""Handle modal close - restore button focus"""
	_update_button_focus()

func _show_placeholder_dialog(title: String, message: String):
	"""Show a simple placeholder dialog for unimplemented features"""
	var dialog = AcceptDialog.new()
	dialog.title = title
	dialog.dialog_text = message
	dialog.size = Vector2(400, 250)
	add_child(dialog)
	dialog.popup_centered()

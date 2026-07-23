extends Control
## Welcome Overlay - first-launch onboarding help layer (issue #720)
##
## A single dismissible welcome/help overlay shown ONCE on a genuine first launch
## (GameConfig.should_show_welcome()). Points the player at the Player Guide.
## Reuses the What's New modal shape + the last_seen_version show-once mechanism
## (GameConfig.welcome_seen is persisted the moment the overlay is shown, so it
## never re-appears -- even if the player quits before finishing a game).
##
## View-layer only: this touches no game state, RNG, turn order, or scoring.

signal closed

const PLAYER_GUIDE_SCENE = "res://scenes/player_guide.tscn"

@onready var guide_button: Button = $CenterContainer/PanelContainer/MarginContainer/VBox/ButtonRow/GuideButton
@onready var close_button: Button = $CenterContainer/PanelContainer/MarginContainer/VBox/ButtonRow/CloseButton

func _ready():
	# Hide by default; the welcome screen decides whether to show us.
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	guide_button.pressed.connect(_on_guide_pressed)
	close_button.pressed.connect(_on_close_pressed)

func _input(event: InputEvent):
	# Only handle input while visible.
	if not visible:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE or event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			_on_close_pressed()
			get_viewport().set_input_as_handled()

## Show the overlay and mark it as seen (persisted show-once).
func show_overlay() -> void:
	visible = true
	mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.grab_focus()
	# Mark seen immediately (like whats_new marks on show): even if the player then
	# opens the Player Guide instead of dismissing, the overlay never re-appears.
	GameConfig.mark_welcome_seen()

## Hide the overlay.
func hide_overlay() -> void:
	visible = false
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	closed.emit()

func _on_guide_pressed() -> void:
	print("[WelcomeOverlay] Opening Player Guide...")
	SceneTransition.go_to(PLAYER_GUIDE_SCENE)

func _on_close_pressed() -> void:
	hide_overlay()

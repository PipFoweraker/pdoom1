extends GutTest
## HOTFIX repro/regression (#664): a fresh game must reach an actionable state.
##
## The ship-blocking bug: after pregame setup the player reaches MainUI but the
## first turn never becomes actionable -- boot did nothing and every action button
## was greyed out. This drives the REAL scene (main.tscn boots MainUI, whose _ready
## auto-boots via _boot_game -- the old vestigial "Init" button was removed in #715)
## and asserts the game either
## presents an initial event dialog OR emits a non-empty actions_available list and
## enables the action buttons.

var _actions_emitted: Array = []
var _actions_signal_count: int = 0
var _events_emitted: Array = []


func _reset_capture() -> void:
	_actions_emitted = []
	_actions_signal_count = 0
	_events_emitted = []


func _on_actions(actions: Array) -> void:
	_actions_signal_count += 1
	_actions_emitted = actions


func _on_event(event: Dictionary) -> void:
	_events_emitted.append(event)


func test_fresh_game_reaches_actionable_state() -> void:
	_reset_capture()

	# Boot the real scene tree exactly as the game does: main.tscn -> TabManager ->
	# MainUI, whose _ready() awaits a frame then calls _boot_game().
	var scene: PackedScene = load("res://scenes/main.tscn")
	assert_not_null(scene, "main.tscn must load")
	var root: Node = scene.instantiate()
	add_child_autofree(root)

	# Grab the live GameManager the MainUI created and listen for the actionable signals.
	var main_ui: Node = root.find_child("MainUI", true, false)
	assert_not_null(main_ui, "MainUI node must exist under the scene root")

	# Let _ready run (it awaits one process_frame before auto-init), then give the
	# start_new_game path several frames to emit its terminal signal.
	await get_tree().process_frame
	var gm = main_ui.game_manager
	assert_not_null(gm, "MainUI must have created a GameManager")
	gm.actions_available.connect(_on_actions)
	gm.event_triggered.connect(_on_event)

	# start_new_game may already have fired before we connected (auto-init runs on the
	# first frame). Fall back to the game state itself as ground truth.
	for _i in range(10):
		await get_tree().process_frame

	var state = gm.state
	assert_not_null(state, "GameManager.state must exist after auto-init")
	assert_true(gm.is_initialized, "GameManager must be initialized after auto-init")

	# Ground-truth actionability: either events are pending (a dialog should be up) OR
	# the game is in ACTION_SELECTION with a non-empty available-action list.
	var available: Array = gm.turn_manager.get_available_actions() if gm.turn_manager else []
	var pending: int = state.pending_events.size()
	var in_action_phase: bool = state.current_phase == GameState.TurnPhase.ACTION_SELECTION

	gut.p("phase=%s pending_events=%d available_actions=%d actions_signals=%d events_signals=%d" % [
		GameState.TurnPhase.keys()[state.current_phase], pending, available.size(),
		_actions_signal_count, _events_emitted.size()])

	var actionable: bool = (pending > 0) or (in_action_phase and available.size() > 0)
	assert_true(actionable,
		"Fresh game must be actionable: pending events OR ACTION_SELECTION with actions. " +
		"phase=%s pending=%d actions=%d" % [
			GameState.TurnPhase.keys()[state.current_phase], pending, available.size()])

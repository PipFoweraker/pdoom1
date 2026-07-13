extends GutTest
## L1 follow-up (#612): the PLAYABLE month path. main_ui's End Turn button calls
## game_manager.end_month(); this smoke drives that exact API headlessly through a full
## month: plan commit -> day-tick playback -> auto-pause windows (event_triggered ->
## resolve_event round-trip, the event_dialog wiring) -> month review dialog -> next plan
## phase. The old end_turn() day-step is untested here on purpose — it is DEV-overlay-only.

var game_manager
var _review_event: Dictionary = {}
var _windows_answered: int = 0
var _saved_historical_events: Array = []


func before_each():
	var GameManagerScript = load("res://scripts/game_manager.gd")
	game_manager = GameManagerScript.new()
	add_child_autofree(game_manager)
	if EventService:
		_saved_historical_events = EventService.transformed_events.duplicate()
		EventService.transformed_events.clear()
	_review_event = {}
	_windows_answered = 0


func after_each():
	if EventService:
		EventService.transformed_events = _saved_historical_events


func _auto_respond(event: Dictionary) -> void:
	"""Play the event_dialog's role: answer every surfaced window with its first option;
	capture the month-review dialog instead of answering it (the assertion target)."""
	if String(event.get("id", "")) == game_manager.MONTH_REVIEW_EVENT_ID:
		_review_event = event
		return
	var options: Array = event.get("options", [])
	var choice_id := ""
	if options.size() > 0 and options[0] is Dictionary:
		choice_id = String(options[0].get("id", ""))
	_windows_answered += 1
	# Deferred, as the real dialog answers on a later frame than the emission.
	game_manager.resolve_event.call_deferred(event, choice_id)


func _keep_alive(_state_dict: Dictionary) -> void:
	"""Harness intervention: pre-rebalance doom drift kills bot runs by turn ~4-12 (the
	L0 pacing datum), which would end the run before the month boundary. Clamp doom so
	the WIRING under test — a full month of playback — is reachable. Balance is G1's job."""
	if game_manager.state != null and not game_manager.state.game_over:
		game_manager.state.doom = 5.0
		if game_manager.state.doom_system != null:
			game_manager.state.doom_system.current_doom = 5.0


func test_end_month_button_path_plays_a_full_month():
	game_manager.start_new_game("l1-button-month-smoke")
	game_manager.day_tick_seconds = 0.01  # fast playback for the headless smoke
	game_manager.event_triggered.connect(_auto_respond)
	game_manager.game_state_updated.connect(_keep_alive)
	_keep_alive({})

	# Resolve any game-start events on the legacy plan-phase path (emitted before our
	# listener connected — they still sit in pending_events).
	var guard := 0
	while game_manager.state.pending_events.size() > 0 and guard < 20:
		guard += 1
		var ev: Dictionary = game_manager.state.pending_events[0]
		var opts: Array = ev.get("options", [])
		var cid := String(opts[0].get("id", "")) if opts.size() > 0 else ""
		game_manager.resolve_event(ev, cid)

	var turn0: int = game_manager.state.turn

	# The commit-plan path with an empty queue: the pass action IS the month plan.
	game_manager.state.queued_actions.append(GameActions.PASS_ACTION_ID)
	game_manager.end_month()
	assert_true(game_manager.month_playback_active or not _review_event.is_empty(),
		"end_month hands control to month playback")

	# Wait for the month boundary's review dialog (windows auto-answered along the way).
	await wait_until(func(): return not _review_event.is_empty() or game_manager.state.game_over, 30)

	assert_false(game_manager.state.game_over, "the kept-alive run survives to the boundary")
	assert_false(_review_event.is_empty(), "the month review dialog surfaced at the boundary")
	assert_string_contains(String(_review_event.get("name", "")), "Month Review",
		"the review dialog is the month review")
	assert_true(game_manager.month_controller.month_open_pending,
		"the boundary tick is held open as the new plan phase")
	assert_gte(game_manager.state.turn - turn0, 15,
		"a calendar month of workday ticks played out (got %d)" % (game_manager.state.turn - turn0))
	assert_false(game_manager.month_playback_active, "playback stopped at the boundary")

	# Closing the review opens the plan phase — the loop is closed: plan, play, review, plan.
	game_manager.resolve_event(_review_event, "begin_planning")
	assert_eq(game_manager.state.current_phase, GameState.TurnPhase.ACTION_SELECTION,
		"back in the plan phase after the review")
	assert_true(game_manager.state.can_end_turn, "the next month plan can be committed")

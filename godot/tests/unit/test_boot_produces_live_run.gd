extends GutTest
## Regression guard for #1023 -- "full UI, Phase: Not Started, no action buttons".
##
## THE ESCAPE. Pip launched 3f408038 and got a perfectly constructed main.tscn with no game
## behind it: feed "Game not started...", footer "Phase: Not Started", zero action buttons,
## all resources 0. The fast gate was green.
##
## What the fast gate already covered (measured, not assumed): deleting the _boot_game() call
## turns test_game_start_actionable.gd and test_ui_scene_reentry_safety.gd red, and dropping
## the force=true from _boot_game()'s fresh-boot branch turns test_ui_scene_reentry_safety.gd
## red. So the two obvious break modes were NOT the hole.
##
## The hole this file closes is the third mode, and it is the one that matches Pip's report
## most literally: **the run boots but the view never receives it.** Every existing boot test
## asserts on GameManager only. A UI left rendering main.tscn's baked chrome -- "Phase: Not
## Started", "58.5%", "Money: $0", "Week 1 | Mon Jul 3, 2017 | Day 1/5" -- is indistinguishable
## from a healthy boot to all 990 of them. That was measured too: severing the state->view
## handler produced exactly ONE failure in the whole suite, this file's placeholder test.
##
## Secondary gaps closed here:
##   * GameManager is an AUTOLOAD, so `is_initialized` can be true for reasons unrelated to
##     THIS boot -- an earlier test file leaves it live and every later assertion passes
##     vacuously. Every test below drives the autoload to a known state FIRST and asserts
##     differentially (state object IDENTITY, not just truthiness), so the guard does not
##     depend on suite file ordering.
##   * GameConfig.pending_load_path is an early-return branch inside _boot_game() that no
##     other test exercises -- a stale or dead path there is a second route to #1023's
##     symptom set without start_new_game() ever being called.
##
## SELF-VERIFICATION (why you can trust these asserts are sensitive). Shipped code is NOT
## mutated to prove this; the negative controls are built in:
##   * test_liveness_predicate_detects_the_1023_condition drives the autoload to the exact
##     post-#1023 state (no run) and asserts the shared predicate REPORTS it -- an assertion
##     that cannot silently become a tautology.
##   * the placeholder test asserts the baked strings ARE present in the frame before boot and
##     GONE after it. Same labels, same run, both directions.
##
## TIER: fast (tests/unit, non-recursive). It instantiates main.tscn -- required, because this
## bug lives in scene lifecycle and coroutine timing, and any test that stubs the scene tree
## would have passed. Precedent for the cost: test_ui_scene_reentry_safety.gd already boots
## main.tscn four times in one file.

const MAIN_SCENE := "res://scenes/main.tscn"
const BOOT_FRAME_BUDGET := 60  # _ready awaits 1 frame then _boot_game; 60 is slack, not need

# Scene-baked placeholder literals in godot/scenes/main.tscn. If any survives a successful
# boot, the player is reading fake numbers -- which is how #1023 presented. Keep in sync with
# main.tscn: TopBar/TurnLabel, TopBar/MoneyLabel, BottomBar/PhaseLabel,
# InstrumentColumn/CoreZone/RightZones/NumericDoomZone/NumericDoomLabel.
const PLACEHOLDER_TURN := "Week 1 |"
const PLACEHOLDER_MONEY := "Money: $0"
const PLACEHOLDER_PHASE := "Not Started"
const PLACEHOLDER_DOOM := "58.5%"

var _prev_pending_load_path: String = ""


func before_each() -> void:
	_prev_pending_load_path = GameConfig.pending_load_path


func after_each() -> void:
	GameConfig.pending_load_path = _prev_pending_load_path


func after_all() -> void:
	# Hand the autoload back VIRGIN, not live. This file sorts first in tests/unit, and
	# test_game_start_actionable.gd's `assert_true(gm.is_initialized)` is only meaningful when
	# it starts from an un-initialized autoload -- leaving a live run here would silently make
	# that older guard vacuous. Restoring engine-start state keeps every later file seeing
	# exactly the environment it saw before this file existed.
	_make_autoload_virgin()


func _make_autoload_virgin() -> void:
	"""Drive the GameManager autoload back to its engine-start state.

	Without this the is_initialized assertions below are vacuous. _release_game_objects()
	first, because GameState / DoomSystem / RiskPool / TurnManager extend Node and are never
	in the tree -- nulling the references without freeing them leaks 4 orphans and would trip
	test_game_lifecycle_hygiene.gd's global orphan-count assertion."""
	GameManager.month_playback_active = false
	GameManager._release_game_objects()
	GameManager.state = null
	GameManager.turn_manager = null
	GameManager.month_controller = null
	GameManager.is_initialized = false
	GameManager.pending_resume = false
	GameManager.last_conference_trip = {}
	GameConfig.pending_load_path = ""


func _liveness_failures() -> Array:
	"""The minimum facts separating a live run from #1023's empty shell, as DATA.

	Returned as a list of reasons rather than asserted inline so the negative-control test can
	feed it the broken condition and confirm it actually reports one."""
	var reasons: Array = []
	if not GameManager.is_initialized:
		reasons.append("GameManager.is_initialized is false (this is #1023's signature)")
	var state = GameManager.state
	if state == null:
		reasons.append("no GameState exists")
		return reasons
	if String(state.game_seed_str).is_empty():
		reasons.append("GameState has an empty seed (unscoreable, unreplayable, forks the board)")
	if state.turn < 1:
		reasons.append("run has not reached turn 1 (turn=%d)" % state.turn)
	var started_phases := [GameState.TurnPhase.TURN_START, GameState.TurnPhase.ACTION_SELECTION]
	if not (state.current_phase in started_phases):
		reasons.append("phase %s is not a started phase" %
			GameState.TurnPhase.keys()[state.current_phase])
	if GameManager.turn_manager == null:
		reasons.append("no TurnManager (no action is executable)")
	return reasons


func _placeholder_failures(main_ui: Node) -> Array:
	"""Which of main.tscn's baked placeholder strings are currently on screen."""
	var found: Array = []
	var phase_label = main_ui.get("phase_label")
	if phase_label != null and String(phase_label.text).contains(PLACEHOLDER_PHASE):
		found.append("BottomBar/PhaseLabel '%s'" % PLACEHOLDER_PHASE)
	var turn_label = main_ui.get("turn_label")
	if turn_label != null and String(turn_label.text).contains(PLACEHOLDER_TURN):
		found.append("TopBar/TurnLabel '%s'" % PLACEHOLDER_TURN)
	var money_label = main_ui.get("money_label")
	if money_label != null and String(money_label.text) == PLACEHOLDER_MONEY:
		found.append("TopBar/MoneyLabel '%s'" % PLACEHOLDER_MONEY)
	var doom_label = main_ui.get("numeric_doom_label")
	if doom_label != null and String(doom_label.text) == PLACEHOLDER_DOOM:
		found.append("NumericDoomLabel '%s'" % PLACEHOLDER_DOOM)
	return found


func _instantiate_main_scene() -> Node:
	"""Add main.tscn to the tree WITHOUT letting any frame pass.

	MainUI._ready() runs synchronously up to its `await get_tree().process_frame`, so at the
	moment this returns the @onready label refs are populated and _boot_game() has NOT run --
	the pre-boot observation window the placeholder negative control needs."""
	var scene: PackedScene = load(MAIN_SCENE)
	assert_not_null(scene, "main.tscn must load")
	var root: Node = scene.instantiate()
	add_child_autofree(root)
	var main_ui: Node = root.find_child("MainUI", true, false)
	assert_not_null(main_ui, "MainUI node must exist under the main.tscn root")
	return main_ui


func _let_boot_complete() -> void:
	"""Let real frames pass, exactly as a launch does. Polls rather than awaiting a fixed
	count so a slow boot (#1023's log shows scene_load at 2887 ms) reads as slow, not failed."""
	for _i in range(BOOT_FRAME_BUDGET):
		await get_tree().process_frame
		if GameManager.is_initialized and GameManager.state != null:
			break


func _boot_main_scene() -> Node:
	var main_ui: Node = _instantiate_main_scene()
	await _let_boot_complete()
	return main_ui


func _assert_live(context: String) -> void:
	var reasons: Array = _liveness_failures()
	assert_eq(reasons.size(), 0,
		"%s: the game must be live after the boot path completes. Problems: %s" % [
			context, "; ".join(PackedStringArray(reasons))])


func test_liveness_predicate_detects_the_1023_condition() -> void:
	"""NEGATIVE CONTROL -- the reason the other tests here mean something.

	This drives the autoload to precisely the state Pip's launch ended in (UI reachable, no
	run) and asserts the shared predicate REPORTS it. If a future refactor makes
	_liveness_failures() unable to fail, this goes red rather than the whole file going
	quietly green. No shipped code is mutated to achieve it."""
	_make_autoload_virgin()
	var reasons: Array = _liveness_failures()
	assert_true(reasons.size() > 0,
		"the liveness predicate must report an un-booted GameManager as broken -- if it "
		+ "cannot detect #1023's own state, every other assertion in this file is a tautology")
	assert_true("; ".join(PackedStringArray(reasons)).contains("is_initialized"),
		"the reported reason must name is_initialized, got: %s" % [reasons])


func test_virgin_boot_creates_a_live_run() -> void:
	# The autoload is forced back to engine-start state, so nothing but THIS boot can satisfy
	# the assertions -- the guard no longer depends on suite file ordering.
	_make_autoload_virgin()
	assert_false(GameManager.is_initialized, "precondition: the autoload must start un-initialized")
	assert_null(GameManager.state, "precondition: no GameState may exist before boot")

	var main_ui: Node = await _boot_main_scene()
	assert_not_null(main_ui)
	_assert_live("virgin boot")


func test_boot_replaces_a_stale_run_left_by_an_earlier_launch() -> void:
	"""A second Launch Lab in the same process (or a leaderboard/settings round trip) reaches
	_boot_game() with the autoload already live and NO pending_resume flag. That is a genuine
	fresh boot, so the fresh-boot branch must pass force=true; if it does not,
	start_new_game()'s self-guard refuses and the player gets #1023's empty shell.

	Asserting on state OBJECT IDENTITY is what makes this visible: `is_initialized` is true
	either way."""
	_make_autoload_virgin()
	GameManager.start_new_game("stale-previous-launch-seed", true)
	var stale_state = GameManager.state
	assert_not_null(stale_state, "precondition: a stale run must be live before booting again")
	# A real second launch arrives with the conference handoff flag clear -- clearing it is the
	# whole point of the scenario, not a convenience.
	GameManager.pending_resume = false
	GameConfig.pending_load_path = ""

	var main_ui: Node = await _boot_main_scene()
	assert_not_null(main_ui)

	# A refusal push_warning()s by design. Accept the log line; the asserts below are the
	# ground truth and fail loudly on their own if a refusal actually happened.
	for e in get_errors():
		e.handled = true

	_assert_live("boot over a stale run")
	assert_ne(GameManager.state, stale_state,
		"a fresh boot of main.tscn must mint a NEW GameState, not silently keep the previous "
		+ "launch's run -- if this fails, _boot_game()'s fresh-boot branch stopped passing "
		+ "force=true and start_new_game() refused (#1023)")


func test_booted_ui_shows_live_state_not_scene_placeholders() -> void:
	"""THE GAP THIS FILE EXISTS FOR: a run that boots but never reaches the view.

	main.tscn ships hardcoded chrome. Those exact strings are what Pip saw. A boot that
	produced state but never pushed it into the labels is just as broken as no boot, and is
	invisible to every assertion made on GameManager alone.

	Built-in negative control: the same detector must FIND the placeholders one frame before
	boot and NOT find them after. A detector that can never fire would fail the first half."""
	_make_autoload_virgin()
	var main_ui: Node = _instantiate_main_scene()

	# Pre-boot: _ready has populated the label refs but is parked on its awaited frame.
	var before: Array = _placeholder_failures(main_ui)
	assert_true(before.size() > 0,
		"negative control: main.tscn's baked placeholders must be on screen BEFORE boot. "
		+ "If none are found, the literals in this file have drifted from the scene and the "
		+ "post-boot assertion below proves nothing. Update the PLACEHOLDER_* constants.")

	await _let_boot_complete()
	await get_tree().process_frame  # one more for the state_updated -> label writes to land
	_assert_live("placeholder check")
	var state = GameManager.state
	if state == null:
		return

	var after: Array = _placeholder_failures(main_ui)
	assert_eq(after.size(), 0,
		"the UI is still showing main.tscn's baked placeholders after a successful boot -- "
		+ "state exists but never reached the view (#1023's exact appearance). Still showing: "
		+ "; ".join(PackedStringArray(after)))

	# Doom is additionally pinned to the live value, so the guard cannot be defeated by balance
	# changing the placeholder into a coincidentally-correct number.
	var doom_label = main_ui.get("numeric_doom_label")
	if doom_label != null:
		assert_eq(String(doom_label.text), "%.1f%%" % state.doom,
			"NumericDoomLabel must render the live doom value, not the scene's baked '%s'" %
				PLACEHOLDER_DOOM)

	# "No action buttons in the left-hand column at all" was #1023's most visible symptom.
	# Only meaningful when no opening event dialog owns the screen (same rule as
	# test_game_start_actionable.gd's actionability check).
	var actions_list = main_ui.get("actions_list")
	assert_not_null(actions_list, "MainUI must expose actions_list (the action column)")
	if actions_list != null and state.pending_events.is_empty():
		assert_true(actions_list.get_child_count() > 0,
			"the action column must be populated after boot -- #1023 showed zero action buttons")


func test_queued_load_of_a_missing_save_still_leaves_a_live_run() -> void:
	"""_boot_game()'s queued-load branch is an early-return path: a stale or bad
	GameConfig.pending_load_path must fall through to a fresh game, never leave the UI standing
	over nothing. Untested before -- and it is one of the two ways to reach #1023's symptom set
	without start_new_game() ever being called."""
	_make_autoload_virgin()
	GameConfig.pending_load_path = "user://does_not_exist_boot_guard.save"

	var main_ui: Node = await _boot_main_scene()
	assert_not_null(main_ui)
	# The failed load emits error_occurred / logs on purpose; accept the noise.
	for e in get_errors():
		e.handled = true

	_assert_live("queued load of a missing save")
	assert_eq(GameConfig.pending_load_path, "",
		"the queued-load flag is one-shot and must be consumed even when the load fails, "
		+ "otherwise the next boot retries the same dead path")

extends GutTest
## Regression guard for the scene-reentry run-killer family (sibling of #979, the conference
## rhythm-break's own live-run clobber). Root cause: GameManager.start_new_game() /
## load_saved_game() used to unconditionally replace `state`, so every caller had to remember
## its own guard -- the dev-mode overlay's leaderboard/settings jump forgot, leaving main.tscn
## live with no handoff, so Launch Lab / Load Game on the far side silently destroyed the run.
##
## This test drives the REAL main.tscn boot (matching test_game_start_actionable.gd), then:
##  1. asserts start_new_game() WITHOUT force refuses to touch a live run;
##  2. asserts the two now-fixed reentry surfaces (leaderboard_screen, settings_menu) detect
##     the live run and relabel their Back button "[BACK TO GAME]";
##  3. asserts the fixed _boot_game() resume path (GameManager.pending_resume) reattaches to
##     the SAME state object rather than minting a new one -- the run survives.
##
## Real scene-tree navigation (SceneTransition.go_to swapping get_tree().current_scene) is
## deliberately NOT exercised here -- no test in this suite swaps the root scene (it would
## risk tearing down the GUT runner itself); main_ui._boot_game() is called directly instead,
## which is exactly what a real reload would invoke.

var _root: Node = null
var _main_ui: Node = null
var _gm: Node = null


func before_each() -> void:
	# Boot the real scene tree exactly as the game does (test_game_start_actionable.gd's
	# pattern): main.tscn -> TabManager -> MainUI, whose _ready() auto-boots via _boot_game().
	var scene: PackedScene = load("res://scenes/main.tscn")
	_root = scene.instantiate()
	add_child_autofree(_root)
	_main_ui = _root.find_child("MainUI", true, false)
	assert_not_null(_main_ui, "MainUI node must exist under the scene root")
	_gm = _main_ui.get("game_manager")
	assert_not_null(_gm, "MainUI must have created/bound a GameManager")


func _wait_for_boot() -> void:
	for _i in range(10):
		await get_tree().process_frame


func test_start_new_game_without_force_refuses_over_live_run() -> void:
	await _wait_for_boot()
	assert_true(_gm.is_initialized, "precondition: a game must be live before the refusal is meaningful")
	var original_state = _gm.state
	var original_seed: String = String(original_state.game_seed_str)

	# No force: must be refused. State object identity and seed must be unchanged.
	_gm.start_new_game("attempted-clobber-seed")

	# The refusal push_warning()s LOUDLY on purpose (that's the fix) -- GUT counts an
	# unhandled push_warning as a test failure by default. Mark it handled: we asserted
	# the actual behavior (refusal) above/below; this just accepts the expected log line.
	for e in get_errors():
		e.handled = true

	assert_eq(_gm.state, original_state,
		"start_new_game() without force must NOT replace a live game's state object")
	assert_eq(String(_gm.state.game_seed_str), original_seed,
		"start_new_game() without force must NOT touch a live game's seed")
	assert_true(_gm.is_initialized, "refused start_new_game() must leave is_initialized true")


func test_start_new_game_with_force_replaces_live_run() -> void:
	# Sanity check for the other half of the guard: force=true is a real, working escape
	# hatch (the debug Reset Game button / genuine fresh-boot path rely on this).
	await _wait_for_boot()
	var original_state = _gm.state
	_gm.start_new_game("deliberate-reset-seed", true)
	assert_ne(_gm.state, original_state,
		"start_new_game(force=true) must replace the state object (deliberate reset)")
	assert_eq(String(_gm.state.game_seed_str), "deliberate-reset-seed")


func test_leaderboard_screen_offers_back_to_game_over_a_live_run() -> void:
	await _wait_for_boot()
	assert_true(_gm.is_initialized and not _gm.state.game_over,
		"precondition: a live, unfinished run must exist")

	var packed: PackedScene = load("res://scenes/leaderboard_screen.tscn")
	var inst: Control = packed.instantiate()
	add_child_autofree(inst)
	await get_tree().process_frame

	assert_true(inst.call("_live_run_active"),
		"leaderboard_screen must detect the live run via GameManager")
	var back_btn: Button = inst.get("back_button")
	assert_not_null(back_btn, "leaderboard_screen must expose its Back button")
	assert_eq(back_btn.text, "[BACK TO GAME]",
		"Back button must be relabeled when a live run is reachable behind this screen")


func test_settings_menu_offers_back_to_game_over_a_live_run() -> void:
	await _wait_for_boot()
	assert_true(_gm.is_initialized and not _gm.state.game_over,
		"precondition: a live, unfinished run must exist")

	var packed: PackedScene = load("res://scenes/settings_menu.tscn")
	var inst: Control = packed.instantiate()
	add_child_autofree(inst)
	await get_tree().process_frame

	assert_true(inst.call("_live_run_active"),
		"settings_menu must detect the live run via GameManager")
	var back_btn: Button = inst.get("back_button")
	assert_not_null(back_btn, "settings_menu must expose its Back button")
	assert_eq(back_btn.text, "[BACK TO GAME]",
		"Back button must be relabeled when a live run is reachable behind this screen")


func test_reentry_resume_path_preserves_the_same_live_state() -> void:
	# Simulates the fixed round trip: dev-overlay jump -> leaderboard/settings -> Back ->
	# main.tscn re-boot. The Back handlers set GameManager.pending_resume=true before
	# navigating; main_ui._boot_game() is the deferred-swap target's _ready path, so calling
	# it again on the SAME live main.tscn instance exercises exactly the decision it makes
	# on a real reload, without swapping get_tree().current_scene (untested/risky territory
	# for this suite -- see file header).
	await _wait_for_boot()
	assert_true(_gm.is_initialized, "precondition: a game must be live")
	var original_state = _gm.state
	var original_turn: int = original_state.turn

	_gm.pending_resume = true
	_main_ui.call("_boot_game")
	await get_tree().process_frame

	assert_false(_gm.pending_resume, "resume_in_place() must consume the one-shot flag")
	assert_eq(_gm.state, original_state,
		"the resume path must reattach to the SAME state object, not mint a new one")
	assert_eq(_gm.state.turn, original_turn, "the run's turn counter must be untouched by reentry")
	assert_true(_gm.is_initialized, "the run must still be live after reentry")

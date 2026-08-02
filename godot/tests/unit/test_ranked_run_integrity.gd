extends GutTest
## Ranked-run integrity: the two guarantees the league board rests on, enforced at
## CONSUMPTION (issue #1084 + the Alpha Tools ruling, decision card
## docs/decision-cards/2026-08-01_dev-powers-nomenclature.html, ruled via PR #1096).
##
## 1. DIFFICULTY (#1058 -> #1084): the lock lived on ONE UI screen (pregame_setup)
##    while difficulty is CONSUMED in GameManager._apply_difficulty_settings, and
##    Settings wrote the field freely -- so any of the other five routes into
##    main.tscn could start an Easy run onto the one comparable board. The lock now
##    lives at consumption: GameConfig.effective_difficulty().
## 2. ALPHA TOOLS: using any dev power makes the run UNRANKED via is_ranked_run(),
##    STICKY AND ONE-WAY -- turning the tool off must not restore ranking, only the
##    run boundary (start_new_game) resets it, and save/load must not launder it.

const DEBUG_OVERLAY := preload("res://scenes/debug_overlay.tscn")
const TEST_SAVE_PATH := "user://saves/test_ranked_run_integrity.json"

var _saved_difficulty: int
var _saved_seed: String
var _saved_scenario: String
var _saved_baseline_mode: int

func before_each():
	_saved_difficulty = GameConfig.difficulty
	_saved_seed = GameConfig.game_seed
	_saved_scenario = GameConfig.scenario_id
	_saved_baseline_mode = GameConfig.baseline_mode
	GameConfig.game_seed = ""
	GameConfig.scenario_id = ""
	GameConfig.baseline_mode = 0  # no background baseline sim noise
	GameConfig._difficulty_lock_override = null  # ship configuration: lock ON
	GameConfig.reset_alpha_tools_flag()

func after_each():
	GameConfig.difficulty = _saved_difficulty
	GameConfig.game_seed = _saved_seed
	GameConfig.scenario_id = _saved_scenario
	GameConfig.baseline_mode = _saved_baseline_mode
	GameConfig._difficulty_lock_override = null
	GameConfig.reset_alpha_tools_flag()
	var abs_path := ProjectSettings.globalize_path(TEST_SAVE_PATH)
	if FileAccess.file_exists(abs_path):
		DirAccess.remove_absolute(abs_path)

func _fresh_gm():
	var gm = load("res://scripts/game_manager.gd").new()
	add_child_autofree(gm)
	return gm

func _release(gm) -> void:
	gm._release_game_objects()
	await get_tree().process_frame

# === Piece 1 (#1084): difficulty is locked where it is CONSUMED ===================

func test_settings_written_easy_still_plays_standard():
	# The exact #1084 bypass: settings_menu wrote difficulty freely (persisted to
	# config.cfg), and a non-pregame route into main.tscn starts the run without the
	# pregame screen's lock ever executing. Simulate that: raw field says Easy, no UI
	# involved, straight to start_new_game.
	GameConfig.difficulty = 0  # Easy
	var gm = _fresh_gm()
	gm.start_new_game("integrity-seed-1")
	assert_eq(gm.state.attention_per_month,
		Balance.inum("difficulty.standard.attention_per_month", 20),
		"#1084: a settings-written Easy must still PLAY Standard -- the Attention grant is enforced at consumption, not on one screen")
	assert_ne(gm.state.attention_per_month,
		Balance.inum("difficulty.easy.attention_per_month", 24),
		"#1084: the Easy grant must NOT reach game state while the league lock holds")
	await _release(gm)

func test_settings_written_hard_still_plays_standard():
	GameConfig.difficulty = 2  # Hard
	var gm = _fresh_gm()
	gm.start_new_game("integrity-seed-2")
	assert_eq(gm.state.attention_per_month,
		Balance.inum("difficulty.standard.attention_per_month", 20),
		"#1084: a settings-written Hard must still PLAY Standard")
	await _release(gm)

func test_effective_difficulty_is_standard_regardless_of_raw_value():
	for raw in [0, 1, 2, -1, 999]:
		GameConfig.difficulty = raw
		assert_eq(GameConfig.effective_difficulty(), 1,
			"league lock: effective difficulty must be Standard for raw value %d" % raw)

func test_raw_preference_survives_and_returns_when_lock_lifts():
	# The raw field is the player's stored PREFERENCE: the lock must not stomp it,
	# and it is honoured again the day the lock lifts (test seam = the lifted state).
	GameConfig.difficulty = 2
	assert_eq(GameConfig.effective_difficulty(), 1, "locked: plays Standard")
	assert_eq(GameConfig.difficulty, 2, "locked: stored preference untouched")
	GameConfig._difficulty_lock_override = false  # the day the lock lifts
	assert_eq(GameConfig.effective_difficulty(), 2, "unlocked: preference honoured")
	GameConfig.difficulty = 999
	assert_eq(GameConfig.effective_difficulty(), 1,
		"unlocked: an invalid persisted value still degrades to Standard (#447 family)")

# === Piece 2: Alpha Tools -- sticky, one-way, run-scoped ==========================

func test_alpha_tools_use_makes_run_unranked():
	assert_true(GameConfig.is_ranked_run(), "a clean standard run is ranked")
	GameConfig.mark_alpha_tools_used(12)
	assert_false(GameConfig.is_ranked_run(),
		"using an Alpha Tool must take the run off the board")

func test_flag_is_sticky_after_toggling_the_tool_off():
	# The exploit the decision card names: use a power at turn 30, turn the tool back
	# off, finish "clean". Toggling the overlay off is the only off-switch the player
	# has, and it must not restore ranking.
	var gm = _fresh_gm()
	gm.name = "GameManager"  # the overlay's ../GameManager fallback resolves HERE
	gm.start_new_game("integrity-seed-sticky")
	GameConfig.mark_alpha_tools_used(30)
	var overlay = DEBUG_OVERLAY.instantiate()
	add_child_autofree(overlay)
	overlay.toggle_visibility()  # tool on (renders the live state)
	overlay.toggle_visibility()  # tool back off
	assert_false(GameConfig.is_ranked_run(),
		"turning the tool off must NOT restore ranking -- the flag is one-way")
	assert_eq(GameConfig.alpha_tools_first_use_turn, 30,
		"the first-use turn is fixed at first use")
	await _release(gm)

func test_second_use_is_not_a_new_first_use():
	assert_true(GameConfig.mark_alpha_tools_used(10),
		"first use returns true -- the one moment the mid-run warning fires")
	assert_false(GameConfig.mark_alpha_tools_used(40),
		"later uses return false -- no repeat warning, no rewrite")
	assert_eq(GameConfig.alpha_tools_first_use_turn, 10,
		"first-use turn must not be overwritten by later uses")

func test_start_new_game_is_the_run_boundary_that_resets_the_flag():
	GameConfig.mark_alpha_tools_used(5)
	assert_false(GameConfig.is_ranked_run(), "tainted run is unranked")
	var gm = _fresh_gm()
	gm.start_new_game("integrity-seed-3")
	assert_true(GameConfig.is_ranked_run(),
		"the flag is RUN-scoped: a fresh run starts clean and ranked")
	await _release(gm)

func test_debug_overlay_add_ap_button_taints_the_run():
	# End-to-end through the real overlay handler: the "Add 5 Action Points" button
	# is an alpha tool and must flip the flag at the moment of use.
	var gm = _fresh_gm()
	gm.name = "GameManager"  # so the overlay's ../GameManager fallback resolves HERE
	gm.start_new_game("integrity-seed-4")
	var overlay = DEBUG_OVERLAY.instantiate()
	add_child_autofree(overlay)
	assert_true(GameConfig.is_ranked_run(), "run starts ranked")
	overlay._on_add_ap_button_pressed()
	assert_false(GameConfig.is_ranked_run(),
		"the Add 5 Action Points button must unrank the run at the moment of use")
	assert_eq(GameConfig.alpha_tools_first_use_turn, gm.state.turn,
		"the taint records the turn the tool was used on")
	await _release(gm)

func test_save_load_cannot_launder_the_flag():
	# The laundering attempt: use a tool, save the tainted run, start fresh (flag
	# resets), then load the save back. The envelope must bring the taint with it.
	var gm = _fresh_gm()
	gm.start_new_game("integrity-seed-5")
	GameConfig.mark_alpha_tools_used(gm.state.turn)
	assert_true(gm.save_game(TEST_SAVE_PATH), "saving the tainted run must succeed")
	gm.start_new_game("integrity-seed-6", true)
	assert_true(GameConfig.is_ranked_run(), "the interposed fresh run is clean")
	assert_true(gm.load_saved_game(TEST_SAVE_PATH, true), "loading back must succeed")
	assert_false(GameConfig.is_ranked_run(),
		"a loaded tainted save stays UNRANKED -- save/load must not launder the flag")
	await _release(gm)

func test_loading_a_clean_save_from_a_tainted_session_is_ranked():
	# The other direction: the flag belongs to the RUN in the save, so a genuinely
	# clean save loaded after a tainted session must come back ranked.
	var gm = _fresh_gm()
	gm.start_new_game("integrity-seed-7")
	assert_true(gm.save_game(TEST_SAVE_PATH), "saving the clean run must succeed")
	GameConfig.mark_alpha_tools_used(3)  # session gets tainted after the save
	assert_true(gm.load_saved_game(TEST_SAVE_PATH, true), "loading back must succeed")
	assert_true(GameConfig.is_ranked_run(),
		"a clean save must not inherit the session's later taint")
	await _release(gm)

func test_scenario_gate_still_works_beside_the_alpha_flag():
	GameConfig.scenario_id = "sandbox_mode"
	assert_false(GameConfig.is_ranked_run(), "scenario runs stay unranked (#1060)")
	GameConfig.scenario_id = ""
	assert_true(GameConfig.is_ranked_run(), "standard run ranked again")

func test_first_use_message_names_the_turn_and_the_one_way_rule():
	# Settled wording (decision card): the mid-run warning is the only place the
	# player learns the flag is one-way, so it must say so, with the turn number.
	GameConfig.mark_alpha_tools_used(30)
	var msg := GameConfig.alpha_tools_first_use_message()
	assert_string_contains(msg, "UNRANKED")
	assert_string_contains(msg, "turn 30")
	assert_string_contains(msg, "does not undo")

extends GutTest
## Ship blocker (v0.14.0, league night 2026-08-07): Pip finished a clean 147-turn
## ranked run and reported "nothing, no opportunity to submit, no reminder". The
## score WAS saved locally and the submit WAS dispatched -- the player was simply
## never told, and could not get to a board from where he was standing.
##
## Measured on tag v0.14.0 before this guard existed (headless probe, 1920x1080):
##   StatsLabel box   = 720 x 300 px, scroll_active = true, scroll value = 0
##   content_height   = 690 px  ->  390 px of overflow
##   line_count       = 30, visible_line_count = 14
##   line 30 of 30    = "> Press ENTER for Leaderboard"
##   ButtonsHBox      = [Copy result] [Play Again] [Main Menu]
## So the ONLY advertised route from a finished run to the leaderboard was a
## keyboard hint sitting 390 px below the fold of a scroll box nobody scrolls,
## and no button offered it. That is the missing affordance.
##
## This guard pins the route to something a player can SEE: a real button in the
## end-screen button row, and a remote-sync status blip that sits inside the
## panel's reading flow rather than orphaned underneath the buttons.

const SCENE_PATH := "res://scenes/ui/game_over_screen.tscn"
const BUTTONS_PATH := "CenterContainer/PanelContainer/MarginContainer/VBox/ButtonsHBox"
const VBOX_PATH := "CenterContainer/PanelContainer/MarginContainer/VBox"

var _prev := {}

func before_each():
	_prev = {
		"enabled": LeaderboardSync.enabled,
		"base": LeaderboardSync.base_url,
		"token": LeaderboardSync.token,
		"optin": GameConfig.submit_scores_global,
		"asked": GameConfig.leaderboard_consent_asked,
		"shown": GameConfig.default_identity_prompt_shown,
		"scenario": GameConfig.scenario_id,
		"player": GameConfig.player_name,
		"lab": GameConfig.lab_name,
	}
	# Pip's live profile at the time of the report: ranked, consented, opted in,
	# identity prompt already answered -> the plain "submit" path.
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "http://127.0.0.1:9"
	LeaderboardSync.token = "test-token"
	GameConfig.scenario_id = ""
	GameConfig.leaderboard_consent_asked = true
	GameConfig.submit_scores_global = true
	GameConfig.default_identity_prompt_shown = true
	GameConfig.player_name = "Beb"
	GameConfig.lab_name = "GRIM"

func after_each():
	LeaderboardSync.enabled = _prev["enabled"]
	LeaderboardSync.base_url = _prev["base"]
	LeaderboardSync.token = _prev["token"]
	GameConfig.submit_scores_global = _prev["optin"]
	GameConfig.leaderboard_consent_asked = _prev["asked"]
	GameConfig.default_identity_prompt_shown = _prev["shown"]
	GameConfig.scenario_id = _prev["scenario"]
	GameConfig.player_name = _prev["player"]
	GameConfig.lab_name = _prev["lab"]
	if FileAccess.file_exists(LeaderboardSync.OUTBOX_PATH):
		DirAccess.remove_absolute(LeaderboardSync.OUTBOX_PATH)

func _defeat_state() -> Dictionary:
	return {
		"game_over": true, "victory": false, "turn": 147, "doom": 100.0,
		"reputation": 20, "money": 5000, "compute": 3.0, "research": 4.0,
		"papers": 1, "safety_researchers": 3, "capability_researchers": 2,
		"compute_engineers": 1, "purchased_upgrades": ["a", "b"],
	}

func _shown_screen() -> Control:
	var screen: Control = load(SCENE_PATH).instantiate()
	add_child_autofree(screen)
	screen.set_anchors_preset(Control.PRESET_FULL_RECT)
	screen.set_deferred("size", Vector2(1920, 1080))
	await get_tree().process_frame
	screen.show_game_over(false, _defeat_state())
	for i in range(3):
		await get_tree().process_frame
	return screen

func test_a_finished_run_offers_a_visible_button_to_the_board():
	# The defect: the route existed only as ENTER, advertised on line 30 of a
	# 14-line window. A player who does not scroll never learns it exists.
	var screen: Control = await _shown_screen()
	var found: Button = null
	for b in screen.get_node(BUTTONS_PATH).get_children():
		if b is Button and str(b.text).to_lower().contains("leaderboard"):
			found = b
	assert_not_null(found,
		"the end screen must offer a VISIBLE leaderboard button -- the ENTER hint sits below the scroll fold")
	if found != null:
		assert_true(found.is_visible_in_tree(), "leaderboard button is actually on screen")
		assert_gt(found.size.x, 0.0, "leaderboard button has non-zero width")
		assert_true(found.pressed.is_connected(screen._continue_to_leaderboard),
			"leaderboard button is wired to the leaderboard route")

func test_the_enter_hint_is_not_the_only_route_and_is_above_the_fold_or_on_a_button():
	# Pins the measurement that proved the defect: whatever the stats scroll
	# overflows by, the route must not depend on the player finding its last line.
	var screen: Control = await _shown_screen()
	var sl: RichTextLabel = screen.stats_label
	var buried := sl.get_line_count() > sl.get_visible_line_count() \
		and str(sl.text).contains("Press ENTER for Leaderboard")
	var has_button := false
	for b in screen.get_node(BUTTONS_PATH).get_children():
		if b is Button and str(b.text).to_lower().contains("leaderboard"):
			has_button = true
	assert_false(buried and not has_button,
		"stats scroll overflows (%d lines, %d visible) so a buried ENTER hint cannot be the only route"
			% [sl.get_line_count(), sl.get_visible_line_count()])

func test_remote_sync_blip_sits_in_the_reading_flow_not_below_the_buttons():
	# The blip was appended LAST to the VBox, i.e. underneath the button row, at
	# 12 px. Put it where the eye already is: directly under the stats scroll.
	var screen: Control = await _shown_screen()
	assert_true(is_instance_valid(screen.sync_status_label), "a ranked opted-in run shows a sync blip")
	var vbox: Node = screen.get_node(VBOX_PATH)
	var buttons: Node = screen.get_node(BUTTONS_PATH)
	assert_lt(screen.sync_status_label.get_index(), buttons.get_index(),
		"sync status must appear ABOVE the button row, not orphaned beneath it")
	assert_true(screen.sync_status_label.is_visible_in_tree(), "sync status is on screen")

func test_submit_outcome_is_distinguishable_from_failure():
	# A successful submission that reads the same as a failure teaches the player
	# nothing. Failure must be explicit and must say the score is not lost.
	var screen: Control = await _shown_screen()
	assert_eq(screen.sync_status_label.text, "Global leaderboard: submitting...",
		"precondition: the blip starts in the submitting state")
	screen._on_sync_submit_completed(true, true, 4, "rank 4")
	var ok_text: String = screen.sync_status_label.text
	screen._on_sync_submit_completed(false, false, 0, "offline -- saved locally")
	var fail_text: String = screen.sync_status_label.text
	assert_true(ok_text.begins_with("[OK]"),
		"a landed score is marked [OK]: got '%s'" % ok_text)
	assert_true(fail_text.begins_with("[!]"),
		"a failed submit is marked [!]: got '%s'" % fail_text)
	assert_true(fail_text.to_lower().contains("retry"),
		"a failed submit must say the score is queued for retry, not silently shrug: got '%s'" % fail_text)

extends GutTest
## Pip's v0.14.0 playtest, 2026-08-07 -- the game-over half of "the leaderboard is
## invisible". Two defects, both of which end with a submission the player never sees.
##
## DEFECT 3 -- WHERE the confirmation renders. sync_status_label was 12pt, ~17px tall,
## and appended to the END of the panel VBox, i.e. BELOW the three 50px buttons. The
## measurement from the failing build:
##   text="Global leaderboard: submitted (rank 1)" rect=(600,1217) 720x17
## A successful submission was visually indistinguishable from nothing happening. The
## bug was never in the submitting; it was in the reporting.
##
## DEFECT 1 -- an anonymous player's ONE nudge, then permanent silence.
## consent_flow_state(asked=false, opted_in=false, has_identity=false, reminded=false)
## returns "remind" once and "silent" for the rest of the install's life. Anonymous is
## the DEFAULT state of a fresh install (game_config.gd:108-109), so the default player
## gets one easily-missed line and is then absent from the board forever with no signal.
##
## WHAT IS NOT UP FOR REVISION: the opt-in requirement itself (privacy ruling
## 2026-07-26). Nothing here defaults anyone to opted-in, and nothing here uploads
## anything. The defect is that a NOT-YET-DECIDED state was rendered identically to a
## DECIDED one, and then decayed to silence.
##
## THE ARGUMENT FOR THE CHOSEN FIX, since a once-only nudge is what failed: the honest
## thing is a STANDING STATE READOUT, not a repeated nudge. A status line that is
## present on every game-over says "your score is local" as a fact about the current
## configuration, the same way a mute icon says the sound is off. It never interrupts,
## never opens a dialog, never escalates, and never changes wording to chase the player
## -- so it cannot become a nag no matter how many runs are played. The rejected
## alternatives: (a) re-prompting every N runs, which is precisely the nagging the
## remind-once ruling forbids; (b) leaving it silent, which is the defect; (c) a
## settings-only indicator, which is invisible from the one screen where the player is
## asking "where did my score go?".
##
## WHAT THESE TESTS CANNOT PROVE: that the relocated label is legible against the panel
## art, or that the wording reads well. That needs Pip on a real build. They prove the
## label is placed above the buttons at a size somebody could notice, and that the
## anonymous state is stated on every run rather than once.

const SCENE_PATH := "res://scenes/ui/game_over_screen.tscn"

var _prev_enabled: bool
var _prev_base: String
var _prev_token: String
var _prev_optin: bool
var _prev_asked: bool
var _prev_reminded: bool
var _prev_scenario: String
var _prev_player: String
var _prev_lab: String

func before_each():
	_prev_enabled = LeaderboardSync.enabled
	_prev_base = LeaderboardSync.base_url
	_prev_token = LeaderboardSync.token
	_prev_optin = GameConfig.submit_scores_global
	_prev_asked = GameConfig.leaderboard_consent_asked
	_prev_reminded = GameConfig.leaderboard_reminder_shown
	_prev_scenario = GameConfig.scenario_id
	_prev_player = GameConfig.player_name
	_prev_lab = GameConfig.lab_name
	GameConfig.scenario_id = ""
	GameConfig.reset_alpha_tools_flag()
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "http://127.0.0.1:9"  # discard port: refuses instantly
	LeaderboardSync.token = "test-token-not-a-real-secret"

func after_each():
	LeaderboardSync.enabled = _prev_enabled
	LeaderboardSync.base_url = _prev_base
	LeaderboardSync.token = _prev_token
	GameConfig.submit_scores_global = _prev_optin
	GameConfig.leaderboard_consent_asked = _prev_asked
	GameConfig.leaderboard_reminder_shown = _prev_reminded
	GameConfig.scenario_id = _prev_scenario
	GameConfig.player_name = _prev_player
	GameConfig.lab_name = _prev_lab

func _screen() -> Control:
	var s: Control = (load(SCENE_PATH) as PackedScene).instantiate()
	add_child_autofree(s)
	return s

# --- DEFECT 3: the confirmation must render where a human is looking -----------

func _buttons_index(screen: Control) -> int:
	var vbox: Node = screen.stats_label.get_parent()
	for i in range(vbox.get_child_count()):
		if vbox.get_child(i).name == "ButtonsHBox":
			return i
	return -1

func test_status_label_sits_above_the_buttons_not_below_them():
	var screen := _screen()
	screen._ensure_sync_status_label()
	var label: Label = screen.sync_status_label
	var vbox: Node = screen.stats_label.get_parent()
	var buttons_idx := _buttons_index(screen)
	assert_gt(buttons_idx, -1, "precondition: the ButtonsHBox row exists in the panel")
	assert_eq(label.get_parent(), vbox, "precondition: the label lives in the panel VBox")
	assert_lt(label.get_index(), buttons_idx,
		"the submission status was appended BELOW three 50px buttons (measured at y=1217, " +
		"the last line in the panel). It must sit above them, near the score.")

func test_status_label_is_big_enough_to_notice():
	# 12pt / 17px tall was the measured size of the line nobody saw. This does not claim
	# a specific size is correct -- only that the size which demonstrably failed is gone.
	var screen := _screen()
	screen._ensure_sync_status_label()
	assert_gte(screen.sync_status_label.get_theme_font_size("font_size"), 16,
		"12pt at the bottom of the panel is the size that read as 'nothing happened'")

# --- DEFECT 1: a not-yet-decided player is told, every run --------------------

func _defeat_state() -> Dictionary:
	return {
		"game_over": true, "victory": false, "turn": 147, "doom": 100.0,
		"reputation": 0, "money": 5000, "compute": 3.0, "research": 4.0, "papers": 1,
	}

func _anonymous_already_nudged() -> Control:
	GameConfig.leaderboard_consent_asked = false
	GameConfig.submit_scores_global = false
	GameConfig.leaderboard_reminder_shown = true  # the one nudge is spent
	GameConfig.player_name = ""
	GameConfig.lab_name = ""
	var s := _screen()
	s.show_game_over(false, _defeat_state())
	return s

func test_anonymous_player_is_still_told_where_the_score_went():
	assert_eq(LeaderboardSync.consent_flow_state(false, false, false, true), "silent",
		"precondition: an already-nudged anonymous player resolves to the silent flow")
	var screen := _anonymous_already_nudged()
	var label: Label = screen.sync_status_label
	assert_true(is_instance_valid(label),
		"the DEFAULT install state (anonymous, never opted in) must not render a blank " +
		"screen -- silence here is indistinguishable from a broken leaderboard")
	assert_true(label.visible, "constructed but hidden is the same as absent")
	assert_string_contains(label.text.to_lower(), "settings",
		"the standing notice must point at where the player can change it")

func test_standing_notice_is_a_readout_never_a_prompt():
	# The non-nagging half of the design, pinned so a later change cannot quietly turn
	# the standing line into a recurring dialog (which the remind-once ruling forbids).
	var screen := _anonymous_already_nudged()
	for child in screen.get_children():
		assert_false(child is AcceptDialog,
			"an already-nudged anonymous player must never be re-prompted -- " +
			"the standing indication is a status line, not a dialog")

func test_standing_notice_does_not_opt_anybody_in():
	# The privacy ruling (2026-07-26) is not up for revision: showing the state must
	# never change the state, and no upload may be attempted.
	var screen := _anonymous_already_nudged()
	assert_false(GameConfig.submit_scores_global,
		"rendering a notice must not flip the opt-in flag")
	assert_false(GameConfig.leaderboard_consent_asked,
		"an anonymous player has still not been ASKED -- the notice is not a decision")
	assert_false(LeaderboardSync.should_submit(),
		"no upload is permitted for a player who has not opted in")
	assert_true(is_instance_valid(screen), "screen instantiated")

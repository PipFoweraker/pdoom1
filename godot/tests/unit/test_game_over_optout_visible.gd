extends GutTest
## Regression (Pip's v0.14.0 playtest, 2026-08-07): a RANKED run on a profile that
## had previously declined the global leaderboard showed the player NOTHING at
## game over -- no submit, no notice, no error. Three runs, three silent screens,
## read as "the leaderboard is broken".
##
## Measured cause: consent_flow_state(asked=true, opted_in=false, ...) returns
## "silent", and _continue_consent_flow's default branch was a bare `pass`. The
## decline moment itself DOES render "Global leaderboard: local only (change in
## Settings)" -- but every run after it rendered nothing at all, so the setting
## became invisible and unfindable from the only screen that depends on it.
##
## This is the project's signature failure mode (#1027): a score that simply
## never appears. The score IS saved locally; the screen must say so.

const SCENE_PATH := "res://scenes/ui/game_over_screen.tscn"

var _prev_enabled: bool
var _prev_base: String
var _prev_token: String
var _prev_optin: bool
var _prev_asked: bool
var _prev_reminded: bool
var _prev_scenario: String

func before_each():
	_prev_enabled = LeaderboardSync.enabled
	_prev_base = LeaderboardSync.base_url
	_prev_token = LeaderboardSync.token
	_prev_optin = GameConfig.submit_scores_global
	_prev_asked = GameConfig.leaderboard_consent_asked
	_prev_reminded = GameConfig.leaderboard_reminder_shown
	_prev_scenario = GameConfig.scenario_id
	# A RANKED run, stated explicitly (a machine with a scenario or a sticky Alpha
	# Tools flag would otherwise take the unranked branch for unrelated reasons).
	GameConfig.scenario_id = ""
	GameConfig.reset_alpha_tools_flag()
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "http://127.0.0.1:9"  # refuses fast; never used here
	LeaderboardSync.token = "test-token"

func after_each():
	LeaderboardSync.enabled = _prev_enabled
	LeaderboardSync.base_url = _prev_base
	LeaderboardSync.token = _prev_token
	GameConfig.submit_scores_global = _prev_optin
	GameConfig.leaderboard_consent_asked = _prev_asked
	GameConfig.leaderboard_reminder_shown = _prev_reminded
	GameConfig.scenario_id = _prev_scenario

func _defeat_state() -> Dictionary:
	return {
		"game_over": true, "victory": false, "turn": 147, "doom": 100.0,
		"reputation": 0, "money": 5000, "compute": 3.0, "research": 4.0, "papers": 1,
	}

func _run_to_game_over() -> Control:
	var screen: Control = (load(SCENE_PATH) as PackedScene).instantiate()
	add_child_autofree(screen)
	screen.show_game_over(false, _defeat_state())
	return screen

func test_remembered_decline_still_tells_the_player_where_the_score_went():
	# The exact profile state measured in Pip's config.cfg on the failing night:
	# submit_scores_global=false, consent_asked=true.
	GameConfig.leaderboard_consent_asked = true
	GameConfig.submit_scores_global = false
	assert_eq(LeaderboardSync.consent_flow_state(true, false, true, false), "silent",
		"precondition: a remembered decline resolves to the silent flow")

	var screen := _run_to_game_over()

	assert_ne(screen.leaderboard_entry_uuid, "",
		"precondition: the score IS saved locally -- the local board is never gated by consent")
	var label = screen.sync_status_label
	assert_true(is_instance_valid(label),
		"a declined player must still SEE something: silence is indistinguishable from a broken leaderboard")
	assert_true(label.visible, "the status label must be visible, not merely constructed")
	assert_string_contains(label.text.to_lower(), "settings",
		"the notice must point at the setting that turns submission back on")

func test_anonymous_already_nudged_stays_quiet():
	# The OTHER "silent" case must not become a nag: an anonymous player who has
	# already had their one gracious nudge is exercising a legitimate choice.
	GameConfig.leaderboard_consent_asked = false
	GameConfig.submit_scores_global = false
	GameConfig.leaderboard_reminder_shown = true
	GameConfig.player_name = ""
	GameConfig.lab_name = ""

	var screen := _run_to_game_over()

	assert_false(is_instance_valid(screen.sync_status_label),
		"remind-once ruling: an already-nudged anonymous player is never nagged again")

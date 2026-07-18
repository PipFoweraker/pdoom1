extends GutTest
## Regression: the remote score POST at game-over must never crash, block, or quit
## the defeat screen. Drives the real GameOverScreen scene with LeaderboardSync ENABLED
## but pointed at an UNREACHABLE endpoint (the live-build condition that first exposed the
## "weird quit" -- leaderboard_config.json enabled=true), and asserts the screen still
## renders and the game-over flow completes without throwing.
##
## See fix/endgame-quit-score-post. The sync client is async/defensive on its own; this
## guards the CALL SITE (game_over_screen.show_game_over) and the fire-and-forget contract.

const SCENE_PATH := "res://scenes/ui/game_over_screen.tscn"

var _prev_enabled: bool
var _prev_base: String
var _prev_token: String
var _prev_optin: bool

func before_each():
	_prev_enabled = LeaderboardSync.enabled
	_prev_base = LeaderboardSync.base_url
	_prev_token = LeaderboardSync.token
	_prev_optin = GameConfig.submit_scores_global
	if FileAccess.file_exists(LeaderboardSync.OUTBOX_PATH):
		DirAccess.remove_absolute(LeaderboardSync.OUTBOX_PATH)

func after_each():
	LeaderboardSync.enabled = _prev_enabled
	LeaderboardSync.base_url = _prev_base
	LeaderboardSync.token = _prev_token
	GameConfig.submit_scores_global = _prev_optin
	if FileAccess.file_exists(LeaderboardSync.OUTBOX_PATH):
		DirAccess.remove_absolute(LeaderboardSync.OUTBOX_PATH)

func _defeat_state() -> Dictionary:
	# Minimal game-over defeat state: doom>=100 death. Every consumer uses .get() with a
	# default, so a sparse dict is a valid worst-case.
	return {
		"game_over": true,
		"victory": false,
		"turn": 12,
		"doom": 100.0,
		"reputation": 20,
		"money": 5000,
		"compute": 3.0,
		"research": 4.0,
		"papers": 1,
	}

func _instance_screen() -> Control:
	var scene: PackedScene = load(SCENE_PATH)
	var screen: Control = scene.instantiate()
	add_child_autofree(screen)
	return screen

func test_show_game_over_survives_unreachable_remote():
	# Live-build condition: sync ENABLED + opted in, but the endpoint refuses fast.
	# Port 9 (discard) on loopback -> RESULT_CANT_CONNECT without waiting on DNS/timeout.
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "http://127.0.0.1:9"
	LeaderboardSync.token = "test-token"
	GameConfig.submit_scores_global = true
	assert_true(LeaderboardSync.should_submit(), "precondition: sync would submit")

	var screen := _instance_screen()
	# Must not throw. Defeat -> doom>=100 path.
	screen.show_game_over(false, _defeat_state())

	assert_true(screen.visible, "defeat screen renders despite remote sync being live")
	assert_gt(screen.final_turns, 0, "score tuple computed")

	# Let the async HTTPRequest resolve/fail; the failure must stay contained.
	await get_tree().create_timer(0.3).timeout
	assert_true(is_instance_valid(screen), "screen still valid after remote failure resolves")

func test_show_game_over_is_idempotent():
	# main_ui calls _on_game_state_updated (hence show_game_over) from multiple sites; a
	# game-over state must be processed ONCE, not re-fire the remote POST every frame.
	#
	# We assert this DETERMINISTICALLY via the durable outbox (each submit_score writes its
	# body there synchronously, de-duped by entry_uuid) instead of racing the async network
	# completion: an unreachable endpoint can take up to the full request timeout to resolve,
	# so counting submit_completed emissions inside a short window is inherently flaky. The
	# re-entrancy guard means 4 refreshes create ONE score entry -> ONE queued body; a broken
	# guard would create four distinct uuids -> four queued bodies.
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "http://127.0.0.1:9"
	LeaderboardSync.token = "test-token"
	GameConfig.submit_scores_global = true

	var screen := _instance_screen()
	for i in range(4):
		screen.show_game_over(false, _defeat_state())

	assert_eq(LeaderboardSync._read_outbox().size(), 1,
		"remote submit fires once, not once-per-refresh (re-entrancy guard)")

func test_show_game_over_noop_when_sync_disabled():
	LeaderboardSync.enabled = false
	var screen := _instance_screen()
	screen.show_game_over(false, _defeat_state())
	assert_true(screen.visible, "defeat screen renders with sync disabled")

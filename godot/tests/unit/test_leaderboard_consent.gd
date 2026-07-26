extends GutTest
## Identity-consent flow tests (privacy ruling 2026-07-26; docs/PRIVACY_POSTURE.md).
## The game-over screen routes score submission through
## LeaderboardSync.consent_flow_state -- a PURE helper, so the whole state
## machine is tested here without scenes or network:
##   - first-time opt-in required before any named submission
##   - the empty-name gracious reminder fires exactly once, ever
##   - remembered decline = silence (no hounding), local play unaffected
##   - settings round-trip persists every consent + privacy key

var SyncScript = load("res://autoload/leaderboard_sync.gd")


# ---- consent_flow_state: the full matrix ------------------------------------
# args: (asked, opted_in, has_identity, reminded)

func test_first_time_with_identity_asks():
	# The core ruling: reaching submission un-asked with a usable name/lab MUST
	# route to the explicit one-time opt-in -- never straight to a submit.
	assert_eq(SyncScript.consent_flow_state(false, false, true, false), "ask")
	assert_eq(SyncScript.consent_flow_state(false, true, true, false), "ask",
		"even a legacy opted-in-looking flag still requires the explicit click first")
	assert_eq(SyncScript.consent_flow_state(false, false, true, true), "ask",
		"the anonymous-nudge flag is irrelevant once the player has an identity")

func test_granted_consent_submits():
	assert_eq(SyncScript.consent_flow_state(true, true, true, false), "submit")
	assert_eq(SyncScript.consent_flow_state(true, true, true, true), "submit")

func test_declined_consent_is_silent_no_hounding():
	# Remembered decline: silent on every later playthrough, whatever else holds.
	assert_eq(SyncScript.consent_flow_state(true, false, true, false), "silent")
	assert_eq(SyncScript.consent_flow_state(true, false, false, false), "silent")
	assert_eq(SyncScript.consent_flow_state(true, false, true, true), "silent")

func test_anonymous_first_time_reminds_exactly_once():
	# Empty name/lab + never asked: ONE gracious reminder...
	assert_eq(SyncScript.consent_flow_state(false, false, false, false), "remind")
	# ...and only one -- the persisted flag turns every later pass silent.
	assert_eq(SyncScript.consent_flow_state(false, false, false, true), "silent")
	assert_eq(SyncScript.consent_flow_state(false, true, false, true), "silent")


# ---- opted-out players keep playing + local scores --------------------------

func test_declined_consent_never_blocks_fetch_or_local():
	# Viewing the global board is read-only and un-gated by consent; the local
	# score save happens BEFORE the consent flow in game_over_screen
	# (_persist_and_submit_score) and is asserted end-to-end in
	# test_game_over_remote_isolation.test_declined_consent_keeps_score_local.
	var prev = GameConfig.submit_scores_global
	var prev_asked = GameConfig.leaderboard_consent_asked
	GameConfig.submit_scores_global = false
	GameConfig.leaderboard_consent_asked = true
	var s = SyncScript.new()
	s.enabled = true
	s.base_url = "https://api.pdoom1.com"
	s.token = "realtoken"
	assert_true(s.can_fetch(), "declined players still VIEW the global board")
	assert_false(s.should_submit(), "declined players never upload")
	s.free()
	GameConfig.submit_scores_global = prev
	GameConfig.leaderboard_consent_asked = prev_asked


# ---- settings round-trip: every consent/privacy key survives save+load ------

func test_settings_round_trip_consent_and_privacy_keys():
	# Snapshot the player's real values; the test ends by restoring AND
	# re-persisting them, leaving disk exactly as found.
	var orig := {
		"asked": GameConfig.leaderboard_consent_asked,
		"optin": GameConfig.submit_scores_global,
		"reminded": GameConfig.leaderboard_reminder_shown,
		"ping": GameConfig.send_launch_ping,
		"dismissed": GameConfig.dismissed_update_version,
	}

	# Distinctive test values (each the opposite of its default).
	GameConfig.leaderboard_consent_asked = true
	GameConfig.submit_scores_global = true
	GameConfig.leaderboard_reminder_shown = true
	GameConfig.send_launch_ping = false
	GameConfig.dismissed_update_version = "9.9.9"
	GameConfig.save_config()

	# Scramble in-memory, then load back from disk.
	GameConfig.leaderboard_consent_asked = false
	GameConfig.submit_scores_global = false
	GameConfig.leaderboard_reminder_shown = false
	GameConfig.send_launch_ping = true
	GameConfig.dismissed_update_version = ""
	GameConfig.load_config()

	assert_true(GameConfig.leaderboard_consent_asked, "consent_asked persisted")
	assert_true(GameConfig.submit_scores_global, "identity opt-in persisted")
	assert_true(GameConfig.leaderboard_reminder_shown, "reminder flag persisted")
	assert_false(GameConfig.send_launch_ping, "ping opt-out persisted")
	assert_eq(GameConfig.dismissed_update_version, "9.9.9", "dismissed update version persisted")

	# Restore the player's real values on disk and in memory.
	GameConfig.leaderboard_consent_asked = orig["asked"]
	GameConfig.submit_scores_global = orig["optin"]
	GameConfig.leaderboard_reminder_shown = orig["reminded"]
	GameConfig.send_launch_ping = orig["ping"]
	GameConfig.dismissed_update_version = orig["dismissed"]
	GameConfig.save_config()

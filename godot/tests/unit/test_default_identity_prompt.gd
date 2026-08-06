extends GutTest
## Default-identity prompt tests (Pip 2026-08-06: two friends' first scores
## landed on the global board as identical "AI Safety Lab" rows).
##
## The game-over screen layers LeaderboardSync.default_identity_prompt_state
## ON TOP of the consent flow -- consent_flow_state itself (privacy ruling
## 2026-07-26) is untouched and stays covered by test_leaderboard_consent.gd.
## Tested here:
##   - the prompt fires ONLY when an upload is imminent with a default identity
##     and has never been offered before
##   - anonymity ("remind"/"silent") and remembered decline are never nagged
##   - GameConfig.has_default_identity() -- either unedited field arms it
##   - the persisted shown-flag round-trips through save/load
##   - Leaderboard.rename_entry retrofits the local row name-only

var SyncScript = load("res://autoload/leaderboard_sync.gd")


# ---- default_identity_prompt_state: the matrix ------------------------------
# args: (flow, is_default, prompt_shown)

func test_prompt_fires_when_upload_imminent_with_default_identity():
	# The two states where an upload is imminent are exactly the two that prompt.
	assert_eq(SyncScript.default_identity_prompt_state("submit", true, false), "prompt",
		"consented player about to auto-upload the default name must get the one-time ask")
	assert_eq(SyncScript.default_identity_prompt_state("ask", true, false), "prompt",
		"first-time consent with a default name: claim the name BEFORE it is worth uploading")

func test_prompt_never_fires_twice():
	# The persisted flag (set at SHOW time) silences it forever -- a player who
	# kept the default made a legitimate choice and is never nagged again.
	assert_eq(SyncScript.default_identity_prompt_state("submit", true, true), "pass")
	assert_eq(SyncScript.default_identity_prompt_state("ask", true, true), "pass")

func test_prompt_never_fires_for_claimed_identity():
	assert_eq(SyncScript.default_identity_prompt_state("submit", false, false), "pass")
	assert_eq(SyncScript.default_identity_prompt_state("ask", false, false), "pass")

func test_prompt_never_fires_when_no_upload_imminent():
	# "remind" = anonymous nudge path, "silent" = remembered decline or already
	# nudged. Neither uploads, so neither may nag about names -- anonymity and
	# decline are legitimate choices (same ruling as the remind-once shape).
	for flow in ["remind", "silent"]:
		assert_eq(SyncScript.default_identity_prompt_state(flow, true, false), "pass",
			"'%s' must never surface the identity prompt" % flow)
		assert_eq(SyncScript.default_identity_prompt_state(flow, true, true), "pass")


# ---- GameConfig.has_default_identity ----------------------------------------

func test_has_default_identity_matrix():
	var prev_player = GameConfig.player_name
	var prev_lab = GameConfig.lab_name

	GameConfig.player_name = GameConfig.DEFAULT_PLAYER_NAME
	GameConfig.lab_name = GameConfig.DEFAULT_LAB_NAME
	assert_true(GameConfig.has_default_identity(), "both fields default")

	GameConfig.player_name = "Pip"
	assert_true(GameConfig.has_default_identity(),
		"lab still default: the board renders the LAB name, so the entry is still generic")

	GameConfig.player_name = GameConfig.DEFAULT_PLAYER_NAME
	GameConfig.lab_name = "Notkilleveryone Inc"
	assert_true(GameConfig.has_default_identity(), "player name still default")

	GameConfig.player_name = "Pip"
	assert_false(GameConfig.has_default_identity(), "both fields claimed")

	# Exact match on purpose: a deliberately-typed near-default is a choice.
	GameConfig.player_name = "researcher"
	GameConfig.lab_name = "My AI Safety Lab"
	assert_false(GameConfig.has_default_identity(),
		"only the literal unedited defaults count as 'default'")

	GameConfig.player_name = prev_player
	GameConfig.lab_name = prev_lab


# ---- persistence: the shown-flag survives save/load -------------------------

func test_prompt_shown_flag_round_trips():
	var orig := {
		"shown": GameConfig.default_identity_prompt_shown,
	}

	GameConfig.default_identity_prompt_shown = true
	GameConfig.save_config()
	GameConfig.default_identity_prompt_shown = false
	GameConfig.load_config()
	assert_true(GameConfig.default_identity_prompt_shown,
		"identity_prompt_shown must persist -- otherwise the prompt fires every session")

	# Restore the player's real value on disk and in memory.
	GameConfig.default_identity_prompt_shown = orig["shown"]
	GameConfig.save_config()


# ---- Leaderboard.rename_entry: the local-row retrofit -----------------------

func test_rename_entry_renames_in_place_name_only():
	var board = Leaderboard.new("test_identity_rename_%d" % Time.get_ticks_usec(), "test")
	var entry = Leaderboard.ScoreEntry.new(12, "AI Safety Lab", 12, "vtest", 60.0)
	var other = Leaderboard.ScoreEntry.new(30, "Rival Lab", 30, "vtest", 90.0)
	board.add_score(entry)
	board.add_score(other)

	assert_true(board.rename_entry(entry.entry_uuid, "Paperclip Holdings"))
	assert_eq(entry.player_name, "Paperclip Holdings")
	assert_eq(other.player_name, "Rival Lab", "only the targeted row is renamed")
	assert_eq(board.get_top_scores(1)[0].entry_uuid, other.entry_uuid,
		"rename is name-only: rank order untouched")

	# Guards: unknown uuid and empty name are refused.
	assert_false(board.rename_entry("no-such-uuid", "X"))
	assert_false(board.rename_entry(entry.entry_uuid, "   "))
	assert_eq(entry.player_name, "Paperclip Holdings")

	board.clear()
	board.free()

extends GutTest
## Destructive tests for GameManager.resign() -- the "Accept Your Fate" path (#959).
##
## WHY DESTRUCTIVE RATHER THAN HAPPY-PATH. resign() is a brand-new trigger into the
## game-over -> leaderboard transition, and that transition is the one that segfaulted
## the v0.11.0 release. A happy-path test proves the button works when everything is
## fine, which is the case nobody was worried about. These push at the states a real
## player is actually in when they give up: nothing queued, mid-turn, already dead,
## clicking twice because the first click did not obviously do anything.
##
## Two traps were found by construction while writing resign(), and both are pinned
## here so they cannot come back silently:
##
##   1. Doom must be written through state.doom_system.current_doom, NOT state.doom.
##      check_win_lose() re-syncs `doom = doom_system.current_doom` before testing the
##      threshold, so a direct write to state.doom is overwritten and the run simply
##      carries on. That failure mode is a button that looks perfect and does nothing.
##
##   2. resign() must not route through end_turn(), which REFUSES when the action queue
##      is empty -- precisely the state a bored player is in. The one player it exists
##      for is the one it would have failed.
##
## GameManager is an autoload, so every test drives it to a known state first rather
## than trusting whatever an earlier file left behind (the ordering-accident hazard,
## #1036).
##
## NOT covered here: resign() with no live run. It guards correctly (early return plus
## push_warning), but GUT counts push_warning as an unexpected error, so asserting it
## fails the test ON THE GUARD WORKING. Left to a manual check rather than weakened.

const SEED := "resign-destructive-seed"


func before_each() -> void:
	GameManager.start_new_game(SEED, true)


func after_all() -> void:
	# Leave the autoload live but consistent for whatever runs next.
	GameManager.start_new_game(SEED, true)


func _doom() -> float:
	return GameManager.state.doom


func test_resign_from_a_fresh_turn_with_nothing_queued_ends_the_run() -> void:
	# The canonical bored player: turn 1, no actions, wants out.
	assert_false(GameManager.state.game_over, "precondition: run is live")
	assert_true(GameManager.state.queued_actions.is_empty(),
		"precondition: nothing queued -- this is the state end_turn() refuses")

	GameManager.resign()

	assert_true(GameManager.state.game_over,
		"resign() must end the run even with an EMPTY action queue -- routing through "
		+ "end_turn() would refuse here, which is the one player this feature is for")
	assert_false(GameManager.state.victory, "a resigned run is not a victory")


func test_resign_drives_doom_through_the_doom_system_not_around_it() -> void:
	# Trap 1. If doom is written to state.doom only, check_win_lose() re-syncs from
	# doom_system and clobbers it -- the run continues and the button looks dead.
	GameManager.resign()

	assert_true(GameManager.state.game_over, "run ended")
	assert_almost_eq(_doom(), 100.0, 0.01, "doom reached the lose threshold")
	if GameManager.state.doom_system != null:
		assert_almost_eq(GameManager.state.doom_system.current_doom, 100.0, 0.01,
			"doom_system is the source of truth check_win_lose() re-syncs FROM -- if this "
			+ "is not 100 the write went to the wrong place and the guard is vacuous")


func test_resigning_twice_is_harmless() -> void:
	# A player clicks, nothing visibly happens for a frame, they click again.
	GameManager.resign()
	var turn_after_first := GameManager.state.turn
	var doom_after_first := _doom()

	GameManager.resign()

	assert_true(GameManager.state.game_over, "still over")
	assert_eq(GameManager.state.turn, turn_after_first,
		"a second resign must not advance or mutate the finished run")
	assert_almost_eq(_doom(), doom_after_first, 0.01, "doom unchanged by the second call")


func test_resign_after_a_natural_loss_does_not_disturb_the_result() -> void:
	# Someone opens the pause menu on the game-over screen and hits it anyway.
	GameManager.state.doom_system.current_doom = 100.0
	GameManager.state.check_win_lose()
	assert_true(GameManager.state.game_over, "precondition: already lost naturally")
	var turn_at_death := GameManager.state.turn

	GameManager.resign()

	assert_eq(GameManager.state.turn, turn_at_death,
		"resign() on an already-finished run must be a no-op, not a second death")


func test_resign_preserves_the_score_the_run_earned() -> void:
	# The whole point: the run still counts. Turns survived is the score (ADR-0002),
	# so resigning must not zero or inflate it.
	var turns_survived := GameManager.state.turn

	GameManager.resign()

	assert_eq(GameManager.state.turn, turns_survived,
		"resigning must not alter turns survived -- that IS the score")
	assert_true(GameManager.state.turn >= 1, "a resigned run still has a real score")


func test_resign_with_a_queued_action_still_ends_the_run() -> void:
	# Mid-planning abandonment: cards on the table, player is done anyway.
	# queued_actions is Array[String] (game_state.gd:251) -- appending a Dictionary is
	# type-rejected and leaves the array empty, which is how this test first failed.
	GameManager.state.queued_actions.append("test_action")
	assert_false(GameManager.state.queued_actions.is_empty(), "precondition: something queued")

	GameManager.resign()

	assert_true(GameManager.state.game_over,
		"a queued action must not block resignation")

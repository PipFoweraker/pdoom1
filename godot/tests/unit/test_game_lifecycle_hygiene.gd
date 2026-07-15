extends GutTest
## Regression guard for the game-object lifecycle leak (docs/qa/SHUTDOWN_HYGIENE_2026-07-16.md,
## Finding #1). GameState, DoomSystem, RiskPool and TurnManager all extend Node but are never
## added to the scene tree, so before the fix every start_new_game / load_saved_game orphaned
## the previous game's 4 Nodes (GUT's orphan monitor reported "8 Orphans" for two games in a
## session). GameManager._release_game_objects() now frees them symmetrically on both paths.
##
## The test drives two consecutive start_new_game calls on a fresh GameManager and asserts the
## global orphan-node count does not grow across the second call (the second start must free the
## first game's subsystems before allocating its own).

func test_start_new_game_frees_prior_game_node_subsystems() -> void:
	var GM = load("res://scripts/game_manager.gd")
	var gm = GM.new()
	add_child_autofree(gm)

	# Neutralise the background baseline simulator so it can't add per-call orphan noise.
	var prev_mode = GameConfig.baseline_mode
	var prev_seed = GameConfig.game_seed
	GameConfig.baseline_mode = 0
	GameConfig.game_seed = ""

	gm.start_new_game("hygiene-seed-1")
	await get_tree().process_frame
	await get_tree().process_frame
	var orphans_after_first: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)

	gm.start_new_game("hygiene-seed-2")
	await get_tree().process_frame
	await get_tree().process_frame
	var orphans_after_second: int = Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)

	# Clean up the trailing game's orphaned subsystems so this test does not pollute others.
	gm._release_game_objects()
	await get_tree().process_frame

	GameConfig.baseline_mode = prev_mode
	GameConfig.game_seed = prev_seed

	var delta: int = orphans_after_second - orphans_after_first
	# Before the fix delta was +4 (state + doom_system + risk_system + turn_manager).
	assert_true(delta <= 0, "second start_new_game must not leak the prior game's Node subsystems (orphan delta=%d, expected <= 0)" % delta)

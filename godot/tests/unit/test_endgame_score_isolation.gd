extends GutTest
## Release-blocker regression (fix/endgame-quit-score-post).
##
## The live v0.11.0 build "quit weirdly" at the defeat screen and NO score ever reached the
## remote board. Root cause: show_game_over() ran a multi-second SYNCHRONOUS baseline
## simulation on the main thread (freeze -> force-quit) and fired the score POST only AFTER
## it, so a force-quit during the freeze meant the POST was never dispatched. Plus there was
## no re-entrancy guard, so the game-over signal (fires on every state update) could submit
## repeatedly.
##
## These tests pin the fixed contract:
##   1. show_game_over() NEVER blocks the main thread (no synchronous baseline at defeat).
##   2. The defeat screen renders even when the remote endpoint is unreachable (no crash).
##   3. Scoring side-effects run EXACTLY ONCE across repeated game-over signals.
##   4. The durable outbox persists a pending score and drops it only on a server ack, and
##      survives a missing / malformed queue file.

const UNREACHABLE := "https://10.255.255.1"  # unroutable: connect never completes -> timeout

func before_each():
	# Isolate the outbox file per test.
	if FileAccess.file_exists(LeaderboardSync.OUTBOX_PATH):
		DirAccess.remove_absolute(LeaderboardSync.OUTBOX_PATH)

func after_each():
	if FileAccess.file_exists(LeaderboardSync.OUTBOX_PATH):
		DirAccess.remove_absolute(LeaderboardSync.OUTBOX_PATH)

func _final_state() -> Dictionary:
	return {
		"turn": 12, "doom": 100.0, "doom_integral": 640.0, "reputation": 30.0,
		"money": 15000, "compute": 4.0, "research": 22.0, "papers": 2,
		"safety_researchers": 1, "capability_researchers": 2, "compute_engineers": 0,
		"purchased_upgrades": [], "doom_momentum": 0.0, "ledger": {},
	}

func _make_screen() -> Node:
	var scene = load("res://scenes/ui/game_over_screen.tscn").instantiate()
	add_child_autofree(scene)
	return scene

# ---- 1 + 2: defeat screen is non-blocking AND survives an unreachable endpoint ----------

func test_show_game_over_does_not_block_and_survives_unreachable_endpoint():
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = UNREACHABLE
	LeaderboardSync.token = "regression-token"
	assert_true(LeaderboardSync.should_submit(), "precondition: remote submit is on")

	var scene = _make_screen()
	await get_tree().process_frame

	var t0 := Time.get_ticks_msec()
	scene.show_game_over(false, _final_state())
	var elapsed := Time.get_ticks_msec() - t0

	# The old blocking baseline sim was ~4000ms. Non-blocking must be well under that; the
	# only work here is cheap. Generous ceiling so the gate isn't flaky on a slow CI box.
	assert_lt(elapsed, 1500, "show_game_over must not block the main thread (was ~4s baseline freeze); took %dms" % elapsed)
	assert_true(scene.visible, "defeat screen must be shown even with the endpoint unreachable")
	assert_eq(scene.title_label.text, "DEFEAT", "defeat title rendered")
	# Score persisted locally the instant the screen appeared (before any async network work).
	assert_ne(scene.leaderboard_entry_uuid, "", "score must be saved locally at defeat")

# ---- 3: re-entrancy -- repeated game-over signals submit/save exactly once ---------------

func test_show_game_over_is_idempotent_across_repeat_calls():
	LeaderboardSync.enabled = false  # keep this test purely local + synchronous
	var scene = _make_screen()
	await get_tree().process_frame

	scene.show_game_over(false, _final_state())
	var uuid1: String = scene.leaderboard_entry_uuid
	assert_ne(uuid1, "", "first game-over saved a score")

	# Second signal (e.g. a leftover day-tick in a month playback) with DIFFERENT state.
	var s2 := _final_state()
	s2["turn"] = 99
	scene.show_game_over(false, s2)
	var uuid2: String = scene.leaderboard_entry_uuid

	assert_eq(uuid1, uuid2, "repeat game-over must NOT create a second score entry (re-entrancy guard)")

# ---- 4: durable outbox -------------------------------------------------------------------

func test_outbox_add_read_remove_roundtrip():
	assert_eq(LeaderboardSync._read_outbox().size(), 0, "outbox starts empty")
	LeaderboardSync._outbox_add({"entry_uuid": "abc", "score": 5})
	LeaderboardSync._outbox_add({"entry_uuid": "def", "score": 7})
	assert_eq(LeaderboardSync._read_outbox().size(), 2, "two distinct scores queued")

	# De-dup by entry_uuid: re-adding the same uuid must not grow the queue.
	LeaderboardSync._outbox_add({"entry_uuid": "abc", "score": 5})
	assert_eq(LeaderboardSync._read_outbox().size(), 2, "re-adding same uuid does not duplicate")

	LeaderboardSync._outbox_remove("abc")
	var remaining := LeaderboardSync._read_outbox()
	assert_eq(remaining.size(), 1, "ack removes exactly the acked score")
	assert_eq(str(remaining[0].get("entry_uuid", "")), "def", "the other score is retained for retry")

func test_outbox_read_degrades_on_missing_and_malformed_file():
	# Missing file -> empty queue, no throw.
	assert_eq(LeaderboardSync._read_outbox().size(), 0, "missing outbox reads as empty")
	# Malformed file -> empty queue, no throw.
	var f := FileAccess.open(LeaderboardSync.OUTBOX_PATH, FileAccess.WRITE)
	f.store_string("{ this is not valid json [[[")
	f.close()
	assert_eq(LeaderboardSync._read_outbox().size(), 0, "malformed outbox degrades to empty (never crashes)")

func test_submit_enqueues_to_outbox_before_dispatch():
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = UNREACHABLE
	LeaderboardSync.token = "regression-token"
	var entry := Leaderboard.ScoreEntry.new(42, "Contoso Safety Lab", 42, "v0.11.0", 1.0, 0, 100, 0)

	LeaderboardSync.submit_score(entry, "seed-x", "v0.11.0")
	# The body is persisted synchronously at dispatch time, before the async result -- so an
	# app-exit right now would still leave the score queued for retry next launch.
	var queued := LeaderboardSync._read_outbox()
	assert_eq(queued.size(), 1, "submit persists the score to the outbox before the POST resolves")
	assert_eq(str(queued[0].get("entry_uuid", "")), entry.entry_uuid, "queued body carries the entry uuid")
	assert_eq(str(queued[0].get("seed", "")), "seed-x", "queued body carries the seed (POST contract)")

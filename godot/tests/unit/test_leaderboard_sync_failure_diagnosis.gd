extends GutTest
## DEFECT 4 (2026-08-07): every remote failure reported the same wrong cause.
##
## `_dispatch_post` distinguished only `RESULT_SUCCESS && code == 200` from everything
## else and DISCARDED `code`, so the status line read "offline -- saved locally" for:
##   - HTTP 403, a rotated/invalid X-PDoom-Token   (network fine, auth broken)
##   - HTTP 404, the endpoint moved                (network fine, deploy broken)
##   - HTTP 500, the server threw                  (network fine, server broken)
##   - an actual timeout / DNS failure             (network genuinely down)
##
## This is a DIAGNOSABILITY defect, and it is the one that would have made the
## 2026-08-07 playtest hardest: if the token rotates, every player and every bug report
## says "offline" while the network is fine, and the true cause is unreachable from the
## field. `LeaderboardSync.submit_status_message` is where the collapse happened, so it
## is what these tests pin.
##
## The bar: two different server-side faults must not produce the same player-facing
## sentence, and none of them may claim the player is offline when the server answered.
##
## SCOPE: pure function, no HTTP, no user:// writes. It cannot prove the strings read
## well on screen -- only that the cause survives the trip to the player.

const OK_MSG_RANK := 1

func _msg_for(result: int, code: int) -> String:
	return LeaderboardSync.submit_status_message(false, 0, result, code)

# --- the success path must be untouched ---------------------------------------

func test_success_still_reads_as_before():
	assert_eq(LeaderboardSync.submit_status_message(true, OK_MSG_RANK, HTTPRequest.RESULT_SUCCESS, 200),
		"submitted (rank 1)", "the success wording is not part of this fix")
	assert_eq(LeaderboardSync.submit_status_message(true, 0, HTTPRequest.RESULT_SUCCESS, 200),
		"submitted", "rank 0 means the server did not report one")

# --- the defect --------------------------------------------------------------

func test_a_real_transport_failure_is_the_only_thing_called_offline():
	# The word "offline" must be reserved for the case where it is TRUE. When it is
	# applied to a 403 it actively misdirects whoever reads the bug report.
	var msg := _msg_for(HTTPRequest.RESULT_CANT_CONNECT, 0)
	assert_string_contains(msg.to_lower(), "offline",
		"a genuine can't-connect is the one case that IS offline")

func test_auth_failure_does_not_claim_the_player_is_offline():
	var msg := _msg_for(HTTPRequest.RESULT_SUCCESS, 403)
	assert_false(msg.to_lower().contains("offline"),
		"HTTP 403 means the server ANSWERED and rejected us -- calling that 'offline' " +
		"is how a rotated token becomes undiagnosable from the field")
	assert_string_contains(msg, "403",
		"the status code must survive to the player, or no bug report can carry it")

func test_missing_endpoint_does_not_claim_the_player_is_offline():
	var msg := _msg_for(HTTPRequest.RESULT_SUCCESS, 404)
	assert_false(msg.to_lower().contains("offline"),
		"HTTP 404 means the server answered -- the endpoint moved, the network did not")
	assert_string_contains(msg, "404", "the status code must reach the player")

func test_server_fault_does_not_claim_the_player_is_offline():
	var msg := _msg_for(HTTPRequest.RESULT_SUCCESS, 500)
	assert_false(msg.to_lower().contains("offline"),
		"HTTP 500 is the server's fault, not the player's connection")
	assert_string_contains(msg, "500", "the status code must reach the player")

func test_three_different_faults_are_three_different_sentences():
	# The collapse itself, stated as one assertion. Before the fix all three of these
	# were byte-identical.
	var forbidden := _msg_for(HTTPRequest.RESULT_SUCCESS, 403)
	var missing := _msg_for(HTTPRequest.RESULT_SUCCESS, 404)
	var broken := _msg_for(HTTPRequest.RESULT_SUCCESS, 500)
	var down := _msg_for(HTTPRequest.RESULT_CANT_CONNECT, 0)
	var seen := {}
	for m in [forbidden, missing, broken, down]:
		assert_false(seen.has(m),
			"two different causes produced the SAME message (%s) -- that is the defect" % m)
		seen[m] = true

func test_every_failure_still_reassures_the_score_is_kept():
	# Non-negotiable: whatever went wrong remotely, the local save already happened and
	# the outbox will retry. A player must never read a failure as "my run was lost".
	for pair in [[HTTPRequest.RESULT_SUCCESS, 403], [HTTPRequest.RESULT_SUCCESS, 404],
			[HTTPRequest.RESULT_SUCCESS, 500], [HTTPRequest.RESULT_CANT_CONNECT, 0],
			[HTTPRequest.RESULT_TIMEOUT, 0]]:
		var msg := _msg_for(pair[0], pair[1])
		assert_string_contains(msg.to_lower(), "saved",
			"failure message '%s' does not say the score was kept locally" % msg)

extends GutTest
## Tests for UpdateCheck (issue #799: anonymous install ping + remote update
## check). No real HTTP in tests: we exercise the pure static helpers (where
## the contract bugs hide -- the string-compare trap, v-prefix tolerance,
## malformed feeds) plus the response handler with stubbed transport results.

var CheckScript = load("res://autoload/update_check.gd")


# ---- parse_version: numeric triples, v-prefix, malformed -> [] ---------------

func test_parse_version_plain():
	assert_eq(CheckScript.parse_version("0.13.1"), [0, 13, 1])

func test_parse_version_v_prefix():
	assert_eq(CheckScript.parse_version("v0.13.1"), [0, 13, 1])
	assert_eq(CheckScript.parse_version("V0.13.1"), [0, 13, 1])

func test_parse_version_whitespace():
	assert_eq(CheckScript.parse_version("  v0.13.1  "), [0, 13, 1])

func test_parse_version_two_part_pads():
	assert_eq(CheckScript.parse_version("0.13"), [0, 13, 0])

func test_parse_version_malformed_rejected():
	assert_eq(CheckScript.parse_version(""), [])
	assert_eq(CheckScript.parse_version("abc"), [])
	assert_eq(CheckScript.parse_version("0.x.1"), [])
	assert_eq(CheckScript.parse_version("0..1"), [])
	assert_eq(CheckScript.parse_version("1.2.3.4"), [])
	assert_eq(CheckScript.parse_version("0.13.-1"), [])

func test_parse_version_ladder_epoch_strings_rejected():
	# Build-vs-ladder split: ladder epochs ("L1", bare "2") are NOT build
	# versions and must never trigger an update notice.
	assert_eq(CheckScript.parse_version("L1"), [])
	assert_eq(CheckScript.parse_version("2"), [])


# ---- is_remote_newer: NUMERIC compare (#799's whole point) -------------------

func test_string_compare_trap():
	# "0.9.0" > "0.11.0" as STRINGS -- the bug #799 explicitly warns about.
	# Numerically, 0.9.0 is OLDER and must not notice.
	assert_false(CheckScript.is_remote_newer("0.9.0", "0.11.0"))
	assert_true(CheckScript.is_remote_newer("0.11.0", "0.9.0"))

func test_newer_patch_minor_major():
	assert_true(CheckScript.is_remote_newer("0.13.2", "0.13.1"))
	assert_true(CheckScript.is_remote_newer("0.14.0", "0.13.9"))
	assert_true(CheckScript.is_remote_newer("1.0.0", "0.13.1"))

func test_equal_and_older_not_newer():
	assert_false(CheckScript.is_remote_newer("0.13.1", "0.13.1"))
	assert_false(CheckScript.is_remote_newer("0.13.0", "0.13.1"))

func test_v_prefix_tolerated_both_sides():
	assert_true(CheckScript.is_remote_newer("v0.13.2", "0.13.1"))
	assert_true(CheckScript.is_remote_newer("0.13.2", "v0.13.1"))
	assert_false(CheckScript.is_remote_newer("v0.13.1", "v0.13.1"))

func test_malformed_never_newer():
	# Fail closed: garbage on either side -> no notice, ever.
	assert_false(CheckScript.is_remote_newer("garbage", "0.13.1"))
	assert_false(CheckScript.is_remote_newer("0.13.2", "garbage"))
	assert_false(CheckScript.is_remote_newer("", ""))


# ---- parse_version_feed: the website's version.json shape --------------------

func test_parse_feed_happy_path():
	var body := '{"latest_release": {"version": "v0.12.0", "published_at": "2026-07-01"}}'
	assert_eq(CheckScript.parse_version_feed(body), "v0.12.0")

func test_parse_feed_malformed_shapes():
	assert_eq(CheckScript.parse_version_feed("not json at all"), "")
	assert_eq(CheckScript.parse_version_feed("[1,2,3]"), "")
	assert_eq(CheckScript.parse_version_feed('{"latest_release": "0.12.0"}'), "")
	assert_eq(CheckScript.parse_version_feed('{"latest_release": {}}'), "")
	assert_eq(CheckScript.parse_version_feed('{"latest_release": {"version": 12}}'), "")
	assert_eq(CheckScript.parse_version_feed(""), "")


# ---- should_show_notice: newer AND not dismissed (#799 "don't re-nag") -------

func test_notice_shows_for_newer_undismissed():
	assert_true(CheckScript.should_show_notice("0.13.2", "0.13.1", ""))

func test_notice_suppressed_when_dismissed_same_version():
	assert_false(CheckScript.should_show_notice("0.13.2", "0.13.1", "0.13.2"))
	# v-prefix on either side of the dismissal must still match.
	assert_false(CheckScript.should_show_notice("v0.13.2", "0.13.1", "0.13.2"))
	assert_false(CheckScript.should_show_notice("0.13.2", "0.13.1", "v0.13.2"))

func test_notice_returns_for_even_newer_release():
	# Dismissing 0.13.2 must NOT silence a later 0.13.3.
	assert_true(CheckScript.should_show_notice("0.13.3", "0.13.1", "0.13.2"))

func test_notice_never_for_older_or_equal():
	assert_false(CheckScript.should_show_notice("0.13.1", "0.13.1", ""))
	assert_false(CheckScript.should_show_notice("0.9.0", "0.13.1", ""))


# ---- build_ping_body: the privacy whitelist (#799 install_id rules) ----------

func test_ping_body_exact_contract():
	var body: Dictionary = CheckScript.build_ping_body("some-uuid", "0.13.1", "Windows", true)
	assert_eq(body["name"], "Game Launch")
	assert_eq(body["domain"], "pdoom1.com")
	assert_eq(body["url"], "app://pdoom1/launch")
	var props: Dictionary = body["props"]
	assert_eq(props["install_id"], "some-uuid")
	assert_eq(props["version"], "0.13.1")
	assert_eq(props["os"], "Windows")
	assert_eq(props["first_launch"], true)

func test_ping_body_carries_nothing_else():
	# PRIVACY REGRESSION GATE: the ping payload is a whitelist. If a new field
	# is ever added, this test forces the privacy conversation first.
	var body: Dictionary = CheckScript.build_ping_body("id", "v", "os", false)
	assert_eq(body.keys().size(), 4, "top-level keys are exactly name/domain/url/props")
	assert_eq((body["props"] as Dictionary).keys().size(), 4,
		"props are exactly install_id/version/os/first_launch -- no machine ids, no PII")

func test_user_agent_minimal():
	assert_eq(CheckScript.build_user_agent("0.13.1", "Windows"), "pdoom1/0.13.1 (Windows)")


# ---- install id: random UUIDv4 shape, never machine-derived ------------------

func test_generate_uuid_v4_shape_and_randomness():
	var a: String = CheckScript.generate_uuid_v4()
	var b: String = CheckScript.generate_uuid_v4()
	assert_true(CheckScript.looks_like_uuid(a), "generated id is a well-formed uuid: %s" % a)
	assert_eq(a[14], "4", "version nibble is 4 (random uuid, not name/machine-derived)")
	assert_true(a[19] in ["8", "9", "a", "b"], "variant nibble is RFC-4122")
	assert_ne(a, b, "two generations differ")

func test_looks_like_uuid_rejects_garbage():
	assert_false(CheckScript.looks_like_uuid(""))
	assert_false(CheckScript.looks_like_uuid("not-a-uuid"))
	assert_false(CheckScript.looks_like_uuid("zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz"))
	assert_true(CheckScript.looks_like_uuid("789d6739-b91d-4f54-800f-d65cf4380c5a"))


# ---- #939 patch-cadence sunset: self-retiring notice -------------------------

func test_patch_notice_active_before_sunset():
	assert_true(CheckScript.is_patch_notice_active("2026-07-26", "2026-08-04"))

func test_patch_notice_dead_on_and_after_sunset():
	assert_false(CheckScript.is_patch_notice_active("2026-08-04", "2026-08-04"))
	assert_false(CheckScript.is_patch_notice_active("2026-08-05", "2026-08-04"))
	assert_false(CheckScript.is_patch_notice_active("2027-01-01", "2026-08-04"))

func test_patch_notice_fails_closed_on_garbage_dates():
	assert_false(CheckScript.is_patch_notice_active("garbage", "2026-08-04"))
	assert_false(CheckScript.is_patch_notice_active("2026-07-26", "soon"))
	assert_false(CheckScript.is_patch_notice_active("", ""))


# ---- response handler with stubbed transport (no real HTTP) ------------------

func _make_checker():
	var checker = CheckScript.new()
	# GUT counts push_warning as an unexpected engine error. We are testing the
	# silent-no-op BEHAVIOUR of the failure paths, not the log channel, so tell
	# the instance its one-per-session warning is already spent (downgrades to
	# plain print).
	checker._warned = true
	autofree(checker)
	return checker

func _feed_body(version: String) -> String:
	return '{"latest_release": {"version": "%s"}}' % version

## A remote version guaranteed newer than the running build, derived from
## GameConfig.CURRENT_VERSION so the test never goes stale on version bumps.
func _newer_than_local() -> String:
	var local: Array = CheckScript.parse_version(GameConfig.CURRENT_VERSION)
	return "%d.%d.%d" % [local[0], local[1], local[2] + 1]

func test_handler_timeout_is_noop():
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_TIMEOUT, 0, "")
	assert_eq(checker.available_version, "", "timeout -> no notice state")
	assert_signal_not_emitted(checker, "update_available")

func test_handler_http_error_is_noop():
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_SUCCESS, 500, _feed_body(_newer_than_local()))
	assert_eq(checker.available_version, "")
	assert_signal_not_emitted(checker, "update_available")

func test_handler_malformed_body_is_noop():
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_SUCCESS, 200, "<html>DreamHost error page</html>")
	assert_eq(checker.available_version, "")
	assert_signal_not_emitted(checker, "update_available")

func test_handler_same_version_no_notice():
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_SUCCESS, 200, _feed_body("v" + GameConfig.CURRENT_VERSION))
	assert_eq(checker.available_version, "")
	assert_signal_not_emitted(checker, "update_available")

func test_handler_newer_version_notices():
	var newer := _newer_than_local()
	var prior_dismissed = GameConfig.dismissed_update_version
	GameConfig.dismissed_update_version = ""
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_SUCCESS, 200, _feed_body("v" + newer))
	assert_eq(checker.available_version, newer, "normalized (no v prefix) newer version cached")
	assert_signal_emitted_with_parameters(checker, "update_available", [newer])
	GameConfig.dismissed_update_version = prior_dismissed

func test_handler_respects_dismissal():
	var newer := _newer_than_local()
	var prior_dismissed = GameConfig.dismissed_update_version
	GameConfig.dismissed_update_version = newer
	var checker = _make_checker()
	watch_signals(checker)
	checker.handle_check_response(HTTPRequest.RESULT_SUCCESS, 200, _feed_body(newer))
	assert_eq(checker.available_version, "", "dismissed version does not re-nag")
	assert_signal_not_emitted(checker, "update_available")
	GameConfig.dismissed_update_version = prior_dismissed


# ---- ping privacy gate: TIER 2, decoupled from leaderboard identity consent --
# (docs/PRIVACY_POSTURE.md, ruled + approved by Pip 2026-07-26: the ping is
# identity-free, so ONLY its own toggle gates it.)

func test_ping_gate_default_on():
	var prior_ping = GameConfig.send_launch_ping
	GameConfig.send_launch_ping = true
	var checker = _make_checker()
	assert_true(checker.should_send_ping())
	GameConfig.send_launch_ping = prior_ping

func test_ping_gate_own_toggle_suppresses():
	var prior_ping = GameConfig.send_launch_ping
	var checker = _make_checker()
	GameConfig.send_launch_ping = false
	assert_false(checker.should_send_ping(), "ping toggle off -> no ping")
	GameConfig.send_launch_ping = prior_ping

func test_ping_fires_regardless_of_leaderboard_choice():
	# The decoupling ruling: leaderboard identity opt-out (or never-consented)
	# must NOT silence the anonymous ping, and vice versa.
	var prior_scores = GameConfig.submit_scores_global
	var prior_asked = GameConfig.leaderboard_consent_asked
	var prior_ping = GameConfig.send_launch_ping
	var checker = _make_checker()
	GameConfig.send_launch_ping = true
	GameConfig.submit_scores_global = false
	GameConfig.leaderboard_consent_asked = false
	assert_true(checker.should_send_ping(), "never-consented leaderboard state does not gate the ping")
	GameConfig.leaderboard_consent_asked = true
	assert_true(checker.should_send_ping(), "explicit leaderboard DECLINE does not gate the ping")
	GameConfig.submit_scores_global = prior_scores
	GameConfig.leaderboard_consent_asked = prior_asked
	GameConfig.send_launch_ping = prior_ping

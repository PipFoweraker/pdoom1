extends GutTest
## Client-side tests for LeaderboardSync (the PHP score API client).
## We can't exercise live HTTP in GUT, so we test the parts where the frozen-contract
## bugs actually hide: building the POST body / GET url, parsing responses, and the
## enabled/opt-out gating (the no-op path). See docs/strategy/BACKEND_AND_DATA_ARCHITECTURE.md.

var SyncScript = load("res://autoload/leaderboard_sync.gd")


func _make_entry() -> Leaderboard.ScoreEntry:
	# score, player_name, level, mode, duration, baseline, doom_integral, baseline_integral
	return Leaderboard.ScoreEntry.new(42, "Contoso Safety Lab", 42, "v0.11.0", 12.5, 30, 777, 100)


# ---- build_post_body: exactly a ScoreEntry dict + seed + version --------------

func test_build_post_body_matches_contract():
	var entry := _make_entry()
	var body: Dictionary = SyncScript.build_post_body(entry.to_dict(), "weekly-2026-w7", "v0.11.0")

	# The two contract-mandated extra fields.
	assert_has(body, "seed", "POST body must carry seed")
	assert_has(body, "version", "POST body must carry version (game_version)")
	assert_eq(body["seed"], "weekly-2026-w7")
	assert_eq(body["version"], "v0.11.0")

	# Every whitelisted ScoreEntry field must survive unchanged.
	for f in ["score", "doom_integral", "player_name", "date", "level_reached",
			"game_mode", "duration_seconds", "entry_uuid", "baseline_score",
			"baseline_doom_integral"]:
		assert_has(body, f, "POST body missing whitelisted field: %s" % f)
	assert_eq(body["score"], 42)
	assert_eq(body["doom_integral"], 777)
	assert_eq(body["player_name"], "Contoso Safety Lab")
	assert_eq(body["baseline_score"], 30)


func test_build_post_body_does_not_mutate_source():
	var entry := _make_entry()
	var src := entry.to_dict()
	SyncScript.build_post_body(src, "s", "v")
	assert_false(src.has("seed"), "build_post_body must not mutate the caller's dict")


# ---- endpoint + GET url -------------------------------------------------------

func test_build_endpoint_appends_score_api():
	assert_eq(SyncScript.build_endpoint("https://api.pdoom1.com"), "https://api.pdoom1.com/score_api.php")

func test_build_endpoint_strips_trailing_slashes():
	assert_eq(SyncScript.build_endpoint("https://api.pdoom1.com/"), "https://api.pdoom1.com/score_api.php")
	assert_eq(SyncScript.build_endpoint("https://api.pdoom1.com///"), "https://api.pdoom1.com/score_api.php")

func test_build_get_url_encodes_and_limits():
	var url: String = SyncScript.build_get_url("https://api.pdoom1.com", "weekly 2026/w7", "v0.11.0", 20)
	assert_true(url.begins_with("https://api.pdoom1.com/score_api.php?"), "GET hits the endpoint")
	assert_true(url.contains("limit=20"), "GET carries limit")
	assert_true(url.contains("version=v0.11.0"), "GET carries version")
	# space and slash must be percent-encoded, not raw.
	assert_false(url.contains("weekly 2026/w7"), "seed must be uri-encoded")
	assert_true(url.contains("seed=weekly"), "encoded seed present")

func test_build_get_url_min_limit_is_one():
	var url: String = SyncScript.build_get_url("https://x", "s", "v", 0)
	assert_true(url.contains("limit=1"), "limit floored to 1")


# ---- parse_submit_response ----------------------------------------------------

func test_parse_submit_response_ok():
	var r: Dictionary = SyncScript.parse_submit_response('{"ok":true,"added":true,"rank":3}')
	assert_true(r["ok"])
	assert_true(r["added"])
	assert_eq(r["rank"], 3)

func test_parse_submit_response_duplicate():
	var r: Dictionary = SyncScript.parse_submit_response('{"ok":true,"added":false,"duplicate":true,"rank":5}')
	assert_true(r["ok"])
	assert_false(r["added"])
	assert_true(r["duplicate"])
	assert_eq(r["rank"], 5)

func test_parse_submit_response_error_body():
	var r: Dictionary = SyncScript.parse_submit_response('{"ok":false,"error":"bad token"}')
	assert_false(r["ok"])
	assert_eq(r["rank"], 0)

func test_parse_submit_response_malformed_never_crashes():
	for junk in ["", "not json", "[]", "null", "{"]:
		var r: Dictionary = SyncScript.parse_submit_response(junk)
		assert_false(r["ok"], "malformed submit body %s -> ok=false" % junk)


# ---- parse_board_entries ------------------------------------------------------

func test_parse_board_entries_ok():
	var payload := '{"ok":true,"seed":"s","version":"v0.11.0","entries":[' + \
		'{"score":99,"doom_integral":10,"player_name":"Alpha","baseline_score":40,"duration_seconds":8.0,"date":"2026-07-17T10:00:00","entry_uuid":"u1"},' + \
		'{"score":88,"doom_integral":5,"player_name":"Beta","entry_uuid":"u2"}]}'
	var r: Dictionary = SyncScript.parse_board_entries(payload)
	assert_true(r["ok"])
	var entries: Array = r["entries"]
	assert_eq(entries.size(), 2, "both entries parsed")
	# ScoreEntry-shaped: property access is what leaderboard_screen relies on.
	assert_eq(entries[0].score, 99)
	assert_eq(entries[0].player_name, "Alpha")
	assert_eq(entries[0].baseline_score, 40)
	assert_eq(entries[0].entry_uuid, "u1")
	assert_eq(entries[1].score, 88)

func test_parse_board_entries_error_ok_false():
	var r: Dictionary = SyncScript.parse_board_entries('{"ok":false,"error":"whatever"}')
	assert_false(r["ok"])
	assert_eq((r["entries"] as Array).size(), 0)

func test_parse_board_entries_malformed_never_crashes():
	for junk in ["", "garbage", "{}", '{"ok":true}', '{"ok":true,"entries":"nope"}']:
		var r: Dictionary = SyncScript.parse_board_entries(junk)
		assert_eq((r["entries"] as Array).size(), 0, "malformed board %s -> no entries" % junk)


# ---- gating: enabled=false is a no-op; opt-out respected ----------------------

func _make_sync():
	# NOT added to the tree -> _ready/HTTP never run; we drive the state directly.
	var s = SyncScript.new()
	return s

func test_disabled_never_submits():
	var s = _make_sync()
	s.enabled = false
	s.base_url = "https://api.pdoom1.com"
	s.token = "realtoken"
	assert_false(s.should_submit(), "enabled=false must be a hard no-op")
	assert_false(s.can_fetch(), "enabled=false must not fetch either")

func test_unconfigured_never_submits():
	var s = _make_sync()
	s.enabled = true
	s.base_url = ""
	s.token = ""
	assert_false(s.is_configured(), "empty url/token is unconfigured")
	assert_false(s.should_submit())
	assert_false(s.can_fetch())

func test_enabled_configured_optin_submits():
	var prev = GameConfig.submit_scores_global
	GameConfig.submit_scores_global = true
	var s = _make_sync()
	s.enabled = true
	s.base_url = "https://api.pdoom1.com"
	s.token = "realtoken"
	assert_true(s.is_configured())
	assert_true(s.can_fetch(), "enabled+configured can fetch the global board")
	assert_true(s.should_submit(), "enabled+configured+opted-in submits")
	GameConfig.submit_scores_global = prev

func test_opt_out_blocks_submit_but_not_fetch():
	var prev = GameConfig.submit_scores_global
	GameConfig.submit_scores_global = false
	var s = _make_sync()
	s.enabled = true
	s.base_url = "https://api.pdoom1.com"
	s.token = "realtoken"
	assert_false(s.should_submit(), "opt-out must block uploads")
	assert_true(s.can_fetch(), "opt-out still lets you VIEW the global board")
	GameConfig.submit_scores_global = prev

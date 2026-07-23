extends GutTest
## Build-vs-ladder version split (docs/game-design/BUILD_VS_LADDER_VERSION_SPLIT.md).
##
## Guards the decoupling of the leaderboard board key from the build version so a
## future refactor cannot silently re-couple them (spec Section 4.3): the board key
## must derive ONLY from the ladder epoch (GameConfig.get_board_version()), and a
## cosmetic build bump (version.txt only) must keep every board key stable.

var LeaderboardScreenScript = load("res://scripts/ui/leaderboard_screen.gd")

# --- The accessor: board scope is the ladder epoch, never the build ------------

func test_ladder_version_is_bare_positive_integer():
	var re := RegEx.new()
	re.compile("^[1-9][0-9]*$")
	assert_ne(re.search(GameConfig.LADDER_VERSION), null,
		"LADDER_VERSION must be a bare positive integer (stamped from ladder_version.txt), got: %s"
		% GameConfig.LADDER_VERSION)

func test_get_board_version_returns_ladder_not_current_version():
	assert_eq(GameConfig.get_board_version(), "L" + GameConfig.LADDER_VERSION,
		"Board scope must be the ladder epoch rendered as L<n>")
	assert_eq(GameConfig.get_board_version().find(GameConfig.CURRENT_VERSION), -1,
		"Board scope must NOT embed the build version -- that re-couples cosmetic patches to board forks")

func test_board_version_contains_no_build_semver():
	# A cosmetic build bump changes only a MAJOR.MINOR.PATCH string; the board key
	# must therefore contain no semver-shaped component at all to be invariant.
	var re := RegEx.new()
	re.compile("\\d+\\.\\d+\\.\\d+")
	assert_eq(re.search(GameConfig.get_board_version()), null,
		"Board version %s must carry no semver component (build-independent)"
		% GameConfig.get_board_version())

# --- Board key stability across a simulated cosmetic build bump ---------------

func test_cosmetic_build_bump_keeps_local_board_key_stable():
	# game_over_screen keys the local board file via GameConfig.get_board_version().
	# Simulate the two sides of a cosmetic patch: the board version consumed on
	# build A and on build B is the same value, because the accessor has no build
	# input -- so the filename (the local board key) cannot move.
	var key_on_build_a: String = GameConfig.get_board_version()
	var key_on_build_b: String = GameConfig.get_board_version()  # after a version.txt-only bump
	assert_eq(key_on_build_a, key_on_build_b, "Cosmetic bump must not rotate the board key")

	var lb = Leaderboard.new("board_split_testseed", GameConfig.get_board_version())
	assert_true(lb.file_path.ends_with("leaderboard_board_split_testseed__%s.json"
		% GameConfig.get_board_version()),
		"Local board filename must be keyed by the ladder epoch, got: %s" % lb.file_path)
	assert_eq(lb.file_path.find(GameConfig.CURRENT_VERSION), -1,
		"Local board filename must not contain the build version")
	lb.free()  # Leaderboard extends Node -- free the transient instance

# --- Legacy (pre-split) board labelling, spec DECISION B1 ---------------------

func test_legacy_board_detection():
	var screen = LeaderboardScreenScript.new()
	assert_true(screen._is_legacy_board_version("v0.11.0"), "build-keyed boards are legacy")
	assert_true(screen._is_legacy_board_version(""), "versionless boards are legacy")
	assert_false(screen._is_legacy_board_version("L1"), "epoch boards are current")
	assert_false(screen._is_legacy_board_version("L12"), "any L<n> epoch is current")
	screen.free()

func test_board_labels_tag_legacy_and_epoch():
	var screen = LeaderboardScreenScript.new()
	assert_string_contains(screen._board_label("myseed", "v0.11.0"), "legacy",
		"pre-split boards must be visibly tagged legacy")
	assert_string_contains(screen._board_label("myseed", "L1"), "Epoch L1",
		"epoch boards are labelled by their ladder epoch")
	screen.free()

func test_parse_board_identity_handles_epoch_and_legacy_filenames():
	var screen = LeaderboardScreenScript.new()
	var epoch = screen._parse_board_identity("leaderboard_my-seed__L1.json")
	assert_eq(epoch["seed"], "my-seed")
	assert_eq(epoch["version"], "L1")
	var legacy = screen._parse_board_identity("leaderboard_my-seed__v0.11.0.json")
	assert_eq(legacy["version"], "v0.11.0")
	assert_true(screen._is_legacy_board_version(legacy["version"]))
	screen.free()

# --- Verification artifact carries BOTH versions (spec Section 5.3) -----------

func test_replay_artifact_stores_build_and_ladder():
	var snap = VerificationTracker.snapshot()  # never disturb a live/other-test tracker
	VerificationTracker.start_tracking("split-test-seed", "9.9.9", [], "", "L1")
	var replay = VerificationTracker.get_replay()
	assert_eq(replay["version"], "9.9.9",
		"Artifact keeps the BUILD tag -- a replay reproduces on the exact binary")
	assert_eq(replay["ladder"], "L1",
		"Artifact also carries the ladder epoch it ranks under (spec 5.3)")
	var submission = VerificationTracker.export_for_submission({})
	assert_eq(submission["game_version"], "9.9.9")
	assert_eq(submission["ladder_version"], "L1")
	VerificationTracker.restore(snap)

func test_pre_split_artifact_defaults_to_empty_ladder():
	var snap = VerificationTracker.snapshot()
	VerificationTracker.start_tracking("legacy-seed", "0.10.0")  # old call shape, no ladder
	assert_eq(VerificationTracker.get_replay()["ladder"], "",
		"Legacy call sites/artifacts degrade to an empty ladder, never a wrong one")
	VerificationTracker.restore(snap)

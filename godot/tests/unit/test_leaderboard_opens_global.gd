extends GutTest
## Pip's v0.14.0 playtest, 2026-08-07: "the leaderboard is invisible."
##
## Two defects in this one screen, both of which end with a player concluding there is
## no global board:
##
## DEFECT 2 -- the screen opened on the LOCAL view and fetched the global board only if
## the player found and pressed a toggle. A player who opens the board sees their own
## handful of scores, and the honest reading of that evidence is "there is no global
## board". This is the one Pip actually hit.
##
## DEFECT 6 (found while fixing 2) -- the global fetch keyed on GameConfig, while the
## LOCAL view keys on the board file being viewed. Those are two different sources for
## one board key and they CAN diverge: GameConfig.game_seed is mutated outside any run
## (welcome_screen.gd:175 clears it on Launch Lab, pregame_setup.gd:160/217 sets it),
## and the seed dropdown changes the local view without GameConfig hearing about it.
## So a player could pick seed A in the dropdown, press Global, and be shown seed B's
## board with the subtitle naming B -- a different board from the one they scored on.
##
## MUST NOT REGRESS #1126/#1127: a FAILED fetch keeps the toggle pressed, says so in
## amber, and offers Retry (test_leaderboard_global_failure_visible.gd pins that).
## Defaulting the view to Global makes that failure path the FIRST thing a networkless
## player sees, so it has to stay intact -- these tests assert the default-on path
## reuses it rather than inventing a second, quieter one.

const SCREEN := preload("res://scenes/leaderboard_screen.tscn")

# A seed that is deliberately NOT whatever GameConfig would report, so a fetch that
# silently falls back to GameConfig is caught by name rather than by coincidence.
const OTHER_SEED := "divergence-probe-seed"
const EPOCH := "L4"

var _saved_enabled: bool
var _saved_base_url: String
var _saved_token: String
var _saved_game_seed: String
var _made_board_path := ""

func before_each():
	_saved_enabled = LeaderboardSync.enabled
	_saved_base_url = LeaderboardSync.base_url
	_saved_token = LeaderboardSync.token
	_saved_game_seed = GameConfig.game_seed
	LeaderboardSync.enabled = true
	# Port 9 (discard) refuses immediately: no test ever waits on a real network, and
	# no request ever leaves the machine. The screen's subtitle is written SYNCHRONOUSLY
	# before dispatch, which is what these tests read.
	LeaderboardSync.base_url = "http://127.0.0.1:9"
	LeaderboardSync.token = "test-token-not-a-real-secret"

func after_each():
	LeaderboardSync.enabled = _saved_enabled
	LeaderboardSync.base_url = _saved_base_url
	LeaderboardSync.token = _saved_token
	GameConfig.game_seed = _saved_game_seed
	# Leave no board files behind (see test_userdata_isolation.gd -- littering user://
	# is how the developer's real league board got wiped).
	if _made_board_path != "":
		DirAccess.remove_absolute(ProjectSettings.globalize_path(_made_board_path))
		_made_board_path = ""

func _make_local_board(board_seed: String) -> String:
	"""Create one real local board file so the screen can discover and select it."""
	var lb = Leaderboard.new(board_seed, EPOCH)
	lb.add_score(Leaderboard.ScoreEntry.new(42, "Probe Lab", 42, "vtest", 1.0))
	_made_board_path = lb.file_path
	lb.free()
	return "%s (%s)" % [board_seed, EPOCH]

func _make_screen():
	var screen = SCREEN.instantiate()
	add_child_autofree(screen)  # runs _ready
	return screen

# --- DEFECT 2 -----------------------------------------------------------------

func test_screen_opens_on_the_global_board_not_local():
	# The whole defect in one assertion: opening the screen with sync configured must
	# already be asking for the global board. Before the fix showing_global was false
	# until a human pressed the toggle.
	var screen = _make_screen()
	assert_not_null(screen.global_toggle_button,
		"precondition: the toggle exists whenever remote sync is configured")
	assert_true(screen.showing_global,
		"the board must OPEN on global -- a player who sees only their own scores " +
		"concludes there is no global board, which is exactly what Pip concluded")
	assert_true(screen.global_toggle_button.button_pressed,
		"the toggle must reflect the view it is actually in, or it lies about state")
	assert_eq(screen.global_toggle_button.text, "View: Global",
		"the toggle label must match the defaulted-on view")

func test_unconfigured_build_still_opens_local_and_builds_no_toggle():
	# Boundary: forks / dev builds with no leaderboard config must be untouched by this.
	# Defaulting to a view that cannot exist would be a worse bug than the one fixed.
	LeaderboardSync.enabled = false
	var screen = _make_screen()
	assert_null(screen.global_toggle_button,
		"no toggle when sync is unconfigured -- the screen stays local-only")
	assert_false(screen.showing_global,
		"an unconfigured build must not claim to be showing a global board")

func test_default_on_global_still_reports_a_failed_fetch_visibly():
	# #1126/#1127 must survive the default flipping. The failure path is now the FIRST
	# thing an offline player sees, so it matters more than it did.
	var screen = _make_screen()
	screen._on_global_board_fetched(false, [])
	assert_true(screen.global_status_row.visible,
		"a failed fetch on the DEFAULT global view must still be reported in words")
	assert_true(screen.global_toggle_button.button_pressed,
		"the toggle must not un-press itself on failure -- that is the #1127 regression")

# --- DEFECT 6: one board key, one source --------------------------------------

func test_global_fetch_keys_on_the_board_being_viewed_not_on_gameconfig():
	# Construct the divergence directly: the screen is viewing OTHER_SEED's board while
	# GameConfig says something else entirely. Before the fix the fetch (and the
	# subtitle it writes) named GameConfig's seed -- a different board from the one
	# whose rows were on screen a moment earlier.
	var key := _make_local_board(OTHER_SEED)
	GameConfig.game_seed = "gameconfig-says-something-else"
	assert_ne(GameConfig.get_display_seed(), OTHER_SEED,
		"precondition: the two candidate sources genuinely disagree")

	var screen = _make_screen()
	screen._discover_boards()
	assert_true(screen._board_files.has(key), "precondition: the probe board was discovered")
	screen.current_seed = key
	screen._fetch_and_show_global()

	assert_string_contains(screen.subtitle.text, OTHER_SEED,
		"the global fetch must key on the board the player is LOOKING AT (%s), " % OTHER_SEED +
		"not on GameConfig.get_display_seed() (%s) -- two sources for one board key" % GameConfig.get_display_seed())
	assert_false(screen.subtitle.text.contains("gameconfig-says-something-else"),
		"the subtitle must not name a board the player never selected")

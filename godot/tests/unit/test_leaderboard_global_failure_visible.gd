extends GutTest
## #1126 regression: a FAILED global-board fetch must be visible to the player.
##
## The bug the first external player hit: on any fetch failure the Local/Global toggle
## reset its own pressed state and its own label, then redrew the local board. Pressing
## "View: Global" therefore produced no observable change whatsoever, and the player
## concluded the button was broken. A failed request and a dead button looked identical.
##
## The bar these tests pin (straight from the issue): after the fix, a player who taps
## Global with no network must be able to tell a failed request from a broken button.
## Concretely, on failure the screen must (a) keep the toggle pressed, (b) say in words
## that the global board could not be reached, and (c) offer a retry.
##
## NOTE ON WHAT THIS CANNOT PROVE: no test here shows the message READS well, is legible
## against the records-room background, or lands in the right place on screen. That needs
## Pip on a real build. These tests only prove the state is reported at all rather than
## erased -- which is exactly what was missing.

const SCREEN := preload("res://scenes/leaderboard_screen.tscn")

var _saved_enabled: bool
var _saved_base_url: String
var _saved_token: String

func before_each():
	# The toggle (and therefore the status row) is only built when remote sync is
	# configured. Force that on so the test does not depend on the shipped config, then
	# restore -- LeaderboardSync is an autoload shared with every other suite.
	_saved_enabled = LeaderboardSync.enabled
	_saved_base_url = LeaderboardSync.base_url
	_saved_token = LeaderboardSync.token
	LeaderboardSync.enabled = true
	LeaderboardSync.base_url = "https://example.invalid"
	LeaderboardSync.token = "test-token-not-a-real-secret"

func after_each():
	LeaderboardSync.enabled = _saved_enabled
	LeaderboardSync.base_url = _saved_base_url
	LeaderboardSync.token = _saved_token

func _make_screen():
	var screen = SCREEN.instantiate()
	add_child_autofree(screen)  # runs _ready -> _setup_global_toggle + status row
	return screen

## Drive the exact callback LeaderboardSync invokes on a timeout / 502 / DNS failure.
## No HTTP is performed: fetch_board's contract is callback(false, []) on ANY failure,
## so this is the real failure path, not a simulation of a different one.
func _screen_in_failed_global_state():
	var screen = _make_screen()
	assert_not_null(screen.global_toggle_button,
		"precondition: the Local/Global toggle must exist when sync is configured")
	screen.showing_global = true
	screen.global_toggle_button.set_pressed_no_signal(true)
	screen.global_toggle_button.text = "View: Global"
	screen._on_global_board_fetched(false, [])
	return screen

# --- The bar from the issue ---------------------------------------------------

func test_failed_fetch_says_something_the_player_can_read():
	var screen = _screen_in_failed_global_state()
	assert_not_null(screen.global_status_label,
		"a failed fetch must have somewhere to report itself")
	assert_true(screen.global_status_row.visible,
		"the status row must be VISIBLE after a failed fetch -- an invisible notice is the bug")
	assert_ne(screen.global_status_label.text, "",
		"a failed fetch must leave a non-empty message; silence is indistinguishable from a dead button")
	assert_string_contains(screen.global_status_label.text, "Global board unavailable",
		"the message must name what failed, not merely be non-empty")

func test_failed_fetch_does_not_un_press_the_toggle():
	# This is the precise regression. The old code called set_pressed_no_signal(false)
	# and reset the label to "View: Local", erasing every trace of the player's input.
	var screen = _screen_in_failed_global_state()
	assert_true(screen.global_toggle_button.button_pressed,
		"the toggle must STAY pressed on failure -- self-un-pressing is what made it look broken")
	assert_eq(screen.global_toggle_button.text, "View: Global",
		"the toggle label must not silently revert to 'View: Local' on a failed fetch")

func test_failed_fetch_offers_a_retry():
	var screen = _screen_in_failed_global_state()
	assert_not_null(screen.global_retry_button, "a failed fetch must offer a retry affordance")
	assert_true(screen.global_retry_button.visible, "the Retry button must be visible after a failure")

func test_failed_fetch_still_shows_local_entries_underneath():
	# The fallback itself was never the problem -- showing local is correct. It just has
	# to be labelled. Assert the screen is not left blank.
	var screen = _screen_in_failed_global_state()
	assert_ne(screen.subtitle.text, "", "the board underneath must still be identified")

# --- The notice must not become permanent chrome ------------------------------

func test_successful_fetch_clears_the_notice():
	var screen = _screen_in_failed_global_state()
	assert_true(screen.global_status_row.visible, "precondition: notice is up after the failure")
	screen.showing_global = true
	screen._on_global_board_fetched(true, [])
	assert_false(screen.global_status_row.visible,
		"a later SUCCESSFUL fetch must clear the failure notice")

func test_returning_to_local_clears_the_notice():
	var screen = _screen_in_failed_global_state()
	screen._filter_and_display()  # the deliberate 'go back to Local' path
	assert_false(screen.global_status_row.visible,
		"choosing Local deliberately must clear the global failure notice")
	assert_false(screen.global_toggle_button.button_pressed,
		"the DELIBERATE local path still un-presses the toggle (only the failure path must not)")

# --- Second silent conflation found in the same file --------------------------

func test_empty_global_board_does_not_read_as_an_empty_local_board():
	# A successful fetch returning zero entries used to render the LOCAL empty state
	# ("Play a game to see your scores here!"), so "nobody has posted yet" and "you have
	# not played yet" looked the same -- and both looked like the toggle did nothing.
	var screen = _make_screen()
	screen.showing_global = true
	screen._on_global_board_fetched(true, [])
	var texts: Array = []
	for child in screen.entries_container.get_children():
		if child is Label:
			texts.append(child.text)
	assert_gt(texts.size(), 0, "an empty board must render an empty-state label")
	assert_string_contains(texts[0], "global board",
		"the empty GLOBAL board must name itself, not reuse the local empty state")

func test_failed_fetch_empty_state_still_reads_as_local():
	# Inverse guard: on a FAILED fetch the rows underneath are the LOCAL board, so if
	# they are empty the empty-state must NOT claim the global board is empty.
	var screen = _screen_in_failed_global_state()
	for child in screen.entries_container.get_children():
		if child is Label and child.text.contains("global board is empty"):
			fail_test("a failed fetch must not claim the GLOBAL board is empty -- those rows are local")
	pass_test("failed fetch does not mislabel the local fallback as an empty global board")

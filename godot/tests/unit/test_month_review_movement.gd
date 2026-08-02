extends GutTest
## A1/A4 (recorded playtest 2026-08-01, [3:45]) -- the month review shows CHANGE, not STATE.
##
## The failure Pip named: "funds is good, but I CAN SEE THAT UP HERE, so this is NOT FRESH
## INFORMATION." The review printed `Funds: $84,200 | Doom: 31.2% | Staff: 3` -- three numbers
## the top bar, the doom meter and the roster already show, every month, unchanged in meaning.
##
## The replacement is start -> end movement, and ONLY for stats that moved: an unchanged stat
## is exactly the non-fresh information A1 deleted, so printing "Funds unchanged" would
## re-open the complaint in different words.
##
## Doom is band movement only (ADR-0015: doom is computed from world state, so a printed
## per-source number would misrepresent how it works; per-cause attribution stays behind the
## paid doom-breakdown instrument, ADR-0001). These tests pin that no doom PERCENTAGE ever
## reaches this string.

const GameManagerScript := preload("res://scripts/game_manager.gd")


func _gm() -> Node:
	var gm: Node = GameManagerScript.new()
	autofree(gm)
	return gm


func _stats(money: float, doom: float, staff: int) -> Dictionary:
	return {"money": money, "doom": doom, "staff": staff}


# --- no baseline -> no block ------------------------------------------------------------

func test_no_baseline_yields_no_movement_block() -> void:
	# Month 1 of a run, and any run resumed from a save (the baseline is display-only and is
	# deliberately not serialized). Degrade to silence rather than print a delta measured
	# against a month the player did not play.
	assert_eq(_gm()._build_month_movement_section({}, _stats(100.0, 10.0, 2)), "")
	assert_eq(_gm()._build_month_movement_section(_stats(100.0, 10.0, 2), {}), "")


func test_a_month_where_nothing_moved_prints_nothing() -> void:
	var same := _stats(84200.0, 31.2, 3)
	assert_eq(_gm()._build_month_movement_section(same, same.duplicate()), "",
		"an unchanged stat is precisely the non-fresh information A1 deleted")


# --- funds ------------------------------------------------------------------------------

func test_funds_render_as_start_to_end_with_a_signed_delta() -> void:
	var out: String = _gm()._build_month_movement_section(
		_stats(102000.0, 10.0, 3), _stats(84200.0, 10.0, 3))
	assert_string_contains(out, "Funds")
	assert_string_contains(out, "->", "movement is a start -> end statement, not a level")
	assert_string_contains(out, "(-", "a month that lost money must read as a LOSS")


func test_funds_gain_is_signed_positive() -> void:
	var out: String = _gm()._build_month_movement_section(
		_stats(10000.0, 10.0, 3), _stats(25000.0, 10.0, 3))
	assert_string_contains(out, "(+")


func test_unchanged_funds_are_omitted_while_another_stat_moved() -> void:
	var out: String = _gm()._build_month_movement_section(
		_stats(50000.0, 10.0, 3), _stats(50000.0, 10.0, 5))
	assert_false(out.contains("Funds"), "only stats that MOVED earn a line")
	assert_string_contains(out, "Staff")


# --- staff ------------------------------------------------------------------------------

func test_staff_growth_and_loss_are_signed() -> void:
	var grew: String = _gm()._build_month_movement_section(
		_stats(1.0, 10.0, 3), _stats(1.0, 10.0, 4))
	assert_string_contains(grew, "(+1)")
	var shrank: String = _gm()._build_month_movement_section(
		_stats(1.0, 10.0, 4), _stats(1.0, 10.0, 2))
	assert_string_contains(shrank, "(-2)")


# --- doom: bands only, never numbers ------------------------------------------------------

func test_doom_inside_one_band_prints_nothing() -> void:
	var low := 1.0
	var slightly_higher := 2.0
	assert_eq(ThemeManager.get_doom_band_index(low), ThemeManager.get_doom_band_index(slightly_higher),
		"test precondition: these two doom values must share a band")
	assert_eq(_gm()._doom_band_movement(low, slightly_higher), "",
		"drift within a band is already on the doom meter -- not fresh information")


func test_doom_band_crossing_is_reported_with_direction() -> void:
	assert_true(ThemeManager.get_doom_band_index(5.0) < ThemeManager.get_doom_band_index(95.0),
		"test precondition: 5%% and 95%% doom must be different bands")
	var up: String = _gm()._doom_band_movement(5.0, 95.0)
	assert_string_contains(up, "crossed up")
	assert_string_contains(up, ThemeManager.get_doom_status_label(95.0))
	var down: String = _gm()._doom_band_movement(95.0, 5.0)
	assert_string_contains(down, "eased down")


func test_doom_movement_never_prints_a_percentage() -> void:
	# ADR-0015 guard. A regression that reintroduced a raw number here would look harmless
	# and would quietly re-assert the retired "single source-destination number bump" model.
	for pair in [[5.0, 95.0], [95.0, 5.0], [31.2, 62.7]]:
		var out: String = _gm()._doom_band_movement(float(pair[0]), float(pair[1]))
		assert_false(out.contains("%"), "no doom percentage may reach the review: got '%s'" % out)


func test_movement_block_never_prints_a_doom_percentage() -> void:
	var out: String = _gm()._build_month_movement_section(
		_stats(102000.0, 5.0, 3), _stats(84200.0, 95.0, 4))
	assert_false(out.contains("%"), "got '%s'" % out)


# --- A1: the deleted level line stays deleted ---------------------------------------------

func test_the_old_state_level_line_is_gone_from_the_source() -> void:
	# Source scan, same idiom as test_action_bar_renderer: the point of A1 is that this exact
	# construction never comes back. A behavioural assertion cannot see it, because the string
	# is only assembled inside a live month boundary.
	var src: String = FileAccess.get_file_as_string("res://scripts/game_manager.gd")
	assert_false(src.contains("Funds: %s   |   Doom:"),
		"the HUD owns funds/doom/staff levels -- the review owns what CHANGED ([3:45])")

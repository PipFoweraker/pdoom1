extends GutTest
## Pip, playing v0.14.0 on league night (2026-08-07):
##
##   "the game-over screen is really hard to read and still involves scrolling and old
##    colour schemes. can you make it bigger so I don't have to scroll?"
##
## THE MEASUREMENT THAT PROVOKED THIS, at 1920x1080 on tag 7368e237:
##   StatsLabel box    720 x 300, scroll_active=true, scroll value=0
##   content_height    713  ->  413px unreachable
##   lines             31 total, 14 visible
##   line 31 of 31     "> Press ENTER for Leaderboard"
##
## Less than half the screen was readable, and the line naming the ONLY advertised
## route to the leaderboard was the last one -- 413px below the bottom of its own box.
## That is why he never found the board. The keyboard shortcut had worked all along.
##
## THE CALL: content was cut FIRST and the box grew SECOND. A death screen is a
## moment, not a document. The ledger rows (seven lines to carry five numbers; four
## more to carry three) became one line each, the redundant "FINAL STATISTICS" header
## went, and the navigation left the document entirely to become a real button. Only
## then was the panel sized to what remained at a 20px body. Growing the box alone
## would have needed roughly 780px of stats to show 31 lines at a legible size, which
## does not fit a 1080-unit viewport with a title, a cause of death and a button row.
##
## WHY THE GUARD IS TWO-SIDED. #1155 recorded that this file's ancestors shipped three
## assertions that could not fail (`child.size <= panel.size`, `minimum <= panel.size`,
## and the one-sided `needed <= authored`). One-sided fit guards get EASIER every time
## the panel grows, so a guard that only says "it fits" would bless any amount of
## padding -- and padding is exactly what Pip did not ask for. So: the panel must fit
## its contents AND not exceed them by more than SLACK_BUDGET_PX.
##
## WHY THE SLACK BUDGET IS 80 AND NOT 40 (#1155 used 40): the measured slack is 40px,
## but the strings on THIS screen vary with how the player died. `_get_defeat_reason`
## and the ledger-attribution line are prose whose wrapped height changes per death
## cause, and the fixture below can only instantiate one cause at a time. 80px is
## ~2.5 lines at 28px -- room for a longer death than the fixture's, and still less
## than a tenth of the panel. It is a budget, not a measurement, and it is stated as
## such.
##
## WHAT THESE TESTS CANNOT PROVE: that 20px reads as comfortable on Pip's display, or
## that the new palette looks right against the panel art. They prove the scrolling is
## gone, the room went into text rather than padding, and the three colours that
## failed WCAG AA are gone. Whether it FEELS better needs Pip on a real build.

const SCENE_PATH := "res://scenes/ui/game_over_screen.tscn"

## The panel may exceed its contents by at most this much. See the header.
const SLACK_BUDGET_PX := 80.0

## WCAG AA for normal-size body text. Not aspirational -- [color=blue] measured 2.23:1
## on this panel and was used for a resource the player is meant to read.
const MIN_CONTRAST := 4.5

## Godot's rendered ground for this panel: game_over_screen.gd:_ready() sets
## bg_color = Color(0.09, 0.04, 0.11, 0.98) over a near-black overlay.
const PANEL_GROUND := Color(0.09, 0.04, 0.11)

var _prev_scenario: String

func before_each():
	_prev_scenario = GameConfig.scenario_id
	GameConfig.scenario_id = ""

func after_each():
	GameConfig.scenario_id = _prev_scenario

## Worst case for HEIGHT, deliberately: a full staff roster (the longest team row),
## upgrades purchased, non-zero momentum (widens the doom row), a baseline to compare
## against, and a ledger death so the attribution line renders. A thin fixture would
## flatter the geometry, which is how the earlier tautologies got written.
func _defeat_state() -> Dictionary:
	return {
		"game_over": true, "victory": false, "turn": 147, "doom": 100.0,
		"doom_momentum": 2.4,
		"reputation": 12, "money": 197208, "compute": 82.0, "research": 44.0,
		"papers": 7,
		"safety_researchers": 3, "capability_researchers": 2, "compute_engineers": 1,
		"purchased_upgrades": ["a", "b", "c"],
		"ledger": {"death_attribution": [
			{"source": "salary debt", "magnitude": 42000.0},
			{"source": "compute debt", "magnitude": 18000.0},
		]},
	}

func _screen() -> Control:
	var s: Control = (load(SCENE_PATH) as PackedScene).instantiate()
	add_child_autofree(s)
	s.show_game_over(false, _defeat_state())
	# The #1173 status line at its LONGEST wording (anonymous-by-default). Measuring
	# without it measures a panel the real game never shows.
	s._ensure_sync_status_label()
	s.sync_status_label.visible = true
	s.sync_status_label.text = "Global leaderboard: OFF -- playing anonymously, score saved locally only (set a name and opt in via Settings)"
	return s

func _settle(_s: Control) -> void:
	# Four frames: RichTextLabel does not report get_content_height() / a settled
	# scrollbar until after its text has been laid out, and the layout happens on the
	# frame AFTER the container resolves its minimum sizes.
	for _i in range(4):
		await get_tree().process_frame

# --- 1. THE ACTUAL REQUEST: no scrolling --------------------------------------

func test_the_stats_block_does_not_scroll():
	var screen := _screen()
	await _settle(screen)
	var stats: RichTextLabel = screen.stats_label
	var content := float(stats.get_content_height())
	assert_lte(content, stats.size.y,
		("the game-over stats must fit their box without scrolling. Measured on the " +
		"build Pip played: a 720x300 box holding 713px of content, so 413px -- and " +
		"the 'Press ENTER for Leaderboard' line -- were unreachable. Content %.0f, " +
		"box %.0f.") % [content, stats.size.y])

func test_no_scrollbar_is_showing():
	# The directly checkable form of "I don't have to scroll": not merely that the
	# content fits, but that Godot is not drawing a scrollbar at all.
	var screen := _screen()
	await _settle(screen)
	var bar: VScrollBar = screen.stats_label.get_v_scroll_bar()
	assert_false(bar.visible,
		"a visible scrollbar IS the complaint -- it tells the player there is text " +
		"they cannot see")

func test_every_line_is_visible():
	var screen := _screen()
	await _settle(screen)
	var stats: RichTextLabel = screen.stats_label
	assert_eq(stats.get_visible_line_count(), stats.get_line_count(),
		("14 of 31 lines were visible on the failing build. Every line the screen " +
		"renders must be a line the player can read. total=%d visible=%d") % [
			stats.get_line_count(), stats.get_visible_line_count()])

# --- 2. THE ROOM WENT INTO TEXT, NOT PADDING ----------------------------------

## What the panel's CONTENTS actually require, independent of what the panel authors.
##
## THE TRAP THIS EXISTS TO AVOID, hit live while writing this file. The obvious
## version -- `panel.get_combined_minimum_size().y` -- is a TAUTOLOGY, because a
## Control's combined minimum already includes its own custom_minimum_size. So
## `needed` silently equals max(contents, authored), the slack is always 0, and the
## guard passes for ANY panel height. Proved on purpose: with the panel forced to
## 1000px (a flat over-grow, 200px of dead space) the whole file still reported 13/13
## green. That is the FOURTH assertion in this screen's lineage that could not fail --
## #1155 records three -- and it is why the number below is derived by zeroing the
## authored minimums first.
##
## Both the panel's and the StatsLabel's authored minimums are zeroed, the tree is
## allowed to re-settle, and the real text height is added back. What comes out is
## panel chrome + title + subtitle + separators + status line + button row + the
## height the actual BBCode occupies.
func _contents_require(screen: Control) -> float:
	var panel: Control = screen.get_node("CenterContainer/PanelContainer")
	var stats: RichTextLabel = screen.stats_label
	var panel_min := panel.custom_minimum_size
	var stats_min := stats.custom_minimum_size
	var text_height := float(stats.get_content_height())
	panel.custom_minimum_size = Vector2(panel_min.x, 0)
	stats.custom_minimum_size = Vector2(stats_min.x, 0)
	for _i in range(4):
		await get_tree().process_frame
	var without_stats := panel.get_combined_minimum_size().y
	panel.custom_minimum_size = panel_min
	stats.custom_minimum_size = stats_min
	for _i in range(4):
		await get_tree().process_frame
	return without_stats + text_height

func test_panel_is_sized_to_its_contents_both_ways():
	# TWO-SIDED on purpose. `needed <= authored` alone is satisfied by ANY oversized
	# panel, so it would rubber-stamp the flat percentage grow Pip's brief rejected.
	var screen := _screen()
	await _settle(screen)
	var panel: Control = screen.get_node("CenterContainer/PanelContainer")
	var authored: float = panel.custom_minimum_size.y
	var needed: float = await _contents_require(screen)
	assert_lte(needed, authored,
		("game_over_screen.tscn authors a %.0fpx panel but its contents need %.0fpx " +
		"-- the contents would be cut off or forced back into a scroll.") % [
			authored, needed])
	assert_lte(authored - needed, SLACK_BUDGET_PX,
		("game_over_screen.tscn authors a %.0fpx panel but the contents only need " +
		"%.0fpx, so it carries %.0fpx of slack. Pip asked for a screen he could " +
		"read, not a bigger empty box -- the room is for text.") % [
			authored, needed, authored - needed])

func test_body_text_is_at_least_the_godot_default():
	# #1155's floor. 16px is Godot's own Label default; body text authored below it is
	# how the pause menu came to read as cramped. At 1280x720 one authored pixel is
	# 0.667 physical, so 20px here is ~13 physical pixels.
	var screen := _screen()
	await _settle(screen)
	assert_gte(screen.stats_label.get_theme_font_size("normal_font_size"), 18,
		"the run summary is the most-read prose on the screen; 16px was the size " +
		"Pip called hard to read")

# --- 3. THE WAY OUT IS NOT INSIDE THE SCROLL ----------------------------------

func _buttons(screen: Control) -> HBoxContainer:
	return screen.get_node(
		"CenterContainer/PanelContainer/MarginContainer/VBox/ButtonsHBox")

func test_leaderboard_is_reachable_by_clicking_something():
	var screen := _screen()
	var names: Array = []
	for c in _buttons(screen).get_children():
		names.append(c.name)
	assert_has(names, "LeaderboardButton",
		("the ONLY advertised route to the board was the string '> Press ENTER for " +
		"Leaderboard' as the last line of a scrolled-off RichTextLabel. A way out of " +
		"a region must not live inside it. Buttons present: %s") % [str(names)])

func test_leaderboard_button_is_wired_to_the_transition():
	var screen := _screen()
	var btn: Button = _buttons(screen).get_node("LeaderboardButton")
	assert_true(btn.pressed.is_connected(screen._on_leaderboard_pressed),
		"a button that says Leaderboard and does nothing is worse than no button")

func test_navigation_prompt_is_gone_from_the_scrolling_text():
	# Belt and braces: if someone re-adds the prompt to the stats block, that is a
	# signal the button was lost and the old failure mode is creeping back.
	var screen := _screen()
	await _settle(screen)
	assert_false(screen.stats_label.text.contains("Press ENTER for Leaderboard"),
		"navigation belongs in the button row, not in the body copy")

# --- 4. #1173 MUST SURVIVE THIS LAYOUT CHANGE ---------------------------------
# Both of these landed the same night and are the fix for "no opportunity to submit".
# A layout rework is exactly the kind of change that quietly eats them.

func test_1173_status_line_still_sits_above_the_buttons():
	var screen := _screen()
	await _settle(screen)
	var vbox: Node = screen.stats_label.get_parent()
	var buttons_idx := -1
	for i in range(vbox.get_child_count()):
		if vbox.get_child(i).name == "ButtonsHBox":
			buttons_idx = i
	assert_gt(buttons_idx, -1, "precondition: the button row still exists")
	assert_lt(screen.sync_status_label.get_index(), buttons_idx,
		"#1173 moved the submit status ABOVE the buttons; it was at y=1217 below " +
		"three 50px buttons and read as nothing having happened")

func test_1173_status_line_is_still_16pt():
	var screen := _screen()
	await _settle(screen)
	assert_gte(screen.sync_status_label.get_theme_font_size("font_size"), 16,
		"#1173 raised this from 12pt; 12pt at the bottom of the panel is the size " +
		"that read as 'nothing happened'")

# --- 5. THE OLD COLOUR SCHEME ---------------------------------------------------

func _lin(v: float) -> float:
	return v / 12.92 if v <= 0.03928 else pow((v + 0.055) / 1.055, 2.4)

func _wcag_lum(c: Color) -> float:
	# NOT Color.get_luminance(): that is the weighted sRGB sum and does not linearise,
	# which overstates every dark colour. An earlier draft of the ThemeManager comment
	# quoted ratios computed that way and was wrong by a factor of two on [color=blue].
	return 0.2126 * _lin(c.r) + 0.7152 * _lin(c.g) + 0.0722 * _lin(c.b)

func _contrast(a: Color, b: Color) -> float:
	var la := _wcag_lum(a)
	var lb := _wcag_lum(b)
	return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

func test_shared_resource_and_staff_colours_are_readable_on_this_panel():
	var checked := 0
	for src in [ThemeManager.RESOURCE_COLORS, ThemeManager.STAFF_COLORS]:
		for key in src:
			var c: Color = src[key]
			var ratio := _contrast(c, PANEL_GROUND)
			assert_gte(ratio, MIN_CONTRAST,
				("%s renders at %.2f:1 on the game-over panel. [color=blue] " +
				"(#0000FF) measured 2.23:1 there and was used for 'Compute' -- a " +
				"number the player is meant to read.") % [key, ratio])
			checked += 1
	assert_gt(checked, 0, "precondition: the shared colour tables are not empty")

func test_this_screens_own_colours_are_readable_on_this_panel():
	var gos = load("res://scripts/ui/game_over_screen.gd")
	for key in ["_C_LABEL", "_C_SCORE_LABEL", "_C_SCORE", "_C_DIM", "_C_VICTORY",
			"_C_DEFEAT", "_C_LINK"]:
		var c: Color = gos.get(key)
		assert_gte(_contrast(c, PANEL_GROUND), MIN_CONTRAST,
			"%s renders at %.2f:1 on the game-over panel" % [
				key, _contrast(c, PANEL_GROUND)])

func test_no_named_web_primaries_remain_in_the_rendered_text():
	# The palette complaint in Pip's own words was "old colour schemes". These names
	# are Godot built-ins that belong to no theme this game ships; UI_STYLE_GUIDE.md's
	# palette contains no fully saturated primary.
	var screen := _screen()
	await _settle(screen)
	var text: String = screen.stats_label.text
	for name in ["color=cyan", "color=yellow", "color=blue", "color=purple",
			"color=lime", "color=green", "color=red", "color=gold", "color=white",
			"color=gray", "color=orange", "color=dodger_blue"]:
		assert_false(text.contains(name),
			("the game-over stats still emit [%s]. Colours on this screen come from " +
			"ThemeManager.RESOURCE_COLORS / STAFF_COLORS or the _C_* constants, all " +
			"of which are contrast-checked above.") % name)

extends GutTest
## The player guide had five scrollbars where it should have one (#1224 part 4,
## first reported by Pip in #1141 three weeks before the playtest that re-found it):
##
##   "these are all scrollable little mid-sections, as opposed to one long
##    continuous scroll, which is weird"
##
## WHAT IT ACTUALLY WAS. `player_guide.tscn` is one outer ScrollContainer
## (ContentScroll) wrapping four RichTextLabels. Every one of the four had:
##
##   custom_minimum_size = Vector2(0, N)   -- 96, 150, 190, 140
##   fit_content          unset (defaults false)
##   scroll_active        unset (defaults TRUE)
##
## In Godot 4 that trio is the recipe for an internal scrollbar: the label is
## clamped to a height, does not grow to its text, and scrolls the overflow
## itself. At the panel's 1100px width all four blocks overflowed -- the
## Resources block is roughly 16 wrapped lines in a 190px box. Outer scrollbar
## plus four inner ones, and "triple" in the original report was an undercount.
##
## IT IS THE ONLY SCREEN IN THE CODEBASE THAT DID IT. Every other RichTextLabel
## already pairs fit_content=true with scroll_active=false --
## bug_report_panel.tscn, main.tscn (x2), whats_new_modal.tscn,
## employee_screen.tscn (x2), welcome_overlay.tscn, and in code plan_screen.gd,
## screen_mode.gd, game_over_screen.gd, travel_panel_controller.gd,
## employee_screen.gd. So this test asserts the house pattern, not a new one.
##
## WHY A TEST AND NOT JUST THE FIX. It has been reported twice and survived a
## copy rewrite in between -- 78be0370 (#1136) relengthened the blocks, which
## plausibly made the nesting worse without anyone seeing it, because nothing
## measured it.

const GUIDE := "res://scenes/player_guide.tscn"

var _guide: Control


func before_each() -> void:
	_guide = load(GUIDE).instantiate()
	add_child_autofree(_guide)


func _rich_labels(node: Node, out: Array) -> Array:
	if node is RichTextLabel:
		out.append(node)
	for child in node.get_children():
		_rich_labels(child, out)
	return out


func test_the_guide_still_has_prose_to_scroll():
	# Negative control. If the guide's labels are ever renamed or restructured
	# away, the assertions below would pass over an empty array and prove nothing.
	var labels := _rich_labels(_guide, [])
	assert_gt(labels.size(), 0,
		"found no RichTextLabel in the guide; the rest of this file is vacuous")
	for lbl in labels:
		assert_gt(lbl.get_parsed_text().length(), 0,
			"%s carries no text" % lbl.name)


func test_no_section_scrolls_by_itself():
	for lbl in _rich_labels(_guide, []):
		assert_false(lbl.scroll_active,
			("%s scrolls internally. The outer ContentScroll is the ONE scroll " +
			"this screen is allowed; a section that scrolls itself hides its own " +
			"tail behind a scrollbar the reader has no reason to look for.")
			% lbl.name)


func test_every_section_grows_to_its_text():
	for lbl in _rich_labels(_guide, []):
		assert_true(lbl.fit_content,
			("%s does not fit_content, so it is sized by its box rather than by " +
			"its prose -- and the copy has been rewritten at least once since " +
			"these heights were authored.") % lbl.name)


func test_no_section_is_clamped_to_an_authored_height():
	for lbl in _rich_labels(_guide, []):
		assert_eq(lbl.custom_minimum_size.y, 0.0,
			("%s carries an authored minimum height of %.0fpx. fit_content only " +
			"grows a label; a floor under it re-creates the clamp that caused " +
			"this, and it goes stale the next time the copy changes.")
			% [lbl.name, lbl.custom_minimum_size.y])


func test_exactly_one_scroll_container_owns_the_content():
	var scrolls: Array = []
	var stack: Array = [_guide]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is ScrollContainer:
			scrolls.append(n.name)
		for c in n.get_children():
			stack.append(c)
	assert_eq(scrolls.size(), 1,
		("the guide should present as one long continuous scroll. Found %d " +
		"ScrollContainers: %s") % [scrolls.size(), str(scrolls)])

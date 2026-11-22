extends GutTest
## UI skins (spike/ui-skins): the switch must be reversible and must not touch font size.

const DEFAULT_AMBER := Color(1.0, 0.72, 0.20)
const DEFAULT_PANEL := Color(0.07, 0.093, 0.082)


func after_each() -> void:
	TerminalTheme.reset()


func _skins() -> Dictionary:
	var f := FileAccess.open("res://data/ui_skins.json", FileAccess.READ)
	assert_not_null(f, "ui_skins.json must exist")
	return JSON.parse_string(f.get_as_text())["skins"]


func test_every_skin_changes_the_palette_and_reset_restores_it_exactly() -> void:
	var skins := _skins()
	assert_gt(skins.size(), 0, "at least one skin")
	for id in skins:
		TerminalTheme.apply_skin(id, skins[id])
		assert_eq(TerminalTheme.current_skin, id)
		assert_ne(TerminalTheme.PANEL_BG, DEFAULT_PANEL, "%s must move PANEL_BG" % id)
		TerminalTheme.reset()
		assert_eq(TerminalTheme.AMBER, DEFAULT_AMBER, "reset after %s restores AMBER" % id)
		assert_eq(TerminalTheme.PANEL_BG, DEFAULT_PANEL, "reset after %s restores PANEL_BG" % id)
		assert_eq(TerminalTheme.current_skin, "default")


func test_a_partial_skin_does_not_inherit_the_previous_skin() -> void:
	var skins := _skins()
	var first: String = skins.keys()[0]
	TerminalTheme.apply_skin(first, skins[first])
	TerminalTheme.apply_skin("partial", {"palette": {"amber": "#112233"}})
	assert_eq(TerminalTheme.PANEL_BG, DEFAULT_PANEL, "untouched token falls back to DEFAULT")
	assert_eq(TerminalTheme.AMBER, Color.html("#112233"))


func test_hand_set_tokens_parse() -> void:
	TerminalTheme.apply_skin("hand", {"palette": {"green_dim": {"hex": "#5f8048", "hand": "why"}}})
	assert_eq(TerminalTheme.GREEN_DIM, Color.html("#5f8048"))


func test_default_skin_has_no_root_theme_and_skins_set_no_font_size() -> void:
	assert_null(TerminalTheme.build_root_theme(), "default must stay byte-identical (no root theme)")
	var skins := _skins()
	for id in skins:
		TerminalTheme.apply_skin(id, skins[id])
		var t := TerminalTheme.build_root_theme()
		assert_not_null(t)
		assert_false(t.has_default_font_size(), "%s must leave font size to base_theme.tres (#1224)" % id)

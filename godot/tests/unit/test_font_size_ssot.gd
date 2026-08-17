extends GutTest
## The font-size SSOT has to be a LEVER, not a declaration (#1224).
##
## Pip, after the 2026-08-14 playtest:
##
##   "the text can just all universally go up 2 to 4 points apart from maybe the
##    player guide"
##
## and, earlier, in #1140:
##
##   "the 10-pixel hint line -- fucking terrible, let's make that like a 50-pixel
##    hint line and just make all the text much bigger"
##
## THE STATE THAT MADE THAT A 367-SITE EDIT, measured on 2026-08-17:
##   215  theme_override_font_sizes/* declarations across godot/scenes/
##   152  add_theme_font_size_override() calls across scripts/ and autoload/
##    19  distinct values, from 8 to 72
##     1  central scale (ThemeManager.ThemeData.fonts), with ONE caller
##     0  times that scale had ever changed a rendered glyph
##
## The last two lines are the point. `notification_manager.gd:167` asked
## `get_font_size("body")` while the dictionary key was `"body_size"`, so the
## call took the silent `, 16` fallback at every invocation since it was
## written. A scale with one caller, and that caller wired to a fallback, is
## indistinguishable from no scale at all -- which is why nobody noticed.
##
## WHY THE GUARD IS SHAPED LIKE THIS. It would be easy to write a test that
## asserts base_theme.tres contains the number 19, and it would prove nothing:
## the old scale ALSO contained plausible numbers. What has to be proved is that
## the number reaches a glyph. So every assertion below goes through
## `get_theme_font_size()` on a real Control in a real tree -- the same call
## Godot makes when it draws -- rather than through the resource file.
##
## THE NEGATIVE CONTROL is test_an_unthemed_control_would_render_at_godot_16.
## Godot's own built-in default is 16, and 16 is what the whole game rendered at
## before this existed. If that test ever reports the SSOT value, the harness has
## stopped distinguishing "the lever works" from "everything is 19 anyway", and
## every other assertion in this file is a tautology.

const SSOT_PATH := "res://theme/base_theme.tres"
const MENU_THEME_PATH := "res://theme/menu_theme.tres"

## Godot's built-in default, i.e. what the game rendered at before the SSOT.
## Named so the negative control below reads as a measurement, not a magic number.
const GODOT_BUILTIN_DEFAULT := 16

## #1155 pinned >= 18 for body prose on the game-over screen, on the grounds that
## 16 was "the size Pip called hard to read". The SSOT is the body size for the
## whole game now, so it inherits that floor rather than being allowed to sit
## under a rule one screen already obeys.
const BODY_FLOOR := 18

var _host: Control


func before_each() -> void:
	_host = Control.new()
	add_child_autofree(_host)


func _child(node: Control) -> Control:
	_host.add_child(node)
	return node


# --- 1. THE SSOT IS WIRED AS THE PROJECT THEME --------------------------------

func test_project_theme_setting_points_at_the_ssot():
	assert_eq(ProjectSettings.get_setting("gui/theme/custom", ""), SSOT_PATH,
		("gui/theme/custom is what puts the SSOT at the bottom of Godot's theme " +
		"lookup chain. Without it the file is an unreferenced resource and " +
		"main.tscn -- which declares no theme of its own -- goes back to %d.")
		% GODOT_BUILTIN_DEFAULT)


func test_the_project_theme_actually_loaded():
	var pt: Theme = ThemeDB.get_project_theme()
	assert_not_null(pt, "the project theme did not load; the setting alone is not proof")
	assert_gt(pt.default_font_size, 0,
		"default_font_size is the one number. A zero or absent value means Godot " +
		"falls through to its own built-in default and the lever is decorative.")


func test_the_one_number_clears_the_floor_1155_already_pinned():
	assert_gte(ThemeManager.base_font_size(), BODY_FLOOR,
		("#1155 pinned body prose at >= %d because %d was the size Pip called hard " +
		"to read. The SSOT is now the body size for every screen, so it cannot " +
		"sit below a floor one screen already obeys.") % [BODY_FLOOR, GODOT_BUILTIN_DEFAULT])


# --- 2. THE NUMBER REACHES A GLYPH --------------------------------------------

func test_an_unoverridden_label_renders_at_the_ssot():
	var lbl: Label = _child(Label.new())
	assert_eq(lbl.get_theme_font_size("font_size"), ThemeManager.base_font_size(),
		"a plain Label with no override is the commonest text in the game")


func test_an_unoverridden_richtextlabel_renders_at_the_ssot():
	# RichTextLabel reads differently-named items (normal_font_size, not
	# font_size). Measured 2026-08-17: default_font_size covers them all without
	# restatement, so base_theme.tres does NOT list them. This is the check that
	# keeps that true across Godot upgrades -- if a future version stops falling
	# back for these names, this fails and the entries go back in.
	var rtl: RichTextLabel = _child(RichTextLabel.new())
	for item in ["normal_font_size", "bold_font_size", "italics_font_size", "mono_font_size"]:
		assert_eq(rtl.get_theme_font_size(item), ThemeManager.base_font_size(),
			"RichTextLabel/%s fell out of the SSOT's reach" % item)


func test_a_button_under_menu_theme_still_reaches_the_ssot():
	# menu_theme.tres used to declare Button/font_sizes/font_size = 16, and
	# because a scene theme beats the project theme, that ONE line was the reason
	# the lever could not move a single button on any of the nine menu screens.
	var menu: Control = _child(Control.new())
	menu.theme = load(MENU_THEME_PATH)
	var btn := Button.new()
	menu.add_child(btn)
	assert_eq(btn.get_theme_font_size("font_size"), ThemeManager.base_font_size(),
		("menu_theme.tres has started declaring a Button font size again. " +
		"Styling belongs there; sizing belongs in base_theme.tres."))


func test_menu_theme_declares_no_font_size_at_all():
	var menu: Theme = load(MENU_THEME_PATH)
	var offenders: Array = []
	for type_name in menu.get_font_size_type_list():
		for item in menu.get_font_size_list(type_name):
			offenders.append("%s/%s" % [type_name, item])
	assert_eq(offenders, [],
		("menu_theme.tres is a STYLING theme. Every font size it declares is a " +
		"size the SSOT cannot reach on nine screens. Found: %s") % [str(offenders)])


# --- 3. THE NEGATIVE CONTROL --------------------------------------------------

func test_the_reading_follows_the_theme_and_is_not_a_constant():
	# The negative control. Every "renders at the SSOT" assertion above would
	# pass for the wrong reason if get_theme_font_size() reported a fixed number
	# regardless of theme, so: give one Control a theme with a deliberately
	# unlike-anything size and prove the reading moves to it.
	#
	# (A first draft used an orphan Control, assuming no tree owner meant no
	# project theme. Measured 2026-08-17: it still reports the SSOT. Godot
	# resolves the project theme even for an un-parented Control, which makes the
	# lever MORE global than assumed -- and made that draft a false control.)
	const ODD_SIZE := 33
	var probe_theme := Theme.new()
	probe_theme.default_font_size = ODD_SIZE
	assert_ne(ODD_SIZE, ThemeManager.base_font_size(),
		"the probe size collided with the real one; pick another")

	var themed: Control = _child(Control.new())
	themed.theme = probe_theme
	var lbl := Label.new()
	themed.add_child(lbl)
	assert_eq(lbl.get_theme_font_size("font_size"), ODD_SIZE,
		("this harness cannot tell one font size from another. Until it can, " +
		"every assertion in this file is a tautology."))


func test_the_ssot_is_not_back_at_godot_s_own_default():
	assert_ne(ThemeManager.base_font_size(), GODOT_BUILTIN_DEFAULT,
		("the SSOT has been set back to Godot's built-in %d, which is what the " +
		"whole game rendered at before #1224. The lever is still wired; the bump " +
		"is gone.") % GODOT_BUILTIN_DEFAULT)


func test_an_explicit_override_still_beats_the_ssot():
	# Stated as a test rather than as a caveat in a comment, because it is the
	# honest boundary of this whole change: the SSOT reaches every UNOVERRIDDEN
	# string, and ~280 override sites remain that it does not reach.
	# tools/check_font_sizes.py counts them.
	var lbl: Label = _child(Label.new())
	lbl.add_theme_font_size_override("font_size", 7)
	assert_eq(lbl.get_theme_font_size("font_size"), 7,
		("an override no longer wins over the project theme. That would be a " +
		"Godot behaviour change, and it would silently resize every screen that " +
		"still carries one."))


# --- 4. ThemeManager.get_font_size() ------------------------------------------

func test_body_returns_the_ssot_and_not_the_old_silent_fallback():
	# THE REGRESSION. This exact call -- get_font_size("body") -- returned 16 for
	# the entire life of the old scale, because the key was "body_size". The
	# assertion is failing-capable: restore the old dictionary and it returns
	# GODOT_BUILTIN_DEFAULT again, which is not base_font_size().
	assert_eq(ThemeManager.get_font_size("body"), ThemeManager.base_font_size(),
		"get_font_size('body') is the call site that was broken from the day it was written")


func test_both_spellings_answer_the_same():
	# The two APIs disagreed about who appends '_size' -- apply_label_style()
	# appended it, get_font_size() did not -- and that disagreement IS the bug.
	# Accepting both is how it stops recurring.
	assert_eq(ThemeManager.get_font_size("body_size"), ThemeManager.get_font_size("body"))
	assert_eq(ThemeManager.get_font_size("title_size"), ThemeManager.get_font_size("title"))


func test_the_scale_is_ordered_and_moves_with_the_one_number():
	var small := ThemeManager.get_font_size("small")
	var body := ThemeManager.get_font_size("body")
	var header := ThemeManager.get_font_size("header")
	var title := ThemeManager.get_font_size("title")
	assert_lt(small, body, "small must be smaller than body")
	assert_lt(body, header, "header must be larger than body")
	assert_lt(header, title, "title must be largest")
	# Offsets, not ratios: turning the one number must move every step by the
	# SAME amount, or Pip's '+2 to +4 points universally' leaves the big text
	# almost where it was.
	var base := ThemeManager.base_font_size()
	assert_eq(body, base, "body IS the one number, not a multiple of it")
	assert_eq(small, base + ThemeManager.FONT_STEPS["small"])
	assert_eq(header, base + ThemeManager.FONT_STEPS["header"])
	assert_eq(title, base + ThemeManager.FONT_STEPS["title"])


func test_a_theme_swap_does_not_move_a_font_size():
	# #1155's rule, generalised: a theme swap must not move a size a test has
	# pinned. ThemeData carried title_size/body_size overrides for the retro
	# theme; picking "Retro Terminal" would have resized the game's prose, and
	# after the bump its 18 would have been a DOWNGRADE from the new body.
	var before := ThemeManager.get_font_size("body")
	var original := ThemeManager.current_theme
	for name in ThemeManager.themes.keys():
		ThemeManager.current_theme = name
		assert_eq(ThemeManager.get_font_size("body"), before,
			"theme '%s' moved the body font size" % name)
	ThemeManager.current_theme = original

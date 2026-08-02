extends GutTest
## B1/B2/B3 (recorded playtest 2026-08-01, [4:55]-[5:03]) -- the month review's forward door.
##
## The failure: MainUI._input blocks SPACE and ENTER outright whenever any dialog is up. That
## rule is correct for a crisis window (it stops an accidental end-turn/commit landing on a
## decision), but the month review is not a decision -- it is a door with one costless option.
## So the two keys every player reaches for did nothing, and the key that DID work (Q) worked
## only because "Begin planning..." happened to be button 0 in the letter map. Pip found Q by
## accident. His ruling: "maybe a space bar or something as well -- maybe not enter, if enter
## is going to be the commit turn thing, we don't want people doing that accidentally."
##
## This suite asserts the ROUTING and the CHROME SUPPRESSION -- both are behaviour, not
## appearance. Nothing here proves the screen LOOKS right; only Pip's eyes can do that.


# --- EventDialog.is_navigation_popup: which popups are doors? --------------------------------

func _popup(options: Array) -> Dictionary:
	return {"id": "x", "name": "X", "type": "popup", "options": options}


func test_single_costless_option_is_a_navigation_popup() -> void:
	var ev := _popup([{"id": "begin_planning", "text": "Begin planning August 2017", "costs": {}}])
	assert_true(EventDialog.is_navigation_popup(ev), "one free option is a door, not a decision")


func test_missing_costs_key_is_still_a_navigation_popup() -> void:
	# The review builder writes costs:{}, but an option Dictionary with no costs key at all
	# renders identically (" (Free)"), so it must classify identically.
	var ev := _popup([{"id": "ok", "text": "Continue"}])
	assert_true(EventDialog.is_navigation_popup(ev))


func test_zero_valued_costs_are_still_free() -> void:
	# format_cost_summary drops non-positive entries, so this option renders " (Free)". The
	# predicate is defined in terms of what format_cost_summary WOULD print precisely so the
	# two can never disagree about what chrome is being suppressed.
	var ev := _popup([{"id": "ok", "text": "Continue", "costs": {"money": 0, "attention": 0}}])
	assert_true(EventDialog.is_navigation_popup(ev))


func test_priced_single_option_is_not_navigation() -> void:
	var ev := _popup([{"id": "pay", "text": "Pay the fine", "costs": {"money": 20000}}])
	assert_false(EventDialog.is_navigation_popup(ev),
		"a single option that COSTS something is still a decision -- keep its cost chrome")


func test_multi_option_event_is_not_navigation() -> void:
	# A crisis window with a free out must keep its [Q]/[W] letter menu: with two options the
	# letters are the only way to say WHICH one a key press picks.
	var ev := _popup([
		{"id": "handle", "text": "Handle it", "costs": {"attention": 2}},
		{"id": "ignore", "text": "Ignore it", "costs": {}},
	])
	assert_false(EventDialog.is_navigation_popup(ev))


func test_zero_option_popup_is_not_navigation() -> void:
	assert_false(EventDialog.is_navigation_popup(_popup([])))


func test_navigation_predicate_agrees_with_the_chrome_it_suppresses() -> void:
	# The chrome being suppressed is exactly this string. If the "(Free)" wording ever changes,
	# this pins that is_navigation_popup changes with it rather than silently classifying
	# every popup as priced (which would quietly restore the [Q] and the price tag).
	assert_eq(EventDialog.format_cost_summary({}), " (Free)")


# main_ui.gd deliberately has NO class_name (it would form a coupling cycle with
# EventResultPresenter, see that file's header), so reach the static through the script
# resource rather than adding a class_name to a 3k-line monolith just to test it.
const MainUIScript := preload("res://scripts/ui/main_ui.gd")


# --- MainUIScript.dialog_key_advances: SPACE yes, ENTER no -----------------------------------------

func _dialog(space_advances: bool) -> Control:
	var d := Control.new()
	d.set_meta("space_advances", space_advances)
	autofree(d)
	return d


func test_space_advances_an_opted_in_dialog() -> void:
	assert_true(MainUIScript.dialog_key_advances(_dialog(true), KEY_SPACE))


func test_enter_never_advances_even_an_opted_in_dialog() -> void:
	# Pip's [5:03] ruling, and the load-bearing half of it: ENTER is the commit-plan binding
	# (main_ui _input, KEY_ENTER -> _on_commit_plan_button_pressed). If dismissing a monthly
	# popup trained ENTER as a "next" reflex, players would commit turns by muscle memory.
	# There is deliberately NO meta that can turn this true.
	assert_false(MainUIScript.dialog_key_advances(_dialog(true), KEY_ENTER))


func test_space_does_not_advance_a_crisis_dialog() -> void:
	# A window/event dialog never sets the meta, so SPACE stays blocked there -- the original
	# accidental-end-turn protection is untouched for every dialog that is a real decision.
	assert_false(MainUIScript.dialog_key_advances(_dialog(false), KEY_SPACE))


func test_space_does_not_advance_a_dialog_with_no_meta_at_all() -> void:
	var d := Control.new()
	autofree(d)
	assert_false(MainUIScript.dialog_key_advances(d, KEY_SPACE),
		"opt-in must default to OFF for every dialog that predates this flag")


func test_null_dialog_is_safe() -> void:
	assert_false(MainUIScript.dialog_key_advances(null, KEY_SPACE))


func test_other_keys_do_not_advance() -> void:
	# Only SPACE is promoted. ESC keeps its own path (modal_stack.handle_escape, #452/#877)
	# and Q keeps working through the positional letter map -- neither routes through here.
	for key in [KEY_ESCAPE, KEY_Q, KEY_A, KEY_1, KEY_TAB]:
		assert_false(MainUIScript.dialog_key_advances(_dialog(true), key),
			"key %d must not be promoted past the dialog key block" % key)

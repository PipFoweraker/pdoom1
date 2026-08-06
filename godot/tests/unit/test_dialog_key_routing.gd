extends GutTest
## Regression tests for MODAL CHOICE KEYS (#567) -- the key a button advertises and the
## key that fires it must be the same key, always.
##
## Input routing is BEHAVIOUR, not appearance, so it is testable without a live input
## stack: DialogKeys is a pure static table and MainUI._dialog_button_index_for_key is a
## thin call into it. The original #567 symptom -- "Key index 3 out of range" when the
## player pressed R at a three-option event -- is pinned directly in
## test_letter_past_button_count_is_not_a_choice.
##
## The source-scan tests at the bottom are deliberate. The defect class here was never a
## wrong constant; it was SIX copies of the same constant in six files with nothing
## forcing them to agree. A test that only checked DialogKeys would pass forever while a
## producer quietly re-grew its own list, which is exactly how this survived from
## 2026-07-22. So the guards check the property that actually matters: no producer owns a
## private copy.

const PRODUCER_SCRIPTS := [
	"res://scripts/ui/event_dialog.gd",
	"res://scripts/ui/submenu_controller.gd",
	"res://scripts/ui/travel_panel_controller.gd",
	"res://scripts/ui/hiring_panel_controller.gd",
	"res://scripts/ui/main_ui.gd",
]


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	assert_not_null(f, "Could not open %s" % path)
	if f == null:
		return ""
	return f.get_as_text()


# --- the table itself ----------------------------------------------------------------

func test_label_and_keycode_round_trip():
	# The whole contract in one line: the key advertised for choice i routes back to i.
	var n := DialogKeys.capacity()
	for i in range(n):
		var keycode := DialogKeys.keycode_for_index(i)
		assert_eq(DialogKeys.index_for_keycode(keycode, n), i,
			"Key advertised for choice %d ('%s') must route to choice %d" % [i, DialogKeys.label_for(i), i])


func test_letter_past_button_count_is_not_a_choice():
	# #567 verbatim: R is letter index 3. On a THREE-option event there is no choice 3,
	# so R must name nothing -- not index 3 for the caller to trip over.
	assert_eq(DialogKeys.index_for_keycode(KEY_R, 3), -1,
		"R on a 3-option dialog must map to no choice (#567 'key index 3 out of range')")
	# ...and must still work the moment a fourth option exists.
	assert_eq(DialogKeys.index_for_keycode(KEY_R, 4), 3,
		"R must select choice 4 when a 4th option is actually on screen")


func test_unbound_key_names_no_choice():
	assert_eq(DialogKeys.index_for_keycode(KEY_M, 9), -1,
		"A key with no label must never select a choice")


func test_numbers_are_an_accepted_alias_bounded_the_same_way():
	# Numbers stay accepted (old habits), but obey the same on-screen bound as letters.
	assert_eq(DialogKeys.index_for_keycode(KEY_2, 3), 1, "2 selects choice 2 when it exists")
	assert_eq(DialogKeys.index_for_keycode(KEY_4, 3), -1, "4 selects nothing on a 3-option dialog")


func test_empty_dialog_routes_nothing():
	assert_eq(DialogKeys.index_for_keycode(KEY_Q, 0), -1,
		"A dialog with no choice buttons must swallow choice keys, not route them")


func test_prefix_is_blank_past_capacity_not_empty_brackets():
	# The old truncated per-panel lists rendered a bare "[] " on the first unlabelled
	# button. Blank means blank.
	assert_eq(DialogKeys.prefix_for(0), "[Q] ")
	assert_eq(DialogKeys.prefix_for(DialogKeys.capacity()), "",
		"A button past key capacity must render NO bracket, not an empty one")
	assert_eq(DialogKeys.label_for(-1), "", "Negative index must be label-less")


func test_labels_and_keys_are_the_same_length():
	assert_eq(DialogKeys.LETTER_LABELS.size(), DialogKeys.LETTER_KEYS.size(),
		"Every advertised label must have a keycode and vice versa")
	assert_eq(DialogKeys.NUMBER_KEYS.size(), DialogKeys.LETTER_KEYS.size(),
		"The alias row must cover the same choice range as the advertised row")


# --- anti-drift: nobody keeps a private copy ------------------------------------------

func test_no_producer_keeps_its_own_key_label_list():
	# The #567 generator was six independent arrays. If one comes back, this goes red.
	for path in PRODUCER_SCRIPTS:
		var src := _read(path)
		assert_false(src.contains('"Q", "W", "E"'),
			"%s must not carry a private choice-key list -- use DialogKeys (#567)" % path)
		assert_false(src.contains('"1", "2", "3"'),
			"%s must not carry a private choice-key list -- use DialogKeys (#567)" % path)


func test_router_delegates_to_the_shared_table():
	var src := _read("res://scripts/ui/main_ui.gd")
	assert_true(src.contains("DialogKeys.index_for_keycode(keycode, active_dialog_buttons.size())"),
		"MainUI must route choice keys through DialogKeys, bounded by the LIVE button count")


func test_hiring_panel_registers_its_choice_buttons():
	# #575: the hiring pipeline registered an EMPTY button array, so every key inside the
	# panel the shortcut had just opened was dead.
	var src := _read("res://scripts/ui/hiring_panel_controller.gd")
	assert_true(src.contains("host.active_dialog_buttons = keyed_buttons"),
		"The hiring pipeline must hand its keyed buttons to the router (#575)")
	assert_true(src.contains("DialogKeys.prefix_for(key_index)"),
		"Each hiring card must ADVERTISE the key that fires it (#575)")

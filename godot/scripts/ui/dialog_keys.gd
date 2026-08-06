class_name DialogKeys
extends RefCounted
## SINGLE SOURCE OF TRUTH for modal choice keys (#567, #575).
##
## WHY THIS EXISTS: before this file, the key a dialog ADVERTISED and the key MainUI
## ACCEPTED were six independent hardcoded arrays -- event_dialog.gd:229, three copies
## in submenu_controller.gd's GRID_CONFIG plus a fourth in its financing builder,
## travel_panel_controller.gd:92, and MainUI._dialog_button_index_for_key. Nothing tied
## them together, so:
##   * they could drift silently (edit one producer's labels, MainUI still routes the
##     old letters -- the player presses what the button says and gets another option);
##   * the SHORT lists (office/scouting shipped 3-4 labels for grids that can hold more)
##     left later buttons with a blank "[] " prefix while MainUI still fired them from
##     an unadvertised key -- a working key nobody could discover;
##   * travel advertised NUMBERS while every sibling panel advertised LETTERS.
## #567's symptom ("Key index 3 out of range" on 'r' in a 3-option event) is one
## instance: R is index 3 in the letter list, and the router had no idea the dialog on
## screen only had three options.
##
## THE RULE (see docs/design/NAVIGATION_AUDIT.md, principle P3): a choice key is
## LEGITIMATE only if the button it fires is on screen AND carries that key's label.
## Producers call label_for() to render; the router calls index_for_keycode() to route.
## One table, so the two can never disagree.
##
## LETTERS are the advertised scheme everywhere (home-row-ish reach, and 1-9 already
## mean "action bar slot" outside a dialog). NUMBERS stay ACCEPTED as an unadvertised
## alias so an old habit is not punished -- but nothing renders them any more.

## Advertised labels, in button order. Index i <-> LETTER_KEYS[i].
const LETTER_LABELS: Array = ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"]
const LETTER_KEYS: Array = [KEY_Q, KEY_W, KEY_E, KEY_R, KEY_A, KEY_S, KEY_D, KEY_F, KEY_Z]

## Accepted-but-unadvertised alias row.
const NUMBER_KEYS: Array = [KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7, KEY_8, KEY_9]


static func capacity() -> int:
	"""How many choices can carry a key at all. Buttons past this get no label and no
	key -- deliberately, so the label and the routing run out together."""
	return LETTER_LABELS.size()


static func label_for(index: int) -> String:
	"""The advertised label for choice `index`, or "" when the index is past capacity."""
	if index < 0 or index >= LETTER_LABELS.size():
		return ""
	return String(LETTER_LABELS[index])


static func prefix_for(index: int) -> String:
	"""Render-ready "[Q] " prefix, or "" past capacity so a keyless button shows no
	empty brackets (the old short-list bug rendered a bare "[] ")."""
	var label := label_for(index)
	if label == "":
		return ""
	return "[%s] " % label


static func keycode_for_index(index: int) -> int:
	"""The advertised keycode for choice `index`, or KEY_NONE past capacity."""
	if index < 0 or index >= LETTER_KEYS.size():
		return KEY_NONE
	return int(LETTER_KEYS[index])


static func index_for_keycode(keycode: int, button_count: int) -> int:
	"""Route a pressed key to a choice index, or -1 when the key names no choice that is
	actually on screen.

	`button_count` is not optional decoration: it is what makes the router honest. R on a
	three-option event returns -1 here rather than -- as before -- returning 3 and leaving
	the caller to discover the array was too short (#567)."""
	if button_count <= 0:
		return -1
	var index: int = LETTER_KEYS.find(keycode)
	if index < 0:
		index = NUMBER_KEYS.find(keycode)
	if index < 0 or index >= button_count:
		return -1
	return index

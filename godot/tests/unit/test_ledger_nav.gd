extends GutTest
## #601/#602: ledger-screen UX + navigation-consistency regressions.
##
## Behaviour that needs a live viewport (the actual L toggle wiring inside MainUI._input,
## ESC returning from the Employee screen, and the visual layout filling the panel) is
## exercised by the boot check + a human eye -- see the PR notes. These tests lock the
## cheap, deterministic invariants: the L keybind, the distinct-red warning constant, and
## the ledger dialog's toggle meta being reachable from the script.

func _ledger_ui_constants() -> Dictionary:
	# Read the script's constant map off the GDScript *resource* (get_script_constant_map is
	# a non-static method, so it needs the loaded resource, not the class reference).
	# #622 L10: the ledger palette moved from main_ui.gd into ledger_screen.gd.
	var script: GDScript = load("res://scripts/ui/ledger_screen.gd")
	return script.get_script_constant_map()

func _make_key_event(keycode: int) -> InputEventKey:
	var ev := InputEventKey.new()
	ev.keycode = keycode
	ev.pressed = true
	return ev

# --- Part A.2: L is the ledger toggle key -------------------------------------

func test_open_ledger_bound_to_L():
	# The toggle in MainUI keys off KeybindManager's "open_ledger" action; it must be L.
	assert_eq(KeybindManager.keybinds["open_ledger"]["key"], KEY_L,
		"open_ledger should be bound to L (the key that both opens and closes the ledger)")

func test_L_matches_open_ledger_action():
	# With nothing focused, an L key event matches open_ledger -- the trigger the toggle uses.
	var vp = KeybindManager.get_viewport()
	if vp and vp.gui_get_focus_owner():
		vp.gui_get_focus_owner().release_focus()
	await get_tree().process_frame
	assert_true(KeybindManager.is_action_pressed(_make_key_event(KEY_L), "open_ledger"),
		"An L key press should match the open_ledger action")

# --- Part A.3: ledger warnings use a distinct RED -----------------------------

func test_ledger_warn_red_is_a_named_constant():
	var consts := _ledger_ui_constants()
	assert_true(consts.has("_LEDGER_WARN_RED"),
		"LedgerScreen should expose a named _LEDGER_WARN_RED constant for ledger warnings")

func test_ledger_warn_colour_reads_as_red():
	var consts := _ledger_ui_constants()
	var c: Color = consts["_LEDGER_WARN_RED"]
	# Red-dominant and clearly not the event-gold / success-green used elsewhere.
	assert_gt(c.r, 0.7, "warning red should be strongly red")
	assert_lt(c.g, 0.5, "warning red should be low in green")
	assert_lt(c.b, 0.5, "warning red should be low in blue")
	assert_gt(c.r, c.g, "red channel must dominate green (distinct from the event gold)")
	assert_gt(c.r, c.b, "red channel must dominate blue")

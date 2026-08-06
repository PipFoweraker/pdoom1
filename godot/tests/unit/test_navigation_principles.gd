extends GutTest
## Executable form of docs/design/NAVIGATION_AUDIT.md (#602, #565, #575).
##
## #602 asked for a PRINCIPLE, not four patches. A principle that only lives in a
## markdown file rots the way decisions/README.md rotted; these tests are the half of
## the principle a future PR is actually checked against.
##
## Pinned here:
##   P1  every screen/panel reachable by hotkey is also reachable by a visible control
##   P2  a key that opens a panel closes it (mirrored toggles)
##   P4  no advertised key is inert, and no working key is unadvertised
##   #575 global shortcuts yield to a focused text field, gate FIRST

## Hotkey-openable submenus -> the action-bar id that must also open them by click.
const HOTKEY_SUBMENUS := {
	"menu_hire": "hire_staff",
	"menu_fundraise": "fundraise",
	"menu_publicity": "publicity",
	"menu_travel": "travel",
}


## Binds whose action NAME is built at runtime, so no literal string exists to grep for.
## bind name -> the exact expression that must appear in source to prove it is dispatched.
const DYNAMIC_BIND_FAMILIES := {
	"action_1": '"action_%d" % (i + 1)',
	"action_2": '"action_%d" % (i + 1)',
	"action_3": '"action_%d" % (i + 1)',
	"action_4": '"action_%d" % (i + 1)',
	"action_5": '"action_%d" % (i + 1)',
	"action_6": '"action_%d" % (i + 1)',
	"action_7": '"action_%d" % (i + 1)',
	"action_8": '"action_%d" % (i + 1)',
	"action_9": '"action_%d" % (i + 1)',
}


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	assert_not_null(f, "Could not open %s" % path)
	if f == null:
		return ""
	return f.get_as_text()


func _all_gd_sources() -> String:
	"""Concatenated text of every non-addon .gd under scripts/ + autoload/. Used to ask
	'does anything anywhere handle this action name?'."""
	var blob := ""
	var stack: Array = ["res://scripts", "res://autoload"]
	while not stack.is_empty():
		var dir_path: String = stack.pop_back()
		var dir := DirAccess.open(dir_path)
		if dir == null:
			continue
		dir.list_dir_begin()
		var name := dir.get_next()
		while name != "":
			var full := "%s/%s" % [dir_path, name]
			if dir.current_is_dir():
				stack.append(full)
			elif name.ends_with(".gd"):
				var f := FileAccess.open(full, FileAccess.READ)
				if f != null:
					blob += f.get_as_text()
			name = dir.get_next()
		dir.list_dir_end()
	return blob


# --- P1: hotkey-only features do not exist -------------------------------------------

func test_every_hotkey_submenu_is_also_in_the_action_bar():
	# #565: Travel & Conferences was reachable ONLY by T -- a whole feature with no
	# visible door. The general rule, not just the travel patch: if a hotkey opens it,
	# the action bar lists it.
	var ids := {}
	for action in GameActions.get_all_actions():
		ids[String(action.get("id", ""))] = action
	for bind_name in HOTKEY_SUBMENUS:
		var action_id: String = HOTKEY_SUBMENUS[bind_name]
		assert_true(ids.has(action_id),
			"Hotkey '%s' opens '%s', so '%s' must be a visible action-bar item (#565, P1)" % [bind_name, action_id, action_id])
		if ids.has(action_id):
			assert_true(bool(ids[action_id].get("is_submenu", false)),
				"'%s' must be flagged is_submenu so the action bar routes it to a panel" % action_id)


func test_travel_is_unlocked_from_the_first_turn():
	# The conference/travel lane has no gate; a locked action is filtered out of the bar
	# entirely, which would reproduce #565 by another route.
	var travel := {}
	for action in GameActions.get_all_actions():
		if String(action.get("id", "")) == "travel":
			travel = action
	assert_false(travel.is_empty(), "travel action must exist")
	var fresh_state := {"turn": 1, "total_staff": 0, "reputation": 0, "research": 0, "papers_published": 0}
	assert_true(GameActions.is_action_unlocked(travel, fresh_state),
		"Travel must be visible from turn 1 -- it is the only door to conferences (#565)")


func test_hotkey_submenus_are_not_hidden_from_the_action_bar():
	for bind_name in HOTKEY_SUBMENUS:
		var action_id: String = HOTKEY_SUBMENUS[bind_name]
		assert_false(ActionBarRenderer.HIDDEN_FROM_ACTION_BAR_IDS.has(action_id),
			"'%s' is hotkey-openable so it must not be hidden from the action bar (P1)" % action_id)


# --- P2: mirrored toggles --------------------------------------------------------------

func test_menu_hotkeys_go_through_the_mirrored_toggle():
	# Each menu hotkey must call _toggle_submenu (open-or-close), not a bare open.
	var src := _read("res://scripts/ui/main_ui.gd")
	for bind_name in HOTKEY_SUBMENUS:
		var action_id: String = HOTKEY_SUBMENUS[bind_name]
		assert_true(src.contains('_toggle_submenu("%s")' % action_id),
			"Hotkey '%s' must toggle '%s', not only open it (#602, P2)" % [bind_name, action_id])
	assert_false(src.contains('submenu_controller.open("hire_staff")'),
		"The hotkey path must not bypass the toggle by calling open() directly (P2)")


func test_bug_reporter_key_is_mirrored_too():
	# The toggle sweep missed N: it opened the bug-report form and could not close it,
	# while BugReportPanel.toggle_panel() sat unused. P2 applies to every panel key.
	var src := _read("res://scripts/ui/main_ui.gd")
	assert_true(src.contains("if bug_report_panel.visible:"),
		"N must close the bug-report form it opened (#602, P2)")


func test_settings_is_reachable_mid_run_by_a_visible_control():
	# P1's sharpest case found by the audit: with a run live, the Settings screen -- and
	# therefore the KEYBIND EDITOR -- had no door at all. F10 was bound and inert; the
	# pause menu offered Resume/Resign/Save/MainMenu/Quit and nothing else.
	var scene := _read("res://scenes/pause_menu.tscn")
	assert_true(scene.contains('[node name="SettingsButton"'),
		"The pause menu must carry a visible Settings entrance (#602, P1)")
	assert_true(scene.contains('method="_on_settings_pressed"'),
		"The pause menu Settings button must be wired")
	var src := _read("res://scripts/ui/pause_menu.gd")
	assert_true(src.contains('SceneTransition.go_to("res://scenes/settings_menu.tscn")'),
		"Pause -> Settings must route through SceneTransition (P7)")


func test_both_doors_into_a_submenu_share_one_function():
	# P1's mechanical half: click and hotkey must produce the SAME panel in the same
	# state, which is only guaranteed if they share the builder.
	var src := _read("res://scripts/ui/main_ui.gd")
	assert_true(src.contains("func _open_submenu(submenu_id: String) -> void:"),
		"There must be ONE door into a submenu")
	assert_true(src.contains('active_dialog.set_meta("submenu_id", submenu_id)'),
		"A live panel must know what it is, so the mirrored toggle cannot desync (P2)")


# --- P4: no inert keys, no unadvertised keys -------------------------------------------

func test_no_keybind_action_is_inert():
	# #602's audit found "menu_research" (R) bound, listed in the rebind screen, and
	# handled by NOTHING. An advertised key that does nothing teaches the player the
	# game is broken. Every bind must be named by some handler somewhere.
	var blob := _all_gd_sources()
	for action_name in KeybindManager.keybinds.keys():
		if DYNAMIC_BIND_FAMILIES.has(action_name):
			# Handled by a constructed name, so a literal-string scan cannot see it. The
			# family's construction expression is asserted separately below, so the bind is
			# still proven live rather than merely excused.
			continue
		# Require the bind to be MATCHED, not merely mentioned. A bare name-count let
		# "settings" pass on the strength of keybind_manager's own ConfigFile section name
		# while F10 did nothing at all -- the guard has to name the consuming call.
		assert_true(blob.contains('is_action_pressed(event, "%s")' % action_name),
			"Keybind '%s' is advertised but nothing matches it (#602, P4)" % action_name)


func test_dynamic_bind_families_are_actually_dispatched():
	var blob := _all_gd_sources()
	for family_expr in DYNAMIC_BIND_FAMILIES.values():
		assert_true(blob.contains(family_expr),
			"Dynamic bind family '%s' must be dispatched somewhere (#602, P4)" % family_expr)


func test_menu_research_stays_deleted():
	assert_false(KeybindManager.keybinds.has("menu_research"),
		"menu_research had no research submenu to open -- it must not come back (#602)")


func test_esc_is_reserved_not_falsely_rebindable():
	# The audit's other inert bind: "cancel" (ESC) was listed in the rebind screen while
	# every ESC handler matched a raw KEY_ESCAPE, so rebinding it changed nothing. A key
	# belongs in keybinds OR in RESERVED_KEYS -- never neither, never both.
	assert_false(KeybindManager.keybinds.has("cancel"),
		"ESC cannot honour a rebind, so it must not be offered as one (#602, P4/P5)")
	assert_true(KeybindManager.RESERVED_KEYS.has("escape"),
		"ESC's non-rebindability must be documented, not merely absent")


func test_keybind_screen_cannot_swallow_esc_as_a_binding():
	# The rebind screen used to CAPTURE whatever key you pressed, ESC included -- so the
	# one screen whose job is keys was the one place you could destroy the universal back
	# key. And with no rebind pending its _input returned early, leaving ESC inert on a
	# full screen. Both are P5 violations.
	var src := _read("res://scripts/ui/keybind_screen.gd")
	assert_true(src.contains("if event.keycode == KEY_ESCAPE:"),
		"The rebind screen must intercept ESC before capturing it as a binding (P5)")
	assert_true(src.contains("_cancel_pending_rebind()"),
		"ESC during a rebind must cancel it, not become the new bind (P5)")


func test_core_gameplay_keys_are_rebindable_not_hardcoded():
	# P4's other direction: a key the game responds to must be a bind the rebind screen
	# can see, or the settings screen lies. SPACE/ENTER/N/V were raw keycodes in _input.
	var src := _read("res://scripts/ui/main_ui.gd")
	for action_name in ["end_turn", "commit_plan", "bug_reporter", "toggle_view"]:
		assert_true(KeybindManager.keybinds.has(action_name),
			"'%s' must exist as a rebindable action" % action_name)
		assert_true(src.contains('is_action_pressed(event, "%s")' % action_name),
			"MainUI must read '%s' through KeybindManager, not a hardcoded keycode (P4)" % action_name)


# --- #575: the text-focus gate runs FIRST ----------------------------------------------

func test_text_focus_gate_precedes_every_shortcut_in_main_ui():
	# Half-applying this is how #575 survived: the gate has to sit ABOVE the shortcut
	# chain, or some keys still get eaten while the player is typing a bug report.
	var src := _read("res://scripts/ui/main_ui.gd")
	var gate := src.find("KeybindManager.is_text_input_focused()")
	assert_gt(gate, -1, "MainUI._input must consult the text-focus gate (#575)")
	for marker in ["is_action_pressed(event, \"open_ledger\")", "event.keycode == KEY_ESCAPE"]:
		var pos := src.find(marker)
		assert_gt(pos, gate,
			"Shortcut '%s' must be handled AFTER the text-focus gate, never before (#575)" % marker)

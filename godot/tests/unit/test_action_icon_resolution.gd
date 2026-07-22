extends GutTest
## Regression guard (#762, widened #768): every action id the UI renders an icon
## for must resolve to a REAL icon, not the magenta-checkerboard placeholder.
##
## The July 2026 regression: most action-icon buttons rendered the placeholder
## because several top-level action ids in data/actions/core.json (operations,
## travel, financing, and the hiring pipeline advertise/use_connections/
## interview_next/hire_best/onboard_next) had no entry in data/icon_mapping.json.
## IconLoader.get_action_icon() falls back to the placeholder for unmapped ids.
##
## #768 follow-up: the original test only drove GameActions.get_all_actions()
## (the top-level left-column icons). submit_paper / attend_conference /
## send_delegation slipped through because they render inside the TRAVEL SUBMENU
## (main_ui.gd:_show_travel_submenu -> IconLoader.get_action_icon(travel_id)),
## NOT the top-level set. So this test now drives EVERY surface in main_ui.gd that
## calls IconLoader.get_action_icon():
##   * get_all_actions()          -> left-column icon stack (main_ui.gd ~1231)
##   * get_fundraising_options()  -> fundraising submenu   (main_ui.gd ~2079)
##   * get_publicity_options()    -> publicity submenu     (main_ui.gd ~2392)
##   * get_strategic_options()    -> strategic submenu     (main_ui.gd ~2590)
##   * get_travel_options()       -> travel submenu        (main_ui.gd ~2785)
##   * get_operations_options()   -> operations submenu    (main_ui.gd ~3621)
## (get_financing_options() is deliberately excluded: its submenu renders text-only
## buttons with no icon, so it is not an icon-rendering surface.)
##
## A placeholder is a runtime-built ImageTexture whose resource_path is empty.


func _fresh_state() -> Dictionary:
	# All top-level core actions have no unlock_conditions, so a minimal empty-ish
	# state unlocks the full set the player sees on turn 1.
	return {
		"turn": 0,
		"total_staff": 0,
		"reputation": 0,
		"papers": 0,
		"research": 0,
		"purchased_upgrades": [],
	}


func _icon_is_real(id: String) -> bool:
	# A real mapped icon loads from res://assets/... with a non-empty resource_path;
	# the placeholder is a code-built ImageTexture with no resource path.
	var tex: Texture2D = IconLoader.get_action_icon(id)
	var has_res_path := tex != null and tex.resource_path.begins_with("res://")
	return has_res_path and not IconLoader.is_placeholder(id)


func test_every_unlocked_action_resolves_to_real_icon() -> void:
	var state := _fresh_state()
	var actions := GameActions.get_all_actions()
	assert_gt(actions.size(), 0, "core action set must be non-empty")

	var placeholder_ids: Array[String] = []
	var checked := 0
	for action in actions:
		if not GameActions.is_action_unlocked(action, state):
			continue
		var id: String = action.get("id", "")
		if id == "" or id == GameActions.PASS_ACTION_ID:
			continue
		checked += 1
		if not _icon_is_real(id):
			placeholder_ids.append(id)

	if placeholder_ids.size() > 0:
		gut.p("[icon-regression] unmapped/placeholder action ids: " + str(placeholder_ids))
	assert_eq(placeholder_ids.size(), 0,
		"every unlocked action must have a real (non-placeholder) icon; missing: " + str(placeholder_ids))
	assert_gt(checked, 0, "expected at least one unlocked action to check")


func test_every_submenu_option_resolves_to_real_icon() -> void:
	# Each of these submenus renders an icon per option via IconLoader.get_action_icon()
	# (see main_ui.gd render sites in the header). Every option id -- regardless of
	# affordability or stub state, since the icon is drawn either way -- must resolve
	# to a real icon. This is the surface #768's three ids (submit_paper /
	# attend_conference / send_delegation) actually render through.
	var surfaces := {
		"fundraising": GameActions.get_fundraising_options(),
		"publicity": GameActions.get_publicity_options(),
		"strategic": GameActions.get_strategic_options(),
		"travel": GameActions.get_travel_options(),
		"operations": GameActions.get_operations_options(),
	}

	var placeholder_ids: Array[String] = []
	var checked := 0
	for surface_name in surfaces.keys():
		var options: Array = surfaces[surface_name]
		for option in options:
			var id: String = option.get("id", "")
			if id == "":
				continue
			checked += 1
			if not _icon_is_real(id):
				placeholder_ids.append("%s/%s" % [surface_name, id])

	if placeholder_ids.size() > 0:
		gut.p("[icon-regression] unmapped/placeholder submenu ids: " + str(placeholder_ids))
	assert_eq(placeholder_ids.size(), 0,
		"every submenu option must have a real (non-placeholder) icon; missing: " + str(placeholder_ids))
	assert_gt(checked, 0, "expected at least one submenu option to check")

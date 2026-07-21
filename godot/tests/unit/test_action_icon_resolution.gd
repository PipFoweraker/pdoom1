extends GutTest
## Regression guard (#762): every unlocked top-level action must resolve to a REAL
## icon, not the magenta-checkerboard placeholder.
##
## The July 2026 regression: most action-icon buttons rendered the placeholder
## because several top-level action ids in data/actions/core.json (operations,
## travel, financing, and the hiring pipeline advertise/use_connections/
## interview_next/hire_best/onboard_next) had no entry in data/icon_mapping.json.
## IconLoader.get_action_icon() falls back to the placeholder for unmapped ids.
##
## This test drives the SAME path the UI does: it takes the action set the main
## panel renders (GameActions.get_all_actions(), filtered by is_action_unlocked at
## a fresh state) and asserts each id resolves to a texture with a real res:// path.
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
		var tex: Texture2D = IconLoader.get_action_icon(id)
		# Placeholder is a code-built ImageTexture with no resource path; a real
		# mapped icon loads from res://assets/... with a non-empty resource_path.
		var is_real := tex != null and tex.resource_path.begins_with("res://")
		if not is_real or IconLoader.is_placeholder(id):
			placeholder_ids.append(id)

	if placeholder_ids.size() > 0:
		gut.p("[icon-regression] unmapped/placeholder action ids: " + str(placeholder_ids))
	assert_eq(placeholder_ids.size(), 0,
		"every unlocked action must have a real (non-placeholder) icon; missing: " + str(placeholder_ids))
	assert_gt(checked, 0, "expected at least one unlocked action to check")

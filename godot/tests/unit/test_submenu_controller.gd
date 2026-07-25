extends GutTest
## CARVE 2 (docs/MAIN_UI_SEAM_MAP.md, R5): characterization + regression lock for the submenu
## orchestration extracted out of main_ui.gd into SubmenuController.
##
## This is a NON-FORKING refactor: the WHAT -- which options each config-driven submenu lists,
## and their costs -- must stay byte-for-byte identical to the pre-carve builders, which each
## read the same GameActions static getter. These tests pin that the controller reads exactly
## that same source (so a fifth copy-paste can't silently diverge) and that the four grid
## submenus are covered by config, while hiring/travel stay bespoke.

const SubmenuControllerScript: GDScript = preload("res://scripts/ui/submenu_controller.gd")

# The four submenus the pre-carve view built with near-identical icon-grid code, now collapsed
# into GRID_CONFIG. Each maps to the GameActions getter its old builder called verbatim.
const GRID_IDS := ["fundraise", "publicity", "strategic", "operations"]


func _controller() -> SubmenuController:
	# host + plan_controller are not touched by _options_for / GRID_CONFIG reads; pass null.
	return SubmenuControllerScript.new(null, null)


func _getter_options(id: String) -> Array:
	# The static getter each pre-carve builder called verbatim. A class_name's static method
	# can't be invoked dynamically (Object.call is rejected on the class), so switch explicitly.
	match id:
		"fundraise":
			return GameActions.get_fundraising_options()
		"publicity":
			return GameActions.get_publicity_options()
		"strategic":
			return GameActions.get_strategic_options()
		"operations":
			return GameActions.get_operations_options()
	return []


# --- The config-driven submenus read the SAME option source as the pre-carve builders --------

func test_grid_config_covers_exactly_the_four_grid_submenus():
	var keys := SubmenuControllerScript.GRID_CONFIG.keys()
	keys.sort()
	var expected := GRID_IDS.duplicate()
	expected.sort()
	assert_eq(keys, expected, "GRID_CONFIG covers exactly the four collapsed grid submenus")


func test_options_for_matches_gameactions_getter_verbatim():
	# The strongest non-forking pin: the controller's option source IS the same static getter
	# each old builder called, so the listed options + costs cannot drift from the pre-carve view.
	var sc := _controller()
	for id in GRID_IDS:
		var via_controller: Array = sc._options_for(id)
		var via_getter: Array = _getter_options(id)
		assert_eq(via_controller.size(), via_getter.size(),
			"%s: controller lists the same number of options as the pre-carve getter" % id)
		for i in range(via_getter.size()):
			assert_eq(via_controller[i].get("id"), via_getter[i].get("id"),
				"%s option %d id preserved" % [id, i])
			assert_eq(via_controller[i].get("costs", {}), via_getter[i].get("costs", {}),
				"%s option %d costs preserved byte-for-byte" % [id, i])


func test_each_grid_submenu_lists_at_least_one_option_each_with_an_id():
	var sc := _controller()
	for id in GRID_IDS:
		var opts: Array = sc._options_for(id)
		assert_gt(opts.size(), 0, "%s submenu is non-empty" % id)
		for opt in opts:
			assert_true(opt.has("id") and opt.get("id") != "", "%s option carries an id" % id)


func test_log_labels_match_the_pre_carve_message_prefixes():
	# The only per-submenu difference in the (formerly 5 copy-pasted) option-selected handler was
	# the message-log prefix. Pin it so the queue-confirmation lines stay identical.
	var cfg := SubmenuControllerScript.GRID_CONFIG
	assert_eq(cfg["fundraise"]["log_label"], "Fundraising")
	assert_eq(cfg["publicity"]["log_label"], "Publicity")
	assert_eq(cfg["strategic"]["log_label"], "Strategic")
	assert_eq(cfg["operations"]["log_label"], "Operations")


func test_bespoke_submenus_are_not_in_grid_config():
	# hiring (candidate cards) and travel (paper/conference sections + sub-dialogs) do NOT
	# generalize into the grid; they must stay bespoke, delegated to via open().
	var cfg := SubmenuControllerScript.GRID_CONFIG
	assert_false(cfg.has("hire_staff"), "hiring stays bespoke, not a grid config entry")
	assert_false(cfg.has("travel"), "travel stays bespoke, not a grid config entry")
	assert_false(cfg.has("financing"), "financing is a bespoke LIST layout, not a grid config entry")


# --- The extraction removed the seven copy-pasted builders from the view --------------------

func test_main_ui_no_longer_declares_the_collapsed_builders():
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	for fn in [
		"func _show_fundraising_submenu",
		"func _show_publicity_submenu",
		"func _show_strategic_submenu",
		"func _show_operations_submenu",
		"func _show_financing_submenu",
		"func _on_fundraising_option_selected",
		"func _on_publicity_option_selected",
		"func _on_strategic_option_selected",
		"func _on_operations_option_selected",
		"func _on_financing_option_selected",
	]:
		assert_false(src.contains(fn),
			"%s moved into SubmenuController; the view must not re-declare it" % fn)


func test_main_ui_keeps_the_genuinely_bespoke_builders():
	# CARVE 3 moved the hiring candidate-card pipeline into HiringPanelController; CARVE 4 moved the
	# travel/conferences pipeline into TravelPanelController. The view keeps a one-line SHIM for each
	# (_show_hiring_submenu / _show_travel_submenu) so SubmenuController.open("hire_staff"/"travel")
	# is unchanged, but no longer declares the card builders or the paper/conference sub-dialogs.
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	assert_true(src.contains("func _show_hiring_submenu"), "hiring entry point (now a shim) stays in the view")
	assert_true(src.contains("func _show_travel_submenu"), "travel entry point (now a shim) stays in the view")
	assert_false(src.contains("func _build_candidate_card"), "candidate-card rendering moved to HiringPanelController (CARVE 3)")
	assert_false(src.contains("func _show_paper_submission_dialog"), "paper submission dialog moved to TravelPanelController (CARVE 4)")

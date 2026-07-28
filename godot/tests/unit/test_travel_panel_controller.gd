extends GutTest
## CARVE 4 (docs/MAIN_UI_SEAM_MAP.md, seams R1 + R5): characterization + regression lock for the
## travel/conferences submenu pipeline extracted out of main_ui.gd into TravelPanelController -- the
## last bespoke submenu (parallel to CARVE 3's hiring lift).
##
## NON-FORKING refactor: every function body is a VERBATIM move; only host-owned members/helpers were
## re-routed through `host.`. No gameplay/RNG/scoring change -- every travel action still routes through
## the SAME GameActions delegates and reads the SAME state payload. These tests pin (a) the extracted
## surface lives on the controller, (b) it left the view (only a shim remains), (c) the action routing
## through the GameActions delegates is byte-preserved, and (d) the travel option set is stable -- so the
## pure-view move cannot have forked behavior.

const CONTROLLER_PATH := "res://scripts/ui/travel_panel_controller.gd"

# The pipeline surface that moved out of the view. Every one must live on the controller now.
const PIPELINE_METHODS := [
	"open",
	"_show_travel_submenu",
	"_on_travel_option_selected",
	"_show_paper_submission_dialog",
	"_show_conference_attendance_dialog",
]


func _controller():
	# host is only dereferenced when a panel is actually opened; _init just stores it. A null host is
	# enough to exercise construction + method-surface characterization headlessly. (This is exactly
	# the construction path that caught the CARVE 3 defect.)
	return TravelPanelController.new(null)


func test_controller_is_a_refcounted_view_module_taking_a_host():
	var c = _controller()
	assert_not_null(c, "TravelPanelController constructs with a host reference")
	assert_true(c is RefCounted, "it is a RefCounted view module (same pattern as HiringPanelController)")


func test_controller_declares_the_whole_extracted_pipeline_surface():
	var c = _controller()
	for m in PIPELINE_METHODS:
		assert_true(c.has_method(m), "TravelPanelController owns %s (moved from the view)" % m)


func test_pipeline_left_the_view_but_the_entry_shim_stays():
	# The view must NOT re-declare the sub-dialog builders / option handler -- else the monolith
	# quietly kept a copy. It DOES keep a _show_travel_submenu() shim (so SubmenuController.open and
	# dev_mode_overlay reach the panel unchanged).
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	for fn in [
		"func _on_travel_option_selected",
		"func _show_paper_submission_dialog",
		"func _show_conference_attendance_dialog",
	]:
		assert_false(src.contains(fn), "%s moved into TravelPanelController; the view must not re-declare it" % fn)
	assert_true(src.contains("func _show_travel_submenu"), "the view keeps a _show_travel_submenu() entry shim")
	assert_true(src.contains("travel_panel.open()"), "the shim delegates to the controller")


func test_non_forking_action_routing_preserved_verbatim():
	# The strongest non-forking pin: every travel action still calls the SAME GameActions delegate it
	# did pre-carve. If any of these string through a different path, the pure-view move forked.
	var src: String = FileAccess.get_file_as_string(CONTROLLER_PATH)
	for delegate in [
		"GameActions.get_travel_options()",
		"GameActions.submit_paper_to_conference(host.game_manager.state, conf_id, topic, research_amount, lead)",
		"GameActions.attend_conference_action(host.game_manager.state, conf_id, \"economy\", traveler)",
	]:
		assert_true(src.contains(delegate), "travel action routes through %s (unchanged from the view)" % delegate)


func test_travel_option_set_and_costs_are_pinned():
	# Characterization of the option set the panel lists (GameActions.get_travel_options). Pins the
	# ids + costs so a later data edit that would silently change what the travel submenu offers is
	# caught. This is the behavior the pure-view carve must not have touched.
	var options: Array = GameActions.get_travel_options()
	assert_true(options.size() >= 3, "travel offers at least the 3 core options (submit / attend / delegation)")

	var by_id := {}
	for opt in options:
		by_id[String(opt.get("id", ""))] = opt

	for expected_id in ["submit_paper", "attend_conference", "send_delegation"]:
		assert_true(by_id.has(expected_id), "travel option '%s' is present" % expected_id)

	# submit_paper: the paper-submission entry, 1 AP (matches the "Submit Paper (1 AP)" sub-dialog button).
	var submit: Dictionary = by_id["submit_paper"]
	assert_eq(int(submit.get("costs", {}).get("attention", -1)), 1, "submit_paper costs 1 Attention")

	# attend_conference: the attendance entry, 2 AP (matches the "Attend (2 AP)" sub-dialog button).
	var attend: Dictionary = by_id["attend_conference"]
	assert_eq(int(attend.get("costs", {}).get("attention", -1)), 2, "attend_conference costs 2 Attention")

	# send_delegation is still the not-yet-built stub (Issue #411) -- the panel greys it out.
	var deleg: Dictionary = by_id["send_delegation"]
	assert_true(bool(deleg.get("is_stub", false)), "send_delegation is still a stub (greyed out in the panel)")

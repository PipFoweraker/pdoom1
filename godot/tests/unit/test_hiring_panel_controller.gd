extends GutTest
## CARVE 3 (docs/MAIN_UI_SEAM_MAP.md, seams R1 + R5): characterization + regression lock for the
## hiring candidate-card pipeline extracted out of main_ui.gd into HiringPanelController.
##
## NON-FORKING refactor: every function body is a VERBATIM move; only host-owned members/helpers
## were re-routed through `host.`. No gameplay/RNG/scoring change -- every hiring action still routes
## through the SAME GameManager.hiring_* delegates. These tests pin (a) the extracted surface lives
## on the controller, (b) it left the view (only a shim remains), and (c) the action routing through
## the GameManager delegates is byte-preserved, so the pure-view move cannot have forked behavior.

# Instantiated via the global class name (registered because main_ui constructs it the same way);
# source-text pins below read the file directly via FileAccess.
const CONTROLLER_PATH := "res://scripts/ui/hiring_panel_controller.gd"

# The pipeline surface that moved out of the view. Every one must live on the controller now.
const PIPELINE_METHODS := [
	"open",
	"_show_hiring_submenu",
	"_build_candidate_card",
	"_build_onboarding_card",
	"_has_hiring_job",
	"_hiring_job_status",
	"_hiring_action_result",
	"_on_hiring_advertise_pressed",
	"_on_hiring_connections_pressed",
	"_on_hiring_interview_pressed",
	"_on_hiring_onboard_pressed",
	"_on_hiring_skip_mentoring_pressed",
	"_show_offer_dialog",
	"_selected_promises",
	"_on_offer_promise_toggled",
	"_on_hiring_send_offer_pressed",
	"update_inflight_display",
]


func _controller():
	# host is only dereferenced when a panel is actually opened; _init just stores it. A null host
	# is enough to exercise construction + method-surface characterization headlessly.
	return HiringPanelController.new(null)


func test_controller_is_a_refcounted_view_module_taking_a_host():
	var c = _controller()
	assert_not_null(c, "HiringPanelController constructs with a host reference")
	assert_true(c is RefCounted, "it is a RefCounted view module (same pattern as SubmenuController)")


func test_controller_declares_the_whole_extracted_pipeline_surface():
	var c = _controller()
	for m in PIPELINE_METHODS:
		assert_true(c.has_method(m), "HiringPanelController owns %s (moved from the view)" % m)


func test_pipeline_left_the_view_but_the_entry_shim_stays():
	# The view must NOT re-declare the card builders / offer dialog / handlers -- else the monolith
	# quietly kept a copy. It DOES keep a _show_hiring_submenu() shim (so SubmenuController.open and
	# the offer-dialog Back button reach the panel unchanged) and the update_inflight_display() call.
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	for fn in [
		"func _build_candidate_card",
		"func _build_onboarding_card",
		"func _show_offer_dialog",
		"func _hiring_action_result",
		"func _on_hiring_advertise_pressed",
		"func _on_offer_promise_toggled",
		"func _update_inflight_hiring_display",
	]:
		assert_false(src.contains(fn), "%s moved into HiringPanelController; the view must not re-declare it" % fn)
	assert_true(src.contains("func _show_hiring_submenu"), "the view keeps a _show_hiring_submenu() entry shim")
	assert_true(src.contains("hiring_panel.open()"), "the shim delegates to the controller")
	assert_true(src.contains("hiring_panel.update_inflight_display(state)"), "HUD refresh routes to the controller")


func test_non_forking_action_routing_preserved_verbatim():
	# The strongest non-forking pin: every hiring action still calls the SAME GameManager delegate it
	# did pre-carve. If any of these string through a different path, the pure-view move forked.
	var src: String = FileAccess.get_file_as_string(CONTROLLER_PATH)
	for delegate in [
		"host.game_manager.hiring_advertise()",
		"host.game_manager.hiring_use_connections()",
		"host.game_manager.hiring_interview(candidate_id)",
		"host.game_manager.hiring_onboard_step(candidate_id, item)",
		"host.game_manager.hiring_offer(candidate_id, cash_spin.value, promises)",
		"host.game_manager.hiring_read(candidate_id",
	]:
		assert_true(src.contains(delegate), "hiring action routes through %s (unchanged from the view)" % delegate)

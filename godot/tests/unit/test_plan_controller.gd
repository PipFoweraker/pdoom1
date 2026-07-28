extends GutTest
## CARVE 1 (docs/MAIN_UI_SEAM_MAP.md, R4): characterization + regression lock for the
## plan/queue/cost logic extracted out of main_ui.gd into PlanController.
##
## The cost-aggregation contract (was main_ui._calculate_queued_costs) is a NON-FORKING
## refactor target: these tests pin the CURRENT behaviour so the extraction cannot drift it.
## Behaviour under test, verbatim from the pre-carve code:
##   - sum every cost resource across the queued actions,
##   - EXCEPT "attention" / "hour_type" (Attention is tracked on the month plan), which is skipped,
##   - an unknown action id resolves to {} costs and contributes nothing,
##   - an empty queue yields {}.

const MainUIScript: GDScript = preload("res://scripts/ui/main_ui.gd")
const PlanControllerScript: GDScript = preload("res://scripts/ui/plan_controller.gd")


func _controller(queue: Array) -> PlanController:
	# game_manager is not needed for the pure cost path; pass null.
	var pc: PlanController = PlanControllerScript.new(null)
	pc.queued_actions = queue
	return pc


# --- Cost aggregation contract (PlanController.calculate_queued_costs) --------------------

func test_money_costs_sum_and_ap_is_skipped():
	# buy_compute {money:50000}; team_building {money:10000, attention:1}
	var costs: Dictionary = _controller([
		{"id": "buy_compute", "name": "Buy Compute"},
		{"id": "team_building", "name": "Team Building"},
	]).calculate_queued_costs()
	assert_eq(costs.get("money", 0), 60000, "money costs sum across queued actions")
	assert_false(costs.has("attention"), "attention is tracked on the month plan, never summed here")


func test_non_money_resource_costs_sum():
	# safety_research {research:10, ap:1}; publish_paper {research:20, ap:1}
	var costs: Dictionary = _controller([
		{"id": "safety_research", "name": "Safety Research"},
		{"id": "publish_paper", "name": "Publish Paper"},
	]).calculate_queued_costs()
	assert_eq(costs.get("research", 0), 30, "research costs aggregate")
	assert_false(costs.has("attention"), "Attention still skipped for research-costing actions")


func test_reputation_cost_surfaces():
	# fundraise_small {attention:1, reputation:2}
	var costs: Dictionary = _controller([
		{"id": "fundraise_small", "name": "Small Fundraise"},
	]).calculate_queued_costs()
	assert_eq(costs.get("reputation", 0), 2, "reputation cost is a real projected cost")
	assert_eq(costs.size(), 1, "only reputation remains once AP is skipped")


func test_unknown_action_contributes_nothing():
	var costs: Dictionary = _controller([
		{"id": "does_not_exist", "name": "Phantom"},
	]).calculate_queued_costs()
	assert_eq(costs.size(), 0, "an unknown id resolves to empty costs and adds nothing")


func test_empty_queue_is_empty_costs():
	assert_eq(_controller([]).calculate_queued_costs().size(), 0, "no queued actions -> no costs")


func test_ap_only_action_yields_empty_costs():
	# take_loan {attention:1} -- the only cost is Attention, which is skipped.
	var costs: Dictionary = _controller([
		{"id": "take_loan", "name": "Take Loan"},
	]).calculate_queued_costs()
	assert_eq(costs.size(), 0, "an AP-only action projects no non-Attention cost")


# --- The extraction preserves the view-facing algorithm ----------------------------------
# main_ui must NOT keep its own copy of the cost math; it delegates to the controller.
# (Guards against a re-introduced _calculate_queued_costs drifting from the controller.)

func test_main_ui_no_longer_declares_its_own_cost_calc():
	var src: String = FileAccess.get_file_as_string("res://scripts/ui/main_ui.gd")
	assert_false(src.contains("func _calculate_queued_costs"),
		"cost logic lives in PlanController now, not as a private method on the view")

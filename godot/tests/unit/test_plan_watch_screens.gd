extends GutTest
## Locks the PlanScreen/WatchScreen extraction contract (BUILD_BRIEF_PLAN_WATCH_UI Lane 1):
## the two screens are real standalone scenes that own + expose their panels, so main_ui can
## drive game logic against those public members instead of absolute $ContentArea/... paths.
## Instantiated standalone (no GameManager autoload dependency in their _ready) so the guard
## stays fast and deterministic.

const PLAN_SCENE := "res://scenes/ui/plan_screen.tscn"
const WATCH_SCENE := "res://scenes/ui/watch_screen.tscn"


func _instance(path: String) -> Node:
	var scene: PackedScene = load(path)
	assert_not_null(scene, "scene %s should load" % path)
	var node: Node = scene.instantiate()
	add_child_autofree(node)
	return node


func test_plan_screen_owns_its_panels():
	var plan = _instance(PLAN_SCENE)
	await get_tree().process_frame
	assert_is(plan, PlanScreen, "plan_screen.tscn root is a PlanScreen")
	assert_not_null(plan.actions_list, "PlanScreen exposes the action hand list")
	assert_not_null(plan.upgrades_list, "PlanScreen exposes the upgrades list")
	assert_not_null(plan.getting_started_hint, "PlanScreen exposes the getting-started hint")
	assert_not_null(plan.command_zone, "PlanScreen exposes the command (pass) zone")


func test_watch_screen_owns_the_feed():
	var watch = _instance(WATCH_SCENE)
	await get_tree().process_frame
	assert_is(watch, WatchScreen, "watch_screen.tscn root is a WatchScreen")
	assert_not_null(watch.message_log, "WatchScreen exposes the feed / message log")


func test_reserve_gauge_degrades_without_plan_data():
	# The optional plan-screen payoff must be crash-safe when no month plan is present.
	var plan = _instance(PLAN_SCENE)
	await get_tree().process_frame
	plan.update_reserve_gauge({})  # no "month_plan" key
	plan.update_reserve_gauge({"month_plan": {"attention_total": 0}})
	pass_test("update_reserve_gauge tolerates missing / empty plan data")


func test_reserve_gauge_renders_with_plan_data():
	var plan = _instance(PLAN_SCENE)
	await get_tree().process_frame
	# ADR-0011 shape: ~20 attention/month, some allocated, some reserved.
	plan.update_reserve_gauge({"month_plan": {
		"attention_total": 20, "attention_spent": 6, "attention_reserved": 4,
	}})
	pass_test("update_reserve_gauge renders allocated/reserved pips without error")

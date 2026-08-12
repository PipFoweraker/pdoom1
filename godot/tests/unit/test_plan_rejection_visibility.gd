extends GutTest
## Locks the PLAN-time rejection surface: an action the player CANNOT afford must produce
## something the player can actually see.
##
## The defect this pins (fix/plan-phase-messages-reach-the-player): log_message() writes into
## watch_screen.message_log, and ScreenModeController registers WatchScreen as watch-only and
## sets visible = false on it for the whole of PLAN. The game opens in PLAN and stays there
## until COMMIT THE MONTH, so a rejection reported with a bare log_message() went into a hidden
## node -- an unaffordable click looked like a dead button.
##
## EventResultPresenter.present_error() already writes BOTH the feed line and PlanScreen's
## toast, and its header names "Not enough Attention" / "Cannot afford ..." as the case it
## fixed. But the view's own affordability pre-checks returned BEFORE GameManager could emit
## error_occurred, so that fix never fired for the clicks that trigger it most. The view now
## reports those refusals through MainUI.report_rejection() -> present_error().
##
## Presentation only: these tests assert on the FEEDBACK, never on queue/attention state.

const PLAN_SCENE := "res://scenes/ui/plan_screen.tscn"
const MAIN_UI_SRC := "res://scripts/ui/main_ui.gd"
const SUBMENU_SRC := "res://scripts/ui/submenu_controller.gd"


class StubHost extends RefCounted:
	## Minimal stand-in for MainUI: EventResultPresenter takes an untyped host and only needs
	## log_message() + plan_screen, so the presenter can be exercised without booting the
	## 3k-line view or a GameManager.
	var logged: Array = []
	var plan_screen: Node = null

	func log_message(text: String, channel: String = "normal") -> void:
		logged.append({"text": text, "channel": channel})


func _plan_screen() -> PlanScreen:
	var scene: PackedScene = load(PLAN_SCENE)
	assert_not_null(scene, "plan_screen.tscn should load")
	var node: PlanScreen = scene.instantiate()
	add_child_autofree(node)
	return node


func _find_error_toast(plan: Node) -> Label:
	for child in plan.get_children():
		if child is Label and child.name == "PlanErrorToast":
			return child
	return null


# --- The PLAN surface itself ----------------------------------------------------------------

func test_plan_screen_exposes_the_error_toast_surface():
	# The whole fix depends on this method existing on the PLAN screen; pin it so a later
	# refactor of PlanScreen cannot quietly remove the only PLAN-visible rejection surface.
	var plan := _plan_screen()
	await get_tree().process_frame
	assert_true(plan.has_method("flash_error"), "PlanScreen exposes flash_error()")


func test_flash_error_makes_a_visible_plain_text_toast():
	var plan := _plan_screen()
	await get_tree().process_frame
	var toast := _find_error_toast(plan)
	assert_not_null(toast, "PlanScreen builds a PlanErrorToast label")
	assert_false(toast.visible, "the toast starts hidden")

	plan.flash_error("Cannot afford action: Hire Researcher")
	assert_true(toast.visible, "flash_error shows the toast on the PLAN screen")
	assert_true(toast.text.contains("Cannot afford action: Hire Researcher"),
		"the toast carries the rejection text, got: %s" % toast.text)
	assert_true(toast.text.begins_with("[!]"), "house-style ASCII chrome, got: %s" % toast.text)


func test_flash_error_ignores_an_empty_message():
	var plan := _plan_screen()
	await get_tree().process_frame
	var toast := _find_error_toast(plan)
	plan.flash_error("")
	assert_false(toast.visible, "an empty rejection does not raise an empty toast")


# --- The one presentation door -----------------------------------------------------------

func test_present_error_reaches_both_the_feed_and_the_plan_toast():
	# present_error is the door BOTH the backend (error_occurred) and the view's own
	# pre-checks now use, so a rejection is recorded in the feed AND surfaced where the
	# player is acting.
	var plan := _plan_screen()
	await get_tree().process_frame
	var host := StubHost.new()
	host.plan_screen = plan
	var presenter := EventResultPresenter.new(host)

	presenter.present_error("Not enough Attention: need 2 operating hours, have 1")

	assert_eq(host.logged.size(), 1, "the rejection is recorded in the feed model")
	assert_true(String(host.logged[0]["text"]).contains("Not enough Attention: need 2 operating hours, have 1"),
		"the feed line carries the message")
	var toast := _find_error_toast(plan)
	assert_true(toast.visible, "the same call raises the PLAN toast the player can see")
	assert_true(toast.text.contains("Not enough Attention: need 2 operating hours, have 1"),
		"the toast carries the message, got: %s" % toast.text)


func test_present_error_survives_a_missing_plan_screen():
	# A rejection raised before/without a PLAN screen must still reach the feed, not crash.
	var host := StubHost.new()
	host.plan_screen = null
	var presenter := EventResultPresenter.new(host)
	presenter.present_error("Cannot afford action: Buy Compute")
	assert_eq(host.logged.size(), 1, "the feed line is written even with no PLAN screen")


# --- The call sites: no PLAN-time rejection may go out through log_message alone -------------

func test_main_ui_declares_report_rejection():
	var src: String = FileAccess.get_file_as_string(MAIN_UI_SRC)
	assert_true(src.contains("func report_rejection"),
		"MainUI keeps the single rejection door the view + SubmenuController report through")


func test_affordability_rejections_route_through_report_rejection():
	# The two sharpest cases: _on_dynamic_action_pressed's own pre-check, which returns before
	# GameManager can emit error_occurred. These MUST NOT go back to a bare log_message().
	var src: String = FileAccess.get_file_as_string(MAIN_UI_SRC)
	assert_true(src.contains("report_rejection(\"Not enough Attention: need %d %s hours, have %d\""),
		"the Attention rejection reports through report_rejection")
	assert_true(src.contains("report_rejection(\"Cannot afford action: %s\" % action_name)"),
		"the affordability rejection reports through report_rejection")
	assert_false(src.contains("log_message(\"[color=red]Cannot afford action:"),
		"the affordability rejection no longer writes only into the PLAN-hidden feed")
	assert_false(src.contains("log_message(\"[color=red]Not enough Attention:"),
		"no Attention rejection writes only into the PLAN-hidden feed")


func test_pass_button_rejections_route_through_report_rejection():
	# The Do Nothing button lives in PlanScreen's command zone, so its refusals are PLAN-time too.
	var src: String = FileAccess.get_file_as_string(MAIN_UI_SRC)
	assert_true(src.contains("report_rejection(\"Cannot pass - not in action selection phase\")"),
		"the wrong-phase pass refusal reports through report_rejection")
	assert_false(src.contains("log_message(\"[color=red]Cannot pass"),
		"the wrong-phase pass refusal is not feed-only")


func test_submenu_rejections_route_through_report_rejection():
	# Submenus are opened from PLAN, so their two refusals are the same defect class.
	var src: String = FileAccess.get_file_as_string(SUBMENU_SRC)
	assert_true(src.contains("host.report_rejection(\"Not enough Attention: need %d %s hours, have %d\""),
		"the submenu Attention rejection reports through the host's rejection door")
	assert_true(src.contains("host.report_rejection(\"Cannot afford: %s\" % action_name)"),
		"the submenu affordability rejection reports through the host's rejection door")
	assert_false(src.contains("log_message(\"[color=red]"),
		"SubmenuController raises no PLAN-time rejection into the hidden feed alone")


func test_report_rejection_messages_are_plain_text():
	# present_error applies the feed colour itself and the PLAN toast is a plain Label, so a
	# BBCode tag passed in here would be printed literally to the player as "[color=red]...".
	for path in [MAIN_UI_SRC, SUBMENU_SRC]:
		var src: String = FileAccess.get_file_as_string(path)
		for line in src.split("\n"):
			if not String(line).contains("report_rejection(\""):
				continue
			assert_false(String(line).contains("[color="),
				"%s: report_rejection takes plain text, not BBCode -- %s" % [path, line.strip_edges()])

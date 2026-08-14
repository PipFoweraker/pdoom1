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
##
## SECOND PASS (fix/submenu-rejection-visibility). #1204 fixed the DIRECT-click path and gave
## SubmenuController.on_option_selected the same two guards, which covers the six icon-grid
## panels plus financing. It did not cover the SUBMENU-DRIVEN path as a whole:
## _on_dynamic_action_pressed returns at its `is_submenu` branch ABOVE those guards, and the two
## BESPOKE panels (hiring, travel) never queue through on_option_selected -- they call the
## GameManager.hiring_* / GameActions conference delegates directly and presented the backend's
## refusal with a bare log_message(), i.e. straight back into the PLAN-hidden feed.
##
## Playtest repro, verbatim: "I can fail silently if I queue 19 fundraisings and then try to make
## offers to 2 people. Making offers doesn't show up as a card."
##
## The guards must NOT move above the `is_submenu` return: opening a menu is free, the CHILD
## inside it carries the cost, so guarding the driver would refuse to open a menu the player is
## entitled to browse. The refusal belongs at child selection -- at the chokepoint each panel
## family already funnels through.

const PLAN_SCENE := "res://scenes/ui/plan_screen.tscn"
const MAIN_UI_SRC := "res://scripts/ui/main_ui.gd"
const SUBMENU_SRC := "res://scripts/ui/submenu_controller.gd"
const HIRING_SRC := "res://scripts/ui/hiring_panel_controller.gd"
const TRAVEL_SRC := "res://scripts/ui/travel_panel_controller.gd"

# Every child-click handler in the hiring panel. All six must reach the ONE chokepoint, which is
# why the refusal surface is fixed in one place rather than six.
const HIRING_CHILD_CLICK_HANDLERS := [
	"_on_hiring_advertise_pressed",
	"_on_hiring_connections_pressed",
	"_on_hiring_interview_pressed",
	"_on_hiring_onboard_pressed",
	"_on_hiring_skip_mentoring_pressed",
	"_on_hiring_send_offer_pressed",
]


class StubHost extends RefCounted:
	## Minimal stand-in for MainUI: EventResultPresenter takes an untyped host and only needs
	## log_message() + plan_screen, so the presenter can be exercised without booting the
	## 3k-line view or a GameManager.
	var logged: Array = []
	var plan_screen: Node = null

	func log_message(text: String, channel: String = "normal") -> void:
		logged.append({"text": text, "channel": channel})


class StubGameManager extends RefCounted:
	## The bespoke panels touch game_manager only for the post-action HUD refresh and the panel
	## rebuild. A null `state` makes _show_hiring_submenu() return at its own first guard, so the
	## chokepoint can be exercised without booting a run.
	var state = null

	func get_game_state() -> Dictionary:
		return {}


class StubPanelHost extends StubHost:
	## Stand-in for MainUI as the BESPOKE panels see it: the feed, the rejection door, the
	## backend-result door, and the two dialog slots. Records which surface each refusal reached,
	## so a test can tell "the player was told" from "it went into the hidden feed".
	var rejections: Array = []
	var outcomes: Array = []
	var game_manager = StubGameManager.new()
	var active_dialog = null
	var active_dialog_buttons: Array = []

	func report_rejection(message: String) -> void:
		rejections.append(message)

	func report_outcome(result: Dictionary, verb: String) -> bool:
		outcomes.append({"result": result, "verb": verb})
		var ok := bool(result.get("success", false))
		if not ok:
			rejections.append(String(result.get("message", "")))
		return ok

	func _on_game_state_updated(_state) -> void:
		pass

	func feed_lines_containing(needle: String) -> Array:
		var hits: Array = []
		for entry in logged:
			if String(entry["text"]).contains(needle):
				hits.append(entry["text"])
		return hits


func _function_body(src: String, func_name: String) -> String:
	"""Source of one top-level function, from its `func` line to the next one."""
	var at: int = src.find("func %s" % func_name)
	if at < 0:
		return ""
	var nxt: int = src.find("\nfunc ", at + 1)
	return src.substr(at, (nxt - at) if nxt > at else -1)


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
	for path in [MAIN_UI_SRC, SUBMENU_SRC, HIRING_SRC, TRAVEL_SRC]:
		var src: String = FileAccess.get_file_as_string(path)
		for line in src.split("\n"):
			if not String(line).contains("report_rejection(\""):
				continue
			assert_false(String(line).contains("[color="),
				"%s: report_rejection takes plain text, not BBCode -- %s" % [path, line.strip_edges()])


# --- The SUBMENU-DRIVEN child paths (fix/submenu-rejection-visibility) ----------------------
#
# What #1204 left uncovered. Four panel families hang off the `is_submenu` early return:
#   1. the six icon-grid panels  -> SubmenuController.on_option_selected   (COVERED by #1204)
#   2. financing (list layout)   -> SubmenuController.on_option_selected   (COVERED by #1204)
#   3. hiring (6 child clicks)   -> HiringPanelController._hiring_action_result
#   4. travel (4 child clicks)   -> TravelPanelController leaf commits
# 3 and 4 presented the backend's refusal with a bare log_message(). These pin the fix at the
# chokepoints, not at the eleven individual buttons.


func test_the_submenu_branch_still_returns_above_the_affordability_guards():
	# Pins the SHAPE of the defect, so the fix cannot be "undone" by hoisting the guards. The
	# submenu DRIVER is free; the CHILD inside the menu carries the cost. Guarding the driver
	# would refuse to OPEN a menu the player is entitled to browse -- a worse bug than the one
	# being fixed. The early return must stay exactly where it is.
	var src: String = FileAccess.get_file_as_string(MAIN_UI_SRC)
	var branch: int = src.find("if action.get(\"is_submenu\", false):")
	var guard: int = src.find("report_rejection(\"Not enough Attention: need %d %s hours, have %d\"")
	assert_true(branch > -1, "the submenu branch is still the first thing the click handler does")
	assert_true(guard > -1, "the Attention guard is still there")
	assert_true(branch < guard,
		"opening a submenu still returns BEFORE the cost guards -- browsing a menu stays free")


func test_a_refused_hiring_child_click_reaches_the_player_not_the_hidden_feed():
	# THE REPRO, at the chokepoint it flows through. Playtest, in the player's own words:
	# "I can fail silently if I queue 19 fundraisings and then try to make offers to 2 people.
	# Making offers doesn't show up as a card."
	# 19 fundraisings exhaust the month plan, so MonthPlan.spend_attention(1) refuses the offer
	# and HiringPipeline hands back {success: false, message: "Not enough Attention ..."}. Every
	# hiring child click lands in _hiring_action_result, which used to render that with a bare
	# log_message() -- into WatchScreen's feed, which ScreenModeController hides for all of PLAN.
	var host := StubPanelHost.new()
	var panel := HiringPanelController.new(host)

	panel._hiring_action_result(
		{"success": false, "message": "Not enough Attention to make an offer (1 needed)"}, "Offer")

	assert_eq(host.rejections.size(), 1,
		"the refused offer is reported through the PLAN-visible door, not swallowed")
	assert_true(String(host.rejections[0]).contains("Not enough Attention"),
		"the message says WHY it was refused, got: %s" % [host.rejections])
	assert_true(String(host.rejections[0]).contains("1 needed"),
		"and names the shortfall, got: %s" % [host.rejections])
	# NOTE the wrapping array: `"%s" % some_array` spreads the array as the argument LIST, so an
	# empty one raises "not enough arguments for format string" -- on the passing path.
	assert_eq(host.feed_lines_containing("Not enough Attention").size(), 0,
		"the panel no longer writes the refusal straight into the PLAN-hidden feed: %s"
			% [host.feed_lines_containing("Not enough Attention")])


func test_an_accepted_hiring_child_click_still_confirms_through_the_same_door():
	# The other half of "same conditions, same early returns": an accepted action must still
	# confirm, and must NOT be reported as a rejection.
	var host := StubPanelHost.new()
	var panel := HiringPanelController.new(host)

	panel._hiring_action_result({"success": true, "message": "Interview scheduled with Ada."}, "Interview")

	assert_eq(host.rejections.size(), 0, "an accepted action raises no rejection")
	assert_eq(host.outcomes.size(), 1, "the acceptance goes out the same one door")
	assert_true(bool(host.outcomes[0]["result"].get("success", false)),
		"the door is handed the backend's verdict verbatim")


func test_hiring_refusals_are_fixed_at_one_chokepoint_not_six_buttons():
	# A fix applied in six places rots in five. All six hiring child-click handlers must keep
	# funnelling through _hiring_action_result, and that one function must be what reports.
	var src: String = FileAccess.get_file_as_string(HIRING_SRC)
	for handler in HIRING_CHILD_CLICK_HANDLERS:
		var body: String = _function_body(src, handler)
		assert_ne(body, "", "%s exists" % handler)
		assert_true(body.contains("_hiring_action_result("),
			"%s reports through the single chokepoint, not its own presentation" % handler)
	assert_true(_function_body(src, "_hiring_action_result").contains("host.report_outcome("),
		"the chokepoint routes the backend verdict through the host's one result door")


func test_travel_child_clicks_report_through_the_same_one_door():
	# Travel's leaves each call a different GameActions delegate, so they cannot share a
	# chokepoint of their own -- they share the HOST's door instead, so the decision about what
	# a refusal looks like still lives in exactly one place.
	var src: String = FileAccess.get_file_as_string(TRAVEL_SRC)
	assert_true(src.contains("host.report_outcome("),
		"travel's backend results go out the same door as hiring's")
	assert_false(src.contains("log_message(\"[color=red]%s[/color]\" % result.get(\"message\", \"Failed to attend\"))"),
		"the failed-conference refusal is no longer feed-only")
	assert_false(src.contains("host.log_message(\"[color=cyan]%s[/color]\" % result.get(\"message\", \"Paper submitted\"))"),
		"a refused paper submission no longer reports itself as a cyan success line")


func test_a_travel_click_that_cannot_do_anything_says_so():
	# The delegation option is a stub: clicking it can never queue anything. That is the same
	# silent-failure class -- during PLAN its "coming soon" line went into the hidden feed, so
	# the button read as broken rather than unimplemented.
	var host := StubPanelHost.new()
	var panel := TravelPanelController.new(host)
	var dialog := Control.new()   # orphan on purpose: the handler queue_free()s it

	panel._on_travel_option_selected("send_delegation", "Send Delegation", dialog)

	assert_eq(host.rejections.size(), 1,
		"a click that cannot land is refused where the player can see it")
	assert_true(String(host.rejections[0]).contains("411"),
		"the refusal still carries the tracking issue, got: %s" % [host.rejections])


# --- The one backend-result door -------------------------------------------------------------


func test_present_outcome_is_the_one_door_for_a_backend_verdict():
	var plan := _plan_screen()
	await get_tree().process_frame
	var host := StubHost.new()
	host.plan_screen = plan
	# Deliberately untyped: while the door is missing this must fail as an ASSERTION, not as a
	# parse error that would take the whole file (and its RED evidence) down with it.
	var presenter = EventResultPresenter.new(host)
	assert_true(presenter.has_method("present_outcome"),
		"EventResultPresenter owns the one backend-result door")
	if not presenter.has_method("present_outcome"):
		return

	var accepted: bool = presenter.present_outcome(
		{"success": false, "message": "Not enough Attention to interview (2 needed)"}, "Interview")

	assert_false(accepted,
		"a refusal reports false so the call site can skip its follow-up -- no phantom tile (#821)")
	var toast := _find_error_toast(plan)
	assert_true(toast.visible, "the refusal is raised on the PLAN screen, where the player clicked")
	assert_true(toast.text.contains("Not enough Attention to interview (2 needed)"),
		"the toast says WHY, got: %s" % toast.text)
	assert_eq(host.logged.size(), 1, "and it is recorded in the feed exactly once")


func test_present_outcome_confirms_an_acceptance_without_raising_a_rejection():
	var plan := _plan_screen()
	await get_tree().process_frame
	var host := StubHost.new()
	host.plan_screen = plan
	var presenter = EventResultPresenter.new(host)
	if not presenter.has_method("present_outcome"):
		assert_true(false, "EventResultPresenter owns the one backend-result door")
		return

	var accepted: bool = presenter.present_outcome({"success": true, "message": "Offer sent to Ada."}, "Offer")

	assert_true(accepted, "an accepted result reports true")
	assert_eq(host.logged.size(), 1, "the acceptance is one plain feed line")
	assert_true(String(host.logged[0]["text"]).contains("Offer sent to Ada."),
		"carrying the backend's own wording, got: %s" % host.logged[0]["text"])
	assert_false(_find_error_toast(plan).visible, "an acceptance raises no PLAN error toast")


func test_present_outcome_never_refuses_in_silence():
	# A backend that refuses with no message must still produce something the player can see:
	# a blank toast is the same dead button by another route.
	var plan := _plan_screen()
	await get_tree().process_frame
	var host := StubHost.new()
	host.plan_screen = plan
	var presenter = EventResultPresenter.new(host)
	if not presenter.has_method("present_outcome"):
		assert_true(false, "EventResultPresenter owns the one backend-result door")
		return

	presenter.present_outcome({"success": false}, "Offer")

	var toast := _find_error_toast(plan)
	assert_true(toast.visible, "a message-less refusal still raises the toast")
	assert_true(toast.text.contains("Offer"), "and names what was refused, got: %s" % toast.text)


func test_main_ui_exposes_the_outcome_door_the_bespoke_panels_report_through():
	var src: String = FileAccess.get_file_as_string(MAIN_UI_SRC)
	assert_true(src.contains("func report_outcome"),
		"MainUI keeps the backend-result door next to report_rejection")


# --- The economy is untouched: the backend still refuses on exactly the same condition -------


func test_the_cumulative_queue_is_what_refuses_the_offer_not_the_offers_own_cost():
	# The actual repro is a CUMULATIVE overbook: one offer costs 1 Attention and the player can
	# afford one offer in isolation -- it is the 19 already-queued fundraisings that leave no
	# Attention behind them. MonthPlan.available() nets out what is already committed, so the
	# refusal is real and belongs to the backend. This test exists so the presentation fix can
	# never be "corrected" into a view-side pre-check that re-derives the rule and drifts.
	var plan := MonthPlan.new()
	plan.begin_month(3, 1)

	assert_true(plan.can_queue(1), "with the month untouched, a 1-Attention offer fits")
	assert_true(plan.spend_attention(3), "the player commits the whole month elsewhere")
	assert_eq(plan.available(), 0, "nothing is left behind the committed plan")
	assert_false(plan.can_queue(1), "so the 1-Attention offer no longer fits -- cumulatively")
	assert_false(plan.spend_attention(1), "and the spend is refused, charging nothing")
	assert_eq(plan.available(), 0, "a refused spend leaves the plan exactly as it was")

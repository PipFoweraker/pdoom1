extends GutTest
## Two related month-playback window fixes (playtest 2026-07-24), both about keeping
## window_queue in sync with the event_dialog (which presents queued windows one at a time
## and advances on EVERY press):
##
## 1. Routing-by-id: choosing an option resolves against the window the dialog PRESENTED
##    (matched by id via `event`), not blindly window_queue[0]. A window left queued would
##    otherwise desync the head from the dialog -> bogus "Unknown option: <id>".
##
## 2. Unaffordable HANDLE handling. Direction-b (playtest 2026-07-24): the event_dialog now
##    stays OPEN on a failed press and surfaces the reason, so the INTERACTIVE default
##    (allow_auto_lapse=false) returns a plain FAILURE and leaves the window QUEUED -- the open
##    dialog keeps it answerable (retry / free out). The 5af981c3 auto-lapse-to-IGNORE survives
##    as an explicit BACKSTOP (allow_auto_lapse=true) for any non-interactive forced-drain with
##    no dialog to keep the window answerable. EXCEPTION preserved on both paths: the #789
##    hiring accept-prompt (option_verbs) never auto-lapses; a genuine Unknown option is surfaced.

func _state() -> GameState:
	var s := GameState.new("window-option-routing-seed")
	s.money = 245000.0
	s.reputation = 50.0
	return s


func _research_event() -> Dictionary:
	# Mirrors EventService._generate_options for the "research" category (build_upon / acknowledge).
	return {
		"id": "hist_some_paper", "name": "Some Paper", "type": "popup", "category": "research",
		"options": [
			{"id": "build_upon", "text": "Build", "costs": {"action_points": 1, "money": 10000},
			 "effects": {"research": 15, "doom": 1}, "message": "Advancing."},
			{"id": "acknowledge", "text": "Ack", "costs": {}, "effects": {"research": 2}, "message": "Noted."},
		],
	}


func _policy_event() -> Dictionary:
	return {
		"id": "hist_some_policy", "name": "Some Policy", "type": "popup", "category": "policy",
		"options": [
			{"id": "support", "text": "Support", "costs": {"action_points": 1},
			 "effects": {"reputation": 5, "doom": -3}, "message": "Supported."},
			{"id": "stay_neutral", "text": "Neutral", "costs": {}, "effects": {}, "message": "Neutral."},
		],
	}


func _verb_window() -> Dictionary:
	# A #789-style option_verbs window (the hiring accept-prompt shape): a failed verb choice
	# is meant to RE-PROMPT (stay queued), not auto-lapse. provision_reserve is unaffordable.
	return {
		"id": "hiring_card", "type": "popup", "delivery_tier": "window",
		"options": [
			{"id": "provision_reserve", "text": "Provision", "costs": {"money": 999999999}, "effects": {}},
			{"id": "skip", "text": "Skip", "costs": {}, "effects": {}},
		],
		"window": {"attention_cost": 1, "option_verbs": {"provision_reserve": "handle_reserve", "skip": "ignore"}},
	}


func _paused_controller(s: GameState, windows: Array) -> MonthController:
	var mc := MonthController.new(s, null)
	mc.window_queue = windows
	mc.status = MonthController.Status.PAUSED_ON_WINDOW
	return mc


func _exhaust_attention(s: GameState) -> void:
	# No reserve, no free capacity, no WIP to cannibalize -> any HANDLE verb fails.
	s.month_plan.attention_reserved = 0
	s.month_plan.attention_spent = s.month_plan.attention_total
	s.month_plan.queued_strategic = []


# --- Fix 1: routing-by-id ---

func test_non_head_window_option_resolves_by_id():
	var s := _state()
	s.month_plan.set_reserve(3)  # Attention available for a HANDLE
	var mc := _paused_controller(s, [_policy_event(), _research_event()])
	var money0 := s.money

	# build_upon lives on the RESEARCH window, which is NOT the head.
	var r := mc.resolve_current_window_option("build_upon", _research_event())
	assert_true(r.get("success", false), "build_upon on a non-head window resolves cleanly")
	assert_eq(s.money, money0 - 10000.0, "the chosen option's in-fiction money cost applied")
	assert_eq(float((r.get("deltas", {}) as Dictionary).get("research", 0.0)), 15.0,
		"the option's research effect was applied")
	assert_eq(mc.window_queue.size(), 1, "the research window was removed by id-match, not the head")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hist_some_policy",
		"the head (policy) window is untouched")


func test_head_choice_still_resolves_the_head():
	# The aligned (normal) case is unchanged: no event supplied -> resolve the head.
	var s := _state()
	s.month_plan.set_reserve(3)
	var mc := _paused_controller(s, [_research_event(), _policy_event()])
	var r := mc.resolve_current_window_option("acknowledge")
	assert_true(r.get("success", false), "the head window's option resolves via the legacy head fallback")
	assert_eq(mc.window_queue.size(), 1, "the head was removed")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hist_some_policy",
		"the research head was the one removed")


func test_routing_by_id_past_a_stuck_verb_window():
	# A verb window that legitimately stays queued (option_verbs re-prompt) must not misroute
	# a later choice: resolving the research window's option still targets it by id.
	var s := _state()
	s.money = 0.0                 # provision_reserve is unaffordable -> the verb window stays
	s.month_plan.set_reserve(3)   # but there IS Attention for the research HANDLE
	var mc := _paused_controller(s, [_verb_window(), _research_event()])

	var r1 := mc.resolve_current_window_option("provision_reserve", _verb_window())
	assert_false(r1.get("success", true), "an unaffordable verb choice fails")
	assert_eq(mc.window_queue.size(), 2, "the option_verbs window is NOT auto-lapsed -- it re-prompts")

	s.money = 245000.0
	var r2 := mc.resolve_current_window_option("build_upon", _research_event())
	assert_true(r2.get("success", false), "build_upon routes to the research window past the stuck verb window")
	assert_false(String(r2.get("message", "")).contains("Unknown option"), "no bogus Unknown option")
	assert_eq(mc.window_queue.size(), 1, "only the research window was removed")
	assert_eq(String((mc.window_queue[0] as Dictionary).get("id", "")), "hiring_card",
		"the still-open verb window remains queued")


# --- Fix 2 (direction-b, playtest 2026-07-24): the INTERACTIVE default keeps the window open
# so the dialog surfaces the reason; the auto-lapse survives only as an explicit backstop. ---

func test_unaffordable_handle_stays_queued_for_the_open_dialog():
	# Direction-b default (allow_auto_lapse=false): an unaffordable HANDLE returns a plain
	# FAILURE and the window STAYS QUEUED. The event_dialog is kept open on this failure and
	# surfaces the reason, so the window is still answerable (the player retries / picks the
	# free out) -- it does NOT fake acceptance by closing, and it does NOT silently lapse.
	var s := _state()
	_exhaust_attention(s)
	var mc := _paused_controller(s, [_research_event()])

	var r := mc.resolve_current_window_option("build_upon", _research_event())
	assert_false(r.get("success", true), "the unaffordable HANDLE fails (the dialog stays open)")
	assert_false(r.get("auto_lapsed", false), "it does NOT silently auto-lapse on the interactive path")
	assert_eq(mc.window_queue.size(), 1, "the window stays queued -- the open dialog keeps it answerable")
	assert_true(mc.is_paused(), "still paused on the window the player can retry")

	# The player then takes the free out (zero-cost ignore option) -> resolves cleanly.
	var r2 := mc.resolve_current_window_option("acknowledge", _research_event())
	assert_true(r2.get("success", false), "the free out resolves the window")
	assert_eq(mc.window_queue.size(), 0, "now the window drains -- the month can finish")
	assert_false(mc.is_paused(), "playback resumes")


func test_unaffordable_handle_auto_lapses_when_backstop_requested():
	# The 5af981c3 soft-lock backstop is retained: a forced-drain caller (no open dialog to keep
	# the window answerable) passes allow_auto_lapse=true, and the window auto-lapses to IGNORE.
	var s := _state()
	_exhaust_attention(s)
	var mc := _paused_controller(s, [_research_event()])

	var r := mc.resolve_current_window_option("build_upon", _research_event(), true)
	assert_true(r.get("success", false), "the unaffordable HANDLE auto-resolves (no dead-end)")
	assert_true(r.get("auto_lapsed", false), "it lapsed to IGNORE because it could not be paid")
	assert_eq(mc.window_queue.size(), 0, "the window was removed -- not orphaned in the queue")
	assert_false(mc.is_paused(), "playback is no longer paused: the month can finish")


func test_unaffordable_handle_in_a_batch_does_not_stick():
	# Backstop batch drain: two windows, no Attention. With allow_auto_lapse=true, answering the
	# head HANDLE auto-lapses it and the whole batch drains, no orphan.
	var s := _state()
	_exhaust_attention(s)
	var mc := _paused_controller(s, [_policy_event(), _research_event()])

	var r1 := mc.resolve_current_window_option("support", _policy_event(), true)
	assert_true(r1.get("auto_lapsed", false), "the unaffordable policy HANDLE lapses")
	assert_eq(mc.window_queue.size(), 1, "the policy window drained; research remains")

	# acknowledge is the zero-cost IGNORE-path option -> always resolvable.
	var r2 := mc.resolve_current_window_option("acknowledge", _research_event(), true)
	assert_true(r2.get("success", false), "the research window resolves; no Unknown option, no orphan")
	assert_eq(mc.window_queue.size(), 0, "the batch fully drained")
	assert_false(mc.is_paused(), "playback resumes -- the month always finishes")


func test_option_verbs_window_is_not_auto_lapsed():
	# Guard the must-preserve #789 behavior even under the backstop: a failed reserve-vs-
	# cannibalize verb choice leaves the option_verbs window OPEN (re-prompt), it does NOT
	# auto-lapse -- so the backstop's option_verbs guard must fire.
	var s := _state()
	s.money = 0.0  # provision_reserve unaffordable
	var mc := _paused_controller(s, [_verb_window()])
	var r := mc.resolve_current_window_option("provision_reserve", _verb_window(), true)
	assert_false(r.get("success", true), "the unaffordable verb choice fails")
	assert_false(r.get("auto_lapsed", false), "an option_verbs window is NOT auto-lapsed")
	assert_eq(mc.window_queue.size(), 1, "the hiring prompt stays queued for a different verb")
	assert_true(mc.is_paused(), "still paused on the re-promptable window (deliberate)")


func test_genuine_unknown_option_is_not_masked():
	# A truly absent option (data/routing error) must still surface, not be swallowed as a lapse,
	# even on the backstop path (its unknown-option guard must fire).
	var s := _state()
	s.month_plan.set_reserve(3)
	var mc := _paused_controller(s, [_research_event()])
	var r := mc.resolve_current_window_option("no_such_option", _research_event(), true)
	assert_false(r.get("success", true), "an unknown option still fails")
	assert_false(r.get("auto_lapsed", false), "it is NOT auto-lapsed -- the error is surfaced")
	assert_string_contains(String(r.get("message", "")), "Unknown option", "the real error is reported")
	assert_eq(mc.window_queue.size(), 1, "the window stays (the caller can decide what to do)")

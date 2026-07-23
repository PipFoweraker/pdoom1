class_name MonthController
extends RefCounted
## Day-tick playback within a plan month, with auto-pause-on-window (L1 / ADR-0009 SUI).
##
## The plan cadence is the month; beneath it the day-turn is the resolution tick. This
## driver advances ticks (delegating the heavy sim to TurnManager), routes each tick's
## fired events by delivery tier, and PAUSES playback whenever a window demands a decision
## -- the auto-pause-on-window the ADR calls for. Ambient/feed events never interrupt.
##
## The window DEMAND budget (workshop#3 addendum #1) is enforced here: only N windows per
## month may demand a decision (2-3 early, more in endgame -- Balance-driven); window-tier
## events beyond the budget are downgraded to the feed (readable, no decision) rather than
## piling onto the player. That is the structural #630 fix: a demand budget, not an
## information budget.
##
## Month boundaries (Clock.is_month_boundary) open a fresh plan phase: a new Attention
## grant, the crisp reserve evaporates (MonthPlan.begin_month), the demand budget resets,
## and duration-elapsed strategic WIP is released. Unanswered windows left open when the
## player advances the month auto-resolve as IGNORE + a mild rep penalty (unless unignorable).

enum Status { READY, PAUSED_ON_WINDOW }

var state: GameState
var turn_manager  # TurnManager (untyped to avoid class_name load-order coupling in tests)

# Windows awaiting a decision on the current tick (auto-pause holds here).
var window_queue: Array = []
# Feed items surfaced this run (pull, no acknowledgment) -- provenance-stamped.
var feed_log: Array = []
var windows_surfaced_this_month: int = 0
var current_month_index: int = -1
var status: int = Status.READY
# Strategic WIP released this tick (duration elapsed) -- surfaced for the caller/L2 to apply
# effects; the controller does not reach into GameActions itself (clean seam).
var last_released_strategic: Array = []
# True while the month-boundary tick is HELD OPEN as the new month's plan phase. The engine
# convention is an OPEN turn during planning (started, not executed -- start_new_game leaves
# turn 1 open the same way); auto-executing the boundary tick would double-run its
# consequence steps when the plan later commits. advance_tick() sets this on a boundary and
# skips _complete_tick; the caller shows the month review and waits for the plan commit
# (GameManager.end_month executes the held-open turn).
var month_open_pending: bool = false


func _init(game_state: GameState, tm = null) -> void:
	state = game_state
	turn_manager = tm
	current_month_index = Clock.month_index(state.turn, state.start_year, state.start_month, state.start_day)


func window_demand_budget() -> int:
	"""Windows allowed to DEMAND a decision this month. Scales up in endgame (addendum #1)."""
	var endgame_turn := Balance.inum("events.endgame_turn", 200)
	if state.turn >= endgame_turn:
		return Balance.inum("events.window_demand_budget_endgame", 6)
	return Balance.inum("events.window_demand_budget", 3)


func is_paused() -> bool:
	return status == Status.PAUSED_ON_WINDOW


func advance_tick() -> Dictionary:
	"""Run one resolution tick. Returns {status, month_opened, windows, feed, released}.
	If a window surfaces, playback PAUSES (status 'paused_on_window') and execute_turn is
	deferred until the queue is answered (resolve_current_window / skip_current_window)."""
	if is_paused():
		return {"status": "paused_on_window", "windows": window_queue, "message": "resolve open windows first"}

	var month_opened := false
	month_open_pending = false
	if turn_manager != null:
		turn_manager.start_turn()  # increments state.turn, fires events into pending_events

	# A new calendar month = a fresh plan phase (Attention grant, reserve evaporates, budget resets).
	var mi := Clock.month_index(state.turn, state.start_year, state.start_month, state.start_day)
	if mi != current_month_index:
		_open_plan_month(mi)
		month_opened = true
		month_open_pending = true

	# Release duration-elapsed strategic WIP (seam: caller/L2 applies their effects).
	last_released_strategic = state.month_plan.take_due_strategic(state.turn)

	# Hiring pipeline (Phase B): resolve any interview/offer/connections jobs due this tick.
	# Stream-neutral when no jobs are in flight (guarded inside on_tick), so pre-existing
	# replays are unaffected.
	var hiring_feed: Array = []
	if state.hiring != null:
		var hiring_events: Array = state.hiring.on_tick(state)
		# #789 seam 3: a scheduled interview resolving used to land SILENTLY -- surface it.
		hiring_feed = _surface_hiring_tick_events(hiring_events)
		# #789 seams 1+2: a hire accepting mid-playback queues onboarding prompt cards
		# (hard-pause windows, FIFO play-queue -- ruling 1). Deliberately NOT counted
		# against the window demand budget: these are the player's own follow-up
		# opportunities on an action they initiated, not external demands.
		_enqueue_hiring_windows(hiring_events)

	var fired: Array = state.pending_events.duplicate()
	state.pending_events.clear()
	var surfaced := _dispatch(fired)
	var feed_out: Array = []
	feed_out.append_array(hiring_feed)
	feed_out.append_array(surfaced.get("feed", []))

	if not window_queue.is_empty():
		status = Status.PAUSED_ON_WINDOW
		# Mirror the open windows into the serialized pending_events so a pause->save->load
		# captures them (GameState owns save fidelity; window_queue is the live view).
		_sync_pending()
		state.current_phase = GameState.TurnPhase.TURN_START
		state.can_end_turn = false
		return {
			"status": "paused_on_window",
			"month_opened": month_opened,
			"windows": window_queue.duplicate(),
			"feed": feed_out,
			"released": last_released_strategic,
		}

	if month_open_pending:
		# The boundary tick is HELD OPEN as the new month's plan phase -- no execute_turn.
		# The plan-commit path (GameManager.end_month) executes it, matching the engine's
		# open-turn-during-planning convention (avoids double-running consequence steps).
		_hold_open_for_planning()
		return {
			"status": "month_open",
			"month_opened": true,
			"windows": [],
			"feed": feed_out,
			"released": last_released_strategic,
		}

	_complete_tick()
	return {
		"status": "ready",
		"month_opened": month_opened,
		"windows": [],
		"feed": feed_out,
		"released": last_released_strategic,
	}


func _surface_hiring_tick_events(events: Array) -> Array:
	"""#789 seam 3 (interview = schedule -> HAPPEN): route a resolved interview to the
	player feed, tagged toast=true so the UI layer also raises a notification. Pure view
	on an already-resolved deterministic outcome -- no RNG, no sim mutation. Returns the
	feed items surfaced (they also land in feed_log)."""
	var out: Array = []
	for e in events:
		if not (e is Dictionary):
			continue
		if String(e.get("kind", "")) != "interview_done":
			continue
		var who := String(e.get("candidate", "?"))
		var feed_event := {
			"id": "hiring_interview_done",
			"name": "Interview held: %s" % who,
			"delivery_tier": EventTiers.TIER_FEED,
			"source_id": "hiring",
			"message": "Interview with %s took place -- new details on their card." % who,
			"toast": true,
			"reveal_level": int(e.get("reveal_level", 0)),
		}
		var item := {"event": feed_event, "source_id": EventTiers.source_id_of(feed_event)}
		feed_log.append(item)
		out.append(item)
	return out


func _enqueue_hiring_windows(events: Array) -> void:
	"""#789 seams 1+2: offer-accept -> onboarding prompt cards on the window queue
	(provision card first, then the optional mentoring card -- FIFO play-queue). The
	accept/reject RNG roll already happened inside the pipeline, so pausing here moves
	no draw. Cards bypass the demand budget (see advance_tick comment)."""
	for e in events:
		if not (e is Dictionary):
			continue
		var kind := String(e.get("kind", ""))
		if kind != "offer_accepted" and kind != "offer_resentful_accept":
			continue
		var cand: Researcher = state.hiring.find_employed(state, String(e.get("candidate_id", "")))
		if cand == null:
			continue
		for w in state.hiring.build_accept_windows(cand):
			window_queue.append(w)


func _dispatch(events: Array) -> Dictionary:
	"""Route a tick's fired events by tier. Windows within the demand budget enqueue for a
	decision; window-tier events beyond the budget downgrade to feed. Returns the feed items
	surfaced this call."""
	var parts := EventTiers.partition(events)
	var surfaced_feed: Array = []
	for f in parts.feed:
		var item := {"event": f, "source_id": EventTiers.source_id_of(f)}
		feed_log.append(item)
		surfaced_feed.append(item)
	# Ambient: board-state mutation, no notification. v1 has no separate ambient effect
	# payload, so this is an acknowledged no-op -- the tier is honoured, content is L4.
	for w in parts.windows:
		if windows_surfaced_this_month < window_demand_budget():
			window_queue.append(w)
			windows_surfaced_this_month += 1
		else:
			# Over budget -> downgrade to feed rather than demand another decision.
			var item := {"event": w, "source_id": EventTiers.source_id_of(w), "over_budget": true}
			feed_log.append(item)
			surfaced_feed.append(item)
	return {"feed": surfaced_feed}


func resolve_current_window(response: String) -> Dictionary:
	"""Answer the head window with a costed response (ADR-0009 S3). When the queue empties,
	the paused tick completes (execute_turn runs). The window is popped only AFTER the
	resolver validates payment -- a failed verb (e.g. handle_reserve with an empty reserve)
	leaves the window open and still demanding a decision, resolvable via another verb
	(pop-before-validate silently dropped it: no effect, no charge, no window)."""
	if not is_paused() or window_queue.is_empty():
		return {"success": false, "message": "no open window"}
	var window: Dictionary = window_queue[0]
	var result := WindowResolver.resolve(state, state.month_plan, window, response, state.rng)
	if not result.get("success", false):
		return result  # window stays queued; playback stays paused
	window_queue.pop_front()
	_sync_pending()
	if window_queue.is_empty():
		status = Status.READY
		_finish_paused_tick()
	return result


func resolve_current_window_option(option_id: String) -> Dictionary:
	"""Answer the head window by choosing one of the event's own options (the v1 dialog
	path -- the event_dialog presents the event's options, not the four verbs). The chosen
	option maps onto the verb menu: the window's ignore option resolves as IGNORE (list
	price, no Attention); any other option is a HANDLE paid reserve-first, falling back to
	cannibalizing (WindowResolver.resolve_chosen_option). Payment source still lands in the
	replay artifact. The explicit four-verb menu (incl. DEFER) is the plan-screen UI's job."""
	if not is_paused() or window_queue.is_empty():
		return {"success": false, "message": "no open window"}
	var window: Dictionary = window_queue[0]
	var result := WindowResolver.resolve_chosen_option(state, state.month_plan, window, option_id, state.rng)
	if result.get("success", false):
		window_queue.pop_front()
		_sync_pending()
		if window_queue.is_empty():
			status = Status.READY
			_finish_paused_tick()
	return result


func skip_current_window() -> Dictionary:
	"""Leave the head window unanswered -- auto-resolves as IGNORE + a mild rep penalty
	(unignorable windows refuse this and stay queued)."""
	if not is_paused() or window_queue.is_empty():
		return {"success": false, "message": "no open window"}
	var window: Dictionary = window_queue[0]
	if EventTiers.is_unignorable(window):
		return {"success": false, "message": "window is unignorable -- must be handled"}
	var result := WindowResolver.resolve(state, state.month_plan, window, "auto_ignore", state.rng)
	if not result.get("success", false):
		return result  # same pop-only-on-success guard as resolve_current_window
	window_queue.pop_front()
	_sync_pending()
	if window_queue.is_empty():
		status = Status.READY
		_finish_paused_tick()
	return result


func _finish_paused_tick() -> void:
	"""The last open window was answered: either complete the tick (execute consequences)
	or, when the pause happened ON the month boundary, hold the tick open as the new plan
	phase instead (see month_open_pending)."""
	if month_open_pending:
		_hold_open_for_planning()
	else:
		_complete_tick()


func _complete_tick() -> void:
	"""Finish a tick once no window is pending: run the consequence phase."""
	state.current_phase = GameState.TurnPhase.ACTION_SELECTION
	state.can_end_turn = true
	if turn_manager != null:
		turn_manager.execute_turn()


func _hold_open_for_planning() -> void:
	"""Leave the boundary tick OPEN (started, not executed): this is the month's plan phase.
	The player queues actions against it; the next end_month() executes it."""
	state.current_phase = GameState.TurnPhase.ACTION_SELECTION
	state.can_end_turn = true


func _sync_pending() -> void:
	"""Keep the serialized pending_events in step with the live window queue, so save/load
	captures an open pause point (ADR-0009 UI: day-tick playback resumes at the window).
	pending_events is Array[Dictionary] -- build a typed array, don't assign an untyped one."""
	var typed: Array[Dictionary] = []
	for w in window_queue:
		if w is Dictionary:
			typed.append(w.duplicate(true))
	state.pending_events = typed


func rehydrate_from_state() -> void:
	"""Rebuild the live pause state from a freshly-loaded GameState. If the save was taken
	while a window was open, pending_events still holds it -- re-enter the paused state so
	playback resumes exactly where it stopped."""
	current_month_index = Clock.month_index(state.turn, state.start_year, state.start_month, state.start_day)
	window_queue = []
	for ev in state.pending_events:
		if ev is Dictionary and EventTiers.is_window(ev):
			window_queue.append(ev)
	status = Status.PAUSED_ON_WINDOW if not window_queue.is_empty() else Status.READY


func _open_plan_month(mi: int) -> void:
	"""Open a new plan month: fresh Attention, crisp reserve evaporation, budget reset."""
	current_month_index = mi
	windows_surfaced_this_month = 0
	var ordinal := Clock.month_ordinal_since_start(state.turn, state.start_year, state.start_month, state.start_day)
	state.month_plan.begin_month(Balance.inum("attention.per_month", 20), ordinal)
	# Hiring pipeline (Phase B): advertise campaigns trickle candidates, un-mentored hires face
	# their attrition roll. Stream-neutral when no campaign/at-risk hire is live (guarded).
	if state.hiring != null:
		var hiring_events: Array = state.hiring.on_month_boundary(state)
		_surface_hiring_notifications(hiring_events)


func _surface_hiring_notifications(events: Array) -> void:
	"""Surface month-boundary hiring outcomes to the player FEED (EventTiers TIER_FEED -- the
	established readable/no-decision channel; not a new channel). Ad campaigns trickling a
	candidate in used to be silent; the player now learns the campaign paid off. Batched: one
	feed line per month, pluralized, so several arrivals don't spam the feed."""
	var ad_hits := 0
	for e in events:
		if e is Dictionary and String(e.get("kind", "")) == "advertise_hit":
			ad_hits += 1
	if ad_hits <= 0:
		return
	var msg := "An applicant responded to your ad campaign." if ad_hits == 1 \
		else "%d applicants responded to your ad campaign." % ad_hits
	var feed_event := {
		"id": "hiring_ad_response",
		"name": "Ad campaign response",
		"delivery_tier": EventTiers.TIER_FEED,
		"source_id": "hiring",
		"message": msg,
		"count": ad_hits,
	}
	feed_log.append({"event": feed_event, "source_id": EventTiers.source_id_of(feed_event)})

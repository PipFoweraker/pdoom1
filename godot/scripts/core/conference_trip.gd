class_name ConferenceTrip
extends RefCounted
## The conference RHYTHM-BREAK shell (ADR-0014; Pip's 2026-07-27 rulings).
##
## WHAT THIS IS: the player voluntarily leaves the normal turn rhythm. Committing to a
## conference consumes ALL of the founder's remaining Attention for the away window (Pip,
## 2026-07-27 1555), pays travel cash up front, and hands the next N day-ticks to the
## standing plan. The world keeps running while the founder is gone -- events fire, salaries
## bill, the ledger compounds -- and everything that happened comes home as a BACKLOG the
## player reads on return. The HoMM analogy: opt into the pocket, the map resolves, the
## outcome is carried back.
##
## WHAT THIS IS NOT: the yields. Reputation and the named contact below are FLAVOR-ONLY
## first-pass placeholders. See the SEAM banners.
##
## MODEL (A) -- SKIP-TURNS, per the design seed's recommendation. The away window is real
## day-ticks driven through the EXISTING MonthController.advance_tick() path, in the existing
## order, drawing from the existing state.rng. No new RNG source, no new turn loop, no
## reordering of TurnManager's load-bearing steps (turn_manager.gd start_turn docstring:
## "STEP ORDER IS LOAD-BEARING"). Determinism is therefore free by construction: an away
## window is a pure function of (state, rng position, conference), so a replay re-simulates
## it identically.
##
## THE ANTI-FREE-BUTTON PROPERTY (seed section 2 -- protect this in any future edit): the
## trip must never be strictly dominant. Three real costs are wired in here:
##   1. travel cash leaves immediately (spiky cash flow, ADR-0012);
##   2. the founder's remaining Attention for the window is consumed and each fresh month
##      that opens while away is drained again -- nothing can be planned from the road;
##   3. with no Attention and no reserve, response windows that fire while away auto-resolve
##      as IGNORE (the documented default, seed section 1) and cost the nonresponse
##      reputation penalty. An UNIGNORABLE window CUTS THE TRIP SHORT and comes home still
##      queued for the player to answer.
## If a later edit removes all three, the framing collapses into a free button.
##
## FEED-CHANNEL DISCIPLINE (seed section 1, FRESH_EYES item 9, #877 modal-stacking history):
## this file produces ONE ordered backlog array. It never opens a dialog and never surfaces
## anything itself. main_ui renders it as a SINGLE dismissible panel on return; the deferred
## window (if any) is listed at the TOP and is only surfaced as a real dialog AFTER that
## panel is closed -- one surface at a time, never a stack of N modals for N missed ticks.

const Definitions = preload("res://scripts/data/definition_loader.gd")

const CATALOGUE_PATH := "res://data/events/conferences.json"

# Runaway guard for the window-drain inner loop. A tick cannot legitimately queue this many
# windows; if it ever does, we cut the trip short rather than spin.
const WINDOW_DRAIN_GUARD := 64

static var _catalogue: Array = []


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------
static func catalogue() -> Array:
	"""The shell catalogue (data/events/conferences.json), cached after first load."""
	if _catalogue.is_empty():
		var data := Definitions.load_object(CATALOGUE_PATH, "ConferenceTrip")
		var out: Array = []
		for entry in data.get("conferences", []):
			if entry is Dictionary:
				out.append(entry)
		_catalogue = out
	return _catalogue


static func reload_catalogue() -> void:
	"""Drop the cache (tests / data tuning) -- mirrors GameActions.reload_definitions()."""
	_catalogue = []


static func by_id(conf_id: String) -> Dictionary:
	for conf in catalogue():
		if String(conf.get("id", "")) == conf_id:
			return conf
	return {}


static func away_ticks(conf: Dictionary) -> int:
	"""The exposed window in day-ticks: travel out + the conference + travel back.
	Pip's 2026-07-27 ruling -- travel days are part of the away window, not free."""
	var travel: int = max(0, int(conf.get("travel_days", 0)))
	var duration: int = max(1, int(conf.get("duration_turns", 1)))
	return travel + duration + travel


static func can_commit(state: GameState, conf_id: String) -> Dictionary:
	"""Gate the commit. Returns {ok: bool, reason: String}."""
	if state == null:
		return {"ok": false, "reason": "no game state"}
	if state.game_over:
		return {"ok": false, "reason": "the run is over"}
	var conf := by_id(conf_id)
	if conf.is_empty():
		return {"ok": false, "reason": "Conference not found: %s" % conf_id}
	if state.has_attended_conference(conf_id):
		return {"ok": false, "reason": "Already attended %s this year" % String(conf.get("name", conf_id))}
	var cost: int = int(conf.get("travel_cost", 0))
	if cost > 0 and not state.can_afford({"money": cost}):
		return {"ok": false, "reason": "Cannot afford travel: %s" % GameConfig.format_money(cost)}
	return {"ok": true, "reason": ""}


# ---------------------------------------------------------------------------
# The trip
# ---------------------------------------------------------------------------
static func run_trip(state: GameState, controller, conf_id: String) -> Dictionary:
	"""Commit to a conference and resolve the whole away window SYNCHRONOUSLY.

	`controller` is the live MonthController (untyped, matching MonthController's own
	turn_manager field, so tests can drive this without class load-order coupling).

	Synchronous on purpose: the sim outcome is fully determined at commit time, so the
	presentation layer (fade -> vignette -> fade) is pure theatre over an already-decided
	result. Nothing about the mini-scene can influence the simulation -- the same one-way
	arrow ADR-0018 draws for the office render surface.

	Returns the trip record consumed by the vignette scene and the return backlog panel."""
	var gate := can_commit(state, conf_id)
	if not bool(gate.get("ok", false)):
		return {"success": false, "message": String(gate.get("reason", "cannot attend")), "backlog": []}

	var conf := by_id(conf_id)
	var ticks := away_ticks(conf)
	var backlog: Array = []
	var trip := {
		"success": true,
		"conference_id": conf_id,
		"conference": conf.duplicate(true),
		"away_ticks": ticks,
		"ticks_resolved": 0,
		"cut_short": false,
		"cut_short_reason": "",
		"attention_consumed": 0,
		"travel_cost": int(conf.get("travel_cost", 0)),
		"start_turn": state.turn,
		"end_turn": state.turn,
		"backlog": backlog,
		"memento": {},
	}

	# --- Book it. Travel cash leaves NOW (cost #1 of the anti-free-button property). ---
	var cost: int = int(conf.get("travel_cost", 0))
	if cost > 0:
		state.spend_resources({"money": cost})
	state.mark_conference_attended(conf_id)

	# --- Commit the OPEN plan turn with whatever the player already queued. That queue IS
	# the standing plan for the departure tick; an empty one routes through the canonical
	# pass, exactly as GameManager.end_month() does for an empty month. ---
	_commit_open_turn(state, controller)
	trip["attention_consumed"] = int(trip["attention_consumed"]) + _consume_founder_capacity(state)

	# --- The away window. ---
	for _i in ticks:
		if state.game_over:
			trip["cut_short"] = true
			trip["cut_short_reason"] = "The run ended while you were away."
			break
		if controller == null:
			break

		var tick_result: Dictionary = controller.advance_tick()
		trip["ticks_resolved"] = int(trip["ticks_resolved"]) + 1
		collect_tick(backlog, state.turn, tick_result)

		if String(tick_result.get("status", "")) == "paused_on_window":
			var drain := _drain_windows_while_away(state, controller, backlog)
			if not bool(drain.get("ok", false)):
				trip["cut_short"] = true
				trip["cut_short_reason"] = String(drain.get("reason", ""))
				break

		# A fresh month opened mid-trip: the boundary tick is HELD OPEN as that month's plan
		# phase (MonthController.month_open_pending). The founder is not there to plan it, so
		# the standing plan commits it and the new Attention grant is consumed immediately --
		# nothing can be planned from the road (cost #2).
		if bool(controller.month_open_pending):
			_commit_open_turn(state, controller)
			trip["attention_consumed"] = int(trip["attention_consumed"]) + _consume_founder_capacity(state)

	trip["end_turn"] = state.turn

	# --- Home. Flavor yields + the stamped memento. ---
	trip["memento"] = _apply_flavor_yields(state, conf, trip)
	return trip


static func collect_tick(backlog: Array, turn: int, tick_result: Dictionary) -> void:
	"""Fold ONE MonthController.advance_tick() result into the return backlog, in surfaced
	order. Kept a separate static so it is unit-testable against a synthetic tick result
	without running a whole sim.

	Entries are plain data: {kind, turn, ...}. kind is one of
	  "feed"               -- a readable feed line that accrued while away
	  "month_opened"       -- a plan month began with nobody home to plan it
	  "strategic_released" -- queued strategic WIP whose duration elapsed
	  "window_auto_ignored"-- a response window fired and auto-resolved to the IGNORE default
	  "window_deferred"    -- an unignorable window that cut the trip short (rendered FIRST)"""
	for item in tick_result.get("feed", []):
		if not (item is Dictionary):
			continue
		var ev: Dictionary = item.get("event", {})
		if not (ev is Dictionary):
			ev = {}
		backlog.append({
			"kind": "feed",
			"turn": turn,
			"source_id": String(item.get("source_id", "?")),
			"id": String(ev.get("id", "")),
			"name": String(ev.get("name", ev.get("id", "update"))),
			"message": String(ev.get("message", "")),
			"channel": String(ev.get("channel", "normal")),
		})

	if bool(tick_result.get("month_opened", false)):
		backlog.append({
			"kind": "month_opened",
			"turn": turn,
			"name": "A new month opened while you were away",
			# COPY UPDATED WITH #980 (4-way lane). The old line ("the grant went unplanned")
			# is literally false now: travel drains the OPERATING family only, so the
			# planning half of the grant survives the boundary and next month's direction is
			# still decidable from the road. What is gone is presence: doors and audits.
			"message": "The month opened with nobody in the building -- its doors and audit hours are gone. Next month's direction is still yours to set.",
		})

	for released in tick_result.get("released", []):
		if not (released is Dictionary):
			continue
		backlog.append({
			"kind": "strategic_released",
			"turn": turn,
			"name": "Strategic work landed: %s" % String(released.get("action_id", "?")),
			"message": "Queued before you left; its duration elapsed while you were gone.",
		})


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------
static func _commit_open_turn(state: GameState, controller) -> void:
	"""Run the currently-open plan turn's consequence phase with the standing plan.

	Mirrors the head of GameManager.end_month() deliberately: an empty queue routes through
	GameActions.PASS_ACTION_ID (the canonical, cost-0, determinism-safe no-op) rather than
	erroring, and the open turn is executed via TurnManager.execute_turn(). We do NOT
	duplicate end_month()'s implicit-reserve line -- the founder is away, so there is no
	reserve to hold; _consume_founder_capacity takes the remainder instead."""
	if state.game_over:
		return
	if state.queued_actions.is_empty():
		state.queued_actions.append(GameActions.PASS_ACTION_ID)
	if controller != null and controller.turn_manager != null:
		controller.turn_manager.execute_turn()


static func _consume_founder_capacity(state: GameState) -> int:
	"""Pip's 2026-07-27 1555 ruling: attending consumes the founder's remaining capacity for
	the away window.

	==== SEAM CLOSED BY T2 (attention migration + 2-way founder hours) ====
	Refined per Pip's #980 noticing: being away is a loss of OPERATOR PRESENCE, not of
	PLANNER MIND. So the trip drains only the OPERATING pool, and drains it with overflow
	FORBIDDEN -- travel must never eat the planning hours that let you decide next month's
	direction from a hotel room. Everything else about the trip's cost model is unchanged.

	==== 4-WAY LANE (Ballot 4) ====
	No code change was needed here, and that is the point: `doors` and `audits` both live in
	the OPERATING family (MonthPlan.KIND_FAMILY), so draining that family kills exactly the
	two presence kinds -- you cannot hold a stakeholder room you are not in, and you cannot
	skip-level ground-truth a researcher from a conference floor. `approvals` (the PLANNING
	family) survives untouched, which IS #980's "planner mind, not operator presence". The
	`month_opened` backlog copy above was rewritten to stop asserting the pre-#980 rule.
	Returns the Attention actually consumed (for the return panel's honesty about the cost)."""
	if state.month_plan == null:
		return 0
	# Cap the drain at whichever binds first: operating hours left, or un-reserved Attention.
	var free: int = mini(
		state.month_plan.hours_available(MonthPlan.HOUR_OPERATING),
		state.month_plan.available()
	)
	if free <= 0:
		return 0
	state.month_plan.spend_attention(free, MonthPlan.HOUR_OPERATING)
	return free


static func _drain_windows_while_away(state: GameState, controller, backlog: Array) -> Dictionary:
	"""Resolve response windows that fired with nobody home.

	Seed section 1: "No response-window items should accrue while away (a response window
	demands presence by definition). An event that WOULD have opened one either auto-resolves
	to a documented default, or defers to the founder's first turn back."
	Both halves are implemented:
	  * ignorable window -> MonthController.skip_current_window() = the documented default
	    (auto-resolve as IGNORE + the mild nonresponse reputation penalty). Uses state.rng
	    through the same WindowResolver path normal play uses -- no new stream.
	  * UNIGNORABLE window -> refuses to be skipped by construction, so it stays queued and
	    the trip is CUT SHORT. It comes home with the player and is answered on return. This
	    is also the soft-lock guard: we never force-resolve a window the engine says must be
	    handled, and we never spin waiting for one.
	Returns {ok: bool, reason: String}. ok=false means cut the trip short."""
	var guard := 0
	while controller.is_paused() and not controller.window_queue.is_empty():
		guard += 1
		if guard > WINDOW_DRAIN_GUARD:
			return {"ok": false, "reason": "Too many demands at once -- you came home early."}
		var window: Dictionary = controller.window_queue[0]
		var label := String(window.get("name", window.get("id", "something")))

		if EventTiers.is_unignorable(window):
			backlog.push_front({
				"kind": "window_deferred",
				"turn": state.turn,
				"id": String(window.get("id", "")),
				"name": label,
				"message": "This could not wait. You came home early; it is still open.",
			})
			return {"ok": false, "reason": "%s demanded your presence." % label}

		var result: Dictionary = controller.skip_current_window()
		if not bool(result.get("success", false)):
			# The engine refused the skip for some other reason -- do not spin, do not
			# force-resolve. Leave it queued and come home to it.
			backlog.push_front({
				"kind": "window_deferred",
				"turn": state.turn,
				"id": String(window.get("id", "")),
				"name": label,
				"message": String(result.get("message", "Still open on your return.")),
			})
			return {"ok": false, "reason": "%s could not be left unanswered." % label}

		backlog.append({
			"kind": "window_auto_ignored",
			"turn": state.turn,
			"id": String(window.get("id", "")),
			"name": label,
			"message": String(result.get("message", "Went unanswered while you were away.")),
		})
	return {"ok": true, "reason": ""}


static func _apply_flavor_yields(state: GameState, conf: Dictionary, trip: Dictionary) -> Dictionary:
	"""==== SEAM: REAL YIELDS ATTACH HERE ====
	FIRST PASS, FLAVOR ONLY -- deliberately, per the design seed's shell-vs-yields split.

	What lands today: a small reputation nudge and ONE named contact breadcrumb with no
	receivable behavior whatsoever.

	What replaces it AFTER adoption-v1 (ADR-0014 point 3, WS3_FINISH_OR_DROP sequencing):
	  * the adoption-accelerant multiplier on the player's published work;
	  * contacts minted as real receivables into the Ledger's counterparty slot
	    (ledger.gd counterparty field, DQ-9);
	  * delegate-vs-founder yield scaling (ADR-0014 point 2).
	Swap THIS FUNCTION BODY. The UX above it -- commit, fade, vignette, away window, backlog
	panel -- does not care whether its yield hook is a stub or a real accelerant call, and
	must not be re-opened to wire the real numbers.

	The contact pick is the trip's only NEW rng draw. It comes from state.rng (the one
	deterministic stream, ADR-0006) and is recorded to the verification artifact like every
	other draw, so replays stay self-consistent. It is drawn only when a trip happens, so
	no pre-existing replay is disturbed."""
	var rep_gain: float = float(conf.get("flavor_reputation", 1.0))
	if rep_gain > 0.0:
		state.add_resources({"reputation": rep_gain})

	var contact: Dictionary = {}
	var pool: Array = conf.get("contacts", [])
	if not pool.is_empty():
		var idx: int = int(state.rng.randi() % pool.size())
		VerificationTracker.record_rng_outcome("conference_contact_pick", float(idx), state.turn)
		contact = {
			"name": String(pool[idx]),
			"met_at": String(conf.get("name", "")),
			"met_on_turn": state.turn,
			"receivable": null,   # SEAM: becomes a Ledger counterparty entry post adoption-v1
			"first_pass": true,
		}

	var name := String(conf.get("name", "the conference"))
	var line := "Back from %s after %d days." % [name, int(trip.get("ticks_resolved", 0))]
	if bool(trip.get("cut_short", false)):
		line = "Back from %s early -- %s" % [name, String(trip.get("cut_short_reason", ""))]

	return {
		"first_pass": true,   # honest label: these are placeholder yields, not the real ones
		"line": line,
		"reputation_gain": rep_gain,
		"contact": contact,
		"keepsake": "Lanyard from %s, kept." % name,
	}

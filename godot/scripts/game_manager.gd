extends Node
## Pure GDScript game manager - NO Python bridge

signal game_state_updated(state: Dictionary)
signal turn_phase_changed(phase: String)
signal actions_available(actions: Array)
signal action_executed(result: Dictionary)
signal error_occurred(error_msg: String)
signal event_triggered(event: Dictionary)

# Game objects
var state: GameState
var turn_manager: TurnManager
var is_initialized: bool = false

# L1 (ADR-0009): the month playback driver. Created with the game; the End Turn button
# routes through end_month() -> MonthController day ticks (auto-pause-on-window). The old
# single day-step (end_turn) survives ONLY behind the DEV MODE overlay.
var month_controller: MonthController = null
var month_playback_active: bool = false
# Seconds between visible day ticks during month playback. var (not const) so headless
# smokes/tests can run a month fast; a player-facing speed control is future UI work.
var day_tick_seconds: float = 0.2
# Rivals-in-review (item 2): last capability_progress seen per visible rival, keyed by id,
# so the month review can show a qualitative month-over-month drift. Display-only cache --
# deliberately NOT serialized (a loaded game just shows "flat" on its first review). Never
# read by the simulation, so it cannot touch determinism.
var _rival_cap_snapshot: Dictionary = {}

## A4 (playtest 2026-08-01): the month review showed LEVELS the HUD already shows. To show
## MOVEMENT instead it needs two readings per stat.
##   _month_stat_snapshot -- the reading taken at the last month boundary, i.e. the START of
##                           the month now being reviewed. Empty before the first boundary.
##   _last_tick_stats     -- the reading taken immediately BEFORE each day tick. At the moment
##                           the boundary tick reports "month_open", this still holds the LAST
##                           DAY of the old month. That matters: the boundary tick has already
##                           run MonthController._open_plan_month(), which charges the NEW
##                           month's office rent -- reading state.money at review time would
##                           book next month's rent against last month's funds delta, every
##                           month, in the same direction.
## Display-only. Nothing here feeds the sim, so determinism/replay are untouched.
var _month_stat_snapshot: Dictionary = {}
var _last_tick_stats: Dictionary = {}
# Synthetic month-review dialog id -- intercepted by resolve_event before any engine path.
const MONTH_REVIEW_EVENT_ID := "__month_review__"

# --- Conference rhythm break (ADR-0014 shell; scripts/core/conference_trip.gd) ---
# One-shot handoff flag: main.tscn is LEFT for the conference mini-scene and re-entered
# afterwards. main_ui._boot_game() would otherwise start_new_game() and destroy the live run,
# so re-entry checks this and resumes in place instead. Set by the vignette on its way out,
# cleared by resume_in_place(). Deliberately NOT serialized -- it is a scene-handoff flag,
# never simulation state.
var pending_resume: bool = false
# The most recent resolved trip record (ConferenceTrip.run_trip). Read by the vignette scene
# and by the return backlog panel. Display data only; the sim already consumed its effects.
var last_conference_trip: Dictionary = {}

func _ready():
	print("[GameManager] Pure GDScript version ready")

func start_new_game(game_seed: String = "", force: bool = false):
	"""Initialize new game - pure GDScript - FIX #418: Handle initial events.

	Self-guard (scene-reentry run-killer family, sibling of #979): this used to
	unconditionally replace `state`, so every caller had to remember its own guard --
	the dev-overlay leaderboard/settings jump forgot, and silently destroyed a live run.
	Refuses to run when a game is already live unless the caller passes force=true.
	Legitimate fresh-start callers (welcome/config_confirmation Launch-Lab chain via
	main_ui._boot_game's fresh-boot branch, the debug "Reset Game" button) pass
	force=true explicitly -- that is the caller declaring "yes, I mean to end the
	current run"."""
	if is_initialized and not force:
		push_warning("[GameManager] start_new_game() REFUSED: a game is already live (is_initialized=true) and force=false would silently destroy it. Pass force=true if this is a deliberate reset/new-game.")
		PerfLog.mark("start_new_game_refused", {"turn": state.turn if state != null else -1})
		return
	# Get config from GameConfig singleton if seed not provided
	if game_seed.is_empty():
		game_seed = GameConfig.get_display_seed()

	print("[GameManager] Starting new game")
	print("  Player: %s" % GameConfig.player_name)
	print("  Lab: %s" % GameConfig.lab_name)
	print("  Seed: %s" % game_seed)
	print("  Difficulty: %s" % GameConfig.get_effective_difficulty_string())
	print("  Scenario: %s" % (GameConfig.scenario_id if not GameConfig.scenario_id.is_empty() else "Standard"))

	# Release the previous game's orphaned Node subsystems before replacing them. Without
	# this, restarting / "play again" inside a session leaks 4 Nodes per game (see
	# _release_game_objects). Stop any in-flight month playback first so no tick touches the
	# state we are about to drop.
	month_playback_active = false
	_release_game_objects()
	_rival_cap_snapshot.clear()  # fresh drift baseline for the new run
	_month_stat_snapshot.clear()  # A4: no month has elapsed yet, so there is no movement to show
	_last_tick_stats.clear()

	# Alpha Tools flag is RUN-scoped (decision card 2026-08-01): a fresh run starts
	# clean; the previous run's taint must not leak forward. This is the ONLY place
	# the sticky one-way flag resets.
	GameConfig.reset_alpha_tools_flag()

	state = GameState.new(game_seed)
	# Early-game org-form choice (DQ-19): copy the pregame selection onto the pure state
	# so FinanceEngine prices/gates instruments per org form. Default nonprofit.
	state.org_type = GameConfig.org_type

	# Apply scenario overrides (before difficulty, so difficulty can further modify)
	_apply_scenario_overrides()

	# Apply difficulty settings to game state
	_apply_difficulty_settings()

	turn_manager = TurnManager.new(state)
	# L1: the month playback driver rides the same state + turn manager.
	month_controller = MonthController.new(state, turn_manager)
	month_playback_active = false
	is_initialized = true

	# Start verification tracking. The event schedule travels with the artifact
	# (ADR-0005: seed = RNG seed + schedule; DQ-6 fix, L0 #620 item 4).
	# Build-vs-ladder split (spec 5.3): the artifact carries BOTH versions --
	# game_version = the BUILD (repro identity: a replay must reproduce on the exact
	# binary that made it), ladder = the EPOCH the score ranks under
	# (GameConfig.get_board_version(), the board key).
	var game_version = GameConfig.CURRENT_VERSION
	# ADR-0016 league metabolism: stamp the artifact with its league (the baseline month).
	# Placeholder until the league pipeline lands -- the run's start month is a stable id
	# carried beside (seed, game_version) so cross-league boards (DQ-3) can key on it.
	var league_id := "%04d-%02d" % [state.start_year, state.start_month]
	VerificationTracker.enable_debug()  # Enable verbose logging
	VerificationTracker.start_tracking(game_seed, game_version, state.event_schedule, league_id, GameConfig.get_board_version())
	print("[GameManager] Verification tracking enabled (debug mode: ON)")

	# Start baseline simulation in background if appropriate (Issue #372)
	# This runs the "no-action" simulation for score comparison at game end
	if GameConfig.should_start_background_baseline():
		print("[GameManager] Starting background baseline simulation (mode: %s)" % GameConfig.get_baseline_mode_string())
		BaselineSimulator.start_background_simulation(game_seed)
	elif GameConfig.should_use_precomputed_baseline():
		print("[GameManager] Using precomputed baseline (weekly league mode)")
		# Precomputed baseline will be set by weekly league system when available
	else:
		print("[GameManager] Baseline mode: Blind (will compute at game end)")

	# Start gameplay music
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)


	# Start first turn (may trigger events!)
	var turn_result = turn_manager.start_turn()

	# Emit initial state
	game_state_updated.emit(state.to_dict())

	# Emit phase (might be turn_start if events, or action_selection if not)
	turn_phase_changed.emit(turn_result["phase"])

	# Check for initial events (FIX #418)
	if turn_result.has("triggered_events") and turn_result["triggered_events"].size() > 0:
		print("[GameManager] Initial events triggered!")
		for event in turn_result["triggered_events"]:
			event_triggered.emit(event)
	else:
		# No events, emit available actions
		var actions = turn_manager.get_available_actions()
		actions_available.emit(actions)

	print("[GameManager] Game initialized - Turn %d" % state.turn)

func select_action(action_id: String) -> bool:
	"""Queue action for execution with immediate AP deduction - FIX #418: Block if events pending.
	Returns true when the action was queued (#622: lets UI callers key their local
	queue display off the same validation instead of duplicating pre-checks)."""
	# Validation: Game initialized
	if not is_initialized:
		var _err = ErrorHandler.report_err(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.ACTIONS,
			"Cannot select action: Game not initialized",
			{"action_id": action_id}
		)
		error_occurred.emit(_err.message)
		return false

	# Validation: No pending events (FIX #418)
	if state.pending_events.size() > 0:
		var _err = ErrorHandler.warning(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.ACTIONS,
			"Cannot select actions while events are pending",
			{"action_id": action_id, "pending_events": state.pending_events.size()}
		)
		error_occurred.emit("Resolve pending events before selecting actions!")
		return false

	# Validation: Correct phase (FIX #418)
	if state.current_phase != GameState.TurnPhase.ACTION_SELECTION:
		var phase_name = GameState.TurnPhase.keys()[state.current_phase]
		var _err = ErrorHandler.warning(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.ACTIONS,
			"Cannot select actions in current phase",
			{"action_id": action_id, "current_phase": phase_name}
		)
		error_occurred.emit("Cannot select actions in %s phase" % phase_name)
		return false

	# Get action details to check AP cost
	var action = _get_action_by_id(action_id)
	if not action or action.is_empty():
		var _err = ErrorHandler.report_err(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.ACTIONS,
			"Action not found",
			{"action_id": action_id}
		)
		error_occurred.emit("Action not found: " + action_id)
		return false

	# T2 (ADR-0011): the founder spends the monthly Attention budget (month_plan). Queuing a
	# strategic action is PLANNER MIND -- it bills PLANNING hours (2-way founder-hour floor).
	var attention_cost: int = GameActions.attention_cost(action)
	var hour_type: String = GameActions.hour_type(action)

	# Validation: Sufficient Attention this plan-month (checks REMAINING = total - spent -
	# reserved, so an explicitly-held reserve is protected from over-queuing).
	var available_attention = state.month_plan.available() if state.month_plan != null else 0
	var hours_ok: bool = state.month_plan != null and state.month_plan.can_spend_hours(attention_cost, hour_type)
	if available_attention < attention_cost or not hours_ok:
		var _err = ErrorHandler.warning(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.RESOURCES,
			"Insufficient Attention",
			{
				"action_id": action_id,
				"action_name": action.get("name", ""),
				"required": attention_cost,
				"available": available_attention,
				"attention_total": state.month_plan.attention_total if state.month_plan else 0,
				"attention_spent": state.month_plan.attention_spent if state.month_plan else 0
			}
		)
		if available_attention >= attention_cost:
			error_occurred.emit("Not enough %s hours: %d needed, %d left this month" % [
				hour_type, attention_cost, state.get_available_hours(hour_type)])
		else:
			error_occurred.emit("Not enough Attention: %d needed, %d left this month" % [attention_cost, available_attention])
		return false

	# Validation: Can afford NON-Attention costs (money/compute/research/... ). Attention is
	# gated above against the month plan, so strip it here -- letting can_afford re-check it
	# would double-gate the same budget.
	var afford_costs = action.get("costs", {}).duplicate()
	afford_costs.erase("attention")
	if not state.can_afford(afford_costs):
		var costs = action.get("costs", {})
		var _err = ErrorHandler.warning(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.RESOURCES,
			"Cannot afford action",
			{
				"action_id": action_id,
				"action_name": action.get("name", ""),
				"costs": costs,
				"state": {
					"money": state.money,
					"compute": state.compute,
					"research": state.research,
					"papers": state.papers,
					"reputation": state.reputation
				}
			}
		)
		error_occurred.emit("Cannot afford " + action.get("name", action_id))
		return false

	# Spend Attention from the monthly budget (the founder currency). This is the same
	# pool queued strategic WIP and the implicit reserve draw from, so end_month's
	# reserve = attention_total - attention_spent stays correct.
	if state.month_plan != null:
		state.month_plan.attention_spent += attention_cost

	# Queue the action
	state.queued_actions.append(action_id)

	ErrorHandler.info(
		ErrorHandler.Category.ACTIONS,
		"Action queued successfully",
		{
			"action_id": action_id,
			"action_name": action.get("name", ""),
			"attention_cost": attention_cost,
			"attention_remaining": state.month_plan.available() if state.month_plan else 0
		}
	)

	print("[GameManager] Action queued: %s (Attention cost: %d, remaining: %d)" % [action_id, attention_cost, state.month_plan.available() if state.month_plan else 0])

	action_executed.emit({
		"success": true,
		"message": "Action queued: " + action.get("name", action_id)
	})

	# Emit updated state to refresh UI
	game_state_updated.emit(state.to_dict())

	return true

func queue_candidate_hire(candidate_name: String, specialization: String) -> bool:
	"""#622 L10: UI-facing path for hiring a NAMED candidate from the pool. Owns the
	state writes main_ui used to do directly (pending_hire_queue + candidate pool),
	so the UI never mutates game state. Validation is select_action's job -- on
	failure it has already emitted error_occurred and nothing is touched here
	(the old UI order queued the candidate BEFORE validating, which could strand
	a candidate out of the pool on a rejected action)."""
	if not is_initialized:
		error_occurred.emit("Cannot hire: Game not initialized")
		return false

	# Find the specific candidate object first (may legitimately be absent: legacy
	# hire actions without a pool candidate keep working, matching the old UI path).
	var candidate_obj: Researcher = null
	for c in state.candidate_pool:
		if c.researcher_name == candidate_name and c.specialization == specialization:
			candidate_obj = c
			break

	var action_id = "hire_%s_researcher" % specialization
	if not select_action(action_id):
		return false  # select_action already emitted the error signal

	if candidate_obj:
		# Queue for hiring (supports multiple hires per turn) and remove from the
		# pool immediately to prevent double-hiring.
		state.pending_hire_queue.append(candidate_obj)
		state.remove_candidate(candidate_obj)
		print("[GameManager] Queued hire: %s (removed from pool, queue size: %d)" % [candidate_name, state.pending_hire_queue.size()])
		# Re-emit: select_action's emit above predates the pool changes.
		game_state_updated.emit(state.to_dict())
	else:
		print("[GameManager] WARNING: Could not find candidate object for: %s" % candidate_name)
	return true


func _get_action_by_id(action_id: String) -> Dictionary:
	"""Helper to get action by ID - delegates to GameActions"""
	return GameActions.get_action_by_id(action_id)

func purchase_upgrade(upgrade_id: String):
	"""Purchase an upgrade - doesn't consume AP"""
	if not is_initialized:
		error_occurred.emit("Cannot purchase upgrade: Game not initialized")
		return

	# Purchase the upgrade
	var result = GameUpgrades.purchase_upgrade(upgrade_id, state)

	if result.get("success", false):
		print("[GameManager] Upgrade purchased: %s" % upgrade_id)
		action_executed.emit(result)

		# Emit updated state (money and upgrades changed)
		game_state_updated.emit(state.to_dict())
	else:
		error_occurred.emit(result.get("message", "Upgrade purchase failed"))

func fire_researcher(researcher_index: int, severance_cost: float):
	"""Fire a researcher with severance payout"""
	if not is_initialized:
		error_occurred.emit("Cannot fire employee: Game not initialized")
		return

	# Validate researcher index
	if researcher_index < 0 or researcher_index >= state.researchers.size():
		error_occurred.emit("Invalid researcher index: %d" % researcher_index)
		return

	# Validate funds
	if state.money < severance_cost:
		error_occurred.emit("Cannot afford severance: need %s, have %s" % [
			GameConfig.format_money(severance_cost),
			GameConfig.format_money(state.money)
		])
		return

	# Get researcher details before removing
	var researcher = state.researchers[researcher_index]
	var researcher_name = researcher.researcher_name

	# Pay severance
	state.money -= severance_cost

	# Remove researcher
	state.remove_researcher(researcher)

	# Create result message
	var result_message = "Fired %s. Severance paid: %s" % [
		researcher_name,
		GameConfig.format_money(severance_cost)
	]

	print("[GameManager] %s" % result_message)

	# Emit result
	action_executed.emit({
		"success": true,
		"message": result_message
	})

	# Emit updated state
	game_state_updated.emit(state.to_dict())

func reserve_ap(amount: int):
	"""Explicitly hold `amount` more Attention for response windows this month (ADR-0009
	crisp reserve). L2: routes to the monthly Attention budget, not the retired per-turn pool."""
	if not is_initialized:
		error_occurred.emit("Cannot reserve Attention: Game not initialized")
		return

	if state.month_plan != null and state.month_plan.set_reserve(state.month_plan.attention_reserved + amount):
		print("[GameManager] Reserved %d Attention for windows (Available: %d, Reserved: %d)" % [amount, state.month_plan.available(), state.month_plan.attention_reserved])
		action_executed.emit({"success": true, "message": "Reserved %d Attention for responses" % amount})

		# Emit updated state
		game_state_updated.emit(state.to_dict())
	else:
		error_occurred.emit("Not enough Attention to reserve (need %d, have %d operating hours)" % [amount, state.get_available_hours(MonthPlan.HOUR_OPERATING)])

func clear_action_queue():
	"""Clear all queued actions and refund their committed Attention."""
	if not is_initialized:
		return

	var refunded := _queued_attention_cost()
	state.queued_actions.clear()
	if state.month_plan != null:
		state.month_plan.refund_attention(refunded, MonthPlan.HOUR_PLANNING)

	print("[GameManager] Queue cleared, refunded %d Attention" % refunded)
	game_state_updated.emit(state.to_dict())


func _queued_attention_cost() -> int:
	"""Sum the Attention cost of the currently queued founder actions (their legacy
	`attention` cost). Used to refund on clear/remove."""
	var total := 0
	for aid in state.queued_actions:
		total += GameActions.attention_cost(_get_action_by_id(aid))
	return total

func set_research_quality(mode: String):
	"""Set the org-wide research quality stance (Issue #500)."""
	if not is_initialized:
		return
	state.set_research_quality(mode)
	print("[GameManager] Research quality set to %s" % state.research_quality_mode)
	game_state_updated.emit(state.to_dict())

func remove_queued_action(action_id: String):
	"""Remove specific action from queue and refund its AP cost"""
	if not is_initialized:
		return

	# Find and remove the action
	var removed_index = -1
	for i in range(state.queued_actions.size()):
		if state.queued_actions[i] == action_id:
			removed_index = i
			break

	if removed_index >= 0:
		# Get Attention cost before removing
		var action = _get_action_by_id(action_id)
		var attention_cost: int = GameActions.attention_cost(action)

		# Remove and refund Attention (queued cards billed PLANNING hours)
		state.queued_actions.remove_at(removed_index)
		if state.month_plan != null:
			state.month_plan.refund_attention(attention_cost, GameActions.hour_type(action))

		print("[GameManager] Removed %s from queue, refunded %d Attention (available: %d)" % [action_id, attention_cost, state.month_plan.available() if state.month_plan else 0])
		game_state_updated.emit(state.to_dict())
	else:
		print("[GameManager] WARNING: Action not found in queue: %s" % action_id)

func resign() -> void:
	"""End the run deliberately and route to the game-over screen (#959, cheap form).

	Deliberately NOT a new path into game-over. It drives doom to the lose
	threshold and then calls the SAME check_win_lose() -> game_state_updated ->
	MainUI -> game_over_screen route that every ordinary loss takes. The
	game-over -> leaderboard transition is the one that segfaulted the v0.11.0
	release, so this adds a new TRIGGER for a proven route rather than a new
	route.

	Doom is written through doom_system, not through state.doom: check_win_lose()
	re-syncs `doom = doom_system.current_doom` before testing the threshold, so a
	direct write to state.doom would be silently overwritten and the run would
	simply carry on -- a failure that would have looked exactly like a dead
	button.

	Not routed through end_turn(): that refuses when the action queue is empty,
	which is precisely the state a bored player is in.
	"""
	if not is_initialized or state == null:
		push_warning("[GameManager] resign() ignored: no live run")
		return
	if state.game_over:
		return
	print("[GameManager] Player resigned at turn %d" % state.turn)
	PerfLog.mark("player_resigned", {"turn": state.turn, "doom": state.doom})
	if state.doom_system:
		state.doom_system.current_doom = 100.0
	state.doom = 100.0
	state.check_win_lose()
	game_state_updated.emit(state.to_dict())


func end_turn():
	"""Execute queued actions and process turn"""
	# Validation: Game initialized
	if not is_initialized:
		var _err = ErrorHandler.report_err(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.TURN,
			"Cannot end turn: Game not initialized",
			{}
		)
		error_occurred.emit(_err.message)
		return

	# Validation: Actions queued
	if state.queued_actions.is_empty():
		var _err = ErrorHandler.warning(  # Underscore prefix indicates intentionally unused
			ErrorHandler.Category.TURN,
			"Cannot end turn: No actions queued",
			{"turn": state.turn, "phase": GameState.TurnPhase.keys()[state.current_phase]}
		)
		error_occurred.emit("No actions queued")
		return

	# Validation: Check phase (should be in ACTION_SELECTION)
	if state.current_phase != GameState.TurnPhase.ACTION_SELECTION:
		var phase_name = GameState.TurnPhase.keys()[state.current_phase]
		ErrorHandler.warning(
			ErrorHandler.Category.TURN,
			"Ending turn in unexpected phase",
			{"turn": state.turn, "phase": phase_name}
		)

	ErrorHandler.info(
		ErrorHandler.Category.TURN,
		"Ending turn",
		{
			"turn": state.turn,
			"queued_actions": state.queued_actions.size(),
			"actions": state.queued_actions
		}
	)

	print("[GameManager] Executing turn...")
	turn_phase_changed.emit("turn_end")

	# L2 (ADR-0011): Attention was already spent at queue time (month_plan.attention_spent);
	# the retired per-turn AP pool is no longer debited here.

	# Execute all queued actions
	var result = turn_manager.execute_turn()

	# Validate turn execution result
	if not result.has("success") or not result.has("action_results"):
		ErrorHandler.report_err(
			ErrorHandler.Category.TURN,
			"Invalid turn execution result",
			{"result_keys": result.keys()}
		)

	# Emit results
	for action_result in result["action_results"]:
		action_executed.emit(action_result)

	# Emit updated state
	game_state_updated.emit(state.to_dict())

	# Check for triggered events
	if result.has("triggered_events"):
		var triggered_events = result["triggered_events"]
		for event in triggered_events:
			event_triggered.emit(event)

	# If game not over, start next turn
	if not state.game_over:
		await get_tree().create_timer(0.5).timeout
		start_next_turn()
	else:
		ErrorHandler.info(
			ErrorHandler.Category.GAME_STATE,
			"Game ended",
			{"victory": state.victory, "final_turn": state.turn}
		)

func start_next_turn():
	"""Begin next turn - FIX #418: Events before actions"""
	print("[GameManager] Starting turn %d" % (state.turn + 1))

	var turn_result = turn_manager.start_turn()

	# Emit phase (might be "turn_start" if events pending, or "action_selection" if not)
	turn_phase_changed.emit(turn_result["phase"])

	# Emit messages
	for message in turn_result["messages"]:
		action_executed.emit({"success": true, "message": message})

	# Emit updated state
	game_state_updated.emit(state.to_dict())

	# Emit triggered events if any (FIX #418)
	if turn_result.has("triggered_events") and turn_result["triggered_events"].size() > 0:
		print("[GameManager] %d event(s) triggered - blocking action selection" % turn_result["triggered_events"].size())
		for event in turn_result["triggered_events"]:
			event_triggered.emit(event)
	else:
		# No events, emit available actions
		var actions = turn_manager.get_available_actions()
		actions_available.emit(actions)

# ============================================================================
# MONTH LOOP (L1 / ADR-0009) -- the playable turn path
#
# The End Turn button routes HERE. end_turn() above is the pre-L1 single day-step
# and survives only behind the DEV MODE overlay (debug escape hatch). Flow:
#   plan commit -> execute the open plan turn -> day-tick playback (visible date
#   advance, auto-pause on response windows presented via the event_dialog) ->
#   month boundary -> review dialog -> next plan phase (boundary tick held open).
# Guard rule (sacred): no routine decision hangs on a day tick -- only windows pause.
# ============================================================================

func attend_conference_trip(conf_id: String) -> Dictionary:
	"""Commit to a conference and resolve the whole away window (ADR-0014 rhythm-break shell).

	The SIM half runs here and finishes before the player sees anything: ConferenceTrip
	drives real day-ticks through the existing MonthController, so the outcome is fully
	determined at commit time and replays identically. The PRESENTATION half (fade ->
	vignette scene -> fade -> return backlog panel) is theatre over an already-decided
	result -- the caller navigates after this returns success.

	Returns the trip record (see ConferenceTrip.run_trip), or {success:false, message} if
	the commit was refused."""
	if not is_initialized:
		error_occurred.emit("Cannot attend: Game not initialized")
		return {"success": false, "message": "Game not initialized"}
	# Stop any in-flight timer-driven month playback first: the away window advances the same
	# ticks synchronously, and two drivers on one MonthController would interleave.
	month_playback_active = false
	var trip: Dictionary = ConferenceTrip.run_trip(state, month_controller, conf_id)
	if not bool(trip.get("success", false)):
		error_occurred.emit(String(trip.get("message", "Cannot attend that conference")))
		return trip
	last_conference_trip = trip
	print("[GameManager] Conference trip resolved: %s, turns %d..%d, %d backlog items%s" % [
		conf_id, int(trip.get("start_turn", 0)), int(trip.get("end_turn", 0)),
		(trip.get("backlog", []) as Array).size(),
		" (CUT SHORT)" if bool(trip.get("cut_short", false)) else ""])
	game_state_updated.emit(state.to_dict())
	return trip


func resume_in_place() -> void:
	"""Re-attach a freshly-loaded main.tscn to the ALREADY-RUNNING game (conference return).

	Mirrors the tail of load_saved_game() minus the loading: push state and the action list
	to the new view. It deliberately does NOT surface pending events -- the return backlog
	panel is the single surface on arrival (feed-channel discipline / the #877 modal-stacking
	lesson). The caller surfaces events afterwards via surface_pending_events()."""
	pending_resume = false
	if not is_initialized or state == null:
		return
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	game_state_updated.emit(state.to_dict())
	turn_phase_changed.emit("action_selection")
	actions_available.emit(turn_manager.get_available_actions())


func surface_pending_events() -> void:
	"""Open any window that came home still unanswered (a trip cut short by an unignorable
	event). Called AFTER the return backlog panel is dismissed, so the player never faces a
	panel and a dialog at the same time."""
	if not is_initialized or state == null or state.pending_events.is_empty():
		return
	turn_phase_changed.emit("turn_start")
	for event in state.pending_events:
		event_triggered.emit(WindowResolver.present_for_dialog(event))


func end_month():
	"""Commit the queued actions as this month's plan and play the month out day by day."""
	if not is_initialized:
		error_occurred.emit("Cannot end month: Game not initialized")
		return
	if month_playback_active:
		return  # already playing the month out
	if state.queued_actions.is_empty():
		# Soft-lock fix: a month with no ACCEPTED actions (e.g. overbooking rejected them all
		# while phantom UI tiles suppressed the pass net) must NOT hard-error. Route through the
		# canonical pass so COMMIT THE MONTH always advances. Determinism-safe: pass id, cost 0,
		# identical to the Do Nothing path. (Phantom-tile cleanup + overbook "teeth" = fast-follow.)
		state.queued_actions.append(GameActions.PASS_ACTION_ID)

	print("[GameManager] Committing month plan (%d actions)..." % state.queued_actions.size())
	turn_phase_changed.emit("turn_end")

	# Dev-mode observability only (no-op in a release cut): time the synchronous month-commit
	# (the CPU-heavy plan execution -- day-tick playback below is timer-paced, not worth timing).
	# stop() runs on BOTH exit paths (game-over early return + normal). Zero sim/RNG effect.
	var _perf := PerfLog.time_section("month_commit", {"turn": state.turn})

	# Execute the OPEN plan turn (started at the previous boundary / game start).
	# L2 (ADR-0011): Attention was spent at queue time; per-action self-charging (the hiring
	# pipeline, etc.) also debits Attention HERE, at execution. No per-turn AP pool debit.
	var result = turn_manager.execute_turn()
	if result.has("action_results"):
		for action_result in result["action_results"]:
			action_executed.emit(action_result)
	game_state_updated.emit(state.to_dict())
	if state.game_over:
		_perf.stop()
		return

	# Implicit reserve (v1): every Attention point NOT spent by this month's executed actions
	# now guards the response windows during day-tick playback (_run_month_playback, below).
	# This MUST run AFTER execute_turn: execution-time self-charging actions (hiring pipeline)
	# spend from `available` (= total - spent - reserved); setting the reserve first drives
	# available to 0 and starves them. Reserving the post-execution remainder is both the fix
	# and the correct semantics -- the reserve protects what's left once commitments have run.
	# The full plan screen makes this an explicit dial.
	if state.month_plan != null:
		state.month_plan.set_reserve(state.month_plan.attention_total - state.month_plan.attention_spent)

	_perf.stop()
	month_playback_active = true
	_run_month_playback()  # async -- runs day ticks until window-pause or month boundary


func _run_month_playback() -> void:
	"""Advance visible day ticks until a window pauses playback or the month boundary is
	reached. Feed items surface as log lines (pull, no acknowledgment); only windows
	interrupt. Resumes from resolve_event when a pause is answered."""
	# Dev-mode tripwire (observation only, no-op in a release cut): a month is ~28-31 day
	# ticks and windows/boundaries end playback. If this loop ever runs away (a divide-by-one
	# / never-reaches-boundary "infi-glitch"), PerfLog flags it LOUD. It does NOT break the
	# loop -- steering game flow from the logger would fork behavior.
	var _tick_iters := 0
	while month_playback_active and state != null and not state.game_over:
		_tick_iters += 1
		PerfLog.check_iterations("month_playback", _tick_iters, 400, {"turn": state.turn})
		await get_tree().create_timer(day_tick_seconds).timeout
		if not month_playback_active or state == null or state.game_over:
			break
		# A4: last reading BEFORE the tick. If this tick turns out to be the boundary, this is
		# the true end-of-month state -- captured before _open_plan_month charges the new
		# month's rent. See the _last_tick_stats declaration.
		_last_tick_stats = _capture_month_stats()
		var r: Dictionary = month_controller.advance_tick()
		game_state_updated.emit(state.to_dict())
		for item in r.get("feed", []):
			var fev: Dictionary = item.get("event", {})
			# #789: feed items tagged toast=true (hiring surfacing, e.g. "interview took
			# place") also raise a transient notification; the feed line below stays the
			# persistent record. View-only -- no sim effect.
			if bool(fev.get("toast", false)):
				NotificationManager.info(String(fev.get("message", fev.get("name", ""))))
			# P0: carry the event's channel so the feed UI can filter the low-severity
			# arxiv/flavour stream out of the default view (EventService tags it "flavour").
			action_executed.emit({"success": true,
				"channel": String(fev.get("channel", "normal")),
				"message": "[color=gray]FEED | %s -- %s[/color]" % [
				String(item.get("source_id", "?")), String(fev.get("name", fev.get("id", "update")))]})
		match String(r.get("status", "")):
			"paused_on_window":
				turn_phase_changed.emit("turn_start")
				for w in month_controller.window_queue:
					# AP pre-stripped so the dialog's cost display matches what window
					# resolution actually charges (Attention, not AP) -- and the window's
					# OWN Attention price stamped on for display, which the strip alone
					# never disclosed (playtest 2026-08-10, the stray cat).
					event_triggered.emit(WindowResolver.present_for_dialog(w))
				return  # playback resumes via resolve_event once answered
			"month_open":
				_finish_month_playback()
				return
	# Loop left by game-over/teardown.
	month_playback_active = false
	if state != null:
		game_state_updated.emit(state.to_dict())


func _finish_month_playback() -> void:
	"""Month boundary reached: stop playback and present the month review (a plain dialog,
	v1). The boundary tick is HELD OPEN as the new month's plan phase -- the next
	end_month() executes it (MonthController.month_open_pending)."""
	month_playback_active = false
	var label := Clock.month_label(state.turn, state.start_year, state.start_month, state.start_day)
	var attention_now: int = state.month_plan.available() if state.month_plan else 0

	# A4: end-of-month reading is the pre-boundary tick where we have one; a run resumed from a
	# save (or a boundary reached without ticking) falls back to the live state.
	var end_stats: Dictionary = _last_tick_stats if not _last_tick_stats.is_empty() else _capture_month_stats()

	# A1 (Pip, [3:45]): "funds is good, but I CAN SEE THAT UP HERE, so this is NOT FRESH
	# INFORMATION." The Funds/Doom/Staff LEVEL line is gone -- the top bar owns funds, the doom
	# meter owns doom, the roster owns staff. What the HUD cannot show is what MOVED over the
	# month, so that is all this block prints, and only for stats that actually moved.
	#
	# The two blocks are COLLECTED as rows and then formatted, rather than built straight to
	# text, because the review now has two consumers: the feed record (text, below) and the
	# clipboard presenter (MonthReviewPanel, which needs the parts separately so a delta can be
	# coloured and right-aligned instead of living inside a sentence). Collect-then-format keeps
	# one source for both -- the strings below are assembled from the SAME rows the panel draws,
	# so the two can never drift. Collection also runs exactly ONCE per boundary: the rivals
	# collector advances _rival_cap_snapshot, so calling it twice would report every rival flat.
	var attention_line := "Attention: %d fresh decisions this month (last month's unspent reserve evaporated -- no banking)." % attention_now
	var movement_rows := _collect_month_movement_rows(_month_stat_snapshot, end_stats)
	var rival_rows := _collect_rivals_review_rows()
	var closing_line := "Queue this month's actions, then press COMMIT THE MONTH to play the month out."
	var body := "%s begins.\n\n%s%s%s" % [
		label, attention_line,
		_format_month_movement_section(movement_rows),
		_format_rivals_review_section(rival_rows)]

	var review := {
		"id": MONTH_REVIEW_EVENT_ID,
		"name": "Month Review -- %s" % label,
		# Name the control the player can actually see. "End Turn" is the internal name for this
		# commit (end_month() below, the EndTurnButton node); the BUTTON is labelled
		# "COMMIT THE MONTH >". This popup is the most-repeated instruction in the game -- once a
		# month, every month -- so it was also the most-repeated wrong one.
		"description": "%s\n\n%s" % [body, closing_line],
		"type": "popup",
		"options": [
			{"id": "begin_planning", "text": "Begin planning %s" % label, "costs": {}, "effects": {}}
		],
		# PRESENTATION PAYLOAD -- the same content as "description", handed over pre-split so the
		# clipboard presenter can typeset it (MonthReviewPanel.build). Every string in here is
		# already in "description"; nothing is computed for the panel that the text does not also
		# say. A presenter that ignores this key still renders the full review from "description",
		# which is what every non-review event dialog does.
		"review": {
			"heading": "Month Review",
			"period": label,
			"lede": "%s begins." % label,
			"attention": attention_line,
			"movement_title": "Last month's movement",
			"movement": movement_rows,
			"rivals_title": "Rivals this month",
			"rivals": rival_rows,
			"closing": closing_line,
		},
	}
	# A10: the review is also the WATCH feed's permanent record, so dismissing the popup costs
	# the player nothing and months can be compared by scrolling back. Emitted BEFORE the popup
	# so the feed line exists even if the popup is torn down by some other path.
	_log_month_review_to_feed(review.get("name", ""), body)
	event_triggered.emit(review)

	# The new month has begun; this reading is the baseline the NEXT review measures against.
	_month_stat_snapshot = _capture_month_stats()


func _capture_month_stats() -> Dictionary:
	"""A4: the three headline stats, read off live state. Display-only, no RNG, no writes."""
	if state == null:
		return {}
	return {
		"money": float(state.money),
		"doom": float(state.doom),
		"staff": int(state.get_total_staff()),
	}


func _build_month_movement_section(start_stats: Dictionary, end_stats: Dictionary) -> String:
	"""A4: start -> end movement for the month just played. Returns "" when there is no
	baseline (first month of a run, or a freshly loaded save) or when nothing moved -- a
	'Funds unchanged' line would be exactly the non-fresh information A1 deleted.

	Doom is reported as BAND movement only, never a number and never per-cause. ADR-0015 makes
	doom a computed consequence of world state, so a printed per-source delta would be a lie
	about how doom works; per-cause attribution stays behind the paid doom-breakdown instrument
	(ADR-0001, spending-buys-sight). A start/end band comparison is world-state display, using
	ThemeManager's canonical band labels -- the same non-color channel the HUD already uses."""
	return _format_month_movement_section(_collect_month_movement_rows(start_stats, end_stats))


func _collect_month_movement_rows(start_stats: Dictionary, end_stats: Dictionary) -> Array:
	"""The movement block as ROWS rather than text -- see _finish_month_playback for why the
	collect/format split exists. Each row carries the pieces the clipboard panel aligns into
	columns (`stat` / `from` / `to` / `delta`) AND the exact `line` the feed record prints, so
	the two renderings are the same content by construction.

	`sign` is the DISPLAY sign only: -1 reads as an adverse move, +1 as a favourable one, 0 as
	neither. It is what colours a delta; nothing downstream may treat it as a magnitude.
	Doom follows the HUD's inversion (main_ui._render_delta_chip: doom rising is bad)."""
	var rows: Array = []
	if start_stats.is_empty() or end_stats.is_empty():
		return rows

	var money_start := float(start_stats.get("money", 0.0))
	var money_end := float(end_stats.get("money", 0.0))
	if not is_equal_approx(money_start, money_end):
		var money_delta := money_end - money_start
		var money_text := "%s%s" % [
			"+" if money_delta > 0.0 else "-", GameConfig.format_money(abs(money_delta))]
		rows.append({
			"stat": "Funds",
			"from": GameConfig.format_money(money_start),
			"to": GameConfig.format_money(money_end),
			"delta": money_text,
			"sign": 1 if money_delta > 0.0 else -1,
			"line": "  Funds   %s -> %s   (%s)" % [
				GameConfig.format_money(money_start), GameConfig.format_money(money_end), money_text],
		})

	var staff_start := int(start_stats.get("staff", 0))
	var staff_end := int(end_stats.get("staff", 0))
	if staff_start != staff_end:
		var staff_text := "%s%d" % [
			"+" if staff_end > staff_start else "-", abs(staff_end - staff_start)]
		rows.append({
			"stat": "Staff",
			"from": str(staff_start),
			"to": str(staff_end),
			"delta": staff_text,
			"sign": 1 if staff_end > staff_start else -1,
			"line": "  Staff   %d -> %d   (%s)" % [staff_start, staff_end, staff_text],
		})

	var doom_start := float(start_stats.get("doom", 0.0))
	var doom_end := float(end_stats.get("doom", 0.0))
	var doom_move := _doom_band_movement(doom_start, doom_end)
	if doom_move != "":
		# ADR-0015: bands, never numbers. The panel gets the two BAND LABELS, which is exactly
		# what the sentence already contains -- no percentage is added to the payload.
		var crossed_up := ThemeManager.get_doom_band_index(doom_end) > ThemeManager.get_doom_band_index(doom_start)
		rows.append({
			"stat": "Doom",
			"from": ThemeManager.get_doom_status_label(doom_start),
			"to": ThemeManager.get_doom_status_label(doom_end),
			"delta": "crossed up" if crossed_up else "eased down",
			"sign": -1 if crossed_up else 1,
			"line": "  Doom    %s" % doom_move,
		})

	return rows


func _format_month_movement_section(rows: Array) -> String:
	"""Rows -> the feed/description text. Byte-identical to what this block has always printed."""
	if rows.is_empty():
		return ""
	var lines: Array[String] = []
	for row in rows:
		lines.append(String(row.get("line", "")))
	return "\n\nLast month's movement:\n" + "\n".join(lines)


func _doom_band_movement(doom_start: float, doom_end: float) -> String:
	"""A4/ADR-0015: band crossing only. "" when the band did not change -- an unchanged band is
	already legible on the doom meter, so printing it would re-open the A1 complaint."""
	var band_start := ThemeManager.get_doom_band_index(doom_start)
	var band_end := ThemeManager.get_doom_band_index(doom_end)
	if band_start == band_end:
		return ""
	var direction := "crossed up" if band_end > band_start else "eased down"
	return "%s -> %s   (%s)" % [
		ThemeManager.get_doom_status_label(doom_start), ThemeManager.get_doom_status_label(doom_end),
		direction]


func _log_month_review_to_feed(review_name: String, body: String) -> void:
	"""A10 (Pip, [3:49] "it's actually just kind of popping up and blocking the screen"): half
	of why the modal feels bad is that dismissing it DESTROYS the only copy. Mirror every
	review into the WATCH feed so closing it is free and past months stay comparable.

	Channel "review" is new and unfiltered -- the existing toggles suppress only "flavour"
	(the arxiv flood) and "rivals" (the intel toggle), so a review can never be silently
	hidden. This is a palliative for the blocking complaint, not the fix: A5 (review as a
	panel, or docked into the plan screen) is the structural answer and is NOT in this PR."""
	var block := "[color=cyan]== %s ==[/color]" % review_name
	for raw_line in body.split("\n"):
		var line := String(raw_line).strip_edges()
		if line == "":
			continue
		block += "\n[color=gray]  %s[/color]" % line
	action_executed.emit({"success": true, "channel": "review", "message": block})


func _build_rivals_review_section() -> String:
	"""Rivals this month (item 2): a short block in the month review naming each VISIBLE
	rival, its focus, and a qualitative capability-drift read since last review. Returns ""
	when nothing is visible so the review stays clean. Deadpan register, display-only (no
	RNG, no sim reads that could move determinism)."""
	return _format_rivals_review_section(_collect_rivals_review_rows())


func _collect_rivals_review_rows() -> Array:
	"""The rivals block as ROWS. NOT idempotent -- it advances _rival_cap_snapshot, so the next
	call reports every rival flat. Call it once per month boundary and pass the rows around
	(_finish_month_playback does); _build_rivals_review_section is the single-call text wrapper.

	`heat` is a DISPLAY band for the qualitative drift label, not a number the player ever sees:
	0 flat, 1 slipping, 2 rising, 3 climbing fast. It exists so the panel can weight a rival that
	is running away from you differently from one standing still, without printing a magnitude
	the review has never printed."""
	var rows: Array = []
	if state == null:
		return rows
	for rival in state.rival_labs:
		if not rival.is_visible_to_player():
			continue
		var rid: String = rival.id
		var prev: float = float(_rival_cap_snapshot.get(rid, rival.capability_progress))
		var delta: float = rival.capability_progress - prev
		var drift: String = RivalLabs.capability_drift_label(delta)
		_rival_cap_snapshot[rid] = rival.capability_progress
		# Thresholds mirror RivalLabs.capability_drift_label -- same cuts, so the band and the
		# words can never disagree about which rival is moving.
		var heat := 0
		if delta > 8.0:
			heat = 3
		elif delta > 0.5:
			heat = 2
		elif delta < -0.5:
			heat = 1
		rows.append({
			"name": rival.get_visible_name(),
			"focus": String(rival.focus),
			"drift": drift,
			"heat": heat,
			"line": "  %s (%s) -- %s" % [rival.get_visible_name(), rival.focus, drift],
		})
	return rows


func _format_rivals_review_section(rows: Array) -> String:
	"""Rows -> the feed/description text. Byte-identical to what this block has always printed."""
	if rows.is_empty():
		return ""
	var lines: Array[String] = []
	for row in rows:
		lines.append(String(row.get("line", "")))
	return "\n\nRivals this month:\n" + "\n".join(lines)


func get_game_state() -> Dictionary:
	if state:
		return state.to_dict()
	return {}

# ============================================================================
# SAVE / LOAD (L7, #618) -- mid-game snapshot, full-state fidelity
# ============================================================================

func _release_game_objects() -> void:
	"""Free the previous game's Node-derived objects before a new game / load replaces them.

	GameState, DoomSystem, RiskPool and TurnManager all extend Node but are NEVER added to
	the scene tree, so simply reassigning `state`/`turn_manager` orphans them -- 4 leaked
	Nodes per game (confirmed by GUT's orphan monitor). Ledger and MonthController are
	RefCounted and free themselves. Every external reader reaches these via `state.doom_system`
	etc. (re-fetched from the current state), so no live reference survives a reset.
	queue_free() is deferred and safe to call on an off-tree node."""
	if state != null and is_instance_valid(state):
		if state.doom_system != null and is_instance_valid(state.doom_system):
			state.doom_system.queue_free()
		if state.risk_system != null and is_instance_valid(state.risk_system):
			state.risk_system.queue_free()
		state.queue_free()
	if turn_manager != null and is_instance_valid(turn_manager):
		turn_manager.queue_free()

func save_game(path: String = SaveLoad.QUICKSAVE_PATH) -> bool:
	"""Snapshot the current game to a save file. Safe to call from the pause menu."""
	if not is_initialized or state == null:
		error_occurred.emit("Cannot save: no game in progress")
		return false
	var err := SaveLoad.save_game(state, path)
	if err != OK:
		error_occurred.emit("Save failed (error %d)" % err)
		return false
	action_executed.emit({"success": true, "message": "Game saved (turn %d)" % state.turn})
	return true

func load_saved_game(path: String = SaveLoad.QUICKSAVE_PATH, force: bool = false) -> bool:
	"""Restore a saved game and resume exactly where it left off (phase, queued
	actions, pending events, rng stream). Returns false if no/corrupt save.

	Self-guard (scene-reentry run-killer family, sibling of #979): same rule as
	start_new_game -- refuses to clobber a live run unless force=true. The one
	legitimate caller (main_ui._boot_game's queued-load branch) passes force=true;
	it only fires straight off a fresh main.tscn boot, before any run exists."""
	if is_initialized and not force:
		push_warning("[GameManager] load_saved_game() REFUSED: a game is already live (is_initialized=true) and force=false would silently destroy it. Pass force=true if this is a deliberate load-over.")
		PerfLog.mark("load_saved_game_refused", {"turn": state.turn if state != null else -1})
		return false
	var envelope := SaveLoad.load_envelope(path)
	if envelope.is_empty():
		error_occurred.emit("No save found to load")
		return false
	var loaded := SaveLoad.restore_state(envelope)
	if loaded == null:
		error_occurred.emit("Save file is corrupt or incompatible")
		return false
	# Drop the old game's Node subsystems (state + doom/risk + turn_manager). The previous
	# code freed only `state`, leaking its orphaned doom_system/risk_system and the old
	# turn_manager on every load.
	_release_game_objects()
	_rival_cap_snapshot.clear()  # drift baseline restarts from the loaded snapshot
	# A4: the movement baseline is NOT serialized (display-only). A loaded run therefore shows
	# no movement block on its first review, then resumes normally -- degrade quietly rather
	# than print a delta measured against a month the player did not play.
	_month_stat_snapshot.clear()
	_last_tick_stats.clear()
	state = loaded
	# Alpha Tools flag travels WITH the save (decision card 2026-08-01): restore the
	# ENVELOPE's value -- default clean for pre-feature saves. Restoring (not OR-ing)
	# means a save/load cycle can neither launder a tainted run (the flag was saved
	# with it) nor smear this session's taint onto a genuinely clean save.
	GameConfig.alpha_tools_used = bool(envelope.get("alpha_tools_used", false))
	GameConfig.alpha_tools_first_use_turn = int(envelope.get("alpha_tools_first_use_turn", -1))
	# Scenario custom events live as node meta (Issue #483), not in state
	# serialization -- re-attach them from the pack recorded in the envelope.
	var save_scenario_id := String(envelope.get("scenario_id", ""))
	if not save_scenario_id.is_empty():
		var loader = ScenarioLoader.new()
		var scenario = loader.load_scenario(save_scenario_id)
		loader.free()  # extends Node, never added to the tree -- dropping it orphans it
		var custom_events = scenario.get("events", [])
		if custom_events.size() > 0:
			state.set_meta("scenario_events", custom_events)
	turn_manager = TurnManager.new(state)
	# L1: rebuild the month playback driver; if the save was taken paused on a window,
	# rehydrate re-enters the paused state so playback resumes at that window.
	month_controller = MonthController.new(state, turn_manager)
	month_controller.rehydrate_from_state()
	month_playback_active = false
	is_initialized = true
	# NOTE: replay verification rebuilds from turn 0 (ADR-0006); a loaded session
	# is a snapshot continuation, so tracking restarts here only to keep the
	# in-turn recording calls alive -- the artifact is not replay-verifiable.
	VerificationTracker.start_tracking(state.game_seed_str, GameConfig.CURRENT_VERSION, [], "", GameConfig.get_board_version())
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	print("[GameManager] Loaded save %s -- turn %d, phase %s" % [
		path, state.turn, GameState.TurnPhase.keys()[state.current_phase]])
	game_state_updated.emit(state.to_dict())
	if state.pending_events.size() > 0:
		# Saved mid-event-resolution: surface the pending events again.
		turn_phase_changed.emit("turn_start")
		for event in state.pending_events:
			event_triggered.emit(event)
	else:
		turn_phase_changed.emit("action_selection")
		actions_available.emit(turn_manager.get_available_actions())
	return true

func resolve_event(event: Dictionary, choice_id: String) -> Dictionary:
	"""Handle player's event choice - FIX #418: Use TurnManager.
	L1: month-review dialogs and paused-playback windows route to the month loop first;
	only plan-phase events (game start / legacy path) reach TurnManager below.

	Returns the resolution result {success, message, ...}. The caller (MainUI._on_event_
	choice_selected) reads success/message to decide whether to CLOSE the event_dialog or keep
	it open with the failure reason (direction-b, playtest 2026-07-24): an unaffordable window
	HANDLE returns {success:false} so the dialog stays up instead of faking acceptance."""
	if not is_initialized:
		error_occurred.emit("Game not initialized")
		return {"success": false, "message": "Game not initialized"}

	# L1: the synthetic month-review dialog just closes into the new plan phase.
	if String(event.get("id", "")) == MONTH_REVIEW_EVENT_ID:
		action_executed.emit({"success": true, "message": "[color=cyan]-- %s --[/color]" % String(event.get("name", "New month"))})
		game_state_updated.emit(state.to_dict())
		turn_phase_changed.emit("action_selection")
		actions_available.emit(turn_manager.get_available_actions())
		return {"success": true, "message": ""}

	# L1: while day-tick playback is paused on response windows, choices route through the
	# month controller (Attention payment, replay payment_source), not the legacy path.
	# Also covers a save loaded mid-pause (controller rehydrated paused, playback inactive).
	if month_controller != null and month_controller.is_paused():
		# Pass the event the dialog presented so the option resolves against THAT window,
		# not blindly window_queue[0] (a prior unresolved window would otherwise desync the
		# head from the dialog -> bogus "Unknown option", playtest 2026-07-24).
		# allow_auto_lapse defaults FALSE: an unaffordable HANDLE returns a plain failure and
		# the window stays queued, kept answerable by the still-open dialog (no orphan/lapse).
		var wresult: Dictionary = month_controller.resolve_current_window_option(choice_id, event)
		if wresult.get("success", false):
			action_executed.emit(wresult)
			game_state_updated.emit(state.to_dict())
			if not month_controller.is_paused():
				# Queue answered: either the boundary plan phase opens, or ticking resumes.
				if month_controller.month_open_pending:
					_finish_month_playback()
				else:
					month_playback_active = true
					_run_month_playback()
		else:
			error_occurred.emit(String(wresult.get("message", "Window resolution failed")))
		return wresult

	# Use TurnManager's resolve_event which handles phase transitions
	var result = turn_manager.resolve_event(event, choice_id)

	if result["success"]:
		action_executed.emit(result)
		game_state_updated.emit(state.to_dict())

		# If all events resolved, transition to action selection
		if result.get("phase_transitioned", false):
			print("[GameManager] All events resolved - transitioning to action selection")
			turn_phase_changed.emit("action_selection")
			# Now emit available actions
			var actions = turn_manager.get_available_actions()
			actions_available.emit(actions)
	else:
		error_occurred.emit(result.get("error", result.get("message", "Event resolution failed")))
	return result

func _apply_difficulty_settings():
	"""Apply difficulty modifiers to game state"""
	# Validate difficulty value first (fix #447 - crash on invalid difficulty)
	if typeof(GameConfig.difficulty) != TYPE_INT:
		print("[GameManager] ERROR: Invalid difficulty type (expected int, got %s), defaulting to Standard" % typeof(GameConfig.difficulty))
		GameConfig.difficulty = 1
	elif GameConfig.difficulty < 0 or GameConfig.difficulty > 2:
		print("[GameManager] ERROR: Invalid difficulty value (%d), defaulting to Standard" % GameConfig.difficulty)
		GameConfig.difficulty = 1

	# LEAGUE LOCK (#1058, enforced HERE per #1084): consume effective_difficulty(),
	# never the raw field. The raw field is written freely by Settings and persisted
	# in config.cfg, and pregame_setup is only one of six routes into main.tscn --
	# enforcing at the single place difficulty becomes game state is what makes
	# "every board entry is a Standard run" a property of the design instead of an
	# accident of routing.
	var effective: int = GameConfig.effective_difficulty()
	if effective != GameConfig.difficulty:
		print("[GameManager] League lock: stored difficulty %d plays as %s (#1058/#1084)" % [GameConfig.difficulty, GameConfig.get_effective_difficulty_string()])

	# Difficulty modifiers come from the Balance surface ("difficulty.*", L9 #621).
	# T2: difficulty scales the MONTHLY ATTENTION GRANT, not a per-turn AP cap (the AP pool
	# is deleted). Fallbacks keep the old easy/standard/hard ORDERING at the Attention
	# denomination (24 / 20 / 16 against a 20 default grant).
	match effective:
		0:  # Easy
			print("[GameManager] Applying EASY difficulty modifiers")
			state.money *= Balance.num("difficulty.easy.money_multiplier", 1.5)  # 50% more starting money
			_set_attention_grant(Balance.inum("difficulty.easy.attention_per_month", 24))
		1:  # Standard
			print("[GameManager] Applying STANDARD difficulty (default)")
			state.money *= Balance.num("difficulty.standard.money_multiplier", 1.0)
			_set_attention_grant(Balance.inum("difficulty.standard.attention_per_month", 20))
		2:  # Hard
			print("[GameManager] Applying HARD difficulty modifiers")
			state.money *= Balance.num("difficulty.hard.money_multiplier", 0.75)  # 25% less starting money
			_set_attention_grant(Balance.inum("difficulty.hard.attention_per_month", 16))
		_:  # Safety default case (should never reach here after validation)
			print("[GameManager] WARNING: Unexpected difficulty value, using Standard")
			# Apply standard difficulty (no changes)


func _set_attention_grant(per_month: int) -> void:
	"""Set the founder's monthly Attention grant and re-open the CURRENT month at the new
	size. Difficulty/scenario overrides are applied AFTER GameState.reset() has opened month
	0, so the grant has to be restated -- month 0 is untouched at that point (nothing spent),
	which is why a plain re-begin is safe here and would not be mid-month."""
	state.attention_per_month = per_month
	if state.month_plan != null:
		# `per_month` is the MODIFIER we just stored, not the budget. Re-open through the
		# derivation point so difficulty/scenario grants pass through the same one function
		# as everything else (2026-08-12 ruling). Same number today, by contract.
		# Month index from the plan's own ordinal, not from `turn`: this restates the month
		# the plan is currently on, which at setup time is month 0 and would be the same
		# either way, but stays correct if it is ever called later.
		var mi: int = Clock.month_index(0, state.start_year, state.start_month, state.start_day) \
			+ state.month_plan.month_ordinal
		var capacity: Dictionary = state.capacity_for_month(mi)
		state.month_plan.begin_month(int(capacity["value"]), state.month_plan.month_ordinal)

func _apply_scenario_overrides():
	"""Apply scenario pack overrides to game state (Issue #483)"""
	var scenario_id = GameConfig.scenario_id
	if scenario_id.is_empty():
		return  # Standard game, no overrides

	var loader = ScenarioLoader.new()
	var scenario = loader.load_scenario(scenario_id)
	loader.free()  # extends Node, never added to the tree -- dropping it orphans it
	# (one leaked Node per run on any machine with a scenario selected; this is what
	# reddened test_game_lifecycle_hygiene's orphan-delta assertion on 2026-07-31)

	if scenario.is_empty():
		push_warning("[GameManager] Failed to load scenario: %s" % scenario_id)
		return

	print("[GameManager] Applying scenario: %s" % scenario.get("title", scenario_id))

	# Apply starting resource overrides
	var resources = scenario.get("starting_resources", {})
	if resources.has("money"):
		state.money = float(resources["money"])
		print("  Money: %s" % GameConfig.format_money(state.money))
	if resources.has("compute"):
		state.compute = float(resources["compute"])
		print("  Compute: %.1f" % state.compute)
	if resources.has("research"):
		state.research = float(resources["research"])
		print("  Research: %.1f" % state.research)
	if resources.has("papers"):
		state.papers = float(resources["papers"])
		print("  Papers: %.1f" % state.papers)
	if resources.has("reputation"):
		state.reputation = float(resources["reputation"])
		print("  Reputation: %.1f" % state.reputation)
	if resources.has("doom"):
		state.doom = float(resources["doom"])
		if state.doom_system:
			state.doom_system.current_doom = state.doom
		print("  Doom: %.1f" % state.doom)
	# T2: scenario packs override the monthly ATTENTION grant. `action_points` is read as a
	# legacy alias so pre-migration scenario JSON keeps loading instead of silently doing
	# nothing (the scenario surface is content, and content lags a code migration).
	if resources.has("attention_per_month") or resources.has("action_points"):
		var grant: int = int(resources.get("attention_per_month", resources.get("action_points", 0)))
		_set_attention_grant(grant)
		print("  Attention per month: %d" % state.attention_per_month)
	if resources.has("stationery"):
		state.stationery = float(resources["stationery"])
		print("  Stationery: %.1f" % state.stationery)

	# Apply config overrides (start date, etc.)
	var config = scenario.get("config", {})
	if config.has("start_year"):
		state.start_year = int(config["start_year"])
	if config.has("start_month"):
		state.start_month = int(config["start_month"])
	if config.has("start_day"):
		state.start_day = int(config["start_day"])
	if config.has("start_year") or config.has("start_month") or config.has("start_day"):
		print("  Start date: %s" % state.get_formatted_date())

	# Register custom events
	var custom_events = scenario.get("events", [])
	if custom_events.size() > 0:
		print("  Custom events: %d" % custom_events.size())
		# Events will be accessed by GameEvents via ScenarioLoader
		# Store scenario events in state for TurnManager to access
		if not state.has_meta("scenario_events"):
			state.set_meta("scenario_events", custom_events)

	print("[GameManager] Scenario applied successfully")


# ============================================================================
# MONTH PLAN LAYER API (L1 / ADR-0009)
#
# Thin delegates exposing the plan-turn layer to callers (the new plan screen speaks
# ONLY through here -- main_ui.gd is left to die by attrition, per the LET-DIE map).
# The founder currency Attention lives on state.month_plan; response windows resolve
# through WindowResolver. The legacy per-turn AP loop above is untouched (L2 removes it).
# ============================================================================

func get_month_plan() -> MonthPlan:
	"""The current month's plan (Attention, reserve, in-flight strategic WIP), or null."""
	return state.month_plan if state else null


func set_attention_reserve(amount: int) -> bool:
	"""Explicitly hold `amount` Attention for response windows this month (plan-time)."""
	if state == null or state.month_plan == null:
		return false
	return state.month_plan.set_reserve(amount)


func queue_strategic_action(action_id: String, attention_cost: int, duration_ticks: int) -> bool:
	"""Queue a strategic action at plan speed -- spends Attention now, lands after its
	duration (ADR-0009 S5, nothing strategic resolves instantly)."""
	if state == null or state.month_plan == null:
		return false
	return state.month_plan.queue_strategic(action_id, attention_cost, duration_ticks, state.turn)


func resolve_window(event: Dictionary, response: String) -> Dictionary:
	"""Resolve a response window with a costed menu choice (handle_reserve /
	handle_cannibalize / defer / ignore). Delegates to WindowResolver; records the
	payment source into the replay artifact."""
	if state == null:
		return {"success": false, "message": "no active game"}
	return WindowResolver.resolve(state, state.month_plan, event, response, state.rng)


# ============================================================================
# HIRING PIPELINE (Phase B) -- thin delegates for the plan-screen hiring panel + tests.
# The mechanics live on state.hiring (HiringPipeline); these just forward through the
# GameManager the UI already speaks to. Targeted (candidate-specific) stages take a
# candidate_id; the no-target menu drivers live in GameActions (advertise/interview_next/...).
# ============================================================================

func get_hiring() -> HiringPipeline:
	return state.hiring if state else null


func hiring_advertise() -> Dictionary:
	"""SOURCE (advertise channel): launch a money-funded campaign that trickles candidates."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	return state.hiring.advertise(state)


func hiring_use_connections() -> Dictionary:
	"""SOURCE (connections channel): spend a favor for one fast pre-vetted lead."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	return state.hiring.use_connections(state)


func hiring_interview(candidate_id: String) -> Dictionary:
	"""INTERVIEW a specific pool candidate (triage) -> reveals their card after a delay."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	return state.hiring.launch_interview(state, candidate_id)


func hiring_offer(candidate_id: String, cash: float, promises: Array = []) -> Dictionary:
	"""OFFER a specific candidate `cash`, optionally attaching appetite promises (which mint
	ledger obligations on acceptance)."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	return state.hiring.make_offer(state, candidate_id, cash, promises)


func hiring_read(candidate_id: String, promises: Array = []) -> Dictionary:
	"""The recruiter/lieutenant negotiation read for a pool candidate (narrowed visible band)."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	var cand := state.hiring.find_pool_candidate(state, candidate_id)
	if cand == null:
		return {"success": false, "message": "no such candidate"}
	return state.hiring.negotiation_read(state, cand, promises)


func hiring_onboard_step(candidate_id: String, item: String) -> Dictionary:
	"""ONBOARD: complete one checklist item (laptop / visa / mentoring) for a new hire."""
	if state == null or state.hiring == null:
		return {"success": false, "message": "no active game"}
	return state.hiring.onboard_step(state, candidate_id, item)

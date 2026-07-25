class_name PlanController
extends RefCounted
## CARVE 1 (docs/MAIN_UI_SEAM_MAP.md, seam R4): the plan / attention / queue LOGIC pulled
## out of the main_ui.gd monolith. main_ui is now a thin view -- it RENDERS the plan and
## WIRES buttons to the calls here; it no longer owns queue/attention/cost math.
##
## This is a NON-FORKING extraction: every method below is a verbatim move of behaviour that
## previously lived in main_ui, wrapping the SAME existing engine surface
## (GameManager -> MonthPlan / MonthController). No gameplay/RNG/scoring change.
##
## What this owns:
##   * queued_actions -- the UI-facing MIRROR of the plan queue (Array of {id, name}). It is
##     the tentative plan the player is assembling on the PLAN screen; the authoritative
##     backend queue is state.queued_actions inside GameManager. The two are kept in step by
##     the mutation methods here (each mirror op has a matching GameManager op), exactly as
##     the pre-carve main_ui did inline.
##   * calculate_queued_costs() -- the turn-preview cost aggregation.
##   * the queue mutation primitives (queue / remove / clear / reset / reserve-all / pass net)
##     and the month commit, each wrapping the GameManager call the view used to make itself.
##
## What stays in the view (main_ui): all rendering (queue tiles, cost preview, buttons),
## danger-zone warnings, message-log lines, and PLAN<->WATCH screen transitions. Those read
## this controller's state and call these methods; they are not plan LOGIC.

var game_manager  # GameManager (untyped: it is an autoload-instanced node, no class_name coupling)

# The tentative plan-time queue the player is building. UI mirror only -- {id, name} entries.
# Rendering reads this directly (main_ui.update_queued_actions_display / QueueGantt); the
# authoritative attention/queue accounting lives in GameManager + MonthPlan.
var queued_actions: Array = []


func _init(gm = null) -> void:
	game_manager = gm


# --- Cost aggregation (was main_ui._calculate_queued_costs) -------------------------------

func calculate_queued_costs() -> Dictionary:
	"""Total the projected costs of every queued action for the turn preview. action_points is
	tracked separately as Attention, so it is skipped here (verbatim from the pre-carve view)."""
	var total_costs: Dictionary = {}
	for queued_action in queued_actions:
		var action_id = queued_action.get("id", "")
		var action_def: Dictionary = GameActions.get_action_by_id(action_id)
		var costs = action_def.get("costs", {})
		for resource in costs.keys():
			if resource == "action_points":
				continue  # AP is already tracked separately
			if not total_costs.has(resource):
				total_costs[resource] = 0
			total_costs[resource] += costs[resource]
	return total_costs


# --- Queue mutations ----------------------------------------------------------------------

func queue_action(action_id: String, action_name: String) -> void:
	"""Add an accepted action tile to the UI mirror. Callers gate on select_action() first
	(the backend accept/overbook check), exactly as the pre-carve view did -- so a rejected
	action never leaves a phantom tile (#821)."""
	queued_actions.append({"id": action_id, "name": action_name})


func select_action(action_id: String) -> bool:
	"""Backend accept gate for a founder action (Attention overbook check lives here). Returns
	false and emits the error via GameManager when the action cannot be committed."""
	return game_manager.select_action(action_id)


func remove_action(action_id: String) -> Dictionary:
	"""Remove a specific action from the queue and refund its Attention (via GameManager).
	Returns {removed: bool, attention_cost: int} so the view can log the refund. Mutates the
	UI mirror first, then the backend queue -- the two lists are independent (matched by id),
	so the order is behaviour-neutral; preserved as the pre-carve view had it."""
	var removed_index := -1
	for i in range(queued_actions.size()):
		if queued_actions[i].get("id") == action_id:
			removed_index = i
			break
	if removed_index < 0:
		return {"removed": false, "attention_cost": 0}
	queued_actions.remove_at(removed_index)
	game_manager.remove_queued_action(action_id)
	var action_def: Dictionary = GameActions.get_action_by_id(action_id)
	var attention_cost: int = action_def.get("costs", {}).get("action_points", 0)
	return {"removed": true, "attention_cost": attention_cost}


func clear_queue() -> bool:
	"""Clear-queue button path: drop every tentative action and REFUND the committed Attention
	(GameManager.clear_action_queue), then clear the UI mirror. Returns false (no-op) on an
	already-empty queue so the view can skip its log line."""
	if queued_actions.is_empty():
		return false
	game_manager.clear_action_queue()  # refunds Attention on the backend queue
	queued_actions.clear()
	return true


func reset_mirror() -> void:
	"""Clear ONLY the UI mirror, with NO refund. Used on COMMIT: the backend queue is consumed
	by end_month(), so refunding here would be wrong. This is the deliberate counterpart to
	clear_queue() -- the two 'clears' are NOT interchangeable (was two distinct inline paths
	in the pre-carve view)."""
	queued_actions.clear()


func queue_pass_fallback() -> String:
	"""COMMIT THE MONTH with nothing planned (#733 + overbook soft-lock net): queue the canonical
	pass action so the month always advances. Mirrors the tile AND routes select_action() so the
	backend queue is non-empty. Determinism-safe: pass mints no RNG. Returns the pass action name
	for the view's log line."""
	var pass_action := GameActions.get_pass_action()
	var pass_id: String = pass_action.get("id", GameActions.PASS_ACTION_ID)
	var pass_name: String = pass_action.get("name", "Do Nothing")
	queued_actions.append({"id": pass_id, "name": pass_name})
	game_manager.select_action(pass_id)
	return pass_name


func needs_pass_fallback() -> bool:
	"""True when COMMIT THE MONTH would otherwise submit an empty ACCEPTED queue (either the UI
	mirror or the backend queue is empty). Guards the pass net -- verbatim condition from the
	pre-carve view (phantom UI tiles must not suppress this net)."""
	if queued_actions.size() == 0:
		return true
	return game_manager.state != null and game_manager.state.queued_actions.is_empty()


func append_reserve_all() -> void:
	"""COMMIT PLAN with no queued actions == reactive strategy: hold all Attention for response
	windows. Adds a virtual 'Reserve All AP' mirror entry and appends the pass id straight onto
	the backend queue (costs {} -> no Attention committed). Verbatim from the pre-carve view
	(L0 #620: ONE pass id)."""
	var reserve_action := {
		"id": GameActions.PASS_ACTION_ID,
		"name": "Reserve All AP",
		"description": "No planned actions - keep all AP available for responding to events",
		"ap_cost": 0,
		"money_cost": 0
	}
	queued_actions.append(reserve_action)
	# Directly append to game state queue (bypass select_action validation) -- a virtual
	# "reserve all AP" entry; pass costs {} so no AP is committed.
	game_manager.state.queued_actions.append(GameActions.PASS_ACTION_ID)


func commit_month() -> void:
	"""Commit the assembled plan and hand control to day-tick playback (L1 / ADR-0009:
	auto-pause on windows, month review at the boundary). Wraps GameManager.end_month()."""
	game_manager.end_month()


# --- Read-through for the view ------------------------------------------------------------

func is_queue_empty() -> bool:
	return queued_actions.is_empty()


func queue_size() -> int:
	return queued_actions.size()

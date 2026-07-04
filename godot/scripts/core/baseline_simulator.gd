extends RefCounted
class_name BaselineSimulator
## Runs headless no-action game simulations for baseline comparison
## Issue #372: Enhanced scoring with baseline comparison
##
## BASELINE COMPUTATION MODES:
## 1. PRECOMPUTED (Weekly League): Baseline stored with seed metadata, zero client computation
##    - Use set_precomputed_baseline() before game starts
##    - Client fetches baseline from league/seed data
##
## 2. EAGER (Custom Games): Run baseline at game start in background
##    - Call start_background_simulation() during game loading
##    - Result ready by game end (no visible delay)
##
## 3. BLIND (Custom Games fallback): Run during gameplay or at end
##    - get_baseline_score() runs synchronously if not cached
##    - Player sees comparison only at game end
##
## BASELINE STRATEGY FOR EVENTS:
## The baseline simulation always picks the FIRST available choice for events.
## This represents a "passive/conservative" strategy:
## - Event choices are ordered with the safest/most neutral option first
## - The baseline represents "doing nothing actively wrong"
## - Player actions should improve upon this baseline
##
## To define custom event strategies, see _get_event_choice_for_baseline()

# Maximum turns to simulate (prevents infinite loops)
const MAX_TURNS: int = 200

# Computation modes
enum Mode {
	PRECOMPUTED,  # Baseline already computed (weekly league)
	EAGER,        # Compute at game start (background)
	BLIND         # Compute on-demand (may delay)
}

# Current mode and state
static var _current_mode: Mode = Mode.BLIND
static var _background_thread: Thread = null
static var _background_result: Dictionary = {}
static var _background_seed: String = ""
static var _is_computing: bool = false

# Cache baseline results to avoid re-simulation
static var _baseline_cache: Dictionary = {}  # seed -> {score: int, final_state: Dictionary}

# Precomputed baselines (from weekly league data)
static var _precomputed_baselines: Dictionary = {}  # seed -> {score: int, ...}

## ============================================================================
## PUBLIC API
## ============================================================================

static func set_precomputed_baseline(game_seed: String, baseline_data: Dictionary):
	"""
	Set a precomputed baseline (e.g., from weekly league server data).
	Call this before game starts when baseline is already known.

	baseline_data should contain: {score: int, turns: int, victory: bool, doom: float}
	"""
	_precomputed_baselines[game_seed] = baseline_data
	_baseline_cache[game_seed] = baseline_data
	_current_mode = Mode.PRECOMPUTED
	print("[BaselineSimulator] Precomputed baseline set for seed %s: Turn %d" % [game_seed, baseline_data.get("turns", 0)])

static func start_background_simulation(game_seed: String):
	"""
	Start baseline simulation in background (EAGER mode).
	Call this at game start - result will be ready by game end.
	"""
	# Don't start if already computing or cached
	if _is_computing or _baseline_cache.has(game_seed) or _precomputed_baselines.has(game_seed):
		return

	_current_mode = Mode.EAGER
	_background_seed = game_seed
	_is_computing = true

	print("[BaselineSimulator] Starting background simulation for seed: %s" % game_seed)

	# Use a thread for true background computation
	# Note: Godot's threading is limited, so we use call_deferred as fallback
	if OS.has_feature("threads"):
		_background_thread = Thread.new()
		_background_thread.start(_thread_simulation.bind(game_seed))
	else:
		# Fallback: run in deferred calls (will still block but spreads load)
		_run_deferred_simulation(game_seed)

static func is_baseline_ready(game_seed: String) -> bool:
	"""Check if baseline is available (precomputed, cached, or background complete)"""
	return _precomputed_baselines.has(game_seed) or _baseline_cache.has(game_seed)

static func get_baseline_score(game_seed: String) -> Dictionary:
	"""
	Get baseline score for a given seed.

	Priority:
	1. Precomputed baselines (weekly league)
	2. Cached results
	3. Background thread result (if complete)
	4. Synchronous computation (BLIND mode fallback)

	Returns: {score: int, final_state: Dictionary, turns: int, victory: bool}
	"""
	# 1. Check precomputed first (weekly league data)
	if _precomputed_baselines.has(game_seed):
		return _precomputed_baselines[game_seed]

	# 2. Check cache
	if _baseline_cache.has(game_seed):
		return _baseline_cache[game_seed]

	# 3. Check if background thread completed
	if _background_seed == game_seed and not _is_computing and _background_result.size() > 0:
		_baseline_cache[game_seed] = _background_result
		return _background_result

	# 4. Wait for background thread if it's computing our seed
	if _background_seed == game_seed and _is_computing:
		print("[BaselineSimulator] Waiting for background computation to complete...")
		_wait_for_background()
		if _background_result.size() > 0:
			_baseline_cache[game_seed] = _background_result
			return _background_result

	# 5. Fallback: synchronous computation (BLIND mode)
	print("[BaselineSimulator] Running synchronous simulation (BLIND mode)")
	var result = _run_baseline_simulation(game_seed)
	_baseline_cache[game_seed] = result
	return result

static func clear_cache():
	"""Clear the baseline cache (useful for testing)"""
	_baseline_cache.clear()
	_precomputed_baselines.clear()
	_background_result.clear()
	_background_seed = ""
	_is_computing = false
	_current_mode = Mode.BLIND

static func get_current_mode() -> Mode:
	"""Get the current baseline computation mode"""
	return _current_mode

## ============================================================================
## THREADING HELPERS
## ============================================================================

static func _thread_simulation(game_seed: String):
	"""Run simulation in a background thread"""
	var result = _run_baseline_simulation(game_seed)
	_background_result = result
	_is_computing = false
	print("[BaselineSimulator] Background simulation complete for seed: %s" % game_seed)

static func _wait_for_background():
	"""Wait for background thread to complete"""
	if _background_thread != null and _background_thread.is_started():
		_background_thread.wait_to_finish()
		_background_thread = null

static func _run_deferred_simulation(game_seed: String):
	"""Fallback: run simulation in deferred calls (single-threaded platforms)"""
	# For single-threaded platforms, just run synchronously
	# A more sophisticated approach could use coroutines/await
	var result = _run_baseline_simulation(game_seed)
	_background_result = result
	_is_computing = false

## ============================================================================
## SIMULATION LOGIC
## ============================================================================

static func _run_baseline_simulation(game_seed: String) -> Dictionary:
	"""
	Run a headless game with no player actions.
	The game proceeds with only passive effects (doom, staff productivity, etc.)
	"""
	print("[BaselineSimulator] Running baseline simulation for seed: %s" % game_seed)

	# Create game state with the same seed
	var state = GameState.new(game_seed)
	var turn_manager = TurnManager.new(state)

	var simulation_start = Time.get_ticks_msec()

	# Run simulation until game over or max turns
	while not state.game_over and state.turn < MAX_TURNS:
		# Start turn (processes passive effects, events, etc.)
		var start_result = turn_manager.start_turn()

		# Handle any events using baseline strategy
		while state.pending_events.size() > 0:
			var event = state.pending_events[0]
			var choices = event.get("choices", [])
			if choices.size() > 0:
				# Use baseline strategy to pick choice
				var choice_id = _get_event_choice_for_baseline(event, choices)
				turn_manager.resolve_event(event, choice_id)
			else:
				# No choices available, remove event
				state.pending_events.remove_at(0)

		# Execute turn with no queued actions (baseline = no player input)
		# The player takes no actions, only passive effects happen
		var turn_result = turn_manager.execute_turn()

	var simulation_time = Time.get_ticks_msec() - simulation_start
	print("[BaselineSimulator] Simulation complete: %d turns, %.2fs" % [state.turn, simulation_time / 1000.0])

	# ADR-0002: score is the (turns, doom_integral) tuple accrued in-engine during the
	# sim — no separate formula. Engine is the sole scoring authority.
	var final_state = state.to_dict()

	return {
		"turns": state.turn,
		"doom_integral": int(round(state.doom_integral)),
		"final_state": final_state,
		"victory": state.victory,
		"doom": state.doom,
		"simulation_time_ms": simulation_time
	}

static func get_comparison_text(player_turns: int, player_integral: int, baseline_turns: int, baseline_integral: int) -> Dictionary:
	"""
	Compare the player's (turns, doom_integral) score against the no-action baseline
	using ADR-0002 lexicographic ordering (turns dominant, doom-integral tiebreak).
	Returns: {text: String, color: Color, cmp: int}
	"""
	if baseline_turns <= 0:
		return {
			"text": "No baseline available",
			"color": Color.GRAY,
			"cmp": 0
		}

	var cmp = GameState.compare_score(player_turns, player_integral, baseline_turns, baseline_integral)

	var text: String
	var color: Color

	if cmp > 0:
		var turn_diff = player_turns - baseline_turns
		if turn_diff > 0:
			text = "%d turn%s longer than baseline!" % [turn_diff, "s" if turn_diff != 1 else ""]
			color = Color(0.2, 1.0, 0.2)  # Bright green
		else:
			# Same survival length, better stewardship (lower doom along the way)
			text = "Same survival, +%d stewardship over baseline" % (player_integral - baseline_integral)
			color = Color(0.6, 1.0, 0.6)  # Light green
	elif cmp < 0:
		var turn_diff = baseline_turns - player_turns
		if turn_diff > 0:
			text = "%d turn%s shorter than baseline" % [turn_diff, "s" if turn_diff != 1 else ""]
			color = Color(1.0, 0.3, 0.3)  # Red
		else:
			text = "Same survival, %d stewardship below baseline" % (baseline_integral - player_integral)
			color = Color(1.0, 0.6, 0.4)  # Orange
	else:
		text = "Matched baseline exactly"
		color = Color(1.0, 1.0, 0.4)  # Yellow

	return {
		"text": text,
		"color": color,
		"cmp": cmp
	}

## ============================================================================
## EVENT STRATEGY
## ============================================================================

static func _get_event_choice_for_baseline(event: Dictionary, choices: Array) -> String:
	"""
	Determine which choice to make for an event in baseline simulation.

	BASELINE STRATEGY PHILOSOPHY:
	The baseline represents a "passive" player who takes no deliberate actions
	but must still respond to events when forced. The strategy is:

	1. DEFAULT: Pick the first choice (index 0)
	   - Events should be designed with the most neutral/safe option first
	   - This represents "doing nothing actively wrong"

	2. SPECIAL CASES: Some events may have specific baseline behaviors
	   - Crisis events: Pick the "do nothing" or "wait and see" option
	   - Investment events: Always decline (no active investment)
	   - Hiring events: Never hire (no deliberate team building)

	EXTENDING THIS STRATEGY:
	To add special handling for specific events:
	1. Check event.get("id") or event.get("type")
	2. Return a specific choice_id for that event
	3. Document the reasoning below

	CURRENT SPECIAL CASES:
	(None yet - all events use first choice default)
	"""

	var event_id = event.get("id", "")
	var event_type = event.get("type", "")

	# Future: Add special case handling here
	# Example:
	# if event_id == "regulatory_investigation":
	#     # Always cooperate (usually the safe choice)
	#     for choice in choices:
	#         if choice.get("id", "") == "cooperate":
	#             return choice.get("id", "")

	# Default: return first choice
	if choices.size() > 0:
		return choices[0].get("id", "")

	return ""

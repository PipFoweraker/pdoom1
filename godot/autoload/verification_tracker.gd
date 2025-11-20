extends Node
## Cumulative Hash Verification Tracker
##
## Maintains a running cryptographic hash that gets updated after every game action,
## event, and RNG outcome. This creates a deterministic "fingerprint" of the entire
## game that can be verified server-side without replaying the full game.
##
## Usage:
##   1. Game start: VerificationTracker.start_tracking(seed)
##   2. After action: VerificationTracker.record_action(action_id, game_state)
##   3. After event: VerificationTracker.record_event(event_id, event_type, turn)
##   4. After event response: VerificationTracker.record_event_response(event_id, response_id, turn)
##   5. After RNG: VerificationTracker.record_rng_outcome(rng_type, value, turn)
##   6. Turn end: VerificationTracker.record_turn_end(turn, game_state)
##   7. Game end: Submit VerificationTracker.get_final_hash()
##
## Technical Details:
##   - Uses SHA-256 for cryptographic strength
##   - Chains each hash to previous (tamper-evident)
##   - Includes game state snapshots (state binding)
##   - Deterministic (same actions → same hash)
##   - Lightweight (64 bytes vs 5-20KB replay)
##
## Security:
##   - Prevents score inflation (can't fake without valid game state)
##   - Prevents state tampering (breaks hash chain)
##   - Prevents replay attacks (timestamp priority server-side)
##   - Prevents cross-seed exploits (hash includes seed)

# Current verification hash (updated throughout game)
var verification_hash: String = ""

# Game seed (for initialization and reference)
var game_seed: String = ""

# Tracking state
var tracking_enabled: bool = false

# Game version (for cross-version compatibility checks)
var game_version: String = ""

# Debug mode (enables verbose logging)
var debug_mode: bool = false


func start_tracking(seed: String, version: String = "unknown"):
	"""
	Initialize verification hash for new game.

	Args:
		seed: Game seed (deterministic RNG source)
		version: Game version (for compatibility checks)
	"""
	game_seed = seed
	game_version = version
	tracking_enabled = true

	# Initialize from seed
	verification_hash = seed.sha256_text()

	# Mix in game version (prevents cross-version exploits)
	var init = "%s|v%s" % [verification_hash, version]
	verification_hash = init.sha256_text()

	if debug_mode:
		print("[VerificationTracker] Started tracking")
		print("  Seed: %s" % seed)
		print("  Version: %s" % version)
		print("  Initial hash: %s..." % verification_hash.substr(0, 16))


func stop_tracking():
	"""Stop tracking (called on game end)."""
	tracking_enabled = false

	if debug_mode:
		print("[VerificationTracker] Stopped tracking")
		print("  Final hash: %s..." % verification_hash.substr(0, 16))


func record_action(action_id: String, state: GameState):
	"""
	Update hash after player action.

	Args:
		action_id: Unique action identifier (e.g., "buy_compute", "hire_safety_researcher_0")
		state: Current game state (for snapshot)
	"""
	if not tracking_enabled:
		return

	# Create deterministic state snapshot
	var snapshot = _create_state_snapshot(state)

	# Hash: previous + action + state
	var data = "%s|action:%s|%s" % [verification_hash, action_id, snapshot]
	verification_hash = data.sha256_text()

	if debug_mode:
		print("[VerificationTracker] Action: %s → %s..." % [action_id, verification_hash.substr(0, 16)])


func record_event(event_id: String, event_type: String, turn: int):
	"""
	Update hash when random event triggers.

	Args:
		event_id: Unique event identifier
		event_type: Event category (e.g., "funding", "breakthrough", "setback")
		turn: Current turn number
	"""
	if not tracking_enabled:
		return

	var data = "%s|event:%s:%s|t%d" % [verification_hash, event_type, event_id, turn]
	verification_hash = data.sha256_text()

	if debug_mode:
		print("[VerificationTracker] Event: %s (%s) → %s..." % [event_id, event_type, verification_hash.substr(0, 16)])


func record_event_response(event_id: String, response_id: String, turn: int):
	"""
	Update hash when player responds to event.

	Args:
		event_id: Event being responded to
		response_id: Player's choice (e.g., "accept", "decline", "option_a")
		turn: Current turn number
	"""
	if not tracking_enabled:
		return

	var data = "%s|response:%s->%s|t%d" % [verification_hash, event_id, response_id, turn]
	verification_hash = data.sha256_text()

	if debug_mode:
		print("[VerificationTracker] Response: %s → %s → %s..." % [event_id, response_id, verification_hash.substr(0, 16)])


func record_rng_outcome(rng_type: String, value: float, turn: int):
	"""
	Update hash for significant RNG outcomes.

	This ensures determinism - same seed + same RNG calls = same hash.

	Args:
		rng_type: Type of RNG event (e.g., "candidate_spec", "event_trigger", "breakthrough")
		value: RNG result (rounded to 6 decimals for consistency)
		turn: Current turn number

	Examples:
		record_rng_outcome("candidate_spec", 0.342156, 5)
		record_rng_outcome("event_probability", 0.891234, 12)
		record_rng_outcome("research_breakthrough", 0.156789, 20)
	"""
	if not tracking_enabled:
		return

	# Round to 6 decimals to avoid floating-point precision issues
	var rounded = snappedf(value, 0.000001)

	var data = "%s|rng:%s=%.6f|t%d" % [verification_hash, rng_type, rounded, turn]
	verification_hash = data.sha256_text()

	if debug_mode:
		print("[VerificationTracker] RNG: %s=%.6f → %s..." % [rng_type, rounded, verification_hash.substr(0, 16)])


func record_turn_end(turn: int, state: GameState):
	"""
	Update hash at end of each turn.

	This creates checkpoints and makes verification more granular.

	Args:
		turn: Turn number
		state: Game state at turn end
	"""
	if not tracking_enabled:
		return

	var snapshot = _create_state_snapshot(state)
	var data = "%s|turn_end:%d|%s" % [verification_hash, turn, snapshot]
	verification_hash = data.sha256_text()

	if debug_mode:
		print("[VerificationTracker] Turn %d end → %s..." % [turn, verification_hash.substr(0, 16)])


func get_final_hash() -> String:
	"""
	Get final verification hash for submission.

	Returns:
		64-character hex SHA-256 hash
	"""
	return verification_hash


func get_hash_prefix(length: int = 16) -> String:
	"""
	Get shortened hash for display (debugging/logging).

	Args:
		length: Number of characters to include

	Returns:
		First N characters of hash
	"""
	return verification_hash.substr(0, length)


func is_tracking() -> bool:
	"""Check if currently tracking."""
	return tracking_enabled


func _create_state_snapshot(state: GameState) -> String:
	"""
	Create deterministic snapshot of game state.

	Critical: Order matters! Changing order changes hash.
	Critical: Round floats to avoid precision issues.

	Args:
		state: Current game state

	Returns:
		Pipe-separated string of key state values
	"""
	# Round floats to 2 decimals (consistent across platforms)
	var money_rounded = snappedf(state.money, 0.01)
	var doom_rounded = snappedf(state.doom, 0.01)
	var papers_rounded = snappedf(state.papers, 0.01)
	var research_rounded = snappedf(state.research, 0.01)
	var compute_rounded = snappedf(state.compute, 0.01)

	# Format: turn|money|doom|papers|research|compute|staff_count
	return "%d|%.2f|%.2f|%.2f|%.2f|%.2f|%d" % [
		state.turn,
		money_rounded,
		doom_rounded,
		papers_rounded,
		research_rounded,
		compute_rounded,
		state.researchers.size()
	]


func get_tracking_summary() -> Dictionary:
	"""
	Get current tracking state (for debugging/logging).

	Returns:
		Dictionary with tracking details
	"""
	return {
		"tracking_enabled": tracking_enabled,
		"game_seed": game_seed,
		"game_version": game_version,
		"current_hash": verification_hash,
		"hash_prefix": get_hash_prefix(16)
	}


func export_for_submission(final_state: Dictionary) -> Dictionary:
	"""
	Export verification data for server submission.

	Args:
		final_state: Final game state dictionary

	Returns:
		Dictionary ready for API submission
	"""
	return {
		"verification_hash": verification_hash,
		"seed": game_seed,
		"game_version": game_version,
		"final_state": final_state,
		"timestamp": Time.get_unix_time_from_system()
	}


# Debug helper: Enable verbose logging
func enable_debug():
	"""Enable debug logging."""
	debug_mode = true
	print("[VerificationTracker] Debug mode enabled")


# Debug helper: Disable verbose logging
func disable_debug():
	"""Disable debug logging."""
	debug_mode = false

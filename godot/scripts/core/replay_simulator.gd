extends RefCounted
class_name ReplaySimulator
## Re-simulates a game from its canonical input-string artifact (ADR-0006) and checks it
## reproduces the same final hash and (turns, doom_integral) score.
##
## Why re-simulation and not just the hash chain: a hash chain only proves a transcript
## is internally self-consistent. It does NOT prove the transcript describes a *legal*
## game. Only replaying the inputs through the real engine does. The input string is
## therefore the canonical artifact — anti-cheat, share format, and bug-repro in one.

# Mirror of BaselineSimulator.MAX_TURNS — bound runaway/immortal runs.
# 10000 day-ticks ≈ 450 fiction-months, past the ADR-0002 400-month mortality cap. The old
# value (200) was a pre-L1 relic: 200 STRATEGIC turns was generous, but 200 day-ticks is
# ~9 fiction-months — post-recalibration (#638) every legitimate run outlives it, and a
# verifier that truncates at the cap REJECTS honest long runs.
const MAX_TURNS: int = 10000


static func replay(replay_data: Dictionary) -> Dictionary:
	"""
	Re-drive a recorded run from its artifact. Returns:
	  {turns:int, doom_integral:int, hash:String, final_state:Dictionary, replayed:bool}

	Side-effect-free: snapshots and restores the global VerificationTracker so a live
	game in progress (e.g. computing a comparison at game-over) is left untouched.
	"""
	var run_seed: String = str(replay_data.get("seed", ""))
	var run_version: String = str(replay_data.get("version", "unknown"))
	var input_log: Array = replay_data.get("log", [])
	# WS-C (ADR-0005): the event schedule is part of the run's identity, so it must be
	# replayed alongside seed+version or a scheduled run won't reproduce.
	var run_schedule: Array = replay_data.get("schedule", [])

	# Group inputs by the turn they were recorded under. start_turn() increments turn
	# first, so a round's event-responses and actions share that post-increment value.
	var actions_by_turn: Dictionary = {}    # turn -> [action_id, ...] (execution order)
	var responses_by_turn: Dictionary = {}  # turn -> {event_id: choice_id}
	for entry in input_log:
		var t: int = int(entry.get("t", 0))
		match str(entry.get("k", "")):
			"a":
				if not actions_by_turn.has(t):
					actions_by_turn[t] = []
				actions_by_turn[t].append(str(entry.get("id", "")))
			"r":
				if not responses_by_turn.has(t):
					responses_by_turn[t] = {}
				responses_by_turn[t][str(entry.get("ev", ""))] = str(entry.get("ch", ""))

	# Isolate the global tracker for the duration of the replay.
	var snap: Dictionary = VerificationTracker.snapshot()

	var state: GameState = GameState.new(run_seed, run_schedule)
	var turn_manager: TurnManager = TurnManager.new(state)
	# Pass the schedule through so a replay-of-a-replay re-emits it (DQ-6, #620).
	VerificationTracker.start_tracking(run_seed, run_version, run_schedule)

	while not state.game_over and state.turn < MAX_TURNS:
		turn_manager.start_turn()
		var t: int = state.turn

		# Resolve triggered events with the recorded choices (fall back to first choice
		# if the artifact is missing one — keeps replay total rather than crashing).
		var guard: int = 0
		while state.pending_events.size() > 0 and guard < 128:
			guard += 1
			var event: Dictionary = state.pending_events[0]
			var event_id: String = str(event.get("id", ""))
			var choices: Array = event.get("choices", [])
			if choices.size() > 0:
				var recorded: Dictionary = responses_by_turn.get(t, {})
				var choice_id: String
				if recorded.has(event_id):
					choice_id = str(recorded[event_id])
				elif typeof(choices[0]) == TYPE_DICTIONARY:
					choice_id = str(choices[0].get("id", ""))
				else:
					choice_id = str(choices[0])
				turn_manager.resolve_event(event, choice_id)
			else:
				state.pending_events.remove_at(0)

		# Queue the recorded actions for this turn, in order.
		state.queued_actions.clear()
		for action_id in actions_by_turn.get(t, []):
			state.queued_actions.append(action_id)
		turn_manager.execute_turn()

	var final_state: Dictionary = state.to_dict()
	var score: Array = GameState.score_tuple(final_state)
	var result: Dictionary = {
		"turns": score[0],
		"doom_integral": score[1],
		"hash": VerificationTracker.get_final_hash(),
		"final_state": final_state,
		"replayed": true
	}

	# Restore the caller's tracker exactly as it was before this replay.
	VerificationTracker.restore(snap)
	return result


static func verify(replay_data: Dictionary, claimed_turns: int, claimed_integral: int, claimed_hash: String = "") -> bool:
	"""
	True only if re-simulating the artifact reproduces the claimed SCORE (turns, integral),
	and — when a claimed_hash is supplied — the claimed verification hash.

	The score check is the sound anti-cheat property: you cannot claim a score higher than
	your input sequence actually produces. The hash is the cheap fast-path fingerprint tier
	(ADR-0006): now that the engine is deterministic (WS-0), an identical seed+input replay
	reproduces an identical hash, so a mismatch means the artifact was tampered or the claim
	forged. Passing "" for claimed_hash skips the fingerprint tier (score-only check).
	"""
	var r: Dictionary = replay(replay_data)
	if r["turns"] != claimed_turns or r["doom_integral"] != claimed_integral:
		return false
	if claimed_hash != "" and str(r["hash"]) != claimed_hash:
		return false
	return true

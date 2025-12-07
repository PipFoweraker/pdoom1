extends Node
class_name TurnManager
## Manages turn execution order - fully deterministic

var state: GameState

func _init(game_state: GameState):
	state = game_state

func _generate_random_candidate() -> Researcher:
	"""Generate a random candidate for the hiring pool"""
	# Random specialization (weighted towards safety early game)
	var specializations = ["safety", "capabilities", "interpretability", "alignment"]
	var weights = [0.35, 0.25, 0.20, 0.20]  # Safety most common

	var roll = state.rng.randf()

	# Record RNG outcome for verification
	VerificationTracker.record_rng_outcome("candidate_spec", roll, state.turn)

	var cumulative = 0.0
	var spec = "safety"
	for i in range(specializations.size()):
		cumulative += weights[i]
		if roll < cumulative:
			spec = specializations[i]
			break

	# Create researcher with random name and stats
	var researcher = Researcher.new()
	researcher.generate_random(state.rng)
	researcher.specialization = spec

	# Assign random traits
	_assign_candidate_traits(researcher)

	return researcher

func _assign_candidate_traits(researcher: Researcher):
	"""Assign random traits to a candidate (40% positive, 25% negative)"""
	# 40% chance of one positive trait
	var positive_roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("trait_positive", positive_roll, state.turn)

	if positive_roll < 0.40:
		var positive_traits = ["workaholic", "team_player", "media_savvy", "safety_conscious", "fast_learner"]
		var trait_index = state.rng.randi() % positive_traits.size()
		VerificationTracker.record_rng_outcome("trait_positive_select", float(trait_index), state.turn)
		var trait_id = positive_traits[trait_index]
		researcher.add_trait(trait_id)

	# 25% chance of one negative trait
	var negative_roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("trait_negative", negative_roll, state.turn)

	if negative_roll < 0.25:
		var negative_traits = ["prima_donna", "leak_prone", "burnout_prone", "pessimist"]
		var trait_index = state.rng.randi() % negative_traits.size()
		VerificationTracker.record_rng_outcome("trait_negative_select", float(trait_index), state.turn)
		var trait_id = negative_traits[trait_index]
		researcher.add_trait(trait_id)

func _populate_candidate_pool() -> int:
	"""Add new candidates to the pool (called each turn)"""
	var added = 0

	# Base 30% chance to add a candidate, plus 10% per empty slot
	var empty_slots = state.MAX_CANDIDATES - state.candidate_pool.size()
	var chance = 0.30 + (empty_slots * 0.10)

	# Higher reputation = better candidates appear more often
	if state.reputation > 60:
		chance += 0.10

	# Roll for new candidate
	var candidate_roll = state.rng.randf()
	VerificationTracker.record_rng_outcome("candidate_spawn", candidate_roll, state.turn)

	if candidate_roll < chance and empty_slots > 0:
		var candidate = _generate_random_candidate()
		state.add_candidate(candidate)
		added += 1

		# Small chance for a second candidate if pool is very empty
		if empty_slots > 3:
			var second_roll = state.rng.randf()
			VerificationTracker.record_rng_outcome("candidate_second", second_roll, state.turn)

			if second_roll < 0.20:
				var second = _generate_random_candidate()
				state.add_candidate(second)
				added += 1

	return added

func start_turn() -> Dictionary:
	"""
	Begin new turn - Phase 1: TURN_START
	FIX #418: Events trigger BEFORE action selection
	"""
	state.turn += 1
	state.current_phase = GameState.TurnPhase.TURN_START
	state.pending_events.clear()
	state.queued_actions.clear()
	state.can_end_turn = false

	# Calculate max AP based on staff (base 3 + 0.5 per staff member)
	var total_staff = state.get_total_staff()
	var max_ap = 3 + int(total_staff * 0.5)
	state.action_points = max_ap

	# Reset AP tracking for new turn (reserve system)
	state.reset_turn_ap()

	# === CANDIDATE POOL POPULATION ===
	var new_candidates = _populate_candidate_pool()

	# === RESEARCHER TURN PROCESSING ===
	# Process individual researchers (burnout, skill growth, loyalty)
	for researcher in state.researchers:
		researcher.process_turn(state.rng)

	# Staff maintenance costs - use actual salaries for individual researchers
	var staff_salaries = 0.0
	if state.researchers.size() > 0:
		for researcher in state.researchers:
			staff_salaries += researcher.current_salary / 12.0  # Monthly salary per turn
		staff_salaries += state.managers * 5000  # Managers still use flat rate
	else:
		# Legacy fallback
		staff_salaries = total_staff * 5000

	if staff_salaries > 0:
		state.add_resources({"money": -staff_salaries})

	# === INDIVIDUAL RESEARCHER PRODUCTIVITY SYSTEM ===
	# First 9 researchers work without a manager (founder manages them)
	# After 9, each manager handles up to 9 additional researchers

	var researcher_count = state.researchers.size()
	# Base capacity of 9 (founder-managed) + 9 per manager
	var management_capacity = 9 + (state.managers * 9)
	var managed_researcher_count = min(researcher_count, management_capacity)
	var unmanaged_count = researcher_count - managed_researcher_count

	# Calculate compute availability
	var available_compute = int(state.compute)

	# Process each researcher individually
	var research_from_employees = 0.0
	var doom_from_capabilities = 0.0
	var doom_reduction_from_safety = 0.0
	var productive_count = 0
	var leak_occurred = false
	var leak_doom = 0.0

	# Calculate team_player bonus (10% per team player present)
	var team_player_count = 0
	for researcher in state.researchers:
		if researcher.has_trait("team_player"):
			team_player_count += 1
	var team_player_bonus = 1.0 + (team_player_count * 0.10)

	# Process researchers in order (first N are managed)
	var researcher_index = 0
	for researcher in state.researchers:
		var is_managed = researcher_index < managed_researcher_count
		var has_compute = available_compute > 0

		if is_managed and has_compute:
			available_compute -= 1
			productive_count += 1

			# Get effective productivity (accounts for burnout, traits)
			var productivity = researcher.get_effective_productivity() * team_player_bonus

			# Research generation based on productivity
			var research_roll = state.rng.randf()
			VerificationTracker.record_rng_outcome("research_gen_%d" % researcher_index, research_roll, state.turn)

			if research_roll < 0.30 * productivity:
				var base_research = state.rng.randi_range(1, 3)
				VerificationTracker.record_rng_outcome("research_amount_%d" % researcher_index, float(base_research), state.turn)

				# Specialization modifiers
				match researcher.specialization:
					"capabilities":
						# +25% research speed
						base_research *= 1.25
						# But adds doom
						doom_from_capabilities += researcher.get_doom_modifier() * productivity
					"safety":
						# Safety research reduces doom
						doom_reduction_from_safety += 0.3 * productivity
						# Apply safety conscious trait
						if researcher.has_trait("safety_conscious"):
							doom_reduction_from_safety += 0.1 * productivity
					"interpretability":
						# Standard research, unlocks special actions (handled elsewhere)
						pass
					"alignment":
						# Reduces negative events (passive, handled in event system)
						doom_reduction_from_safety += 0.15 * productivity

				research_from_employees += base_research

			# Check for leak_prone trait (1% chance per turn)
			if researcher.has_trait("leak_prone"):
				var leak_roll = state.rng.randf()
				VerificationTracker.record_rng_outcome("leak_check_%d" % researcher_index, leak_roll, state.turn)

				if leak_roll < 0.01:
					leak_occurred = true
					leak_doom += 3.0  # Leak causes doom increase

		researcher_index += 1

	# Apply doom effects
	state.add_resources({"doom": -doom_reduction_from_safety})
	state.add_resources({"doom": doom_from_capabilities})
	if leak_occurred:
		state.add_resources({"doom": leak_doom})

	# Unmanaged researchers cause doom
	var unmanaged_employees = unmanaged_count
	var total_unproductive = (researcher_count - productive_count)
	if total_unproductive > 0:
		var doom_penalty = total_unproductive * 0.5
		state.add_resources({"doom": doom_penalty})

	# Apply research gains
	state.add_resources({"research": research_from_employees})

	# === STATIONERY SYSTEM ===
	# Staff consume stationery each turn
	var stationery_consumption = 0.0
	var safety_count = 0
	if state.researchers.size() > 0:
		for researcher in state.researchers:
			match researcher.specialization:
				"safety", "alignment":
					stationery_consumption += 1.0
					safety_count += 1
				"interpretability":
					stationery_consumption += 0.8
				"capabilities":
					stationery_consumption += 0.5
		stationery_consumption += state.managers * 0.5
	else:
		# Legacy fallback
		stationery_consumption = (state.safety_researchers * 1.0) + (state.managers * 0.5) + (state.compute_engineers * 0.3)
		safety_count = state.safety_researchers

	state.stationery = max(0.0, state.stationery - stationery_consumption)

	# Penalties when out of stationery
	var stationery_doom_penalty = 0.0
	if state.stationery <= 0:
		# Safety researchers are most impacted - can't document properly
		stationery_doom_penalty = safety_count * 0.3
		state.add_resources({"doom": stationery_doom_penalty})

	# Supply automation: auto-order when low
	var supply_auto_ordered = false
	if state.has_upgrade("supply_automation") and state.stationery < 30:
		if state.money >= 2000:
			state.money -= 2000
			state.stationery = min(state.stationery + 50.0, 100.0)
			supply_auto_ordered = true

	var messages = [
		"Turn %d started" % state.turn,
		"Action Points: %d (base 3 + %d from %d staff)" % [max_ap, max_ap - 3, total_staff]
	]

	if staff_salaries > 0:
		messages.append("Paid %s in staff salaries" % GameConfig.format_money(staff_salaries))

	if research_from_employees > 0:
		messages.append("Generated %.1f research from %d productive researchers" % [research_from_employees, productive_count])

	if doom_reduction_from_safety > 0:
		messages.append("Safety/alignment work reduced doom by %.1f" % doom_reduction_from_safety)

	if doom_from_capabilities > 0:
		messages.append("Capabilities research added %.1f doom" % doom_from_capabilities)

	if leak_occurred:
		messages.append("WARNING: Research leak detected! (+%.1f doom)" % leak_doom)

	if team_player_count > 0:
		messages.append("Team player bonus: +%d%% productivity" % int((team_player_bonus - 1.0) * 100))

	if unmanaged_employees > 0:
		messages.append("WARNING: %d unmanaged researchers (need more managers!)" % unmanaged_employees)

	if total_unproductive > 0:
		messages.append("WARNING: %d unproductive researchers! (+%.1f doom)" % [total_unproductive, total_unproductive * 0.5])

	# Stationery messages
	if stationery_consumption > 0:
		messages.append("Stationery used: %.1f (remaining: %.0f)" % [stationery_consumption, state.stationery])

	if stationery_doom_penalty > 0:
		messages.append("WARNING: Out of stationery! Safety work hampered (+%.1f doom)" % stationery_doom_penalty)

	if supply_auto_ordered:
		messages.append("Supply automation ordered stationery ($2k, +50 supplies)")

	# Candidate pool messages
	if new_candidates > 0:
		messages.append("%d new candidate(s) available for hire (%d total in pool)" % [new_candidates, state.candidate_pool.size()])
	elif state.candidate_pool.size() == 0:
		messages.append("No candidates in hiring pool")

	# CHECK FOR EVENTS FIRST (FIX #418)
	# Events must be presented and resolved BEFORE player selects actions
	var triggered_events = GameEvents.check_triggered_events(state, state.rng)

	if triggered_events.size() > 0:
		# Record triggered events in verification hash
		for triggered_event in triggered_events:
			var event_id = triggered_event.get("id", "")
			var event_type = triggered_event.get("trigger_type", "unknown")
			VerificationTracker.record_event(event_id, event_type, state.turn)

		# Events block action selection until resolved
		state.pending_events = triggered_events
		state.current_phase = GameState.TurnPhase.TURN_START  # Stay in TURN_START
		state.can_end_turn = false
		messages.append("%d event(s) require attention!" % triggered_events.size())
	else:
		# No events, can proceed to action selection
		state.current_phase = GameState.TurnPhase.ACTION_SELECTION
		state.can_end_turn = true

	return {
		"success": true,
		"phase": "turn_start" if triggered_events.size() > 0 else "action_selection",
		"messages": messages,
		"triggered_events": triggered_events,
		"can_select_actions": triggered_events.size() == 0,
		"can_end_turn": state.can_end_turn
	}

func execute_turn() -> Dictionary:
	"""Execute queued actions - Phase 2"""
	var results = []
	var all_success = true

	# Execute each queued action in order
	for action_id in state.queued_actions:
		var result = GameActions.execute_action(action_id, state)
		results.append(result)
		if not result["success"]:
			all_success = false

		# Record action in verification hash
		VerificationTracker.record_action(action_id, state)

	# Clear queued actions
	state.queued_actions.clear()

	# Check for paper publication (research threshold)
	if state.research >= 100:
		var papers_to_publish = int(state.research / 100)
		state.papers += papers_to_publish
		state.research = fmod(state.research, 100)  # Keep remainder
		state.add_resources({"reputation": papers_to_publish * 5})  # Papers boost reputation
		results.append({
			"success": true,
			"message": "Published %d paper%s! (+%d reputation)" % [
				papers_to_publish,
				"s" if papers_to_publish > 1 else "",
				papers_to_publish * 5
			]
		})

	# === RIVAL LABS TAKE ACTIONS ===
	var rival_doom_contribution = 0.0
	for rival in state.rival_labs:
		var rival_result = RivalLabs.process_rival_turn(rival, state, state.rng)
		rival_doom_contribution += rival_result["doom_contribution"]
		results.append({
			"success": true,
			"message": "%s: %s" % [rival_result["name"], ", ".join(rival_result["actions"])]
		})


	# === ORGANIZATION DISCOVERY (Issue #474) ===
	for rival in state.rival_labs:
		var discovery_result = RivalLabs.check_discovery(rival, state, state.rng)
		if discovery_result["discovered"]:
			results.append({
				"success": true,
				"message": "[INTEL] " + discovery_result["message"]
			})

	# === PAPER SUBMISSION DECISIONS (Issue #468) ===
	state.check_conference_year_reset()  # Reset attended conferences if year changed
	var paper_decisions = PaperSubmissions.process_paper_decisions(
		state.paper_submissions,
		state.turn,
		state.reputation,
		state.rng
	)
	for decision in paper_decisions:
		# Record RNG for verification
		VerificationTracker.record_rng_outcome(
			"paper_decision_%s" % decision["paper"].id,
			decision["probability"] if decision.has("probability") else 0.0,
			state.turn
		)
		results.append({
			"success": true,
			"message": "[PAPER] " + decision["message"]
		})

	# === USE DOOM SYSTEM FOR CALCULATION ===
	if state.doom_system:
		# Set rival contribution (calculated externally)
		state.doom_system.set_rival_doom_contribution(rival_doom_contribution)

		# Calculate doom with momentum system
		var doom_result = state.doom_system.calculate_doom_change(state)

		# Create detailed message
		var doom_msg = "Doom %.1f → %.1f (change: %+.1f)" % [
			doom_result["new_doom"] - doom_result["total_change"],
			doom_result["new_doom"],
			doom_result["total_change"]
		]

		# Add breakdown if significant changes
		if abs(doom_result["total_change"]) > 0.1:
			var breakdown_parts = []
			for source in doom_result["sources"]:
				var value = doom_result["sources"][source]
				if abs(value) > 0.1:
					breakdown_parts.append("%s: %+.1f" % [source, value])
			if breakdown_parts.size() > 0:
				doom_msg += "\n  └─ " + ", ".join(breakdown_parts)

		# Add momentum info if significant
		if abs(doom_result["momentum"]) > 0.5:
			doom_msg += "\n  └─ Momentum: %s (%.1f)" % [
				state.doom_system.get_momentum_description(),
				doom_result["momentum"]
			]

		results.append({
			"success": true,
			"message": doom_msg
		})

		# Sync to state.doom for backward compatibility
		state.doom = state.doom_system.current_doom
	else:
		# Fallback if doom system not initialized
		var total_doom_increase = 1.0 + (state.capability_researchers * 0.5) + rival_doom_contribution
		state.add_resources({"doom": total_doom_increase})
		results.append({
			"success": true,
			"message": "Doom +%.1f (legacy calculation)" % total_doom_increase
		})

	# REMOVED: Event checking now happens in start_turn() (FIX #418)
	# Events are checked BEFORE actions, not after

	# Record turn end in verification hash
	VerificationTracker.record_turn_end(state.turn, state)

	# Check win/lose
	state.check_win_lose()

	if state.game_over:
		if state.victory:
			results.append({"success": true, "message": "VICTORY! p(doom) reached 0!"})
		else:
			var reason = "p(doom) = 100" if state.doom >= 100 else "Reputation = 0"
			results.append({"success": false, "message": "GAME OVER: " + reason})

	return {
		"success": all_success,
		"action_results": results,
		"turn_complete": true
	}

func resolve_event(event: Dictionary, choice_id: String) -> Dictionary:
	"""
	Resolve player's event choice during TURN_START phase
	FIX #418: After all events resolved, transition to ACTION_SELECTION
	"""
	if state.current_phase != GameState.TurnPhase.TURN_START:
		return {
			"success": false,
			"error": "Cannot resolve events in phase %s" % state.current_phase
		}

	# Execute the event choice
	var result = GameEvents.execute_event_choice(event, choice_id, state)

	if not result["success"]:
		return result

	# Record event response in verification hash
	var event_id = event.get("id", "")
	var event_type = event.get("trigger_type", "unknown")
	VerificationTracker.record_event_response(event_id, choice_id, state.turn)

	# Remove this event from pending
	var new_pending: Array[Dictionary] = []
	for pending in state.pending_events:
		if pending.get("id", "") != event_id:
			new_pending.append(pending)
	state.pending_events = new_pending

	# If no more pending events, transition to ACTION_SELECTION
	if state.pending_events.size() == 0:
		state.current_phase = GameState.TurnPhase.ACTION_SELECTION
		state.can_end_turn = true
		result["phase_transitioned"] = true
		result["new_phase"] = "action_selection"
	else:
		result["pending_events"] = state.pending_events.size()

	result["can_select_actions"] = state.pending_events.size() == 0
	result["can_end_turn"] = state.can_end_turn

	return result

func get_available_actions() -> Array[Dictionary]:
	"""Get actions player can currently take"""
	var all_actions = GameActions.get_all_actions()
	var available: Array[Dictionary] = []

	for action in all_actions:
		var can_afford = state.can_afford(action["costs"])
		var action_copy = action.duplicate()
		action_copy["affordable"] = can_afford
		available.append(action_copy)

	return available

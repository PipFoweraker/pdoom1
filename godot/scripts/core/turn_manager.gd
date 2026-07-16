extends Node
class_name TurnManager
## Manages turn execution order - fully deterministic

var state: GameState

func _init(game_state: GameState):
	state = game_state

# NOTE: the free per-turn candidate-pool refill was REMOVED (hiring-pipeline redesign). It
# was a placeholder from before sourcing existed: it kept the 6-slot pool full for free every
# turn, so paid advertised/connections candidates were silently discarded (pool already at
# cap), undermining the whole source->interview->offer pipeline. Candidates now come ONLY from
# the turn-0 founding-team seed (GameState._populate_initial_candidates) and from sourcing
# (HiringPipeline advertise / use_connections). The legacy instant-hire from the existing pool
# is unaffected. This also drops the per-turn candidate_spawn/trait RNG draws from the turn
# stream -- deterministic replays re-simulate against the same new stream, so they stay
# self-consistent (WS-0 / ADR-0006).

func start_turn() -> Dictionary:
	"""
	Begin new turn - Phase 1: TURN_START
	FIX #418: Events trigger BEFORE action selection

	L0 (#620): split into named, movable step functions with NO behavior change.
	L1 (ADR-0009) will redistribute these steps across plan/day-tick/review phases.
	STEP ORDER IS LOAD-BEARING: it defines the deterministic RNG stream that
	recorded replays re-simulate — reordering steps invalidates every replay.
	"""
	_step_begin_turn()
	_step_apply_scheduled_causes()
	var ledger_result: Dictionary = _step_ledger_tick_and_bill()
	var total_staff: int = state.get_total_staff()
	var max_ap: int = _step_grant_action_points(total_staff)
	_step_process_researcher_lifecycles()
	var staff_salaries: float = _step_pay_salaries(total_staff)
	var prod: Dictionary = _step_researcher_productivity()
	var stationery: Dictionary = _step_consume_stationery()
	var messages: Array = _build_start_turn_messages(max_ap, total_staff, staff_salaries, prod, stationery, ledger_result)
	var triggered_events: Array[Dictionary] = _step_check_events(messages)

	return {
		"success": true,
		"phase": "turn_start" if triggered_events.size() > 0 else "action_selection",
		"messages": messages,
		"triggered_events": triggered_events,
		"can_select_actions": triggered_events.size() == 0,
		"can_end_turn": state.can_end_turn
	}

func _step_begin_turn() -> void:
	"""Advance the turn counter and reset per-turn phase/queue state."""
	state.turn += 1
	state.current_phase = GameState.TurnPhase.TURN_START
	state.pending_events.clear()
	state.queued_actions.clear()
	state.can_end_turn = false

func _step_apply_scheduled_causes() -> void:
	"""WS-C (ADR-0005): apply any scheduled causes due this turn BEFORE events/rivals
	react, so the authored cause (e.g. a rival funding wave) shapes this turn's
	emergent outcome. Causes touch sim inputs only — never doom directly."""
	SeedSchedule.apply_due_causes(state)

func _step_ledger_tick_and_bill() -> Dictionary:
	"""WS-1 (ADR-0003): the Liability Ledger bills AFTER scheduled causes, so an
	exposure cause can land the same turn it fires. Compounding payables are the
	mortality guarantee (ADR-0002): an un-serviced debt eventually bills more than
	the player can cover, and the resulting bankruptcy escalation is the death —
	traceable to specific entries via the ledger's attribution trail.
	Returns this turn's billed + newly-exposed entries for the EE-7 (ADR-0012)
	loss-legibility message builder."""
	var billed_entries: Array = []
	var exposed_entries: Array = []
	if state.ledger:
		billed_entries = state.ledger.tick_and_bill(state)
		# BL-2: secret liabilities have a per-turn chance to surface (deterministic via
		# state.rng). Chance from Balance (L9 #621); exposure tuning parked (workshop #2).
		exposed_entries = state.ledger.check_exposures(state, Balance.num("ledger.exposure_chance_per_turn", 0.15))
	return {"billed": billed_entries, "exposed": exposed_entries}

func _step_grant_action_points(total_staff: int) -> int:
	"""Grant this turn's AP: difficulty base + staff bonus (0.5 per staff member).
	FIX #541: use state.max_action_points (set by difficulty: Easy=4, Standard=3,
	Hard=2) as the base instead of a hardcoded 3, so difficulty actually changes AP.
	Per-staff bonus sourced from Balance ("action_points.per_staff", L9 #621)."""
	var max_ap = state.max_action_points + int(total_staff * Balance.num("action_points.per_staff", 0.5))
	state.action_points = max_ap

	# Reset AP tracking for new turn (reserve system)
	state.reset_turn_ap()
	return max_ap

func _step_process_researcher_lifecycles() -> void:
	"""=== RESEARCHER TURN PROCESSING ===
	Per-researcher upkeep: burnout, skill growth, loyalty (consumes state.rng)."""
	for researcher in state.researchers:
		researcher.process_turn(state.rng)

func _step_pay_salaries(total_staff: int) -> float:
	"""Staff maintenance costs - use actual salaries for individual researchers.
	Salary cadence routes through Clock (L0 #620): annual/260 per workday-turn.
	Was /12 — a full month billed every day, causing the turn-7 cash crash (#573).
	Salary BASE magnitudes come from Balance ("salaries.*", L9 #621); the /260
	workday divisor defers to L0's Clock. Magnitude tunable (workshop #2 / #574)."""
	var staff_salaries = 0.0
	if state.researchers.size() > 0:
		for researcher in state.researchers:
			staff_salaries += Clock.annual_to_per_turn(researcher.current_salary)
		staff_salaries += state.managers * Clock.annual_to_per_turn(Balance.num("salaries.manager_annual", 60000.0))  # Managers ~$60k/yr (#573; was $5000 flat = a month's pay per day)
	else:
		# Legacy fallback
		staff_salaries = total_staff * Clock.annual_to_per_turn(Balance.num("salaries.legacy_staff_annual", 60000.0))  # per-workday (#573)

	if staff_salaries > 0:
		state.add_resources({"money": -staff_salaries})
	return staff_salaries

func _step_researcher_productivity() -> Dictionary:
	"""=== INDIVIDUAL RESEARCHER PRODUCTIVITY SYSTEM ===
	First 9 researchers work without a manager (founder manages them);
	after 9, each manager handles up to 9 additional researchers.
	Returns this turn's productivity tallies for the message builder."""
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
	# #576: compute is a consumable, not just a capacity gate. Each productive
	# researcher burns compute this turn; we accumulate the total here and
	# actually decrement state.compute after the loop (previously the `-= 1`
	# below only touched the local `available_compute`, so compute never fell).
	var compute_consumed = 0.0
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
			# Flat 1 compute/researcher/turn for now. PARKED (#576 follow-up):
			# "researchers request compute at different rates" — make this a
			# per-researcher rate (by specialization / skill) instead of 1.
			var compute_request = 1
			available_compute -= compute_request
			compute_consumed += compute_request
			productive_count += 1

			# Get effective productivity (accounts for burnout, traits)
			var productivity = researcher.get_effective_productivity() * team_player_bonus

			# Research generation based on productivity
			var research_roll = state.rng.randf()
			VerificationTracker.record_rng_outcome("research_gen_%d" % researcher_index, research_roll, state.turn)

			if research_roll < 0.30 * productivity:
				var base_research: float = state.rng.randi_range(1, 3)  # float fixes the 1.25 capabilities truncation
				base_research *= state.get_research_multiplier()  # Issue #500: per-researcher research-quality speed
				VerificationTracker.record_rng_outcome("research_amount_%d" % researcher_index, base_research, state.turn)

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

	# ADR-0015: researcher hazard is no longer a direct doom write. Capability work raises the
	# PLAYER frontier and safety work raises safety_absorption + global_alarm — the DoomSystem
	# intermediary advance (_advance_intermediaries) reads the productive roster each tick and
	# does that accounting as the overhang/alarm streams. The old add_resources({"doom": ...})
	# writes here were silently clobbered (Finding A) AND double-counted that same influence;
	# both are removed. A researcher LEAK is a discrete reckless incident -> global_panic.
	if leak_occurred:
		state.global_panic += leak_doom * Balance.num("doom.streams.leak_panic_scale", 0.02)

	# Unmanaged researchers cause doom
	var unmanaged_employees = unmanaged_count
	var total_unproductive = (researcher_count - productive_count)

	# Apply research gains
	state.add_resources({"research": research_from_employees})

	# #576: actually burn the compute the researchers consumed this turn.
	# Matches the money-spend pattern above (add_resources with a negative).
	# compute_consumed <= int(state.compute) by construction (the has_compute
	# gate stops handing out compute at 0), so this stays non-negative.
	if compute_consumed > 0:
		state.add_resources({"compute": -compute_consumed})
		state.compute = max(0.0, state.compute)

	# Issue #500: research-quality risk contributions (feeds risk pools, not doom directly)
	state.apply_research_quality_risk(state.turn)

	return {
		"research_from_employees": research_from_employees,
		"productive_count": productive_count,
		"doom_reduction_from_safety": doom_reduction_from_safety,
		"doom_from_capabilities": doom_from_capabilities,
		"leak_occurred": leak_occurred,
		"leak_doom": leak_doom,
		"team_player_count": team_player_count,
		"team_player_bonus": team_player_bonus,
		"unmanaged_employees": unmanaged_employees,
		"total_unproductive": total_unproductive,
	}

func _step_consume_stationery() -> Dictionary:
	"""=== STATIONERY SYSTEM === Staff consume stationery each turn; running out
	hampers safety documentation (doom penalty); supply automation auto-orders."""
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
		# Safety researchers can't document properly -> a mild hazard. ADR-0015: not a direct
		# doom write (was clobbered/inert) — routed to global_panic (a documentation-failure
		# incident the world reacts to). Kept in the return dict for the turn message.
		stationery_doom_penalty = safety_count * 0.3
		state.global_panic += stationery_doom_penalty * Balance.num("doom.streams.leak_panic_scale", 0.02)

	# Supply automation: auto-order when low
	var supply_auto_ordered = false
	if state.has_upgrade("supply_automation") and state.stationery < 30:
		if state.money >= 2000:
			state.money -= 2000
			state.stationery = min(state.stationery + 50.0, 100.0)
			supply_auto_ordered = true

	return {
		"stationery_consumption": stationery_consumption,
		"stationery_doom_penalty": stationery_doom_penalty,
		"supply_auto_ordered": supply_auto_ordered,
	}

func _build_start_turn_messages(max_ap: int, total_staff: int, staff_salaries: float, prod: Dictionary, stationery: Dictionary, ledger_result: Dictionary) -> Array:
	"""Assemble the turn-start message list. Pure reads — no sim mutation, no RNG."""
	var billed_entries: Array = ledger_result.get("billed", [])
	var exposed_entries: Array = ledger_result.get("exposed", [])
	var research_from_employees: float = prod["research_from_employees"]
	var productive_count: int = prod["productive_count"]
	var doom_reduction_from_safety: float = prod["doom_reduction_from_safety"]
	var doom_from_capabilities: float = prod["doom_from_capabilities"]
	var leak_occurred: bool = prod["leak_occurred"]
	var leak_doom: float = prod["leak_doom"]
	var team_player_count: int = prod["team_player_count"]
	var team_player_bonus: float = prod["team_player_bonus"]
	var unmanaged_employees: int = prod["unmanaged_employees"]
	var total_unproductive: int = prod["total_unproductive"]
	var stationery_consumption: float = stationery["stationery_consumption"]
	var stationery_doom_penalty: float = stationery["stationery_doom_penalty"]
	var supply_auto_ordered: bool = stationery["supply_auto_ordered"]

	var messages = [
		"Turn %d started" % state.turn,
		"Action Points: %d (base 3 + %d from %d staff)" % [max_ap, max_ap - 3, total_staff]
	]

	# EE-7 (ADR-0012): the ledger's kill path must be LEGIBLE — every bill, its
	# fallout, and every exposure gets an explicit line with its resource deltas.
	for e in billed_entries:
		var amt_txt: String = GameConfig.format_money(e.principal) if e.currency == "money" else ("%.1f %s" % [e.principal, e.currency])
		messages.append("Ledger bill due: '%s' — %s" % [e.source, amt_txt])
	for c in state.cause_log:
		if int(c.turn) == state.turn and str(c.kind).begins_with("ledger"):
			var fx: Dictionary = c.effects
			var parts := []
			if fx.has("money_shortfall"):
				parts.append("unpaid %s" % GameConfig.format_money(float(fx["money_shortfall"])))
			if fx.has("doom") and float(fx["doom"]) != 0.0:
				parts.append("%+.1f doom" % float(fx["doom"]))
			if fx.has("reputation") and float(fx["reputation"]) != 0.0:
				parts.append("%+.1f reputation" % float(fx["reputation"]))
			if fx.has("governance") and float(fx["governance"]) != 0.0:
				parts.append("%+.0f governance" % float(fx["governance"]))
			if fx.has("governance_deficit"):
				parts.append("governance deficit %.0f" % float(fx["governance_deficit"]))
			if parts.size() > 0:
				messages.append("WARNING: Ledger fallout ('%s'): %s" % [str(c.source), ", ".join(parts)])
	for ex in exposed_entries:
		messages.append("WARNING: Secret liability EXPOSED: '%s' — reputation/governance damage; a blackmail offer follows." % ex.source)

	if staff_salaries > 0:
		messages.append("Paid %s in staff salaries" % GameConfig.format_money(staff_salaries))

		# Low-cash / bankruptcy warning (#573) — surface cash danger BEFORE a silent defeat
		var ledger_due_soon: float = 0.0
		if state.ledger and state.ledger.soonest_fuse() >= 0 and state.ledger.soonest_fuse() <= 1:
			ledger_due_soon = state.ledger.outstanding()
		var next_turn_bills: float = staff_salaries + ledger_due_soon
		if state.money < next_turn_bills:
			messages.append("CRITICAL: Cash (%s) won't cover next turn's bills (%s) — bankruptcy imminent!" % [GameConfig.format_money(state.money), GameConfig.format_money(next_turn_bills)])
			# EE-8: funding-starvation watermark on the ADR-0012 cascade. One-shot per
			# starvation episode (flag resets on recovery). Recording only.
			if not state.funding_starvation_noted:
				state.funding_starvation_noted = true
				state.note_cause("funding_starvation", "payroll",
					{"cash_level": state.money, "bills_due": next_turn_bills})
		else:
			state.funding_starvation_noted = false
			if state.money < staff_salaries * 3.0:
				messages.append("WARNING: Low cash — about %d turn(s) of payroll left (%s)." % [int(state.money / staff_salaries), GameConfig.format_money(state.money)])

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

	# Candidate pool status. No free per-turn refill anymore (hiring-pipeline redesign):
	# new candidates arrive only via sourcing (advertise / connections), surfaced through the
	# pipeline's own feed notifications, not here.
	if state.candidate_pool.size() == 0:
		messages.append("No candidates in hiring pool")

	return messages

func _step_check_events(messages: Array) -> Array[Dictionary]:
	"""CHECK FOR EVENTS FIRST (FIX #418): events must be presented and resolved
	BEFORE the player selects actions; pending events block ACTION_SELECTION."""
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

	return triggered_events

func execute_turn() -> Dictionary:
	"""Execute queued actions - Phase 2

	L0 (#620): split into named, movable step functions with NO behavior change.
	L1 (ADR-0009) will redistribute these consequence steps across day ticks.
	STEP ORDER IS LOAD-BEARING (deterministic RNG stream — see start_turn)."""
	var results = []
	var all_success: bool = _step_execute_queued_actions(results)
	_step_publish_papers(results)
	var rival_doom_contribution: float = _step_process_rival_turns(results)
	_step_check_rival_discovery(results)
	_step_process_paper_decisions(results)
	_step_resolve_doom(results, rival_doom_contribution)
	# NOTE: event checking happens in start_turn() (FIX #418) — before actions, not after.
	_step_process_risk_pools(results)
	_step_finalize_turn(results)

	return {
		"success": all_success,
		"action_results": results,
		"turn_complete": true
	}

func _step_execute_queued_actions(results: Array) -> bool:
	"""Execute each queued action in order, recording each into the replay log."""
	var all_success = true
	for action_id in state.queued_actions:
		var result = GameActions.execute_action(action_id, state)
		results.append(result)
		if not result["success"]:
			all_success = false

		# Record action in verification hash
		VerificationTracker.record_action(action_id, state)

	# Clear queued actions
	state.queued_actions.clear()
	return all_success

func _step_publish_papers(results: Array) -> void:
	"""Check for paper publication (research threshold)."""
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

func _step_process_rival_turns(results: Array) -> float:
	"""=== RIVAL LABS TAKE ACTIONS ===

	ADR-0015 (Legacy #7): the per-action rival doom literals AND the rivals.per_tick_doom_scale
	shim are RETIRED. Rivals act on their own state — capability_research/hire raise their
	capability_progress (their frontier_capability slice, which the overhang stream converts to
	hazard), reckless capability moves raise global_panic. No rival doom is returned; the doom
	comes out of the intermediaries on the next DoomSystem tick. Returns 0.0 (compat)."""
	for rival in state.rival_labs:
		var rival_result = RivalLabs.process_rival_turn(rival, state, state.rng)
		results.append({
			"success": true,
			"message": "%s: %s" % [rival_result["name"], ", ".join(rival_result["actions"])]
		})
	return 0.0

func _step_check_rival_discovery(results: Array) -> void:
	"""=== ORGANIZATION DISCOVERY (Issue #474) ==="""
	for rival in state.rival_labs:
		var discovery_result = RivalLabs.check_discovery(rival, state, state.rng)
		if discovery_result["discovered"]:
			results.append({
				"success": true,
				"message": "[INTEL] " + discovery_result["message"]
			})

func _step_process_paper_decisions(results: Array) -> void:
	"""=== PAPER SUBMISSION DECISIONS (Issue #468) ==="""
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

func _step_resolve_doom(results: Array, rival_doom_contribution: float) -> void:
	"""=== USE DOOM SYSTEM FOR CALCULATION === (momentum model; legacy fallback)."""
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

	# Record the post-resolution doom for the trend graph (#512), covering both branches
	state.record_doom_history()

func _step_process_risk_pools(results: Array) -> void:
	"""=== RISK SYSTEM PROCESSING === Process risk pools and check for triggered
	events. See godot/docs/design/RISK_SYSTEM.md for design documentation."""
	if state.risk_system:
		var risk_triggers = state.risk_system.process_turn(state, state.rng)

		if risk_triggers.size() > 0:
			for risk_trigger in risk_triggers:
				var pool_name = risk_trigger.get("pool", "")
				var pool_display = risk_trigger.get("pool_name", "Unknown")
				var severity = risk_trigger.get("severity", "minor")
				var from_threshold = risk_trigger.get("from_threshold", false)

				# Fetch actual event content from events.gd
				var event_data = GameEvents.get_risk_event_for_pool(pool_name, severity, state.rng)

				if event_data.is_empty():
					# Fallback if no event defined for this pool/severity
					var fallback_doom = {"minor": 2.0, "moderate": 5.0, "severe": 9.0, "catastrophic": 15.0}
					var doom_impact = fallback_doom.get(severity, 3.0)
					if state.doom_system:
						state.doom_system.add_event_doom(doom_impact, "risk_%s" % pool_name)
					else:
						state.add_resources({"doom": doom_impact})
					results.append({
						"success": true,
						"message": "[RISK] %s event (%s): +%.1f doom" % [pool_display, severity, doom_impact]
					})
					continue

				# Apply all effects from the event
				var effects = event_data.get("effects", {})
				var doom_from_event = 0.0
				# #631 follow-up: some risk events (e.g. insider_threat "Key
				# Resignation") describe an actual staff departure, not just a
				# resource hit. `lose_researcher` used to silently vanish here —
				# state.add_resources() only recognizes scalar keys, so an
				# unrecognized key like this was dropped with no error and no
				# effect (the same no-op class fixed for poaching in #633).
				var departure_notes: Array[String] = []

				for resource in effects:
					var amount = effects[resource]
					if resource == "doom":
						doom_from_event = amount
						# Use doom system if available for proper tracking
						if state.doom_system:
							state.doom_system.add_event_doom(amount, "risk_%s" % pool_name)
						else:
							state.add_resources({"doom": amount})
					elif resource == "lose_researcher":
						departure_notes.append_array(
							GameEvents.remove_researchers(state, int(amount), "", "resigned")
						)
					else:
						# Apply other resource changes directly
						state.add_resources({resource: amount})

				# Record for verification
				VerificationTracker.record_rng_outcome(
					"risk_event_%s" % event_data.get("id", pool_name),
					doom_from_event,
					state.turn
				)

				# Create detailed result message
				var event_name = event_data.get("name", "Risk Event")
				var event_message = event_data.get("message", "")
				var trigger_type = "[THRESHOLD]" if from_threshold else ""
				# Legibility (#631 follow-up): name who left, same as the event-driven
				# poaching fix — otherwise a departure is invisible in the log.
				for note in departure_notes:
					event_message += "\n  └─ %s" % note

				results.append({
					"success": true,
					"message": "[RISK] %s %s: %s\n  └─ %s" % [
						trigger_type,
						event_name,
						event_data.get("description", ""),
						event_message
					]
				})

		# Log risk summary in dev mode (if needed)
		# print(state.risk_system.get_debug_summary())

func _step_finalize_turn(results: Array) -> void:
	"""Record turn end in the verification hash, check win/lose, accrue survival credit."""
	VerificationTracker.record_turn_end(state.turn, state)

	# Check win/lose
	state.check_win_lose()

	# ADR-0002: accrue this turn's survival credit into the doom-integral score
	# tiebreaker. A turn that ended the game earns no stewardship credit.
	if not state.game_over:
		state.accrue_survival_credit()

	if state.game_over:
		if state.victory:
			results.append({"success": true, "message": "VICTORY! p(doom) reached 0!"})
		else:
			var reason = "p(doom) = 100" if state.doom >= 100 else "Reputation = 0"
			results.append({"success": false, "message": "GAME OVER: " + reason})


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

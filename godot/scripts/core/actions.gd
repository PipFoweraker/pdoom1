extends Node
class_name GameActions
## Action definitions - what players can do

static func get_all_actions() -> Array[Dictionary]:
	"""Return all available actions"""
	return [
		{
			"id": "pass",
			"name": "Do Nothing (Pass)",
			"description": "Skip this action. Conserve resources but waste time.",
			"costs": {},  # Free action, always available
			"category": "management"
		},
		{
			"id": "hire_staff",
			"name": "Hire Staff",
			"description": "Open hiring menu to recruit researchers",
			"costs": {},  # No cost to open menu
			"category": "hiring",
			"is_submenu": true
		},
		{
			"id": "buy_compute",
			"name": "Purchase Compute",
			"description": "Buy more computing power",
			"costs": {"money": 50000},
			"category": "resources"
		},
		{
			"id": "safety_research",
			"name": "Safety Research",
			"description": "Conduct AI safety research",
			"costs": {"research": 10, "action_points": 1},
			"category": "research"
		},
		{
			"id": "capability_research",
			"name": "Capability Research",
			"description": "Advance AI capabilities",
			"costs": {"research": 10, "action_points": 1},
			"category": "research"
		},
		{
			"id": "publish_paper",
			"name": "Publish Safety Paper",
			"description": "Publish research to reduce p(doom)",
			"costs": {"research": 20, "action_points": 1},
			"category": "research"
		},
		{
			"id": "fundraise",
			"name": "Fundraising",
			"description": "Choose funding strategy - different risk/reward options",
			"costs": {},  # No cost to open menu
			"category": "management",
			"is_submenu": true
		},
		{
			"id": "publicity",
			"name": "Publicity",
			"description": "Public outreach and influence campaigns",
			"costs": {},  # No cost to open menu
			"category": "influence",
			"is_submenu": true
		},
		{
			"id": "team_building",
			"name": "Team Building",
			"description": "Improve morale, reduce doom slightly",
			"costs": {"money": 10000, "action_points": 1},
			"category": "management"
		},
		{
			"id": "audit_safety",
			"name": "Safety Audit",
			"description": "Comprehensive safety review",
			"costs": {"money": 40000, "action_points": 2},
			"category": "research"
		},
		{
			"id": "order_supplies",
			"name": "Order Office Supplies",
			"description": "Restock stationery (+50 supplies). Staff consume supplies each turn.",
			"costs": {"money": 2000, "action_points": 1},
			"category": "management"
		},
		# Strategic submenu for high-cost/risky actions
		{
			"id": "strategic",
			"name": "Strategic",
			"description": "High-stakes strategic moves and risky plays",
			"costs": {},  # No cost to open menu
			"category": "strategic",
			"is_submenu": true
		}
	]

static func get_action_by_id(action_id: String) -> Dictionary:
	"""Get specific action definition"""
	for action in get_all_actions():
		if action["id"] == action_id:
			return action
	# Check submenu actions
	for action in get_hiring_options():
		if action["id"] == action_id:
			return action
	for action in get_fundraising_options():
		if action["id"] == action_id:
			return action
	for action in get_publicity_options():
		if action["id"] == action_id:
			return action
	for action in get_strategic_options():
		if action["id"] == action_id:
			return action
	return {}

static func get_hiring_options() -> Array[Dictionary]:
	"""Get all hiring submenu options"""
	return [
		{
			"id": "hire_safety_researcher",
			"name": "Safety Researcher",
			"description": "Focused on AI safety and alignment research",
			"costs": {"money": 60000, "action_points": 1},
			"category": "hiring"
		},
		{
			"id": "hire_capability_researcher",
			"name": "Capability Researcher",
			"description": "Advances AI capabilities (increases doom!)",
			"costs": {"money": 60000, "action_points": 1},
			"category": "hiring"
		},
		{
			"id": "hire_compute_engineer",
			"name": "Compute Engineer",
			"description": "Improves compute efficiency",
			"costs": {"money": 50000, "action_points": 1},
			"category": "hiring"
		},
		{
			"id": "hire_manager",
			"name": "Manager",
			"description": "Oversees a team of up to 8 researchers",
			"costs": {"money": 80000, "action_points": 1},
			"category": "hiring"
		},
		{
			"id": "hire_ethicist",
			"name": "AI Ethicist",
			"description": "Add philosophical perspective to research (+5 reputation)",
			"costs": {"money": 70000, "action_points": 1},
			"category": "hiring"
		}
	]

static func get_fundraising_options() -> Array[Dictionary]:
	"""Get all fundraising submenu options"""
	return [
		{
			"id": "fundraise_small",
			"name": "Modest Funding Round",
			"description": "Conservative fundraising - lower amounts, lower risk, always available",
			"costs": {"action_points": 1, "reputation": 2},
			"gains": {"money_min": 30000, "money_max": 60000},
			"category": "funding"
		},
		{
			"id": "fundraise_big",
			"name": "Major Funding Round",
			"description": "Aggressive funding - higher amounts but requires strong reputation",
			"costs": {"action_points": 2, "reputation": 8},
			"gains": {"money_min": 80000, "money_max": 150000},
			"category": "funding"
		},
		{
			"id": "take_loan",
			"name": "Business Loan",
			"description": "Immediate funds via debt - creates future repayment obligation",
			"costs": {"action_points": 1},
			"gains": {"money": 75000, "debt": 90000},  # +15k interest
			"category": "funding"
		},
		{
			"id": "apply_grant",
			"name": "Research Grant",
			"description": "Government/foundation funding - requires published papers",
			"costs": {"action_points": 1, "papers": 1},
			"gains": {"money_min": 50000, "money_max": 100000},
			"category": "funding"
		}
	]

static func get_publicity_options() -> Array[Dictionary]:
	"""Get all publicity/influence submenu options"""
	return [
		{
			"id": "network",
			"name": "Networking",
			"description": "Build relationships and connections in the AI safety community",
			"costs": {"action_points": 1},
			"category": "influence"
		},
		{
			"id": "media_campaign",
			"name": "Media Campaign",
			"description": "Public outreach through press and social media",
			"costs": {"money": 30000, "action_points": 2},
			"category": "influence"
		},
		{
			"id": "lobby_government",
			"name": "Lobby Government",
			"description": "Advocate for AI safety regulation (costly but impactful)",
			"costs": {"money": 80000, "action_points": 2},
			"category": "influence"
		},
		{
			"id": "release_warning",
			"name": "Public Warning",
			"description": "Warn public about AI risks - risky but high impact",
			"costs": {"action_points": 2, "reputation": 15},
			"category": "influence"
		},
		{
			"id": "open_source_release",
			"name": "Open Source Tools",
			"description": "Release safety research publicly for community benefit",
			"costs": {"papers": 3, "action_points": 1},
			"category": "influence"
		}
	]

static func get_strategic_options() -> Array[Dictionary]:
	"""Get all strategic/high-stakes submenu options"""
	return [
		{
			"id": "acquire_startup",
			"name": "Acquire Startup",
			"description": "Buy struggling AI startup for talent and compute",
			"costs": {"money": 150000, "action_points": 2},
			"category": "strategic"
		},
		{
			"id": "sabotage_competitor",
			"name": "Corporate Espionage",
			"description": "Slow down competitors (unethical, risky)",
			"costs": {"money": 100000, "action_points": 3, "reputation": 20},
			"category": "strategic"
		},
		{
			"id": "emergency_pivot",
			"name": "Emergency Pivot",
			"description": "Convert capability researchers to safety focus",
			"costs": {"money": 50000, "action_points": 2},
			"category": "strategic"
		},
		{
			"id": "grant_proposal",
			"name": "Grant Proposal",
			"description": "Apply for government/foundation funding",
			"costs": {"action_points": 1, "papers": 1},
			"category": "strategic"
		}
	]

static func execute_action(action_id: String, state: GameState) -> Dictionary:
	"""Execute an action, modify state, return result"""
	# Special case: pass_turn is a virtual action that doesn't need to be in the action list
	if action_id == "pass_turn":
		return {"success": true, "message": "Passed turn (no actions taken)"}

	var action = get_action_by_id(action_id)
	if action.is_empty():
		return {"success": false, "message": "Unknown action: " + action_id}

	# Check affordability
	if not state.can_afford(action["costs"]):
		return {"success": false, "message": "Cannot afford " + action["name"]}

	# Spend costs
	state.spend_resources(action["costs"])

	# Apply effects based on action type
	var result = {"success": true, "message": action["name"] + " executed"}

	match action_id:
		"pass":
			# Do nothing action - just waste the action point with no effect
			result["message"] = "Passed this action. No resources spent."

		"hire_staff":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening hiring menu..."
			result["open_submenu"] = "hiring"

		"hire_safety_researcher":
			var hire_result = _hire_from_pool(state, "safety")
			if not hire_result["success"]:
				result["success"] = false
				# Refund resources since hire failed
				state.add_resources(action["costs"])
			result["message"] = hire_result["message"]

		"hire_capability_researcher":
			var hire_result = _hire_from_pool(state, "capabilities")
			if not hire_result["success"]:
				result["success"] = false
				state.add_resources(action["costs"])
			result["message"] = hire_result["message"]

		"hire_interpretability_researcher":
			var hire_result = _hire_from_pool(state, "interpretability")
			if not hire_result["success"]:
				result["success"] = false
				state.add_resources(action["costs"])
			result["message"] = hire_result["message"]

		"hire_alignment_researcher":
			var hire_result = _hire_from_pool(state, "alignment")
			if not hire_result["success"]:
				result["success"] = false
				state.add_resources(action["costs"])
			result["message"] = hire_result["message"]

		"hire_compute_engineer":
			state.compute_engineers += 1
			result["message"] = "Hired compute engineer (+1 compute staff)"

		"hire_manager":
			state.managers += 1
			var capacity = state.get_management_capacity()
			result["message"] = "Hired manager (+1 manager, capacity: %d employees)" % capacity

		"buy_compute":
			state.add_resources({"compute": 50})
			result["message"] = "Purchased compute (+50 compute)"

		"safety_research":
			# Safety research reduces doom
			var doom_reduction = state.safety_researchers * 1.0
			state.add_resources({"doom": -doom_reduction})
			result["message"] = "Safety research (-%0.1f doom)" % doom_reduction

		"capability_research":
			# Capability research generates research points
			var research_gained = state.capability_researchers * 5.0
			state.add_resources({"research": research_gained})
			result["message"] = "Capability research (+%0.1f research)" % research_gained

		"publish_paper":
			# Check for media_savvy researchers (bonus reputation)
			var media_savvy_bonus = 0
			for researcher in state.researchers:
				if researcher.has_trait("media_savvy"):
					media_savvy_bonus += 3  # +3 reputation per media savvy researcher
			var total_rep = 2 + media_savvy_bonus
			state.add_resources({"papers": 1, "doom": -3, "reputation": total_rep})
			if media_savvy_bonus > 0:
				result["message"] = "Published paper (+1 paper, -3 doom, +%d reputation including media bonus)" % total_rep
			else:
				result["message"] = "Published paper (+1 paper, -3 doom, +2 reputation)"

		"fundraise":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening fundraising menu..."
			result["open_submenu"] = "fundraising"

		"publicity":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening publicity menu..."
			result["open_submenu"] = "publicity"

		"strategic":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening strategic menu..."
			result["open_submenu"] = "strategic"

		"fundraise_small":
			var money_raised = state.rng.randi_range(30000, 60000)

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("fundraise_small_amount", float(money_raised), state.turn)

			state.add_resources({"money": money_raised})
			result["message"] = "Modest funding round successful! Raised %s" % GameConfig.format_money(money_raised)

		"fundraise_big":
			var base_amount = state.rng.randi_range(80000, 150000)

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("fundraise_big_amount", float(base_amount), state.turn)

			var rep_bonus = int(state.reputation * 500)
			var total_raised = base_amount + rep_bonus
			state.add_resources({"money": total_raised})
			result["message"] = "Major funding round! Raised %s (base: %s, reputation bonus: %s)" % [GameConfig.format_money(total_raised), GameConfig.format_money(base_amount), GameConfig.format_money(rep_bonus)]

		"take_loan":
			state.add_resources({"money": 75000})
			# Note: debt tracking would require expanded state
			result["message"] = "Loan approved! Received %s (repayment: %s due later)" % [GameConfig.format_money(75000), GameConfig.format_money(90000)]

		"apply_grant":
			var grant_amount = state.rng.randi_range(50000, 100000)

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("apply_grant_amount", float(grant_amount), state.turn)

			var paper_bonus = state.papers * 5000
			var total = grant_amount + paper_bonus
			state.add_resources({"money": total})
			result["message"] = "Grant approved! Received %s (base: %s, papers bonus: %s)" % [GameConfig.format_money(total), GameConfig.format_money(grant_amount), GameConfig.format_money(paper_bonus)]

		"network":
			state.add_resources({"reputation": 3})
			result["message"] = "Networking (+3 reputation)"

		"team_building":
			# Reduce burnout for all researchers
			var burnout_reduced = 0.0
			for researcher in state.researchers:
				var reduction = min(researcher.burnout, 15.0)
				researcher.reduce_burnout(reduction)
				burnout_reduced += reduction
			state.add_resources({"reputation": 2, "doom": -1})
			if burnout_reduced > 0:
				result["message"] = "Team building event (+2 reputation, -1 doom, -%.0f team burnout)" % burnout_reduced
			else:
				result["message"] = "Team building event (+2 reputation, -1 doom)"

		"media_campaign":
			var rep_gained = 10 + int(state.reputation * 0.1)
			state.add_resources({"reputation": rep_gained})
			result["message"] = "Media campaign (+%d reputation)" % rep_gained

		"audit_safety":
			var doom_reduced = 5 + state.safety_researchers
			state.add_resources({"doom": -doom_reduced, "reputation": 3})
			result["message"] = "Safety audit (-%d doom, +3 reputation)" % doom_reduced

		"order_supplies":
			state.stationery = min(state.stationery + 50.0, 100.0)
			result["message"] = "Office supplies restocked (+50 stationery, now at %.0f)" % state.stationery

		"lobby_government":
			# Lobbying reduces doom but costs reputation (fix #449)
			var doom_reduction = 8 + (state.reputation * 0.1)
			state.add_resources({"doom": -doom_reduction, "reputation": -10})
			result["message"] = "Government lobbying (-%0.1f doom, -10 reputation)" % doom_reduction

		"release_warning":
			# Risky: big doom reduction but reputation hit and random outcome
			var doom_roll = state.rng.randi_range(-5, 10)
			var rep_roll = state.rng.randi_range(-10, 5)

			# Record RNG outcomes for verification
			VerificationTracker.record_rng_outcome("release_warning_doom", float(doom_roll), state.turn)
			VerificationTracker.record_rng_outcome("release_warning_rep", float(rep_roll), state.turn)

			var doom_reduction = 15 + doom_roll
			var rep_change = rep_roll
			state.add_resources({"doom": -doom_reduction, "reputation": rep_change})
			result["message"] = "Public warning issued (-%d doom, %+d reputation)" % [doom_reduction, rep_change]

		"acquire_startup":
			# Gain staff and compute
			var staff_type = state.rng.randi_range(0, 2)

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("acquire_startup_type", float(staff_type), state.turn)

			match staff_type:
				0:
					state.safety_researchers += 2
					result["message"] = "Acquired safety-focused startup (+2 safety researchers, +30 compute)"
				1:
					state.capability_researchers += 2
					state.add_resources({"doom": 3})
					result["message"] = "Acquired capability startup (+2 cap researchers, +30 compute, +3 doom)"
				2:
					state.compute_engineers += 2
					result["message"] = "Acquired compute startup (+2 compute engineers, +30 compute)"
			state.add_resources({"compute": 30})

		"sabotage_competitor":
			# Unethical but effective - chance of backfire
			var sabotage_roll = state.rng.randf()

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("sabotage_success", sabotage_roll, state.turn)

			if sabotage_roll > 0.3:  # 70% success
				var doom_reduction = 20
				state.add_resources({"doom": -doom_reduction})
				result["message"] = "Sabotage successful! Competitor delayed (-%d doom)" % doom_reduction
			else:  # 30% caught
				state.add_resources({"doom": 10, "reputation": -25})
				result["message"] = "Sabotage EXPOSED! Major scandal (+10 doom, -25 reputation)"

		"open_source_release":
			# Share research for global benefit
			var doom_reduction = 10 + (state.papers * 2)
			state.add_resources({"doom": -doom_reduction, "reputation": 15})
			result["message"] = "Open source release! (-%d doom, +15 reputation)" % doom_reduction

		"emergency_pivot":
			# Convert capability researchers to safety researchers
			var pivot_roll = state.rng.randi_range(1, 3)

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("emergency_pivot_count", float(pivot_roll), state.turn)

			var converted = min(state.capability_researchers, pivot_roll)
			if converted > 0:
				state.capability_researchers -= converted
				state.safety_researchers += converted
				result["message"] = "Emergency pivot! Converted %d researchers to safety" % converted
			else:
				result["success"] = false
				result["message"] = "No capability researchers to convert!"

		"grant_proposal":
			# Random funding based on reputation
			var base_funding = 80000
			var bonus = state.reputation * 1500
			var total = base_funding + bonus
			state.add_resources({"money": total})
			result["message"] = "Grant approved! Received %s" % GameConfig.format_money(total)

		"hire_ethicist":
			# Ethicist improves safety research effectiveness
			state.add_resources({"reputation": 5})
			# Note: Would track ethicist count in expanded state
			result["message"] = "Hired AI ethicist (+5 reputation, improves safety research)"

	return result

static func _assign_random_traits(researcher: Researcher, rng: RandomNumberGenerator):
	"""Assign random traits to a new researcher"""
	# 40% chance of one positive trait
	if rng.randf() < 0.40:
		var positive_traits = ["workaholic", "team_player", "media_savvy", "safety_conscious", "fast_learner"]
		var trait_id = positive_traits[rng.randi() % positive_traits.size()]
		researcher.add_trait(trait_id)

	# 25% chance of one negative trait
	if rng.randf() < 0.25:
		var negative_traits = ["prima_donna", "leak_prone", "burnout_prone", "pessimist"]
		var trait_id = negative_traits[rng.randi() % negative_traits.size()]
		researcher.add_trait(trait_id)

static func _hire_from_pool(state: GameState, specialization: String) -> Dictionary:
	"""Try to hire a candidate from the pool with matching specialization"""
	var candidates = state.get_candidates_by_spec(specialization)

	if candidates.size() == 0:
		# No matching candidates - fail gracefully
		return {
			"success": false,
			"message": "No %s specialists in hiring pool (wait for candidates)" % specialization
		}

	# Hire the first matching candidate
	var candidate = candidates[0]
	state.hire_candidate(candidate)

	var trait_info = ""
	if candidate.traits.size() > 0:
		trait_info = " [%s]" % candidate.get_trait_description()

	var spec_name = specialization.capitalize()
	return {
		"success": true,
		"message": "Hired %s (%s Specialist, Skill %d)%s" % [
			candidate.researcher_name,
			spec_name,
			candidate.skill_level,
			trait_info
		],
		"hired_researcher": candidate
	}

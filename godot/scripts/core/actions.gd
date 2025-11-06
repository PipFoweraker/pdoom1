extends Node
class_name GameActions
## Action definitions - what players can do

static func get_all_actions() -> Array[Dictionary]:
	"""Return all available actions"""
	return [
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
			"id": "network",
			"name": "Networking",
			"description": "Build relationships, gain reputation",
			"costs": {"action_points": 1},
			"category": "management"
		},
		{
			"id": "team_building",
			"name": "Team Building",
			"description": "Improve morale, reduce doom slightly",
			"costs": {"money": 10000, "action_points": 1},
			"category": "management"
		},
		{
			"id": "media_campaign",
			"name": "Media Campaign",
			"description": "Public outreach, gain reputation",
			"costs": {"money": 30000, "action_points": 2},
			"category": "management"
		},
		{
			"id": "audit_safety",
			"name": "Safety Audit",
			"description": "Comprehensive safety review",
			"costs": {"money": 40000, "action_points": 2},
			"category": "research"
		},
		# New strategic actions
		{
			"id": "lobby_government",
			"name": "Lobby Government",
			"description": "Advocate for AI safety regulation",
			"costs": {"money": 80000, "action_points": 2, "reputation": 10},
			"category": "influence"
		},
		{
			"id": "release_warning",
			"name": "Public Warning",
			"description": "Warn public about AI risks - risky but impactful",
			"costs": {"action_points": 2, "reputation": 15},
			"category": "influence"
		},
		{
			"id": "acquire_startup",
			"name": "Acquire AI Startup",
			"description": "Buy struggling AI startup for talent/compute",
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
			"id": "open_source_release",
			"name": "Open Source Safety Tools",
			"description": "Release safety research publicly",
			"costs": {"papers": 3, "action_points": 1},
			"category": "influence"
		},
		{
			"id": "emergency_pivot",
			"name": "Emergency Pivot",
			"description": "Radical strategy change - convert capability researchers to safety",
			"costs": {"money": 50000, "action_points": 2},
			"category": "strategic"
		},
		{
			"id": "grant_proposal",
			"name": "Write Grant Proposal",
			"description": "Apply for government/foundation funding",
			"costs": {"action_points": 1, "papers": 1},
			"category": "funding"
		},
		{
			"id": "hire_ethicist",
			"name": "Hire AI Ethicist",
			"description": "Add philosophical perspective to research",
			"costs": {"money": 70000, "action_points": 1},
			"category": "hiring"
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
			"description": "Can oversee 9 employees (prevents unproductive staff)",
			"costs": {"money": 80000, "action_points": 1},
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

static func execute_action(action_id: String, state: GameState) -> Dictionary:
	"""Execute an action, modify state, return result"""
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
		"hire_staff":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening hiring menu..."
			result["open_submenu"] = "hiring"

		"hire_safety_researcher":
			var safety_researcher = Researcher.new("safety")
			state.add_researcher(safety_researcher)
			result["message"] = "Hired %s (Safety Specialist, Skill %d)" % [safety_researcher.researcher_name, safety_researcher.skill_level]

		"hire_capability_researcher":
			var cap_researcher = Researcher.new("capabilities")
			state.add_researcher(cap_researcher)
			result["message"] = "Hired %s (Capabilities Specialist, Skill %d)" % [cap_researcher.researcher_name, cap_researcher.skill_level]

		"hire_interpretability_researcher":
			var interp_researcher = Researcher.new("interpretability")
			state.add_researcher(interp_researcher)
			result["message"] = "Hired %s (Interpretability Specialist, Skill %d)" % [interp_researcher.researcher_name, interp_researcher.skill_level]

		"hire_alignment_researcher":
			var align_researcher = Researcher.new("alignment")
			state.add_researcher(align_researcher)
			result["message"] = "Hired %s (Alignment Specialist, Skill %d)" % [align_researcher.researcher_name, align_researcher.skill_level]

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
			state.add_resources({"papers": 1, "doom": -3, "reputation": 2})
			result["message"] = "Published paper (+1 paper, -3 doom, +2 reputation)"

		"fundraise":
			# Submenu action - doesn't execute, opens dialog
			result["message"] = "Opening fundraising menu..."
			result["open_submenu"] = "fundraising"

		"fundraise_small":
			var money_raised = state.rng.randi_range(30000, 60000)
			state.add_resources({"money": money_raised})
			result["message"] = "Modest funding round successful! Raised $%d" % money_raised

		"fundraise_big":
			var base_amount = state.rng.randi_range(80000, 150000)
			var rep_bonus = int(state.reputation * 500)
			var total_raised = base_amount + rep_bonus
			state.add_resources({"money": total_raised})
			result["message"] = "Major funding round! Raised $%d (base: $%d, reputation bonus: $%d)" % [total_raised, base_amount, rep_bonus]

		"take_loan":
			state.add_resources({"money": 75000})
			# Note: debt tracking would require expanded state
			result["message"] = "Loan approved! Received $75,000 (repayment: $90,000 due later)"

		"apply_grant":
			var grant_amount = state.rng.randi_range(50000, 100000)
			var paper_bonus = state.papers * 5000
			var total = grant_amount + paper_bonus
			state.add_resources({"money": total})
			result["message"] = "Grant approved! Received $%d (base: $%d, papers bonus: $%d)" % [total, grant_amount, paper_bonus]

		"network":
			state.add_resources({"reputation": 3})
			result["message"] = "Networking (+3 reputation)"

		"team_building":
			state.add_resources({"reputation": 2, "doom": -1})
			result["message"] = "Team building event (+2 reputation, -1 doom)"

		"media_campaign":
			var rep_gained = 10 + int(state.reputation * 0.1)
			state.add_resources({"reputation": rep_gained})
			result["message"] = "Media campaign (+%d reputation)" % rep_gained

		"audit_safety":
			var doom_reduced = 5 + state.safety_researchers
			state.add_resources({"doom": -doom_reduced, "reputation": 3})
			result["message"] = "Safety audit (-%d doom, +3 reputation)" % doom_reduced

		"lobby_government":
			# Lobbying reduces doom and can trigger policy events
			var doom_reduction = 8 + (state.reputation * 0.1)
			state.add_resources({"doom": -doom_reduction, "reputation": 5})
			result["message"] = "Government lobbying (-%0.1f doom, +5 reputation)" % doom_reduction

		"release_warning":
			# Risky: big doom reduction but reputation hit and random outcome
			var doom_reduction = 15 + state.rng.randi_range(-5, 10)
			var rep_change = state.rng.randi_range(-10, 5)
			state.add_resources({"doom": -doom_reduction, "reputation": rep_change})
			result["message"] = "Public warning issued (-%d doom, %+d reputation)" % [doom_reduction, rep_change]

		"acquire_startup":
			# Gain staff and compute
			var staff_type = state.rng.randi_range(0, 2)
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
			if state.rng.randf() > 0.3:  # 70% success
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
			var converted = min(state.capability_researchers, state.rng.randi_range(1, 3))
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
			result["message"] = "Grant approved! Received $%d" % total

		"hire_ethicist":
			# Ethicist improves safety research effectiveness
			state.add_resources({"reputation": 5})
			# Note: Would track ethicist count in expanded state
			result["message"] = "Hired AI ethicist (+5 reputation, improves safety research)"

	return result

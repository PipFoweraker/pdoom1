extends Node
class_name GameActions
## Action definitions - what players can do
##
## Actions can have unlock conditions that determine when they become visible.
## Unlock conditions are checked via is_action_unlocked() before displaying.
##
## Unlock condition types:
##   turn_min: int - Minimum turn number to unlock
##   staff_min: int - Minimum total staff count to unlock
##   reputation_min: float - Minimum reputation to unlock
##   papers_min: int - Minimum papers published to unlock
##   has_upgrade: String - Requires specific upgrade to be purchased
##   research_min: float - Minimum research points to unlock


## Check if an action is unlocked based on game state
static func is_action_unlocked(action: Dictionary, state: Dictionary) -> bool:
	"""Check if action unlock conditions are met"""
	var conditions = action.get("unlock_conditions", {})

	# No conditions = always unlocked
	if conditions.is_empty():
		return true

	# Check turn requirement
	if conditions.has("turn_min"):
		if state.get("turn", 0) < conditions["turn_min"]:
			return false

	# Check staff requirement
	if conditions.has("staff_min"):
		if state.get("total_staff", 0) < conditions["staff_min"]:
			return false

	# Check reputation requirement
	if conditions.has("reputation_min"):
		if state.get("reputation", 0) < conditions["reputation_min"]:
			return false

	# Check papers requirement
	if conditions.has("papers_min"):
		if state.get("papers", 0) < conditions["papers_min"]:
			return false

	# Check research requirement
	if conditions.has("research_min"):
		if state.get("research", 0) < conditions["research_min"]:
			return false

	# Check upgrade requirement
	if conditions.has("has_upgrade"):
		var purchased = state.get("purchased_upgrades", [])
		if not purchased.has(conditions["has_upgrade"]):
			return false

	return true


## Get unlock status description for UI tooltip
static func get_unlock_hint(action: Dictionary, state: Dictionary) -> String:
	"""Get a hint about what's needed to unlock an action"""
	var conditions = action.get("unlock_conditions", {})
	var hints: Array[String] = []

	if conditions.has("turn_min"):
		var current = state.get("turn", 0)
		var required = conditions["turn_min"]
		if current < required:
			hints.append("Unlocks at turn %d" % required)

	if conditions.has("staff_min"):
		var current = state.get("total_staff", 0)
		var required = conditions["staff_min"]
		if current < required:
			hints.append("Requires %d staff (%d/%d)" % [required, current, required])

	if conditions.has("reputation_min"):
		var current = state.get("reputation", 0)
		var required = conditions["reputation_min"]
		if current < required:
			hints.append("Requires %.0f reputation (%.0f/%.0f)" % [required, current, required])

	if conditions.has("papers_min"):
		var current = state.get("papers", 0)
		var required = conditions["papers_min"]
		if current < required:
			hints.append("Requires %d papers (%d/%d)" % [required, current, required])

	if conditions.has("has_upgrade"):
		var upgrade_id = conditions["has_upgrade"]
		var purchased = state.get("purchased_upgrades", [])
		if not purchased.has(upgrade_id):
			hints.append("Requires upgrade: %s" % upgrade_id)

	if hints.is_empty():
		return ""
	return " | ".join(hints)


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
			"category": "management",
			"unlock_conditions": {"staff_min": 2}  # Unlocks when you have 2+ staff
		},
		{
			"id": "audit_safety",
			"name": "Safety Audit",
			"description": "Comprehensive safety review",
			"costs": {"money": 40000, "action_points": 2},
			"category": "research",
			"unlock_conditions": {"turn_min": 5}  # Unlocks at turn 5
		},
		# Operations submenu for routine management tasks
		{
			"id": "operations",
			"name": "Operations",
			"description": "Routine office operations and maintenance",
			"costs": {},  # No cost to open menu
			"category": "management",
			"is_submenu": true
		},
		# Strategic submenu for high-cost/risky actions
		{
			"id": "strategic",
			"name": "Strategic",
			"description": "High-stakes strategic moves and risky plays",
			"costs": {},  # No cost to open menu
			"category": "strategic",
			"is_submenu": true,
			"unlock_conditions": {"turn_min": 10, "reputation_min": 30}  # Advanced options
		},
		# Travel & Conferences submenu (Issue #468)
		{
			"id": "travel",
			"name": "Travel & Conferences",
			"description": "Academic travel, paper submissions, and conference attendance",
			"costs": {},  # No cost to open menu
			"category": "research",
			"is_submenu": true,
			"unlock_conditions": {"papers_min": 1}  # Need at least 1 paper to unlock
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
	for action in get_travel_options():
		if action["id"] == action_id:
			return action
	for action in get_operations_options():
		if action["id"] == action_id:
			return action
	# Special pass action (not in any submenu)
	if action_id == "pass":
		return get_pass_action()
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

static func get_travel_options() -> Array[Dictionary]:
	"""Get all travel/conference submenu options (Issue #468)"""
	return [
		{
			"id": "submit_paper",
			"name": "Submit Paper",
			"description": "Submit research paper to a conference (multi-turn review process)",
			"costs": {"research": 15, "action_points": 1},
			"category": "travel"
		},
		{
			"id": "attend_conference",
			"name": "Attend Conference",
			"description": "Travel to present accepted paper or network at a conference",
			"costs": {"action_points": 2},  # Money cost calculated dynamically
			"category": "travel"
		},
		{
			"id": "send_delegation",
			"name": "Send Delegation",
			"description": "[Coming Soon] Send researchers to attend on your behalf",
			"costs": {},
			"category": "travel",
			"is_stub": true
		}
	]

static func get_operations_options() -> Array[Dictionary]:
	"""Get all operations/maintenance submenu options"""
	return [
		{
			"id": "order_supplies",
			"name": "Order Office Supplies",
			"description": "Restock stationery (+50 supplies). Staff consume supplies each turn.",
			"costs": {"money": 2000, "action_points": 1},
			"category": "operations"
		},
		{
			"id": "office_maintenance",
			"name": "Office Maintenance",
			"description": "Routine repairs and cleaning. Improves morale slightly.",
			"costs": {"money": 5000, "action_points": 1},
			"category": "operations"
		}
	]

static func get_pass_action() -> Dictionary:
	"""Get the special pass/do nothing action (shown in command zone, not action list)"""
	return {
		"id": "pass",
		"name": "Do Nothing",
		"description": "Skip this action. Conserve resources but waste time.",
		"costs": {},  # Free action, always available
		"category": "command"
	}

static func execute_action(action_id: String, state: GameState) -> Dictionary:
	"""Execute an action, modify state, return result
	Note: AP costs are handled by the commit system in game_manager.gd (committed_ap).
	Only non-AP costs (money, research, etc.) are spent here."""
	# Special case: pass_turn is a virtual action that doesn't need to be in the action list
	if action_id == "pass_turn":
		return {"success": true, "message": "Passed turn (no actions taken)"}

	var action = get_action_by_id(action_id)
	if action.is_empty():
		return {"success": false, "message": "Unknown action: " + action_id}

	# Build costs without AP (AP already deducted via committed_ap system)
	var execution_costs = action["costs"].duplicate()
	execution_costs.erase("action_points")

	# Check affordability (non-AP costs only)
	if not state.can_afford(execution_costs):
		return {"success": false, "message": "Cannot afford " + action["name"]}

	# Spend non-AP costs
	state.spend_resources(execution_costs)

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

		"travel":
			# Submenu action - doesn't execute, opens dialog (Issue #468)
			result["message"] = "Opening travel menu..."
			result["open_submenu"] = "travel"

		"operations":
			# Submenu action - opens operations menu
			result["message"] = "Opening operations menu..."
			result["open_submenu"] = "operations"

		"submit_paper":
			# Paper submission action (Issue #468)
			# This is handled by UI - creates paper and adds to state
			result["message"] = "Opening paper submission dialog..."
			result["open_dialog"] = "submit_paper"

		"attend_conference":
			# Conference attendance action (Issue #468)
			# This is handled by UI - selects conference and pays costs
			result["message"] = "Opening conference selection..."
			result["open_dialog"] = "attend_conference"

		"send_delegation":
			# Stub for Issue #411 - delegation system
			result["success"] = false
			result["message"] = "[Issue #411] Delegation system coming soon! For now, attend conferences yourself."
			# Refund any spent costs
			state.add_resources(action["costs"])

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
	var candidate: Researcher = null

	# Check if a specific candidate was queued for this specialization
	for i in range(state.pending_hire_queue.size()):
		var queued = state.pending_hire_queue[i]
		if queued.specialization == specialization:
			candidate = queued
			state.pending_hire_queue.remove_at(i)
			break

	# If no specific candidate queued, get first match from pool
	if candidate == null:
		var candidates = state.get_candidates_by_spec(specialization)
		if candidates.size() == 0:
			# No matching candidates - fail gracefully
			return {
				"success": false,
				"message": "No %s specialists in hiring pool (wait for candidates)" % specialization
			}
		candidate = candidates[0]
		# Remove from pool since we're hiring them
		state.remove_candidate(candidate)

	# Hire the selected candidate
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

# ============================================
# Paper Submission & Conference Functions (Issue #468)
# ============================================

static func submit_paper_to_conference(state: GameState, conf_id: String, topic: int, research_amount: float, lead_researcher: Researcher) -> Dictionary:
	"""Submit a paper to a conference"""
	var conf = Conferences.get_conference_by_id(conf_id)
	if conf == null:
		return {"success": false, "message": "Conference not found: " + conf_id}

	# Check research cost
	if state.research < research_amount:
		return {"success": false, "message": "Not enough research points"}

	# Check AP cost
	if state.action_points < 1:
		return {"success": false, "message": "Not enough action points"}

	# Calculate paper quality
	var has_media_savvy = lead_researcher != null and lead_researcher.has_trait("media_savvy")
	var lead_skill = lead_researcher.skill_level if lead_researcher != null else 3
	var quality = PaperSubmissions.calculate_paper_quality(research_amount, lead_skill, 0, has_media_savvy)

	# Create paper submission
	var paper = PaperSubmissions.PaperSubmission.new()
	paper.target_conference_id = conf_id
	paper.topic = topic
	paper.research_invested = research_amount
	paper.quality = quality
	paper.lead_researcher_name = lead_researcher.researcher_name if lead_researcher != null else "Anonymous"
	paper.submit_turn = state.turn
	paper.decision_turn = state.turn + (conf.review_period_weeks * 5)  # 5 turns per week
	paper.status = PaperSubmissions.Status.UNDER_REVIEW
	paper.title = PaperSubmissions.generate_paper_title(topic, state.rng)

	# Spend resources
	state.spend_resources({"research": research_amount, "action_points": 1})

	# Add to tracking
	state.add_paper_submission(paper)

	# Record for verification
	VerificationTracker.record_rng_outcome("paper_quality_%s" % paper.id, quality, state.turn)

	var accept_prob = Conferences.calculate_acceptance_probability(quality, conf.prestige, state.reputation)

	return {
		"success": true,
		"message": "Submitted '%s' to %s (Quality: %.0f%%, Est. acceptance: %.0f%%)" % [
			paper.title,
			conf.name,
			quality * 100,
			accept_prob * 100
		],
		"paper": paper
	}

static func get_travel_cost_with_class(conf: Conferences.Conference, travel_class: String) -> Dictionary:
	"""Calculate travel cost including travel class multiplier (Issue #469)"""
	var base_cost = conf.get_travel_cost()
	var class_data = Researcher.TRAVEL_CLASS.get(travel_class, Researcher.TRAVEL_CLASS["economy"])
	var multiplier = class_data["cost_multiplier"]

	return {
		"flights": int(base_cost.flights * multiplier),
		"accommodation": int(base_cost.accommodation * multiplier),
		"registration": base_cost.registration,  # Registration doesn't change
		"total": int((base_cost.flights + base_cost.accommodation) * multiplier) + base_cost.registration,
		"travel_class": travel_class,
		"class_name": class_data["name"]
	}

static func attend_conference_action(state: GameState, conf_id: String, travel_class: String = "economy", traveler: Researcher = null) -> Dictionary:
	"""Attend a conference (with or without presenting)
	Issue #469: includes travel class and jet lag
	TODO: Multi-stage travel booking - player shouldn't see all options upfront.
	Future flow: Express Interest → Arrange Travel (class, costs) → Attend
	Requires situational awareness or researcher scouting to preview details."""
	var conf = Conferences.get_conference_by_id(conf_id)
	if conf == null:
		return {"success": false, "message": "Conference not found: " + conf_id}

	# Check if already attended this year
	if state.has_attended_conference(conf_id):
		return {"success": false, "message": "Already attended %s this year" % conf.name}

	# Calculate travel cost with class (Issue #469)
	var travel_cost = get_travel_cost_with_class(conf, travel_class)

	# Check affordability
	if not state.can_afford({"money": travel_cost.total, "action_points": 2}):
		return {"success": false, "message": "Cannot afford: %s + 2 AP required" % GameConfig.format_money(travel_cost.total)}

	# Spend resources
	state.spend_resources({"money": travel_cost.total, "action_points": 2})
	state.mark_conference_attended(conf_id)

	# Apply jet lag to traveler if specified (Issue #469)
	var jet_lag_msg = ""
	if traveler != null and conf.location_tier > 1:
		traveler.apply_jet_lag(conf.location_tier, travel_class)
		if traveler.jet_lag_turns > 0:
			jet_lag_msg = " | %s has jet lag (%d turns)" % [traveler.researcher_name, traveler.jet_lag_turns]

	# Check if presenting a paper
	var presenting_paper = state.get_accepted_paper_for_conference(conf_id)
	if presenting_paper != null:
		presenting_paper.status = PaperSubmissions.Status.PRESENTED

		# Presenting gives full benefits
		var rep_gain = conf.reputation_gain * 1.5
		var doom_reduction = conf.doom_reduction

		# Safety papers reduce doom more
		if presenting_paper.is_safety_paper():
			doom_reduction *= 1.5

		state.add_resources({"reputation": rep_gain, "doom": -doom_reduction})

		return {
			"success": true,
			"message": "Presented '%s' at %s! (+%.0f rep, -%.1f doom, cost: %s %s)%s" % [
				presenting_paper.title,
				conf.name,
				rep_gain,
				doom_reduction,
				GameConfig.format_money(travel_cost.total),
				travel_cost.class_name,
				jet_lag_msg
			],
			"presented": true,
			"paper": presenting_paper,
			"travel_class": travel_class
		}
	else:
		# Networking only - reduced benefits
		var rep_gain = conf.reputation_gain * 0.5
		state.add_resources({"reputation": rep_gain})

		return {
			"success": true,
			"message": "Attended %s for networking (+%.0f rep, cost: %s %s)%s" % [
				conf.name,
				rep_gain,
				GameConfig.format_money(travel_cost.total),
				travel_cost.class_name,
				jet_lag_msg
			],
			"presented": false,
			"travel_class": travel_class
		}

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
			"description": "Raise money from investors",
			"costs": {"action_points": 2, "reputation": 5},
			"category": "management"
		},
		{
			"id": "network",
			"name": "Networking",
			"description": "Build relationships, gain reputation",
			"costs": {"action_points": 1},
			"category": "management"
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
			state.safety_researchers += 1
			result["message"] = "Hired safety researcher (+1 safety staff)"

		"hire_capability_researcher":
			state.capability_researchers += 1
			state.add_resources({"doom": 2})  # Capabilities increase doom
			result["message"] = "Hired capability researcher (+1 cap staff, +2 doom)"

		"hire_compute_engineer":
			state.compute_engineers += 1
			result["message"] = "Hired compute engineer (+1 compute staff)"

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
			var money_raised = 100000 + (state.reputation * 1000)
			state.add_resources({"money": money_raised})
			result["message"] = "Fundraised $%d" % money_raised

		"network":
			state.add_resources({"reputation": 3})
			result["message"] = "Networking (+3 reputation)"

	return result

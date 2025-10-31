extends Node
class_name GameEvents
## Random and triggered events system

# Track which events have already triggered
static var triggered_events: Array[String] = []

static func get_all_events() -> Array[Dictionary]:
	"""Return all event definitions"""
	return [
		{
			"id": "funding_crisis",
			"name": "Funding Crisis",
			"description": "Your lab is running dangerously low on funds!",
			"type": "popup",
			"trigger_type": "turn_and_resource",
			"trigger_turn": 10,
			"trigger_condition": "money < 50000",
			"repeatable": false,
			"options": [
				{
					"id": "emergency_fundraise",
					"text": "Emergency Fundraising",
					"effects": {"money": 75000},
					"message": "Secured emergency funding: +$75,000"
				},
				{
					"id": "accept",
					"text": "Continue Anyway",
					"effects": {},
					"message": "Continuing with limited funds..."
				}
			]
		},
		{
			"id": "talent_recruitment",
			"name": "Talent Opportunity",
			"description": "A brilliant researcher wants to join your lab at reduced cost!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.15,
			"min_turn": 5,
			"repeatable": true,
			"options": [
				{
					"id": "hire_discounted",
					"text": "Hire at Discount ($25k)",
					"costs": {"money": 25000},
					"effects": {"safety_researchers": 1, "doom": -2},
					"message": "Hired talented researcher at discount! (+1 safety researcher, -2 doom)"
				},
				{
					"id": "decline",
					"text": "Decline Offer",
					"effects": {},
					"message": "Declined recruitment opportunity"
				}
			]
		},
		{
			"id": "ai_breakthrough",
			"name": "AI Breakthrough!",
			"description": "Your team has made an unexpected AI capability advancement!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.10,
			"min_turn": 8,
			"repeatable": true,
			"options": [
				{
					"id": "publish_open",
					"text": "Publish Openly",
					"effects": {"doom": 5, "reputation": 10, "research": 20},
					"message": "Published breakthrough! (+5 doom, +10 reputation, +20 research)"
				},
				{
					"id": "keep_proprietary",
					"text": "Keep Proprietary",
					"effects": {"doom": 2, "research": 30},
					"message": "Kept research proprietary (+2 doom, +30 research)"
				},
				{
					"id": "safety_review",
					"text": "Conduct Safety Review First",
					"costs": {"action_points": 1, "money": 20000},
					"effects": {"doom": 1, "research": 15, "reputation": 5},
					"message": "Safety review complete (+1 doom, +15 research, +5 reputation)"
				}
			]
		},
		{
			"id": "funding_windfall",
			"name": "Unexpected Funding",
			"description": "A philanthropist wants to donate to your safety research!",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "papers >= 3 and reputation >= 40",
			"repeatable": false,
			"options": [
				{
					"id": "accept_donation",
					"text": "Accept Donation",
					"effects": {"money": 150000, "reputation": 5},
					"message": "Accepted $150,000 donation! (+5 reputation)"
				},
				{
					"id": "decline_donation",
					"text": "Decline (Stay Independent)",
					"effects": {"reputation": 3},
					"message": "Declined donation to maintain independence (+3 reputation)"
				}
			]
		},
		{
			"id": "compute_deal",
			"name": "Compute Partnership",
			"description": "A tech company offers discounted compute access!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.12,
			"min_turn": 6,
			"repeatable": true,
			"options": [
				{
					"id": "accept_deal",
					"text": "Accept Deal",
					"effects": {"compute": 100, "reputation": -2},
					"message": "Accepted compute deal (+100 compute, -2 reputation for corporate ties)"
				},
				{
					"id": "negotiate",
					"text": "Negotiate Better Terms",
					"costs": {"reputation": 5},
					"effects": {"compute": 150},
					"message": "Negotiated better terms! (+150 compute, -5 reputation)"
				},
				{
					"id": "decline_deal",
					"text": "Decline",
					"effects": {},
					"message": "Declined compute partnership"
				}
			]
		},
		{
			"id": "employee_burnout",
			"name": "Employee Burnout Crisis",
			"description": "Your team is overworked! Several researchers are considering leaving.",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "safety_researchers >= 5",
			"repeatable": true,
			"options": [
				{
					"id": "team_retreat",
					"text": "Organize Team Retreat ($30k)",
					"costs": {"money": 30000},
					"effects": {"reputation": 5, "doom": -2},
					"message": "Team retreat restored morale (+5 reputation, -2 doom)"
				},
				{
					"id": "salary_raise",
					"text": "Give Raises ($50k)",
					"costs": {"money": 50000},
					"effects": {"reputation": 8},
					"message": "Salary raises improved retention (+8 reputation)"
				},
				{
					"id": "ignore_burnout",
					"text": "Push Through",
					"effects": {"doom": 3},
					"message": "Team morale suffered (+3 doom)"
				}
			]
		},
		{
			"id": "rival_poaching",
			"name": "Rival Lab Poaching",
			"description": "A well-funded competitor is trying to recruit your best researchers!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.08,
			"min_turn": 10,
			"repeatable": true,
			"options": [
				{
					"id": "counter_offer",
					"text": "Counter-Offer ($80k)",
					"costs": {"money": 80000},
					"effects": {},
					"message": "Successfully retained researchers with counter-offer"
				},
				{
					"id": "let_go",
					"text": "Let Them Go",
					"effects": {"safety_researchers": -1, "money": 20000},
					"message": "Lost researcher but saved money (-1 safety researcher, +$20k saved)"
				}
			]
		},
		{
			"id": "media_scandal",
			"name": "Media Scandal",
			"description": "Negative press coverage is damaging your lab's reputation!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.06,
			"min_turn": 7,
			"repeatable": true,
			"options": [
				{
					"id": "pr_campaign",
					"text": "Launch PR Campaign ($40k)",
					"costs": {"money": 40000},
					"effects": {"reputation": 10},
					"message": "PR campaign restored public image (+10 reputation)"
				},
				{
					"id": "ignore_media",
					"text": "Ignore and Focus on Work",
					"effects": {"reputation": -8},
					"message": "Reputation suffered from negative coverage (-8 reputation)"
				}
			]
		},
		{
			"id": "government_regulation",
			"name": "New AI Regulation Proposed",
			"description": "Government is considering new AI safety regulations. Should you lobby?",
			"type": "popup",
			"trigger_type": "threshold",
			"trigger_condition": "doom >= 60",
			"repeatable": false,
			"options": [
				{
					"id": "support_regulation",
					"text": "Publicly Support ($50k lobbying)",
					"costs": {"money": 50000, "action_points": 1},
					"effects": {"doom": -10, "reputation": 15},
					"message": "Regulation passed! Global safety improved (-10 doom, +15 reputation)"
				},
				{
					"id": "oppose_regulation",
					"text": "Oppose (Stay Competitive)",
					"effects": {"doom": 5, "reputation": -5},
					"message": "Regulation weakened (+5 doom, -5 reputation)"
				},
				{
					"id": "stay_neutral",
					"text": "Remain Neutral",
					"effects": {"doom": 2},
					"message": "Stayed neutral as doom increased (+2 doom)"
				}
			]
		},
		{
			"id": "technical_failure",
			"name": "Critical System Failure",
			"description": "Your compute infrastructure suffered a major failure!",
			"type": "popup",
			"trigger_type": "random",
			"probability": 0.05,
			"min_turn": 12,
			"repeatable": true,
			"options": [
				{
					"id": "emergency_repair",
					"text": "Emergency Repair ($60k)",
					"costs": {"money": 60000},
					"effects": {"compute": 30},
					"message": "System repaired and upgraded (+30 compute)"
				},
				{
					"id": "basic_fix",
					"text": "Basic Fix ($20k)",
					"costs": {"money": 20000},
					"effects": {"compute": -20},
					"message": "System limping along (-20 compute)"
				}
			]
		},
		{
			"id": "stray_cat",
			"name": "A Stray Cat Appears!",
			"description": "A friendly stray cat has wandered into your lab. It seems to enjoy watching the researchers work and occasionally walks across keyboards. Adopt it?",
			"type": "popup",
			"trigger_type": "turn_exact",
			"trigger_turn": 7,
			"repeatable": false,
			"options": [
				{
					"id": "adopt_cat",
					"text": "Adopt the Cat",
					"costs": {"money": 500},
					"effects": {"has_cat": 1, "doom": -1},
					"message": "Cat adopted! Your researchers' morale improves slightly. The cat has claimed its spot in the lab. (-1 doom)"
				},
				{
					"id": "feed_and_release",
					"text": "Feed It and Let It Go",
					"costs": {"money": 100},
					"effects": {},
					"message": "You give the cat some food and it wanders off, purring contentedly."
				},
				{
					"id": "shoo_away",
					"text": "Shoo It Away",
					"effects": {"doom": 1},
					"message": "The cat leaves, disappointed. Your researchers seem a bit sad. (+1 doom for being heartless)"
				}
			]
		}
	]

static func check_triggered_events(state: GameState, rng: RandomNumberGenerator) -> Array[Dictionary]:
	"""Check all events and return those that should trigger this turn"""
	var to_trigger: Array[Dictionary] = []

	for event in get_all_events():
		if should_trigger(event, state, rng):
			to_trigger.append(event)
			if not event.get("repeatable", false):
				triggered_events.append(event["id"])

	return to_trigger

static func should_trigger(event: Dictionary, state: GameState, rng: RandomNumberGenerator) -> bool:
	"""Check if event should trigger"""
	var event_id = event.get("id", "")

	# Don't trigger if already triggered (unless repeatable)
	if event_id in triggered_events and not event.get("repeatable", false):
		return false

	var trigger_type = event.get("trigger_type", "")

	match trigger_type:
		"turn_exact":
			# Exact turn trigger (e.g., cat on turn 7)
			return state.turn == event.get("trigger_turn", -1)

		"turn_and_resource":
			# Specific turn + condition
			if state.turn != event.get("trigger_turn", -1):
				return false
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"threshold":
			# Resource threshold condition
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"random":
			# Random chance after min turn
			if state.turn < event.get("min_turn", 0):
				return false
			return rng.randf() < event.get("probability", 0.1)

	return false

static func evaluate_condition(condition: String, state: GameState) -> bool:
	"""Evaluate condition string safely"""
	# Simple parser for conditions like "money < 50000"
	# Format: "resource operator value"

	if condition == "false":
		return false
	if condition == "true":
		return true

	var parts = condition.split(" ")
	if parts.size() < 3:
		return false

	var resource_name = parts[0]
	var operator = parts[1]
	var value_str = parts[2]

	# Get resource value from state
	var resource_value = 0.0
	match resource_name:
		"money":
			resource_value = state.money
		"compute":
			resource_value = state.compute
		"research":
			resource_value = state.research
		"papers":
			resource_value = state.papers
		"reputation":
			resource_value = state.reputation
		"doom":
			resource_value = state.doom
		"action_points":
			resource_value = state.action_points
		"safety_researchers":
			resource_value = state.safety_researchers
		"capability_researchers":
			resource_value = state.capability_researchers
		"compute_engineers":
			resource_value = state.compute_engineers
		"managers":
			resource_value = state.managers
		_:
			return false

	var threshold = float(value_str)

	# Evaluate operator
	match operator:
		"<":
			return resource_value < threshold
		">":
			return resource_value > threshold
		"<=":
			return resource_value <= threshold
		">=":
			return resource_value >= threshold
		"==":
			return abs(resource_value - threshold) < 0.01
		"!=":
			return abs(resource_value - threshold) >= 0.01

	return false

static func execute_event_choice(event: Dictionary, choice_id: String, state: GameState) -> Dictionary:
	"""Execute player's event choice and return result"""
	var options = event.get("options", [])

	# Find chosen option
	var chosen_option: Dictionary = {}
	for opt in options:
		if opt.get("id", "") == choice_id:
			chosen_option = opt
			break

	if chosen_option.is_empty():
		return {"success": false, "message": "Unknown choice"}

	# Check costs
	var costs = chosen_option.get("costs", {})
	if not state.can_afford(costs):
		return {"success": false, "message": "Cannot afford this choice"}

	# Pay costs
	state.spend_resources(costs)

	# Apply effects
	var effects = chosen_option.get("effects", {})
	for key in effects.keys():
		var value = effects[key]

		# Map effect keys to state properties
		match key:
			"money":
				state.money += value
			"compute":
				state.compute += value
			"research":
				state.research += value
			"papers":
				state.papers += value
			"reputation":
				state.reputation += value
			"doom":
				state.doom += value
			"safety_researchers":
				state.safety_researchers += value
			"capability_researchers":
				state.capability_researchers += value
			"compute_engineers":
				state.compute_engineers += value
			"has_cat":
				state.has_cat = (value > 0)

	var message = chosen_option.get("message", "Event resolved")
	return {"success": true, "message": message}

static func reset_triggered_events():
	"""Clear triggered events (for new game)"""
	triggered_events.clear()

extends Node
class_name GameUpgrades
## Upgrade definitions - one-time purchases that don't consume action points

static func get_all_upgrades() -> Array[Dictionary]:
	"""Return all available upgrades"""
	return [
		{
			"id": "upgrade_computer",
			"name": "Upgrade Computer System",
			"description": "Boosts research effectiveness (+1 research per action)",
			"cost": 200000,
			"effect_key": "better_computers",
			"category": "infrastructure"
		},
		{
			"id": "comfy_chairs",
			"name": "Buy Comfy Office Chairs",
			"description": "Staff morale up (less likely to lose staff on low funds)",
			"cost": 120000,
			"effect_key": "comfy_chairs",
			"category": "office"
		},
		{
			"id": "secure_cloud",
			"name": "Secure Cloud Provider",
			"description": "Reduces doom spikes from lab breakthroughs",
			"cost": 160000,
			"effect_key": "secure_cloud",
			"category": "infrastructure"
		},
		{
			"id": "accounting_software",
			"name": "Accounting Software",
			"description": "Enables cash flow tracking, prevents board oversight",
			"cost": 500000,
			"effect_key": "accounting_software",
			"category": "management"
		},
		{
			"id": "hpc_cluster",
			"name": "High-Performance Computing Cluster",
			"description": "Advanced compute infrastructure (+20 compute, research effectiveness +25%)",
			"cost": 800000,
			"effect_key": "hpc_cluster",
			"category": "infrastructure"
		},
		{
			"id": "research_automation",
			"name": "Research Automation Suite",
			"description": "AI-assisted research tools (research actions more effective with compute)",
			"cost": 600000,
			"effect_key": "research_automation",
			"category": "research"
		},
		{
			"id": "cat_adoption",
			"name": "Adopt Office Cat",
			"description": "Morale boost! Reduces doom by 5, unlocks cat-related events",
			"cost": 50000,
			"effect_key": "office_cat",
			"category": "office"
		},
		{
			"id": "supply_automation",
			"name": "Supply Management System",
			"description": "Auto-orders supplies when low (maintains stationery without AP cost)",
			"cost": 25000,
			"effect_key": "supply_automation",
			"category": "office"
		}
	]

static func get_upgrade_by_id(upgrade_id: String) -> Dictionary:
	"""Get specific upgrade definition"""
	for upgrade in get_all_upgrades():
		if upgrade["id"] == upgrade_id:
			return upgrade
	return {}

static func purchase_upgrade(upgrade_id: String, state: GameState) -> Dictionary:
	"""Purchase an upgrade, modify state, return result"""
	var upgrade = get_upgrade_by_id(upgrade_id)
	if upgrade.is_empty():
		return {"success": false, "message": "Unknown upgrade: " + upgrade_id}

	# Check if already purchased
	if state.has_upgrade(upgrade_id):
		return {"success": false, "message": "Already purchased!"}

	# Check affordability (only money cost)
	var cost = upgrade.get("cost", 0)
	if state.money < cost:
		return {"success": false, "message": "Cannot afford %s (need %s, have %s)" % [upgrade["name"], GameConfig.format_money(cost), GameConfig.format_money(state.money)]}

	# Spend money
	state.spend_resources({"money": cost})

	# Add upgrade to purchased list
	state.add_upgrade(upgrade_id)

	# Apply immediate effects based on upgrade
	var result = {"success": true, "message": "%s purchased! (%s)" % [upgrade["name"], GameConfig.format_money(cost)]}

	match upgrade_id:
		"upgrade_computer":
			# Note: Effect is applied passively in research actions
			result["message"] += " Research actions now more effective!"

		"comfy_chairs":
			# Passive morale effect
			result["message"] += " Staff morale improved!"

		"secure_cloud":
			# Passive doom mitigation
			result["message"] += " Research breakthroughs less risky!"

		"accounting_software":
			# Unlocks cash flow tracking
			result["message"] += " Cash flow tracking enabled!"

		"hpc_cluster":
			state.add_resources({"compute": 20})
			result["message"] += " +20 compute, research 25% more effective!"

		"research_automation":
			# Passive research boost with compute
			result["message"] += " Research scales with compute!"

		"cat_adoption":
			state.add_resources({"doom": -5})
			# Note: Cat-related state is tracked separately
			result["message"] += " -5 doom! The cat has arrived!"

		"supply_automation":
			# Passive effect: auto-orders supplies when below 30
			result["message"] += " Supplies will auto-order when low!"

	return result

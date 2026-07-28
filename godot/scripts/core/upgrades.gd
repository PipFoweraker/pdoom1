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
			# 970: "less likely to lose staff on low funds" was unbacked -- no low-funds
			# staff-attrition system exists to hook into. Inventing one is a design call
			# (Pip's), not a silent reinterpretation onto an unrelated system. Re-priced
			# to 0 and relabelled as flavor-only pending that call.
			"id": "comfy_chairs",
			"name": "Buy Comfy Office Chairs",
			"description": "Nicer office chairs. Flavor only for now -- no mechanical effect (#970).",
			"cost": 0,
			"effect_key": "comfy_chairs",
			"category": "office"
		},
		{
			"id": "secure_cloud",
			"name": "Secure Cloud Provider",
			"description": "Dampens player-frontier growth from capability breakthroughs",
			"cost": 160000,
			"effect_key": "secure_cloud",
			"category": "infrastructure"
		},
		{
			# 970: "cash flow tracking" and "prevents board oversight" were both unbacked --
			# board_seat ledger riders are explicitly inert-by-design (ledger.gd: "consequences
			# are owned by other lanes... L5's boundary forbids doom conversion here"), so
			# there is nothing real to prevent yet. Re-priced to 0 and relabelled pending a
			# real governance/board-oversight mechanic (Pip's design call).
			"id": "accounting_software",
			"name": "Accounting Software",
			"description": "Basic bookkeeping tooling. Flavor only for now -- no mechanical effect (#970).",
			"cost": 0,
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
			# #970: wired -- GameActions.execute_action("capability_research", ...) reads
			# has_upgrade("upgrade_computer") and adds the flat research bonus.
			result["message"] += " Research actions now more effective!"

		"comfy_chairs":
			# #970: STOP SELLING -- no low-funds staff-attrition system exists to back
			# "less likely to lose staff on low funds". Re-priced to 0 (see get_all_upgrades);
			# flavor-only, no gameplay claim.
			result["message"] += " Chairs installed. Purely cosmetic for now."

		"secure_cloud":
			# #970: wired -- DoomSystem._advance_intermediaries reads has_upgrade("secure_cloud")
			# and dampens player-frontier growth from capabilities researchers.
			result["message"] += " Research breakthroughs less risky!"

		"accounting_software":
			# #970: STOP SELLING -- "cash flow tracking" / "prevents board oversight" had no
			# backing system (board_seat riders are explicitly inert-by-design). Re-priced to
			# 0 (see get_all_upgrades); flavor-only, no gameplay claim.
			result["message"] += " Software installed. Purely cosmetic for now."

		"hpc_cluster":
			state.add_resources({"compute": 20})
			# #970: wired -- GameActions.execute_action("capability_research", ...) reads
			# has_upgrade("hpc_cluster") and applies the +25% research multiplier.
			result["message"] += " +20 compute, research 25% more effective!"

		"research_automation":
			# #970: wired -- GameActions.execute_action("capability_research", ...) reads
			# has_upgrade("research_automation") and adds a compute-scaled research bonus.
			result["message"] += " Research scales with compute!"

		"cat_adoption":
			# ADR-0015: the cat's morale boost raises global_alarm (a happier, more careful org),
			# not a printed doom write.
			state.global_alarm += Balance.num("doom.streams.upgrade_cat_alarm", 5.0)
			# Note: Cat-related state is tracked separately
			result["message"] += " The cat has arrived!"

		"supply_automation":
			# Passive effect: auto-orders supplies when below 30
			result["message"] += " Supplies will auto-order when low!"

	return result

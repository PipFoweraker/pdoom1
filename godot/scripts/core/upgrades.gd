extends Node
class_name GameUpgrades
## Upgrade definitions and management

static func get_all_upgrades() -> Array[Dictionary]:
	"""Return all available upgrades"""
	return [
		{
			"id": "upgrade_computers",
			"name": "Upgrade Computer System",
			"description": "Boosts research effectiveness (+1 research per action)",
			"cost": 200,
			"purchased": false,
			"effect_key": "better_computers"
		},
		{
			"id": "comfy_chairs",
			"name": "Buy Comfy Office Chairs",
			"description": "Staff morale up (less likely to lose staff on low funds)",
			"cost": 120,
			"purchased": false,
			"effect_key": "comfy_chairs"
		},
		{
			"id": "secure_cloud",
			"name": "Secure Cloud Provider",
			"description": "Reduces doom spikes from lab breakthroughs",
			"cost": 160,
			"purchased": false,
			"effect_key": "secure_cloud"
		},
		{
			"id": "accounting_software",
			"name": "Accounting Software",
			"description": "Enables cash flow tracking, prevents board oversight",
			"cost": 500,
			"purchased": false,
			"effect_key": "accounting_software"
		},
		{
			"id": "compact_activity_display",
			"name": "Compact Activity Display",
			"description": "Minimize activity log to save screen space",
			"cost": 150,
			"purchased": false,
			"effect_key": "compact_activity_display"
		},
		{
			"id": "hpc_cluster",
			"name": "High-Performance Computing Cluster",
			"description": "Advanced compute infrastructure (+20 compute, research effectiveness +25%)",
			"cost": 800,
			"purchased": false,
			"effect_key": "hpc_cluster"
		},
		{
			"id": "research_automation",
			"name": "Research Automation Suite",
			"description": "AI-assisted research tools (research actions more effective with compute)",
			"cost": 600,
			"purchased": false,
			"effect_key": "research_automation"
		}
	]

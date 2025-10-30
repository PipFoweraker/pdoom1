extends Node
class_name GameState
## Core game state - all resources and game status

# Resources
var money: float = 100000.0
var compute: float = 100.0
var research: float = 0.0  # Generated from compute
var papers: float = 0.0
var reputation: float = 50.0
var doom: float = 50.0  # 0-100, lose at 100
var action_points: int = 3

# Staff
var safety_researchers: int = 0
var capability_researchers: int = 0
var compute_engineers: int = 0

# Game status
var turn: int = 0
var game_over: bool = false
var victory: bool = false
var seed: String = ""

# Queued actions for this turn
var queued_actions: Array[String] = []

func _init(game_seed: String = ""):
	seed = game_seed if game_seed != "" else str(Time.get_ticks_msec())
	reset()

func reset():
	"""Reset to starting state"""
	money = 100000.0
	compute = 100.0
	research = 0.0
	papers = 0.0
	reputation = 50.0
	doom = 50.0
	action_points = 3

	safety_researchers = 0
	capability_researchers = 0
	compute_engineers = 0

	turn = 0
	game_over = false
	victory = false
	queued_actions.clear()

func can_afford(costs: Dictionary) -> bool:
	"""Check if player can afford given costs"""
	if costs.has("money") and money < costs["money"]:
		return false
	if costs.has("compute") and compute < costs["compute"]:
		return false
	if costs.has("research") and research < costs["research"]:
		return false
	if costs.has("papers") and papers < costs["papers"]:
		return false
	if costs.has("action_points") and action_points < costs["action_points"]:
		return false
	return true

func spend_resources(costs: Dictionary):
	"""Spend resources (assumes can_afford was checked)"""
	if costs.has("money"):
		money -= costs["money"]
	if costs.has("compute"):
		compute -= costs["compute"]
	if costs.has("research"):
		research -= costs["research"]
	if costs.has("papers"):
		papers -= costs["papers"]
	if costs.has("action_points"):
		action_points -= costs["action_points"]

func add_resources(gains: Dictionary):
	"""Add resources"""
	if gains.has("money"):
		money += gains["money"]
	if gains.has("compute"):
		compute += gains["compute"]
	if gains.has("research"):
		research += gains["research"]
	if gains.has("papers"):
		papers += gains["papers"]
	if gains.has("reputation"):
		reputation += gains["reputation"]
	if gains.has("doom"):
		doom += gains["doom"]
		doom = clamp(doom, 0.0, 100.0)

func check_win_lose():
	"""Check victory/defeat conditions"""
	if doom >= 100.0:
		game_over = true
		victory = false
	elif reputation <= 0.0:
		game_over = true
		victory = false
	elif doom <= 0.0:
		game_over = true
		victory = true

func get_total_staff() -> int:
	return safety_researchers + capability_researchers + compute_engineers

func to_dict() -> Dictionary:
	"""Serialize state for UI"""
	return {
		"money": money,
		"compute": compute,
		"research": research,
		"papers": papers,
		"reputation": reputation,
		"doom": doom,
		"action_points": action_points,
		"safety_researchers": safety_researchers,
		"capability_researchers": capability_researchers,
		"compute_engineers": compute_engineers,
		"total_staff": get_total_staff(),
		"turn": turn,
		"game_over": game_over,
		"victory": victory
	}

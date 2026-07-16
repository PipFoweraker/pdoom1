extends Control
## Standalone demo/harness for the OfficeFloor component (Pip: open this to SEE it).
## Spawns a mock roster covering every FSM state and lets you toggle Tier 0/1 and
## reshuffle. Uses ONLY mock plain-data dicts — no GameState, proving OfficeFloor
## is a pure view that needs nothing but a snapshot.

const OfficeFloorScene := preload("res://scenes/ui/office_floor/office_floor.tscn")

var _floor: OfficeFloor
var _status: Label

# Mock roster: each entry exercises a different mechanical -> sprite state.
var _roster: Array = [
	{"id": 0, "name": "Sage",   "specialization": "safety",           "burnout": 10.0, "loyalty": 70, "assigned": true,  "unmanaged": false}, # working
	{"id": 1, "name": "Riley",  "specialization": "capabilities",     "burnout": 20.0, "loyalty": 60, "assigned": true,  "unmanaged": true},  # walking/drift
	{"id": 2, "name": "Quinn",  "specialization": "interpretability", "burnout": 92.0, "loyalty": 55, "assigned": true,  "unmanaged": false}, # stressed
	{"id": 3, "name": "Morgan", "specialization": "alignment",        "burnout": 15.0, "loyalty": 8,  "assigned": true,  "unmanaged": false}, # idle (disengaged)
	{"id": 4, "name": "Parker", "specialization": "safety",           "burnout": 5.0,  "loyalty": 80, "assigned": true,  "unmanaged": false}, # working
	{"id": 5, "name": "Lane",   "specialization": "capabilities",     "burnout": 40.0, "loyalty": 45, "assigned": true,  "unmanaged": true},  # walking/drift
]

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var root := VBoxContainer.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)

	var bar := HBoxContainer.new()
	root.add_child(bar)

	var tier_btn := Button.new()
	tier_btn.text = "Toggle Tier (0/1)"
	tier_btn.pressed.connect(_on_toggle_tier)
	bar.add_child(tier_btn)

	var stress_btn := Button.new()
	stress_btn.text = "Stress a random hire"
	stress_btn.pressed.connect(_on_stress_random)
	bar.add_child(stress_btn)

	var calm_btn := Button.new()
	calm_btn.text = "Calm everyone"
	calm_btn.pressed.connect(_on_calm_all)
	bar.add_child(calm_btn)

	_status = Label.new()
	bar.add_child(_status)

	_floor = OfficeFloorScene.instantiate()
	_floor.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_floor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(_floor)

	_floor.set_tier(0)
	_push_roster()

func _push_roster() -> void:
	_floor.set_roster(_roster)
	_update_status()

func _update_status() -> void:
	var counts := {}
	for st in EmployeeFSM.map_roster(_roster):
		counts[st] = counts.get(st, 0) + 1
	_status.text = "  Tier %d  |  %d staff  |  %s" % [_floor.tier, _roster.size(), str(counts)]

func _on_toggle_tier() -> void:
	_floor.set_tier(1 if _floor.tier == 0 else 0)
	_update_status()

func _on_stress_random() -> void:
	var i := randi() % _roster.size()
	_roster[i]["burnout"] = 95.0
	_push_roster()

func _on_calm_all() -> void:
	for e in _roster:
		e["burnout"] = 10.0
	_push_roster()

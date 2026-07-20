extends Control
## Diagnostic STUB for the minimal-leaderboard build (v0.11.0 leaderboard-crash
## isolation). Attached to leaderboard_screen_minimal.tscn. Deliberately dependency-free:
## no preloads, no autoload calls, no @onready node derefs -- so a crash while LOADING
## the minimal scene can only be the scene STRUCTURE / sub-resources / the scene-change
## machinery itself, NOT the real leaderboard_screen.gd content. See
## docs/LEADERBOARD_CRASH_DIAGNOSIS.md for how this is used.

func _ready() -> void:
	printerr("[LBMIN-TRACE] minimal leaderboard stub _ready ENTERED")

func _on_back_button_pressed() -> void:
	printerr("[LBMIN-TRACE] back pressed")
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

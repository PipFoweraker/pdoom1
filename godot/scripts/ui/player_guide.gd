extends Control
## Player Guide - Tutorial and help information

func _ready():
	print("[PlayerGuide] Guide displayed")

func _on_back_pressed():
	"""Return to welcome screen"""
	print("[PlayerGuide] Returning to welcome screen")
	SceneTransition.go_to("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()

extends CanvasLayer
## Global Scene Transition System
## Provides fade in/out transitions between scenes

# Transition state
var is_transitioning: bool = false

# Transition settings
var fade_duration: float = 0.3  # seconds
var fade_color: Color = Color.BLACK

# UI nodes
var fade_rect: ColorRect

func _ready():
	print("[SceneTransition] Initializing global scene transitions...")

	# Create fade rectangle
	fade_rect = ColorRect.new()
	fade_rect.color = fade_color
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

	# Make it cover the whole screen
	fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade_rect.grow_horizontal = Control.GROW_DIRECTION_BOTH
	fade_rect.grow_vertical = Control.GROW_DIRECTION_BOTH

	# Start invisible
	fade_rect.modulate.a = 0.0

	add_child(fade_rect)

	print("[SceneTransition] Ready")

func change_scene(target_scene: String):
	"""Transition to a new scene with fade effect"""
	if is_transitioning:
		print("[SceneTransition] Already transitioning, ignoring request")
		return

	is_transitioning = true
	print("[SceneTransition] Transitioning to: ", target_scene)

	# Block input during transition
	fade_rect.mouse_filter = Control.MOUSE_FILTER_STOP

	# Fade out
	await fade_out()

	# Change scene
	get_tree().change_scene_to_file(target_scene)

	# Fade in
	await fade_in()

	# Re-enable input
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	is_transitioning = false

	print("[SceneTransition] Transition complete")

func fade_out() -> void:
	"""Fade to black"""
	var tween = create_tween()
	tween.tween_property(fade_rect, "modulate:a", 1.0, fade_duration)
	await tween.finished

func fade_in() -> void:
	"""Fade from black"""
	var tween = create_tween()
	tween.tween_property(fade_rect, "modulate:a", 0.0, fade_duration)
	await tween.finished

func quick_fade() -> void:
	"""Quick fade effect (for UI feedback)"""
	var tween = create_tween()
	tween.tween_property(fade_rect, "modulate:a", 0.3, 0.1)
	tween.tween_property(fade_rect, "modulate:a", 0.0, 0.1)
	await tween.finished

func set_fade_color(color: Color):
	"""Change the fade color"""
	fade_color = color
	fade_rect.color = color

func set_fade_duration(duration: float):
	"""Change fade duration"""
	fade_duration = duration

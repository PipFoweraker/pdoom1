extends CanvasLayer
## Global scene navigation -- THE single chokepoint for changing scenes.
##
## CONTRACT (enforced by tools/check_scene_nav.py, run in pre-commit + CI):
## ALL navigation goes through SceneTransition.go_to() / .reload(). No other script may
## call get_tree().change_scene_to_file() / change_scene_to_packed() / reload_current_scene()
## directly. This file is the ONLY sanctioned caller.
##
## WHY THIS IS MANDATORY (v0.11.0 release-blocker -- docs/LEADERBOARD_CRASH_DIAGNOSIS.md):
## calling change_scene_to_file() synchronously from inside an _input()/_gui_input() handler
## segfaulted the RELEASE build (0xc0000005, faulting module = the engine binary, BEFORE the
## new scene's _ready). change_scene_to_file() synchronously loads + instantiates the target
## scene; doing that mid input-dispatch drove the optimized engine into a deterministic
## native deref. game-over -> leaderboard (keyboard ENTER, from _input) detonated; the same
## nav from a Button `pressed` signal (mouse) was fine. The pattern was latent in ~5 more
## screens (config_confirmation, settings_menu, leaderboard_screen, welcome_screen, ...).
##
## go_to()/reload() ALWAYS call_deferred the actual swap onto a clean idle frame, so the
## unsafe "load a scene from inside input dispatch" case is structurally impossible no matter
## where a caller invokes them. That is the whole point: safety is a property of the router,
## not of every call site remembering to defer.

# Re-entrancy: one navigation at a time. A second request while one is in flight is dropped.
var is_transitioning: bool = false

# Fade settings (fade is OPT-IN per call; default navigation is instant + behavior-preserving).
var fade_duration: float = 0.3
var fade_color: Color = Color.BLACK
var fade_rect: ColorRect

# Pending-navigation state, read by the deferred _run_transition().
var _pending_target: String = ""
var _pending_reload: bool = false
var _pending_fade: bool = false


func _ready() -> void:
	print("[SceneTransition] Initializing global scene navigation...")
	fade_rect = ColorRect.new()
	fade_rect.color = fade_color
	fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade_rect.grow_horizontal = Control.GROW_DIRECTION_BOTH
	fade_rect.grow_vertical = Control.GROW_DIRECTION_BOTH
	fade_rect.modulate.a = 0.0
	add_child(fade_rect)
	print("[SceneTransition] Ready -- route all navigation through go_to()/reload()")


## Navigate to a scene file. SAFE FROM ANY CONTEXT (input handlers, signals, _process):
## the actual scene swap is always deferred to a clean idle frame. Pass use_fade=true for a
## fade-to-color transition; default is instant.
func go_to(target_scene: String, use_fade: bool = false) -> void:
	if is_transitioning:
		push_warning("[SceneTransition] navigation already in progress; ignoring go_to(%s)" % target_scene)
		return
	if not ResourceLoader.exists(target_scene):
		push_error("[SceneTransition] scene not found, navigation aborted: %s" % target_scene)
		return
	is_transitioning = true
	_pending_target = target_scene
	_pending_reload = false
	_pending_fade = use_fade
	print("[SceneTransition] go_to(%s) queued (fade=%s)" % [target_scene, use_fade])
	call_deferred("_run_transition")


## Reload the current scene. SAFE FROM ANY CONTEXT (deferred, same as go_to).
func reload(use_fade: bool = false) -> void:
	if is_transitioning:
		push_warning("[SceneTransition] navigation already in progress; ignoring reload()")
		return
	is_transitioning = true
	_pending_target = ""
	_pending_reload = true
	_pending_fade = use_fade
	print("[SceneTransition] reload() queued (fade=%s)" % use_fade)
	call_deferred("_run_transition")


## Back-compat alias for the pre-v0.11.0 API. Prefer go_to().
func change_scene(target_scene: String) -> void:
	go_to(target_scene, true)


func _run_transition() -> void:
	# Runs on a clean idle frame (out of any input/signal callstack).
	if _pending_fade:
		fade_rect.mouse_filter = Control.MOUSE_FILTER_STOP
		await fade_out()

	if _pending_reload:
		get_tree().reload_current_scene()
	else:
		get_tree().change_scene_to_file(_pending_target)

	if _pending_fade:
		await fade_in()
		fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

	_pending_target = ""
	_pending_reload = false
	_pending_fade = false
	is_transitioning = false


func fade_out() -> void:
	var tween := create_tween()
	tween.tween_property(fade_rect, "modulate:a", 1.0, fade_duration)
	await tween.finished


func fade_in() -> void:
	var tween := create_tween()
	tween.tween_property(fade_rect, "modulate:a", 0.0, fade_duration)
	await tween.finished


func quick_fade() -> void:
	"""Quick fade blip (UI feedback, not a scene change)."""
	var tween := create_tween()
	tween.tween_property(fade_rect, "modulate:a", 0.3, 0.1)
	tween.tween_property(fade_rect, "modulate:a", 0.0, 0.1)
	await tween.finished


func set_fade_color(color: Color) -> void:
	fade_color = color
	fade_rect.color = color


func set_fade_duration(duration: float) -> void:
	fade_duration = duration

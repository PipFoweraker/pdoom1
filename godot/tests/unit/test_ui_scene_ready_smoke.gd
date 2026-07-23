extends GutTest
## UI-scene _ready smoke test (anti-hollow uplift, ADR-0017).
##
## WHY THIS EXISTS: the v0.11.0-alpha release-blocker was a segfault while LOADING
## the leaderboard scene on the game-over -> leaderboard transition. The existing
## test_smoke_load_all.gd instantiate()s every scene but NEVER enters the SceneTree,
## so _ready() never runs -- it cannot see a fault that happens at add-to-tree time.
## This test closes that specific gap: it INSTANTIATES + ADDS-TO-TREE + runs _ready()
## on every standalone UI screen and every scene under scenes/ui/**, asserting the
## process survives (no crash) and the node is still valid after a frame.
##
## WHAT IT CATCHES: a null-deref / bad @onready path / autoload-contract break / any
## GDScript fault that fires in _ready() and takes the process down. A hard native
## crash kills the whole run -> the runner reports missing results -> RED (exactly the
## signal we want for the leaderboard fault, IF it reproduces headlessly).
##
## RENDER-GATE LIMITATION (read before trusting a green here): headless Godot uses a
## dummy rendering/audio driver. It does NOT GPU-decode textures, allocate real VRAM,
## or run the platform's release-mode renderer. A crash that only manifests in a
## release EXPORT with a real GPU (the class the v0.11.0 leaderboard segfault is
## suspected to be) will NOT reproduce here. This test is a necessary gate, not a
## sufficient one: the human release-build playtest (play -> lose -> leaderboard on a
## real machine) remains the final ship gate. See docs/LEADERBOARD_CRASH_DIAGNOSIS.md.

# Every scene under these roots is swept recursively.
const SCENE_DIR_ROOTS := ["res://scenes/ui"]

# Standalone top-level screens (navigation targets) added explicitly. main.tscn is
# deliberately EXCLUDED: adding it to the tree boots the entire game (timers, audio,
# turn manager) with side effects unsuitable for a smoke test; the existing
# test_smoke_load_all.gd::test_main_scene_chain_instantiates covers its load path.
const EXPLICIT_SCENES := [
	"res://scenes/welcome.tscn",
	"res://scenes/leaderboard_screen.tscn",
	"res://scenes/pregame_setup.tscn",
	"res://scenes/settings_menu.tscn",
	"res://scenes/pause_menu.tscn",
	"res://scenes/keybind_screen.tscn",
	"res://scenes/player_guide.tscn",
	"res://scenes/config_confirmation.tscn",
]

# Scenes whose _ready() self-navigates or hard-requires an in-progress game such that
# adding them cold would disrupt the run. Each entry MUST carry a justification -- an
# empty/undocumented skip is how a test goes hollow. (Empty today; kept as the
# documented escape hatch so a future problem scene is skipped visibly, not silently.)
const SKIP := {}

# Floor so the sweep cannot pass vacuously if the tree is moved/renamed.
const MIN_SCENES := 12


func _collect(root: String, ext: String) -> Array:
	var out: Array = []
	var dir := DirAccess.open(root)
	if dir == null:
		return out
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		if name == "." or name == "..":
			name = dir.get_next()
			continue
		var path := root + "/" + name
		if dir.current_is_dir():
			out.append_array(_collect(path, ext))
		elif name.ends_with(ext):
			out.append(path)
		name = dir.get_next()
	dir.list_dir_end()
	return out


func _all_scenes() -> Array:
	var scenes: Array = []
	for root in SCENE_DIR_ROOTS:
		scenes.append_array(_collect(root, ".tscn"))
	for s in EXPLICIT_SCENES:
		if not scenes.has(s):
			scenes.append(s)
	scenes.sort()
	return scenes


func test_ui_scenes_ready_without_crash():
	var scenes := _all_scenes()
	assert_gte(scenes.size(), MIN_SCENES,
		"sweep found only %d UI scenes (< floor %d) -- the walk may be hollow" % [scenes.size(), MIN_SCENES])

	var processed := 0
	var failed: Array = []
	for path in scenes:
		if SKIP.has(path):
			gut.p("  SKIP (%s): %s" % [SKIP[path], path])
			continue

		var packed = load(path)
		if packed == null or not (packed is PackedScene) or not packed.can_instantiate():
			failed.append("%s (load/can_instantiate failed)" % path)
			continue

		var inst = packed.instantiate()
		if inst == null:
			failed.append("%s (instantiate returned null)" % path)
			continue

		# add_child fires _ready(). If _ready() hard-crashes the engine, the whole
		# process dies here and the runner reports missing results (RED) -- which is
		# the intended detection for the leaderboard-class fault.
		add_child(inst)
		# Two frames: let _ready() run and one idle tick settle (deferred calls, first
		# layout pass) before we tear the node down.
		await get_tree().process_frame
		await get_tree().process_frame

		# Reaching here proves no hard crash. is_instance_valid guards the rare scene
		# that legitimately frees itself in _ready (would be a false-negative to assert
		# against); we only require that we survived and can clean up.
		if is_instance_valid(inst):
			remove_child(inst)
			inst.free()
		processed += 1

	if not failed.is_empty():
		for f in failed:
			gut.p("  FAILED: %s" % f)
	assert_eq(failed.size(), 0,
		"%d UI scene(s) failed to instantiate/enter-tree (see list above)" % failed.size())
	assert_gte(processed, MIN_SCENES,
		"only %d UI scenes ran _ready (< floor %d)" % [processed, MIN_SCENES])
	gut.p("ui-ready smoke: %d UI scenes entered the tree and ran _ready cleanly" % processed)

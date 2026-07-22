extends GutTest
## "Nothing is hollow at load time" smoke test (test-strategy uplift).
##
## THE guard against the parse-error class that broke the game today
## (feat/hiring-phase-b-pipeline commit a2de3a7): a one-line GDScript parse error
## in main_ui.gd made the ENTIRE script fail to load, so the game would not start
## -- yet 436 unit tests passed, because unit tests exercise core/GameManager logic
## and NEVER load the UI script. A test that passes without exercising the thing it
## claims to protect is hollow.
##
## This test closes that gap directly: it LOADS every project .gd script and
## INSTANTIATES every scene, asserting no parse/load error. A broken script that no
## other test touches now names itself and turns the fast gate RED.
##
## Mechanism: ResourceLoader.load() returns null (and prints a Parse Error) for a
## script that fails to compile; a scene whose attached script fails to compile
## cannot instantiate. Loading scripts is cheap (already imported); instantiate()
## builds the node tree WITHOUT entering the SceneTree, so _ready() side effects do
## not fire -- fast and free of the running-game's timers/audio.
##
## Kept in tests/unit (the fast gate) on purpose: this is the cheapest, highest-
## leverage check in the suite and must gate every scoped change.

# Trees to sweep for scripts. Third-party (addons) and the tests themselves are
# excluded: GUT already loads every test_*.gd (a broken one is caught by the
# runner's manifest check), and addons are not ours to police.
const SCRIPT_ROOTS := ["res://scripts", "res://autoload"]
const SCENE_ROOTS := ["res://scenes"]

# Floors so the directory walk itself cannot go hollow: if a refactor moves the
# source tree and the walker silently finds nothing, these fail LOUDLY rather than
# reporting a vacuous green (the exact failure mode -- "passed while testing
# nothing" -- this whole file exists to kill).
const MIN_SCRIPTS := 80
const MIN_SCENES := 15

# Autoloads declared in project.godot [autoload]. If the boot chain were broken the
# engine would not have started GUT at all, but asserting each singleton is present
# documents the contract and catches a singleton renamed out from under a caller.
const EXPECTED_AUTOLOADS := [
	"ErrorHandler", "GameConfig", "Balance", "SceneTransition", "ThemeManager",
	"NotificationManager", "KeybindManager", "ScreenshotManager", "LogExporter",
	"IconLoader", "MusicManager", "VerificationTracker", "EventService",
	"GameManager", "Achievements",
]


func _collect(root: String, ext: String) -> Array:
	## Recursive list of res:// paths under `root` ending in `ext`.
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


func test_all_scripts_compile():
	# Load every project .gd. A parse error -> load() returns null -> this names the
	# file and fails. This is the direct counterfactual for today's main_ui.gd bug.
	var scripts: Array = []
	for root in SCRIPT_ROOTS:
		scripts.append_array(_collect(root, ".gd"))
	scripts.sort()

	assert_gte(scripts.size(), MIN_SCRIPTS,
		"walker found only %d scripts (< floor %d) -- the sweep itself may be hollow" % [scripts.size(), MIN_SCRIPTS])

	var broken: Array = []
	for path in scripts:
		var res = load(path)
		if res == null:
			broken.append(path)
	if not broken.is_empty():
		for p in broken:
			gut.p("  FAILED TO LOAD: %s" % p)
	assert_eq(broken.size(), 0,
		"%d project script(s) failed to compile/load (see list above)" % broken.size())
	gut.p("smoke: %d scripts compiled cleanly" % scripts.size())


func test_all_scenes_instantiate():
	# Instantiate every scene. Catches a broken attached script AND a structurally
	# broken .tscn. instantiate() does NOT enter the SceneTree, so _ready() side
	# effects stay dormant.
	var scenes: Array = []
	for root in SCENE_ROOTS:
		scenes.append_array(_collect(root, ".tscn"))
	scenes.sort()

	assert_gte(scenes.size(), MIN_SCENES,
		"walker found only %d scenes (< floor %d) -- the sweep itself may be hollow" % [scenes.size(), MIN_SCENES])

	var broken: Array = []
	for path in scenes:
		var packed = load(path)
		if packed == null or not (packed is PackedScene) or not packed.can_instantiate():
			broken.append(path + " (load/can_instantiate failed)")
			continue
		var inst = packed.instantiate()
		if inst == null:
			broken.append(path + " (instantiate returned null)")
			continue
		inst.free()
	if not broken.is_empty():
		for p in broken:
			gut.p("  FAILED TO INSTANTIATE: %s" % p)
	assert_eq(broken.size(), 0,
		"%d scene(s) failed to instantiate (see list above)" % broken.size())
	gut.p("smoke: %d scenes instantiated cleanly" % scenes.size())


func test_wired_backdrop_textures_resolve():
	# #756: main.tscn gained an office backdrop and leaderboard_screen.tscn gained a
	# records-room ground. Instantiating the scene proves the .tscn is structurally
	# sound; this additionally asserts the Texture2D ext_resources actually RESOLVED
	# to a real imported texture (a missing/renamed asset would load as null and read
	# as an invisible-but-passing scene). NOTE: headless loads the .ctex header but
	# does NOT fully decode pixels -- this cannot catch the #728-class render-decode
	# crash. A real (non-headless) launch remains the true validation.
	var cases := [
		["res://scenes/main.tscn", "Backdrop", "office_wide_day"],
		["res://scenes/leaderboard_screen.tscn", "Background", "records_microfiche"],
	]
	for case in cases:
		var scene_path: String = case[0]
		var node_name: String = case[1]
		var expect_stem: String = case[2]
		var packed = load(scene_path)
		assert_not_null(packed, "%s must load" % scene_path)
		if packed == null:
			continue
		var inst = packed.instantiate()
		assert_not_null(inst, "%s must instantiate" % scene_path)
		if inst == null:
			continue
		var bg = inst.get_node_or_null(node_name)
		assert_not_null(bg, "%s must have a '%s' backdrop node" % [scene_path, node_name])
		if bg != null:
			assert_true(bg is TextureRect, "%s/%s must be a TextureRect" % [scene_path, node_name])
			var tex = bg.texture
			assert_not_null(tex, "%s/%s texture ext_resource must resolve (asset present + imported)" % [scene_path, node_name])
			if tex != null and tex.resource_path != "":
				assert_true(tex.resource_path.contains(expect_stem),
					"%s/%s texture should be %s, got %s" % [scene_path, node_name, expect_stem, tex.resource_path])
		inst.free()
	gut.p("smoke: wired backdrop textures resolved (main + leaderboard)")


func test_autoload_singletons_present():
	# The boot chain (project.godot [autoload]) must be intact. A missing singleton
	# means an autoload script failed to load or was renamed away from its callers.
	var missing: Array = []
	for name in EXPECTED_AUTOLOADS:
		if get_node_or_null("/root/" + name) == null:
			missing.append(name)
	if not missing.is_empty():
		gut.p("  MISSING AUTOLOADS: %s" % str(missing))
	assert_eq(missing.size(), 0,
		"%d declared autoload singleton(s) missing at /root (boot chain broken)" % missing.size())


func test_main_scene_chain_instantiates():
	# The specific counterfactual for today's failure: main.tscn attaches
	# scripts/ui/main_ui.gd. If main_ui.gd has a parse error, main.tscn cannot
	# instantiate. This asserts the exact chain the game boots into.
	var packed = load("res://scenes/main.tscn")
	assert_not_null(packed, "main.tscn must load")
	assert_true(packed is PackedScene and packed.can_instantiate(),
		"main.tscn must be instantiable (attached scripts must compile)")
	var inst = packed.instantiate()
	assert_not_null(inst, "main.tscn must instantiate (main_ui.gd et al. must compile)")
	if inst != null:
		inst.free()

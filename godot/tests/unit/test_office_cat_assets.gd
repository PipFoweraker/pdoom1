extends GutTest
## Guards the office cat against issue #796, where every cat in the SHIPPED build
## rendered as the engine's magenta/black missing-texture checkerboard while the
## artwork sat correctly imported in the pack the whole time.
##
## The mechanism, because it decides what these tests can and cannot prove:
## Godot's exporter does NOT put the source .jpg into the .pck. It ships the
## imported texture (.godot/imported/<name>.jpg-<md5>.ctex) plus the .import file
## that points at it. FileAccess reads the packed file table literally and answers
## "no such file" for res://assets/cats/simple/web-arwen.jpg; ResourceLoader goes
## through the import system and resolves the .ctex. office_cat.gd guarded its
## load() with FileAccess.file_exists(), so the guard failed for all eight cats in
## every exported build and the placeholder path ran every single time.
##
## HONEST LIMITATION -- READ BEFORE TRUSTING A GREEN RUN.
## These tests run against the SOURCE TREE, where the .jpg files are on disk and
## FileAccess.file_exists() therefore returns true. They CANNOT reproduce the
## export-only failure, and they cannot prove a texture reaches a screen. Only a
## human looking at a cat in an exported build proves that. What they do buy:
## (1) the eight referenced assets exist and decode, and (2) the guard in
## office_cat.gd does not regress to FileAccess, which is the actual defect and is
## invisible to any behavioural test run from the editor.

const OFFICE_CAT_SCRIPT_PATH := "res://scripts/ui/office_cat.gd"

# Eight cats shipped in v0.13.2. Floored so a refactor that empties CAT_NAMES
# cannot pass this file vacuously.
const MIN_CATS := 8


func _cat_names() -> Dictionary:
	var script: GDScript = load(OFFICE_CAT_SCRIPT_PATH)
	assert_not_null(script, "could not load " + OFFICE_CAT_SCRIPT_PATH)
	var consts: Dictionary = script.get_script_constant_map()
	assert_true(consts.has("CAT_NAMES"), "office_cat.gd no longer defines CAT_NAMES")
	return consts.get("CAT_NAMES", {})


func _cat_path_prefix() -> String:
	var script: GDScript = load(OFFICE_CAT_SCRIPT_PATH)
	var consts: Dictionary = script.get_script_constant_map()
	return str(consts.get("CAT_IMAGES_PATH", ""))


func test_cat_roster_is_not_empty():
	var names := _cat_names()
	assert_true(
		names.size() >= MIN_CATS,
		"expected at least %d office cats, found %d" % [MIN_CATS, names.size()]
	)


func test_every_cat_resolves_through_resource_loader():
	# ResourceLoader.exists() is the check that is TRUE in both the editor and an
	# exported build. If this fails, the asset is genuinely gone or was renamed.
	var prefix := _cat_path_prefix()
	assert_ne(prefix, "", "office_cat.gd no longer defines CAT_IMAGES_PATH")
	for file_name in _cat_names().keys():
		var path: String = prefix + str(file_name)
		assert_true(
			ResourceLoader.exists(path),
			"cat asset does not resolve through the import system: " + path
		)


func test_every_cat_loads_as_a_texture():
	var prefix := _cat_path_prefix()
	for file_name in _cat_names().keys():
		var path: String = prefix + str(file_name)
		var tex := load(path) as Texture2D
		assert_not_null(tex, "cat asset did not load as Texture2D: " + path)
		if tex != null:
			assert_true(
				tex.get_width() > 0 and tex.get_height() > 0,
				"cat texture decoded to a zero-sized image: " + path
			)


func test_guard_does_not_regress_to_file_access():
	# The #796 defect is invisible from the editor, so this asserts on the SOURCE.
	# Same spirit as the check_scene_nav / no-emoji source gates: the failure mode
	# only exists in a shipped artifact, so the source is where it must be caught.
	var f := FileAccess.open(OFFICE_CAT_SCRIPT_PATH, FileAccess.READ)
	assert_not_null(f, "could not read " + OFFICE_CAT_SCRIPT_PATH)
	if f == null:
		return
	var src := f.get_as_text()
	f.close()

	assert_false(
		src.contains("FileAccess.file_exists(image_path)"),
		"office_cat.gd guards its texture load with FileAccess.file_exists(), which is"
		+ " ALWAYS FALSE in an exported build for an imported asset -- this is the exact"
		+ " regression that shipped the magenta checkerboard in #796. Use"
		+ " ResourceLoader.exists() instead."
	)
	assert_true(
		src.contains("ResourceLoader.exists(image_path)"),
		"office_cat.gd should gate its texture load on ResourceLoader.exists(image_path)"
	)


func test_placeholder_is_a_real_texture_not_the_engine_checkerboard():
	# Defence in depth: even when a cat IS missing, the fallback must be a real
	# ImageTexture. PlaceholderTexture2D is not a real texture and the renderer
	# substitutes its missing-texture fill -- the magenta/black checkerboard the
	# player actually saw.
	var script: GDScript = load(OFFICE_CAT_SCRIPT_PATH)
	assert_not_null(script, "could not load " + OFFICE_CAT_SCRIPT_PATH)
	var f := FileAccess.open(OFFICE_CAT_SCRIPT_PATH, FileAccess.READ)
	if f == null:
		return
	var src := f.get_as_text()
	f.close()
	assert_false(
		src.contains("PlaceholderTexture2D.new()"),
		"office_cat.gd fallback uses PlaceholderTexture2D, which renders as the engine's"
		+ " missing-texture checkerboard. Build a muted ImageTexture instead (#796)."
	)

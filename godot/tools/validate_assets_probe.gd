extends SceneTree
## Asset-import validation probe (run headless via tools/validate_assets.py).
##
## PURPOSE: catch a bad-asset landmine BEFORE it ships -- a corrupt/undecodable texture
## or resource that imports "successfully" but fails to load, which is exactly the kind
## of silent time-bomb that could crash a release build. It walks res://assets, LOADS
## every importable resource, and asserts each one resolves to a non-null resource of a
## sane type. A failure names the file and sets a non-zero exit code.
##
## HEADLESS-SAFE CHECKS ONLY: textures are validated by metadata (get_width/get_height
## > 0), NOT by get_image() -- VRAM-compressed textures legitimately discard their CPU
## image under the headless dummy renderer, so a get_image() check would false-fail. So
## this proves the resource is STRUCTURALLY loadable; it does NOT GPU-decode. That last
## mile is the human release-build playtest (see docs/LEADERBOARD_CRASH_DIAGNOSIS.md).

const ASSET_ROOT := "res://assets"

# Extensions we treat as loadable Godot resources. (.import sidecars and .uid are meta.)
const LOADABLE_EXT := [
	"png", "jpg", "jpeg", "webp", "svg", "bmp", "tga",   # textures
	"ogg", "wav", "mp3",                                  # audio
	"ttf", "otf", "woff", "woff2",                        # fonts
	"tres", "res",                                        # packed resources
]

# Floor so a moved/emptied asset tree fails LOUDLY instead of passing vacuously.
const MIN_ASSETS := 200


func _collect(root: String) -> Array:
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
			out.append_array(_collect(path))
		else:
			var ext := name.get_extension().to_lower()
			if LOADABLE_EXT.has(ext):
				out.append(path)
		name = dir.get_next()
	dir.list_dir_end()
	return out


func _init():
	print("[validate_assets] walking %s ..." % ASSET_ROOT)
	var assets := _collect(ASSET_ROOT)
	assets.sort()
	print("[validate_assets] found %d loadable asset files" % assets.size())

	var failures: Array = []
	var checked := 0
	for path in assets:
		var res = ResourceLoader.load(path)
		if res == null:
			failures.append("%s (ResourceLoader.load returned null -- corrupt or failed import)" % path)
			continue
		if res is Texture2D:
			var tex := res as Texture2D
			if tex.get_width() <= 0 or tex.get_height() <= 0:
				failures.append("%s (Texture2D has non-positive size %dx%d)" % [path, tex.get_width(), tex.get_height()])
				continue
		checked += 1

	print("[validate_assets] checked=%d  failed=%d" % [checked, failures.size()])
	for f in failures:
		printerr("[validate_assets][FAIL] %s" % f)

	if assets.size() < MIN_ASSETS:
		printerr("[validate_assets][FATAL] found only %d assets (< floor %d) -- the walk itself may be hollow" % [assets.size(), MIN_ASSETS])
		quit(2)
		return
	if not failures.is_empty():
		printerr("[validate_assets][FATAL] %d asset(s) failed to load -- DO NOT SHIP" % failures.size())
		quit(1)
		return
	print("[validate_assets][PASS] all %d assets loaded structurally cleanly" % checked)
	quit(0)

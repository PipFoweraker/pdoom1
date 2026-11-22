extends Node
## Skin capture harness (spike/ui-skins, 2026-11-22). Boots the real game screen once per
## UI skin and saves a PNG of each, so skins can be compared side by side without anyone
## clicking through Settings. Dev tooling: lives under godot/tools/, which every export
## preset excludes (tools/*), so it never ships.
##
## Needs a real window (headless renders no frames). Run from the repo root, with APPDATA
## isolated (CLAUDE.md -- bare Godot runs write to the real player profile):
##   APPDATA="$LOCALAPPDATA/Temp/claude/godot-iso-skins" \
##     <godot> --path godot --windowed --resolution 1920x1080 res://tools/skin_capture.tscn \
##     -- --out=<abs dir> [--skins=default,terminal_f,...] [--settle=4]
##
## Driver lives on the root Window (not the current scene) so SceneTransition swapping
## main.tscn in and out does not free it mid-run.

var _out_dir := ""
var _skins: Array = []
var _settle := 4.0


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			_out_dir = arg.trim_prefix("--out=")
		elif arg.begins_with("--skins="):
			_skins = Array(arg.trim_prefix("--skins=").split(","))
		elif arg.begins_with("--settle="):
			_settle = float(arg.trim_prefix("--settle="))
	if _out_dir == "":
		push_error("[SkinCapture] pass -- --out=<dir>")
		get_tree().quit(2)
		return
	if _skins.is_empty():
		_skins = ["default"] + ThemeManager.skins.keys()
	DirAccess.make_dir_recursive_absolute(_out_dir)
	_reparent_to_root.call_deferred()


func _reparent_to_root() -> void:
	var root := get_tree().root
	get_parent().remove_child(self)
	root.add_child(self)
	get_tree().current_scene = null
	_run()


func _run() -> void:
	var written := 0
	for skin in _skins:
		if not ThemeManager.themes.has(skin):
			push_error("[SkinCapture] unknown skin %s" % skin)
			continue
		ThemeManager.apply_theme(skin)
		SceneTransition.go_to("res://scenes/main.tscn")
		await get_tree().create_timer(_settle, true).timeout  # process_always: the capture must tick even if a modal paused the tree
		await RenderingServer.frame_post_draw
		var img := get_tree().root.get_texture().get_image()
		var path := _out_dir.path_join("skin_%s.png" % skin)
		var err := img.save_png(path)
		print("[SkinCapture] %s -> %s (err %d, %dx%d)" % [skin, path, err, img.get_width(), img.get_height()])
		if err == OK:
			written += 1
	ThemeManager.apply_theme("default")
	print("[SkinCapture] done: %d/%d written" % [written, _skins.size()])
	get_tree().quit(0 if written == _skins.size() else 1)

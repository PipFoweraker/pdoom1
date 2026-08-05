extends Node
## Compile-coverage walker for the GDScript syntax gate (issue #1082).
##
## Run via:
##   godot --headless --path godot res://tools/syntax_walk.tscn
##
## Why a SCENE and not --script/--check-only: booting a scene boots the
## project NORMALLY -- autoloads are initialised and the class_name cache is
## live -- so load()ing any script here cannot false-positive with
## "Identifier not found: <autoload>" the way per-file --check-only does
## (186/260 files "failed" that way; see issue #1082). And unlike the old
## bare `--quit` boot, load()ing EVERY .gd forces the engine to parse files
## that no autoload or scene reaches.
##
## Division of labour: this node only enumerates, load()s, and prints a
## completion manifest. A parse-broken script makes Godot emit
## "SCRIPT ERROR: Parse Error: ..." / "Failed to load script ..." on stderr;
## scripts/run_godot_tests.py check_syntax() greps for those AND requires the
## SYNTAX_WALK_COMPLETE marker with a file count matching its own disk glob.
## The pass/fail decision lives entirely in Python, outside GUT -- GUT counts
## unexpected engine errors as test failures, which is exactly why a
## GUT-hosted version of this walk cannot work (issue #1082, approach 3).

## Top-level directories we do not gate (third-party code).
const SKIP_TOP_DIRS: Array[String] = ["addons"]


func _ready() -> void:
	var scripts: Array[String] = []
	_collect("res://", scripts)
	scripts.sort()
	for path in scripts:
		# load(), not preload(), so a broken target cannot break THIS
		# script's own compile. Result intentionally unused: load() returns
		# non-null even for a parse-broken script (proven on #1082), so the
		# error signal is the engine's stderr output, not the return value.
		var _res := load(path)
	# Machine-readable completion manifest. If this scene fails to run at
	# all the marker never prints and the gate fails CLOSED (#640: proof of
	# run required, silence is failure).
	print("SYNTAX_WALK_COMPLETE files=%d" % scripts.size())
	get_tree().quit(0)


func _collect(dir_path: String, out: Array[String]) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		push_error("syntax_walk: cannot open directory %s" % dir_path)
		return
	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		if not entry.begins_with("."):
			var full := dir_path.path_join(entry)
			if dir.current_is_dir():
				var skip := dir_path == "res://" and entry in SKIP_TOP_DIRS
				if not skip:
					_collect(full, out)
			elif entry.ends_with(".gd"):
				out.append(full)
		entry = dir.get_next()
	dir.list_dir_end()

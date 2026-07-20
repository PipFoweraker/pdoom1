extends GutTest
## No-UI-dead-ends escape-contract test (fix/ui-no-dead-ends, ADR-0017 red-first).
##
## THE failure class this guards: a panel opens with NO working way out -- no close/
## back control, and Esc does nothing -- trapping the player (the reported Liability
## Ledger bug). A per-button hand-written list would rot; instead this test
## AUTO-DISCOVERS openable overlay panels and asserts each has a WORKING EXIT.
##
## Discovery (no hardcoded per-panel list -- future panels are covered automatically):
##   1. Scene panels: every res://scenes/ui/**/*.tscn whose basename ends in the
##      overlay-convention suffixes "_panel" or "_modal".
##   2. Procedural panels: every res://scripts/ui/*.gd that exposes a build_screen()
##      builder (the Liability Ledger is built this way, not from a .tscn).
## Both sources grow automatically as the UI grows, provided the naming/build
## conventions in docs/game-design/UI_ESCAPE_CONTRACT.md are followed.
##
## Working exit (the contract, EITHER is sufficient):
##   - an _input/_unhandled_input/_shortcut_input handler that closes the panel on
##     ui_cancel (Esc), OR
##   - a discoverable close/back Button whose press hides/frees the panel (or emits a
##     zero-arg close/closed/cancel/dismiss signal for a parent to act on).
## Verified FUNCTIONALLY: the panel is instanced in the live tree, shown, then a real
## ui_cancel InputEvent is dispatched (and, failing that, its close button pressed);
## the panel must end up freed / hidden / signalled-closed. A panel that survives both
## with no exit is a dead-end and fails the test, naming itself.
##
## Red-first proof (ADR-0017): run against the UNFIXED Liability Ledger, this file goes
## RED naming ledger_screen.gd -- build_screen() returned a bare Panel with no intrinsic
## exit. See the PR body for the captured red output.

const SCENE_UI_ROOT := "res://scenes/ui"
const SCRIPT_UI_ROOT := "res://scripts/ui"
const OVERLAY_SUFFIXES := ["_panel", "_modal"]  # summonable-overlay naming convention

# Floor so the discovery walk cannot silently go hollow (ADR-0017 "silence is failure").
const MIN_PANELS := 3

const CLOSE_TEXT_KEYWORDS := [
	"close", "back", "cancel", "dismiss", "done", "return", "exit", "ok",
	"continue", "✕", "✖", "x",
]
const CLOSE_SIGNAL_KEYWORDS := ["close", "cancel", "dismiss", "back", "done", "exit"]

var _bg: Control  # a stand-in "game" background the panels open on top of


func before_each() -> void:
	_bg = Control.new()
	_bg.name = "DeadEndTestBackground"
	_bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	get_tree().root.add_child(_bg)


func after_each() -> void:
	if is_instance_valid(_bg):
		_bg.queue_free()
	_bg = null


# --- Discovery -----------------------------------------------------------------

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


func _discover_scene_panels() -> Array:
	var panels: Array = []
	for path in _collect(SCENE_UI_ROOT, ".tscn"):
		var base := String(path).get_file().get_basename()  # e.g. "bug_report_panel"
		for suffix in OVERLAY_SUFFIXES:
			if base.ends_with(suffix):
				panels.append({"name": base, "path": path, "kind": "scene"})
				break
	return panels


func _discover_procedural_panels() -> Array:
	var panels: Array = []
	for path in _collect(SCRIPT_UI_ROOT, ".gd"):
		var script = load(path)
		if script == null or not (script is GDScript):
			continue
		for m in script.get_script_method_list():
			if String(m.get("name", "")) == "build_screen":
				panels.append({"name": path.get_file().get_basename(), "path": path, "kind": "proc"})
				break
	return panels


func _discover_all_panels() -> Array:
	var all: Array = _discover_scene_panels()
	all.append_array(_discover_procedural_panels())
	all.sort_custom(func(a, b): return String(a.name) < String(b.name))
	return all


# --- Building an instance we can drive -----------------------------------------

func _build_panel_node(spec: Dictionary):
	## Returns [node, cleanup_extra] or null. cleanup_extra is a builder object that
	## must be freed after the node (procedural builders are Nodes we instanced).
	if spec.kind == "scene":
		var packed = load(spec.path)
		if packed == null or not (packed is PackedScene) or not packed.can_instantiate():
			return null
		return [packed.instantiate(), null]
	# procedural: instance the builder, call build_screen(null, size) -> Control panel.
	var script = load(spec.path)
	if script == null:
		return null
	var builder = script.new()
	if builder == null or not builder.has_method("build_screen"):
		if builder is Node:
			builder.free()
		return null
	var panel = builder.build_screen(null, Vector2(1152, 648))
	return [panel, builder]


func _activate(node) -> void:
	## Show the panel the way it is actually opened, so lazily-built content exists.
	if node.has_method("show_panel"):
		node.show_panel()
	elif node.has_method("present"):
		node.present("Escape-contract self-test", "This panel must be escapable.")
	if node is CanvasItem and not node.visible:
		node.visible = true


# --- Exit detection ------------------------------------------------------------

func _gather_buttons(node: Node, out: Array) -> void:
	for child in node.get_children():
		if child is Button:
			out.append(child)
		_gather_buttons(child, out)


func _find_close_button(node: Node) -> Button:
	var buttons: Array = []
	_gather_buttons(node, buttons)
	# Prefer a semantically-named close/back/cancel button.
	for b in buttons:
		var t := String(b.text).strip_edges().to_lower()
		for kw in CLOSE_TEXT_KEYWORDS:
			if t == kw or (kw.length() > 1 and t.contains(kw)):
				return b
	# Otherwise the first button that is actually wired to something.
	for b in buttons:
		if b.pressed.get_connections().size() > 0:
			return b
	return null


func _watch_close_signals(node: Node, flag: Array) -> void:
	for s in node.get_signal_list():
		if int(s.get("args", []).size()) != 0:
			continue  # only zero-arg signals can take our zero-arg sink safely
		var n := String(s.name).to_lower()
		for kw in CLOSE_SIGNAL_KEYWORDS:
			if n.contains(kw):
				node.connect(s.name, func(): flag[0] = true)
				break


func _send_ui_cancel() -> void:
	var ev := InputEventKey.new()
	ev.keycode = KEY_ESCAPE
	ev.physical_keycode = KEY_ESCAPE
	ev.pressed = true
	get_viewport().push_input(ev)


func _settle() -> void:
	await get_tree().process_frame
	await get_tree().process_frame


func _is_gone_or_hidden(node) -> bool:
	if not is_instance_valid(node):
		return true
	if node is CanvasItem:
		return not node.visible
	if node is CanvasLayer:
		return not node.visible
	return false


func _has_working_exit(node) -> bool:
	var closed := [false]
	_watch_close_signals(node, closed)

	# 1) The contract's preferred path: ui_cancel (Esc) closes it.
	_send_ui_cancel()
	await _settle()
	if _is_gone_or_hidden(node) or closed[0]:
		return true

	# 2) Fallback: a discoverable close/back button that hides/frees/signals.
	if is_instance_valid(node):
		var btn := _find_close_button(node)
		if btn != null and is_instance_valid(btn):
			btn.pressed.emit()
			await _settle()
			if _is_gone_or_hidden(node) or closed[0]:
				return true
	return false


# --- Tests ---------------------------------------------------------------------

func test_discovery_is_not_hollow():
	# If the walk finds (almost) nothing, a refactor moved the tree and this whole
	# file would pass vacuously -- fail LOUDLY instead (ADR-0017 MIN floor).
	var panels := _discover_all_panels()
	var names := panels.map(func(p): return p.name)
	gut.p("discovered %d openable panels: %s" % [panels.size(), str(names)])
	assert_gte(panels.size(), MIN_PANELS,
		"discovery found only %d panels (< floor %d) -- the walk may be hollow" % [panels.size(), MIN_PANELS])


func test_no_ui_dead_ends():
	var panels := _discover_all_panels()
	assert_gte(panels.size(), MIN_PANELS, "no panels discovered -- discovery is hollow")

	var dead_ends: Array = []
	for spec in panels:
		var built = _build_panel_node(spec)
		if built == null:
			dead_ends.append("%s (could not instance/build -- %s)" % [spec.name, spec.path])
			continue
		var node = built[0]
		var builder = built[1]
		if node == null or not (node is Node):
			dead_ends.append("%s (build_screen/instantiate returned non-Node)" % spec.name)
			if builder is Node and is_instance_valid(builder):
				builder.free()
			continue

		_bg.add_child(node)
		await _settle()  # let _ready() run
		_activate(node)
		await _settle()

		var ok: bool = await _has_working_exit(node)
		if not ok:
			dead_ends.append("%s [%s] -- opens with NO working exit (no ui_cancel handler, no close/back button that hides/frees it)" % [spec.name, spec.kind])
			gut.p("  DEAD-END: %s (%s)" % [spec.name, spec.path])
		else:
			gut.p("  ok: %s (%s)" % [spec.name, spec.kind])

		if is_instance_valid(node):
			node.queue_free()
		if builder is Node and is_instance_valid(builder):
			builder.free()
		await _settle()

	assert_eq(dead_ends.size(), 0,
		"%d UI panel(s) are dead-ends (no working exit): %s" % [dead_ends.size(), str(dead_ends)])

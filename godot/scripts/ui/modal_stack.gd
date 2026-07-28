class_name ModalStack
extends RefCounted
## Issue #877: THE single LIFO chokepoint that owns modal/overlay lifetime.
##
## WHY: before this, four independent systems wrote MainUI.active_dialog BY HAND --
## the submenu/ledger/hiring/travel builders (free-first idiom), EventDialog
## (_on_event_dialog_opened), EmployeePanel (_on_employee_dialog_opened) and the
## standalone BugReportPanel (which never registered at all). A single slot kept in
## sync by N hand-written call sites is a dual source of truth: the scene tree says
## one thing, `active_dialog` says another. Every symptom in #877/#883/#886 is one
## instance of that desync -- orphaned panels still visible at z=1000 with a live
## input barrier but untracked, so no key path could close them (soft-lock).
##
## THE RULE: nothing sets `active_dialog` directly any more. Call sites `present()`
## here; this class owns:
##   * the LIFO list (`_entries`, last == topmost),
##   * strict top-first teardown (a newcomer pops the whole stack before taking the
##     slot -- these modals are exclusive by design, none of them compose visually),
##   * priority refusal: an event dialog is PRIORITY_MUST_ANSWER (#452 -- events must
##     be answered, not dismissed), so a lower-priority modal opening over one is
##     REFUSED rather than allowed to orphan it,
##   * self-healing bookkeeping: every entry is pinned to its node's `tree_exited`
##     (and, for hide-mode entries, `visibility_changed`), so however a panel dies --
##     its own [X] lambda, a cancel button's `queue_free()`, a replacing dialog, the
##     scene going away -- the stack pops it and re-syncs the host. That is what makes
##     an orphan structurally impossible rather than merely unlikely.
##
## BARRIERS: this class deliberately does NOT own input barriers. Each mount point
## ties its barrier to `dialog.tree_exited` (main_ui._present_modal_dialog,
## event_dialog._show_next_event, employee_panel.show_staff_id_card), so freeing the
## node always frees its barrier. Owning them here would just add a second slot to
## keep in sync -- the exact bug class this exists to kill.

enum CloseMode {
	FREE,   ## the node is built per-open and is queue_free()d on close (every dialog)
	HIDE,   ## the node is a persistent scene member; close means hide (BugReportPanel)
}

## A modal at this priority cannot be preempted by a lower one; the lower open is
## refused outright. Event dialogs use it (#452: an event must be answered).
const PRIORITY_MUST_ANSWER := 10
const PRIORITY_NORMAL := 0

var host   # MainUI node (untyped: avoids a class_name coupling cycle, as with SubmenuController)

var _entries: Array = []   # LIFO: _entries[-1] is the topmost modal


func _init(host_ref) -> void:
	host = host_ref


# --- queries -----------------------------------------------------------------------

func depth() -> int:
	_prune()
	return _entries.size()


func is_empty() -> bool:
	return depth() == 0


func top_node() -> Control:
	_prune()
	if _entries.is_empty():
		return null
	return _entries[-1]["node"]


func top_kind() -> String:
	_prune()
	if _entries.is_empty():
		return ""
	return String(_entries[-1]["kind"])


func can_present(priority: int = PRIORITY_NORMAL) -> bool:
	"""False when the topmost modal outranks the newcomer (an event dialog blocks
	everything below PRIORITY_MUST_ANSWER). Call sites check this BEFORE building a
	panel where that is cheaper than building-then-discarding."""
	_prune()
	if _entries.is_empty():
		return true
	return priority >= int(_entries[-1]["priority"])


# --- the chokepoint ----------------------------------------------------------------

func present(node: Control, buttons: Array = [], opts: Dictionary = {}) -> bool:
	"""Push `node` as the topmost modal. Returns false (and changes nothing) if a
	higher-priority modal holds the top. Re-entrant: presenting the current top again
	only refreshes its key routing, so a double-fire of an `opened` signal is a no-op."""
	if node == null or not is_instance_valid(node):
		return false
	var priority := int(opts.get("priority", PRIORITY_NORMAL))

	_prune()
	if not _entries.is_empty() and _entries[-1]["node"] == node:
		_entries[-1]["buttons"] = buttons
		sync()
		return true

	if not can_present(priority):
		# Refused: re-assert the truth in case a call site optimistically wrote
		# host.active_dialog before mounting.
		sync()
		return false

	_pop_all(node)

	_entries.append({
		"node": node,
		"buttons": buttons,
		"priority": priority,
		"close_mode": int(opts.get("close_mode", CloseMode.FREE)),
		"kind": String(opts.get("kind", "")),
	})
	var gone_cb := _on_node_gone.bind(node)
	if not node.tree_exited.is_connected(gone_cb):
		node.tree_exited.connect(gone_cb, CONNECT_ONE_SHOT)
	if int(opts.get("close_mode", CloseMode.FREE)) == CloseMode.HIDE:
		var vis_cb := _on_node_visibility_changed.bind(node)
		if not node.visibility_changed.is_connected(vis_cb):
			node.visibility_changed.connect(vis_cb)
	sync()
	return true


func dismiss_top() -> bool:
	"""Close STRICTLY the topmost modal (the LIFO half of #877). Never touches a
	buried one, so a close key can never reach past what the player is looking at."""
	_prune()
	if _entries.is_empty():
		sync()
		return false
	var entry: Dictionary = _entries.pop_back()
	_close_entry(entry)
	sync()
	return true


func dismiss_all() -> void:
	"""Tear the whole stack down top-first (scene exit / hard reset paths)."""
	_pop_all(null)
	sync()


func dismiss(node: Control) -> bool:
	"""Close a specific registered modal wherever it sits in the stack."""
	_prune()
	for i in range(_entries.size() - 1, -1, -1):
		if _entries[i]["node"] == node:
			var entry: Dictionary = _entries[i]
			_entries.remove_at(i)
			_close_entry(entry)
			sync()
			return true
	return false


func handle_escape() -> bool:
	"""ESC closes the TOPMOST modal only. Returns true when ESC was consumed --
	including the refusal case (an event dialog swallows ESC per #452 rather than
	letting it fall through to the pause menu behind the still-visible dialog)."""
	_prune()
	if _entries.is_empty():
		return false
	if int(_entries[-1]["priority"]) >= PRIORITY_MUST_ANSWER:
		return true
	dismiss_top()
	return true


# --- bookkeeping -------------------------------------------------------------------

func sync() -> void:
	"""Push the stack's truth into the host's key-routing slots. These stay public on
	MainUI because _input/_unhandled_input read them, but this is now their ONLY writer."""
	_prune()
	if host == null or not is_instance_valid(host):
		return
	if _entries.is_empty():
		host.active_dialog = null
		host.active_dialog_buttons = []
	else:
		host.active_dialog = _entries[-1]["node"]
		host.active_dialog_buttons = _entries[-1]["buttons"]


func _prune() -> void:
	"""Drop entries whose node died or is dying. `is_queued_for_deletion` counts: a
	queue_free()d panel is already gone as far as the player is concerned, and leaving
	it in `active_dialog` is exactly the 'tracked slot points at a dying node' failure."""
	for i in range(_entries.size() - 1, -1, -1):
		var n = _entries[i]["node"]
		if n == null or not is_instance_valid(n) or n.is_queued_for_deletion():
			_entries.remove_at(i)


func _pop_all(exclude: Control) -> void:
	while not _entries.is_empty():
		var entry: Dictionary = _entries.pop_back()
		if entry["node"] == exclude:
			continue
		_close_entry(entry)


func _close_entry(entry: Dictionary) -> void:
	var n = entry["node"]
	if n == null or not is_instance_valid(n):
		return
	if int(entry["close_mode"]) == CloseMode.HIDE:
		if n.has_method("hide_panel"):
			n.hide_panel()
		else:
			n.visible = false
	elif not n.is_queued_for_deletion():
		n.queue_free()


func _forget(node: Control) -> void:
	for i in range(_entries.size() - 1, -1, -1):
		if _entries[i]["node"] == node:
			_entries.remove_at(i)


func _on_node_gone(node: Control) -> void:
	"""A registered modal left the tree by ANY path. This is the self-healing edge:
	the stack never needs the closer to tell it what happened."""
	_forget(node)
	sync()


func _on_node_visibility_changed(node: Control) -> void:
	if node != null and is_instance_valid(node) and not node.visible:
		_forget(node)
		sync()

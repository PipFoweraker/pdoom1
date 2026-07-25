extends GutTest
## Adversarial modal/overlay lifecycle invariants + seeded fuzz (SIMULATION tier).
##
## WHY THIS EXISTS: modal state in MainUI is a DUAL source of truth -- a single
## `active_dialog` slot (main_ui.gd) that must stay in sync with the scene tree
## (what is actually visible), kept in sync BY HAND in N separate open/close
## handlers. The suite before this file was unit-deterministic and never drove
## hostile INPUT SEQUENCES against live UI state, so a cross-handler desync
## (open dialog A, then B fires mid-flight) was invisible to it. Exemplar bug:
## `_on_event_dialog_opened` overwrote `active_dialog` without freeing the prior
## occupant, so an event firing while the ledger was open ORPHANED the ledger --
## visible at z=1000 with a live input barrier, but untracked, so Esc/L/N could
## not close it (issue #877 / PR #883).
##
## THE INVARIANTS this file drives adversarially (checked after every hostile step):
##   I1 tracked-slot validity: active_dialog is null OR a valid, in-tree, visible node.
##   I2 no orphan modal panel: every VISIBLE top-layer modal panel (z >= 999 under
##      the scene root or the viewport root) IS the tracked active_dialog.
##   I3 no orphan input barrier: no full-rect MOUSE_FILTER_STOP overlay survives
##      without a tracked dialog to own it (a surviving barrier == mouse soft-lock).
##   I4 at most ONE live barrier after the tree settles (two barriers == a leak).
##   I5 button routing integrity: every valid button in active_dialog_buttons lives
##      INSIDE the tracked dialog (stale buttons route keys into a freed panel).
##   I6 event-presenter consistency: is_showing_event <=> an event panel is visible;
##      a non-empty event queue with is_showing_event false is a stuck presenter.
##   I7 closability: after driving the host close paths, no modal panel or barrier
##      remains visible (nothing is ever visible-but-unclosable).
##
## DETERMINISM: the monkey fuzz uses a fixed literal seed (MONKEY_SEED) -- no
## Date/Time randomness anywhere. Every failure prints the executed op trace, so
## a repro is: same seed, same op list, same tier. Game-content randomness does
## not influence the checks: synthetic events carry one FREE option (always
## resolvable) and no assertion reads balance/affordability data.
##
## TIER NOTE: this is a destructive/fuzz suite -- it boots the full main.tscn.
## It lives in tests/unit/simulation (NON-BLOCKING) on purpose: it must never
## flake the fast gate, and it is EXPECTED RED until the #877/#883 class of
## fixes lands. Red here means "the modal layer still desyncs", not "bad test".
##
## Suspect code (file:line at time of writing):
##   * main_ui.gd:1787  _on_event_dialog_opened -- overwrites active_dialog, no free.
##   * event_dialog.gd:95-102 -- click_blocker parented to viewport root, freed ONLY
##     by report_choice_result(success); NOT tied to the dialog via tree_exited.
##   * employee_panel.gd:193-207 -- staff-card blocker freed only by its own click /
##     close_requested lambdas; both lambdas capture the panel and die once it frees.

const MONKEY_SEED := 727272          # fixed literal -- change ONLY deliberately
const MONKEY_STEPS := 140            # hostile ops per fuzz run
const SETTLE_FRAMES := 2             # frames to let queue_free()s land

const MAIN_SCENE := "res://scenes/main.tscn"

# Dialog kinds the drivers can open. "event" and "employee_card" are the two
# signal-driven adopters (the suspect class); the rest use the free-first idiom.
const SUBMENU_KINDS := [
	"ledger", "doom_trend",
	"fundraise", "publicity", "strategic", "operations", "financing",
	"hire_staff", "travel",
]

var _main: Node = null               # instantiated main.tscn root (tab_manager)
var _ui: Node = null                 # the MainUI VBoxContainer child
var _root_children_before: Array = []
var _saved_historical_events: Array = []
var _event_serial := 0

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

func before_all():
	if EventService:
		_saved_historical_events = EventService.transformed_events.duplicate()

func after_all():
	if EventService:
		EventService.transformed_events = _saved_historical_events

func before_each():
	# Historical-event dataset off: boot must not race a data-driven popup.
	if EventService:
		EventService.transformed_events.clear()
	GameConfig.pending_load_path = ""
	_snapshot_root_children()

	var packed: PackedScene = load(MAIN_SCENE)
	_main = packed.instantiate()
	add_child_autofree(_main)
	# _ready awaits one frame then _boot_game -> start_new_game; give it room.
	for i in range(6):
		await get_tree().process_frame

	_ui = _find_main_ui(_main)
	assert_not_null(_ui, "main.tscn must contain the MainUI node (script main_ui.gd)")
	# Boot may have presented a turn-1 event; start every test from a clean slate.
	await _nuke_all_overlays()

func after_each():
	get_tree().paused = false
	if _ui != null and is_instance_valid(_ui):
		await _nuke_all_overlays()
	# EventDialog parents panels/blockers to the VIEWPORT ROOT -- they would outlive
	# the autofreed main.tscn instance and leak into the next test. Sweep any child
	# of root that appeared during this test.
	for child in get_tree().root.get_children():
		if not _root_children_before.has(child) and child != _main and is_instance_valid(child):
			if child is Control:
				child.queue_free()
	for i in range(SETTLE_FRAMES):
		await get_tree().process_frame
	_ui = null
	_main = null

# ---------------------------------------------------------------------------
# Harness helpers
# ---------------------------------------------------------------------------

func _snapshot_root_children() -> void:
	_root_children_before = []
	for child in get_tree().root.get_children():
		_root_children_before.append(child)

func _find_main_ui(root: Node) -> Node:
	if root.get_script() != null and String(root.get_script().resource_path).ends_with("main_ui.gd"):
		return root
	for child in root.get_children():
		var hit := _find_main_ui(child)
		if hit != null:
			return hit
	return null

func _pump(frames: int = SETTLE_FRAMES) -> void:
	for i in range(frames):
		await get_tree().process_frame

func _mk_event(tag: String) -> Dictionary:
	_event_serial += 1
	return {
		"id": "adv_ui_evt_%s_%d" % [tag, _event_serial],
		"name": "Adversarial UI test event (%s)" % tag,
		"description": "Synthetic event injected by test_adversarial_ui_state.",
		"options": [
			{"id": "ok", "text": "Acknowledge", "costs": {}, "effects": {}, "message": "ok"},
		],
	}

func _present_event(tag: String) -> Dictionary:
	var evt := _mk_event(tag)
	_ui.event_dialog.present(evt)
	await _pump()
	return evt

func _resolve_active_event() -> void:
	"""Resolve the currently shown event via its first (free) button -- the same
	pressed-signal path the mouse/keyboard routing uses."""
	if _ui.active_dialog == null or not is_instance_valid(_ui.active_dialog):
		return
	if not _ui.active_dialog.has_meta("is_event_dialog"):
		return
	# TurnManager.resolve_event requires TURN_START phase (FIX #418 contract).
	if GameManager.state != null:
		GameManager.state.current_phase = GameState.TurnPhase.TURN_START
	var buttons: Array = _ui.active_dialog_buttons
	if buttons.size() > 0 and is_instance_valid(buttons[0]):
		buttons[0].pressed.emit()
	await _pump()

func _open(kind: String) -> void:
	match kind:
		"ledger":
			_ui._show_ledger_screen()
		"doom_trend":
			_ui._show_doom_trend_expanded()
		"fundraise", "publicity", "strategic", "operations", "financing", "hire_staff", "travel":
			_ui.submenu_controller.open(kind)
		"employee_card":
			_ui.employee_panel.show_staff_id_card({
				"specialization": "safety", "name": "Test Subject",
				"skill_level": 5, "current_salary": 60000,
				"base_productivity": 1.0, "burnout": 0.0, "loyalty": 50,
				"turns_employed": 1, "jet_lag_turns": 0, "jet_lag_severity": 0.0,
			})
		"event":
			await _present_event("open")
			return
		_:
			fail_test("unknown open kind: %s" % kind)
	await _pump()

func _close_tracked() -> void:
	"""Drive the host's own close path for whatever is tracked."""
	if _ui.active_dialog != null and is_instance_valid(_ui.active_dialog) \
			and _ui.active_dialog.has_meta("is_event_dialog"):
		await _resolve_active_event()
	else:
		_ui._close_active_submenu()
		await _pump()

# --- overlay census ---------------------------------------------------------

func _overlay_parents() -> Array:
	# The two mount points every modal in this codebase uses: the scene root
	# (tab_manager -- submenus, ledger, staff card) and the viewport root
	# (event dialog + its blocker, fanfare).
	var parents: Array = []
	if _ui != null and is_instance_valid(_ui) and _ui.tab_manager != null:
		parents.append(_ui.tab_manager)
	parents.append(get_tree().root)
	return parents

func _visible_modal_panels() -> Array:
	var found: Array = []
	for parent in _overlay_parents():
		for child in parent.get_children():
			if child is Panel and is_instance_valid(child) and child.visible \
					and not child.is_queued_for_deletion() and child.z_index >= 999:
				found.append(child)
	return found

func _live_stop_barriers() -> Array:
	var found: Array = []
	for parent in _overlay_parents():
		for child in parent.get_children():
			if child is ColorRect and is_instance_valid(child) and child.visible \
					and not child.is_queued_for_deletion() \
					and child.mouse_filter == Control.MOUSE_FILTER_STOP:
				found.append(child)
	return found

func _nuke_all_overlays() -> void:
	"""Force the UI back to a clean state regardless of how desynced it got.
	This is harness-only surgery -- production code has no equivalent, which is
	exactly why an orphan is a soft-lock for a player."""
	for p in _visible_modal_panels():
		p.queue_free()
	for b in _live_stop_barriers():
		b.queue_free()
	_ui.active_dialog = null
	_ui.active_dialog_buttons = []
	if _ui.event_dialog != null and is_instance_valid(_ui.event_dialog):
		_ui.event_dialog.event_queue.clear()
		_ui.event_dialog.is_showing_event = false
		_ui.event_dialog._pending_dialog = null
		_ui.event_dialog._pending_blocker = null
		_ui.event_dialog._reason_label = null
	await _pump()

# --- the invariant oracle ----------------------------------------------------

func _check_invariants(context: String) -> Array:
	"""Returns a list of violation strings (empty == all invariants hold)."""
	var v: Array = []
	var ad = _ui.active_dialog

	# I1 tracked-slot validity
	if ad != null:
		if not is_instance_valid(ad) or ad.is_queued_for_deletion():
			v.append("%s | I1: active_dialog points at a freed/dying node" % context)
			ad = null
		elif not ad.is_inside_tree():
			v.append("%s | I1: active_dialog valid but NOT in the scene tree" % context)
		elif not ad.visible:
			v.append("%s | I1: active_dialog in tree but NOT visible" % context)

	# I2 no orphan modal panel
	var panels := _visible_modal_panels()
	for p in panels:
		if p != ad:
			v.append("%s | I2: ORPHAN modal panel '%s' (z=%d, parent=%s) visible but untracked -- the #883 class" \
				% [context, p.name, p.z_index, p.get_parent().name])

	# I3 no orphan barrier / I4 at most one barrier
	var barriers := _live_stop_barriers()
	if ad == null and barriers.size() > 0:
		v.append("%s | I3: %d input barrier(s) live with NO tracked dialog -- mouse soft-lock" \
			% [context, barriers.size()])
	if barriers.size() > 1:
		v.append("%s | I4: %d simultaneous input barriers (leak -- expected at most 1)" \
			% [context, barriers.size()])

	# I5 button routing integrity
	for btn in _ui.active_dialog_buttons:
		if btn != null and is_instance_valid(btn) and not btn.is_queued_for_deletion():
			if ad == null:
				v.append("%s | I5: live routed button '%s' with NO tracked dialog" % [context, btn.text])
			elif not ad.is_ancestor_of(btn):
				v.append("%s | I5: routed button '%s' lives OUTSIDE the tracked dialog" % [context, btn.text])

	# I6 event-presenter consistency
	var ed = _ui.event_dialog
	if ed != null and is_instance_valid(ed):
		var event_panel_visible := false
		for p in panels:
			if p.has_meta("is_event_dialog"):
				event_panel_visible = true
		if ed.is_showing_event and not event_panel_visible:
			v.append("%s | I6: presenter thinks an event is showing but NO event panel is visible (stuck -- future events will queue forever)" % context)
		if not ed.is_showing_event and ed.event_queue.size() > 0:
			v.append("%s | I6: %d queued event(s) with presenter idle (stuck queue)" % [context, ed.event_queue.size()])

	return v

func _assert_no_violations(violations: Array, headline: String) -> void:
	for msg in violations:
		gut.p("  VIOLATION: %s" % msg)
	assert_eq(violations.size(), 0,
		"%s -- %d invariant violation(s), see VIOLATION lines above" % [headline, violations.size()])

func _assert_closable(context: String, violations: Array) -> void:
	"""I7: after driving host close paths (bounded), nothing modal may remain."""
	for i in range(6):
		if _ui.active_dialog == null and _visible_modal_panels().is_empty():
			break
		await _close_tracked()
	if not _visible_modal_panels().is_empty() or not _live_stop_barriers().is_empty():
		violations.append("%s | I7: overlays remain after exhausting host close paths (%d panel(s), %d barrier(s)) -- visible-but-unclosable" \
			% [context, _visible_modal_panels().size(), _live_stop_barriers().size()])

# ---------------------------------------------------------------------------
# 1. Baseline: every dialog kind opens and closes cleanly on its own
# ---------------------------------------------------------------------------

func test_every_dialog_kind_opens_and_closes_clean():
	var violations: Array = []
	var kinds: Array = SUBMENU_KINDS.duplicate()
	kinds.append("employee_card")
	kinds.append("event")
	for kind in kinds:
		await _open(kind)
		violations.append_array(_check_invariants("open(%s)" % kind))
		await _assert_closable("close(%s)" % kind, violations)
		violations.append_array(_check_invariants("after close(%s)" % kind))
		await _nuke_all_overlays()
	_assert_no_violations(violations, "single open/close cycle per dialog kind")

# ---------------------------------------------------------------------------
# 2. THE EXEMPLAR: an event fires while another dialog is open
# ---------------------------------------------------------------------------

func test_event_firing_over_each_open_dialog_kind():
	# The #883 bug class straight on: open X, then event_triggered fires.
	# EXPECTED (invariant): X is freed before the event panel takes the slot.
	# CURRENT main: _on_event_dialog_opened does not free -> X orphans on screen.
	var violations: Array = []
	for kind in ["ledger", "doom_trend", "fundraise", "financing", "employee_card"]:
		await _open(kind)
		await _present_event(String(kind))
		violations.append_array(_check_invariants("event over %s" % kind))
		await _resolve_active_event()
		violations.append_array(_check_invariants("event resolved over %s" % kind))
		await _assert_closable("drain after event over %s" % kind, violations)
		await _nuke_all_overlays()
	_assert_no_violations(violations, "event dialog opening over an already-open dialog")

func test_orphaned_ledger_amplifies_on_reopen():
	# Player-visible amplification of the exemplar: once the ledger is orphaned,
	# active_dialog is null after the event resolves, so pressing L again opens a
	# SECOND ledger on top of the orphan. Assert there is only ever ONE ledger.
	var violations: Array = []
	await _open("ledger")
	await _present_event("amplify")
	await _resolve_active_event()
	# Reopen via the same entry point the L key drives.
	_ui._show_ledger_screen()
	await _pump()
	var ledgers := 0
	for p in _visible_modal_panels():
		if p.has_meta("is_ledger"):
			ledgers += 1
	if ledgers > 1:
		violations.append("reopen-after-orphan | I2: %d ledger panels visible at once (orphan + fresh copy)" % ledgers)
	violations.append_array(_check_invariants("ledger reopened after orphan"))
	await _assert_closable("drain amplified ledgers", violations)
	_assert_no_violations(violations, "orphaned ledger duplicates on reopen")

# ---------------------------------------------------------------------------
# 3. INVERSE: opening dialogs while a live event dialog is up
# ---------------------------------------------------------------------------

func test_opening_each_dialog_kind_over_a_live_event_dialog():
	# The mouse path is barred by the event blocker, but programmatic paths
	# (dev-overlay jump buttons drive _show_ledger_screen / travel / employee
	# directly) and future code CAN do this. EXPECTED: either refused, or the
	# event dialog + ITS ROOT-LEVEL BLOCKER are both torn down. CURRENT: the
	# free-first idiom frees the event PANEL but the blocker lives at the
	# viewport root untracked (event_dialog.gd:95-102) -> permanent mouse-block
	# + is_showing_event stuck true.
	var violations: Array = []
	for kind in ["ledger", "fundraise", "doom_trend"]:
		await _present_event(String(kind))
		await _open(kind)
		violations.append_array(_check_invariants("%s over live event" % kind))
		await _assert_closable("drain %s over event" % kind, violations)
		violations.append_array(_check_invariants("after drain %s over event" % kind))
		await _nuke_all_overlays()
	_assert_no_violations(violations, "opening a dialog over a live event dialog")

func test_same_frame_collision_event_then_ledger():
	# Frame-exact hostile interleave: present() has an await inside -- open the
	# ledger in the SAME frame, inside that window, before the presenter settles.
	var violations: Array = []
	_ui.event_dialog.present(_mk_event("sameframe"))
	_ui._show_ledger_screen()          # no await between -- mid-flight collision
	await _pump(3)
	violations.append_array(_check_invariants("same-frame event+ledger"))
	await _assert_closable("drain same-frame collision", violations)
	_assert_no_violations(violations, "same-frame event/ledger collision")

# ---------------------------------------------------------------------------
# 4. Pairwise replacement matrix across the submenu family
# ---------------------------------------------------------------------------

func test_pairwise_dialog_replacement_matrix():
	# Every ordered pair (A, B) of free-first dialogs: open A, open B on top.
	# EXPECTED: A freed, B tracked, exactly one barrier, closable.
	var violations: Array = []
	for a in SUBMENU_KINDS:
		for b in SUBMENU_KINDS:
			await _open(a)
			await _open(b)
			var ctx := "pair %s->%s" % [a, b]
			violations.append_array(_check_invariants(ctx))
			await _assert_closable("close " + ctx, violations)
			if violations.size() > 12:
				gut.p("  (aborting matrix early -- violation budget exceeded)")
				_assert_no_violations(violations, "pairwise replacement matrix (aborted early)")
				return
			await _nuke_all_overlays()
	_assert_no_violations(violations, "pairwise replacement matrix")

func test_rapid_double_open_same_kind():
	var violations: Array = []
	for kind in ["ledger", "fundraise", "employee_card"]:
		# Two opens in the SAME frame -- the first queue_free has not landed yet.
		await _open(kind)
		match kind:
			"ledger":
				_ui._show_ledger_screen()
			"fundraise":
				_ui.submenu_controller.open("fundraise")
			"employee_card":
				_ui.employee_panel.show_staff_id_card({"specialization": "safety", "name": "Twin"})
		await _pump(3)
		violations.append_array(_check_invariants("double-open %s" % kind))
		await _assert_closable("drain double-open %s" % kind, violations)
		await _nuke_all_overlays()
	_assert_no_violations(violations, "rapid double-open of the same dialog kind")

# ---------------------------------------------------------------------------
# 5. Event queue integrity under sequential resolution
# ---------------------------------------------------------------------------

func test_two_queued_events_resolve_sequentially_clean():
	var violations: Array = []
	await _present_event("q1")
	await _present_event("q2")     # queues behind q1
	violations.append_array(_check_invariants("two events queued"))
	await _resolve_active_event()  # q1 -> q2 auto-shows
	violations.append_array(_check_invariants("after resolving first"))
	await _resolve_active_event()  # q2
	violations.append_array(_check_invariants("after resolving second"))
	if _ui.event_dialog.is_showing_event:
		violations.append("event queue drain | I6: presenter still showing after both resolved")
	_assert_no_violations(violations, "sequential resolution of a queued event pair")

# ---------------------------------------------------------------------------
# 6. Seeded monkey fuzz -- SAFE op set (free-first family only; must stay GREEN)
# ---------------------------------------------------------------------------

func test_monkey_safe_ops_seeded():
	# Regression lock for the free-first idiom: no event/staff-card ops, so this
	# run is expected GREEN today and must STAY green.
	var rng := RandomNumberGenerator.new()
	rng.seed = MONKEY_SEED
	var ops: Array = SUBMENU_KINDS.duplicate()
	ops.append("close")
	ops.append("pump")
	var trace: Array = []
	for step in range(MONKEY_STEPS):
		var op: String = ops[rng.randi_range(0, ops.size() - 1)]
		trace.append(op)
		match op:
			"close":
				await _close_tracked()
			"pump":
				await _pump(1)
			_:
				await _open(op)
		var violations := _check_invariants("safe-monkey step %d (%s)" % [step, op])
		if violations.size() > 0:
			gut.p("REPRO seed=%d trace=%s" % [MONKEY_SEED, str(trace)])
			_assert_no_violations(violations, "safe monkey (seed %d) broke at step %d" % [MONKEY_SEED, step])
			return
	assert_true(true, "safe monkey: %d ops, invariants held" % MONKEY_STEPS)

# ---------------------------------------------------------------------------
# 7. Seeded monkey fuzz -- FULL op set (events + staff card; documents the class)
# ---------------------------------------------------------------------------

func test_monkey_full_ops_seeded():
	# The full hostile surface. EXPECTED RED until the #877/#883 class is fixed;
	# the printed trace + fixed seed reproduce the first desync exactly.
	var rng := RandomNumberGenerator.new()
	rng.seed = MONKEY_SEED
	var ops: Array = SUBMENU_KINDS.duplicate()
	ops.append_array(["event", "event", "resolve", "employee_card", "close", "pump"])
	var trace: Array = []
	for step in range(MONKEY_STEPS):
		var op: String = ops[rng.randi_range(0, ops.size() - 1)]
		trace.append(op)
		match op:
			"close":
				await _close_tracked()
			"resolve":
				await _resolve_active_event()
			"pump":
				await _pump(1)
			_:
				await _open(op)
		var violations := _check_invariants("full-monkey step %d (%s)" % [step, op])
		if violations.size() > 0:
			gut.p("REPRO seed=%d trace=%s" % [MONKEY_SEED, str(trace)])
			_assert_no_violations(violations, "full monkey (seed %d) broke at step %d" % [MONKEY_SEED, step])
			return
	assert_true(true, "full monkey: %d ops, invariants held" % MONKEY_STEPS)

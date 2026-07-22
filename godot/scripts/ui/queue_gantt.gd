class_name QueueGantt
extends VBoxContainer
## The committed-queue gantt / "operations underway" tracker (UI_PROPOSALS_2026-07-22 P10 /
## BUILD_BRIEF_PLAN_WATCH_UI PLAN elem 2 + WATCH elem 4 -- the headline drift D2). One row per
## in-flight / queued play: [#] name [====----] ETA. The fishing-line made visual.
##
## PURE VIEW (ADR-0006): reads a serialized state snapshot + the plan-time tentative queue and
## renders; it NEVER writes game state, mutates the sim, or touches RNG. Shown only in the
## "proposed" A/B layout; the classic one-line QueuePanel hint is untouched.
##
## Data source (read-only, per the task): month_plan.queued_strategic is the real gantt data --
## each carries queued_on_turn + resolves_on_turn, so duration and ETA are exact and WATCH can
## fill a true progress bar. state.hiring.jobs (in-flight interview/offer/connections) are
## folded in with their ETA. The plan-time tentative queue (main_ui.queued_actions -- {id,name})
## is appended as order-only "planned" rows so PLAN shows the month-ahead before you commit.
##
## Queue-order-as-priority: month_plan resolves strategic WIP by resolves_on_turn tick, NOT by
## list order, and exposes no reorder method -- so the mechanic has NO engine surface. Per the
## brief we therefore render the order READ-ONLY (a priority number, no reorder handle) and note
## it; wiring reorder is a sim change out of scope for this UI-only harness.

const _BAR_CELLS := 12


func _ready() -> void:
	add_theme_constant_override("separation", 2)


## Extract gantt rows from a serialized game-state Dictionary (GameState.to_dict() shape) plus
## the plan-time tentative queue. Static + tree-free so it is unit-testable in isolation. Each
## row: {name:String, eta:int, duration:int, progress:float, kind:String, has_eta:bool}.
static func rows_from_state(state: Dictionary, tentative: Array = []) -> Array:
	var rows: Array = []
	var cur := int(state.get("turn", 0))

	# Committed strategic WIP -- the real duration + ETA + progress.
	var mp: Dictionary = state.get("month_plan", {})
	for item in mp.get("queued_strategic", []):
		if not (item is Dictionary):
			continue
		var q := int(item.get("queued_on_turn", cur))
		var r := int(item.get("resolves_on_turn", cur))
		var dur: int = max(1, r - q)
		var prog: float = clampf(float(cur - q) / float(dur), 0.0, 1.0)
		rows.append({
			"name": _pretty(String(item.get("action_id", "work"))),
			"eta": r, "duration": dur, "progress": prog,
			"kind": "strategic", "has_eta": true,
		})

	# In-flight hiring jobs (Phase B pipeline) -- ETA known; no queued_on_turn, so no fill.
	var hiring: Dictionary = state.get("hiring", {})
	for job in hiring.get("jobs", []):
		if not (job is Dictionary):
			continue
		var r := int(job.get("resolves_on_turn", cur))
		rows.append({
			"name": _pretty(String(job.get("kind", "hire"))),
			"eta": r, "duration": max(1, r - cur), "progress": 0.0,
			"kind": "hiring", "has_eta": true,
		})

	# Plan-time tentative queue -- order only, no ETA until committed.
	for t in tentative:
		if not (t is Dictionary):
			continue
		rows.append({
			"name": String(t.get("name", "?")),
			"eta": -1, "duration": 0, "progress": 0.0,
			"kind": "planned", "has_eta": false,
		})
	return rows


## Rebuild the visible rows. `watch_mode` swaps the register (green/live vs amber/plan) and is
## what makes the progress fill meaningful (in PLAN nothing has started, so bars read hollow).
func update_rows(rows: Array, watch_mode: bool = false) -> void:
	for child in get_children():
		child.queue_free()

	if rows.is_empty():
		var hint := Label.new()
		hint.text = "No operations underway -- queue plays in PLAN."
		hint.add_theme_font_override("font", TerminalTheme.mono_font())
		hint.add_theme_color_override("font_color", TerminalTheme.TEXT_DIM)
		hint.add_theme_font_size_override("font_size", 10)
		add_child(hint)
		return

	var accent: Color = TerminalTheme.GREEN if watch_mode else TerminalTheme.AMBER
	var accent_dim: Color = TerminalTheme.GREEN_DIM if watch_mode else TerminalTheme.AMBER_DIM
	var priority := 0
	for row in rows:
		priority += 1
		add_child(_build_row(priority, row, accent, accent_dim, watch_mode))


func row_count() -> int:
	"""Number of built gantt rows (excludes the empty-state hint). For tests + the header."""
	var n := 0
	for child in get_children():
		# queue_free() from a prior update is deferred -- old rows linger for a frame; exclude them.
		if child.has_meta("gantt_row") and not child.is_queued_for_deletion():
			n += 1
	return n


func _build_row(priority: int, row: Dictionary, accent: Color, accent_dim: Color, watch_mode: bool) -> Control:
	var line := HBoxContainer.new()
	line.set_meta("gantt_row", true)
	line.add_theme_constant_override("separation", 6)

	var num := Label.new()
	num.text = "%d" % priority
	num.custom_minimum_size = Vector2(16, 0)
	num.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	num.add_theme_font_override("font", TerminalTheme.mono_font())
	num.add_theme_color_override("font_color", accent)
	num.add_theme_font_size_override("font_size", 11)
	line.add_child(num)

	var name_label := Label.new()
	name_label.text = String(row.get("name", "?"))
	name_label.custom_minimum_size = Vector2(96, 0)
	name_label.clip_text = true
	name_label.add_theme_font_override("font", TerminalTheme.mono_font())
	name_label.add_theme_color_override("font_color", TerminalTheme.TEXT)
	name_label.add_theme_font_size_override("font_size", 11)
	line.add_child(name_label)

	var bar := Label.new()
	bar.text = _bar_string(row, watch_mode)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.add_theme_font_override("font", TerminalTheme.mono_font())
	bar.add_theme_color_override("font_color", accent_dim if not watch_mode else accent)
	bar.add_theme_font_size_override("font_size", 11)
	line.add_child(bar)

	var eta := Label.new()
	if bool(row.get("has_eta", false)):
		eta.text = "T%d" % int(row.get("eta", 0))
		eta.tooltip_text = "Lands on resolution tick (turn) %d." % int(row.get("eta", 0))
	else:
		eta.text = "queued"
	eta.add_theme_font_override("font", TerminalTheme.mono_font())
	eta.add_theme_color_override("font_color", accent_dim)
	eta.add_theme_font_size_override("font_size", 10)
	line.add_child(eta)

	return line


func _bar_string(row: Dictionary, watch_mode: bool) -> String:
	if not bool(row.get("has_eta", false)):
		return "[" + "-".repeat(_BAR_CELLS) + "]"  # planned, not committed -> hollow
	var prog: float = clampf(float(row.get("progress", 0.0)), 0.0, 1.0) if watch_mode else 0.0
	var filled: int = clampi(int(round(prog * _BAR_CELLS)), 0, _BAR_CELLS)
	return "[" + "=".repeat(filled) + "-".repeat(_BAR_CELLS - filled) + ">"


static func _pretty(raw: String) -> String:
	"""Turn an action_id / job kind into a readable label (safe, no data lookup)."""
	if raw.is_empty():
		return "work"
	return raw.replace("_", " ").capitalize()

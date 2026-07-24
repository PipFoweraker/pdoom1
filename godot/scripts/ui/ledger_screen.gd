extends Node
class_name LedgerScreen
## Liability Ledger UI -- extracted from main_ui.gd (#622, build lane L10).
##
## Owns the leather palette, the compact clickable summary button (BL-1/#578),
## and the full ledger screen builder (#601). Zero turn/AP coupling -- this module
## survives the turn-engine rewrite untouched.
##
## MainUI keeps the single _show_ledger_screen entry point (L key, summary click,
## financing submenu, dev overlay) and its active_dialog bookkeeping; this module
## just builds the widgets and reports state.

## BBCode line for the host's message log (the one-shot "payment due" warning).
signal message_logged(text: String)

# Leather-ledger palette (playtester: "rich brown leathery colour"). Warm saddle base
# with a darker border; ink colours are bright/warm so state stays legible on brown.
const _LEDGER_LEATHER := Color(0.32, 0.20, 0.11)        # base saddle brown
const _LEDGER_LEATHER_HOVER := Color(0.40, 0.26, 0.15)  # lighter on hover -- inviting
const _LEDGER_LEATHER_PRESSED := Color(0.24, 0.15, 0.08)
const _LEDGER_LEATHER_BORDER := Color(0.14, 0.08, 0.03)  # dark stitched edge
const _LEDGER_INK_CLEAN := Color(0.86, 0.80, 0.62)       # warm parchment cream
const _LEDGER_INK_DUE := Color(1.0, 0.55, 0.42)          # warm red -- payment due
const _LEDGER_INK_SECRET := Color(1.0, 0.80, 0.45)       # warm amber -- secrets/owed
# #601: ledger warnings on the message log get a DISTINCT RED so they stand apart from the
# normal event/positive greens/golds. Kept as a named constant so it's unit-testable.
const _LEDGER_WARN_RED := Color(0.93, 0.24, 0.20)

var _summary_button: Button
var _ledger_due_soon_logged: bool = false  # #578: only log the "payment due" reminder on entry, not every frame

static func _make_leather_box(bg: Color) -> StyleBoxFlat:
	"""A warm saddle-leather StyleBoxFlat: dark stitched border + subtle rounding."""
	var box := StyleBoxFlat.new()
	box.bg_color = bg
	box.border_color = _LEDGER_LEATHER_BORDER
	box.set_border_width_all(3)
	box.set_corner_radius_all(8)
	box.content_margin_left = 14
	box.content_margin_right = 14
	box.content_margin_top = 8
	box.content_margin_bottom = 8
	return box

static func _apply_leather_style(btn: Button) -> void:
	"""Give the ledger access button its rich brown leather look across all states."""
	btn.add_theme_stylebox_override("normal", _make_leather_box(_LEDGER_LEATHER))
	btn.add_theme_stylebox_override("hover", _make_leather_box(_LEDGER_LEATHER_HOVER))
	btn.add_theme_stylebox_override("pressed", _make_leather_box(_LEDGER_LEATHER_PRESSED))
	btn.add_theme_stylebox_override("focus", _make_leather_box(_LEDGER_LEATHER_HOVER))

## Player-facing due date for a ledger entry (Pip 2026-07-24: the ledger used to show
## raw turn counts, but the game's clock is DAYS -- this is a pure display conversion,
## NOT a new time system. The underlying fuse is already day-tick-grained: turn_manager
## calls Ledger.tick_and_bill() exactly once per turn (turn_manager.gd
## _step_ledger_tick_and_bill), and Clock defines turn = 1 workday (clock.gd), so
## `turn + fuse` is the due turn and Clock.date_for_turn() gives its real calendar date.
## Returns "due this turn" when the fuse has reached 0 (bills THIS tick, per the
## Ledger.Entry.fuse doc: "0 = due now"); otherwise "due <date> (in N days)" using
## Clock.calendar_days_between() so weekends are counted correctly, not just turn deltas.
static func _due_text(fuse: int, turn: int, start_year: int, start_month: int, start_day: int) -> String:
	if fuse <= 0:
		return "due this turn"
	var due_turn := turn + fuse
	var d := Clock.date_for_turn(due_turn, start_year, start_month, start_day)
	var date_txt := "%d %s %d" % [int(d.day), Clock.MONTH_ABBR[int(d.month) - 1], int(d.year)]
	var days := Clock.calendar_days_between(turn, due_turn)
	return "due %s (in %d day%s)" % [date_txt, days, "" if days == 1 else "s"]

func create_summary_button() -> Button:
	"""BL-1: compact Liability Ledger summary button. Kept terse so the main view stays
	uncrowded; the full ledger is a switchable screen (Financing).
	#578: it's a flat Button so the summary is directly clickable to open the full
	ledger screen (playtester: "no easy way of getting to the ledger from the main UI").
	Playtester: the ledger access was "kind of hidden" -- make it ~5x bigger with a
	rich brown leather look so it reads as a distinct, inviting object, not a label."""
	_summary_button = Button.new()
	_summary_button.flat = false
	_summary_button.focus_mode = Control.FOCUS_NONE
	_summary_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	_summary_button.custom_minimum_size = Vector2(0, 64)  # heft -- was an 11px flat label
	_summary_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_summary_button.add_theme_font_size_override("font_size", 20)
	_summary_button.add_theme_color_override("font_color", _LEDGER_INK_CLEAN)
	_apply_leather_style(_summary_button)
	_summary_button.text = " Liability Ledger -- clean"
	_summary_button.tooltip_text = "Open the Liability Ledger  (press L)"
	return _summary_button

func update_summary(ledger_data: Dictionary, turn: int = 0,
		start_year: int = GameState.DEFAULT_START_YEAR,
		start_month: int = GameState.DEFAULT_START_MONTH,
		start_day: int = GameState.DEFAULT_START_DAY) -> void:
	"""BL-1 compact summary: outstanding owed, soonest due, secret count. Deliberately
	terse so the main view stays uncrowded; the full ledger is a switchable screen.
	turn/start_* let the soonest-fuse count be shown as a real calendar date (see
	_due_text) instead of a raw turn count."""
	if not _summary_button:
		return
	var owed: float = float(ledger_data.get("outstanding_payable", 0.0))
	var soonest: int = int(ledger_data.get("soonest_fuse", -1))
	var secrets: int = int(ledger_data.get("secret_count", 0))
	if ledger_data.is_empty() or (owed <= 0.0 and secrets == 0):
		_summary_button.text = " Liability Ledger -- clean  (click / L)"
		_summary_button.add_theme_color_override("font_color", _LEDGER_INK_CLEAN)
		_ledger_due_soon_logged = false
		return
	var due_txt := _due_text(soonest, turn, start_year, start_month, start_day) if soonest >= 0 else "no due"
	var secret_txt := ("  |  %d secret" % secrets) if secrets > 0 else ""
	# #578: due-soon reminder. When the soonest payable fuse is within ~1-2 turns, flag it
	# visibly ([!] prefix + strong red) and drop a one-shot message-log line so the player is
	# warned things are coming due, not just left to notice on their own.
	var due_soon := soonest >= 0 and soonest <= 2 and owed > 0.0
	var prefix := "[!] " if due_soon else " "
	_summary_button.text = "%sLedger: %s owed  |  %s%s" % [prefix, GameConfig.format_money(owed), due_txt, secret_txt]
	if due_soon:
		# Urgent: warm red (legible on brown leather), and log once on entry into the window.
		_summary_button.add_theme_color_override("font_color", _LEDGER_INK_DUE)
		if not _ledger_due_soon_logged:
			message_logged.emit("[color=#%s][!] Ledger: %s payment %s -- open the ledger (click summary or press L) to review.[/color]" % [_LEDGER_WARN_RED.to_html(false), GameConfig.format_money(owed), due_txt])
			_ledger_due_soon_logged = true
	else:
		_ledger_due_soon_logged = false
		# Warm parchment when only owed; warm amber as secret liabilities mount (exposure pressure).
		_summary_button.add_theme_color_override("font_color", _LEDGER_INK_CLEAN if secrets == 0 else _LEDGER_INK_SECRET)

func build_screen(ledger, viewport_size: Vector2, on_close: Callable = Callable(),
		turn: int = 0,
		start_year: int = GameState.DEFAULT_START_YEAR,
		start_month: int = GameState.DEFAULT_START_MONTH,
		start_day: int = GameState.DEFAULT_START_DAY) -> Panel:
	"""BL-1: the full Liability Ledger screen -- lists every live entry (source, currency,
	principal, fuse, secrecy) plus death attribution.

	#601: styled as a distinct leather-bound object whose inner content FILLS the panel
	(the old build left everything cramped top-left with the terms truncated). The entries
	are laid out as a real column table so nothing like 'due 16 Aug 2017 (in 12 days)
	@25%/t' gets clipped, and the panel carries an is_ledger meta so the L key can toggle
	it closed (#601). turn/start_* convert each entry's fuse to a real calendar due date
	(see _due_text) instead of a raw turn count.

	The host owns overlay parenting, z-index, active_dialog bookkeeping, and chrome."""
	# Larger, centred panel so the ledger reads as a substantial object, not a scrap.
	var dialog := Panel.new()
	var panel_size := Vector2(minf(720.0, viewport_size.x - 60.0), minf(560.0, viewport_size.y - 60.0))
	dialog.custom_minimum_size = panel_size
	dialog.size = panel_size
	dialog.position = ((viewport_size - panel_size) / 2.0).max(Vector2(20, 20))
	dialog.set_meta("is_ledger", true)  # lets the L key toggle it closed (#601)

	# Distinct leather binding so the ledger stands apart from the grey submenus. Setting a
	# bespoke 'panel' stylebox here makes the close-affordance chrome keep it (#510).
	var ledger_panel_style := _make_leather_box(Color(0.16, 0.11, 0.07, 0.99))
	dialog.add_theme_stylebox_override("panel", ledger_panel_style)

	# Fill the whole panel: anchor the margin to all four edges so the content stretches
	# to the panel's size instead of collapsing to its top-left minimum (#601).
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 22)
	margin.add_theme_constant_override("margin_right", 22)
	margin.add_theme_constant_override("margin_top", 20)
	margin.add_theme_constant_override("margin_bottom", 30)
	dialog.add_child(margin)
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	margin.add_child(vbox)

	var title := Label.new()
	title.text = " LIABILITY LEDGER"
	title.add_theme_font_size_override("font_size", 22)
	title.add_theme_color_override("font_color", _LEDGER_INK_CLEAN)
	vbox.add_child(title)

	var rule := HSeparator.new()
	vbox.add_child(rule)

	if ledger == null:
		var none := Label.new()
		none.text = "(no ledger)"
		none.add_theme_color_override("font_color", _LEDGER_INK_CLEAN)
		vbox.add_child(none)
	else:
		var summary := Label.new()
		summary.text = "Owed: %s        Favors: %s        Secrets: %d" % [
			GameConfig.format_money(ledger.outstanding(Ledger.Side.PAYABLE)),
			GameConfig.format_money(ledger.outstanding(Ledger.Side.RECEIVABLE)),
			ledger.secret_entries().size()]
		summary.add_theme_font_size_override("font_size", 15)
		summary.add_theme_color_override("font_color", _LEDGER_INK_SECRET)
		vbox.add_child(summary)

		# Scroll grows to consume the remaining panel height, so the table fills the space.
		var scroll := ScrollContainer.new()
		scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
		scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		vbox.add_child(scroll)

		var live = ledger.entries.filter(func(e): return not e.settled)
		if live.is_empty():
			var clean := Label.new()
			clean.text = "Clean books. Every mitigation you take will show up here as a bill."
			clean.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			clean.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			clean.add_theme_color_override("font_color", Color(0.6, 0.75, 0.6))
			scroll.add_child(clean)
		else:
			# Real column table: Source | Amount | Due | Notes. Each cell sizes to its own
			# content so terms like 'due 16 Aug 2017 (in 12 days) @25%/t' are never
			# truncated (#601).
			var table := GridContainer.new()
			table.columns = 4
			table.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			table.add_theme_constant_override("h_separation", 24)
			table.add_theme_constant_override("v_separation", 8)
			scroll.add_child(table)

			for head in ["Source", "Amount", "Due", "Notes"]:
				var h := Label.new()
				h.text = head
				h.add_theme_font_size_override("font_size", 12)
				h.add_theme_color_override("font_color", Color(0.70, 0.62, 0.45))
				table.add_child(h)

			for e in live:
				var side_txt = "owe" if e.side == Ledger.Side.PAYABLE else "owed"
				var interest_txt = ("  @%.0f%%/t" % (e.interest * 100.0)) if e.interest > 0.0 else ""
				var note_txt = "SECRET" if e.secret else ""
				var row_color = _LEDGER_INK_SECRET if e.secret else _LEDGER_INK_CLEAN
				var cells = [
					str(e.source),
					"%s %.0f %s" % [side_txt, e.principal, e.currency],
					"%s%s" % [_due_text(e.fuse, turn, start_year, start_month, start_day), interest_txt],
					note_txt,
				]
				for cell_text in cells:
					var cell := Label.new()
					cell.text = cell_text
					cell.add_theme_font_size_override("font_size", 14)
					cell.add_theme_color_override("font_color", row_color)
					table.add_child(cell)

		if ledger.death_attribution.size() > 0:
			var att := Label.new()
			att.text = "Attributed damage: %d billed shortfalls" % ledger.death_attribution.size()
			att.add_theme_color_override("font_color", _LEDGER_WARN_RED)
			vbox.add_child(att)

	# fix/ui-no-dead-ends: give the ledger its OWN exit so it is never a dead-end.
	# The reported bug -- opened the ledger, no working close/back, Esc did nothing --
	# came from build_screen returning a bare Panel whose exit was ENTIRELY host-provided
	# (MainUI._decorate_active_submenu for the [X], MainUI._input for Esc). If that host
	# wiring is absent or regresses, the player is trapped. Routing through the shared
	# submenu chrome attaches a visible [X] close control AND intrinsic ui_cancel (Esc)
	# handling to the panel itself. on_close defaults to a self-free so the panel is
	# escapable in isolation; the host passes its own close routine to keep bookkeeping.
	var close_cb: Callable = on_close
	if not close_cb.is_valid():
		close_cb = func(): dialog.queue_free()
	SubmenuChrome.add_close_affordance(dialog, close_cb)

	return dialog

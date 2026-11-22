class_name MonthReviewPanel
extends RefCounted
## The month review as an OBJECT, not an overlay (Pip, 2026-08-14: "the month review screen
## could come in, like, clipboard form or some other diegetic form").
##
## Why a clipboard. The thesis of this game is that the bureaucracy IS the game. A month
## summary drawn as a HUD panel says "here is your data"; a month summary drawn as a sheet
## somebody clipped to a board and left on your desk says "here is what your month amounted
## to, and a person typed it up". The second one is the game's own argument, and it is the
## same instinct as the 2026-08-12 calendar ruling ("semi-diegetic ... shrink or grow rather
## than disappear and reappear entirely"). It also earns the modal: an object with physical
## presence has an obvious reason to sit on top of the feed.
##
## Diegetic here does NOT mean photorealistic. The register is still the terminal/CRT one the
## rest of the UI implies (TerminalTheme) and the dark office the isometric floor view shows:
## a hardboard clip, a manila sheet at the luminance paper actually has in a dark room, and
## everything on it TYPED -- the same monospace the feed and the plan screen use. The board is
## drawn with styleboxes, not art, so it costs nothing and cannot go stale; see BOARD ART SLOT
## below for the single swap that would finish it.
##
## PRESENTATION ONLY. Every string on the sheet arrives pre-built in the event's "review"
## payload (game_manager._finish_month_playback), which is assembled from the SAME rows as the
## plain-text "description" the WATCH feed records. This file computes no numbers, reads no
## game state, and rewrites no wording -- it decides where the words sit and what colour the
## ink is. A presenter that ignores the payload still renders the whole review from
## "description", which is what every other event dialog does.

# --- SURFACE ART SLOTS ------------------------------------------------------
# Two surfaces make the object, and both are ALREADY-PACKED art -- no promotion was needed and
# none was done. They were sitting in the pack unreferenced:
#
#   BOARD  res://assets/textures/surfaces/tex_plywood_stained_512.png
#          Stained plywood with grain, spotting and coffee rings. It is the desk-furniture
#          register the isometric office floor implies, and dark enough (mid-olive, further
#          dimmed by BOARD_TINT) to sit inside the CRT palette rather than beside it.
#   PAPER  res://assets/textures/surfaces/tex_grid_graphpaper_aged_512.png
#          Aged graph paper, foxed, with two coffee rings printed into it. This is the whole
#          argument in one asset: the month summary is a form somebody typed on the paper that
#          was to hand.
#
# Set either to "" and that surface falls back to the flat fill below -- the layout is
# identical either way, so an art lane can swap in a purpose-drawn clipboard by editing one
# string. What a purpose-drawn replacement would need:
#   BOARD  a hardboard plate, any size, no baked lighting (the shadow is drawn), top edge
#          plain because the metal clip is drawn over it.
#   PAPER  a sheet with visible tooth that stays DIM. A scanned-document white will blow a
#          hole in this palette; the graph paper works because it is foxed, not bright.
# Still MISSING from the pack, and worth requesting as art rather than faking: a real clip
# (the metal jaw here is two styleboxes), and monochrome line-art stamp glyphs at ~24px for
# the Funds / Staff / Doom rows. The existing 64px resource icons are NOT usable for that --
# they are glossy vignetted RPG icons with baked dark backgrounds, and on a lit manila sheet
# they read as stickers, not as print.
const BOARD_TEXTURE_PATH := "res://assets/textures/surfaces/tex_plywood_stained_512.png"
const PAPER_TEXTURE_PATH := "res://assets/textures/surfaces/tex_grid_graphpaper_aged_512.png"
## Multiplied over the surface art. Both source textures are lit for a bright screen; these
## take the board down to furniture and the paper to office-light manila.
const BOARD_TINT := Color(0.60, 0.56, 0.50)
const PAPER_TINT := Color(0.88, 0.86, 0.84)

# --- The object -------------------------------------------------------------
# Hardboard: warm near-black, one step off TerminalTheme.BG_DARK's green-tinted black so the
# board reads as a physical thing sitting IN FRONT of the terminal rather than part of it.
const BOARD := Color(0.145, 0.125, 0.105)
const BOARD_EDGE := Color(0.33, 0.28, 0.21)
const CLIP_METAL := Color(0.56, 0.575, 0.585)
const CLIP_METAL_DARK := Color(0.26, 0.275, 0.285)

# Manila under office light. Deliberately ~0.79 and warm, not paper-white: a full-luminance
# sheet next to this game's palette reads as a browser window, not an object on a desk.
const PAPER := Color(0.795, 0.775, 0.705)
# The attention box's wash. TRANSLUCENT, not a solid fill: the sheet is textured art, and an
# opaque box punched into it would read as a UI widget stuck on the paper rather than a rule
# printed on it.
const PAPER_SHADE := Color(0.20, 0.16, 0.08, 0.10)
const PAPER_EDGE := Color(0.60, 0.585, 0.525)
const PAPER_RULE := Color(0.545, 0.53, 0.475)     # hairlines printed on the form

const INK := Color(0.125, 0.125, 0.115)
const INK_DIM := Color(0.355, 0.35, 0.32)
const STAMP := Color(0.58, 0.185, 0.145)          # faded red rubber stamp

# Delta inks. Same MEANING as main_ui's _DELTA_GOOD / _DELTA_BAD chips (favourable green,
# adverse red) re-mixed for paper: those two are tuned to survive a near-black panel and go
# washy on manila, so these are the printed renderings of the same hues. Sign, not judgement --
# game_manager supplies the sign, this file only picks the pigment.
const INK_GOOD := Color(0.09, 0.40, 0.15)
const INK_BAD := Color(0.62, 0.13, 0.10)
const INK_WARN := Color(0.60, 0.38, 0.05)         # amber ink, the middle heat band

# Rival heat bands (game_manager._collect_rivals_review_rows): 0 flat, 1 slipping, 2 rising,
# 3 climbing fast. Colour is HEAT, not verdict -- how fast the rival is moving, which is the
# one thing three indented sentences could not show at a glance.
const HEAT_INKS := [INK_DIM, INK_GOOD, INK_WARN, INK_BAD]

# --- Type sizes -------------------------------------------------------------
# Pip, 2026-08-14: "the text can just all universally go up 2 to 4 points." Applied here only
# (a global sweep is a separate change). Baselines are the generic event dialog's: body 16,
# small 14, title 18, navigation button 16.
const SIZE_BODY := 19        # 16 + 3
const SIZE_SMALL := 17       # 14 + 3
const SIZE_CLOSING := 18     # 16 + 2
const SIZE_PERIOD := 20      # 18 + 2
# The masthead is the one line that breaks the +2..+4 rule: 18 -> 24. It is now the title of a
# sheet with three times the area under it, and at 22 it did not read as a masthead beside
# 19pt body. Flagged rather than smuggled -- easy to pull back to 22.
const SIZE_HEADING := 24
## Font size for the single navigation button, applied by EventDialog. 16 + 4.
const SIZE_BUTTON := 20
## Button footprint on the board, applied by EventDialog (generic navigation is 520x54).
const BUTTON_SIZE := Vector2(560, 62)

# --- Geometry ---------------------------------------------------------------
# The ask was "double or triple the area". The generic event dialog is a fixed 600x450
# (270,000 px^2) at every resolution; this scales with the viewport and caps out at 1120x760.
#   1920x1080 -> 1120 x 760  = 851,200 px^2  = 3.15x
#   1600x900  -> 1120 x 720  = 806,400 px^2  = 2.99x
#   1280x720  ->  921 x 576  = 530,700 px^2  = 1.97x
# i.e. triple where Pip plays, still double on the smallest supported window.
const WIDTH_RATIO := 0.72
const HEIGHT_RATIO := 0.80
const MAX_SIZE := Vector2(1120.0, 760.0)
const MIN_SIZE := Vector2(640.0, 470.0)

## Backdrop opacity behind the clipboard. The generic dialog uses 0.6, which left the WATCH
## feed reading at nearly full strength around the panel -- the review was covering the thing
## it summarises rather than replacing it. At 0.85 the office goes dark and the object is the
## only lit surface, which is also what makes it read as an object.
const BACKDROP_ALPHA := 0.85


static func is_month_review(event: Dictionary) -> bool:
	"""True when this event carries a month-review presentation payload. Keyed on the payload,
	not on the event id, so the presenter never needs to know game_manager's constants -- and
	so a review built without a payload degrades to the generic dialog instead of crashing."""
	var payload = event.get("review", null)
	return payload is Dictionary and not (payload as Dictionary).is_empty()


static func apply_geometry(dialog: Panel, viewport_size: Vector2) -> void:
	"""Size and centre the board. Kept separate from build() so the caller sets geometry before
	the layout is filled, exactly as the generic path does."""
	var w := clampf(viewport_size.x * WIDTH_RATIO, MIN_SIZE.x, MAX_SIZE.x)
	var h := clampf(viewport_size.y * HEIGHT_RATIO, MIN_SIZE.y, MAX_SIZE.y)
	dialog.custom_minimum_size = Vector2(w, h)
	dialog.size = Vector2(w, h)
	dialog.position = Vector2(
		roundf((viewport_size.x - w) / 2.0),
		roundf((viewport_size.y - h) / 2.0))


static func build(dialog: Panel, event: Dictionary) -> VBoxContainer:
	"""Draw the clipboard into `dialog` and return the container the caller must put the option
	button (and the rejection-reason label) into. That slot is on the BOARD, below the sheet:
	the paper is the report, the board is where the action lives, and keeping the button off
	the paper preserves the teal 'forward door' chrome that B2/B3 gave it -- teal ink on manila
	would have been unreadable."""
	var review: Dictionary = event.get("review", {})
	var font := TerminalTheme.mono_font()

	_skin_board(dialog)

	var outer := MarginContainer.new()
	outer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	outer.add_theme_constant_override("margin_left", 16)
	outer.add_theme_constant_override("margin_right", 16)
	outer.add_theme_constant_override("margin_top", 10)
	outer.add_theme_constant_override("margin_bottom", 14)
	dialog.add_child(outer)

	var board_v := VBoxContainer.new()
	board_v.add_theme_constant_override("separation", 8)
	outer.add_child(board_v)

	board_v.add_child(_build_clip())
	board_v.add_child(_build_sheet(review, font))

	# The action slot, on the board under the sheet.
	var footer := VBoxContainer.new()
	footer.add_theme_constant_override("separation", 6)
	footer.alignment = BoxContainer.ALIGNMENT_CENTER
	board_v.add_child(footer)
	return footer


# --- the board and its clip -------------------------------------------------

static func _skin_board(dialog: Panel) -> void:
	"""Hardboard fill, plywood grain over it, and a drop shadow. The shadow is what lifts the
	object off the darkened office behind it; without it the panel reads as a flat rectangle
	again no matter what is painted on it."""
	var sb := StyleBoxFlat.new()
	sb.bg_color = BOARD
	sb.border_color = BOARD_EDGE
	sb.set_border_width_all(2)
	sb.set_corner_radius_all(4)
	sb.shadow_color = Color(0.0, 0.0, 0.0, 0.60)
	sb.shadow_size = 26
	sb.shadow_offset = Vector2(0, 10)
	dialog.add_theme_stylebox_override("panel", sb)
	_add_surface(dialog, BOARD_TEXTURE_PATH, BOARD_TINT, 2)


static func _build_clip() -> Control:
	"""The metal clip. Two stacked bars: a dark jaw and a lit plate over it. Cheap, and it is
	the single detail that makes the rectangle read as a clipboard rather than a card."""
	var centre := CenterContainer.new()
	var jaw := Panel.new()
	jaw.custom_minimum_size = Vector2(196, 20)
	var jaw_sb := StyleBoxFlat.new()
	jaw_sb.bg_color = CLIP_METAL_DARK
	jaw_sb.set_corner_radius_all(4)
	jaw_sb.border_color = Color(0.14, 0.15, 0.155)
	jaw_sb.set_border_width_all(1)
	jaw.add_theme_stylebox_override("panel", jaw_sb)
	centre.add_child(jaw)

	var plate := Panel.new()
	plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	plate.offset_left = 26
	plate.offset_right = -26
	plate.offset_top = 4
	plate.offset_bottom = -7
	var plate_sb := StyleBoxFlat.new()
	plate_sb.bg_color = CLIP_METAL
	plate_sb.set_corner_radius_all(2)
	plate.add_theme_stylebox_override("panel", plate_sb)
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	jaw.add_child(plate)
	return centre


# --- the sheet --------------------------------------------------------------

static func _build_sheet(review: Dictionary, font: Font) -> Control:
	var paper := PanelContainer.new()
	paper.size_flags_vertical = Control.SIZE_EXPAND_FILL
	var sb := StyleBoxFlat.new()
	sb.bg_color = PAPER
	sb.border_color = PAPER_EDGE
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(1)
	sb.shadow_color = Color(0.0, 0.0, 0.0, 0.35)
	sb.shadow_size = 8
	sb.shadow_offset = Vector2(0, 3)
	paper.add_theme_stylebox_override("panel", sb)
	# The sheet's ground. A PanelContainer lays every child out over its whole content rect, so
	# this goes in FIRST and everything added after it is printed on top.
	_add_surface(paper, PAPER_TEXTURE_PATH, PAPER_TINT, 1)

	var pad := MarginContainer.new()
	pad.add_theme_constant_override("margin_left", 26)
	pad.add_theme_constant_override("margin_right", 26)
	pad.add_theme_constant_override("margin_top", 20)
	pad.add_theme_constant_override("margin_bottom", 18)
	paper.add_child(pad)

	var sheet := VBoxContainer.new()
	sheet.add_theme_constant_override("separation", 12)
	pad.add_child(sheet)

	sheet.add_child(_build_masthead(review, font))
	sheet.add_child(_rule(2))

	var lede := String(review.get("lede", ""))
	if lede != "":
		sheet.add_child(_ink_label(lede, SIZE_BODY, INK, font))

	var attention := String(review.get("attention", ""))
	if attention != "":
		sheet.add_child(_build_attention_box(attention, font))

	var columns := _build_columns(review, font)
	if columns != null:
		sheet.add_child(columns)
	else:
		# Nothing moved and no rival is visible (month 1, or a freshly loaded save). Let the
		# sheet breathe rather than jamming the closing line under the attention box.
		var filler := Control.new()
		filler.size_flags_vertical = Control.SIZE_EXPAND_FILL
		sheet.add_child(filler)

	var closing := String(review.get("closing", ""))
	if closing != "":
		sheet.add_child(_rule(1))
		sheet.add_child(_build_closing(closing, font))
	return paper


static func _build_masthead(review: Dictionary, font: Font) -> Control:
	"""Typed heading on the left, the period it covers on the right -- the two halves of the
	event name ("Month Review -- October 2017") set as a form header instead of one string."""
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)

	var heading := _ink_label(String(review.get("heading", "")), SIZE_HEADING, INK, font)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(heading)

	var period := _ink_label(String(review.get("period", "")), SIZE_PERIOD, INK_DIM, font)
	period.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	period.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	row.add_child(period)
	return row


static func _build_attention_box(text: String, font: Font) -> Control:
	"""The attention line is a RULE OF THE GAME, not a status line, so it is set as one: a
	stamped left rule, a tinted panel, and the house-style `[!]` gutter glyph. Not one word of
	Pip's sentence is changed -- it is the frame around it that says 'this is the standing
	rule', which three blank lines of the old wall of text could not."""
	var box := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = PAPER_SHADE
	sb.set_corner_radius_all(0)
	sb.border_color = STAMP
	sb.border_width_left = 4
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	box.add_theme_stylebox_override("panel", sb)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	box.add_child(row)

	var marker := _ink_label("[!]", SIZE_BODY, STAMP, font)
	marker.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	row.add_child(marker)

	var body := _ink_label(text, SIZE_BODY, INK, font)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(body)
	return box


static func _build_columns(review: Dictionary, font: Font) -> Control:
	"""Movement and rivals, side by side. Returns null when neither block has content.

	Both blocks used to be indented text under a colon, which is why every line competed: a
	dollar delta, a headcount and three rival sentences were all the same weight in the same
	column. Movement is now a table (stat / from -> to / signed delta chip) and each rival is
	its own carded row, so the two read as two different kinds of thing."""
	var movement: Array = review.get("movement", [])
	var rivals: Array = review.get("rivals", [])
	if movement.is_empty() and rivals.is_empty():
		return null

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = false

	var row := HBoxContainer.new()
	row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.size_flags_vertical = Control.SIZE_EXPAND_FILL
	row.add_theme_constant_override("separation", 24)
	scroll.add_child(row)

	if not movement.is_empty():
		var left := _build_column(String(review.get("movement_title", "")), font)
		for entry in movement:
			if entry is Dictionary:
				left.add_child(_build_movement_row(entry, font))
		left.size_flags_stretch_ratio = 1.15
		row.add_child(left)

	if not movement.is_empty() and not rivals.is_empty():
		var sep := VSeparator.new()
		var sep_sb := StyleBoxFlat.new()
		sep_sb.bg_color = PAPER_RULE
		sep_sb.content_margin_left = 0
		sep.add_theme_stylebox_override("separator", sep_sb)
		sep.add_theme_constant_override("separation", 1)
		row.add_child(sep)

	if not rivals.is_empty():
		var right := _build_column(String(review.get("rivals_title", "")), font)
		for entry in rivals:
			if entry is Dictionary:
				right.add_child(_build_rival_card(entry, font))
		row.add_child(right)
	return scroll


static func _build_column(title: String, font: Font) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 7)
	if title != "":
		col.add_child(_ink_label(title, SIZE_BODY, INK_DIM, font))
		col.add_child(_rule(1))
	return col


static func _build_movement_row(entry: Dictionary, font: Font) -> Control:
	"""stat | from -> to | signed delta chip. The delta gets its own bordered chip at the right
	margin so a column of them stacks into a readable edge -- the point of the change: a delta
	should read as a delta, not as the tail of a sentence."""
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)

	var stat := _ink_label(String(entry.get("stat", "")), SIZE_BODY, INK_DIM, font)
	stat.custom_minimum_size = Vector2(72, 0)
	row.add_child(stat)

	var from_to := _ink_label("%s -> %s" % [
		String(entry.get("from", "")), String(entry.get("to", ""))], SIZE_BODY, INK, font)
	from_to.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	from_to.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	row.add_child(from_to)

	row.add_child(_delta_chip(String(entry.get("delta", "")), int(entry.get("sign", 0)), font))
	return row


static func _delta_chip(text: String, sign_hint: int, font: Font) -> Control:
	"""A signed, coloured, boxed delta. `sign_hint` is game_manager's DISPLAY sign (+1
	favourable, -1 adverse, 0 neither) -- the same inversion the HUD's per-turn chips use, so a
	falling doom band and a rising balance agree about which way is up."""
	var ink := INK_DIM
	if sign_hint > 0:
		ink = INK_GOOD
	elif sign_hint < 0:
		ink = INK_BAD

	var chip := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(ink.r, ink.g, ink.b, 0.10)
	sb.border_color = Color(ink.r, ink.g, ink.b, 0.45)
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(2)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 1
	sb.content_margin_bottom = 1
	chip.add_theme_stylebox_override("panel", sb)

	var label := _ink_label(text, SIZE_BODY, ink, font)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	chip.add_child(label)
	return chip


static func _build_rival_card(entry: Dictionary, font: Font) -> Control:
	"""One rival, one card: name and focus on the top line, the drift read underneath in the
	heat ink. Three indented sentences all said 'capabilities ...' in the same colour; a
	stack of cards says at a glance which one is running."""
	var heat: int = clampi(int(entry.get("heat", 0)), 0, HEAT_INKS.size() - 1)
	var ink: Color = HEAT_INKS[heat]

	var card := PanelContainer.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.0, 0.0, 0.0, 0.035)
	sb.set_corner_radius_all(0)
	sb.border_color = ink
	sb.border_width_left = 3
	sb.content_margin_left = 10
	sb.content_margin_right = 8
	sb.content_margin_top = 5
	sb.content_margin_bottom = 5
	card.add_theme_stylebox_override("panel", sb)

	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 1)
	card.add_child(col)

	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 8)
	var name_label := _ink_label(String(entry.get("name", "")), SIZE_BODY, INK, font)
	name_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(name_label)
	var focus := String(entry.get("focus", ""))
	if focus != "":
		var focus_label := _ink_label(focus, SIZE_SMALL, INK_DIM, font)
		focus_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		top.add_child(focus_label)
	col.add_child(top)

	var drift := _ink_label(String(entry.get("drift", "")), SIZE_SMALL, ink, font)
	drift.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	col.add_child(drift)
	return card


static func _build_closing(text: String, font: Font) -> Control:
	"""The standing instruction, set as a footer with the house `>>` gutter rather than as the
	last paragraph of the same block of prose."""
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	row.add_child(_ink_label(">>", SIZE_CLOSING, INK_DIM, font))
	var body := _ink_label(text, SIZE_CLOSING, INK, font)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(body)
	return row


# --- small helpers ----------------------------------------------------------

static func _ink_label(text: String, size: int, color: Color, font: Font) -> Label:
	"""Every word on the sheet is typed: same monospace family as the feed and plan screen
	(TerminalTheme.mono_font), which is what keeps a paper object inside the terminal register."""
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	if font != null:
		label.add_theme_font_override("font", font)
	return label


static func _rule(thickness: int) -> HSeparator:
	"""A printed hairline. HSeparator draws its 'separator' stylebox, so a flat fill of
	PAPER_RULE at a fixed height is the rule itself."""
	var sep := HSeparator.new()
	var sb := StyleBoxFlat.new()
	sb.bg_color = PAPER_RULE
	sb.content_margin_top = 0
	sb.content_margin_bottom = 0
	sep.add_theme_stylebox_override("separator", sb)
	sep.add_theme_constant_override("separation", thickness)
	return sep


static func _add_surface(node: Control, path: String, tint: Color, inset: int) -> void:
	"""SURFACE ART SLOT. Paints `path` across `node` as a background TextureRect, inset by
	`inset` px so the stylebox's own border still reads as the edge of the object.

	KEEP_ASPECT_COVERED, not tiling: both textures carry a distinctive coffee ring, and tiling a
	512px square across a 1100px sheet would print that ring twice, which announces the texture
	as wallpaper. Covering scales the square up and crops -- one ring, no seam, no distortion.

	Silent no-op when the slot is empty or the resource is missing: a missing asset must degrade
	to the flat fill underneath, never to a pink checkerboard or a broken modal the player
	cannot dismiss.

	The texture goes inside a clipping WRAPPER rather than clipping the panel itself, because
	`clip_contents` on the panel would also clip the panel's own stylebox -- taking the drop
	shadow with it, and the shadow is what makes the board read as an object sitting in front
	of the terminal rather than a rectangle drawn on it."""
	if path == "" or not ResourceLoader.exists(path):
		return
	var tex = load(path)
	if not (tex is Texture2D):
		push_warning("[MonthReviewPanel] art slot '%s' is not a Texture2D -- using the flat fill" % path)
		return

	var clip := Control.new()
	clip.clip_contents = true
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	clip.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	clip.offset_left = inset
	clip.offset_top = inset
	clip.offset_right = -inset
	clip.offset_bottom = -inset
	node.add_child(clip)

	var ground := TextureRect.new()
	ground.texture = tex
	ground.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ground.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	ground.modulate = tint
	ground.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ground.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	clip.add_child(ground)

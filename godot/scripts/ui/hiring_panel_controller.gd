class_name HiringPanelController
extends RefCounted
## CARVE 3 (docs/MAIN_UI_SEAM_MAP.md, seams R1 + R5): the hiring candidate-card pipeline pulled
## out of the main_ui.gd monolith. Before this it was ~600 inline lines -- the pool panel, the
## per-candidate reveal-gated card, the onboarding checklist card, the offer/negotiation dialog,
## and the in-flight-hiring instrument -- all special-cased in the view (SubmenuController CARVE 2
## deliberately left hiring bespoke rather than force it into the icon-grid). This is its home now.
##
## NON-FORKING extraction (structure-only): every function body is a VERBATIM move; only host-owned
## members/helpers (active_dialog state, game_manager, the shared modal shell, log_message,
## _inflight_hiring_box) are re-routed through `host.`, exactly as SubmenuController composes them.
## No gameplay/RNG/scoring change; every action still routes through the existing GameManager
## hiring_* delegates. Ladder stays L2.
##
## What it owns (was inline in main_ui):
##   * open() -> _show_hiring_submenu() -- the pipeline panel (source -> interview -> offer -> onboard)
##   * _build_candidate_card / _build_onboarding_card -- the two reveal-gated / checklist cards
##   * _show_offer_dialog + promise toggles -- the per-candidate negotiation flow
##   * the _on_hiring_* button handlers + _hiring_action_result refresh loop
##   * update_inflight_display() -- the in-flight-hiring instrument column populator (HUD refresh)
##
## PURE VIEW (ADR-0006): reads live Researcher objects / state payload; never touches sim/RNG/turn
## loop. main_ui keeps a one-line _show_hiring_submenu() shim so SubmenuController.open("hire_staff")
## and the offer-dialog Back button reach the panel unchanged.

var host  # MainUI node (untyped: avoids a class_name coupling cycle main_ui <-> controller)


func _init(host_ref) -> void:
	host = host_ref


# --- Single entry point (SubmenuController.open("hire_staff") delegates here via the view shim) ---

func open() -> void:
	_show_hiring_submenu()


func _show_hiring_submenu():
	"""Phase-B hiring pipeline panel (source -> interview -> offer -> onboard). PURE VIEW:
	every action routes through the existing GameManager.hiring_* delegates and the panel
	reads the live Researcher objects in state.candidate_pool / state.researchers, so
	reveal-gated card data (get_card_data) shows exactly what interviewing has earned."""
	# #877: free-first moved into ModalStack (via host._present_modal_dialog) -- it pops the
	# incumbent top-first, or refuses this open when an unanswered event holds the top.

	var st = host.game_manager.state
	if st == null:
		return

	var dialog := Panel.new()
	var dsize := Vector2(580, 640)
	dialog.custom_minimum_size = dsize
	dialog.size = dsize
	var vp: Vector2 = host.get_viewport().get_visible_rect().size
	dialog.position = Vector2((vp.x - dsize.x) / 2.0, max(40.0, (vp.y - dsize.y) / 2.0))

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	dialog.add_child(margin)

	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 8)
	margin.add_child(root)

	var header := Label.new()
	header.text = "HIRING PIPELINE"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 15)
	header.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	root.add_child(header)

	var att: int = st.get_available_attention()
	var sub := Label.new()
	sub.text = "Attention available: %d   |   Money: %s   |   Reputation: %d" % [att, GameConfig.format_money(st.money), int(st.reputation)]
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.add_theme_font_size_override("font_size", 10)
	sub.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	root.add_child(sub)

	# --- SOURCE row (two channels) ---
	var source_box := HBoxContainer.new()
	source_box.add_theme_constant_override("separation", 8)
	root.add_child(source_box)

	var ad_btn := Button.new()
	ad_btn.text = "Advertise\n($8k + 3 Att)"
	ad_btn.tooltip_text = "Launch an ad campaign: candidates trickle into the pool over the coming months."
	ad_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ad_btn.focus_mode = Control.FOCUS_NONE
	ad_btn.pressed.connect(_on_hiring_advertise_pressed)
	source_box.add_child(ad_btn)

	var conn_btn := Button.new()
	conn_btn.text = "Use Connections\n(6 rep + 2 Att)"
	conn_btn.tooltip_text = "Call in a favor for one fast, pre-vetted lead (success scales with your reputation)."
	conn_btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	conn_btn.focus_mode = Control.FOCUS_NONE
	conn_btn.pressed.connect(_on_hiring_connections_pressed)
	source_box.add_child(conn_btn)

	# --- Scrollable body: candidate pool + onboarding ---
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(scroll)

	var body := VBoxContainer.new()
	body.add_theme_constant_override("separation", 6)
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(body)

	# #575: the hiring panel used to register ZERO choice buttons, so the shortcut that
	# OPENED it left every key inside it dead -- the player pressed 1/2/3 at a list of
	# candidates and nothing happened. One keyed button per candidate card, collected in
	# render order, handed to the router at the bottom of this function.
	var keyed_buttons: Array = []

	var pool_hdr := Label.new()
	pool_hdr.text = "CANDIDATE POOL (%d/%d)" % [st.candidate_pool.size(), st.MAX_CANDIDATES]
	pool_hdr.add_theme_font_size_override("font_size", 12)
	pool_hdr.add_theme_color_override("font_color", Color(0.6, 0.85, 0.6))
	body.add_child(pool_hdr)

	if st.candidate_pool.is_empty():
		var empty := Label.new()
		empty.text = "No candidates yet. Advertise or use connections to source some."
		empty.add_theme_font_size_override("font_size", 10)
		empty.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
		body.add_child(empty)
	else:
		for cand in st.candidate_pool:
			body.add_child(_build_candidate_card(cand, keyed_buttons.size(), keyed_buttons))

	var onboarding := []
	for r in st.researchers:
		if r.hire_state == Researcher.HireState.EMPLOYED and (not r.onboarded or (not r.mentoring_done and not r.mentoring_skipped)):
			onboarding.append(r)
	if not onboarding.is_empty():
		var ob_hdr := Label.new()
		ob_hdr.text = "ONBOARDING (%d)" % onboarding.size()
		ob_hdr.add_theme_font_size_override("font_size", 12)
		ob_hdr.add_theme_color_override("font_color", Color(0.85, 0.75, 0.5))
		body.add_child(ob_hdr)
		for r in onboarding:
			body.add_child(_build_onboarding_card(r))

	host._add_submenu_close_affordance(dialog)
	host.active_dialog = dialog
	host.active_dialog_buttons = keyed_buttons
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _build_candidate_card(cand, key_index: int, keyed_buttons: Array) -> PanelContainer:
	"""One pool candidate: reveal-gated card fields (get_card_data -> hidden fields render as
	the ??? placeholder) + Interview / Make Offer actions wired to the hiring_* delegates.

	#575: exactly ONE button per card carries a key -- the card's PRIMARY action (Interview
	while there is anything left to learn, otherwise Make Offer). It is appended to
	`keyed_buttons` at `key_index` whether or not it is disabled, so the key-to-card
	alignment does not shift when a candidate becomes unactionable; MainUI refuses to fire
	a disabled button, so a dead key is silent rather than wrong."""
	var c: Dictionary = cand.get_card_data()
	var panel := PanelContainer.new()
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 6)
	panel.add_child(hb)
	# Deterministic per-person portrait (DQ-15 / #758, not archetype-matched yet -- see
	# PortraitLibrary docstring); falls back to text-only if the asset is missing.
	var portrait := PortraitLibrary.make_texture_rect(cand.appearance_id)
	if portrait != null:
		hb.add_child(portrait)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 2)
	hb.add_child(vb)

	var title := Label.new()
	title.text = "%s  -  %s  [%s]" % [c["name"], c["lane"], c["hire_state"]]
	title.add_theme_font_size_override("font_size", 12)
	vb.add_child(title)

	var reveal: int = int(c.get("reveal_level", 0))
	var stats := Label.new()
	stats.add_theme_font_size_override("font_size", 9)
	stats.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))
	var skill_txt = str(c["skill_level"])
	# #1087: "$%d/yr" printed an ungrouped "$140000". Money is money everywhere.
	var comp_txt = ("%s/yr" % GameConfig.format_money(float(c["salary_expectation"]))) if (c["salary_expectation"] is float or c["salary_expectation"] is int) else str(c["salary_expectation"])
	stats.text = "Seniority: %s   Skill: %s   Comp: %s   (reveal %d/%d)" % [c["seniority_band"], skill_txt, comp_txt, reveal, Researcher.MAX_REVEAL]
	vb.add_child(stats)

	var deep := Label.new()
	deep.add_theme_font_size_override("font_size", 9)
	deep.add_theme_color_override("font_color", Color(0.6, 0.6, 0.72))
	var appetite_txt = ""
	if c["appetites"] is Dictionary:
		var parts := []
		for k in Researcher.APPETITE_KEYS:
			parts.append("%s %d%%" % [k, int(round(float(c["appetites"][k]) * 100.0))])
		appetite_txt = ", ".join(parts)
	else:
		appetite_txt = str(c["appetites"])
	var loyalty_txt = ("%d%%" % int(round(float(c["loyalty_risk"]) * 100.0))) if c["loyalty_risk"] is float else str(c["loyalty_risk"])
	# feat/quirk-skeleton: show the catalogue display name, not the raw id ("Loose Lips",
	# not "loose_lips"). Placeholder/"none" strings pass through untouched.
	var quirk_txt := str(c["quirk"])
	if QuirkCatalogue.has(quirk_txt):
		quirk_txt = QuirkCatalogue.display_name(quirk_txt)
	deep.text = "Appetites: %s\nLoyalty risk: %s   Quirk: %s" % [appetite_txt, loyalty_txt, quirk_txt]
	vb.add_child(deep)

	var status_txt := _hiring_job_status(cand.candidate_id)
	if status_txt != "":
		var jl := Label.new()
		jl.text = status_txt
		jl.add_theme_font_size_override("font_size", 9)
		jl.add_theme_color_override("font_color", Color(0.5, 0.7, 0.9))
		vb.add_child(jl)

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 6)
	vb.add_child(actions)
	var cid: String = cand.candidate_id

	var iv := Button.new()
	iv.text = "Interview (2 Att)"
	iv.focus_mode = Control.FOCUS_NONE
	iv.add_theme_font_size_override("font_size", 10)
	if cand.reveal_level >= Researcher.MAX_REVEAL:
		iv.disabled = true
		iv.tooltip_text = "Already fully interviewed."
	elif _has_hiring_job(cid, "interview"):
		iv.disabled = true
		iv.tooltip_text = "Interview already scheduled."
	else:
		iv.tooltip_text = "Interview this candidate: reveals the next card layer after a few turns."
	iv.pressed.connect(_on_hiring_interview_pressed.bind(cid))
	actions.add_child(iv)

	var offer := Button.new()
	offer.text = "Make Offer (1 Att)"
	offer.focus_mode = Control.FOCUS_NONE
	offer.add_theme_font_size_override("font_size", 10)
	if cand.hire_state != Researcher.HireState.CANDIDATE_IN_POOL:
		offer.disabled = true
		offer.tooltip_text = "Not available for an offer right now."
	elif _has_hiring_job(cid, "offer"):
		offer.disabled = true
		offer.tooltip_text = "Offer already out."
	offer.pressed.connect(_show_offer_dialog.bind(cid))
	actions.add_child(offer)

	# #575: key the card's primary action and ADVERTISE the key on that exact button, so the
	# label the player reads and the button the key fires are the same object.
	var primary: Button = iv if not iv.disabled else offer
	var prefix := DialogKeys.prefix_for(key_index)
	if prefix != "":
		primary.text = prefix + primary.text
	keyed_buttons.append(primary)

	return panel

func _build_onboarding_card(r) -> PanelContainer:
	"""One onboarding hire: checklist state, the productivity debuff made legible, and a
	button per pending step (#789: laptop / visa / systems / meet people / mentoring /
	skip). Calls hiring_onboard_step. This is the non-paused path; the accept-prompt
	window is the paused one."""
	var st = host.game_manager.state
	var status: Dictionary = st.hiring.onboarding_status(r)
	var panel := PanelContainer.new()
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 6)
	panel.add_child(hb)
	# Deterministic per-person portrait (DQ-15 / #758); see _build_candidate_card above.
	var portrait := PortraitLibrary.make_texture_rect(r.appearance_id)
	if portrait != null:
		hb.add_child(portrait)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 2)
	hb.add_child(vb)

	var title := Label.new()
	title.text = "%s  -  %s" % [r.researcher_name, r.get_specialization_name()]
	title.add_theme_font_size_override("font_size", 12)
	vb.add_child(title)

	var prod := Label.new()
	prod.add_theme_font_size_override("font_size", 9)
	if not r.onboarded:
		prod.text = "NOT PRODUCTIVE until checklist clears (currently x0.4 output)."
		prod.add_theme_color_override("font_color", Color(0.9, 0.4, 0.4))
	elif r.mentoring_skipped:
		prod.text = "Mentoring skipped: lasting x0.85 output + attrition risk."
		prod.add_theme_color_override("font_color", Color(0.9, 0.7, 0.4))
	else:
		prod.text = "Productive. Mentoring still recommended."
		prod.add_theme_color_override("font_color", Color(0.5, 0.8, 0.5))
	vb.add_child(prod)

	var check := Label.new()
	check.add_theme_font_size_override("font_size", 9)
	check.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))
	var laptop_mark = "[x]" if status["laptop_done"] else "[ ]"
	var visa_line = ""
	if status["needs_visa"]:
		var visa_mark = "[x]" if status["visa_done"] else "[ ]"
		visa_line = "   Visa %s" % visa_mark
	# #789: the hard checklist grew (laptop -> systems -> meet people, + visa).
	var sys_mark = "[x]" if status["systems_done"] else "[ ]"
	var meet_mark = "[x]" if status["meet_people_done"] else "[ ]"
	var ment_mark = "[x]" if status["mentoring_done"] else ("SKIPPED" if status["mentoring_skipped"] else "[ ]")
	check.text = "Laptop %s%s   Systems %s   Meet %s   Mentoring %s" % [laptop_mark, visa_line, sys_mark, meet_mark, ment_mark]
	vb.add_child(check)

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 6)
	vb.add_child(actions)
	var cid: String = r.candidate_id

	if not r.laptop_done:
		var b := Button.new()
		b.text = "Laptop ($3k,1Att)"
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_font_size_override("font_size", 10)
		b.pressed.connect(_on_hiring_onboard_pressed.bind(cid, "laptop"))
		actions.add_child(b)
	if status["needs_visa"] and not r.visa_done:
		var b2 := Button.new()
		b2.text = "Visa ($5k,2Att)"
		b2.focus_mode = Control.FOCUS_NONE
		b2.add_theme_font_size_override("font_size", 10)
		b2.pressed.connect(_on_hiring_onboard_pressed.bind(cid, "visa"))
		actions.add_child(b2)
	# #789 steps (Attention from the tunable HiringPipeline.ONBOARD_ATTENTION const).
	if not r.systems_done:
		var bs := Button.new()
		bs.text = "Systems (%dAtt)" % int(HiringPipeline.ONBOARD_ATTENTION["systems"])
		bs.focus_mode = Control.FOCUS_NONE
		bs.add_theme_font_size_override("font_size", 10)
		bs.disabled = not r.laptop_done
		bs.tooltip_text = "Onboard them to your systems." if r.laptop_done else "Needs their laptop first."
		bs.pressed.connect(_on_hiring_onboard_pressed.bind(cid, "systems"))
		actions.add_child(bs)
	if not r.meet_people_done:
		var bm := Button.new()
		bm.text = "Meet people (%dAtt)" % int(HiringPipeline.ONBOARD_ATTENTION["meet_people"])
		bm.focus_mode = Control.FOCUS_NONE
		bm.add_theme_font_size_override("font_size", 10)
		bm.pressed.connect(_on_hiring_onboard_pressed.bind(cid, "meet_people"))
		actions.add_child(bm)
	if not r.mentoring_done and not r.mentoring_skipped:
		var b3 := Button.new()
		b3.text = "Mentor (2Att)"
		b3.focus_mode = Control.FOCUS_NONE
		b3.add_theme_font_size_override("font_size", 10)
		b3.pressed.connect(_on_hiring_onboard_pressed.bind(cid, "mentoring"))
		actions.add_child(b3)
		var b4 := Button.new()
		b4.text = "Skip mentoring"
		b4.focus_mode = Control.FOCUS_NONE
		b4.add_theme_font_size_override("font_size", 10)
		b4.tooltip_text = "Save the Attention now, but arm a productivity debuff + early-attrition risk."
		b4.pressed.connect(_on_hiring_skip_mentoring_pressed.bind(cid))
		actions.add_child(b4)

	return panel

func _has_hiring_job(candidate_id: String, kind: String) -> bool:
	"""True if a pipeline job of `kind` is already in flight for this candidate."""
	var h = host.game_manager.state.hiring
	if h == null:
		return false
	for j in h.jobs:
		if String(j.get("candidate_id", "")) == candidate_id and String(j.get("kind", "")) == kind:
			return true
	return false

func _hiring_job_status(candidate_id: String) -> String:
	"""Short 'X in progress (resolves in ~N turns)' line for any in-flight job, else ''."""
	var h = host.game_manager.state.hiring
	if h == null:
		return ""
	var turn := int(host.game_manager.state.turn)
	for j in h.jobs:
		if String(j.get("candidate_id", "")) != candidate_id:
			continue
		var kind := String(j.get("kind", ""))
		var eta := int(j.get("resolves_on_turn", 0)) - turn
		return ">> %s in progress (resolves in ~%d turn(s))" % [kind.capitalize(), max(0, eta)]
	return ""

func _hiring_action_result(result: Dictionary, verb: String) -> void:
	"""Log a hiring delegate's result, refresh the HUD (attention/money changed), and rebuild
	the pipeline panel in place so new reveal / job state is visible immediately."""
	var ok := bool(result.get("success", false))
	var msg := String(result.get("message", ""))
	var color := "cyan" if ok else "red"
	host.log_message("[color=%s]%s: %s[/color]" % [color, verb, msg])
	host._on_game_state_updated(host.game_manager.get_game_state())
	_show_hiring_submenu()

func _on_hiring_advertise_pressed() -> void:
	_hiring_action_result(host.game_manager.hiring_advertise(), "Advertise")

func _on_hiring_connections_pressed() -> void:
	_hiring_action_result(host.game_manager.hiring_use_connections(), "Connections")

func _on_hiring_interview_pressed(candidate_id: String) -> void:
	_hiring_action_result(host.game_manager.hiring_interview(candidate_id), "Interview")

func _on_hiring_onboard_pressed(candidate_id: String, item: String) -> void:
	_hiring_action_result(host.game_manager.hiring_onboard_step(candidate_id, item), "Onboard")

func _on_hiring_skip_mentoring_pressed(candidate_id: String) -> void:
	var st = host.game_manager.state
	_hiring_action_result(st.hiring.skip_mentoring(st, candidate_id), "Onboard")

func _show_offer_dialog(candidate_id: String) -> void:
	"""Per-candidate OFFER flow: the recruiter negotiation read (band, personified SA), a cash
	field, and appetite-promise toggles that re-read the band live. Sends via hiring_offer."""
	var st = host.game_manager.state
	var cand = st.hiring.find_pool_candidate(st, candidate_id)
	if cand == null:
		return
	# #877: free-first moved into ModalStack (via host._present_modal_dialog) -- it pops the
	# incumbent top-first, or refuses this open when an unanswered event holds the top.

	var dialog := Panel.new()
	var dsize := Vector2(460, 470)
	dialog.custom_minimum_size = dsize
	dialog.size = dsize
	var vp: Vector2 = host.get_viewport().get_visible_rect().size
	dialog.position = Vector2((vp.x - dsize.x) / 2.0, max(40.0, (vp.y - dsize.y) / 2.0))

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 12)
	margin.add_theme_constant_override("margin_bottom", 12)
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	dialog.add_child(margin)

	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	margin.add_child(vb)

	var hdr := Label.new()
	hdr.text = "OFFER: %s" % cand.researcher_name
	hdr.add_theme_font_size_override("font_size", 14)
	hdr.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	vb.add_child(hdr)

	var read: Dictionary = host.game_manager.hiring_read(candidate_id, [])
	var read_lbl := Label.new()
	read_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	read_lbl.text = String(read.get("text", ""))
	read_lbl.add_theme_font_size_override("font_size", 10)
	read_lbl.add_theme_color_override("font_color", Color(0.8, 0.8, 0.6))
	vb.add_child(read_lbl)

	var band_lbl := Label.new()
	band_lbl.text = "Read band: $%d  ..  $%d" % [int(read.get("low", 0)), int(read.get("high", 0))]
	band_lbl.add_theme_font_size_override("font_size", 9)
	band_lbl.add_theme_color_override("font_color", Color(0.6, 0.6, 0.6))
	vb.add_child(band_lbl)

	# #789: make the onboarding follow-up a PREDICTABLE sink at offer time ("plan for it
	# when you make the offer"): project the hard-checklist Attention and show the current
	# crisp reserve, so the player can pre-fund the accept-prompt before ending the turn.
	var onboard_att: int = st.hiring.hard_checklist_attention(cand)
	var mentor_att: int = st.hiring.item_attention("mentoring")
	var reserve_now: int = st.month_plan.reserve_remaining() if st.month_plan != null else 0
	var onboard_lbl := Label.new()
	onboard_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	onboard_lbl.text = "If they accept: onboarding costs ~%d Attention (+%d optional mentoring). Reserve on hand: %d." % [onboard_att, mentor_att, reserve_now]
	onboard_lbl.add_theme_font_size_override("font_size", 9)
	onboard_lbl.add_theme_color_override("font_color", Color(0.7, 0.8, 0.9))
	vb.add_child(onboard_lbl)

	var cash_row := HBoxContainer.new()
	cash_row.add_theme_constant_override("separation", 8)
	vb.add_child(cash_row)
	var cash_caption := Label.new()
	cash_caption.text = "Cash offer ($/yr):"
	cash_caption.add_theme_font_size_override("font_size", 10)
	cash_row.add_child(cash_caption)
	var cash_spin := SpinBox.new()
	cash_spin.min_value = 0
	cash_spin.max_value = maxf(200000.0, float(read.get("high", 0)) * 1.5)
	cash_spin.step = 1000
	cash_spin.value = float(read.get("mid", read.get("high", 60000)))
	cash_spin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cash_row.add_child(cash_spin)

	var promise_hdr := Label.new()
	promise_hdr.text = "Promises (buy the ask down; each mints a ledger obligation on accept):"
	promise_hdr.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	promise_hdr.add_theme_font_size_override("font_size", 9)
	promise_hdr.add_theme_color_override("font_color", Color(0.7, 0.7, 0.7))
	vb.add_child(promise_hdr)

	var promise_labels := {
		"first_authorship": "First authorship (prestige)",
		"mentorship": "Mentorship (mentees)",
		"compute_budget": "Compute budget (compute)",
		"mission_charter": "Mission charter (mission purity)",
	}
	var promise_boxes := {}
	for pid in promise_labels:
		var cb := CheckBox.new()
		# Legibility (fix/promise-currency): show the future obligation each promise costs BEFORE
		# the player commits, so the ledger cost is never opaque (e.g. "owes 1 first-author paper
		# slot in ~10 turns"). Cost text is data-driven from the Ledger promise spec.
		var promise_cost: String = Ledger.appetite_promise_cost_text(pid)
		cb.text = promise_labels[pid] if promise_cost == "" else "%s -- %s" % [promise_labels[pid], promise_cost]
		cb.add_theme_font_size_override("font_size", 10)
		cb.focus_mode = Control.FOCUS_NONE
		cb.toggled.connect(_on_offer_promise_toggled.bind(candidate_id, promise_boxes, read_lbl, band_lbl))
		vb.add_child(cb)
		promise_boxes[pid] = cb

	var btn_row := HBoxContainer.new()
	btn_row.add_theme_constant_override("separation", 8)
	vb.add_child(btn_row)
	var send := Button.new()
	send.text = "Send Offer (1 Att)"
	send.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	send.focus_mode = Control.FOCUS_NONE
	send.pressed.connect(_on_hiring_send_offer_pressed.bind(candidate_id, cash_spin, promise_boxes))
	btn_row.add_child(send)
	var cancel := Button.new()
	cancel.text = "Back"
	cancel.focus_mode = Control.FOCUS_NONE
	cancel.pressed.connect(_show_hiring_submenu)
	btn_row.add_child(cancel)

	host._add_submenu_close_affordance(dialog)
	host.active_dialog = dialog
	host.active_dialog_buttons = []
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

func _selected_promises(promise_boxes: Dictionary) -> Array:
	var promises := []
	for pid in promise_boxes:
		if promise_boxes[pid].button_pressed:
			promises.append(pid)
	return promises

func _on_offer_promise_toggled(_pressed: bool, candidate_id: String, promise_boxes: Dictionary, read_lbl: Label, band_lbl: Label) -> void:
	"""Re-read the negotiation band as promises toggle, so the player sees the ask move."""
	var read: Dictionary = host.game_manager.hiring_read(candidate_id, _selected_promises(promise_boxes))
	read_lbl.text = String(read.get("text", ""))
	band_lbl.text = "Read band: $%d  ..  $%d" % [int(read.get("low", 0)), int(read.get("high", 0))]

func _on_hiring_send_offer_pressed(candidate_id: String, cash_spin: SpinBox, promise_boxes: Dictionary) -> void:
	var promises := _selected_promises(promise_boxes)
	_hiring_action_result(host.game_manager.hiring_offer(candidate_id, cash_spin.value, promises), "Offer")


func update_inflight_display(state: Dictionary) -> void:
	"""Surface in-flight hiring durations + onboarding checklists with progress, in the
	shared instrument column. VIEW-only (ADR-0006): reads the state payload only (hiring
	jobs, candidate pool, roster); never touches the sim / RNG / turn loop."""
	if host._inflight_hiring_box == null:
		return
	for child in host._inflight_hiring_box.get_children():
		child.queue_free()

	var turn_now := int(state.get("turn", 0))
	var hiring: Dictionary = state.get("hiring", {})
	var jobs: Array = hiring.get("jobs", [])
	var pool: Array = state.get("candidate_pool", [])
	var staff: Array = state.get("researchers", [])

	# candidate_id -> display name (pool candidates + employed onboarding hires)
	var name_by_id := {}
	for c in pool:
		name_by_id[String(c.get("candidate_id", ""))] = String(c.get("name", "?"))
	for r in staff:
		name_by_id[String(r.get("candidate_id", ""))] = String(r.get("name", "?"))

	# Each row: {title, done, total, unit}
	var rows: Array = []

	for job in jobs:
		var kind := String(job.get("kind", ""))
		var cid := String(job.get("candidate_id", ""))
		var who := String(name_by_id.get(cid, ""))
		var resolves := int(job.get("resolves_on_turn", 0))
		var remaining: int = max(0, resolves - turn_now)
		var total := 1
		var title := ""
		match kind:
			"interview":
				total = Balance.inum("hiring.interview.duration_ticks", 3)
				title = "Interview: %s" % (who if who != "" else "candidate")
			"offer":
				total = Balance.inum("hiring.offer.duration_ticks", 2)
				title = "Offer: %s" % (who if who != "" else "candidate")
			"connections":
				total = Balance.inum("hiring.connections.duration_ticks", 2)
				title = "Networking: sourcing a lead"
			_:
				total = max(1, remaining)
				title = kind
		var done: int = clampi(total - remaining, 0, total)
		rows.append({"title": title, "done": done, "total": total, "unit": "ticks"})

	# Onboarding hires (checklist, not tick-timed). #789 hard checklist: laptop +
	# systems + meet people [+ visa]. Legacy/direct hires default onboarded=true, so
	# only pipeline hires still cooking show here.
	for r in staff:
		if bool(r.get("onboarded", true)):
			continue
		var flags: Array = ["laptop_done", "systems_done", "meet_people_done"]
		if bool(r.get("needs_visa", false)):
			flags.append("visa_done")
		var steps_done := 0
		for f in flags:
			if bool(r.get(f, false)):
				steps_done += 1
		rows.append({"title": "Onboarding: %s" % String(r.get("name", "?")),
			"done": steps_done, "total": flags.size(), "unit": "steps"})

	if rows.is_empty():
		host._inflight_hiring_box.visible = false
		return
	host._inflight_hiring_box.visible = true

	var header := Label.new()
	header.text = "IN-FLIGHT HIRING"
	header.add_theme_font_size_override("font_size", 11)
	header.add_theme_color_override("font_color", Color(0.7, 0.85, 1.0))
	host._inflight_hiring_box.add_child(header)

	for row in rows:
		var line := HBoxContainer.new()
		line.add_theme_constant_override("separation", 6)
		var lbl := Label.new()
		lbl.text = row["title"]
		lbl.add_theme_font_size_override("font_size", 10)
		lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		line.add_child(lbl)
		var bar := ProgressBar.new()
		bar.min_value = 0
		bar.max_value = maxi(1, int(row["total"]))
		bar.value = int(row["done"])
		bar.show_percentage = false
		bar.custom_minimum_size = Vector2(60, 12)
		bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		line.add_child(bar)
		var ticks := Label.new()
		ticks.text = "%d/%d %s" % [int(row["done"]), int(row["total"]), row["unit"]]
		ticks.add_theme_font_size_override("font_size", 10)
		ticks.add_theme_color_override("font_color", Color(0.8, 0.8, 0.6))
		line.add_child(ticks)
		host._inflight_hiring_box.add_child(line)

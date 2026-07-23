extends Control
## Cold-open onboarding sequence -- #801 SHIP-NOW CORE.
##
## Diegetic on-ramp played ONCE before the player first reaches main.tscn:
##   segmented fade-up-from-black text beats  ->  a "primitive phone"
##   (lock -> 4-digit keypad -> unlock -> Bank + Messages)  ->  main game,
## seeding the first-lever nudge (GameConfig.show_first_lever_hint) that main_ui
## reads to pulse the hire button.
##
## SAFETY / SCOPE:
##  * PURE PRESENTATION. Reads no scoring state, mutates no game state, draws no RNG,
##    touches no seed -- it does NOT fork the leaderboard ladder. The only game value it
##    reads is Balance.num("starting_resources.money") for the Bank readout (a static
##    data lookup, the same value config_confirmation.gd already displays).
##  * ALL scene navigation routes through the SceneTransition autoload (never
##    change_scene_to_file directly) -- the v0.11.0 leaderboard-segfault rule.
##  * Show-once via GameConfig.should_show_intro() / mark_intro_seen()
##    (last_seen_intro_version gate; mirrors the whats-new modal pattern).
##
## Design source: docs/game-design/COLD_OPEN_SEQUENCE.md +
## docs/game-design/ONBOARDING_STORY_DESIGN.md (#801).

# ============================================================================
# TUNABLE COPY + TIMING -- Pip edits EVERYTHING player-facing here, in ONE place.
# Copy is placeholder / Pip's to finalize (see COLD_OPEN_SEQUENCE.md beats).
# ============================================================================

# The narrative beats, played top-to-bottom. kind "text" = a fade-up line; the single
# kind "phone" beat hands off to the interactive phone. duration = auto-advance hold (s).
const BEATS: Array = [
	{"kind": "text", "text": "Doom is coming.", "duration": 3.0},
	{"kind": "text", "text": "But... when am I?\nWhat can I do?  What *day* is it?", "duration": 4.0},
	{"kind": "text", "text": "*checks pockets*  --  a primitive phone!", "duration": 3.0},
	{"kind": "phone", "text": "", "duration": 0.0},
]

# --- Phone: lock screen ---
const PHONE_CLOCK: String = "07:03"
const PHONE_LOCK_PROMPT: String = "I wonder what my passcode is..."
const PHONE_LOCK_TAP_HINT: String = "[ tap to wake ]"

# --- Phone: keypad ---
const PHONE_KEYPAD_PROMPT: String = "Enter passcode"
# The Editor's benevolent hand: ANY 4 digits unlock. Phrased as good fortune.
const PHONE_UNLOCK_LUCKY: String = "Oh! how lucky!"

# --- Phone home: Bank app ---
const BANK_TITLE: String = "BANK"
const BANK_SUBTITLE: String = "Operating account -- balance"

# --- Phone home: Messages app + the Mysterious Helpful Stranger (first-lever nudge) ---
const MESSAGES_TITLE: String = "MESSAGES"
const STRANGER_NAME: String = "Mysterious Helpful Stranger"
const STRANGER_MESSAGE: String = "Hello past me! I am expository filler (for now). Get to work: hire a researcher -- it lowers doom. -- MHS"

# --- Chrome ---
const CONTINUE_LABEL: String = "Begin  >>"
# Hold-to-skip affordance (revealed on first keypress). "Conviction ring" = the radial fill.
const SKIP_AFFORDANCE_LABEL: String = "hold to skip"
const SKIP_BUTTON_LABEL: String = "SKIP"

# --- Timing dials (seconds) ---
const FADE_IN_TIME: float = 0.9
const FADE_OUT_TIME: float = 0.6
const OPENING_BLACK_HOLD: float = 0.5   # initial darkness before the first line rises
const POP_OVERSHOOT: float = 1.06       # pop-in scale overshoot (1.0 = no pop)
const LUCKY_HOLD: float = 1.3           # how long "Oh! how lucky!" holds before home
const HOLD_SKIP_SECONDS: float = 3.0    # how long the conviction ring takes to fill -> skip
const HOLD_DECAY_SECONDS: float = 0.7   # how fast the ring empties when released early

# Hero art behind the fade (imports as CompressedTexture2D). Re-pointed from the retired
# dump_october_31_2025/hero-bg (main #792 moved that dir out of godot/ to shrink the .pck)
# to a shipped in-tree background -- a wide dawn office fits the fade-up-from-black arrival.
const HERO_ART: String = "res://assets/images/backgrounds/office_wide_dawn.webp"

# ============================================================================
# End tunables. Machinery below.
# ============================================================================

var _beat_index: int = 0
var _phone_active: bool = false
var _finishing: bool = false
var _entered_digits: String = ""
var _active_tween: Tween

# Hold-to-skip state (the ONLY skip path). Revealed on first keypress; press-and-hold
# spacebar or the SKIP button fills the conviction ring over HOLD_SKIP_SECONDS; releasing
# early decays it. A completed hold-to-skip auto-flips GameConfig.play_intros off.
var _skip_revealed: bool = false
var _holding_skip: bool = false
var _hold_progress: float = 0.0

# Node refs (built in code)
var _bg: TextureRect
var _black: ColorRect
var _text_label: Label
var _phone_root: Control
var _lock_panel: Control
var _keypad_panel: Control
var _keypad_dots: Label
var _lucky_label: Label
var _home_panel: Control
var _skip_affordance: Control
var _conviction_ring: ConvictionRing


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_build_ui()
	# Begin fully black, then drive the beats.
	_black.modulate.a = 1.0
	await get_tree().create_timer(OPENING_BLACK_HOLD).timeout
	_play_next_beat()


func _build_ui() -> void:
	# Hero background (dimmed so text reads), behind a black fade overlay.
	_bg = TextureRect.new()
	_bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	_bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if ResourceLoader.exists(HERO_ART):
		_bg.texture = load(HERO_ART)
	_bg.modulate = Color(0.45, 0.45, 0.45, 1.0)  # darken the hero
	add_child(_bg)

	_black = ColorRect.new()
	_black.color = Color.BLACK
	_black.set_anchors_preset(Control.PRESET_FULL_RECT)
	_black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_black)

	# Narrative text: full-rect, centred, pivot kept centred so pop-in scales in place.
	_text_label = Label.new()
	_text_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_text_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_text_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_text_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text_label.add_theme_font_override("font", TerminalTheme.mono_font())
	_text_label.add_theme_font_size_override("font_size", 40)
	_text_label.add_theme_color_override("font_color", TerminalTheme.GREEN)
	_text_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_text_label.modulate.a = 0.0
	_text_label.resized.connect(func() -> void: _text_label.pivot_offset = _text_label.size / 2.0)
	add_child(_text_label)

	_build_skip_affordance()
	_build_phone()


func _build_skip_affordance() -> void:
	# Hidden until the FIRST keypress. Bottom-right corner. Press-and-hold spacebar or this
	# SKIP button to fill the conviction ring; on full -> skip. This is the only skip path.
	_skip_affordance = HBoxContainer.new()
	_skip_affordance.add_theme_constant_override("separation", 10)
	_skip_affordance.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	_skip_affordance.anchor_left = 1.0
	_skip_affordance.anchor_top = 1.0
	_skip_affordance.anchor_right = 1.0
	_skip_affordance.anchor_bottom = 1.0
	_skip_affordance.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	_skip_affordance.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_skip_affordance.offset_left = -260
	_skip_affordance.offset_top = -80
	_skip_affordance.offset_right = -20
	_skip_affordance.offset_bottom = -20
	_skip_affordance.alignment = BoxContainer.ALIGNMENT_END
	_skip_affordance.visible = false

	var hint := Label.new()
	hint.text = SKIP_AFFORDANCE_LABEL
	hint.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	hint.add_theme_font_override("font", TerminalTheme.mono_font())
	hint.add_theme_font_size_override("font_size", 14)
	hint.add_theme_color_override("font_color", TerminalTheme.TEXT_DIM)
	_skip_affordance.add_child(hint)

	# The conviction ring sits on the SKIP button (button hold fills it; spacebar hold too).
	var btn := Button.new()
	btn.text = SKIP_BUTTON_LABEL
	btn.custom_minimum_size = Vector2(56, 56)
	btn.add_theme_font_override("font", TerminalTheme.mono_font())
	btn.add_theme_font_size_override("font_size", 12)
	btn.button_down.connect(_start_hold_skip)
	btn.button_up.connect(_stop_hold_skip)
	_skip_affordance.add_child(btn)

	_conviction_ring = ConvictionRing.new()
	_conviction_ring.set_anchors_preset(Control.PRESET_FULL_RECT)
	_conviction_ring.mouse_filter = Control.MOUSE_FILTER_IGNORE
	btn.add_child(_conviction_ring)

	add_child(_skip_affordance)


func _build_phone() -> void:
	# The phone body: a narrow, primitive, grungy CRT-green slab, centred.
	_phone_root = PanelContainer.new()
	_phone_root.custom_minimum_size = Vector2(360, 620)
	_phone_root.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_phone_root.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_phone_root.set_anchors_preset(Control.PRESET_CENTER)
	# Anchor to centre of screen.
	_phone_root.anchor_left = 0.5
	_phone_root.anchor_top = 0.5
	_phone_root.anchor_right = 0.5
	_phone_root.anchor_bottom = 0.5
	_phone_root.offset_left = -180
	_phone_root.offset_top = -310
	_phone_root.offset_right = 180
	_phone_root.offset_bottom = 310
	TerminalTheme.style_panel(_phone_root, TerminalTheme.RULE_BRIGHT, TerminalTheme.PANEL_BG_DEEP)
	_phone_root.visible = false
	_phone_root.modulate.a = 0.0
	add_child(_phone_root)

	var body := MarginContainer.new()
	body.add_theme_constant_override("margin_left", 14)
	body.add_theme_constant_override("margin_right", 14)
	body.add_theme_constant_override("margin_top", 14)
	body.add_theme_constant_override("margin_bottom", 14)
	_phone_root.add_child(body)

	# All three phone states stack in the same slot; visibility toggles between them.
	_lock_panel = _build_lock_panel()
	_keypad_panel = _build_keypad_panel()
	_home_panel = _build_home_panel()
	body.add_child(_lock_panel)
	body.add_child(_keypad_panel)
	body.add_child(_home_panel)

	# "Oh! how lucky!" toast, overlaid centre of the phone.
	_lucky_label = Label.new()
	_lucky_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lucky_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_lucky_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_lucky_label.text = PHONE_UNLOCK_LUCKY
	_lucky_label.add_theme_font_override("font", TerminalTheme.mono_font())
	_lucky_label.add_theme_font_size_override("font_size", 32)
	_lucky_label.add_theme_color_override("font_color", TerminalTheme.AMBER)
	_lucky_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lucky_label.visible = false
	_phone_root.add_child(_lucky_label)

	_keypad_panel.visible = false
	_home_panel.visible = false


func _build_lock_panel() -> Control:
	var v := VBoxContainer.new()
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", 24)

	var clock := Label.new()
	clock.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	clock.text = PHONE_CLOCK
	clock.add_theme_font_override("font", TerminalTheme.mono_font())
	clock.add_theme_font_size_override("font_size", 54)
	clock.add_theme_color_override("font_color", TerminalTheme.TEXT)
	v.add_child(clock)

	var prompt := Label.new()
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	prompt.text = PHONE_LOCK_PROMPT
	prompt.add_theme_font_override("font", TerminalTheme.mono_font())
	prompt.add_theme_font_size_override("font_size", 16)
	prompt.add_theme_color_override("font_color", TerminalTheme.TEXT_DIM)
	v.add_child(prompt)

	var tap := Button.new()
	tap.text = PHONE_LOCK_TAP_HINT
	tap.add_theme_font_override("font", TerminalTheme.mono_font())
	tap.pressed.connect(_on_wake_phone)
	v.add_child(tap)

	return v


func _build_keypad_panel() -> Control:
	var v := VBoxContainer.new()
	v.alignment = BoxContainer.ALIGNMENT_CENTER
	v.add_theme_constant_override("separation", 16)

	var prompt := Label.new()
	prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt.text = PHONE_KEYPAD_PROMPT
	prompt.add_theme_font_override("font", TerminalTheme.mono_font())
	prompt.add_theme_font_size_override("font_size", 16)
	prompt.add_theme_color_override("font_color", TerminalTheme.TEXT_DIM)
	v.add_child(prompt)

	_keypad_dots = Label.new()
	_keypad_dots.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_keypad_dots.add_theme_font_override("font", TerminalTheme.mono_font())
	_keypad_dots.add_theme_font_size_override("font_size", 40)
	_keypad_dots.add_theme_color_override("font_color", TerminalTheme.GREEN)
	_update_dots()
	v.add_child(_keypad_dots)

	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 10)
	grid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	for n in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
		grid.add_child(_make_digit_button(n))
	# Bottom row: DEL, 0, (blank)
	grid.add_child(_make_key_button("DEL", _on_keypad_del))
	grid.add_child(_make_digit_button("0"))
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(72, 72)
	grid.add_child(spacer)
	v.add_child(grid)

	return v


func _make_digit_button(digit: String) -> Button:
	return _make_key_button(digit, func() -> void: _on_keypad_digit(digit))


func _make_key_button(label: String, cb: Callable) -> Button:
	var b := Button.new()
	b.text = label
	b.custom_minimum_size = Vector2(72, 72)
	b.add_theme_font_override("font", TerminalTheme.mono_font())
	b.add_theme_font_size_override("font_size", 24)
	b.pressed.connect(cb)
	return b


func _build_home_panel() -> Control:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)

	# --- Bank app ---
	var bank := PanelContainer.new()
	TerminalTheme.style_panel(bank, TerminalTheme.AMBER_DIM, TerminalTheme.PANEL_BG)
	var bank_v := VBoxContainer.new()
	bank.add_child(bank_v)
	var bank_title := Label.new()
	bank_title.text = BANK_TITLE
	bank_title.add_theme_font_override("font", TerminalTheme.mono_font())
	bank_title.add_theme_font_size_override("font_size", 18)
	bank_title.add_theme_color_override("font_color", TerminalTheme.AMBER)
	bank_v.add_child(bank_title)
	var bank_sub := Label.new()
	bank_sub.text = BANK_SUBTITLE
	bank_sub.add_theme_font_override("font", TerminalTheme.mono_font())
	bank_sub.add_theme_font_size_override("font_size", 13)
	bank_sub.add_theme_color_override("font_color", TerminalTheme.TEXT_DIM)
	bank_v.add_child(bank_sub)
	var bank_amount := Label.new()
	# Read-only: the same starting-money data value config_confirmation.gd displays.
	# Static Balance lookup -- no RNG, no state mutation.
	bank_amount.text = GameConfig.format_money(Balance.num("starting_resources.money", 245000.0))
	bank_amount.add_theme_font_override("font", TerminalTheme.mono_font())
	bank_amount.add_theme_font_size_override("font_size", 30)
	bank_amount.add_theme_color_override("font_color", TerminalTheme.GREEN)
	bank_v.add_child(bank_amount)
	v.add_child(bank)

	# --- Messages app (the Stranger's first-lever nudge) ---
	var msg := PanelContainer.new()
	TerminalTheme.style_panel(msg, TerminalTheme.RULE_BRIGHT, TerminalTheme.PANEL_BG)
	var msg_v := VBoxContainer.new()
	msg.add_child(msg_v)
	var msg_title := Label.new()
	msg_title.text = MESSAGES_TITLE
	msg_title.add_theme_font_override("font", TerminalTheme.mono_font())
	msg_title.add_theme_font_size_override("font_size", 18)
	msg_title.add_theme_color_override("font_color", TerminalTheme.GREEN)
	msg_v.add_child(msg_title)
	var sender := Label.new()
	sender.text = STRANGER_NAME
	sender.add_theme_font_override("font", TerminalTheme.mono_font())
	sender.add_theme_font_size_override("font_size", 14)
	sender.add_theme_color_override("font_color", TerminalTheme.AMBER)
	msg_v.add_child(sender)
	var body := Label.new()
	body.text = STRANGER_MESSAGE
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size = Vector2(300, 0)
	body.add_theme_font_override("font", TerminalTheme.mono_font())
	body.add_theme_font_size_override("font_size", 15)
	body.add_theme_color_override("font_color", TerminalTheme.TEXT)
	msg_v.add_child(body)
	v.add_child(msg)

	# --- Continue into the game ---
	var cont := Button.new()
	cont.text = CONTINUE_LABEL
	cont.add_theme_font_override("font", TerminalTheme.mono_font())
	cont.add_theme_font_size_override("font_size", 20)
	cont.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	cont.pressed.connect(func() -> void: _finish(false))
	v.add_child(cont)

	return v


# ---------------------------------------------------------------------------
# Beat driver
# ---------------------------------------------------------------------------
func _play_next_beat() -> void:
	if _finishing:
		return
	if _beat_index >= BEATS.size():
		_finish(false)
		return
	var beat: Dictionary = BEATS[_beat_index]
	_beat_index += 1
	match beat.get("kind", "text"):
		"phone":
			_show_phone()
		_:
			_play_text_beat(beat)


func _play_text_beat(beat: Dictionary) -> void:
	_text_label.text = str(beat.get("text", ""))
	_text_label.modulate.a = 0.0
	_text_label.scale = Vector2(0.94, 0.94)
	var dur: float = float(beat.get("duration", 3.0))
	_kill_active_tween()
	_active_tween = create_tween()
	# Fade the opening black away as the first line rises, then just fade text per-beat.
	if _black.modulate.a > 0.0:
		_active_tween.parallel().tween_property(_black, "modulate:a", 0.0, FADE_IN_TIME)
	# Pop-in: fade + overshoot scale (parallel), hold, fade out.
	_active_tween.parallel().tween_property(_text_label, "modulate:a", 1.0, FADE_IN_TIME)
	_active_tween.parallel().tween_property(_text_label, "scale", Vector2(POP_OVERSHOOT, POP_OVERSHOOT), FADE_IN_TIME * 0.6) \
		.set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	_active_tween.tween_property(_text_label, "scale", Vector2.ONE, 0.15)
	_active_tween.tween_interval(dur)
	_active_tween.tween_property(_text_label, "modulate:a", 0.0, FADE_OUT_TIME)
	_active_tween.tween_callback(_play_next_beat)


func _show_phone() -> void:
	_phone_active = true
	_kill_active_tween()
	# Fade any lingering text out and the phone in.
	_active_tween = create_tween()
	_active_tween.tween_property(_text_label, "modulate:a", 0.0, FADE_OUT_TIME * 0.5)
	_active_tween.tween_callback(func() -> void: _phone_root.visible = true)
	_active_tween.tween_property(_phone_root, "modulate:a", 1.0, FADE_IN_TIME)


func _on_wake_phone() -> void:
	_lock_panel.visible = false
	_keypad_panel.visible = true
	_update_dots()


func _on_keypad_digit(digit: String) -> void:
	if _entered_digits.length() >= 4:
		return
	_entered_digits += digit
	_update_dots()
	if _entered_digits.length() >= 4:
		# Any 4 digits unlock (Editor's benevolent hand).
		await get_tree().create_timer(0.15).timeout
		_on_unlock()


func _on_keypad_del() -> void:
	if _entered_digits.length() > 0:
		_entered_digits = _entered_digits.substr(0, _entered_digits.length() - 1)
		_update_dots()


func _update_dots() -> void:
	if _keypad_dots == null:
		return
	var filled := _entered_digits.length()
	var slots: Array = []
	for i in range(4):
		slots.append("*" if i < filled else "_")
	_keypad_dots.text = "  ".join(slots)


func _on_unlock() -> void:
	_keypad_panel.visible = false
	# "Oh! how lucky!" toast, then reveal the home screen.
	_lucky_label.visible = true
	_lucky_label.modulate.a = 0.0
	_kill_active_tween()
	_active_tween = create_tween()
	_active_tween.tween_property(_lucky_label, "modulate:a", 1.0, 0.4)
	_active_tween.tween_interval(LUCKY_HOLD)
	_active_tween.tween_property(_lucky_label, "modulate:a", 0.0, 0.4)
	_active_tween.tween_callback(func() -> void:
		_lucky_label.visible = false
		_home_panel.visible = true)


# ---------------------------------------------------------------------------
# Input: click = ADVANCE beat; keys reveal + drive the hold-to-skip
# ---------------------------------------------------------------------------
func _input(event: InputEvent) -> void:
	if _finishing:
		return
	# ANY keypress during the cinematic reveals the hold-to-skip affordance.
	if event is InputEventKey and event.pressed and not event.echo:
		_reveal_skip_affordance()
		# Spacebar is the keyboard hold-to-skip: press to begin filling, release to cancel.
		if event.keycode == KEY_SPACE:
			get_viewport().set_input_as_handled()
			_start_hold_skip()
			return
	elif event is InputEventKey and not event.pressed and event.keycode == KEY_SPACE:
		# Spacebar released before the ring filled -> cancel (it decays).
		get_viewport().set_input_as_handled()
		_stop_hold_skip()


func _unhandled_input(event: InputEvent) -> void:
	# Click = ADVANCE to the next beat (NOT skip). Only during the NARRATIVE: once the phone
	# is active, clicks belong to the keypad / continue button (they're consumed at the gui
	# layer, so they never reach _unhandled_input anyway). Clicks on the SKIP button are also
	# gui-consumed, so a stray click here can't be the skip button.
	if _finishing or _phone_active:
		return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		get_viewport().set_input_as_handled()
		_advance_beat_now()


func _reveal_skip_affordance() -> void:
	if _skip_revealed:
		return
	_skip_revealed = true
	if _skip_affordance:
		_skip_affordance.visible = true


func _advance_beat_now() -> void:
	# Skip the CURRENT beat's remaining fade/hold and jump to the next beat immediately.
	if _finishing or _phone_active:
		return
	_kill_active_tween()
	_play_next_beat()


# ---------------------------------------------------------------------------
# Hold-to-skip (conviction ring): press-and-hold fills; release decays; full -> skip
# ---------------------------------------------------------------------------
func _start_hold_skip() -> void:
	if _finishing:
		return
	_reveal_skip_affordance()
	_holding_skip = true


func _stop_hold_skip() -> void:
	_holding_skip = false


func _process(delta: float) -> void:
	if _finishing:
		return
	if _holding_skip:
		_hold_progress += delta / HOLD_SKIP_SECONDS
		if _hold_progress >= 1.0:
			_hold_progress = 1.0
			_finish(true, true)  # completed hold-to-skip auto-flips play_intros off
	elif _hold_progress > 0.0:
		_hold_progress = max(0.0, _hold_progress - delta / HOLD_DECAY_SECONDS)
	if _conviction_ring:
		_conviction_ring.set_progress(_hold_progress)


# ---------------------------------------------------------------------------
# Finish
# ---------------------------------------------------------------------------
func _finish(skipped: bool, via_hold_skip: bool = false) -> void:
	if _finishing:
		return
	_finishing = true
	_holding_skip = false
	_kill_active_tween()
	# Seed the first-lever nudge for main_ui (pulse the hire button). Set on BOTH
	# complete and skip -- a first-time player benefits from the pointer either way.
	GameConfig.show_first_lever_hint = true
	# Auto-flip the story-intro preference off ONLY on an explicit hold-to-skip (the "I skip
	# intros" signal). Watching to completion does NOT flip it. Reversible in settings.
	if via_hold_skip:
		GameConfig.play_intros = false
		GameConfig.save_config()
		print("[ColdOpen] hold-to-skip completed -> play_intros auto-flipped OFF")
	# Show-once: a skip counts as seen (same as the whats-new modal).
	GameConfig.mark_intro_seen()
	print("[ColdOpen] finishing (skipped=%s, via_hold_skip=%s) -> main" % [skipped, via_hold_skip])
	SceneTransition.go_to("res://scenes/main.tscn")


func _kill_active_tween() -> void:
	if _active_tween != null and _active_tween.is_valid():
		_active_tween.kill()
	_active_tween = null


# ---------------------------------------------------------------------------
# Conviction ring: a radial fill drawn over the SKIP button (0..1 progress).
# ---------------------------------------------------------------------------
class ConvictionRing:
	extends Control

	var _progress: float = 0.0

	func set_progress(p: float) -> void:
		var clamped: float = clampf(p, 0.0, 1.0)
		if is_equal_approx(clamped, _progress):
			return
		_progress = clamped
		queue_redraw()

	func _draw() -> void:
		var centre: Vector2 = size / 2.0
		var radius: float = min(size.x, size.y) * 0.5 - 3.0
		if radius <= 0.0:
			return
		# Dim background ring (the track).
		draw_arc(centre, radius, 0.0, TAU, 48, TerminalTheme.RULE, 3.0, true)
		# Filled arc, clockwise from 12 o'clock, proportional to conviction.
		if _progress > 0.0:
			var start: float = -PI / 2.0
			draw_arc(centre, radius, start, start + TAU * _progress, 48, TerminalTheme.AMBER, 4.0, true)

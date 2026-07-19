extends CanvasLayer
class_name FanfarePopup
## Reusable Civ-style "fade-up reveal" popup for momentous events / unlocks (#578).
##
## Instead of a new action button silently appearing (and causing layout jank), call
## FanfarePopup.show_fanfare(title, body, image_path) to fade a centred card up over the
## screen: a title, flavour body text, an OPTIONAL image slot, and a Continue/dismiss.
##
## The image slot is optional and works text-only for now; hero banners from
## art_prompts/hero_banners.yaml will drop into `image_path` later once generated.
##
## Example:
##   FanfarePopup.show_fanfare(
##       "STRATEGIC MOVES UNLOCKED",
##       "Your reputation now opens doors to high-stakes plays...",
##       "")  # or "res://assets/banners/strategic.png" later
##
## The whole tree is built in code so the .tscn stays a trivial one-node asset (no fragile
## node-path wiring); dismiss is via the focused Continue button (Enter/Space) or a backdrop
## click, so it never fights the main UI's global key handling.

var _fade: Control          # everything under here is faded/tinted as one
var _backdrop: ColorRect    # full-viewport dimming behind the card (blocks the game visually)
var _card: Panel            # the centred card that also slides up
var _image: TextureRect
var _title_label: Label
var _body_label: Label
var _continue_btn: Button
var _dismissing: bool = false
var _built: bool = false


## Static entry point. `parent` defaults to the scene-tree root so callers can fire-and-forget.
static func show_fanfare(title: String, body: String, image_path: String = "", parent: Node = null) -> FanfarePopup:
	var popup: FanfarePopup = preload("res://scenes/ui/fanfare_popup.tscn").instantiate()
	var host: Node = parent
	if host == null:
		var loop := Engine.get_main_loop()
		if loop is SceneTree:
			host = (loop as SceneTree).root
	if host == null:
		push_error("[FanfarePopup] no host node to attach to; aborting")
		popup.free()
		return null
	host.add_child(popup)
	popup.present(title, body, image_path)
	return popup


func _ready() -> void:
	layer = 128  # above any in-scene CanvasLayers / the game UI
	_build()


func _build() -> void:
	if _built:
		return
	_built = true

	_fade = Control.new()
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_STOP  # eat clicks so the game underneath doesn't react
	add_child(_fade)

	# Dimming backdrop: a near-opaque black overlay that covers the whole viewport and
	# sits behind the card, so background event triggers can't animate through it (#603).
	# Fades in/out with the card (via _fade.modulate) for the Civ-II "party arrives" reveal.
	# Kept a touch below fully opaque so it darkens rather than fully hides the game.
	_backdrop = ColorRect.new()
	_backdrop.name = "Backdrop"
	_backdrop.color = Color(0.0, 0.0, 0.0, 0.8)
	_backdrop.set_anchors_preset(Control.PRESET_FULL_RECT)
	_backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
	_backdrop.gui_input.connect(_on_backdrop_input)
	_fade.add_child(_backdrop)

	# The card. Positioned/animated manually (not in a container) so it can slide up.
	_card = Panel.new()
	_card.custom_minimum_size = Vector2(460, 0)
	var card_style := StyleBoxFlat.new()
	card_style.bg_color = Color(0.10, 0.12, 0.16, 0.98)
	card_style.set_border_width_all(2)
	card_style.border_color = Color(0.55, 0.68, 0.60, 1.0)
	card_style.set_corner_radius_all(10)
	card_style.content_margin_left = 26
	card_style.content_margin_right = 26
	card_style.content_margin_top = 22
	card_style.content_margin_bottom = 22
	_card.add_theme_stylebox_override("panel", card_style)
	_fade.add_child(_card)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	vbox.add_theme_constant_override("separation", 14)
	_card.add_child(vbox)

	# Optional image slot (hero banner drops in here later).
	_image = TextureRect.new()
	_image.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	_image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_image.custom_minimum_size = Vector2(408, 0)
	_image.visible = false
	vbox.add_child(_image)

	_title_label = Label.new()
	_title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_title_label.add_theme_font_size_override("font_size", 22)
	_title_label.add_theme_color_override("font_color", Color(0.95, 0.88, 0.62))
	vbox.add_child(_title_label)

	_body_label = Label.new()
	_body_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_body_label.custom_minimum_size = Vector2(408, 0)
	_body_label.add_theme_font_size_override("font_size", 14)
	_body_label.add_theme_color_override("font_color", Color(0.85, 0.87, 0.9))
	vbox.add_child(_body_label)

	_continue_btn = Button.new()
	_continue_btn.text = "Continue"
	_continue_btn.custom_minimum_size = Vector2(0, 34)
	_continue_btn.pressed.connect(_dismiss)
	vbox.add_child(_continue_btn)


## Populate content and play the fade-up reveal. Safe to call once, right after instancing.
func present(title: String, body: String, image_path: String = "") -> void:
	_build()
	_title_label.text = title
	_body_label.text = body
	if image_path != "" and ResourceLoader.exists(image_path):
		_image.texture = load(image_path)
		_image.visible = true
	else:
		_image.visible = false

	# Wait for the card to lay out so we know its size, then centre + animate.
	await get_tree().process_frame
	var vp := get_viewport().get_visible_rect().size
	var final_pos := (vp - _card.size) * 0.5
	final_pos.y = maxf(final_pos.y, 20.0)
	_card.position = final_pos + Vector2(0, 30)  # start a touch lower, then rise
	_fade.modulate.a = 0.0

	var tw := create_tween().set_parallel(true).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(_fade, "modulate:a", 1.0, 0.5)  # backdrop + card fade in together (~0.5s)
	tw.tween_property(_card, "position", final_pos, 0.5)

	if is_instance_valid(_continue_btn):
		_continue_btn.grab_focus()


func _on_backdrop_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		_dismiss()


func _unhandled_input(event: InputEvent) -> void:
	# Escape contract (fix/ui-no-dead-ends): Esc dismisses the fanfare, like the backdrop
	# click and the Continue button -- so it is never a dead-end on the keyboard path.
	if event.is_action_pressed("ui_cancel"):
		_dismiss()
		get_viewport().set_input_as_handled()


func _dismiss() -> void:
	if _dismissing:
		return
	_dismissing = true
	var tw := create_tween()
	tw.tween_property(_fade, "modulate:a", 0.0, 0.22)
	tw.tween_callback(queue_free)

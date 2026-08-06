extends Control
## Credits screen -- the one place in the product where contributors are named.
##
## Everything here is rendered from res://data/credits.json, which is GENERATED
## from CREDITS.md. Do not add a hardcoded name to this file; add it to
## CREDITS.md and run scripts/generate_credits.py.
##
## The cats go FIRST, deliberately. Eight people gave their cat's photo, one of
## the eight appears in every run, and until now the product had nowhere to say
## thank you. It is also the section a person would screenshot, which is the
## honest reason it is at the top rather than filed under "assets".

const CAT_IMAGES_PATH := "res://assets/cats/simple/"
const CAT_TILE_SIZE := Vector2(150, 150)

## Website link policy (docs/copy/README.md): the game NEVER depends on the
## website. This is the site ROOT, which exists today (UpdateCheck already reads
## https://pdoom1.com/data/version.json), not a deep link to a "meet the cats"
## page that may or may not be built. A hardcoded deep link would make this
## screen quietly wrong the moment the website reorganised, and the game has no
## way to find that out.
const WEBSITE_URL := "https://pdoom1.com"

@onready var content: VBoxContainer = $Panel/VBox/ContentScroll/Content
@onready var back_button: Button = $Panel/VBox/Footer/BackButton
@onready var website_button: Button = $Panel/VBox/Footer/WebsiteButton


func _ready() -> void:
	back_button.pressed.connect(_on_back_pressed)
	website_button.pressed.connect(_on_website_pressed)
	website_button.tooltip_text = "Opens the project website in your browser"
	_build()
	back_button.grab_focus()
	print("[CreditsScreen] Rendered %d cats, %d sections" % [
		CreditsData.cats().size(), CreditsData.sections().size()
	])


func _build() -> void:
	for child in content.get_children():
		child.queue_free()
	_build_cats()
	for section in CreditsData.sections():
		if typeof(section) == TYPE_DICTIONARY:
			_build_section(section)


func _build_cats() -> void:
	var cats: Array = CreditsData.cats()
	if cats.is_empty():
		return
	_add_heading("THE CATS")
	_add_paragraph(
		"One of these cats is in your office every run, picked at random."
		+ " They are real cats, contributed by their people with permission."
	)
	var flow := HFlowContainer.new()
	flow.add_theme_constant_override("h_separation", 18)
	flow.add_theme_constant_override("v_separation", 14)
	content.add_child(flow)
	for entry in cats:
		if typeof(entry) == TYPE_DICTIONARY:
			flow.add_child(_build_cat_card(entry))


func _build_cat_card(entry: Dictionary) -> Control:
	var card := VBoxContainer.new()
	card.add_theme_constant_override("separation", 2)

	var frame := PanelContainer.new()
	frame.custom_minimum_size = CAT_TILE_SIZE
	var picture := TextureRect.new()
	picture.custom_minimum_size = CAT_TILE_SIZE
	picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	picture.texture = _load_cat_texture(str(entry.get("asset", "")))
	frame.add_child(picture)
	card.add_child(frame)

	var name_label := Label.new()
	name_label.text = str(entry.get("name", ""))
	name_label.custom_minimum_size.x = CAT_TILE_SIZE.x
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 17)
	card.add_child(name_label)

	# An unconfirmed credit form renders as NOTHING, never as a placeholder
	# string. generate_credits.py blanks the field; this is the second half of
	# that contract.
	var credit := str(entry.get("credited_to", ""))
	if credit != "":
		var credit_label := Label.new()
		credit_label.text = "photo by " + credit
		credit_label.custom_minimum_size.x = CAT_TILE_SIZE.x
		credit_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		credit_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		credit_label.add_theme_font_size_override("font_size", 14)
		credit_label.add_theme_color_override("font_color", Color(0.70, 0.78, 0.86, 1.0))
		card.add_child(credit_label)

	return card


## Same import-system lesson as office_cat.gd (#796): ResourceLoader.exists(),
## never FileAccess.file_exists(), because the exported .pck holds the imported
## .ctex and not the source .jpg. A missing cat degrades to a muted swatch, not
## to the engine's magenta checkerboard.
func _load_cat_texture(asset: String) -> Texture2D:
	if asset != "":
		var path := CAT_IMAGES_PATH + asset
		if ResourceLoader.exists(path):
			var texture := load(path) as Texture2D
			if texture != null:
				return texture
		push_warning("[CreditsScreen] cat image not found: " + path)
	var image := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	image.fill(Color(0.16, 0.17, 0.20, 1.0))
	return ImageTexture.create_from_image(image)


func _build_section(section: Dictionary) -> void:
	var entries: Array = section.get("entries", [])
	if entries.is_empty():
		return
	_add_heading(str(section.get("title", "")).to_upper())
	for entry in entries:
		if typeof(entry) != TYPE_DICTIONARY:
			continue
		var text := str(entry.get("text", ""))
		if text == "":
			continue
		if str(entry.get("kind", "")) == "item":
			_add_paragraph("  >>  " + text)
		else:
			_add_paragraph(text)


func _add_heading(text: String) -> void:
	var spacer := Control.new()
	spacer.custom_minimum_size.y = 10
	content.add_child(spacer)
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 24)
	label.add_theme_color_override("font_color", Color(0.91, 0.64, 0.24, 1.0))
	content.add_child(label)
	content.add_child(HSeparator.new())


func _add_paragraph(text: String) -> void:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.custom_minimum_size.x = 960
	label.add_theme_font_size_override("font_size", 17)
	content.add_child(label)


func _on_back_pressed() -> void:
	SceneTransition.go_to("res://scenes/welcome.tscn")


func _on_website_pressed() -> void:
	OS.shell_open(WEBSITE_URL)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_pressed()
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_W:
			_on_website_pressed()
			get_viewport().set_input_as_handled()

extends Control
## Office Cat Display System - Simplified
##
## Displays random office cat from available cat images.
## For now, just shows a single static cat image (no doom variants).
## Future: Contributor system with doom-level variants.

@onready var cat_texture: TextureRect = $VBox/CatPanel/CatTexture
@onready var contributor_label: Label = $VBox/ContributorLabel
@onready var doom_meter_container: Control = $VBox/DoomMeterContainer

const CAT_IMAGES_PATH = "res://assets/cats/simple/"
const CAT_NAMES = {
	"web-arwen.jpg": "Arwen",
	"web-arwen-chuck.jpg": "Arwen & Chuck",
	"web-chucky.jpg": "Chucky",
	"web-doom-cat.jpg": "Doom Cat",
	"web-luna.jpg": "Luna",
	"web-mando.jpg": "Mando",
	"web-missy.jpg": "Missy",
	"web-nigel.jpg": "Nigel"
}

var current_cat_image: String = ""
var current_cat_name: String = "Office Cat"

func _ready():
	# Select a random cat and display it
	select_random_cat()
	visible = true

## Select and display a random cat
func select_random_cat() -> void:
	var cat_files = CAT_NAMES.keys()
	if cat_files.is_empty():
		push_warning("No cat images available")
		use_placeholder()
		return

	# Pick a random cat
	var random_index = randi() % cat_files.size()
	var cat_file = cat_files[random_index]
	current_cat_name = CAT_NAMES[cat_file]

	# Load and display
	var image_path = CAT_IMAGES_PATH + cat_file
	set_cat_image(image_path)
	contributor_label.text = current_cat_name

## Update doom level (currently does nothing, kept for compatibility)
## @param doom_percentage: Current doom level (0.0 to 1.0)
func update_doom_level(doom_percentage: float) -> void:
	pass  # No doom variants yet

## Set cat image from path
func set_cat_image(image_path: String) -> void:
	if image_path == current_cat_image:
		return  # No change needed

	current_cat_image = image_path

	# Load texture
	if FileAccess.file_exists(image_path):
		var texture = load(image_path) as Texture2D
		if texture:
			cat_texture.texture = texture
			print("[OfficeCat] Loaded cat image: %s (%s)" % [current_cat_name, image_path])
		else:
			push_warning("Failed to load cat texture: " + image_path)
			use_placeholder()
	else:
		push_warning("Cat image not found: " + image_path)
		use_placeholder()

## Use placeholder when image is missing
func use_placeholder() -> void:
	# Create a simple colored rectangle as placeholder
	var placeholder_texture = PlaceholderTexture2D.new()
	placeholder_texture.size = Vector2(256, 256)
	cat_texture.texture = placeholder_texture

## Cycle to next cat (for future feature: click to cycle)
func cycle_contributor() -> void:
	select_random_cat()

## Get current cat info (for tooltips, etc.)
func get_current_contributor_info() -> String:
	return "%s\n\nOffice Cat - Keeping morale high!\n\nClick to see another cat!" % current_cat_name

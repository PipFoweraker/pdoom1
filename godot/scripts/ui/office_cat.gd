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

	# Load texture.
	#
	# MUST be ResourceLoader.exists(), NEVER FileAccess.file_exists() (issue #796).
	# Godot's exporter does not put the source .jpg in the .pck at all -- it ships
	# only the imported texture (.godot/imported/<name>.jpg-<md5>.ctex) plus the
	# .import metadata that points at it. FileAccess reads the packed file table
	# literally, so file_exists("res://assets/cats/simple/web-arwen.jpg") is FALSE
	# for EVERY cat in a shipped build even though the artwork is right there.
	# ResourceLoader goes through the import system and resolves the .ctex.
	# The rest of this project already uses ResourceLoader.exists() for exactly
	# this (music_manager, portrait_library, resource_bar, fanfare_popup, ...);
	# office_cat was the last holdout.
	if ResourceLoader.exists(image_path):
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
##
## Defence in depth for #796. The old body assigned a PlaceholderTexture2D, which
## is not a real texture -- the renderer substitutes its missing-texture fill, and
## what the player saw on screen was a magenta/black checkerboard the size of the
## cat panel. That is the single loudest "this software is broken" signal a game
## can show, and it was showing for a purely cosmetic optional asset.
##
## If a cat ever goes missing again, fail QUIETLY: a muted swatch that reads as
## "no photo" rather than as a rendering fault. The push_warning() above is where
## a developer is meant to learn about it, not the player's screen.
func use_placeholder() -> void:
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	img.fill(Color(0.16, 0.17, 0.20, 1.0))
	cat_texture.texture = ImageTexture.create_from_image(img)

## Cycle to next cat (for future feature: click to cycle)
func cycle_contributor() -> void:
	select_random_cat()

## Get current cat info (for tooltips, etc.)
func get_current_contributor_info() -> String:
	return "%s\n\nOffice Cat - Keeping morale high!\n\nClick to see another cat!" % current_cat_name

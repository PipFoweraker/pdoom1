extends Control
## Office Cat Display System
##
## Displays contributor cats with doom-level variants.
## Cats transition between 5 states based on current doom level.
##
## @tutorial: See docs/CONTRIBUTOR_SYSTEM.md for contributor recognition program

@onready var cat_texture: TextureRect = $VBox/CatPanel/CatTexture
@onready var contributor_label: Label = $VBox/ContributorLabel
@onready var doom_meter_container: Control = $VBox/DoomMeterContainer

var contributor_manager: ContributorManager
var current_doom_percentage: float = 0.0
var current_cat_image: String = ""

func _ready():
	# Initialize contributor manager
	contributor_manager = ContributorManager.new()
	add_child(contributor_manager)

	# Connect signals
	contributor_manager.contributors_loaded.connect(_on_contributors_loaded)
	contributor_manager.contributor_changed.connect(_on_contributor_changed)

	# Hide by default until contributors are loaded
	visible = false

## Called when contributors are loaded
func _on_contributors_loaded(count: int):
	if count > 0:
		# Select a random contributor to display
		contributor_manager.select_random_contributor()
		visible = true
	else:
		# No contributors, show default cat
		var default_image = contributor_manager.get_default_cat_image(current_doom_percentage)
		set_cat_image(default_image)
		contributor_label.text = "Office Cat"
		visible = true

## Called when contributor changes
func _on_contributor_changed(contributor: Dictionary):
	if contributor.is_empty():
		return

	# Update contributor label
	var name = contributor.get("name", "Unknown Contributor")
	var contribution_types = contributor.get("contribution_types", [])
	var type_str = ", ".join(contribution_types)
	contributor_label.text = "%s - %s" % [name, type_str]

	# Update cat image for current doom level
	update_cat_for_doom_level(current_doom_percentage)

## Update doom level and cat image
## @param doom_percentage: Current doom level (0.0 to 1.0)
func update_doom_level(doom_percentage: float) -> void:
	current_doom_percentage = doom_percentage
	update_cat_for_doom_level(doom_percentage)

## Update cat image based on doom level
func update_cat_for_doom_level(doom_percentage: float) -> void:
	var image_path = contributor_manager.get_cat_image_for_doom_level(doom_percentage)
	set_cat_image(image_path)

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

## Cycle to next contributor (for future feature: click to cycle)
func cycle_contributor() -> void:
	if contributor_manager.get_contributor_count() > 1:
		contributor_manager.select_random_contributor()

## Get current contributor info (for tooltips, etc.)
func get_current_contributor_info() -> String:
	var contributor = contributor_manager.get_current_contributor()
	if contributor.is_empty():
		return "Default Office Cat\n\nContribute to PDoom to get your cat featured here!"

	var name = contributor.get("name", "Unknown")
	var cat_name = contributor.get("cat_name", "Office Cat")
	var types = contributor.get("contribution_types", [])
	var type_str = ", ".join(types)

	return "%s's cat: %s\nContributions: %s\n\nClick to see another contributor!" % [name, cat_name, type_str]

extends HBoxContainer
## Resource Bar - Visual display with icon, label, and optional progress bar

@export var resource_name: String = "Resource"
@export var resource_key: String = "resource"
@export var show_icon: bool = true
@export var show_progress_bar: bool = false
@export var max_value: float = 100.0
@export var format_string: String = "%.0f"

var icon_texture: TextureRect
var name_label: Label
var value_label: Label
var progress_bar: ProgressBar

var current_value: float = 0.0

func _ready():
	custom_minimum_size = Vector2(200, 40)
	add_theme_constant_override("separation", 10)

	# Create icon (if enabled)
	if show_icon:
		icon_texture = TextureRect.new()
		icon_texture.custom_minimum_size = Vector2(32, 32)
		icon_texture.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		icon_texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		add_child(icon_texture)

		# Try to load icon from theme
		var icon_path = ThemeManager.get_asset("icon_" + resource_key)
		if icon_path != "" and ResourceLoader.exists(icon_path):
			icon_texture.texture = load(icon_path)

	# Create labels container
	var labels_container = VBoxContainer.new()
	labels_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(labels_container)

	# Resource name label
	name_label = Label.new()
	name_label.text = resource_name
	ThemeManager.apply_label_style(name_label, "small")
	name_label.add_theme_color_override("font_color", ThemeManager.get_color("text_dim"))
	labels_container.add_child(name_label)

	# Value display (with optional progress bar)
	if show_progress_bar:
		var bar_container = HBoxContainer.new()
		bar_container.add_theme_constant_override("separation", 5)

		progress_bar = ProgressBar.new()
		progress_bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		progress_bar.max_value = max_value
		progress_bar.show_percentage = false
		bar_container.add_child(progress_bar)

		value_label = Label.new()
		value_label.custom_minimum_size = Vector2(60, 0)
		ThemeManager.apply_label_style(value_label, "body")
		bar_container.add_child(value_label)

		labels_container.add_child(bar_container)
	else:
		value_label = Label.new()
		ThemeManager.apply_label_style(value_label, "body")
		labels_container.add_child(value_label)

	# Connect to theme changes
	ThemeManager.theme_changed.connect(_on_theme_changed)

	_update_display()

func _on_theme_changed(theme_name: String):
	if name_label:
		ThemeManager.apply_label_style(name_label, "small")
		name_label.add_theme_color_override("font_color", ThemeManager.get_color("text_dim"))

	if value_label:
		ThemeManager.apply_label_style(value_label, "body")

	_update_display()

## Set the resource value
func set_value(value: float):
	current_value = value

	if progress_bar:
		progress_bar.value = value

	_update_display()

## Update the visual display
func _update_display():
	if not value_label:
		return

	# Format the value
	var formatted = format_string % current_value

	# Add special formatting based on resource type
	match resource_key:
		"money":
			formatted = "$" + formatted
		"doom":
			formatted = formatted + "%"
			# Color-code doom
			if value_label:
				value_label.add_theme_color_override("font_color", ThemeManager.get_doom_color(current_value))
		"research", "compute":
			# Show decimal
			formatted = format_string % current_value

	value_label.text = formatted

## Set the maximum value for progress bar
func set_max(max_val: float):
	max_value = max_val
	if progress_bar:
		progress_bar.max_value = max_val

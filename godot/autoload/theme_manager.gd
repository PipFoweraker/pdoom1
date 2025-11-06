extends Node
## Theme Manager - Centralized visual theming system
## Supports multiple themes, easy asset swapping, consistent styling

# Current theme
var current_theme: String = "default"
var themes: Dictionary = {}

# Theme data structure
class ThemeData:
	var name: String
	var display_name: String

	# Colors
	var colors: Dictionary = {
		"background": Color(0.15, 0.15, 0.15),
		"panel": Color(0.2, 0.2, 0.25),
		"panel_dark": Color(0.1, 0.1, 0.15),
		"text": Color(0.95, 0.95, 0.95),
		"text_dim": Color(0.6, 0.6, 0.6),
		"accent": Color(0.3, 0.5, 0.8),
		"accent_hover": Color(0.4, 0.6, 0.9),
		"accent_pressed": Color(0.2, 0.4, 0.7),
		"success": Color(0.2, 0.8, 0.3),
		"warning": Color(0.9, 0.7, 0.2),
		"error": Color(0.9, 0.3, 0.2),
		"doom_low": Color(0.3, 0.8, 0.3),
		"doom_medium": Color(0.9, 0.7, 0.2),
		"doom_high": Color(0.9, 0.3, 0.2),
		"doom_critical": Color(0.7, 0.1, 0.1),
	}

	# Fonts
	var fonts: Dictionary = {
		"title_size": 32,
		"header_size": 24,
		"body_size": 16,
		"small_size": 12,
	}

	# Spacing
	var spacing: Dictionary = {
		"margin": 20,
		"padding": 10,
		"gap": 5,
		"button_height": 50,
	}

	# UI Styles
	var styles: Dictionary = {
		"button_corner_radius": 4,
		"panel_corner_radius": 8,
		"border_width": 2,
	}

	# Asset paths
	var assets: Dictionary = {
		# Cat assets
		"cat": "res://assets/images/office_cat.png",
		"cat_closeup": "res://assets/images/misc/cat_closeup.png",
		"cat_icon": "res://assets/ui/buttons/glowcat/cat_icon.svg",

		# Backgrounds
		"background_office": "res://assets/images/backgrounds/office_scene.png",
		"background_computer_1": "res://assets/images/misc/computer_1.png",
		"background_computer_2": "res://assets/images/misc/computer_2.png",

		# UI Components
		"glow_button_shader": "res://assets/ui/buttons/glowcat/GlowButton.shader",
		"glow_button_script": "res://assets/ui/buttons/glowcat/GlowButton.gd",

		# Icons (placeholders - not yet created)
		"logo": "res://assets/images/logo.png",
		"icon_money": "res://assets/icons/money.png",
		"icon_compute": "res://assets/icons/compute.png",
		"icon_research": "res://assets/icons/research.png",
		"icon_doom": "res://assets/icons/doom.png",
		"icon_paper": "res://assets/icons/paper.png",
		"icon_reputation": "res://assets/icons/reputation.png",
	}

	func _init(theme_name: String = "default"):
		name = theme_name
		display_name = theme_name.capitalize()

# Signals
signal theme_changed(theme_name: String)

func _ready():
	_initialize_default_themes()
	load_theme_config()
	apply_theme(current_theme)

	print("[ThemeManager] Initialized with theme: %s" % current_theme)

## Initialize built-in themes
func _initialize_default_themes():
	# Default theme (current style)
	var default = ThemeData.new("default")
	default.display_name = "Default"
	themes["default"] = default

	# Retro Terminal theme
	var retro = ThemeData.new("retro")
	retro.display_name = "Retro Terminal"
	retro.colors["background"] = Color(0.0, 0.0, 0.0)
	retro.colors["panel"] = Color(0.05, 0.1, 0.05)
	retro.colors["text"] = Color(0.0, 1.0, 0.0)
	retro.colors["accent"] = Color(0.0, 0.8, 0.0)
	retro.fonts["title_size"] = 36
	retro.fonts["body_size"] = 18
	themes["retro"] = retro

	# High Contrast theme
	var high_contrast = ThemeData.new("high_contrast")
	high_contrast.display_name = "High Contrast"
	high_contrast.colors["background"] = Color(0.0, 0.0, 0.0)
	high_contrast.colors["panel"] = Color(0.1, 0.1, 0.1)
	high_contrast.colors["text"] = Color(1.0, 1.0, 1.0)
	high_contrast.colors["accent"] = Color(1.0, 1.0, 0.0)
	high_contrast.styles["border_width"] = 3
	themes["high_contrast"] = high_contrast

## Load theme configuration from file
func load_theme_config():
	var config = ConfigFile.new()
	var err = config.load("user://theme.cfg")

	if err == OK:
		current_theme = config.get_value("settings", "current_theme", "default")

		# Load custom themes
		var custom_themes = config.get_value("settings", "custom_themes", [])
		for theme_name in custom_themes:
			var theme_data = ThemeData.new(theme_name)

			# Load colors
			if config.has_section(theme_name + "_colors"):
				for key in config.get_section_keys(theme_name + "_colors"):
					theme_data.colors[key] = config.get_value(theme_name + "_colors", key)

			themes[theme_name] = theme_data

## Save theme configuration
func save_theme_config():
	var config = ConfigFile.new()
	config.set_value("settings", "current_theme", current_theme)
	config.save("user://theme.cfg")

## Apply a theme globally
func apply_theme(theme_name: String):
	if not themes.has(theme_name):
		push_error("Theme '%s' not found" % theme_name)
		return

	current_theme = theme_name
	theme_changed.emit(theme_name)
	save_theme_config()

	print("[ThemeManager] Applied theme: %s" % theme_name)

## Get current theme data
func get_theme() -> ThemeData:
	return themes.get(current_theme, themes["default"])

## Get a color from current theme
func get_color(color_name: String) -> Color:
	var theme = get_theme()
	return theme.colors.get(color_name, Color.WHITE)

## Get a font size from current theme
func get_font_size(size_name: String) -> int:
	var theme = get_theme()
	return theme.fonts.get(size_name, 16)

## Get a spacing value from current theme
func get_spacing(spacing_name: String) -> int:
	var theme = get_theme()
	return theme.spacing.get(spacing_name, 10)

## Get a style value from current theme
func get_style(style_name: String) -> int:
	var theme = get_theme()
	return theme.styles.get(style_name, 0)

## Get an asset path from current theme
func get_asset(asset_name: String) -> String:
	var theme = get_theme()
	return theme.assets.get(asset_name, "")

## Create a styled button
func create_button(text: String, size: Vector2 = Vector2.ZERO) -> Button:
	var button = Button.new()
	button.text = text

	if size != Vector2.ZERO:
		button.custom_minimum_size = size
	else:
		# Smaller buttons: 32px height instead of 40px
		button.custom_minimum_size = Vector2(200, 32)

	apply_button_style(button)
	return button

## Apply button style to existing button (Style Guide colors)
func apply_button_style(button: Button):
	# Style Guide colors
	var STEEL_DARK = Color(0.110, 0.153, 0.188)
	var ELECTRIC_BLUE = Color(0.204, 0.596, 0.859)
	var NEON_MAGENTA = Color(0.929, 0.263, 0.792)

	# Create normal state - dark background with blue border
	var style_normal = StyleBoxFlat.new()
	style_normal.bg_color = STEEL_DARK
	style_normal.border_color = ELECTRIC_BLUE
	style_normal.border_width_left = 2
	style_normal.border_width_top = 2
	style_normal.border_width_right = 2
	style_normal.border_width_bottom = 2
	style_normal.corner_radius_top_left = 4
	style_normal.corner_radius_top_right = 4
	style_normal.corner_radius_bottom_left = 4
	style_normal.corner_radius_bottom_right = 4

	# Create hover state - brighter blue glow
	var style_hover = style_normal.duplicate()
	style_hover.bg_color = STEEL_DARK.lightened(0.1)
	style_hover.border_color = ELECTRIC_BLUE.lightened(0.2)
	style_hover.shadow_color = Color(ELECTRIC_BLUE.r, ELECTRIC_BLUE.g, ELECTRIC_BLUE.b, 0.3)
	style_hover.shadow_size = 4

	# Create pressed state - magenta accent
	var style_pressed = style_normal.duplicate()
	style_pressed.bg_color = STEEL_DARK.lightened(0.15)
	style_pressed.border_color = NEON_MAGENTA

	# Disabled state - grey and transparent
	var style_disabled = style_normal.duplicate()
	style_disabled.bg_color = STEEL_DARK.darkened(0.2)
	style_disabled.border_color = Color(0.4, 0.4, 0.5)

	# Apply styles
	button.add_theme_stylebox_override("normal", style_normal)
	button.add_theme_stylebox_override("hover", style_hover)
	button.add_theme_stylebox_override("pressed", style_pressed)
	button.add_theme_stylebox_override("disabled", style_disabled)

	# Font styling (white text, 12px)
	button.add_theme_color_override("font_color", Color.WHITE)
	button.add_theme_color_override("font_disabled_color", Color(0.5, 0.5, 0.5))
	button.add_theme_font_size_override("font_size", 12)

## Create a styled panel
func create_panel(size: Vector2 = Vector2.ZERO) -> PanelContainer:
	var panel = PanelContainer.new()

	if size != Vector2.ZERO:
		panel.custom_minimum_size = size

	apply_panel_style(panel)
	return panel

## Apply panel style to existing panel
func apply_panel_style(panel: PanelContainer, dark: bool = false):
	var theme = get_theme()

	var style = StyleBoxFlat.new()
	style.bg_color = theme.colors["panel_dark"] if dark else theme.colors["panel"]
	style.border_color = theme.colors["accent"].darkened(0.3)
	style.border_width_left = theme.styles["border_width"]
	style.border_width_top = theme.styles["border_width"]
	style.border_width_right = theme.styles["border_width"]
	style.border_width_bottom = theme.styles["border_width"]
	style.corner_radius_top_left = theme.styles["panel_corner_radius"]
	style.corner_radius_top_right = theme.styles["panel_corner_radius"]
	style.corner_radius_bottom_left = theme.styles["panel_corner_radius"]
	style.corner_radius_bottom_right = theme.styles["panel_corner_radius"]
	style.content_margin_left = theme.spacing["padding"]
	style.content_margin_top = theme.spacing["padding"]
	style.content_margin_right = theme.spacing["padding"]
	style.content_margin_bottom = theme.spacing["padding"]

	panel.add_theme_stylebox_override("panel", style)

## Create a styled label
func create_label(text: String, size_type: String = "body") -> Label:
	var label = Label.new()
	label.text = text
	apply_label_style(label, size_type)
	return label

## Apply label style to existing label
func apply_label_style(label: Label, size_type: String = "body"):
	var theme = get_theme()
	var font_size = theme.fonts.get(size_type + "_size", theme.fonts["body_size"])

	label.add_theme_color_override("font_color", theme.colors["text"])
	label.add_theme_font_size_override("font_size", font_size)

## Get doom color based on percentage
func get_doom_color(doom_percent: float) -> Color:
	var theme = get_theme()

	if doom_percent < 30.0:
		return theme.colors["doom_low"]
	elif doom_percent < 60.0:
		return theme.colors["doom_medium"]
	elif doom_percent < 85.0:
		return theme.colors["doom_high"]
	else:
		return theme.colors["doom_critical"]

## List all available themes
func get_available_themes() -> Array:
	return themes.keys()

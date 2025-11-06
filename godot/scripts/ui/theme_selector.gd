extends PanelContainer
## Theme Selector Widget - Dropdown to switch themes

@onready var theme_dropdown = $MarginContainer/HBoxContainer/ThemeDropdown
@onready var label = $MarginContainer/HBoxContainer/Label

func _ready():
	_populate_themes()
	theme_dropdown.item_selected.connect(_on_theme_selected)
	ThemeManager.theme_changed.connect(_on_theme_changed)

	# Apply current theme styling
	ThemeManager.apply_panel_style(self)
	ThemeManager.apply_label_style(label, "body")

func _populate_themes():
	theme_dropdown.clear()

	var themes = ThemeManager.get_available_themes()
	for i in range(themes.size()):
		var theme_name = themes[i]
		var theme_data = ThemeManager.themes[theme_name]
		theme_dropdown.add_item(theme_data.display_name)

		if theme_name == ThemeManager.current_theme:
			theme_dropdown.selected = i

func _on_theme_selected(index: int):
	var themes = ThemeManager.get_available_themes()
	if index < themes.size():
		ThemeManager.apply_theme(themes[index])

func _on_theme_changed(theme_name: String):
	print("[ThemeSelector] Theme changed to: %s" % theme_name)
	# Re-apply styling with new theme
	ThemeManager.apply_panel_style(self)

extends PanelContainer
## Enhanced Resource Display - Styled with ThemeManager

@export var icon_size: int = 32

# Resource data
var resources: Dictionary = {
	"turn": {"value": 0, "icon": null, "color": "text"},
	"money": {"value": 0, "icon": null, "color": "warning"},
	"compute": {"value": 0, "icon": null, "color": "accent"},
	"research": {"value": 0, "icon": null, "color": "success"},
	"papers": {"value": 0, "icon": null, "color": "text"},
	"reputation": {"value": 0, "icon": null, "color": "accent"},
	"doom": {"value": 0, "icon": null, "color": "error"},
	"ap": {"value": 0, "icon": null, "color": "text"},
}

func _ready():
	# Apply theme styling
	ThemeManager.apply_panel_style(self)

	# Listen for theme changes
	ThemeManager.theme_changed.connect(_on_theme_changed)

func _on_theme_changed(theme_name: String):
	ThemeManager.apply_panel_style(self)
	_update_display()

## Update all resource displays
func update_resources(state: Dictionary):
	resources["turn"]["value"] = state.get("turn", 0)
	resources["money"]["value"] = state.get("money", 0)
	resources["compute"]["value"] = state.get("compute", 0)
	resources["research"]["value"] = state.get("research_progress", 0)
	resources["papers"]["value"] = state.get("papers_published", 0)
	resources["reputation"]["value"] = state.get("reputation", 0)
	resources["doom"]["value"] = state.get("doom", 0)
	resources["ap"]["value"] = state.get("action_points", 0)

	_update_display()

## Update the visual display
func _update_display():
	# This is a simple version - you can expand with icons, progress bars, etc.
	pass

## Format resource value for display
func format_value(key: String, value: float) -> String:
	match key:
		"money":
			return "$%.0f" % value
		"compute", "research":
			return "%.1f" % value
		"doom":
			return "%.1f%%" % value
		_:
			return "%.0f" % value

## Get color for resource
func get_resource_color(key: String) -> Color:
	if key == "doom":
		return ThemeManager.get_doom_color(resources["doom"]["value"])
	else:
		var color_name = resources[key].get("color", "text")
		return ThemeManager.get_color(color_name)

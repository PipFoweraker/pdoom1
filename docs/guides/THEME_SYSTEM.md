# Theme System Documentation

## Overview

The P(Doom) theme system provides centralized visual styling with support for multiple themes, easy asset swapping, and consistent UI across the entire game.

## Architecture

### ThemeManager (Autoload)
**Location**: `godot/autoload/theme_manager.gd`

Global singleton that manages themes, colors, fonts, spacing, and assets.

### ThemeData Class
Each theme contains:
- **Colors**: Background, panels, text, accents, status colors, doom meter colors
- **Fonts**: Title, header, body, and small font sizes
- **Spacing**: Margins, padding, gaps, button heights
- **Styles**: Corner radius, border widths
- **Assets**: Paths to images, icons, fonts

## Built-in Themes

### Default
- Modern dark theme with blue accents
- Based on current UI style
- Recommended for general use

### Retro Terminal
- Black background with green text
- Monochrome CRT aesthetic
- Larger fonts for readability
- Perfect for that 80s hacker vibe

### High Contrast
- Maximum readability
- Black/white with yellow accents
- Thicker borders
- Accessibility-focused

## Usage

### Getting Theme Values

```gdscript
# Colors
var bg_color = ThemeManager.get_color("background")
var doom_color = ThemeManager.get_doom_color(doom_percent)  # Auto-selects based on %

# Fonts
var title_size = ThemeManager.get_font_size("title")

# Spacing
var margin = ThemeManager.get_spacing("margin")

# Assets
var cat_image = ThemeManager.get_asset("cat")
```

### Creating Styled UI Elements

```gdscript
# Styled button
var button = ThemeManager.create_button("Click Me", Vector2(200, 50))

# Or apply style to existing button
ThemeManager.apply_button_style(my_button)

# Styled panel
var panel = ThemeManager.create_panel(Vector2(400, 300))
ThemeManager.apply_panel_style(my_panel, dark=true)  # Dark variant

# Styled label
var label = ThemeManager.create_label("Hello", "header")  # header/body/title/small
ThemeManager.apply_label_style(my_label, "body")
```

### Switching Themes

```gdscript
# Programmatic
ThemeManager.apply_theme("retro")

# In UI (theme_selector widget)
# Automatically saves preference to user://theme.cfg
```

### Responding to Theme Changes

```gdscript
func _ready():
    ThemeManager.theme_changed.connect(_on_theme_changed)

func _on_theme_changed(theme_name: String):
    # Re-apply styling
    ThemeManager.apply_button_style(my_button)
    ThemeManager.apply_panel_style(my_panel)
```

## Asset Management

### Directory Structure
```
godot/assets/
|--- images/
|   |--- backgrounds/
|   |--- ui/
|   |--- characters/
|   `--- misc/
|--- icons/
|   |--- resources/
|   |--- actions/
|   `--- status/
|--- fonts/
`--- audio/
    |--- sfx/
    `--- music/
```

### Adding New Assets

1. Place asset in appropriate directory
2. Update `theme_manager.gd`:

```gdscript
var assets: Dictionary = {
    "my_new_icon": "res://assets/icons/my_icon.png"
}
```

3. Access via `ThemeManager.get_asset("my_new_icon")`

### Asset Naming Conventions
- Lowercase with underscores: `office_cat.png`
- Include size for variants: `icon_money_64.png`
- Group by purpose: `ui_panel_dark.png`

## Creating Custom Themes

### Option 1: Code (for built-in themes)

```gdscript
var my_theme = ThemeData.new("my_theme")
my_theme.display_name = "My Awesome Theme"
my_theme.colors["background"] = Color(0.1, 0.1, 0.2)
my_theme.colors["accent"] = Color(1.0, 0.5, 0.0)
my_theme.fonts["title_size"] = 48
ThemeManager.themes["my_theme"] = my_theme
```

### Option 2: Config File (for user themes)

Automatically saved to `user://theme.cfg` when modified.

## Best Practices

1. **Always use ThemeManager** instead of hardcoded colors/sizes
2. **Connect to theme_changed signal** for dynamic UI
3. **Test all themes** before release
4. **Document asset sources** in assets/ASSETS_README.md
5. **Optimize large assets** (compress, resize appropriately)

## Roadmap

- [ ] Theme preview in settings
- [ ] Custom theme editor
- [ ] Import/export theme files
- [ ] Per-window theme overrides
- [ ] Animation/transition styles in themes
- [ ] Sound effects per theme (optional)

## Files

- `godot/autoload/theme_manager.gd` - Core theme system
- `godot/scripts/ui/theme_selector.gd` - UI widget for theme switching
- `godot/assets/ASSETS_README.md` - Asset organization guide
- `THEME_SYSTEM.md` - This file

# Godot UI Implementation Guide - Color Scheme

## Overview

This document provides specific implementation instructions for applying the approved UI color scheme to the Godot port of P(Doom). Based on the analysis in `UI_COLOR_SCHEME_RECOMMENDATIONS.md`, this guide focuses on **Option 3: Enhanced Grey Background with Black Text**.

## Recommended Color Scheme (Option 3)

```gdscript
# Color constants in Godot (RGB values normalized to 0-1 range)
const BG_COLOR = Color(0.549, 0.549, 0.549, 1.0)      # (140, 140, 140) - Lighter grey
const TITLE_COLOR = Color(0.0, 0.0, 0.0, 1.0)         # (0, 0, 0) - Black
const TEXT_COLOR = Color(0.078, 0.078, 0.078, 1.0)    # (20, 20, 20) - Near black
const INSTRUCTION_COLOR = Color(0.039, 0.039, 0.039, 1.0)  # (10, 10, 10) - Very dark grey

# Alternative: using RGB8 for easier readability
const BG_COLOR_RGB8 = Color8(140, 140, 140, 255)
const TITLE_COLOR_RGB8 = Color8(0, 0, 0, 255)
const TEXT_COLOR_RGB8 = Color8(20, 20, 20, 255)
const INSTRUCTION_COLOR_RGB8 = Color8(10, 10, 10, 255)
```

## Implementation Methods

### Method 1: Theme Resource (Recommended for Global Styling)

Create a theme resource file `res://themes/main_menu_theme.tres`:

```gdscript
[gd_resource type="Theme" format=3]

[resource]
# Default font colors
default_font_color = Color(0.078, 0.078, 0.078, 1)  # (20, 20, 20)

# Label settings for regular text
Label/colors/font_color = Color(0.078, 0.078, 0.078, 1)
Label/font_sizes/font_size = 18

# RichTextLabel for instructions
RichTextLabel/colors/default_color = Color(0.039, 0.039, 0.039, 1)  # (10, 10, 10)

# Background panel style
panel_bg/StyleBoxFlat/bg_color = Color(0.549, 0.549, 0.549, 1)  # (140, 140, 140)
```

Apply in main menu scene:

```gdscript
extends Control

func _ready():
    # Load and apply theme
    var menu_theme = preload("res://themes/main_menu_theme.tres")
    theme = menu_theme
```

### Method 2: Per-Control Override (For Specific Elements)

For individual control nodes (useful for titles with different colors):

```gdscript
# For title labels (Menu Controls, In-Game Controls)
$MenuTitle.add_theme_color_override("font_color", Color8(0, 0, 0, 255))
$MenuTitle.add_theme_font_size_override("font_size", 20)

# For control text items
$ControlsList.add_theme_color_override("font_color", Color8(20, 20, 20, 255))

# For instructions at bottom
$Instructions.add_theme_color_override("font_color", Color8(10, 10, 10, 255))

# For background panel
$BackgroundPanel.add_theme_stylebox_override("panel", create_bg_stylebox())

func create_bg_stylebox() -> StyleBoxFlat:
    var style = StyleBoxFlat.new()
    style.bg_color = Color8(140, 140, 140, 255)
    style.border_width_all = 0
    return style
```

### Method 3: Custom Control Script (Most Flexible)

Create a custom main menu control script:

```gdscript
extends Control
class_name MainMenu

# Color constants
const COLORS = {
    "bg": Color8(140, 140, 140, 255),
    "title": Color8(0, 0, 0, 255),
    "text": Color8(20, 20, 20, 255),
    "instruction": Color8(10, 10, 10, 255)
}

# Font settings
const FONT_SIZES = {
    "title": 24,
    "text": 18,
    "instruction": 16
}

@onready var menu_controls_title = $MenuControlsTitle
@onready var menu_controls_list = $MenuControlsList
@onready var ingame_controls_title = $InGameControlsTitle
@onready var ingame_controls_list = $InGameControlsList
@onready var instructions = $Instructions

func _ready():
    _apply_color_scheme()

func _apply_color_scheme():
    # Background
    $Background.color = COLORS.bg
    
    # Titles (Menu Controls, In-Game Controls)
    menu_controls_title.add_theme_color_override("font_color", COLORS.title)
    menu_controls_title.add_theme_font_size_override("font_size", FONT_SIZES.title)
    
    ingame_controls_title.add_theme_color_override("font_color", COLORS.title)
    ingame_controls_title.add_theme_font_size_override("font_size", FONT_SIZES.title)
    
    # Control lists
    for control_label in menu_controls_list.get_children():
        if control_label is Label:
            control_label.add_theme_color_override("font_color", COLORS.text)
            control_label.add_theme_font_size_override("font_size", FONT_SIZES.text)
    
    for control_label in ingame_controls_list.get_children():
        if control_label is Label:
            control_label.add_theme_color_override("font_color", COLORS.text)
            control_label.add_theme_font_size_override("font_size", FONT_SIZES.text)
    
    # Instructions
    instructions.add_theme_color_override("font_color", COLORS.instruction)
    instructions.add_theme_font_size_override("font_size", FONT_SIZES.instruction)
```

## Scene Structure Recommendations

### Main Menu Scene Hierarchy

```
MainMenu (Control)
|--- Background (ColorRect)
|   `--- color: Color8(140, 140, 140, 255)
|
|--- CenterContainer
|   |--- VBoxContainer
|   |   |--- TitleLabel
|   |   `--- MenuButtons (VBoxContainer)
|   |       |--- LaunchButton
|   |       |--- SettingsButton
|   |       `--- ExitButton
|
|--- SidePanel_Left (VBoxContainer)
|   |--- MenuControlsTitle (Label)
|   |   `--- text: "Menu Controls:"
|   |   `--- font_color: Color8(0, 0, 0, 255) [BOLD]
|   `--- MenuControlsList (VBoxContainer)
|       |--- ControlLabel1 (Label)
|       |   `--- font_color: Color8(20, 20, 20, 255)
|       |--- ControlLabel2 (Label)
|       `--- ControlLabel3 (Label)
|
|--- SidePanel_Right (VBoxContainer)
|   |--- InGameControlsTitle (Label)
|   |   `--- text: "In-Game Controls:"
|   |   `--- font_color: Color8(0, 0, 0, 255) [BOLD]
|   `--- InGameControlsList (VBoxContainer)
|       |--- ControlLabel1 (Label)
|       |   `--- font_color: Color8(20, 20, 20, 255)
|       `--- ControlLabel2 (Label)
|
`--- BottomContainer
    `--- Instructions (Label)
        `--- text: "Use mouse or arrow keys to navigate"
        `--- font_color: Color8(10, 10, 10, 255)
```

## Font Weight and Styling

### Bold Titles

For title labels, use bold fonts to create visual hierarchy:

```gdscript
# Option 1: Use theme override with bold font
var bold_font = preload("res://fonts/consolas_bold.ttf")
$MenuControlsTitle.add_theme_font_override("font", bold_font)

# Option 2: Use BBCode in RichTextLabel
$MenuControlsTitle.bbcode_enabled = true
$MenuControlsTitle.bbcode_text = "[b]Menu Controls:[/b]"
```

### Font Resources Setup

1. Import Consolas or similar monospace font:
   - `res://fonts/consolas_regular.ttf`
   - `res://fonts/consolas_bold.ttf`

2. Create FontData resources with appropriate sizes:
   ```gdscript
   # Title font (bold, size 24)
   var title_font = FontData.new()
   title_font.path = "res://fonts/consolas_bold.ttf"
   title_font.size = 24
   
   # Text font (regular, size 18)
   var text_font = FontData.new()
   text_font.path = "res://fonts/consolas_regular.ttf"
   text_font.size = 18
   ```

## Dynamic Theme Switching (Optional)

For accessibility options or user preferences:

```gdscript
extends Control

enum ColorScheme {
    NORMAL,        # Option 3 - Enhanced Grey
    HIGH_CONTRAST, # Option 1 - Pure black text
    COLOR_CODED    # Option 4 - Color-coded sections
}

var current_scheme = ColorScheme.NORMAL

func apply_color_scheme(scheme: ColorScheme):
    match scheme:
        ColorScheme.NORMAL:
            _apply_normal_scheme()
        ColorScheme.HIGH_CONTRAST:
            _apply_high_contrast_scheme()
        ColorScheme.COLOR_CODED:
            _apply_color_coded_scheme()

func _apply_normal_scheme():
    # Option 3 colors
    var colors = {
        "bg": Color8(140, 140, 140, 255),
        "title": Color8(0, 0, 0, 255),
        "text": Color8(20, 20, 20, 255),
        "instruction": Color8(10, 10, 10, 255)
    }
    _apply_colors(colors)

func _apply_high_contrast_scheme():
    # Option 1 colors (all black)
    var colors = {
        "bg": Color8(128, 128, 128, 255),
        "title": Color8(0, 0, 0, 255),
        "text": Color8(20, 20, 20, 255),
        "instruction": Color8(30, 30, 30, 255)
    }
    _apply_colors(colors)

func _apply_color_coded_scheme():
    # Option 4 colors (menu = blue, ingame = red)
    $MenuControlsTitle.add_theme_color_override("font_color", Color8(0, 60, 120, 255))
    $InGameControlsTitle.add_theme_color_override("font_color", Color8(100, 20, 20, 255))
    # ... etc

func _apply_colors(colors: Dictionary):
    $Background.color = colors.bg
    $MenuControlsTitle.add_theme_color_override("font_color", colors.title)
    $InGameControlsTitle.add_theme_color_override("font_color", colors.title)
    # Apply to other elements...
```

## Contrast Validation

### Built-in Contrast Check

Add validation to ensure WCAG compliance:

```gdscript
func calculate_contrast_ratio(fg: Color, bg: Color) -> float:
    var l1 = _relative_luminance(fg)
    var l2 = _relative_luminance(bg)
    var lighter = max(l1, l2)
    var darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

func _relative_luminance(color: Color) -> float:
    var r = _linearize(color.r)
    var g = _linearize(color.g)
    var b = _linearize(color.b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

func _linearize(value: float) -> float:
    if value <= 0.03928:
        return value / 12.92
    else:
        return pow((value + 0.055) / 1.055, 2.4)

func validate_colors():
    var bg = Color8(140, 140, 140, 255)
    var title = Color8(0, 0, 0, 255)
    var text = Color8(20, 20, 20, 255)
    
    var title_ratio = calculate_contrast_ratio(title, bg)
    var text_ratio = calculate_contrast_ratio(text, bg)
    
    assert(title_ratio >= 4.5, "Title contrast does not meet WCAG AA")
    assert(text_ratio >= 4.5, "Text contrast does not meet WCAG AA")
    
    print("Title contrast: ", title_ratio, ":1 (", "AAA" if title_ratio >= 7.0 else "AA", ")")
    print("Text contrast: ", text_ratio, ":1 (", "AAA" if text_ratio >= 7.0 else "AA", ")")
```

## Migration from Pygame

### Color Value Mapping

| Element | Pygame RGB (OLD) | Pygame RGB (NEW) | Godot Color8 | Godot Color (0-1) |
|---------|------------------|------------------|--------------|-------------------|
| Background | (128, 128, 128) | (140, 140, 140) | (140, 140, 140, 255) | (0.549, 0.549, 0.549, 1.0) |
| Titles | (160, 160, 160) | (0, 0, 0) | (0, 0, 0, 255) | (0.0, 0.0, 0.0, 1.0) |
| Text | (140, 140, 140) | (20, 20, 20) | (20, 20, 20, 255) | (0.078, 0.078, 0.078, 1.0) |
| Instructions | (180, 180, 180) | (10, 10, 10) | (10, 10, 10, 255) | (0.039, 0.039, 0.039, 1.0) |

### Code Translation Example

**Pygame (ui.py):**
```python
left_title_surf = shortcut_font.render('Menu Controls:', True, (0, 0, 0))
shortcut_surf = shortcut_font.render(shortcut_text, True, (20, 20, 20))
```

**Godot (main_menu.gd):**
```gdscript
$MenuControlsTitle.text = "Menu Controls:"
$MenuControlsTitle.add_theme_color_override("font_color", Color8(0, 0, 0, 255))

for control_text in menu_controls:
    var label = Label.new()
    label.text = control_text
    label.add_theme_color_override("font_color", Color8(20, 20, 20, 255))
    $MenuControlsList.add_child(label)
```

## Testing Checklist

- [ ] Background color matches (140, 140, 140)
- [ ] Title text is black (0, 0, 0) with bold font
- [ ] Control text is near-black (20, 20, 20)
- [ ] Instructions are very dark grey (10, 10, 10)
- [ ] Contrast ratios meet WCAG AA (>=4.5:1)
- [ ] Text is readable on low-quality displays
- [ ] Color scheme works in different lighting conditions
- [ ] No color-only information (for colorblind users)
- [ ] Font sizes are appropriate (18px minimum for body text)
- [ ] Bold titles create clear visual hierarchy

## Additional Resources

- WCAG Contrast Guidelines: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- Godot Theme Documentation: https://docs.godotengine.org/en/stable/classes/class_theme.html
- Color Accessibility Tools: https://webaim.org/resources/contrastchecker/

## Next Steps

1. Create theme resource with recommended colors
2. Set up main menu scene structure
3. Apply colors using preferred method (theme, override, or script)
4. Test on multiple displays
5. Add accessibility options for user customization
6. Document color scheme in Godot project style guide

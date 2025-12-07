# Glowing Cat Button UI Kit

**Design Language**: Early-2000s command center aesthetic (Windows XP/Bloomberg/NATO C2)
**Theme**: Smoked glass + dark plastic + neon accents
**Status**: Ready for integration

## Files

- **cat_icon.svg** - Scalable cat icon (stroke-based, uses currentColor)
- **GlowButton.shader** - Godot 4.x CanvasItem shader for neon glow effect
- **GlowButton.gd** - Button script with hover/press/armed states
- **glow_buttons.css** - Web reference implementation
- **glow_cat_button_design.md** - Complete design system documentation

## Quick Start (Godot 4.x)

### 1. Basic Glowing Button

```gdscript
# In your scene
var button = Button.new()
button.custom_minimum_size = Vector2(200, 56)
button.text = "CONFIRM"

# Add the glow button script
button.set_script(load("res://assets/ui/buttons/glowcat/GlowButton.gd"))

# The shader material will be auto-created
# Or manually create it:
var material = ShaderMaterial.new()
material.shader = load("res://assets/ui/buttons/glowcat/GlowButton.shader")
button.material = material

add_child(button)
```

### 2. With Cat Icon

```gdscript
# Add TextureRect as child
var icon = TextureRect.new()
icon.texture = load("res://assets/ui/buttons/glowcat/cat_icon.svg")
icon.custom_minimum_size = Vector2(22, 22)
icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
button.add_child(icon)
```

### 3. Colorway Options

```gdscript
# Export variables in GlowButton.gd
button.colorway = 0  # 0 = Teal (default), 1 = Amber (armed/warning)
button.glow_strength = 1.2  # Adjust glow intensity
```

## Design Tokens

### Colors
- **Action Teal**: `#1EC3B3` (hover: `#0FA5A0`)
- **Warn/Armed Amber**: `#F6A800`
- **Base Graphite**: `#0E1318`
- **Off-white Text**: `#E9F2F2`
- **Chrome Highlight**: `#6B7C8C`

### Doom-Tier Overlays (Global)
- Tier 0: None
- Tier 1: `#F6A800 @ 6%`
- Tier 2: `#E9752E @ 10%`
- Tier 3: `#E24A3B @ 14%`
- Tier 4: `#B31217 @ 18%`

### Sizes
- **Standard height**: 48px
- **CTA height**: 56px
- **Corner radius**: 12px (standard), 999px (pill)
- **Icon size**: 20-24px

## Button Types

1. **Primary (Confirm/Commit)**: Teal fill + neon ring
2. **Secondary (Utility)**: Dark fill, teal text/icon
3. **Destructive/Armed**: Amber (hover)  ->  Red (pressed)
4. **Icon-only (Round)**: 56px circular with cat icon
5. **Pill CTA**: Maximum radius for high-prominence actions

## State Behavior

- **Default**: Dark gradient with subtle top highlight
- **Hover**: +3-6% brightness, stronger glow ring
- **Pressed**: Inverted bevel, content nudged +1px down
- **Focused**: 1px teal focus ring (accessibility)
- **Disabled**: Desaturated, reduced contrast
- **Armed/Danger**: Amber ring + cat icon

## Integration with ThemeManager

To integrate with our theme system, update `theme_manager.gd`:

```gdscript
# Add to ThemeData.assets
"glow_button_shader": "res://assets/ui/buttons/glowcat/GlowButton.shader",
"glow_button_script": "res://assets/ui/buttons/glowcat/GlowButton.gd",
"cat_icon": "res://assets/ui/buttons/glowcat/cat_icon.svg",
```

## Web Demo

Open `index.html` (not included) in a browser to see the web reference implementation.

## Credits

Design system: glow_cat_button_design.md
Last updated: 2025-10-31

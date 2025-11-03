# Asset Integration Guide - October 31, 2025

## Assets Organized ✅

All assets from `dump_october_31_2025/` have been properly organized into the asset structure.

### File Moves Summary

**UI Components** → `godot/assets/ui/buttons/glowcat/`
- cat_icon.svg
- GlowButton.shader
- GlowButton.gd
- glow_buttons.css (web reference)
- glow_cat_button_design.md (design system)

**Images** → `godot/assets/images/`
- `backgrounds/office_scene.png` (was: "main office doom chair scene.png")
- `misc/computer_1.png` (was: "vibes computer 1.png")
- `misc/computer_2.png` (was: "vibes computer 2.png")
- `misc/cat_closeup.png` (was: "zoomed in doom cat.png")

## ThemeManager Integration ✅

All new assets registered in `theme_manager.gd`:

```gdscript
ThemeManager.get_asset("cat_icon")              // SVG cat icon
ThemeManager.get_asset("cat_closeup")           // Zoomed cat photo
ThemeManager.get_asset("background_office")     // Office scene
ThemeManager.get_asset("background_computer_1") // Computer scene 1
ThemeManager.get_asset("background_computer_2") // Computer scene 2
ThemeManager.get_asset("glow_button_shader")    // Neon glow shader
ThemeManager.get_asset("glow_button_script")    // Button behavior
```

## Next Steps for Integration

### 1. Glow Button System

The glow button system is ready to use but needs integration:

**Option A: Replace ThemeManager.create_button()**
Update `theme_manager.gd` to use GlowButton by default:

```gdscript
func create_button(text: String, size: Vector2 = Vector2.ZERO) -> Button:
	var button = Button.new()
	button.text = text

	# Use glow button script
	button.set_script(load(get_asset("glow_button_script")))

	# Rest of setup...
```

**Option B: Add create_glow_button() method**
Keep existing button creation, add new method:

```gdscript
func create_glow_button(text: String, armed: bool = false) -> Button:
	var button = Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(200, 56)

	# Apply glow button script
	var glow_script = load(get_asset("glow_button_script"))
	button.set_script(glow_script)

	# Set colorway: 0 = teal, 1 = amber (armed)
	button.colorway = 1 if armed else 0

	return button
```

### 2. Background Images

Use office scene as main game background:

```gdscript
# In main.tscn or welcome.tscn
var bg = TextureRect.new()
bg.texture = load(ThemeManager.get_asset("background_office"))
bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
# Add as background layer
```

### 3. Cat Icon Usage

The SVG cat icon is perfect for small UI elements:

```gdscript
# In button or icon display
var cat_icon = TextureRect.new()
cat_icon.texture = load(ThemeManager.get_asset("cat_icon"))
cat_icon.custom_minimum_size = Vector2(22, 22)
cat_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
```

### 4. Doom-Tier Color Overlays

From the design system, implement global doom overlays:

```gdscript
# In ThemeManager or DoomSystem
func get_doom_overlay_color(doom_percent: float) -> Color:
	if doom_percent < 20:
		return Color.TRANSPARENT  # Tier 0
	elif doom_percent < 40:
		return Color("#F6A800", 0.06)  # Tier 1
	elif doom_percent < 60:
		return Color("#E9752E", 0.10)  # Tier 2
	elif doom_percent < 80:
		return Color("#E24A3B", 0.14)  # Tier 3
	else:
		return Color("#B31217", 0.18)  # Tier 4

# Apply as ColorRect overlay on root
var overlay = ColorRect.new()
overlay.color = get_doom_overlay_color(current_doom)
overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
# Add to scene tree
```

## Design System Summary

### Early-2000s Command Center Aesthetic
- **Era**: Windows XP/Bloomberg terminals/NATO C2
- **Materials**: Smoked glass + dark ABS plastic + neon accents
- **Mood**: Calm professional → escalates ominously with doom

### Color Palette
```
Action Teal:    #1EC3B3 (hover: #0FA5A0)
Warn Amber:     #F6A800
Base Graphite:  #0E1318
Steel:          #1C2730
Text:           #E9F2F2
Chrome:         #6B7C8C
```

### Button States
- **Default**: Dark gradient + subtle highlight
- **Hover**: +3-6% brightness, stronger glow
- **Pressed**: Inverted bevel, content +1px down
- **Armed**: Amber ring + cat icon
- **Focused**: 1px teal focus ring

## Image Optimization TODO

All images are quite large (1.8-2.6MB each). Recommended optimizations:

```bash
# Using ImageMagick or similar
convert office_scene.png -resize 1920x1080 -quality 85 office_scene_optimized.png
convert cat_closeup.png -resize 512x512 -quality 90 cat_closeup_optimized.png
```

Or use Godot's import settings:
- Compress → Lossless or Lossy
- Mipmaps → Enable
- Normal Map → Disabled

## File Cleanup

Original dump folder can be removed after verification:

```bash
# AFTER testing that all assets work
rm -rf godot/assets/dump_october_31_2025/
```

## Testing Checklist

- [ ] Load office_scene.png as background
- [ ] Create glow button with cat_icon.svg
- [ ] Test button hover/press states
- [ ] Verify SVG scales cleanly
- [ ] Test doom overlay color system
- [ ] Optimize image file sizes
- [ ] Remove dump folder

## Credits

**Design System**: glow_cat_button_design.md
**Assets**: User-provided, October 31, 2025
**Integration**: Theme system + asset management

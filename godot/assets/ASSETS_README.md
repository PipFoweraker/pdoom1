# P(Doom) Assets Directory

This directory contains all visual and audio assets for the game.

## Directory Structure

```
assets/
├── images/          # Game images
│   ├── backgrounds/ # Background images
│   ├── ui/          # UI elements, borders, panels
│   ├── characters/  # Researcher portraits, character art
│   └── misc/        # Miscellaneous images (cat, logo, etc.)
├── icons/           # Small UI icons
│   ├── resources/   # Money, compute, research icons
│   ├── actions/     # Action icons
│   └── status/      # Status indicators, doom meter, etc.
├── fonts/           # Custom fonts
└── audio/           # Sound effects and music (future)
    ├── sfx/
    └── music/
```

## Asset Guidelines

### Image Formats
- **PNG** for UI elements, icons, characters (supports transparency)
- **JPEG** for backgrounds (smaller file size)
- **SVG** for scalable icons (Godot 4.x supports SVG)

### Recommended Sizes
- **Icons**: 32x32, 64x64, 128x128
- **Character Portraits**: 256x256 or 512x512
- **UI Panels**: Variable, design at 2x for retina displays
- **Backgrounds**: 1920x1080 or higher

### Naming Conventions
- Use lowercase with underscores: `office_cat.png`
- Include size in name if multiple versions: `icon_money_64.png`
- Group by purpose: `ui_panel_dark.png`, `character_researcher_safety.png`

## Current Assets

### Images
- `images/office_cat.png` - Office cat mascot (3.8MB - consider optimizing)

### Icons (Placeholders Needed)
- [ ] `icons/money.png` - Money/funding icon
- [ ] `icons/compute.png` - Compute resource icon
- [ ] `icons/research.png` - Research progress icon
- [ ] `icons/doom.png` - Doom meter icon
- [ ] `icons/paper.png` - Published paper icon
- [ ] `icons/reputation.png` - Reputation icon

### Fonts (Optional)
- Consider adding a monospace font for retro terminal theme
- Add custom font for titles/headers

## Theme Integration

All assets are referenced through `ThemeManager` which allows:
- Easy theme switching
- Consistent asset paths
- Runtime asset swapping

To add a new asset:
1. Place file in appropriate directory
2. Update `theme_manager.gd` assets dictionary
3. Access via `ThemeManager.get_asset("asset_name")`

## Optimization Tips

- Use Godot's import settings to optimize textures
- Enable mipmaps for textures that scale
- Use texture atlases for many small icons
- Compress large backgrounds
- Current `office_cat.png` is 3.8MB - recommend resizing to 512x512 and re-exporting

## License & Attribution

Document asset sources and licenses here:
- `office_cat.png` - [Source/License]
- Future assets - Add attribution as needed

# P(Doom) UI Style Guide
## Visual Design System for Godot Implementation

_Last updated: 2025-11-20_
_Status: Living document - evolving as brand identity develops_

---

## 1. Design Philosophy

### Core Aesthetic
**Early 2000s Command Center** - Bloomberg terminals, NATO C2 systems, Windows XP/Longhorn prototypes

**Material Language:**
- Smoked glass overlays
- Dark ABS plastic surfaces
- Anodized edge accents
- Subtle film grain texture (container-level only)
- Faint scanlines for retro-tech feel

**Emotional Arc:**
- **Default state**: Calm, professional, methodical
- **Mid-game**: Tension building, amber warnings
- **High doom**: Ominous, critical alerts, red overlays

---

## 2. Color System

### Current Theme: Red-Magenta-Purple Hues
_Note: May transition to purple-green theme as brand evolves_

#### Base Palette
```gdscript
# Dark Surfaces
graphite = Color(0.055, 0.075, 0.094)      # #0E1318
steel = Color(0.110, 0.153, 0.188)         # #1C2730
deep = Color(0.059, 0.090, 0.114)          # #0F171D

# Accents
action_teal = Color(0.118, 0.765, 0.702)   # #1EC3B3
action_teal_hover = Color(0.059, 0.647, 0.627)  # #0FA5A0
warn_amber = Color(0.965, 0.659, 0.000)    # #F6A800
danger_red = Color(0.702, 0.027, 0.090)    # #B31217

# Neutrals
off_white = Color(0.914, 0.949, 0.949)     # #E9F2F2
chrome = Color(0.420, 0.486, 0.549)        # #6B7C8C
```

#### Doom Tier Overlays
Progressive color washes applied globally as doom escalates:

```gdscript
tier_0 = null  # No overlay (0-19% doom)
tier_1 = Color(0.965, 0.659, 0.000, 0.06)  # Amber 6% (20-39%)
tier_2 = Color(0.914, 0.459, 0.180, 0.10)  # Orange 10% (40-59%)
tier_3 = Color(0.886, 0.290, 0.231, 0.14)  # Red-orange 14% (60-79%)
tier_4 = Color(0.702, 0.071, 0.090, 0.18)  # Deep red 18% (80-100%)
```

#### Functional Colors
```gdscript
# Resource displays (from ThemeManager)
doom_low = Color(0.3, 0.8, 0.3)       # <30% doom - safe green
doom_medium = Color(0.9, 0.7, 0.2)    # 30-60% doom - warning yellow
doom_high = Color(0.9, 0.3, 0.2)      # 60-80% doom - danger orange
doom_critical = Color(0.7, 0.1, 0.1)  # >80% doom - critical red

# UI feedback
success = Color(0.2, 0.9, 0.4)        # Completion, purchases
info = Color(0.4, 0.7, 1.0)           # Informational
warning = Color(0.95, 0.8, 0.2)       # Caution
error = Color(0.95, 0.3, 0.2)         # Errors, failures
```

---

## 3. Typography

### Font System
```gdscript
# Primary UI Font: Inter (or Godot default)
# Display Font: Michroma/Orbitron (headers, titles)

# Sizes
title = 48           # Main screen titles
subtitle = 18        # Section headers
heading = 24         # Panel titles
body = 14            # Standard text
caption = 12         # Tooltips, hints
```

### Text Treatment
- **All-caps for labels**: +0.06em letter-spacing
- **Title case for actions/buttons**
- **Sentence case for descriptions**

---

## 4. Spacing & Layout

### Grid System
```gdscript
# Base unit: 8px
spacing_tiny = 4
spacing_small = 8
spacing_medium = 16
spacing_large = 24
spacing_xlarge = 32

# Common margins
margin_panel = 10
margin_container = 20
margin_section = 30
```

### Component Dimensions
```gdscript
# Buttons
button_height_standard = 48
button_height_cta = 56
button_padding_h = 16  # to 22
button_padding_v = 8   # to 12

# Panels
corner_radius_standard = 12
corner_radius_pill = 999

# Icons
icon_small = 20
icon_medium = 24
icon_large = 32
```

---

## 5. Visual Effects

### Glow & Neon
Based on GlowButton design system:

```gdscript
# Button states
default_glow = 0.3
hover_glow = 0.5
pressed_glow = 0.2
armed_glow = 0.7

# Edge treatment
edge_ring_width = 1.0  # Crisp 1px edge
edge_blur = 4.0        # Soft outer bloom
```

### Bevel & Depth
```gdscript
# Subtle 3D press effect
highlight_top = Color(chrome, 0.3)     # Top edge
shadow_bottom = Color(0, 0, 0, 0.4)    # Bottom edge

# State variants
pressed_content_offset = Vector2(0, 1)  # 1px down when pressed
```

### Film Grain & Scanlines
**Applied at container level only** - never per-button
```gdscript
grain_opacity = 0.03
scanline_opacity = 0.05
scanline_spacing = 4  # pixels
```

### Background Texture System
**Tileable textures** for screen backgrounds with subtle overlay effects.

#### Texture Categories
```gdscript
# Terminal textures (CRT/scanline effects) - godot/assets/textures/terminal/
tex_amber_scanlines    # Amber CRT scanlines
tex_amber_noise        # Amber static noise
tex_green_scanlines    # Green CRT scanlines
tex_green_grid         # Green character grid
tex_blue_dos_bg        # DOS blue background
tex_blue_bsod_pattern  # BSOD error pattern
tex_gray_lowcontrast   # Low contrast gray
tex_gray_dither        # Gray dither pattern
tex_cyan_ispf          # ISPF panel background
tex_cyan_border        # Cyan box border pattern

# Surface textures (materials) - godot/assets/textures/surfaces/
tex_grid_graphpaper_aged     # Aged graph paper
tex_grid_perforated_metal    # Perforated metal
tex_grid_circuit_trace       # Circuit board traces
tex_concrete_institutional   # Soviet concrete
tex_linoleum_damaged         # Damaged linoleum
tex_painted_metal_panel      # Painted metal
tex_plywood_stained          # Stained plywood
tex_crt_burnin               # CRT phosphor burn
tex_oxidized_copper          # Oxidized copper traces
tex_bakelite_cracked         # Cracked bakelite
```

#### Screen Assignments
```gdscript
# Format: [Background texture] + [Overlay texture at opacity]
welcome_screen     = tex_grid_circuit_trace + tex_green_scanlines (15%)
settings_menu      = tex_painted_metal_panel + tex_gray_dither (10%)
pregame_setup      = tex_bakelite_cracked + tex_amber_scanlines (12%)
leaderboard_screen = tex_oxidized_copper + tex_cyan_ispf (8%)
end_game_screen    = tex_crt_burnin overlay (15%)
```

#### Usage in Scenes
```gdscript
# TextureRect with stretch_mode = 1 (tile)
[node name="Background" type="TextureRect" parent="."]
texture = ExtResource("2_background")
stretch_mode = 1  # STRETCH_TILE

# Overlay with low opacity
[node name="ScanlineOverlay" type="TextureRect" parent="."]
modulate = Color(1, 1, 1, 0.15)  # 15% opacity
texture = ExtResource("3_overlay")
stretch_mode = 1
```

#### Accessing via ThemeManager
```gdscript
var texture_path = ThemeManager.get_asset("tex_amber_scanlines")
var texture = load(texture_path)
```

---

## 6. Button System

### Types
1. **Primary (Confirm/Commit)**
   - Teal fill + neon ring
   - Use for main actions

2. **Secondary (Utility/Status)**
   - Dark fill, teal text/icon
   - Softer glow ring

3. **Destructive/Armed**
   - Amber hover  ->  red pressed
   - For dangerous actions

4. **Icon-only (Round)**
   - 56px circular
   - Neon cat or system icon

5. **Disabled**
   - Desaturated, 60% opacity
   - Maintain >=4.5:1 contrast

### State Matrix
```gdscript
# Default
bg = LinearGradient(Color("#22303A"), Color("#172028"))
border = Color(chrome, 0.3)

# Hover
bg_brightness += 0.05
glow_strength += 0.2

# Pressed
bg = LinearGradient(Color("#0F1A20"), Color("#0B1318"))
content_offset = Vector2(0, 1)

# Focused
focus_ring = Color(action_teal)
focus_ring_width = 2

# Armed/Danger
border_color = Color(warn_amber)
icon = "cat_armed"
```

---

## 7. Overlay System
_Inspired by Starcraft/Civilization_

### AP Spending Indicators
**Current need:** Visual feedback when player commits Action Points

#### Proposed Implementations:
1. **AP Bar Pulsing**
   - Pulse/flash when AP decreases
   - Color-code: green  ->  yellow  ->  red as AP depletes

2. **Action Queue Visualization**
   - Small icons showing queued actions
   - Subtle glow effect on queue

3. **Button Confirmation**
   - Brief flash/glow on action button when pressed
   - Ripple effect emanating from button

4. **Resource Change Indicators**
   - Floating "+/-" numbers near resource displays
   - Color-coded by resource type

### Doom Tier Overlays
**Full-screen color wash** that intensifies with doom level:
```gdscript
# Applied as ColorRect with blend mode
overlay.modulate = get_doom_tier_color(current_doom)
overlay.blend_mode = ADD or MULTIPLY
```

### Critical Alerts
**For high-doom states (>80%)**:
- Pulsing red vignette around screen edges
- Subtle screen shake on doom increases
- Warning icons in corner

---

## 8. Animation Principles

### Timing
```gdscript
# Durations (seconds)
instant = 0.1
quick = 0.2
standard = 0.3
slow = 0.5
dramatic = 1.0

# Easing
ease_in = Tween.EASE_IN
ease_out = Tween.EASE_OUT
ease_in_out = Tween.EASE_IN_OUT
```

### Common Animations
- **Button press**: 0.1s ease_in_out
- **Panel slide**: 0.3s ease_out
- **Notification toast**: 0.2s slide + fade
- **Resource change**: 0.5s number count-up
- **Modal appear**: 0.2s fade + scale(0.95 -> 1.0)

---

## 9. Iconography

### Icon Style
- **Stroke-based** SVG icons
- 1.5px minimum stroke at 1x scale
- Rounded joins for neon continuity
- Uses `currentColor` for dynamic tinting

### Icon Grid
- 20px: Small icons (resource indicators)
- 24px: Standard icons (actions)
- 32px: Large icons (headers, special actions)

### Signature Icons
- **Cat icon**: Hero motif for special/armed actions
- **Warning triangle**: Doom alerts
- **Checkmark**: Completed/purchased
- **Lock**: Unavailable/locked

---

## 10. Accessibility Guidelines

### Contrast Requirements
- **Body text**: >=4.5:1 against background
- **Large text (18pt+)**: >=3:1
- **Disabled text**: >=4.5:1 maintained

### Focus Indicators
- Always visible focus ring
- 2px minimum width
- High contrast color (teal)
- Never rely on color alone

### Scaling
- All elements work at 110% UI scale
- Touch targets minimum 44x44px
- Text remains readable when scaled

---

## 11. Notification System

### Toast Notifications
From NotificationManager:

```gdscript
# Types
SUCCESS: green background, checkmark icon
INFO: blue background, info icon
WARNING: amber background, warning icon
ERROR: red background, error icon
ACHIEVEMENT: purple background, star icon

# Animation
slide_in: 0.2s from right
display: 3s (configurable)
slide_out: 0.2s to right
stacking: auto-adjust vertical position
```

### Position
- Top-right corner
- 10px margin from edges
- Auto-stack with 10px gap

---

## 12. Theme System Integration

### Using ThemeManager
```gdscript
# Get themed colors
var color = ThemeManager.get_doom_color(doom_percent)
var bg = ThemeManager.theme.colors["background"]

# Create themed buttons
var button = ThemeManager.create_button("Action Name")

# Create themed labels
var label = ThemeManager.create_label("Text", "large")

# Access theme assets
var icon = load(ThemeManager.theme.assets["cat_icon"])
```

### Available Themes
1. **Default**: Professional blue-grays
2. **Retro Terminal**: Green CRT aesthetic
3. **High Contrast**: Accessibility-focused

---

## 13. Brand Evolution Notes

### Current Direction
- **Primary**: Red-magenta-purple hues
- **Accent**: Teal for actions
- **Warning**: Amber
- **Danger**: Deep red

### Future Consideration
- **Potential shift**: Purple-green color scheme
- **Reasoning**: Distinct from other AI safety games
- **Testing**: Create theme variant before committing

### Design Principles to Maintain
1. Early-2000s command center aesthetic
2. Professional but slightly ominous
3. Clear information hierarchy
4. Accessible and readable
5. Consistent visual language

---

## 14. Implementation Checklist

### For New UI Elements
- [ ] Uses ThemeManager for colors
- [ ] Follows spacing grid (8px base unit)
- [ ] Maintains >=4.5:1 text contrast
- [ ] Has hover/pressed/disabled states
- [ ] Includes focus indicator
- [ ] Works at 110% scale
- [ ] Tested with all themes
- [ ] Doom tier overlays don't break it
- [ ] Touch-friendly (>=44px targets)
- [ ] Smooth animations (0.1-0.3s)

### For Visual Effects
- [ ] Film grain/scanlines at container level only
- [ ] Glow effects subtle (not overwhelming)
- [ ] Colors stay within brand palette
- [ ] Performance tested (60fps maintained)
- [ ] Works across screen resolutions

---

## 15. Resources & References

### Design Assets
- `godot/assets/ui/buttons/glowcat/` - Button design system
- `godot/assets/images/backgrounds/` - Office scene assets
- `godot/autoload/theme_manager.gd` - Theme implementation

### Documentation
- `glow_cat_button_design.md` - Detailed button specs
- `THEME_SYSTEM.md` - Theme system usage
- `UI_POLISH_GUIDE.md` - Component library
- `ASSET_INTEGRATION_GUIDE.md` - Asset usage

### External Inspiration
- **Bloomberg Terminal**: Information density, professional feel
- **Starcraft 2**: Resource overlays, alert system
- **Civilization VI**: Turn indicator, action queue
- **NATO C2 Systems**: Tactical interface, status indicators

---

## 16. Questions & Decisions Log

### Open Questions
1. **AP Spending Indicators**: Which visual approach?
   - Option A: AP bar pulsing + color changes
   - Option B: Action queue visualization with icons
   - Option C: Floating "+/- AP" text near buttons
   - Decision: TBD - need mockups

2. **Color Theme Transition**: When/if to switch to purple-green?
   - Current: Red-magenta-purple
   - Proposed: Purple-green
   - Decision: TBD - test theme variant first

3. **Overlay Intensity**: How prominent should doom overlays be?
   - Current: 6-18% opacity gradual increase
   - Concern: Don't obscure gameplay
   - Decision: TBD - playtest feedback

### Resolved Decisions
- SUCCESS Use ThemeManager for all color access (centralized)
- SUCCESS Button system based on GlowButton design (neon + bevel)
- SUCCESS Info bar at bottom for persistent context (vs tooltips)
- SUCCESS Cat panel moved to top-right (better space usage)
- SUCCESS Notifications slide from right, auto-stack (NotificationManager)

---

_This document will evolve as the brand identity develops. Update this file when making visual design decisions._

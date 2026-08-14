# P(Doom) UI Style Guide
## Visual Design System for Godot Implementation

_Last updated: 2026-07-20_
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
# Doom tiers (from ThemeManager -- the SINGLE source since L6/#617):
# DOOM_STOPS is the smooth colour ramp; DOOM_STATUS_BANDS the tier thresholds.
# NOMINAL <15 | ELEVATED <37 | HIGH <52 | SEVERE <67 | EXTREME <80
# | CATASTROPHIC <92 | TERMINAL <=100
# Use ThemeManager.get_doom_color / get_doom_stroke_color for colours and
# get_doom_band_index / get_doom_band / get_doom_status_label for tiers --
# never hardcode doom thresholds in a screen.

# UI feedback
success = Color(0.2, 0.9, 0.4)        # Completion, purchases
info = Color(0.4, 0.7, 1.0)           # Informational
warning = Color(0.95, 0.8, 0.2)       # Caution
error = Color(0.95, 0.3, 0.2)         # Errors, failures

# EE-7 per-turn resource delta chips (main_ui): green = helped, red = hurt
# (doom is sign-inverted: doom falling renders green)
delta_good = Color(0.35, 0.85, 0.40)  # _DELTA_GOOD
delta_bad = Color(0.95, 0.30, 0.25)   # _DELTA_BAD
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

### The 16px floor, and why it is not 14

Everything above is authored against a 1920x1080 base viewport, and
`project.godot` stretches it with `stretch/mode="canvas_items"` /
`aspect="expand"`. So on a 1280x720 laptop one authored pixel is **0.667
physical pixels**: a 14px label is ~9 real pixels and an 11px hint is ~7.

Consequence, and the rule: **no font a player reads while operating a control
goes below 16** (which is also Godot's own `Label` default -- several screens
were authoring BELOW the engine default). Secondary explanatory prose may sit
at 14; nothing goes under 14.

Corollary for panels with hand-authored sizes: growing the box does not fix
cramping, growing the type does. If a panel ends up materially bigger than the
size its contents need, the room belonged in the type scale.

### Pause menu (ESC) type scale

Enlarged 2026-08-06 after Pip in a preview build: *"Overall things feel a bit
cramped. If we increase the size of the Escape screen by 30%, the text could be
larger and friendlier."* Sizes live in `godot/scenes/pause_menu.tscn` and, for
the music picker, as named constants at the top of
`godot/scripts/ui/music_controls.gd`.

| Element | Was | Now |
|---|---|---|
| Panel title ("GAME PAUSED") | 36 | 40 |
| Section headers ("Audio Settings", "Music track") | 18 / 14 | 22 / 22 |
| Control rows (volume labels, percentages) | 14 | 18 |
| Buttons | 16 | 20 |
| Music picker (OptionButton) | 16 (theme default) | 20 |
| Music "now playing" readout | 12 | 16 |
| Music hint prose | 11 | 14 |
| Panel box | 640 x 600 | 800 x 792 |

The two section headers were 18 and 14 before -- the same kind of thing at two
sizes, one row apart. That reads as "cramped" and never as "a bug", which is
why `test_music_player_controls.gd` now pins them equal.

`test_music_player_controls.gd` also guards this table from BOTH sides: the
authored panel must be big enough for its contents **and not more than 40px
bigger**, so a future resize that adds padding instead of legibility fails.

### Game-over screen type scale

Enlarged 2026-08-07 after Pip on v0.14.0: *"the game-over screen is really hard
to read and still involves scrolling and old colour schemes. can you make it
bigger so I don't have to scroll?"*

Measured on the build he played, at 1920x1080: the stats box was 720x300 holding
**736px** of content across **32 lines, 14 of them visible** -- and line 32 was
`> Press ENTER for Leaderboard`, the only advertised route to the board.

| Element | Was | Now |
|---|---|---|
| Stats body (RichTextLabel) | 16 (Godot default) | 20 |
| Buttons | 16 | 20 |
| Button box | 150 x 50 | 160 x 56 (Leaderboard 190) |
| Stats box min height | 300 | 470 |
| Panel box | 780 x 460 | 920 x 800 |
| Lines of content (worst case) | 32 | 16 |
| Overflow | +436px, scrollbar shown | -40px, no scrollbar |

**Content was cut before the box grew.** The ledger rows collapsed from one line
per field to one line per category (resources: 7 lines -> 1; team: 4 -> 1), the
redundant "FINAL STATISTICS" header went, and the achievements block -- the one
unbounded region, which printed a title *and* a flavor line per unlock -- is
capped at three plus "(+N more)". Growing the box alone would have needed ~780px
of stats to show 32 lines at a legible size, which does not fit a 1080-unit
viewport alongside a title, a cause of death and a button row.

**Navigation does not live inside a scrolling region.** `> Press ENTER for
Leaderboard` is now `LeaderboardButton` in the button row. ENTER still works.

`test_game_over_is_readable.gd` guards the box from both sides (fit, and no more
than **80px** of slack -- wider than the pause menu's 40 because the death-cause
prose varies in wrapped height per run) and additionally asserts **zero scroll**:
content fits, no scrollbar is visible, and every rendered line is a visible line.

### Named web colours are not a palette

The game-over screen was written in Godot's built-in colour names -- `cyan`,
`gold`, `yellow`, `purple`, `blue`, `lime`, `dodger_blue`. Those are X11/CSS
defaults belonging to no theme this game ships, and this palette contains no
fully saturated primary. Two of them also failed WCAG AA on that panel's
`#170a1c` ground (contrast measured, not estimated):

| | contrast on the game-over panel | |
|---|---|---|
| `[color=blue]` #0000FF | **2.23:1** | fails AA, used for "Compute" |
| `[color=purple]` #A020F0 | **3.61:1** | fails AA, used for "Research" |
| `[color=red]` #FF0000 | 4.79:1 | passes, barely -- the cause-of-death line |
| after | 9.09 / 8.44 / 6.76:1 | |

The other nine were legible and merely garish (cyan 15.3:1, yellow 17.8:1). Both
problems are real; they are not the same problem.

Resource and staff readout colours now live in `ThemeManager.RESOURCE_COLORS` /
`STAFF_COLORS` as **`const`**, not in `ThemeData.colors`, so a theme swap cannot
move a contrast ratio a test has pinned -- the same reasoning that keeps the
pause menu's font sizes off `get_font_size()`, applied to a different property.
Hues are unchanged (money reads gold, compute blue, research purple) so this does
not diverge from the same mapping in `main_ui.gd`'s action tooltips; only the
luminance moved.

**Known duplication, deliberately not fixed here:** `main_ui.gd` carries that
same five-way mapping as raw BBCode names and still renders the dark ones. Its 65
colour literals are a separate change to a 3k-line monolith; the const exists so
that change has somewhere to land.

When computing contrast, linearise sRGB. `Color.get_luminance()` is the weighted
sRGB sum and does **not** linearise; using it overstates every dark colour, and an
earlier draft of this section quoted ratios that were wrong by roughly 2x on
`[color=blue]` for exactly that reason.

### Colours: local palettes are allowed, undocumented ones are not

`MusicControls` uses the pause menu's own amber `Color(0.91, 0.64, 0.24)` --
the panel border and the Audio Settings header, not `ThemeManager`'s generic
`warning` amber `Color(0.9, 0.7, 0.2)`, which is close but not equal and would
have split two adjacent headers. Sizes there are likewise NOT read from
`ThemeManager.get_font_size()`, because that returns the ACTIVE theme's scale
(`retro` sets `body_size` 18 where `default` sets 16) and the pause menu's
panel height is hand-authored and test-guarded against its contents -- a theme
swap would push the content past a box no test run could have seen.

### The diegetic register: the month review clipboard

`MonthReviewPanel` (`scripts/ui/month_review_panel.gd`) is the first surface
that is an OBJECT rather than a panel -- Pip, 2026-08-14: "the month review
screen could come in, like, clipboard form or some other diegetic form", the
same instinct as the 2026-08-12 "semi-diegetic" calendar ruling. Expect more of
these; this is the register they should share.

Diegetic here does NOT mean photorealistic. The rules that made it work:

- **It is still the terminal register.** Every word on the sheet is set in
  `TerminalTheme.mono_font()`, the same family as the WATCH feed and the plan
  screen. A paper object typeset in a proportional face would have left the
  world the rest of the UI implies.
- **Paper stays DIM.** `PAPER_TINT` takes the sheet art down to office-light
  manila. A scanned-document white next to this palette reads as a browser
  window, not as a thing on a desk. Same for the board: `BOARD_TINT` takes
  stained plywood down to furniture.
- **A drop shadow is what makes it an object,** not the colour. The board
  carries `shadow_size 26` at `Color(0,0,0,0.60)`; without it the panel reads
  as a rectangle again whatever is painted on it. Corollary: never set
  `clip_contents` on the panel itself to crop its surface art -- that clips the
  panel's own stylebox and takes the shadow with it. Put the texture in a
  clipping child (see `_add_surface`).
- **Surface art goes in as a `TextureRect` ground, `KEEP_ASPECT_COVERED`, not
  tiled.** Both surface textures carry a distinctive coffee ring; tiling a
  512px square across a 1100px sheet prints the ring twice and announces the
  texture as wallpaper.
- **Ink is a separate palette from the dark-panel palette.** `INK_GOOD` /
  `INK_BAD` are the printed renderings of main_ui's `_DELTA_GOOD` /
  `_DELTA_BAD` -- same MEANING (favourable green, adverse red, doom
  sign-inverted), remixed because colours tuned to survive a near-black panel
  go washy on manila. If you build another paper surface, take the inks from
  `MonthReviewPanel`, not from the HUD.
- **Overlays on textured art must be translucent.** `PAPER_SHADE` (the
  attention callout's wash) is `alpha 0.10`; an opaque box punched into the
  sheet reads as a widget stuck on the paper rather than a rule printed on it.
- **Keep the controls off the paper.** The forward-door button sits on the
  BOARD below the sheet, which preserves its B2/B3 teal-on-dark primary chrome
  -- teal ink on manila is unreadable.

Type on this panel is +2..+4pt over the generic event dialog (body 16 -> 19,
small 14 -> 17, button 16 -> 20) per Pip's 2026-08-14 note; the masthead is the
declared exception at 18 -> 24. This is a per-panel bump, NOT a global sweep.

Surface art currently used, both pre-existing and previously unreferenced:
`res://assets/textures/surfaces/tex_plywood_stained_512.png` (board) and
`res://assets/textures/surfaces/tex_grid_graphpaper_aged_512.png` (sheet).
Both are single-const slots so a purpose-drawn clipboard swaps in without
touching the layout.

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

## 17. Menu Chrome Tokens (2026-07-20 consistency pass)

Menus/modals were retoned from legacy slate-blue chrome to the palette in
`docs/art/palette.json` + `docs/art/PALETTE_AND_DOOM_INTENSITY.md` (warm-grime
+ heavy-outline heft; amber as the one saturated accent at rest). Full audit:
`docs/game-design/UI_MENU_CONSISTENCY_2026-07-20.md`.

```gdscript
# Menu button styleboxes (welcome, settings, pregame, config-confirm, guide)
menu_btn_bg = Color(0.18, 0.145, 0.278)        # #2E2547 doom-indigo fill
menu_btn_outline = Color(0.09, 0.04, 0.11)     # #170A1C heavy dark outline (rest)
menu_btn_hover_bg = Color(0.231, 0.192, 0.349) # lightened indigo
menu_btn_hover_border = Color(0.91, 0.64, 0.24)  # #E8A33D cozy amber
menu_btn_pressed_bg = Color(0.106, 0.078, 0.165) # #1B142A
menu_btn_active_border = Color(0.965, 0.659, 0)  # #F6A800 amber (pressed/focus)

# Modal panels (pause, whats-new, bug-report, player-guide)
modal_bg = Color(0.09, 0.04, 0.11)             # #170A1C deep aubergine
modal_border = Color(0.91, 0.64, 0.24, 0.8)    # dimmed amber frame

# Text accents
menu_header = Color(0.91, 0.64, 0.24)          # section headers (was ice blue)
menu_title = Color(0.914, 0.949, 0.949)        # #E9F2F2 off-white titles
external_link = Color(0.118, 0.765, 0.702)     # #1EC3B3 teal (AI Safety link)
```

### Consolidated into `godot/theme/menu_theme.tres` (#743)

These tokens now live in ONE shared `Theme` resource, `godot/theme/menu_theme.tres`,
applied at the root `Control` of every menu/screen (welcome, settings, pregame,
config-confirmation, player-guide, pause, keybind, leaderboard, game-over). It
replaced the five per-scene stylebox copies and also themes the stock controls
that used to fall back to default Godot gray: `Button`, `OptionButton` (+ its
`PopupMenu`), `HSlider`, `CheckButton`/`CheckBox`, `LineEdit`, and `Panel`. A
palette swap is now a one-file edit here (the chrome-vs-data asset policy).

- Emphasis CTAs (pregame/config-confirm "Launch Lab") use the `PrimaryButton`
  theme type variation (amber-bordered lighter fill at rest) instead of a bespoke
  inline stylebox.
- Runtime-created buttons (`ThemeManager.apply_button_style`) pull their chrome
  from this same resource, so the old pre-palette STEEL_DARK/ELECTRIC_BLUE/
  NEON_MAGENTA "Style Guide" colors are retired.
- Emoji stripped from menu labels to the ASCII house register (welcome
  "Leaderboard"/"AI Safety Info", pregame "Roll", leaderboard "Leaderboard"
  title, submenu close "X").
- Leaderboard = DEFERRED "institutional records room" (archives + classic
  high-score callbacks); only inherits the shared Theme for now. The deep re-skin
  lands after the title-screen theme decisions (Pip ruling 2026-07-21).

Rules of thumb:
- Resting buttons get the dark heavy outline; amber appears only on
  hover/press/focus and on the active modal frame.
- Blue is reserved for the weirdness axis (computers acting up), purple for
  band 3+ eldritch -- neither is menu chrome.
- In-game HUD amber uses the TerminalTheme register (`Color(1, 0.72, 0.2)`),
  not #F6A800; keep each register internally consistent.

---

_This document will evolve as the brand identity develops. Update this file when making visual design decisions._

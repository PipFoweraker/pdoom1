# Godot Design Assets & Style Guide

**Status**: Planning
**Priority**: After Phase 5 core features working
**Style**: Techno retro from pygame loading screen

---

## Design Direction

### Core Aesthetic
- **Source**: Pygame loading screen (cool techno retro style)
- **Goal**: Bring that vibe into Godot UI
- **Mood**: Retrofuturism, terminal-like, high-tech bureaucracy

### What User Wants
> "Can you comfortably import some of the UI elements from the cool techno retro style loading screen in the old UI? That's really all I liked."

---

## Asset Inventory

### Cat Images 🐱

**Location**: `assets/images/`

1. **Doom's Cat Throne** (GPT-generated)
   - File: `20250915_0948_Doom's Cat Throne_simple_compose_01k559ztmqefybe80mbvyqgyvd.png`
   - Use: Easter egg, achievement unlock, special event?

2. **Office Cat Default**
   - File: `pdoom1 office cat default png.png`
   - Use: Main cat easter egg sprite

3. **Small Doom Cat**
   - File: `small doom caat.png` (adorable typo!)
   - Use: UI icon, cursor, notification?

4. **Ominous Office Inferno** (GPT-generated)
   - File: `20250915_0952_Ominous Office Inferno_remix_01k55a6bc5fkxbq4txbwr8f61m.png`
   - Use: Background art, menu backdrop, late-game screen?

### Cat Easter Egg Original Concept
- **Status**: Stalled until now
- **Action**: Search docs/issues for original cat easter egg spec
- **Ideas**:
  - "Hire Office Cat" action (morale boost?)
  - Random cat appearances
  - Cat photos unlock as achievements
  - Cat-themed endings

---

## Pygame Style Reference

### Loading Screen Elements to Extract

**File to examine**: `pygame/ui.py` (loading screen code)

**Elements to port**:
1. **Color palette** - Techno retro colors (cyans, magentas, neons?)
2. **Font style** - Monospace terminal font?
3. **Layout patterns** - How were panels arranged?
4. **Visual effects** - Scanlines, glitches, CRT effects?
5. **Animation style** - Loading bar, text reveals?

### Action Items
- [ ] Extract pygame loading screen code
- [ ] Identify color hex values
- [ ] Find font files used
- [ ] Screenshot loading screen for reference
- [ ] Document layout measurements

---

## Godot Implementation Plan

### Phase 1: Extract & Document (1 session)
1. Run pygame game to see loading screen
2. Screenshot and annotate design elements
3. Extract colors to palette file
4. Find/copy font files
5. Document measurements and spacing

### Phase 2: Godot Theme (1 session)
1. Create Godot Theme resource
2. Apply colors to theme
3. Import font files
4. Style buttons, labels, panels
5. Test on existing UI

### Phase 3: Cat Integration (1 session)
1. Import cat images to Godot
2. Create cat easter egg system
3. Add "Hire Office Cat" action?
4. Cat-themed achievements
5. Random cat events

### Phase 4: Advanced Effects (optional)
1. CRT scanline shader
2. Text glitch effects
3. Animated backgrounds
4. Screen shake on events
5. Particle systems for flair

---

## Technical Notes

### Godot Theme System
```gdscript
# Create theme resource
var theme = Theme.new()

# Set colors
theme.set_color("font_color", "Label", Color("#00FFFF"))
theme.set_color("bg_color", "Panel", Color("#0A0A0A"))

# Set fonts
var font = load("res://assets/fonts/terminal.ttf")
theme.set_font("font", "Label", font)

# Apply to Control node
$MainUI.theme = theme
```

### Cat Sprite Example
```gdscript
# Random cat appearance
var cat_sprite = Sprite2D.new()
cat_sprite.texture = load("res://assets/images/small doom caat.png")
cat_sprite.position = Vector2(randf_range(100, 900), randf_range(100, 600))
add_child(cat_sprite)

# Fade in animation
var tween = create_tween()
tween.tween_property(cat_sprite, "modulate:a", 1.0, 1.0).from(0.0)
```

---

## Asset Migration Checklist

### From pygame/assets/ to godot/assets/

**Images**:
- [ ] Copy all cat images
- [ ] Copy loading screen graphics
- [ ] Copy any UI element sprites
- [ ] Copy background art

**Fonts**:
- [ ] Find pygame fonts
- [ ] Copy to godot/assets/fonts/
- [ ] Test in Godot

**Sounds** (for later):
- [ ] Copy sound effects
- [ ] Copy music tracks
- [ ] Test audio system

**Themes/Colors**:
- [ ] Document pygame color palette
- [ ] Create Godot theme file
- [ ] Apply to main scene

---

## Cat Easter Egg Ideas

### Option 1: Hidden Action
- "Hire Office Cat" appears after certain milestone
- Cost: $10k, -1 compute (cat sits on keyboard)
- Effect: +5 morale, random cat events

### Option 2: Random Encounters
- 5% chance each turn a cat appears
- Player can click cat for bonus
- Cat photos added to collection

### Option 3: Achievement System
- "Cat Hoarder" - Find all 4 cat images
- "Feline Overlord" - Hire 10 cats
- "Purr-ductivity" - Win game with cats employed

### Option 4: Late Game Content
- After Turn 20, cat research becomes available
- "Feline AI Alignment" study
- Cats vs. AI endgame scenario?

---

## Questions to Resolve

1. **Original Cat Concept**: Where is the original easter egg spec?
2. **Loading Screen**: Can we run pygame to screenshot it?
3. **Font Licensing**: Are pygame fonts free to use in Godot?
4. **Art Attribution**: Credit GPT-generated art?
5. **Gameplay Impact**: Should cats have mechanical effects or pure flavor?

---

## Timeline

**Phase 5** (Current): Focus on core features, no design work yet
**Phase 5 Complete**: Then start design migration
**Phase 6**: Parallel design work with feature implementation
**Phase 7**: Polish and final visual touches

---

## References

- Pygame UI code: `pygame/ui.py`
- Asset directory: `assets/images/`
- Godot theme docs: https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_theme_editor.html
- 2D sprite tutorial: https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html

---

**Status**: Documented, ready for implementation after Phase 5
**Excitement Level**: 🐱🎨 HIGH (cats + retro aesthetics!)

---

*"Plus an old easter egg about putting cats in the game that was stalled until now." - User, 2025-10-17*

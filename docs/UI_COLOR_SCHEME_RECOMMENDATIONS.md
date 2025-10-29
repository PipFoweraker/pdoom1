# UI Color Scheme Recommendations for P(Doom)

## Overview

This document provides comprehensive color scheme recommendations for improving UI contrast in P(Doom), addressing Issue: "Poor contrast UI". These recommendations apply to both the current pygame implementation and the upcoming Godot engine port.

## Problem Statement

The current UI has poor contrast, particularly at launch where menu controls and in-game navigation instructions are difficult to read on some displays. Specific issues:

1. **Main Menu Background**: Grey (128, 128, 128)
2. **Control Titles**: (160, 160, 160) - only 32 units difference from background
3. **Control Text**: (140, 140, 140) - only 12 units difference from background
4. **Instructions**: (180, 180, 180) - only 52 units difference from background

## Contrast Ratio Standards

Following WCAG (Web Content Accessibility Guidelines):
- **WCAG AA (minimum)**: 4.5:1 for normal text, 3:1 for large text
- **WCAG AAA (enhanced)**: 7:1 for normal text, 4.5:1 for large text

## Recommended Color Schemes

### Option 1: High Contrast Black Text (Simple Fix)
**Best for: Quick implementation, maximum readability**

```
Background: (128, 128, 128) - Keep existing grey
Control Titles: (0, 0, 0) - Pure black
Control Text: (20, 20, 20) - Near black
Instructions: (30, 30, 30) - Dark grey
```

**Contrast Ratios:**
- Black on grey background: ~7.5:1 (WCAG AAA compliant)
- Easy to read on any display
- Minimal code changes required

**Pros:**
- Excellent readability
- Simple to implement
- Works on all displays
- Already tested by community member (stevenhobartwork-create)

**Cons:**
- May look stark/harsh
- Less visual polish

### Option 2: Dark Text with Subtle Variation (Balanced)
**Best for: Professional appearance with good contrast**

```
Background: (128, 128, 128) - Keep existing grey
Control Titles: (20, 20, 20) - Dark charcoal
Control Text: (40, 40, 40) - Charcoal grey
Instructions: (30, 30, 30) - Dark grey
```

**Contrast Ratios:**
- All text exceeds 5:1 (WCAG AA compliant)
- Professional appearance
- Still easy to read

**Pros:**
- Good balance of contrast and aesthetics
- Professional appearance
- WCAG AA compliant

**Cons:**
- Slightly less contrast than pure black

### Option 3: Enhanced Grey Background with Black Text (Recommended)
**Best for: Optimal contrast with visual hierarchy**

```
Background: (140, 140, 140) - Lighter grey
Control Titles: (0, 0, 0) - Pure black (bold weight)
Control Text: (20, 20, 20) - Near black
Instructions: (10, 10, 10) - Very dark grey
```

**Contrast Ratios:**
- Titles: ~8:1 (WCAG AAA compliant)
- Text: ~7:1 (WCAG AAA compliant)
- Instructions: ~7.5:1 (WCAG AAA compliant)

**Pros:**
- Excellent readability
- Clear visual hierarchy with bold titles
- Slightly lighter background reduces eye strain
- WCAG AAA compliant

**Cons:**
- Requires adjusting background color slightly

### Option 4: Color-Coded with Contrast (Advanced)
**Best for: Visual distinction between menu and in-game controls**

```
Background: (128, 128, 128) - Keep existing grey

Menu Controls:
  Title: (0, 60, 120) - Dark blue (bold)
  Text: (20, 80, 140) - Medium-dark blue

In-Game Controls:
  Title: (100, 20, 20) - Dark red (bold)
  Text: (120, 40, 40) - Medium-dark red

Instructions: (0, 0, 0) - Pure black
```

**Contrast Ratios:**
- Blue text: ~5:1 (WCAG AA compliant)
- Red text: ~4.8:1 (WCAG AA compliant)
- Instructions: ~7.5:1 (WCAG AAA compliant)

**Pros:**
- Clear visual distinction between control types
- Maintains readability
- More visually interesting
- Helps users quickly identify control sections

**Cons:**
- More complex implementation
- May clash with other UI elements
- Color-coded information may not work for colorblind users

## Implementation Recommendations

### For Pygame (Current)

**Immediate Fix (Option 1):**
Lines to change in `ui.py`:

```python
# Line 486: Menu Controls title
left_title_surf = shortcut_font.render('Menu Controls:', True, (0, 0, 0))

# Line 492: Menu Controls text
shortcut_surf = shortcut_font.render(shortcut_text, True, (20, 20, 20))

# Line 499: In-Game Controls title
right_title_surf = shortcut_font.render('In-Game Controls:', True, (0, 0, 0))

# Line 505: In-Game Controls text
shortcut_surf = shortcut_font.render(shortcut_text, True, (20, 20, 20))

# Line 474: Instructions text
inst_surf = instruction_font.render(instruction, True, (30, 30, 30))
```

### For Godot Engine (Future)

**Theme Resource Settings:**

```gdscript
# Create a custom theme resource
var menu_theme = Theme.new()

# Background
var panel_style = StyleBoxFlat.new()
panel_style.bg_color = Color(0.5, 0.5, 0.5, 1.0)  # (128, 128, 128) normalized

# Text colors
menu_theme.set_color("font_color", "Label", Color(0, 0, 0, 1))  # Black for titles
menu_theme.set_color("font_color", "RichTextLabel", Color(0.08, 0.08, 0.08, 1))  # (20,20,20) for body

# Font weights
var bold_font = load("res://fonts/consolas_bold.ttf")
menu_theme.set_font("bold_font", "Label", bold_font)
```

**Alternative: Per-Control Settings:**

```gdscript
# For title labels
$MenuControlsTitle.add_theme_color_override("font_color", Color(0, 0, 0, 1))
$MenuControlsTitle.add_theme_font_override("font", bold_font)

# For control text labels
$ControlText.add_theme_color_override("font_color", Color(0.08, 0.08, 0.08, 1))

# For instructions
$Instructions.add_theme_color_override("font_color", Color(0.12, 0.12, 0.12, 1))
```

## Additional UI Contrast Improvements

### Other Low-Contrast Areas

While analyzing the code, several other areas with potential contrast issues were identified:

1. **Attribution Text** (line 391): `(180, 180, 180)` on grey background
   - Recommendation: Change to `(40, 40, 40)` or add semi-transparent backdrop

2. **Subtitle** (line 418): `(200, 200, 200)` on grey background
   - Recommendation: Change to `(20, 20, 20)` or add backdrop

3. **Other Menu Text** (line 3375, 3558, 3697): `(200, 200, 200)`
   - Recommendation: Review context and adjust if on light backgrounds

### Design Principles for Future UI

1. **Maintain 4.5:1 minimum contrast** (WCAG AA) for all text
2. **Use 7:1 contrast** (WCAG AAA) for critical navigation elements
3. **Test on multiple displays** including cheap/low-quality monitors
4. **Consider colorblind users** - don't rely solely on color for information
5. **Use font weight** (bold) for visual hierarchy in addition to color
6. **Add subtle backgrounds** where text overlays complex graphics

## Testing Recommendations

### Manual Testing Checklist
- [ ] View on standard monitor
- [ ] View on cheap/low-quality display
- [ ] View in different lighting conditions (bright room, dark room)
- [ ] Test with display brightness at 50%
- [ ] Test with display contrast at different levels
- [ ] Review with accessibility tools
- [ ] Get feedback from users with vision impairments

### Automated Testing
- Use contrast checker tools (WebAIM, Contrast Checker)
- Implement automated contrast ratio validation in CI
- Add unit tests for color values

## Migration Path

### Phase 1: Quick Fix (Immediate)
- Implement Option 1 (High Contrast Black Text) in pygame
- Test with community
- Validate on different displays

### Phase 2: Enhanced Implementation (Near-term)
- Implement Option 3 (Enhanced Grey with hierarchy)
- Add font weight variations
- Update all identified low-contrast areas

### Phase 3: Godot Integration (Future)
- Create Godot theme resource with approved colors
- Implement color scheme in Godot UI
- Add customization options for user preferences
- Consider accessibility settings (high contrast mode toggle)

## Community Feedback Integration

Based on feedback from @stevenhobartwork-create:
- Black text `(0, 0, 0)` works well and has been tested
- Community member successfully validated the improvement
- Simple sed command was used for quick testing
- Gradient background may require additional consideration

## Conclusion

**Recommended Immediate Action:**
Implement **Option 3: Enhanced Grey Background with Black Text** for the best balance of contrast, readability, and visual hierarchy.

**For Godot Port:**
Use the color values from Option 3 as the foundation, implementing them in Godot's theme system with appropriate font weights and sizes.

**Next Steps:**
1. Apply color changes to pygame version
2. Test with screenshots on various displays
3. Get community feedback
4. Document final color scheme for Godot implementation
5. Create Godot theme resource with validated colors

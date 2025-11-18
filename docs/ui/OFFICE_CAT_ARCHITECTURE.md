# Office Cat System Architecture

## Overview
The Office Cat is a single-display morale/wellness indicator that replaces the doom meter when adopted. Cat appears ONLY in the middle panel - no top bar icon.

## Component Structure

### Middle Panel Cat Display
**Location**: `main.tscn` → `TabManager/MainUI/ContentArea/MiddlePanel/OfficeCatSection`

**Purpose**: Replaces doom meter as primary health/morale indicator when cat is adopted

**Structure**:
```
OfficeCatSection (VBoxContainer, alignment=2 for bottom anchoring)
  ├─ OfficeCatLabel (Label)
  │   └─ Text: "OFFICE CAT" (orange #FF9900)
  └─ OfficeCatContainer (CenterContainer)
      └─ OfficeCat (Control, from office_cat.tscn)
          └─ VBox (VBoxContainer)
              ├─ CatPanel (PanelContainer 256x256)
              │   └─ CatTexture (TextureRect - doom variants)
              ├─ ContributorLabel (Label - contributor info)
              └─ DoomMeterContainer (Control - reserved space)
```

**Visibility Control**: [main_ui.gd:424-433](../godot/scripts/ui/main_ui.gd#L424-L433)
```gdscript
if state.get("has_cat", false):
    doom_meter_section.visible = false
    office_cat_section.visible = true
    office_cat.visible = true  # Override internal auto-hide
else:
    doom_meter_section.visible = true
    office_cat_section.visible = false
    office_cat.visible = false
```

**Properties**:
- Size: 280x350px minimum
- Layout: Container mode (`layout_mode = 2`)
- Bottom-anchored via parent VBoxContainer `alignment = 2`
- Interactive with contributor system
- Doom-level variants (happy → corrupted)

---

## Scene Files

### main.tscn (Primary UI)
Defines cat display location:
- Lines 213-231: Middle panel OfficeCatSection

**Removed**: Top bar CatPanel (no longer needed)

### office_cat.tscn (Reusable Component)
**Critical Setting**: `layout_mode = 2` (Container mode)
- **Why**: Respects parent CenterContainer positioning
- **Old Bug**: Was `layout_mode = 3` (Anchor mode) causing top-right positioning

---

## Script Files

### main_ui.gd (Main Controller)
**@onready References** (Lines 32-33):
```gdscript
@onready var office_cat = $ContentArea/MiddlePanel/OfficeCatSection/OfficeCatContainer/OfficeCat
@onready var office_cat_section = $ContentArea/MiddlePanel/OfficeCatSection
```

**Visibility Logic** (Lines 424-433):
```gdscript
if state.get("has_cat", false):
    doom_meter_section.visible = false
    office_cat_section.visible = true
    office_cat.visible = true
else:
    doom_meter_section.visible = true
    office_cat_section.visible = false
    office_cat.visible = false
```

**Doom Level Updates** (Lines 420-421):
```gdscript
if office_cat:
    office_cat.update_doom_level(doom / 100.0)
```

### office_cat.gd (Cat Display Controller)
**Initialization** (Lines 17-27):
- Starts `visible = false` (prevents flash before contributors load)
- Creates ContributorManager instance
- Loads contributor data asynchronously

**Doom Variant System**:
```gdscript
func update_doom_level(doom_percentage: float) -> void:
    current_doom_percentage = doom_percentage
    update_cat_for_doom_level(doom_percentage)
```

**Contributor Integration**:
- Loads from `res://data/contributors.json`
- Selects random contributor on load
- Updates cat image based on doom level (5 variants)

---

## Data Flow

1. **Game State** → `has_cat` boolean triggers visibility
2. **Doom Percentage** → Updates cat variant image
3. **Contributor System** → Provides cat images and metadata
4. **UI Updates** → `_update_ui_from_state()` handles all visibility

---

## Design Decisions

### Why Single Display (No Top Bar Icon)?
- Simplicity: Cat fully replaces doom meter, no duplicate indicators
- Focus: All attention on main health indicator in middle panel
- Consistency: Matches doom meter's single-location design

### Why Bottom-Anchored?
- Classic RTS UI pattern (StarCraft, X-COM)
- Health indicators locked to screen edge
- Consistent with doom meter positioning

### Why Force Visible?
- `office_cat.gd` auto-hides until contributors load
- We need immediate visibility on adoption
- Override prevents flashing/delay

---

## Bug Fixes Applied

### Issue: Cat appears in top-right of viewport
**Cause**: `office_cat.tscn` had `layout_mode = 3` (Anchor mode)
**Solution**: Changed to `layout_mode = 2` (Container mode)
**Fixed in**: office_cat.tscn:6

### Issue: Cat not visible after adoption
**Cause**: `office_cat.gd` sets `visible = false` in `_ready()`
**Solution**: Force `office_cat.visible = true` in main_ui.gd
**Fixed in**: main_ui.gd:428

### Issue: Removed top bar cat icon
**Cause**: Redundant display (was planned but not needed)
**Solution**: Removed CatPanel node from main.tscn
**Fixed in**: main.tscn (lines 142-151 removed)

---

## Future Enhancements

1. **Smooth Transitions**: Fade animation between doom meter ↔ cat
2. **Click Interaction**: Cycle through contributors
3. **Tooltips**: Show contributor info on hover
4. **Size Adaptation**: Responsive sizing based on panel space

---

## Related Documentation
- [UI Layout Guide](UI_LAYOUT_GUIDE.md) - Overall UI structure
- [Contributor System](../CONTRIBUTOR_SYSTEM.md) - Cat image management
- [UI Changes Log](../ui_changes_20251117/CHANGES_COMPLETED.md) - Recent updates

---

**Last Updated**: 2025-11-17
**Maintainer**: P(Doom) Development Team

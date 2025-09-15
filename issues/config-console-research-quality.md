# UX Enhancement: Config Console Area for Research Quality Settings

**Issue Type**: Enhancement  
**Priority**: Medium  
**Estimated Effort**: 2-3 hours  
**Target Branch**: `main` (after current hotfix merge)

## Problem Statement

Research quality settings (`Set Research Quality: Rushed/Standard/Thorough`) currently appear as separate action buttons mixed with actual game actions, creating UI clutter and poor UX flow. Players have to:

1. Find research quality buttons among other actions
2. Remember to set quality before doing research
3. Navigate through cluttered action lists

## Proposed Solution

Create a dedicated **Config Console Area** positioned below the End Turn button that consolidates game settings and configuration options.

### Design Concept
- **Location**: Below End Turn button (bottom-center area)
- **Visual Style**: Small panel with compact controls
- **Research Quality**: Traffic light style indicator showing current setting
  - 🔴 Rushed (fast, technical debt)
  - 🟡 Standard (balanced)
  - 🟢 Thorough (slow, high quality)
- **Expandable**: Future settings can be added (employee management, etc.)

### Benefits
1. **Cleaner Action Buttons**: Remove config actions from main action list
2. **Contextual Settings**: Research quality visible when doing research
3. **Scalable Design**: Foundation for future config options
4. **Better UX Flow**: Set once, applies to all research actions

## Technical Requirements

### UI Changes
- [ ] Create config console drawing function
- [ ] Position below end turn button
- [ ] Traffic light research quality indicator
- [ ] Click handling for quality changes

### Backend Integration
- [ ] Remove research quality from actions list
- [ ] Maintain existing research quality system
- [ ] Add config console to safe zones for UI positioning

### Visual Design
- [ ] Match existing UI theme and colors
- [ ] Compact design that doesn't dominate screen
- [ ] Clear visual feedback for current settings

## Implementation Notes

- Should integrate with existing visual feedback system
- Consider accessibility (colorblind-friendly indicators)
- Test with compact UI mode compatibility
- Maintain backward compatibility with save files

## Acceptance Criteria

- [ ] Research quality no longer appears in action buttons
- [ ] Config console shows current research quality setting
- [ ] Clicking console toggles between quality levels
- [ ] Visual indicator matches current setting
- [ ] Research actions use console setting automatically
- [ ] No impact on existing save game compatibility

## Future Enhancements

This config console could eventually house:
- Employee management shortcuts
- Automation toggles
- Display preferences
- Advanced game settings

---

**Created**: September 15, 2025  
**Session**: Visual improvements hotfix  
**Related**: Action button color coding, UI layout improvements

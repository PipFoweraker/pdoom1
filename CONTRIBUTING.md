# Contributing Guidelines

## Copilot and Automation Instructions

- Always install dependencies (`pip install -r requirements.txt`) before running code or tests.
- The `main` branch is stable and does not need runtime bug checks for every PR.
- Always include `import pygame` at the start of any Python file that uses pygame.
- Only update documentation files (README.md, PLAYERGUIDE.md) if there are user-facing changes.
- When updating DEVELOPERGUIDE.md, it's okay to be verbose and include a table of contents.

## UI Enhancement Development Protocols

When implementing UI and visual feedback enhancements, follow these protocols:

### Keyboard Shortcut Implementation
- **Mapping**: Use 1-9 keys for first 9 actions in action list
- **Visual Integration**: Display shortcuts as "[N] Action Name" on buttons  
- **Error Handling**: Provide clear error messages for insufficient resources/AP
- **Validation**: Use `execute_action_by_keyboard()` method with full validation
- **Sound Feedback**: Play `play_ap_spend_sound()` on successful action execution

### Action Point (AP) Feedback System
- **Visual Feedback**: Set `ap_glow_timer = 30` for 30-frame glow effect
- **Audio Feedback**: Use `SoundManager.play_ap_spend_sound()` for AP spend
- **Error Tracking**: Use `track_error()` method for easter egg detection  
- **Button States**: Update button states to reflect AP availability

### Employee Blob Positioning
- **Safe Zones**: Use `_calculate_blob_position()` to avoid UI overlap
- **Screen Responsive**: Scale positions with screen dimensions (w, h parameters)
- **Grid Layout**: Automatic grid arrangement within safe zones
- **Animation**: Support smooth transitions for blob movement

### Testing Requirements
- **Keyboard Tests**: Test all shortcut keys with valid/invalid conditions
- **AP Feedback Tests**: Verify visual and audio feedback triggering
- **Blob Position Tests**: Validate safe zone positioning and screen scaling
- **Error Handling Tests**: Test easter egg system and error tracking

### Sound Integration
- **Sound Manager**: Use existing `SoundManager` class for audio feedback
- **Error Beeps**: Use `play_error_beep()` for easter egg system
- **AP Sounds**: Use `play_ap_spend_sound()` for Action Point feedback
- **Headless Testing**: Ensure sound systems work in headless environments

### Documentation Updates
- **DEVELOPERGUIDE.md**: Add verbose technical details and code examples
- **PLAYERGUIDE.md**: Update controls section with keyboard shortcuts
- **Test Coverage**: Document all new test cases and their purposes

Cheers!
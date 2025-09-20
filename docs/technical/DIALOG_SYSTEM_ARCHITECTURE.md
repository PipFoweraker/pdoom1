"""
Dialog System Architecture Documentation

This document describes the dialog system architecture implemented to fix
non-responsive dialog actions (Technical Debt, Intelligence, Media & PR).

## Overview

The P(Doom) dialog system provides a modal interface for complex player
decisions that require selecting from multiple options. This system was
enhanced to fix non-responsive dialog actions and leverage the existing
DialogManager for better maintainability.

## Architecture Components

### 1. Dialog Trigger Functions (Game State)
Location: `src/core/game_state.py`

Each dialog action has a trigger function that creates pending dialog state:

- `_trigger_intelligence_dialog()` - Creates intelligence operations dialog
- `_trigger_media_dialog()` - Creates media & PR operations dialog  
- `_trigger_technical_debt_dialog()` - Creates technical debt management dialog

**Structure:**
```python
def _trigger_media_dialog(self) -> None:
    """Trigger media & PR operations dialog."""
    # Create dialog options based on current game state
    options = self._get_available_media_options()
    
    # Set pending dialog state
    self.pending_media_dialog = {
        'title': 'Media & PR Operations',
        'description': 'Select a media and public relations operation to execute.',
        'options': options
    }
```

### 2. Dialog UI Rendering (UI Layer)
Location: `src/ui/dialogs.py`

Each dialog type has a dedicated rendering function:

- `draw_intelligence_dialog()` - Renders intelligence dialog UI
- `draw_media_dialog()` - Renders media & PR dialog UI
- `draw_technical_debt_dialog()` - Renders technical debt dialog UI

**Structure:**
```python
def draw_media_dialog(screen: pygame.Surface, media_dialog: Dict[str, Any], 
                     w: int, h: int) -> List[Dict[str, Any]]:
    """
    Draw the media & PR operations dialog.
    
    Returns:
        List of clickable rect information for click handling
    """
    # Render dialog background, title, description
    # Render option buttons with hover effects
    # Render cancel button
    # Return clickable rectangles for event handling
```

### 3. Dialog Integration (Main Game Loop)
Location: `main.py`

Dialog rendering and click handling are integrated into the main game loop:

**Rendering Integration (~Line 2970):**
```python
# Draw media dialog if active
if game_state and game_state.pending_media_dialog:
    from src.ui.dialogs import draw_media_dialog
    cached_media_dialog_rects = draw_media_dialog(
        screen, game_state.pending_media_dialog, SCREEN_W, SCREEN_H)
else:
    cached_media_dialog_rects = None
```

**Click Handling Integration (~Line 2070):**
```python
# Check for media dialog clicks
elif game_state and game_state.pending_media_dialog and cached_media_dialog_rects:
    for rect_info in cached_media_dialog_rects:
        if rect_info['rect'].collidepoint(mx, my):
            if rect_info['type'] == 'media_option':
                game_state.select_media_option(rect_info['option_id'])
            elif rect_info['type'] == 'cancel':
                game_state.dismiss_media_dialog()
```

### 4. Dialog Management (Centralized)
Location: `src/core/dialog_manager.py`

The DialogManager provides centralized dialog state management:

```python
class DialogManager:
    @staticmethod
    def dismiss_dialog(game_state, dialog_type: str) -> None:
        """Universal dialog dismiss function."""
        dialog_attr = f'pending_{dialog_type}_dialog'
        if hasattr(game_state, dialog_attr):
            setattr(game_state, dialog_attr, None)
    
    @staticmethod
    def has_pending_dialog(game_state, dialog_type: str) -> bool:
        """Check if a dialog of given type is pending."""
        dialog_attr = f'pending_{dialog_type}_dialog'
        return (hasattr(game_state, dialog_attr) and 
                getattr(game_state, dialog_attr) is not None)
```

## Dialog Types

### Intelligence Dialog
- **Purpose**: Intelligence gathering operations
- **Options**: Scout Opponents, Espionage, General News Reading, Counter-Intelligence
- **Integration**: Fully functional (reference implementation)

### Media & PR Dialog  
- **Purpose**: Media and public relations operations
- **Options**: Press Release, Exclusive Interview, Damage Control, Social Media Campaign, Community Outreach
- **Integration**: ✅ **Fixed** - Now fully functional

### Technical Debt Dialog
- **Purpose**: Technical debt management operations  
- **Options**: Refactoring Sprint, Technical Debt Audit, Code Review
- **Integration**: ✅ **Fixed** - Now fully functional

## Dialog Option Structure

Each dialog option must include these fields:

```python
{
    'id': str,              # Unique identifier for the option
    'name': str,            # Display name for the option
    'description': str,     # Brief description of what the option does
    'cost': int,           # Money cost to execute the option
    'ap_cost': int,        # Action points cost to execute the option
    'available': bool,     # Whether the option can be selected
    'details': str         # Optional additional details
}
```

## Dialog Workflow

1. **Trigger**: User clicks dialog action button (e.g., "Media & PR")
2. **Action Execution**: Action's upside lambda calls `gs._trigger_*_dialog()`
3. **State Creation**: Trigger function creates `pending_*_dialog` state
4. **UI Rendering**: Main loop detects pending dialog and calls `draw_*_dialog()`
5. **Click Handling**: Main loop processes clicks on dialog elements
6. **Option Selection**: Clicks call `select_*_option()` or `dismiss_*_dialog()`
7. **State Cleanup**: Dialog state is cleared after selection/cancellation

## Click Handling Pattern

All dialogs follow this click handling pattern:

```python
if rect_info['type'] == 'dialog_option':
    # Execute the selected option
    game_state.select_dialog_option(rect_info['option_id'])
elif rect_info['type'] == 'cancel':
    # Dismiss the dialog without action
    game_state.dismiss_dialog()
```

## Modal Behavior

Dialogs implement modal behavior:
- Clicks inside dialog area are handled by dialog logic
- Clicks outside dialog area dismiss the dialog
- Only one dialog can be active at a time
- Dialogs block other UI interactions while active

## Error Handling

The dialog system includes robust error handling:
- Missing options are handled gracefully
- Unavailable options are rendered but not clickable
- Dialog state is validated before rendering
- Click handling includes bounds checking

## Performance Considerations

- Dialog rendering is only performed when dialogs are active
- Clickable rectangles are cached between frames
- Dialog options are generated dynamically based on game state
- UI rendering uses efficient pygame drawing operations

## Testing

Comprehensive test suite at `tests/test_dialog_system_integration.py`:
- Dialog trigger function validation
- UI rendering function testing
- Click handling workflow testing
- DialogManager integration testing
- End-to-end workflow validation

## Future Enhancements

Potential areas for improvement:
- Dialog animation system for smoother transitions
- Keyboard navigation support for accessibility
- Dialog stacking for complex multi-step workflows
- Enhanced visual feedback for option availability
- Customizable dialog themes and styling

## Troubleshooting

Common issues and solutions:

**Dialog doesn't appear:**
- Check that trigger function creates pending dialog state
- Verify dialog rendering is integrated in main loop
- Ensure dialog has valid options array

**Dialog appears but clicks don't work:**
- Check click handling is integrated in main loop
- Verify cached rectangles are being created
- Ensure selection functions exist in game state

**Dialog options show as unavailable:**
- Check option availability logic in trigger function
- Verify game state meets option requirements
- Review cost calculations and resource availability
"""
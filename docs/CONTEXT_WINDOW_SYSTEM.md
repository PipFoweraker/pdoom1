# Context Window System

## Overview

The Context Window is a new UI feature that addresses text overflow on action and upgrade buttons by moving detailed information to a dedicated panel at the bottom of the screen. This system provides a cleaner interface while maintaining access to important game information.

## Features

### 1. Persistent Information Display
- **Bottom Panel**: Always visible at the bottom of the screen in non-tutorial mode
- **Dynamic Content**: Shows detailed information about hovered actions, upgrades, or default game state
- **Configurable**: Height and behavior can be customized through configuration files

### 2. Improved Button Design
- **Cleaner Text**: Action and upgrade buttons show only essential text (name + shortcut key)
- **No Overflow**: Detailed descriptions moved to context window
- **Compact Mode**: Utilizes existing compact UI system for icon-based buttons

### 3. Interactive Features
- **Hover Detection**: Automatically updates when hovering over UI elements
- **Minimize/Maximize**: Toggle button to collapse/expand the context window
- **Responsive Layout**: Adjusts to different screen sizes

## Implementation Details

### Core Functions

#### Context Information Generation
```python
def create_action_context_info(action, game_state, action_idx):
    """Create context info for an action to display in the context window."""
    # Returns dict with 'title', 'description', 'details'

def create_upgrade_context_info(upgrade, game_state, upgrade_idx):
    """Create context info for an upgrade to display in the context window."""
    # Returns dict with 'title', 'description', 'details'

def get_default_context_info(game_state):
    """Get default context info when nothing is hovered."""
    # Returns dict with general game state information
```

#### UI Integration
```python
def draw_context_window(screen, context_info, w, h, minimized=False, config=None):
    """Draw the context window at the bottom of the screen."""
    # Configurable height and positioning
    # Returns context_rect and button_rect for click handling
```

### Configuration System

The context window behavior is controlled through the configuration system:

```json
{
  "ui": {
    "context_window": {
      "enabled": true,
      "always_visible": true,
      "minimized": false,
      "height_percent": 0.13,
      "minimized_height_percent": 0.06,
      "position": "bottom"
    }
  }
}
```

#### Configuration Options
- **enabled**: Enable/disable the context window system
- **always_visible**: Show context window even when nothing is hovered
- **minimized**: Start the window in minimized state
- **height_percent**: Height as percentage of screen height (expanded)
- **minimized_height_percent**: Height when minimized
- **position**: Position on screen (currently only "bottom" supported)

### Layout Adjustments

Several UI elements were repositioned to accommodate the context window:

#### Safe Zones
- Event log area reduced from 27% to 14% height
- End turn button moved up by 14% of screen height
- Context window reserved bottom 13% of screen

#### Button Positioning
- Traditional end turn button: moved from y=88% to y=74%
- Compact end turn button: moved from bottom-2% to bottom-15%
- Event log: height reduced to prevent overlap

## Usage Examples

### Basic Hover Information
When hovering over an action button:
```
Title: [1] Grow Community
Description: +Reputation, possible staff; costs money.
Details:
- Cost: $25
- Action Points: 1
- Delegatable: Requires 1 admin staff, 0 AP, 100% effective
```

### Default Information
When no UI element is hovered:
```
Title: P(Doom) Context Panel
Description: Hover over actions or upgrades to see detailed information here.
Details:
- Turn 5
- Money: $500
- Action Points: 3
- p(Doom): 25
```

### Upgrade Information
When hovering over an upgrade:
```
Title: Upgrade Computer System
Description: Boosts research effectiveness (+1 research per action)
Details:
- Cost: $200
- ✓ Available for purchase
```

## Technical Implementation

### Game State Integration
The system integrates with existing hover tracking in `GameState`:
- `hovered_action_idx`: Tracks which action is currently hovered
- `hovered_upgrade_idx`: Tracks which upgrade is currently hovered
- `context_window_minimized`: Tracks minimize state

### UI Mode Detection
```python
use_compact_ui = not getattr(game_state, 'tutorial_enabled', True)
show_context_window = use_compact_ui or always_visible
```

### Responsive Design
The context window automatically adjusts:
- Font sizes scale with screen dimensions
- Layout adapts to available space
- Details shown horizontally to maximize information density

## Benefits

### User Experience
- **Reduced Clutter**: Clean button interface without text overflow
- **Better Information Access**: Detailed information always available when needed
- **Persistent Reference**: Game state information always visible
- **Configurable**: Users can customize behavior to their preferences

### Technical Benefits
- **Modular Design**: Context information generation separated from UI rendering
- **Configuration Support**: Easy to modify behavior without code changes
- **Backward Compatibility**: Tutorial mode retains original button descriptions
- **Extensible**: Easy to add new types of context information

## Future Enhancements

### Potential Improvements
1. **Multiple Positions**: Support for top/side positioning
2. **Custom Content**: Allow mods to add custom context information
3. **History**: Track recently viewed information
4. **Tooltips**: Integration with existing tooltip system
5. **Animations**: Smooth transitions when content changes

### Configuration Extensions
```json
{
  "context_window": {
    "animations": {
      "enabled": true,
      "duration": 300,
      "easing": "ease-in-out"
    },
    "content": {
      "show_shortcuts": true,
      "show_costs": true,
      "show_availability": true,
      "max_details": 4
    }
  }
}
```

## Testing

The implementation includes comprehensive testing:
- Context information generation
- Configuration integration
- Hover state management
- UI positioning and layout
- Error handling and fallbacks

Run the test suite:
```bash
python test_context_window.py
```

## Migration Notes

### For Existing Users
- Context window appears automatically in non-tutorial mode
- Tutorial mode behavior unchanged for compatibility
- Configuration can disable feature if not desired

### For Developers
- New helper functions available for context information
- Existing hover tracking system extended
- Configuration system supports new UI settings
- Safe zone calculations updated for layout changes

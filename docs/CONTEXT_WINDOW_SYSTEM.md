# Context Window System

## Overview

The Context Window is a retro-styled UI feature that addresses text overflow on action and upgrade buttons by moving detailed information to a dedicated DOS-style panel at the bottom of the screen. This system provides a cleaner interface while maintaining access to important game information with a distinctive 80's terminal aesthetic.

## Features

### 1. Retro Terminal Design
- **80's Aesthetic**: Distinctive techno-green color scheme reminiscent of old computer terminals
- **DOS Typography**: All text rendered in ALL CAPS using Courier font for authentic retro feel
- **Bottom Panel**: Takes up 8-10% of screen height, always visible in non-tutorial mode
- **Terminal Colors**: Light readable green background with bright green text

### 2. Smart Action Filtering
- **Hide Locked Actions**: Only shows actions that are currently available/unlocked
- **Dynamic Layout**: Button layout adjusts based on number of available actions
- **Clean Interface**: Reduces visual clutter by hiding unavailable options

### 3. Improved Button Design
- **Cleaner Text**: Action and upgrade buttons show only essential text (name + shortcut key)
- **No Overflow**: Detailed descriptions moved to context window
- **Hover Integration**: Full information appears in context window on mouse hover
- **Compact Mode**: Utilizes existing compact UI system for icon-based buttons

### 4. Interactive Features
- **Hover Detection**: Automatically updates when hovering over UI elements
- **Minimize/Maximize**: Toggle button to collapse/expand the context window
- **Responsive Layout**: Adjusts to different screen sizes
- **Smart Mapping**: Proper click and hover handling for filtered actions

## Implementation Details

### Action Filtering System
```python
# Filter actions to only show available ones (hide locked actions)
available_actions = []
available_action_indices = []
for idx, action in enumerate(game_state.actions):
    # Check if action is unlocked (no rules or rules return True)
    if not action.get("rules") or action["rules"](game_state):
        available_actions.append(action)
        available_action_indices.append(idx)

# Store mapping for click handling
game_state.display_to_action_index_map = available_action_indices
```

### Core Functions

#### Context Information Generation
```python
def create_action_context_info(action, game_state, action_idx):
    """Create context info for an action to display in the context window."""
    # Returns dict with 'title', 'description', 'details'
    # Enhanced with delegation info and availability status

def create_upgrade_context_info(upgrade, game_state, upgrade_idx):
    """Create context info for an upgrade to display in the context window."""
    # Returns dict with 'title', 'description', 'details'
    # Shows purchase status and availability

def get_default_context_info(game_state):
    """Get default context info when nothing is hovered."""
    # Returns dict with general game state information
    # Shows turn, money, AP, and p(Doom) in DOS style
```

#### UI Integration
```python
def draw_context_window(screen, context_info, w, h, minimized=False, config=None):
    """Draw the retro-styled context window at the bottom of the screen."""
    # 80's techno-green color scheme
    # DOS-style Courier font with ALL CAPS text
    # Configurable height (8-10% of screen)
    # Returns context_rect and button_rect for click handling
```

## Styling Details

### Color Scheme
- **Background**: `(40, 80, 40)` - Dark techno green
- **Border**: `(100, 200, 100)` - Bright green outline
- **Header**: `(60, 120, 60)` - Medium green for title bar
- **Text Colors**:
  - Title: `(200, 255, 200)` - Bright green
  - Description: `(180, 255, 180)` - Medium bright green
  - Details: `(150, 220, 150)` - Medium green

### Typography
- **Font**: Courier (monospace for DOS feel)
- **Style**: ALL CAPS for authentic terminal aesthetic
- **Sizes**: Responsive based on screen height

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
- v Available for purchase
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

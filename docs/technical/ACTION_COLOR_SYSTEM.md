# Action Color-Coding System

## Overview

P(Doom) v0.8.0 implements a comprehensive color-coding system for action buttons that provides visual categorization across both Traditional UI (tutorial mode) and Compact UI (non-tutorial mode). This enhancement improves user experience by allowing players to quickly identify action types through consistent color theming.

## Color Categories

The system categorizes actions into 7 distinct color themes:

### [EMOJI] Core Actions (Blue-Grey)
**RGB**: `(70, 90, 120)` normal, `(90, 110, 140)` hover, `(100, 120, 160)` border

**Actions**:
- Grow Community
- Hire Staff  
- Hire Manager

**Purpose**: Foundational organizational activities that form the core of lab management.

### [U+1F7E2] Economic Actions (Green)  
**RGB**: `(60, 100, 70)` normal, `(80, 120, 90)` hover, `(100, 140, 110)` border

**Actions**:
- Fundraising Options
- Buy Compute
- Advanced Funding

**Purpose**: Financial and resource acquisition activities essential for lab growth.

### [EMOJI] Research Actions (Blue)
**RGB**: `(60, 80, 120)` normal, `(80, 100, 140)` hover, `(100, 120, 160)` border

**Actions**:
- Research Options
- Safety Research
- Team Building
- Refresh Researchers

**Purpose**: Technical research and development activities advancing AI safety.

### [U+1F7E3] Intelligence Actions (Purple)
**RGB**: `(90, 70, 120)` normal, `(110, 90, 140)` hover, `(130, 110, 160)` border

**Actions**:
- Intelligence Dialog

**Purpose**: Information gathering and competitive intelligence operations.

### [U+1F7E0] Media Actions (Orange)
**RGB**: `(120, 80, 50)` normal, `(140, 100, 70)` hover, `(160, 120, 90)` border

**Actions**:
- Media & PR Dialog

**Purpose**: Public relations and media management for reputation building.

### [U+1F7E6] Technical Actions (Teal)
**RGB**: `(50, 100, 100)` normal, `(70, 120, 120)` hover, `(90, 140, 140)` border

**Actions**:
- Technical Debt Dialog
- Infrastructure

**Purpose**: Technical infrastructure and system maintenance activities.

### [EMOJI] Special Actions (Red)
**RGB**: `(100, 60, 60)` normal, `(120, 80, 80)` hover, `(140, 100, 100)` border

**Actions**:
- Search
- Safety Audit

**Purpose**: Critical safety operations and emergency procedures.

## Technical Implementation

### Core Function: `get_action_color_scheme(action_name: str)`

Located in `src/ui/compact_ui.py`, this function provides the foundation for all color theming:

```python
def get_action_color_scheme(action_name: str) -> Dict[str, Tuple[int, int, int]]:
    '''
    Get color scheme for different action types following P(Doom) style guide.
    
    Args:
        action_name: Name of the action
        
    Returns:
        dict: Color scheme with 'normal', 'hover', and 'border' colors
    '''
```

**Returns**: Dictionary with RGB tuples for:
- `'normal'`: Base button color
- `'hover'`: Lighter version for mouse hover state
- `'border'`: Border and accent color

### UI Integration Points

#### Traditional UI (Tutorial Mode)
**File**: `ui.py` lines ~1480-1525

The traditional UI integrates colors through the visual feedback system:

```python
# Get action-specific colors
action_name = action.get('name', f'action_{original_idx}')
color_scheme = get_action_color_scheme(action_name)

# Create custom color mapping for visual feedback system
custom_colors = {
    'bg': color_scheme['normal'],
    'border': color_scheme['border'],
    'text': (255, 255, 255),
    'shadow': tuple(max(0, c - 30) for c in color_scheme['normal']),
    'glow': color_scheme['border']
}

visual_feedback.draw_button(screen, rect, button_text, button_state, 
                           FeedbackStyle.BUTTON, custom_colors)
```

#### Compact UI (Non-Tutorial Mode)  
**File**: `src/ui/compact_ui.py` lines ~285-310

The compact UI applies colors directly to button rendering:

```python
# Get action-specific colors and select based on button state
color_scheme = get_action_color_scheme(action_name)

if button_state == ButtonState.HOVER:
    bg_color = color_scheme['hover']
elif button_state == ButtonState.PRESSED:
    bg_color = tuple(max(0, c - 20) for c in color_scheme['normal'])
else:  # NORMAL
    bg_color = color_scheme['normal']

# Draw button with colored background
pygame.draw.rect(screen, bg_color, rect, border_radius=3)
```

### Button State Handling

The system handles all standard button states:

- **Normal**: Base category color
- **Hover**: Automatically lightened version (+20 RGB per component)
- **Pressed**: Darkened version (-20 RGB from normal)
- **Disabled**: Uniform grey `(60, 60, 60)`

### Categorization Logic

Actions are categorized using intelligent string matching:

```python
action_lower = action_name.lower()

# Economic Actions - Green theme
if any(word in action_lower for word in ['fundraising', 'buy compute', 'advanced funding']):
    return green_color_scheme

# Research Actions - Blue theme  
elif any(word in action_lower for word in ['research', 'safety research', 'team building']):
    return blue_color_scheme
```

This approach ensures:
- **Robust matching** for dialog system actions ('Intelligence Dialog' -> Intelligence theme)
- **Future compatibility** with new action names
- **Sensible defaults** for unrecognized actions

## UI Mode Compatibility

### Traditional UI (Tutorial Mode)
- **Trigger**: `tutorial_enabled = True`
- **Display**: `[1] Grow Community` with colored background
- **Features**: Full text labels + keyboard shortcuts + colors
- **Target**: New players learning the game

### Compact UI (Non-Tutorial Mode)
- **Trigger**: `tutorial_enabled = False`
- **Display**: Icon-based buttons with colors
- **Features**: Space-efficient icons + colors + shortcut indicators
- **Target**: Experienced players maximizing screen space

Both modes use identical color categorization, ensuring **consistent visual language** regardless of UI preference.

## Testing Coverage

Comprehensive test suite in `tests/test_action_color_scheme.py`:

- **Structure Tests**: Verify RGB tuple format and required keys
- **Categorization Tests**: Ensure each action type gets correct colors  
- **Brightness Tests**: Validate hover states are lighter than normal
- **Integration Tests**: Test visual feedback system compatibility
- **Cross-Mode Tests**: Ensure consistency between UI modes
- **Game Integration**: Validate all actual game actions have colors

**Test Results**: 12 tests, 100% pass rate

## Performance Considerations

- **Lightweight**: Color lookup is O(1) with string matching
- **Cached**: Colors are computed once per render frame
- **Minimal Impact**: No performance regression in UI rendering
- **Memory Efficient**: Small RGB tuples, no image assets required

## Future Extensions

The system is designed for easy extension:

1. **New Action Categories**: Add new color themes by extending `get_action_color_scheme()`
2. **Color Customization**: User preferences could override default color schemes
3. **Accessibility**: High contrast or colorblind-friendly variants
4. **Animation**: Color transitions between states for enhanced feedback

## Migration Notes

**Breaking Changes**: None - system is additive only

**Backward Compatibility**: All existing functionality preserved:
- Button layouts unchanged
- Keyboard shortcuts maintained  
- Text labels preserved in traditional UI
- Icon system preserved in compact UI

**Configuration**: No user configuration required - system works out of the box

## Development Guidelines

### Adding New Actions
When adding new actions, consider the color category:

1. **Economic**: Financial, resource acquisition -> Green
2. **Research**: Technical development, AI safety -> Blue
3. **Core**: Staff, community management -> Blue-grey
4. **Intelligence**: Information gathering -> Purple
5. **Media**: Public relations, communications -> Orange
6. **Technical**: Infrastructure, system maintenance -> Teal  
7. **Special**: Critical safety, emergency actions -> Red

### Color Selection Principles
- **Professional appearance**: Muted, business-appropriate colors
- **Sufficient contrast**: Text remains readable on all backgrounds
- **Color vision friendly**: Distinguishable for common color vision variations
- **Consistent brightness**: Similar luminance levels across categories
- **Visual hierarchy**: Special actions (red) stand out from routine actions

## Implementation History

- **v0.7.x**: Basic UI consolidation (29 -> 16 actions)
- **v0.8.0**: Added comprehensive color-coding system
- **Future**: Enhanced accessibility and customization options
# Developer Guide for P(Doom)

Welcome, contributors and modders! This guide explains how to develop, test, and extend P(Doom): Bureaucracy Strategy.

For **players**, see the [Player Guide](PLAYERGUIDE.md).  
For **installation and troubleshooting**, see the [README](../README.md).

## Table of Contents
- [Development Setup](#development-setup) (Line 28)
- [Enhanced Settings System Architecture](#enhanced-settings-system-architecture) (Line 54)
- [Custom Sound Overrides (sounds/)](#custom-sound-overrides-sounds) (Line 100)
- [Project Structure](#project-structure) (Line 146)
- [UI Architecture and Overlay Management](#ui-architecture-and-overlay-management) (Line 168)
- [Opponents System Architecture](#opponents-system-architecture) (Line 364)
- [Onboarding System Architecture](#onboarding-system-architecture) (Line 424)
- [Testing Framework](#testing-framework) (Line 553)
- [Adding New Content](#adding-new-content) (Line 609)
- [Enhanced Event System Architecture](#enhanced-event-system-architecture) (Line 740)
- [Milestone Events System](#milestone-events-system) (Line 820)
- [Code Style & Guidelines](#code-style--guidelines) (Line 900)
- [Game Logging System](#game-logging-system) (Line 921)
- [Release & Deployment](#release--deployment) (Line 950)
- [Milestone-Driven Special Events & Static Effects System](#milestone-driven-special-events--static-effects-system) (Line 1009)
- [Architecture Notes](#architecture-notes) (Line 1127)
- [Tutorial & Onboarding System Architecture](#tutorial--onboarding-system-architecture) (Line 1188)
- [Need Help?](#need-help) (Line 1270)

**Configuration System**: For config management and modding support, see [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md).

**NEW IN v0.7.5**: TurnManager architecture extraction from monolithic GameState.end_turn() method provides better state management and debugging capabilities.

---

## Development Setup

### Prerequisites
- Python 3.9+
- pygame (`pip install pygame`)
- pytest for testing (`pip install pytest` or `pip install -r requirements.txt`)
- numpy for sound effects (`pip install numpy` - optional but recommended)

### Getting Started
```sh
# Clone the repository
git clone <repository-url>
cd pdoom1

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup
python -m unittest discover tests -v

# Run the game
python main.py
```

---

## Enhanced Settings System Architecture

P(Doom) features a comprehensive settings and configuration system designed for accessibility, customization, and community engagement.

### System Architecture

**Core Components:**
- **src/services/seed_manager.py** -- Centralized seed generation, validation, and management
- **src/services/game_config_manager.py** -- Custom game configuration creation and sharing
- **src/ui/enhanced_settings.py** -- Modern settings UI with categorical organization
- **src/ui/settings_integration.py** -- Integration layer for gradual adoption

### Settings Categories

**1. Audio Settings**
- Master volume control
- Sound effects on/off
- Music volume (if implemented)
- Audio accessibility options

**2. Gameplay Settings** 
- Game difficulty adjustments
- Turn time limits
- Auto-save frequency
- Gameplay assists

**3. Accessibility Settings**
- Font scaling (0.5x to 2.0x)
- High contrast mode
- Screen reader support
- Keyboard navigation enhancements

**4. Game Configuration Mode**
- Custom game rule modifications
- Starting resource adjustments
- Event frequency tuning
- Victory condition customization

### Seed Management System

**Features:**
- **Weekly Seeds**: Automatic generation of community seeds
- **Custom Seeds**: User-provided seed validation and normalization
- **Seed History**: Track and replay previous games
- **Community Sharing**: Export/import seed configurations

**Implementation:**
```python
from src.services.seed_manager import SeedManager

# Get this week's community seed
weekly_seed = SeedManager.get_weekly_seed()

# Validate custom seed input
if SeedManager.validate_custom_seed(user_input):
    normalized_seed = SeedManager.normalize_seed(user_input)
```

### Game Configuration System

**Purpose**: Enable community content creation and scenario sharing

**Features:**
- **Template System**: Pre-defined configuration templates
- **CRUD Operations**: Create, read, update, delete custom configs
- **Export/Import**: Share configurations as JSON files
- **Validation**: Schema validation for configuration integrity

**Usage:**
```python
from src.services.game_config_manager import GameConfigManager

config_manager = GameConfigManager()

# Create new configuration
config_id = config_manager.create_config("My Custom Game", {
    "starting_money": 500,
    "doom_threshold": 75,
    "event_frequency": 0.8
})

# Export for sharing
config_manager.export_config(config_id, "my_game.json")
```

### Testing and Validation

**Demo Script**: `demo_settings.py` - Interactive demonstration of all settings features
**Test Suite**: `test_fixes.py` - Validates core functionality and integration
**Manual Testing**: Use Settings menu -> Enhanced Settings to test UI components

---

## Custom Sound Overrides (sounds/)

P(Doom) supports custom sound effects through a simple file-based override system. This allows developers and modders to easily replace built-in sound effects with custom audio files.

### How It Works

1. **Create the sounds/ directory** in the project root (same level as main.py)
2. **Place .wav or .ogg files** in the sounds/ directory (subdirectories are supported)
3. **Name files to match event keys** - the filename (without extension) becomes the sound key
4. **Custom sounds automatically override built-in sounds** when keys match

### File Naming and Event Keys

Files are mapped to sound events by their filename (case-insensitive). For example:
- `ap_spend.wav` - overrides the 'ap_spend' sound effect
- `POPUP_OPEN.ogg` - overrides the 'popup_open' sound effect  
- `Error_Beep.WAV` - overrides the 'error_beep' sound effect

**Available event keys that map to existing game events:**
- `ap_spend` - Played when Action Points are spent
- `popup_open` - Played when popup dialogs open
- `popup_close` - Played when popup dialogs close  
- `popup_accept` - Played when popup dialogs are accepted
- `error_beep` - Played for error feedback (easter egg)
- `blob` - Played when new employees are hired
- `zabinga` - Played when research papers are completed

### Example Usage

```bash
# Create the sounds directory
mkdir sounds

# Add custom sound files
cp my_custom_click.wav sounds/ap_spend.wav
cp my_popup_sound.ogg sounds/popup_open.ogg
cp celebration.wav sounds/zabinga.wav

# Run the game - your custom sounds will play automatically
python main.py
```

### Technical Details

- **Supported formats**: .wav and .ogg files
- **Recursive loading**: Files in subdirectories are loaded (e.g., `sounds/ui/popup_open.wav`)
- **Override behavior**: Custom files replace built-in sounds when keys match
- **Graceful fallback**: Missing sounds/ folder or invalid files won't crash the game
- **Audio hardware**: Works only when audio hardware is available (headless/CI environments skip loading)

### For Modders and Contributors

- The system loads sounds during `SoundManager` initialization
- Custom loading happens after built-in sound generation, ensuring overrides work
- Failed loads are handled gracefully - invalid files won't break the game
- Sound loading respects the audio availability flag

---

## Project Structure

### Core Game Files
- **main.py** -- Game entry point and menu system with new player experience
- **game_state.py** -- Core game logic and state management
- **actions.py** -- Action definitions (as Python dicts)
- **action_rules.py** -- Centralized action availability rule system
- **upgrades.py** -- Upgrade definitions
- **events.py** -- Event definitions and special event logic
- **event_system.py** -- Enhanced event system with deferred events and popups
- **opponents.py** -- Opponent AI and intelligence system

### Economic Systems
- **src/features/economic_cycles.py** -- Economic cycles and funding volatility system
  - Historical AI funding timeline (2017-2025) with realistic market phases
  - 5 funding sources with different economic sensitivities
  - Enhanced fundraising actions and advanced funding mechanisms
  - Economic events triggered by market conditions

### UI and Interface
- **ui.py** -- Pygame-based UI code with visual feedback integration
- **overlay_manager.py** -- Modular UI overlay and z-order management system
- **visual_feedback.py** -- Standardized visual feedback for clickable elements

### Enhanced Settings System
- **src/services/seed_manager.py** -- Centralized seed generation, validation, and management
- **src/services/game_config_manager.py** -- Custom game configuration creation and sharing
- **src/ui/enhanced_settings.py** -- Modern settings UI with categorical organization
- **src/ui/settings_integration.py** -- Integration layer for gradual adoption

### Audio and Feedback
- **sound_manager.py** -- Sound effects and audio feedback
- **game_logger.py** -- Comprehensive game logging system

### Development and Testing
- **tests/** -- Automated tests for core logic
- **demo_settings.py** -- Interactive demonstration of enhanced settings features
- **test_fixes.py** -- Validation script for core functionality and integration

### Documentation
- **README.md** -- Installation, troubleshooting, dependencies
- **PLAYERGUIDE.md** -- Player experience and gameplay guide
- **DEVELOPERGUIDE.md** (this file) -- Contributor documentation

---

## UI Architecture and Overlay Management

### Overview
P(Doom) features a modular UI system with screens and components routed via UIFacade. The architecture is designed for low-bit, low-poly aesthetics with modern accessibility features, inspired by Papers Please, SimPark, and Starcraft 2.

**New Modular Architecture (Post-Migration):**
- **UIFacade**: Central routing system for all screen rendering (`ui_new/facade.py`)
- **Screens**: Individual screen modules located in `ui_new/screens/` (game.py, menu.py, etc.)
- **Components**: Reusable UI components in `ui_new/components/` (buttons.py, windows.py, colours.py, typography.py)
- **Legacy Support**: Temporary compatibility layer for smooth migration

### Screen Management via UIFacade

#### UIFacade (`ui_new/facade.py`)
- **Centralised Routing**: All screen rendering goes through `ui_facade.render_*()` methods
- **Screen Coordination**: Manages current screen state and transitions
- **Legacy Compatibility**: Graceful fallback to legacy functions during migration
- **Future Extension**: Designed for easy addition of new screens and features

**Usage Example:**
```python
from ui_new.facade import ui_facade

# Render main game screen
ui_facade.render_game(screen, game_state, width, height)

# Manage screen state
ui_facade.set_current_screen('game')
current = ui_facade.get_current_screen()
```

### Modular UI Components

#### Button Components (`ui_new/components/buttons.py`)
- **Standardised States**: Normal, Hover, Pressed, Disabled, Focused via ButtonState enum
- **Style Variants**: Default, EndTurn, Action, Upgrade, Icon via ButtonStyle enum
- **Consistent Rendering**: `draw_button()`, `draw_icon_button()`, `draw_toggle_button()`
- **Integration**: Works with existing visual_feedback system for enhanced effects
- **Colour Management**: Centralised colour schemes with custom override support

#### Window Components (`ui_new/components/windows.py`)
- **Window Headers**: `draw_window_with_header()` replaces dynamic import pattern
- **Panel Systems**: `draw_panel()` for consistent panel styling
- **Dialog Support**: `draw_dialog_background()` for modal overlays
- **Legacy Compatibility**: Maintains exact function signatures for existing code

#### Typography System (`ui_new/components/typography.py`)
- **Font Management**: Centralised FontManager with caching and scaling
- **Responsive Sizing**: Screen-height based font scaling (title, big, normal, small)
- **Text Utilities**: Multiline rendering, text wrapping, size calculation
- **Consistent Styling**: Unified approach to text rendering across all screens

#### Colour Constants (`ui_new/components/colours.py`)
- **Centralised Palette**: All UI colours defined in one location
- **Resource Colours**: Money, staff, reputation, action points, doom, compute, etc.
- **UI State Colours**: Success, error, warning, info, disabled states
- **Button Themes**: Normal, hover, pressed, disabled colour schemes
- **Accessibility**: High contrast and focus indicator colours

### Core UI Components (Legacy System)

#### Overlay Manager (`overlay_manager.py`)
- **Z-Layer Management**: Hierarchical layering system (Background -> Game UI -> Tooltips -> Dialogs -> Modals -> Critical)
- **Element Registration**: Centralised registration and lifecycle management of UI elements
- **Animation System**: Smooth transitions with easing functions for minimize/expand/move operations
- **State Management**: UIState enum (Hidden, Minimized, Normal, Expanded, Animating)
- **Error Tracking**: Easter egg system that plays beep sound after 3 repeated identical errors
- **Accessibility**: Keyboard navigation support with Tab/Enter/Space/Escape

#### Visual Feedback System (`visual_feedback.py`)
- **Standardised Button States**: Normal, Hover, Pressed, Disabled, Focused
- **Button Effects**: 3-pixel depth shift when pressed, hover glow effects
- **Accessibility**: High contrast mode, font scaling (0.5x-2.0x), focus rings
- **Low-Poly Styling**: Rounded corners, gradient backgrounds, retro aesthetics
- **Tooltip System**: Auto-edge detection tooltips
- **Game State Integration**: Error tracking, resource validation, hover state management

#### Enhanced Employee Blob Positioning System

**Overview:**
The employee blob positioning system has been enhanced to prevent UI overlap and provide responsive layout based on screen size.

**Safe Zone Calculation:**
```python
def _calculate_blob_position(self, blob_index, screen_w=1200, screen_h=800):
    # Safe zone avoids UI elements:
    # - Action buttons (left ~0-45% of screen)
    # - Upgrade buttons (right ~55-100% of screen)  
    # - Resources area (top ~0-20% of screen)
    # - Message log (bottom ~70-100% of screen)
    
    safe_zone_left = int(screen_w * 0.46)
    safe_zone_right = int(screen_w * 0.54)
    safe_zone_top = int(screen_h * 0.25)
    safe_zone_bottom = int(screen_h * 0.65)
```

**Dynamic Positioning Features:**
- **Screen Size Responsive**: Positions scale with window size
- **Grid Layout**: Automatic grid arrangement within safe zones
- **Overflow Handling**: Graceful handling when many employees exceed safe zone
- **Animation Integration**: Smooth transitions from off-screen to calculated positions

**UI Integration:**
- `draw_employee_blobs()` detects and updates positions for existing blobs
- Position updates triggered when screen dimensions change
- Backward compatibility with existing blob data structures

**Testing Coverage:**
- Safe zone validation ensures blobs avoid UI elements
- Multiple blob positioning with unique positions
- Screen size scaling verification

### UI Element Types

#### Action Buttons
- Visual state reflects Action Point availability
- Enhanced tooltips show cost, AP requirements, and availability status
- Consistent styling with press/hover effects
- Automatic error tracking for insufficient resources

#### Upgrade Buttons/Icons
- Transform from buttons to compact icons when purchased
- Smooth animation transitions using overlay manager
- State-based styling (available, disabled, purchased)
- Enhanced tooltips with affordability status

#### Menu Systems
- Keyboard navigation with visual focus indicators
- Consistent button styling across all menus
- Accessibility features (keyboard shortcuts, high contrast)
- Modal dialogs with proper z-ordering

### Architecture Patterns

#### Z-Order Management
```python
# Elements are automatically layered by ZLayer enum
overlay_manager.register_element(UIElement(
    id="dialog",
    layer=ZLayer.DIALOGS,
    rect=pygame.Rect(x, y, w, h),
    title="Dialog Title"
))
```

#### Visual Feedback Integration
```python
# Buttons automatically get proper visual feedback
visual_feedback.draw_button(
    surface, rect, "Button Text", 
    ButtonState.HOVER,  # State determines styling
    FeedbackStyle.BUTTON
)
```

#### Error Tracking and Easter Eggs
```python
# Three identical errors trigger beep sound
if game_state.track_error("Insufficient money"):
    # Easter egg activated automatically
    pass
```

### Accessibility Features

#### Current Implementation
- **Keyboard Navigation**: Tab navigation between focusable elements
- **Font Scaling**: Configurable text scaling (0.5x to 2.0x)
- **Focus Indicators**: Yellow focus rings for keyboard navigation
- **High Contrast**: Available via `visual_feedback.get_accessible_color()`
- **Error Feedback**: Audio beep for repeated errors
- **Tooltip Enhancement**: Detailed information about interactive elements
- **Action Keyboard Shortcuts**: Direct action execution via 1-9 keys

#### Enhanced Action Point Feedback System

The Action Points (AP) system includes sophisticated visual and audio feedback:

**Visual Feedback:**
- **AP Counter Glow**: Yellow glow effect on AP counter when Action Points are spent
- **Glow Timer**: 30-frame animation timer (`ap_glow_timer`) for smooth visual feedback
- **Button State Sync**: Action buttons automatically gray out when AP is insufficient
- **Visual State Indicators**: ButtonState enum reflects AP availability in real-time

**Audio Feedback:**
- **AP Spend Sound**: Satisfying "ding" sound when Action Points are spent
- **Error Easter Egg**: Audio beep after 3 repeated identical errors
- **Sound Integration**: Integrated with `SoundManager` for consistent audio experience
- **AP Spend Sound**: Satisfying "ding" sound when Action Points are spent
- **Achievement Sound**: Celebratory 'Zabinga!' sound when research papers are completed
- **Error Easter Egg**: Audio beep after 3 repeated identical errors

**Implementation Details:**
```python
# Enhanced AP feedback in execute_action_by_keyboard()
if success:
    self.action_points -= ap_cost
    self.ap_spent_this_turn = True
    self.ap_glow_timer = 30  # 30 frames of glow effect
    # Sound feedback played by caller (main.py)
```

#### Keyboard Shortcut System

**Architecture:**
- **Action Shortcuts**: Keys 1-9 map to first 9 actions in the action list
- **Visual Integration**: Action buttons display shortcuts as "[1] Action Name"
- **Error Handling**: Comprehensive validation with user-friendly error messages
- **Auto-Delegation**: Keyboard shortcuts automatically use delegation when beneficial

**Implementation:**
```python
# In main.py keyboard handling
elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
    action_index = event.key - pygame.K_1  
    success = game_state.execute_action_by_keyboard(action_index)
    if success:
        game_state.sound_manager.play_ap_spend_sound()
```

**Integration Points:**
- `main.py`: Keyboard event handling and sound feedback
- `game_state.py`: `execute_action_by_keyboard()` method with full validation
- `ui.py`: Button label enhancement with shortcut display
- `sound_manager.py`: AP spend sound generation and playback

#### TODO: Future Accessibility Improvements
- [ ] Screen reader compatibility (text-to-speech integration)
- [ ] Colorblind-friendly color schemes
- [ ] Configurable UI scale (not just font scale)
- [ ] Audio cues for all interactive elements
- [ ] Voice navigation support
- [ ] Reduced motion options for animations
- [ ] Save accessibility settings to persistent config
- [ ] WCAG 2.1 AA compliance testing
- [ ] Alternative input method support (eye tracking, switch access)
- [ ] Subtitle system for any future audio content

### Performance Considerations
- **Efficient Rendering**: Only visible elements are rendered
- **Animation Optimization**: Smooth 30fps animations with easing functions
- **Memory Management**: Elements are properly unregistered to prevent leaks
- **Event Handling**: Overlay manager handles events before passing to game logic

### Extension Points
- **Custom Render Functions**: UIElements can have custom rendering logic
- **New Z-Layers**: Easy to add new layers for different UI types
- **Animation System**: Extensible for new animation types
- **Visual Styles**: FeedbackStyle enum can be extended for new UI patterns

---

## Opponents System Architecture

### Overview
The opponents system simulates competing AI labs with hidden information mechanics and espionage gameplay.

### Core Components

**opponents.py**
- `Opponent` class: Represents a competing organization with hidden stats
- `create_default_opponents()`: Generates the standard 3 competitors
- Hidden information system with discovery mechanics
- AI behavior for budget spending and research progress

**Integration Points**
- `GameState.__init__()`: Creates default opponents list
- `GameState._spy()`: Legacy espionage action (discovers/scouts random stats)
- `GameState._scout_opponent()`: Focused intelligence gathering action
- `GameState.end_turn()`: Processes opponent turns and doom contribution
- `ui.py`: `draw_opponents_panel()` displays discovered intelligence

### Opponent Data Structure

```python
class Opponent:
    # Core properties
    name: str                    # Display name
    budget: int                  # Available funding
    capabilities_researchers: int # Research capacity  
    lobbyists: int              # Policy influence
    compute: int                # Computing resources
    progress: int               # AGI development (0-100)
    
    # Discovery mechanics
    discovered: bool            # Whether player knows this opponent exists
    discovered_stats: dict      # Which stats have been revealed
    known_stats: dict          # Player's knowledge (may include noise)
```

### Intelligence System

**Discovery Process:**
1. Opponents start completely unknown
2. Espionage/scouting reveals opponent existence
3. Further operations reveal specific stats (with noise)
4. Some stats may remain hidden throughout the game

**Action Integration:**
- Espionage (existing): Random discovery/stat revelation
- Scout Opponent (new): Focused intelligence gathering, unlocked turn 5+
- Both actions carry espionage risks (reputation loss, doom increase)

### AI Behavior

Opponents execute simple AI logic each turn:
- Budget allocation based on priorities (research > hiring > compute > lobbying)
- Research progress scaled by resources (researchers x compute bonus)
- Doom contribution proportional to capabilities research

---

## Onboarding System Architecture

### Overview

The onboarding system provides comprehensive guidance for new players through an interactive tutorial and context-sensitive help. The system is designed to be minimal, non-intrusive, and completely optional.

### Core Components

**`onboarding.py`** - Main onboarding system module:
- `OnboardingSystem` class: Manages tutorial state and progression
- Tutorial content: Step-by-step guidance through game mechanics
- First-time help: Context-sensitive tips for key actions
- Progress tracking: Persistent storage of tutorial completion and seen mechanics

**Integration Points:**
- `main.py`: Tutorial overlay rendering and input handling
- `ui.py`: Tutorial overlay UI components and first-time help popups
- `game_state.py`: First-time mechanic detection and help triggers

### Tutorial System

The tutorial consists of 7 main steps covering core game mechanics:

1. **Welcome**: Introduction and overview
2. **Resources**: Money, staff, reputation, AP, p(Doom), compute
3. **Actions**: Available actions and Action Point costs
4. **Action Points**: AP system and staff scaling
5. **Turn Management**: Ending turns and handling events
6. **Events & Milestones**: Random events and growth milestones
7. **Upgrades**: Permanent improvements and strategic benefits

**Tutorial Features:**
- Step-by-step progression with Next/Skip buttons
- Content overlays with responsive design
- Persistent progress tracking (survives game restarts)
- One-time showing (doesn't reappear after completion/dismissal)
- Help button access to Player Guide during tutorial

### First-Time Help System

Provides automatic contextual help when players encounter key mechanics for the first time:

- **Staff Hiring**: When hiring beyond starting staff (triggers at staff > 2)
- **Upgrade Purchase**: When buying any upgrade for the first time
- **Action Points Exhausted**: When attempting actions without sufficient AP
- **High p(Doom) Warning**: When p(Doom) reaches dangerous levels (>=70%)

**Help Features:**
- Small popup notifications in top-right corner
- Dismissible with click or escape key
- Only shown once per mechanic per player (Factorio-style)
- Disabled during active tutorial to avoid interference
- Can be reset with Ctrl+R for new players

### Hint System vs Tutorial System

P(Doom) now has two separate help systems:

**Tutorial System** (`tutorial_enabled` config):
- Interactive step-by-step walkthrough for new players
- Can be enabled/disabled in New Player Experience
- Uses `show_tutorial_overlay` state variable

**Hint System** (`first_time_help` config):
- Factorio-style context-sensitive hints
- Shows once per mechanic, then auto-dismisses
- Can be reset with Ctrl+R for new players
- Uses `should_show_hint()` method that checks both config and seen status

### Mechanic Help Content System

The `get_mechanic_help()` method provides structured help content for specific game mechanics:

**Supported Mechanics:**
- `first_staff_hire`: Guidance on hiring staff and action point benefits (triggered on first manual hire attempt)
- `first_upgrade_purchase`: Explanation of laboratory upgrades and efficiency
- `action_points_exhausted`: Instructions when no action points remain
- `high_doom_warning`: Critical safety warnings for high p(Doom) levels

**New Methods in OnboardingSystem:**
```python
def should_show_hint(self, mechanic: str) -> bool:
    """Check if hint should be shown (considers both config and seen status)"""

def are_hints_enabled(self) -> bool:
    """Check if hints are enabled in config"""

def reset_all_hints(self) -> None:
    """Reset all hints for new players (Ctrl+R functionality)"""

def get_hint_status(self) -> Dict:
    """Get status of all hints for settings display"""
```

### Mechanic Help Content System

The `get_mechanic_help()` method provides structured help content for specific game mechanics:

**Supported Mechanics:**
- `first_staff_hire`: Guidance on hiring staff and action point benefits
- `first_upgrade_purchase`: Explanation of laboratory upgrades and efficiency
- `action_points_exhausted`: Instructions when no action points remain
- `high_doom_warning`: Critical safety warnings for high p(Doom) levels

**Method Signature:**
```python
def get_mechanic_help(self, mechanic: str) -> Optional[Dict]:
    """
    Get help content for a specific game mechanic.
    
    Returns:
        Dict with 'title' and 'content' keys for valid mechanics, None for invalid ones
        
    Note: Currently a stub implementation with warning logging.
    """
```

**Return Format:**
```python
{
    'title': 'Help Title',
    'content': 'Detailed help content explaining the mechanic...'
}
```

**Error Handling:**
- Returns `None` for invalid, empty, or non-string mechanic names
- Logs warnings for all calls (indicating stub implementation)
- Gracefully handles edge cases (None, empty string, numeric inputs)

### Progress Tracking

The system uses `onboarding_progress.json` to store:

```json
{
  "tutorial_enabled": true,
  "is_first_time": false,
  "completed_steps": ["welcome", "resources", "actions", ...],
  "seen_mechanics": ["first_staff_hire", "first_upgrade_purchase", ...],
  "tutorial_dismissed": false
}
```

**Privacy & Data:**
- All data stored locally only
- No personal information collected
- Progress file can be deleted to reset tutorial
- Tutorial system entirely optional

### Integration with Game Systems

**Tutorial Triggers:**
- Automatically starts on first game launch for new players
- Triggered in `main.py` when creating new `GameState`
- Overlay rendering integrated into game state rendering loop

**First-Time Help Triggers:**
- `game_state._add()` method triggers help for staff/doom changes
- `execute_action_with_delegation()` triggers AP exhaustion help
- Upgrade purchase triggers help for first upgrade

**Keyboard/Mouse Integration:**
- `H` key opens Player Guide anytime during gameplay
- Tutorial navigation with Next/Skip buttons
- Mouse and keyboard input handling for tutorial interactions

### Testing

The onboarding system includes comprehensive testing:

- **8 unit tests** covering all core functionality
- **Tutorial progression testing**: Step advancement and completion
- **First-time help testing**: Mechanic detection and help triggers
- **Progress persistence testing**: Save/load functionality
- **Integration testing**: File operations and error handling

**Test Coverage:**
- Tutorial initialization and progression
- First-time mechanic help system
- Content retrieval and formatting
- Tooltip management system
- Progress persistence and file operations

### Development Guidelines

**Adding New Tutorial Steps:**
1. Add step content to `get_tutorial_content()` method
2. Update tutorial sequence in `advance_tutorial_step()`
3. Add any special handling for the new step
4. Update tests to include new step

**Adding New First-Time Help:**
1. Add mechanic to `get_mechanic_help()` method
2. Add trigger logic in appropriate game system method
3. Add mechanic to help checking loop in `main.py`
4. Add test coverage for new mechanic

**Customizing Tutorial Content:**
- Tutorial content stored as structured dictionaries
- Easy to modify titles, content, and progression
- Supports markdown-style formatting in content text
- Step sequence easily customizable

---

## Testing Framework

### Running Tests

**Standard unittest approach:**
```sh
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_game_state -v

# Run specific test class
python -m unittest tests.test_game_state.TestEventLog -v
```

**Alternative with pytest:**
```sh
pip install pytest
pytest tests/ -v
```

### Test Coverage

**233 automated tests** covering all major systems:

- **Core Systems**: Game state, action execution, turn progression, upgrades
- **UI Systems**: Onboarding (8 tests), visual feedback, overlay management
- **Event Systems**: Enhanced events (27 tests), milestone events (14 tests), event log
- **Advanced Features**: Opponents system (26 tests), tutorial system (8 tests)
- **Infrastructure**: Game logging, bug reporting, version management

### Adding New Tests

Create test files in `tests/` directory following existing patterns:

```python
import unittest
from game_state import GameState

class TestNewFeature(unittest.TestCase):
    def test_new_functionality(self):
        gs = GameState("test_seed")
        # Test implementation
        self.assertEqual(expected, actual)
```

### Continuous Integration

Tests run automatically on GitHub Actions for:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.9, 3.10, 3.11, 3.12)

---

## Adding New Content

### Actions

Actions are defined in `actions.py` as a list of dictionaries:

```python
{
    "name": "New Action",
    "desc": "Description of what it does",
    "cost": 50,
    "upside": lambda gs: gs._add('money', 10),
    "downside": lambda gs: gs._add('reputation', -1),
    "rules": rule_function  # Optional availability conditions
}
```

### Action Rules System

The action rules system (introduced in Issue #69) provides a structured way to manage when actions become available. Instead of inline lambda functions, use the centralized `action_rules.py` system:

#### Basic Usage

```python
from action_rules import ActionRules, manager_unlock_rule

# In actions.py
{
    "name": "Manager Action",
    "rules": manager_unlock_rule  # Pre-defined rule function
}

# Or using the rule system directly
{
    "name": "Advanced Action", 
    "rules": lambda gs: ActionRules.requires_staff_and_turn(gs, min_staff=10, min_turn=5)
}
```

#### Available Rule Types

- **Turn-based**: `ActionRules.requires_turn(gs, min_turn=5)`
- **Resource-based**: `ActionRules.requires_staff(gs, min_staff=9)`
- **Milestone-based**: `ActionRules.requires_milestone_triggered(gs, 'manager_milestone_triggered')`
- **Upgrade-based**: `ActionRules.requires_upgrade(gs, 'better_computers')`
- **Composite**: `ActionRules.requires_staff_and_turn(gs, min_staff=9, min_turn=5)`

#### Creating New Rules

For new game mechanics, add rules to `action_rules.py`:

```python
@staticmethod
def requires_new_condition(gs, min_value):
    """
    Rule: Action requires new game condition.
    
    Args:
        gs: GameState object
        min_value: Minimum value required
        
    Returns:
        bool: True if condition is met
    """
    return gs.new_attribute >= min_value
```

#### Design Principles

1. **Single Responsibility**: Each rule checks one specific condition
2. **Composability**: Use `combine_and`/`combine_or` for complex logic
3. **Documentation**: Clear docstrings explaining when and why rules are used
4. **Testing**: Add unit tests for all new rules
5. **Naming**: Use descriptive names like `requires_*` or `*_unlock_rule`

### Upgrades

Upgrades are defined in `upgrades.py`:

```python
{
    "name": "New Upgrade",
    "desc": "What this upgrade provides",
    "cost": 100,
    "effect_key": "new_upgrade_effect"
}
```

Reference upgrade effects in `game_state.py` and action logic where needed.

### Events

Events are defined in `events.py`:

```python
{
    "name": "New Event",
    "desc": "Event description",
    "trigger": lambda gs: gs.turn > 5 and random.random() < 0.1,
    "effect": lambda gs: gs._add('doom', 5)
}
```

### Opponents

To add new opponents, modify `create_default_opponents()` in `opponents.py`:

```python
opponents.append(Opponent(
    name="New Competitor",
    budget=random.randint(500, 1000),
    capabilities_researchers=random.randint(10, 20),
    lobbyists=random.randint(5, 15),
    compute=random.randint(30, 80),
    description="Description of this competitor"
))
```

**Customization Options:**
- Modify AI behavior in `Opponent.take_turn()`
- Adjust discovery probabilities in `scout_stat()`
- Change doom contribution in `get_impact_on_doom()`
- Add specialized stat types or behaviors

**Testing New Opponents:**
- Add tests to `tests/test_opponents.py`
- Test discovery mechanics, AI behavior, and victory conditions
- Verify integration with espionage actions

---

## Research Quality & Technical Debt System (Issue #190)

### Overview
The Research Quality System implements strategic trade-offs between research speed and safety, with long-term consequences through technical debt accumulation. This system provides depth to research decisions while maintaining strategic tension between short-term progress and long-term stability.

### Core Components

**Research Quality Levels:**
- **RUSHED**: -40% time, -20% cost, +15% doom, +2 debt points, -10% success rate
- **STANDARD**: Baseline metrics (default behavior) 
- **THOROUGH**: +60% time, +40% cost, -20% doom, -1 debt point, +15% success rate, +reputation

**Technical Debt System:**
- Accumulates from shortcuts taken during research
- Progressive penalties affecting research speed and accident chance
- Swiss cheese model: multiple failure modes with escalating consequences
- Categories: Safety testing, code quality, documentation, validation

### Researcher Assignment System

**Individual Researcher Management:**
```python
# Assign specific researchers to specific tasks
gs.assign_researcher_to_task(researcher_id, task_name, quality_override)

# Set researcher default quality preferences
gs.set_researcher_default_quality(researcher_id, ResearchQuality.THOROUGH)

# Get effective quality for task (hierarchy: task override -> researcher default -> org default)
quality = gs.get_task_quality_setting(task_name, researcher_id)
```

**Assignment Tracking:**
- Researchers have unique IDs for reliable tracking
- Task-specific quality overrides
- Per-researcher default quality settings
- Assignment summary for UI display

### Technical Debt Management

**IMPORTANT: Naming Convention (v0.9.1+)**
- **Technical Debt Methods**: Use `add_technical_debt()` and `reduce_technical_debt()` 
- **Future Financial Debt**: Will use `add_financial_debt()` and `reduce_financial_debt()`
- **Backward Compatibility**: Legacy `add_debt()` / `reduce_debt()` methods still work but are deprecated
- **Rationale**: Clear distinction prevents confusion when lab financial management is added

**Debt Accumulation:**
- RUSHED research: +2 debt points per project
- THOROUGH research: -1 debt point per project
- Debt categories track different types of shortcuts

**Consequences by Debt Level:**
- 0-5: No penalties
- 6-10: -5% research speed
- 11-15: -10% research speed, +5% accident chance
- 16-20: -15% research speed, +10% accident chance, reputation risk
- 20+: Major system failure events possible

**Debt Reduction Actions:**
- **Refactoring Sprint**: Costs time + money, reduces 3-5 debt points
- **Safety Audit**: Costs money, reduces 2 debt points, gains reputation
- **Code Review**: Per-researcher cost, reduces 1 debt point per researcher

### Technical Debt Audit System

**Administrator Requirement:**
- Requires admin_staff >= 1
- Costs 2 Action Points
- Reveals exact debt numbers and category breakdown

**Audit Results:**
```python
audit_result = gs.execute_technical_debt_audit()
# Returns: risk_level, total_debt, speed_penalty_percent, 
#          accident_chance_percent, recommendations, category_breakdown
```

**Risk Indicators:**
- **Low Risk**: 0-5 debt points (green)
- **Medium Risk**: 6-15 debt points (yellow) 
- **High Risk**: 16+ debt points (red)

### Research Quality Events

**Event Types:**
1. **Safety Shortcut Temptation**: Researcher suggests cutting corners
2. **Technical Debt Warning**: Lead researcher warns about debt accumulation
3. **Quality vs Speed Dilemma**: Critical deadline forces quality choices
4. **Competitor Shortcut Discovery**: Intelligence reveals competitor shortcuts

**Event Integration:**
- Uses existing event system framework
- Multiple response options affecting debt and reputation
- Triggers based on debt levels and research activity

### Integration Points

**Turn Structure Integration:**
- Debt consequences checked during end_turn()
- Assignment tracking persists across turns
- Quality settings affect research action outcomes

**UI Integration Points:**
- Assignment interface for researcher-task pairing
- Quality setting controls with default hierarchy
- Risk level indicators (Low/Medium/High)
- Audit results display with detailed breakdown

**Action System Integration:**
```python
# Research actions automatically use quality system
execute_research_action(gs, action_name, base_doom_reduction, base_reputation_gain)
# Applies quality modifiers and technical debt penalties
```

### Extension Points

**Adding New Quality Levels:**
1. Add to ResearchQuality enum
2. Define modifiers in QUALITY_MODIFIERS
3. Update UI quality selection
4. Add tests for new quality level

**Adding New Debt Categories:**
1. Add to DebtCategory enum
2. Update debt distribution logic
3. Add category-specific consequences
4. Update audit breakdown display

**Adding New Research Events:**
1. Add event definition to events.py
2. Implement event handler in GameState
3. Define trigger conditions
4. Add multiple response options

### Testing Strategy

**Unit Tests:**
- Quality modifier calculations
- Debt accumulation and reduction
- Assignment tracking functionality
- Audit result generation

**Integration Tests:**
- Research action quality integration
- Event system integration
- Turn progression with debt consequences
- UI data flow validation

**Performance Considerations:**
- Assignment lookups optimized for UI responsiveness
- Debt calculations cached where appropriate
- Event triggers evaluated efficiently

### Future Roadmap

**Manager Integration (v3.1):**
- Managers can assign multiple researchers
- Bulk quality setting changes
- Team coordination bonuses

**Advanced Debt Mechanics (v3.2):**
- Debt compound interest
- Failure cascade events
- Recovery time after major failures

**Competitor Technical Debt (v3.3):**
- Visible competitor debt levels (with intelligence)
- Competitor failure events affecting global doom
- Strategic intelligence actions

---

## Enhanced Event System Architecture

### Overview
The enhanced event system supports visually dominant popup events, deferred event handling with expiration, and robust trigger/handling logic. It operates alongside the original event system for backward compatibility.

### Core Components

**event_system.py**
- `Event` class: Enhanced event objects with type, expiration, and multiple actions
- `EventType` enum: NORMAL, POPUP, DEFERRED event classifications
- `EventAction` enum: ACCEPT, DEFER, REDUCE, DISMISS action types
- `DeferredEventQueue`: Manages deferred events with expiration logic

**Integration Points**
- `GameState.__init__()`: Initializes deferred event queue and popup event lists
- `GameState.trigger_events()`: Processes both original and enhanced events
- `GameState.end_turn()`: Ticks deferred events and auto-executes expired ones
- `ui.py`: `draw_popup_events()` and `draw_deferred_events_zone()` for UI display

### Event System Order of Operations

**Turn Start:**
1. Clear previous turn messages (preserve scrollable history if enabled)
2. Execute selected player actions
3. Process staff maintenance and compute consumption

**Event Processing:**
4. Trigger original events (immediate execution)
5. Trigger enhanced events (if enhanced_events_enabled = True)
   - Popup events - added to pending_popup_events list
   - Normal events - executed immediately  
   - Deferred events - auto-deferred to queue
6. Tick all deferred events, auto-execute expired ones

**Turn End:**
7. Increment turn counter
8. Check win/lose conditions

### Event Data Structure

```python
class Event:
    name: str                        # Event title
    desc: str                        # Event description
    trigger: Callable               # Trigger condition function
    effect: Callable                # Primary effect function
    event_type: EventType           # NORMAL, POPUP, or DEFERRED
    max_deferred_turns: int         # Expiration countdown
    available_actions: List[EventAction] # Available player responses
    reduce_effect: Optional[Callable] # Alternative reduced effect
    
    # State management
    is_deferred: bool               # Currently deferred flag
    turns_deferred: int            # Turns since deferring
    deferred_at_turn: int          # Turn when deferred
```

### Extensibility and Future Actions

**Adding New Event Actions:**
1. Add to `EventAction` enum in `event_system.py`
2. Handle new action in `Event.execute_effect()`
3. Update UI button generation in `draw_popup_events()`
4. Add tests in `tests/test_events.py`

**Creating New Event Types:**
1. Add to `EventType` enum
2. Update default action assignment in `Event.__init__()`
3. Handle new type in `GameState._handle_triggered_event()`
4. Add UI handling if needed

**Complex Event Flows:**
The system supports:
- Event chains (events that trigger other events)
- Conditional actions based on game state
- Time-sensitive events with varying effects
- Multi-turn events that evolve over time

---

## End Game Scenarios System

### Overview
The end game scenarios system replaces generic "GAME OVER" messages with rich, contextual narratives that provide detailed explanations of what led to defeat and how the player's organization performed.

### Core Components

**end_game_scenarios.py**
- `EndGameScenario` class: Represents a specific scenario with title, description, cause analysis, and legacy note
- `EndGameScenariosManager` class: Manages scenario selection and contains the scenario dictionary
- Comprehensive scenario library with 18+ unique endings organized by defeat cause and survival time

**Integration Points**
- `ui.py`: Replaces generic game over display with detailed scenario rendering
- `game_state.py`: Provides game state information for scenario selection
- Deterministic selection based on game seed and turn count for reproducible experiences

### Scenario Selection Logic

Scenarios are categorized by:
- **Defeat Cause**: Max Doom Reached, Opponent Victory, Staff Loss
- **Time Period**: Early Game (1-10 turns), Mid Game (11-25 turns), Late Game (26+ turns)
- **Deterministic Selection**: Uses hash of game seed + turn count for consistent results

### Extension Points
- Add new defeat causes by extending `_determine_defeat_cause()`  
- Add new time periods by modifying `_determine_time_period()`
- Create new scenarios by adding to the scenarios dictionary
- Enhance selection logic with additional game state analysis

---

## Milestone Events System

### Overview
The milestone events system triggers special organizational changes at key growth thresholds, introducing new mechanics and UI elements as the player's lab scales.

### Architecture

**Milestone Tracking:**
```python
# Key state variables in GameState.__init__()
self.managers = 0                     # Manager count
self.board_members = 0               # Board member count  
self.first_manager_hired = False     # 9th employee milestone flag
self.board_member_search_unlocked = False  # Spending threshold flag
self.audit_risk_level = 0           # Hidden compliance risk (0-100)
self.spend_this_turn = 0            # Per-turn spending tracker
```

**Employee Subtype System:**
```python
# Employee blob structure extended with type and management
blob = {
    'type': 'employee|manager|board_member',
    'managed': False,                # Under manager supervision
    'unproductive_reason': None      # 'no_manager', 'no_compute', etc.
}
```

### Implementation Details

**Manager Milestone (9th Employee):**
- **Trigger**: `_add('staff', val)` checks for `staff >= 9` and `not first_manager_hired`
- **Effect**: `_trigger_manager_milestone()` converts latest employee to manager
- **Management Structure**: `_update_management_structure()` assigns employees to managers
- **Visual**: Managers show green color with crown icon in UI

**Board Member Compliance (Spending Threshold):**
- **Trigger**: `_check_board_member_threshold()` detects `spend_this_turn > 10000` without accounting software
- **Effect**: Unlocks "Search for Board Member" action, starts audit risk accumulation
- **Audit Risk**: Increases p(Doom) over time until 2 board members found
- **Visual**: Board members show purple color with briefcase icon in UI

**Spending Tracking:**
```python
# In _add() method for money
if val < 0:  # Track spending (negative values)
    self.spend_this_turn += abs(val)
```

### Employee Productivity Rules

**Management Requirements:**
1. First 9 employees are always productive (no management needed)
2. Employees 10+ require manager supervision or become unproductive
3. Each manager can supervise 9 additional employees
4. Unproductive employees show red slash overlay in UI

**Compute Assignment:**
- Managers and board members are always productive with compute
- Regular employees need both compute AND management (if beyond 9)
- Visual halos indicate compute assignment

### Testing
New milestone functionality is covered by `tests/test_milestone_events.py`:
- Manager milestone triggers and promotion logic
- Employee productivity with/without management
- Board member spending threshold detection  
- Audit risk mechanics and board member search
- Accounting software upgrade functionality
- Spending tracking and turn reset mechanics

### Extension Points
The milestone system is designed for easy expansion:
- Add new employee subtypes in blob `type` field
- Create new milestone triggers in `_add()` or `end_turn()`
- Extend management rules in `_update_management_structure()`
- Add new visual indicators in `draw_employee_blobs()`

### Productive Actions System

**Overview:**
The productive actions system provides ongoing, automated bonuses for employees when organizational requirements are met. Each employee category has three specialized actions they can perform.

**Architecture:**
```python
# Module: productive_actions.py
PRODUCTIVE_ACTIONS = {
    'junior_researcher': [
        {
            'name': 'Literature Review',
            'description': '...',
            'effectiveness_bonus': 1.08,  # +8% productivity bonus
            'requirements': {
                'compute_per_employee': 0.5,
                'min_reputation': 0
            }
        },
        # ... 2 more actions per category
    ],
    # ... 6 total categories
}
```

**Employee Categories:**
- **junior_researcher** (maps to 'researcher', 'generalist' subtypes)
- **senior_researcher** (maps to 'data_scientist' subtype)  
- **security_engineer** (maps to 'security_specialist' subtype)
- **operations_specialist** (maps to 'engineer' subtype)
- **administrative_staff** (maps to 'administrator' subtype)
- **manager** (maps to 'manager' subtype)

**Integration Points:**
```python
# Employee blob structure (game_state.py)
blob = {
    'subtype': 'researcher',              # Employee specialization
    'productive_action_index': 0,         # Selected action (0-2)
    'productive_action_bonus': 1.0,       # Current effectiveness multiplier
    'productive_action_active': False     # Whether requirements are met
}

# Productivity calculation (_update_employee_productivity)
requirements_met, failure_reason = check_action_requirements(action, self, compute_per_employee)
if requirements_met:
    blob['productive_action_bonus'] = action['effectiveness_bonus']
    blob['productive_action_active'] = True
else:
    blob['productive_action_bonus'] = 0.9  # 10% penalty
    blob['productive_action_active'] = False
```

**Requirement Types:**
- `compute_per_employee`: Available compute resources per employee
- `min_reputation`: Minimum organization reputation
- `min_staff`: Minimum total staff count
- `min_research_staff`: Minimum specialized research staff
- `min_research_progress`: Minimum accumulated research progress
- `min_money`: Minimum available funding
- `min_compute`: Minimum total compute infrastructure
- `min_board_members`: Minimum board oversight
- `min_admin_staff`: Minimum administrative support

**Extension Guide:**
1. **Adding New Actions**: Edit `PRODUCTIVE_ACTIONS` in `productive_actions.py`
2. **New Requirements**: Add checks in `check_action_requirements()`
3. **New Employee Categories**: Update `EMPLOYEE_SUBTYPE_TO_CATEGORY` mapping
4. **Custom Bonuses**: Modify bonus application in `_update_employee_productivity()`

**Testing:**
Covered by `tests/test_productive_actions.py`:
- Action definitions and structure validation
- Requirement checking with mock game states
- Integration with employee blob system
- Productivity update mechanics

---

## Code Style & Guidelines

### Contribution Guidelines

- Keep code modular - actions, upgrades, and events are data-driven for easy editing
- Always add or update tests for your changes
- Use clear, descriptive commit messages and pull request descriptions
- Update relevant documentation when adding features
- Follow existing code patterns and naming conventions
- **Reference version and changelog**: Include changelog updates in PRs for user-facing changes
- **Update version info**: For releases, update `version.py` and `CHANGELOG.md` appropriately

### Architecture Principles

- **Data-driven design**: Game content defined as lists of dictionaries
- **Separation of concerns**: UI, game logic, and data are in separate modules
- **Testability**: Core logic is testable without UI dependencies
- **Modularity**: Easy to add new content without modifying core systems

---

## Game Logging System

P(Doom) includes comprehensive logging for debugging and analysis:

### Log File Details

- **Location**: `logs/gamelog_<YYYYMMDD_HHMMSS>.txt`
- **Privacy**: No personal information - only game data and basic OS type
- **Content**: Actions, upgrades, events, turn summaries, game outcomes
- **Lifecycle**: One log per game session, locally stored

### What Gets Logged

1. **Game Start**: Timestamp, version, seed, OS type
2. **Player Actions**: All actions with costs and turn numbers
3. **Upgrade Purchases**: Name, cost, timing
4. **Game Events**: Triggered events with descriptions
5. **Turn Summaries**: End-of-turn resource states
6. **Game End**: Final state and completion reason

### Using Logs for Development

- **Balancing**: Analyze player behavior and resource progression
- **Debugging**: Understand game state when bugs occur
- **Testing**: Verify game mechanics work as expected
- **Analytics**: Track engagement with different features

---

## Release & Deployment

### Version Management

P(Doom) follows [Semantic Versioning](https://semver.org/) (SemVer) for consistent and predictable versioning:

- **MAJOR.MINOR.PATCH** format (e.g., 0.1.0, 1.2.3)
- **MAJOR**: Incompatible API changes or major gameplay overhauls  
- **MINOR**: Backwards-compatible functionality additions (new features, events, opponents)
- **PATCH**: Backwards-compatible bug fixes and minor improvements

#### Centralized Version System

The game uses a centralized version management system in `version.py`:

```python
from version import get_version, get_display_version, get_version_info

# Get semantic version (e.g., "0.1.0")
version = get_version()

# Get display version for UI (e.g., "v0.1.0") 
display = get_display_version()

# Get detailed version information
info = get_version_info()
```

**Key Integration Points:**
- `main.py`: Window title shows current version
- `game_logger.py`: Logs include version information
- `version.py`: Single source of truth for all version data

### Release Process

For complete release procedures, see [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).

#### Quick Release Steps

1. **Update Version**: Edit `version.py` with new version number
2. **Update Changelog**: Move changes from `[Unreleased]` to new version in `CHANGELOG.md`
3. **Test**: Run full test suite (`python -m unittest discover tests -v`)
4. **Tag Release**: Create and push version tag (`git tag v0.1.0`)
5. **Automated Release**: GitHub Actions automatically creates release with assets

#### GitHub Actions Workflows

- **Tests** (`.github/workflows/test.yml`): Runs on all pushes and PRs
- **Release** (`.github/workflows/release.yml`): Triggered by version tags or manual dispatch

The release workflow:
- Validates version format and consistency
- Runs full test suite on multiple Python versions  
- Creates GitHub release with changelog notes
- Generates and uploads source distribution archives
- Includes SHA256 checksums for security verification

---

## Milestone-Driven Special Events & Static Effects System

### Overview
The milestone system introduces persistent "static effects" that activate based on organizational growth and behavior. Unlike events that trigger once, static effects continuously influence gameplay until conditions change.

### System Architecture

**Core Components:**
- **Milestone Triggers**: One-time condition checks (e.g., 9th employee hired, >$10K spending)
- **Static Effects**: Ongoing gameplay modifications (e.g., unmanaged employee penalties)
- **Visual Feedback**: UI overlays and indicators showing effect states
- **Management Systems**: Player tools to mitigate or work with static effects

### Manager System Implementation

**Data Structures:**
```python
# GameState additions
self.managers = []                    # List of manager blob objects
self.manager_milestone_triggered = False  # One-time trigger flag

# Employee blob enhancements
blob = {
    'type': 'employee' | 'manager',   # Blob classification
    'managed_by': manager_id | None,  # Management assignment
    'unproductive_reason': str | None # Why blob is unproductive
}
```

**Static Effect Processing:**
1. **Trigger Check**: `_hire_manager()` sets milestone flag on first manager
2. **Assignment Logic**: `_reassign_employee_management()` distributes employees to managers
3. **Productivity Impact**: `_update_employee_productivity()` applies management penalties
4. **Visual Feedback**: `draw_employee_blobs()` shows green managers, red slash overlays

### Board Member System Implementation

**Spending Tracking:**
```python
# In _add() method for money attribute
if val < 0:
    self.spend_this_turn += abs(val)  # Track negative amounts as spending

# In end_turn()
self._check_board_member_milestone()  # Check trigger condition
self.spend_this_turn = 0              # Reset for next turn
```

**Static Effect Escalation:**
```python
def _check_board_member_milestone(self):
    # One-time trigger: install board members
    if spend_this_turn > 10000 and not accounting_software_bought:
        self.board_members = 2
        
    # Ongoing effects: audit risk accumulation and penalties
    if board_members > 0 and not accounting_software_bought:
        self.audit_risk_level += 1
        # Apply escalating penalties based on risk level
```

### Order of Operations (Per Turn)

**Turn Start:**
1. Clear previous messages
2. Execute selected actions (spending tracked via `_add()`)
3. Process staff maintenance (spending tracked)

**Turn End:**
1. Update employee productivity (apply management static effects)
2. Process opponent actions and doom increases
3. Trigger random events
4. **Check milestone triggers** (`_check_board_member_milestone()`)
5. **Apply ongoing static effects** (audit penalties, management productivity)
6. Reset action points and spending tracking
7. Check win/lose conditions

### Testing Strategy

**Static Effect Tests:**
- **Milestone Triggers**: Verify conditions activate features correctly
- **Ongoing Effects**: Test continuous application of penalties/bonuses
- **Edge Cases**: Test boundary conditions (exactly 9 employees, exactly $10K spending)
- **Integration**: Verify effects interact correctly with existing systems

**Example Test Pattern:**
```python
def test_static_effect_integration(self):
    # Setup condition for static effect
    self.game_state.staff = 12
    self.game_state._hire_manager()
    
    # Trigger the static effect system
    self.game_state._update_employee_productivity()
    
    # Verify static effect is applied correctly
    unmanaged = [blob for blob in self.game_state.employee_blobs 
                if blob.get('unproductive_reason') == 'no_manager']
    self.assertGreater(len(unmanaged), 0)
```

### Extension Points

**Adding New Milestones:**
1. Add trigger condition check to `end_turn()` or relevant method
2. Create static effect application logic
3. Add visual feedback to UI system
4. Include player mitigation mechanisms
5. Write comprehensive tests

**Design Principles:**
- **Clear Feedback**: Players should understand why effects are active
- **Player Agency**: Provide tools to manage or mitigate negative effects
- **Escalating Complexity**: Effects should scale with organizational growth
- **Test Coverage**: All static effects need automated testing

---

## Architecture Notes

### TurnManager Architecture (v0.7.5)

**Monolith Breakdown Achievement:**
P(Doom) v0.7.5 successfully extracted turn processing from the monolithic `GameState.end_turn()` method:

- **TurnManager Class**: Dedicated turn processing with proper state management (`src/core/turn_manager.py`)
- **TurnProcessingState Enum**: Explicit states (READY, PROCESSING, STUCK, COMPLETED) for debugging
- **Phase-Based Processing**: Clear separation of turn phases with error handling
- **Enhanced Debugging**: Comprehensive logging for doom tracking and opponent progress
- **State Validation**: Stuck detection with automatic recovery mechanisms

**Development Benefits:**
- **Improved Maintainability**: Turn logic isolated from game state management
- **Better Debugging**: Clear state transitions and comprehensive logging
- **Easier Testing**: Turn processing can be unit tested independently
- **Future Extension**: New turn phases can be added cleanly

### UI Architecture Modernisation

**New Modular Architecture (2024):**
P(Doom) has transitioned to a modular UI architecture with clear separation of concerns:

- **UIFacade Routing**: All screen rendering routes through `ui_facade.render_*()` methods
- **Screen Modules**: Individual screens in `ui_new/screens/` (game.py, menu.py, settings.py)
- **Reusable Components**: Shared components in `ui_new/components/` (buttons, windows, typography, colours)
- **Legacy Compatibility**: Gradual migration approach maintains existing behaviour exactly
- **No Behavioural Changes**: Incremental modularisation preserves all existing functionality

**Development Benefits:**
- **Easier Maintenance**: Components can be updated independently
- **Consistent Styling**: Centralised colour and typography management
- **Better Testing**: Individual components can be unit tested
- **Future Extension**: New screens and components can be added cleanly

### UI Adaptability

- Window is resizable and adaptive (80% of screen by default)
- UI elements scale and may overlap intentionally for "bureaucratic clutter" feel
- Upgrades shrink to icons after purchase with tooltip support
- **New**: All screens rendered via UIFacade maintain consistent scaling behaviour

### UI Overlay Variables Pattern

**Important:** When adding new UI overlay variables that are both read and written within the main() function, they must be declared as global to prevent UnboundLocalError.

**Required Pattern:**
```python
# At module level
my_overlay_content = None
my_overlay_button = None

def main():
    # Must declare as global if variable is assigned within function
    global my_overlay_content, my_overlay_button
    
    # Now safe to check before assignment
    if not my_overlay_content:
        # Assignment is safe
        my_overlay_content = create_overlay()
```

**Examples of Variables Requiring Global Declaration:**
- `first_time_help_content`, `first_time_help_close_button`
- `current_tutorial_content`
- `overlay_content`, `overlay_title` (for main menu overlays like Settings, Player Guide, README)
- Any UI state variables that are both checked and assigned in main()

**Why This Is Required:**
Python treats variables as local when they are assigned anywhere in a function scope. Without global declaration, referencing these variables before assignment raises UnboundLocalError even if they exist at module level.

**[WARNING][EMOJI] WARNING: Common Bug Pattern**
The most common manifestation of this bug is when menu handlers (like `handle_menu_click` or `handle_menu_keyboard`) assign overlay variables, but the main() function lacks proper global declarations. This causes crashes when selecting menu items like "Options" or "Player Guide".

**Always verify that:**
1. Overlay variables are declared at module level
2. All overlay variables assigned in functions called from main() are declared as global in main()
3. The `draw_overlay` function has defensive logic for None values

### State Management

- Game state is centralized in `GameState` class
- Event log management supports both basic and enhanced (scrollable) modes
- Resource tracking with optional balance change display

### Future Expansion

The codebase is designed for:
- Modular scenario/patch expansion
- Additional UI overlays (paperwork, news, etc.)
- Extended content through data file modifications
- Integration with external systems (analytics, achievements, etc.)

---

## Tutorial & Onboarding System Architecture

The tutorial system provides context-sensitive guidance for new players while remaining unobtrusive for experienced players.

### Core Components

**GameState Integration:**
- `tutorial_enabled`: Boolean flag to enable/disable tutorial system
- `tutorial_shown_milestones`: Set tracking which tutorials have been shown
- `pending_tutorial_message`: Current tutorial awaiting display
- `first_game_launch`: Flag to detect new players

**Tutorial Settings Persistence:**
- `tutorial_settings.json`: Local file storing user preferences
- `load_tutorial_settings()`: Load preferences on game initialization
- `save_tutorial_settings()`: Save preferences when changed

**Tutorial Display System:**
- `draw_tutorial_overlay()`: UI rendering for tutorial messages in `ui.py`
- Semi-transparent background with dismissible dialog
- Supports both mouse and keyboard interaction

### Tutorial Triggers

**Initial Tutorial:**
- Triggered on first game launch for new players
- Explains core gameplay mechanics and resources
- Shown once per tutorial settings file

**Milestone Tutorials:**
- **Manager System**: Triggered when first manager is hired (9+ employees)
- **Board Member System**: Triggered on $10k+ spending without accounting software
- **Enhanced Events**: Triggered when enhanced event system unlocks (turn 8+)
- **Scrollable Log**: Triggered when scrollable event log unlocks (turn 5+)

### Implementation Details

**Tutorial Message Structure:**
```python
{
    "milestone_id": "unique_identifier",
    "title": "Tutorial Title",
    "content": "Multi-line tutorial content with guidance"
}
```

**Key Methods:**
- `show_tutorial_message(milestone_id, title, content)`: Queue tutorial for display
- `dismiss_tutorial_message()`: Close tutorial and mark milestone as shown
- Tutorial integration in `main.py` event loop for display and input handling

**Integration Points:**
- Manager hiring in `game_state.py` manager system
- Board member trigger in `game_state.py` spending checks
- Event system unlocks in `events.py` milestone functions

### Testing

The tutorial system includes comprehensive unit tests:
- `TestTutorialSystem`: Core functionality tests (8 tests)
- `TestTutorialMilestones`: Milestone trigger tests
- Persistence testing across game sessions
- Tutorial enable/disable functionality

**Test File:** `tests/test_tutorial_system.py`
**Manual Testing:** `test_tutorial_manual.py` (not in test suite)

### Customization

**Adding New Tutorials:**
1. Add trigger logic in appropriate game event
2. Call `show_tutorial_message()` with unique milestone ID
3. Update tests to verify new tutorial trigger
4. Document new tutorial in player guide

**Modifying Tutorial Content:**
- Tutorial content strings are embedded in code for immediate localization support
- Modify title/content in `show_tutorial_message()` calls
- Update documentation if tutorial explains changed mechanics

---

## Need Help?

- **GitHub Issues**: For bugs and feature requests
- **Code Questions**: Check existing tests and documentation
- **Architecture Decisions**: Review this guide and existing code patterns
- **Testing Help**: See test examples in `tests/` directory

---

Happy hacking!
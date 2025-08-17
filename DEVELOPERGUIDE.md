# Developer Guide for P(Doom)

Welcome, contributors and modders! This guide explains how to develop, test, and extend P(Doom): Bureaucracy Strategy.

For **players**, see the [Player Guide](PLAYERGUIDE.md).  
For **installation and troubleshooting**, see the [README](README.md).

## Table of Contents
- [Development Setup](#development-setup) (Line 28)
- [Custom Sound Overrides (sounds/)](#custom-sound-overrides-sounds) (Line 54)
- [Project Structure](#project-structure) (Line 100)
- [UI Architecture and Overlay Management](#ui-architecture-and-overlay-management) (Line 122)
- [Opponents System Architecture](#opponents-system-architecture) (Line 318)
- [Onboarding System Architecture](#onboarding-system-architecture) (Line 378)
- [Testing Framework](#testing-framework) (Line 507)
- [Adding New Content](#adding-new-content) (Line 563)
- [Enhanced Event System Architecture](#enhanced-event-system-architecture) (Line 694)
- [Milestone Events System](#milestone-events-system) (Line 774)
- [Code Style & Guidelines](#code-style--guidelines) (Line 854)
- [Game Logging System](#game-logging-system) (Line 875)
- [Release & Deployment](#release--deployment) (Line 904)
- [Milestone-Driven Special Events & Static Effects System](#milestone-driven-special-events--static-effects-system) (Line 963)
- [Architecture Notes](#architecture-notes) (Line 1081)
- [Tutorial & Onboarding System Architecture](#tutorial--onboarding-system-architecture) (Line 1142)
- [Need Help?](#need-help) (Line 1224)

**Configuration System**: For config management and modding support, see [CONFIG_SYSTEM.md](CONFIG_SYSTEM.md).

---

## Development Setup

### Prerequisites
- Python 3.8+
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

- **main.py** — Game entry point and menu system
- **game_state.py** — Core game logic and state management
- **actions.py** — Action definitions (as Python dicts)
- **action_rules.py** — Centralized action availability rule system
- **upgrades.py** — Upgrade definitions
- **events.py** — Event definitions and special event logic
- **event_system.py** — Enhanced event system with deferred events and popups
- **opponents.py** — Opponent AI and intelligence system
- **ui.py** — Pygame-based UI code with visual feedback integration
- **overlay_manager.py** — Modular UI overlay and z-order management system
- **visual_feedback.py** — Standardized visual feedback for clickable elements
- **sound_manager.py** — Sound effects and audio feedback
- **game_logger.py** — Comprehensive game logging system
- **tests/** — Automated tests for core logic
- **README.md** — Installation, troubleshooting, dependencies
- **PLAYERGUIDE.md** — Player experience and gameplay guide
- **DEVELOPERGUIDE.md** (this file) — Contributor documentation

---

## UI Architecture and Overlay Management

### Overview
P(Doom) features a modular UI overlay system inspired by Papers Please, SimPark, and Starcraft 2, designed for low-bit, low-poly aesthetics with modern accessibility features.

The UI architecture is currently under incremental modularisation, with key screens migrated to `pdoom1/ui/screens/` and rendered through the UIFacade for stable interface management.

### Core UI Components

#### UIFacade (`pdoom1/ui/facade.py`)
- **Stable Interface**: Thin facade providing stable API for UI operations during refactoring
- **Screen Routing**: Routes rendering calls to appropriate screen modules
- **Overlay Integration**: Coordinates with OverlayManager for layered UI elements
- **Screen Methods**: 
  - `render_main_menu()`: Main menu with navigation options (migrated from ui.py)
  - `render_loading()`: Loading progress with status text (migrated from ui.py)
  - `render_audio_menu()`: Audio settings interface (migrated from ui.py)
  - `render_seed_selection()`: Seed selection screen with weekly/custom options (migrated from ui.py)
  - `render_game()`: In-game HUD and overlay coordination

#### Modular Screens (`pdoom1/ui/screens/`)
- **main_menu.py**: Main menu screen implementation with keyboard navigation
- **loading.py**: Loading screen with progress bars and accessibility support
- **audio_menu.py**: Audio settings menu with volume controls
- **seed_selection.py**: Seed selection screen for weekly and custom seeds
- **game_hud.py**: In-game HUD components and layout

Current status: Individual screen functions migrated with identical behaviour preserved. Future work will introduce Screen classes with state management.

#### Overlay Manager (`pdoom1/ui/overlay_manager.py`)
The overlay manager has been moved to the `pdoom1/ui/` package as part of the UI modularisation effort. It continues to provide:

- **Z-Layer Management**: Hierarchical layering system (Background -> Game UI -> Tooltips -> Dialogs -> Modals -> Critical)
- **Element Registration**: Centralised registration and lifecycle management of UI elements
- **Animation System**: Smooth transitions with easing functions for minimise/expand/move operations
- **State Management**: UIState enum (Hidden, Minimised, Normal, Expanded, Animating)
- **Error Tracking**: Easter egg system that plays beep sound after 3 repeated identical errors
- **Accessibility**: Keyboard navigation support with Tab/Enter/Space/Escape

**Import Compatibility**: The overlay manager is still accessible via the top-level import for backward compatibility:
```python
# Legacy import (shows deprecation warning)
from overlay_manager import OverlayManager

# New preferred imports
from pdoom1.ui import OverlayManager
from pdoom1.ui.overlay_manager import OverlayManager, UIElement, ZLayer, UIState
```

#### UI Facade (`pdoom1/ui/facade.py`)
A thin facade providing a stable interface to the UI subsystem:

- **Stable Interface**: Wraps internal OverlayManager with consistent API
- **Future-Proof**: Enables UI refactoring without breaking external callers
- **Proxy Methods**: Routes common operations (register_element, render_elements, etc.)
- **Advanced Access**: Provides `overlay_manager` property for direct access when needed

**Usage Example**:
```python
from pdoom1.ui.facade import UIFacade

ui = UIFacade()
ui.register_element(my_element)
ui.render_elements(screen)
```

**Game HUD Rendering**: The facade now provides `render_game()` method that coordinates rendering of the main game HUD via the existing `ui.draw_ui` function and overlay elements through the OverlayManager. This maintains identical behaviour to the original rendering with no changes to game logic:

```python
# In main game loop (main.py)
ui_facade = UIFacade(game_state.overlay_manager)
ui_facade.render_game(screen, game_state, SCREEN_W, SCREEN_H)
```

#### UI Screens Scaffolding (`pdoom1/ui/screens/`)
A scaffolding system for organizing different UI screens with consistent interfaces:

- **Base Protocol**: `Screen` abstract base class defining render contract for all UI screens
- **GameHudScreen**: Implemented screen that wraps existing `ui.draw_ui` + OverlayManager coordination
- **Screen Stubs**: MainMenuScreen, LoadingScreen, AudioMenuScreen (TODOs for future implementation)
- **Consistent Interface**: All screens implement `render()`, `update()`, and `handle_event()` methods

**Current Implementation**:
```python
from pdoom1.ui.screens import GameHudScreen

# GameHudScreen acts as thin wrapper over existing rendering
hud_screen = GameHudScreen(overlay_manager)
hud_screen.render(screen, game_state=gs, w=800, h=600)
```

**Design Principles**:
- Screens are lightweight with minimal logic
- Delegation to existing systems (ui.py, OverlayManager) 
- No behavioural changes during refactoring
- Future-ready for main menu/loading screen migration

#### Visual Feedback System (`visual_feedback.py`)
- **Standardized Button States**: Normal, Hover, Pressed, Disabled, Focused
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
- Research progress scaled by resources (researchers × compute bonus)
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
- **High p(Doom) Warning**: When p(Doom) reaches dangerous levels (≥70%)

**Help Features:**
- Small popup notifications in top-right corner
- Dismissible with click or escape key
- Only shown once per mechanic per player
- Disabled during active tutorial to avoid interference

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
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

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

### UI Adaptability

- Window is resizable and adaptive (80% of screen by default)
- UI elements scale and may overlap intentionally for "bureaucratic clutter" feel
- Upgrades shrink to icons after purchase with tooltip support

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

**⚠️ WARNING: Common Bug Pattern**
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
# Developer Guide for P(Doom)

Welcome, contributors and modders! This guide explains how to develop, test, and extend P(Doom): Bureaucracy Strategy.

For **players**, see the [Player Guide](PLAYERGUIDE.md).  
For **installation and troubleshooting**, see the [README](README.md).

---

## Development Setup

### Prerequisites
- Python 3.8+
- pygame (`pip install pygame`)
- pytest for testing (`pip install pytest` or `pip install -r requirements.txt`)

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

## Project Structure

- **main.py** — Game entry point and menu system
- **game_state.py** — Core game logic and state management
- **actions.py** — Action definitions (as Python dicts)
- **upgrades.py** — Upgrade definitions
- **events.py** — Event definitions and special event logic
- **event_system.py** — Enhanced event system with deferred events and popups
- **opponents.py** — Opponent AI and intelligence system
- **ui.py** — Pygame-based UI code
- **game_logger.py** — Comprehensive game logging system
- **tests/** — Automated tests for core logic
- **README.md** — Installation, troubleshooting, dependencies
- **PLAYERGUIDE.md** — Player experience and gameplay guide
- **DEVELOPERGUIDE.md** (this file) — Contributor documentation

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

Current test coverage includes 115 automated tests covering:

- ✅ **Enhanced Event System** - Event class, deferred events, popup handling, expiration logic (27 tests)
- ✅ **Event Log Management** - Activity log clears each turn, shows only current events
- ✅ **Game State Management** - Resource management and state transitions
- ✅ **Upgrade System** - Purchase logic and effect activation  
- ✅ **Game Logging** - Comprehensive session logging
- ✅ **Core Game Mechanics** - Action execution, turn progression, game-over conditions
- ✅ **Opponents System** - AI behavior, discovery mechanics, intelligence gathering (26 tests)
- ✅ **Compute & Sound** - Employee productivity and audio systems
- ✅ **Bug Reporting** - Error reporting and privacy features

### Adding New Tests

1. Create test files in `tests/` directory named `test_*.py`
2. Test functions should be named `test_*`
3. Use existing tests as templates for structure and style
4. Always add tests for new features or bug fixes

Example test structure:
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
    "rules": None  # Optional conditions
}
```

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
   - Popup events → added to pending_popup_events list
   - Normal events → executed immediately  
   - Deferred events → auto-deferred to queue
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

## Architecture Notes

### UI Adaptability

- Window is resizable and adaptive (80% of screen by default)
- UI elements scale and may overlap intentionally for "bureaucratic clutter" feel
- Upgrades shrink to icons after purchase with tooltip support

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

## Need Help?

- **GitHub Issues**: For bugs and feature requests
- **Code Questions**: Check existing tests and documentation
- **Architecture Decisions**: Review this guide and existing code patterns
- **Testing Help**: See test examples in `tests/` directory

---

Happy hacking!
# P(Doom): Bureaucracy Strategy Game Prototype
A satirical meta-strategy game about AI Safety, inspired by *Papers, Please*, *Pandemic*, and clicker games.

## Getting Started

### Requirements
- Python 3.8+
- [pygame](https://www.pygame.org/) (`pip install pygame`)

### How to Run
```sh
pip install pygame
python main.py
```

Or, install all dependencies (including testing tools) from requirements:
```sh
pip install -r requirements.txt
python main.py
```

### Testing

This project includes comprehensive automated tests to ensure core functionality works correctly. All tests are located in the `tests/` directory.

#### Running Tests

**Standard approach using unittest:**
```sh
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_game_state -v

# Run specific test category (e.g., event log tests)
python -m unittest tests.test_game_state.TestEventLog -v
```

**Alternative with pytest (if installed):**
```sh
pip install pytest
pytest tests/ -v
```

#### Key Test Coverage

The test suite validates critical functionality including:

- ✅ **Event Log Management:** Activity log clears at start of each turn and shows only current-turn events
- ✅ **Game State:** Resource management, turn progression, win/loss conditions
- ✅ **Upgrade System:** Purchase logic, effect activation, cost validation
- ✅ **Action System:** Action execution, cost deduction, effect application
- ✅ **Game Logging:** Comprehensive session logging for debugging and analysis

#### Continuous Integration

The repository includes GitHub Actions workflow (`.github/workflows/test.yml`) that automatically runs tests on:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

#### Adding New Tests

- All test files should be placed in the `tests/` directory
- Test files should be named `test_*.py` (e.g., `test_game_state.py`, `test_actions.py`)
- Test functions should be named `test_*` (e.g., `test_player_can_buy_upgrade()`)
- Follow existing test patterns and keep tests focused and readable

#### Test Coverage

This project maintains automated tests for core game functionality. Current test coverage includes:

- **GameState (`tests/test_game_state.py`)**: 
  - GameState initialization and default values
  - Core resource setup (money, staff, reputation, doom)
  - Game state collections and properties
  - **Event Log Management:** Activity log clears at start of each turn and shows only current-turn events
  - **Scrollable Event Log:** Feature flag management, history storage, and turn-based event accumulation

- **Upgrades (`tests/test_upgrades.py`)**:
  - Upgrade purchasing with sufficient money
  - Upgrade purchase failure with insufficient money  
  - Prevention of duplicate purchases
  - Upgrade effect activation and management
  - Success and failure message generation
  - Upgrade initialization and structure validation

- **Game Logging (`tests/test_game_logging.py`)**:
  - Session logging for debugging and analysis
  - Action, event, and upgrade logging
  - Game completion and log file generation

- **Compute & Sound Systems (`tests/test_compute_and_sound.py`)**:
  - Compute resource system and employee productivity logic
  - Buy Compute action functionality and cost validation
  - Research progress tracking and paper publication
  - Sound system controls and audio effect management
  - Employee blob visualization and animation system
  - Staff hiring/firing with blob management integration

**Contributors:** Please keep this Test Coverage section current when adding new test files or expanding test coverage. This helps other contributors understand what is already tested and what areas might need additional testing.

#### For Contributors

When adding new features or modifying existing code:

1. **Always add or update tests** for your changes
2. **Run the full test suite** before submitting contributions: `pytest`
3. **Ensure all tests pass** - don't break existing functionality
4. **Write clear, descriptive test names** that explain what is being tested
5. **Update the Test Coverage section** in both README.md and PLAYERGUIDE.md when adding new tests
6. **Don't commit test artifacts** - the `.gitignore` file excludes `__pycache__/`, `.pytest_cache/`, `*.pyc`, and other test artifacts from version control

Tests help ensure the game remains stable and functional as it evolves!

**Note:** The repository's `.gitignore` file is configured to automatically exclude Python and pytest artifacts, so you don't need to worry about accidentally committing cache files or test artifacts.

### Main Menu

When you launch the game, you'll see a main menu with the following options:

- **Launch with Weekly Seed**: Start immediately with the current week's challenge seed
- **Launch with Custom Seed**: Enter your own seed for repeatable games  
- **Settings**: Access sound controls and gameplay information
- **Player Guide**: View the complete player guide with controls and strategies
- **README**: View this documentation file

**Navigation:**
- Use mouse clicks or arrow keys to navigate
- Press Enter or click to select an option
- Press Escape to quit from the main menu

### Sound & Settings

- **Sound Effects**: Enabled by default, includes "blobby" sounds for new employee hires
- **Mute Button**: Click the sound icon (♪/🔇) in bottom-right corner during gameplay
- **Settings Menu**: Access from main menu for detailed information about controls and features
- **Auto-Disable**: Sound automatically disables if no audio device is available

### Gameplay

- The game now starts with a **main menu** where you can choose your game mode.
- Select "Launch with Weekly Seed" for the current week's challenge, or "Launch with Custom Seed" to enter your own.
- Enter a seed at startup (or leave blank for weekly challenge seed).
- Select actions (left column) by clicking buttons. Buy upgrades (right) by clicking. Purchased upgrades shrink to icons at the top right.
- **Compute Resources**: Purchase compute with "Buy Compute" action ($100 per 10 flops) to keep employees productive.
- Take as many actions as you want, then click "End Turn" (or press Space) to process choices and see results.
- Manage Money, Staff, Reputation, p(Doom) (AI risk), Compute, and Research Progress. Pay staff each turn.
- **Employee Blobs**: Watch animated employee blobs in the lower middle area. Productive employees glow!
- **Weekly Cycle**: Each turn is one week. Employees consume compute and contribute to research papers.
- **Sound Effects**: Enjoy "bloop" sounds when hiring staff. Toggle with mute button (bottom right).
- Watch out for random events and opponent progress!
- **Game Over**: p(Doom) reaches 100, all staff leave, or the opponent finishes their AGI.
- At game end, see your turn survived and local high score (per seed).

---

## Adaptive UI

- The window is 80% of your screen by default and resizable.
- UI elements adapt to fit; if crowded, elements may overlap (intentional for "bureaucratic clutter" vibe).
- Upgrades, when purchased, shrink to icons at the top right with tooltips on mouseover.

### Enhanced Activity Log

The game features a **Scrollable Event Log** system that provides enhanced activity tracking:

- **Standard Mode:** Basic activity log showing current turn events only
- **Enhanced Mode:** Unlocked after Turn 5 through the "Event Log System Upgrade" event
  - **Visual Enhancements:** Blue border, scrollable indicator, and navigation hints
  - **Complete History:** Access to all previous turn activities with turn headers
  - **Navigation Controls:** Arrow keys (↑↓) and mouse wheel scrolling support
  - **Smart Organization:** Turn-based organization with clear visual separation

**UI Improvements:**
- Visual border and indicators for enhanced readability
- Scroll arrows (▲▼) to indicate available content above/below current view
- Responsive sizing that adapts to screen dimensions
- Maintains current turn visibility while providing historical access

---

## Compute Resources & Employee System

### New Game Features

**Compute Resource System:**
- New compute resource added to game state, starts at 0
- "Buy Compute" action: $100 per 10 flops
- Weekly consumption: employees attempt to use 1 compute each
- Starting funding increased to $100,000 to support compute infrastructure

**Employee Productivity Cycle:**
- Each turn represents one week of operations
- Employees with compute access contribute to research progress (30% chance)
- Employees without compute incur doom penalties
- Research papers published when progress reaches 100 (+5 reputation per paper)

**Visual Employee Blobs:**
- Animated round blobs representing each staff member
- New hires animate in from the left side
- Productive employees display glowing green halos
- Clustered positioning in lower middle area, no overlapping
- Sound effects: "bloop" sound when new employees are hired

**Sound System:**
- Integrated SoundManager class with pygame audio
- Graceful fallback when no audio device available
- Mute button in bottom-right corner during gameplay
- Settings menu accessible from main menu

---

## Expanding the Game

### 1. **Adding/Editing Actions**

- Actions are in `actions.py` as a list of dicts.
- Each dict has: `name`, `desc`, `cost`, `upside`, `downside`, and `rules`.
- Example:
    ```python
    {
        "name": "Lobby Politicians",
        "desc": "+Reputation, possible doom reduction; costly.",
        "cost": 70,
        "upside": lambda gs: (gs._add('reputation', 3), gs._add('doom', -2)),
        "downside": lambda gs: gs._add('money', -10 if random.random() < 0.2 else 0),
        "rules": None
    }
    ```
- Add new actions by adding new dicts to `ACTIONS` in `actions.py`.

### 2. **Adding Upgrades**

- Upgrades are in `upgrades.py` as a list of dicts.
- Each dict: `name`, `desc`, `cost`, `effect_key`.
- Effects are handled in `game_state.py` and referenced in action logic.
- Add new upgrades by adding dicts to `UPGRADES` in `upgrades.py`.

### 3. **Adding/Editing Events**

- Events are in `events.py`.
- Each dict: `name`, `desc`, `trigger` (lambda returning bool), `effect` (lambda for effect).
- Example:
    ```python
    {
        "name": "Media Scandal",
        "desc": "Negative press coverage! Lose reputation.",
        "trigger": lambda gs: gs.reputation > 10 and random.random() < 0.1,
        "effect": lambda gs: gs._add('reputation', -random.randint(2, 4))
    }
    ```
- Add new events by adding dicts to `EVENTS` in `events.py`.

**Built-in Events:**
- **Lab Breakthrough:** Doom spikes based on security upgrades
- **Funding Crisis:** Financial setbacks when resources are low
- **Staff Burnout:** Staff leave when overworked and underpaid
- **Buy Accounting Software:** Enables balance change tracking (Turn 3+)
- **Event Log System Upgrade:** Unlocks scrollable activity history (Turn 5+)

### 4. **Seeded Challenges & Weekly Modes**

- The game prompts for a seed at startup.
- Use the same seed for repeatable scenarios (e.g., weekly challenge, competitions).
- The weekly seed is year+ISO week (e.g., `202531` for 2025 week 31).
- High scores are stored locally for each seed in `local_highscore.json`.

---

## Testing

The game includes automated tests to ensure core functionality works correctly. Tests are located in the `tests/` directory.

### Running Tests

Run all tests using Python's built-in unittest module:

```sh
python3 -m unittest discover tests -v
```

Or run a specific test file:

```sh
python3 -m unittest tests.test_game_state -v
```

### Sample Test

Here's an example test that verifies GameState initialization:

```python
import unittest
from game_state import GameState

class TestGameStateInitialization(unittest.TestCase):
    def test_game_state_default_values(self):
        """Test that a new GameState starts with the correct default values."""
        game_state = GameState("test_seed")
        
        # Verify core resource defaults
        self.assertEqual(game_state.money, 300)
        self.assertEqual(game_state.staff, 2)
        self.assertEqual(game_state.reputation, 15)
        self.assertEqual(game_state.doom, 12)
        self.assertFalse(game_state.game_over)
```

### Adding New Tests

When adding new features or fixing bugs, please add corresponding tests:

1. Create a new test file in `tests/` directory (e.g., `test_new_feature.py`)
2. Import the modules you want to test
3. Create test classes that inherit from `unittest.TestCase`
4. Write test methods that start with `test_`
5. Use assertions to verify expected behavior
6. Run tests to ensure they pass
7. **Update the Test Coverage section** in both README.md and PLAYERGUIDE.md to document what your tests cover

This helps keep the game stable and makes it easier for future contributors to understand expected behavior.

---

## Tips & Modular Structure

- All game content (actions, upgrades, events) is in its own file for easy patching.
- Add new features by editing the relevant file and referencing new upgrades in action/event logic.
- "Cluttered" UI and tooltips for purchased upgrades are intentional for future expansion (e.g., paperwork, news, etc.).
- The code is ready for further modularization and scenario/patch expansion!

### Game Logs

P(Doom) automatically generates detailed game logs for debugging and analysis purposes:

- **Location**: Game logs are saved in the `logs/` directory
- **Purpose**: Logs capture all actions, upgrades, events, and turn summaries for debugging and game balancing
- **Privacy**: Logs contain only game data and basic OS info - no personal information
- **Format**: Human-readable text files named `gamelog_<YYYYMMDD_HHMMSS>.txt`

These logs are useful for:
- **Players**: Reporting bugs with detailed game state information
- **Developers**: Analyzing game balance and debugging issues
- **Contributors**: Understanding game mechanics and testing changes

Log files are automatically excluded from version control but the `logs/` directory structure is preserved.

---

**Not affiliated with any AI org. For fun, education, and satire only.**

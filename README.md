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

This project uses [pytest](https://pytest.org/) as the testing framework. All tests are located in the `tests/` directory.

#### Installing Testing Dependencies

If you haven't already installed from requirements.txt:

```sh
pip install pytest
```

Or install all dependencies including testing tools:

```sh
pip install -r requirements.txt
```

#### Running Tests

To run all tests:

```sh
pytest
```

To run tests with verbose output:

```sh
pytest -v
```

To run a specific test file:

```sh
pytest tests/test_filename.py
```

#### Adding New Tests

- All test files should be placed in the `tests/` directory
- Test files should be named `test_*.py` (e.g., `test_game_state.py`, `test_actions.py`)
- Test functions should be named `test_*` (e.g., `test_player_can_buy_upgrade()`)
- Follow existing test patterns and keep tests focused and readable

#### For Contributors

When adding new features or modifying existing code:

1. **Always add or update tests** for your changes
2. **Run the full test suite** before submitting contributions: `pytest`
3. **Ensure all tests pass** - don't break existing functionality
4. **Write clear, descriptive test names** that explain what is being tested

Tests help ensure the game remains stable and functional as it evolves!

### Main Menu

When you launch the game, you'll see a main menu with the following options:

- **Launch with Weekly Seed**: Start immediately with the current week's challenge seed
- **Launch with Custom Seed**: Enter your own seed for repeatable games  
- **Options**: Placeholder for future settings (currently inactive)
- **Player Guide**: View the complete player guide with controls and strategies
- **README**: View this documentation file

**Navigation:**
- Use mouse clicks or arrow keys to navigate
- Press Enter or click to select an option
- Press Escape to quit from the main menu

### Gameplay

- The game now starts with a **main menu** where you can choose your game mode.
- Select "Launch with Weekly Seed" for the current week's challenge, or "Launch with Custom Seed" to enter your own.
- Enter a seed at startup (or leave blank for weekly challenge seed).
- Select actions (left column) by clicking buttons. Buy upgrades (right) by clicking. Purchased upgrades shrink to icons at the top right.
- Take as many actions as you want, then click "End Turn" (or press Space) to process choices and see results.
- Manage Money, Staff, Reputation, and p(Doom) (AI risk). Pay staff each turn.
- Watch out for random events and opponent progress!
- **Game Over**: p(Doom) reaches 100, all staff leave, or the opponent finishes their AGI.
- At game end, see your turn survived and local high score (per seed).

---

## Adaptive UI

- The window is 80% of your screen by default and resizable.
- UI elements adapt to fit; if crowded, elements may overlap (intentional for "bureaucratic clutter" vibe).
- Upgrades, when purchased, shrink to icons at the top right with tooltips on mouseover.

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

This helps keep the game stable and makes it easier for future contributors to understand expected behavior.

---

## Tips & Modular Structure

- All game content (actions, upgrades, events) is in its own file for easy patching.
- Add new features by editing the relevant file and referencing new upgrades in action/event logic.
- "Cluttered" UI and tooltips for purchased upgrades are intentional for future expansion (e.g., paperwork, news, etc.).
- The code is ready for further modularization and scenario/patch expansion!

---

**Not affiliated with any AI org. For fun, education, and satire only.**
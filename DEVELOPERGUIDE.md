# Developer Guide for P(Doom)

Welcome, contributors and modders! This guide explains how to develop, test, and extend P(Doom): Bureaucracy Strategy. It covers the project’s structure, testing practices, and guidelines for adding new features.

---

## Project Structure

- **main.py** — Game entry point and menu system.
- **game_state.py** — Core game logic and state management.
- **actions.py** — Action definitions (as Python dicts).
- **upgrades.py** — Upgrade definitions.
- **events.py** — Event definitions and special event logic.
- **ui.py** — Pygame-based UI code.
- **tests/** — Automated tests for core logic.
- **README.md** — Project overview, install, run, troubleshooting.
- **PLAYERGUIDE.md** — Gameplay instructions, tips, and FAQ for players.
- **DEVELOPERGUIDE.md** (this file) — Contributor and code documentation.

---

## Coding & Contribution Guidelines

- Keep code modular: actions, upgrades, and events are data-driven lists of dicts for easy editing and patching.
- When adding or changing features, always add or update corresponding tests.
- Use clear, descriptive commit messages and pull request descriptions.
- When you make changes affecting gameplay, update PLAYERGUIDE.md as well.

---

## Testing

### Running Tests

This project uses `pytest`. All tests are in the `tests/` directory.

```sh
pip install pytest
pytest
```

Or run a specific test file:

```sh
pytest tests/test_game_state.py
```

### Adding New Tests

- Place new test files in `tests/`
- Name files as `test_*.py`
- Test functions should be named `test_*`
- Use the existing tests as templates for structure and style

#### Example (pytest style):

```python
from game_state import GameState

def test_game_state_defaults():
    gs = GameState("testseed")
    assert gs.money == 300
    assert gs.staff == 2
    assert gs.reputation == 15
    assert gs.doom == 12
```

#### Example (unittest style):

```python
import unittest
from game_state import GameState

class TestGameState(unittest.TestCase):
    def test_defaults(self):
        gs = GameState("abc")
        self.assertEqual(gs.money, 300)
```

### Test Coverage

- Tests exist for GameState, upgrades, and some core mechanics.
- When you add new tests, update the “Test Coverage” sections in both README.md and PLAYERGUIDE.md.
- Tests should cover the main “happy path” and error/edge cases where appropriate.

---

## Adding New Content

### Actions

- Add new actions as dicts in `actions.py`.
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

### Upgrades

- Add new upgrades as dicts in `upgrades.py`.
- Reference new effects in `game_state.py` if needed (see `upgrade_effects`).

### Events

- Add new events as dicts in `events.py`.
- Each event should have a `trigger` and an `effect`.
- If you introduce new event logic, document it here.

---

## Documentation Maintenance

- README.md: Project intro, install, quickstart, troubleshooting, links to guides.
- PLAYERGUIDE.md: Player-facing gameplay guide.
- DEVELOPERGUIDE.md: Contributor/developer info (this file).
- When making changes, ensure relevant guides are updated and cross-referenced as appropriate.
- If your change affects gameplay or user experience, update PLAYERGUIDE.md.
- If your change affects code, tests, or architecture, update this guide.

---

## Troubleshooting for Developers

- If tests are failing, ensure your environment matches requirements (Python 3.8+, pygame, pytest).
- If you encounter import errors, check your working directory and PYTHONPATH.
- For UI bugs, test different screen sizes; the UI adapts but may have quirks.
- For gameplay bugs, add focused tests to isolate logic errors.

---

## Further Resources

- [pytest documentation](https://docs.pytest.org/)
- [pygame documentation](https://www.pygame.org/docs/)
- Open issues or discussions on GitHub for further help.

---

Happy hacking!
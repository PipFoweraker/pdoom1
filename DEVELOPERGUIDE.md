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

## Game Logs

P(Doom) includes a comprehensive logging system that captures all meaningful in-game actions and events for debugging, analysis, and balancing purposes.

### Log File Location and Format

- **Directory**: `logs/` (created automatically)
- **File naming**: `gamelog_<YYYYMMDD_HHMMSS>.txt` (web-safe format)
- **Encoding**: UTF-8 text files

### What Gets Logged

The logging system captures:

1. **Game Start Information**:
   - Timestamp of game start
   - Game version
   - Seed used
   - Basic OS type (Linux/Windows/Darwin only - no personal info)

2. **Player Actions**:
   - All actions selected and executed
   - Action costs and turn numbers
   - Timestamps for each action

3. **Upgrade Purchases**:
   - Upgrade name and cost
   - Turn when purchased
   - Timestamps

4. **Game Events**:
   - Triggered events with descriptions
   - Turn numbers and timestamps

5. **Turn Summaries**:
   - End-of-turn resource states (Money, Staff, Reputation, Doom)
   - Turn progression tracking

6. **Game End**:
   - Reason for game ending (victory/defeat/quit/crash)
   - Final turn number and resource state
   - Final timestamp

### Privacy and Data Protection

The logging system is designed to be privacy-conscious:

- **No personal information**: No usernames, file paths, or system details beyond OS type
- **Local only**: Logs are stored locally in the `logs/` directory
- **Minimal system info**: Only basic OS type for debugging compatibility issues
- **No network transmission**: Logs never leave the player's machine

### Log Lifecycle Management

- **Creation**: One log file per game session
- **Retention**: No automatic cleanup - players manage their own log files
- **Size**: Logs are typically small (< 1KB for normal games)
- **Git exclusion**: Log files are excluded from version control via `.gitignore`

### Using Logs for Development

Logs are valuable for:

- **Balancing**: Analyzing player behavior patterns and resource progression
- **Debugging**: Understanding game state when bugs are reported
- **Testing**: Verifying game mechanics work as expected
- **Analytics**: Understanding how players engage with different features

### Log File Schema Example

```
=== GAME START ===
Timestamp: 2025-07-31 10:10:06
Game Version: v3
Seed: weekly_seed_202531
OS: Linux
==================
[10:10:06] Turn 0: Action 'Grow Community' (cost: 25)
[10:10:06] Turn 0: Upgrade 'Accounting Software' purchased (cost: 50)
[10:10:06] Turn 0: Event 'Media Leak' - Reputation drops but awareness grows
[10:10:06] Turn 1 End: Money=225, Staff=3, Reputation=18, Doom=14/100

=== GAME END ===
Timestamp: 10:10:45
Reason: Player victory - opponent progress halted
Final Turn: 15
Final Money: 150
Final Staff: 5
Final Reputation: 45
Final Doom: 75/100
================
```

### Future Log Management

Consider implementing:

- Log rotation or archival for long-term players
- Optional anonymized analytics export
- Log parsing tools for developers
- Integration with telemetry systems (with explicit user consent)

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
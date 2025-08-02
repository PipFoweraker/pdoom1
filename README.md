# P(Doom): Bureaucracy Strategy Game Prototype

A satirical meta-strategy game about AI Safety, inspired by *Papers, Please*, *Pandemic*, and clicker games.

**📖 Documentation:**
- **[Player Guide](PLAYERGUIDE.md)** - How to play, controls, and strategies
- **[Developer Guide](DEVELOPERGUIDE.md)** - Contributing, code structure, and testing

## Quick Start

### Requirements
- Python 3.8+
- [pygame](https://www.pygame.org/)

### Installation & Setup
```sh
# Install core dependency
pip install pygame

# Or install all dependencies (including testing tools)
pip install -r requirements.txt
```

### Run the Game
```sh
python main.py
```

The game will open with a main menu where you can choose game modes, access documentation, or report bugs.

## Game Features

### Core Gameplay
- **Resource Management**: Balance money, staff, reputation, and p(Doom) levels
- **Action System**: Choose from various actions each turn to advance your strategy
- **Research & Development**: Publish papers, buy compute, and advance AI safety
- **Enhanced Event System**: Navigate unexpected challenges with advanced response options

### Enhanced Event System
The game features a sophisticated event system that evolves as you play:

**Event Types:**
- **Normal Events**: Standard immediate events (existing gameplay)
- **Popup Events**: Critical situations requiring immediate attention with multiple response options
- **Deferred Events**: Events you can postpone for strategic timing, but they expire after several turns

**Event Actions:**
- **Accept**: Handle the event with full impact
- **Defer**: Postpone the event for later (limited turns)
- **Reduce**: Handle with reduced impact through quick response
- **Dismiss**: Ignore the event (may have consequences)

**Unlocking Enhanced Events:**
- Enhanced event system unlocks automatically after turn 8
- Provides popup overlays for critical events and a deferred events zone
- Allows strategic management of multiple concurrent crises

### Opponents System
Race against 3 competing AI labs, each with unique characteristics:
- **TechCorp Labs**: Well-funded tech giant with aggressive timelines
- **National AI Initiative**: Government-backed program with regulatory influence  
- **Frontier Dynamics**: Secretive startup with mysterious backing

**Intelligence Gathering:**
- Use **Espionage** to discover competitors and gather basic intelligence
- Unlock **Scout Opponent** (turn 5+) for focused intelligence operations
- Reveal hidden stats: budget, researchers, lobbyists, compute resources, and progress
- Monitor opponent activities and strategic decisions

**Competitive Dynamics:**
- Opponents spend budget on capabilities research, hiring, and lobbying
- Track competitor progress toward dangerous AGI deployment (0-100%)
- Game ends if any opponent reaches 100% progress
- Opponent research contributes to global p(Doom) levels

## Troubleshooting

### Common Issues

**Game won't start:**
- Ensure Python 3.8+ is installed: `python --version`
- Install pygame: `pip install pygame`
- Check that all files are in the same directory

**Missing pygame module:**
```sh
pip install pygame
```

**Black screen or UI not responding:**
- Try resizing the window
- Restart the game
- Check terminal for error messages

### Error Logs
The game automatically creates detailed logs in the `logs/` directory:
- **Location**: `logs/gamelog_<YYYYMMDD_HHMMSS>.txt`
- **Contents**: Game actions, events, and state changes
- **Privacy**: No personal information collected
- **Use**: Helpful for reporting bugs and debugging issues

### Testing the Installation
Verify your installation works by running the test suite:

```sh
# Run all tests (should show 32 tests passing)
python -m unittest discover tests -v
```

If tests fail, check your Python and pygame installation.

### Getting Help

- **In-game**: Use the "Report Bug" option in the main menu
- **Documentation**: See [Player Guide](PLAYERGUIDE.md) for gameplay help
- **Development**: See [Developer Guide](DEVELOPERGUIDE.md) for code issues

### Dependencies

**Core Requirements:**
- Python 3.8+
- pygame (graphics and input handling)

**Optional/Development:**
- pytest (for testing)
- Standard library modules: os, sys, json, random, datetime

**System Requirements:**
- Any OS that supports Python and pygame (Windows, macOS, Linux)
- ~50MB disk space
- Basic graphics support (no special hardware needed)

---

**Not affiliated with any AI org. For fun, education, and satire only.**

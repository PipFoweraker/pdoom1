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

# P(Doom): Bureaucracy Strategy Game

P(Doom) is a Python-based pygame strategy game about AI Safety. It's a GUI application with comprehensive testing and documentation.

**Current Version**: v0.2.12 "Development Infrastructure Enhancement"

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Development Infrastructure Status

### Type Annotation Progress (MAJOR MILESTONE ACHIEVED)
- **ui.py**: ✅ **100% COMPLETE** (4,235 lines, 35+ functions fully annotated)
- **game_state.py**: ✅ **85-90% COMPLETE** (55+ of ~65 methods annotated)
- **Estimated pylance reduction**: 60-70% of original 5,093+ strict mode issues resolved
- **Established patterns**: pygame.Surface, Optional[Dict], Tuple[bool, str], Union types
- **Next targets**: Complete remaining ~10 game_state.py methods, then select next monolith

### Dev Blog System (NEW INFRASTRUCTURE)
- **Automated documentation**: `python dev-blog/create_entry.py [template] [slug]`
- **Index generation**: `python dev-blog/generate_index.py`
- **Templates available**: development-session, milestone
- **ASCII-only enforcement**: All content must use ASCII characters only
- **Website integration**: Ready for automated content pickup

### Quality Assurance Tools
- **autoflake cleanup**: Use `.venv\\Scripts\\python.exe -m autoflake --remove-all-unused-imports --remove-unused-variables --check --recursive .`
- **Type checking**: pylance strict mode with comprehensive coverage
- **Import validation**: Regular `from src.core.game_state import GameState` checks

## Working Effectively

### Bootstrap and Setup
- **Python Version**: Requires Python 3.9+. Tested and verified on Python 3.12.3.
- Install dependencies: `pip install -r requirements.txt`
  - Core dependencies: pygame>=2.0.0, numpy>=1.20.0, jsonschema>=4.0.0, pytest>=7.0.0
  - Installation takes ~10-30 seconds typically
- **No build process required** - This is pure Python with no compilation step

### Running Tests
- **CRITICAL**: Run the full test suite: `python -m unittest discover tests -v`
- **TIMING**: Test suite takes approximately 38 seconds with 507 tests. NEVER CANCEL - Set timeout to 90+ seconds.
- Alternative test runner: `python -m pytest tests/ -v`
- **Expected**: 4 tests currently fail (unrelated to core functionality) - this is normal
- **Audio warnings**: ALSA warnings in headless environments are normal and don't affect functionality

### Running the Game
- **Start the game**: `python main.py`
- **IMPORTANT**: This is a pygame GUI application that requires a display
- **Headless environment**: Game will start but you cannot interact with the GUI
- **Validation in headless**: Use programmatic testing instead of GUI interaction

### Development Validation
- **Always validate programmatically** after making changes:
```python
from src.core.game_state import GameState
from src.services.version import get_display_version
print(f'Testing P(Doom) {get_display_version()}')
gs = GameState('test-seed')
print('✓ Game state initializes correctly')
# Test your specific changes here
```

### Type Annotation Workflow (ESTABLISHED PATTERNS)
- **UI functions**: Use `pygame.Surface` for all rendering parameters
- **Rect methods**: Return `Tuple[int, int, int, int]` for coordinate tuples
- **Complex returns**: `Optional[Dict[str, Any]]` for optional data, `Tuple[bool, str]` for success/message
- **Union types**: `Union[pygame.Rect, Tuple[int, int, int, int]]` for flexible input
- **Method signatures**: Always include parameter and return type annotations
- **Import validation**: Test `from src.core.game_state import GameState` after changes

## Validation

### Manual Testing Requirements
- **After code changes**: Always run the test suite with 90+ second timeout
- **Game functionality**: Validate using GameState programmatic tests, not GUI interaction
- **Turn mechanics**: Game starts at turn 0, advances to turn 1 after first end_turn()
- **Resource systems**: Test money, staff, doom, action points, and reputation systems
- **Action execution**: Verify actions can be selected and executed correctly

### CI/CD Validation
- **Before committing**: Always run `python -m unittest discover tests -v`
- **GitHub Actions**: Tests run on Python 3.9, 3.10, 3.11, 3.12
- **Version consistency**: Version managed in `version.py` using semantic versioning

## Repository Navigation

### Key Directories and Files
```
├── main.py                 # Main entry point - start game here
├── game_state.py          # Core game logic and state management
├── actions.py             # Available player actions and mechanics
├── events.py              # Random events and game scenarios
├── ui.py                  # User interface rendering and interaction
├── tests/                 # Comprehensive test suite (507 tests)
├── configs/               # Game configuration files
├── version.py             # Centralized version management
├── requirements.txt       # Python dependencies
└── docs/                  # Documentation and guides
```

### Important Files for Common Tasks
- **Game mechanics**: `game_state.py`, `actions.py`, `events.py`
- **UI changes**: `ui.py`, `overlay_manager.py`, `visual_feedback.py`
- **Configuration**: `config_manager.py`, `configs/`
- **Testing**: `tests/` (extensive test coverage for all systems)
- **Audio**: `sound_manager.py`
- **Opponents**: `opponents.py`
- **Onboarding**: `onboarding.py`, tutorial system

### Documentation Files
- **README.md**: Installation and quick start guide
- **docs/DEVELOPERGUIDE.md**: Comprehensive development documentation
- **docs/CONTRIBUTING.md**: Development guidelines and protocols
- **docs/PLAYERGUIDE.md**: Gameplay instructions and controls
- **docs/CONFIG_SYSTEM.md**: Configuration and customization guide

## Common Development Tasks

### Adding New Game Features
- **Actions**: Modify `actions.py` and add tests in `tests/test_actions.py`
- **Events**: Update `events.py` and test in `tests/test_events.py`
- **UI elements**: Update `ui.py` and test UI behavior programmatically
- **Game mechanics**: Core logic goes in `game_state.py`

### Testing New Features
- **Always add tests**: Follow existing patterns in `tests/` directory
- **Test file naming**: Use `test_<feature>.py` format
- **Test structure**: Import unittest, extend unittest.TestCase
- **Game state setup**: Use `GameState('test-seed')` for consistent testing

### Configuration and Settings
- **Default config**: Generated automatically in `config_manager.py`
- **User configs**: Stored in `configs/` directory
- **Schema validation**: Uses `jsonschema` for configuration validation

### Version Management
- **Update version**: Edit `version.py` following semantic versioning
- **Version display**: Available via `get_display_version()` function
- **Release process**: See `RELEASE_CHECKLIST.md` for complete procedures

## Critical Timing and Timeout Information

### Command Timeouts (NEVER CANCEL)
- **Test suite**: 38 seconds typical, use 90+ second timeout
- **Dependency installation**: 30 seconds typical, use 60+ second timeout
- **Game initialization**: <1 second, use 10+ second timeout for safety
- **Individual test files**: Usually <5 seconds, use 30+ second timeout

### CI/CD Timing Expectations
- **GitHub Actions test workflow**: ~2-3 minutes across all Python versions
- **Release workflow**: ~5-10 minutes including artifact generation
- **Local development cycle**: Dependencies + tests = ~70 seconds total

## Architecture Notes

### Game Systems
- **Turn-based**: Players select actions, then advance turn
- **Resource management**: Money, staff, reputation, doom, action points, compute
- **Event system**: Random events affect game state each turn
- **Opponent AI**: 3 AI labs with different strategies and hidden information
- **Milestone system**: Unlocks new mechanics as lab grows

### Technical Architecture
- **Pygame**: GUI framework for rendering and input
- **JSON**: Configuration and save data format
- **unittest**: Primary testing framework (pytest also supported)
- **Modular design**: Clear separation between game logic, UI, and systems

### Audio System
- **Optional dependency**: Game works without audio
- **NumPy required**: For sound effects (install numpy for full experience)
- **Headless compatibility**: Audio disabled in environments without sound hardware

## Troubleshooting

### Common Issues and Solutions
- **pygame import errors**: Ensure `pip install pygame` completed successfully
- **ALSA warnings**: Normal in headless environments, game functions correctly
- **Test failures**: 4 tests currently fail (known issue), not related to core functionality
- **Audio issues**: Install numpy (`pip install numpy`) for sound effects
- **Display issues**: GUI requires display - use programmatic validation in headless environments

### Error Recovery
- **Dependency issues**: Re-run `pip install -r requirements.txt`
- **Test environment**: Use `python -c "from game_state import GameState; GameState('test')"` to verify
- **Version check**: Use `python -c "from version import get_display_version; print(get_display_version())"`

## Quick Reference Commands

### Essential Commands (Copy-Paste Ready)
```bash
# Install dependencies
pip install -r requirements.txt

# Run full test suite (NEVER CANCEL - 90+ second timeout)
python -m unittest discover tests -v

# Quick functionality test
python -c "from game_state import GameState; gs = GameState('test'); print('✓ Working correctly')"

# Start the game (requires display)
python main.py

# Check version
python -c "from version import get_display_version; print(get_display_version())"
```

### Development Workflow
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation
python -c "from game_state import GameState; GameState('test')"

# 3. Run tests before changes (90+ second timeout)
python -m unittest discover tests -v

# 4. Make your changes

# 5. Run tests after changes (90+ second timeout)
python -m unittest discover tests -v

# 6. Test specific functionality programmatically
python -c "# Your validation code here"
```

Remember: This is a GUI application - always use programmatic validation rather than attempting to interact with the pygame window in automated environments.
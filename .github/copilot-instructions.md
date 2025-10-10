# P(Doom): Bureaucracy Strategy Game

P(Doom) is a Python-based pygame strategy game about AI Safety. It's a GUI application with comprehensive testing and documentation.

**Current Version**: v0.8.0 "Alpha Release - Modular Architecture"

**CRITICAL ASCII-ONLY RULE: ALL commit messages, GitHub issue comments, documentation, and project content MUST use ASCII characters only. NO Unicode symbols, emojis, or special characters. Use text like "SUCCESS" instead of checkmarks, "BULLET" instead of bullet points.**

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Session Handoff Protocol

### Session Documentation Standards
- **Handoff files**: Use format `SESSION_HANDOFF_YYYY-MM-DD_HHMM.md`
- **Archive location**: Move completed handoffs to `docs/development-sessions/`
- **Template**: Maintain `SESSION_HANDOFF_TEMPLATE.md` for consistent structure
- **Key sections**: Achievements, Next Priorities, Technical Context, Success Metrics

### Development State Tracking
- **Current version**: Always verify via `src/services/version.py`
- **Architecture status**: Track modular extraction progress (currently 558 lines extracted)
- **Test suite status**: Document test count and expected runtime (~500+ tests, 90+ seconds)
- **Documentation organization**: Reference current `docs/` structure with 5 subdirectories

### Context Preservation Between Sessions
- **Technical debt**: Document refactoring targets and architectural decisions
- **Community engagement**: Track alpha testing feedback and GitHub activity
- **Performance metrics**: Note baseline measurements for regression detection
- **Configuration state**: Document any settings or environment changes

## Version Management Protocol
- **CRITICAL**: Always verify version display matches current development state
- **In-game version**: Check UI footer displays correct version from `src/services/version.py`
- **Branch versioning**: Hotfix branches increment patch version beyond main branch
- **Version synchronization**: If version appears outdated, check `src/services/version.py` and update accordingly
- **Format**: `vMAJOR.MINOR.PATCH+BUILD` (e.g., "v0.3.4+hotfix1")

## Critical System Information (v0.8.0)
- **MODULAR ARCHITECTURE ACHIEVEMENT**: 558 lines extracted from game_state.py monolith (11.6% reduction)
- **6 FOCUSED MODULES CREATED**: Clean separation of concerns with zero regressions
- **ALPHA TESTING READY**: F10 dev mode, screenshot tools, verbose logging, debug overlays
- **DOCUMENTATION ORGANIZED**: 5 focused subdirectories replacing flat structure
- **MODERN README**: Updated with screenshots, alpha features, and v0.8.0 achievements
- **BOOTSTRAP ECONOMIC SYSTEM**: Complete economic calibration implemented ($100k starting funds)
- **RECENT MAJOR WORK**: Monolith refactoring, documentation organization, README modernization

## Development Infrastructure Status

### Type Annotation Progress (MAJOR MILESTONE ACHIEVED)
- **ui.py**: SUCCESS **100% COMPLETE** (4,235 lines, 35+ functions fully annotated)
- **game_state.py**: SUCCESS **85-90% COMPLETE** (55+ of ~65 methods annotated)
- **Estimated pylance reduction**: 60-70% of original 5,093+ strict mode issues resolved
- **Established patterns**: pygame.Surface, Optional[Dict], Tuple[bool, str], Union types
- **Next targets**: Complete remaining ~10 game_state.py methods, then select next monolith

### Dev Blog System (NEW INFRASTRUCTURE)
- **Automated documentation**: `python dev-blog/create_entry.py [template] [slug]`
- **Index generation**: `python dev-blog/generate_index.py`
- **Templates available**: development-session, milestone
- **ASCII-only enforcement**: All content must use ASCII characters only
- **Website integration**: Ready for automated content pickup

### Strategic Planning System (NEW INFRASTRUCTURE)
- **Alpha/Beta Roadmap**: Complete 8-week strategic release plan in `assets/ALPHA_BETA_ROADMAP.md`
- **Issue Tracking**: 6 strategic issues created for systematic implementation
- **HIGH Priority**: Starting cash ($2K -> $100K COMPLETED), leaderboard activation, logging system
- **MEDIUM Priority**: Multi-turn delegation, dev tools enhancement, deterministic RNG
- **Ready for Implementation**: Week 1-2 targets quick wins, Week 3-8 for advanced features

### ASCII Compliance Requirements
- **CRITICAL**: All commit messages must use ASCII characters only
- **GitHub interactions**: NO emojis or Unicode in issue comments, PR descriptions, close messages
- **Documentation**: No Unicode characters (emojis, special symbols) in any text
- **Code comments**: ASCII-only for cross-platform compatibility
- **File content**: All project files must be ASCII-compliant
- **Terminal output**: Use "SUCCESS", "ERROR", "WARNING" instead of symbols

## Alpha Testing Protocol (v0.8.0+)

### Current Alpha Features
- **Dev mode**: F10 toggle, Ctrl+D diagnostics, Ctrl+E emergency recovery
- **Screenshot system**: `[` key capture with automatic timestamping
- **Verbose logging**: Configurable detail levels for troubleshooting
- **Debug overlays**: Real-time performance and state information

### Community Feedback Integration
- **GitHub Discussions**: Primary channel for alpha testing feedback
- **Issue templates**: Structured bug reports with log excerpts and screenshots
- **Testing scenarios**: Provide specific checklist items for community validation
- **Performance tracking**: Document baseline metrics for comparison

### Quality Assurance Requirements
- **Pre-session validation**: Always run module import tests before development
- **Post-session testing**: Full test suite execution with regression checking
- **Cross-platform verification**: Test on multiple OS when possible
- **Performance profiling**: Regular analysis of startup time and memory usage

## Modular Architecture Status (Updated 2025-09-19)

### Extraction Progress
- **Total extracted**: 558 lines from game_state.py monolith
- **Current modules**: 6 focused components with clean separation
- **Remaining monolith**: 5,682 lines (down from 6,240 original)
- **Next targets**: Input management system, audio system, UI rendering pipeline

### Module Dependencies
- **Import validation**: Test all extracted modules on session start
- **Circular dependency prevention**: Monitor import chains during development
- **Type annotation maintenance**: Preserve comprehensive typing during refactoring
- **Test coverage**: Ensure each module has dedicated test coverage

### Refactoring Guidelines
- **Minimum extraction**: Target 100+ line extractions for meaningful modules
- **Functional cohesion**: Group related functionality, avoid utility dump modules
- **Clean interfaces**: Minimize parameter passing between modules
- **Regression prevention**: Validate all functionality after each extraction

### Quality Assurance Tools
- **Standards enforcement**: Use `python scripts/enforce_standards.py --check-all` for comprehensive project validation
- **ASCII compliance**: Use `python scripts/ascii_compliance_fixer.py` to remove Unicode characters from all files
- **autoflake cleanup**: Use `python -m autoflake --remove-all-unused-imports --remove-unused-variables --check --recursive .`
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
print('CHECKED Game state initializes correctly')
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
|--- main.py                 # Main entry point - start game here
|--- game_state.py          # Core game logic and state management
|--- actions.py             # Available player actions and mechanics
|--- events.py              # Random events and game scenarios
|--- ui.py                  # User interface rendering and interaction
|--- tests/                 # Comprehensive test suite (507 tests)
|--- configs/               # Game configuration files
|--- version.py             # Centralized version management
|--- requirements.txt       # Python dependencies
`--- docs/                  # Documentation and guides
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
python -c "from game_state import GameState; gs = GameState('test'); print('CHECKED Working correctly')"

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
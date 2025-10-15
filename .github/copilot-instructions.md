# P(Doom): Bureaucracy Strategy Game

P(Doom) is a Python-based pygame strategy game about AI Safety. It's a GUI application with comprehensive testing, automation, and documentation.

**Current Version**: v0.10.1 "Advanced Infrastructure - Automation & Quality Systems"

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## CRITICAL UPDATES FROM v0.8.0 TO v0.10.1

### **AUTOMATION REVOLUTION COMPLETE**
- **Issue Sync Automation**: 42+ local issues bidirectionally sync with GitHub (RESOLVES 380)
- **CI/CD Pipeline**: Enhanced multi-stage pipeline with quality gates
- **Pre-commit Hooks**: ASCII compliance, version consistency, import validation
- **Quality Assurance**: Comprehensive automated standards enforcement

### **PROGRAMMATIC CONTROL SYSTEM**
- **Complete game control without GUI**: Validated programmatic testing infrastructure
- **Automated testing scenarios**: Multi-turn game progression, state validation
- **Performance profiling**: Baseline measurement and regression detection
- **Cross-platform validation**: Windows encoding fixes implemented

### **INFRASTRUCTURE MATURITY**
- **Robust error handling**: Subprocess encoding fixes for Windows systems
- **Comprehensive logging**: Enhanced audit trails and debugging capabilities
- **Version management**: Centralized system with website sync automation
- **Documentation organization**: 5 focused subdirectories with automated sync

## Session Handoff Protocol

### Session Documentation Standards
- **Handoff files**: Use format `SESSION_COMPLETION_SUMMARY_YYYY-MM-DD_TOPIC.md`
- **Archive location**: Move completed handoffs to `docs/development-sessions/`
- **Template**: Maintain comprehensive structure with achievements, technical context, success metrics
- **Key sections**: Mission Accomplished, Technical Implementation, Testing Results, Next Steps

### Development State Tracking
- **Current version**: Always verify via `src/services/version.py` (currently v0.10.1)
- **Architecture status**: Track modular extraction progress and programmatic control systems
- **Test suite status**: Document test count and expected runtime (~500+ tests, 90+ seconds)
- **Automation status**: Monitor CI/CD pipeline health, issue sync functionality, quality gates

### Context Preservation Between Sessions
- **Technical debt**: Document refactoring targets and architectural decisions
- **Automation status**: Track CI/CD pipeline health, issue sync performance
- **Quality metrics**: Note baseline measurements and quality gate performance
- **Infrastructure changes**: Document encoding fixes, programmatic control enhancements

## Version Management Protocol
- **CRITICAL**: Always verify version display matches current development state
- **In-game version**: Check UI footer displays correct version from `src/services/version.py`
- **Current version**: v0.10.1 with comprehensive infrastructure automation
- **Version synchronization**: If version appears outdated, check `src/services/version.py` and update accordingly
- **Format**: `vMAJOR.MINOR.PATCH` (semantic versioning with optional pre-release/build metadata)

## Critical System Information (v0.10.1)

### **AUTOMATION INFRASTRUCTURE COMPLETE**
- **BIDIRECTIONAL ISSUE SYNC**: GitHub <-> Local markdown with robust encoding (42+ issues synchronized)
- **ENHANCED CI/CD**: Multi-stage pipeline with quality gates, version validation, cross-platform testing
- **PRE-COMMIT SYSTEMS**: ASCII compliance, import validation, standards enforcement
- **QUALITY ASSURANCE**: Comprehensive automated validation with `scripts/enforce_standards.py`

### **PROGRAMMATIC CONTROL ACHIEVEMENT**
- **GUI-FREE GAME CONTROL**: Complete programmatic testing infrastructure operational
- **AUTOMATED SCENARIOS**: Multi-turn progression, state validation, performance profiling
- **CROSS-PLATFORM READY**: Windows encoding issues resolved, universal compatibility
- **TESTING INFRASTRUCTURE**: 500+ tests with comprehensive coverage and regression prevention

### **INFRASTRUCTURE MATURITY**
- **MODULAR ARCHITECTURE**: Continued extraction from monoliths with clean separation
- **DOCUMENTATION EXCELLENCE**: 5 focused subdirectories with automated synchronization
- **VERSION MANAGEMENT**: Centralized system with website integration and automated workflows
- **ERROR HANDLING**: Robust subprocess encoding with platform-specific fallbacks

## Development Infrastructure Status

### Automation Systems (NEW IN v0.10.1)
- **Issue Sync**: `scripts/issue_sync_bidirectional.py` with UTF-8 encoding fixes
- **CI/CD Pipeline**: `.github/workflows/enhanced-cicd-pipeline.yml` with quality gates
- **Pre-commit Hooks**: ASCII compliance, version consistency, import validation
- **Quality Enforcement**: `scripts/enforce_standards.py --check-all` comprehensive validation

### Programmatic Control System (NEW IN v0.10.1)
- **GUI-free testing**: Complete game control without pygame display
- **Automated scenarios**: Multi-turn progression and state validation
- **Performance profiling**: Baseline measurements and regression detection
- **Cross-platform compatibility**: Windows encoding fixes implemented

### Type Annotation Progress (ONGOING)
- **ui.py**: 100% COMPLETE (4,235 lines, 35+ functions fully annotated)
- **game_state.py**: 85-90% COMPLETE (55+ of ~65 methods annotated)
- **Estimated pylance reduction**: 60-70% of original 5,093+ strict mode issues resolved
- **Established patterns**: pygame.Surface, Optional[Dict], Tuple[bool, str], Union types

### ASCII Compliance Requirements (ENHANCED)
- **CRITICAL**: All commit messages must use ASCII characters only
- **Automated enforcement**: `scripts/ascii_compliance_fixer.py` with intelligent conversion
- **Pre-commit validation**: Automatic ASCII compliance checking before commits
- **Cross-platform compatibility**: Enhanced for Windows development environments

## Working Effectively

### Bootstrap and Setup
- **Python Version**: Requires Python 3.9+. Tested and verified on Python 3.12.3.
- Install dependencies: `pip install -r requirements.txt`
  - Core dependencies: pygame>=2.0.0, numpy>=1.20.0, jsonschema>=4.0.0, pytest>=7.0.0
  - Installation takes ~10-30 seconds typically
- **No build process required** - This is pure Python with no compilation step
- **Automated quality checks**: Pre-commit hooks ensure code quality automatically

### Running Tests
- **CRITICAL**: Run the full test suite: `python -m unittest discover tests -v`
- **TIMING**: Test suite takes approximately 38-45 seconds with 500+ tests. NEVER CANCEL - Set timeout to 90+ seconds.
- **Alternative test runner**: `python -m pytest tests/ -v`
- **Expected**: All tests should pass with the enhanced infrastructure
- **Audio warnings**: ALSA warnings in headless environments are normal and don't affect functionality

### Running the Game
- **Start the game**: `python main.py`
- **IMPORTANT**: This is a pygame GUI application that requires a display
- **Headless environment**: Game will start but you cannot interact with the GUI
- **Programmatic control**: Use `GameState('test-seed')` for headless testing and validation

### Development Validation (ENHANCED)
- **Always validate programmatically** after making changes:
```python
from src.core.game_state import GameState
from src.services.version import get_display_version
print(f'Testing P(Doom) {get_display_version()}')
gs = GameState('test-seed')
print('CHECKED Game state initializes correctly')
# Test your specific changes here
```

### Quality Assurance Tools (NEW)
- **Comprehensive validation**: `python scripts/enforce_standards.py --check-all`
- **ASCII compliance**: `python scripts/ascii_compliance_fixer.py` for Unicode removal
- **Import validation**: Automated testing of core module imports
- **Pre-commit hooks**: Automatic quality validation before commits

### Type Annotation Workflow (ESTABLISHED PATTERNS)
- **UI functions**: Use `pygame.Surface` for all rendering parameters
- **Rect methods**: Return `Tuple[int, int, int, int]` for coordinate tuples
- **Complex returns**: `Optional[Dict[str, Any]]` for optional data, `Tuple[bool, str]` for success/message
- **Union types**: `Union[pygame.Rect, Tuple[int, int, int, int]]` for flexible input
- **Method signatures**: Always include parameter and return type annotations
- **Import validation**: Test `from src.core.game_state import GameState` after changes

## Automation Infrastructure (NEW SECTION)

### Issue Synchronization System
- **Bidirectional sync**: `python scripts/issue_sync_bidirectional.py --sync-all --live`
- **GitHub integration**: Automated GitHub <-> local markdown synchronization
- **Encoding robustness**: UTF-8 with Windows-specific fallback handling
- **Audit trail**: Comprehensive logging of all synchronization operations

### CI/CD Pipeline Enhancement
- **Multi-stage validation**: Basic validation, code quality, advanced testing
- **Quality gates**: ASCII compliance, version consistency, import validation
- **Cross-platform testing**: Windows, macOS, Linux compatibility validation
- **Automated deployment**: Release workflows with comprehensive testing

### Pre-commit Hook System
- **ASCII compliance**: Automatic Unicode character detection and conversion
- **Version validation**: Ensure version consistency across files
- **Import checking**: Validate core module import functionality
- **Standards enforcement**: Comprehensive code quality validation

## Programmatic Control System (NEW SECTION)

### GUI-Free Game Control
- **Complete game state management**: Full game control without pygame display
- **Automated testing scenarios**: Multi-turn progression and validation
- **State verification**: Comprehensive game state consistency checking
- **Performance profiling**: Baseline measurements and regression detection

### Cross-Platform Compatibility
- **Windows encoding fixes**: Robust subprocess handling with UTF-8 fallbacks
- **Universal compatibility**: Tested across Windows, macOS, Linux environments
- **Error recovery**: Graceful degradation on platform-specific issues
- **Comprehensive logging**: Enhanced debugging capabilities for all platforms

### Testing Infrastructure Enhancement
- **500+ comprehensive tests**: Full coverage with programmatic validation
- **Regression prevention**: Automated detection of functionality breaks
- **Performance tracking**: Baseline measurement and monitoring
- **Quality assurance**: Continuous validation of core game functionality
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

## Repository Navigation (UPDATED)

### Key Directories and Files
```
|--- main.py                 # Main entry point - start game here
|--- src/core/game_state.py  # Core game logic and state management
|--- src/core/actions.py     # Available player actions and mechanics
|--- src/services/version.py # Centralized version management (v0.10.1)
|--- scripts/                # Automation scripts and quality tools
|--- tests/                  # Comprehensive test suite (500+ tests)
|--- configs/                # Game configuration files
|--- requirements.txt        # Python dependencies
`--- docs/                   # Documentation and guides (5 subdirectories)
```

### Automation Scripts (NEW)
- **Issue sync**: `scripts/issue_sync_bidirectional.py` - GitHub synchronization
- **Quality enforcement**: `scripts/enforce_standards.py` - Comprehensive validation
- **ASCII compliance**: `scripts/ascii_compliance_fixer.py` - Unicode cleanup
- **Pre-version bump**: `scripts/pre_version_bump.py` - Release validation

### Infrastructure Files (NEW)
- **CI/CD pipeline**: `.github/workflows/enhanced-cicd-pipeline.yml`
- **Version sync**: `.github/workflows/sync-game-version.yml`
- **Quality checks**: `.github/workflows/quality-checks.yml`
- **Pre-commit hooks**: Automated quality validation system

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

## Quick Reference Commands (UPDATED)

### Essential Commands (Copy-Paste Ready)
```bash
# Install dependencies
pip install -r requirements.txt

# Run full test suite (NEVER CANCEL - 90+ second timeout)
python -m unittest discover tests -v

# Quick functionality test
python -c "from src.core.game_state import GameState; gs = GameState('test'); print('CHECKED Working correctly')"

# Start the game (requires display)
python main.py

# Check version (current: v0.10.1)
python -c "from src.services.version import get_display_version; print(get_display_version())"

# Run comprehensive quality checks
python scripts/enforce_standards.py --check-all

# Sync issues with GitHub
python scripts/issue_sync_bidirectional.py --sync-all --live
```

### Development Workflow (ENHANCED)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify installation and run quality checks
python scripts/enforce_standards.py --check-all

# 3. Run tests before changes (90+ second timeout)
python -m unittest discover tests -v

# 4. Make your changes

# 5. Run tests after changes (90+ second timeout)
python -m unittest discover tests -v

# 6. Test specific functionality programmatically
python -c "# Your validation code here"

# 7. Optional: Sync with GitHub issues
python scripts/issue_sync_bidirectional.py --sync-all
```

### Quality Assurance Workflow (NEW)
```bash
# Comprehensive validation
python scripts/enforce_standards.py --check-all

# ASCII compliance check and fix
python scripts/ascii_compliance_fixer.py

# Version consistency check
python -c "from src.services.version import get_display_version; print(f'Current: {get_display_version()}')"

# Import validation
python -c "from src.core.game_state import GameState; print('CHECKED Imports working')"
```

## Troubleshooting (ENHANCED)

### Common Issues and Solutions
- **pygame import errors**: Ensure `pip install pygame` completed successfully
- **ALSA warnings**: Normal in headless environments, game functions correctly
- **Encoding issues**: Use UTF-8 with fallback handling (Windows compatibility)
- **Import failures**: Run `python scripts/enforce_standards.py --check-all` for validation
- **Version inconsistencies**: Check `src/services/version.py` for current version

### Automation System Troubleshooting
- **Issue sync failures**: Check GitHub CLI installation and authentication
- **CI/CD pipeline issues**: Review `.github/workflows/` files for configuration
- **Pre-commit hook failures**: Run quality checks manually to identify issues
- **Quality gate failures**: Use `scripts/enforce_standards.py` for detailed analysis

### Error Recovery (ENHANCED)
- **Dependency issues**: Re-run `pip install -r requirements.txt`
- **Test environment**: Use programmatic validation instead of GUI interaction
- **Version check**: Use `python -c "from src.services.version import get_display_version; print(get_display_version())"`
- **Quality validation**: Run comprehensive checks with `scripts/enforce_standards.py --check-all`

## CHANGES SUMMARY: v0.8.0 → v0.10.1

### **NEW: Complete Automation Infrastructure**
- Bidirectional GitHub issue synchronization (42+ issues)
- Enhanced CI/CD pipeline with quality gates
- Pre-commit hook system with automated validation
- Comprehensive quality assurance tools

### **NEW: Programmatic Control System**
- GUI-free game testing and validation
- Automated multi-turn game scenarios
- Cross-platform compatibility (Windows encoding fixes)
- Performance profiling and regression detection

### **ENHANCED: Infrastructure Maturity**
- Centralized version management (v0.10.1)
- Robust error handling and encoding fixes
- Enhanced documentation organization
- Comprehensive testing infrastructure (500+ tests)

Remember: This is a GUI application with comprehensive automation - always use programmatic validation rather than attempting to interact with the pygame window in automated environments. The automation infrastructure enables sophisticated development workflows with quality assurance built-in.
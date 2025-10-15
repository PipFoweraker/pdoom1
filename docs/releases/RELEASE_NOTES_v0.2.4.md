# Release Notes - P(Doom) v0.2.4 'Economic Cycles & Enhanced Onboarding'

**Release Date**: September 6, 2025  
**Version**: 0.2.4  
**Branch**: drop-python-38-support  

## [PARTY] Major New Features

### [EMOJI] Economic Cycles & Funding Volatility System (Issue #192)

We're excited to introduce a comprehensive economic cycles system that adds significant strategic depth to P(Doom). This feature models realistic AI funding patterns based on historical market data from 2017-2025.

**Key Features:**
- **Historical Timeline**: Experience realistic AI funding cycles based on actual market events
- **5 Economic Phases**: Boom, Stable, Correction, Recession, and Recovery periods
- **5 Funding Sources**: Each with different sensitivities to economic conditions
  - Seed funding (friends, family, angels) - least cycle sensitive
  - Venture capital - highly cycle sensitive
  - Corporate investments - moderately sensitive
  - Government funding - counter-cyclical
  - Revenue generation - growth dependent
- **Enhanced Fundraising**: 4 new advanced funding actions including Series A, government grants, and corporate partnerships
- **Economic Events**: 7 new economic-specific events that trigger based on market conditions

**Strategic Impact:**
Players must now consider economic timing when planning fundraising activities. A funding strategy that works during a boom period may fail during a recession, adding a new layer of strategic planning to the game.

### [EMOJI] New Player Experience Enhancement

We've completely redesigned the initial game flow to provide a better onboarding experience for new players.

**Improvements:**
- **Enhanced Menu**: Replaced 'Launch Lab' with 'New Player Experience' in the main menu
- **Checkbox Interface**: Choose between tutorial guidance and intro scenario
- **Contextual Introduction**: Optional intro text that explains the game premise and starting conditions
- **Responsive Design**: UI adapts to different screen sizes and input methods

**Better Onboarding:**
New players can now choose their preferred experience level - jump straight into the action or get guided through the complex systems that make P(Doom) engaging.

## [EMOJI] Technical Improvements

### [EMOJI] ASCII Compatibility Enhancement

Resolved encoding issues that affected some Windows systems and international users.

**Changes:**
- Converted all Unicode symbols (arrows, emojis, special characters) to ASCII equivalents
- Fixed 'charmap' codec errors on systems with non-UTF-8 default encoding
- Maintained visual consistency while ensuring maximum compatibility
- Improved terminal output across different environments

### [CHART] Enhanced Test Coverage

Added comprehensive unit testing for new features.

**New Tests:**
- 7 unit tests for economic cycles system covering initialization, phase progression, and integration
- 10 unit tests for new player experience covering UI rendering and state management
- All tests passing with full integration validation

### [EMOJI][EMOJI] Improved Architecture

The economic cycles system demonstrates our commitment to modular, extensible design.

**Design Principles:**
- Clean separation between game logic, UI, and economic mechanics
- Deterministic RNG integration for reproducible gameplay
- Backward compatibility maintained for existing save files
- Extensible foundation for future economic features

## [EMOJI] File Changes Summary

### New Files
- `src/features/economic_cycles.py` (379 lines) - Complete economic system implementation
- `tests/test_economic_cycles.py` - Economic cycles unit tests  
- `tests/test_new_player_experience.py` - New player experience unit tests
- `docs/ECONOMIC_CYCLES_IMPLEMENTATION.md` - Detailed implementation guide

### Modified Files
- `main.py` - New player experience state management and event handling
- `ui.py` - New player experience UI and ASCII compatibility fixes
- `src/core/game_state.py` - Economic cycles integration
- `src/core/actions.py` - Enhanced fundraising with advanced actions
- `src/core/events.py` - Economic-specific events
- Various documentation files updated

## [EMOJI] Compatibility & Migration

**Backward Compatibility**: Existing save files continue to work seamlessly. The economic cycles system automatically initializes with appropriate phase data for the current turn.

**System Requirements**: 
- Python 3.9+ (unchanged from v0.2.3)
- pygame 2.0+ (unchanged)
- No additional dependencies required

**Performance Impact**: Minimal computational overhead (< 1ms per turn) with approximately 50KB additional memory usage for economic state tracking.

## [ROCKET] Future Enhancements

The economic cycles system is designed with extensibility in mind. Future versions may include:
- Regional market variations
- Debt and loan mechanics
- Player influence on economic cycles
- Crisis opportunity mechanics
- Advanced funding strategies

## [EMOJI] Bug Fixes

- Fixed encoding issues causing crashes on some Windows systems
- Resolved Unicode display problems in terminal output
- Improved cross-platform compatibility for international users

## [PRAY] Contributors

This release represents significant work on game systems and user experience. Special thanks to all contributors and testers who helped validate these new features.

---

**Full Changelog**: See [CHANGELOG.md](../CHANGELOG.md) for complete version history  
**Installation Guide**: See [README.md](../README.md) for setup instructions  
**Developer Documentation**: See [docs/DEVELOPERGUIDE.md](DEVELOPERGUIDE.md) for technical details  

**Questions or Issues?** Please open an issue on our GitHub repository.

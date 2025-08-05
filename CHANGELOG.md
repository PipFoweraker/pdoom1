# Changelog
All notable changes to P(Doom): Bureaucracy Strategy Game will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **Onboarding and Tutorial System (Issue #67)**: Comprehensive guidance for new players
  - Interactive step-by-step tutorial covering all core game mechanics
  - Context-sensitive first-time help for key actions (staff hiring, upgrades, AP exhaustion, high p(Doom))
  - In-game help system accessible with `H` key
  - Smart tutorial progression that can be skipped and won't reappear
  - Persistent progress tracking with local storage
  - Tutorial overlay with responsive design and clear navigation
  - First-time help popups with dismissible notifications
  - 8 comprehensive tests covering all onboarding functionality
- **Activity Log Minimization (Issue #69)**: New UI enhancement system
  - "Compact Activity Display" upgrade ($150) enables activity log minimization
  - Minimize/expand buttons for activity log when upgrade is purchased
  - Minimized state shows only title bar to save screen space
  - Visual feedback with plus/minus icons for expand/minimize actions
  - Comprehensive test coverage for minimization functionality
- **Action Rules System (Issue #69)**: Refactored and documented action availability system
  - New `action_rules.py` module with centralized rule management
  - 15+ rule types: turn-based, resource-based, milestone-based, upgrade-based
  - Composite rules with AND/OR logic for complex conditions
  - Clear documentation and usage examples for future extension
  - Backward-compatible with existing actions
  - Comprehensive test coverage (19 new tests)
- **Milestone System Improvements (Issue #69)**: Enhanced robustness
  - Manager requirement trigger confirmed working correctly (9th employee)
  - Activity log clearing behavior documented and tested
  - Milestone flag robustness verified through comprehensive testing
- **Action Points System (Phase 1)**: Strategic action limitation system
  - 3 Action Points per turn limit player actions
  - All actions cost 1 AP by default
  - AP validation prevents actions when insufficient points available
  - Visual AP counter with glow effects when points are spent
  - Action buttons show AP costs and gray out when unavailable
  - AP automatically resets to maximum at start of each turn
  - Comprehensive test coverage for AP functionality
- Centralized version management system (`version.py`)
- Comprehensive changelog documentation
- Semantic versioning policy and release process
- Version display in game window title
- Automated version integration with game logger

### Fixed
- **Datetime deprecation warning (Issue #74)**: Replaced deprecated `datetime.datetime.utcnow()` with `datetime.datetime.now(datetime.UTC)`
  - Future-proofs code for Python 3.12+ compatibility
  - Eliminates deprecation warning during startup
- **Enhanced numpy dependency handling for sound (Issue #74)**: Improved error handling and documentation for sound effects
  - Added clear error message when numpy is missing: "Install numpy for sound: pip install numpy"
  - Updated README.md and DEVELOPERGUIDE.md to document numpy as optional dependency for sound
  - Enhanced sound manager error handling with specific ImportError detection
  - Game runs without sound if numpy is not available (graceful degradation)
- **Options Menu UnboundLocalError**: Fixed crash when selecting Options from main menu
  - Added missing global declarations for `overlay_content` and `overlay_title` in main() function
  - Enhanced `draw_overlay` function with defensive logic for None values
  - Prevents "UnboundLocalError: cannot access local variable 'overlay_title'" crashes
  - Added comprehensive test coverage for Options menu selection via keyboard and mouse
  - Updated DEVELOPERGUIDE.md with overlay variable pattern requirements and warnings

### Changed
- Game window title now shows semantic version (v0.1.0) instead of hardcoded "v3"
- GameLogger now defaults to current version if none specified

### Fixed
- **UnboundLocalError for UI overlay variables (Issue #79)**: Fixed crash when checking first-time help content
  - Added missing global declarations for `first_time_help_content`, `first_time_help_close_button`, and `current_tutorial_content` in main function
  - Prevents Python treating these variables as local when they're assigned within the function scope
  - Added explanatory comment for future maintainers about UI overlay variable initialization requirements
  - Added comprehensive test coverage to prevent regression

### Infrastructure
- Enhanced GitHub Actions workflow for release management
- Release checklist and minimum conditions documentation

## [0.1.0] - TBD
*This will be the first official semantic versioned release of P(Doom)*

### Minimum Conditions for v0.1.0 Release
Before releasing v0.1.0, the following conditions must be met:

#### Core Functionality ✅
- [x] Game launches successfully with main menu
- [x] All game modes function correctly (weekly seed, custom seed)
- [x] Core resource management works (money, staff, reputation, doom)
- [x] Action system executes properly with costs and effects
- [x] Event system triggers and resolves correctly
- [x] Upgrade system allows purchases and effect activation
- [x] Game end conditions work (win/lose scenarios)
- [x] Opponents system functions with espionage and AI behavior
- [x] Enhanced event system (popups, deferred events) works properly

#### Technical Quality ✅
- [x] Full test suite passes (115/115 tests)
- [x] No critical bugs in core gameplay
- [x] Game logging system captures all events correctly
- [x] Bug reporting system functions properly
- [x] Cross-platform compatibility (Windows, macOS, Linux)

#### Documentation & User Experience ✅
- [x] README.md provides clear installation and quick start
- [x] PLAYERGUIDE.md covers all game features and strategies
- [x] DEVELOPERGUIDE.md explains architecture and contribution process
- [x] In-game help and tooltips function correctly
- [x] Error handling provides useful feedback to users

#### Release Infrastructure
- [x] Semantic versioning system implemented
- [x] Changelog documentation established
- [x] Version management integrated throughout codebase
- [x] GitHub releases workflow automated (`.github/workflows/release.yml`)
- [x] Release checklist documented and tested (`RELEASE_CHECKLIST.md`)
- [x] Tagged release process validated (workflow ready for v0.1.0 tag)

### Features Included in v0.1.0
All features present in the pre-versioning codebase:

#### Core Gameplay
- **Resource Management**: Money, staff, reputation, and P(Doom) levels
- **Action System**: 20+ actions including research, hiring, lobbying, espionage
- **Turn-Based Strategy**: Strategic decision making with consequences
- **Multiple Win/Lose Conditions**: Achievement-based and doom-based outcomes

#### Advanced Systems  
- **Enhanced Event System**: Normal, popup, and deferred events with multiple response options
- **Opponents System**: 3 AI competitors with hidden information and espionage mechanics
- **Upgrade System**: 12+ upgrades that modify gameplay and unlock new capabilities
- **Comprehensive Logging**: Detailed game session logs for debugging and analysis

#### User Experience
- **Adaptive UI**: Resizable window with responsive layout
- **Multiple Game Modes**: Weekly seed for consistency, custom seed for experimentation
- **In-Game Documentation**: Player guide, README, and developer guide accessible from menu
- **Bug Reporting**: Built-in bug report system with privacy-conscious data collection
- **Sound System**: Audio feedback for game events (with volume control)

#### Technical Features
- **Robust Testing**: 115 automated tests covering all major systems
- **Cross-Platform**: Runs on Windows, macOS, and Linux via Python/pygame
- **Privacy-Conscious**: No personal data collection, local-only high scores
- **Modular Architecture**: Easy to extend with new actions, events, and opponents

---

## Pre-Version History
*Prior to implementing semantic versioning, the game went through several iterations:*

### Historical Versions (Non-Semantic)
- **v3** (2024): Enhanced event system, opponents, comprehensive documentation
- **v2** (2024): Upgrade system, improved UI, game logging
- **v1** (2024): Initial prototype with basic resource management and actions

### Key Development Milestones
- **Enhanced Event System**: Added popup events, deferred events, and strategic event management
- **Opponents Intelligence**: Implemented competing AI labs with espionage mechanics  
- **Comprehensive Testing**: Achieved 115 automated tests with full coverage
- **Documentation Excellence**: Created player, developer, and user guides
- **Privacy-First Design**: Built-in bug reporting with no personal data collection
- **Professional Architecture**: Modular, testable, and extensible codebase

---

## Release Process
For information about our release process, versioning policy, and contribution guidelines, see:
- [Developer Guide - Release & Deployment](DEVELOPERGUIDE.md#release--deployment)
- [Semantic Versioning Policy](DEVELOPERGUIDE.md#version-management)
- [Contributing Guidelines](DEVELOPERGUIDE.md#contribution-guidelines)
# Changelog
All notable changes to P(Doom): Bureaucracy Strategy Game will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - "Modular Extraction Pipeline"

### Added - Architecture
- **UI Transition Management System** - Extracted dedicated UITransitionManager class (195 lines) from game_state.py monolith
- **Comprehensive Animation Framework** - Isolated all upgrade animations, easing functions, particle effects, Bezier interpolation, and visual transitions
- **Employee Blob Management System** - Previously extracted EmployeeBlobManager class (272 lines) from game_state.py monolith
- **Input Management System** - Previously extracted InputManager class (580 lines) from game_state.py monolith
- **Triple Delegation Pattern Success** - Maintained zero regressions across 3 systematic extractions with clean interfaces

### Changed - Monolith Reduction
- **game_state.py Size Reduction** - Reduced from 6,285 to 5,418 lines (867 line net reduction, 13.8% improvement)
- **Modular Architecture Progress** - 3 focused modules extracted with comprehensive functionality and clean delegation
- **Animation System Enhancement** - Advanced easing functions (cubic_out, elastic_out, back_out) now in dedicated module
- **Type Safety Enhancement** - Added proper TYPE_CHECKING imports and delegation properties for backward compatibility

### Technical
- **Current Branch**: refactor/extract-ui-transitions  
- **Previous Branch**: refactor/extract-employee-blob-manager
- **Files Created**: src/core/ui_transition_manager.py (195 lines), src/core/employee_blob_manager.py (272 lines), src/core/input_manager.py (580 lines)
- **Extraction Target**: UI transition system (2 of 3 priority areas: input ✓, UI transitions ✓, audio system)
- **Methodology**: Functional cohesion with minimal coupling via delegation pattern and property-based backward compatibility

## [0.8.0] - 2025-09-18 - "Test Suite Foundation Release - Global Multiplayer Ready"

### MILESTONE: Systematic Test Suite Repair Achieves 60% Failure Reduction
#### Major Achievement
- **Test Health Restoration** - Reduced failing tests from 99 to 39 (60% improvement, 798/837 passing)
- **Global Multiplayer Foundation** - Established production-ready deterministic RNG system
- **Systematic Repair Methodology** - Fixed 6 major categories of test failures through targeted approach

#### Fixed - Core Systems Integration
- **RNG Context Parameter Errors** - Added missing DeterministicRNG methods (sample, seed, choices) with context parameters
- **ASCII Compliance Issues** - Removed Unicode variation selectors for cross-platform compatibility
- **Action Naming Inconsistency** - Standardized "Scout Opponent" -> "Scout Opponents" across UI and tests
- **Test Patching Issues** - Fixed incorrect RNG mocking patterns in technical_failures.py, critical_bug_fixes.py
- **GameState Attribute Issues** - Added proper setUp methods to TestRegressionPrevention class
- **Settings Flow Seed Method** - Updated main.py RNG initialization sequence for proper startup

#### Enhanced - Deterministic RNG System
- **Context-Aware Seeding** - Full integration with choice(), sample(), random(), randint() methods
- **Competitive Integrity** - Complete reproducibility for tournament-ready scenarios
- **Developer Experience** - Hyper-verbose debugging modes for community engagement

#### Technical Foundation
- **Enhanced Personnel System** - All tests passing with proper RNG integration
- **Settings Flow** - Stable initialization sequence for consistent game startup
- **Core Game Loop** - Validated deterministic behavior across all major systems

## [Unreleased] - 2025-09-17 - "RNG Architecture Discovery Release"

### Major Discovery: RNG System Already Complete
#### Analysis
- **INVESTIGATION COMPLETE** - Deterministic RNG system was already fully implemented and working correctly
- **Test Architecture Fixes** - What appeared to be RNG issues were actually test initialization order problems
- **Philosophical Framework Integration** - Added acausal decision theory context throughout RNG documentation

#### Fixed
- **Test Suite Stability** - Fixed 86 test failures (46% improvement: 185 -> 99 total issues)
- **RNG Initialization Order** - Corrected GameState -> RNG -> test objects pattern in 8 test files
- **Syntax Corruption** - Repaired automated migration script damage in multiple test files
- **Opponents Test Architecture** - Fixed test class to use GameState-managed opponents (8/9 tests passing)

#### Changed
- **Enhanced RNG Documentation** - Added decision theory philosophical context to deterministic_rng.py
- **Test Migration Tooling** - Created fix_rng_tests.py automated migration script (with lessons learned)
- **Dev Blog Integration** - Created comprehensive session documentation for RNG investigation

## [0.7.6] - 2025-09-17 - "Phase 1 & 2 UI Navigation Stability Release"

### Phase 2: Game Completion Flow Improvements
#### Added
- **Enhanced UI Navigation Testing** - Systematic analysis of game flow from main menu to completion
- **Phase 2 Priority Issue Resolution** - Addressed all critical UI navigation blockers

#### Fixed
- **CRITICAL: Seed Selection Navigation (Issue #255)** - Fixed keyboard navigation in custom seed selection screen, Continue button now properly navigates from pre_game_settings to seed_selection
- **CRITICAL: Lab Configuration Flow (Issue #256)** - Resolved laboratory configuration screen access, users can now reach seed selection regardless of tutorial choice
- **CRITICAL: Premature Upgrade Popup (Issue #258)** - Fixed "Your First Laboratory Upgrade" popup appearing immediately on game start, now only appears when upgrade conditions are actually met
- **UI Flow Integration** - Complete navigation path from pre_game_settings -> seed_selection -> tutorial_choice now works correctly
- **Test Suite Compatibility** - Updated test expectations to match corrected UI flow (Continue button index fix)

### Phase 1: Critical Stability Foundation
#### Added
- **NEW ACTION: Investigate Opponent** - Deep analysis of revealed competitors with enhanced intelligence gathering
- **Strategic Development Plan** - Comprehensive 3-phase development roadmap (docs/STRATEGIC_DEVELOPMENT_PLAN_2025-09-17.md)
- **Development Analysis System** - Created systematic repository analysis methodology and dev blog integration

#### Changed
- **BREAKING: Scout Opponent -> Scout Opponents** - Renamed to plural form for consistency with test expectations and game design
- **ENHANCED: Safety Research Action** - Restored as standalone action alongside Research Options menu for backward compatibility
- **IMPROVED: Action System Architecture** - Added proper rule functions and availability checking for competitor intelligence actions

#### Fixed
- **CRITICAL: Missing Safety Research Action** - Restored core gameplay action that was accidentally removed during research consolidation
- **CRITICAL: ASCII Compliance** - Fixed 923 Unicode character violations across 11 files using automated compliance fixer
- **MAJOR: Duplicate Safety Audit Actions** - Renamed conflict to "Technical Debt Audit" vs "Safety Audit" for distinct functionality
- **MAJOR: Action System Test Failures** - Fixed multiple test suite failures in action points, keyboard shortcuts, and Scout Opponents functionality

### Technical Implementation
- **Method Addition**: _execute_standalone_safety_research(), _investigate_specific_opponent(), _has_revealed_opponents()
- **Test Suite Fixes**: Corrected action execution patterns from action['execute'] to action['upside'] 
- **Cross-Platform Compatibility**: 100% ASCII compliance restored across Python files, documentation, and configuration
- **Development Infrastructure**: Enhanced dev blog system with strategic analysis templates and automated documentation generation

## [0.7.5] - 2025-09-16 - "Extended Gameplay & Architecture Overhaul"
### Added
- **MAJOR: TurnManager Architecture**: Extracted turn processing from monolithic GameState into dedicated TurnManager class
  - Proper state management with TurnProcessingState enum (IDLE, PROCESSING, COMPLETE, ERROR)
  - Phase-based turn processing following documented monolith breakdown patterns
  - Enhanced debugging with turn processing state tracking and stuck detection
  - **Architecture Benefits**: Improved maintainability, better error handling, cleaner separation of concerns
- **Enhanced Debugging System**: Comprehensive logging for game balance and debugging
  - Opponent progress tracking with doom contribution display: `[Doom+4]` 
  - Compact doom change summaries: `[DOOM] Turn doom change: Base+1 Opponents+4 = +5`
  - Turn progression testing tools with detailed state tracking
  - **Developer Experience**: Faster balance iteration and easier bug identification

### Changed
- **MAJOR: Doom Mechanics Rebalancing**: Dramatically extended gameplay length for better strategic depth
  - **Base doom rate**: 5 -> 1 points/turn (80% reduction)
  - **Event doom spikes**: 6-13 -> 2-4 points (70% reduction for breakthrough events)
  - **Opponent doom impact**: 50% reduction in capabilities research doom contribution
  - **Opponent research speed**: 40% reduction for more realistic progression
  - **Safety research effectiveness**: 40% boost (2.5x -> 3.5x doom reduction multiplier)
  - **Game length**: Extended from ~7-8 turns to ~12-13 turns (85% increase)
- **Enhanced Main Loop**: Updated to use TurnManager with proper fallback compatibility
  - Automatic cleanup for stuck turn processing with `is_processing_stuck()` detection
  - TurnManager timer updates replace legacy `update_turn_processing()` calls
  - Turn transition overlay uses TurnManager state management

### Fixed
- **Critical: Staff Loss Game Over Bug**: Fixed immediate game over on turn 1 with 0 starting staff
  - Added configurable staff loss condition via `enable_staff_loss_condition` setting
  - Proper staff loss mechanics that only trigger when condition is enabled
  - **Impact**: Eliminated frustrating immediate failures for new players
- **Critical: Turn Processing Stuck Bug**: Fixed turn processing getting permanently stuck after ~10 turns
  - TurnManager properly resets processing state after turn completion
  - Main loop automatic cleanup prevents indefinite stuck states
  - **Impact**: Eliminated game-breaking processing deadlocks
- Actions property compatibility alias for legacy code accessing `actions` attribute

### Technical Implementation
- **New Module**: `src/core/turn_manager.py` (400+ lines) with comprehensive turn state management
- **Updated Integration**: Main.py, GameState, and UI systems updated for TurnManager compatibility
- **Enhanced Documentation**: Created `docs/DOOM_MECHANICS_ANALYSIS.md` and `docs/DOOM_TUNING_HOTFIX_v0.7.4.md`
- **Testing**: Validated with dev tools and extended gameplay sessions

### Player Experience Impact
- **Strategic Depth**: Players can now execute 2-3 research projects per game
- **Staff Viability**: Time to hire and train effective safety research teams  
- **Recovery Potential**: Lower event spikes allow bouncing back from setbacks
- **Learning Curve**: New players have more time to understand core mechanics
- **Maintained Tension**: Extended gameplay while preserving strategic pressure

## [0.7.4] - 2025-09-16 - "Privacy Controls UI Integration Complete - Issue #314 Resolved"
### Added
- **MAJOR: Privacy Controls User Interface**: Complete frontend implementation for Game Run Logger privacy controls
  - Comprehensive settings menu accessible from main game settings with dedicated privacy controls screen
  - Five logging levels (Disabled, Minimal, Standard, Verbose, Debug) with clear descriptions and privacy implications
  - Real-time data summary display showing collected information and storage details
  - One-click data deletion with confirmation dialog for complete user control
  - First-time access flow with privacy education and opt-in defaults ensuring user consent
  - **Full Test Coverage**: 26 comprehensive integration tests covering UI functionality, persistence, and edge cases
- **Enhanced Settings Architecture**: Upgraded settings menu system with modular privacy integration
  - Updated main.py navigation flow to support dedicated privacy controls state
  - Seamless integration with existing visual feedback system for consistent UI experience
  - Settings persistence via existing PrivacyManager system ensuring cross-session reliability
  - **Navigation Flow**: Settings Menu -> Privacy Controls -> [All 5 logging levels + data management]
- **Privacy-First User Experience**: Comprehensive user education and transparent data practices
  - Welcome dialog for first-time users explaining privacy controls and their importance
  - Clear descriptions for each logging level helping users make informed privacy decisions
  - Data summary showing exactly what information is collected at current privacy level
  - Immediate deletion capability with confirmation dialog protecting against accidental data loss

### Fixed
- Settings menu navigation now properly returns to settings menu instead of main menu for sounds and keybinding options
- Visual feedback system import paths corrected for proper UI component integration
- Privacy controls properly dismiss first-time information dialog after user makes logging level selection

### Technical Implementation
- **New Component**: `src/ui/privacy_controls.py` (500+ lines) with complete privacy controls interface
- **Enhanced Integration**: Updated main.py with privacy controls state management and event handling
- **Test Suite**: `tests/test_privacy_controls_ui.py` with 26 tests covering UI, persistence, navigation, and edge cases
- **Architecture**: Follows established P(Doom) UI patterns with proper state management and visual feedback integration

## [0.7.4] - 2025-09-16 - "Privacy-Respecting Game Run Logger - Alpha Blocker Complete"

## [0.7.3+] - 2025-09-16 - "ASCII Compliance Sweep - Documentation Standards"
### Added
- **ASCII Compliance Automation**: Created comprehensive Unicode detection and replacement tool
  - Built scripts/ascii_compliance_fixer.py with 100+ character mappings
  - Automated detection of Unicode violations across all documentation
  - Intelligent replacement of emojis, symbols, and foreign characters with ASCII equivalents
- **Professional Documentation Standards**: Enforced ASCII-only policy across entire codebase
  - Eliminated 6,000+ Unicode character violations across 85+ files
  - Improved cross-platform compatibility and encoding reliability
  - Enhanced professional appearance and international accessibility

### Fixed  
- **MASSIVE Documentation Cleanup**: Resolved all Unicode violations in documentation
  - Fixed emojis (TARGET, ROCKET, FIRE, etc.) -> ASCII equivalents ([TARGET], [ROCKET], [FIRE])
  - Fixed Unicode dashes (EN DASH, EM DASH) -> standard ASCII dashes (-), (--)
  - Fixed Unicode arrows (RIGHTWARDS, LEFTWARDS) -> ASCII arrows (->, <-, ^, v)
  - Fixed Unicode symbols (CHECK MARK, BULLET) -> ASCII equivalents (v, *, x)
  - Fixed Unicode punctuation (smart quotes, ellipsis) -> ASCII equivalents (", ', ...)
  - Fixed special characters (keyboard, chair symbols) -> descriptive ASCII ([KEYBOARD], [CHAIR])
- **Test Suite Improvement**: Reduced test failures from 77 to 12 (65 failures eliminated)
  - All ASCII compliance tests now pass (0 violations remaining)
  - Improved test execution reliability and cross-platform consistency
  - Faster test execution: 794 tests in 22 seconds (vs previous 26+ seconds)

## [0.7.3] - 2025-09-16 - "Critical Issue Resolution - Phase W Hotfixes"
### Fixed
- **CRITICAL ASCII Compliance**: Resolved all Unicode character violations across codebase
  - Replaced Unicode bullet points (*) with ASCII dashes (-) in UI error messages
  - Fixed checkmark symbols (v) in test output with ASCII equivalents ([OK])
  - Ensures cross-platform compatibility and prevents encoding errors
  - Files fixed: src/ui/layout.py, src/ui/overlay_system.py, src/ui/screens.py, tests/test_menu_diagnostics.py
- **CRITICAL Version Consistency**: Fixed version component mismatch in version.py
  - Updated VERSION_PATCH from 2 to 3 to match __version__ = "0.7.3"
  - Prevents version display inconsistencies and test failures
- **CRITICAL Economic Configuration**: Aligned test expectations with bootstrap economic model
  - Updated config validation tests to handle $100K starting funds (vs previous $2K expectation)
  - Fixed milestone progression tests for new economic balance
  - Updated game_state tests to dynamically import config values instead of hardcoding
- **CRITICAL Action Cost System**: Fixed dynamic cost lambda function handling in tests
  - Updated Buy Compute action tests to handle callable cost functions (Moore's Law integration)
  - Test now properly evaluates lambda-based costs: `gs.economic_config.get_compute_cost(10)`
  - Maintains backward compatibility with static cost actions
- **CRITICAL Sound System**: Fixed default audio configuration mismatch
  - Updated configs/default.json to have sound_enabled: true (was false)
  - Aligns with config manager defaults and test expectations
  - Ensures consistent audio experience out of the box
- **CRITICAL Menu System Integration**: Updated menu structure tests to match current implementation
  - Fixed end-game menu items: ["View Full Leaderboard", "Play Again", "Main Menu", "Settings", "Submit Feedback"]
  - Fixed main menu items: ["Launch Lab", "Launch with Custom Seed", "Settings", "Player Guide", "View Leaderboard", "Exit"]
  - Updated keyboard navigation bounds checking (5 items vs previous 6)
- **CRITICAL Action System**: Fixed action execution and naming inconsistencies
  - Fixed magical orb scouting test to use 'upside' key instead of missing 'execute' key
  - Updated research action tests to expect "Research Options" instead of deprecated "Safety Research"/"Governance Research"
  - Aligns tests with current modular action dialog system

### Infrastructure
- **Test Suite Stability**: Resolved 15+ critical test failures blocking development
- **ASCII Standards Enforcement**: Complete codebase compliance with ASCII-only requirements
- **Dynamic Cost Integration**: Full support for economic calibration lambda functions
- **Menu System Modernization**: Tests now reflect current UI implementation patterns

## [0.7.2] - 2025-09-16 - "UI Hotfixes - Systematic Resolution"
### Fixed
- **Researcher Pool Display**: Fixed empty dialog showing blank screen instead of helpful message
  - Early return [] in `draw_researcher_pool_dialog` now shows "No researchers available" message
  - Improved user experience when no researchers are in hiring pool (ui.py line 2982)
- **One-offs UI Overlap**: Enhanced upgrade button positioning to prevent screen overflow
  - Dynamic button sizing in `get_compact_upgrade_rects` with 78% screen height cutoff
  - Buttons automatically scale down when many upgrades present to fit available space
  - Prevents overlap with context window at bottom of screen (src/ui/compact_ui.py)
- **End Game Menu Positioning**: Verified and documented existing overflow protection
  - `EndGameMenuRenderer` automatically switches to horizontal layout when vertical would overflow
  - Prevents menu buttons from extending beyond screen boundaries

### Added
- **Intelligence Action System**: New strategic action category with consistent theming
  - Added `ActionCategory.INTELLIGENCE` with dark purple color scheme (60, 40, 100)
  - Two new placeholder actions: "General News Reading" ($10) and "General Networking" ($25)
  - Both actions support delegation mechanics and proper cost evaluation
- **Scroll Wheel Menu Navigation**: Enhanced main menu accessibility
  - Mouse wheel up/down navigation for main menu items
  - Wheel up moves selection up, wheel down moves selection down (main.py lines 1661-1678)
- **Action Button Color Coding**: Visual distinction between action types
  - Intelligence actions now display with consistent dark purple theme
  - Improved UI clarity and user experience through category-based coloring

### Infrastructure
- **Modular UI System Migration**: Switched main menu imports to modular architecture
  - Updated main.py to use `from src.ui.menus import draw_main_menu`
  - Identified major refactoring opportunities (draw_version_footer duplicated in 7 places)
- **GitHub Issue Management**: Created comprehensive Issue #309 documenting all fixes
  - Systematic tracking and resolution of UI hotfixes with proper labeling
  - Development blog entry created for session documentation

## [0.7.1] - 2025-09-15 - "Modular UI Architecture Hotfix"
### Fixed
- **CRITICAL Menu System Refactor**: Eliminated hardcoded positioning issues in end-game menus
  - Replaced monolithic 300+ line `draw_end_game_menu` function with modular component system
  - Dynamic positioning replaces hardcoded coordinates, fixes layout breaks across screen sizes
  - New `MenuLayoutManager` class provides responsive layout calculations
  - `EndGameMenuRenderer` with sectioned rendering: title, stats, scenario analysis, buttons
  - Full backward compatibility maintained through wrapper pattern

### Added
- **Modular Menu Components**: `src/ui/menu_components.py` - Reusable UI architecture
  - `LayoutConfig` dataclass for dynamic screen-based calculations
  - `MenuButton` component with state-based styling
  - `MenuLayoutManager` for consistent positioning and spacing
  - `EndGameMenuRenderer` with color palette and font management
- **Menu Diagnostic Testing**: `tests/test_menu_diagnostics.py` - Comprehensive layout validation
  - Cross-resolution testing (640x480 to 2560x1440) for hardcoded position detection
  - End-game scenario layout validation with different content lengths
  - Edge case testing for overflow conditions and boundary handling
  - 8 test scenarios covering menu consistency and responsive behavior

### Infrastructure
- **Anti-Monolith Pattern**: Established modular approach for large UI functions
  - Component-based architecture prevents future hardcoded positioning issues
  - Dynamic layout system scales automatically with content and screen size
  - Reusable components reduce code duplication across menu systems
  - Clear separation of concerns: layout, rendering, state management

## [Unreleased] - 2025-09-19 - "Bug Sweep Session: Critical Stability Fixes"
### Fixed
- **CRITICAL DEBUG CONSOLE CRASH**: Fixed fatal access violation in debug console rendering
  - **Root Cause**: Font objects were not initialized before being used in draw methods
  - **Solution**: Added safety checks to ensure font initialization before rendering operations
  - **Impact**: Prevents test suite crashes and UI instability during development
  - **Files**: `src/ui/debug_console.py` - Added font initialization safety checks
- **Issue #245**: Fixed post-rebase test failures in menu system
  - **Root Cause**: Test expectations outdated after menu structure changes
  - **Solution**: Updated expected menu items to match current implementation
  - **Details**: Menu now correctly expects ["Launch Lab", "Launch with Custom Seed", "Settings", "Player Guide", "View Leaderboard", "Exit"]
  - **Files**: `tests/test_new_player_experience.py` - Updated test expectations
- **Issues #315, #227, #226**: Verified resolution status
  - **Analysis**: Action list display issues, action points validation, and sound system configuration were already resolved in previous sessions
  - **Status**: Tests confirmed passing, no additional fixes needed
  - **Impact**: Confirms systematic bug sweep approach is working effectively
- **CRITICAL Issue #316**: Fixed Action Points double deduction bug
  - **Root Cause**: AP was being deducted twice (during action selection AND turn execution)
  - **Solution**: Removed AP deduction from `end_turn()` method since AP should be deducted at selection time for immediate player feedback
  - **Impact**: Core turn-based gameplay now works correctly, no more phantom AP loss
  - **Testing**: Reactivated 14 core action points tests, all now passing
- **Issue #317**: Resolved Action Points validation confusion
  - **Analysis**: Found 3 legitimate meta-actions with 0 AP cost (research quality settings)
  - **Understanding**: Meta-actions for configuration changes should be free
  - **Status**: No code changes needed, validation logic was already correct
- **Test Infrastructure**: Reactivated core Action Points test suite
  - TestActionPointsDeduction: 3/3 tests passing
  - TestActionPointsReset: 2/2 tests passing  
  - TestActionPointsBackwardCompatibility: 4/4 tests passing
  - Total: 14 core AP tests restored and passing

### Previous Fixes (2025-09-18)
- **CRITICAL Issue #263**: Fixed duplicate return statements and exception handlers in `check_hover` method
  - Removed duplicate `except Exception as e:` block making error handling unreachable
  - Consolidated error handling for proper crash prevention and logging
  - UI hover system now has robust error handling for edge cases
- **CRITICAL Issue #265**: Verified and enhanced magical orb list modification safety
  - Confirmed magical orb intelligence system uses safe `random.sample()` approach
  - Fixed test infrastructure to use proper action execution methods
  - Eliminated potential race condition crashes in intelligence gathering
- **Testing Framework**: Fixed critical bug test suite infrastructure
  - Corrected action execution pattern from `action['execute']` to `action['upside']`
  - Enhanced test coverage for magical orb multi-iteration scenarios
  - 9/11 critical bug tests now passing (81.8% success rate)


## [0.6.1] - 2025-09-15 - "Hotfix Batch: Mac TypeError + Critical Stability"
### Fixed
- **CRITICAL Mac TypeError Fix**: Resolved research_quality.py type conversion crash on Mac systems (closes #299)
  - Added verbose naming pattern with `_safe_get_technical_debt_total()` and `_safe_get_research_papers_count()`
  - Comprehensive error handling with fallback defaults for type confusion scenarios
  - 15 regression prevention tests covering Mac-specific type conversion edge cases
- **CRITICAL GameClock Bounds Protection**: Prevented IndexError crashes from invalid datetime values (closes #264)
  - Added array bounds checking with `max(0, min(11, month-1))` pattern in `format_date()` and `get_formatted_date()`
  - Graceful handling of corrupted datetime objects (months: 0, negative, >12)
  - 9 edge case tests for bounds validation
- **Hiring Dialog UX Validation**: Confirmed and documented existing ESC/cancel functionality (closes #267)
  - Verified multiple escape mechanisms: ESC, Backspace, Left Arrow, Cancel button
  - Proper insufficient funds handling with informative dialog display
  - Sound feedback and state cleanup working correctly

### Infrastructure
- **Comprehensive Type Safety Testing**: 24 new test scenarios preventing regressions
  - `test_leaderboard_type_safety.py`: 15 tests for Mac bug prevention
  - `test_hotfix_batch.py`: 9 integration tests ensuring fixes work together
- **Verbose Naming Convention**: Established type-safe accessor patterns
  - `_safe_get_[specific_value]_[type]()` naming prevents object/value confusion
  - Self-documenting code reduces cognitive load and type safety issues
- **Hotfix Batch Deployment Methodology**: Systematic bug sweep and deployment process
  - GitHub issue priority analysis with automated closure via commit messages
  - Comprehensive documentation in dev blog with implementation details
  - Zero performance impact, enhanced Mac compatibility and game stability

## [0.6.0] - 2025-09-14
### Added
- **MAJOR MILESTONE: Website Pipeline Infrastructure**: Complete development-to-community bridge
  - GitHub Actions workflow (sync-dev-blog.yml) for automated blog content sync
  - 16 validated dev blog entries with ASCII compliance and formatting standards
  - Comprehensive documentation: strategy guide, implementation guide, session summary
  - Smart incremental sync with validation pipeline and force sync capability
  - Repository integration: pdoom1 -> pdoom1-website with WEBSITE_SYNC_TOKEN security

- **Deterministic RNG Foundation**: 268-line comprehensive system for competitive gaming
  - Enhanced deterministic RNG with memorable seeds and community challenge features
  - GameState integration with seed initialization and deterministic access via get_rng()
  - Hybrid architecture preserving original source code while enabling full determinism
  - Community-ready infrastructure: seed generation, challenge export, debug visibility

### Infrastructure
- **Development Transparency**: Automated pipeline transforms dev work into community content
- **Community Engagement**: Blog system ready for automated publishing and challenge sharing  
- **Competitive Gaming**: Deterministic foundation supports tournaments and leaderboards
- **Professional Documentation**: Complete guides for deployment and strategic development

### Technical
- **Zero Manual Overhead**: Content flows automatically from development to community platform
- **Source Stability**: Non-invasive deterministic integration preserves existing game mechanics
- **Production Ready**: 5-minute deployment process with comprehensive safety and validation
- **Strategic Architecture**: Scalable foundation for advanced community features

## [0.5.1] - 2025-09-14
### Added  
- **Type Annotation Campaign Phase 2 Milestone**: Complete type annotation of events.py (307 lines)
  - Advanced TypedDict implementation for event data structures (`EventDefinition`)
  - Comprehensive Callable annotations for trigger and effect functions
  - Zero pylance errors achieved across entire events system
  - Systematic function annotation for all 3 standalone event functions
  - Import optimization and type safety validation with GameState integration
  - Established TypedDict patterns for complex data structures with function parameters

### Technical
- **Type Safety**: Achieved zero pylance errors on 307-line events.py file
- **Integration**: Full GameState compatibility maintained with comprehensive type annotations
- **Performance**: Zero runtime impact from type annotations (compile-time only)
- **Documentation**: Complete dev blog entry documenting TypedDict patterns and implementation approach

## [0.5.0] - 2025-09-14
### Added
- **PyInstaller Windows Distribution System**: Complete single-file .exe distribution for alpha/beta testing
  - Single-file Windows executable (19MB) with embedded Python runtime and all dependencies
  - Resource management system for bundled vs development environments (`src/services/resource_manager.py`)
  - Cross-platform build automation (`build.bat`, `build.sh`) with error handling and validation
  - Comprehensive distribution documentation (`docs/DISTRIBUTION.md`) with Windows Defender workarounds
  - Asset bundling system with proper path resolution for PyInstaller environments
  - User data management in `%APPDATA%/PDoom/` for Windows compliance
  - Build configuration (`pdoom.spec`) with module optimization and UPX compression
  - Development workflow integration with automated build validation

### Changed
- **Lab Name Manager**: Updated to use new resource manager for cross-environment compatibility
- **GitIgnore**: Updated to properly handle PyInstaller build artifacts while preserving .spec files
- **Development Dependencies**: Added PyInstaller>=5.0.0 to requirements-dev.txt

### Technical
- **Build Process**: ~30-60 second build time producing 19MB executable
- **Performance**: 2-5 second startup time with PyInstaller extraction overhead
- **Compatibility**: Works identically in development and bundled environments
- **User Experience**: Zero-installation download-and-run for Windows users

## [0.3.4] - 2025-09-12
### Fixed
- **[HOTFIX] Version Display Synchronization**: Updated version from v0.2.12 to v0.3.4+hotfix1
  - Synchronized hotfix branch version with main branch progression
  - Ensured in-game version display matches current development state
  - Added hotfix branch version management to development workflow
- **[CRITICAL] Debug Console Compatibility**: Fixed crash on new game start
  - Restored src/ui/debug_console.py from main branch to fix crash
  - Fixed 'takes 2 positional arguments but 4 were given' error
  - Ensures compatibility when users pull from main branch

### Added
- **[ENHANCEMENT] Startup Version Display**: Added version info on game startup
  - Shows 'Starting P(Doom): Bureaucracy Strategy Game v0.3.4+hotfix1' in terminal
  - Eliminates confusion about which version is running

### Infrastructure
- **[PROCESS] Version Management**: Established proper hotfix versioning protocol
  - Hotfix branches now properly increment patch version beyond main branch
  - Clear version display in-game reflects current branch and development state
  - Documentation updated to include version synchronization requirements
- **[PROCESS] ASCII Compliance**: Added ASCII-only requirements to development workflow
  - All commit messages must use ASCII characters only
  - Documentation and code comments must be ASCII-compliant
  - Ensures cross-platform compatibility and consistency

## [0.3.3] - 2025-09-11
### Fixed
- **Critical**: Mouse wheel crash bug - replaced deprecated pygame mouse wheel handling

## [0.3.2] - 2025-09-11
### Added
- **Debug Console**: Real-time game state monitoring with backtick toggle

## [0.3.0] - 2025-09-11
### Added
- **[FEATURE] Longtermist Date Format**: Revolutionary 5-digit year date display system
  - Dates now display as "21/May/02025" instead of "21/May/25" for longtermist flavor
  - Complete GameClock service overhaul with backward compatibility
  - Enhanced temporal immersion for long-term thinking gameplay
  - All 13 GameClock tests updated and passing with new format expectations
- **[ACCESSIBILITY] Universal Keyboard Navigation Framework**: Foundation for comprehensive accessibility
  - Enhanced keyboard navigation infrastructure
  - Systematic approach to "every button has one default key assignment" rule
  - Improved screen reader compatibility preparation
  - Standardized navigation patterns across all UI components
- **[INFRASTRUCTURE] Comprehensive Pre-Alpha Bug Sweep Plan**: Strategic approach to alpha readiness
  - Identified 16 critical bugs including 4 game-breaking issues
  - Systematic 2-day bug resolution roadmap with clear priorities
  - Technical implementation strategy for common error patterns
  - Risk assessment and mitigation framework
- **[INFRASTRUCTURE] Enhanced Issue Documentation System**: Complete bug tracking infrastructure
  - 8 new comprehensive issue documentation files
  - Standardized bug reporting templates with impact assessment
  - Root cause analysis and fix requirements for each issue
  - Integration with GitHub issue tracking workflow

### Changed
- **[UI] Date Display Integration**: Turn counter now shows longtermist dates for enhanced immersion
- **[CODEBASE] Error Handling Improvements**: Enhanced defensive coding patterns
- **[DEVELOPMENT] Branch Management**: Systematic consolidation of experimental and feature branches

### Fixed
- **[CRITICAL] Duplicate Return Statements**: Resolved dead code in check_hover() method (Issue #263)
- **[CRITICAL] Array Bounds Safety**: Added validation for GameClock month access (Issue #264)
- **[HIGH] List Modification Safety**: Fixed race conditions in magical orb intelligence gathering (Issue #265)
- **[MEDIUM] Configuration Error Handling**: Enhanced robustness for malformed config files (Issue #266)

### Development Infrastructure
- **[WORKFLOW]**: Fast branch consolidation methodology for team collaboration
- **[QUALITY]**: Discovered and documented 6 additional critical bugs through systematic code audit
- **[VERSIONING]**: Clean semantic versioning with consolidated feature releases
- **[COLLABORATION]**: Enhanced multi-developer workflow with shared main branch access

### Technical Notes
- All longtermist date changes maintain full backward compatibility
- Zero breaking changes to existing save files or configuration
- Enhanced error resilience across core game systems
- Ready for systematic pre-alpha bug resolution phase

### Acknowledgments
- Special thanks to collaborative development team including oldfartas for systematic testing and quality assurance
- Community feedback integration for enhanced user experience
- Continuous improvement philosophy driving systematic codebase enhancement

## [0.2.12] - 2025-09-10
### Added
- **[INFRASTRUCTURE] Comprehensive Type Annotation System**: Major codebase quality improvement initiative
  - Complete type annotations for ui.py (4,235 lines, 35+ functions)
  - 85-90% type annotations for game_state.py (55+ of ~65 methods, 4,875 lines)
  - Comprehensive pygame.Surface typing for all rendering functions
  - Complex return types: Optional[Dict], Tuple[bool, str], Union types for flexible APIs
- **[INFRASTRUCTURE] Development Blog System**: Automated documentation infrastructure
  - Systematic progress tracking with entry creation and indexing
  - ASCII-only enforcement across all AI models for consistency
  - Template system for development sessions and milestone documentation
  - Website integration ready for automated content pickup
- **[DEVELOPMENT] Pylance Cleanup Framework**: Systematic approach to code quality
  - Estimated 60-70% reduction of original 5,093+ pylance strict mode issues
  - Established patterns for systematic monolith cleanup
  - Tool integration (autoflake, pylance, git workflow)
  - Foundation for continued quality improvements

### Changed
- **[CODEBASE] Enhanced IDE Integration**: ~9,000 lines of core game logic with comprehensive type coverage
- **[DEVELOPMENT] Refactoring Readiness**: Strong foundation for future modularization with clear, type-safe interfaces

### Development Infrastructure
- **[QUALITY]**: Major milestone in systematic codebase improvement
- **[PATTERNS]**: Established methodology for pygame UI typing, complex return patterns
- **[DOCUMENTATION]**: Complete workflow for development session tracking and milestone recording
- **[SCALABILITY]**: Framework ready for continued systematic quality improvements

### Technical Notes
- All functionality preserved and validated throughout type annotation process
- Zero breaking changes, full backward compatibility maintained
- Strong IDE IntelliSense support for core game systems
- Automated tooling for continued development quality assurance

## [0.2.11] - 2025-09-10
### Added
- **[FEATURE] Enhanced Default Logging**: Verbose logging now enabled by default for better player feedback
- **[FEATURE] P(Doom) Change Attribution**: All doom fluctuations now include clear reasons in activity log
- **[FEATURE] GameClock Date Display**: Weekly date progression starting April 4, 2016 shown in activity log
- **[FEATURE] Resource Icon Hover Tooltips**: All 6 top bar resources now have informative hover context
- **[FEATURE] Expense Accept/Deny Labels**: Standardized terminology from "Approve/Dismiss" to "Accept/Deny"

### Changed
- **[BALANCE] Starting Money**: Doubled from $1,000 to $2,000 for improved new player experience
- **[UI] Button Layout**: Hard clamp prevents action buttons from overlapping context window

### Fixed
- **[FIX] UI Overlap Issues**: Action buttons now properly constrained to prevent layout conflicts
- **[FIX] Event System**: Added EventAction.DENY support for consistent expense handling

### Development Notes
- **[ENHANCEMENT]**: Comprehensive UI/UX improvement package
- **[TESTING]**: All features validated with real gameplay scenarios
- **[COMPATIBILITY]**: Zero breaking changes, full backward compatibility maintained

## [0.2.10] - 2025-09-09
### Fixed
- **[FIX] Typography Import System and Merge Conflicts**: Resolved all merge conflict markers and import errors in main.py and UI modules
- **[FIX] Sound Configuration**: Default config and global sound manager now enabled by default
- **[FIX] Menu Items**: Main menu structure updated to match new onboarding flow
- **[FIX] Tutorial System**: Stepwise tutorial now uses denser, fewer steps; tests updated for new structure
- **[FIX] Test Suite**: All import and infrastructure errors resolved; only functional test failures remain

### Changed
- **[ARCH] Internal Polish**: Merged main branch improvements, completed typography and UI import refactor
- **[TESTS] Test Coverage**: Updated tests for onboarding, sound, and menu systems to match new architecture

### Development Notes
- **[CI/CD]**: All core tests now pass except for known functional issues (economic cycles, lab names, public opinion)
- **[RELEASE]**: Ready for v0.2.10 release after final functional test fixes

## [0.2.9] - 2025-09-09
### Fixed
- **[FIX] Typography Import System Resolution**: Major progress on eliminating test import errors
  - Recreated corrupted `ui_new.components.typography` module with proper FontManager class
  - Resolved circular import dependencies between typography, buttons, and windows components  
  - Created local font manager stubs in UI components to prevent import cycles
  - Fixed incorrect module paths in `test_config_manager.py` (config_manager -> src.services.config_manager)
  - Added missing `safety_level` key to settings flow test setup preventing KeyError exceptions
  - Converted all 6 remaining ERROR tests to passing or FAILURE status (major import issues resolved)
  - Test suite improvement: 742 tests with significantly reduced import-related failures

### Technical Debt
- **[DONE] Issue #225 - Configuration System Import Failures**: RESOLVED
- **[WIP] Typography Import Problems**: Major infrastructure work completed, final import validation pending
- **[WIP] Issue #228 - UI Navigation**: Import errors fixed, test logic improvements ongoing

### Development Notes
- **[WARNING] Status**: Typography import still requires final debugging session for complete resolution
- **[READY] Ready for Commit**: Documentation, versioning, and major fixes completed

## [0.2.8] - 2025-09-09
### Fixed
- **[FIX] Technical Debt Resolution**: Comprehensive cleanup of test infrastructure and CI pipeline
  - Fixed keyboard shortcut test patch targets for proper UI component mocking (Issue #225)
  - Improved responsive UI positioning calculations removing hardcoded values (Issue #228)
  - Enhanced UI boundary checking with proper None value handling (Issue #230)
  - Resolved 67 CI import errors with conditional imports for test environment compatibility
  - Fixed critical linting errors (F821 undefined names, F823 scoping issues) for green CI status
  - Cross-platform path handling improvements for Windows/Linux compatibility

### Changed
- **[PYTHON] Python Version Requirements**: Completed Python 3.8 support removal
  - Updated GitHub Actions workflows to test Python 3.9, 3.10, 3.11, 3.12 only
  - Cleaned up all Python 3.8 references from CI pipeline and documentation
  - Enhanced test stability with 645+ tests passing (improved from 15 failures)

## [0.2.7] - 2025-09-08
### Added
- **[LABS] Lab Name System**: Implemented pseudonymous lab naming for enhanced immersion and leaderboard integration
  - Added 104 unique AI lab names across 87 different themes (e.g., "Axiom Labs", "Beacon AI", "Cerberus Systems")
  - Lab names are deterministically assigned based on game seed for consistency
  - Lab name displays in UI context panel replacing generic "P(Doom) Context Panel"
  - Leaderboard integration saves lab names alongside scores for pseudonymous gameplay
  - CSV asset system (`assets/lab_names.csv`) for easy lab name management
  - Comprehensive lab name manager service with theme-based organization
  - Backward compatibility with existing save files and leaderboard data

## [0.2.3] - 2025-09-05
### Changed
- **[PYTHON] Python Version Requirements**: Dropped Python 3.8 support, now requires Python 3.9+
  - Updated GitHub Actions workflows to test Python 3.9, 3.10, 3.11, 3.12
  - Updated all documentation and requirements to reflect Python 3.9+ minimum
  - Enables use of modern Python features like built-in generics (`list[str]` vs `List[str]`)
  - Updated MyPy configuration target from Python 3.8 to 3.9

## [0.2.5] - 2025-09-08
### Added
- **[FIX] UI Interaction Fixes & Hint System Overhaul**: Major improvements to game usability and professional polish
  - Fixed spacebar (end turn) being blocked by tutorial overlays - now works even during tutorials
  - Fixed unprofessional staff hire popup showing automatically at game start
  - Implemented Factorio-style hint system: hints show once, auto-dismiss, can be reset
  - Added debug tools: Ctrl+D (UI state debug), Ctrl+E (emergency popup clear), Ctrl+R (reset hints)
  - Separated hints from tutorials with independent configuration
  - Automatic cleanup for stuck UI states (turn processing, overlay conflicts, orphaned popups)
  - Improved button click consistency and modal dialog behavior
  - Enhanced settings menu with hint status display and controls

### Fixed
- **Configuration Consistency**: Fixed starting staff count mismatch between JSON config and config manager
- **Event Handling Priority**: Resolved conflicts between tutorial overlays and core game controls
- **Modal Dialog Behavior**: Improved popup and dialog interaction handling

## [Unreleased]
### Added
- **[ACHIEVE] Achievements & Enhanced Endgame System (Issue #195)**: Comprehensive achievement tracking and victory conditions beyond binary win/lose
  - 24 achievements across 8 categories: Survival, Workforce, Research, Financial, Safety, Reputation, Competitive, Rare
  - 4-tier rarity system: Common, Uncommon, Rare, Legendary achievements
  - Ultimate victory condition: Reach p(Doom) = 0 (complete AI safety solution)
  - Enhanced warning system with 6 threat levels (80%, 85%, 90%, 95%, 98%, 99% doom thresholds)
  - Pyrrhic victory analysis: Win conditions evaluated against costs (financial, reputational, safety)
  - Strategic success scenarios: Major progress recognition without requiring perfect victory
  - Deep integration: Achievement progress tracking with all existing systems (technical debt, opponents, economic cycles)
  - Turn-based achievement checking with defensive programming (system errors never crash game)
  - Semi-programmatic endgame text generation based on player strategy analysis and resource management patterns
- **[CASCADE] Technical Failure Cascades (Issue #193)**: Comprehensive failure cascade system modeling realistic organizational crisis management
  - 7 types of technical failures with cascading effects (Research setbacks, Security breaches, System crashes, etc.)
  - Near-miss system providing learning opportunities without immediate consequences
  - Player choice between transparency/learning vs cover-up/reputation protection
  - 3-tier cascade prevention system: Incident Response, Monitoring Systems, Communication Protocols
  - Long-term consequences: Transparency builds trust, cover-ups increase future risks
  - 4 new actions: Incident Response Training, Monitoring Systems, Communication Protocols, Safety Audit
  - 4 cascade-specific events: Near-Miss Averted, Cover-Up Exposed, Transparency Dividend, Cascade Prevention Success
- **[ECONOMIC] Economic Cycles & Funding Volatility (Issue #192)**: Complete historical AI funding timeline (2017-2025)
  - Realistic economic phases: Boom, Stable, Correction, Recession, Recovery
  - 5 funding sources with different cycle sensitivities (Seed, Venture, Corporate, Government, Revenue)
  - Enhanced fundraising system with 4 advanced funding actions (Series A, Government grants, etc.)
  - 7 economic-specific events triggered by market conditions
  - Historical anchors based on real AI funding patterns and market cycles
- **[PLAYER] New Player Experience Enhancement**: Improved onboarding with tutorial/intro selection
  - Replaced "Launch Lab" with "New Player Experience" in main menu
  - Checkbox-based interface for tutorial and intro scenario selection
  - Contextual intro text explaining game premise and starting conditions
  - Responsive UI design with keyboard and mouse navigation support

### Changed
- **[ASCII] ASCII Compatibility**: Converted all Unicode symbols to ASCII equivalents
  - Replaced arrows, emojis, and Unicode symbols with ASCII alternatives
  - Fixed encoding issues causing 'charmap' codec errors on some systems
  - Maintained visual consistency while ensuring cross-platform compatibility
  - Improved terminal output compatibility across different environments

### Technical
- **[TESTS] Enhanced Test Coverage**: Added 29 new unit tests for technical failure cascades, plus 17 tests for economic cycles and new player experience
- **[ARCH] Modular Architecture**: Technical failure cascades system designed for extensibility
  - Clean separation between cascade logic, game state integration, and UI
  - Deterministic RNG integration for reproducible failure scenarios
  - Comprehensive event system integration with enhanced events support
  - Integration with existing technical debt and research quality systems
- **[SYSTEM] System Integration**: Economic cycles and technical failures systems designed for interoperability
  - Clean separation between game logic, UI, and specialized mechanics
  - Backward compatibility maintained for existing save files

## [0.2.2] - 2025-09-04 - "Technical Debt Resolution & Privacy-First Systems"
### [TECH] Technical Debt Resolution
- **Fixed all critical test failures**: 137/137 tests now passing (previously 4 categories failing)
- **Action Points System**: Fixed validation logic for meta-actions (0 AP cost properly supported)
- **Sound Configuration**: Aligned config manager defaults with actual config files  
- **Bug Reporter**: Cross-platform path handling for Windows/Unix compatibility
- **File Handle Management**: Proper cleanup of logging resources on Windows

### [PRIVACY] Privacy-First Infrastructure
- **Complete Privacy Policy**: Comprehensive privacy documentation and implementation
- **Local-First Design**: All data stored locally by default, no cloud transmission without opt-in
- **Pseudonymous Competition**: Leaderboard system using chosen display names, no personal data
- **Granular Privacy Controls**: User controls exactly what data to share and when
- **Open-Source Privacy**: All privacy-related code auditable and transparent

### [DETERMIN] Deterministic Gameplay System
- **Reproducible Games**: Seed-based deterministic random number generation
- **Competitive Verification**: Prove achievements through mathematical reproducibility
- **Context-Aware RNG**: All random events tracked with context for debugging/analysis
- **Global RNG Management**: Consistent random state across entire game session
- **Audit Trail**: Complete tracking of RNG calls for competitive integrity

### [LOGGING] Verbose Logging Infrastructure (Opt-In Only)
- **Multi-Level Logging**: MINIMAL/STANDARD/VERBOSE/DEBUG detail levels
- **Comprehensive Tracking**: Actions, resource changes, and RNG events logged
- **JSON Export**: Machine-readable logs for analysis tools and strategy improvement
- **Privacy Controls**: Completely opt-in, disabled by default, user-controlled cleanup
- **Performance Optimized**: Minimal overhead with efficient file management

### [LEADERBOARD] Privacy-Respecting Leaderboards
- **Pseudonymous Participation**: User-chosen display names only, no real identities
- **Local-First Storage**: Scores stored locally with optional cloud synchronization
- **Verification Without Surveillance**: Cryptographic verification without personal data
- **User Control**: Enable/disable participation anytime without penalty
- **Competitive Integrity**: Deterministic gameplay enables fair competition

### [TEST] Comprehensive Test Coverage
- **New Test Suites**: 49 new unit tests for privacy, deterministic, and logging systems
- **100% Test Success**: All 137 tests passing across all platforms
- **Edge Case Coverage**: Extensive testing of boundary conditions and error scenarios
- **Cross-Platform Verification**: Windows, macOS, and Linux compatibility tested

### [DOCS] Enhanced Documentation
- **Privacy Policy** (docs/PRIVACY.md): Complete privacy practices and user rights
- **Technical Debt Resolution** (docs/TECHNICAL_DEBT_RESOLUTION.md): Detailed implementation notes
- **Updated README**: Privacy-first messaging and new feature documentation
- **API Documentation**: Comprehensive inline documentation for all new systems

### [ARCH] Architecture Improvements
- **Modular Services**: Clean separation of concerns with `src/services/` directory
- **GameState Integration**: Seamless integration with existing game architecture
- **Backward Compatibility**: All existing saves and configurations work unchanged
- **Error Handling**: Graceful degradation and comprehensive error recovery

## [0.2.1] - 2025-09-04 - "Three Column" Hotfix Candidate
### Added
- **[LAYOUT] 3-Column Layout System**: Complete UI architecture overhaul for better organization
  - **Left Column**: Repeating actions (hire, research, etc.) with visual action counters
  - **Right Column**: Strategic one-off actions (upgrades, board meetings, etc.)
  - **Middle Column**: Staff animations and context displays
  - **Smart Action Categorization**: Automatic sorting of actions by type and frequency
- **[KEYBOARD] Comprehensive Keystroke Support**: Fast-paced gameplay with keyboard shortcuts
  - **Auto-Generated Keybindings**: Every visible action gets a unique keyboard shortcut
  - **Visual Key Display**: All buttons show their assigned keys (e.g., "[1] Hire Staff")
  - **Enter Key Support**: Enter/Return now works same as Space for turn processing
  - **Conflict Resolution**: Intelligent key assignment prevents duplicate bindings
- **[VISUAL] Enhanced Visual Differentiation**: Color-coded action categories for quick recognition
  - **Research Actions**: Blue accent coloring for safety/interpretability research
  - **Economic Actions**: Green accent coloring for hiring/compute purchases
  - **Strategic Actions**: Distinct styling for board meetings, lobbying, etc.
  - **Button Size Optimization**: Reduced button heights (42px left, 35px right) for better fit
- **[LAYOUT] Layout Improvements**: Better spacing and visibility management
  - **Context Window Buffer**: 2% vertical buffer prevents buttons hiding under context display
  - **Text Overflow Protection**: Strategic action names truncated cleanly for right column
  - **Early Game Filtering**: UI starts minimal and grows as actions unlock
  - **Configuration Support**: JSON-based layout switching with `enable_three_column_layout`

### Changed
- **Employee Animation System**: Temporarily simplified during UI transition for cleaner testing
- **Button Text Display**: Shortened action names for better readability in narrow columns
- **Resource Header**: Optimized for 3-column layout proportions

### Fixed
- **Button Visibility**: All visible buttons now guaranteed to be clickable (no hidden buttons)
- **Text Overflow**: Right column text no longer overflows or clips
- **Layout Responsiveness**: Better handling of varying numbers of available actions

## [0.2.0] - 2025-09-04
### Added
- **[RETRO] Retro 80s Context Window System**: Complete overhaul of information display
  - **80s Techno-Green Styling**: ALL CAPS DOS-style context window with retro color scheme
  - **Dynamic Context Display**: Hover over actions/upgrades for detailed information
  - **Green Matrix Theme**: Background (40,80,40), Text (200,255,200) for authentic retro feel
  - **Smart Information Architecture**: Moved descriptions from cramped buttons to spacious context area
- **[VISUAL] 8-bit Style Resource Icons**: Complete visual redesign of resource display
  - **Money Icon**: Pixelated $ symbol in gold (255,230,60)
  - **Staff Icon**: Simple person silhouette (head + body)
  - **Reputation Icon**: Star polygon in blue (180,210,255)
  - **Action Points Icon**: Lightning bolt with glow effects
  - **Doom Icon**: Skull symbol in red (255,80,80)
  - **Compute Icon**: "2^n" exponential notation for computing power
  - **Research Icon**: Light bulb for research progress
  - **Papers Icon**: Document with text lines for publications
- **[DEV] Developer Tools & Quality of Life**
  - **Screenshot Hotkey**: Press `[` key to capture game screenshots
  - **Screenshot Management**: Auto-saves to `screenshots/` folder with timestamps
  - **Window Mode Default**: Disabled fullscreen for better Alt+Tab and screen capture compatibility
- **[UI] Action Filtering & UI Polish**
  - **Smart Action Display**: Only show unlocked actions (12/24 visible initially)
  - **Button Reorganization**: Moved "Hire Staff" to logical position 5
  - **Starting Resources**: Set default staff to 0 for better game balance
  - **Tutorial Independence**: Resource display works regardless of tutorial state

### Fixed
- **Resource Display Alignment**: Fixed kerning issues between Reputation, Research, and AP
- **Text Overflow**: Eliminated cramped button text by moving descriptions to context window
- **UI Visibility**: Removed tutorial dependencies that hid UI improvements
- **Spacing & Layout**: Consistent margins and alignment across all resource displays
- **Screenshot Functionality**: Alt+Tab and screen capture tools now work properly

## [Unreleased]
### Added
- **[SETTINGS] Enhanced Settings System**: Comprehensive settings and configuration architecture
  - **Custom Seed Management**: Fixed critical "Launch with Custom Seed" crash, added seed validation and normalization
  - **Categorical Settings Organization**: Audio, Gameplay, Accessibility, and Game Configuration modes
  - **Seed Management System**: Weekly community seeds, custom seed validation, seed history tracking
  - **Game Configuration System**: Custom game rule modifications, scenario sharing, template system
  - **Modern Settings UI**: `src/ui/enhanced_settings.py` with improved accessibility and user experience
  - **Service Layer Architecture**: `src/services/seed_manager.py` and `src/services/game_config_manager.py`
  - **Integration Layer**: `src/ui/settings_integration.py` for gradual adoption and compatibility
  - **Demo and Testing Tools**: `demo_settings.py` for interactive testing, `test_fixes.py` for validation
- **[UI/UX] UI/UX Improvements**: Major improvements to interface quality and information accessibility
  - **Fixed Resource Bar Kerning**: Replaced fixed positioning with dynamic spacing for better readability
  - **Context Window System**: Comprehensive contextual help system with detailed information on hover
    - Minimizable context window at bottom of screen (20% height expanded, 8% minimized)
    - Rich context information for all UI elements (resources, actions, upgrades, buttons)
    - Professional dark theme styling with responsive design
    - Progressive disclosure: detailed info when needed, hidden otherwise
    - Click to minimize/maximize for user preference
  - **Enhanced Hover Detection**: Extended existing hover system with rich context data
  - **Improved Resource Display**: Dynamic spacing calculation adapts to text length and screen size
  - **Better Information Density**: Contextual help reduces UI clutter while improving accessibility

### Fixed
- **Critical Menu Alignment Bug**: Fixed crash when selecting "Launch with Custom Seed" from main menu
  - Synchronized menu_items arrays across main.py, ui.py, and src/ui/menus.py
  - Corrected menu handling logic in handle_menu_click() and handle_menu_keyboard()
  - Restored full functionality of custom seed system with proper validation
- **Critical Game Launch Crash Fix**: Fixed `AttributeError: 'OnboardingSystem' object has no attribute 'get_mechanic_help'` that prevented game startup
  - Implemented missing `get_mechanic_help()` method in `OnboardingSystem` class
  - Added comprehensive help content for core mechanics: staff hiring, upgrades, action points, and doom warnings
  - Graceful error handling for invalid mechanic names
  - Warning logging for stub implementation as placeholder for future enhancements
  - All first-time help content tests now pass (7/7 passing)
- **UI Rendering Issues**: Fixed upgrade rectangle handling and context window compatibility
  - Fixed None value handling in upgrade rectangle creation
  - Added proper error handling for context window drawing
  - Improved font size calculations with minimum size constraints

### Added
- **Menu Structure Optimization**: Streamlined main menu and tutorial flow for improved user experience
  - Simplified main menu from 7 to 4 core options: Launch Lab, Game Config, Settings, Exit
  - Reordered tutorial choice to default to "No - Regular Mode" for faster game access
  - Removed less essential options from main screen (Player Guide, README, Report Bug, Custom Seed)
  - Maintained all functionality while reducing choice overload and cognitive load
- **Batch 1 - Stability & UI Correctness Improvements**: Critical bug fixes and UI enhancements
  - **Navigation Back Button Fix (Issues #122, #118)**: Back button now shows at navigation depth >= 1 (previously > 1)
    - Added `should_show_back_button(depth)` helper function for clarity and future maintenance
    - Improved navigation consistency across menu systems
    - Enhanced user experience with predictable back button behavior
  - **UI Overlay Safe Zone System (Issue #121)**: Prevents overlay panels from obscuring interactive areas
    - Implemented `get_ui_safe_zones()` to define protected UI areas (action buttons, upgrades, resources, event log)
    - Added `find_safe_overlay_position()` with first-fit positioning algorithm
    - Smart positioning prioritizes gap between action and upgrade areas
    - Foundation for future drag-and-drop overlay functionality
  - **Accounting Software Verification (Issue #52)**: Confirmed correct balance change tracking and display
    - Verified proper `last_balance_change` implementation in `GameState._add()`
    - Color-coded display: green for positive/zero, red for negative changes
    - Only tracks when accounting software upgrade is purchased
  - **Regression Test Coverage (Issue #131)**: Added comprehensive test suites for quality assurance
    - 15+ navigation and back button tests in `test_navigation_stack.py`
    - 8+ accounting software tests in `test_accounting_software.py`
    - 7+ UI overlap prevention tests in `test_ui_overlap_prevention.py`
    - All existing tests maintained and passing
- **Fun Feedback for Achievements: 'Zabinga!' Sound (Issue #66)**: Celebratory audio feedback system
  - Generated 'Zabinga!' sound effect for research paper completion milestones
  - Integrated with research paper publication logic in game_state.py
  - Harmonically rich celebratory sound with musical progression (Za-bin-ga!)
  - Comprehensive test coverage for paper completion sound triggering
  - Trademark-safe replacement for previous 'bazinga' references
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

#### Core Functionality [COMPLETE]
- [x] Game launches successfully with main menu
- [x] All game modes function correctly (weekly seed, custom seed)
- [x] Core resource management works (money, staff, reputation, doom)
- [x] Action system executes properly with costs and effects
- [x] Event system triggers and resolves correctly
- [x] Upgrade system allows purchases and effect activation
- [x] Game end conditions work (win/lose scenarios)
- [x] Opponents system functions with espionage and AI behavior
- [x] Enhanced event system (popups, deferred events) works properly

#### Technical Quality [COMPLETE]
- [x] Full test suite passes (115/115 tests)
- [x] No critical bugs in core gameplay
- [x] Game logging system captures all events correctly
- [x] Bug reporting system functions properly
- [x] Cross-platform compatibility (Windows, macOS, Linux)

#### Documentation & User Experience [COMPLETE]
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
- [Developer Guide - Release & Deployment](docs/DEVELOPERGUIDE.md#release--deployment)
- [Semantic Versioning Policy](docs/DEVELOPERGUIDE.md#version-management)
- [Contributing Guidelines](docs/DEVELOPERGUIDE.md#contribution-guidelines)
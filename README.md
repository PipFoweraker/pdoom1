# P(Doom): Bureaucracy Strategy Game

A satirical meta-strategy game about AI Safety, inspired by *Papers, Please*, *Pandemic*, and clicker games.

**Current Version:** See [CHANGELOG.md](CHANGELOG.md) for latest release information and version history.

WARNING
This is Buggy As Shit.  If you are not using exactly whatever kludge windows python bash default install I am using, this might not even work or will be unexpectedly ugly. Expect bugs, expect failure. If you are here and reading this, you got in early, cool beans. Stable build coming after unstable 0.1.1 release for early alpha and to maybe point hapless game  playing agents at.

**📖 Documentation:**
- **[Player Guide](docs/PLAYERGUIDE.md)** - How to play, controls, and strategies  
- **[Developer Guide](docs/DEVELOPERGUIDE.md)** - Contributing, code structure, and testing
- **[Configuration System](docs/CONFIG_SYSTEM.md)** - Game customization and settings
- **[Integration Guide](INTEGRATION_GUIDE.md)** - Enhanced settings system integration
- **[Settings System Summary](SETTINGS_SYSTEM_SUMMARY.md)** - Overview of new features
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## Table of Contents
- [Quick Start](#quick-start) (Line 29)
  - [Requirements](#requirements) (Line 31)
  - [Installation & Setup](#installation--setup) (Line 35)
  - [Run the Game](#run-the-game) (Line 44)
- [Game Features](#game-features) (Line 51)
- [Visual Feedback System](#visual-feedback-system) (Line 65)
- [Tutorial & Onboarding System](#tutorial--onboarding-system) (Line 76)
- [Troubleshooting](#troubleshooting) (Line 87)
  - [Common Issues](#common-issues) (Line 89)
  - [Error Logs](#error-logs) (Line 111)
  - [Testing the Installation](#testing-the-installation) (Line 118)
  - [Getting Help](#getting-help) (Line 130)
  - [Dependencies](#dependencies) (Line 137)
- [Versioning and Releases](#versioning-and-releases) (Line 152)

## Quick Start

### Requirements
- Python 3.8+
- [pygame](https://www.pygame.org/)

### Installation & Setup
```sh
# Install core dependency
pip install pygame

# For sound effects (optional but recommended)
pip install numpy

# Or install all dependencies (including testing tools)
pip install -r requirements.txt
```

### Run the Game
```sh
python main.py
```

The game opens with an enhanced main menu featuring:
- **Launch Lab**: Start with weekly challenge seed
- **Launch with Custom Seed**: Enter custom seed for reproducible gameplay
- **Settings**: Organized settings (Audio, Gameplay, Accessibility, Keybindings)  
- **Player Guide**: In-game documentation and help

### Game Configuration & Community Features

P(Doom) now includes a comprehensive configuration system for community engagement:

```sh
# Try the enhanced settings demo
python demo_settings.py

# Test the new functionality
python test_fixes.py
```

**Community Features:**
- Create custom game configurations with different starting resources and difficulty
- Share config + seed combinations for community challenges
- Export/import configuration packages
- Templates for Standard, Hardcore, Sandbox, and Speedrun modes

For complete configuration details, see **[Configuration System](docs/CONFIG_SYSTEM.md)**.

## Game Features

P(Doom) offers a rich strategy experience with sophisticated systems that evolve as you play:

- **📚 Complete Tutorial System**: Interactive guidance for new players with context-sensitive help
- **⚡ Strategic Action Points**: Resource management system that scales with your organization  
- **🏢 Milestone Events**: Unlock new mechanics as your lab grows (managers, board oversight, etc.)
- **🤖 AI Opponents**: Compete against 3 unique labs with hidden information and espionage
- **🎯 Enhanced Settings System**: Organized settings (Audio, Gameplay, Accessibility, Keybindings)
- **⚙️ Game Configuration**: Create and share custom game configurations and seeds
- **🌱 Seed Management**: Weekly challenge seeds, custom seeds, and community sharing
- **🏆 Community Features**: Export/import config + seed packages for challenges
- **Enhanced Events**: Advanced crisis management with deferral and response options
- **🎨 Visual Feedback**: Smooth UI transitions and clear state indicators
- **🔊 Audio Feedback**: Sound effects for achievements and important actions
- **♿ Accessibility**: Keyboard navigation, scalable text, and comprehensive help system
- **💡 Context Window System**: Comprehensive contextual help with detailed information on hover
- **📐 Improved UI Layout**: Fixed kerning and dynamic spacing for better readability

For complete gameplay details, see the **[Player Guide](docs/PLAYERGUIDE.md)**.

## Visual Feedback System

P(Doom) features smooth visual transitions and clear feedback:

- **Upgrade Animations**: Watch purchased upgrades smoothly transition to icons
- **Action Point Glow**: Visual feedback when AP is spent
- **UI State Changes**: Clear indicators for all interactions
- **Accessibility**: High contrast, keyboard navigation, and scalable text

For detailed UI guide, see the **[Player Guide](docs/PLAYERGUIDE.md#visual-feedback--ui-transitions)**.

## Tutorial & Onboarding System

P(Doom) includes comprehensive guidance for new players:

- **Interactive Tutorial**: Step-by-step guidance on first playthrough
- **Context-Sensitive Help**: Automatic tips for new mechanics
- **In-Game Help**: Press `H` for instant access to the Player Guide
- **Fully Optional**: Skip or disable if you prefer to learn by playing

For complete tutorial details, see the **[Player Guide](docs/PLAYERGUIDE.md#new-player-tutorial--help-system)**.

## Troubleshooting

### Common Issues

**Game won't start:**
- Ensure Python 3.8+ is installed: `python --version`
- Install pygame: `pip install pygame`
- Check that all files are in the same directory

**"Launch with Custom Seed" not working (Fixed):**
- This issue has been resolved in the latest version
- Menu items are now properly aligned between UI and click handlers
- Custom seed functionality works correctly

**Menu navigation issues (Fixed):**
- Menu items now properly match between display and functionality
- Keyboard and mouse navigation work consistently
- Settings menu is now organized into logical categories

**AttributeError crashes on startup (Fixed):**
- If you encounter `AttributeError: 'OnboardingSystem' object has no attribute 'get_mechanic_help'`, update to the latest version
- This critical launch crash has been fixed by implementing the missing method
- The fix includes comprehensive help content for core game mechanics

**Missing pygame module:**
```sh
pip install pygame
```

**Black screen or UI not responding:**
- Try resizing the window
- Restart the game
- Check terminal for error messages

**UnboundLocalError crashes (Fixed in latest version):**
- If you encounter crashes related to "first_time_help_content" or similar variables, update to the latest version
- This issue has been resolved in recent releases
- See CHANGELOG.md for version history and fixes

### Error Logs
The game automatically creates detailed logs in the `logs/` directory:
- **Location**: `logs/gamelog_<YYYYMMDD_HHMMSS>.txt`
- **Contents**: Game actions, events, and state changes
- **Privacy**: No personal information collected
- **Use**: Helpful for reporting bugs and debugging issues

### Testing the Installation

**Quick functionality test:**
```sh
python test_fixes.py
```
This validates that all systems are working properly, including the enhanced settings and configuration features.

**Enhanced settings demonstration:**
```sh
python demo_settings.py
```
Interactive demo of the new settings menu system and game configuration features.

**Full test suite (recommended for developers):**
```sh
# Run all tests (should show ~507 tests passing, takes about 38 seconds)
python -m unittest discover tests -v
```

**Important**: Always run tests before deploying changes. Tests are automatically run in the deployment pipeline to ensure code quality and prevent regressions.

If tests fail, check your Python and pygame installation.

### Getting Help

- **In-game**: Use the bug reporting system (accessible through end-game menu)
- **Documentation**: See [Player Guide](docs/PLAYERGUIDE.md) for gameplay help
- **Development**: See [Developer Guide](docs/DEVELOPERGUIDE.md) for code issues
- **Releases**: Check [Changelog](CHANGELOG.md) for version history and known issues

### Dependencies

**Core Requirements:**
- Python 3.8+
- pygame (graphics and input handling)

**Optional/Development:**
- pytest (for testing)
- numpy (for sound effects - install with `pip install numpy`)
- Standard library modules: os, sys, json, random, datetime

**Note:** Sound effects require numpy. If numpy is not installed, the game will run without sound. Install numpy for full audio experience: `pip install numpy`

**System Requirements:**
- Any OS that supports Python and pygame (Windows, macOS, Linux)
- ~50MB disk space
- Basic graphics support (no special hardware needed)

## Versioning and Releases

This project follows [Semantic Versioning](https://semver.org/) (SemVer) for all releases:

- **MAJOR** (X.0.0): Incompatible gameplay changes, save file format changes
- **MINOR** (0.X.0): New features, game modes, backwards-compatible enhancements  
- **PATCH** (0.0.X): Bug fixes, performance improvements, documentation

### Release Information
- **Current Target**: v0.1.0 (first official semantic versioned release)
- **Release Notes**: See [CHANGELOG.md](CHANGELOG.md) for detailed version history
- **Release Process**: Automated via GitHub Actions on version tags
- **Minimum Conditions**: All features tested, documented, and stable

### For Developers
- Version managed centrally in `version.py`
- Version automatically displayed in:
  - Window title bar
  - Bottom right corner of main menu and game UI
  - Accessible via `get_display_version()` function
  - Falls back to "dev" when running unbuilt/development versions
- Release checklist documented in `docs/RELEASE_CHECKLIST.md`
- Automated testing and release workflows in `.github/workflows/`
- All releases include source archives and checksums

---

**Not affiliated with any AI org. For fun, education, and satire only.**

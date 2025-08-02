# P(Doom): Bureaucracy Strategy Game

A satirical meta-strategy game about AI Safety, inspired by *Papers, Please*, *Pandemic*, and clicker games.

**Current Version:** See [CHANGELOG.md](CHANGELOG.md) for latest release information and version history.

**📖 Documentation:**
- **[Player Guide](PLAYERGUIDE.md)** - How to play, controls, and strategies  
- **[Developer Guide](DEVELOPERGUIDE.md)** - Contributing, code structure, and testing
- **[Changelog](CHANGELOG.md)** - Version history and release notes

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
- **Action Points System**: Strategic action limitation with 3 Action Points per turn
- **Action System**: Choose from various actions each turn to advance your strategy
- **Research & Development**: Publish papers, buy compute, and advance AI safety
- **Enhanced Event System**: Navigate unexpected challenges with advanced response options
- **Milestone-Driven Special Events**: Unlock new mechanics as your organization grows

### Milestone-Driven Special Events
The game features a sophisticated milestone system that unlocks new mechanics and challenges as your organization scales:

**Management Milestones:**
- **Manager System**: At 9+ employees, hire managers to oversee teams (1.5x hiring cost)
- **Team Clusters**: Each manager can oversee up to 9 employees effectively
- **Static Effects**: Unmanaged employees beyond 9 become unproductive (red slash overlay)
- **Visual Feedback**: Managers appear as green blobs vs blue employee blobs

**Financial Oversight Milestones:**
- **Board Member Installation**: Spend >$10,000 in a turn without accounting software triggers board oversight
- **Compliance Monitoring**: Board members install 2 board members with audit powers
- **Search Actions**: Unlock compliance searches with 20% success rate for various benefits
- **Audit Risk**: Accumulating penalties for non-compliance (reputation loss, financial fines)

**Upgrade Systems:**
- **Accounting Software**: Visible right-panel upgrade ($500) enables cash flow tracking
- **Compliance Prevention**: Purchasing accounting software blocks board member milestone
- **Cash Flow UI**: Persistent balance change indicators when accounting software is active

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

### Action Points System
The game features a sophisticated Action Points (AP) system that creates strategic depth through resource management and staff scaling:

**Basic Mechanics:**
- **Base Action Points**: 3 AP per turn
- **Staff Scaling**: Regular staff provide +0.5 AP each
- **Admin Assistants**: Specialized staff providing +1.0 AP each
- **Visual Feedback**: AP counter shows current/max AP with glow effects when spent
- **Turn Reset**: AP automatically resets to calculated maximum at the start of each turn

**Specialized Staff Types:**
- **Admin Assistants**: High-cost staff (+1.0 AP bonus each) for maximum action capacity
- **Research Staff**: Enable delegation of research actions (Safety Research, Governance Research)
- **Operations Staff**: Enable delegation of operational actions (Buy Compute)

**Delegation System:**
- **Research Delegation**: Research actions can be delegated to research staff with 80% effectiveness
- **Operations Delegation**: Operational actions can be delegated to ops staff, often with lower AP costs
- **Auto-Delegation**: Actions are automatically delegated when beneficial (lower AP cost)
- **Staff Requirements**: Each delegatable action requires minimum specialized staff

**Strategic Implications:**
- **Early Game**: Careful AP budgeting with limited 3-4 AP per turn
- **Mid Game**: Strategic staff investment decisions between regular, admin, and specialized staff
- **Late Game**: Complex staff compositions enabling high AP counts and efficient delegation
- **Prioritization**: High-impact actions require careful AP planning and staff allocation

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
# Run all tests (should show 152 tests passing, including milestone and static effects tests)
python -m unittest discover tests -v
```

**Important**: Always run tests before deploying changes. Tests are automatically run in the deployment pipeline to ensure code quality and prevent regressions.

If tests fail, check your Python and pygame installation.

### Getting Help

- **In-game**: Use the "Report Bug" option in the main menu
- **Documentation**: See [Player Guide](PLAYERGUIDE.md) for gameplay help
- **Development**: See [Developer Guide](DEVELOPERGUIDE.md) for code issues
- **Releases**: Check [Changelog](CHANGELOG.md) for version history and known issues

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
- Release checklist documented in `RELEASE_CHECKLIST.md`
- Automated testing and release workflows in `.github/workflows/`
- All releases include source archives and checksums

---

**Not affiliated with any AI org. For fun, education, and satire only.**

# P(DOOM): PRIVACY-FIRST BUREAUCRACY STRATEGY GAME

> **A SATIRICAL STRATEGY GAME ABOUT AI SAFETY RESEARCH IN A BUREAUCRATIC NIGHTMARE**
> 
> **FEATURING DETERMINISTIC GAMEPLAY AND PRIVACY-RESPECTING COMPETITION**
> 
> INSPIRED BY PAPERS PLEASE, PANDEMIC, AND CLICKER GAMES

**Current Version:** v0.2.0 "Technical Debt Resolution" - Privacy-First & Deterministic Gameplay

🛡️ **PRIVACY-FIRST DESIGN** - Your data stays under your control  
🎯 **DETERMINISTIC GAMEPLAY** - Reproducible games for competitive verification  
📊 **OPTIONAL ANALYTICS** - Detailed logging for strategy improvement (opt-in only)  
🏆 **PSEUDONYMOUS COMPETITION** - Compete without compromising privacy  

=========================================
QUICK START
=========================================

PREREQUISITES:
- Python 3.8 or higher (3.12+ recommended)
- Git (for cloning the repository)
- Command line access (Terminal, PowerShell, Git Bash, etc.)

🔒 **PRIVACY NOTE:** P(Doom) is designed with privacy-first principles. All data stays local by default, and any optional features require explicit opt-in. See [docs/PRIVACY.md](docs/PRIVACY.md) for full details.

STEP 1: GET PYTHON
------------------
Windows:
    # Check if you have Python
    python --version

    # If not installed, download from: https://python.org/downloads
    # OR install via Microsoft Store: "Python 3.12"

macOS:
    # Check if you have Python
    python3 --version

    # Install via Homebrew (recommended):
    brew install python3

    # OR download from: https://python.org/downloads

Linux:
    # Ubuntu/Debian:
    sudo apt update && sudo apt install python3 python3-pip

    # Fedora/RHEL:
    sudo dnf install python3 python3-pip

STEP 2: GET GIT (if needed)
---------------------------
    # Check if you have Git
    git --version

    # If not: https://git-scm.com/downloads
    # Windows users: Git Bash is recommended for best experience

STEP 3: INSTALL THE GAME
------------------------
    # Clone the repository
    git clone https://github.com/PipFoweraker/pdoom1.git

    # Navigate to game directory
    cd pdoom1/pdoom1

    # Install dependencies
    pip install -r requirements.txt

    # Run the game!
    python main.py

ALTERNATIVE: DOWNLOAD ZIP
-------------------------
1. Download: Latest Release ZIP from GitHub
2. Extract to your desired folder
3. Open command line in the pdoom1/pdoom1 folder
4. Run: pip install -r requirements.txt
5. Play: python main.py

================================================================================
GAME FEATURES (v0.2.2)
================================================================================

🆕 **PRIVACY-FIRST SYSTEMS:**
- **Local-First Storage**: All your data stays on your device by default
- **Pseudonymous Competition**: Compete without revealing personal information
- **Granular Privacy Controls**: Choose exactly what data to share and when
- **Open-Source Privacy**: Audit our privacy implementation yourself

🎯 **DETERMINISTIC GAMEPLAY:**
- **Reproducible Games**: Same seed = same outcomes for competitive verification
- **Mathematical Fairness**: Prove your achievements without sharing personal data
- **Strategy Verification**: Analyze optimal plays with deterministic replay
- **Competitive Integrity**: Fair competition through cryptographic verification

📊 **ADVANCED ANALYTICS (OPT-IN):**
- **Verbose Logging**: Detailed action tracking for strategy improvement
- **Performance Metrics**: Turn-by-turn analysis of resource management
- **RNG Transparency**: Full audit trail of random events for debugging
- **Data Export**: JSON export for custom analysis tools

🏆 **PRIVACY-RESPECTING LEADERBOARDS:**
- **Pseudonymous Only**: Compete with chosen display names, not real identities
- **User-Controlled**: Enable/disable leaderboard participation anytime
- **Local-First**: Scores stored locally with optional cloud sync
- **Verification Without Surveillance**: Prove achievements without data harvesting

3-COLUMN UI LAYOUT:
- Left Column: Repeating actions (Hire, Research, Build)
- Right Column: Strategic decisions (Board Meetings, Lobbying) 
- Middle Column: Staff visualizations and context displays

FULL KEYBOARD SUPPORT:
- Every action has a hotkey - look for [1], [H], [R] etc. on buttons
- Enter/Return = Same as Space (process turn)
- [ key = Take screenshot
- Escape = Quit game

ENHANCED VISUAL DESIGN:
- Retro 80s terminal aesthetic with green matrix styling
- Smart context window - hover over actions for details
- Color-coded actions - blue for research, green for economic
- 8-bit style resource icons with authentic pixelated look

================
HOW TO PLAY
================

1. Start the game with "python main.py"
2. Use your mouse to click actions or keyboard shortcuts shown on buttons
3. Manage resources: Money, Staff, Action Points, Reputation
4. Research AI Safety while dealing with bureaucratic chaos
5. Compete with rival labs and try to prevent AI doom!

CONTROLS:
- Mouse: Click buttons and UI elements
- Keyboard: Use hotkeys shown on buttons (e.g., [1], [H], [R])
- Space/Enter: Process turn and advance time
- [ key: Take screenshot
- Escape: Quit game

================
TROUBLESHOOTING
================

QUICK FIXES:
    # Game won't start?
    python --version  # Should be 3.8+
    pip install pygame

    # Missing dependencies?
    pip install -r requirements.txt

    # Still having issues?
    python -c "import pygame; print('Pygame working!')"

COMMON ISSUES:
- "pygame not found" -> Run "pip install pygame"
- "Python not found" -> Install Python from python.org
- Screen too small -> Game runs at 1024x768, resize your window
- Keyboard not working -> Make sure game window has focus (click on it)

WINDOWS USERS:
- Use Git Bash or PowerShell for best compatibility
- Python from Microsoft Store works great, this was built using python downloaded fresh. Weird path issues with Microsoft, boo.
- Antivirus blocking? Add folder to exclusions

================
DOCUMENTATION & SUPPORT
================

PLAYER RESOURCES:
- Player Guide (docs/PLAYERGUIDE.md) - How to play, controls, and strategies  
- Configuration Guide (docs/CONFIG_SYSTEM.md) - Customize your experience
- Changelog (CHANGELOG.md) - Version history and new features

DEVELOPER RESOURCES:  
- Developer Guide (docs/DEVELOPERGUIDE.md) - Contributing and code structure
- Integration Guide (INTEGRATION_GUIDE.md) - Advanced customization
- Hotfix Workflow (docs/HOTFIX_WORKFLOW.md) - Version management

GETTING HELP:
- GitHub Issues: Report bugs or request features
- GitHub Discussions: General questions and feedback

================
ADVANCED FEATURES
================

GAME MODES:
- **Standard**: Balanced gameplay experience
- **Deterministic**: Reproducible games using custom seeds for competitive play
- **Weekly Challenge**: Community seed competition with pseudonymous leaderboards
- **Privacy Mode**: All analytics and logging disabled (default)

PRIVACY CONTROLS:
    # Access privacy settings in-game
    Settings → Privacy → [Configure all privacy options]
    
    # Or review privacy documentation
    See: docs/PRIVACY.md

CONFIGURATION:
    # Try advanced settings
    python demo_settings.py

    # Test installation (includes privacy system tests)
    python test_fixes.py

For complete customization options, see Configuration Guide (docs/CONFIG_SYSTEM.md).

<<<<<<< HEAD
================================================================================
PRIVACY & DATA PROTECTION
================================================================================

P(Doom) is designed with **privacy-first principles**:

🔒 **YOUR DATA STAYS YOURS:**
- All game data stored locally by default
- No personal information required to play
- No data transmission without explicit opt-in

🎮 **PRIVACY-ENHANCED GAMING:**
- **Deterministic mode**: Compete fairly without sharing personal data
- **Pseudonymous leaderboards**: Choose your own display name
- **Optional analytics**: Enable detailed logging only if you want strategy insights
- **Local-first architecture**: Full offline functionality

📋 **TRANSPARENT PRACTICES:**
- **Open source**: All privacy code is auditable
- **Clear controls**: Granular privacy settings in-game
- **User ownership**: Export, modify, or delete your data anytime
- **No surprises**: Clear documentation of all data practices

**Read our full privacy policy:** [docs/PRIVACY.md](docs/PRIVACY.md)

================================================================================
DEVELOPMENT & CONTRIBUTING
================================================================================

RUNNING TESTS:
    # Quick validation (includes new privacy & deterministic systems)
    python test_fixes.py

    # Full test suite (137 tests)
    python -m pytest -v

    # Test specific new systems
    python -m pytest tests/test_deterministic_rng.py tests/test_verbose_logging.py tests/test_leaderboard.py -v

DOCUMENTATION:
- **Privacy Policy** (docs/PRIVACY.md) - Complete privacy documentation
- **Technical Debt Resolution** (docs/TECHNICAL_DEBT_RESOLUTION.md) - Recent improvements
- Developer Guide (docs/DEVELOPERGUIDE.md) - Code structure and contributing
- Player Guide (docs/PLAYERGUIDE.md) - Complete gameplay reference
- Hotfix Workflow (docs/HOTFIX_WORKFLOW.md) - Version management

================
VERSION STATUS
================

Current: v0.2.1 "Three Column" - Hotfix Candidate

This version is in ACTIVE DEVELOPMENT with rapid updates for UI stability. 
Expect frequent patches (0.2.2, 0.2.3, etc.) as we polish the experience.

Stability Target: v0.3.0 for wider distribution

================================================================================
LICENSE & ATTRIBUTION
================================================================================

Not affiliated with any AI organization. For fun, education, and satire only.

Created by @PipFoweraker
Report Issues: https://github.com/PipFoweraker/pdoom1/issues
Discussions: https://github.com/PipFoweraker/pdoom1/discussions

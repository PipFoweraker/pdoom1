# P(Doom): AI Safety Strategy Game

**A satirical strategy game about managing an AI safety lab racing to solve alignment before it's too late.**

![P(Doom) Screenshot](screenshots/pdoom_screenshot_20250918_104357.png)

## Quick Start

**Play Now:**
- **Windows**: Download from [Releases](https://github.com/PipFoweraker/pdoom1/releases)
- **Python**: `pip install -r requirements.txt && python main.py`
- **Godot**: Open `godot/project.godot` in Godot 4.x

## What is P(Doom)?

You manage a bootstrap AI safety lab with limited funds, racing against well-funded competitors to solve the alignment problem. Make strategic decisions about hiring, research, and resource allocation while P(Doom) rises or falls based on your choices.

**Core Gameplay:**
- Hire safety researchers vs. capability researchers
- Balance research output with existential risk
- Manage compute, money, and reputation
- React to random events and rival lab actions
- Try to reach turn 100 with P(Doom) at 0%

## Documentation

### For Players
- **[Installation Guide](docs/user-guide/INSTALLATION.md)** - Get the game running
- **[How to Play](docs/user-guide/GAMEPLAY.md)** - Game mechanics and strategy
- **[FAQ](docs/user-guide/FAQ.md)** - Common questions

### For Developers
- **[Contributing](docs/developer/CONTRIBUTING.md)** - How to contribute
- **[Architecture](docs/developer/ARCHITECTURE.md)** - Codebase structure
- **[Testing](docs/developer/TESTING.md)** - Running tests

### For Distributors
- **[Deployment](docs/deployment/DEPLOYMENT.md)** - Creating builds
- **[Privacy](docs/PRIVACY.md)** - Privacy design principles

## Current Version: v0.10.0

### Godot Implementation (Active Development)
- Full UI implementation with menus, settings, pre-game setup
- Comprehensive leaderboard system with seed filtering
- Error handling and debug tools (F3 overlay)
- Turn-based gameplay with event system
- **NEW**: Stray cat adoption event (turn 7)

### Python Implementation (Legacy/Stable)
- Command-line gameplay
- Global leaderboard export system
- Privacy-first analytics
- Extensive test coverage

## Links

- **Website**: [pdoom.org](https://pdoom.org) *(coming soon)*
- **Issues**: [GitHub Issues](https://github.com/PipFoweraker/pdoom1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/PipFoweraker/pdoom1/discussions)
- **License**: MIT

## Status

- **Python version**: Stable (v0.10.x)
- **Godot version**: Active development (v0.5.x)
- **Platform**: Windows, Linux, macOS (Python) | Godot 4.x export support

---

**Made with coffee and existential dread** | [Contributors](docs/CONTRIBUTORS.md)

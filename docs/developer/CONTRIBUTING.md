# Contributing to P(Doom)

Welcome! This guide will get you from zero to running the game in under 30 minutes.

## Quick Start (5 minutes)

### Prerequisites

- **Godot 4.5.1** - [Download here](https://godotengine.org/download)
- **Git** - For cloning the repository

### Clone and Run

```bash
# Clone the repository
git clone https://github.com/PipFoweraker/pdoom1.git
cd pdoom1

# Open the project in Godot
# Option A: Command line
godot godot/project.godot

# Option B: Open Godot Editor, click "Import", navigate to godot/ folder
```

Press **F5** to run the game. That's it!

## Development Setup

### Recommended Editor Setup

**VS Code Extensions:**
- [godot-tools](https://marketplace.visualstudio.com/items?itemName=geequlim.godot-tools) - GDScript support

**Godot Editor Settings:**
- External Editor: VS Code (Editor > Editor Settings > Text Editor > External)

### Project Structure

```
pdoom1/
├── godot/                 # Main game code
│   ├── scripts/           # GDScript files
│   │   ├── core/          # Game logic (game_state.gd, turn_manager.gd)
│   │   └── ui/            # UI controllers
│   ├── scenes/            # Godot scenes (.tscn)
│   ├── data/              # JSON data files (actions, events, upgrades)
│   ├── assets/            # Art, audio, fonts
│   └── tests/             # Unit and integration tests
├── docs/                  # Documentation
└── .github/               # CI/CD workflows
```

### Key Files to Know

| File | Purpose |
|------|---------|
| `godot/scripts/core/game_state.gd` | Core game state and logic |
| `godot/scripts/core/turn_manager.gd` | Turn processing |
| `godot/data/actions.json` | Action definitions |
| `godot/data/events.json` | Event definitions |
| `godot/data/upgrades.json` | Upgrade definitions |

## Running Tests

### Quick Syntax Check

```bash
# Check all GDScript files compile
godot --headless --path godot --quit
```

### Run Unit Tests

```bash
# Using the test runner script
cd godot
./tests/run_all_tests.sh    # Linux/macOS
./tests/run_all_tests.ps1   # Windows PowerShell

# Or run directly with Godot
godot --headless --path godot -s res://tests/run_tests.gd
```

### Run Specific Tests

```bash
# Run GUT tests for a specific directory
godot --headless --path godot -s res://addons/gut/gut_cmdln.gd \
  -gdir=res://tests/unit/ -gexit
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

- Follow existing code patterns
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes

```bash
# Syntax check
godot --headless --path godot --quit

# Run the game and test manually
godot godot/project.godot
# Press F5 to run
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: Add your feature description"
git push origin feature/your-feature-name
```

### 5. Open a Pull Request

Go to GitHub and create a PR against `main`. Fill out the PR template.

## Contribution Types

### Adding Game Content (Easiest)

Game content is data-driven. Add new items by editing JSON files:

- **New Action**: Edit `godot/data/actions.json`
- **New Event**: Edit `godot/data/events.json`
- **New Upgrade**: Edit `godot/data/upgrades.json`

See the existing entries for the expected format.

### Bug Fixes

1. Check [existing issues](https://github.com/PipFoweraker/pdoom1/issues)
2. Comment on the issue to claim it
3. Create a fix branch: `git checkout -b fix/issue-123-description`
4. Submit a PR referencing the issue

### New Features

1. Open an issue first to discuss the feature
2. Wait for approval before starting significant work
3. Keep PRs focused - one feature per PR

### Documentation

Documentation improvements are always welcome! Look for:
- Typos and unclear wording
- Missing information
- Outdated instructions

## Code Style

### GDScript

- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Add type hints where practical
- Keep functions focused and small

```gdscript
# Good
func calculate_doom_change(amount: int) -> int:
    return clamp(amount, -10, 10)

# Avoid
func calc(a):
    return a if a > -10 and a < 10 else (-10 if a < -10 else 10)
```

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `test:` Adding or updating tests

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/PipFoweraker/pdoom1/discussions)
- **Bugs**: Open an [Issue](https://github.com/PipFoweraker/pdoom1/issues)
- **Feature Ideas**: Open an Issue with the `enhancement` label

## First-Time Contributors

Look for issues labeled [`good first issue`](https://github.com/PipFoweraker/pdoom1/labels/good%20first%20issue). These are specifically scoped for newcomers.

**Good first contributions:**
- Fix typos in documentation
- Add missing tooltips
- Improve error messages
- Add test coverage for existing features
- Add new events or actions (content)

## Recognition

Contributors are recognized in:
- The in-game credits
- The [CONTRIBUTORS.md](../CONTRIBUTORS.md) file
- Our [Contributor Rewards Program](../CONTRIBUTOR_REWARDS.md) - submit a photo of your cat!

Thank you for contributing to P(Doom)!

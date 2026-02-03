# Contributing to P(Doom)

Welcome! This guide will get you from zero to running the game in under 30 minutes.

## Quick Start (5 minutes)

### Prerequisites

- **Godot 4.5.1** - [Download here](https://godotengine.org/download) (standard, not .NET)
- **Git** - For cloning the repository
- **Python 3.9+** - For tooling scripts (optional but recommended)

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

### Install Dependencies (Optional)

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Makefile Commands

If you have `make` available:

```bash
make run       # Launch the game
make test      # Run GUT unit tests
make lint      # Check GDScript syntax
make validate  # Validate data files
make health    # Run project health check
make clean     # Clean cache files
```

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
├── scripts/               # Python tooling and CI scripts
├── docs/                  # Documentation
└── .github/               # CI/CD workflows
```

### Key Files to Know

| File | Purpose |
|------|---------|
| `godot/scripts/core/game_state.gd` | Core game state and logic |
| `godot/scripts/core/turn_manager.gd` | Turn processing |
| `godot/autoload/event_service.gd` | Event system and historical data |
| `godot/data/actions.json` | Action definitions |
| `godot/data/events.json` | Event definitions |

## Using the Debug Overlay

Press **~** (tilde) in-game to toggle the debug overlay. It has tabs for:

- **Game State**: turn number, resources, doom value, staff, queued actions, events
- **Errors**: error log
- **Performance**: FPS, frame time, memory, draw calls
- **Debug Controls**: add resources, trigger specific events, reset game

This is invaluable for testing and reproducing bugs.

## Running Tests

Tests use the [GUT (Godot Unit Testing)](https://github.com/bitwes/Gut) framework.

### Quick Syntax Check

```bash
godot --headless --path godot --quit
```

### Run Unit Tests

```bash
# Using the Python test runner
python scripts/run_godot_tests.py --quick

# CI mode (exits with status code)
python scripts/run_godot_tests.py --quick --ci-mode
```

### From the Godot Editor

- Open the GUT panel (bottom dock)
- Click "Run All"

## Branch Workflow

We use a two-branch model:

- **`main`** - Stable releases only
- **`develop`** - Active development, all PRs target here

### Making Changes

1. **Fork** the repository on GitHub

2. **Create a feature branch from develop:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-123-description
   ```

3. **Make your changes**
   - Follow existing code patterns
   - Add tests for new functionality
   - Update documentation if needed

4. **Test your changes:**
   ```bash
   godot --headless --path godot --quit  # Syntax check
   python scripts/run_godot_tests.py --quick  # Run tests
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request** targeting `develop` (not main)

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

### QA Testing

We use a structured QA checklist at `QA_CHECKLIST.md`. Look for issues labeled `good first issue` and `qa-testing`.

To contribute via testing:
1. Claim a QA issue by commenting on it
2. Work through the checklist items
3. File separate bug reports for each bug found (using the **QA Bug Report** template)
4. Comment on the QA issue with your results

### New Features

1. Open an issue first to discuss the feature
2. Wait for approval before starting significant work
3. Keep PRs focused - one feature per PR

### Documentation

Documentation improvements are always welcome! Look for:
- Typos and unclear wording
- Missing information
- Outdated instructions

## Filing Bugs

Use the GitHub issue templates:
- **Bug Report**: for general bugs found while playing
- **QA Bug Report**: for bugs found during structured QA testing sessions

Include as much context as possible: game version, platform, steps to reproduce, debug overlay state, and screenshots.

You can also press **\\** (backslash) in-game to open the built-in bug reporter, which automatically captures game state.

## Code Style

### GDScript

Follow the [Godot style guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html):

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

### Python

Python scripts follow PEP 8 (enforced by `ruff` and `black`). Pre-commit hooks enforce formatting.

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/PipFoweraker/pdoom1/discussions)
- **Bugs**: Open an [Issue](https://github.com/PipFoweraker/pdoom1/issues)
- **Feature Ideas**: Open an Issue with the `enhancement` label

## First-Time Contributors

Look for issues labeled [`good first issue`](https://github.com/PipFoweraker/pdoom1/labels/good%20first%20issue). These are specifically scoped for newcomers.

**Good first contributions:**
- QA testing sections (see `qa-testing` label)
- Fix GDScript warnings (issue #506)
- Fix typos in documentation
- Add missing tooltips
- Improve error messages

## Recognition

Contributors are recognized in:
- The in-game credits
- The [CONTRIBUTORS.md](docs/CONTRIBUTORS.md) file
- Our [Contributor Rewards Program](docs/CONTRIBUTOR_REWARDS.md) - submit a photo of your cat!

Thank you for contributing to P(Doom)!

# Contributing to P(Doom)

## Getting Started

### Prerequisites
- [Godot 4.5.1](https://godotengine.org/download/) (standard, not .NET)
- [Python 3.9+](https://python.org) (for build scripts and tooling)
- [Git](https://git-scm.com/)

### Setting Up the Project

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/pdoom1.git
   cd pdoom1
   ```

2. **Install Python dependencies** (for tooling/CI scripts):
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Open the Godot project:**
   - Open Godot 4.5.1
   - Click "Import" and navigate to `godot/project.godot`
   - The project will import assets on first open (this can take a moment)

4. **Run the game:**
   - Press F5 in the Godot editor, or
   - From command line: `godot --path godot`

### Running Tests

Tests use the [GUT (Godot Unit Testing)](https://github.com/bitwes/Gut) framework.

**From the Godot editor:**
- Open the GUT panel (bottom dock)
- Click "Run All"

**From the command line:**
```bash
python scripts/run_godot_tests.py --quick
```

**CI mode (used in GitHub Actions):**
```bash
python scripts/run_godot_tests.py --quick --ci-mode
```

### Using the Debug Overlay

Press **~** (tilde) in-game to toggle the debug overlay. It has tabs for:
- **Game State**: turn, resources, doom, staff, queued actions, events
- **Errors**: error log
- **Performance**: FPS, frame time, memory, draw calls
- **Debug Controls**: add resources, trigger events, reset game

This is invaluable for testing and reproducing bugs.

## Branch Workflow

1. **Fork** the repository
2. Create a **feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Push to your fork and open a **Pull Request** targeting `develop`

The `main` branch contains stable releases. All work goes through `develop` first.

## Filing Bugs

Use the GitHub issue templates:
- **Bug Report**: for general bugs found while playing
- **QA Bug Report**: for bugs found during structured QA testing sessions

Include as much context as possible: game version, platform, steps to reproduce, debug overlay state, and screenshots.

You can also press **\\** (backslash) in-game to open the built-in bug reporter, which automatically captures game state.

## QA Testing

We use a structured QA checklist at `QA_CHECKLIST.md` in the repository root. Look for issues labeled `good first issue` and `qa-testing` for testing tasks.

Each QA issue covers a section of the checklist. To contribute:
1. Claim the issue by commenting on it
2. Work through the checklist items
3. File separate bug report issues for each bug found (using the QA Bug Report template)
4. Comment on the QA issue with your results (items passed, items failed, items untestable)

## Code Style

- GDScript follows the [Godot style guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
- Python scripts follow PEP 8 (enforced by `ruff` and `black`)
- Pre-commit hooks enforce formatting on commit

## What to Work On

- Issues labeled **`good first issue`** are scoped for newcomers
- Issues labeled **`help wanted`** need contributors
- The QA checklist sections are always open for testing
- Check the issue tracker for current priorities

# Godot Development Tools

Development utilities for P(Doom) Godot implementation.

## Tools Overview

### SUCCESS `dev_tool_minimal.gd` - Code Validation Tool (WORKING)

Validates GameState code structure without instantiating it. **This is the recommended tool to use.**

**Why minimal?** Instantiating GameState triggers all autoloads (GameManager, GameConfig, etc.) which prevent clean script exit. The minimal version inspects the code without running it.

**Usage:**

```bash
# Full path (recommended until PATH is fixed)
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" --headless --script tools/dev_tool_minimal.gd

# Run all validations
godot --headless --script tools/dev_tool_minimal.gd

# Run specific validation
godot --headless --script tools/dev_tool_minimal.gd --test exists
godot --headless --script tools/dev_tool_minimal.gd --test methods
godot --headless --script tools/dev_tool_minimal.gd --test properties
```

**What it checks:**
- SUCCESS GameState script exists and loads
- SUCCESS GameState has expected methods
- SUCCESS GameState has expected properties
- SUCCESS Lists all available methods and properties

**Example Output:**
```
[CHECKED] GameState script found: res://scripts/core/game_state.gd
[CHECKED] seed - Found
[CHECKED] turn - Found
[CHECKED] money - Found
[CHECKED] doom - Found
[CHECKED] reputation - Found
```

---

### WARNING `dev_tool_v2.gd` - Runtime Testing (HANGS - DO NOT USE)

This version instantiates GameState to test runtime behavior, but it hangs due to autoload initialization.

**Status:** Does not exit cleanly, requires Ctrl+C to kill
**Issue:** Autoloads (GameManager, etc.) prevent script exit
**Solution:** Use `dev_tool_minimal.gd` instead for validation

---

### WARNING `dev_tool.gd` - Original Full Test Suite (HANGS - DO NOT USE)

Original comprehensive test suite. Has same hanging issue as v2.

**Status:** Archived for reference
**Use instead:** `dev_tool_minimal.gd`

---

### SUCCESS `quick_test.gd` - Basic Functionality Test (WORKING)

Simple test to verify GDScript basics and script loading.

**Usage:**
```bash
godot --headless --script tools/quick_test.gd
```

**What it does:**
- Tests basic GDScript functionality
- Checks for autoloads
- Loads GameState script (but doesn't instantiate)
- Quick validation that environment is working

---

## PATH Issues with Godot

**Problem:** Space in "Program Files" breaks bash PATH

**Temporary Solution (per session):**
```bash
alias godot='"/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"'
```

**Permanent Solution (create wrapper in project root):**
```bash
# Create godot.sh in project root
printf '#!/bin/bash\n"/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" "$@"\n' > ../godot.sh
chmod +x ../godot.sh

# Use it
./godot.sh --headless --script tools/dev_tool_minimal.gd
```

**Best Solution (move Godot):**
```bash
mkdir -p /c/Godot
cp "/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" /c/Godot/godot.exe
export PATH="/c/Godot:$PATH"  # Add to ~/.bashrc
```

---

## Discovered GameState Structure

From validation tool output:

**Methods:**
- `reset()` - Reset game state
- `can_afford(amount)` - Check if player can afford cost

**Properties:**
- `seed` - Game seed
- `turn` - Current turn number
- `money`, `compute`, `research`, `papers` - Resources
- `reputation`, `doom` - Key metrics
- `action_points`, `committed_ap`, `reserved_ap`, `used_event_ap` - Action point tracking
- `safety_researchers`, `capability_researchers`, `compute_engineers`, `managers` - Staff (not single `staff` property)

**Note:** Method names differ from Python version:
- Python: `initialize()`  ->  Godot: `reset()`
- Python: `advance_turn()` / `end_turn()`  ->  Godot: (different implementation)

---

## Development Workflow

### Quick Validation
```bash
cd godot
"/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe" --headless --script tools/dev_tool_minimal.gd
```

### Check Specific Aspect
```bash
# Check methods only
godot --headless --script tools/dev_tool_minimal.gd --test methods

# Check properties only
godot --headless --script tools/dev_tool_minimal.gd --test properties
```

### After Code Changes
```bash
# Validate code structure is intact
godot --headless --script tools/dev_tool_minimal.gd
```

---

## Comparison: Python vs Godot Tools

| Feature | Python (tools/dev_tool.py) | Godot (tools/dev_tool_minimal.gd) |
|---------|---------------------------|-----------------------------------|
| **Status** | SUCCESS Working | SUCCESS Working |
| **Method** | Runtime testing | Static validation |
| **Exit behavior** | Clean | Clean (forced with OS.kill) |
| **Instantiates GameState** | Yes | No (avoids autoload issues) |
| **Tests gameplay** | Yes | No (structure only) |
| **Tests consistency** | Yes (seed parity) | No |
| **Use case** | Full integration testing | Code structure validation |

---

## Future Improvements

### High Priority
1. **Fix autoload hanging issue** - Investigate why autoloads prevent script exit
2. **Create wrapper script** - Permanent solution to PATH problem
3. **Runtime testing** - Get dev_tool_v2.gd working without hanging

### Medium Priority
4. **Seed parity validator** - Compare Python vs Godot results
5. **Integration tests** - Headless full-game simulations
6. **CI/CD integration** - Automate validation in GitHub Actions

### Low Priority
7. **Performance profiling** - Automated benchmarks
8. **Export validation** - Test built executables

---

## Troubleshooting

### Script hangs and won't exit
**Problem:** Instantiating GameState triggers autoloads that don't shut down
**Solution:** Use `dev_tool_minimal.gd` which doesn't instantiate
**Workaround:** Kill with Ctrl+C

### "bash: /c/Program: No such file or directory"
**Problem:** Space in "Program Files" breaks bash
**Solution:** Use full quoted path: `"/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"`
**Or:** Create wrapper script (see PATH Issues section)

### "Could not load GameState script"
**Problem:** Wrong working directory or script path
**Solution:** Run from `godot/` directory: `cd godot`
**Check:** Script is at `res://scripts/core/game_state.gd`

---

## Notes

- All tools work in `--headless` mode (no GUI)
- Exit codes: 0 = success, 1 = failure
- Verbose output by default for debugging
- Tools are deterministic and repeatable

---

## Contributing

When adding new tools:
1. Test exit behavior (`quit(0)` or `OS.kill()`)
2. Add verbose logging
3. Document in this README
4. Avoid instantiating objects with autoload dependencies
5. Prefer validation over runtime testing when possible

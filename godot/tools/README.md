# Godot Development Tools

Development utilities for P(Doom) Godot implementation.

## Tools

### `dev_tool.gd` - Interactive Development Testing

Ported from Python `tools/dev_tool.py`. Provides quick testing and validation of game systems.

**Usage:**

```bash
# Interactive menu (runs all tests)
godot --script tools/dev_tool.gd

# List available tests
godot --script tools/dev_tool.gd --list

# Run specific test
godot --script tools/dev_tool.gd --test game_state
godot --script tools/dev_tool.gd --test seeds
godot --script tools/dev_tool.gd --test leaderboard
godot --script tools/dev_tool.gd --test turn
godot --script tools/dev_tool.gd --test dual
godot --script tools/dev_tool.gd --test session
```

**Available Tests:**

- `game_state` - Test GameState initialization and basic operations
- `seeds` - Test seed variation consistency
- `leaderboard` - Test leaderboard system integration
- `turn` - Test turn progression over multiple turns
- `dual` - Test dual identity system (player + lab names)
- `session` - Test complete game session simulation

**Example Output:**

```
===========================================================
P(Doom) Godot Development Tool
===========================================================
[TEST] Running: game_state
===========================================================
Testing GameState initialization and basic operations...
  Initial State:
    Seed: dev-test-seed
    Turn: 1
    Money: $100000
    Staff: 0
    Reputation: 0.0
    Doom: 80.0%
    Action Points: 3 / 3

  Testing turn advancement...
    Turn advanced: 1 → 2
    Action Points reset: 3

[✓] GameState working correctly
[OK] Test completed: game_state
```

## Comparison with Python Version

| Feature | Python | Godot | Notes |
|---------|--------|-------|-------|
| Interactive Menu | ✓ | ✓ | Godot runs all tests in sequence |
| Game State Tests | ✓ | ✓ | Fully ported |
| Seed Variations | ✓ | ✓ | Includes consistency checks |
| Leaderboard Tests | ✓ | ⚠️ | Depends on Leaderboard autoload |
| Turn Progression | ✓ | ✓ | 10-turn simulation |
| Complete Session | ✓ | ✓ | Full session lifecycle |

## Future Additions

### Seed Parity Validator
Compare Python and Godot implementations for identical behavior:

```bash
godot --script tools/validate_seed_parity.gd --seed "test-123"
```

### Performance Profiler
Automated performance benchmarking:

```bash
godot --script tools/profile_performance.gd --iterations 100
```

### Integration Test Suite
Headless full-game simulations:

```bash
godot --script tools/run_integration_tests.gd --headless
```

## Development Workflow

1. **Make changes to game code**
2. **Run quick validation:**
   ```bash
   godot --script tools/dev_tool.gd --test game_state
   ```
3. **Test specific systems:**
   ```bash
   godot --script tools/dev_tool.gd --test seeds
   ```
4. **Run full test suite:**
   ```bash
   godot --script tools/dev_tool.gd
   ```

## Integration with CI/CD

Add to GitHub Actions workflow:

```yaml
- name: Run Godot Dev Tools
  run: |
    godot --headless --script tools/dev_tool.gd
```

## Notes

- Tools run in `SceneTree` context, not as scenes
- Use `--headless` flag for CI/CD environments
- Exit codes: 0 = success, 1 = failure
- All tests should be deterministic and repeatable

# Baseline Scoring System

> Issue #372: Enhanced scoring with baseline comparison

## Overview

The Baseline Scoring System provides players with meaningful context for their scores by comparing their performance against a "no-action" baseline simulation. This answers the question: "How much did my decisions actually matter?"

## Architecture

### Computation Modes

The system supports three computation modes to balance performance and user experience:

| Mode | When Used | Computation | Delay |
|------|-----------|-------------|-------|
| **PRECOMPUTED** | Weekly League | Server-side, stored with seed | Zero |
| **EAGER** | Custom Games (default) | Background thread at game start | None visible |
| **BLIND** | Fallback | Synchronous at game end | 0.5-2 seconds |

### Mode Selection Logic

```
Weekly League (empty seed) + Auto mode -> PRECOMPUTED
Custom Game + Auto/Eager mode -> EAGER (background thread)
Blind mode selected -> BLIND (on-demand)
```

## Components

### BaselineSimulator (`godot/scripts/core/baseline_simulator.gd`)

The core simulation engine that runs headless games with no player actions.

**Key Functions:**

```gdscript
# Set precomputed baseline (weekly league)
BaselineSimulator.set_precomputed_baseline(seed, {
    "score": 85000,
    "turns": 47,
    "victory": false,
    "doom": 100.0
})

# Start background simulation (eager mode)
BaselineSimulator.start_background_simulation(game_seed)

# Check if baseline is ready
if BaselineSimulator.is_baseline_ready(game_seed):
    var result = BaselineSimulator.get_baseline_score(game_seed)

# Get baseline (handles all modes automatically)
var baseline = BaselineSimulator.get_baseline_score(game_seed)
# Returns: {score, final_state, turns, victory, doom, simulation_time_ms}
```

### GameConfig Settings (`godot/autoload/game_config.gd`)

```gdscript
# baseline_mode values:
# 0 = Auto (precomputed for weekly, eager for custom)
# 1 = Eager (always compute at game start)
# 2 = Blind (always compute on-demand at end)

GameConfig.baseline_mode = 0  # Default: Auto

# Helper functions
GameConfig.should_use_precomputed_baseline()  # true for weekly league
GameConfig.should_start_background_baseline()  # true for custom games
GameConfig.get_baseline_mode_string()  # "Auto", "Eager", or "Blind"
```

### Integration Points

**GameManager** (`godot/scripts/game_manager.gd`):
- Starts background baseline at game initialization (if appropriate)

**GameOverScreen** (`godot/scripts/ui/game_over_screen.gd`):
- Retrieves baseline score via `get_baseline_score()`
- Displays comparison text and percentage

**Leaderboard** (`godot/scripts/leaderboard.gd`):
- Stores `baseline_score` with each entry
- Enables historical comparison

## Baseline Event Strategy

When the baseline simulation encounters events, it must make choices. The strategy is documented and extensible.

### Philosophy

The baseline represents a **passive player** who:
- Takes no deliberate actions (no hiring, no research, no upgrades)
- Must respond to mandatory events
- Chooses the "neutral/safe" option when forced

### Current Strategy

**Default behavior:** Always pick the first choice (index 0).

This works because events should be designed with choices ordered by passivity:
1. First choice = most neutral/safe/passive option
2. Later choices = more active/risky options

### Extending the Strategy

To add special handling for specific events, modify `_get_event_choice_for_baseline()`:

```gdscript
static func _get_event_choice_for_baseline(event: Dictionary, choices: Array) -> String:
    var event_id = event.get("id", "")

    # Example: Always cooperate with regulators
    if event_id == "regulatory_investigation":
        for choice in choices:
            if choice.get("id", "") == "cooperate":
                return choice.get("id", "")

    # Example: Never accept risky investments
    if event_id == "venture_capital_offer":
        for choice in choices:
            if choice.get("id", "") == "decline":
                return choice.get("id", "")

    # Default: first choice
    return choices[0].get("id", "") if choices.size() > 0 else ""
```

### Event Design Guidelines

When creating events, order choices to support baseline comparison:

```json
{
  "id": "media_interview_request",
  "choices": [
    {"id": "decline", "text": "Politely decline"},      // Index 0: Passive (baseline picks this)
    {"id": "accept", "text": "Accept interview"},        // Index 1: Active
    {"id": "exclusive", "text": "Offer exclusive access"} // Index 2: Aggressive
  ]
}
```

## Weekly League Integration

For weekly leagues, baselines should be precomputed server-side when generating the seed:

### Server-Side Computation

```python
# When generating weekly seed
def generate_weekly_league(week_number):
    seed = f"weekly-2025-w{week_number}"

    # Run baseline simulation server-side
    baseline_result = run_baseline_simulation(seed)

    return {
        "seed": seed,
        "baseline": {
            "score": baseline_result.score,
            "turns": baseline_result.turns,
            "victory": baseline_result.victory,
            "doom": baseline_result.final_doom
        }
    }
```

### Client-Side Usage

```gdscript
# When loading weekly league data
func load_weekly_league(league_data: Dictionary):
    var seed = league_data["seed"]
    var baseline = league_data["baseline"]

    # Set precomputed baseline before game starts
    BaselineSimulator.set_precomputed_baseline(seed, baseline)

    # Start game - baseline already available
    game_manager.start_new_game(seed)
```

## Performance Characteristics

### Simulation Time

| Game Length | Typical Time | Notes |
|-------------|--------------|-------|
| 20 turns | ~200ms | Early defeat |
| 50 turns | ~500ms | Standard game |
| 100 turns | ~1.5s | Long game |
| 200 turns | ~3s | Maximum (capped) |

### Memory Usage

- Single GameState object (~10KB)
- TurnManager instance (~5KB)
- Result cache per seed (~1KB)

### Threading

- Background simulation uses Godot's Thread class
- Falls back to synchronous on single-threaded platforms
- Thread-safe static cache

## Score Comparison Display

The system provides formatted comparison text:

```gdscript
var comparison = BaselineSimulator.get_comparison_text(player_score, baseline_score)
# Returns: {text, color, percentage, difference}

# Example outputs:
# "+45000 points (52% better than baseline!)" - Bright green
# "+12000 points (15% better)" - Light green
# "-8000 points (10% below baseline)" - Orange
# "Matched baseline exactly!" - Yellow
```

### Color Coding

| Performance | Color | Meaning |
|-------------|-------|---------|
| +100% or more | Bright Green | Exceptional |
| +50% to +99% | Green | Great |
| +1% to +49% | Light Green | Good |
| Exactly 0% | Yellow | Matched baseline |
| -1% to -49% | Orange | Below average |
| -50% or worse | Red | Poor |

## Testing

### Clear Cache for Testing

```gdscript
# Reset all baseline state
BaselineSimulator.clear_cache()
```

### Verify Baseline Computation

```gdscript
# Run baseline and log results
var result = BaselineSimulator.get_baseline_score("test-seed")
print("Baseline score: %d" % result.score)
print("Turns survived: %d" % result.turns)
print("Final doom: %.1f%%" % result.doom)
print("Computation time: %dms" % result.simulation_time_ms)
```

## Future Considerations

### Difficulty-Specific Baselines

Currently, baselines don't account for difficulty settings. Future enhancement:

```gdscript
# Key could include difficulty
var cache_key = "%s-%s" % [game_seed, difficulty_string]
```

### Scenario-Specific Baselines

Scenarios with custom starting conditions may need separate baselines:

```gdscript
# Key could include scenario
var cache_key = "%s-%s" % [game_seed, scenario_id]
```

### Analytics

Baseline comparisons could feed into analytics:
- Average player performance vs baseline
- Which events most impact baseline divergence
- Skill progression over time

## Related Documentation

- [SCORING_SYSTEM_PROPOSAL.md](SCORING_SYSTEM_PROPOSAL.md) - Overall scoring design
- [LEADERBOARD_BACKEND_ARCHITECTURE.md](LEADERBOARD_BACKEND_ARCHITECTURE.md) - Backend integration
- [SCENARIOS.md](SCENARIOS.md) - Scenario system (affects baselines)

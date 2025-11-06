# Error Handling Quick Reference

## TL;DR

- **Press F3** to toggle Debug Overlay
- **ErrorHandler** is available globally in all GDScript files
- **Validate before acting** to catch issues early

## Common Patterns

### 1. Validate Input
```gdscript
func process_action(action_id: String):
    # Validate action_id is not empty
    if not ErrorHandler.validate(
        action_id != "",
        ErrorHandler.Category.ACTIONS,
        "Action ID cannot be empty"
    ):
        return  # Validation failed, error logged

    # Continue with logic...
```

### 2. Report Errors with Context
```gdscript
func buy_item(item: String, cost: int):
    if money < cost:
        ErrorHandler.error(
            ErrorHandler.Category.RESOURCES,
            "Cannot afford item",
            {
                "item": item,
                "cost": cost,
                "current_money": money
            }
        )
        return
```

### 3. Log Successful Operations
```gdscript
func complete_research():
    papers += 1
    ErrorHandler.info(
        ErrorHandler.Category.GAME_STATE,
        "Research completed successfully",
        {"papers": papers}
    )
```

### 4. Warn About Recoverable Issues
```gdscript
func apply_doom_change(change: float):
    doom += change
    if doom > 80:
        ErrorHandler.warning(
            ErrorHandler.Category.GAME_STATE,
            "Doom approaching critical threshold",
            {"doom": doom, "change": change}
        )
```

## Error Severity Guidelines

| Severity | When to Use |
|----------|-------------|
| `INFO` | Successful operations, state transitions |
| `WARNING` | Unexpected but recoverable situations |
| `ERROR` | Invalid operations that block gameplay |
| `FATAL` | Critical errors requiring game restart |

## Error Categories

| Category | Usage |
|----------|-------|
| `GAME_STATE` | Game lifecycle, state validation |
| `RESOURCES` | Money, compute, research, etc. |
| `ACTIONS` | Action selection and execution |
| `EVENTS` | Event triggering and resolution |
| `TURN` | Turn management and processing |
| `SAVE_LOAD` | Game persistence |
| `CONFIG` | Configuration and settings |
| `VALIDATION` | General input validation |

## Debug Overlay Shortcuts

| Key | Action |
|-----|--------|
| **F3** | Toggle Debug Overlay |

### Tabs

1. **Game State**: View resources, staff, events, rivals
2. **Errors**: Recent errors with context
3. **Performance**: FPS, memory, rendering stats
4. **Controls**: Debug cheats and tools

### Debug Controls

- **Add $50k Money**: Instant cash injection for testing
- **Add 5 Action Points**: Extra AP to test action queuing
- **Trigger Random Event**: Force event spawn
- **Skip Turn**: Fast-forward gameplay
- **Reset Game**: Quick restart

## Best Practices

### ✅ DO

```gdscript
// DO: Validate before acting
if not ErrorHandler.validate(state != null, ErrorHandler.Category.GAME_STATE, "State is null"):
    return

// DO: Provide rich context
ErrorHandler.error(
    ErrorHandler.Category.RESOURCES,
    "Insufficient resources",
    {"required": 100, "available": money}
)

// DO: Use appropriate severity
ErrorHandler.warning(...)  // For recoverable issues
ErrorHandler.error(...)    // For blocking issues
```

### ❌ DON'T

```gdscript
// DON'T: Use generic messages
ErrorHandler.error(ErrorHandler.Category.ACTIONS, "Error")  // Too vague!

// DON'T: Skip validation
money -= cost  // What if money < cost?

// DON'T: Use wrong severity
ErrorHandler.fatal(...)  // Unless game truly cannot continue

// DON'T: Log in hot paths
func _process(delta):
    ErrorHandler.info(...)  // Will spam 60 times per second!
```

## Quick Troubleshooting

### "ErrorHandler not found"
- **Cause**: Autoload not registered
- **Fix**: Check `project.godot` has `ErrorHandler="*res://autoload/error_handler.gd"`

### "Debug Overlay not appearing"
- **Cause**: F3 not mapped or scene not instantiated
- **Fix**: Ensure debug_overlay.tscn is added to main scene tree

### "Too many errors"
- **Cause**: Validation failing in loop
- **Fix**: Open Debug Overlay → Errors tab to see pattern

### "Performance degradation"
- **Cause**: Debug Overlay refresh rate too high
- **Fix**: Increase refresh rate slider (2-5 seconds)

## Examples from Codebase

### GameManager: Action Selection
```gdscript
func select_action(action_id: String):
    // Validation: Game initialized
    if not is_initialized:
        var err = ErrorHandler.error(
            ErrorHandler.Category.ACTIONS,
            "Cannot select action: Game not initialized",
            {"action_id": action_id}
        )
        error_occurred.emit(err.message)
        return

    // Validation: Sufficient AP
    if state.action_points < ap_cost:
        var err = ErrorHandler.warning(
            ErrorHandler.Category.RESOURCES,
            "Insufficient action points",
            {
                "action_id": action_id,
                "required": ap_cost,
                "available": state.action_points
            }
        )
        error_occurred.emit(...)
        return
```

### GameState: Spend Resources
```gdscript
func spend_resources(costs: Dictionary):
    // Validate affordability first
    if not can_afford(costs):
        ErrorHandler.error(
            ErrorHandler.Category.RESOURCES,
            "Attempted to spend unaffordable resources",
            {"costs": costs, "current": {...}}
        )
        return

    // Spend and validate results
    money -= costs.get("money", 0)
    if money < 0:
        ErrorHandler.warning(
            ErrorHandler.Category.RESOURCES,
            "Money went negative",
            {"money": money}
        )
```

## Error Log Export

### Via Debug Overlay
1. Press F3
2. Go to Controls tab
3. (Future: Export button)

### Via Code
```gdscript
# Export to file
ErrorHandler.save_error_log_to_file("user://debug_log.txt")

# Get as string
var log = ErrorHandler.export_error_log()
print(log)

# Get statistics
var stats = ErrorHandler.get_error_stats()
print("Total errors: %d" % stats["total"])
```

## Integration with Testing

```gdscript
# In test files (GUT framework)
func test_action_validation():
    # Clear error history before test
    ErrorHandler.clear_history()

    # Perform action that should fail
    game_manager.select_action("invalid_action")

    # Check error was reported
    var errors = ErrorHandler.get_recent_errors(1)
    assert_eq(errors.size(), 1, "Should have 1 error")
    assert_eq(errors[0].category, ErrorHandler.Category.ACTIONS)
```

## Performance Notes

- **ErrorHandler**: ~0.1-0.3ms per error report (negligible)
- **Debug Overlay** (hidden): ~0ms (only input check)
- **Debug Overlay** (visible): ~0.5-2ms (depends on refresh rate)
- **Validation**: ~0.01-0.05ms per check (negligible)

**Recommendation**: Use liberally during development, keep in production builds (minimal overhead).

---

**Quick Tips**:
1. Always validate input before processing
2. Provide context - future you will thank present you
3. Use appropriate severity levels
4. Press F3 when something seems wrong
5. Check Errors tab first when debugging

**Questions?** See `OPTION_E_ERROR_HANDLING_COMPLETE.md` for full documentation.

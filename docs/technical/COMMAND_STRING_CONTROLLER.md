# Command String Controller - Deterministic P(Doom) Strategy System

The Command String Controller provides a simple, ASCII-only interface for controlling P(Doom) gameplay using abbreviated command strings. This enables deterministic strategy execution, testing automation, and easy strategy sharing between players.

## Quick Start

```bash
# Test the command system
python test_command_strings.py

# Run a simple strategy
python command_string_example.py "H F S T" my-seed

# Show available commands and examples
python command_string_example.py
```

## Command Reference

### Single-Letter Commands
- **T** = End Turn (advance turn)
- **H** = Hire Staff 
- **F** = Fundraise
- **S** = Safety Research
- **C** = Buy Compute
- **R** = Research Options (menu)
- **G** = Grow Community
- **I** = Intelligence (scout opponents)
- **E** = Espionage (advanced intelligence)
- **U** = Upgrade (specify which upgrade)
- **P** = Press Release
- **N** = Networking
- **M** = Monitoring Systems
- **A** = Conduct Audit
- **L** = Lobbying
- **D** = Data Analysis
- **O** = Outreach Program

### Repetition Syntax
Use `*` followed by a number (1-99) to repeat commands:
- `H*3` = Hire staff 3 times
- `T*5` = End turn 5 times
- `F*2 S*3` = Fundraise twice, then safety research 3 times

### Command String Format
Commands are separated by spaces:
```
"T H F S T"           # Basic sequence
"H*3 F*2 S T"         # With repetition
"F S C T H I T"       # Mixed strategy
```

## Example Strategies

### Early Game Strategies
```
"H*2 F*3 T"           # Early Economy: Build staff and funding
"F S*3 C T H S"       # Research Focus: Prioritize safety early
"H F S C T*2 H F"     # Balanced Growth: Steady progression
```

### Specialized Strategies
```
"I*3 E H F S T"       # Intelligence Heavy: Scout opponents first
"G*2 P N H F T"       # Community Building: Focus on reputation
"T*10"                # Speed Run: Skip to turn 10 quickly
```

### Advanced Strategies
```
"H*5 F*3 S*2 C U T"   # Resource Buildup: Mass hiring and funding
"F S C H I E T*3"     # Information Warfare: Intelligence then coast
"G P N L A M T"       # Governance Focus: Political and audit actions
```

## Deterministic Execution

With the same seed and command string, execution is 100% deterministic:
- All random events occur in identical order
- Opponent actions are exactly the same
- Resource changes are identical
- Perfect for strategy validation and sharing

```python
# These will produce identical results every time
controller.execute_command_string("H*3 F*2 S T", "fixed-seed-123")
controller.execute_command_string("H*3 F*2 S T", "fixed-seed-123")
```

## Programmatic Usage

### Basic Controller Setup
```python
from src.testing.command_string_controller import CommandStringController
from src.core.game_state import GameState

# Create game state
game_state = GameState("my-seed-123")

# Create controller
controller = CommandStringController(game_state)

# Execute strategy
report = controller.execute_command_string("H F S T", "my-seed-123")

print(f"Executed {report.total_commands} commands")
print(f"Success rate: {report.successful_commands}/{report.total_commands}")
```

### Validation Before Execution
```python
from src.testing.command_string_controller import CommandStringParser

parser = CommandStringParser()

# Validate command string
is_valid, message = parser.validate_command_string("H*3 F*2 S T")
if is_valid:
    print("Command string is valid!")
    expanded = parser.expand_command_string("H*3 F*2 S T")
    print(f"Will execute {len(expanded)} commands: {expanded}")
else:
    print(f"Invalid command string: {message}")
```

### Detailed Execution Reports
```python
# Execute and get detailed report
report = controller.execute_command_string("H F S T", "test-seed")

# Access execution details
print(f"Total execution time: {report.total_execution_time_ms:.1f}ms")
print(f"Final turn: {report.final_turn}")

# Check individual command results
for result in report.command_results:
    if not result.success:
        print(f"Failed: {result.command} - {result.message}")

# Save report to file
report.save_to_file("strategy_report.json")
```

## ASCII-Only Design

All commands and content use standard ASCII characters for maximum compatibility:
- PASS Works in all text editors and terminals
- PASS Copy-paste friendly across all platforms
- PASS No Unicode or special character dependencies
- PASS Safe for configuration files and documentation

## Integration with Existing Code

### Adding New Commands
To add a new command (e.g., 'W' for Whistleblowing):

1. **Add to COMMAND_MAP** in `CommandStringParser`:
```python
COMMAND_MAP = {
    # ... existing commands ...
    'W': 'whistleblowing',
}
```

2. **Add description**:
```python
descriptions = {
    # ... existing descriptions ...
    'W': 'Whistleblowing - Report safety violations',
}
```

3. **Add handler** in `CommandStringController`:
```python
def _dispatch_command(self, cmd_letter: str) -> Tuple[bool, str]:
    # ... existing handlers ...
    elif cmd_letter == 'W':
        return self._whistleblowing()

def _whistleblowing(self) -> Tuple[bool, str]:
    return self._find_and_execute_action(['whistleblow'], "Whistleblowing")
```

### Error Handling
The system handles various error conditions gracefully:
- Invalid command letters
- Invalid repetition counts
- Game state errors
- Action availability issues
- Unexpected exceptions

All errors are captured in the execution report for debugging.

## Testing Infrastructure

### Automated Validation
```bash
# Run full command system tests
python test_command_strings.py

# Expected output: All tests PASSED!
```

### Manual Testing
```bash
# Test basic functionality
python command_string_example.py

# Test specific strategies
python command_string_example.py "H*2 F S T" test-strategy-1
python command_string_example.py "I*3 E T" intelligence-test
```

### Integration Testing
The command system integrates with existing P(Doom) testing infrastructure:
- Uses existing `GameState` class
- Respects game action availability
- Follows turn-based mechanics
- Captures all state changes

## File Structure
- `src/testing/command_string_controller.py` - Main controller implementation
- `test_command_strings.py` - Automated test suite
- `command_string_example.py` - Integration examples and demos
- `COMMAND_STRING_CONTROLLER.md` - This documentation file

## Performance Characteristics
- Command parsing: <1ms for typical strings
- Command execution: 0.5-2ms per command
- Report generation: <5ms for complete reports
- Memory usage: Minimal overhead over base game state

## Future Enhancements
- Visual command builder UI
- Strategy tournament automation
- Command string optimizer
- Interactive strategy debugger
- Community strategy repository

---

*The Command String Controller enables "HFS*FCS" style deterministic strategy execution, making P(Doom) strategies shareable via simple text strings that execute identically across all installations.*

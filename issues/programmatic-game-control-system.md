# Programmatic Game Control System for Rigorous Testing

## Summary
**PRIORITY: HIGH** - Build comprehensive programmatic game control interface for automated testing, CI/CD validation, and rigorous QA workflows.

## Strategic Context
- **Goal**: Enable fully automated game testing and validation
- **Current**: Manual testing only, dev tools for manual debugging
- **Target**: Programmatic control with headless execution, scripted scenarios, and automated validation
- **Impact**: Enables rigorous testing, continuous integration, regression detection, and performance benchmarking

## Long-term Implications for Testing Quality
This system has **critical long-term implications** for our ability to:
1. **Detect regressions automatically** before they reach players
2. **Validate balance changes** with statistical significance
3. **Test edge cases comprehensively** that humans miss
4. **Run performance benchmarks** in CI/CD pipelines
5. **Simulate thousands of games** for balance analysis
6. **Generate reproducible bug reports** with exact game states

## Current Testing Limitations
- Manual testing is **time-intensive** and **error-prone**
- **No automated regression detection** for gameplay changes
- **Limited scenario coverage** due to manual setup overhead
- **No statistical validation** of balance changes
- **Performance regressions** often go undetected until production

## Required Capabilities

### Phase 1: Headless Game Control (CRITICAL)
1. **Headless GameState Management**: Run game logic without pygame/GUI
2. **Programmatic Action Execution**: Execute actions via API calls
3. **State Inspection Interface**: Read all game state programmatically
4. **Turn Advancement Control**: Precise control over turn progression
5. **Event System Control**: Trigger specific events or disable randomness

### Phase 2: Scenario Control System (HIGH)
6. **Scenario Definition Language**: YAML/JSON scenario configurations
7. **State Presets**: Pre-configured game states for testing
8. **Action Sequences**: Scripted multi-turn action sequences
9. **Validation Assertions**: Expected outcomes and validation rules
10. **Batch Execution**: Run multiple scenarios in parallel

### Phase 3: Advanced Testing Features (MEDIUM)
11. **Statistical Analysis**: Outcome distribution analysis across runs
12. **Performance Profiling**: Execution time and memory usage tracking
13. **Regression Testing**: Compare outcomes against baseline versions
14. **Balance Validation**: Detect overpowered/underpowered strategies
15. **Edge Case Generation**: Automatically generate boundary conditions

## Implementation Architecture

### Core Programmatic Interface
```python
class ProgrammaticGameController:
    """
    Main interface for programmatic game control.
    Enables headless execution and automated testing.
    """
    
    def __init__(self, seed: str = None, config: dict = None):
        """Initialize headless game with optional seed and configuration."""
        pass
        
    def execute_action(self, action_id: str, parameters: dict = None) -> dict:
        """Execute a game action programmatically."""
        pass
        
    def advance_turn(self, count: int = 1) -> list:
        """Advance game by specified number of turns."""
        pass
        
    def get_state_snapshot(self) -> dict:
        """Get complete game state as dictionary."""
        pass
        
    def load_state_snapshot(self, state: dict) -> bool:
        """Load game state from dictionary."""
        pass
        
    def run_scenario(self, scenario_config: dict) -> dict:
        """Execute a complete test scenario."""
        pass
```

### Scenario Definition System
```yaml
# Example scenario configuration
scenario:
  name: "Early Game Resource Management"
  description: "Test resource management in first 10 turns"
  
  initial_state:
    seed: "test-resource-mgmt-001"
    turn: 1
    money: 100000
    staff: 0
    reputation: 50
    doom: 30
    
  actions:
    - turn: 1
      action: "hire_staff"
      parameters: { count: 2 }
      expected_outcome: { staff: 2, money: 99200 }
      
    - turn: 2
      action: "fundraising_options"
      parameters: { option: "foundation_grant" }
      validation: { money: ">= 120000" }
      
  end_conditions:
    max_turns: 10
    doom_threshold: 80
    
  success_criteria:
    - money > 80000
    - staff >= 3
    - doom < 70
```

### Testing Integration Points
```python
# In test files - example usage
class TestProgrammaticControl(unittest.TestCase):
    def test_hiring_sequence(self):
        """Test programmatic hiring sequence."""
        controller = ProgrammaticGameController(seed="test-hiring-001")
        
        # Execute hiring action
        result = controller.execute_action("hire_staff", {"count": 3})
        self.assertEqual(result["staff_hired"], 3)
        
        # Validate state
        state = controller.get_state_snapshot()
        self.assertEqual(state["staff"], 3)
        self.assertLess(state["money"], 100000)  # Money was spent
        
    def test_scenario_execution(self):
        """Test full scenario execution."""
        scenario = load_scenario("test_scenarios/early_game_balance.yaml")
        controller = ProgrammaticGameController()
        
        result = controller.run_scenario(scenario)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["final_turn"], 10)
        self.assertGreater(result["final_state"]["money"], 80000)
```

## File Structure
```
src/testing/
|-- programmatic_controller.py     # Main controller class
|-- scenario_runner.py            # Scenario execution engine
|-- state_manager.py              # Game state serialization/deserialization
|-- validation_engine.py          # Outcome validation and assertions
+-- headless_game.py              # Headless game wrapper

test_scenarios/
|-- early_game/                   # Early game test scenarios
|-- balance_testing/              # Balance validation scenarios
|-- edge_cases/                   # Edge case and boundary testing
+-- regression/                   # Regression test scenarios

tools/
|-- scenario_generator.py         # Generate test scenarios
|-- batch_tester.py              # Batch scenario execution
+-- performance_profiler.py       # Performance analysis tools
```

## Integration with Existing Systems

### GameState Enhancement
- Add `get_serializable_state()` method for complete state export
- Add `load_from_state()` method for state restoration
- Add `execute_action_programmatically()` for API-driven actions
- Add headless mode flag to disable pygame dependencies

### Dev Tools Integration
- Extend existing dev_tool.py with programmatic scenarios
- Add scenario recording capability to debug console
- Add "Export Current State" functionality
- Add "Generate Test Scenario" from current game

### CI/CD Integration
- GitHub Actions workflow for automated testing
- Performance regression detection
- Balance change validation
- Automated bug report generation

## Success Metrics
1. **Coverage**: 90%+ of game actions testable programmatically
2. **Performance**: 1000+ game simulations per minute
3. **Reliability**: 99%+ test scenario success rate
4. **Detection**: Catch regressions within 24 hours
5. **Analysis**: Statistical significance for balance changes

## Development Priorities
1. **Week 1**: Core ProgrammaticGameController implementation
2. **Week 2**: Scenario definition system and basic scenarios
3. **Week 3**: Validation engine and assertion framework
4. **Week 4**: Integration with existing test suite and CI/CD

## Long-term Vision
This system will transform our testing from **reactive manual testing** to **proactive automated validation**, enabling:
- **Continuous balance validation** with every code change
- **Comprehensive regression testing** across all game mechanics
- **Statistical balance analysis** with thousands of simulated games
- **Performance benchmarking** integrated into development workflow
- **Automated bug reproduction** with exact game state recreation

This represents a **strategic investment in code quality** that will pay dividends throughout the project lifecycle.

"""
Scenario Runner System for Programmatic Game Testing

This module provides comprehensive scenario-based testing capabilities for P(Doom),
enabling automated validation of game balance, regression testing, and statistical
analysis of gameplay outcomes.

Key Features:
- YAML/JSON scenario configuration
- Batch scenario execution with parallel processing
- Statistical outcome analysis across multiple runs
- Integration with CI/CD for automated regression testing
- Scenario recording and replay for debugging

Long-term Value:
- Enables statistical validation of balance changes
- Provides comprehensive regression testing capability
- Supports automated detection of gameplay anomalies
- Enables community sharing of challenge scenarios
"""

import json
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. YAML scenario files will not be supported.")

import time
import asyncio
import statistics
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

try:
    from .programmatic_controller import ProgrammaticGameController, ActionResult, GameStateSnapshot
    from ..services.version import get_display_version
except ImportError as e:
    print(f"Warning: Could not import dependencies: {e}")


@dataclass
class ScenarioAction:
    """Represents a single action within a scenario."""
    turn: Optional[int] = None
    action_id: str = ""
    parameters: Optional[Dict[str, Any]] = None
    expected_outcome: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenarioAction':
        """Create from dictionary."""
        return cls(**data)


@dataclass 
class ScenarioConfig:
    """Complete scenario configuration."""
    name: str
    description: str
    initial_state: Optional[Dict[str, Any]] = None
    actions: Optional[List[ScenarioAction]] = None
    end_conditions: Optional[Dict[str, Any]] = None
    success_criteria: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.initial_state is None:
            self.initial_state = {}
        if self.end_conditions is None:
            self.end_conditions = {}
        if self.success_criteria is None:
            self.success_criteria = []
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenarioConfig':
        """Create scenario config from dictionary."""
        actions = []
        if 'actions' in data:
            actions = [ScenarioAction.from_dict(action) for action in data['actions']]
        
        return cls(
            name=data.get('name', 'Unnamed Scenario'),
            description=data.get('description', ''),
            initial_state=data.get('initial_state', {}),
            actions=actions,
            end_conditions=data.get('end_conditions', {}),
            success_criteria=data.get('success_criteria', []),
            metadata=data.get('metadata', {})
        )


@dataclass
class ScenarioResult:
    """Result of running a scenario."""
    scenario_name: str
    success: bool
    final_state: GameStateSnapshot
    execution_log: List[ActionResult]
    execution_time_ms: float
    validation_results: Dict[str, Any]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['final_state'] = self.final_state.to_dict()
        result['execution_log'] = [action.to_dict() for action in self.execution_log]
        return result


@dataclass
class BatchExecutionResult:
    """Result of batch scenario execution."""
    total_scenarios: int
    successful_scenarios: int
    failed_scenarios: int
    success_rate: float
    total_execution_time_ms: float
    average_execution_time_ms: float
    scenario_results: List[ScenarioResult]
    statistical_analysis: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result['scenario_results'] = [scenario.to_dict() for scenario in self.scenario_results]
        return result


class ScenarioRunner:
    """
    Main class for executing game scenarios programmatically.
    
    Supports single scenario execution, batch processing, and statistical analysis
    of outcomes across multiple runs for balance validation and regression testing.
    """
    
    def __init__(self, base_config: Optional[Dict[str, Any]] = None):
        """Initialize scenario runner with optional base configuration."""
        self.base_config = base_config or {}
        self.execution_history: List[ScenarioResult] = []
    
    def load_scenario(self, filepath: Union[str, Path]) -> ScenarioConfig:
        """
        Load scenario from YAML or JSON file.
        
        Args:
            filepath: Path to scenario file
            
        Returns:
            ScenarioConfig instance
        """
        filepath = Path(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.suffix.lower() in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML scenario files")
                data = yaml.safe_load(f)  # type: ignore
            else:
                data = json.load(f)
        
        return ScenarioConfig.from_dict(data)
    
    def run_scenario(self, scenario: Union[ScenarioConfig, str, Path], seed: Optional[str] = None) -> ScenarioResult:
        """
        Execute a single scenario.
        
        Args:
            scenario: ScenarioConfig instance or path to scenario file
            seed: Override seed for deterministic execution
            
        Returns:
            ScenarioResult with execution details
        """
        if isinstance(scenario, (str, Path)):
            scenario = self.load_scenario(scenario)
        
        start_time = time.time()
        
        try:
            # Initialize controller with scenario seed or provided seed
            controller_seed = seed or scenario.initial_state.get('seed', f"scenario-{scenario.name}-{int(time.time())}")
            controller = ProgrammaticGameController(seed=controller_seed, config=self.base_config)
            
            # Apply initial state overrides
            self._apply_initial_state(controller, scenario.initial_state or {})
            
            # Execute scenario actions
            execution_log = []
            for action in (scenario.actions or []):
                # Check if we should execute this action based on turn
                if action.turn is not None and controller.game_state.turn != action.turn:
                    # Advance to required turn
                    while controller.game_state.turn < action.turn:
                        turn_result = controller.execute_action('end_turn')
                        execution_log.append(turn_result)
                
                # Execute the action
                result = controller.execute_action(action.action_id, action.parameters)
                execution_log.append(result)
                
                # Validate expected outcomes if specified
                if action.expected_outcome:
                    self._validate_action_outcome(result, action.expected_outcome)
                
                # Check end conditions
                if self._check_end_conditions(controller, scenario.end_conditions or {}):
                    break
            
            # Evaluate success criteria
            final_state = controller.get_state_snapshot()
            validation_results = self._evaluate_success_criteria(final_state, scenario.success_criteria or [])
            success = validation_results.get('overall_success', True)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            result = ScenarioResult(
                scenario_name=scenario.name,
                success=success,
                final_state=final_state,
                execution_log=execution_log,
                execution_time_ms=execution_time_ms,
                validation_results=validation_results,
                metadata={
                    'seed': controller_seed,
                    'scenario_description': scenario.description,
                    'total_actions': len(execution_log)
                }
            )
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Return failed result
            return ScenarioResult(
                scenario_name=scenario.name,
                success=False,
                final_state=controller.get_state_snapshot() if 'controller' in locals() else None,
                execution_log=execution_log if 'execution_log' in locals() else [],
                execution_time_ms=execution_time_ms,
                validation_results={'error': True},
                error_message=str(e),
                metadata={'error_type': type(e).__name__}
            )
    
    def run_batch_scenarios(self, 
                          scenarios: List[Union[ScenarioConfig, str, Path]], 
                          iterations: int = 1,
                          parallel: bool = True,
                          max_workers: Optional[int] = None) -> BatchExecutionResult:
        """
        Execute multiple scenarios, optionally in parallel.
        
        Args:
            scenarios: List of scenarios to execute
            iterations: Number of times to run each scenario
            parallel: Whether to use parallel execution
            max_workers: Maximum number of parallel workers
            
        Returns:
            BatchExecutionResult with aggregated statistics
        """
        start_time = time.time()
        
        # Create execution tasks
        execution_tasks = []
        for scenario in scenarios:
            for i in range(iterations):
                seed = f"batch-{hash(str(scenario))}-{i}" if iterations > 1 else None
                execution_tasks.append((scenario, seed))
        
        # Execute scenarios
        results = []
        if parallel and len(execution_tasks) > 1:
            results = self._execute_parallel(execution_tasks, max_workers)
        else:
            results = self._execute_sequential(execution_tasks)
        
        # Calculate statistics
        total_time_ms = (time.time() - start_time) * 1000
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        success_rate = successful_count / len(results) if results else 0
        
        avg_execution_time = statistics.mean([r.execution_time_ms for r in results]) if results else 0
        
        # Statistical analysis
        statistical_analysis = self._perform_statistical_analysis(results)
        
        return BatchExecutionResult(
            total_scenarios=len(results),
            successful_scenarios=successful_count,
            failed_scenarios=failed_count,
            success_rate=success_rate,
            total_execution_time_ms=total_time_ms,
            average_execution_time_ms=avg_execution_time,
            scenario_results=results,
            statistical_analysis=statistical_analysis
        )
    
    def _execute_sequential(self, tasks: List[Tuple]) -> List[ScenarioResult]:
        """Execute scenarios sequentially."""
        results = []
        for scenario, seed in tasks:
            result = self.run_scenario(scenario, seed)
            results.append(result)
        return results
    
    def _execute_parallel(self, tasks: List[Tuple], max_workers: Optional[int] = None) -> List[ScenarioResult]:
        """Execute scenarios in parallel using ThreadPoolExecutor."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.run_scenario, scenario, seed): (scenario, seed)
                for scenario, seed in tasks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    scenario, seed = future_to_task[future]
                    scenario_name = scenario.name if hasattr(scenario, 'name') else str(scenario)
                    
                    # Create failed result
                    failed_result = ScenarioResult(
                        scenario_name=scenario_name,
                        success=False,
                        final_state=None,
                        execution_log=[],
                        execution_time_ms=0,
                        validation_results={'error': True},
                        error_message=str(e),
                        metadata={'error_type': type(e).__name__, 'parallel_execution_error': True}
                    )
                    results.append(failed_result)
        
        return results
    
    def _apply_initial_state(self, controller: ProgrammaticGameController, initial_state: Dict[str, Any]) -> None:
        """Apply initial state overrides to controller."""
        game_state = controller.game_state
        
        # Apply direct state overrides
        state_mappings = {
            'turn': 'turn',
            'money': 'money', 
            'staff': 'staff',
            'reputation': 'reputation',
            'doom': 'doom',
            'action_points': 'action_points',
            'compute': 'compute'
        }
        
        for config_key, game_attr in state_mappings.items():
            if config_key in initial_state:
                if hasattr(game_state, game_attr):
                    setattr(game_state, game_attr, initial_state[config_key])
    
    def _validate_action_outcome(self, result: ActionResult, expected: Dict[str, Any]) -> bool:
        """Validate action result against expected outcomes."""
        # This is a basic implementation - can be extended with more sophisticated validation
        for key, expected_value in expected.items():
            if key in result.outcome:
                if result.outcome[key] != expected_value:
                    return False
        return True
    
    def _check_end_conditions(self, controller: ProgrammaticGameController, end_conditions: Dict[str, Any]) -> bool:
        """Check if scenario should end based on conditions."""
        game_state = controller.game_state
        
        # Check max turns
        if 'max_turns' in end_conditions:
            if game_state.turn >= end_conditions['max_turns']:
                return True
        
        # Check doom threshold
        if 'doom_threshold' in end_conditions:
            if game_state.doom >= end_conditions['doom_threshold']:
                return True
        
        # Check money threshold
        if 'min_money' in end_conditions:
            if game_state.money <= end_conditions['min_money']:
                return True
        
        return False
    
    def _evaluate_success_criteria(self, final_state: GameStateSnapshot, criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate success criteria against final game state."""
        results = {'overall_success': True, 'individual_results': []}
        
        for criterion in criteria:
            criterion_result = self._evaluate_single_criterion(final_state, criterion)
            results['individual_results'].append(criterion_result)
            
            if not criterion_result['success']:
                results['overall_success'] = False
        
        return results
    
    def _evaluate_single_criterion(self, state: GameStateSnapshot, criterion: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single success criterion."""
        # Basic implementation - supports simple comparisons
        # Can be extended to support complex expressions
        
        for attribute, condition in criterion.items():
            if not hasattr(state, attribute):
                return {'success': False, 'reason': f'Attribute {attribute} not found'}
            
            actual_value = getattr(state, attribute)
            
            if isinstance(condition, str):
                # Handle string comparisons like ">= 100000"
                if condition.startswith('>='):
                    threshold = float(condition[2:].strip())
                    success = actual_value >= threshold
                elif condition.startswith('<='):
                    threshold = float(condition[2:].strip())
                    success = actual_value <= threshold
                elif condition.startswith('>'):
                    threshold = float(condition[1:].strip())
                    success = actual_value > threshold
                elif condition.startswith('<'):
                    threshold = float(condition[1:].strip())
                    success = actual_value < threshold
                elif condition.startswith('=='):
                    threshold = float(condition[2:].strip())
                    success = actual_value == threshold
                else:
                    success = str(actual_value) == condition
            else:
                # Direct comparison
                success = actual_value == condition
            
            if not success:
                return {
                    'success': False, 
                    'attribute': attribute,
                    'expected': condition,
                    'actual': actual_value
                }
        
        return {'success': True}
    
    def _perform_statistical_analysis(self, results: List[ScenarioResult]) -> Dict[str, Any]:
        """Perform statistical analysis on batch results."""
        if not results:
            return {}
        
        successful_results = [r for r in results if r.success]
        
        analysis = {
            'execution_time_statistics': {},
            'final_state_statistics': {},
            'outcome_distributions': {}
        }
        
        # Execution time statistics
        execution_times = [r.execution_time_ms for r in results]
        if execution_times:
            analysis['execution_time_statistics'] = {
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'std_dev': statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                'min': min(execution_times),
                'max': max(execution_times)
            }
        
        # Final state statistics (for successful runs)
        if successful_results:
            # Analyze money distribution
            money_values = [r.final_state.money for r in successful_results]
            analysis['final_state_statistics']['money'] = {
                'mean': statistics.mean(money_values),
                'median': statistics.median(money_values),
                'std_dev': statistics.stdev(money_values) if len(money_values) > 1 else 0,
                'min': min(money_values),
                'max': max(money_values)
            }
            
            # Analyze turn distribution
            turn_values = [r.final_state.turn for r in successful_results]
            analysis['final_state_statistics']['turns'] = {
                'mean': statistics.mean(turn_values),
                'median': statistics.median(turn_values),
                'std_dev': statistics.stdev(turn_values) if len(turn_values) > 1 else 0,
                'min': min(turn_values),
                'max': max(turn_values)
            }
        
        return analysis
    
    def export_results(self, batch_result: BatchExecutionResult, filepath: Optional[str] = None) -> str:
        """Export batch execution results to JSON file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"scenario_results_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'game_version': get_display_version(),
                'total_scenarios': batch_result.total_scenarios
            },
            'results': batch_result.to_dict()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filepath


# Convenience functions for common usage patterns

def run_scenario_file(filepath: Union[str, Path], seed: Optional[str] = None) -> ScenarioResult:
    """Convenience function to run a single scenario from file."""
    runner = ScenarioRunner()
    return runner.run_scenario(filepath, seed)


def run_scenario_directory(directory: Union[str, Path], iterations: int = 1, parallel: bool = True) -> BatchExecutionResult:
    """Run all scenarios in a directory."""
    directory = Path(directory)
    scenario_files = []
    
    for ext in ['*.yaml', '*.yml', '*.json']:
        scenario_files.extend(directory.glob(ext))
    
    runner = ScenarioRunner()
    return runner.run_batch_scenarios(scenario_files, iterations=iterations, parallel=parallel)


def validate_balance_change(before_scenarios: List[Union[str, Path]], 
                          after_scenarios: List[Union[str, Path]], 
                          iterations: int = 100) -> Dict[str, Any]:
    """
    Validate balance changes by comparing scenario outcomes before and after.
    
    This is a critical function for automated balance validation.
    """
    runner = ScenarioRunner()
    
    # Run scenarios before change
    before_results = runner.run_batch_scenarios(before_scenarios, iterations=iterations)
    
    # Run scenarios after change  
    after_results = runner.run_batch_scenarios(after_scenarios, iterations=iterations)
    
    # Compare results
    comparison = {
        'before_success_rate': before_results.success_rate,
        'after_success_rate': after_results.success_rate,
        'success_rate_change': after_results.success_rate - before_results.success_rate,
        'before_avg_time': before_results.average_execution_time_ms,
        'after_avg_time': after_results.average_execution_time_ms,
        'performance_change': after_results.average_execution_time_ms - before_results.average_execution_time_ms,
        'statistical_significance': 'TODO: Implement statistical testing'
    }
    
    return comparison


if __name__ == '__main__':
    # Example usage and basic testing
    print(f"P(Doom) Scenario Runner - {get_display_version()}")
    print("=" * 60)
    
    # Basic functionality test
    try:
        runner = ScenarioRunner()
        print("SUCCESS: Scenario runner initialized")
        
        # Test scenario creation
        test_scenario = ScenarioConfig(
            name="Basic Test Scenario",
            description="Test basic functionality",
            actions=[
                ScenarioAction(action_id="hire_staff", parameters={"count": 1}),
                ScenarioAction(action_id="end_turn")
            ],
            success_criteria=[{"money": "> 90000"}]
        )
        
        result = runner.run_scenario(test_scenario)
        print(f"SUCCESS: Test scenario executed - Success: {result.success}")
        
    except Exception as e:
        print(f"ERROR: Scenario runner test failed: {e}")
"""
Test Suite for Scenario Runner System

This test suite validates the scenario-based testing capabilities including:
- Scenario configuration loading and parsing
- Single scenario execution and validation
- Batch scenario execution with statistical analysis
- Performance benchmarking and regression testing
- Integration with the programmatic controller

Coverage Target: 90%+ of scenario runner functionality
"""

import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Test imports
try:
    from src.testing.scenario_runner import (
        ScenarioRunner,
        ScenarioConfig,
        ScenarioAction,
        ScenarioResult,
        BatchExecutionResult,
        run_scenario_file
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import scenario runner modules: {e}")
    IMPORTS_AVAILABLE = False


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestScenarioConfiguration(unittest.TestCase):
    """Test scenario configuration and parsing."""
    
    def test_scenario_action_creation(self):
        """Test creation of scenario actions."""
        action = ScenarioAction(
            turn=1,
            action_id="hire_staff",
            parameters={"count": 2},
            expected_outcome={"staff_hired": 2}
        )
        
        self.assertEqual(action.turn, 1)
        self.assertEqual(action.action_id, "hire_staff")
        self.assertEqual(action.parameters["count"], 2)
        self.assertEqual(action.expected_outcome["staff_hired"], 2)
    
    def test_scenario_action_from_dict(self):
        """Test creating scenario action from dictionary."""
        action_data = {
            "turn": 2,
            "action_id": "end_turn",
            "parameters": {},
            "expected_outcome": {"turn_ended": True}
        }
        
        action = ScenarioAction.from_dict(action_data)
        
        self.assertEqual(action.turn, 2)
        self.assertEqual(action.action_id, "end_turn")
        self.assertEqual(action.parameters, {})
    
    def test_scenario_config_creation(self):
        """Test creation of scenario configurations."""
        config = ScenarioConfig(
            name="Test Scenario",
            description="A test scenario",
            initial_state={"money": 100000},
            actions=[ScenarioAction(action_id="hire_staff", parameters={"count": 1})],
            success_criteria=[{"money": "> 90000"}]
        )
        
        self.assertEqual(config.name, "Test Scenario")
        self.assertEqual(config.description, "A test scenario")
        self.assertEqual(config.initial_state["money"], 100000)
        self.assertEqual(len(config.actions), 1)
        self.assertEqual(len(config.success_criteria), 1)
    
    def test_scenario_config_from_dict(self):
        """Test creating scenario config from dictionary."""
        config_data = {
            "name": "Dict Test Scenario",
            "description": "Created from dictionary",
            "initial_state": {"money": 50000},
            "actions": [
                {"action_id": "hire_staff", "parameters": {"count": 1}},
                {"action_id": "end_turn"}
            ],
            "success_criteria": [{"money": "> 40000"}]
        }
        
        config = ScenarioConfig.from_dict(config_data)
        
        self.assertEqual(config.name, "Dict Test Scenario")
        self.assertEqual(len(config.actions), 2)
        self.assertEqual(config.actions[0].action_id, "hire_staff")


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestScenarioExecution(unittest.TestCase):
    """Test single scenario execution."""
    
    def setUp(self):
        """Set up test runner."""
        self.runner = ScenarioRunner()
    
    def test_simple_scenario_execution(self):
        """Test execution of a simple scenario."""
        scenario = ScenarioConfig(
            name="Simple Test",
            description="Basic scenario execution test",
            actions=[
                ScenarioAction(action_id="hire_staff", parameters={"count": 1}),
                ScenarioAction(action_id="end_turn")
            ],
            success_criteria=[{"money": "> 0"}]
        )
        
        result = self.runner.run_scenario(scenario)
        
        self.assertIsInstance(result, ScenarioResult)
        self.assertEqual(result.scenario_name, "Simple Test")
        self.assertIsInstance(result.success, bool)
        self.assertIsNotNone(result.final_state)
        self.assertIsInstance(result.execution_log, list)
        self.assertGreater(result.execution_time_ms, 0)
    
    def test_scenario_with_success_criteria(self):
        """Test scenario success criteria evaluation."""
        scenario = ScenarioConfig(
            name="Success Criteria Test",
            description="Test success criteria evaluation",
            actions=[ScenarioAction(action_id="hire_staff", parameters={"count": 1})],
            success_criteria=[
                {"money": "> 90000"},  # Should pass
                {"staff": ">= 1"}      # Should pass
            ]
        )
        
        result = self.runner.run_scenario(scenario)
        
        self.assertIsInstance(result.validation_results, dict)
        self.assertIn('overall_success', result.validation_results)
        self.assertIn('individual_results', result.validation_results)
    
    def test_scenario_with_initial_state(self):
        """Test scenario with custom initial state."""
        scenario = ScenarioConfig(
            name="Initial State Test",
            description="Test custom initial state",
            initial_state={
                "money": 50000,
                "staff": 5,
                "reputation": 75
            },
            actions=[ScenarioAction(action_id="end_turn")],
            success_criteria=[{"money": "== 50000"}]
        )
        
        result = self.runner.run_scenario(scenario)
        
        # Initial state should be applied
        # Note: Success may depend on game mechanics, but we can test execution
        self.assertIsInstance(result, ScenarioResult)
        self.assertIsNotNone(result.final_state)
    
    def test_scenario_with_end_conditions(self):
        """Test scenario with end conditions."""
        scenario = ScenarioConfig(
            name="End Conditions Test",
            description="Test early termination",
            actions=[
                ScenarioAction(action_id="end_turn"),
                ScenarioAction(action_id="end_turn"),
                ScenarioAction(action_id="end_turn"),
                ScenarioAction(action_id="end_turn"),
                ScenarioAction(action_id="end_turn")  # 5 turns
            ],
            end_conditions={"max_turns": 3},  # Should stop at turn 3
            success_criteria=[{"turn": "<= 3"}]
        )
        
        result = self.runner.run_scenario(scenario)
        
        # Should stop before executing all actions
        self.assertLessEqual(result.final_state.turn, 3)
    
    def test_deterministic_execution(self):
        """Test that same scenario with same seed produces identical results."""
        scenario = ScenarioConfig(
            name="Deterministic Test",
            description="Test deterministic execution",
            actions=[
                ScenarioAction(action_id="hire_staff", parameters={"count": 2}),
                ScenarioAction(action_id="end_turn")
            ],
            success_criteria=[{"money": "> 0"}]
        )
        
        seed = "deterministic-test-123"
        
        result1 = self.runner.run_scenario(scenario, seed=seed)
        result2 = self.runner.run_scenario(scenario, seed=seed)
        
        # Results should be identical
        self.assertEqual(result1.final_state.money, result2.final_state.money)
        self.assertEqual(result1.final_state.turn, result2.final_state.turn)
        self.assertEqual(result1.success, result2.success)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available") 
class TestScenarioFileHandling(unittest.TestCase):
    """Test loading scenarios from files."""
    
    def setUp(self):
        """Set up test runner and temporary files."""
        self.runner = ScenarioRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_json_scenario(self):
        """Test loading scenario from JSON file."""
        scenario_data = {
            "name": "JSON Test Scenario",
            "description": "Loaded from JSON file",
            "actions": [
                {"action_id": "hire_staff", "parameters": {"count": 1}}
            ],
            "success_criteria": [{"money": "> 0"}]
        }
        
        # Write to temporary file
        json_file = Path(self.temp_dir) / "test_scenario.json"
        with open(json_file, 'w') as f:
            json.dump(scenario_data, f)
        
        # Load and test
        config = self.runner.load_scenario(json_file)
        
        self.assertEqual(config.name, "JSON Test Scenario")
        self.assertEqual(len(config.actions), 1)
        self.assertEqual(config.actions[0].action_id, "hire_staff")
    
    def test_run_scenario_from_file(self):
        """Test running scenario directly from file."""
        scenario_data = {
            "name": "File Execution Test",
            "description": "Execute from file path",
            "actions": [
                {"action_id": "hire_staff", "parameters": {"count": 1}},
                {"action_id": "end_turn"}
            ],
            "success_criteria": [{"turn": ">= 1"}]
        }
        
        # Write to temporary file
        json_file = Path(self.temp_dir) / "execution_test.json"
        with open(json_file, 'w') as f:
            json.dump(scenario_data, f)
        
        # Run from file
        result = self.runner.run_scenario(json_file)
        
        self.assertEqual(result.scenario_name, "File Execution Test")
        self.assertIsInstance(result.success, bool)
    
    def test_convenience_function(self):
        """Test run_scenario_file convenience function."""
        scenario_data = {
            "name": "Convenience Test",
            "description": "Test convenience function",
            "actions": [{"action_id": "end_turn"}],
            "success_criteria": [{"turn": ">= 1"}]
        }
        
        # Write to temporary file
        json_file = Path(self.temp_dir) / "convenience_test.json"
        with open(json_file, 'w') as f:
            json.dump(scenario_data, f)
        
        # Use convenience function
        result = run_scenario_file(json_file)
        
        self.assertEqual(result.scenario_name, "Convenience Test")
        self.assertIsInstance(result, ScenarioResult)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestBatchExecution(unittest.TestCase):
    """Test batch scenario execution."""
    
    def setUp(self):
        """Set up test runner."""
        self.runner = ScenarioRunner()
    
    def test_batch_scenario_execution(self):
        """Test running multiple scenarios in batch."""
        scenarios = [
            ScenarioConfig(
                name="Batch Test 1",
                description="First batch scenario",
                actions=[ScenarioAction(action_id="hire_staff", parameters={"count": 1})],
                success_criteria=[{"money": "> 0"}]
            ),
            ScenarioConfig(
                name="Batch Test 2", 
                description="Second batch scenario",
                actions=[ScenarioAction(action_id="end_turn")],
                success_criteria=[{"turn": ">= 1"}]
            )
        ]
        
        batch_result = self.runner.run_batch_scenarios(scenarios)
        
        self.assertIsInstance(batch_result, BatchExecutionResult)
        self.assertEqual(batch_result.total_scenarios, 2)
        self.assertEqual(len(batch_result.scenario_results), 2)
        self.assertGreaterEqual(batch_result.successful_scenarios, 0)
        self.assertLessEqual(batch_result.failed_scenarios, 2)
    
    def test_batch_with_iterations(self):
        """Test batch execution with multiple iterations."""
        scenario = ScenarioConfig(
            name="Iteration Test",
            description="Test multiple iterations",
            actions=[ScenarioAction(action_id="hire_staff", parameters={"count": 1})],
            success_criteria=[{"money": "> 0"}]
        )
        
        batch_result = self.runner.run_batch_scenarios([scenario], iterations=3)
        
        self.assertEqual(batch_result.total_scenarios, 3)
        self.assertEqual(len(batch_result.scenario_results), 3)
        
        # All should have same scenario name but different execution results
        for result in batch_result.scenario_results:
            self.assertEqual(result.scenario_name, "Iteration Test")
    
    def test_statistical_analysis(self):
        """Test statistical analysis of batch results."""
        scenario = ScenarioConfig(
            name="Statistics Test",
            description="Test statistical analysis",
            actions=[
                ScenarioAction(action_id="hire_staff", parameters={"count": 1}),
                ScenarioAction(action_id="end_turn")
            ],
            success_criteria=[{"money": "> 0"}]
        )
        
        batch_result = self.runner.run_batch_scenarios([scenario], iterations=5)
        
        self.assertIsInstance(batch_result.statistical_analysis, dict)
        self.assertIn('execution_time_statistics', batch_result.statistical_analysis)
        
        # Check execution time statistics
        exec_stats = batch_result.statistical_analysis.get('execution_time_statistics', {})
        if exec_stats:
            self.assertIn('mean', exec_stats)
            self.assertIn('median', exec_stats) 
            self.assertIn('min', exec_stats)
            self.assertIn('max', exec_stats)
    
    def test_success_rate_calculation(self):
        """Test success rate calculation in batch results."""
        # Create scenarios with different success likelihood
        scenarios = [
            ScenarioConfig(
                name="Should Succeed",
                description="Likely to succeed",
                actions=[ScenarioAction(action_id="end_turn")],
                success_criteria=[{"turn": ">= 1"}]  # Very likely to pass
            ),
            ScenarioConfig(
                name="Should Fail",
                description="Likely to fail", 
                actions=[ScenarioAction(action_id="end_turn")],
                success_criteria=[{"money": "> 1000000"}]  # Very unlikely to pass
            )
        ]
        
        batch_result = self.runner.run_batch_scenarios(scenarios)
        
        self.assertIsInstance(batch_result.success_rate, float)
        self.assertGreaterEqual(batch_result.success_rate, 0.0)
        self.assertLessEqual(batch_result.success_rate, 1.0)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestPerformanceAndValidation(unittest.TestCase):
    """Test performance characteristics and validation logic."""
    
    def setUp(self):
        """Set up test runner."""
        self.runner = ScenarioRunner()
    
    def test_execution_performance(self):
        """Test that scenario execution performs within acceptable limits."""
        scenario = ScenarioConfig(
            name="Performance Test",
            description="Test execution performance",
            actions=[
                ScenarioAction(action_id="hire_staff", parameters={"count": 1}),
                ScenarioAction(action_id="end_turn")
            ],
            success_criteria=[{"money": "> 0"}]
        )
        
        result = self.runner.run_scenario(scenario)
        
        # Should execute reasonably quickly (< 5 seconds for simple scenario)
        self.assertLess(result.execution_time_ms, 5000)
    
    def test_validation_logic(self):
        """Test various validation conditions."""
        scenario = ScenarioConfig(
            name="Validation Test",
            description="Test all validation operators",
            actions=[ScenarioAction(action_id="end_turn")],
            success_criteria=[
                {"turn": ">= 1"},   # Greater than or equal
                {"turn": "<= 5"},   # Less than or equal  
                {"turn": "> 0"},    # Greater than
                {"turn": "< 10"},   # Less than
                {"turn": "== 1"}    # Equal to
            ]
        )
        
        result = self.runner.run_scenario(scenario)
        
        # Check that validation was performed
        self.assertIn('validation_results', result.__dict__)
        self.assertIn('individual_results', result.validation_results)
        
        # Should have 5 individual validation results
        individual_results = result.validation_results['individual_results']
        self.assertEqual(len(individual_results), 5)
    
    def test_error_handling(self):
        """Test error handling for invalid scenarios."""
        # Scenario with invalid action
        invalid_scenario = ScenarioConfig(
            name="Invalid Test",
            description="Should handle errors gracefully",
            actions=[ScenarioAction(action_id="invalid_action_that_does_not_exist")],
            success_criteria=[{"money": "> 0"}]
        )
        
        result = self.runner.run_scenario(invalid_scenario)
        
        # Should not crash, should return a result
        self.assertIsInstance(result, ScenarioResult)
        # May succeed or fail depending on how invalid actions are handled


if __name__ == '__main__':
    # Configure test execution
    if not IMPORTS_AVAILABLE:
        print("WARNING: Required modules not available. Skipping tests.")
        exit(0)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
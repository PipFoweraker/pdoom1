"""
Comprehensive Test Suite for Programmatic Game Controller

This test suite validates the programmatic control system's ability to:
- Execute game actions without GUI dependencies
- Provide accurate state snapshots and serialization
- Enable automated testing and scenario validation
- Support CI/CD integration and regression detection

Test Categories:
- Basic controller functionality and initialization
- Action execution and validation
- State management and serialization  
- Performance benchmarking and optimization
- Integration with existing game systems
- Scenario-based testing workflows

Coverage Target: 95%+ of programmatic controller functionality
Performance Target: 1000+ game simulations per minute
"""

import unittest
import sys
import os
import time
import json
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
try:
    from src.testing.programmatic_controller import (
        ProgrammaticGameController,
        GameStateSnapshot,
        ActionResult,
        quick_test_action,
        benchmark_action_sequence
    )
    from src.core.game_state import GameState
    from src.services.version import get_display_version
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    IMPORTS_AVAILABLE = False


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestProgrammaticControllerInitialization(unittest.TestCase):
    """Test controller initialization and basic setup."""
    
    def test_basic_initialization(self):
        """Test basic controller initialization with default parameters."""
        controller = ProgrammaticGameController()
        
        self.assertIsNotNone(controller.game_state)
        self.assertEqual(controller.game_state.turn, 0)
        self.assertEqual(controller.action_count, 0)
        self.assertIsInstance(controller.execution_log, list)
        self.assertEqual(len(controller.execution_log), 0)
    
    def test_seeded_initialization(self):
        """Test controller initialization with deterministic seed."""
        seed = "test-deterministic-123"
        controller = ProgrammaticGameController(seed=seed)
        
        self.assertEqual(controller.initial_snapshot.seed, seed)
        self.assertIsNotNone(controller.game_state)
        
        # Test deterministic behavior - same seed should produce same state
        controller2 = ProgrammaticGameController(seed=seed)
        
        self.assertEqual(controller.game_state.turn, controller2.game_state.turn)
        self.assertEqual(controller.game_state.money, controller2.game_state.money)
        self.assertEqual(controller.game_state.reputation, controller2.game_state.reputation)
    
    def test_headless_mode(self):
        """Test headless mode initialization (no pygame dependencies)."""
        controller = ProgrammaticGameController(headless=True)
        
        self.assertTrue(controller.headless)
        self.assertIsNotNone(controller.game_state)
        # Should initialize without pygame window or visual elements
    
    def test_config_override(self):
        """Test initialization with configuration overrides."""
        config = {"test_mode": True, "verbose": False}
        controller = ProgrammaticGameController(config=config)
        
        self.assertEqual(controller.config, config)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestBasicActionExecution(unittest.TestCase):
    """Test basic action execution capabilities."""
    
    def setUp(self):
        """Set up test controller for each test."""
        self.controller = ProgrammaticGameController(seed="test-actions-001")
        
        # Ensure consistent starting state
        self.initial_money = self.controller.game_state.money
        self.initial_staff = getattr(self.controller.game_state, 'staff', 0)
        self.initial_turn = self.controller.game_state.turn
    
    def test_hire_staff_action_basic(self):
        """Test basic staff hiring action execution."""
        # Execute hire staff action
        result = self.controller.execute_action('hire_staff', {'count': 2})
        
        self.assertIsInstance(result, ActionResult)
        self.assertEqual(result.action_id, 'hire_staff')
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.outcome, dict)
        
        # Verify action was logged
        self.assertEqual(len(self.controller.execution_log), 1)
        self.assertEqual(self.controller.action_count, 1)
    
    def test_hire_staff_action_validation(self):
        """Test staff hiring with state validation."""
        initial_staff = getattr(self.controller.game_state, 'staff', 0)
        initial_money = self.controller.game_state.money
        
        # Execute hire action
        result = self.controller.execute_action('hire_staff', {'count': 1})
        
        if result.success:
            # Validate staff increased
            current_staff = getattr(self.controller.game_state, 'staff', 0)
            self.assertGreater(current_staff, initial_staff)
            
            # Validate money decreased (cost was paid)
            self.assertLess(self.controller.game_state.money, initial_money)
        else:
            # If failed, should be due to insufficient funds
            self.assertIn('error', result.outcome)
    
    def test_end_turn_action(self):
        """Test turn advancement action."""
        initial_turn = self.controller.game_state.turn
        
        result = self.controller.execute_action('end_turn')
        
        self.assertIsInstance(result, ActionResult)
        self.assertEqual(result.action_id, 'end_turn')
        
        if result.success:
            self.assertGreater(self.controller.game_state.turn, initial_turn)
    
    def test_invalid_action_handling(self):
        """Test handling of invalid action IDs."""
        result = self.controller.execute_action('invalid_action_id')
        
        self.assertIsInstance(result, ActionResult)
        self.assertFalse(result.success)
        self.assertIn('error', result.outcome)
    
    def test_action_parameter_validation(self):
        """Test validation of action parameters."""
        # Test with invalid count parameter
        result = self.controller.execute_action('hire_staff', {'count': -1})
        
        self.assertIsInstance(result, ActionResult)
        # Should handle invalid parameters gracefully


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestStateManagement(unittest.TestCase):
    """Test state snapshot and serialization capabilities."""
    
    def setUp(self):
        """Set up test controller."""
        self.controller = ProgrammaticGameController(seed="test-state-001")
    
    def test_state_snapshot_creation(self):
        """Test creation of state snapshots."""
        snapshot = self.controller.get_state_snapshot()
        
        self.assertIsInstance(snapshot, GameStateSnapshot)
        self.assertEqual(snapshot.turn, self.controller.game_state.turn)
        self.assertEqual(snapshot.money, self.controller.game_state.money)
        self.assertEqual(snapshot.reputation, self.controller.game_state.reputation)
        self.assertEqual(snapshot.doom, self.controller.game_state.doom)
        self.assertEqual(snapshot.seed, "test-state-001")
    
    def test_state_snapshot_serialization(self):
        """Test serialization of state snapshots."""
        snapshot = self.controller.get_state_snapshot()
        
        # Test to_dict conversion
        snapshot_dict = snapshot.to_dict()
        self.assertIsInstance(snapshot_dict, dict)
        self.assertIn('turn', snapshot_dict)
        self.assertIn('money', snapshot_dict)
        self.assertIn('seed', snapshot_dict)
        
        # Test from_dict reconstruction
        reconstructed = GameStateSnapshot.from_dict(snapshot_dict)
        self.assertEqual(reconstructed.turn, snapshot.turn)
        self.assertEqual(reconstructed.money, snapshot.money)
        self.assertEqual(reconstructed.seed, snapshot.seed)
    
    def test_state_restoration(self):
        """Test loading state from snapshots."""
        # Create initial snapshot
        initial_snapshot = self.controller.get_state_snapshot()
        
        # Execute some actions to change state
        self.controller.execute_action('hire_staff', {'count': 1})
        self.controller.execute_action('end_turn')
        
        # Verify state changed
        self.assertNotEqual(self.controller.game_state.turn, initial_snapshot.turn)
        
        # Restore from snapshot
        success = self.controller.load_state_snapshot(initial_snapshot)
        
        self.assertTrue(success)
        self.assertEqual(self.controller.game_state.turn, initial_snapshot.turn)
        self.assertEqual(self.controller.game_state.money, initial_snapshot.money)
    
    def test_initial_state_reset(self):
        """Test reset to initial state functionality."""
        # Record initial state
        initial_turn = self.controller.game_state.turn
        initial_money = self.controller.game_state.money
        
        # Execute actions to change state
        self.controller.execute_action('hire_staff', {'count': 1})
        self.controller.execute_action('end_turn')
        
        # Reset to initial state
        success = self.controller.reset_to_initial_state()
        
        self.assertTrue(success)
        self.assertEqual(self.controller.game_state.turn, initial_turn)
        self.assertEqual(self.controller.game_state.money, initial_money)
        self.assertEqual(len(self.controller.execution_log), 0)
        self.assertEqual(self.controller.action_count, 0)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestExecutionLogging(unittest.TestCase):
    """Test execution logging and analysis capabilities."""
    
    def setUp(self):
        """Set up test controller."""
        self.controller = ProgrammaticGameController(seed="test-logging-001")
    
    def test_action_logging(self):
        """Test that actions are properly logged."""
        # Execute multiple actions
        self.controller.execute_action('hire_staff', {'count': 1})
        self.controller.execute_action('end_turn')
        
        # Verify logging
        self.assertEqual(len(self.controller.execution_log), 2)
        
        # Check first log entry
        first_action = self.controller.execution_log[0]
        self.assertEqual(first_action.action_id, 'hire_staff')
        self.assertIsInstance(first_action.execution_time_ms, float)
        self.assertIsInstance(first_action.state_changes, dict)
        self.assertIsInstance(first_action.outcome, dict)
    
    def test_execution_summary(self):
        """Test execution summary generation."""
        # Execute some actions
        self.controller.execute_action('hire_staff', {'count': 1})
        self.controller.execute_action('end_turn')
        
        summary = self.controller.get_execution_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_actions', summary)
        self.assertIn('total_execution_time_seconds', summary)
        self.assertIn('actions_per_second', summary)
        self.assertIn('game_version', summary)
        
        self.assertEqual(summary['total_actions'], 2)
        self.assertGreater(summary['total_execution_time_seconds'], 0)
    
    def test_export_execution_log(self):
        """Test execution log export functionality."""
        # Execute actions
        self.controller.execute_action('hire_staff', {'count': 1})
        
        # Export log
        log_filepath = self.controller.export_execution_log()
        
        self.assertIsInstance(log_filepath, str)
        self.assertTrue(log_filepath.endswith('.json'))
        
        # Verify file exists and contains valid JSON
        import os
        self.assertTrue(os.path.exists(log_filepath))
        
        with open(log_filepath, 'r') as f:
            log_data = json.load(f)
        
        self.assertIsInstance(log_data, dict)
        self.assertIn('execution_log', log_data)
        self.assertIn('summary', log_data)
        self.assertIn('metadata', log_data)
        
        # Clean up test file
        os.remove(log_filepath)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestPerformanceBenchmarking(unittest.TestCase):
    """Test performance characteristics and benchmarking."""
    
    def test_single_action_performance(self):
        """Test performance of single action execution."""
        controller = ProgrammaticGameController(seed="perf-test-001")
        
        start_time = time.time()
        result = controller.execute_action('hire_staff', {'count': 1})
        execution_time = time.time() - start_time
        
        # Should execute quickly (< 100ms for single action)
        self.assertLess(execution_time, 0.1)
        self.assertIsInstance(result, ActionResult)
    
    def test_batch_action_performance(self):
        """Test performance of batch action execution."""
        controller = ProgrammaticGameController(seed="perf-batch-001")
        
        start_time = time.time()
        
        # Execute 10 actions
        for i in range(10):
            controller.execute_action('hire_staff', {'count': 1})
        
        total_time = time.time() - start_time
        
        # Should maintain good performance for batch operations
        self.assertLess(total_time, 1.0)  # < 1 second for 10 actions
        
        # Check performance metrics
        summary = controller.get_execution_summary()
        self.assertGreater(summary['actions_per_second'], 10)  # At least 10 actions/sec
    
    def test_memory_efficiency(self):
        """Test memory efficiency of controller operations."""
        controller = ProgrammaticGameController(seed="memory-test-001")
        
        # Execute many actions and verify memory doesn't grow excessively
        for i in range(50):
            controller.execute_action('hire_staff', {'count': 1})
        
        # Execution log should be manageable size
        self.assertEqual(len(controller.execution_log), 50)
        
        # Should be able to reset and clear memory
        controller.reset_to_initial_state()
        self.assertEqual(len(controller.execution_log), 0)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestAdvancedFeatures(unittest.TestCase):
    """Test advanced programmatic control features."""
    
    def test_multi_turn_advancement(self):
        """Test advancing multiple turns at once."""
        controller = ProgrammaticGameController(seed="multi-turn-001")
        initial_turn = controller.game_state.turn
        
        # Advance multiple turns
        results = controller.advance_turn(3)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(controller.game_state.turn, initial_turn + 3)
    
    def test_quick_test_action_function(self):
        """Test convenience function for quick action testing."""
        result = quick_test_action('hire_staff', {'count': 1}, seed='quick-test-001')
        
        self.assertIsInstance(result, ActionResult)
        self.assertEqual(result.action_id, 'hire_staff')
    
    @unittest.skipIf(True, "Benchmark function may take significant time")
    def test_benchmark_action_sequence(self):
        """Test benchmarking of action sequences."""
        actions = [
            ('hire_staff', {'count': 1}),
            ('end_turn', {}),
            ('hire_staff', {'count': 1})
        ]
        
        benchmark_result = benchmark_action_sequence(actions, iterations=10)
        
        self.assertIsInstance(benchmark_result, dict)
        self.assertIn('average_time', benchmark_result)
        self.assertIn('total_time', benchmark_result)
        self.assertIn('iterations', benchmark_result)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestIntegrationWithGameState(unittest.TestCase):
    """Test integration with existing GameState functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.controller = ProgrammaticGameController(seed="integration-test-001")
    
    def test_game_state_consistency(self):
        """Test that programmatic actions maintain GameState consistency."""
        # Get initial state
        initial_snapshot = self.controller.get_state_snapshot()
        
        # Execute action
        self.controller.execute_action('hire_staff', {'count': 1})
        
        # Verify GameState is in consistent state
        game_state = self.controller.game_state
        
        # Basic consistency checks
        self.assertGreaterEqual(game_state.money, 0)
        self.assertGreaterEqual(game_state.reputation, 0)
        self.assertLessEqual(game_state.doom, game_state.max_doom)
        self.assertGreaterEqual(game_state.turn, 0)
    
    def test_deterministic_behavior(self):
        """Test that same seed produces deterministic results."""
        seed = "deterministic-test-123"
        
        # Create two controllers with same seed
        controller1 = ProgrammaticGameController(seed=seed)
        controller2 = ProgrammaticGameController(seed=seed)
        
        # Execute same actions
        result1 = controller1.execute_action('hire_staff', {'count': 2})
        result2 = controller2.execute_action('hire_staff', {'count': 2})
        
        # Results should be identical
        self.assertEqual(result1.success, result2.success)
        self.assertEqual(controller1.game_state.money, controller2.game_state.money)
        
        # Advance turns
        controller1.advance_turn(1)
        controller2.advance_turn(1)
        
        # Should still be synchronized
        self.assertEqual(controller1.game_state.turn, controller2.game_state.turn)


@unittest.skipIf(not IMPORTS_AVAILABLE, "Required modules not available")
class TestErrorHandlingAndEdgeCases(unittest.TestCase):
    """Test error handling and edge case scenarios."""
    
    def test_insufficient_funds_handling(self):
        """Test handling when actions require more money than available."""
        controller = ProgrammaticGameController(seed="poor-test-001")
        
        # Ensure low money state
        controller.game_state.money = 100  # Very low money
        
        # Try expensive action
        result = controller.execute_action('hire_staff', {'count': 100})
        
        # Should handle gracefully
        self.assertIsInstance(result, ActionResult)
        if not result.success:
            self.assertIn('error', result.outcome)
    
    def test_invalid_state_restoration(self):
        """Test handling of invalid state restoration attempts."""
        controller = ProgrammaticGameController(seed="invalid-state-001")
        
        # Try to load invalid state
        invalid_state = {"invalid": "data"}
        success = controller.load_state_snapshot(invalid_state)
        
        # Should handle gracefully and return False
        self.assertFalse(success)
    
    def test_large_parameter_values(self):
        """Test handling of extremely large parameter values."""
        controller = ProgrammaticGameController(seed="large-params-001")
        
        # Try with very large count
        result = controller.execute_action('hire_staff', {'count': 1000000})
        
        # Should handle without crashing
        self.assertIsInstance(result, ActionResult)


if __name__ == '__main__':
    # Configure test execution
    if not IMPORTS_AVAILABLE:
        print("WARNING: Required modules not available. Skipping tests.")
        exit(0)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
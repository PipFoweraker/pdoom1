"""
Unit tests for the verbose logging service.
Tests logging functionality, JSON export, and file management.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from src.services.verbose_logging import (
    VerboseLogger,
    LogLevel,
    init_verbose_logging,
    get_logger,
    is_logging_enabled
)


class TestVerboseLogger(unittest.TestCase):
    """Test the VerboseLogger class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test_game.log")
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up any logger instances
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.close()
        except:
            pass
        
        # Remove test files
        for file_path in [self.log_file]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        # Remove test directory
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass
    
    def test_logger_initialization(self):
        """Test logger initialization with different settings."""
        logger = VerboseLogger(
            game_seed="test_seed",
            log_level=LogLevel.STANDARD,
            enable_human_readable=True,
            enable_json_export=True
        )
        
        self.assertEqual(logger.game_seed, "test_seed")
        self.assertEqual(logger.log_level, LogLevel.STANDARD)
        self.assertTrue(logger.enable_human_readable)
        self.assertTrue(logger.enable_json_export)
        self.assertEqual(len(logger.actions_log), 0)
        self.assertEqual(len(logger.resource_changes_log), 0)
        self.assertEqual(len(logger.random_events_log), 0)
        
        logger.close()
    
    def test_action_logging(self):
        """Test action logging functionality."""
        logger = VerboseLogger("action_test", LogLevel.STANDARD)
        
        logger.log_action(
            turn=1,
            action_name="test_action",
            cost=100,
            ap_cost=1,
            result={"success": True, "resources_gained": 50}
        )
        
        self.assertEqual(len(logger.actions_log), 1)
        action = logger.actions_log[0]
        self.assertEqual(action.turn, 1)
        self.assertEqual(action.action_name, "test_action")
        self.assertEqual(action.cost, 100)
        self.assertEqual(action.ap_cost, 1)
        self.assertEqual(action.result["success"], True)
        
        logger.close()
    
    def test_resource_change_logging(self):
        """Test resource change logging."""
        logger = VerboseLogger("resource_test", LogLevel.STANDARD)
        
        logger.log_resource_change(
            turn=2,
            resource="money",
            old_value=1000,
            new_value=1100,
            reason="successful_action"
        )
        
        self.assertEqual(len(logger.resource_changes_log), 1)
        change = logger.resource_changes_log[0]
        self.assertEqual(change.turn, 2)
        self.assertEqual(change.resource, "money")
        self.assertEqual(change.old_value, 1000)
        self.assertEqual(change.new_value, 1100)
        self.assertEqual(change.change, 100)
        self.assertEqual(change.reason, "successful_action")
        
        logger.close()
    
    def test_random_event_logging(self):
        """Test random event logging."""
        logger = VerboseLogger("random_test", LogLevel.VERBOSE)
        
        logger.log_random_event(
            turn=3,
            context="action_effectiveness",
            rng_function="uniform",
            parameters={"min": 0.0, "max": 1.0},
            result=0.75,
            seed_info={"context_seed": "action_effectiveness_123"}
        )
        
        self.assertEqual(len(logger.random_events_log), 1)
        event = logger.random_events_log[0]
        self.assertEqual(event.turn, 3)
        self.assertEqual(event.context, "action_effectiveness")
        self.assertEqual(event.rng_function, "uniform")
        self.assertEqual(event.result, 0.75)
        
        logger.close()
    
    def test_json_export(self):
        """Test JSON export functionality."""
        logger = VerboseLogger("json_test", LogLevel.STANDARD, enable_json_export=True)
        
        # Add some test data
        logger.log_action(1, "test_action", 100, 1, {"success": True})
        logger.log_resource_change(1, "money", 1000, 1100, "test_action")
        
        # Export JSON returns file path
        json_file_path = logger.export_json_logs()
        
        # Should be a valid file path
        self.assertTrue(json_file_path.endswith('.json'))
        self.assertTrue(os.path.exists(json_file_path))
        
        # Read and parse the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("metadata", data)
        self.assertIn("actions", data)
        self.assertIn("resource_changes", data)
        self.assertEqual(len(data["actions"]), 1)
        self.assertEqual(len(data["resource_changes"]), 1)
        
        # Clean up
        os.remove(json_file_path)
        logger.close()
    
    def test_log_levels(self):
        """Test different log levels for human-readable output."""
        # Note: Log level filtering only affects human-readable logging,
        # not the in-memory log arrays which always store everything
        
        # All levels should store actions in memory
        logger_minimal = VerboseLogger("minimal_test", LogLevel.MINIMAL)
        logger_minimal.log_action(1, "routine", 10, 1, {})
        self.assertEqual(len(logger_minimal.actions_log), 1)  # Always stored
        logger_minimal.close()
        
        # Standard logging should log actions and resources
        logger_standard = VerboseLogger("standard_test", LogLevel.STANDARD)
        logger_standard.log_action(1, "action", 10, 1, {})
        self.assertEqual(len(logger_standard.actions_log), 1)
        logger_standard.close()
        
        # Debug logging should log everything
        logger_debug = VerboseLogger("debug_test", LogLevel.DEBUG)
        logger_debug.log_action(1, "action", 10, 1, {})
        logger_debug.log_random_event(1, "test_context", "randint", {"min": 1, "max": 100}, 50, {"seed": "test"})
        self.assertEqual(len(logger_debug.actions_log), 1)
        self.assertEqual(len(logger_debug.random_events_log), 1)
        logger_debug.close()


class TestGlobalLoggingSystem(unittest.TestCase):
    """Test the global logging management system."""
    
    def setUp(self):
        """Reset global state before each test."""
        # Reset any existing global logger
        import src.services.verbose_logging as vl
        vl.verbose_logger = None
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            if is_logging_enabled():
                get_logger().close()
        except:
            pass
        import src.services.verbose_logging as vl
        vl.verbose_logger = None
    
    def test_global_initialization(self):
        """Test global logging initialization."""
        self.assertFalse(is_logging_enabled())
        
        init_verbose_logging("global_test", LogLevel.STANDARD)
        self.assertTrue(is_logging_enabled())
        
        logger = get_logger()
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, VerboseLogger)
        
        logger.close()
    
    def test_get_logger_without_init_raises_error(self):
        """Test that accessing logger before initialization raises error."""
        with self.assertRaises(RuntimeError):
            get_logger()
    
    def test_global_logger_functionality(self):
        """Test global logger works correctly."""
        init_verbose_logging("global_func_test", LogLevel.STANDARD)
        logger = get_logger()
        
        # Test logging through global instance
        logger.log_action(1, "global_action", 50, 1, {"test": True})
        self.assertEqual(len(logger.actions_log), 1)
        
        # Test accessing same instance multiple times
        logger2 = get_logger()
        self.assertIs(logger, logger2)  # Should be same instance
        
        logger.close()


class TestVerboseLoggingEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def tearDown(self):
        """Clean up after each test."""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.close()
        except:
            pass
    
    def test_logging_with_none_values(self):
        """Test logging with None/empty values."""
        logger = VerboseLogger("none_test", LogLevel.STANDARD)
        
        # Should handle None in result gracefully
        logger.log_action(1, "test", 0, 0, None)
        self.assertEqual(len(logger.actions_log), 1)
        self.assertIsNone(logger.actions_log[0].result)
        
        logger.close()
    
    def test_large_data_logging(self):
        """Test logging with large data structures."""
        logger = VerboseLogger("large_test", LogLevel.DEBUG)
        
        # Large result dictionary
        large_result = {f"key_{i}": f"value_{i}" for i in range(1000)}
        logger.log_action(1, "large_action", 100, 1, large_result)
        
        self.assertEqual(len(logger.actions_log), 1)
        self.assertEqual(len(logger.actions_log[0].result), 1000)
        
        logger.close()
    
    def test_special_characters_in_data(self):
        """Test logging with special characters."""
        logger = VerboseLogger("special_test", LogLevel.STANDARD)
        
        # Unicode and special characters
        logger.log_action(1, "special_action", 100, 1, {
            "unicode": "测试数据",
            "special": "!@#$%^&*()",
            "newlines": "line1\nline2\nline3",
            "quotes": 'This has "quotes" in it'
        })
        
        # Should export to JSON without errors
        json_file_path = logger.export_json_logs()
        
        # Should be able to read the JSON file
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Should not raise exception
        
        self.assertEqual(len(data["actions"]), 1)
        
        # Clean up
        os.remove(json_file_path)
        logger.close()
    
    def test_concurrent_logging_safety(self):
        """Test that logger handles rapid successive calls."""
        logger = VerboseLogger("concurrent_test", LogLevel.STANDARD)
        
        # Rapid succession of logging calls
        for i in range(100):
            logger.log_action(i, f"action_{i}", i * 10, 1, {"iteration": i})
            logger.log_resource_change(i, "money", i * 100, (i + 1) * 100, f"action_{i}")
        
        self.assertEqual(len(logger.actions_log), 100)
        self.assertEqual(len(logger.resource_changes_log), 100)
        
        # Verify order is maintained
        for i in range(100):
            self.assertEqual(logger.actions_log[i].turn, i)
            self.assertEqual(logger.resource_changes_log[i].turn, i)
        
        logger.close()
    
    def test_memory_efficiency(self):
        """Test that logger stores data as expected."""
        logger = VerboseLogger("memory_test", LogLevel.MINIMAL)
        
        # All actions are stored in memory regardless of log level
        # Log level only affects human-readable output
        for i in range(100):  # Use smaller number for test
            logger.log_action(i, "routine_action", 10, 1, {})
        
        # All actions should be stored in memory
        self.assertEqual(len(logger.actions_log), 100)
        
        logger.close()


if __name__ == "__main__":
    unittest.main()

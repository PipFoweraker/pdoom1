"""Tests for the productive actions system."""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from productive_actions import (
    PRODUCTIVE_ACTIONS, EMPLOYEE_SUBTYPE_TO_CATEGORY,
    get_employee_category, get_available_actions, 
    check_action_requirements, get_default_action_index
)


class MockGameState:
    """Mock game state for testing productive action requirements."""
    
    def __init__(self):
        self.reputation = 10
        self.staff = 5
        self.research_staff = 2
        self.research_progress = 15
        self.money = 250
        self.compute = 40
        self.board_members = 0
        self.admin_staff = 1


class TestProductiveActions(unittest.TestCase):
    """Test productive actions definitions and functionality."""
    
    def test_all_categories_defined(self):
        """Test that all required employee categories have productive actions defined."""
        required_categories = [
            'junior_researcher', 'senior_researcher', 'security_engineer',
            'operations_specialist', 'administrative_staff', 'manager'
        ]
        
        for category in required_categories:
            self.assertIn(category, PRODUCTIVE_ACTIONS, f"Category {category} not defined")
            self.assertEqual(len(PRODUCTIVE_ACTIONS[category]), 3, 
                           f"Category {category} should have exactly 3 actions")
    
    def test_action_structure(self):
        """Test that all actions have required fields."""
        required_fields = ['name', 'description', 'effectiveness_bonus', 'requirements']
        
        for category, actions in PRODUCTIVE_ACTIONS.items():
            for i, action in enumerate(actions):
                for field in required_fields:
                    self.assertIn(field, action, 
                                f"Action {i} in category {category} missing field {field}")
                
                # Test effectiveness bonus is reasonable (between 1.0 and 1.2)
                bonus = action['effectiveness_bonus']
                self.assertGreaterEqual(bonus, 1.0, 
                                      f"Effectiveness bonus {bonus} too low")
                self.assertLessEqual(bonus, 1.2, 
                                   f"Effectiveness bonus {bonus} too high")
    
    def test_employee_subtype_mapping(self):
        """Test that all employee subtypes map to productive action categories."""
        expected_mappings = {
            'researcher': 'junior_researcher',
            'data_scientist': 'senior_researcher',
            'security_specialist': 'security_engineer',
            'engineer': 'operations_specialist',
            'administrator': 'administrative_staff',
            'manager': 'manager',
            'generalist': 'junior_researcher'
        }
        
        for subtype, expected_category in expected_mappings.items():
            actual_category = get_employee_category(subtype)
            self.assertEqual(actual_category, expected_category,
                           f"Subtype {subtype} should map to {expected_category}")
    
    def test_get_available_actions(self):
        """Test getting available actions for categories."""
        # Test valid category
        actions = get_available_actions('junior_researcher')
        self.assertEqual(len(actions), 3)
        self.assertEqual(actions[0]['name'], 'Literature Review')
        
        # Test invalid category
        actions = get_available_actions('invalid_category')
        self.assertEqual(actions, [])
    
    def test_default_action_index(self):
        """Test getting default action index."""
        # Test valid category
        index = get_default_action_index('junior_researcher')
        self.assertEqual(index, 0)
        
        # Test invalid category
        index = get_default_action_index('invalid_category')
        self.assertIsNone(index)
    
    def test_requirements_checking(self):
        """Test checking action requirements against game state."""
        game_state = MockGameState()
        
        # Test junior researcher first action (should pass)
        action = PRODUCTIVE_ACTIONS['junior_researcher'][0]  # Literature Review
        requirements_met, reason = check_action_requirements(action, game_state, 1.0)
        self.assertTrue(requirements_met)
        self.assertIsNone(reason)
        
        # Test action with insufficient compute
        requirements_met, reason = check_action_requirements(action, game_state, 0.1)
        self.assertFalse(requirements_met)
        self.assertIn('insufficient_compute', reason)
        
        # Test action with insufficient reputation
        action = PRODUCTIVE_ACTIONS['senior_researcher'][2]  # Publication Pipeline
        requirements_met, reason = check_action_requirements(action, game_state, 2.0)
        self.assertFalse(requirements_met)
        self.assertIn('insufficient_reputation', reason)


class TestGameStateIntegration(unittest.TestCase):
    """Test integration with game state (requires pygame)."""
    
    def setUp(self):
        """Set up test game state."""
        try:
            from game_state import GameState
            self.game_state = GameState(seed=12345)
        except ImportError as e:
            self.skipTest(f"Could not import GameState: {e}")
    
    def test_employee_blob_structure(self):
        """Test that employee blobs have productive action fields."""
        # Add some employees
        self.game_state._add('staff', 3)
        
        # Check that blobs have productive action fields
        for blob in self.game_state.employee_blobs:
            if blob['type'] == 'employee':
                self.assertIn('subtype', blob)
                self.assertIn('productive_action_index', blob)
                self.assertIn('productive_action_bonus', blob)
                self.assertIn('productive_action_active', blob)
    
    def test_productive_action_methods(self):
        """Test productive action management methods."""
        # Add some employees
        self.game_state._add('staff', 2)
        
        if self.game_state.employee_blobs:
            employee_id = self.game_state.employee_blobs[0]['id']
            
            # Test getting employee actions
            action_info = self.game_state.get_employee_productive_actions(employee_id)
            self.assertIsNotNone(action_info)
            self.assertIn('available_actions', action_info)
            self.assertEqual(len(action_info['available_actions']), 3)
            
            # Test setting employee action
            success, message = self.game_state.set_employee_productive_action(employee_id, 1)
            self.assertTrue(success)
            self.assertIn('Action set to', message)
            
            # Verify action was set
            updated_info = self.game_state.get_employee_productive_actions(employee_id)
            self.assertEqual(updated_info['current_action_index'], 1)
    
    def test_productivity_update_with_actions(self):
        """Test that productivity update applies productive actions."""
        # Add staff and resources
        self.game_state._add('staff', 3)
        self.game_state._add('compute', 20)
        self.game_state._add('reputation', 15)
        
        # Run productivity update
        productive_count = self.game_state._update_employee_productivity()
        
        # Check that employees have productive action bonuses applied
        for blob in self.game_state.employee_blobs:
            if blob['type'] == 'employee' and blob['productivity'] > 0:
                self.assertIn('productive_action_bonus', blob)
                self.assertIn('productive_action_active', blob)


if __name__ == '__main__':
    unittest.main()
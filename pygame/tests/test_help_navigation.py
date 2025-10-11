'''
Test the help screen navigation fix.

Test that pressing 'H' in game properly uses the navigation stack
so that Escape returns to the game instead of the main menu.
'''

import unittest
import sys
import os

# Add the parent directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHelpScreenNavigation(unittest.TestCase):
    '''Test help screen navigation fix'''
    
    def test_navigation_stack_functions(self):
        '''Test that navigation stack functions work correctly'''
        import main
        
        # Start with empty navigation stack
        main.navigation_stack = []
        main.current_state = 'game'
        
        # Push a state
        main.push_navigation_state('overlay')
        
        # Should be in overlay state now
        self.assertEqual(main.current_state, 'overlay')
        self.assertEqual(len(main.navigation_stack), 1)
        self.assertEqual(main.navigation_stack[0], 'game')
        
        # Pop should return to previous state
        success = main.pop_navigation_state()
        self.assertTrue(success)
        self.assertEqual(main.current_state, 'game')
        self.assertEqual(len(main.navigation_stack), 0)
        
        # Pop from empty stack should return False and not change state
        success = main.pop_navigation_state()
        self.assertFalse(success)
        self.assertEqual(main.current_state, 'game')
    
    def test_multiple_navigation_levels(self):
        '''Test navigation stack with multiple levels'''
        import main
        
        # Start fresh
        main.navigation_stack = []
        main.current_state = 'game'
        
        # Push multiple states
        main.push_navigation_state('overlay')  # game -> overlay
        main.push_navigation_state('bug_report')  # overlay -> bug_report
        
        self.assertEqual(main.current_state, 'bug_report')
        self.assertEqual(len(main.navigation_stack), 2)
        self.assertEqual(main.navigation_stack, ['game', 'overlay'])
        
        # Pop back through the stack
        success = main.pop_navigation_state()
        self.assertTrue(success)
        self.assertEqual(main.current_state, 'overlay')
        
        success = main.pop_navigation_state()
        self.assertTrue(success)
        self.assertEqual(main.current_state, 'game')
        
        # Stack should be empty now
        self.assertEqual(len(main.navigation_stack), 0)


if __name__ == '__main__':
    unittest.main()
# !/usr/bin/env python3
'''
P(Doom) Comprehensive Testing Framework
=====================================

Brute force testing system to systematically test all game interactions
and find potential crashes, bugs, and edge cases.

Usage:
    python dev_tool_testing.py --help
    python dev_tool_testing.py --test-all
    python dev_tool_testing.py --test-actions
    python dev_tool_testing.py --test-ui-interactions
    python dev_tool_testing.py --stress-test
'''

import argparse
import sys
import traceback
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Game imports
try:
    from src.core.game_state import GameState
    from src.core.research_quality import TechnicalDebt, DebtCategory
    import pygame
    pygame.init()
    PYGAME_AVAILABLE = True
except ImportError as e:
    print(f'Warning: Could not import game modules: {e}')
    PYGAME_AVAILABLE = False

@dataclass
class TestResult:
    '''Container for test results'''
    test_name: str
    passed: bool
    error_message: str = ''
    execution_time: float = 0.0
    details: Dict[str, Any] = None

class ComprehensiveGameTester:
    '''Comprehensive testing framework for P(Doom) game'''
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.game_state: Optional[GameState] = None
        
    def log(self, message: str) -> None:
        '''Log message if verbose mode is enabled'''
        if self.verbose:
            print(f'[{datetime.now().strftime('%H:%M:%S')}] {message}')
    
    def setup_game_state(self, seed: str = 'test-seed') -> bool:
        '''Initialize game state for testing'''
        try:
            self.game_state = GameState(seed)
            self.log(f'v Game state initialized with seed: {seed}')
            return True
        except Exception as e:
            self.log(f'x Failed to initialize game state: {e}')
            return False
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        '''Run a single test and capture results'''
        start_time = time.time()
        try:
            test_func()
            execution_time = time.time() - start_time
            result = TestResult(test_name, True, execution_time=execution_time)
            self.log(f'v {test_name} passed ({execution_time:.3f}s)')
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f'{type(e).__name__}: {str(e)}'
            result = TestResult(test_name, False, error_msg, execution_time)
            self.log(f'x {test_name} failed ({execution_time:.3f}s): {error_msg}')
            if self.verbose:
                traceback.print_exc()
        
        self.results.append(result)
        return result
    
    def test_core_game_state_operations(self) -> None:
        '''Test all core game state operations for crashes'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        # Test basic attribute access
        self.game_state.money
        self.game_state.staff
        self.game_state.doom
        self.game_state.reputation
        self.game_state.action_points
        
        # Test critical methods
        self.game_state.end_turn()
        self.game_state.turn
        
        # Test event handling
        len(self.game_state.messages)
        len(self.game_state.event_log_history)
    
    def test_all_available_actions(self) -> None:
        '''Test executing all available actions'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        original_money = self.game_state.money
        original_staff = self.game_state.staff
        
        # Get all available actions
        actions = self.game_state.actions
        self.log(f'Testing {len(actions)} available actions')
        
        for action in actions:
            action_name = action.get('name', 'Unknown Action')
            try:
                # Check if action is available/affordable
                # Handle both callable and static costs
                if 'cost' in action:
                    cost = action['cost']
                    if callable(cost):
                        cost = cost(self.game_state)  # FIX: Pass game state parameter
                    if cost > self.game_state.money:
                        continue
                        
                if 'staff_required' in action and action['staff_required'] > self.game_state.staff:
                    continue
                
                # Execute action safely
                messages = []
                
                # Some actions require parameters, skip complex ones for now
                if 'execute' in action:
                    self.log(f'  Testing action: {action_name}')
                    action['execute'](self.game_state, messages)
                    
            except Exception as e:
                # Log action-specific errors but don't fail the test
                self.log(f'    Warning: Action '{action_name}' failed: {e}')
    
    def test_research_quality_system(self) -> None:
        '''Test the research quality system comprehensively'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        # Initialize technical debt system
        self.game_state.technical_debt = TechnicalDebt()
        
        # Test all debt categories
        for category in [DebtCategory.SAFETY_TESTING, DebtCategory.CODE_QUALITY, 
                        DebtCategory.DOCUMENTATION, DebtCategory.VALIDATION]:
            self.game_state.technical_debt.add_debt(5, category)
            self.game_state.technical_debt.reduce_debt(2, category)
        
        # Test research options that caused the original crash
        # These need proper cost/duration values to avoid KeyError
        rush_option = {'id': 'rush_research', 'name': 'Rush Research', 'cost': 1000, 'duration': 1, 
                      'min_doom_reduction': 1, 'max_doom_reduction': 3, 'reputation_gain': 2}
        quality_option = {'id': 'quality_research', 'name': 'Quality Research', 'cost': 2000, 'duration': 2,
                         'min_doom_reduction': 2, 'max_doom_reduction': 5, 'reputation_gain': 5}
        
        self.game_state._execute_research_option(rush_option)
        self.game_state._execute_research_option(quality_option)
    
    def test_mouse_wheel_edge_cases(self) -> None:
        '''Test mouse wheel handling in various scenarios'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        # Test various configurations
        test_configs = [
            (False, [], []),
            (True, [], []),
            (True, ['event'] * 50, ['message'] * 30),
        ]
        
        for enabled, history, messages in test_configs:
            self.game_state.scrollable_event_log_enabled = enabled
            self.game_state.event_log_history = history
            self.game_state.messages = messages
            
            # Simulate mouse wheel events
            self.game_state.event_log_scroll_offset = max(0, 
                self.game_state.event_log_scroll_offset - 3)
            max_scroll = max(0, len(self.game_state.event_log_history) + 
                           len(self.game_state.messages) - 7)
            self.game_state.event_log_scroll_offset = min(max_scroll, 
                self.game_state.event_log_scroll_offset + 3)
    
    def test_list_operations_safety(self) -> None:
        '''Test list operations for thread safety and modification issues'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        # Test opponent list operations
        original_opponents = self.game_state.opponents.copy()
        
        # Test safe sampling (the fix for issue #265)
        import random
        if self.game_state.opponents:
            selected = get_rng().sample(self.game_state.opponents, 
                                   min(2, len(self.game_state.opponents)))
        
        # Restore original state
        self.game_state.opponents = original_opponents
    
    def test_ui_hover_operations(self) -> None:
        '''Test UI hover operations that caused duplicate return bug'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        # Test various mouse positions
        test_positions = [
            (0, 0), (100, 100), (400, 300), (800, 600),
            (-1, -1), (9999, 9999)  # Edge cases
        ]
        
        for x, y in test_positions:
            try:
                result = self.game_state.check_hover((x, y), 800, 600)
                # Should not crash, result can be None or valid data
            except Exception as e:
                self.log(f'    Warning: Hover at ({x}, {y}) failed: {e}')
    
    def stress_test_game_cycles(self, cycles: int = 50) -> None:
        '''Stress test the game by running many cycles'''
        if not self.game_state:
            raise RuntimeError('Game state not initialized')
        
        self.log(f'Running {cycles} game turn cycles...')
        
        for i in range(cycles):
            try:
                # Execute a few actions per turn
                # Handle both callable and static costs
                affordable_actions = []
                for a in self.game_state.actions:
                    try:
                        cost = a.get('cost', 0)
                        # Handle callable costs (economic config)
                        if callable(cost):
                            cost = cost(self.game_state)  # FIX: Pass game state parameter
                        if cost <= self.game_state.money:
                            affordable_actions.append(a)
                    except Exception:
                        # Skip actions with problematic cost calculations
                        continue
                
                if affordable_actions:
                    action = affordable_actions[0]
                    if 'execute' in action:
                        action['execute'](self.game_state, [])
                
                # End turn
                self.game_state.end_turn()
                
                if i % 10 == 0:
                    self.log(f'  Completed {i+1}/{cycles} cycles')
                    
            except Exception as e:
                self.log(f'  Stress test failed at cycle {i+1}: {e}')
                raise
    
    def run_comprehensive_test_suite(self) -> None:
        '''Run all tests in the comprehensive suite'''
        self.log('Starting comprehensive P(Doom) test suite...')
        
        if not PYGAME_AVAILABLE:
            self.log('Warning: Pygame not available, some tests may be skipped')
        
        # Initialize game state
        if not self.setup_game_state():
            return
        
        # Core functionality tests
        self.run_test(self.test_core_game_state_operations, 'Core Game State Operations')
        
        # Critical bug regression tests
        self.run_test(self.test_research_quality_system, 'Research Quality System')
        self.run_test(self.test_mouse_wheel_edge_cases, 'Mouse Wheel Edge Cases') 
        self.run_test(self.test_list_operations_safety, 'List Operations Safety')
        self.run_test(self.test_ui_hover_operations, 'UI Hover Operations')
        
        # Comprehensive system tests
        self.run_test(self.test_all_available_actions, 'All Available Actions')
        
        # Stress tests
        self.run_test(lambda: self.stress_test_game_cycles(20), 'Game Cycle Stress Test')
    
    def generate_report(self) -> Dict[str, Any]:
        '''Generate comprehensive test report'''
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        total_time = sum(r.execution_time for r in self.results)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_execution_time': round(total_time, 3)
            },
            'test_results': [
                {
                    'name': r.test_name,
                    'passed': r.passed,
                    'error': r.error_message,
                    'time': round(r.execution_time, 3)
                }
                for r in self.results
            ]
        }
        
        return report
    
    def print_summary(self) -> None:
        '''Print test summary to console'''
        report = self.generate_report()
        summary = report['summary']
        
        print('\n' + '='*60)
        print('P(DOOM) COMPREHENSIVE TEST RESULTS')
        print('='*60)
        print(f'Total Tests: {summary['total_tests']}')
        print(f'Passed: {summary['passed']} v')
        print(f'Failed: {summary['failed']} x')
        print(f'Success Rate: {summary['success_rate']:.1f}%')
        print(f'Execution Time: {summary['total_execution_time']:.3f} seconds')
        
        if summary['failed'] > 0:
            print('\nFAILED TESTS:')
            for result in report['test_results']:
                if not result['passed']:
                    print(f'  x {result['name']}: {result['error']}')
        
        print('='*60)


def main():
    '''Main entry point for the testing framework'''
    parser = argparse.ArgumentParser(description='P(Doom) Comprehensive Testing Framework')
    parser.add_argument('--test-all', action='store_true', 
                       help='Run all comprehensive tests')
    parser.add_argument('--test-actions', action='store_true',
                       help='Test all game actions')
    parser.add_argument('--test-ui', action='store_true',
                       help='Test UI interactions')
    parser.add_argument('--stress-test', action='store_true',
                       help='Run stress tests')
    parser.add_argument('--cycles', type=int, default=50,
                       help='Number of cycles for stress test')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce output verbosity')
    parser.add_argument('--output', type=str,
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    if not any([args.test_all, args.test_actions, args.test_ui, args.stress_test]):
        parser.print_help()
        return
    
    tester = ComprehensiveGameTester(verbose=not args.quiet)
    
    try:
        if args.test_all:
            tester.run_comprehensive_test_suite()
        else:
            if not tester.setup_game_state():
                return
            
            if args.test_actions:
                tester.run_test(tester.test_all_available_actions, 'All Available Actions')
            
            if args.test_ui:
                tester.run_test(tester.test_ui_hover_operations, 'UI Hover Operations')
                tester.run_test(tester.test_mouse_wheel_edge_cases, 'Mouse Wheel Edge Cases')
            
            if args.stress_test:
                tester.run_test(lambda: tester.stress_test_game_cycles(args.cycles), 
                               f'Stress Test ({args.cycles} cycles)')
        
        # Print results
        tester.print_summary()
        
        # Save results if requested
        if args.output:
            report = tester.generate_report()
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f'\nResults saved to: {args.output}')
            
    except KeyboardInterrupt:
        print('\n\nTesting interrupted by user')
    except Exception as e:
        print(f'\nFatal error in testing framework: {e}')
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

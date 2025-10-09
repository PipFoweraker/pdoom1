'''
Tests for Enhanced Deterministic RNG System

Validates community-focused features:
- Memorable seed generation
- Complete reproducibility
- Call history tracking
- Challenge export functionality
- Verbose debugging capabilities
'''

import unittest
from unittest.mock import patch
from src.services.deterministic_rng import (
    init_deterministic_rng, get_rng, reset_rng, create_challenge_seed,
    get_challenge_export
)


class TestEnhancedDeterministicRNG(unittest.TestCase):
    '''Test suite for enhanced deterministic RNG functionality.'''
    
    def setUp(self):
        '''Reset RNG state before each test.'''
        reset_rng()
    
    def tearDown(self):
        '''Clean up after each test.'''
        reset_rng()
    
    def test_memorable_seed_generation(self):
        '''Test that memorable seeds are generated consistently.'''
        with patch('time.time', return_value=1234567890):
            seed1 = create_challenge_seed('Test Challenge')
            seed2 = create_challenge_seed('Test Challenge')
            
            # Should be deterministic based on timestamp
            self.assertEqual(seed1, seed2)
            self.assertIn('PDOOM', seed1)
            self.assertIn('-', seed1)  # Should have dashes separating parts
    
    def test_call_history_tracking(self):
        '''Test that all RNG calls are properly recorded.'''
        init_deterministic_rng('TEST-SEED-123')
        rng = get_rng()
        rng.set_turn(5)
        
        # Make various RNG calls
        rng.random('test_context_1')
        rng.randint(1, 100, 'test_context_2')
        rng.choice(['a', 'b', 'c'], 'test_context_3')
        
        # Verify call history
        self.assertEqual(len(rng.call_history), 3)
        
        # Check first call details
        first_call = rng.call_history[0]
        self.assertEqual(first_call.turn, 5)
        self.assertEqual(first_call.call_type, 'random')
        self.assertEqual(first_call.parameters['context'], 'test_context_1')
        
        # Check reproducibility
        result1 = first_call.result
        
        # Reset and reproduce
        reset_rng()
        init_deterministic_rng('TEST-SEED-123')
        rng2 = get_rng()
        rng2.set_turn(5)
        result2 = rng2.random('test_context_1')
        
        self.assertEqual(result1, result2)
    
    def test_perfect_reproducibility(self):
        '''Test that identical seeds produce identical sequences.'''
        seed = 'PERFECT-REPRO-TEST'
        
        # First run
        init_deterministic_rng(seed)
        rng1 = get_rng()
        results1 = []
        for i in range(10):
            results1.append(rng1.random(f'context_{i}'))
        
        # Second run with same seed
        reset_rng()
        init_deterministic_rng(seed)
        rng2 = get_rng()
        results2 = []
        for i in range(10):
            results2.append(rng2.random(f'context_{i}'))
        
        # Should be identical
        self.assertEqual(results1, results2)
    
    def test_context_independence(self):
        '''Test that different contexts produce independent sequences.'''
        init_deterministic_rng('CONTEXT-TEST')
        rng = get_rng()
        
        # Get results in one order
        result_a1 = rng.random('context_a')
        result_b1 = rng.random('context_b')
        result_a2 = rng.random('context_a')
        
        # Reset and get in different order
        reset_rng()
        init_deterministic_rng('CONTEXT-TEST')
        rng = get_rng()
        
        result_b1_alt = rng.random('context_b')
        result_a1_alt = rng.random('context_a')
        result_a2_alt = rng.random('context_a')
        
        # Context results should be identical regardless of call order
        self.assertEqual(result_a1, result_a1_alt)
        self.assertEqual(result_b1, result_b1_alt)
        self.assertEqual(result_a2, result_a2_alt)
    
    def test_verbose_debug_output(self):
        '''Test verbose debugging functionality.'''
        init_deterministic_rng('DEBUG-TEST')
        rng = get_rng()
        rng.enable_verbose_debug(True)
        rng.set_turn(42)
        
        # Capture output
        with patch('builtins.print') as mock_print:
            rng.random('debug_context')
            
            # Verify debug output was generated
            mock_print.assert_called()
            call_args = str(mock_print.call_args_list[-1])
            self.assertIn('Turn 42', call_args)
            self.assertIn('random', call_args)
            self.assertIn('debug_context', call_args)
    
    def test_challenge_export_functionality(self):
        '''Test challenge export for community sharing.'''
        init_deterministic_rng('EXPORT-TEST-SEED')
        rng = get_rng()
        rng.set_turn(10)
        
        # Make some calls to populate history
        rng.random('game_start')
        rng.randint(1, 6, 'dice_roll')
        rng.choice(['win', 'lose'], 'outcome')
        
        # Test export
        export_data = get_challenge_export()
        self.assertIsNotNone(export_data)
        
        challenge_info = export_data['challenge_info']
        self.assertEqual(challenge_info['seed'], 'EXPORT-TEST-SEED')
        self.assertEqual(challenge_info['total_rng_calls'], 3)
        self.assertEqual(challenge_info['turns_played'], 10)
        self.assertIn('deterministic_signature', challenge_info)
        
        # Verify call history is included
        call_history = export_data['call_history']
        self.assertEqual(len(call_history), 3)
        
        # Verify call details
        first_call = call_history[0]
        self.assertEqual(first_call['turn'], 10)
        self.assertEqual(first_call['call_type'], 'random')
    
    def test_debug_info_completeness(self):
        '''Test that debug info contains all expected fields.'''
        init_deterministic_rng('DEBUG-INFO-TEST')
        rng = get_rng()
        rng.set_turn(15)
        rng.enable_verbose_debug(False)
        
        # Make some calls
        rng.random('test1')
        rng.randint(1, 10, 'test2')
        
        debug_info = rng.get_debug_info()
        
        # Verify all expected fields
        expected_fields = [
            'base_seed', 'context_counters', 'total_calls',
            'call_history_count', 'current_turn', 'verbose_debug'
        ]
        
        for field in expected_fields:
            self.assertIn(field, debug_info)
        
        # Verify values
        self.assertEqual(debug_info['base_seed'], 'DEBUG-INFO-TEST')
        self.assertEqual(debug_info['total_calls'], 2)
        self.assertEqual(debug_info['call_history_count'], 2)
        self.assertEqual(debug_info['current_turn'], 15)
        self.assertFalse(debug_info['verbose_debug'])
    
    def test_deterministic_signature_consistency(self):
        '''Test that deterministic signatures are consistent for same scenarios.'''
        seed = 'SIGNATURE-TEST'
        
        # Run scenario twice
        signatures = []
        for _ in range(2):
            init_deterministic_rng(seed)
            rng = get_rng()
            rng.set_turn(5)
            
            # Make identical calls
            rng.random('scenario_start')
            rng.randint(1, 20, 'scenario_action')
            
            challenge_info = rng.get_challenge_info()
            signatures.append(challenge_info['deterministic_signature'])
            reset_rng()
        
        # Signatures should be identical
        self.assertEqual(signatures[0], signatures[1])
    
    def test_all_rng_methods_with_recording(self):
        '''Test that all RNG methods properly record calls.'''
        init_deterministic_rng('METHODS-TEST')
        rng = get_rng()
        
        # Test all methods
        test_sequence = [1, 2, 3, 4, 5]
        rng.random('random_test')
        rng.randint(1, 10, 'randint_test') 
        rng.choice(test_sequence, 'choice_test')
        rng.uniform(0.0, 1.0, 'uniform_test')
        rng.shuffle(test_sequence.copy(), 'shuffle_test')
        
        # Verify all calls recorded
        self.assertEqual(len(rng.call_history), 5)
        
        # Verify call types
        call_types = [call.call_type for call in rng.call_history]
        expected_types = ['random', 'randint', 'choice', 'uniform', 'shuffle']
        self.assertEqual(call_types, expected_types)


if __name__ == '__main__':
    unittest.main()

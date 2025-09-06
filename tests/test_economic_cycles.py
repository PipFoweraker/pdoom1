"""
Unit tests for the Economic Cycles system.

Tests the economic volatility and funding system added for Issue #192.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.economic_cycles import EconomicCycles, EconomicPhase, FundingSource, EconomicState
from src.core.game_state import GameState


class TestEconomicCycles(unittest.TestCase):
    """Test cases for the EconomicCycles system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState(seed="test-seed-123")
        self.cycles = self.game_state.economic_cycles
    
    def test_initialization(self):
        """Test that economic cycles initialize correctly."""
        self.assertIsNotNone(self.cycles)
        self.assertIsInstance(self.cycles.current_state.phase, EconomicPhase)
    
    def test_phase_types(self):
        """Test that all economic phases are valid."""
        for phase in EconomicPhase:
            self.assertIsInstance(phase, EconomicPhase)
    
    def test_funding_source_types(self):
        """Test that all funding sources are valid.""" 
        for source in FundingSource:
            self.assertIsInstance(source, FundingSource)
    
    def test_integration_with_game_state(self):
        """Test integration with GameState."""
        # Test that economic cycles integrate properly with game state
        self.assertIsNotNone(self.game_state.economic_cycles)
        
        # Test that end turn updates economic cycles
        initial_turn = self.game_state.turn
        self.game_state.end_turn()
        
        # Game should advance
        self.assertEqual(self.game_state.turn, initial_turn + 1)
    
    def test_economic_state_structure(self):
        """Test that economic state has correct structure."""
        state = self.cycles.current_state
        self.assertIsInstance(state, EconomicState)
        self.assertIsInstance(state.phase, EconomicPhase)
        self.assertIsInstance(state.funding_multiplier, float)
        self.assertGreater(state.funding_multiplier, 0.0)


class TestEconomicCyclesBasicFeatures(unittest.TestCase):
    """Test basic economic cycles features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = GameState(seed="basic-test")
    
    def test_game_state_has_economic_cycles(self):
        """Test that game state includes economic cycles."""
        self.assertTrue(hasattr(self.game_state, 'economic_cycles'))
        self.assertIsNotNone(self.game_state.economic_cycles)
    
    def test_economic_cycles_persist_across_turns(self):
        """Test that economic cycles persist when advancing turns."""
        initial_cycles = self.game_state.economic_cycles
        
        # Advance a few turns
        for _ in range(3):
            self.game_state.end_turn()
        
        # Economic cycles should still exist
        self.assertIsNotNone(self.game_state.economic_cycles)
        self.assertIs(self.game_state.economic_cycles, initial_cycles)


if __name__ == '__main__':
    unittest.main()

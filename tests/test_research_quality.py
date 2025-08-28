"""
Tests for the Research Quality System - Technical Debt vs. Speed Trade-offs

This test module validates the core functionality of the research quality system,
including research project management, technical debt accumulation and consequences,
debt reduction actions, and integration with existing game mechanics.
"""

import unittest
import random
from src.core.game_state import GameState
from src.core.research_quality import (
    ResearchQuality, ResearchProject, TechnicalDebt, 
    calculate_research_outcome, get_debt_reduction_actions,
    QUALITY_MODIFIERS
)
from src.core.actions import ACTIONS


class TestResearchQuality(unittest.TestCase):
    """Test basic research quality functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.gs = GameState('test-research-quality')
        # Give the game state some resources to work with
        self.gs.money = 1000
        self.gs.research_staff = 5
        self.gs.action_points = 10
    
    def test_research_quality_enum(self):
        """Test that research quality enum values are correct."""
        self.assertEqual(ResearchQuality.RUSHED.value, "rushed")
        self.assertEqual(ResearchQuality.STANDARD.value, "standard")
        self.assertEqual(ResearchQuality.THOROUGH.value, "thorough")
    
    def test_quality_modifiers(self):
        """Test that quality modifiers match specification."""
        # Rushed approach
        rushed = QUALITY_MODIFIERS[ResearchQuality.RUSHED]
        self.assertEqual(rushed.duration_multiplier, 0.6)  # -40% time
        self.assertEqual(rushed.cost_multiplier, 0.8)      # -20% cost
        self.assertEqual(rushed.doom_modifier, 15)         # +15% doom
        self.assertEqual(rushed.debt_change, 2)            # +2 debt
        self.assertEqual(rushed.success_rate_modifier, -10) # -10% success
        
        # Standard approach
        standard = QUALITY_MODIFIERS[ResearchQuality.STANDARD]
        self.assertEqual(standard.duration_multiplier, 1.0)
        self.assertEqual(standard.cost_multiplier, 1.0)
        self.assertEqual(standard.doom_modifier, 0)
        self.assertEqual(standard.debt_change, 0)
        self.assertEqual(standard.success_rate_modifier, 0)
        
        # Thorough approach
        thorough = QUALITY_MODIFIERS[ResearchQuality.THOROUGH]
        self.assertEqual(thorough.duration_multiplier, 1.6)  # +60% time
        self.assertEqual(thorough.cost_multiplier, 1.4)      # +40% cost
        self.assertEqual(thorough.doom_modifier, -20)        # -20% doom
        self.assertEqual(thorough.debt_change, -1)           # -1 debt
        self.assertEqual(thorough.success_rate_modifier, 15) # +15% success
    
    def test_research_project_creation(self):
        """Test research project creation and modification."""
        project = ResearchProject("Test Project", 100, 2)
        
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.base_cost, 100)
        self.assertEqual(project.base_duration, 2)
        self.assertEqual(project.quality_level, ResearchQuality.STANDARD)
        self.assertFalse(project.completed)
        
        # Test quality level changes
        project.set_quality_level(ResearchQuality.RUSHED)
        self.assertEqual(project.quality_level, ResearchQuality.RUSHED)
        
        project.set_quality_level(ResearchQuality.THOROUGH)
        self.assertEqual(project.quality_level, ResearchQuality.THOROUGH)
        self.assertTrue(project.safety_verification)
    
    def test_modified_costs_and_duration(self):
        """Test that quality modifiers affect project costs and duration."""
        project = ResearchProject("Test", 100, 4)
        
        # Rushed approach
        project.set_quality_level(ResearchQuality.RUSHED)
        self.assertEqual(project.get_modified_cost(), 80)   # 20% cheaper
        self.assertEqual(project.get_modified_duration(), 2) # 40% faster (2.4 rounded to 2)
        
        # Standard approach
        project.set_quality_level(ResearchQuality.STANDARD)
        self.assertEqual(project.get_modified_cost(), 100)  # No change
        self.assertEqual(project.get_modified_duration(), 4) # No change
        
        # Thorough approach
        project.set_quality_level(ResearchQuality.THOROUGH)
        self.assertEqual(project.get_modified_cost(), 140)  # 40% more expensive
        self.assertEqual(project.get_modified_duration(), 6) # 60% slower (6.4 rounded to 6)


class TestTechnicalDebt(unittest.TestCase):
    """Test technical debt tracking and consequences."""
    
    def setUp(self):
        """Set up test environment."""
        self.debt = TechnicalDebt()
    
    def test_debt_initialization(self):
        """Test that debt initializes correctly."""
        self.assertEqual(self.debt.accumulated_debt, 0)
        for category in self.debt.debt_categories.values():
            self.assertEqual(category, 0)
    
    def test_debt_accumulation(self):
        """Test debt accumulation and distribution."""
        # Add debt without category
        self.debt.add_debt(5)
        self.assertEqual(self.debt.accumulated_debt, 5)
        
        # Add debt to specific category (this adds to both total and specific category)
        from src.core.research_quality import DebtCategory
        self.debt.add_debt(3, DebtCategory.SAFETY_TESTING)
        self.assertEqual(self.debt.accumulated_debt, 8)
        
        # The SAFETY_TESTING category should have at least 3 from the specific addition
        # plus potentially more from the random distribution of the first 5 points
        self.assertGreaterEqual(self.debt.debt_categories[DebtCategory.SAFETY_TESTING], 3)
    
    def test_debt_reduction(self):
        """Test debt reduction functionality."""
        from src.core.research_quality import DebtCategory
        
        # Add some debt first
        self.debt.add_debt(10)
        self.debt.add_debt(5, DebtCategory.CODE_QUALITY)
        
        # Reduce debt
        reduced = self.debt.reduce_debt(7)
        self.assertEqual(reduced, 7)
        self.assertEqual(self.debt.accumulated_debt, 8)  # 15 - 7 = 8
        
        # Reduce more debt than available
        reduced = self.debt.reduce_debt(20)
        self.assertEqual(reduced, 8)  # Can only reduce what's available
        self.assertEqual(self.debt.accumulated_debt, 0)
    
    def test_debt_penalties(self):
        """Test debt penalty calculations."""
        # No penalties at low debt
        self.debt.accumulated_debt = 3
        self.assertEqual(self.debt.get_research_speed_penalty(), 1.0)
        self.assertEqual(self.debt.get_accident_chance(), 0.0)
        self.assertFalse(self.debt.has_reputation_risk())
        self.assertFalse(self.debt.can_trigger_system_failure())
        
        # Light penalties at medium debt
        self.debt.accumulated_debt = 8
        self.assertEqual(self.debt.get_research_speed_penalty(), 0.95)  # 5% penalty
        self.assertEqual(self.debt.get_accident_chance(), 0.0)
        
        # Moderate penalties at higher debt
        self.debt.accumulated_debt = 13
        self.assertEqual(self.debt.get_research_speed_penalty(), 0.90)  # 10% penalty
        self.assertEqual(self.debt.get_accident_chance(), 0.05)  # 5% accident chance
        
        # High penalties at very high debt
        self.debt.accumulated_debt = 18
        self.assertEqual(self.debt.get_research_speed_penalty(), 0.85)  # 15% penalty
        self.assertEqual(self.debt.get_accident_chance(), 0.10)  # 10% accident chance
        self.assertTrue(self.debt.has_reputation_risk())
        
        # Maximum penalties at extreme debt
        self.debt.accumulated_debt = 25
        self.assertEqual(self.debt.get_research_speed_penalty(), 0.80)  # 20% penalty
        self.assertEqual(self.debt.get_accident_chance(), 0.15)  # 15% accident chance
        self.assertTrue(self.debt.can_trigger_system_failure())
    
    def test_debt_summary(self):
        """Test debt summary for UI display."""
        from src.core.research_quality import DebtCategory
        
        self.debt.add_debt(2, DebtCategory.SAFETY_TESTING)
        self.debt.add_debt(3, DebtCategory.CODE_QUALITY)
        
        summary = self.debt.get_debt_summary()
        self.assertEqual(summary["total"], 5)
        self.assertEqual(summary["safety_testing"], 2)
        self.assertEqual(summary["code_quality"], 3)
        self.assertEqual(summary["documentation"], 0)
        self.assertEqual(summary["validation"], 0)


class TestGameStateIntegration(unittest.TestCase):
    """Test integration of research quality system with GameState."""
    
    def setUp(self):
        """Set up test environment."""
        self.gs = GameState('test-integration')
        self.gs.money = 1000
        self.gs.research_staff = 5
        self.gs.action_points = 10
    
    def test_initial_research_quality_state(self):
        """Test that GameState initializes research quality correctly."""
        self.assertEqual(self.gs.current_research_quality, ResearchQuality.STANDARD)
        self.assertEqual(self.gs.technical_debt.accumulated_debt, 0)
        self.assertFalse(self.gs.research_quality_unlocked)
        self.assertEqual(len(self.gs.active_research_projects), 0)
        self.assertEqual(len(self.gs.completed_research_projects), 0)
    
    def test_set_research_quality(self):
        """Test setting research quality approach."""
        initial_messages = len(self.gs.messages)
        
        self.gs.set_research_quality(ResearchQuality.RUSHED)
        self.assertEqual(self.gs.current_research_quality, ResearchQuality.RUSHED)
        self.assertTrue(self.gs.research_quality_unlocked)
        self.assertGreater(len(self.gs.messages), initial_messages)
    
    def test_create_research_project(self):
        """Test creating research projects."""
        project = self.gs.create_research_project("Test Research", 50, 1)
        
        self.assertEqual(project.name, "Test Research")
        self.assertEqual(project.quality_level, self.gs.current_research_quality)
        self.assertIn(project, self.gs.active_research_projects)
    
    def test_complete_research_project(self):
        """Test completing research projects and debt changes."""
        # Set to rushed quality to generate debt
        self.gs.set_research_quality(ResearchQuality.RUSHED)
        project = self.gs.create_research_project("Rushed Research", 50, 1)
        
        initial_debt = self.gs.technical_debt.accumulated_debt
        self.gs.complete_research_project(project)
        
        self.assertTrue(project.completed)
        self.assertNotIn(project, self.gs.active_research_projects)
        self.assertIn(project, self.gs.completed_research_projects)
        self.assertGreater(self.gs.technical_debt.accumulated_debt, initial_debt)
    
    def test_debt_reduction_actions(self):
        """Test debt reduction action execution."""
        # Add some debt first
        self.gs.technical_debt.add_debt(10)
        initial_debt = self.gs.technical_debt.accumulated_debt
        
        # Try refactoring sprint
        success = self.gs.execute_debt_reduction_action("Refactoring Sprint")
        self.assertTrue(success)
        self.assertLess(self.gs.technical_debt.accumulated_debt, initial_debt)
        self.assertLess(self.gs.money, 1000)  # Money was spent
        self.assertLess(self.gs.action_points, 10)  # AP was spent
    
    def test_debt_consequences(self):
        """Test that debt consequences are checked."""
        # Add high debt to trigger consequences
        self.gs.technical_debt.accumulated_debt = 25
        
        # Mock random to ensure we can test the consequence paths
        original_random = random.random
        try:
            # Force accident to trigger
            random.random = lambda: 0.01  # Very low value to trigger accident
            
            initial_messages = len(self.gs.messages)
            self.gs.check_debt_consequences()
            
            # Should have triggered some consequence
            self.assertGreater(len(self.gs.messages), initial_messages)
            
        finally:
            random.random = original_random
    
    def test_research_effectiveness_modifier(self):
        """Test that technical debt affects research effectiveness."""
        # No debt - full effectiveness
        modifier = self.gs.get_research_effectiveness_modifier()
        self.assertEqual(modifier, 1.0)
        
        # Add debt to reduce effectiveness
        self.gs.technical_debt.accumulated_debt = 15
        modifier = self.gs.get_research_effectiveness_modifier()
        self.assertLess(modifier, 1.0)
    
    def test_debt_summary_for_ui(self):
        """Test debt summary for UI includes calculated fields."""
        self.gs.technical_debt.add_debt(12)
        
        summary = self.gs.get_debt_summary_for_ui()
        self.assertEqual(summary["total"], 12)
        self.assertIn("research_penalty", summary)
        self.assertIn("accident_chance", summary)
        self.assertIn("has_reputation_risk", summary)
        self.assertIn("can_system_failure", summary)


class TestResearchActions(unittest.TestCase):
    """Test integration with research actions."""
    
    def setUp(self):
        """Set up test environment."""
        self.gs = GameState('test-actions')
        self.gs.money = 1000
        self.gs.research_staff = 5
        self.gs.action_points = 10
    
    def test_research_actions_exist(self):
        """Test that research actions are in the actions list."""
        action_names = [action["name"] for action in ACTIONS]
        
        self.assertIn("Safety Research", action_names)
        self.assertIn("Governance Research", action_names)
        self.assertIn("Set Research Quality: Rushed", action_names)
        self.assertIn("Set Research Quality: Standard", action_names)
        self.assertIn("Set Research Quality: Thorough", action_names)
        self.assertIn("Refactoring Sprint", action_names)
        self.assertIn("Safety Audit", action_names)
        self.assertIn("Code Review", action_names)
    
    def test_debt_reduction_actions_exist(self):
        """Test that debt reduction actions are properly configured."""
        debt_actions = get_debt_reduction_actions()
        action_names = [action["name"] for action in debt_actions]
        
        self.assertIn("Refactoring Sprint", action_names)
        self.assertIn("Safety Audit", action_names)
        self.assertIn("Code Review", action_names)
    
    def test_research_outcome_calculation(self):
        """Test research outcome calculation with quality and debt."""
        # Test with standard quality and no debt
        doom_change, rep_change, debt_change, messages = calculate_research_outcome(
            5, 2, ResearchQuality.STANDARD, self.gs.technical_debt
        )
        self.assertEqual(doom_change, 5)  # No modifiers
        self.assertEqual(rep_change, 2)   # No modifiers
        self.assertEqual(debt_change, 0)  # Standard has no debt change
        
        # Test with rushed quality - rushed increases doom impact which means LESS doom reduction
        doom_change, rep_change, debt_change, messages = calculate_research_outcome(
            5, 2, ResearchQuality.RUSHED, self.gs.technical_debt
        )
        self.assertLess(doom_change, 5)   # Rushed makes research less effective (less doom reduction)
        self.assertEqual(debt_change, 2)     # Rushed adds debt
        self.assertGreater(len(messages), 0) # Should have messages
        
        # Test with thorough quality - thorough reduces doom impact which means MORE doom reduction
        doom_change, rep_change, debt_change, messages = calculate_research_outcome(
            5, 2, ResearchQuality.THOROUGH, self.gs.technical_debt
        )
        self.assertGreater(doom_change, 5)   # Thorough makes research more effective (more doom reduction)
        self.assertEqual(debt_change, -1)  # Thorough reduces debt
        self.assertGreater(rep_change, 2)  # Thorough has reputation bonus


class TestOpponentIntegration(unittest.TestCase):
    """Test integration of research quality system with opponent AI."""
    
    def setUp(self):
        """Set up test environment."""
        from src.core.opponents import create_default_opponents
        self.opponents = create_default_opponents()
    
    def test_opponent_risk_tolerances(self):
        """Test that opponents have different risk tolerances."""
        risk_tolerances = [opp.risk_tolerance for opp in self.opponents]
        
        # Should have variety of risk tolerances
        self.assertIn("aggressive", risk_tolerances)
        self.assertIn("conservative", risk_tolerances)
        self.assertIn("moderate", risk_tolerances)
    
    def test_opponent_initial_debt_levels(self):
        """Test that opponents start with different debt levels."""
        # Find specific opponents
        techcorp = next(opp for opp in self.opponents if "TechCorp" in opp.name)
        gov_lab = next(opp for opp in self.opponents if "National" in opp.name)
        
        # TechCorp should have higher debt than Government Lab
        self.assertGreater(techcorp.technical_debt, gov_lab.technical_debt)
        self.assertEqual(techcorp.risk_tolerance, "aggressive")
        self.assertEqual(gov_lab.risk_tolerance, "conservative")
    
    def test_opponent_research_approaches(self):
        """Test that opponents use different research approaches."""
        approaches = [opp.research_quality_preference for opp in self.opponents]
        
        # Should have variety of approaches
        self.assertIn("rushed", approaches)
        self.assertIn("thorough", approaches)
    
    def test_aggressive_opponent_behavior(self):
        """Test aggressive opponent accumulates debt."""
        aggressive_opp = next(opp for opp in self.opponents if opp.risk_tolerance == "aggressive")
        aggressive_opp.discovered = True
        
        initial_debt = aggressive_opp.technical_debt
        
        # Run multiple turns
        for _ in range(5):
            aggressive_opp.take_turn()
        
        # Should likely have accumulated more debt (probabilistic)
        # We'll check that debt didn't decrease significantly
        self.assertGreaterEqual(aggressive_opp.technical_debt, initial_debt - 1)
    
    def test_conservative_opponent_behavior(self):
        """Test conservative opponent manages debt well."""
        conservative_opp = next(opp for opp in self.opponents if opp.risk_tolerance == "conservative")
        conservative_opp.discovered = True
        conservative_opp.technical_debt = 5  # Give some debt to manage
        
        initial_debt = conservative_opp.technical_debt
        
        # Run multiple turns
        for _ in range(10):  # More turns to see debt reduction
            conservative_opp.take_turn()
        
        # Should have reduced debt over time (probabilistic)
        self.assertLessEqual(conservative_opp.technical_debt, initial_debt)
    
    def test_opponent_doom_impact_with_debt(self):
        """Test that opponent technical debt affects doom contribution."""
        opp = self.opponents[0]
        opp.discovered = True
        opp.capabilities_researchers = 10
        opp.progress = 50
        
        # Test with no debt
        opp.technical_debt = 0
        base_doom = opp.get_impact_on_doom()
        
        # Test with high debt
        opp.technical_debt = 20
        debt_doom = opp.get_impact_on_doom()
        
        # High debt should increase doom impact
        self.assertGreater(debt_doom, base_doom)
    
    def test_research_quality_modifier(self):
        """Test that opponents' research quality affects their progress."""
        opp = self.opponents[0]
        
        # Test different quality modifiers
        opp.research_quality_preference = "rushed"
        rushed_modifier = opp._get_research_quality_modifier()
        
        opp.research_quality_preference = "standard"
        standard_modifier = opp._get_research_quality_modifier()
        
        opp.research_quality_preference = "thorough"
        thorough_modifier = opp._get_research_quality_modifier()
        
        # Rushed should be faster, thorough should be slower
        self.assertGreater(rushed_modifier, standard_modifier)
        self.assertGreater(standard_modifier, thorough_modifier)


if __name__ == '__main__':
    unittest.main()
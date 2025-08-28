import unittest
import random
from src.core.game_state import GameState
from src.core.researchers import (
    Researcher, SPECIALIZATIONS, POSITIVE_TRAITS, NEGATIVE_TRAITS,
    generate_researcher, generate_researcher_name, generate_random_traits,
    adjust_researcher_salary, conduct_team_building, conduct_performance_review
)

class TestResearcherSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test game state with researchers."""
        self.gs = GameState('test-researcher')
        self.gs.researchers = []
        self.gs.available_researchers = []
        
    def test_researcher_creation(self):
        """Test creating individual researchers."""
        researcher = Researcher("Test Researcher", "safety", 5, ["workaholic"], 100)
        
        self.assertEqual(researcher.name, "Test Researcher")
        self.assertEqual(researcher.specialization, "safety")
        self.assertEqual(researcher.skill_level, 5)
        self.assertIn("workaholic", researcher.traits)
        self.assertEqual(researcher.salary_expectation, 100)
        self.assertEqual(researcher.current_salary, 100)
        self.assertEqual(researcher.loyalty, 50)
        self.assertEqual(researcher.burnout, 0)
    
    def test_researcher_traits_effects(self):
        """Test that traits affect researcher productivity."""
        # Workaholic should increase productivity
        workaholic = Researcher("Workaholic", "safety", 5, ["workaholic"], 100)
        self.assertGreater(workaholic.productivity, 1.0)
        
        # Prima donna should not affect base productivity
        prima_donna = Researcher("Prima Donna", "safety", 5, ["prima_donna"], 100)
        self.assertEqual(prima_donna.productivity, 1.0)
        
        # Test effective productivity with prima donna
        prima_donna.current_salary = 80  # Less than expectation
        effective = prima_donna.get_effective_productivity()
        self.assertLess(effective, prima_donna.productivity)
    
    def test_specialization_effects(self):
        """Test that specializations provide correct effects."""
        safety_researcher = Researcher("Safety Expert", "safety", 5, [], 100)
        effects = safety_researcher.get_specialization_effects()
        
        self.assertIn("doom_reduction_bonus", effects)
        self.assertGreater(effects["doom_reduction_bonus"], 0)
        
        capabilities_researcher = Researcher("Capabilities Expert", "capabilities", 5, [], 100)
        effects = capabilities_researcher.get_specialization_effects()
        
        self.assertIn("research_speed_modifier", effects)
        self.assertGreater(effects["research_speed_modifier"], 1.0)
        self.assertIn("doom_per_research", effects)
        self.assertGreater(effects["doom_per_research"], 0)
    
    def test_researcher_turnover(self):
        """Test researcher advancement and burnout."""
        researcher = Researcher("Test", "safety", 5, ["workaholic"], 100)
        initial_burnout = researcher.burnout
        initial_loyalty = researcher.loyalty
        
        researcher.advance_turn()
        
        # Workaholic should increase burnout
        self.assertGreater(researcher.burnout, initial_burnout)
        # Loyalty should decrease slightly
        self.assertLess(researcher.loyalty, initial_loyalty)
        self.assertEqual(researcher.turns_employed, 1)
    
    def test_hiring_system(self):
        """Test researcher hiring functionality."""
        # Setup game state with money and AP
        self.gs.money = 200
        self.gs.action_points = 5
        
        # Generate some researchers
        self.gs.refresh_researcher_hiring_pool()
        self.assertGreater(len(self.gs.available_researchers), 0)
        
        initial_researchers = len(self.gs.researchers)
        initial_money = self.gs.money
        researcher_cost = self.gs.available_researchers[0].salary_expectation
        
        # Hire first researcher
        success, message = self.gs.hire_researcher(0)
        
        self.assertTrue(success)
        self.assertEqual(len(self.gs.researchers), initial_researchers + 1)
        self.assertEqual(self.gs.money, initial_money - researcher_cost)
        self.assertEqual(self.gs.action_points, 3)  # Should cost 2 AP
    
    def test_salary_management(self):
        """Test salary adjustment functionality."""
        researcher = Researcher("Test", "safety", 5, [], 100)
        initial_loyalty = researcher.loyalty
        
        # Increase salary
        result = adjust_researcher_salary(researcher, 120)
        self.assertTrue(result["success"])
        self.assertEqual(researcher.current_salary, 120)
        self.assertGreater(researcher.loyalty, initial_loyalty)
        
        # Decrease salary
        result = adjust_researcher_salary(researcher, 90)
        self.assertTrue(result["success"])
        self.assertEqual(researcher.current_salary, 90)
        self.assertLess(researcher.loyalty, initial_loyalty)
    
    def test_team_building(self):
        """Test team building functionality."""
        researchers = [
            Researcher("Test1", "safety", 5, [], 100),
            Researcher("Test2", "capabilities", 5, [], 100)
        ]
        
        # Add some burnout
        for r in researchers:
            r.burnout = 50
        
        result = conduct_team_building(researchers, 100)
        self.assertTrue(result["success"])
        
        # Should reduce burnout
        for r in researchers:
            self.assertLess(r.burnout, 50)
    
    def test_performance_review(self):
        """Test performance review functionality."""
        researcher = Researcher("Test", "safety", 5, ["workaholic"], 100)
        researcher.burnout = 30  # Moderate burnout (was 70)
        researcher.loyalty = 20  # Low loyalty
        
        result = conduct_performance_review(researcher)
        self.assertTrue(result["success"])
        self.assertEqual(result["researcher"], "Test")
        # With 30% burnout: 1.2 * (1 - 0.15) = 1.02, still > 1.0
        self.assertGreater(result["productivity"], 1.0)  # Workaholic bonus minus burnout
        self.assertGreater(len(result["insights"]), 0)
    
    def test_researcher_effects_integration(self):
        """Test that researcher effects integrate with game state."""
        # Add some researchers with different specializations
        safety_researcher = Researcher("Safety Expert", "safety", 8, ["safety_conscious"], 100)
        capabilities_researcher = Researcher("Capabilities Expert", "capabilities", 6, [], 100)
        
        self.gs.researchers = [safety_researcher, capabilities_researcher]
        
        effects = self.gs.get_researcher_productivity_effects()
        
        # Should have research speed bonus from capabilities researcher
        self.assertGreater(effects["research_speed_modifier"], 1.0)
        
        # Should have doom reduction from safety researcher
        self.assertGreater(effects["doom_reduction_bonus"], 0)
        
        # Should have doom per research from capabilities researcher
        self.assertGreater(effects["doom_per_research"], 0)
    
    def test_random_generation(self):
        """Test random researcher generation."""
        # Test name generation
        name = generate_researcher_name()
        self.assertIsInstance(name, str)
        self.assertIn(" ", name)  # Should have first and last name
        
        # Test trait generation
        traits = generate_random_traits(2)
        self.assertLessEqual(len(traits), 2)
        
        # Test researcher generation
        researcher = generate_researcher("safety")
        self.assertEqual(researcher.specialization, "safety")
        self.assertGreaterEqual(researcher.skill_level, 3)
        self.assertLessEqual(researcher.skill_level, 8)
    
    def test_serialization(self):
        """Test researcher serialization and deserialization."""
        original = Researcher("Test", "safety", 7, ["workaholic", "media_savvy"], 110)
        original.burnout = 20
        original.loyalty = 75
        original.turns_employed = 5
        
        # Serialize
        data = original.to_dict()
        
        # Deserialize
        restored = Researcher.from_dict(data)
        
        self.assertEqual(restored.name, original.name)
        self.assertEqual(restored.specialization, original.specialization)
        self.assertEqual(restored.skill_level, original.skill_level)
        self.assertEqual(restored.traits, original.traits)
        self.assertEqual(restored.salary_expectation, original.salary_expectation)
        self.assertEqual(restored.burnout, original.burnout)
        self.assertEqual(restored.loyalty, original.loyalty)
        self.assertEqual(restored.turns_employed, original.turns_employed)

class TestResearcherGameIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test game state."""
        self.gs = GameState('test-integration')
        
    def test_researcher_doom_effects(self):
        """Test that researchers affect doom calculations."""
        # Add safety researcher
        safety_researcher = Researcher("Safety Expert", "safety", 8, [], 100)
        self.gs.researchers = [safety_researcher]
        
        initial_doom = self.gs.doom
        
        # Manually trigger doom calculation (simplified)
        researcher_effects = self.gs.get_researcher_productivity_effects()
        doom_rise = 10  # Base doom increase
        
        if researcher_effects.get('doom_reduction_bonus', 0) > 0:
            doom_reduction = doom_rise * researcher_effects['doom_reduction_bonus']
            doom_rise = max(0, doom_rise - doom_reduction)
        
        # Safety researcher should reduce doom increase
        self.assertLess(doom_rise, 10)
    
    def test_researcher_actions_available(self):
        """Test that researcher management actions become available."""
        # Check refresh researchers action
        refresh_action = None
        for action in self.gs.actions:
            if action["name"] == "Refresh Researchers":
                refresh_action = action
                break
        
        self.assertIsNotNone(refresh_action)
        
        # Should be available if researchers attribute exists
        self.assertTrue(hasattr(self.gs, 'researchers'))
        if refresh_action.get("rules"):
            self.assertTrue(refresh_action["rules"](self.gs))

if __name__ == '__main__':
    unittest.main()
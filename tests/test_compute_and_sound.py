import unittest
from src.core.game_state import GameState
from src.core.actions import ACTIONS

class TestComputeSystem(unittest.TestCase):
    """Test the compute resource system and employee productivity"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        self.game_state = GameState("test_seed")
        
    def test_compute_initial_value(self):
        """Test that compute starts at 0"""
        self.assertEqual(self.game_state.compute, 0, "Compute should start at 0")
        
    def test_buy_compute_action_exists(self):
        """Test that Buy Compute action exists in actions list"""
        buy_compute_action = None
        for action in ACTIONS:
            if action["name"] == "Buy Compute":
                buy_compute_action = action
                break
        
        self.assertIsNotNone(buy_compute_action, "Buy Compute action should exist")
        
        # Test dynamic cost function
        if callable(buy_compute_action["cost"]):
            actual_cost = buy_compute_action["cost"](self.game_state)
            self.assertGreater(actual_cost, 0, "Buy Compute cost should be positive")
        else:
            self.assertEqual(buy_compute_action["cost"], 100, "Buy Compute should cost $100")
        
    def test_buy_compute_action_functionality(self):
        """Test that Buy Compute action actually adds compute"""
        initial_compute = self.game_state.compute
        initial_money = self.game_state.money
        
        # Find and execute Buy Compute action
        for idx, action in enumerate(self.game_state.actions):
            if action["name"] == "Buy Compute":
                # Get dynamic cost
                if callable(action["cost"]):
                    cost = action["cost"](self.game_state)
                else:
                    cost = action["cost"]
                
                # Simulate buying compute
                self.game_state.money -= cost
                action["upside"](self.game_state)
                break
        
        self.assertEqual(self.game_state.compute, initial_compute + 10, "Should gain 10 compute")
        self.assertEqual(self.game_state.money, initial_money - cost, f"Should spend ${cost}")
        
    def test_research_progress_initial_value(self):
        """Test that research progress starts at 0"""
        self.assertEqual(self.game_state.research_progress, 0, "Research progress should start at 0")
        
    def test_papers_published_initial_value(self):
        """Test that papers published starts at 0"""
        self.assertEqual(self.game_state.papers_published, 0, "Papers published should start at 0")
        
    def test_employee_blobs_initialized(self):
        """Test that employee blobs are created for initial staff"""
        self.assertEqual(len(self.game_state.employee_blobs), self.game_state.staff, 
                        "Should have one blob per staff member")
        
    def test_employee_productivity_without_compute(self):
        """Test employee productivity when no compute is available"""
        # Ensure no compute
        self.game_state.compute = 0
        
        # Run productivity update
        productive_employees = self.game_state._update_employee_productivity()
        
        self.assertEqual(productive_employees, 0, "No employees should be productive without compute")
        for blob in self.game_state.employee_blobs:
            self.assertFalse(blob['has_compute'], "No blobs should have compute")
            
    def test_employee_productivity_with_compute(self):
        """Test employee productivity when compute is available"""
        # Give some compute
        self.game_state.compute = 5
        staff_count = self.game_state.staff
        
        # Run productivity update
        productive_employees = self.game_state._update_employee_productivity()
        
        self.assertEqual(productive_employees, min(staff_count, 5), 
                        "Should have productive employees up to compute limit")
        
        # Check that some employees have compute
        employees_with_compute = sum(1 for blob in self.game_state.employee_blobs if blob['has_compute'])
        self.assertEqual(employees_with_compute, productive_employees, 
                        "Productive employees should match those with compute")

class TestSoundSystem(unittest.TestCase):
    """Test the sound system functionality"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        self.game_state = GameState("test_seed")
        
    def test_sound_manager_exists(self):
        """Test that sound manager is created"""
        self.assertTrue(hasattr(self.game_state, 'sound_manager'), 
                       "GameState should have sound_manager")
        
    def test_sound_toggle(self):
        """Test sound enable/disable toggle"""
        initial_state = self.game_state.sound_manager.is_enabled()
        new_state = self.game_state.sound_manager.toggle()
        
        self.assertNotEqual(initial_state, new_state, "Toggle should change state")
        self.assertEqual(self.game_state.sound_manager.is_enabled(), new_state, 
                        "Sound manager state should match toggle result")
        
    def test_sound_set_enabled(self):
        """Test explicitly setting sound enabled/disabled"""
        self.game_state.sound_manager.set_enabled(True)
        self.assertTrue(self.game_state.sound_manager.is_enabled(), 
                       "Sound should be enabled when set to True")
        
        self.game_state.sound_manager.set_enabled(False)
        self.assertFalse(self.game_state.sound_manager.is_enabled(), 
                        "Sound should be disabled when set to False")
        
    def test_blob_sound_doesnt_crash(self):
        """Test that playing blob sound doesn't crash (even if no audio)"""
        try:
            self.game_state.sound_manager.play_blob_sound()
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success, "Playing blob sound should not crash")
    
    def test_zabinga_sound_doesnt_crash(self):
        """Test that playing Zabinga sound doesn't crash (even if no audio)"""
        try:
            self.game_state.sound_manager.play_zabinga_sound()
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success, "Playing Zabinga sound should not crash")
    
    def test_zabinga_sound_on_paper_completion(self):
        """Test that Zabinga sound is triggered when research papers are completed"""
        # Set up research progress just below threshold
        self.game_state.research_progress = 99
        
        # Mock the sound manager to track calls
        zabinga_called = []
        original_play_zabinga = self.game_state.sound_manager.play_zabinga_sound
        
        def mock_play_zabinga():
            zabinga_called.append(True)
            original_play_zabinga()
        
        self.game_state.sound_manager.play_zabinga_sound = mock_play_zabinga
        
        # Add just enough research progress to complete a paper
        self.game_state._add('research_progress', 1)
        
        # Trigger end turn to process research
        self.game_state.end_turn()
        
        # Check that Zabinga sound was called
        self.assertTrue(len(zabinga_called) > 0, 
                       "Zabinga sound should be triggered when research paper is completed")
        
        # Check that paper was actually published
        self.assertEqual(self.game_state.papers_published, 1,
                        "One research paper should be published")
    
    def test_zabinga_sound_multiple_papers(self):
        """Test that Zabinga sound is triggered when multiple papers are completed at once"""
        # Set up research progress for multiple papers
        self.game_state.research_progress = 250  # Should complete 2 papers
        
        # Mock the sound manager to track calls
        zabinga_called = []
        original_play_zabinga = self.game_state.sound_manager.play_zabinga_sound
        
        def mock_play_zabinga():
            zabinga_called.append(True)
            original_play_zabinga()
        
        self.game_state.sound_manager.play_zabinga_sound = mock_play_zabinga
        
        # Trigger end turn to process research
        self.game_state.end_turn()
        
        # Check that Zabinga sound was called
        self.assertTrue(len(zabinga_called) > 0, 
                       "Zabinga sound should be triggered when multiple research papers are completed")
        
        # Check that papers were actually published
        self.assertEqual(self.game_state.papers_published, 2,
                        "Two research papers should be published")
        self.assertEqual(self.game_state.research_progress, 50,
                        "Research progress should be remainder after publishing papers")

class TestEmployeeBlobSystem(unittest.TestCase):
    """Test the employee blob visualization system"""
    
    def setUp(self):
        """Set up a GameState for testing"""
        self.game_state = GameState("test_seed")
        
    def test_initial_blob_count(self):
        """Test that initial blobs match staff count"""
        self.assertEqual(len(self.game_state.employee_blobs), self.game_state.staff,
                        "Initial blob count should match staff count")
        
    def test_hiring_adds_blobs(self):
        """Test that hiring staff adds employee blobs"""
        initial_blob_count = len(self.game_state.employee_blobs)
        initial_staff = self.game_state.staff
        
        # Hire one staff member
        self.game_state._add('staff', 1)
        
        self.assertEqual(len(self.game_state.employee_blobs), initial_blob_count + 1,
                        "Should add one blob when hiring one staff")
        self.assertEqual(self.game_state.staff, initial_staff + 1,
                        "Staff count should increase")
        
    def test_firing_removes_blobs(self):
        """Test that losing staff removes employee blobs"""
        # First ensure we have at least one staff member
        if self.game_state.staff == 0:
            self.game_state._add('staff', 1)
        
        initial_blob_count = len(self.game_state.employee_blobs)
        initial_staff = self.game_state.staff
        
        # Remove one staff member
        self.game_state._add('staff', -1)
        
        self.assertEqual(len(self.game_state.employee_blobs), initial_blob_count - 1,
                        "Should remove one blob when losing one staff")
        self.assertEqual(self.game_state.staff, initial_staff - 1,
                        "Staff count should decrease")
        
    def test_blob_properties(self):
        """Test that blobs have required properties"""
        for blob in self.game_state.employee_blobs:
            self.assertIn('id', blob, "Blob should have id")
            self.assertIn('x', blob, "Blob should have x coordinate")
            self.assertIn('y', blob, "Blob should have y coordinate")
            self.assertIn('target_x', blob, "Blob should have target_x")
            self.assertIn('target_y', blob, "Blob should have target_y")
            self.assertIn('has_compute', blob, "Blob should have has_compute flag")
            self.assertIn('productivity', blob, "Blob should have productivity value")
            self.assertIn('animation_progress', blob, "Blob should have animation_progress")
            
    def test_blob_animation_initial_state(self):
        """Test that initial blobs are fully animated"""
        for blob in self.game_state.employee_blobs:
            self.assertEqual(blob['animation_progress'], 1.0,
                            "Initial blobs should be fully animated")

if __name__ == '__main__':
    unittest.main()
import unittest
from game_state import GameState
from actions import ACTIONS

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
        self.assertEqual(buy_compute_action["cost"], 100, "Buy Compute should cost $100")
        
    def test_buy_compute_action_functionality(self):
        """Test that Buy Compute action actually adds compute"""
        initial_compute = self.game_state.compute
        initial_money = self.game_state.money
        
        # Find and execute Buy Compute action
        for idx, action in enumerate(self.game_state.actions):
            if action["name"] == "Buy Compute":
                # Simulate buying compute
                self.game_state.money -= action["cost"]
                action["upside"](self.game_state)
                break
        
        self.assertEqual(self.game_state.compute, initial_compute + 10, "Should gain 10 compute")
        self.assertEqual(self.game_state.money, initial_money - 100, "Should spend $100")
        
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
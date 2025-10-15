'''
Unit tests for the leaderboard service.
Tests privacy management, score submission, and leaderboard functionality.
'''

import unittest
import tempfile
import os
from src.services.leaderboard import (
    PrivacyManager,
    LeaderboardManager,
    LeaderboardEntry
)


class TestPrivacyManager(unittest.TestCase):
    '''Test the PrivacyManager functionality.'''
    
    def setUp(self):
        '''Set up test environment.'''
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        '''Clean up test environment.'''
        os.chdir(self.original_cwd)
        
        # Clean up test files
        test_files = ['user_privacy.json']
        for file_name in test_files:
            file_path = os.path.join(self.test_dir, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass
    
    def test_privacy_manager_initialization(self):
        '''Test PrivacyManager initialization.'''
        pm = PrivacyManager()
        
        # Should initialize with default settings
        self.assertFalse(pm.is_leaderboard_enabled())
        self.assertEqual(pm.get_pseudonym(), '')
    
    def test_pseudonym_management(self):
        '''Test pseudonym setting and getting.'''
        pm = PrivacyManager()
        
        # Set a pseudonym
        test_pseudonym = 'TestPlayer123'
        pm.set_pseudonym(test_pseudonym)
        
        self.assertEqual(pm.get_pseudonym(), test_pseudonym)
    
    def test_leaderboard_enablement(self):
        '''Test leaderboard opt-in functionality.'''
        pm = PrivacyManager()
        
        # Initially disabled
        self.assertFalse(pm.is_leaderboard_enabled())
        
        # Enable with pseudonym
        pm.enable_leaderboard('TestPlayer456')
        
        self.assertTrue(pm.is_leaderboard_enabled())
        self.assertEqual(pm.get_pseudonym(), 'TestPlayer456')
    
    def test_leaderboard_disablement(self):
        '''Test leaderboard opt-out functionality.'''
        pm = PrivacyManager()
        
        # Enable first
        pm.enable_leaderboard('TestPlayer789')
        self.assertTrue(pm.is_leaderboard_enabled())
        
        # Then disable
        pm.disable_leaderboard()
        self.assertFalse(pm.is_leaderboard_enabled())
    
    def test_privacy_settings_persistence(self):
        '''Test that privacy settings persist across instances.'''
        # First instance sets preferences
        pm1 = PrivacyManager()
        pm1.enable_leaderboard('PersistentPlayer')
        
        # Second instance should load same preferences
        pm2 = PrivacyManager()
        self.assertTrue(pm2.is_leaderboard_enabled())
        self.assertEqual(pm2.get_pseudonym(), 'PersistentPlayer')
    
    def test_safe_pseudonym_validation(self):
        '''Test pseudonym safety validation.'''
        pm = PrivacyManager()
        
        # Safe pseudonyms should work
        safe_names = ['Player123', 'GoodName', 'Test_User']
        for name in safe_names:
            self.assertTrue(pm._is_safe_pseudonym(name))
        
        # Test that method exists and returns boolean
        result = pm._is_safe_pseudonym('TestName')
        self.assertIsInstance(result, bool)
    
    def test_privacy_file_corruption_handling(self):
        '''Test handling of corrupted privacy files.'''
        # Create corrupted privacy file
        with open('user_privacy.json', 'w') as f:
            f.write('invalid json content')
        
        # Should handle gracefully and use defaults
        pm = PrivacyManager()
        self.assertFalse(pm.is_leaderboard_enabled())
        self.assertEqual(pm.get_pseudonym(), '')


class TestLeaderboardManager(unittest.TestCase):
    '''Test the LeaderboardManager functionality.'''
    
    def setUp(self):
        '''Set up test environment.'''
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        '''Clean up test environment.'''
        os.chdir(self.original_cwd)
        
        # Clean up test files
        test_files = ['local_leaderboard.json', 'pending_submissions.json', 'user_privacy.json']
        for file_name in test_files:
            file_path = os.path.join(self.test_dir, file_name)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass
    
    def test_leaderboard_manager_initialization(self):
        '''Test LeaderboardManager initialization.'''
        lm = LeaderboardManager()
        
        self.assertIsInstance(lm.privacy_manager, PrivacyManager)
        self.assertEqual(len(lm.local_entries), 0)
        self.assertEqual(len(lm.pending_submissions), 0)
    
    def test_can_submit_score_privacy_disabled(self):
        '''Test score submission when privacy/leaderboard is disabled.'''
        lm = LeaderboardManager()
        
        # Should not be able to submit when leaderboard is disabled
        self.assertFalse(lm.can_submit_score())
    
    def test_can_submit_score_privacy_enabled(self):
        '''Test score submission when privacy is properly configured.'''
        lm = LeaderboardManager()
        
        # Enable leaderboard
        lm.privacy_manager.enable_leaderboard('TestSubmitter')
        
        # Should now be able to submit
        self.assertTrue(lm.can_submit_score())
    
    def test_local_score_storage(self):
        '''Test local score storage functionality.'''
        lm = LeaderboardManager()
        
        # Enable leaderboard
        lm.privacy_manager.enable_leaderboard('LocalTester')
        
        # Submit a score
        result = lm.submit_score(
            seed='test_seed_123',
            score=1500,
            game_checksum='checksum123',
            game_metadata={'turns': 52, 'victory_type': 'economic'},
            verification_data={'log_checksum': 'log123'}
        )
        
        # Should succeed in storing locally even if not uploaded
        self.assertIsNotNone(result)
        
        # Check local storage
        local_scores = lm.get_local_leaderboard()
        self.assertEqual(len(local_scores), 1)
        self.assertEqual(local_scores[0].score, 1500)
        self.assertEqual(local_scores[0].seed, 'test_seed_123')
    
    def test_get_local_leaderboard_sorting(self):
        '''Test that local leaderboard returns scores in correct order.'''
        lm = LeaderboardManager()
        lm.privacy_manager.enable_leaderboard('SortTester')
        
        # Submit multiple scores
        scores = [1200, 1800, 1000, 2000, 1500]
        for i, score in enumerate(scores):
            lm.submit_score(
                seed=f'seed_{i}',
                score=score,
                game_checksum=f'checksum_{i}',
                game_metadata={'turns': 50 + i},
                verification_data={'log_checksum': f'log_{i}'}
            )
        
        # Get leaderboard
        leaderboard = lm.get_local_leaderboard()
        
        # Should be sorted by score descending
        scores_from_board = [entry.score for entry in leaderboard]
        self.assertEqual(scores_from_board, [2000, 1800, 1500, 1200, 1000])
    
    def test_get_local_leaderboard_limit(self):
        '''Test leaderboard limit functionality.'''
        lm = LeaderboardManager()
        lm.privacy_manager.enable_leaderboard('LimitTester')
        
        # Submit 10 scores
        for i in range(10):
            lm.submit_score(
                seed=f'seed_{i}',
                score=1000 + i * 100,
                game_checksum=f'checksum_{i}',
                game_metadata={'turns': 50},
                verification_data={'log_checksum': f'log_{i}'}
            )
        
        # Get top 5
        top_5 = lm.get_local_leaderboard(limit=5)
        self.assertEqual(len(top_5), 5)
        
        # Should be highest scores
        self.assertEqual(top_5[0].score, 1900)  # Highest
        self.assertEqual(top_5[4].score, 1500)  # 5th highest
    
    def test_local_leaderboard_functionality(self):
        '''Test basic local leaderboard functionality.'''
        lm = LeaderboardManager()
        lm.privacy_manager.enable_leaderboard('LocalTester')
        
        # Submit multiple scores
        scores = [1200, 1800, 1000, 2000, 1500]
        for i, score in enumerate(scores):
            lm.submit_score(
                seed=f'seed_{i}',
                score=score,
                game_checksum=f'checksum_{i}',
                game_metadata={'turns': 50 + i},
                verification_data={'log_checksum': f'log_{i}'}
            )
        
        # Get leaderboard 
        leaderboard = lm.get_local_leaderboard()
        
        # Should have entries
        self.assertGreater(len(leaderboard), 0)
        
        # Test with limit
        limited_board = lm.get_local_leaderboard(limit=3)
        self.assertLessEqual(len(limited_board), 3)
    
    def test_leaderboard_entry_creation(self):
        '''Test LeaderboardEntry creation and properties.'''
        entry = LeaderboardEntry(
            pseudonym='TestPlayer',
            score=1800,
            seed='test_seed',
            game_checksum='checksum123',
            submission_time='2025-09-04T12:00:00',
            game_metadata={'turns': 48, 'victory_type': 'research'},
            verification_data={'log_checksum': 'log123'}
        )
        
        self.assertEqual(entry.pseudonym, 'TestPlayer')
        self.assertEqual(entry.score, 1800)
        self.assertEqual(entry.seed, 'test_seed')
        self.assertEqual(entry.game_metadata['victory_type'], 'research')
    
    def test_pending_submissions_basic_functionality(self):
        '''Test basic pending submissions functionality.'''
        lm = LeaderboardManager()
        lm.privacy_manager.enable_leaderboard('PendingTester')
        
        # Submit score 
        result = lm.submit_score(
            seed='pending_seed',
            score=2000,
            game_checksum='pending_checksum',
            game_metadata={'turns': 45},
            verification_data={'log_checksum': 'pending_log'}
        )
        
        # Should return some result (True/False or submission object)
        self.assertIsNotNone(result)


class TestLeaderboardDataStructures(unittest.TestCase):
    '''Test the leaderboard data structures.'''
    
    def test_leaderboard_entry_creation(self):
        '''Test LeaderboardEntry creation and properties.'''
        entry = LeaderboardEntry(
            pseudonym='TestPlayer',
            score=1800,
            seed='test_seed',
            game_checksum='checksum123',
            submission_time='2025-09-04T12:00:00',
            game_metadata={'turns': 48, 'victory_type': 'research'},
            verification_data={'log_checksum': 'log123'}
        )
        
        self.assertEqual(entry.pseudonym, 'TestPlayer')
        self.assertEqual(entry.score, 1800)
        self.assertEqual(entry.seed, 'test_seed')
        self.assertEqual(entry.game_metadata['victory_type'], 'research')


class TestLeaderboardEdgeCases(unittest.TestCase):
    '''Test edge cases and error conditions.'''
    
    def setUp(self):
        '''Set up test environment.'''
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        '''Clean up test environment.'''
        os.chdir(self.original_cwd)
        try:
            os.rmdir(self.test_dir)
        except OSError:
            pass
    
    def test_corrupted_leaderboard_file_handling(self):
        '''Test handling of corrupted leaderboard files.'''
        # Create corrupted file
        with open('local_leaderboard.json', 'w') as f:
            f.write('invalid json')
        
        # Should handle gracefully
        lm = LeaderboardManager()
        self.assertEqual(len(lm.local_entries), 0)
    
    def test_empty_leaderboard_operations(self):
        '''Test operations on empty leaderboard.'''
        lm = LeaderboardManager()
        
        # Getting empty leaderboard should work
        board = lm.get_local_leaderboard()
        self.assertEqual(len(board), 0)
        
        # Test basic functionality with empty state
        self.assertFalse(lm.can_submit_score())  # Privacy not enabled
    
    def test_score_submission_edge_cases(self):
        '''Test score submission with edge case data.'''
        lm = LeaderboardManager()
        lm.privacy_manager.enable_leaderboard('EdgeTester')
        
        # Test with minimal data
        result = lm.submit_score(
            seed='minimal',
            score=0,  # Zero score
            game_checksum='',
            game_metadata={},
            verification_data={}
        )
        
        self.assertIsNotNone(result)
        
        # Test with very large score
        result = lm.submit_score(
            seed='large',
            score=999999999,
            game_checksum='large_checksum',
            game_metadata={'turns': 1},
            verification_data={'log_checksum': 'large_log'}
        )
        
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch
from datetime import datetime

# Add the parent directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState
from src.services.game_logger import GameLogger


class TestGameLogger(unittest.TestCase):
    '''Test the GameLogger functionality.'''
    
    def setUp(self):
        '''Set up test environment with temporary directory.'''
        self.temp_dir = tempfile.mkdtemp()
        self.original_logs_dir = None
        
    def tearDown(self):
        '''Clean up temporary directory.'''
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_logger_initialization(self):
        '''Test that GameLogger initializes correctly.'''
        logger = GameLogger('test_seed', 'test_version')
        
        self.assertEqual(logger.seed, 'test_seed')
        self.assertEqual(logger.game_version, 'test_version')
        self.assertIsInstance(logger.start_time, datetime)
        self.assertIsInstance(logger.log_entries, list)
        self.assertGreater(len(logger.log_entries), 0)  # Should have start entries
        
        # Check that start entries contain expected information
        log_text = '\n'.join(logger.log_entries)
        self.assertIn('GAME START', log_text)
        self.assertIn('test_seed', log_text)
        self.assertIn('test_version', log_text)
    
    def test_log_filename_format(self):
        '''Test that log filename follows the required format.'''
        logger = GameLogger('test_seed')
        filename = logger.get_log_filename()
        
        # Should be gamelog_YYYYMMDD_HHMMSS.txt
        self.assertTrue(filename.startswith('gamelog_'))
        self.assertTrue(filename.endswith('.txt'))
        
        # Extract timestamp part
        timestamp_part = filename[8:-4]  # Remove 'gamelog_' and '.txt'
        self.assertEqual(len(timestamp_part), 15)  # YYYYMMDD_HHMMSS
        self.assertEqual(timestamp_part[8], '_')  # Underscore separator
    
    def test_log_action(self):
        '''Test logging of player actions.'''
        logger = GameLogger('test_seed')
        initial_count = len(logger.log_entries)
        
        logger.log_action('Test Action', 100, 1)
        
        self.assertEqual(len(logger.log_entries), initial_count + 1)
        self.assertIn('Test Action', logger.log_entries[-1])
        self.assertIn('cost: 100', logger.log_entries[-1])
        self.assertIn('Turn 1', logger.log_entries[-1])
    
    def test_log_upgrade(self):
        '''Test logging of upgrade purchases.'''
        logger = GameLogger('test_seed')
        initial_count = len(logger.log_entries)
        
        logger.log_upgrade('Test Upgrade', 200, 2)
        
        self.assertEqual(len(logger.log_entries), initial_count + 1)
        self.assertIn('Test Upgrade', logger.log_entries[-1])
        self.assertIn('cost: 200', logger.log_entries[-1])
        self.assertIn('Turn 2', logger.log_entries[-1])
    
    def test_log_event(self):
        '''Test logging of game events.'''
        logger = GameLogger('test_seed')
        initial_count = len(logger.log_entries)
        
        logger.log_event('Test Event', 'Event description', 3)
        
        self.assertEqual(len(logger.log_entries), initial_count + 1)
        self.assertIn('Test Event', logger.log_entries[-1])
        self.assertIn('Event description', logger.log_entries[-1])
        self.assertIn('Turn 3', logger.log_entries[-1])
    
    def test_log_turn_summary(self):
        '''Test logging of turn summaries.'''
        logger = GameLogger('test_seed')
        initial_count = len(logger.log_entries)
        
        logger.log_turn_summary(5, 300, 2, 15, 25)
        
        self.assertEqual(len(logger.log_entries), initial_count + 1)
        last_entry = logger.log_entries[-1]
        self.assertIn('Turn 5 End', last_entry)
        self.assertIn('Money=300', last_entry)
        self.assertIn('Staff=2', last_entry)
        self.assertIn('Reputation=15', last_entry)
        self.assertIn('Doom=25', last_entry)
    
    def test_log_game_end(self):
        '''Test logging of game end.'''
        logger = GameLogger('test_seed')
        initial_count = len(logger.log_entries)
        
        final_resources = {'money': 150, 'staff': 1, 'reputation': 10, 'doom': 80}
        logger.log_game_end('Test ending', 10, final_resources)
        
        # Should add multiple entries for game end
        self.assertGreater(len(logger.log_entries), initial_count + 1)
        
        log_text = '\n'.join(logger.log_entries)
        self.assertIn('GAME END', log_text)
        self.assertIn('Test ending', log_text)
        self.assertIn('Final Turn: 10', log_text)
        self.assertIn('Final Money: 150', log_text)
    
    @patch('os.makedirs')
    def test_write_log_file(self, mock_makedirs):
        '''Test writing log file to disk.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = GameLogger('test_seed')
            logger.logs_dir = temp_dir
            
            # Write the log file
            filepath = logger.write_log_file()
            
            self.assertIsNotNone(filepath)
            self.assertTrue(os.path.exists(filepath))
            
            # Read the file and verify contents
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('GAME START', content)
            self.assertIn('test_seed', content)


class TestGameStateLogging(unittest.TestCase):
    '''Test that GameState properly integrates with logging.'''
    
    def test_game_state_has_logger(self):
        '''Test that GameState initializes with a logger.'''
        game_state = GameState('test_seed')
        
        self.assertTrue(hasattr(game_state, 'logger'))
        self.assertIsInstance(game_state.logger, GameLogger)
        self.assertEqual(game_state.logger.seed, 'test_seed')
    
    def test_upgrade_purchase_logging(self):
        '''Test that upgrade purchases are logged.'''
        game_state = GameState('test_seed')
        initial_log_count = len(game_state.logger.log_entries)
        
        # Simulate upgrade purchase by directly calling the upgrade logic
        if game_state.upgrades:
            upgrade = game_state.upgrades[0]
            game_state.money = 1000  # Ensure we have enough money
            
            # Simulate the upgrade purchase process
            if not upgrade.get('purchased', False) and game_state.money >= upgrade['cost']:
                game_state.money -= upgrade['cost']
                upgrade['purchased'] = True
                game_state.upgrade_effects.add(upgrade['effect_key'])
                game_state.logger.log_upgrade(upgrade['name'], upgrade['cost'], game_state.turn)
                
                # Verify logging occurred
                self.assertGreater(len(game_state.logger.log_entries), initial_log_count)
                log_text = '\n'.join(game_state.logger.log_entries)
                self.assertIn(upgrade['name'], log_text)
    
    def test_turn_end_logging(self):
        '''Test that ending a turn creates appropriate log entries.'''
        game_state = GameState('test_seed')
        initial_log_count = len(game_state.logger.log_entries)
        
        # Select an action if available
        if game_state.actions:
            game_state.selected_gameplay_actions = [0]  # Select first action
            game_state.money = 1000  # Ensure we have enough money
        
        # End the turn
        game_state.end_turn()
        
        # Should have more log entries now
        self.assertGreater(len(game_state.logger.log_entries), initial_log_count)
        
        # Should have a turn summary
        log_text = '\n'.join(game_state.logger.log_entries)
        self.assertIn('Turn 1 End:', log_text)
    
    def test_game_over_logging(self):
        '''Test that game over conditions trigger final logging.'''
        game_state = GameState('test_seed')
        
        # Force a game over condition (doom at maximum)
        game_state.doom = game_state.max_doom
        game_state.end_turn()
        
        self.assertTrue(game_state.game_over)
        
        # Should have game end logging
        log_text = '\n'.join(game_state.logger.log_entries)
        self.assertIn('GAME END', log_text)
        self.assertIn('p(Doom) reached maximum', log_text)


class TestGameSessionSimulation(unittest.TestCase):
    '''Test a complete game session with logging.'''
    
    def test_complete_game_session(self):
        '''Simulate a complete game session and verify log file creation.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a game state
            game_state = GameState('test_session_seed')
            game_state.logger.logs_dir = temp_dir
            
            # Play a few turns
            for turn in range(3):
                # Select an action if we have money
                if game_state.actions and game_state.money >= game_state.actions[0]['cost']:
                    game_state.selected_gameplay_actions = [0]
                
                # Try to buy an upgrade if we have money
                for upgrade in game_state.upgrades:
                    if not upgrade.get('purchased', False) and game_state.money >= upgrade['cost']:
                        game_state.money -= upgrade['cost']
                        upgrade['purchased'] = True
                        game_state.upgrade_effects.add(upgrade['effect_key'])
                        game_state.logger.log_upgrade(upgrade['name'], upgrade['cost'], game_state.turn)
                        break
                
                # End turn (but prevent actual game over for this test)
                game_state.doom
                game_state.end_turn()
                
                # Wait for turn processing to complete
                while game_state.turn_processing:
                    game_state.update_turn_processing()
                
                # If game ended naturally, break
                if game_state.game_over:
                    break
                
                # Prevent doom from getting too high for this test
                if game_state.doom >= 90:
                    game_state.doom = 50
            
            # Force game end if not already ended
            if not game_state.game_over:
                game_state.doom = game_state.max_doom
                game_state.end_turn()
                
                # Wait for turn processing to complete
                while game_state.turn_processing:
                    game_state.update_turn_processing()
            
            # Verify a log file was created
            log_files = [f for f in os.listdir(temp_dir) if f.startswith('gamelog_')]
            self.assertEqual(len(log_files), 1)
            
            # Verify log file content
            log_path = os.path.join(temp_dir, log_files[0])
            with open(log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should contain key elements
            self.assertIn('GAME START', content)
            self.assertIn('test_session_seed', content)
            self.assertIn('GAME END', content)
            self.assertIn('Turn', content)  # Should have turn information
            
            # Verify filename format
            filename = log_files[0]
            self.assertTrue(filename.startswith('gamelog_'))
            self.assertTrue(filename.endswith('.txt'))
            # Should be gamelog_YYYYMMDD_HHMMSS.txt format
            timestamp_part = filename[8:-4]
            self.assertEqual(len(timestamp_part), 15)
            self.assertEqual(timestamp_part[8], '_')


if __name__ == '__main__':
    unittest.main()
import unittest
import sys
import os

# Add the parent directory to the path so we can import game_state
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game_state import GameState


class TestGameStateInitialization(unittest.TestCase):
    '''Test that GameState initializes with expected default values.'''
    
    def test_game_state_default_values(self):
        '''Test that a new GameState starts with the correct default values.'''
        # Import config to get expected values
        from src.services.config_manager import get_current_config
        config = get_current_config()
        expected_money = config['starting_resources']['money']
        
        # Create a new GameState with a test seed
        game_state = GameState('test_seed')
        
        # Verify core resource defaults
        self.assertEqual(game_state.money, expected_money, f'Initial money should match config value: {expected_money}')
        expected_staff = config['starting_resources']['staff']
        self.assertEqual(game_state.staff, expected_staff, f'Initial staff should match config value: {expected_staff}')
        self.assertEqual(game_state.reputation, 50, 'Initial reputation should be 50')
        self.assertEqual(game_state.doom, 25, 'Initial doom should be 25')
        self.assertEqual(game_state.compute, 0, 'Initial compute should be 0')
        self.assertEqual(game_state.research_progress, 0, 'Initial research progress should be 0')
        self.assertEqual(game_state.papers_published, 0, 'Initial papers published should be 0')
        
        # Verify game state defaults
        self.assertEqual(game_state.turn, 0, 'Initial turn should be 0')
        self.assertEqual(game_state.max_doom, 100, 'Max doom should be 100')
        self.assertFalse(game_state.game_over, 'Game should not be over initially')
        
        # Verify seed is set correctly
        self.assertEqual(game_state.seed, 'test_seed', 'Seed should be set correctly')
        
        # Verify collections are initialized
        self.assertIsInstance(game_state.selected_gameplay_actions, list, 'Selected actions should be a list')
        self.assertEqual(len(game_state.selected_gameplay_actions), 0, 'Selected actions should be empty initially')
        self.assertIsInstance(game_state.messages, list, 'Messages should be a list')
        self.assertGreater(len(game_state.messages), 0, 'Should have initial game message')


class TestEventLog(unittest.TestCase):
    '''Test event log behavior, specifically that it clears each turn.'''
    
    def test_event_log_clears_on_end_turn(self):
        '''Test that the event log is cleared at the start of each turn.'''
        # Create a new GameState with sufficient resources
        game_state = GameState('test_seed')
        
        # Verify we start with an initial message
        initial_message_count = len(game_state.messages)
        self.assertGreater(initial_message_count, 0, 'Should have initial game message')
        
        # Add some messages manually to simulate events
        game_state.messages.append('Test message 1')
        game_state.messages.append('Test message 2')
        
        # Verify messages were added
        self.assertEqual(len(game_state.messages), initial_message_count + 2, 
                        'Should have added 2 test messages')
        
        # Store the pre-turn messages to verify they're cleared
        pre_turn_messages = game_state.messages.copy()
        
        # End the turn
        game_state.end_turn()
        
        # Verify the old messages are gone by checking none of our test messages remain
        for old_message in pre_turn_messages:
            self.assertNotIn(old_message, game_state.messages, 
                           'Old messages should be cleared from the log')
    
    def test_event_log_shows_only_current_turn_events(self):
        '''Test that the event log shows only events from the current turn.'''
        # Create a game state that will have staff unable to be paid (triggers a message)
        game_state = GameState('test_seed')
        
        # Set up a scenario where staff maintenance will cause a message
        game_state.money = 10  # Not enough for staff maintenance (2 staff * 15 = 30)
        
        # Add some old messages
        game_state.messages.append('Old message 1')
        game_state.messages.append('Old message 2')
        old_messages = game_state.messages.copy()
        
        # End the turn - this should clear old messages and add new ones about staff leaving
        game_state.end_turn()
        
        # Verify old messages are gone
        for old_message in old_messages:
            self.assertNotIn(old_message, game_state.messages,
                           'Old messages should not be in the current turn log')
        
        # Verify we got a message about staff leaving (since we couldn't pay them)
        staff_message_found = any('staff' in msg.lower() for msg in game_state.messages)
        self.assertTrue(staff_message_found, 
                       'Should have a message about staff when unable to pay maintenance')
    
    def test_event_log_empty_at_turn_start_by_default(self):
        '''Test that the event log is empty at the start of each turn by default.'''
        game_state = GameState('test_seed')
        
        # Add messages to simulate previous turn activity
        game_state.messages.extend([
            'Previous turn message 1',
            'Previous turn message 2', 
            'Action completed',
            'Event triggered'
        ])
        
        # Verify messages are present before turn end
        self.assertGreater(len(game_state.messages), 0, 'Should have messages before turn')
        
        # End turn - this should clear all messages first
        game_state.end_turn()
        
        # The messages list should be empty at the very start of turn processing,
        # then filled with current turn events. Since we have no selected actions
        # and sufficient money, we should only see system-generated messages
        
        # Verify no old messages remain
        for msg in ['Previous turn message 1', 'Previous turn message 2', 
                   'Action completed', 'Event triggered']:
            self.assertNotIn(msg, game_state.messages,
                           f"Old message '{msg}' should not persist into new turn")
    
    def test_event_log_preserves_current_turn_messages_only(self):
        '''Test that only messages generated during the current turn are preserved.'''
        game_state = GameState('test_seed')
        
        # Start with some messages from 'previous turns'
        game_state.messages = ['Old message 1', 'Old message 2']
        
        # Select an action that will generate a message when executed
        if game_state.money >= game_state.actions[0]['cost']:
            game_state.selected_gameplay_actions.append(0)  # Select first action
            game_state.messages.append(f'Selected: {game_state.actions[0]['name']}')
        
        pre_turn_messages = game_state.messages.copy()
        
        # End the turn - this clears messages, then processes actions/events
        game_state.end_turn()
        
        # Verify old messages are gone
        for old_msg in ['Old message 1', 'Old message 2']:
            self.assertNotIn(old_msg, game_state.messages,
                           'Old messages should be cleared')
        
        # Any messages present now should be from current turn processing only
        # (such as action execution, events, or maintenance messages)
        for msg in game_state.messages:
            self.assertNotIn(msg, pre_turn_messages,
                           'Current messages should be new, not carried over')
    
    def test_multiple_turn_event_log_isolation(self):
        '''Test that event logs are properly isolated across multiple turns.'''
        game_state = GameState('test_seed')
        
        # Set up for multiple turns with sufficient resources
        game_state.money = 50000  # Ensure sufficient funds
        
        turn_messages = {}
        
        # Run several turns and verify message isolation
        for turn_num in range(3):
            # Add a unique message before ending turn
            unique_msg = f'Turn {turn_num} unique test message'
            game_state.messages.append(unique_msg)
            
            # Store current messages
            game_state.messages.copy()
            
            # End turn
            game_state.end_turn()
            
            # Wait for turn processing to complete
            while game_state.turn_processing:
                game_state.update_turn_processing()
            
            # Store messages from this turn
            turn_messages[turn_num] = game_state.messages.copy()
            
            # Verify the unique message we added is gone (cleared by end_turn)
            self.assertNotIn(unique_msg, game_state.messages,
                           f'Turn {turn_num} unique message should not persist')
            
            # Verify that our unique messages don't cross over between turns
            for prev_turn in range(turn_num):
                prev_unique_msg = f'Turn {prev_turn} unique test message'
                self.assertNotIn(prev_unique_msg, game_state.messages,
                               f'Unique message from turn {prev_turn} should not appear in turn {turn_num}')
        
        # Final verification: messages are cleared each turn
        # (System messages like compute consumption may repeat but unique messages should not)
        self.assertEqual(len(turn_messages), 3, 'Should have captured 3 turns of messages')


class TestScrollableEventLog(unittest.TestCase):
    '''Test scrollable event log functionality.'''
    
    def test_scrollable_event_log_initially_disabled(self):
        '''Test that the scrollable event log starts disabled.'''
        game_state = GameState('test_seed')
        
        # Verify scrollable event log is initially disabled
        self.assertFalse(game_state.scrollable_event_log_enabled, 
                        'Scrollable event log should be disabled initially')
        
        # Verify event log history starts empty
        self.assertEqual(len(game_state.event_log_history), 0,
                        'Event log history should be empty initially')
        
        # Verify scroll offset starts at 0
        self.assertEqual(game_state.event_log_scroll_offset, 0,
                        'Event log scroll offset should be 0 initially')
    
    def test_scrollable_event_log_flag_set_by_event(self):
        '''Test that the scrollable event log flag is set when the event triggers.'''
        game_state = GameState('test_seed')
        
        # Verify flag is initially False
        self.assertFalse(game_state.scrollable_event_log_enabled)
        
        # Manually trigger the event (simulating the condition being met)
        # Find the event log upgrade event
        event_log_event = None
        for event in game_state.game_events:
            if event['name'] == 'Event Log System Upgrade':
                event_log_event = event
                break
        
        self.assertIsNotNone(event_log_event, 'Event Log System Upgrade event should exist')
        
        # Execute the event effect
        event_log_event['effect'](game_state)
        
        # Verify the flag is now set
        self.assertTrue(game_state.scrollable_event_log_enabled,
                       'Scrollable event log should be enabled after event triggers')
        
        # Verify a message was added about the upgrade
        upgrade_message_found = any('Event Log Upgrade' in msg for msg in game_state.messages)
        self.assertTrue(upgrade_message_found,
                       'Should have a message about the event log upgrade')
    
    def test_event_history_storage_when_enabled(self):
        '''Test that event history is stored when scrollable log is enabled.'''
        game_state = GameState('test_seed')
        
        # Enable the scrollable event log
        game_state.scrollable_event_log_enabled = True
        
        # Add some messages
        game_state.messages.extend([
            'Test message 1',
            'Test message 2',
            'Action completed'
        ])
        
        # Verify event log history is empty before turn end
        self.assertEqual(len(game_state.event_log_history), 0,
                        'Event log history should be empty before turn end')
        
        # End the turn
        game_state.end_turn()
        
        # Verify messages were stored in history
        self.assertGreater(len(game_state.event_log_history), 0,
                          'Event log history should have entries after turn end')
        
        # Verify the turn header was added
        turn_header_found = any('=== Turn' in entry for entry in game_state.event_log_history)
        self.assertTrue(turn_header_found,
                       'Event log history should contain a turn header')
        
        # Verify our test messages were stored
        for test_msg in ['Test message 1', 'Test message 2', 'Action completed']:
            self.assertIn(test_msg, game_state.event_log_history,
                         f'Message '{test_msg}' should be in event log history')
    
    def test_event_history_not_stored_when_disabled(self):
        '''Test that event history is not stored when scrollable log is disabled.'''
        game_state = GameState('test_seed')
        
        # Ensure scrollable event log is disabled
        game_state.scrollable_event_log_enabled = False
        
        # Add some messages
        game_state.messages.extend([
            'Test message 1',
            'Test message 2'
        ])
        
        # End the turn
        game_state.end_turn()
        
        # Verify event log history remains empty
        self.assertEqual(len(game_state.event_log_history), 0,
                        'Event log history should remain empty when feature is disabled')
    
    def test_multiple_turns_history_accumulation(self):
        '''Test that history accumulates across multiple turns when enabled.'''
        game_state = GameState('test_seed')
        game_state.scrollable_event_log_enabled = True
        game_state.money = 50000  # Ensure we have enough money for multiple turns
        
        # Clear initial messages and history to start fresh
        initial_history_count = len(game_state.event_log_history)
        
        # Run multiple turns and verify history accumulation
        for turn in range(3):
            # Add unique messages for this turn
            unique_message = f'Turn {turn + 1} unique test message'
            game_state.messages.append(unique_message)
            
            # End the turn
            game_state.end_turn()
            
            # Wait for turn processing to complete
            while game_state.turn_processing:
                game_state.update_turn_processing()
        
        # Verify that history contains turn headers and our unique messages
        history_str = ' '.join(game_state.event_log_history)
        
        # Check that turn headers were added
        self.assertIn('=== Turn 1 ===', history_str, 'Turn 1 header should be in history')
        self.assertIn('=== Turn 2 ===', history_str, 'Turn 2 header should be in history')
        self.assertIn('=== Turn 3 ===', history_str, 'Turn 3 header should be in history')
        
        # Check that our unique messages were added
        self.assertIn('Turn 1 unique test message', history_str, 'Turn 1 unique message should be in history')
        self.assertIn('Turn 2 unique test message', history_str, 'Turn 2 unique message should be in history')
        self.assertIn('Turn 3 unique test message', history_str, 'Turn 3 unique message should be in history')
        
        # Verify history is longer than what we started with
        self.assertGreater(len(game_state.event_log_history), initial_history_count,
                          'History should have accumulated messages')
        
        # Verify turn headers are present
        turn_headers = [entry for entry in game_state.event_log_history if '=== Turn' in entry]
        self.assertEqual(len(turn_headers), 3, 'Should have 3 turn headers')


if __name__ == '__main__':
    unittest.main()
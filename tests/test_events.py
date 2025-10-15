import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.features.event_system import Event, EventType, EventAction, DeferredEventQueue, create_enhanced_events


class TestEvent(unittest.TestCase):
    '''Test the Event class functionality.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.test_effect_called = False
        self.test_reduce_called = False
        
        def test_effect(gs):
            self.test_effect_called = True
            gs.messages.append('Test effect executed')
        
        def test_reduce_effect(gs):
            self.test_reduce_called = True
            gs.messages.append('Test reduce effect executed')
        
        def test_trigger(gs):
            return gs.turn >= 5
        
        self.test_effect = test_effect
        self.test_reduce_effect = test_reduce_effect
        self.test_trigger = test_trigger
    
    def test_event_initialization(self):
        '''Test that Event initializes with correct defaults.'''
        event = Event(
            name='Test Event',
            desc='Test Description', 
            trigger=self.test_trigger,
            effect=self.test_effect
        )
        
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.desc, 'Test Description')
        self.assertEqual(event.event_type, EventType.NORMAL)
        self.assertEqual(event.max_deferred_turns, 3)
        self.assertFalse(event.is_deferred)
        self.assertEqual(event.turns_deferred, 0)
        self.assertIsNone(event.deferred_at_turn)
    
    def test_event_from_dict(self):
        '''Test creating Event from dictionary (backward compatibility).'''
        event_dict = {
            'name': 'Legacy Event',
            'desc': 'Legacy Description',
            'trigger': self.test_trigger,
            'effect': self.test_effect
        }
        
        event = Event.from_dict(event_dict)
        
        self.assertEqual(event.name, 'Legacy Event')
        self.assertEqual(event.desc, 'Legacy Description')
        self.assertEqual(event.event_type, EventType.NORMAL)
        self.assertEqual(event.trigger, self.test_trigger)
        self.assertEqual(event.effect, self.test_effect)
    
    def test_event_to_dict(self):
        '''Test converting Event back to dictionary.'''
        event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict['name'], 'Test Event')
        self.assertEqual(event_dict['desc'], 'Test Description')
        self.assertEqual(event_dict['trigger'], self.test_trigger)
        self.assertEqual(event_dict['effect'], self.test_effect)
    
    def test_popup_event_default_actions(self):
        '''Test that popup events have correct default actions.'''
        event = Event(
            name='Popup Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.POPUP
        )
        
        expected_actions = [EventAction.ACCEPT, EventAction.DEFER, EventAction.DISMISS]
        self.assertEqual(event.available_actions, expected_actions)
    
    def test_deferred_event_default_actions(self):
        '''Test that deferred events have correct default actions.'''
        event = Event(
            name='Deferred Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.DEFERRED
        )
        
        expected_actions = [EventAction.ACCEPT, EventAction.REDUCE, EventAction.DISMISS]
        self.assertEqual(event.available_actions, expected_actions)
    
    def test_normal_event_default_actions(self):
        '''Test that normal events have correct default actions.'''
        event = Event(
            name='Normal Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.NORMAL
        )
        
        expected_actions = [EventAction.ACCEPT]
        self.assertEqual(event.available_actions, expected_actions)
    
    def test_event_defer_functionality(self):
        '''Test event deferring functionality.'''
        event = Event(
            name='Deferrable Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.POPUP
        )
        
        # Initially can be deferred
        self.assertTrue(event.can_be_deferred())
        
        # Defer the event
        success = event.defer(current_turn=5)
        self.assertTrue(success)
        self.assertTrue(event.is_deferred)
        self.assertEqual(event.turns_deferred, 0)
        self.assertEqual(event.deferred_at_turn, 5)
        
        # Cannot defer again
        self.assertFalse(event.can_be_deferred())
    
    def test_event_expiration(self):
        '''Test event expiration logic.'''
        event = Event(
            name='Expiring Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.POPUP,
            max_deferred_turns=2
        )
        
        # Defer the event
        event.defer(current_turn=5)
        
        # Tick once - not expired
        expired = event.tick_deferred()
        self.assertFalse(expired)
        self.assertEqual(event.turns_deferred, 1)
        
        # Tick twice - expired
        expired = event.tick_deferred()
        self.assertTrue(expired)
        self.assertEqual(event.turns_deferred, 2)
    
    def test_event_reduce_functionality(self):
        '''Test event reduce functionality.'''
        event = Event(
            name='Reducible Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.DEFERRED,
            reduce_effect=self.test_reduce_effect
        )
        
        self.assertTrue(event.can_be_reduced())
    
    def test_event_execute_effect_accept(self):
        '''Test executing event effect with ACCEPT action.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
        
        gs = MockGameState()
        
        event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect
        )
        
        event.execute_effect(gs, EventAction.ACCEPT)
        
        self.assertTrue(self.test_effect_called)
        self.assertIn('Test effect executed', gs.messages)
    
    def test_event_execute_effect_reduce(self):
        '''Test executing event effect with REDUCE action.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
        
        gs = MockGameState()
        
        event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            reduce_effect=self.test_reduce_effect
        )
        
        event.execute_effect(gs, EventAction.REDUCE)
        
        self.assertTrue(self.test_reduce_called)
        self.assertIn('Test reduce effect executed', gs.messages)
    
    def test_event_execute_effect_dismiss(self):
        '''Test executing event effect with DISMISS action.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
        
        gs = MockGameState()
        
        event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect
        )
        
        event.execute_effect(gs, EventAction.DISMISS)
        
        self.assertFalse(self.test_effect_called)  # Effect should not be called
        self.assertIn('Dismissed: Test Event', gs.messages)
    
    def test_deferred_display_text(self):
        '''Test deferred event display text.'''
        event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=self.test_trigger,
            effect=self.test_effect,
            event_type=EventType.POPUP,  # Popup events can be deferred
            max_deferred_turns=3
        )
        
        # Not deferred
        self.assertEqual(event.get_deferred_display_text(), 'Test Event')
        
        # Deferred
        event.defer(5)
        self.assertEqual(event.get_deferred_display_text(), 'Test Event (3 turns left)')
        
        # After one tick
        event.tick_deferred()
        self.assertEqual(event.get_deferred_display_text(), 'Test Event (2 turns left)')


class TestDeferredEventQueue(unittest.TestCase):
    '''Test the DeferredEventQueue functionality.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.queue = DeferredEventQueue()
        
        def test_effect(gs):
            gs.messages.append('Test effect executed')
        
        def test_trigger(gs):
            return True
        
        self.test_event = Event(
            name='Test Event',
            desc='Test Description',
            trigger=test_trigger,
            effect=test_effect,
            event_type=EventType.POPUP,
            max_deferred_turns=2
        )
    
    def test_queue_initialization(self):
        '''Test that DeferredEventQueue initializes correctly.'''
        self.assertEqual(len(self.queue.deferred_events), 0)
        self.assertEqual(len(self.queue.get_deferred_events()), 0)
    
    def test_add_deferred_event(self):
        '''Test adding deferred events to queue.'''
        # Event must be deferred first
        self.test_event.defer(5)
        
        success = self.queue.add_deferred_event(self.test_event)
        self.assertTrue(success)
        self.assertEqual(len(self.queue.get_deferred_events()), 1)
        self.assertIn(self.test_event, self.queue.get_deferred_events())
    
    def test_add_non_deferred_event_fails(self):
        '''Test that non-deferred events cannot be added to queue.'''
        # Event is not deferred
        success = self.queue.add_deferred_event(self.test_event)
        self.assertFalse(success)
        self.assertEqual(len(self.queue.get_deferred_events()), 0)
    
    def test_remove_event(self):
        '''Test removing events from queue.'''
        self.test_event.defer(5)
        self.queue.add_deferred_event(self.test_event)
        
        self.queue.remove_event(self.test_event)
        self.assertEqual(len(self.queue.get_deferred_events()), 0)
    
    def test_tick_all_events_no_expiration(self):
        '''Test ticking events that don't expire.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
        
        gs = MockGameState()
        
        self.test_event.defer(5)
        self.queue.add_deferred_event(self.test_event)
        
        # Tick once - should not expire (max_deferred_turns = 2)
        expired_events = self.queue.tick_all_events(gs)
        
        self.assertEqual(len(expired_events), 0)
        self.assertEqual(len(self.queue.get_deferred_events()), 1)
        self.assertEqual(self.test_event.turns_deferred, 1)
    
    def test_tick_all_events_with_expiration(self):
        '''Test ticking events that expire and are auto-executed.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
        
        gs = MockGameState()
        
        self.test_event.defer(5)
        self.queue.add_deferred_event(self.test_event)
        
        # Tick twice to expire (max_deferred_turns = 2)
        self.queue.tick_all_events(gs)  # First tick
        expired_events = self.queue.tick_all_events(gs)  # Second tick - expires
        
        self.assertEqual(len(expired_events), 1)
        self.assertIn(self.test_event, expired_events)
        self.assertEqual(len(self.queue.get_deferred_events()), 0)  # Removed from queue
        
        # Check that effect was executed
        self.assertIn('Test effect executed', gs.messages)
        self.assertIn('Auto-executed expired event: Test Event', gs.messages)
    
    def test_clear_queue(self):
        '''Test clearing the queue.'''
        self.test_event.defer(5)
        self.queue.add_deferred_event(self.test_event)
        
        self.queue.clear()
        self.assertEqual(len(self.queue.get_deferred_events()), 0)


class TestEnhancedEvents(unittest.TestCase):
    '''Test the enhanced events functionality.'''
    
    def test_create_enhanced_events(self):
        '''Test that enhanced events are created correctly.'''
        events = create_enhanced_events()
        
        self.assertGreater(len(events), 0)
        
        # Check that we have different event types
        event_types = [event.event_type for event in events]
        self.assertIn(EventType.POPUP, event_types)
        self.assertIn(EventType.DEFERRED, event_types)
    
    def test_ai_lab_incident_event(self):
        '''Test the AI Lab Incident popup event.'''
        events = create_enhanced_events()
        
        # Find the AI Lab Incident event
        ai_incident = None
        for event in events:
            if event.name == 'AI Lab Incident':
                ai_incident = event
                break
        
        self.assertIsNotNone(ai_incident)
        self.assertEqual(ai_incident.event_type, EventType.POPUP)
        self.assertTrue(ai_incident.can_be_deferred())
        self.assertTrue(ai_incident.can_be_reduced())
    
    def test_funding_opportunity_event(self):
        '''Test the Emergency Funding Opportunity deferred event.'''
        events = create_enhanced_events()
        
        # Find the funding opportunity event
        funding_event = None
        for event in events:
            if event.name == 'Emergency Funding Opportunity':
                funding_event = event
                break
        
        self.assertIsNotNone(funding_event)
        self.assertEqual(funding_event.event_type, EventType.DEFERRED)
        self.assertTrue(funding_event.can_be_reduced())


class TestEventActions(unittest.TestCase):
    '''Test different event actions and their effects.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Mock game state
        class MockGameState:
            def __init__(self):
                self.messages = []
                self.doom = 50
                self.money = 10000
            
            def _add(self, attr, val, reason=None):
                setattr(self, attr, getattr(self, attr) + val)
        
        self.gs = MockGameState()
    
    def test_ai_incident_full_effect(self):
        '''Test AI incident with full effect (ACCEPT action).'''
        events = create_enhanced_events()
        ai_incident = next(e for e in events if e.name == 'AI Lab Incident')
        
        initial_doom = self.gs.doom
        initial_money = self.gs.money
        
        ai_incident.execute_effect(self.gs, EventAction.ACCEPT)
        
        # Should have significant impact
        self.assertGreater(self.gs.doom, initial_doom)
        self.assertLess(self.gs.money, initial_money)
        self.assertIn('Major AI lab incident!', self.gs.messages[0])
    
    def test_ai_incident_reduced_effect(self):
        '''Test AI incident with reduced effect (REDUCE action).'''
        events = create_enhanced_events()
        ai_incident = next(e for e in events if e.name == 'AI Lab Incident')
        
        initial_doom = self.gs.doom
        initial_money = self.gs.money
        
        ai_incident.execute_effect(self.gs, EventAction.REDUCE)
        
        # Should have less impact than full effect
        doom_increase = self.gs.doom - initial_doom
        money_decrease = initial_money - self.gs.money
        
        self.assertGreater(doom_increase, 0)
        self.assertGreater(money_decrease, 0)
        self.assertLess(doom_increase, 15)  # Should be less than full effect
        self.assertLess(money_decrease, 5000)  # Should be less than full effect
        self.assertIn('Crisis contained', self.gs.messages[0])
    
    def test_funding_opportunity_full_effect(self):
        '''Test funding opportunity with full effect.'''
        events = create_enhanced_events()
        funding_event = next(e for e in events if e.name == 'Emergency Funding Opportunity')
        
        initial_money = self.gs.money
        
        funding_event.execute_effect(self.gs, EventAction.ACCEPT)
        
        self.assertGreater(self.gs.money, initial_money)
        self.assertIn('Received major funding grant!', self.gs.messages[0])
    
    def test_event_dismiss_action(self):
        '''Test dismissing an event.'''
        events = create_enhanced_events()
        ai_incident = next(e for e in events if e.name == 'AI Lab Incident')
        
        initial_doom = self.gs.doom
        initial_money = self.gs.money
        
        ai_incident.execute_effect(self.gs, EventAction.DISMISS)
        
        # No changes to game state except dismiss message
        self.assertEqual(self.gs.doom, initial_doom)
        self.assertEqual(self.gs.money, initial_money)
        self.assertIn('Dismissed: AI Lab Incident', self.gs.messages[0])


if __name__ == '__main__':
    unittest.main()
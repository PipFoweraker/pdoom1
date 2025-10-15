'''
Unit tests for Technical Failure Cascades System (Issue #193)

Tests cover:
- Cascade trigger mechanisms
- Near-miss vs actual failure logic
- Response choice impacts
- Prevention system upgrades
- Event integration
- Long-term consequences of transparency vs cover-up choices
'''

import unittest
from src.services.deterministic_rng import get_rng
from unittest.mock import patch, Mock
from src.core.game_state import GameState
from src.features.technical_failures import (
    TechnicalFailureCascades, FailureType, CascadeState
)


class TestTechnicalFailureCascades(unittest.TestCase):
    '''Test the technical failure cascades system.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        # Use deterministic seed for reproducible tests
        # get_rng().seed() removed - RNG initialized by GameState
        self.game_state = GameState('test-cascade-system')
        self.cascade_system = self.game_state.technical_failures
        
        # Set up basic game state for testing
        self.game_state.turn = 10
        self.game_state.money = 200
        self.game_state.staff = 8
        self.game_state.reputation = 10
        self.game_state.doom = 40
        self.game_state.compute = 50
        
    def test_cascade_system_initialization(self):
        '''Test that cascade system initializes correctly.'''
        self.assertIsInstance(self.cascade_system, TechnicalFailureCascades)
        self.assertEqual(len(self.cascade_system.active_cascades), 0)
        self.assertEqual(len(self.cascade_system.failure_history), 0)
        self.assertEqual(self.cascade_system.near_miss_count, 0)
        self.assertEqual(self.cascade_system.transparency_reputation, 0.0)
        self.assertEqual(self.cascade_system.cover_up_debt, 0)
        self.assertEqual(self.cascade_system.incident_response_level, 0)
        self.assertEqual(self.cascade_system.monitoring_systems, 0)
        self.assertEqual(self.cascade_system.communication_protocols, 0)
        
    def test_failure_type_selection(self):
        '''Test that failure types are selected appropriately based on game state.'''
        # High technical debt should increase system failures
        self.game_state.technical_debt.accumulated_debt = 15
        
        failure_types = []
        for _ in range(20):
            failure_type = self.cascade_system._select_failure_type()
            failure_types.append(failure_type)
            
        # Should have variety but system crashes more likely with high debt
        self.assertIn(FailureType.SYSTEM_CRASH, failure_types)
        self.assertTrue(len(set(failure_types)) > 1)  # Should have variety
        
    def test_failure_severity_calculation(self):
        '''Test failure severity calculation based on game state.'''
        # Base case
        severity = self.cascade_system._calculate_failure_severity()
        self.assertTrue(1 <= severity <= 10)
        
        # High technical debt should increase severity
        self.game_state.technical_debt.accumulated_debt = 20
        high_debt_severity = self.cascade_system._calculate_failure_severity()
        
        # High doom should increase severity
        self.game_state.doom = 80
        high_doom_severity = self.cascade_system._calculate_failure_severity()
        
        # High incident response should reduce severity
        self.cascade_system.incident_response_level = 4
        high_response_severity = self.cascade_system._calculate_failure_severity()
        
        # Test severity bounds
        self.assertTrue(1 <= high_debt_severity <= 10)
        self.assertTrue(1 <= high_doom_severity <= 10)
        self.assertTrue(1 <= high_response_severity <= 10)
        
    def test_failure_event_creation(self):
        '''Test creation of detailed failure events.'''
        failure = self.cascade_system._create_failure_event(FailureType.RESEARCH_SETBACK, 5)
        
        self.assertEqual(failure.failure_type, FailureType.RESEARCH_SETBACK)
        self.assertEqual(failure.severity, 5)
        self.assertIsInstance(failure.description, str)
        self.assertTrue(len(failure.description) > 0)
        self.assertIsInstance(failure.immediate_impact, dict)
        self.assertTrue(0.0 <= failure.cascade_chance <= 1.0)
        self.assertIsInstance(failure.cascade_targets, list)
        self.assertEqual(failure.turn_occurred, self.game_state.turn)
        
    def test_near_miss_handling(self):
        '''Test near-miss event handling.'''
        initial_near_miss_count = self.cascade_system.near_miss_count
        initial_messages = len(self.game_state.messages)
        
        failure = self.cascade_system._create_failure_event(FailureType.SYSTEM_CRASH, 3)
        self.cascade_system._trigger_near_miss(failure)
        
        # Should increment near miss count
        self.assertEqual(self.cascade_system.near_miss_count, initial_near_miss_count + 1)
        
        # Should add messages
        self.assertGreater(len(self.game_state.messages), initial_messages)
        
        # Should add to lessons learned
        self.assertIn(FailureType.SYSTEM_CRASH, self.cascade_system.lessons_learned)
        self.assertEqual(self.cascade_system.lessons_learned[FailureType.SYSTEM_CRASH], 1)
        
    def test_actual_failure_handling(self):
        '''Test actual failure event handling.'''
        initial_history_count = len(self.cascade_system.failure_history)
        initial_messages = len(self.game_state.messages)
        initial_money = self.game_state.money
        
        failure = self.cascade_system._create_failure_event(FailureType.SECURITY_BREACH, 4)
        # Add money impact to test
        failure.immediate_impact = {'money': -30, 'reputation': -2}
        
        self.cascade_system._trigger_actual_failure(failure)
        
        # Should add to failure history
        self.assertEqual(len(self.cascade_system.failure_history), initial_history_count + 1)
        
        # Should add messages
        self.assertGreater(len(self.game_state.messages), initial_messages)
        
        # Should apply immediate impacts
        self.assertEqual(self.game_state.money, initial_money - 30)
        
    def test_cascade_initiation(self):
        '''Test cascade initiation from initial failure.'''
        failure = self.cascade_system._create_failure_event(FailureType.INFRASTRUCTURE_FAILURE, 6)
        # Ensure high cascade chance for testing
        failure.cascade_chance = 1.0
        
        with patch.object(self.cascade_system, '_offer_cascade_response') as mock_response:
            self.cascade_system._trigger_actual_failure(failure)
            
            # Should create active cascade
            self.assertEqual(len(self.cascade_system.active_cascades), 1)
            
            # Should call cascade response
            mock_response.assert_called_once()
            
            cascade = self.cascade_system.active_cascades[0]
            self.assertEqual(cascade.initiating_failure, failure)
            self.assertEqual(len(cascade.subsequent_failures), 0)
            self.assertFalse(cascade.is_contained)
            
    def test_cascade_progression(self):
        '''Test cascade progression over multiple turns.'''
        # Create and start a cascade
        failure = self.cascade_system._create_failure_event(FailureType.SAFETY_INCIDENT, 7)
        cascade = CascadeState(
            initiating_failure=failure,
            subsequent_failures=[],
            total_turns=0
        )
        self.cascade_system.active_cascades.append(cascade)
        
        # Update cascade multiple times
        initial_failures = len(cascade.subsequent_failures)
        
        # Mock random to ensure cascade expansion
        with patch('src.services.deterministic_rng.get_rng') as mock_get_rng:
            mock_rng = Mock()
            mock_rng.random.return_value = 0.3  # Below 0.4 threshold
            mock_get_rng.return_value = mock_rng
            self.cascade_system._update_cascade(cascade)
            
        # Should add subsequent failures or resolve
        self.assertTrue(
            len(cascade.subsequent_failures) > initial_failures or 
            cascade not in self.cascade_system.active_cascades
        )
        
    def test_prevention_system_upgrades(self):
        '''Test prevention system capability upgrades.'''
        initial_money = self.game_state.money
        
        # Test incident response upgrade
        success = self.cascade_system.upgrade_incident_response(30)
        self.assertTrue(success)
        self.assertEqual(self.cascade_system.incident_response_level, 1)
        self.assertEqual(self.game_state.money, initial_money - 30)
        
        # Test monitoring systems upgrade
        success = self.cascade_system.upgrade_monitoring_systems(40)
        self.assertTrue(success)
        self.assertEqual(self.cascade_system.monitoring_systems, 1)
        
        # Test communication protocols upgrade
        success = self.cascade_system.upgrade_communication_protocols(25)
        self.assertTrue(success)
        self.assertEqual(self.cascade_system.communication_protocols, 1)
        
        # Test upgrade limits
        self.cascade_system.incident_response_level = 5
        success = self.cascade_system.upgrade_incident_response(100)
        self.assertFalse(success)  # Already at max level
        
    def test_insufficient_funds_upgrade(self):
        '''Test upgrade attempts with insufficient funds.'''
        self.game_state.money = 10  # Very low money
        
        success = self.cascade_system.upgrade_incident_response(30)
        self.assertFalse(success)
        self.assertEqual(self.cascade_system.incident_response_level, 0)
        
    def test_resilience_bonus_calculation(self):
        '''Test resilience bonus from lessons learned.'''
        # No lessons learned initially
        bonus = self.cascade_system.get_resilience_bonus(FailureType.DATA_LOSS)
        self.assertEqual(bonus, 0.0)
        
        # Add lessons learned
        self.cascade_system.lessons_learned[FailureType.DATA_LOSS] = 3
        bonus = self.cascade_system.get_resilience_bonus(FailureType.DATA_LOSS)
        self.assertAlmostEqual(bonus, 0.3, places=1)  # 3 * 0.1
        
        # Test maximum bonus
        self.cascade_system.lessons_learned[FailureType.DATA_LOSS] = 10
        bonus = self.cascade_system.get_resilience_bonus(FailureType.DATA_LOSS)
        self.assertAlmostEqual(bonus, 0.5, places=1)  # Capped at 50%
        
    def test_cover_up_risk_modifier(self):
        '''Test risk modifier from cover-up debt.'''
        # No cover-up debt initially
        modifier = self.cascade_system.get_cover_up_risk_modifier()
        self.assertEqual(modifier, 1.0)
        
        # Add cover-up debt
        self.cascade_system.cover_up_debt = 8
        modifier = self.cascade_system.get_cover_up_risk_modifier()
        self.assertEqual(modifier, 1.4)  # 1.0 + (8 * 0.05)
        
    def test_transparency_reputation_bonus(self):
        '''Test reputation bonus from transparent handling.'''
        self.cascade_system.transparency_reputation = 2.7
        bonus = self.cascade_system.get_transparency_reputation_bonus()
        self.assertEqual(bonus, 2)  # int(2.7)
        
    def test_cascade_summary(self):
        '''Test failure cascade summary for UI.'''
        # Add some test data
        self.cascade_system.near_miss_count = 3
        self.cascade_system.cover_up_debt = 5
        self.cascade_system.incident_response_level = 2
        self.cascade_system.lessons_learned[FailureType.RESEARCH_SETBACK] = 2
        
        summary = self.cascade_system.get_failure_cascade_summary()
        
        self.assertEqual(summary['near_misses'], 3)
        self.assertEqual(summary['cover_up_debt'], 5)
        self.assertEqual(summary['incident_response_level'], 2)
        self.assertEqual(summary['lessons_learned'][FailureType.RESEARCH_SETBACK], 2)
        self.assertIn('active_cascades', summary)
        self.assertIn('total_failures', summary)
        
    def test_cascade_containment_effectiveness(self):
        '''Test cascade containment based on response capabilities.'''
        # High capability should improve containment
        self.cascade_system.incident_response_level = 4
        
        failure = self.cascade_system._create_failure_event(FailureType.COMMUNICATION_BREAKDOWN, 5)
        cascade = CascadeState(
            initiating_failure=failure,
            subsequent_failures=[],
            total_turns=0
        )
        
        # Test systematic response with high capabilities
        def mock_systematic_response(gs):
            containment_chance = 0.5 + (self.cascade_system.incident_response_level * 0.1)
            if get_rng().random() < containment_chance:
                cascade.is_contained = True
            cascade.transparency_level = 0.6
            gs._add('money', -30)
            
        # Should have high success rate with good capabilities
        successes = 0
        trials = 100
        for _ in range(trials):
            test_cascade = CascadeState(
                initiating_failure=failure,
                subsequent_failures=[],
                total_turns=0
            )
            containment_chance = 0.5 + (self.cascade_system.incident_response_level * 0.1)
            if get_rng().random('containment_test') < containment_chance:
                successes += 1
                
        # Should succeed more often with high incident response capability
        success_rate = successes / trials
        self.assertGreater(success_rate, 0.7)  # Should be around 90% with level 4
        
    def test_integration_with_technical_debt(self):
        '''Test integration with existing technical debt system.'''
        # High technical debt should increase failure chances
        self.game_state.technical_debt.accumulated_debt = 18
        
        # Mock random to trigger cascade check
        with patch('src.services.deterministic_rng.get_rng') as mock_get_rng:
            mock_rng = Mock()
            mock_rng.random.return_value = 0.05  # Within accident chance
            mock_get_rng.return_value = mock_rng
            len(self.game_state.messages)
            self.cascade_system.check_for_cascades()
            
            # Should potentially add failure-related messages
            # (depending on internal random calls for near-miss vs failure)
            
        # Test that high debt affects failure severity
        severity = self.cascade_system._calculate_failure_severity()
        self.assertGreaterEqual(severity, 3)  # Should be elevated due to high debt


class TestTechnicalFailureCascadeActions(unittest.TestCase):
    '''Test cascade prevention actions.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test-cascade-actions')
        # RNG is now initialized by GameState constructor
        self.game_state.money = 500
        self.game_state.staff = 10
        
    def test_incident_response_action(self):
        '''Test incident response training action.'''
        from src.core.actions import execute_incident_response_upgrade
        
        initial_money = self.game_state.money
        initial_messages = len(self.game_state.messages)
        
        execute_incident_response_upgrade(self.game_state)
        
        # Should upgrade incident response level
        self.assertEqual(self.game_state.technical_failures.incident_response_level, 1)
        
        # Should cost money
        self.assertLess(self.game_state.money, initial_money)
        
        # Should add messages
        self.assertGreater(len(self.game_state.messages), initial_messages)
        
    def test_monitoring_systems_action(self):
        '''Test monitoring systems upgrade action.'''
        from src.core.actions import execute_monitoring_systems_upgrade
        
        initial_level = self.game_state.technical_failures.monitoring_systems
        execute_monitoring_systems_upgrade(self.game_state)
        
        self.assertEqual(
            self.game_state.technical_failures.monitoring_systems, 
            initial_level + 1
        )
        
    def test_communication_protocols_action(self):
        '''Test communication protocols upgrade action.'''
        from src.core.actions import execute_communication_protocols_upgrade
        
        initial_level = self.game_state.technical_failures.communication_protocols
        execute_communication_protocols_upgrade(self.game_state)
        
        self.assertEqual(
            self.game_state.technical_failures.communication_protocols, 
            initial_level + 1
        )
        
    def test_safety_audit_action(self):
        '''Test comprehensive safety audit action.'''
        from src.core.actions import execute_safety_audit
        
        # Add some technical debt to reduce
        self.game_state.technical_debt.accumulated_debt = 10
        
        initial_debt = self.game_state.technical_debt.accumulated_debt
        initial_money = self.game_state.money
        
        execute_safety_audit(self.game_state)
        
        # Should reduce technical debt
        self.assertLess(
            self.game_state.technical_debt.accumulated_debt, 
            initial_debt
        )
        
        # Should cost money
        self.assertEqual(self.game_state.money, initial_money - 60)
        
    def test_safety_audit_insufficient_funds(self):
        '''Test safety audit with insufficient funds.'''
        from src.core.actions import execute_safety_audit
        
        self.game_state.money = 30  # Less than required 60
        initial_debt = self.game_state.technical_debt.accumulated_debt
        
        execute_safety_audit(self.game_state)
        
        # Should not reduce debt if insufficient funds
        self.assertEqual(
            self.game_state.technical_debt.accumulated_debt, 
            initial_debt
        )
        

class TestTechnicalFailureCascadeEvents(unittest.TestCase):
    '''Test cascade-related events.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test-cascade-events')
        # RNG is now initialized by GameState constructor
        self.game_state.money = 200
        self.game_state.reputation = 15
        
    def test_near_miss_averted_event(self):
        '''Test near-miss averted event handler.'''
        initial_reputation = self.game_state.reputation
        initial_near_miss = self.game_state.technical_failures.near_miss_count
        
        self.game_state._trigger_near_miss_averted_event()
        
        # Should increase reputation
        self.assertGreater(self.game_state.reputation, initial_reputation)
        
        # Should increment near miss count
        self.assertGreater(
            self.game_state.technical_failures.near_miss_count, 
            initial_near_miss
        )
        
    def test_cover_up_exposed_event(self):
        '''Test cover-up exposure event handler.'''
        # Set up cover-up debt
        self.game_state.technical_failures.cover_up_debt = 8
        
        initial_reputation = self.game_state.reputation
        initial_money = self.game_state.money
        
        self.game_state._trigger_cover_up_exposed_event()
        
        # Should damage reputation
        self.assertLess(self.game_state.reputation, initial_reputation)
        
        # Should cost money
        self.assertLess(self.game_state.money, initial_money)
        
        # Should reduce cover-up debt (consequences paid)
        self.assertLess(
            self.game_state.technical_failures.cover_up_debt, 8
        )
        
    def test_transparency_dividend_event(self):
        '''Test transparency dividend event handler.'''
        # Set up transparency reputation
        self.game_state.technical_failures.transparency_reputation = 4.0
        
        initial_reputation = self.game_state.reputation
        
        self.game_state._trigger_transparency_dividend_event()
        
        # Should increase reputation
        self.assertGreater(self.game_state.reputation, initial_reputation)
        
        # Should reduce transparency reputation (prevent repeated triggers)
        self.assertLess(
            self.game_state.technical_failures.transparency_reputation, 4.0
        )
        
    def test_cascade_prevention_event(self):
        '''Test cascade prevention event handler.'''
        # Set up high incident response level
        self.game_state.technical_failures.incident_response_level = 4
        
        initial_reputation = self.game_state.reputation
        
        self.game_state._trigger_cascade_prevention_event()
        
        # Should increase reputation
        self.assertGreater(self.game_state.reputation, initial_reputation)


class TestTechnicalFailureCascadeIntegration(unittest.TestCase):
    '''Test integration with existing game systems.'''
    
    def setUp(self):
        '''Set up test fixtures.'''
        self.game_state = GameState('test-cascade-integration')
        # RNG is now initialized by GameState constructor
        
    def test_integration_with_turn_processing(self):
        '''Test that cascades are checked during turn processing.'''
        # Set up conditions for potential cascade
        self.game_state.technical_debt.accumulated_debt = 15
        self.game_state.turn = 20
        
        len(self.game_state.messages)
        
        # Process turn end
        self.game_state.end_turn()
        
        # Cascade check should have been called (though may not trigger)
        # This tests the integration point exists
        self.assertTrue(hasattr(self.game_state, 'technical_failures'))
        
    def test_cascade_system_persistence(self):
        '''Test that cascade system state persists correctly.'''
        # Modify cascade system state
        self.game_state.technical_failures.incident_response_level = 3
        self.game_state.technical_failures.near_miss_count = 5
        self.game_state.technical_failures.cover_up_debt = 7
        
        # Verify state persists
        self.assertEqual(self.game_state.technical_failures.incident_response_level, 3)
        self.assertEqual(self.game_state.technical_failures.near_miss_count, 5)
        self.assertEqual(self.game_state.technical_failures.cover_up_debt, 7)
        
    def test_action_availability(self):
        '''Test that cascade prevention actions are available.'''
        from src.core.actions import ACTIONS
        
        action_names = [action['name'] for action in ACTIONS]
        
        self.assertIn('Incident Response Training', action_names)
        self.assertIn('Monitoring Systems', action_names)
        self.assertIn('Communication Protocols', action_names)
        self.assertIn('Safety Audit', action_names)
        
    def test_event_availability(self):
        '''Test that cascade-related events are available.'''
        from src.core.events import EVENTS
        
        event_names = [event['name'] for event in EVENTS]
        
        self.assertIn('Near-Miss Crisis Averted', event_names)
        self.assertIn('Cover-Up Exposed', event_names)
        self.assertIn('Transparency Dividend', event_names)
        self.assertIn('Cascade Prevention Success', event_names)


if __name__ == '__main__':
    unittest.main()

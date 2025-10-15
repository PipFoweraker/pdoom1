'''
Deterministic Event System Manager

This module manages the deterministic event system for P(Doom), providing 
competitive gameplay through reproducible event triggers and effects.
Extracted from game_state.py to improve modularity and maintainability.

Key Features:
- 30 deterministic event trigger methods using context-aware RNG
- Complete event orchestration via trigger_events()
- Enhanced event handling with popup/deferred support
- Zero-regression delegation pattern for backward compatibility

Architecture:
- Follows established InputManager/EmployeeBlobManager/UITransitionManager patterns
- Clean separation of event logic from core game state
- Maintains all existing APIs through delegation
'''

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.core.game_state import GameState

from src.services.deterministic_rng import get_rng
from src.features.event_system import EventType, EventAction, Event


class DeterministicEventManager:
    '''
    Manages the deterministic event system for competitive P(Doom) gameplay.
    
    This manager encapsulates all event trigger logic, effect processing, and
    orchestration to provide reproducible event behavior using seed-based RNG.
    '''
    
    def __init__(self, game_state: 'GameState'):
        '''Initialize the deterministic event manager with game state reference.'''
        self.game_state = game_state
    
    # =================================================================
    # DETERMINISTIC EVENT TRIGGER METHODS
    # =================================================================
    
    def deterministic_event_trigger_lab_breakthrough(self) -> bool:
        '''Deterministic replacement for Lab Breakthrough event trigger.'''
        return (self.game_state.doom > 35 and 
                get_rng().random(f'event_lab_breakthrough_trigger_turn_{self.game_state.turn}') < self.game_state.doom / 120)
    
    def deterministic_event_trigger_funding_crisis(self) -> bool:
        '''Deterministic replacement for Funding Crisis event trigger.'''
        return (self.game_state.money < 80 and 
                get_rng().random(f'event_funding_crisis_trigger_turn_{self.game_state.turn}') < 0.2)
    
    def deterministic_event_effect_funding_crisis(self) -> None:
        '''Deterministic replacement for Funding Crisis event effect.'''
        loss = get_rng().randint(40, 100, f'event_funding_crisis_amount_turn_{self.game_state.turn}')
        self.game_state._add('money', -loss)
    
    def deterministic_event_trigger_staff_burnout(self) -> bool:
        '''Deterministic replacement for Staff Burnout event trigger.'''
        return (self.game_state.staff > 6 and 
                self.game_state.money < self.game_state.staff * self.game_state.staff_maintenance and 
                get_rng().random(f'event_staff_burnout_trigger_turn_{self.game_state.turn}') < 0.2)
    
    def deterministic_event_effect_staff_burnout(self) -> None:
        '''Deterministic replacement for Staff Burnout event effect.'''
        loss = get_rng().randint(1, 2, f'event_staff_burnout_amount_turn_{self.game_state.turn}')
        self.game_state._add('staff', -loss)
    
    def deterministic_event_trigger_competitor_spotted(self) -> bool:
        '''Deterministic replacement for Competitor Spotted event trigger.'''
        return (self.game_state.turn >= 3 and 
                get_rng().random(f'event_competitor_spotted_trigger_turn_{self.game_state.turn}') < (0.05 + self.game_state.doom / 1000))
    
    def deterministic_event_trigger_industry_intelligence(self) -> bool:
        '''Deterministic replacement for Industry Intelligence Update event trigger.'''
        return (getattr(self.game_state, 'scouting_unlocked', False) and 
                any(opp.discovered for opp in self.game_state.opponents) and 
                get_rng().random(f'event_industry_intelligence_trigger_turn_{self.game_state.turn}') < 0.15)
    
    def deterministic_event_trigger_expense_request(self) -> bool:
        '''Deterministic replacement for Employee Expense Request event trigger.'''
        return (self.game_state.staff >= 2 and 
                get_rng().random(f'event_expense_request_trigger_turn_{self.game_state.turn}') < (0.1 + self.game_state.staff * 0.01))
    
    def deterministic_event_trigger_researcher_breakthrough(self) -> bool:
        '''Deterministic replacement for Researcher Breakthrough event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) == 0:
            return False
        return get_rng().random(f'event_researcher_breakthrough_trigger_turn_{self.game_state.turn}') < len(self.game_state.researchers) * 0.03
    
    def deterministic_event_trigger_researcher_burnout_crisis(self) -> bool:
        '''Deterministic replacement for Researcher Burnout Crisis event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) == 0:
            return False
        has_high_burnout = any(r.burnout > 60 for r in self.game_state.researchers)
        return has_high_burnout and get_rng().random(f'event_researcher_burnout_crisis_trigger_turn_{self.game_state.turn}') < 0.15
    
    def deterministic_event_trigger_researcher_poaching(self) -> bool:
        '''Deterministic replacement for Researcher Poaching Attempt event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) == 0:
            return False
        return (self.game_state.turn > 3 and 
                get_rng().random(f'event_researcher_poaching_trigger_turn_{self.game_state.turn}') < len(self.game_state.researchers) * 0.02)
    
    def deterministic_event_trigger_research_ethics_concern(self) -> bool:
        '''Deterministic replacement for Research Ethics Concern event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) == 0:
            return False
        has_capabilities_researcher = any(r.specialization == 'capabilities' for r in self.game_state.researchers)
        return (has_capabilities_researcher and 
                self.game_state.doom > 40 and 
                get_rng().random(f'event_research_ethics_concern_trigger_turn_{self.game_state.turn}') < 0.1)
    
    def deterministic_event_trigger_researcher_conference(self) -> bool:
        '''Deterministic replacement for Researcher Conference Invitation event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) == 0:
            return False
        has_media_savvy = any(r.traits and 'media_savvy' in r.traits for r in self.game_state.researchers)
        return (has_media_savvy and 
                self.game_state.reputation > 15 and 
                get_rng().random(f'event_researcher_conference_trigger_turn_{self.game_state.turn}') < 0.08)
    
    def deterministic_event_trigger_collaborative_research(self) -> bool:
        '''Deterministic replacement for Collaborative Research Opportunity event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) < 2:
            return False
        return (self.game_state.reputation > 20 and 
                get_rng().random(f'event_collaborative_research_trigger_turn_{self.game_state.turn}') < 0.06)
    
    def deterministic_event_trigger_researcher_loyalty_crisis(self) -> bool:
        '''Deterministic replacement for Researcher Loyalty Crisis event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) <= 1:
            return False
        low_loyalty_count = sum(1 for r in self.game_state.researchers if r.loyalty < 30)
        return (low_loyalty_count >= 2 and 
                get_rng().random(f'event_researcher_loyalty_crisis_trigger_turn_{self.game_state.turn}') < 0.12)
    
    def deterministic_event_trigger_safety_shortcut(self) -> bool:
        '''Deterministic replacement for Safety Shortcut Temptation event trigger.'''
        return (getattr(self.game_state, 'research_quality_unlocked', False) and 
                len(getattr(self.game_state, 'researcher_assignments', [])) > 0 and 
                get_rng().random(f'event_safety_shortcut_trigger_turn_{self.game_state.turn}') < 0.15)
    
    def deterministic_event_trigger_technical_debt_warning(self) -> bool:
        '''Deterministic replacement for Technical Debt Warning event trigger.'''
        if not hasattr(self.game_state, 'technical_debt'):
            return False
        return (self.game_state.technical_debt.accumulated_debt >= 8 and 
                not self.game_state.technical_debt.has_reputation_risk() and 
                get_rng().random(f'event_technical_debt_warning_trigger_turn_{self.game_state.turn}') < 0.20)
    
    def deterministic_event_trigger_quality_speed_dilemma(self) -> bool:
        '''Deterministic replacement for Quality vs Speed Dilemma event trigger.'''
        if not hasattr(self.game_state, 'researchers') or len(self.game_state.researchers) < 2:
            return False
        return (self.game_state.turn >= 8 and 
                get_rng().random(f'event_quality_speed_dilemma_trigger_turn_{self.game_state.turn}') < 0.10)
    
    def deterministic_event_trigger_competitor_shortcut_discovery(self) -> bool:
        '''Deterministic replacement for Competitor Shortcut Discovery event trigger.'''
        if self.game_state.turn < 10:
            return False
        has_risky_competitor = any(hasattr(opp, 'technical_debt') and opp.technical_debt > 5 
                                  for opp in getattr(self.game_state, 'opponents', []))
        return (has_risky_competitor and 
                get_rng().random(f'event_competitor_shortcut_discovery_trigger_turn_{self.game_state.turn}') < 0.12)
    
    def deterministic_event_trigger_vc_drought(self) -> bool:
        '''Deterministic replacement for Venture Capital Drought event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles'):
            return False
        is_downturn = self.game_state.economic_cycles.current_state.phase.name in ['RECESSION', 'CORRECTION']
        return (is_downturn and 
                self.game_state.turn % 15 == 0 and 
                get_rng().random(f'event_vc_drought_trigger_turn_{self.game_state.turn}') < 0.3)
    
    def deterministic_event_trigger_bubble_warning(self) -> bool:
        '''Deterministic replacement for AI Bubble Burst Warning event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles'):
            return False
        return (self.game_state.economic_cycles.current_state.phase.name == 'BOOM' and
                self.game_state.turn > 50 and 
                get_rng().random(f'event_bubble_warning_trigger_turn_{self.game_state.turn}') < 0.15)
    
    def deterministic_event_trigger_government_funding(self) -> bool:
        '''Deterministic replacement for Government AI Initiative event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles'):
            return False
        return (self.game_state.turn > 20 and 
                self.game_state.reputation >= 8 and 
                get_rng().random(f'event_government_funding_trigger_turn_{self.game_state.turn}') < 0.08)
    
    def deterministic_event_trigger_corporate_partnership(self) -> bool:
        '''Deterministic replacement for Corporate Partnership Opportunity event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles'):
            return False
        is_downturn = self.game_state.economic_cycles.current_state.phase.name in ['RECESSION', 'CORRECTION']
        return (not is_downturn and 
                self.game_state.reputation >= 12 and 
                get_rng().random(f'event_corporate_partnership_trigger_turn_{self.game_state.turn}') < 0.10)
    
    def deterministic_event_trigger_emergency_measures(self) -> bool:
        '''Deterministic replacement for Emergency Cost Cutting event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles'):
            return False
        is_downturn = self.game_state.economic_cycles.current_state.phase.name in ['RECESSION', 'CORRECTION']
        return (is_downturn and 
                self.game_state.money < 150 and 
                get_rng().random(f'event_emergency_measures_trigger_turn_{self.game_state.turn}') < 0.25)
    
    def deterministic_event_trigger_competitor_funding(self) -> bool:
        '''Deterministic replacement for Competitor Funding Announcement event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles') or self.game_state.turn < 8:
            return False
        any_competitor_discovered = any(opp.discovered for opp in getattr(self.game_state, 'opponents', []))
        return (any_competitor_discovered and 
                get_rng().random(f'event_competitor_funding_trigger_turn_{self.game_state.turn}') < 0.12)
    
    def deterministic_event_trigger_ai_winter_warning(self) -> bool:
        '''Deterministic replacement for AI Winter Warning event trigger.'''
        if not hasattr(self.game_state, 'economic_cycles') or self.game_state.turn < 30:
            return False
        is_recession = self.game_state.economic_cycles.current_state.phase.name == 'RECESSION'
        return (is_recession and 
                get_rng().random(f'event_ai_winter_warning_trigger_turn_{self.game_state.turn}') < 0.08)
    
    def deterministic_event_trigger_near_miss_averted(self) -> bool:
        '''Deterministic replacement for Near-Miss Crisis Averted event trigger.'''
        if not hasattr(self.game_state, 'technical_failures'):
            return False
        return (self.game_state.technical_failures.incident_response_level >= 2 and 
                self.game_state.doom > 25 and 
                get_rng().random(f'event_near_miss_averted_trigger_turn_{self.game_state.turn}') < 0.12)
    
    def deterministic_event_trigger_cover_up_exposed(self) -> bool:
        '''Deterministic replacement for Cover-Up Exposed event trigger.'''
        if not hasattr(self.game_state, 'technical_failures'):
            return False
        return (self.game_state.technical_failures.cover_up_debt >= 3 and 
                get_rng().random(f'event_cover_up_exposed_trigger_turn_{self.game_state.turn}') < 0.18)
    
    def deterministic_event_trigger_transparency_dividend(self) -> bool:
        '''Deterministic replacement for Transparency Dividend event trigger.'''
        if not hasattr(self.game_state, 'technical_failures'):
            return False
        return (self.game_state.technical_failures.transparency_reputation >= 5 and 
                get_rng().random(f'event_transparency_dividend_trigger_turn_{self.game_state.turn}') < 0.15)
    
    def deterministic_event_trigger_cascade_prevention(self) -> bool:
        '''Deterministic replacement for Cascade Prevention Success event trigger.'''
        if not hasattr(self.game_state, 'technical_failures'):
            return False
        return (self.game_state.technical_failures.incident_response_level >= 3 and 
                get_rng().random(f'event_cascade_prevention_trigger_turn_{self.game_state.turn}') < 0.1)
    
    # =================================================================
    # EVENT ORCHESTRATION METHODS
    # =================================================================
    
    def trigger_events(self) -> None:
        '''Trigger events using deterministic replacements for competitive gameplay.'''
        # Deterministic event mapping - replaces random calls in event lambda functions
        deterministic_events = {
            'Lab Breakthrough': {
                'trigger': self.deterministic_event_trigger_lab_breakthrough,
                'effect': lambda gs: gs._breakthrough_event()
            },
            'Funding Crisis': {
                'trigger': self.deterministic_event_trigger_funding_crisis,
                'effect': self.deterministic_event_effect_funding_crisis
            },
            'Staff Burnout': {
                'trigger': self.deterministic_event_trigger_staff_burnout,
                'effect': self.deterministic_event_effect_staff_burnout
            },
            'Competitor Spotted': {
                'trigger': self.deterministic_event_trigger_competitor_spotted,
                'effect': lambda gs: gs._trigger_competitor_discovery()
            },
            'Industry Intelligence Update': {
                'trigger': self.deterministic_event_trigger_industry_intelligence,
                'effect': lambda gs: gs._provide_competitor_update()
            },
            'Employee Expense Request': {
                'trigger': self.deterministic_event_trigger_expense_request,
                'effect': lambda gs: gs._trigger_expense_request()
            },
            'Researcher Breakthrough': {
                'trigger': self.deterministic_event_trigger_researcher_breakthrough,
                'effect': lambda gs: gs._researcher_breakthrough()
            },
            'Researcher Burnout Crisis': {
                'trigger': self.deterministic_event_trigger_researcher_burnout_crisis,
                'effect': lambda gs: gs._researcher_burnout_crisis()
            },
            'Researcher Poaching Attempt': {
                'trigger': self.deterministic_event_trigger_researcher_poaching,
                'effect': lambda gs: gs._researcher_poaching_attempt()
            },
            'Research Ethics Concern': {
                'trigger': self.deterministic_event_trigger_research_ethics_concern,
                'effect': lambda gs: gs._research_ethics_concern()
            },
            'Researcher Conference Invitation': {
                'trigger': self.deterministic_event_trigger_researcher_conference,
                'effect': lambda gs: gs._researcher_conference_invitation()
            },
            'Collaborative Research Opportunity': {
                'trigger': self.deterministic_event_trigger_collaborative_research,
                'effect': lambda gs: gs._collaborative_research_opportunity()
            },
            'Researcher Loyalty Crisis': {
                'trigger': self.deterministic_event_trigger_researcher_loyalty_crisis,
                'effect': lambda gs: gs._researcher_loyalty_crisis()
            },
            'Safety Shortcut Temptation': {
                'trigger': self.deterministic_event_trigger_safety_shortcut,
                'effect': lambda gs: gs._trigger_safety_shortcut_event()
            },
            'Technical Debt Warning': {
                'trigger': self.deterministic_event_trigger_technical_debt_warning,
                'effect': lambda gs: gs._trigger_technical_debt_warning()
            },
            'Quality vs Speed Dilemma': {
                'trigger': self.deterministic_event_trigger_quality_speed_dilemma,
                'effect': lambda gs: gs._trigger_quality_speed_dilemma()
            },
            'Competitor Shortcut Discovery': {
                'trigger': self.deterministic_event_trigger_competitor_shortcut_discovery,
                'effect': lambda gs: gs._trigger_competitor_shortcut_discovery()
            },
            'Venture Capital Drought': {
                'trigger': self.deterministic_event_trigger_vc_drought,
                'effect': lambda gs: gs._trigger_funding_drought_event()
            },
            'AI Bubble Burst Warning': {
                'trigger': self.deterministic_event_trigger_bubble_warning,
                'effect': lambda gs: gs._trigger_bubble_warning_event()
            },
            'Government AI Initiative Announced': {
                'trigger': self.deterministic_event_trigger_government_funding,
                'effect': lambda gs: gs._trigger_government_funding_event()
            },
            'Corporate Partnership Opportunity': {
                'trigger': self.deterministic_event_trigger_corporate_partnership,
                'effect': lambda gs: gs._trigger_corporate_partnership_event()
            },
            'Emergency Cost Cutting Required': {
                'trigger': self.deterministic_event_trigger_emergency_measures,
                'effect': lambda gs: gs._trigger_emergency_measures_event()
            },
            'Competitor Funding Announcement': {
                'trigger': self.deterministic_event_trigger_competitor_funding,
                'effect': lambda gs: gs._trigger_competitor_funding_event()
            },
            'AI Winter Warning': {
                'trigger': self.deterministic_event_trigger_ai_winter_warning,
                'effect': lambda gs: gs._trigger_ai_winter_warning_event()
            },
            'Near-Miss Crisis Averted': {
                'trigger': self.deterministic_event_trigger_near_miss_averted,
                'effect': lambda gs: gs._trigger_near_miss_averted_event()
            },
            'Cover-Up Exposed': {
                'trigger': self.deterministic_event_trigger_cover_up_exposed,
                'effect': lambda gs: gs._trigger_cover_up_exposed_event()
            },
            'Transparency Dividend': {
                'trigger': self.deterministic_event_trigger_transparency_dividend,
                'effect': lambda gs: gs._trigger_transparency_dividend_event()
            },
            'Cascade Prevention Success': {
                'trigger': self.deterministic_event_trigger_cascade_prevention,
                'effect': lambda gs: gs._trigger_cascade_prevention_event()
            }
        }
        
        # Process events with deterministic replacements where available
        for event_dict in self.game_state.game_events:
            event_name = event_dict['name']
            
            # Use deterministic version if available, otherwise fall back to original
            if event_name in deterministic_events:
                trigger_func = deterministic_events[event_name]['trigger']
                effect_func = deterministic_events[event_name]['effect']
                
                if trigger_func():
                    effect_func(self.game_state)
                    event_message = f'Event: {event_dict['name']} - {event_dict['desc']}'
                    self.game_state.messages.append(event_message)
                    self.game_state.logger.log_event(event_dict['name'], event_dict['desc'], self.game_state.turn)
            else:
                # Use original lambda functions for events not yet migrated
                if event_dict['trigger'](self.game_state):
                    event_dict['effect'](self.game_state)
                    event_message = f'Event: {event_dict['name']} - {event_dict['desc']}'
                    self.game_state.messages.append(event_message)
                    self.game_state.logger.log_event(event_dict['name'], event_dict['desc'], self.game_state.turn)
        
        # Handle enhanced events (if enabled)
        if self.game_state.enhanced_events_enabled:
            self._trigger_enhanced_events()
    
    def _trigger_enhanced_events(self) -> None:
        '''Trigger enhanced events with popup/deferred support.'''
        from src.features.event_system import create_enhanced_events
        
        # Get enhanced events (in a real implementation, these would be stored)
        enhanced_events = create_enhanced_events()
        
        for event in enhanced_events:
            if event.trigger(self.game_state):
                if event.event_type == EventType.POPUP:
                    # Add to pending popup events for UI handling
                    self.game_state.pending_popup_events.append(event)
                else:
                    # Handle normal/deferred events immediately
                    self._handle_triggered_event(event)
    
    def _handle_triggered_event(self, event: Any) -> None:
        '''Handle a triggered event based on its type.'''
        if event.event_type == EventType.NORMAL:
            # Execute immediately like original events
            event.execute_effect(self.game_state, EventAction.ACCEPT)
            event_message = f'Event: {event.name} - {event.desc}'
            self.game_state.messages.append(event_message)
            self.game_state.logger.log_event(event.name, event.desc, self.game_state.turn)
        elif event.event_type == EventType.DEFERRED:
            # For now, auto-defer deferred events (UI will handle choice later)
            if event.defer(self.game_state.turn):
                self.game_state.deferred_events.add_deferred_event(event)
                self.game_state.messages.append(f'Deferred: {event.name} - {event.desc}')
                self.game_state.logger.log_event(f'Deferred: {event.name}', event.desc, self.game_state.turn)
    
    def handle_popup_event_action(self, event: Event, action: EventAction) -> None:
        '''Handle player action on a popup event.'''
        if action == EventAction.DEFER and event.can_be_deferred():
            if event.defer(self.game_state.turn):
                self.game_state.deferred_events.add_deferred_event(event)
                self.game_state.messages.append(f'Deferred: {event.name}')
        else:
            event.execute_effect(self.game_state, action)
        
        # Remove from pending popup events
        if event in self.game_state.pending_popup_events:
            self.game_state.pending_popup_events.remove(event)
        
        # Log the action
        self.game_state.logger.log_event(f'Player {action.value}: {event.name}', event.desc, self.game_state.turn)
    
    def clear_stuck_popup_events(self) -> bool:
        '''
        Safety method to clear popup events that may have become stuck.
        Called when UI interaction issues are detected.
        '''
        if hasattr(self.game_state, 'pending_popup_events') and self.game_state.pending_popup_events:
            # Log that we're clearing stuck events
            num_cleared = len(self.game_state.pending_popup_events)
            self.game_state.add_message(f'Cleared {num_cleared} stuck popup event(s)')
            self.game_state.pending_popup_events.clear()
            return True
        return False
'''
Technical Failure Cascades System (Issue #193)

This module implements a comprehensive technical failure cascade system that models:
- How initial failures can trigger additional failures
- Player choices between transparency/learning vs cover-up/reputation protection
- Near-miss events that provide learning opportunities without consequences
- Cascade prevention and containment mechanisms

The system builds on the existing technical debt and accident systems to create
realistic domino effects that organizations must manage.
'''

from src.services.deterministic_rng import get_rng
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class FailureType(Enum):
    '''Types of technical failures that can occur.'''
    RESEARCH_SETBACK = 'research_setback'
    SECURITY_BREACH = 'security_breach'
    SYSTEM_CRASH = 'system_crash'
    DATA_LOSS = 'data_loss'
    SAFETY_INCIDENT = 'safety_incident'
    INFRASTRUCTURE_FAILURE = 'infrastructure_failure'
    COMMUNICATION_BREAKDOWN = 'communication_breakdown'


class ResponseType(Enum):
    '''Types of responses to failures.'''
    TRANSPARENCY = 'transparency'
    COVER_UP = 'cover_up'
    INVESTIGATION = 'investigation'
    QUICK_FIX = 'quick_fix'
    IGNORE = 'ignore'


@dataclass
class FailureEvent:
    '''Represents a technical failure event.'''
    failure_type: FailureType
    severity: int  # 1-10 scale
    description: str
    immediate_impact: Dict[str, int]  # Resource impacts
    cascade_chance: float  # Probability of triggering cascade
    cascade_targets: List[FailureType]  # What failures this can trigger
    requires_response: bool = True
    turn_occurred: int = 0


@dataclass
class CascadeState:
    '''Tracks the state of an ongoing failure cascade.'''
    initiating_failure: FailureEvent
    subsequent_failures: List[FailureEvent]
    total_turns: int
    is_contained: bool = False
    transparency_level: float = 0.0  # 0.0 = full cover-up, 1.0 = full transparency


class TechnicalFailureCascades:
    '''
    Manages technical failure cascades, near-misses, and organizational responses.
    
    This system creates realistic failure scenarios where:
    - Initial failures can trigger additional failures
    - Organizations must balance transparency with reputation protection  
    - Learning from failures improves future resilience
    - Cover-ups may prevent immediate reputation damage but increase future risks
    '''
    
    def __init__(self, game_state):
        self.game_state = game_state
        self.active_cascades: List[CascadeState] = []
        self.failure_history: List[FailureEvent] = []
        self.near_miss_count: int = 0
        self.transparency_reputation: float = 0.0  # Reputation for transparent handling
        self.cover_up_debt: int = 0  # Accumulated debt from cover-ups
        self.lessons_learned: Dict[FailureType, int] = {}  # Resilience from learning
        
        # Cascade prevention capabilities
        self.incident_response_level: int = 0  # 0-5 scale
        self.monitoring_systems: int = 0  # Early warning capability
        self.communication_protocols: int = 0  # Cross-team coordination
        
    def check_for_cascades(self) -> None:
        '''Check if any active cascades should progress or new ones should start.'''
        # Update existing cascades
        for cascade in self.active_cascades[:]:  # Copy list for safe modification
            self._update_cascade(cascade)
            
        # Check for new cascade triggers from technical debt accidents
        if hasattr(self.game_state, 'technical_debt'):
            debt_accident_chance = self.game_state.technical_debt.get_accident_chance()
            if debt_accident_chance > 0 and get_rng().random('random_context') < debt_accident_chance * 0.3:
                self._trigger_potential_cascade()
                
    def _trigger_potential_cascade(self) -> None:
        '''Trigger a potential cascade-starting failure.'''
        # Determine failure type based on current game state
        failure_type = self._select_failure_type()
        severity = self._calculate_failure_severity()
        
        # Create the initial failure
        failure = self._create_failure_event(failure_type, severity)
        
        # Decide if this becomes a near-miss or actual failure
        near_miss_chance = 0.4 + (self.monitoring_systems * 0.1)
        
        if get_rng().random('random_context') < near_miss_chance:
            self._trigger_near_miss(failure)
        else:
            self._trigger_actual_failure(failure)
            
    def _select_failure_type(self) -> FailureType:
        '''Select failure type based on current game state and context.'''
        # Weight failure types based on game state
        weights = {}
        
        # Research-heavy organizations more prone to research setbacks
        if hasattr(self.game_state, 'researchers') and len(self.game_state.researchers) > 3:
            weights[FailureType.RESEARCH_SETBACK] = 3.0
            weights[FailureType.DATA_LOSS] = 2.0
            
        # High technical debt increases system failures
        if hasattr(self.game_state, 'technical_debt') and self.game_state.technical_debt.accumulated_debt > 10:
            weights[FailureType.SYSTEM_CRASH] = 2.5
            weights[FailureType.INFRASTRUCTURE_FAILURE] = 2.0
            
        # Larger organizations have communication issues
        if self.game_state.staff > 8:
            weights[FailureType.COMMUNICATION_BREAKDOWN] = 2.0
            
        # High doom or reputation issues increase safety incidents
        if self.game_state.doom > 50 or self.game_state.reputation < 5:
            weights[FailureType.SAFETY_INCIDENT] = 2.5
            weights[FailureType.SECURITY_BREACH] = 2.0
            
        # Default weights for all types
        for failure_type in FailureType:
            if failure_type not in weights:
                weights[failure_type] = 1.0
                
        # Select based on weights
        total_weight = sum(weights.values())
        rand_val = get_rng().random('random_context') * total_weight
        
        cumulative = 0.0
        for failure_type, weight in weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                return failure_type
                
        return FailureType.SYSTEM_CRASH  # Fallback
        
    def _calculate_failure_severity(self) -> int:
        '''Calculate failure severity (1-10) based on game state.'''
        base_severity = get_rng().randint(3, 7, 'failure_severity')
        
        # Technical debt increases severity
        if hasattr(self.game_state, 'technical_debt'):
            debt_modifier = min(3, self.game_state.technical_debt.accumulated_debt // 5)
            base_severity += debt_modifier
            
        # High doom increases severity
        doom_modifier = min(2, self.game_state.doom // 25)
        base_severity += doom_modifier
        
        # Incident response capability reduces severity
        response_modifier = min(3, self.incident_response_level)
        base_severity -= response_modifier
        
        return max(1, min(10, base_severity))
        
    def _create_failure_event(self, failure_type: FailureType, severity: int) -> FailureEvent:
        '''Create a detailed failure event.'''
        # Define failure templates
        failure_templates = {
            FailureType.RESEARCH_SETBACK: {
                'descriptions': [
                    'Critical bug discovered in core algorithm',
                    'Research data validation failure',
                    'Model training corruption detected',
                    'Experimental protocol violation'
                ],
                'base_impact': {'research_progress': -15, 'reputation': -2},
                'cascade_targets': [FailureType.DATA_LOSS, FailureType.COMMUNICATION_BREAKDOWN],
                'base_cascade_chance': 0.3
            },
            FailureType.SECURITY_BREACH: {
                'descriptions': [
                    'Unauthorized access to research systems',
                    'Data exfiltration attempt detected',
                    'Insider threat security incident',
                    'External cyber attack on infrastructure'
                ],
                'base_impact': {'reputation': -4, 'money': -30},
                'cascade_targets': [FailureType.DATA_LOSS, FailureType.INFRASTRUCTURE_FAILURE],
                'base_cascade_chance': 0.4
            },
            FailureType.SYSTEM_CRASH: {
                'descriptions': [
                    'Critical system failure during peak operations',
                    'Database corruption causes widespread outage',
                    'Memory leak crashes production systems',
                    'Network infrastructure failure'
                ],
                'base_impact': {'compute': -20, 'research_progress': -10},
                'cascade_targets': [FailureType.DATA_LOSS, FailureType.COMMUNICATION_BREAKDOWN],
                'base_cascade_chance': 0.35
            },
            FailureType.DATA_LOSS: {
                'descriptions': [
                    'Critical research data irretrievably lost',
                    'Backup system failure during restore',
                    'Accidental deletion of experiment results',
                    'Storage corruption affects key datasets'
                ],
                'base_impact': {'research_progress': -25, 'reputation': -3},
                'cascade_targets': [FailureType.RESEARCH_SETBACK, FailureType.COMMUNICATION_BREAKDOWN],
                'base_cascade_chance': 0.25
            },
            FailureType.SAFETY_INCIDENT: {
                'descriptions': [
                    'AI system exhibits unexpected dangerous behavior',
                    'Safety protocol bypass leads to incident',
                    'Alignment failure in deployed system',
                    'Uncontrolled capability emergence detected'
                ],
                'base_impact': {'doom': 8, 'reputation': -5},
                'cascade_targets': [FailureType.SECURITY_BREACH, FailureType.COMMUNICATION_BREAKDOWN],
                'base_cascade_chance': 0.5
            },
            FailureType.INFRASTRUCTURE_FAILURE: {
                'descriptions': [
                    'Power grid failure affects all operations',
                    'Cooling system breakdown threatens hardware',
                    'Network connectivity lost to external systems',
                    'Physical security breach at facility'
                ],
                'base_impact': {'compute': -30, 'money': -50},
                'cascade_targets': [FailureType.SYSTEM_CRASH, FailureType.DATA_LOSS],
                'base_cascade_chance': 0.4
            },
            FailureType.COMMUNICATION_BREAKDOWN: {
                'descriptions': [
                    'Critical information not shared between teams',
                    'Management unaware of developing crisis',
                    'Coordination failure during incident response',
                    'Key personnel unavailable during emergency'
                ],
                'base_impact': {'reputation': -2, 'staff': -1},
                'cascade_targets': [FailureType.RESEARCH_SETBACK, FailureType.SAFETY_INCIDENT],
                'base_cascade_chance': 0.2
            }
        }
        
        template = failure_templates[failure_type]
        description = get_rng().choice(template['descriptions'], 'failure_description')
        
        # Scale impact by severity
        impact = {}
        for resource, base_amount in template['base_impact'].items():
            impact[resource] = int(base_amount * (severity / 5.0))
            
        # Adjust cascade chance by severity and prevention capabilities
        cascade_chance = template['base_cascade_chance'] * (severity / 5.0)
        cascade_chance *= (1.0 - self.incident_response_level * 0.1)
        cascade_chance = max(0.0, min(1.0, cascade_chance))
        
        return FailureEvent(
            failure_type=failure_type,
            severity=severity,
            description=description,
            immediate_impact=impact,
            cascade_chance=cascade_chance,
            cascade_targets=template['cascade_targets'],
            turn_occurred=self.game_state.turn
        )
        
    def _trigger_near_miss(self, failure: FailureEvent) -> None:
        '''Handle a near-miss event - almost became a failure.'''
        self.near_miss_count += 1
        
        # Create near-miss message
        self.game_state.messages.append(
            f'[WARNING]? NEAR MISS: {failure.description} - incident avoided by quick response!'
        )
        
        # Near-misses provide learning opportunities with no immediate penalties
        self.game_state.messages.append(
            '? Teams conduct post-incident review to prevent future occurrences.'
        )
        
        # Add to lessons learned
        if failure.failure_type not in self.lessons_learned:
            self.lessons_learned[failure.failure_type] = 0
        self.lessons_learned[failure.failure_type] += 1
        
        # Small reputation bonus for good incident response
        if self.incident_response_level > 2:
            self.game_state._add('reputation', 1)
            self.game_state.messages.append('? Strong incident response protocols earn recognition.')
            
    def _trigger_actual_failure(self, failure: FailureEvent) -> None:
        '''Handle an actual failure event.'''
        self.failure_history.append(failure)
        
        # Apply immediate impacts
        for resource, amount in failure.immediate_impact.items():
            if hasattr(self.game_state, resource):
                self.game_state._add(resource, amount)
                
        # Create failure message
        severity_text = ['Minor', 'Moderate', 'Serious', 'Major', 'Critical'][min(4, failure.severity // 2)]
        self.game_state.messages.append(
            f'[ALERT] {severity_text.upper()} FAILURE: {failure.description}'
        )
        
        # Check if this triggers a cascade
        if get_rng().random('random_context') < failure.cascade_chance:
            self._start_cascade(failure)
        else:
            # Single failure - offer response choices
            self._offer_failure_response(failure)
            
    def _start_cascade(self, initiating_failure: FailureEvent) -> None:
        '''Start a failure cascade from an initial failure.'''
        cascade = CascadeState(
            initiating_failure=initiating_failure,
            subsequent_failures=[],
            total_turns=0
        )
        
        self.active_cascades.append(cascade)
        
        self.game_state.messages.append(
            '[WARNING]? CASCADE ALERT: Initial failure may trigger additional failures!'
        )
        self.game_state.messages.append(
            '? Incident response teams mobilizing to contain the situation.'
        )
        
        # Immediate cascade response choice
        self._offer_cascade_response(cascade)
        
    def _offer_failure_response(self, failure: FailureEvent) -> None:
        '''Offer player choices for responding to a single failure.'''
        from src.features.event_system import Event, EventType, EventAction
        
        # Create response event
        response_desc = (
            f'How should your organization respond to this {failure.failure_type.value}? '
            f'Your choice will affect reputation, learning, and future risks.'
        )
        
        def handle_transparency(gs):
            '''Full transparency - learn from failure but take reputation hit.'''
            gs.messages.append('? TRANSPARENCY: Full incident report published publicly.')
            gs._add('reputation', -failure.severity // 2)  # Immediate reputation cost
            
            # Long-term benefits
            self.transparency_reputation += 0.5
            if failure.failure_type not in self.lessons_learned:
                self.lessons_learned[failure.failure_type] = 0
            self.lessons_learned[failure.failure_type] += 2  # Double learning
            
            gs.messages.append('? Transparent handling builds long-term trust and learning.')
            
        def handle_investigation(gs):
            '''Thorough investigation - balanced approach.'''
            gs.messages.append('? INVESTIGATION: Internal review conducted, limited public disclosure.')
            gs._add('reputation', -max(1, failure.severity // 3))  # Reduced reputation cost
            gs._add('money', -get_rng().randint(10, 25, 'randint_context'))  # Investigation costs
            
            # Moderate learning
            if failure.failure_type not in self.lessons_learned:
                self.lessons_learned[failure.failure_type] = 0
            self.lessons_learned[failure.failure_type] += 1
            
        def handle_cover_up(gs):
            '''Cover up - preserve reputation but increase future risks.'''
            gs.messages.append('? COVER-UP: Incident classified, minimal public disclosure.')
            
            # No immediate reputation loss but accumulate cover-up debt
            self.cover_up_debt += failure.severity
            gs._add('money', -get_rng().randint(20, 40, 'randint_context'))  # Cover-up costs
            
            # Increase future failure chances
            if hasattr(gs, 'technical_debt'):
                gs.technical_debt.add_debt(failure.severity // 2)
                
            gs.messages.append('[WARNING]? Cover-up successful but may increase future risks.')
            
        # Use enhanced events if available
        if hasattr(self.game_state, 'enhanced_events_enabled') and self.game_state.enhanced_events_enabled:
            response_event = Event(
                name='Failure Response Decision',
                desc=response_desc,
                trigger=lambda gs: True,
                effect=handle_investigation,  # Default action
                event_type=EventType.POPUP,
                available_actions=[EventAction.ACCEPT, EventAction.DEFER, EventAction.DISMISS]
            )
            
            response_event.action_handlers = {
                'transparency': handle_transparency,
                'investigation': handle_investigation,
                'cover_up': handle_cover_up
            }
            
            if hasattr(self.game_state, 'pending_popup_events'):
                self.game_state.pending_popup_events.append(response_event)
            else:
                handle_investigation(self.game_state)  # Fallback
        else:
            # Simple random choice for now
            responses = [handle_transparency, handle_investigation, handle_cover_up]
            get_rng().choice(responses, 'choice_context')(self.game_state)
            
    def _offer_cascade_response(self, cascade: CascadeState) -> None:
        '''Offer choices for responding to a cascade situation.'''
        response_desc = (
            f'A failure cascade is developing! How do you want to respond? '
            f'Quick action may prevent additional failures but affect other resources.'
        )
        
        def handle_all_hands(gs):
            '''All-hands emergency response.'''
            gs.messages.append('[ALERT] ALL HANDS: Emergency response mobilized across all teams.')
            cascade.is_contained = True
            cascade.transparency_level = 0.8  # High visibility response
            
            # High cost but effective containment
            gs._add('money', -get_rng().randint(50, 100, 'randint_context'))
            gs._add('staff', -get_rng().randint(1, 2, 'randint_context'))  # Some staff burnout
            gs.messages.append('? Aggressive response contains cascade but exhausts resources.')
            
        def handle_systematic(gs):
            '''Systematic containment approach.'''
            gs.messages.append('[LIST] SYSTEMATIC: Following established incident response protocols.')
            
            # Moderate effectiveness based on incident response level
            containment_chance = 0.5 + (self.incident_response_level * 0.1)
            if get_rng().random('random_context') < containment_chance:
                cascade.is_contained = True
                gs.messages.append('? Systematic approach successfully contains cascade.')
            else:
                gs.messages.append('[WARNING]? Protocols help but cascade continues to develop.')
                
            cascade.transparency_level = 0.6
            gs._add('money', -get_rng().randint(20, 40, 'randint_context'))
            
        def handle_minimize(gs):
            '''Minimize response - try to contain quietly.'''
            gs.messages.append('? MINIMIZE: Quiet containment attempt to limit visibility.')
            cascade.transparency_level = 0.2  # Low visibility
            
            # Lower effectiveness but less cost
            containment_chance = 0.3 + (self.incident_response_level * 0.05)
            if get_rng().random('random_context') < containment_chance:
                cascade.is_contained = True
                gs.messages.append('? Minimal response surprisingly effective.')
            else:
                gs.messages.append('? Insufficient response allows cascade to worsen.')
                # Add extra subsequent failure
                self._add_cascade_failure(cascade)
                
        # Choose response (simplified for now)
        responses = [handle_all_hands, handle_systematic, handle_minimize]
        choice = get_rng().choice(responses, 'choice_context')
        choice(self.game_state)
        
    def _update_cascade(self, cascade: CascadeState) -> None:
        '''Update an ongoing cascade.'''
        cascade.total_turns += 1
        
        # If cascade is contained, resolve it
        if cascade.is_contained:
            self._resolve_cascade(cascade)
            return
            
        # Otherwise, potentially add more failures
        if cascade.total_turns <= 3 and get_rng().random('random_context') < 0.4:
            self._add_cascade_failure(cascade)
            
        # Auto-resolve after 3 turns
        if cascade.total_turns >= 3:
            self.game_state.messages.append('? Cascade eventually contained through persistent efforts.')
            self._resolve_cascade(cascade)
            
    def _add_cascade_failure(self, cascade: CascadeState) -> None:
        '''Add a subsequent failure to a cascade.'''
        # Select target failure type from cascade targets
        if not cascade.initiating_failure.cascade_targets:
            return
            
        target_type = get_rng().choice(cascade.initiating_failure.cascade_targets, 'choice_context')
        
        # Subsequent failures are usually less severe
        severity = max(1, cascade.initiating_failure.severity - get_rng().randint(1, 3, 'randint_context'))
        
        subsequent_failure = self._create_failure_event(target_type, severity)
        cascade.subsequent_failures.append(subsequent_failure)
        
        # Apply impact
        for resource, amount in subsequent_failure.immediate_impact.items():
            if hasattr(self.game_state, resource):
                self.game_state._add(resource, amount)
                
        self.game_state.messages.append(
            f'?? CASCADE: {subsequent_failure.description}'
        )
        
    def _resolve_cascade(self, cascade: CascadeState) -> None:
        '''Resolve a completed cascade.'''
        total_failures = 1 + len(cascade.subsequent_failures)
        
        self.game_state.messages.append(
            f'? CASCADE RESOLVED: {total_failures} failures over {cascade.total_turns} turns.'
        )
        
        # Apply long-term consequences based on response
        if cascade.transparency_level > 0.7:
            # High transparency builds trust
            self.transparency_reputation += 1.0
            self.game_state.messages.append('? Transparent cascade handling builds stakeholder trust.')
        elif cascade.transparency_level < 0.3:
            # Low transparency increases cover-up debt
            self.cover_up_debt += total_failures * 2
            self.game_state.messages.append('[WARNING]? Quiet handling increases institutional risk.')
            
        # Learning from cascades
        for failure in [cascade.initiating_failure] + cascade.subsequent_failures:
            if failure.failure_type not in self.lessons_learned:
                self.lessons_learned[failure.failure_type] = 0
            self.lessons_learned[failure.failure_type] += 1
            
        # Remove from active cascades
        if cascade in self.active_cascades:
            self.active_cascades.remove(cascade)
            
    def get_resilience_bonus(self, failure_type: FailureType) -> float:
        '''Get resilience bonus for a specific failure type based on lessons learned.'''
        if failure_type not in self.lessons_learned:
            return 0.0
            
        lessons = self.lessons_learned[failure_type]
        return min(0.5, lessons * 0.1)  # Max 50% reduction, 10% per lesson
        
    def get_cover_up_risk_modifier(self) -> float:
        '''Get risk modifier based on accumulated cover-up debt.'''
        if self.cover_up_debt == 0:
            return 1.0
            
        # Each point of cover-up debt increases future failure chance by 5%
        return 1.0 + (self.cover_up_debt * 0.05)
        
    def get_transparency_reputation_bonus(self) -> int:
        '''Get reputation bonus from transparent failure handling.'''
        return int(self.transparency_reputation)
        
    def upgrade_incident_response(self, cost: int) -> bool:
        '''Upgrade incident response capabilities.'''
        if self.game_state.money >= cost and self.incident_response_level < 5:
            self.game_state._add('money', -cost)
            self.incident_response_level += 1
            self.game_state.messages.append(
                f'[LIST] Incident Response upgraded to level {self.incident_response_level}'
            )
            return True
        return False
        
    def upgrade_monitoring_systems(self, cost: int) -> bool:
        '''Upgrade monitoring and early warning systems.'''
        if self.game_state.money >= cost and self.monitoring_systems < 5:
            self.game_state._add('money', -cost)
            self.monitoring_systems += 1
            self.game_state.messages.append(
                f'? Monitoring Systems upgraded to level {self.monitoring_systems}'
            )
            return True
        return False
        
    def upgrade_communication_protocols(self, cost: int) -> bool:
        '''Upgrade communication and coordination protocols.'''
        if self.game_state.money >= cost and self.communication_protocols < 5:
            self.game_state._add('money', -cost)
            self.communication_protocols += 1
            self.game_state.messages.append(
                f'? Communication Protocols upgraded to level {self.communication_protocols}'
            )
            return True
        return False
        
    def get_failure_cascade_summary(self) -> Dict[str, Any]:
        '''Get summary of failure cascade system state for UI.'''
        return {
            'active_cascades': len(self.active_cascades),
            'total_failures': len(self.failure_history),
            'near_misses': self.near_miss_count,
            'transparency_reputation': self.transparency_reputation,
            'cover_up_debt': self.cover_up_debt,
            'incident_response_level': self.incident_response_level,
            'monitoring_systems': self.monitoring_systems,
            'communication_protocols': self.communication_protocols,
            'lessons_learned': dict(self.lessons_learned)
        }

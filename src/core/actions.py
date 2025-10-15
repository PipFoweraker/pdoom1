from src.services.deterministic_rng import get_rng
from typing import TYPE_CHECKING

from src.core.action_rules import manager_unlock_rule, search_unlock_rule

if TYPE_CHECKING:
    from src.core.game_state import GameState

def execute_fundraising_action(gs: 'GameState') -> None:
    '''
    Execute enhanced fundraising action using economic cycles system.
    
    Args:
        gs: GameState instance
    '''
    from src.features.economic_cycles import FundingSource 
    # Check if economic cycles system is available
    if not hasattr(gs, 'economic_cycles'):
        # Fallback to original fundraising logic
        amount = get_rng().randint(40, 70, 'randint_context') + gs.reputation * 2
        gs._add('money', amount)
        gs.messages.append(f'Raised ${amount}k in funding')
        return
    
    # Get available funding sources
    funding_info = gs.economic_cycles.get_funding_round_info()
    available_sources = funding_info['available_sources']
    
    if not available_sources:
        gs.messages.append('No funding sources available given current reputation and market conditions')
        return
    
    # Choose funding source (prefer venture during boom, government during recession)
    phase = funding_info['phase']
    
    # Smart source selection based on market conditions
    if phase.name == 'BOOM' and any(s['source'] == FundingSource.VENTURE for s in available_sources):
        chosen_source = next(s for s in available_sources if s['source'] == FundingSource.VENTURE)
    elif phase.name in ['RECESSION', 'CORRECTION'] and any(s['source'] == FundingSource.GOVERNMENT for s in available_sources):
        chosen_source = next(s for s in available_sources if s['source'] == FundingSource.GOVERNMENT)
    else:
        # Choose best available multiplier
        chosen_source = max(available_sources, key=lambda s: s['multiplier'])
    
    # Calculate funding amount
    base_amount = get_rng().randint(40, 70, 'randint_context') + gs.reputation * 2
    multiplier = chosen_source['multiplier']
    final_amount = int(base_amount * multiplier)
    
    # Apply funding
    gs._add('money', final_amount)
    
    # Record funding round
    gs.economic_cycles.record_funding_round(final_amount, chosen_source['source'], gs.turn)
    
    # Generate appropriate message
    source_name = chosen_source['source'].value.title()
    phase_context = f'during {phase.name.lower()} market conditions' if multiplier != 1.0 else ''
    gs.messages.append(f'Secured ${final_amount}k from {source_name} {phase_context}')
    
    # Unlock advanced funding actions after first major round
    if final_amount >= 100 and not hasattr(gs, 'advanced_funding_unlocked'):
        gs.advanced_funding_unlocked = True
        gs.messages.append('Advanced funding strategies now available!')

def execute_series_a_funding(gs: 'GameState') -> None:
    '''Execute Series A venture capital funding round.'''
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback for missing economic system
        amount = get_rng().randint(150, 300, 'randint_context') + gs.reputation * 5
        gs._add('money', amount)
        gs.messages.append(f'Secured ${amount}k in Series A funding')
        return
    
    # Series A is heavily dependent on venture capital markets
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.VENTURE)
    
    if multiplier < 0.6:  # Difficult VC environment
        gs.messages.append('Series A funding extremely difficult in current market conditions')
        gs.messages.append('Consider alternative funding sources or wait for market recovery')
        return
    
    # Calculate substantial funding amount
    base_amount = get_rng().randint(150, 300, 'randint_context') + gs.reputation * 5
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.VENTURE, gs.turn)
    
    phase = gs.economic_cycles.current_state.phase.name
    gs.messages.append(f'Series A completed: ${final_amount}k from institutional VCs')
    gs.messages.append(f'Market conditions: {phase.lower()}')

def execute_government_grant_application(gs: 'GameState') -> None:
    '''Execute government grant application.'''
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = get_rng().randint(50, 120, 'randint_context')
        gs._add('money', amount)
        gs.messages.append(f'Government grant awarded: ${amount}k')
        return
    
    # Government funding is counter-cyclical (better during downturns)
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.GOVERNMENT)
    
    # Base amount depends on reputation and safety focus
    safety_bonus = 20 if gs.reputation >= 15 else 0
    base_amount = get_rng().randint(50, 100, 'randint_context') + safety_bonus
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.GOVERNMENT, gs.turn)
    
    # Government grants have different requirements
    if multiplier > 1.2:
        gs.messages.append(f'Emergency government funding secured: ${final_amount}k')
    else:
        gs.messages.append(f'Government research grant awarded: ${final_amount}k')
    
    # Small reputation boost for government validation
    gs._add('reputation', 1)

def execute_corporate_partnership(gs: 'GameState') -> None:
    '''Execute corporate strategic partnership.'''
    from src.features.economic_cycles import FundingSource
    
    corp_names = ['TechGiant', 'DataCorp', 'CloudSystems', 'AutomationInc']
    partner = get_rng().choice(corp_names, 'choice_context')
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = get_rng().randint(80, 200, 'randint_context')
        gs._add('money', amount)
        gs.messages.append(f'Partnership with {partner}: ${amount}k investment')
        return
    
    # Corporate partnerships are less volatile than VC
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.CORPORATE)
    
    # Amount based on reputation and staff size
    base_amount = get_rng().randint(80, 150, 'randint_context') + gs.reputation * 3 + gs.staff * 5
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.CORPORATE, gs.turn)
    
    gs.messages.append(f'Strategic partnership with {partner}: ${final_amount}k')
    
    # Corporate partnerships provide some stability but limit growth
    if get_rng().random('random_context') < 0.7:
        gs._add('reputation', get_rng().randint(1, 3, 'randint_context'))
    else:
        gs.messages.append('Partnership comes with operational constraints')

def execute_revenue_diversification(gs: 'GameState') -> None:
    '''Execute revenue diversification strategy.'''
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = get_rng().randint(30, 80, 'randint_context')
        gs._add('money', amount)
        gs.messages.append(f'Customer revenue generated: ${amount}k')
        return
    
    # Revenue depends on market conditions and reputation
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.REVENUE)
    
    # Revenue scales with reputation and staff capability
    base_amount = gs.reputation * 2 + gs.staff * 3 + get_rng().randint(20, 50, 'randint_context')
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.REVENUE, gs.turn)
    
    gs.messages.append(f'Customer revenue diversification: +${final_amount}k recurring income')
    
    # Revenue diversification reduces funding dependency
    if not hasattr(gs, 'revenue_streams'):
        gs.revenue_streams = 0
    gs.revenue_streams += 1
    
    if gs.revenue_streams >= 3:
        gs.messages.append('Significant revenue diversification achieved - reduced funding dependence!')
        gs._add('reputation', 2)

def execute_research_action(gs: 'GameState', action_name: str, base_doom_reduction: int, base_reputation_gain: int) -> None:
    '''
    Execute a research action using the research quality system.
    
    Args:
        gs: GameState instance
        action_name: Name of the research action for project tracking
        base_doom_reduction: Base doom reduction before modifiers
        base_reputation_gain: Base reputation gain before modifiers
    '''
    from src.core.research_quality import calculate_research_outcome
    from src.features.public_opinion import create_media_story_from_action
    
    # Create a research project for this action
    project = gs.create_research_project(action_name, 0, 1)  # Cost and duration handled by action itself
    
    # Calculate outcome with quality modifiers and technical debt
    doom_change, reputation_change, debt_change, messages = calculate_research_outcome(
        base_doom_reduction, base_reputation_gain, gs.current_research_quality, gs.technical_debt
    )
    
    # Apply the calculated effects
    gs._add('doom', -doom_change, f'research action: {action_name}')  # Negative because we're reducing doom
    gs._add('reputation', reputation_change)
    
    # Add research quality messages
    gs.messages.extend(messages)
    
    # Complete the project to apply debt changes
    gs.complete_research_project(project)
    
    # Unlock research quality system on first use
    if not gs.research_quality_unlocked:
        gs.research_quality_unlocked = True
        gs.messages.append('? Research Quality System unlocked! Choose your approach wisely.')
    
    # Generate media story if research has significant impact
    if hasattr(gs, 'media_system') and reputation_change >= 2:
        # Map action names to media-friendly types
        action_mapping = {
            'Safety Research': 'safety_research',
            'Governance Research': 'safety_research', 
            'Interpretability Research': 'safety_research',
            'AI Alignment Research': 'safety_research'
        }
        
        media_action_name = action_mapping.get(action_name, 'safety_research')
        company_name = getattr(gs, 'company_name', 'Your Lab')
        
        media_story = create_media_story_from_action(
            media_action_name, company_name, gs.turn, reputation_change
        )
        
        if media_story:
            gs.media_system.public_opinion.add_media_story(media_story)

def get_quality_modified_cost(base_cost: int, gs) -> int:
    '''Get cost modified by current research quality.'''
    from src.core.research_quality import QUALITY_MODIFIERS
    modifiers = QUALITY_MODIFIERS[gs.current_research_quality]
    return int(base_cost * modifiers.cost_multiplier)

def get_quality_description_suffix(gs) -> str:
    '''Get description suffix showing current research quality.'''
    if not hasattr(gs, 'current_research_quality'):
        return ''
    
    quality = gs.current_research_quality.value.title()
    if quality == 'Standard':
        return ''
    return f' [{quality} approach]'

# Technical Failure Cascade Prevention Actions for Issue #193

def execute_incident_response_upgrade(gs: 'GameState') -> None:
    '''Execute incident response capability upgrade.'''
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append('Incident response training conducted for all staff')
        gs._add('reputation', 1)
        return
        
    upgrade_cost = (gs.technical_failures.incident_response_level + 1) * 30
    if gs.technical_failures.upgrade_incident_response(upgrade_cost):
        gs.messages.append('Teams trained in advanced incident response protocols')
        gs._add('reputation', 1)
    else:
        gs.messages.append('Insufficient funds for incident response upgrade')

def execute_monitoring_systems_upgrade(gs: 'GameState') -> None:
    '''Execute monitoring systems upgrade.'''
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append('Monitoring systems enhanced for better oversight')
        gs._add('compute', 5)
        return
        
    upgrade_cost = (gs.technical_failures.monitoring_systems + 1) * 40
    if gs.technical_failures.upgrade_monitoring_systems(upgrade_cost):
        gs.messages.append('Advanced monitoring and early warning systems deployed')
        gs._add('compute', 2)  # Monitoring requires some compute
    else:
        gs.messages.append('Insufficient funds for monitoring system upgrade')

def execute_communication_protocols_upgrade(gs: 'GameState') -> None:
    '''Execute communication protocols upgrade.'''
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append('Communication protocols standardized across organization')
        gs._add('reputation', 1)
        return
        
    upgrade_cost = (gs.technical_failures.communication_protocols + 1) * 25
    if gs.technical_failures.upgrade_communication_protocols(upgrade_cost):
        gs.messages.append('Cross-team coordination and crisis communication improved')
        gs._add('reputation', 1)
    else:
        gs.messages.append('Insufficient funds for communication protocol upgrade')

def execute_safety_audit(gs: 'GameState') -> None:
    '''Execute comprehensive safety audit to reduce technical debt and prevent failures.'''
    audit_cost = 60
    
    if gs.money < audit_cost:
        gs.messages.append('Insufficient funds for comprehensive safety audit')
        return
        
    gs._add('money', -audit_cost)
    
    # Reduce technical debt significantly
    if hasattr(gs, 'technical_debt'):
        debt_reduced = get_rng().randint(3, 6, 'randint_context')
        gs.technical_debt.reduce_debt(debt_reduced)
        gs.messages.append(f'Safety audit identifies and resolves {debt_reduced} technical debt issues')
    
    # Improve failure prevention temporarily
    if hasattr(gs, 'technical_failures'):
        # Temporary improvement to all prevention systems
        gs.messages.append('Audit recommendations strengthen all incident response capabilities')
        gs._add('reputation', 2)
    else:
        gs.messages.append('Comprehensive safety audit improves organizational practices')
        gs._add('reputation', 2)
        
    # Small chance to discover near-miss that could have been a failure
    if get_rng().random('random_context') < 0.3:
        gs.messages.append('[WARNING]? Audit discovers potential failure that was narrowly avoided!')
        if hasattr(gs, 'technical_failures'):
            gs.technical_failures.near_miss_count += 1

ACTIONS = [
    {
        'name': 'Grow Community',
        'desc': '+Reputation, possible staff; costs money.',
        'cost': 25,
        'ap_cost': 1,  # Action Points cost
        'delegatable': True,  # Can be delegated to admin staff
        'delegate_staff_req': 1,  # Requires 1 admin staff to delegate
        'delegate_ap_cost': 0,  # Lower AP cost when delegated (routine task)
        'delegate_effectiveness': 1.0,  # Full effectiveness when delegated
        'upside': lambda gs: (gs._add('reputation', get_rng().randint(2, 5, 'randint_context')),
                              gs._add('staff', get_rng().choice([0, 1]))),
        'downside': lambda gs: None,
        'rules': None
    },
    {
        'name': 'Fundraising Options',
        'desc': 'Open fundraising menu with multiple strategic options',
        'cost': 0,
        'ap_cost': 0,  # No AP cost for opening menu
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to admin staff
        'delegate_staff_req': 1,  # Requires 1 admin staff to delegate  
        'delegate_ap_cost': 1,  # Same AP cost when delegated (requires personal touch)
        'delegate_effectiveness': 0.9,  # 90% effectiveness when delegated
        'upside': lambda gs: gs._trigger_fundraising_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': None  # Always available - balance through other mechanics
    },
    {
        'name': 'Research Options',
        'desc': 'Open research menu with strategic focus and quality options',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to research staff
        'delegate_staff_req': 2,  # Requires 2 research staff to delegate
        'delegate_ap_cost': 1,  # Same AP cost when delegated
        'delegate_effectiveness': 0.9,  # 90% effectiveness when delegated (research planning)
        'upside': lambda gs: gs._trigger_research_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': None  # Always available - balance through other mechanics
    },
    # DEMO HOTFIX: 'Buy Compute' moved to Infrastructure dialog - commented out standalone action
    # {
    #     'name': 'Buy Compute',
    #     'desc': 'Purchase compute resources. Cost decreases over time (Moore's Law).',
    #     'cost': lambda gs: gs.economic_config.get_compute_cost(10),
    #     'ap_cost': 1,  # Action Points cost
    #     'delegatable': True,  # Phase 3: Can be delegated (operational task)
    #     'delegate_staff_req': 1,  # Requires 1 operations staff to delegate
    #     'delegate_ap_cost': 0,  # Lower AP cost when delegated (routine task)
    #     'delegate_effectiveness': 1.0,  # Full effectiveness when delegated (routine task)
    #     'upside': lambda gs: gs._add('compute', 10),
    #     'downside': lambda gs: None,
    #     'rules': None
    # },
    {
        'name': 'Hire Staff',
        'desc': 'Open hiring dialog to select from available employee types.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'upside': lambda gs: gs._trigger_hiring_dialog(),
        'downside': lambda gs: None,
        'rules': None
    },
    {
        'name': 'Intelligence',
        'desc': 'Open intelligence dialog to select from scouting and information gathering options.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'upside': lambda gs: gs._trigger_intelligence_dialog(),
        'downside': lambda gs: None,
        'rules': None
    },
    {
        'name': 'Media & PR',
        'desc': 'Open media & PR dialog to select from press releases, interviews, and communication options.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to admin staff
        'delegate_staff_req': 1,  # Requires 1 admin staff to delegate
        'delegate_ap_cost': 1,  # Same AP cost when delegated (requires coordination)
        'delegate_effectiveness': 0.9,  # 90% effectiveness when delegated
        'upside': lambda gs: gs._trigger_media_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': None
    },
    {
        'name': 'Technical Debt',
        'desc': 'Open technical debt management dialog for code quality and safety improvements.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to research staff
        'delegate_staff_req': 2,  # Requires 2 research staff to delegate (technical work)
        'delegate_ap_cost': 1,  # Same AP cost when delegated
        'delegate_effectiveness': 0.85,  # 85% effectiveness when delegated (requires oversight)
        'upside': lambda gs: gs._trigger_technical_debt_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': None
    },
    {
        'name': 'Advanced Funding',
        'desc': 'Open advanced funding dialog for Series A, grants, partnerships, and revenue diversification.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to admin staff
        'delegate_staff_req': 1,  # Requires 1 admin staff to delegate
        'delegate_ap_cost': 1,  # Same AP cost when delegated (requires coordination)
        'delegate_effectiveness': 0.8,  # 80% effectiveness when delegated (requires personal touch)
        'upside': lambda gs: gs._trigger_advanced_funding_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': lambda gs: getattr(gs, 'advanced_funding_unlocked', False)  # Requires advanced funding to be unlocked
    },
    {
        'name': 'Infrastructure',
        'desc': 'Open infrastructure dialog for incident response, monitoring systems, and communication protocols.',
        'cost': 0,  # No immediate cost - cost depends on selection
        'ap_cost': 1,
        'action_type': 'submenu',  # Opens dialog menu
        'delegatable': True,  # Can be delegated to operations staff
        'delegate_staff_req': 1,  # Requires 1 operations staff to delegate
        'delegate_ap_cost': 1,  # Same AP cost when delegated
        'delegate_effectiveness': 0.9,  # 90% effectiveness when delegated (operational tasks)
        'upside': lambda gs: gs._trigger_infrastructure_dialog(),
        'downside': lambda gs: None,  # No downside for opening menu
        'rules': None  # Always available - balance through other mechanics
    },
    {
        'name': 'Hire Manager',
        'desc': 'Team leader; required for organizations with 9+ employees.',
        'cost': 90,
        'ap_cost': 1,
        'upside': lambda gs: gs._hire_employee_subtype('manager'),
        'downside': lambda gs: None,
        'rules': manager_unlock_rule
    },
    {
        'name': 'Search',
        'desc': 'Board-mandated compliance searches (20% success rate). Unlocks with board members.',
        'cost': 25,
        'ap_cost': 1,  # Action Points cost
        'upside': lambda gs: gs._board_search(),
        'downside': lambda gs: None,
        'rules': search_unlock_rule  # Requires board members (refactored rule)
    },
    # DEMO HOTFIX: 'Refresh Researchers' moved to Hire Staff dialog - commented out standalone action
    # {
    #     'name': 'Refresh Researchers',
    #     'desc': 'Get new specialist researcher applications for hiring.',
    #     'cost': 10,
    #     'ap_cost': 1,
    #     'upside': lambda gs: gs.refresh_researcher_hiring_pool(),
    #     'downside': lambda gs: None,
    #     'rules': lambda gs: hasattr(gs, 'researchers')  # Only available if researcher system is enabled
    # },
    {
        'name': 'Team Building',
        'desc': 'Reduce researcher burnout and improve team cohesion ($50).',
        'cost': 50,
        'ap_cost': 1,
        'upside': lambda gs: gs.conduct_researcher_management_action('team_building', cost=50),
        'downside': lambda gs: None,
        'rules': lambda gs: hasattr(gs, 'researchers') and len(gs.researchers) > 0
    },
    {
        'name': 'Safety Research',
        'desc': 'Traditional AI safety research - interpretability, alignment, robustness (costs $40k)',
        'cost': 40,
        'ap_cost': 1,
        'delegatable': True,  # Can be delegated to research staff
        'delegate_staff_req': 2,  # Requires 2 research staff to delegate
        'delegate_ap_cost': 1,  # Same AP cost when delegated (complex task)
        'delegate_effectiveness': 0.9,  # 90% effectiveness when delegated
        'upside': lambda gs: gs._execute_standalone_safety_research(),
        'downside': lambda gs: None,
        'rules': None  # Always available
    },
    {
        'name': 'Safety Audit',
        'desc': 'Comprehensive audit to identify and fix potential failure points',
        'cost': 60,
        'ap_cost': 2,
        'upside': lambda gs: execute_safety_audit(gs),
        'downside': lambda gs: None,
        'rules': lambda gs: gs.staff >= 3  # Need sufficient staff for meaningful audit
    }
]
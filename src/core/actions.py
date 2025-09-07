import random
from src.core.action_rules import manager_unlock_rule, scout_unlock_rule, search_unlock_rule
from src.core.research_quality import ResearchQuality

def execute_fundraising_action(gs):
    """
    Execute enhanced fundraising action using economic cycles system.
    
    Args:
        gs: GameState instance
    """
    from src.features.economic_cycles import FundingSource
    
    # Check if economic cycles system is available
    if not hasattr(gs, 'economic_cycles'):
        # Fallback to original fundraising logic
        amount = random.randint(40, 70) + gs.reputation * 2
        gs._add('money', amount)
        gs.messages.append(f"Raised ${amount}k in funding")
        return
    
    # Get available funding sources
    funding_info = gs.economic_cycles.get_funding_round_info()
    available_sources = funding_info['available_sources']
    
    if not available_sources:
        gs.messages.append("No funding sources available given current reputation and market conditions")
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
    base_amount = random.randint(40, 70) + gs.reputation * 2
    multiplier = chosen_source['multiplier']
    final_amount = int(base_amount * multiplier)
    
    # Apply funding
    gs._add('money', final_amount)
    
    # Record funding round
    gs.economic_cycles.record_funding_round(final_amount, chosen_source['source'], gs.turn)
    
    # Set cooldown to prevent excessive fundraising
    gs.funding_round_cooldown = 3  # 3 turn cooldown
    
    # Generate appropriate message
    source_name = chosen_source['source'].value.title()
    phase_context = f"during {phase.name.lower()} market conditions" if multiplier != 1.0 else ""
    gs.messages.append(f"Secured ${final_amount}k from {source_name} {phase_context}")
    
    # Unlock advanced funding actions after first major round
    if final_amount >= 100 and not hasattr(gs, 'advanced_funding_unlocked'):
        gs.advanced_funding_unlocked = True
        gs.messages.append("Advanced funding strategies now available!")

def execute_series_a_funding(gs):
    """Execute Series A venture capital funding round."""
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback for missing economic system
        amount = random.randint(150, 300) + gs.reputation * 5
        gs._add('money', amount)
        gs.messages.append(f"Secured ${amount}k in Series A funding")
        return
    
    # Series A is heavily dependent on venture capital markets
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.VENTURE)
    
    if multiplier < 0.6:  # Difficult VC environment
        gs.messages.append("Series A funding extremely difficult in current market conditions")
        gs.messages.append("Consider alternative funding sources or wait for market recovery")
        return
    
    # Calculate substantial funding amount
    base_amount = random.randint(150, 300) + gs.reputation * 5
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.VENTURE, gs.turn)
    
    # Longer cooldown for major rounds
    gs.funding_round_cooldown = 5
    
    phase = gs.economic_cycles.current_state.phase.name
    gs.messages.append(f"Series A completed: ${final_amount}k from institutional VCs")
    gs.messages.append(f"Market conditions: {phase.lower()}")

def execute_government_grant_application(gs):
    """Execute government grant application."""
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = random.randint(50, 120)
        gs._add('money', amount)
        gs.messages.append(f"Government grant awarded: ${amount}k")
        return
    
    # Government funding is counter-cyclical (better during downturns)
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.GOVERNMENT)
    
    # Base amount depends on reputation and safety focus
    safety_bonus = 20 if gs.reputation >= 15 else 0
    base_amount = random.randint(50, 100) + safety_bonus
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.GOVERNMENT, gs.turn)
    
    # Government grants have different requirements
    if multiplier > 1.2:
        gs.messages.append(f"Emergency government funding secured: ${final_amount}k")
    else:
        gs.messages.append(f"Government research grant awarded: ${final_amount}k")
    
    # Small reputation boost for government validation
    gs._add('reputation', 1)

def execute_corporate_partnership(gs):
    """Execute corporate strategic partnership."""
    from src.features.economic_cycles import FundingSource
    
    corp_names = ["TechGiant", "DataCorp", "CloudSystems", "AutomationInc"]
    partner = random.choice(corp_names)
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = random.randint(80, 200)
        gs._add('money', amount)
        gs.messages.append(f"Partnership with {partner}: ${amount}k investment")
        return
    
    # Corporate partnerships are less volatile than VC
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.CORPORATE)
    
    # Amount based on reputation and staff size
    base_amount = random.randint(80, 150) + gs.reputation * 3 + gs.staff * 5
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.CORPORATE, gs.turn)
    
    gs.messages.append(f"Strategic partnership with {partner}: ${final_amount}k")
    
    # Corporate partnerships provide some stability but limit growth
    if random.random() < 0.7:
        gs._add('reputation', random.randint(1, 3))
    else:
        gs.messages.append("Partnership comes with operational constraints")

def execute_revenue_diversification(gs):
    """Execute revenue diversification strategy."""
    from src.features.economic_cycles import FundingSource
    
    if not hasattr(gs, 'economic_cycles'):
        # Fallback
        amount = random.randint(30, 80)
        gs._add('money', amount)
        gs.messages.append(f"Customer revenue generated: ${amount}k")
        return
    
    # Revenue depends on market conditions and reputation
    multiplier = gs.economic_cycles.get_funding_multiplier(FundingSource.REVENUE)
    
    # Revenue scales with reputation and staff capability
    base_amount = gs.reputation * 2 + gs.staff * 3 + random.randint(20, 50)
    final_amount = int(base_amount * multiplier)
    
    gs._add('money', final_amount)
    gs.economic_cycles.record_funding_round(final_amount, FundingSource.REVENUE, gs.turn)
    
    gs.messages.append(f"Customer revenue diversification: +${final_amount}k recurring income")
    
    # Revenue diversification reduces funding dependency
    if not hasattr(gs, 'revenue_streams'):
        gs.revenue_streams = 0
    gs.revenue_streams += 1
    
    if gs.revenue_streams >= 3:
        gs.messages.append("Significant revenue diversification achieved - reduced funding dependence!")
        gs._add('reputation', 2)

def execute_research_action(gs, action_name: str, base_doom_reduction: int, base_reputation_gain: int):
    """
    Execute a research action using the research quality system.
    
    Args:
        gs: GameState instance
        action_name: Name of the research action for project tracking
        base_doom_reduction: Base doom reduction before modifiers
        base_reputation_gain: Base reputation gain before modifiers
    """
    from src.core.research_quality import calculate_research_outcome
    from src.features.public_opinion import create_media_story_from_action
    
    # Create a research project for this action
    project = gs.create_research_project(action_name, 0, 1)  # Cost and duration handled by action itself
    
    # Calculate outcome with quality modifiers and technical debt
    doom_change, reputation_change, debt_change, messages = calculate_research_outcome(
        base_doom_reduction, base_reputation_gain, gs.current_research_quality, gs.technical_debt
    )
    
    # Apply the calculated effects
    gs._add('doom', -doom_change)  # Negative because we're reducing doom
    gs._add('reputation', reputation_change)
    
    # Add research quality messages
    gs.messages.extend(messages)
    
    # Complete the project to apply debt changes
    gs.complete_research_project(project)
    
    # Unlock research quality system on first use
    if not gs.research_quality_unlocked:
        gs.research_quality_unlocked = True
        gs.messages.append("🔬 Research Quality System unlocked! Choose your approach wisely.")
    
    # Generate media story if research has significant impact
    if hasattr(gs, 'media_system') and reputation_change >= 2:
        # Map action names to media-friendly types
        action_mapping = {
            "Safety Research": "safety_research",
            "Governance Research": "safety_research", 
            "Interpretability Research": "safety_research",
            "AI Alignment Research": "safety_research"
        }
        
        media_action_name = action_mapping.get(action_name, "safety_research")
        company_name = getattr(gs, 'company_name', 'Your Lab')
        
        media_story = create_media_story_from_action(
            media_action_name, company_name, gs.turn, reputation_change
        )
        
        if media_story:
            gs.media_system.public_opinion.add_media_story(media_story)

def get_quality_modified_cost(base_cost: int, gs) -> int:
    """Get cost modified by current research quality."""
    from src.core.research_quality import QUALITY_MODIFIERS
    modifiers = QUALITY_MODIFIERS[gs.current_research_quality]
    return int(base_cost * modifiers.cost_multiplier)

def get_quality_description_suffix(gs) -> str:
    """Get description suffix showing current research quality."""
    if not hasattr(gs, 'current_research_quality'):
        return ""
    
    quality = gs.current_research_quality.value.title()
    if quality == "Standard":
        return ""
    return f" [{quality} approach]"

# Technical Failure Cascade Prevention Actions for Issue #193

def execute_incident_response_upgrade(gs):
    """Execute incident response capability upgrade."""
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append("Incident response training conducted for all staff")
        gs._add('reputation', 1)
        return
        
    upgrade_cost = (gs.technical_failures.incident_response_level + 1) * 30
    if gs.technical_failures.upgrade_incident_response(upgrade_cost):
        gs.messages.append("Teams trained in advanced incident response protocols")
        gs._add('reputation', 1)
    else:
        gs.messages.append("Insufficient funds for incident response upgrade")

def execute_monitoring_systems_upgrade(gs):
    """Execute monitoring systems upgrade."""
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append("Monitoring systems enhanced for better oversight")
        gs._add('compute', 5)
        return
        
    upgrade_cost = (gs.technical_failures.monitoring_systems + 1) * 40
    if gs.technical_failures.upgrade_monitoring_systems(upgrade_cost):
        gs.messages.append("Advanced monitoring and early warning systems deployed")
        gs._add('compute', 2)  # Monitoring requires some compute
    else:
        gs.messages.append("Insufficient funds for monitoring system upgrade")

def execute_communication_protocols_upgrade(gs):
    """Execute communication protocols upgrade."""
    if not hasattr(gs, 'technical_failures'):
        gs.messages.append("Communication protocols standardized across organization")
        gs._add('reputation', 1)
        return
        
    upgrade_cost = (gs.technical_failures.communication_protocols + 1) * 25
    if gs.technical_failures.upgrade_communication_protocols(upgrade_cost):
        gs.messages.append("Cross-team coordination and crisis communication improved")
        gs._add('reputation', 1)
    else:
        gs.messages.append("Insufficient funds for communication protocol upgrade")

def execute_safety_audit(gs):
    """Execute comprehensive safety audit to reduce technical debt and prevent failures."""
    audit_cost = 60
    
    if gs.money < audit_cost:
        gs.messages.append("Insufficient funds for comprehensive safety audit")
        return
        
    gs._add('money', -audit_cost)
    
    # Reduce technical debt significantly
    if hasattr(gs, 'technical_debt'):
        debt_reduced = random.randint(3, 6)
        gs.technical_debt.reduce_debt(debt_reduced)
        gs.messages.append(f"Safety audit identifies and resolves {debt_reduced} technical debt issues")
    
    # Improve failure prevention temporarily
    if hasattr(gs, 'technical_failures'):
        # Temporary improvement to all prevention systems
        gs.messages.append("Audit recommendations strengthen all incident response capabilities")
        gs._add('reputation', 2)
    else:
        gs.messages.append("Comprehensive safety audit improves organizational practices")
        gs._add('reputation', 2)
        
    # Small chance to discover near-miss that could have been a failure
    if random.random() < 0.3:
        gs.messages.append("⚠️ Audit discovers potential failure that was narrowly avoided!")
        if hasattr(gs, 'technical_failures'):
            gs.technical_failures.near_miss_count += 1

ACTIONS = [
    {
        "name": "Grow Community",
        "desc": "+Reputation, possible staff; costs money.",
        "cost": 25,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Can be delegated to admin staff
        "delegate_staff_req": 1,  # Requires 1 admin staff to delegate
        "delegate_ap_cost": 0,  # Lower AP cost when delegated (routine task)
        "delegate_effectiveness": 1.0,  # Full effectiveness when delegated
        "upside": lambda gs: (gs._add('reputation', random.randint(2, 5)),
                              gs._add('staff', random.choice([0, 1]))),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Fundraise",
        "desc": "Raise capital (amount varies by market conditions and reputation)",
        "cost": 0,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Can be delegated to admin staff
        "delegate_staff_req": 1,  # Requires 1 admin staff to delegate  
        "delegate_ap_cost": 1,  # Same AP cost when delegated (requires personal touch)
        "delegate_effectiveness": 0.9,  # 90% effectiveness when delegated
        "upside": lambda gs: execute_fundraising_action(gs),
        "downside": lambda gs: gs._add('reputation', -1 if random.random() < 0.25 else 0),
        "rules": lambda gs: getattr(gs, 'funding_round_cooldown', 0) <= 0
    },
    {
        "name": "Safety Research",
        "desc": "Reduce doom, +rep. Costly. Quality affects effectiveness and debt.",
        "cost": 40,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Phase 3: Can be delegated
        "delegate_staff_req": 2,  # Requires 2 research staff to delegate
        "delegate_ap_cost": 1,  # Same AP cost when delegated (research is complex)
        "delegate_effectiveness": 0.8,  # 80% effectiveness when delegated
        "upside": lambda gs: execute_research_action(gs, "Safety Research", 
                                                   random.randint(2, 6) + 
                                                   (1 if 'better_computers' in gs.upgrade_effects else 0) +
                                                   (2 if 'hpc_cluster' in gs.upgrade_effects else 0) +
                                                   (1 if 'research_automation' in gs.upgrade_effects and gs.compute >= 10 else 0),
                                                   2),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Governance Research",
        "desc": "Reduce doom, +reputation. Costly. Quality affects effectiveness and debt.",
        "cost": 45,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Phase 3: Can be delegated
        "delegate_staff_req": 2,  # Requires 2 research staff to delegate
        "delegate_ap_cost": 1,  # Same AP cost when delegated
        "delegate_effectiveness": 0.8,  # 80% effectiveness when delegated
        "upside": lambda gs: execute_research_action(gs, "Governance Research",
                                                   random.randint(2, 5) + 
                                                   (1 if 'better_computers' in gs.upgrade_effects else 0) +
                                                   (2 if 'hpc_cluster' in gs.upgrade_effects else 0) +
                                                   (1 if 'research_automation' in gs.upgrade_effects and gs.compute >= 10 else 0),
                                                   3),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Buy Compute",
        "desc": "Purchase compute resources. $100 per 10 flops.",
        "cost": 100,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Phase 3: Can be delegated (operational task)
        "delegate_staff_req": 1,  # Requires 1 operations staff to delegate
        "delegate_ap_cost": 0,  # Lower AP cost when delegated (routine task)
        "delegate_effectiveness": 1.0,  # Full effectiveness when delegated (routine task)
        "upside": lambda gs: gs._add('compute', 10),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Staff",
        "desc": "Open hiring dialog to select from available employee types.",
        "cost": 0,  # No immediate cost - cost depends on selection
        "ap_cost": 1,
        "upside": lambda gs: gs._trigger_hiring_dialog(),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Scout Opponents",
        "desc": "Gather intelligence on competing labs; reveals their capabilities.",
        "cost": 75,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Can be delegated to admin staff
        "delegate_staff_req": 1,  # Requires 1 admin staff to delegate
        "delegate_ap_cost": 1,  # Same AP cost when delegated
        "delegate_effectiveness": 0.9,  # 90% effectiveness when delegated
        "upside": lambda gs: gs._scout_opponents(),
        "downside": lambda gs: None,
        "rules": scout_unlock_rule
    },
    {
        "name": "Hire Manager",
        "desc": "Team leader; required for organizations with 9+ employees.",
        "cost": 90,
        "ap_cost": 1,
        "upside": lambda gs: gs._hire_employee_subtype("manager"),
        "downside": lambda gs: None,
        "rules": manager_unlock_rule
    },
    {
        "name": "Espionage",
        "desc": "Chance to reveal opponent progress, risky.",
        "cost": 30,
        "ap_cost": 1,  # Action Points cost
        "upside": lambda gs: gs._spy(),
        "downside": lambda gs: gs._espionage_risk(),
        "rules": None
    },
    {
        "name": "Scout Opponent",
        "desc": "Focused intel gathering on competitors (unlocked turn 5+).",
        "cost": 50,
        "ap_cost": 1,  # Action Points cost
        "upside": lambda gs: gs._scout_opponent(),
        "downside": lambda gs: gs._espionage_risk(),
        "rules": scout_unlock_rule  # Unlocks after turn 5 (refactored rule)
    },
    {
        "name": "Search",
        "desc": "Board-mandated compliance searches (20% success rate). Unlocks with board members.",
        "cost": 25,
        "ap_cost": 1,  # Action Points cost
        "upside": lambda gs: gs._board_search(),
        "downside": lambda gs: None,
        "rules": search_unlock_rule  # Requires board members (refactored rule)
    },
    {

        "name": "Refresh Researchers",
        "desc": "Get new specialist researcher applications for hiring.",
        "cost": 10,
        "ap_cost": 1,
        "upside": lambda gs: gs.refresh_researcher_hiring_pool(),
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'researchers')  # Only available if researcher system is enabled
    },
    {
        "name": "Team Building",
        "desc": "Reduce researcher burnout and improve team cohesion ($50).",
        "cost": 50,
        "ap_cost": 1,
        "upside": lambda gs: gs.conduct_researcher_management_action("team_building", cost=50),
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'researchers') and len(gs.researchers) > 0
    },
    {
        "name": "Set Research Quality: Rushed",
        "desc": "Fast research: -40% time, -20% cost, +15% doom, +2 debt, -10% success",
        "cost": 0,
        "ap_cost": 0,  # Free action to change approach
        "upside": lambda gs: gs.set_research_quality(ResearchQuality.RUSHED),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.research_quality_unlocked  # Unlocks after first research
    },
    {
        "name": "Set Research Quality: Standard",
        "desc": "Balanced research: baseline time, cost, doom, and success rates",
        "cost": 0,
        "ap_cost": 0,  # Free action to change approach
        "upside": lambda gs: gs.set_research_quality(ResearchQuality.STANDARD),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.research_quality_unlocked  # Unlocks after first research
    },
    {
        "name": "Set Research Quality: Thorough", 
        "desc": "Careful research: +60% time, +40% cost, -20% doom, -1 debt, +15% success",
        "cost": 0,
        "ap_cost": 0,  # Free action to change approach
        "upside": lambda gs: gs.set_research_quality(ResearchQuality.THOROUGH),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.research_quality_unlocked  # Unlocks after first research
    },
    {
        "name": "Refactoring Sprint",
        "desc": "Major code cleanup. Costs $100k + 2 AP, reduces debt by 3-5 points",
        "cost": 100,
        "ap_cost": 2,
        "upside": lambda gs: gs.execute_debt_reduction_action("Refactoring Sprint"),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.technical_debt.accumulated_debt >= 5  # Need significant debt to justify
    },
    {
        "name": "Safety Audit",
        "desc": "Comprehensive safety review. Costs $200k, reduces debt by 2, +reputation",
        "cost": 200,
        "ap_cost": 1,
        "upside": lambda gs: gs.execute_debt_reduction_action("Safety Audit"),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.technical_debt.accumulated_debt >= 3  # Need some debt to audit
    },
    {
        "name": "Code Review",
        "desc": "Peer review process. $50k per researcher, reduces debt by 1 per researcher",
        "cost": 0,  # Dynamic cost based on researchers
        "ap_cost": 1,
        "upside": lambda gs: gs.execute_debt_reduction_action("Code Review"),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.research_staff >= 1 and gs.technical_debt.accumulated_debt >= 1
    },
    # Media & Public Opinion Actions
    {
        "name": "Press Release",
        "desc": "Issue press release to control narrative. Costs $50k, improves public trust.",
        "cost": 50000,
        "ap_cost": 1,
        "upside": lambda gs: gs.media_system.execute_media_action('press_release', gs) if hasattr(gs, 'media_system') else None,
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'media_system')
    },
    {
        "name": "Exclusive Interview",
        "desc": "High-impact interview with major outlet. Costs reputation and time.",
        "cost": 0,
        "ap_cost": 1,
        "upside": lambda gs: gs.media_system.execute_media_action('exclusive_interview', gs) if hasattr(gs, 'media_system') else None,
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'media_system') and gs.reputation >= 10
    },
    {
        "name": "Damage Control",
        "desc": "Reduce negative media coverage impact by 50%. Costs $200k.",
        "cost": 200000,
        "ap_cost": 1,
        "upside": lambda gs: gs.media_system.execute_media_action('damage_control', gs) if hasattr(gs, 'media_system') else None,
        "downside": lambda gs: None,
        "rules": lambda gs: (hasattr(gs, 'media_system') and 
                           any(story.story_type.value == 'scandal' for story in gs.public_opinion.active_stories))
    },
    {
        "name": "Social Media Campaign", 
        "desc": "Targeted social media push to improve public sentiment. Costs $75k.",
        "cost": 75000,
        "ap_cost": 1,
        "upside": lambda gs: gs.media_system.execute_media_action('social_media_campaign', gs) if hasattr(gs, 'media_system') else None,
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'media_system')
    },
    {
        "name": "Public Statement",
        "desc": "Issue statement on current events. Low cost, moderate impact. $10k.",
        "cost": 10000,
        "ap_cost": 1,
        "upside": lambda gs: gs.media_system.execute_media_action('public_statement', gs) if hasattr(gs, 'media_system') else None,
        "downside": lambda gs: None,
        "rules": lambda gs: hasattr(gs, 'media_system')
    },
    # Advanced Economic & Funding Actions for Issue #192
    {
        "name": "Series A Funding",
        "desc": "Pursue institutional venture capital funding (requires proven traction)",
        "cost": 0,
        "ap_cost": 2,  # More complex than basic fundraising
        "upside": lambda gs: execute_series_a_funding(gs),
        "downside": lambda gs: gs._add('reputation', -1 if random.random() < 0.4 else 0),
        "rules": lambda gs: (getattr(gs, 'advanced_funding_unlocked', False) and 
                           gs.reputation >= 15 and 
                           getattr(gs, 'funding_round_cooldown', 0) <= 0)
    },
    {
        "name": "Government Grant Application",
        "desc": "Apply for government AI safety research grants (counter-cyclical funding)",
        "cost": 10,  # Application costs
        "ap_cost": 1,
        "upside": lambda gs: execute_government_grant_application(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: (getattr(gs, 'advanced_funding_unlocked', False) and 
                           gs.reputation >= 8)
    },
    {
        "name": "Corporate Partnership",
        "desc": "Negotiate strategic partnership with established technology company",
        "cost": 0,
        "ap_cost": 2,
        "upside": lambda gs: execute_corporate_partnership(gs),
        "downside": lambda gs: gs._add('reputation', -2 if random.random() < 0.3 else 0),
        "rules": lambda gs: (getattr(gs, 'advanced_funding_unlocked', False) and 
                           gs.reputation >= 12)
    },
    {
        "name": "Revenue Diversification",
        "desc": "Develop customer revenue streams to reduce funding dependence",
        "cost": 50,
        "ap_cost": 2,
        "upside": lambda gs: execute_revenue_diversification(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: (getattr(gs, 'advanced_funding_unlocked', False) and 
                           gs.reputation >= 10 and gs.staff >= 5)
    },
    # Technical Failure Cascade Prevention Actions for Issue #193
    {
        "name": "Incident Response Training",
        "desc": "Upgrade incident response capabilities to prevent failure cascades",
        "cost": lambda gs: (getattr(gs.technical_failures, 'incident_response_level', 0) + 1) * 30 if hasattr(gs, 'technical_failures') else 30,
        "ap_cost": 1,
        "upside": lambda gs: execute_incident_response_upgrade(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: (hasattr(gs, 'technical_failures') and 
                           gs.technical_failures.incident_response_level < 5) or not hasattr(gs, 'technical_failures')
    },
    {
        "name": "Monitoring Systems",
        "desc": "Deploy advanced monitoring for early failure detection",
        "cost": lambda gs: (getattr(gs.technical_failures, 'monitoring_systems', 0) + 1) * 40 if hasattr(gs, 'technical_failures') else 40,
        "ap_cost": 1,
        "upside": lambda gs: execute_monitoring_systems_upgrade(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: (hasattr(gs, 'technical_failures') and 
                           gs.technical_failures.monitoring_systems < 5) or not hasattr(gs, 'technical_failures')
    },
    {
        "name": "Communication Protocols",
        "desc": "Standardize crisis communication and coordination procedures",
        "cost": lambda gs: (getattr(gs.technical_failures, 'communication_protocols', 0) + 1) * 25 if hasattr(gs, 'technical_failures') else 25,
        "ap_cost": 1,
        "upside": lambda gs: execute_communication_protocols_upgrade(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: (hasattr(gs, 'technical_failures') and 
                           gs.technical_failures.communication_protocols < 5) or not hasattr(gs, 'technical_failures')
    },
    {
        "name": "Safety Audit",
        "desc": "Comprehensive audit to identify and fix potential failure points",
        "cost": 60,
        "ap_cost": 2,
        "upside": lambda gs: execute_safety_audit(gs),
        "downside": lambda gs: None,
        "rules": lambda gs: gs.staff >= 3  # Need sufficient staff for meaningful audit
    }
]
import random
from src.core.action_rules import manager_unlock_rule, scout_unlock_rule, search_unlock_rule
from src.core.research_quality import ResearchQuality

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
        "desc": "+Money (scaled by rep), small rep risk.",
        "cost": 0,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Can be delegated to admin staff
        "delegate_staff_req": 1,  # Requires 1 admin staff to delegate  
        "delegate_ap_cost": 1,  # Same AP cost when delegated (requires personal touch)
        "delegate_effectiveness": 0.9,  # 90% effectiveness when delegated
        "upside": lambda gs: gs._add('money', random.randint(40, 70) + gs.reputation * 2),
        "downside": lambda gs: gs._add('reputation', -1 if random.random() < 0.25 else 0),
        "rules": None
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
        "name": "Hire Staff",
        "desc": "Open hiring dialog to select from available employee types.",
        "cost": 0,  # No immediate cost - cost depends on selection
        "ap_cost": 1,
        "upside": lambda gs: gs._trigger_hiring_dialog(),
        "downside": lambda gs: None,
        "rules": None
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
    }
]
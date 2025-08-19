import random
from src.core.action_rules import manager_unlock_rule, scout_unlock_rule, search_unlock_rule

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
        "desc": "Reduce doom, +rep. Costly.",
        "cost": 40,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Phase 3: Can be delegated
        "delegate_staff_req": 2,  # Requires 2 research staff to delegate
        "delegate_ap_cost": 1,  # Same AP cost when delegated (research is complex)
        "delegate_effectiveness": 0.8,  # 80% effectiveness when delegated
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 6) - 
                                    (1 if 'better_computers' in gs.upgrade_effects else 0) -
                                    (2 if 'hpc_cluster' in gs.upgrade_effects else 0) -
                                    (1 if 'research_automation' in gs.upgrade_effects and gs.compute >= 10 else 0)),
                              gs._add('reputation', 2)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Governance Research",
        "desc": "Reduce doom, +reputation. Costly.",
        "cost": 45,
        "ap_cost": 1,  # Action Points cost
        "delegatable": True,  # Phase 3: Can be delegated
        "delegate_staff_req": 2,  # Requires 2 research staff to delegate
        "delegate_ap_cost": 1,  # Same AP cost when delegated
        "delegate_effectiveness": 0.8,  # 80% effectiveness when delegated
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 5) - 
                                    (1 if 'better_computers' in gs.upgrade_effects else 0) -
                                    (2 if 'hpc_cluster' in gs.upgrade_effects else 0) -
                                    (1 if 'research_automation' in gs.upgrade_effects and gs.compute >= 10 else 0)), 
                              gs._add('reputation', 3)),
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
        "name": "Hire Admin Assistant",
        "desc": "Executive assistant; provides +1 staff and +1 admin staff.",
        "cost": 80,
        "ap_cost": 2,
        "upside": lambda gs: gs._hire_employee_subtype("administrator"),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Research Staff",
        "desc": "Research specialist; provides +1 staff, +1 research staff, and research progress.",
        "cost": 70,
        "ap_cost": 2,
        "upside": lambda gs: gs._hire_employee_subtype("researcher"),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Operations Staff",
        "desc": "Technical specialist; provides +1 staff, +1 ops staff, and compute boost.",
        "cost": 70,
        "ap_cost": 2,
        "upside": lambda gs: gs._hire_employee_subtype("engineer"),
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
    }
]
import random
from action_rules import manager_unlock_rule, scout_unlock_rule, search_unlock_rule

ACTIONS = [
    {
        "name": "Grow Community",
        "desc": "+Reputation, possible staff; costs money.",
        "cost": 25,
        "ap_cost": 1,  # Action Points cost
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
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 6) - (1 if 'better_computers' in gs.upgrade_effects else 0)),
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
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 5)), gs._add('reputation', 3)),
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
        "desc": "+Staff, costs money.",
        "cost": 60,
        "ap_cost": 1,  # Action Points cost
        "upside": lambda gs: gs._add('staff', 1),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Admin Assistant",
        "desc": "Hire admin assistant (+1.0 Action Points per turn). Costly but high AP boost.",
        "cost": 80,
        "ap_cost": 2,  # Higher AP cost due to specialized nature
        "upside": lambda gs: (gs._add('admin_staff', 1), gs._add('staff', 1)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Research Staff",
        "desc": "Hire research specialist (enables research action delegation).",
        "cost": 70,
        "ap_cost": 2,  # Higher AP cost due to specialized nature
        "upside": lambda gs: (gs._add('research_staff', 1), gs._add('staff', 1)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Operations Staff",
        "desc": "Hire operations specialist (enables operational action delegation).",
        "cost": 70,
        "ap_cost": 2,  # Higher AP cost due to specialized nature
        "upside": lambda gs: (gs._add('ops_staff', 1), gs._add('staff', 1)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Manager",
        "desc": "Hire manager for large teams (1.5x staff cost). Unlocks at 9+ staff.",
        "cost": 90,  # 1.5x normal staff cost
        "ap_cost": 1,  # Action Points cost
        "upside": lambda gs: gs._hire_manager(),
        "downside": lambda gs: None,
        "rules": manager_unlock_rule  # Unlocks at 9+ staff (refactored rule)
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
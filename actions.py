import random

ACTIONS = [
    {
        "name": "Grow Community",
        "desc": "+Reputation, possible staff; costs money.",
        "cost": 25,
        "upside": lambda gs: (gs._add('reputation', random.randint(2, 5)),
                              gs._add('staff', random.choice([0, 1]))),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Fundraise",
        "desc": "+Money (scaled by rep), small rep risk.",
        "cost": 0,
        "upside": lambda gs: gs._add('money', random.randint(40, 70) + gs.reputation * 2),
        "downside": lambda gs: gs._add('reputation', -1 if random.random() < 0.25 else 0),
        "rules": None
    },
    {
        "name": "Safety Research",
        "desc": "Reduce doom, +rep. Costly.",
        "cost": 40,
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 6) - (1 if 'better_computers' in gs.upgrade_effects else 0)),
                              gs._add('reputation', 2)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Governance Research",
        "desc": "Reduce doom, +reputation. Costly.",
        "cost": 45,
        "upside": lambda gs: (gs._add('doom', -random.randint(2, 5)), gs._add('reputation', 3)),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Buy Compute",
        "desc": "Purchase compute resources. $100 per 10 flops.",
        "cost": 100,
        "upside": lambda gs: gs._add('compute', 10),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Hire Staff",
        "desc": "+Staff, costs money.",
        "cost": 60,
        "upside": lambda gs: gs._add('staff', 1),
        "downside": lambda gs: None,
        "rules": None
    },
    {
        "name": "Espionage",
        "desc": "Chance to reveal opponent progress, risky.",
        "cost": 30,
        "upside": lambda gs: gs._spy(),
        "downside": lambda gs: gs._espionage_risk(),
        "rules": None
    }
]
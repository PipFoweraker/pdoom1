import random

EVENTS = [
    {
        "name": "Lab Breakthrough",
        "desc": "A frontier lab makes a major breakthrough, doom spikes!",
        "trigger": lambda gs: gs.doom > 35 and random.random() < gs.doom / 120,
        "effect": lambda gs: gs._breakthrough_event()
    },
    {
        "name": "Funding Crisis",
        "desc": "Major donor pulls out, lose money.",
        "trigger": lambda gs: gs.money < 80 and random.random() < 0.2,
        "effect": lambda gs: gs._add('money', -random.randint(40, 100))
    },
    {
        "name": "Staff Burnout",
        "desc": "Overworked staff quit.",
        "trigger": lambda gs: gs.staff > 6 and gs.money < gs.staff * gs.staff_maintenance and random.random() < 0.2,
        "effect": lambda gs: gs._add('staff', -random.randint(1, 2))
    }
]
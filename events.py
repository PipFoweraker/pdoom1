import random
def buy_accounting_software(gs):
    """
    Custom event effect function for buying accounting software.
    Deducts $500, sets flag, enables balance change display and monthly costs.
    """
    if gs.money >= 500:
        gs.money -= 500
        gs.accounting_software_bought = True
        gs.messages.append("You bought accounting software! Balance change details enabled, monthly costs always visible.")
    else:
        gs.messages.append("Not enough money to buy accounting software.")
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
    {
        "name": "Buy Accounting Software",
        "desc": "Purchased accounting software for $500. Balance change details now available.",
        # Trigger: After turn 3, and only if not already bought
        "trigger": lambda gs: gs.turn >= 3 and not getattr(gs, "accounting_software_bought", False),
        "effect": buy_accounting_software
    },
]
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

def unlock_scrollable_event_log(gs):
    """
    Custom event effect function for unlocking the scrollable event log.
    Sets the scrollable_event_log_enabled flag and provides user feedback.
    """
    gs.scrollable_event_log_enabled = True
    gs.messages.append("Event Log Upgrade unlocked! You can now scroll through your complete activity history with arrow keys or mouse wheel.")

def unlock_enhanced_events(gs):
    """
    Custom event effect function for unlocking the enhanced event system.
    Enables popup events, deferred events, and advanced event handling.
    """
    gs.enhanced_events_enabled = True
    gs.messages.append("Enhanced Event System unlocked! Your organization can now handle complex events with advanced response options.")

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
    },
    {
        "name": "Event Log System Upgrade",
        "desc": "Your organization upgraded its event tracking system! Full activity history now available.",
        # Trigger: After turn 5, and only if not already unlocked
        "trigger": lambda gs: gs.turn >= 5 and not getattr(gs, "scrollable_event_log_enabled", False),
        "effect": unlock_scrollable_event_log
    },
    {
        "name": "Enhanced Event System Upgrade",
        "desc": "Your organization developed advanced event handling capabilities! Complex crisis management now available.",
        # Trigger: After turn 8, and only if not already unlocked
        "trigger": lambda gs: gs.turn >= 8 and not getattr(gs, "enhanced_events_enabled", False),
        "effect": unlock_enhanced_events
    },
]

import random

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

def trigger_first_manager_hire(gs):
    """
    Special event effect function for triggering the first manager hire.
    This is called when the organization reaches 9 staff for the first time.
    """
    if not gs.manager_milestone_triggered:
        gs.messages.append("SPECIAL EVENT: Your organization has grown to 9 employees!")
        gs.messages.append("Management complexity requires hiring your first Manager.")
        gs.messages.append("The 'Hire Manager' action is now available to organize your growing team.")
        gs.manager_milestone_triggered = True

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
    {
        "name": "First Manager Required",
        "desc": "Your organization has reached 9 employees! Management structure needs to be established.",
        # Trigger: When staff reaches 9 and manager milestone hasn't been triggered yet
        "trigger": lambda gs: gs.staff >= 9 and not gs.manager_milestone_triggered,
        "effect": trigger_first_manager_hire
    },
]

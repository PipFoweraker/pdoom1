import random

def unlock_scrollable_event_log(gs):
    """
    Custom event effect function for unlocking the scrollable event log.
    Sets the scrollable_event_log_enabled flag and provides user feedback.
    """
    gs.scrollable_event_log_enabled = True
    gs.messages.append("Event Log Upgrade unlocked! You can now scroll through your complete activity history with arrow keys or mouse wheel.")
    
    # Show tutorial for scrollable event log
    gs.show_tutorial_message(
        "scrollable_event_log",
        "Scrollable Event Log Unlocked!",
        "Your activity tracking has been upgraded!\n\n"
        "New features:\n\n"
        "? Complete activity history preserved\n"
        "? Scroll with arrow keys or mouse wheel\n"
        "? Review past decisions and their outcomes\n"
        "? Better strategic planning with historical context\n\n"
        "Use this to learn from past events and improve your strategy!"
    )

def unlock_enhanced_events(gs):
    """
    Custom event effect function for unlocking the enhanced event system.
    Enables popup events, deferred events, and advanced event handling.
    """
    gs.enhanced_events_enabled = True
    gs.messages.append("Enhanced Event System unlocked! Your organization can now handle complex events with advanced response options.")
    
    # Show tutorial for enhanced events system
    gs.show_tutorial_message(
        "enhanced_events_system",
        "Enhanced Event System Unlocked!",
        "Your organization has developed advanced event handling capabilities!\n\n"
        "New event types are now available:\n\n"
        "? POPUP Events: Critical situations requiring immediate attention\n"
        "? DEFERRED Events: Events you can postpone for strategic timing\n"
        "? Multiple Response Options: Accept, Reduce, Defer, or Dismiss\n"
        "? Event Queue: Manage multiple concurrent crises\n\n"
        "Use these tools to handle complex challenges strategically!"
    )

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
    {
        "name": "Intelligence Network Established",
        "desc": "Your organization has developed intelligence gathering capabilities! Competitor scouting now available.",
        # Trigger: After turn 6 and reputation >= 10, unlocks Scout Opponents action
        "trigger": lambda gs: gs.turn >= 6 and gs.reputation >= 10 and not getattr(gs, "scouting_unlocked", False),
        "effect": lambda gs: (
            setattr(gs, "scouting_unlocked", True),
            gs.messages.append("Intelligence gathering capabilities unlocked! 'Scout Opponents' action is now available."),
            gs.messages.append("Use this to discover and monitor competing AI laboratories.")
        )
    },
    {
        "name": "Competitor Spotted",
        "desc": "Your contacts report increased activity in the AI capabilities space.",
        # Trigger: Random chance after turn 3, more likely as doom increases
        "trigger": lambda gs: gs.turn >= 3 and random.random() < (0.05 + gs.doom / 1000),
        "effect": lambda gs: gs._trigger_competitor_discovery()
    },
    {
        "name": "Industry Intelligence Update",
        "desc": "Your intelligence network provides updates on competitor activities.",
        # Trigger: Random chance if any opponents are discovered and scouting is unlocked
        "trigger": lambda gs: (getattr(gs, "scouting_unlocked", False) and 
                              any(opp.discovered for opp in gs.opponents) and 
                              random.random() < 0.15),
        "effect": lambda gs: gs._provide_competitor_update()
    },
    {
        "name": "Employee Expense Request",
        "desc": "An employee has submitted an expense request for approval.",
        # Trigger: Regular chance based on staff count, more likely with more staff
        "trigger": lambda gs: gs.staff >= 2 and random.random() < (0.1 + gs.staff * 0.01),
        "effect": lambda gs: gs._trigger_expense_request()
    },
    # Enhanced Personnel System Events
    {
        "name": "Researcher Breakthrough",
        "desc": "One of your researchers makes a significant breakthrough!",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 0 and 
                              random.random() < len(gs.researchers) * 0.03),
        "effect": lambda gs: gs._researcher_breakthrough()
    },
    {
        "name": "Researcher Burnout Crisis",
        "desc": "High burnout levels are affecting your research team.",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 0 and 
                              any(r.burnout > 60 for r in gs.researchers) and random.random() < 0.15),
        "effect": lambda gs: gs._researcher_burnout_crisis()
    },
    {
        "name": "Researcher Poaching Attempt",
        "desc": "A competitor is trying to poach one of your researchers!",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 0 and 
                              gs.turn > 3 and random.random() < len(gs.researchers) * 0.02),
        "effect": lambda gs: gs._researcher_poaching_attempt()
    },
    {
        "name": "Research Ethics Concern",
        "desc": "One of your researchers raises concerns about the ethical implications of your research.",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 0 and 
                              any(r.specialization == 'capabilities' for r in gs.researchers) and
                              gs.doom > 40 and random.random() < 0.1),
        "effect": lambda gs: gs._research_ethics_concern()
    },
    {
        "name": "Researcher Conference Invitation",
        "desc": "One of your researchers has been invited to present at a prestigious conference.",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 0 and 
                              any(r.traits and 'media_savvy' in r.traits for r in gs.researchers) and
                              gs.reputation > 15 and random.random() < 0.08),
        "effect": lambda gs: gs._researcher_conference_invitation()
    },
    {
        "name": "Collaborative Research Opportunity",
        "desc": "An opportunity for collaborative research with another organization has emerged.",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) >= 2 and 
                              gs.reputation > 20 and random.random() < 0.06),
        "effect": lambda gs: gs._collaborative_research_opportunity()
    },
    {
        "name": "Researcher Loyalty Crisis",
        "desc": "Several researchers are showing signs of low loyalty and may leave.",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) > 1 and 
                              sum(1 for r in gs.researchers if r.loyalty < 30) >= 2 and random.random() < 0.12),
        "effect": lambda gs: gs._researcher_loyalty_crisis()
    },
    # Research Quality Events for Issue #190
    {
        "name": "Safety Shortcut Temptation",
        "desc": "A researcher suggests cutting corners on safety validation to speed up progress.",
        "trigger": lambda gs: (gs.research_quality_unlocked and 
                              len(gs.researcher_assignments) > 0 and 
                              random.random() < 0.15),
        "effect": lambda gs: gs._trigger_safety_shortcut_event()
    },
    {
        "name": "Technical Debt Warning",
        "desc": "Your lead researcher warns that accumulated shortcuts are creating risks.",
        "trigger": lambda gs: (gs.technical_debt.accumulated_debt >= 8 and 
                              not gs.technical_debt.has_reputation_risk() and 
                              random.random() < 0.20),
        "effect": lambda gs: gs._trigger_technical_debt_warning()
    },
    {
        "name": "Quality vs Speed Dilemma",
        "desc": "A critical deadline approaches. Do you maintain quality or rush to completion?",
        "trigger": lambda gs: (hasattr(gs, 'researchers') and len(gs.researchers) >= 2 and 
                              gs.turn >= 8 and random.random() < 0.10),
        "effect": lambda gs: gs._trigger_quality_speed_dilemma()
    },
    {
        "name": "Competitor Shortcut Discovery",
        "desc": "Intelligence suggests a competitor is taking dangerous shortcuts in their research.",
        "trigger": lambda gs: (gs.turn >= 10 and 
                              any(hasattr(opp, 'technical_debt') and opp.technical_debt > 5 
                                  for opp in getattr(gs, 'opponents', [])) and 
                              random.random() < 0.12),
        "effect": lambda gs: gs._trigger_competitor_shortcut_discovery()
    },
    # Economic Cycles & Funding Volatility Events for Issue #192
    {
        "name": "Venture Capital Drought",
        "desc": "Rising interest rates have spooked venture capitalists. Funding is much harder to secure.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.economic_cycles.current_state.phase.name in ['RECESSION', 'CORRECTION'] and
                              gs.turn % 15 == 0 and random.random() < 0.3),
        "effect": lambda gs: gs._trigger_funding_drought_event()
    },
    {
        "name": "AI Bubble Burst Warning",
        "desc": "Industry analysts warn that AI valuations are unsustainable. Market correction incoming.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.economic_cycles.current_state.phase.name == 'BOOM' and
                              gs.turn > 50 and random.random() < 0.15),
        "effect": lambda gs: gs._trigger_bubble_warning_event()
    },
    {
        "name": "Government AI Initiative Announced",
        "desc": "Government announces massive AI research funding initiative.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.turn > 20 and gs.reputation >= 8 and 
                              random.random() < 0.08),
        "effect": lambda gs: gs._trigger_government_funding_event()
    },
    {
        "name": "Corporate Partnership Opportunity",
        "desc": "A major corporation is looking for AI partnerships during the economic downturn.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.economic_cycles.current_state.phase.name in ['RECESSION', 'CORRECTION'] and
                              gs.reputation >= 12 and random.random() < 0.12),
        "effect": lambda gs: gs._trigger_corporate_partnership_event()
    },
    {
        "name": "Emergency Cost Cutting Required",
        "desc": "Economic conditions force you to consider emergency cost reduction measures.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.economic_cycles.current_state.phase.name == 'RECESSION' and
                              gs.money < gs.staff * 50 and random.random() < 0.25),
        "effect": lambda gs: gs._trigger_emergency_measures_event()
    },
    {
        "name": "Competitor Funding Announcement",
        "desc": "A major competitor secures massive funding round, increasing competitive pressure.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.economic_cycles.current_state.phase.name == 'BOOM' and
                              any(opp.discovered for opp in getattr(gs, 'opponents', [])) and
                              random.random() < 0.1),
        "effect": lambda gs: gs._trigger_competitor_funding_event()
    },
    {
        "name": "AI Winter Warning",
        "desc": "Industry veterans warn of potential 'AI Winter' if current promises don't materialize.",
        "trigger": lambda gs: (hasattr(gs, 'economic_cycles') and 
                              gs.doom > 60 and gs.turn > 100 and 
                              random.random() < 0.08),
        "effect": lambda gs: gs._trigger_ai_winter_warning_event()
    },
    # Technical Failure Cascade Events for Issue #193
    {
        "name": "Near-Miss Crisis Averted",
        "desc": "Quick thinking prevents a potential technical failure from becoming a crisis.",
        "trigger": lambda gs: (hasattr(gs, 'technical_failures') and 
                              gs.technical_failures.monitoring_systems >= 2 and 
                              random.random() < 0.12),
        "effect": lambda gs: gs._trigger_near_miss_averted_event()
    },
    {
        "name": "Cover-Up Exposed",
        "desc": "Past incident cover-ups come to light, damaging organizational credibility.",
        "trigger": lambda gs: (hasattr(gs, 'technical_failures') and 
                              gs.technical_failures.cover_up_debt >= 8 and 
                              random.random() < gs.technical_failures.cover_up_debt * 0.02),
        "effect": lambda gs: gs._trigger_cover_up_exposed_event()
    },
    {
        "name": "Transparency Dividend",
        "desc": "Your organization's transparent failure handling is recognized as industry best practice.",
        "trigger": lambda gs: (hasattr(gs, 'technical_failures') and 
                              gs.technical_failures.transparency_reputation >= 3.0 and 
                              random.random() < 0.15),
        "effect": lambda gs: gs._trigger_transparency_dividend_event()
    },
    {
        "name": "Cascade Prevention Success",
        "desc": "Advanced incident response capabilities prevent a potential failure cascade.",
        "trigger": lambda gs: (hasattr(gs, 'technical_failures') and 
                              gs.technical_failures.incident_response_level >= 3 and 
                              random.random() < 0.1),
        "effect": lambda gs: gs._trigger_cascade_prevention_event()
    }
]

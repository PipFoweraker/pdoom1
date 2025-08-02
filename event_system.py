"""
Event System - Enhanced event handling with deferred events, pop-ups, and expiration.

This module provides the Event class and related functionality for managing
game events that can be deferred, have expiration times, and support
different UI presentation modes.
"""

from enum import Enum
from typing import Callable, Optional, Dict, Any, List


class EventType(Enum):
    """Event type enumeration for different event behaviors."""
    NORMAL = "normal"       # Standard immediate events
    POPUP = "popup"         # Events that require immediate attention with popup UI
    DEFERRED = "deferred"   # Events that can be deferred for later handling


class EventAction(Enum):
    """Available actions that can be taken on events."""
    ACCEPT = "accept"       # Accept the event (execute its effect)
    DEFER = "defer"         # Defer the event for later
    REDUCE = "reduce"       # Reduce the event's impact
    DISMISS = "dismiss"     # Dismiss the event without effect


class Event:
    """
    Enhanced event class supporting deferred handling, expiration, and different UI modes.
    
    Backward compatible with existing event dictionaries while adding new functionality.
    """
    
    def __init__(self, name: str, desc: str, trigger: Callable, effect: Callable,
                 event_type: EventType = EventType.NORMAL, 
                 max_deferred_turns: int = 3,
                 available_actions: Optional[List[EventAction]] = None,
                 reduce_effect: Optional[Callable] = None):
        """
        Initialize an Event.
        
        Args:
            name: Event name/title
            desc: Event description
            trigger: Function that returns True when event should trigger
            effect: Function to execute when event is accepted
            event_type: Type of event (normal, popup, deferred)
            max_deferred_turns: How many turns the event can be deferred
            available_actions: List of actions available for this event
            reduce_effect: Optional function for reduced impact when event is reduced
        """
        self.name = name
        self.desc = desc
        self.trigger = trigger
        self.effect = effect
        self.event_type = event_type
        self.max_deferred_turns = max_deferred_turns
        self.reduce_effect = reduce_effect
        
        # Set default available actions based on event type
        if available_actions is None:
            if event_type == EventType.POPUP:
                self.available_actions = [EventAction.ACCEPT, EventAction.DEFER, EventAction.DISMISS]
            elif event_type == EventType.DEFERRED:
                self.available_actions = [EventAction.ACCEPT, EventAction.REDUCE, EventAction.DISMISS]
            else:
                self.available_actions = [EventAction.ACCEPT]
        else:
            self.available_actions = available_actions
        
        # State for deferred events
        self.is_deferred = False
        self.turns_deferred = 0
        self.deferred_at_turn = None
    
    @classmethod
    def from_dict(cls, event_dict: Dict[str, Any]) -> 'Event':
        """
        Create an Event from a dictionary (for backward compatibility).
        
        Args:
            event_dict: Dictionary with name, desc, trigger, effect keys
            
        Returns:
            Event instance
        """
        return cls(
            name=event_dict["name"],
            desc=event_dict["desc"], 
            trigger=event_dict["trigger"],
            effect=event_dict["effect"],
            event_type=EventType.NORMAL
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Event back to dictionary format for compatibility."""
        return {
            "name": self.name,
            "desc": self.desc,
            "trigger": self.trigger,
            "effect": self.effect
        }
    
    def can_be_deferred(self) -> bool:
        """Check if this event can be deferred."""
        return EventAction.DEFER in self.available_actions and not self.is_deferred
    
    def can_be_reduced(self) -> bool:
        """Check if this event can have reduced impact."""
        return EventAction.REDUCE in self.available_actions and self.reduce_effect is not None
    
    def defer(self, current_turn: int) -> bool:
        """
        Defer this event.
        
        Args:
            current_turn: Current game turn
            
        Returns:
            True if successfully deferred, False otherwise
        """
        if not self.can_be_deferred():
            return False
        
        self.is_deferred = True
        self.turns_deferred = 0
        self.deferred_at_turn = current_turn
        return True
    
    def tick_deferred(self) -> bool:
        """
        Advance the deferred event by one turn.
        
        Returns:
            True if event has expired and should be auto-executed, False otherwise
        """
        if not self.is_deferred:
            return False
        
        self.turns_deferred += 1
        return self.turns_deferred >= self.max_deferred_turns
    
    def execute_effect(self, game_state, action: EventAction = EventAction.ACCEPT):
        """
        Execute the event effect based on the chosen action.
        
        Args:
            game_state: Game state object
            action: Action chosen by player
        """
        if action == EventAction.ACCEPT:
            self.effect(game_state)
        elif action == EventAction.REDUCE and self.reduce_effect:
            self.reduce_effect(game_state)
        elif action == EventAction.DISMISS:
            # Just add a dismissal message
            game_state.messages.append(f"Dismissed: {self.name}")
        
        # Reset deferred state after execution
        self.is_deferred = False
        self.turns_deferred = 0
        self.deferred_at_turn = None
    
    def get_deferred_display_text(self) -> str:
        """Get display text for deferred events showing turns remaining."""
        if not self.is_deferred:
            return self.name
        
        turns_left = self.max_deferred_turns - self.turns_deferred
        return f"{self.name} ({turns_left} turns left)"


class DeferredEventQueue:
    """Manages a queue of deferred events with expiration logic."""
    
    def __init__(self):
        self.deferred_events: List[Event] = []
    
    def add_deferred_event(self, event: Event) -> bool:
        """
        Add an event to the deferred queue.
        
        Args:
            event: Event to defer (must already be marked as deferred)
            
        Returns:
            True if successfully added, False otherwise
        """
        if not event.is_deferred:
            return False
        
        if event not in self.deferred_events:
            self.deferred_events.append(event)
        return True
    
    def remove_event(self, event: Event):
        """Remove an event from the deferred queue."""
        if event in self.deferred_events:
            self.deferred_events.remove(event)
    
    def tick_all_events(self, game_state) -> List[Event]:
        """
        Advance all deferred events by one turn and auto-execute expired ones.
        
        Args:
            game_state: Game state object
            
        Returns:
            List of events that were auto-executed due to expiration
        """
        expired_events = []
        
        for event in self.deferred_events[:]:  # Create a copy to iterate over
            if event.tick_deferred():
                # Event has expired, execute it automatically
                expired_events.append(event)
                event.execute_effect(game_state, EventAction.ACCEPT)
                self.remove_event(event)
                game_state.messages.append(f"Auto-executed expired event: {event.name}")
        
        return expired_events
    
    def get_deferred_events(self) -> List[Event]:
        """Get all currently deferred events."""
        return self.deferred_events.copy()
    
    def clear(self):
        """Clear all deferred events (for game reset/restart)."""
        self.deferred_events.clear()


# Example enhanced events using the new system
def create_enhanced_events():
    """Create sample enhanced events demonstrating the new system."""
    
    def popup_crisis_effect(gs):
        """Major crisis that requires immediate attention."""
        gs._add('doom', 15)
        gs._add('money', -5000)
        gs.messages.append("Major AI lab incident! Immediate action required!")
    
    def popup_crisis_reduce(gs):
        """Reduced effect for the crisis."""
        gs._add('doom', 8)
        gs._add('money', -2000)
        gs.messages.append("Crisis contained through quick response.")
    
    def funding_opportunity_effect(gs):
        """Funding opportunity that can be deferred."""
        gs._add('money', 10000)
        gs.messages.append("Received major funding grant!")
    
    def funding_opportunity_reduce(gs):
        """Reduced funding if not acted on quickly."""
        gs._add('money', 5000)
        gs.messages.append("Received partial funding due to delayed response.")
    
    enhanced_events = [
        Event(
            name="AI Lab Incident",
            desc="A major incident at a competitor's lab raises safety concerns worldwide!",
            trigger=lambda gs: gs.doom > 50 and gs.turn > 10,
            effect=popup_crisis_effect,
            event_type=EventType.POPUP,
            max_deferred_turns=2,
            available_actions=[EventAction.ACCEPT, EventAction.REDUCE, EventAction.DEFER, EventAction.DISMISS],
            reduce_effect=popup_crisis_reduce
        ),
        Event(
            name="Emergency Funding Opportunity",
            desc="A major donor offers emergency funding for AI safety research.",
            trigger=lambda gs: gs.money < 30000 and gs.turn > 5,
            effect=funding_opportunity_effect,
            event_type=EventType.DEFERRED,
            max_deferred_turns=4,
            reduce_effect=funding_opportunity_reduce
        ),
        Event(
            name="Staff Training Workshop",
            desc="Optional advanced training workshop for staff efficiency.",
            trigger=lambda gs: gs.staff > 4 and gs.turn > 8,
            effect=lambda gs: gs.messages.append("Staff completed advanced training!"),
            event_type=EventType.DEFERRED,
            max_deferred_turns=3
        )
    ]
    
    return enhanced_events
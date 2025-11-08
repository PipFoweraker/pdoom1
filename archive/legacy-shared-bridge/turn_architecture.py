#!/usr/bin/env python3
"""
Ideal Turn Architecture for Godot Implementation

Based on docs/issues/turn-sequencing-architecture.md
Implements proper turn phases to fix pygame's architectural debt.

Turn Flow:
1. TURN_START: Process deferred events, trigger new events
2. ACTION_SELECTION: Player selects actions with full information
3. TURN_PROCESSING: Execute actions, process game state
4. TURN_END: Update UI, prepare for next turn
"""

from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass


class TurnPhase(Enum):
    """Turn phase state machine"""
    TURN_START = "turn_start"          # Events trigger, info presented
    ACTION_SELECTION = "action_selection"  # Player chooses actions
    TURN_PROCESSING = "turn_processing"    # Actions execute
    TURN_END = "turn_end"              # Cleanup, prepare next turn


@dataclass
class TurnState:
    """State tracking for turn progression"""
    phase: TurnPhase = TurnPhase.TURN_START
    pending_events: List[Dict[str, Any]] = None
    selected_actions: List[str] = None
    can_end_turn: bool = False

    def __post_init__(self):
        if self.pending_events is None:
            self.pending_events = []
        if self.selected_actions is None:
            self.selected_actions = []


class TurnManager:
    """
    Manages proper turn sequencing following ideal architecture.

    This fixes pygame's architectural debt where events triggered
    AFTER actions, breaking player agency.
    """

    def __init__(self, game_logic):
        self.logic = game_logic
        self.turn_state = TurnState()

    def start_turn(self) -> Dict[str, Any]:
        """
        Phase 1: TURN_START
        - Process deferred events from previous turn
        - Trigger new events
        - Present all information to player
        """
        self.turn_state.phase = TurnPhase.TURN_START
        self.turn_state.pending_events = []
        self.turn_state.selected_actions = []

        # Check for events FIRST
        events = self.logic.check_events()

        if events:
            # Events block action selection until resolved
            self.turn_state.pending_events = events
            self.turn_state.can_end_turn = False
        else:
            # No events, can proceed to action selection
            self.turn_state.phase = TurnPhase.ACTION_SELECTION
            self.turn_state.can_end_turn = True

        return {
            "success": True,
            "phase": self.turn_state.phase.value,
            "events": events,
            "can_end_turn": self.turn_state.can_end_turn
        }

    def resolve_event(self, event_id: str, choice_id: str) -> Dict[str, Any]:
        """
        Handle event choice during TURN_START phase.
        After resolving all events, transition to ACTION_SELECTION.
        """
        if self.turn_state.phase != TurnPhase.TURN_START:
            return {
                "success": False,
                "error": f"Cannot resolve events in phase {self.turn_state.phase.value}"
            }

        # Handle the event choice
        result = self.logic.handle_event_choice(event_id, choice_id)

        # Remove from pending
        self.turn_state.pending_events = [
            e for e in self.turn_state.pending_events
            if e.get('id') != event_id
        ]

        # If no more pending events, transition to action selection
        if not self.turn_state.pending_events:
            self.turn_state.phase = TurnPhase.ACTION_SELECTION
            self.turn_state.can_end_turn = True

        return {
            "success": result.success,
            "phase": self.turn_state.phase.value,
            "pending_events": len(self.turn_state.pending_events),
            "can_end_turn": self.turn_state.can_end_turn
        }

    def select_action(self, action_id: str) -> Dict[str, Any]:
        """
        Phase 2: ACTION_SELECTION
        Player selects actions (doesn't execute yet).
        """
        if self.turn_state.phase != TurnPhase.ACTION_SELECTION:
            return {
                "success": False,
                "error": f"Cannot select actions in phase {self.turn_state.phase.value}"
            }

        # Add to selected actions (don't execute yet!)
        if action_id not in self.turn_state.selected_actions:
            self.turn_state.selected_actions.append(action_id)

        return {
            "success": True,
            "selected_actions": self.turn_state.selected_actions,
            "can_end_turn": True
        }

    def end_turn(self) -> Dict[str, Any]:
        """
        Phase 3: TURN_PROCESSING
        - Execute all selected actions
        - Process staff maintenance
        - Process opponents
        - Check milestones
        - Increment turn counter

        Phase 4: TURN_END
        - Prepare for next turn cycle
        """
        if not self.turn_state.can_end_turn:
            return {
                "success": False,
                "error": "Cannot end turn - resolve pending events first",
                "phase": self.turn_state.phase.value
            }

        # Transition to processing
        self.turn_state.phase = TurnPhase.TURN_PROCESSING
        self.turn_state.can_end_turn = False

        results = []

        # Execute all selected actions
        for action_id in self.turn_state.selected_actions:
            result = self.logic.execute_action(action_id)
            results.append({
                "action_id": action_id,
                "success": result.success,
                "messages": result.messages
            })

        # Process turn end (maintenance, opponents, etc.)
        turn_result = self.logic.process_turn_end()

        # Transition to turn end
        self.turn_state.phase = TurnPhase.TURN_END

        # Clear selected actions
        self.turn_state.selected_actions = []

        return {
            "success": True,
            "phase": self.turn_state.phase.value,
            "action_results": results,
            "turn_number": self.logic.state.turn,
            "state": self._serialize_state()
        }

    def get_current_phase(self) -> Dict[str, Any]:
        """Get current turn phase information"""
        return {
            "phase": self.turn_state.phase.value,
            "can_end_turn": self.turn_state.can_end_turn,
            "pending_events": len(self.turn_state.pending_events),
            "selected_actions": len(self.turn_state.selected_actions)
        }

    def _serialize_state(self) -> Dict[str, Any]:
        """Serialize game state"""
        state = self.logic.state
        return {
            "turn": state.turn,
            "money": state.money,
            "compute": state.compute,
            "safety": state.safety,
            "capabilities": state.capabilities,
            "game_over": state.game_over,
            "victory": state.victory,
            "employees": {
                "safety": state.employees.get('safety_researchers', 0),
                "capabilities": state.employees.get('capabilities_researchers', 0),
                "compute": state.employees.get('compute_researchers', 0),
                "total": state.get_total_employees()
            },
            "upgrades": state.upgrades
        }

#!/usr/bin/env python3
"""
Bridge server between Godot (GDScript) and Python game logic.

Provides a simple JSON-based IPC interface for Godot to interact with
the shared game logic.

Usage:
    python bridge_server.py [--port 9999]

Communication Protocol:
    - Godot sends JSON commands over stdin or socket
    - Bridge responds with JSON results over stdout or socket
    - All game state is managed by shared/ logic
"""

import sys
import json
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from core.game_logic import GameLogic
from core.engine_interface import MockEngine
from turn_architecture import TurnManager


class GodotBridge:
    """Bridge between Godot and Python game logic"""

    def __init__(self):
        self.engine = MockEngine()
        self.logic = None
        self.turn_manager = None
        self.initialized = False

    def handle_command(self, command: dict) -> dict:
        """Process a command from Godot and return result"""
        action = command.get("action", "")

        try:
            if action == "init_game":
                return self._init_game(command)
            elif action == "start_turn":
                return self._start_turn()
            elif action == "select_action":
                return self._select_action(command)
            elif action == "execute_action":
                return self._execute_action(command)
            elif action == "end_turn":
                return self._end_turn(command)
            elif action == "resolve_event":
                return self._resolve_event(command)
            elif action == "get_actions":
                return self._get_actions()
            elif action == "get_state":
                return self._get_state()
            elif action == "get_phase":
                return self._get_phase()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _init_game(self, command: dict) -> dict:
        """Initialize a new game with proper turn architecture"""
        seed = command.get("seed", "default-seed")
        self.logic = GameLogic(self.engine, seed=seed)
        self.turn_manager = TurnManager(self.logic)
        self.initialized = True

        # Start first turn (triggers initial events if any)
        turn_start = self.turn_manager.start_turn()

        return {
            "success": True,
            "type": "game_initialized",
            "state": self._serialize_state(),
            "turn_phase": turn_start
        }

    def _start_turn(self) -> dict:
        """Start a new turn (Phase 1: events and info)"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        result = self.turn_manager.start_turn()
        return {
            "success": True,
            "type": "turn_start",
            "phase_info": result,
            "state": self._serialize_state()
        }

    def _select_action(self, command: dict) -> dict:
        """Select an action during ACTION_SELECTION phase"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        action_id = command.get("action_id")
        result = self.turn_manager.select_action(action_id)

        return {
            "success": result.get("success", False),
            "type": "action_selected",
            "result": result
        }

    def _resolve_event(self, command: dict) -> dict:
        """Resolve an event choice during TURN_START phase"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        event_id = command.get("event_id")
        choice_id = command.get("choice_id")

        result = self.turn_manager.resolve_event(event_id, choice_id)

        return {
            "success": result.get("success", False),
            "type": "event_resolved",
            "result": result,
            "state": self._serialize_state()
        }

    def _get_phase(self) -> dict:
        """Get current turn phase information"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        phase_info = self.turn_manager.get_current_phase()

        return {
            "success": True,
            "phase_info": phase_info
        }

    def _execute_action(self, command: dict) -> dict:
        """Execute a game action"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        action_id = command.get("action_id")
        # execute_action returns TurnResult which contains messages list
        turn_result = self.logic.execute_action(action_id)

        return {
            "success": turn_result.success,
            "type": "action_result",
            "result": {
                "success": turn_result.success,
                "messages": turn_result.messages
            },
            "state": self._serialize_state()
        }

    def _end_turn(self, command: dict) -> dict:
        """End the current turn (executes selected actions, processes game state)"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        result = self.turn_manager.end_turn()

        return {
            "success": result.get("success", False),
            "type": "turn_end",
            "result": result
        }

    def _get_actions(self) -> dict:
        """Get available actions"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        actions = self.logic.get_available_actions()

        return {
            "success": True,
            "actions": [self._serialize_action(a) for a in actions]
        }

    def _get_state(self) -> dict:
        """Get current game state"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        return {
            "success": True,
            "state": self._serialize_state()
        }

    def _handle_event(self, command: dict) -> dict:
        """Handle event choice"""
        if not self.initialized:
            return {"success": False, "error": "Game not initialized"}

        event_id = command.get("event_id")
        choice_id = command.get("choice_id")

        result = self.logic.handle_event_choice(event_id, choice_id)

        return {
            "success": result.success,
            "type": "event_result",
            "result": {
                "success": result.success,
                "message": result.message
            },
            "state": self._serialize_state()
        }

    def _serialize_state(self) -> dict:
        """Convert game state to JSON-serializable dict"""
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

    def _serialize_action(self, action: dict) -> dict:
        """Convert action to JSON-serializable dict"""
        return {
            "id": action.get("id", ""),
            "name": action.get("name", ""),
            "desc": action.get("desc", ""),
            "cost": action.get("cost", 0),
            "ap_cost": action.get("ap_cost", 1),
            "category": action.get("category", "")
        }

    def _serialize_event(self, event: dict) -> dict:
        """Convert event to JSON-serializable dict"""
        return {
            "id": event.get("id", ""),
            "name": event.get("name", ""),
            "description": event.get("description", ""),
            "options": [
                {
                    "id": opt.id,
                    "text": opt.text
                }
                for opt in event.get("options", [])
            ]
        }


def run_stdio_mode():
    """Run bridge in stdio mode (one command per line)"""
    bridge = GodotBridge()
    print(json.dumps({"ready": True}), flush=True)

    for line in sys.stdin:
        try:
            command = json.loads(line.strip())
            result = bridge.handle_command(command)
            print(json.dumps(result), flush=True)
        except json.JSONDecodeError as e:
            error = {"success": False, "error": f"Invalid JSON: {e}"}
            print(json.dumps(error), flush=True)
        except Exception as e:
            error = {"success": False, "error": f"Unexpected error: {e}"}
            print(json.dumps(error), flush=True)


if __name__ == "__main__":
    run_stdio_mode()

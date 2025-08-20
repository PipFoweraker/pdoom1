"""
P(Doom) - A strategic laboratory management game focused on AI Safety.

This package provides a pygame-based strategy game where players manage
an AI research laboratory while balancing resources, reputation, and the
risk of catastrophic outcomes.

Main modules:
- src.core: Core game logic and state management
- src.ui: User interface components
- src.services: Support services (logging, audio, etc.)
- src.features: Game features and systems
"""

__version__ = "1.0.0"  # Will be managed by version.py eventually

# Package-level imports for convenience
from src.core.game_state import GameState

__all__ = ["GameState"]
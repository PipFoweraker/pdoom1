"""
Game constants and default values extracted from game_state.py

This module contains all the constant values, default settings, and magic numbers
used throughout the game to improve maintainability and reduce code duplication.
"""

# File paths
SCORE_FILE = "local_highscore.json"

# Default game values (matching current config reality)
DEFAULT_STARTING_RESOURCES = {
    'money': 100000,  # Current bootstrap model: $100K realistic nonprofit funding
    'staff': 2, 
    'reputation': 5, 
    'doom': 25, 
    'action_points': 3,  # Updated to match current config
    'compute': 0,  # Updated to match current config  
    'grants': 0,
    'technical_debt': 0
}

# Game balance constants
HIGH_DOOM_WARNING_THRESHOLD = 70
DEFAULT_STAFF_MAINTENANCE = 15

# Reputation thresholds
HIGH_REPUTATION_THRESHOLD = 60
LOW_REPUTATION_THRESHOLD = 30
HIGH_TRUST_VALUE = 60.0
LOW_TRUST_VALUE = 40.0

# Action point system (updated to current config reality)
DEFAULT_ACTION_POINTS = 3  # Current base AP per turn
ACTION_POINT_REFILL_AMOUNT = 3

# Other defaults
DEFAULT_MAX_DOOM = 100
DEFAULT_STARTING_YEAR = 2016

# Research quality constants (if needed)
MIN_RESEARCH_QUALITY = 0.1
MAX_RESEARCH_QUALITY = 1.0

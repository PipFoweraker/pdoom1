'''
P(Doom)1 Leaderboard Module

Provides command-line interface for leaderboard management and web export.

Usage:
    python -m pdoom1.leaderboard export --format web --output ./web_export/
    python -m pdoom1.leaderboard status
    python -m pdoom1.leaderboard list

This module serves as the interface between the game's leaderboard system
and external consumers like the pdoom1-website repository.
'''

__version__ = '1.0.0'
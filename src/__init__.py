'''
PDoom1 - A Python implementation of the classic Doom game.

This package provides modular services for game functionality including
audio management, persistent settings, local scoring, and game clock.
'''

__version__ = '1.0.0'
__author__ = 'PDoom1 Contributors'

# Make core services easily importable with graceful failure handling
__all__ = []

try:
    __all__.append('AudioManager')
except ImportError:
    pass

try:
    __all__.append('GameClock')
except ImportError:
    pass

try:
    __all__.append('Settings')
except ImportError:
    pass

try:
    __all__.append('get_data_dir')
except ImportError:
    pass

try:
    __all__.append('LocalLeaderboard')
except ImportError:
    pass
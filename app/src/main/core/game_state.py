"""
Game state definitions.

Defines the high-level game states used to control screen transitions.
"""

from enum import Enum, auto


class GameState(Enum):
    """
    Enumeration of the high-level game states used to switch between screens.
    """
    START = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    SHOP = auto()
    QUIT = auto()

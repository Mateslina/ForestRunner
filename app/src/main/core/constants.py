"""
Game-wide constants.

Defines screen dimensions, physics values, player parameters, and ground layout
constants used across the game.
"""

# game
WIDTH = 1280
HEIGHT = 720
BASE_SPEED = 300

# ground
GROUND_Y = int(HEIGHT - HEIGHT / 3)
GROUND_HEIGHT = HEIGHT - GROUND_Y
MIN_GROUND_WIDTH = 300
MAX_GROUND_WIDTH = 1400
MIN_GAP_WIDTH = 100
MAX_GAP_WIDTH = 250

# physics
GRAVITY = 2000.0
JUMP_VELOCITY = -900.0

# player
PLAYER_WIDTH = 80
PLAYER_HEIGHT = 120
PLAYER_X = 100

"""
Asset models.

Contains small, frozen dataclasses used to group loaded sprites.
"""

from dataclasses import dataclass
from typing import Dict, List

import pygame as pg


@dataclass(frozen=True)
class ObstacleSprites:
    """Sprites used by obstacles (colliding gameplay entities)."""

    rock_tiles: List[pg.Surface]
    bird_frames: List[pg.Surface]


@dataclass(frozen=True)
class CoinSprites:
    """Sprites for coin variants."""

    normal: pg.Surface
    double: pg.Surface


@dataclass(frozen=True)
class PowerupSprites:
    """Sprites for all power-up items (including extra life)."""

    all: Dict[str, pg.Surface]


@dataclass(frozen=True)
class CollectibleSprites:
    """Sprites for all collectible items (coins and power-ups)."""

    coins: CoinSprites
    powerups: PowerupSprites


@dataclass(frozen=True)
class PlayerSprites:
    """Player animation frames and size metadata."""

    run_frames: List[pg.Surface]
    crouch_frames: List[pg.Surface]
    stand_size: tuple[int, int]
    crouch_size: tuple[int, int]


@dataclass(frozen=True)
class UIAssets:
    """UI-related background and decorative sprites."""

    shop_background: pg.Surface
    title_sign: pg.Surface

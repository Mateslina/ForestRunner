"""
Coin entity.

Defines a collectible coin that scrolls left with the world speed and can be
rendered and collided with via its rect.
"""

import pygame as pg


class Coin:
    """A collectible that scrolls left with the world speed."""

    def __init__(self, x: float, y: float, sprite: pg.Surface):
        """Create a coin at world coordinates (x, y) using the given sprite."""
        self.x = float(x)
        self.y = float(y)

        self.sprite = sprite

        w, h = sprite.get_size()
        self.rect = pg.Rect(round(self.x), round(self.y), w, h)

    def update(self, dt: float, speed: float) -> None:
        """Move coin position left based on world speed."""
        self.x -= speed * dt
        self.rect.x = round(self.x)

    def draw(self, surface: pg.Surface) -> None:
        """Draw the coin sprite."""
        surface.blit(self.sprite, self.rect.topleft)

"""
Power-up entity.

Defines a collectible power-up that moves with the world, can be collected by
the player, and uses a sprite + rect for rendering and collision.
"""

import pygame as pg


class PowerUp:
    """
    Collectible power-up.

    Holds position, kind, sprite, and collision rect. Moves left with the world
    speed and can be drawn to a surface.
    """

    def __init__(self, x: float, y: float, kind: str, sprite: pg.Surface):
        """Create a power-up at (x, y) with a kind label and sprite."""
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.sprite = sprite

        w = self.sprite.get_width()
        h = self.sprite.get_height()
        self.rect = pg.Rect(round(self.x), round(self.y), w, h)

    def update(self, dt: float, speed: float) -> None:
        """Move the power-up left according to world speed."""
        self.x -= speed * dt
        self.rect.x = round(self.x)

    def draw(self, surface: pg.Surface) -> None:
        """Draw the power-up sprite."""
        surface.blit(self.sprite, self.rect.topleft)

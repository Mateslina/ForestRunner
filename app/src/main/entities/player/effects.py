"""
Visual effects helpers for the player.
- Shield glow drawing
- Invulnerability blinking (sprite visibility toggle)
"""

import pygame as pg


def draw_shield_glow(screen: pg.Surface, rect: pg.Rect, offset: int) -> None:
    """Draw a simple glowing shield ring centered on `rect`."""
    radius = int(max(rect.width, rect.height) * 0.75)
    diameter = radius * 2

    cx = int(rect.centerx)
    cy = int(rect.centery + offset)

    glow = pg.Surface((diameter, diameter), pg.SRCALPHA)  # pylint: disable=no-member
    pg.draw.circle(glow, (120, 220, 255, 110), (radius, radius), radius)
    pg.draw.circle(glow, (180, 245, 255, 140), (radius, radius), int(radius * 0.75))
    pg.draw.circle(glow, (60, 200, 255, 255), (radius, radius), radius, width=3)

    screen.blit(glow, (cx - radius, cy - radius))


def sprite_visible_during_invuln(invulnerable: bool, blink_ms: int = 100) -> bool:
    """
    Return True if the sprite should be drawn this frame.

    When invulnerable, toggles visibility every `blink_ms` milliseconds.
    """
    if not invulnerable:
        return True
    return (pg.time.get_ticks() // blink_ms) % 2 == 1

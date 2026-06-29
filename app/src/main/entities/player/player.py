"""
Player entity.

Implements player physics, animation and rendering, including crouching,
jumping, shield and invulnerability.
"""

from dataclasses import dataclass
from typing import Any

import pygame as pg

from main.entities.player.effects import draw_shield_glow, sprite_visible_during_invuln
from main.entities.player.player_controller import PlayerController
from main.core.constants import PLAYER_X, GROUND_Y, JUMP_VELOCITY


@dataclass
class PlayerSprites:
    """Holds player animation frames."""
    run_frames: list[pg.Surface]
    crouch_frames: list[pg.Surface]


@dataclass
class PlayerAnim:
    """Animation indices and timer."""
    run_i: int = 0
    crouch_i: int = 0
    t: float = 0.0


@dataclass
class PlayerBuffs:
    """Shield and invulnerability state."""
    shield_active: bool = False
    shield_time: float = 0.0
    invuln_time: float = 0.0


@dataclass
class PlayerMotion:
    """Movement/pose state."""
    velocity: float = 0.0
    on_ground: bool = True
    crouching: bool = False


@dataclass
class PlayerGeom:
    """Geometry, sizes and collision rect."""
    y: float
    stand_w: int
    stand_h: int
    crouch_w: int
    crouch_h: int
    rect: pg.Rect


class Player:
    """Player entity class. Implements player movement and drawing on screen."""

    def __init__(self, assets: Any) -> None:
        """Create a player from loaded assets and reset to default state."""
        sprites = PlayerSprites(
            run_frames=assets.player.run_frames,
            crouch_frames=assets.player.crouch_frames,
        )
        self.controller = PlayerController()
        self.sprites = sprites
        self.anim = PlayerAnim()
        self.buffs = PlayerBuffs()
        self.motion = PlayerMotion()

        # player dimensions
        stand_w, stand_h = sprites.run_frames[0].get_size()
        crouch_w, crouch_h = sprites.crouch_frames[0].get_size()

        y = float(GROUND_Y - stand_h)

        rect = pg.Rect(PLAYER_X, round(y), stand_w, stand_h)
        self.geom = PlayerGeom(
            y=y,
            stand_w=stand_w,
            stand_h=stand_h,
            crouch_w=crouch_w,
            crouch_h=crouch_h,
            rect=rect,
        )

    @property
    def rect(self) -> pg.Rect:
        """Player collision rectangle."""
        return self.geom.rect

    @property
    def on_ground(self) -> bool:
        """Whether the player is currently standing on solid ground."""
        return self.motion.on_ground

    @property
    def shield_active(self) -> bool:
        """Whether the player currently has an active shield."""
        return self.buffs.shield_active

    @property
    def invulnerable(self) -> bool:
        """Whether the player is currently invulnerable."""
        return self.buffs.invuln_time > 0.0

    # ---------------- input/state ----------------

    def jump(self) -> None:
        """Start a jump if the player is on the ground."""
        if self.motion.on_ground:
            self.motion.velocity = JUMP_VELOCITY
            self.motion.on_ground = False

    def set_crouch(self, active: bool) -> None:
        """Enable/disable crouching (only allowed on the ground)."""
        if active and not self.motion.on_ground:
            return
        self.motion.crouching = bool(active)
        self.sync_rect()

    def give_shield(self, duration: float) -> None:
        """Activate a shield for the given duration (seconds)."""
        self.buffs.shield_active = True
        self.buffs.shield_time = float(duration)

    def consume_shield(self) -> None:
        """Consume the currently active shield."""
        self.buffs.shield_active = False
        self.buffs.shield_time = 0.0

    def set_invulnerable(self, duration: float) -> None:
        """Make the player invulnerable for `duration` seconds."""
        self.buffs.invuln_time = float(duration)

    def respawn(self) -> None:
        """Reset the player to a safe standing state."""
        self.motion.velocity = 0.0
        self.motion.crouching = False
        self.motion.on_ground = True
        self.geom.y = float(GROUND_Y - self.geom.stand_h)
        self.sync_rect()

    # ---------------- update ----------------

    def update(self, dt: float, ground: Any, speed: float) -> None:
        """Update physics, timers, animation and collision state."""
        self.controller.update(self, dt, ground, speed)

    # ---------------- rect/sprite ----------------

    def sync_rect(self) -> None:
        """Update collision rect to match current pose and position."""
        r = self.geom.rect
        r.x = PLAYER_X

        if self.motion.crouching:
            r.size = (self.geom.crouch_w, self.geom.crouch_h)
            r.y = round(self.geom.y + (self.geom.stand_h - self.geom.crouch_h))
        else:
            r.size = (self.geom.stand_w, self.geom.stand_h)
            r.y = round(self.geom.y)

    def _current_sprite(self) -> pg.Surface:
        """Return the sprite surface that should be drawn this frame."""
        if not self.motion.on_ground:
            return self.sprites.run_frames[0]
        if self.motion.crouching:
            return self.sprites.crouch_frames[self.anim.crouch_i]
        return self.sprites.run_frames[self.anim.run_i]

    # ---------------- draw ----------------

    def draw(self, screen: pg.Surface) -> None:
        """Draw the player sprite and optional shield effects."""
        sprite = self._current_sprite()
        offset = 15 if not self.motion.crouching else 4

        if self.buffs.shield_active:
            draw_shield_glow(screen, self.geom.rect, offset)

        if not sprite_visible_during_invuln(self.invulnerable, blink_ms=100):
            return

        screen.blit(sprite, (self.geom.rect.x, self.geom.rect.y + offset))

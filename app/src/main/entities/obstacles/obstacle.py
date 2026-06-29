"""
Obstacles system.

Defines obstacle entities (ground + flying).
"""

from dataclasses import dataclass
from typing import Optional, List

import pygame as pg

from main.core.constants import GROUND_Y, PLAYER_HEIGHT


@dataclass
class ObstacleState:
    """Mutable runtime state for an obstacle."""
    x: float
    speed: float
    flying: bool


@dataclass
class ObstacleAnim:
    """Animation state for a framed sprite."""
    fps: float = 8.0
    time_acc: float = 0.0
    frame_index: int = 0


@dataclass
class ObstacleBody:
    """Geometry for obstacle rendering and collisions."""
    rect: pg.Rect
    hitbox: pg.Rect
    width: int
    height: int


@dataclass
class ObstacleSprites:
    """Either a static sprite or animated frames."""
    sprite: Optional[pg.Surface] = None
    frames: Optional[List[pg.Surface]] = None


class Obstacle:
    """Single obstacle instance (ground or flying)."""

    HITBOX_SHRINK_X = 0.3
    HITBOX_SHRINK_Y = 0.6
    FLYING_SPEED_MULT = 1.25

    def __init__(
        self,
        *,
        x: float,
        flying: bool,
        speed: float = 0.0,
        sprites: ObstacleSprites,
    ) -> None:
        self.state = ObstacleState(x=float(x), speed=float(speed), flying=bool(flying))
        self.sprites = sprites
        self.anim = ObstacleAnim()
        self.body = self._build_body()

    def _sprite_size(self) -> tuple[int, int]:
        """Return (w, h) derived from frames or sprite."""
        surf = self.sprites.frames[0] if self.sprites.frames else self.sprites.sprite
        return surf.get_width(), surf.get_height()

    def _build_body(self) -> ObstacleBody:
        """Create rect + hitbox based on sprite size and flight mode."""
        width, height = self._sprite_size()

        if self.state.flying:
            bottom = GROUND_Y - PLAYER_HEIGHT * 0.75
            y = float(bottom - height)  # 0.75 of player hegiht above ground
        else:
            y = float(GROUND_Y - height)  # on the ground

        rect = pg.Rect(round(self.state.x), round(y), width, height)

        # make hitboxes less punishing
        shrink_x = int(width * self.HITBOX_SHRINK_X)
        shrink_y = int(height * self.HITBOX_SHRINK_Y)

        hit = rect.inflate(-shrink_x, -shrink_y)
        hit.bottom = rect.bottom

        return ObstacleBody(rect=rect, hitbox=hit, width=width, height=height)

    def update(self, dt: float, *, speed: float) -> None:
        """Advance position and animation."""
        base_speed = float(speed)
        mult = self.FLYING_SPEED_MULT if self.state.flying else 1.0
        self.state.speed = base_speed * mult

        self.state.x -= self.state.speed * dt
        self.body.rect.x = round(self.state.x)

        self.body.hitbox.centerx = self.body.rect.centerx
        self.body.hitbox.bottom = self.body.rect.bottom

        if self.sprites.frames:
            self._advance_anim(dt)

    # @generated [all] ChatGPT: how to change animation frames smoothly
    def _advance_anim(self, dt: float) -> None:
        """Advance animation timer and frame index."""
        frames = self.sprites.frames or ()
        if not frames:
            return

        # update accumulated time since last frame change
        self.anim.time_acc += dt
        step = 1.0 / float(self.anim.fps)

        while self.anim.time_acc >= step:
            self.anim.time_acc -= step
            self.anim.frame_index = (self.anim.frame_index + 1) % len(frames)

    def draw(self, surface: pg.Surface) -> None:
        """Draw obstacle."""
        if self.sprites.frames:
            surface.blit(self.sprites.frames[self.anim.frame_index], self.body.rect.topleft)
            return
        surface.blit(self.sprites.sprite, self.body.rect.topleft)

    @property
    def hitbox(self) -> pg.Rect:
        """Collision hitbox."""
        return self.body.hitbox

    @property
    def rect(self) -> pg.Rect:
        """Visual rect."""
        return self.body.rect

    @property
    def is_off_screen(self) -> bool:
        """True if obstacle is completely left of screen."""
        return self.state.x + float(self.body.width) < 0.0

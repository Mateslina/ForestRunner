"""
Obstacle manager system.

Spawns, updates, draws obstacles and performs collision queries.
"""

from dataclasses import dataclass
import random
from typing import Optional, List

import pygame as pg

from main.core.constants import PLAYER_X

from main.entities.obstacles.obstacle import Obstacle, ObstacleSprites
from main.entities.ground import Ground


@dataclass(frozen=True)
class SpawnDecision:
    """Computed spawn decision."""

    flying: bool
    x: float
    sprites: ObstacleSprites


@dataclass
class SpriteConfig:
    """Sprites used by obstacles."""

    ground_sprites: List[pg.Surface]
    bird_frames: List[pg.Surface]


class ObstacleManager:
    """Spawns and manages all obstacles."""

    BIRD_SPAWN_X_OFFSET = 75.0
    MIN_REACTION_TIME = 0.35

    def __init__(
        self,
        assets,
        *,
        rand: random.Random | None = None,
    ) -> None:
        self.rand = rand or random.Random()
        self.obstacles: list[Obstacle] = []
        self.sprites = SpriteConfig(
            ground_sprites=assets.obstacles.rock_tiles,
            bird_frames=assets.obstacles.bird_frames,
        )

    def spawn_obstacle_at(
        self,
        x: float,
        ground: Ground,
        flying: bool = False,
    ) -> None:
        """
        Spawn an obstacle at x positions.
        Different rules apply for different obstacles.
        """
        # find where and what obstacle to spawn
        decision = self._decide_spawn(
            x=float(x),
            flying=bool(flying),
            ground=ground,
        )
        # create it
        self.obstacles.append(
            Obstacle(
                x=decision.x,
                flying=decision.flying,
                sprites=decision.sprites,
            )
        )

    def _decide_spawn(
        self,
        x: float,
        flying: bool,
        ground: Ground,
    ) -> SpawnDecision:
        """
        Decide whether to spawn flying vs ground, and prepare sprites.
        First tries to spawn bird obstacle, then fallsback to ground.
        """
        if flying:
            decision = self._try_make_flying_spawn(x, ground)
            if decision is not None:
                return decision
        return self._make_ground_spawn(x)

    def _try_make_flying_spawn(
        self,
        x: float,
        ground: Ground,
    ) -> Optional[SpawnDecision]:
        """Return a valid flying spawn decision, or None if not possible."""
        frames = self.sprites.bird_frames
        spawn_x = float(x) + float(self.BIRD_SPAWN_X_OFFSET)

        ok = self._flying_has_safe_ground(spawn_x, ground, frames)
        if not ok:
            return None

        return SpawnDecision(
            flying=True,
            x=spawn_x,
            sprites=ObstacleSprites(frames=frames, sprite=None),
        )

    # @generated [all] ChatGPT : i need to spawn the bird obstacle with offset such when its x reaches the player, the player has solid ground around them
    def _flying_has_safe_ground(
        self,
        spawn_x: float,
        ground: Ground,
        frames: List[pg.Surface],
    ) -> bool:
        """Validate that bird will be above solid ground when reaching the player."""
        v_ground = ground.speed
        v_bird = v_ground * Obstacle.FLYING_SPEED_MULT

        t = (float(spawn_x) - float(PLAYER_X)) / max(1e-6, v_bird)
        if t <= 0.0:
            return False

        t = max(t, float(self.MIN_REACTION_TIME))
        x_future = float(PLAYER_X) + v_ground * t

        bird_w = frames[0].get_width()
        span = max(180.0, float(bird_w) * 2.5)

        return ground.is_solid_at_x(
            x_future - span * 0.5,
            x_future + span * 0.5,
            min_overlap=span * 0.8,
        )

    def _make_ground_spawn(self, x: float) -> SpawnDecision:
        """Create a ground obstacle spawn decision."""
        sprite = self.rand.choice(self.sprites.ground_sprites)
        return SpawnDecision(
            flying=False,
            x=float(x),
            sprites=ObstacleSprites(sprite=sprite, frames=None),
        )

    def update(self, dt: float, current_speed: float) -> None:
        """Update all obstacles and remove off-screen ones."""
        speed = float(current_speed)
        for obstacle in self.obstacles:
            obstacle.update(dt, speed=speed)
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen]

    def draw(self, surface: pg.Surface) -> None:
        """Draw all obstacles."""
        for obstacle in self.obstacles:
            obstacle.draw(surface)

    def get_first_collision(self, rect: pg.Rect) -> Optional[Obstacle]:
        """Return the first obstacle colliding with `rect` (by hitbox)."""
        for obstacle in self.obstacles:
            if obstacle.hitbox.colliderect(rect):
                return obstacle
        return None

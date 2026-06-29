"""
Collectible spawner.

Selects valid (x, y) spawn points for collectibles ahead of the player.
Uses multiple strategies (under flying obstacle, above ground obstacle,
above gaps, or on solid ground) while keeping distance from other obstacles.
"""

from dataclasses import dataclass
import random
from typing import Optional

import pygame as pg

from main.core.constants import GROUND_Y, PLAYER_HEIGHT, WIDTH


@dataclass(frozen=True)
class SpawnPoint:
    """World-space spawn point for a collectible."""

    x: float
    y: float


@dataclass(frozen=True)
class SpawnWindow:
    """Spawn x-window bounds."""

    min_x: float
    max_x: float


@dataclass(frozen=True)
class ItemSize:
    """Collectible size in pixels."""

    w: float
    h: float


@dataclass(frozen=True)
class StrategyContext:
    """Common context passed to spawn strategies."""

    item: ItemSize
    window: SpawnWindow
    ground: object
    obstacles: object
    window_obstacles: list[object]
    segments: list[tuple[float, float]]


class CollectibleSpawner:  # pylint: disable=too-few-public-methods
    """
    Selects valid (x, y) spawn points for collectibles ahead of the player.

    Prefers placements relative to obstacles and gaps, falls back to solid ground,
    and avoids spawning too close to obstacles.
    """

    SPAWN_MAX_X_FACTOR = 1.7
    OBSTACLE_PADDING_X = 40
    OBSTACLE_PADDING_Y = 25

    def __init__(self, rand: random.Random | None = None) -> None:
        self.rand = rand or random.Random()

    def pick_spawn_point(
        self,
        item_w: float,
        item_h: float,
        ground: object,
        obstacles: object,
    ) -> Optional[SpawnPoint]:
        """Return a spawn point that matches the collectible placement rules."""
        window = self._spawn_window()
        segments = self._sorted_segments(ground)
        if not segments:
            return None

        window_obstacles = self._obstacles_in_window(
            obstacles, window.min_x, window.max_x
        )

        ctx = StrategyContext(
            item=ItemSize(w=float(item_w), h=float(item_h)),
            window=window,
            ground=ground,
            obstacles=obstacles,
            window_obstacles=window_obstacles,
            segments=segments,
        )

        return (
            self._spawn_under_flying(ctx) or
            self._spawn_above_ground_obstacle(ctx) or
            self._spawn_above_gap(ctx) or
            self._spawn_on_solid_ground(ctx)
        )

    # ---------------- shared helpers ----------------

    def _spawn_window(self) -> SpawnWindow:
        """Spawn x window: [screen_width, screen_width * factor]."""
        left = float(WIDTH)
        right = float(WIDTH) * float(self.SPAWN_MAX_X_FACTOR)
        return SpawnWindow(min_x=left, max_x=right)

    @staticmethod
    def _sorted_segments(ground: object) -> list[tuple[float, float]]:
        """Return sorted (start_x, end_x) ground segments."""
        segs = [(float(x), float(x + w)) for (x, w) in ground.get_segments()]
        segs.sort(key=lambda t: t[0])
        return segs

    @staticmethod
    # @generated [all] ChatGPT : how to effectively get the gaps between ground segments
    def _gaps_in_window(
        segs: list[tuple[float, float]],
        min_x: float,
        max_x: float,
    ) -> list[tuple[float, float]]:
        """Compute gaps between segments within [min_x, max_x]."""
        if len(segs) < 2:
            return []

        gaps: list[tuple[float, float]] = []
        for (_, a2), (b1, _) in zip(segs, segs[1:]):
            gap_start = a2
            gap_end = b1
            if gap_end <= gap_start:
                continue

            left = max(gap_start, min_x)
            right = min(gap_end, max_x)
            if right > left:
                gaps.append((left, right))
        return gaps

    @staticmethod
    def _obstacles_in_window(
        obstacles: object, min_x: float, max_x: float
    ) -> list[object]:
        """Return obstacles whose rects overlap [min_x, max_x]."""
        res: list[object] = []
        for obs in obstacles:
            ox1 = float(obs.rect.left)
            ox2 = float(obs.rect.right)
            if ox2 < min_x or ox1 > max_x:
                continue
            res.append(obs)
        return res

    def _too_close_to_obstacle_rect(self, rect: pg.Rect, obstacles: object) -> bool:
        """Check if `rect` collides with any obstacle padded rect."""
        for obs in obstacles:
            padded = obs.rect.inflate(
                self.OBSTACLE_PADDING_X * 2,
                self.OBSTACLE_PADDING_Y * 2,
            )
            if rect.colliderect(padded):
                return True
        return False

    # ---------------- spawn strategies ----------------
    # @generated [partially] ChatGPT : how to center rect below another
    def _spawn_under_flying(self, ctx: StrategyContext) -> Optional[SpawnPoint]:
        """Spawn on ground under a flying obstacle, centered on it."""
        flying = [o for o in ctx.window_obstacles if o.state.flying]
        flying.sort(key=lambda o: o.rect.x)

        for obs in flying:
            x = float(obs.rect.centerx) - ctx.item.w * 0.5
            y = float(GROUND_Y - ctx.item.h)
            rect = pg.Rect(round(x), round(y), round(ctx.item.w), round(ctx.item.h))

            if self._too_close_to_obstacle_rect(rect, ctx.obstacles):
                continue
            if not ctx.ground.is_solid_at_x(
                x, x + ctx.item.w, min_overlap=ctx.item.w * 0.5
            ):
                continue
            return SpawnPoint(x=x, y=y)

        return None

    def _spawn_above_ground_obstacle(
        self, ctx: StrategyContext
    ) -> Optional[SpawnPoint]:
        """Spawn above a ground obstacle (reward jump)."""
        ground_obs = [o for o in ctx.window_obstacles if not o.state.flying]
        ground_obs.sort(key=lambda o: o.rect.x)

        for obs in ground_obs:
            x = float(obs.rect.centerx) - ctx.item.w * 0.5
            y = float(obs.rect.top) - ctx.item.h - 60.0
            rect = pg.Rect(round(x), round(y), round(ctx.item.w), round(ctx.item.h))

            if self._too_close_to_obstacle_rect(rect, ctx.obstacles):
                continue
            return SpawnPoint(x=x, y=y)

        return None

    def _spawn_above_gap(self, ctx: StrategyContext) -> Optional[SpawnPoint]:
        """Spawn above a gap to encourage risky pathing."""
        gaps = self._gaps_in_window(ctx.segments, ctx.window.min_x, ctx.window.max_x)
        gaps.sort(key=lambda g: g[0])

        for gl, gr in gaps:
            center = (gl + gr) * 0.5
            x = center - ctx.item.w * 0.5
            y = float(GROUND_Y - PLAYER_HEIGHT - 120)
            rect = pg.Rect(round(x), round(y), round(ctx.item.w), round(ctx.item.h))

            if self._too_close_to_obstacle_rect(rect, ctx.obstacles):
                continue
            return SpawnPoint(x=x, y=y)

        return None

    def _spawn_on_solid_ground(self, ctx: StrategyContext) -> Optional[SpawnPoint]:
        """Fallback: spawn on solid ground at a random x in the window."""
        for _ in range(8):
            x = self.rand.uniform(ctx.window.min_x, ctx.window.max_x)
            y = float(GROUND_Y - ctx.item.h)
            rect = pg.Rect(round(x), round(y), round(ctx.item.w), round(ctx.item.h))

            if self._too_close_to_obstacle_rect(rect, ctx.obstacles):
                continue
            if not ctx.ground.is_solid_at_x(
                x,
                x + ctx.item.w,
                min_overlap=ctx.item.w * 0.5,
            ):
                continue

            return SpawnPoint(x=x, y=y)

        return None

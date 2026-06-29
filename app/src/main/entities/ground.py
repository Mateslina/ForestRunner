"""
Ground system.

Maintains a scrolling set of ground segments with randomly generated platforms
and gaps. Also emits obstacle spawn requests based on configured chance.
"""

from dataclasses import dataclass
import math
import random
from typing import Optional

import pygame as pg

from main.core.assets.assets import GroundTiles
from main.core.constants import (
    GROUND_Y,
    WIDTH,
    GROUND_HEIGHT,
    MAX_GROUND_WIDTH,
    MIN_GROUND_WIDTH,
    MIN_GAP_WIDTH,
    MAX_GAP_WIDTH,
)


@dataclass(frozen=True)
class ObstacleSpawnRequest:
    """Request describing where and what type of obstacle to spawn."""
    x: float
    flying: bool


@dataclass
class GroundState:
    """Mutable ground state."""
    speed: float
    spawn_x_pos: float
    obstacle_chance: float
    segments: list[tuple[float, pg.Surface]]


class Ground:
    """Scrolling ground made from pre-rendered segments."""

    DEFAULT_OBSTACLE_CHANCE = 0.4
    FLYING_OBSTACLE_CHANCE = 0.5

    def __init__(self, speed: float, tiles: GroundTiles) -> None:
        self.rand = random.Random()

        self.tiles = tiles
        self.tile_w = self.tiles.top_mid.get_width()
        self.tile_h = self.tiles.top_mid.get_height()

        self.state = GroundState(
            speed=float(speed),
            spawn_x_pos=float(WIDTH),
            obstacle_chance=self.DEFAULT_OBSTACLE_CHANCE,
            segments=[],
        )
        self._init_first_segment()

    # ---------- public API ----------

    @property
    def speed(self) -> float:
        """Current world speed."""
        return float(self.state.speed)

    @speed.setter
    def speed(self, value: float) -> None:
        self.state.speed = float(value)

    @property
    def obstacle_chance(self) -> float:
        """Chance per spawn to create an obstacle request."""
        return float(self.state.obstacle_chance)

    @obstacle_chance.setter
    def obstacle_chance(self, value: float) -> None:
        self.state.obstacle_chance = float(value)

    def reset(self, speed: float) -> None:
        """Reset ground to the initial state (new run)."""
        self.state.speed = float(speed)
        self.state.spawn_x_pos = float(WIDTH)
        self.state.obstacle_chance = self.DEFAULT_OBSTACLE_CHANCE
        self.state.segments.clear()
        self._init_first_segment()

    def get_segments(self) -> list[tuple[float, int]]:
        """Return list of (segment_start_x, segment_width_px)."""
        return [(x, surf.get_width()) for (x, surf) in self.state.segments]

    def update(self, dt: float) -> list[ObstacleSpawnRequest]:
        """Scroll ground, cull offscreen segments, and generate new ones."""
        dx = self.state.speed * dt
        self.state.spawn_x_pos -= dx

        self.state.segments = [(x - dx, surf) for (x, surf) in self.state.segments]
        self.state.segments = [
            (x, surf)
            for (x, surf) in self.state.segments
            if x + surf.get_width() > 0
        ]

        # spawmn more segments from the last one upto needed width
        rightmost = max(
            (x + surf.get_width() for (x, surf) in self.state.segments),
            default=0.0,
        )
        width_needed = max(self.state.spawn_x_pos, rightmost + WIDTH)
        return self._ground_buffer(width_needed)

    def draw(self, screen: pg.Surface) -> None:
        """Draw all segments at ground level."""
        for seg_x, surf in self.state.segments:
            screen.blit(surf, (round(seg_x), GROUND_Y))

    def is_solid_at_x(self, x1: float, x2: float, min_overlap: float = 1.0) -> bool:
        """Return True if [x1, x2] overlaps any ground segment by `min_overlap`."""
        for seg_x, surf in self.state.segments:
            w = surf.get_width()
            overlap = min(x2, seg_x + w) - max(x1, seg_x)
            if overlap >= min_overlap:
                return True
        return False

    # ---------- initialization ----------

    def _init_first_segment(self) -> None:
        tiles = math.ceil(WIDTH / self.tile_w)
        initial_width = tiles * self.tile_w

        initial_surface = self._build_segment_surface(
            initial_width,
            use_left_corner=True,
            use_right_corner=False,
        )
        self.state.segments.append((0.0, initial_surface))

    # ---------- generation helpers ----------

    def _build_segment_surface(
        self,
        width_px: int,
        *,
        use_left_corner: bool = True,
        use_right_corner: bool = True,
    ) -> pg.Surface:
        """Build one ground segment surface from tiles."""
        rows = max(1, math.ceil(GROUND_HEIGHT / self.tile_h))
        cols = max(1, math.ceil(width_px / self.tile_w))

        surf = pg.Surface((width_px, GROUND_HEIGHT), pg.SRCALPHA)  # pylint: disable=no-member

        for i in range(cols):
            x = i * self.tile_w

            if i == 0 and use_left_corner:
                top_tile = self.tiles.top_left
                fill_tile = self.tiles.fill_left
            elif i == cols - 1 and use_right_corner:
                top_tile = self.tiles.top_right
                fill_tile = self.tiles.fill_right
            else:
                top_tile = self.tiles.top_mid
                fill_tile = self.tiles.fill_mid

            # blit top layer
            surf.blit(top_tile, (x, 0))

            # blit the rest of fill layers
            y = self.tile_h
            for _ in range(rows - 1):
                surf.blit(fill_tile, (x, y))
                y += self.tile_h

        return surf

    def _rand_length_multiple_of_tile(self, min_px: int, max_px: int) -> int:
        """Random length that is an integer multiple of the tile width."""
        min_tiles = math.ceil(min_px / self.tile_w)
        max_tiles = math.floor(max_px / self.tile_w)
        if max_tiles < min_tiles:
            return min_px
        return self.rand.randint(min_tiles, max_tiles) * self.tile_w

    def _rand_platform_len(self) -> int:
        """Random platform length in px."""
        return self._rand_length_multiple_of_tile(MIN_GROUND_WIDTH, MAX_GROUND_WIDTH)

    def _rand_gap_len(self) -> int:
        """Random gap length in px."""
        return self._rand_length_multiple_of_tile(MIN_GAP_WIDTH, MAX_GAP_WIDTH)

    def _has_gap_before(self, seg_start: float) -> bool:
        """Whether there is a real gap immediately before the next segment."""
        if not self.state.segments:
            return True
        last_x, last_surf = self.state.segments[-1]
        last_end = last_x + last_surf.get_width()
        return seg_start > last_end + 0.5

    # @generated [partially] ChatGPT : helped with logic for displaying the ends and beignings of ground segments correctly and the "replace gap with obstacle and solid ground" logic
    def _spawn_ground(self) -> Optional[ObstacleSpawnRequest]:
        """Spawn the next platform (+ optional gap extension), maybe emit obstacle request."""
        platform_width = self._rand_platform_len()
        gap_width = self._rand_gap_len()

        seg_start = self.state.spawn_x_pos
        gap_before = self._has_gap_before(seg_start)

        if self.rand.random() < self.state.obstacle_chance:
            # obstacles replaces gap with solid ground below it
            total_width = platform_width + gap_width
            seg_surface = self._build_segment_surface(
                total_width,
                use_left_corner=gap_before,
                use_right_corner=False,
            )
            self.state.segments.append((seg_start, seg_surface))
            self.state.spawn_x_pos += float(total_width)

            # decide if obstacle will be flying
            flying = self.rand.random() < self.FLYING_OBSTACLE_CHANCE

            # obstacles should spawn at least third of lenght of segment from edge
            margin = total_width / 3.0
            region_start = seg_start + margin
            region_end = seg_start + total_width - margin
            if region_end <= region_start:
                return None

            obs_x = self.rand.uniform(region_start, region_end)
            return ObstacleSpawnRequest(x=obs_x, flying=flying)

        seg_surface = self._build_segment_surface(
            platform_width,
            use_left_corner=gap_before,
            use_right_corner=True,
        )
        self.state.segments.append((seg_start, seg_surface))
        self.state.spawn_x_pos += float(platform_width + gap_width)
        return None

    def _ground_buffer(self, width_needed: float) -> list[ObstacleSpawnRequest]:
        """Generate segments until we cover `width_needed`, returning obstacle requests."""
        requests: list[ObstacleSpawnRequest] = []
        while self.state.spawn_x_pos < width_needed:
            req = self._spawn_ground()
            if req is not None:
                requests.append(req)
        return requests

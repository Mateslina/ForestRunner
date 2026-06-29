"""
Parallax background rendering.

Provides a multi-layer parallax system with pre-rendered scrolling layers and a
tiled ground fill, updated based on world speed.
"""

import random
from dataclasses import dataclass
import pygame as pg

from main.core.constants import WIDTH, HEIGHT, GROUND_Y, GROUND_HEIGHT


@dataclass(frozen=True)
class ScaleRange:
    """Scale range for randomly scaling sprites."""

    low: float = 1.0
    high: float = 1.5


@dataclass(frozen=True)
class LayerGenerationConfig:
    """Parameters controlling how a parallax layer surface is generated."""

    density: int
    y_base: int
    scale: ScaleRange = ScaleRange()
    seed: int | None = None


@dataclass(frozen=True)
class ParallaxLayerConfig:
    """Configuration for generating a parallax layer."""

    base_sprites: list[pg.Surface]
    speed_factor: float
    tint_color: tuple[int, int, int] | None
    alpha: int
    generation: LayerGenerationConfig


@dataclass
class LayerScrollState:
    """Pre-rendered surface and its horizontal scroll state."""

    surface: pg.Surface
    speed_factor: float
    scroll_x: float = 0.0


@dataclass
class BackgroundState:
    """Grouped state for the entire background."""

    sky_color: tuple[int, int, int]
    ground_fill: LayerScrollState


@dataclass(frozen=True)
class PlacementParams:
    """Inputs for computing a sprite placement."""

    sprite: pg.Surface
    scale: float
    slot_center: float
    slot_width: float
    y_base: int


def _compute_placement(
    rng: random.Random, params: PlacementParams
) -> tuple[pg.Surface, int, int]:
    """Compute scaled sprite image and its on-surface placement."""
    w = int(params.sprite.get_width() * params.scale)
    h = int(params.sprite.get_height() * params.scale)
    img = pg.transform.smoothscale(params.sprite, (w, h))

    # get random x-pos around the center
    jitter = rng.uniform(-0.3 * params.slot_width, 0.3 * params.slot_width)
    center_x = params.slot_center + jitter

    # set the position of sprite correctly
    x = int(center_x - w / 2)
    x = max(x, 0)
    x = min(x, WIDTH - w)

    y = params.y_base - h
    return img, x, y


def _apply_tint(surface: pg.Surface, tint_color: tuple[int, int, int]) -> None:
    """Apply a multiplicative tint to the entire surface in-place."""
    tint_surf = pg.Surface(surface.get_size(), pg.SRCALPHA)  # pylint: disable=no-member
    tint_surf.fill((*tint_color, 255))
    surface.blit(
        tint_surf,
        (0, 0),
        special_flags=pg.BLEND_RGBA_MULT,  # pylint: disable=no-member
    )


def _build_layer_surface(config: ParallaxLayerConfig) -> pg.Surface:
    """Pre-render a parallax layer to a single surface."""
    surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)  # pylint: disable=no-member

    gen = config.generation
    rng = random.Random(gen.seed)
    slot_width = WIDTH / float(gen.density)

    for i in range(gen.density):
        sprite = rng.choice(config.base_sprites)
        scale = rng.uniform(gen.scale.low, gen.scale.high)
        slot_center = (i + 0.5) * slot_width

        img, x, y = _compute_placement(
            rng,
            PlacementParams(
                sprite=sprite,
                scale=scale,
                slot_center=slot_center,
                slot_width=slot_width,
                y_base=gen.y_base,
            ),
        )
        surface.blit(img, (x, y))

    if config.tint_color is not None:
        _apply_tint(surface, config.tint_color)

    if config.alpha < 255:
        surface.set_alpha(config.alpha)

    return surface


def _create_ground_fill_surface(tile: pg.Surface) -> pg.Surface:
    """Create a tinted, tiled ground-fill surface."""
    tile_w = tile.get_width()
    tile_h = tile.get_height()

    surf = pg.Surface((WIDTH, GROUND_HEIGHT), pg.SRCALPHA)  # pylint: disable=no-member

    # create a grid from the square tiles
    for x in range(0, WIDTH, tile_w):
        for y in range(0, GROUND_HEIGHT, tile_h):
            surf.blit(tile, (x, y))

    _apply_tint(surf, (80, 80, 80))
    return surf


def _advance_scroll(
    scroll_x: float, dt: float, world_speed: float, speed_factor: float
) -> float:
    """Advance scroll and wrap around screen width."""
    scroll_x -= world_speed * speed_factor * dt
    if scroll_x <= -WIDTH:
        scroll_x += WIDTH
    return scroll_x


class ParallaxLayer:
    """A horizontally scrolling parallax layer rendered from random sprites."""

    def __init__(self, config: ParallaxLayerConfig):
        self.state = LayerScrollState(
            surface=_build_layer_surface(config),
            speed_factor=float(config.speed_factor),
            scroll_x=0.0,
        )

    def update(self, dt: float, world_speed: float) -> None:
        """Update layer scroll state."""
        self.state.scroll_x = _advance_scroll(
            self.state.scroll_x,
            dt,
            world_speed,
            self.state.speed_factor,
        )

    def draw(self, screen: pg.Surface) -> None:
        """Draw the layer as two tiled copies."""
        x = int(self.state.scroll_x)
        screen.blit(self.state.surface, (x, 0))
        screen.blit(self.state.surface, (x + WIDTH, 0))


class ParallaxBackground:
    """Manages sky, ground fill, and multiple parallax layers."""

    def __init__(self, tree_sprites: list[pg.Surface], ground_fill_tile: pg.Surface):
        self.layers = self._build_layers(tree_sprites)

        ground_fill = LayerScrollState(
            surface=_create_ground_fill_surface(ground_fill_tile),
            speed_factor=1.0,
            scroll_x=0.0,
        )

        self.state = BackgroundState(
            sky_color=(150, 200, 255),
            ground_fill=ground_fill,
        )

    @staticmethod
    def _build_layers(tree_sprites: list[pg.Surface]) -> list[ParallaxLayer]:
        """Create the parallax layer stack."""
        y_base = GROUND_Y
        configs = [
            ParallaxLayerConfig(
                base_sprites=tree_sprites,
                speed_factor=0.2,
                tint_color=(0, 0, 0),
                alpha=255,
                generation=LayerGenerationConfig(
                    density=60,
                    y_base=y_base,
                    scale=ScaleRange(low=0.7, high=0.9),
                    seed=1,
                ),
            ),
            ParallaxLayerConfig(
                base_sprites=tree_sprites,
                speed_factor=0.4,
                tint_color=(80, 120, 80),
                alpha=255,
                generation=LayerGenerationConfig(
                    density=8,
                    y_base=y_base,
                    scale=ScaleRange(low=0.9, high=1.1),
                    seed=2,
                ),
            ),
            ParallaxLayerConfig(
                base_sprites=tree_sprites,
                speed_factor=0.6,
                tint_color=None,
                alpha=255,
                generation=LayerGenerationConfig(
                    density=6,
                    y_base=y_base,
                    scale=ScaleRange(low=1.0, high=1.2),
                    seed=3,
                ),
            ),
        ]
        return [ParallaxLayer(cfg) for cfg in configs]

    def update(self, dt: float, world_speed: float) -> None:
        """Update all parallax layers and the ground fill scroll."""
        for layer in self.layers:
            layer.update(dt, world_speed)

        gf = self.state.ground_fill
        gf.scroll_x = _advance_scroll(
            gf.scroll_x,
            dt,
            world_speed,
            gf.speed_factor,
        )

    def draw(self, screen: pg.Surface) -> None:
        """Draw sky, horizon, ground fill, and all parallax layers."""
        screen.fill(self.state.sky_color)

        # bottom 60% are black
        horizon_y = int(HEIGHT * 0.4)
        pg.draw.rect(screen, (0, 0, 0), (0, horizon_y, WIDTH, HEIGHT - horizon_y))

        x = int(self.state.ground_fill.scroll_x)
        screen.blit(self.state.ground_fill.surface, (x, GROUND_Y))
        screen.blit(self.state.ground_fill.surface, (x + WIDTH, GROUND_Y))

        for layer in self.layers:
            layer.draw(screen)

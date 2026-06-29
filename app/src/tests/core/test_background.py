# @generated [all] ChatGPT : generate tests based on class implementation
import pytest

import main.core.background as bg_mod
from main.core.background import (
    ParallaxLayer,
    ParallaxBackground,
    ParallaxLayerConfig,
    LayerGenerationConfig,
    ScaleRange,
)
from main.core.constants import WIDTH, HEIGHT, GROUND_HEIGHT


@pytest.mark.parametrize(
    "start_scroll, expected_after",
    [
        (-float(WIDTH) - 1.0, True),   # should wrap to > -WIDTH
        (-float(WIDTH) + 1.0, False),  # should not wrap
    ],
)
def test_advance_scroll_wraps_only_when_needed(start_scroll, expected_after):
    out = bg_mod._advance_scroll(  # pylint: disable=protected-access
        scroll_x=start_scroll,
        dt=0.0,
        world_speed=0.0,
        speed_factor=1.0,
    )

    if expected_after:
        assert out > -float(WIDTH)
    else:
        assert out == start_scroll


def test_parallax_layer_wraps_scroll_and_draw_does_not_crash(surface_factory):
    tree = surface_factory((10, 20))

    cfg = ParallaxLayerConfig(
        base_sprites=[tree],
        speed_factor=1.0,
        tint_color=None,
        alpha=255,
        generation=LayerGenerationConfig(
            density=2,
            y_base=100,
            scale=ScaleRange(low=1.0, high=1.0),
            seed=0,
        ),
    )
    layer = ParallaxLayer(cfg)

    layer.state.scroll_x = -float(WIDTH) - 1.0

    layer.update(dt=0.0, world_speed=0.0)
    assert layer.state.scroll_x > -float(WIDTH)

    screen = surface_factory((WIDTH, HEIGHT))
    layer.draw(screen)


def test_parallax_background_updates_ground_fill_wrap_and_draw_does_not_crash(surface_factory):
    tree = surface_factory((10, 20))
    tile = surface_factory((16, 16))

    bg = ParallaxBackground(tree_sprites=[tree], ground_fill_tile=tile)

    bg.state.ground_fill.scroll_x = -float(WIDTH) - 2.0

    bg.update(dt=0.0, world_speed=0.0)
    assert bg.state.ground_fill.scroll_x > -float(WIDTH)

    screen = surface_factory((WIDTH, HEIGHT))
    bg.draw(screen)


def test_create_ground_fill_surface_size(surface_factory):
    tile = surface_factory((32, 32))

    surf = bg_mod._create_ground_fill_surface(tile)  # pylint: disable=protected-access
    assert surf.get_size() == (WIDTH, GROUND_HEIGHT)

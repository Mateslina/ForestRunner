# @generated [all] ChatGPT : generate tests based on class implementation
import pytest

from main.entities.collectibles.powerups import PowerUp
from tests.entities.collectibles.collectible_asserts import (
    InitSpec,
    assert_collectible_draw_blits,
    assert_collectible_init,
    assert_collectible_update_moves_left,
)
from tests.helpers.constants import POWERUP_KEYS


@pytest.mark.parametrize("kind", POWERUP_KEYS)
def test_powerup_init_sets_rect_and_fields(surface_factory, kind):
    sprite = surface_factory((12, 8))
    p = PowerUp(100.0, 40.0, kind=kind, sprite=sprite)

    assert p.kind == kind
    assert_collectible_init(p, sprite, InitSpec(x=100.0, y=40.0, size=(12, 8)))


@pytest.mark.parametrize(
    "dt,speed,start_x,expected_x",
    [
        (0.25, 400.0, 100.0, 0.0),  # move 100px left
        (0.0, 999.0, 50.0, 50.0),   # no move
    ],
)
@pytest.mark.parametrize("kind", POWERUP_KEYS)
def test_powerup_update_moves_left_and_updates_rect_x(surface_factory, kind, dt, speed, start_x, expected_x):
    sprite = surface_factory((12, 8))
    p = PowerUp(start_x, 40.0, kind=kind, sprite=sprite)

    assert_collectible_update_moves_left(
        p,
        dt=dt,
        speed=speed,
        expected_x=expected_x,
        expected_y=40.0,
    )


@pytest.mark.parametrize("kind", POWERUP_KEYS)
def test_powerup_draw_blits_sprite(surface_factory, kind):
    sprite = surface_factory((12, 8))
    p = PowerUp(10.0, 10.0, kind=kind, sprite=sprite)

    assert_collectible_draw_blits(p, sprite)

# @generated [all] ChatGPT : generate tests based on class implementation
import pytest

from main.entities.collectibles.coins import Coin
from tests.entities.collectibles.collectible_asserts import (
    InitSpec,
    assert_collectible_draw_blits,
    assert_collectible_init,
    assert_collectible_update_moves_left,
)


def test_coin_init_sets_rect_from_position_and_sprite_size(surface_factory):
    sprite = surface_factory((10, 12))
    c = Coin(100.0, 50.0, sprite)

    assert_collectible_init(c, sprite, InitSpec(x=100.0, y=50.0, size=(10, 12)))


@pytest.mark.parametrize(
    "dt,speed,start_x,expected_x",
    [
        (0.5, 200.0, 100.0, 0.0),    # move 100px left
        (0.25, 400.0, 100.0, 0.0),   # move 100px left
        (0.0, 999.0, 50.0, 50.0),    # no move
    ],
)
def test_coin_update_moves_left_and_updates_rect_x(surface_factory, dt, speed, start_x, expected_x):
    sprite = surface_factory((10, 10))
    c = Coin(float(start_x), 50.0, sprite)

    assert_collectible_update_moves_left(
        c,
        dt=float(dt),
        speed=float(speed),
        expected_x=float(expected_x),
        expected_y=50.0,
    )


def test_coin_draw_blits_to_surface(surface_factory):
    sprite = surface_factory((12, 8))
    c = Coin(10.0, 20.0, sprite=sprite)

    assert_collectible_draw_blits(c, sprite)

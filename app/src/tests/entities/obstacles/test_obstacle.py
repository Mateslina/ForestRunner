# @generated [all] ChatGPT : generate tests based on class implementation
import pytest

from main.core.constants import GROUND_Y, PLAYER_HEIGHT
from main.entities.obstacles.obstacle import Obstacle, ObstacleSprites
from tests.helpers.fakes import BlitSpy


def test_ground_obstacle_sets_rect_on_ground(surface_factory):
    sprite = surface_factory((30, 40))
    o = Obstacle(x=500, flying=False, speed=0.0, sprites=ObstacleSprites(sprite=sprite))

    assert o.rect.width == 30
    assert o.rect.height == 40
    assert o.rect.bottom == GROUND_Y
    assert o.rect.y == int(round(GROUND_Y - o.rect.height))


def test_flying_obstacle_sets_rect_above_ground(surface_factory):
    frames = [surface_factory((30, 40)), surface_factory((30, 40))]
    o = Obstacle(x=500, flying=True, speed=0.0, sprites=ObstacleSprites(frames=frames))

    expected_bottom = GROUND_Y - PLAYER_HEIGHT * 0.75
    assert abs(o.rect.bottom - expected_bottom) <= 1


def test_hitbox_is_shrunk_and_bottom_aligned_to_rect(surface_factory):
    sprite = surface_factory((100, 50))
    o = Obstacle(x=100, flying=False, speed=0.0, sprites=ObstacleSprites(sprite=sprite))

    assert o.hitbox.width < o.rect.width
    assert o.hitbox.height < o.rect.height
    assert o.hitbox.bottom == o.rect.bottom


@pytest.mark.parametrize(
    "flying, base_speed, dt, expected_speed",
    [
        (False, 200.0, 0.5, 200.0),
        (True, 200.0, 0.5, 200.0 * Obstacle.FLYING_SPEED_MULT),
    ],
)
def test_update_applies_speed_multiplier_and_moves_left(surface_factory, flying, base_speed, dt, expected_speed):
    sprite = surface_factory((10, 10))
    sprites = ObstacleSprites(frames=[sprite, sprite]) if flying else ObstacleSprites(sprite=sprite)

    o = Obstacle(x=100.0, flying=flying, speed=0.0, sprites=sprites)
    old_x = o.state.x

    o.update(dt, speed=base_speed)

    assert o.state.speed == expected_speed
    assert o.state.x == old_x - expected_speed * dt
    assert o.rect.x == int(round(o.state.x))


def test_update_keeps_hitbox_centerx_and_bottom_in_sync_with_rect(surface_factory):
    sprite = surface_factory((40, 30))
    o = Obstacle(x=100.0, flying=False, speed=0.0, sprites=ObstacleSprites(sprite=sprite))

    o.update(dt=0.25, speed=120.0)

    assert o.hitbox.centerx == o.rect.centerx
    assert o.hitbox.bottom == o.rect.bottom


def test_animation_advances_when_frames_present(surface_factory):
    frames = [surface_factory((10, 10)), surface_factory((10, 10))]
    o = Obstacle(x=200.0, flying=True, speed=0.0, sprites=ObstacleSprites(frames=frames))

    o.update(dt=0.25, speed=0.0)
    assert o.anim.frame_index in (0, 1)


def test_animation_does_not_advance_when_static_sprite(surface_factory):
    sprite = surface_factory((10, 10))
    o = Obstacle(x=200.0, flying=False, speed=0.0, sprites=ObstacleSprites(sprite=sprite))

    idx_before = o.anim.frame_index
    time_before = o.anim.time_acc

    o.update(dt=1.0, speed=0.0)

    assert o.anim.frame_index == idx_before
    assert o.anim.time_acc == time_before


def test_draw_uses_sprite_when_static(surface_factory):
    sprite = surface_factory((20, 10))
    o = Obstacle(x=100, flying=False, sprites=ObstacleSprites(sprite=sprite))

    screen = BlitSpy()
    o.draw(screen)

    src, dest = screen.calls[-1]
    assert src is sprite
    assert dest == o.rect.topleft


def test_draw_uses_current_frame_when_animated(surface_factory):
    f0 = surface_factory((20, 10))
    f1 = surface_factory((20, 10))
    o = Obstacle(x=100, flying=True, sprites=ObstacleSprites(frames=[f0, f1]))

    o.anim.frame_index = 1
    screen = BlitSpy()
    o.draw(screen)

    src, dest = screen.calls[-1]
    assert src is f1
    assert dest == o.rect.topleft


@pytest.mark.parametrize(
    "x, width, expected",
    [
        (-1.0, 10, False),     # still visible (partially)
        (-10.0, 10, False),    # edge case: exactly at 0
        (-11.0, 10, True),     # fully off-screen
    ],
)
def test_is_off_screen(surface_factory, x, width, expected):
    sprite = surface_factory((width, 5))
    o = Obstacle(x=x, flying=False, speed=0.0, sprites=ObstacleSprites(sprite=sprite))
    assert o.is_off_screen is expected

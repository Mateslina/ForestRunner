# @generated [all] ChatGPT : generate tests based on class implementation
import random
from types import SimpleNamespace

import pytest

from main.core.constants import PLAYER_X
from main.entities.obstacles.obstacle_manager import ObstacleManager
from main.entities.obstacles.obstacle import Obstacle
from tests.helpers.fakes import GroundSolidSpy


def _assets_for_manager(surface_factory):
    # manager expects: assets.obstacles.rock_tiles, assets.obstacles.bird_frames
    obstacles = SimpleNamespace(
        rock_tiles=[surface_factory((10, 10)), surface_factory((12, 12))],
        bird_frames=[surface_factory((30, 20)), surface_factory((30, 20))],
    )
    return SimpleNamespace(obstacles=obstacles)


def test_spawn_ground_obstacle_when_flying_false(surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy()

    mgr.spawn_obstacle_at(x=500.0, ground=ground, flying=False)

    assert len(mgr.obstacles) == 1
    o = mgr.obstacles[0]
    assert o.state.flying is False
    assert o.sprites.sprite is not None
    assert o.sprites.frames is None


def test_spawn_flying_obstacle_uses_offset_and_frames_when_safe_ground(monkeypatch, surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy(solid=True)

    monkeypatch.setattr(mgr, "_flying_has_safe_ground", lambda *a, **k: True)

    base_x = 600.0
    mgr.spawn_obstacle_at(x=base_x, ground=ground, flying=True)

    assert len(mgr.obstacles) == 1
    o = mgr.obstacles[0]
    assert o.state.flying is True
    assert o.sprites.frames is assets.obstacles.bird_frames
    assert o.sprites.sprite is None
    assert o.state.x == pytest.approx(base_x + mgr.BIRD_SPAWN_X_OFFSET)


def test_spawn_flying_falls_back_to_ground_when_not_safe(monkeypatch, surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy(solid=False)

    monkeypatch.setattr(mgr, "_flying_has_safe_ground", lambda *a, **k: False)

    mgr.spawn_obstacle_at(x=700.0, ground=ground, flying=True)

    assert len(mgr.obstacles) == 1
    o = mgr.obstacles[0]
    assert o.state.flying is False
    assert o.sprites.sprite is not None
    assert o.sprites.frames is None


def test_flying_has_safe_ground_rejects_if_spawn_is_left_of_player(surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy(solid=True)
    frames = assets.obstacles.bird_frames

    assert mgr._flying_has_safe_ground(float(PLAYER_X), ground, frames) is False  # pylint: disable=protected-access


def test_flying_has_safe_ground_calls_ground_is_solid_with_expected_overlap(surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy(solid=True, speed=400.0)
    frames = assets.obstacles.bird_frames

    spawn_x = float(PLAYER_X) + 500.0
    ok = mgr._flying_has_safe_ground(spawn_x, ground, frames)  # pylint: disable=protected-access
    assert ok is True
    assert len(ground.calls) == 1

    x1, x2, min_overlap = ground.calls[0]
    assert x2 > x1
    assert min_overlap > 0.0


def test_update_moves_obstacles_and_culls_offscreen(surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy()

    mgr.spawn_obstacle_at(x=10.0, ground=ground, flying=False)
    mgr.spawn_obstacle_at(x=500.0, ground=ground, flying=False)

    keep = mgr.obstacles[1]
    mgr.obstacles[0].state.x = -10_000.0  # far left => offscreen

    mgr.update(dt=0.0, current_speed=300.0)

    assert len(mgr.obstacles) == 1
    assert mgr.obstacles[0] is keep


def test_draw_calls_each_obstacle_draw(monkeypatch, surface_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy()

    mgr.spawn_obstacle_at(x=100.0, ground=ground, flying=False)
    mgr.spawn_obstacle_at(x=200.0, ground=ground, flying=False)

    screen = surface_factory((800, 600))

    calls = {"n": 0}

    def counted_draw(self, surface):
        assert surface is screen
        calls["n"] += 1

    monkeypatch.setattr(Obstacle, "draw", counted_draw)

    mgr.draw(screen)
    assert calls["n"] == 2


def test_get_first_collision_returns_first_by_order(surface_factory, rect_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy()

    mgr.spawn_obstacle_at(x=100.0, ground=ground, flying=False)
    mgr.spawn_obstacle_at(x=200.0, ground=ground, flying=False)

    player = rect_factory(0, 0, 5, 5)
    for o in mgr.obstacles:
        o.body.hitbox = player.copy()

    hit = mgr.get_first_collision(player)
    assert hit is mgr.obstacles[0]


def test_get_first_collision_returns_none_when_no_collisions(surface_factory, rect_factory):
    assets = _assets_for_manager(surface_factory)
    mgr = ObstacleManager(assets, rand=random.Random(0))
    ground = GroundSolidSpy()

    mgr.spawn_obstacle_at(x=100.0, ground=ground, flying=False)

    player = rect_factory(0, 0, 1, 1)
    mgr.obstacles[0].body.hitbox = rect_factory(1000, 1000, 10, 10)

    assert mgr.get_first_collision(player) is None

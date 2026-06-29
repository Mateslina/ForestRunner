# @generated [all] ChatGPT : generate tests based on class implementation

import random
import pytest

from main.core.constants import WIDTH
from main.entities.ground import Ground, ObstacleSpawnRequest


class TilesFake:
    """
    Minimal GroundTiles fake required by Ground.
    Uses surface_factory to avoid local pygame.Surface duplication.
    """
    def __init__(self, surface_factory):
        self.top_mid = surface_factory()
        self.fill_mid = surface_factory()
        self.top_left = surface_factory()
        self.top_right = surface_factory()
        self.fill_left = surface_factory()
        self.fill_right = surface_factory()


@pytest.fixture
def ground(surface_factory):
    g = Ground(speed=300.0, tiles=TilesFake(surface_factory))
    g.rand = random.Random(0)  # deterministic
    return g


def test_ground_initial_segment_exists_and_covers_screen(ground: Ground):
    segs = ground.get_segments()
    assert len(segs) == 1
    x0, w0 = segs[0]
    assert x0 == 0.0
    assert w0 >= WIDTH


def test_ground_reset_restores_defaults_and_one_segment(ground: Ground):
    ground.speed = 999.0
    ground.state.spawn_x_pos = -123.0
    ground.obstacle_chance = 0.9
    ground.state.segments.append((1000.0, ground.tiles.top_mid))

    ground.reset(300.0)

    assert ground.speed == 300.0
    assert ground.state.spawn_x_pos == float(WIDTH)
    assert ground.obstacle_chance == Ground.DEFAULT_OBSTACLE_CHANCE
    assert len(ground.state.segments) == 1
    assert ground.state.segments[0][0] == 0.0


def test_rand_length_multiple_of_tile_respects_tile_multiple(ground: Ground):
    tw = ground.tile_w
    out = ground._rand_length_multiple_of_tile(100, 300)
    assert out % tw == 0
    assert 100 <= out <= 300


def test_rand_length_multiple_of_tile_falls_back_if_range_too_tight(ground: Ground):
    tw = ground.tile_w
    min_px = tw * 10 + 1
    max_px = tw * 10
    out = ground._rand_length_multiple_of_tile(min_px, max_px)
    assert out == min_px


def test_spawn_ground_without_obstacle_returns_none_and_advances_spawn(ground: Ground, monkeypatch):
    monkeypatch.setattr(ground.rand, "random", lambda: 0.999)

    start = ground.state.spawn_x_pos
    req = ground._spawn_ground()

    assert req is None
    assert ground.state.spawn_x_pos > start
    assert len(ground.state.segments) >= 2


def test_spawn_ground_with_obstacle_returns_request_and_advances_spawn(ground: Ground, monkeypatch):
    monkeypatch.setattr(ground.rand, "random", lambda: 0.0)

    start = ground.state.spawn_x_pos
    req = ground._spawn_ground()

    assert isinstance(req, ObstacleSpawnRequest)
    assert isinstance(req.flying, bool)
    assert req.x > start
    assert ground.state.spawn_x_pos > start
    assert len(ground.state.segments) >= 2


def test_update_moves_segments_left_and_removes_offscreen(ground: Ground, monkeypatch):
    monkeypatch.setattr(ground.rand, "random", lambda: 0.999)

    ground.state.segments.append((-50.0, ground.tiles.top_mid))

    x0_before = ground.state.segments[0][0]
    dt = 0.1
    dx = ground.speed * dt

    _reqs = ground.update(dt)

    x0_after = ground.state.segments[0][0]
    assert x0_after == pytest.approx(x0_before - dx, rel=1e-6)

    assert all(x + surf.get_width() > 0 for (x, surf) in ground.state.segments)


def test_is_solid_at_x_detects_overlap(ground: Ground):
    assert ground.is_solid_at_x(0.0, 10.0, min_overlap=1.0) is True
    assert ground.is_solid_at_x(-100.0, -50.0, min_overlap=1.0) is False


def test_ground_buffer_generates_until_needed(ground: Ground, monkeypatch):
    monkeypatch.setattr(ground.rand, "random", lambda: 0.999)

    ground.state.spawn_x_pos = 0.0
    reqs = ground._ground_buffer(width_needed=float(WIDTH) * 2.0)

    assert isinstance(reqs, list)
    assert ground.state.spawn_x_pos >= float(WIDTH) * 2.0

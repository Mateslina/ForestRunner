# @generated [all] ChatGPT : generate tests based on class implementation
import random

from main.core.constants import GROUND_Y, WIDTH, PLAYER_HEIGHT
from main.entities.collectibles.collectible_spawner import CollectibleSpawner, SpawnPoint
from tests.helpers.fakes import GroundWithSegmentsFake, ObstacleFake


def test_spawn_window_bounds_are_in_front_of_screen():
    sp = CollectibleSpawner(random.Random(0))
    win = sp._spawn_window()  # pylint: disable=protected-access

    assert win.min_x == float(WIDTH)
    assert win.max_x > win.min_x


def test_gaps_in_window_detects_gap_between_segments():
    sp = CollectibleSpawner(random.Random(0))
    segs = [(0.0, 100.0), (200.0, 300.0)]  # (start_x, end_x)

    gaps = sp._gaps_in_window(segs, min_x=50.0, max_x=250.0)  # pylint: disable=protected-access
    assert gaps == [(100.0, 200.0)]


def test_pick_spawn_point_returns_none_if_no_segments():
    sp = CollectibleSpawner(random.Random(0))
    ground = GroundWithSegmentsFake([])
    assert sp.pick_spawn_point(10.0, 10.0, ground, obstacles=[]) is None


def test_pick_spawn_prefers_under_flying_obstacle():
    ground = GroundWithSegmentsFake([(0.0, int(WIDTH * 3))])  # (start_x, width)
    flying = ObstacleFake(int(WIDTH + 100), int(GROUND_Y - 200), 80, 40, flying=True)
    sp = CollectibleSpawner(rand=random.Random(0))

    pt = sp.pick_spawn_point(item_w=20, item_h=20, ground=ground, obstacles=[flying])

    assert pt is not None
    assert isinstance(pt, SpawnPoint)
    assert pt.y == float(GROUND_Y - 20)


def test_pick_spawn_prefers_above_ground_obstacle_when_no_flying():
    ground = GroundWithSegmentsFake([(0.0, int(WIDTH * 3))])  # (start_x, width)
    rock = ObstacleFake(int(WIDTH + 120), int(GROUND_Y - 60), 80, 60, flying=False)
    sp = CollectibleSpawner(rand=random.Random(0))

    pt = sp.pick_spawn_point(item_w=20, item_h=20, ground=ground, obstacles=[rock])

    assert pt is not None
    assert isinstance(pt, SpawnPoint)
    assert pt.y == float(rock.rect.top - 20 - 60)


def test_pick_spawn_above_gap_when_no_obstacles():
    ground = GroundWithSegmentsFake(
        [
            (0.0, int(WIDTH + 200)),
            (int(WIDTH + 400), int(WIDTH)),  # gap (WIDTH+200 .. WIDTH+400)
        ]
    )
    sp = CollectibleSpawner(rand=random.Random(0))

    pt = sp.pick_spawn_point(item_w=20, item_h=20, ground=ground, obstacles=[])

    assert pt is not None
    assert isinstance(pt, SpawnPoint)
    assert pt.y == float(GROUND_Y - PLAYER_HEIGHT - 120)


def test_pick_spawn_on_solid_ground_fallback(monkeypatch):
    ground = GroundWithSegmentsFake([(0.0, int(WIDTH * 3))])  # (start_x, width)
    sp = CollectibleSpawner(rand=random.Random(0))

    monkeypatch.setattr(sp.rand, "uniform", lambda a, b: float(WIDTH + 10))

    pt = sp.pick_spawn_point(item_w=20, item_h=20, ground=ground, obstacles=[])

    assert pt is not None
    assert isinstance(pt, SpawnPoint)
    assert pt.y == float(GROUND_Y - 20)

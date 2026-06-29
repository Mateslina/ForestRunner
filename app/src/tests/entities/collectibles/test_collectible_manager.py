# @generated [all] ChatGPT : generate tests based on class implementation
from main.entities.collectibles.collectible_manager import CollectibleManager, SpawnTiming
from main.entities.collectibles.collectible_spawner import SpawnPoint
from main.entities.collectibles.coins import Coin
from main.entities.collectibles.powerups import PowerUp
from tests.helpers.constants import POWERUP_KEYS
from tests.helpers.fakes import (
    SpawnerReturning,
    GroundFake,
    ObstaclesFake,
)

KIND = POWERUP_KEYS[0]


def test_set_coin_sprite_updates_existing_coins_rect_size_and_keeps_anchor(fake_collectible_assets, surface_factory):
    m = CollectibleManager(assets=fake_collectible_assets)

    m.items.coins.append(Coin(100.0, 100.0, sprite=m.state.coin_sprite_current))
    old_midbottom = m.items.coins[0].rect.midbottom

    new_sprite = surface_factory((30, 40))
    m.set_coin_sprite(new_sprite)

    assert m.state.coin_sprite_current is new_sprite
    assert m.items.coins[0].sprite is new_sprite
    assert m.items.coins[0].rect.size == (30, 40)
    assert m.items.coins[0].rect.midbottom == old_midbottom


def test_try_spawn_retry_when_no_spawn_point(fake_collectible_assets):
    m = CollectibleManager(assets=fake_collectible_assets)
    m.state.time_to_next_spawn = 0.0
    m.spawner = SpawnerReturning(pt=None)

    m._try_spawn(ground=GroundFake(), obstacles=ObstaclesFake())  # pylint: disable=protected-access

    assert m.state.time_to_next_spawn == 0.5
    assert not m.items.coins
    assert not m.items.powerups


def test_try_spawn_coin(monkeypatch, fake_collectible_assets):
    timing = SpawnTiming(powerup_chance=0.0)
    m = CollectibleManager(assets=fake_collectible_assets, timing=timing)
    m.state.time_to_next_spawn = 0.0

    m.spawner = SpawnerReturning(pt=SpawnPoint(x=200.0, y=300.0))
    monkeypatch.setattr(m, "_next_time", lambda: 1.23)

    m._try_spawn(ground=GroundFake(), obstacles=ObstaclesFake())  # pylint: disable=protected-access

    assert len(m.items.coins) == 1
    assert len(m.items.powerups) == 0
    assert m.items.coins[0].rect.topleft == (200, 300)
    assert m.state.time_to_next_spawn == 1.23


def test_try_spawn_powerup(monkeypatch, fake_collectible_assets):
    timing = SpawnTiming(powerup_chance=1.0)
    m = CollectibleManager(assets=fake_collectible_assets, timing=timing)
    m.state.time_to_next_spawn = 0.0

    m.spawner = SpawnerReturning(pt=SpawnPoint(x=200.0, y=300.0))
    monkeypatch.setattr(m, "_next_time", lambda: 2.0)
    monkeypatch.setattr(m, "_pick_powerup_kind", lambda: KIND)

    m._try_spawn(ground=GroundFake(), obstacles=ObstaclesFake())  # pylint: disable=protected-access

    assert len(m.items.coins) == 0
    assert len(m.items.powerups) == 1
    assert m.items.powerups[0].kind == KIND
    assert m.state.time_to_next_spawn == 2.0


def test_remove_offscreen_filters(fake_collectible_assets):
    m = CollectibleManager(assets=fake_collectible_assets)

    c1 = Coin(-20, 0, sprite=m.state.coin_sprite_current)  # offscreen (rect.right <= 0)
    c2 = Coin(10, 0, sprite=m.state.coin_sprite_current)   # onscreen
    m.items.coins = [c1, c2]

    powerup_sprite = fake_collectible_assets.collectibles.powerups.all[KIND]

    p1 = PowerUp(-50, 0, kind=KIND, sprite=powerup_sprite)
    p2 = PowerUp(10, 0, kind=KIND, sprite=powerup_sprite)
    m.items.powerups = [p1, p2]

    m._remove_offscreen()  # pylint: disable=protected-access

    assert m.items.coins == [c2]
    assert m.items.powerups == [p2]


def test_collect_coin_collisions_counts_and_removes(fake_collectible_assets, rects):
    m = CollectibleManager(assets=fake_collectible_assets)

    m.items.coins = [
        Coin(0, 0, sprite=m.state.coin_sprite_current),
        Coin(100, 0, sprite=m.state.coin_sprite_current),
    ]

    got = m.collect_coin_collisions(rects["origin_10x10"])

    assert got == 1
    assert len(m.items.coins) == 1
    assert m.items.coins[0].rect.topleft == (100, 0)


def test_collect_powerup_collisions_returns_objects_and_removes(fake_collectible_assets, rects):
    m = CollectibleManager(assets=fake_collectible_assets)

    powerup_sprite = fake_collectible_assets.collectibles.powerups.all[KIND]

    p_hit = PowerUp(0, 0, kind=KIND, sprite=powerup_sprite)
    p_miss = PowerUp(100, 0, kind=KIND, sprite=powerup_sprite)
    m.items.powerups = [p_hit, p_miss]

    got = m.collect_powerup_collisions(rects["origin_10x10"])

    assert got == [p_hit]
    assert m.items.powerups == [p_miss]

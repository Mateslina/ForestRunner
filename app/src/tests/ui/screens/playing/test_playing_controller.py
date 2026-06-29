# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace

import pygame as pg
import pytest

from main.ui.screens.playing.playing_controller import PlayingController
from main.core.game_state import GameState
from main.core.constants import BASE_SPEED, GROUND_Y


# ------------------------ lightweight stubs ------------------------

class _PlayerStub:
    def __init__(self, rect_factory):
        self.rect = rect_factory(50, int(GROUND_Y - 60), 40, 60)
        self.on_ground = True

        self.shield_active = False
        self.shield_time = 0.0
        self.invuln_time = 0.0

        self.did_respawn = False
        self.invuln_set = None

        self.jump_calls = 0
        self.crouch_calls: list[bool] = []

    def update(self, dt, ground, speed):
        _ = (dt, ground, speed)

    def jump(self):
        self.jump_calls += 1

    def set_crouch(self, active: bool):
        self.crouch_calls.append(bool(active))

    def give_shield(self, duration: float):
        self.shield_active = True
        self.shield_time = float(duration)

    def consume_shield(self):
        self.shield_active = False
        self.shield_time = 0.0

    def respawn(self):
        self.did_respawn = True

    def set_invulnerable(self, duration: float):
        self.invuln_time = max(self.invuln_time, float(duration))
        self.invuln_set = float(duration)

    @property
    def invulnerable(self):
        return self.invuln_time > 0.0


class _GroundStub:
    def __init__(self):
        self.speed = float(BASE_SPEED)
        self.obstacle_chance = 0.3
        self._update_returns: list[object] = []
        self.reset_calls: list[float] = []
        self.update_calls: list[float] = []

    def reset(self, speed: float):
        self.reset_calls.append(float(speed))
        self.speed = float(speed)

    def update(self, dt: float):
        self.update_calls.append(float(dt))
        return list(self._update_returns)

    def is_solid_at_x(self, *a, **k):
        return True


class _ObstaclesStub:
    def __init__(self, *a, **k):
        self.obstacles: list[object] = []
        self.spawn_calls: list[tuple[float, bool]] = []
        self.update_calls: list[tuple[float, float]] = []
        self._first_collision = None

    def spawn_obstacle_at(self, x, ground=None, flying=False):
        _ = ground
        self.spawn_calls.append((float(x), bool(flying)))

    def update(self, dt, current_speed):
        self.update_calls.append((float(dt), float(current_speed)))

    def draw(self, win):
        _ = win

    def get_first_collision(self, rect):
        _ = rect
        return self._first_collision


class _CollectiblesStub:
    def __init__(self, *a, **k):
        self.update_calls: list[tuple[float, float]] = []
        self.set_sprite_calls: list[pg.Surface] = []
        self._coins_to_collect = 0
        self._powerups_to_collect: list[object] = []

    def set_coin_sprite(self, sprite):
        self.set_sprite_calls.append(sprite)

    def update(self, dt, speed, ground, obstacles):
        _ = (ground, obstacles)
        self.update_calls.append((float(dt), float(speed)))

    def collect_coin_collisions(self, rect):
        _ = rect
        return int(self._coins_to_collect)

    def collect_powerup_collisions(self, rect):
        _ = rect
        return list(self._powerups_to_collect)

    def draw(self, win):
        _ = win


class _BackgroundStub:
    def __init__(self):
        self.update_calls: list[tuple[float, float]] = []
        self.draw_calls = 0

    def update(self, dt, speed):
        self.update_calls.append((float(dt), float(speed)))

    def draw(self, win):
        _ = win
        self.draw_calls += 1


class _HUDStub:
    def __init__(self):
        self.draw_calls: list[object] = []

    def draw(self, win, hud_state):
        _ = win
        self.draw_calls.append(hud_state)


class _AssetsStub:
    def __init__(self, surface_factory, player_frames):
        self.collectibles = SimpleNamespace(
            coins=SimpleNamespace(
                normal=surface_factory((10, 10)),
                double=surface_factory((15, 10)),
            ),
            powerups=SimpleNamespace(
                all={
                    "shield": surface_factory((10, 10)),
                    "double_score": surface_factory((10, 10)),
                    "double_coins": surface_factory((10, 10)),
                    "extra_life": surface_factory((10, 10)),
                }
            ),
        )
        self.player = player_frames  # <-- DEDUPE
        self.obstacles = SimpleNamespace(
            rock_tiles=[surface_factory((10, 10))],
            bird_frames=[surface_factory((10, 10)), surface_factory((10, 10))],
        )


class _PowerUpObj:
    def __init__(self, kind: str):
        self.kind = kind


@pytest.fixture
def ctrl(monkeypatch, game_stub):
    import main.ui.screens.playing.playing_controller as ctrl_mod

    class _PlayerFactory:
        def __call__(self, assets):
            _ = assets
            return game_stub.ctx.player

    monkeypatch.setattr(ctrl_mod, "Player", _PlayerFactory())
    monkeypatch.setattr(ctrl_mod, "ObstacleManager", lambda assets: _ObstaclesStub())
    monkeypatch.setattr(ctrl_mod, "CollectibleManager", lambda assets: _CollectiblesStub())

    return PlayingController(game_stub)


# ------------------------ tests ------------------------

def test_controller_init_resets_player_and_ground(ctrl, game_stub):
    assert game_stub.ctx.ground.reset_calls == [float(BASE_SPEED)]
    assert ctrl.run.lives == ctrl.run.max_lives
    assert ctrl.run.max_lives == 3


def test_controller_on_jump_forwards_to_player(ctrl, game_stub):
    ctrl.on_jump()
    assert game_stub.ctx.player.jump_calls == 1


def test_controller_set_crouch_forwards_to_player(ctrl, game_stub):
    ctrl.set_crouch(True)
    ctrl.set_crouch(False)
    assert game_stub.ctx.player.crouch_calls == [True, False]


def test_controller_update_score_increases(ctrl):
    ctrl.run.score = 0.0
    ctrl._update_score(0.5)
    assert ctrl.run.score == pytest.approx(0.5)


def test_controller_double_score_buff_expires(ctrl):
    ctrl.run.buffs.score_mult = 2.0
    ctrl.run.buffs.double_score_time = 0.1

    ctrl._update_buffs(0.2)
    assert ctrl.run.buffs.double_score_time == 0.0
    assert ctrl.run.buffs.score_mult == 1.0


def test_controller_double_coins_buff_expires_and_resets_icon(ctrl, game_stub):
    ctrl.run.buffs.coins_mult = 2
    ctrl.run.buffs.double_coins_time = 0.1

    ctrl._update_buffs(0.2)
    assert ctrl.run.buffs.double_coins_time == 0.0
    assert ctrl.run.buffs.coins_mult == 1
    assert ctrl.collectibles.set_sprite_calls[-1] is game_stub.ctx.assets.collectibles.coins.normal


def test_controller_collects_coins_with_multiplier(ctrl):
    ctrl.run.buffs.coins_mult = 2
    ctrl.collectibles._coins_to_collect = 3

    ctrl._update_world(0.1)
    assert ctrl.run.collected_coins == 6


def test_controller_powerup_double_score_sets_multiplier_and_timer(ctrl, game_stub):
    ctrl.collectibles._powerups_to_collect = [_PowerUpObj("double_score")]
    game_stub.ctx.progress.upgrades["double_score_duration_level"] = 1

    ctrl._update_world(0.1)
    assert ctrl.run.buffs.score_mult == 2.0
    assert ctrl.run.buffs.double_score_time >= 8.0


def test_controller_powerup_double_coins_applies_multiplier_and_swaps_sprite(ctrl, game_stub):
    ctrl.collectibles._powerups_to_collect = [_PowerUpObj("double_coins")]
    game_stub.ctx.progress.upgrades["double_coins_duration_level"] = 2

    ctrl._update_world(0.1)
    assert ctrl.run.buffs.coins_mult == 2
    assert ctrl.run.buffs.double_coins_time >= 12.0
    assert ctrl.collectibles.set_sprite_calls[-1] is game_stub.ctx.assets.collectibles.coins.double


def test_controller_powerup_shield_calls_player_give_shield(ctrl, game_stub):
    ctrl.collectibles._powerups_to_collect = [_PowerUpObj("shield")]
    game_stub.ctx.progress.upgrades["shield_duration_level"] = 2

    ctrl._update_world(0.1)
    assert game_stub.ctx.player.shield_active is True
    assert game_stub.ctx.player.shield_time == pytest.approx(6.0)


def test_controller_powerup_extra_life_increases_lives_up_to_max(ctrl):
    ctrl.run.max_lives = 3
    ctrl.run.lives = 2

    ctrl.collectibles._powerups_to_collect = [_PowerUpObj("extra_life")]
    ctrl._update_world(0.1)
    assert ctrl.run.lives == 3

    ctrl.collectibles._powerups_to_collect = [_PowerUpObj("extra_life")]
    ctrl._update_world(0.1)
    assert ctrl.run.lives == 3


def test_check_end_conditions_invulnerable_early_return(ctrl, game_stub):
    game_stub.ctx.player.invuln_time = 1.0
    ctrl.run.lives = 1

    ctrl._check_end_conditions()
    assert game_stub.set_screen_calls == []


def test_check_end_conditions_collision_with_shield_consumes_and_removes_obstacle(ctrl, game_stub):
    game_stub.ctx.player.shield_active = True
    obs = SimpleNamespace(
        rect=game_stub.ctx.player.rect.copy(),
        hitbox=game_stub.ctx.player.rect.copy(),
    )
    ctrl.obstacles.obstacles = [obs]
    ctrl.obstacles._first_collision = obs

    ctrl._check_end_conditions()
    assert game_stub.ctx.player.shield_active is False
    assert obs not in ctrl.obstacles.obstacles
    assert game_stub.set_screen_calls == []


def test_check_end_conditions_death_loses_life_and_revives(ctrl, game_stub):
    ctrl.run.lives = 2
    ctrl.run.max_lives = 3

    obs = SimpleNamespace(
        rect=game_stub.ctx.player.rect.copy(),
        hitbox=game_stub.ctx.player.rect.copy(),
    )
    ctrl.obstacles._first_collision = obs

    ctrl._check_end_conditions()
    assert ctrl.run.lives == 1
    assert game_stub.ctx.player.did_respawn is True
    assert game_stub.ctx.player.invuln_set == pytest.approx(ctrl.REVIVE_INVULNERABLE_TIME)
    assert game_stub.set_screen_calls == []


def test_check_end_conditions_last_life_game_over_updates_score_and_bank(ctrl, game_stub):
    ctrl.run.lives = 1
    ctrl.run.collected_coins = 7
    ctrl.run.score = 123.9
    game_stub.ctx.progress.high_score = 10

    game_stub.ctx.player.on_ground = False
    game_stub.ctx.player.rect.bottom = int(GROUND_Y + ctrl.FALL_DEATH_MARGIN + 50)

    ctrl._check_end_conditions()

    assert game_stub.ctx.progress.high_score == 123
    assert game_stub.ctx.progress.coins_bank == 7
    assert game_stub.runtime.temp["final_score"] == 123
    assert game_stub.runtime.temp["coins_collected"] == 7
    assert game_stub.set_screen_calls[-1] == GameState.GAME_OVER


def test_update_difficulty_scales_speed_and_obstacle_chance(ctrl, game_stub):
    ctrl.run.score = 1000.0
    ctrl._update_difficulty()

    assert game_stub.ctx.ground.speed == pytest.approx(BASE_SPEED * 2.5)
    assert game_stub.ctx.ground.obstacle_chance == pytest.approx(0.9)


def test_update_world_spawns_obstacles_from_ground_requests(ctrl, game_stub):
    req1 = SimpleNamespace(x=123.0, flying=False)
    req2 = SimpleNamespace(x=456.0, flying=True)
    game_stub.ctx.ground._update_returns = [req1, req2]

    ctrl._update_world(0.1)
    assert ctrl.obstacles.spawn_calls == [(123.0, False), (456.0, True)]


def test_revive_sets_invulnerable_and_removes_overlapping_obstacles(ctrl, game_stub):
    overlap = SimpleNamespace(rect=game_stub.ctx.player.rect.copy())
    far = SimpleNamespace(rect=game_stub.ctx.player.rect.move(500, 0))
    ctrl.obstacles.obstacles = [overlap, far]

    ctrl._revive()
    assert game_stub.ctx.player.did_respawn is True
    assert game_stub.ctx.player.invuln_set == pytest.approx(ctrl.REVIVE_INVULNERABLE_TIME)
    assert overlap not in ctrl.obstacles.obstacles
    assert far in ctrl.obstacles.obstacles

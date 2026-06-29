# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace

import pygame as pg
import pytest

from main.ui.screens.playing.playing import PlayingScreen


class _CtrlStub:
    def __init__(self):
        self.jump_calls = 0
        self.crouch_calls: list[bool] = []
        self.update_calls: list[float] = []
        self.obstacles = SimpleNamespace(draw=lambda win: None)
        self.collectibles = SimpleNamespace(draw=lambda win: None)
        self.run = SimpleNamespace(
            collected_coins=0,
            lives=3,
            max_lives=3,
            buffs=SimpleNamespace(double_score_time=0.0),
        )

    @property
    def display_score(self):
        return 123

    def on_jump(self):
        self.jump_calls += 1

    def set_crouch(self, crouch: bool):
        self.crouch_calls.append(bool(crouch))

    def update(self, dt: float):
        self.update_calls.append(float(dt))


class _Spy:
    def __init__(self):
        self.draw_calls = 0

    def draw(self, *a, **k):
        self.draw_calls += 1


class _HudSpy:
    def __init__(self):
        self.calls = 0

    def draw(self, win, hud_state):
        _ = (win, hud_state)
        self.calls += 1


@pytest.fixture
def screen_game_stub(surface_factory, monkeypatch):
    game = SimpleNamespace()
    game.ctx = SimpleNamespace()
    game.runtime = SimpleNamespace()

    game.runtime.window = surface_factory((800, 600))

    game.ctx.background = _Spy()
    game.ctx.ground = _Spy()
    game.ctx.player = _Spy()
    game.ctx.hud = _HudSpy()

    import main.ui.screens.playing.playing as screen_mod
    monkeypatch.setattr(screen_mod, "PlayingController", lambda _game: _CtrlStub())

    return game


def test_playing_screen_input_forwards_to_controller(screen_game_stub):
    s = PlayingScreen(screen_game_stub)

    s.handle_events(pg.event.Event(pg.KEYDOWN, {"key": pg.K_UP}))
    assert s.ctrl.jump_calls == 1

    s.handle_events(pg.event.Event(pg.KEYDOWN, {"key": pg.K_DOWN}))
    assert s.ctrl.crouch_calls[-1] is True

    s.handle_events(pg.event.Event(pg.KEYUP, {"key": pg.K_DOWN}))
    assert s.ctrl.crouch_calls[-1] is False


def test_playing_screen_update_calls_controller(screen_game_stub):
    s = PlayingScreen(screen_game_stub)
    s.update(0.25)
    assert s.ctrl.update_calls == [0.25]


def test_playing_screen_draw_draws_world_and_hud(screen_game_stub):
    s = PlayingScreen(screen_game_stub)
    s.draw()

    assert screen_game_stub.ctx.background.draw_calls == 1
    assert screen_game_stub.ctx.ground.draw_calls == 1
    assert screen_game_stub.ctx.player.draw_calls == 1
    assert screen_game_stub.ctx.hud.calls == 1

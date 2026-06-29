# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg

from main.ui.screens.start import StartScreen
from main.core.game_state import GameState
from main.core.constants import BASE_SPEED


def _click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


def test_start_screen_update_moves_backdrop_and_ground(game_stub):
    s = StartScreen(game_stub)

    s.update(0.1)

    assert game_stub.ctx.ground.speed == float(BASE_SPEED)

    # background spy stores (dt, args, kwargs); StartScreen passes speed as positional arg
    assert game_stub.ctx.background.update_calls == [(0.1, (float(BASE_SPEED),), {})]

    assert game_stub.ctx.ground.update_calls == [0.1]


def test_start_screen_draw_populates_buttons(game_stub):
    s = StartScreen(game_stub)
    s.draw()

    assert GameState.PLAYING in s.buttons
    assert GameState.SHOP in s.buttons
    assert GameState.QUIT in s.buttons
    assert all(isinstance(r, pg.Rect) for r in s.buttons.values())


def test_start_screen_click_play_calls_set_screen(game_stub):
    s = StartScreen(game_stub)
    s.draw()

    e = _click(s.buttons[GameState.PLAYING].center)
    s.handle_events(e)

    assert game_stub.set_screen_calls[-1] == GameState.PLAYING


def test_start_screen_click_shop_calls_set_screen(game_stub):
    s = StartScreen(game_stub)
    s.draw()

    e = _click(s.buttons[GameState.SHOP].center)
    s.handle_events(e)

    assert game_stub.set_screen_calls[-1] == GameState.SHOP


def test_start_screen_click_quit_sets_running_false(game_stub):
    s = StartScreen(game_stub)
    s.draw()

    e = _click(s.buttons[GameState.QUIT].center)
    s.handle_events(e)

    assert game_stub.runtime.running is False


def test_start_screen_click_outside_buttons_does_nothing(game_stub):
    s = StartScreen(game_stub)
    s.draw()

    before = list(game_stub.set_screen_calls)
    before_running = game_stub.runtime.running

    s.handle_events(_click((1, 1)))

    assert game_stub.set_screen_calls == before
    assert game_stub.runtime.running == before_running

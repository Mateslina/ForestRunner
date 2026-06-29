# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

from main.ui.screens.game_over import GameOverScreen
from main.core.game_state import GameState


def _click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


@pytest.fixture
def game_over_game_stub(game_stub):
    # do NOT shadow the shared fixture name; just customize it
    game_stub.runtime.temp = {"final_score": 123, "coins_collected": 7}
    game_stub.ctx.progress.high_score = 200
    game_stub.ctx.progress.coins_bank = 999
    return game_stub


def test_game_over_reads_temp_values(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    assert s.final_score == 123
    assert s.run_coins == 7


def test_game_over_missing_temp_defaults_to_zero(game_over_game_stub):
    game_over_game_stub.runtime.temp = None
    s = GameOverScreen(game_over_game_stub)
    assert s.final_score == 0
    assert s.run_coins == 0


def test_game_over_draw_populates_buttons(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    assert GameState.PLAYING in s.buttons
    assert GameState.SHOP in s.buttons
    assert GameState.START in s.buttons
    assert all(isinstance(r, pg.Rect) for r in s.buttons.values())


def test_game_over_click_restart_goes_playing(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    e = _click(s.buttons[GameState.PLAYING].center)
    s.handle_events(e)

    assert game_over_game_stub.set_screen_calls[-1] == GameState.PLAYING


def test_game_over_click_shop_goes_shop(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    e = _click(s.buttons[GameState.SHOP].center)
    s.handle_events(e)

    assert game_over_game_stub.set_screen_calls[-1] == GameState.SHOP


def test_game_over_click_title_goes_start(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    e = _click(s.buttons[GameState.START].center)
    s.handle_events(e)

    assert game_over_game_stub.set_screen_calls[-1] == GameState.START


def test_game_over_click_outside_buttons_does_nothing(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    before = list(game_over_game_stub.set_screen_calls)
    e = _click((1, 1))
    s.handle_events(e)

    assert game_over_game_stub.set_screen_calls == before


def test_game_over_draw_calls_world_draws(game_over_game_stub):
    s = GameOverScreen(game_over_game_stub)
    s.draw()

    assert game_over_game_stub.ctx.background.draw_calls >= 1
    assert game_over_game_stub.ctx.ground.draw_calls >= 1
    assert game_over_game_stub.ctx.player.draw_calls >= 1

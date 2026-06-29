# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace

import pygame as pg
import pytest

from main.core.game_state import GameState
from main.ui.screens.shop.shop import ShopScreen
from tests.helpers.constants import POWERUP_KEYS, UPGRADE_KEYS


def _click(pos):
    return pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": pos})


@pytest.fixture
def shop(game_stub, monkeypatch, surface_factory):
    # progress defaults (use shared keys)
    game_stub.ctx.progress.coins_bank = 200
    game_stub.ctx.progress.upgrades = {k: 0 for k in UPGRADE_KEYS}

    # build minimal assets tree in one shot (avoid getattr chains)
    game_stub.ctx.assets = SimpleNamespace(
        ui=SimpleNamespace(
            shop_background=surface_factory((800, 600)),
        ),
        collectibles=SimpleNamespace(
            coins=SimpleNamespace(
                normal=surface_factory((16, 16)),
            ),
            powerups=SimpleNamespace(
                all={k: surface_factory((32, 32)) for k in POWERUP_KEYS},
            ),
        ),
    )

    monkeypatch.setattr(pg.mouse, "get_pos", lambda: (0, 0))

    return ShopScreen(game_stub)


def test_shop_constructs_logic_items(shop: ShopScreen):
    assert len(shop.logic.items) == 4
    keys = [i.key for i in shop.logic.items]
    assert "shield_duration_level" in keys
    assert "double_coins_duration_level" in keys
    assert "double_score_duration_level" in keys
    assert "max_lives_level" in keys


def test_shop_draw_creates_back_button_and_item_buttons(shop: ShopScreen):
    shop.draw()

    assert shop.back_button is not None
    assert isinstance(shop.back_button, pg.Rect)

    assert len(shop.buttons) == len(shop.logic.items)
    assert all(isinstance(r, pg.Rect) for r in shop.buttons)


def test_shop_click_back_goes_start(shop: ShopScreen):
    shop.draw()

    e = _click(shop.back_button.center)
    shop.handle_events(e)

    assert shop.game.set_screen_calls[-1] == GameState.START


def test_shop_click_item_buys_when_can_buy(shop: ShopScreen):
    shop.game.ctx.progress.coins_bank = 999
    shop.draw()

    item0 = shop.logic.items[0]
    before_lvl = shop.game.ctx.progress.upgrades[item0.key]
    before_coins = shop.game.ctx.progress.coins_bank
    cost = shop.logic.cost(item0)

    e = _click(shop.buttons[0].center)
    shop.handle_events(e)

    assert shop.game.ctx.progress.upgrades[item0.key] == before_lvl + 1
    assert shop.game.ctx.progress.coins_bank == before_coins - cost


def test_shop_click_item_does_not_buy_when_insufficient(shop: ShopScreen):
    shop.game.ctx.progress.coins_bank = 0
    shop.draw()

    item0 = shop.logic.items[0]
    before_lvl = shop.game.ctx.progress.upgrades[item0.key]

    e = _click(shop.buttons[0].center)
    shop.handle_events(e)

    assert shop.game.ctx.progress.upgrades[item0.key] == before_lvl


def test_shop_click_when_back_button_not_drawn_does_not_crash(shop: ShopScreen):
    # Regression: handle_events must handle back_button=None
    e = _click((10, 10))
    shop.handle_events(e)

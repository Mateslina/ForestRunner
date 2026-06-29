# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg

from main.core.game_state import GameState
from main.ui.ui_helpers import (
    clicked_button,
    draw_bank_coins_top_right,
    draw_top_right_icon_amount,
    layout_button_group,
    make_button_drawer,
)

# ----------------------------
# layout_button_group
# ----------------------------


def test_layout_button_group_creates_rects_for_all_keys():
    rects = layout_button_group(
        w=800,
        h=600,
        keys=[GameState.PLAYING, GameState.SHOP, GameState.START],
    )

    assert set(rects.keys()) == {GameState.PLAYING, GameState.SHOP, GameState.START}
    assert all(isinstance(r, pg.Rect) for r in rects.values())


def test_layout_button_group_vertical_spacing_is_monotonic():
    rects = layout_button_group(
        w=800,
        h=600,
        keys=[GameState.PLAYING, GameState.SHOP, GameState.START],
    )
    ys = [rects[k].y for k in [GameState.PLAYING, GameState.SHOP, GameState.START]]
    assert ys[0] < ys[1] < ys[2]


def test_layout_button_group_is_centered_horizontally():
    rects = layout_button_group(
        w=800,
        h=600,
        keys=[GameState.PLAYING],
    )
    r = rects[GameState.PLAYING]
    assert r.centerx == 800 // 2


# ----------------------------
# clicked_button
# ----------------------------

def test_clicked_button_returns_key_on_left_click_inside_rect():
    rect = pg.Rect(10, 10, 100, 40)
    buttons = {GameState.PLAYING: rect}

    e = pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": rect.center})
    assert clicked_button(e, buttons) == GameState.PLAYING


def test_clicked_button_returns_none_on_left_click_outside_rect():
    rect = pg.Rect(10, 10, 100, 40)
    buttons = {GameState.PLAYING: rect}

    e = pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 1, "pos": (0, 0)})
    assert clicked_button(e, buttons) is None


def test_clicked_button_ignores_non_left_click():
    rect = pg.Rect(10, 10, 100, 40)
    buttons = {GameState.PLAYING: rect}

    e = pg.event.Event(pg.MOUSEBUTTONDOWN, {"button": 3, "pos": rect.center})
    assert clicked_button(e, buttons) is None


def test_clicked_button_ignores_non_mousebuttondown_event():
    rect = pg.Rect(10, 10, 100, 40)
    buttons = {GameState.PLAYING: rect}

    e = pg.event.Event(pg.KEYDOWN, {"key": pg.K_RETURN})
    assert clicked_button(e, buttons) is None


# ----------------------------
# make_button_drawer (smoke)
# ----------------------------

def test_make_button_drawer_runs_without_crash(monkeypatch, surface_factory, headless_pygame):
    _ = headless_pygame  # ensure pg.font.SysFont is safe in CI/headless

    win = surface_factory((200, 100))
    font = pg.font.SysFont(None, 24)

    monkeypatch.setattr(pg.mouse, "get_pos", lambda: (0, 0))

    draw_btn = make_button_drawer(win, font)
    rect = pg.Rect(10, 10, 100, 40)

    draw_btn(rect, "OK", hovered=False)
    draw_btn(rect, "OK", hovered=True)


# ----------------------------
# draw_top_right_icon_amount (smoke)
# ----------------------------

def test_draw_top_right_icon_amount_runs_without_crash(surface_factory):
    win = surface_factory((300, 200))
    icon = surface_factory((40, 40))
    amount = surface_factory((60, 20))

    draw_top_right_icon_amount(win, window_w=300, icon=icon, amount_surf=amount)


# ----------------------------
# draw_bank_coins_top_right (cache behavior)
# ----------------------------

def test_draw_bank_coins_top_right_populates_cache(surface_factory, headless_pygame):
    _ = headless_pygame  # ensures font operations won't crash headless

    win = surface_factory((800, 600))
    base_coin = surface_factory((20, 20))
    cache: dict = {}

    draw_bank_coins_top_right(win=win, window_w=800, coins_bank=123, base_coin=base_coin, cache=cache)

    assert "coin_sprite" in cache
    assert "coin_size" in cache
    assert "amount_font" in cache
    assert isinstance(cache["coin_sprite"], pg.Surface)


def test_draw_bank_coins_top_right_reuses_cached_font(surface_factory, headless_pygame):
    _ = headless_pygame

    win = surface_factory((800, 600))
    base_coin = surface_factory((20, 20))
    cache: dict = {}

    draw_bank_coins_top_right(win=win, window_w=800, coins_bank=1, base_coin=base_coin, cache=cache)
    font1 = cache["amount_font"]

    draw_bank_coins_top_right(win=win, window_w=800, coins_bank=2, base_coin=base_coin, cache=cache)
    font2 = cache["amount_font"]

    assert font1 is font2


def test_draw_bank_coins_top_right_rebuilds_sprite_if_base_coin_size_changes(surface_factory, headless_pygame):
    _ = headless_pygame

    win = surface_factory((800, 600))
    cache: dict = {}

    coin_a = surface_factory((20, 20))
    draw_bank_coins_top_right(win=win, window_w=800, coins_bank=1, base_coin=coin_a, cache=cache)
    sprite1 = cache["coin_sprite"]
    size1 = cache["coin_size"]

    coin_b = surface_factory((40, 40))
    draw_bank_coins_top_right(win=win, window_w=800, coins_bank=1, base_coin=coin_b, cache=cache)
    sprite2 = cache["coin_sprite"]
    size2 = cache["coin_size"]

    assert size2 != size1
    assert sprite2 is not sprite1

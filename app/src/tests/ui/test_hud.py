# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

from main.ui.hud import HUD, HudState
from main.ui.ui_helpers import WHITE, YELLOW


class FontStub:
    def __init__(self, h: int = 24):
        self._h = int(h)

    def get_height(self) -> int:
        return self._h

    def render(self, text, aa, color):
        _ = aa
        _ = color
        w = max(1, 10 * len(str(text)))
        return pg.Surface((w, self._h), pg.SRCALPHA)


@pytest.fixture
def hud(fake_collectible_assets):
    return HUD(FontStub(18), FontStub(36), fake_collectible_assets)


def test_hud_scales_hearts_once_and_creates_empty_alpha(hud: HUD):
    assert hud._heart_full.get_size() == (HUD.ICON_SIZE, HUD.ICON_SIZE)
    assert hud._heart_empty.get_size() == (HUD.ICON_SIZE, HUD.ICON_SIZE)
    assert hud._heart_empty.get_alpha() == 60


def test_score_color_white_when_no_buff(hud: HUD):
    c = hud._score_color(0.0)
    assert tuple(c) == tuple(WHITE)


def test_score_color_yellow_when_buff_active_more_than_one_second(hud: HUD):
    c = hud._score_color(2.0)
    assert tuple(c) == tuple(YELLOW)


def test_score_color_flickers_in_last_second(monkeypatch, hud: HUD):
    monkeypatch.setattr(pg.time, "get_ticks", lambda: 0)
    c0 = hud._score_color(0.5)

    monkeypatch.setattr(pg.time, "get_ticks", lambda: 100)
    c1 = hud._score_color(0.5)

    assert tuple(c0) != tuple(c1)


def test_draw_runs_and_does_not_crash(monkeypatch, hud: HUD, surface_factory):
    win = surface_factory((800, 600))
    monkeypatch.setattr(pg.time, "get_ticks", lambda: 0)

    hud.draw(
        win,
        HudState(
            score=123,
            collected_coins=45,
            lives=2,
            max_lives=4,
            double_score_time=0.0,
        ),
    )

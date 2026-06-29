# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

from main.entities.player.effects import draw_shield_glow, sprite_visible_during_invuln
from tests.helpers.fakes import BlitSpy


def test_sprite_visible_during_invuln_returns_true_when_not_invulnerable(monkeypatch):
    monkeypatch.setattr(pg.time, "get_ticks", lambda: 0)
    assert sprite_visible_during_invuln(invulnerable=False) is True


@pytest.mark.parametrize(
    "ticks, blink_ms, expected",
    [
        (0, 100, False),     # 0//100 = 0 -> even -> hidden
        (99, 100, False),    # still 0 -> hidden
        (100, 100, True),    # 1 -> visible
        (199, 100, True),    # still 1 -> visible
        (200, 100, False),   # 2 -> hidden
        (250, 50, True),     # 250//50 = 5 -> odd -> visible
    ],
)
def test_sprite_visible_during_invuln_blinks_by_ticks(monkeypatch, ticks, blink_ms, expected):
    monkeypatch.setattr(pg.time, "get_ticks", lambda: ticks)
    assert sprite_visible_during_invuln(invulnerable=True, blink_ms=blink_ms) is expected


def test_draw_shield_glow_blits_without_crash(surface_factory, rect_factory):
    screen = surface_factory((320, 200))
    rect = rect_factory(100, 60, 40, 60)

    draw_shield_glow(screen, rect, offset=0)


def test_draw_shield_glow_uses_offset(rect_factory):
    screen = BlitSpy(size=(320, 200))
    rect = rect_factory(100, 60, 40, 60)

    draw_shield_glow(screen, rect, offset=10)

    assert len(screen.calls) == 1
    glow_surf, (x0, y0) = screen.calls[0]

    assert isinstance(glow_surf, pg.Surface)
    assert isinstance(x0, int)
    assert isinstance(y0, int)

    radius = int(max(rect.width, rect.height) * 0.75)  # 45
    cx = rect.centerx  # 120
    cy = rect.centery + 10  # 100
    assert (x0, y0) == (cx - radius, cy - radius)

    assert glow_surf.get_size() == (radius * 2, radius * 2)

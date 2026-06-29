# @generated [all] ChatGPT : generate tests based on class implementation
from dataclasses import dataclass
from typing import Protocol, Tuple

import pygame as pg

from tests.helpers.fakes import BlitSpy


class _HasSpriteRectXY(Protocol):
    x: float
    y: float
    sprite: pg.Surface
    rect: pg.Rect

    def update(self, dt: float, speed: float) -> None:
        ...

    def draw(self, screen) -> None:
        ...


@dataclass(frozen=True)
class InitSpec:
    x: float
    y: float
    size: Tuple[int, int]


def assert_collectible_init(entity: _HasSpriteRectXY, sprite: pg.Surface, spec: InitSpec) -> None:
    assert entity.x == spec.x
    assert entity.y == spec.y
    assert entity.sprite is sprite
    assert entity.rect.topleft == (int(spec.x), int(spec.y))
    assert entity.rect.size == spec.size


def assert_collectible_update_moves_left(
    entity: _HasSpriteRectXY,
    *,
    dt: float,
    speed: float,
    expected_x: float,
    expected_y: float,
) -> None:
    entity.update(dt=dt, speed=speed)
    assert entity.x == expected_x
    assert entity.rect.x == int(expected_x)
    assert entity.rect.y == int(expected_y)


def assert_collectible_draw_blits(entity: _HasSpriteRectXY, sprite: pg.Surface) -> None:
    screen = BlitSpy()
    entity.draw(screen)

    assert screen.calls
    src, dest = screen.calls[-1]
    assert src is sprite
    assert dest == entity.rect.topleft

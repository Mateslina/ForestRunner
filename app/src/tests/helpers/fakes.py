# @generated [all] ChatGPT : generate tests based on class implementation
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pygame as pg


# ----------------------------
# generic spies (UI/world)
# ----------------------------

class UpdateSpy:
    def __init__(self):
        self.update_calls: list[tuple[float, tuple[Any, ...], dict[str, Any]]] = []
        self.draw_calls = 0

    def update(self, dt: float, *args, **kwargs):
        self.update_calls.append((float(dt), tuple(args), dict(kwargs)))

    def draw(self, *a, **k):
        self.draw_calls += 1


class GroundSpy:
    def __init__(self):
        self.speed = 0.0
        self.reset_calls: list[float] = []
        self.update_calls: list[float] = []
        self.draw_calls = 0
        self.obstacle_chance = 0.0  # some code reads it
        self._update_returns: list[Any] = []  # optional: spawn requests

    def reset(self, speed: float):
        self.speed = float(speed)
        self.reset_calls.append(float(speed))

    def update(self, dt: float):
        self.update_calls.append(float(dt))
        return list(self._update_returns)

    def draw(self, *a, **k):
        self.draw_calls += 1

    def is_solid_at_x(self, *a, **k):
        return True


class PlayerSpy:
    """
    Spy that matches what PlayingController tests expect (based on your failing attrs),
    while still being usable as a generic Player double.
    """

    def __init__(self, *, rect: pg.Rect | None = None):
        self.draw_calls = 0
        self.update_calls: list[tuple[tuple, dict]] = []

        self.rect = rect.copy() if rect is not None else pg.Rect(0, 0, 40, 60)

        self.on_ground = True

        self.invuln_time = 0.0
        self.invuln_set: float | None = None
        self.set_invulnerable_calls: list[float] = []

        self.crouch_calls: list[bool] = []

        self.shield_active = False
        self.shield_time = 0.0
        self.give_shield_calls: list[float] = []
        self.consume_shield_calls = 0

        self.jump_calls = 0

        self.respawn_calls = 0
        self.did_respawn = False

    def update(self, *a, **k):
        self.update_calls.append((a, k))

    def draw(self, *a, **k):
        self.draw_calls += 1

    def jump(self):
        self.jump_calls += 1

    def set_crouch(self, crouch: bool):
        self.crouch_calls.append(bool(crouch))

    def give_shield(self, duration: float):
        self.shield_active = True
        self.shield_time = float(duration)
        self.give_shield_calls.append(float(duration))

    def consume_shield(self):
        self.consume_shield_calls += 1
        self.shield_active = False
        self.shield_time = 0.0

    def respawn(self):
        self.respawn_calls += 1
        self.did_respawn = True
        self.on_ground = True

    def set_invulnerable(self, duration: float):
        d = float(duration)
        self.invuln_time = max(self.invuln_time, d)
        self.invuln_set = d
        self.set_invulnerable_calls.append(d)

    @property
    def invulnerable(self) -> bool:
        return self.invuln_time > 0.0


class HudSpy:
    def __init__(self):
        self.draw_calls: list[Any] = []

    def draw(self, win, hud_state):
        _ = win
        self.draw_calls.append(hud_state)


# ----------------------------
# collectibles fakes
# ----------------------------

@dataclass(frozen=True)
class SpawnPointFake:
    x: float
    y: float


class SpawnerReturning:
    def __init__(self, pt: SpawnPointFake):
        self.pt = pt

    def pick_spawn_point(self, item_w, item_h, ground, obstacles):
        _ = (item_w, item_h, ground, obstacles)
        return self.pt


class GroundFake:
    pass


class ObstaclesFake:
    pass


class GroundWithSegmentsFake:
    def __init__(self, segs):
        self._segs = list(segs)

    def get_segments(self):
        return list(self._segs)

    def is_solid_at_x(self, x1, x2, min_overlap=1.0):
        for sx, w in self._segs:
            overlap = min(x2, sx + w) - max(x1, sx)
            if overlap >= min_overlap:
                return True
        return False


@dataclass
class ObstacleStateFake:
    flying: bool


class ObstacleFake:
    def __init__(self, x, y, w, h, flying=False):
        self.rect = pg.Rect(x, y, w, h)
        self.state = ObstacleStateFake(flying=bool(flying))


# ----------------------------
# Game stub (UI screens)
# ----------------------------

class GameStub:
    """
    Shared UI Game stub.

    Uses surface_factory so we don't duplicate pg init / SDL dummy init.
    Fonts use pg.font.SysFont -> guarded by headless_pygame fixture in tests.
    """

    def __init__(
        self,
        surface_factory,
        *,
        font_small=None,
        font_big=None,
        player_frames=None,
    ):
        self.set_screen_calls: list[Any] = []

        self.runtime = SimpleNamespace(
            window=surface_factory((800, 600)),
            running=True,
            temp=None,
        )

        if font_small is None:
            font_small = pg.font.SysFont(None, 24)
        if font_big is None:
            font_big = pg.font.SysFont(None, 48)

        if player_frames is None:
            player_frames = SimpleNamespace(
                run_frames=[surface_factory((40, 60)), surface_factory((40, 60))],
                crouch_frames=[surface_factory((40, 30)), surface_factory((40, 30))],
            )

        assets = SimpleNamespace(
            ui=SimpleNamespace(
                title_sign=surface_factory((420, 160)),
                shop_background=surface_factory((800, 600)),
            ),
            collectibles=SimpleNamespace(
                coins=SimpleNamespace(
                    normal=surface_factory((32, 32)),
                    double=surface_factory((48, 32)),
                ),
                powerups=SimpleNamespace(
                    all={
                        "shield": surface_factory((32, 32)),
                        "double_score": surface_factory((32, 32)),
                        "double_coins": surface_factory((32, 32)),
                        "extra_life": surface_factory((32, 32)),
                    }
                ),
            ),
            obstacles=SimpleNamespace(
                rock_tiles=[surface_factory((32, 32))],
                bird_frames=[surface_factory((32, 32)), surface_factory((32, 32))],
            ),
            player=player_frames,
            ground=SimpleNamespace(
                fill_mid=surface_factory((32, 32)),
            ),
        )

        self.ctx = SimpleNamespace(
            assets=assets,
            fonts=SimpleNamespace(small=font_small, big=font_big),
            progress=SimpleNamespace(coins_bank=0, upgrades={}, high_score=0),
            background=UpdateSpy(),
            ground=GroundSpy(),
            player=PlayerSpy(),
            hud=HudSpy(),
        )

    def set_screen(self, state):
        self.set_screen_calls.append(state)


class BlitSpy:
    def __init__(self, size=(800, 600)):
        self._size = size
        self.calls = []  # (source, dest)

    def get_size(self):
        return self._size

    def blit(self, source, dest):
        self.calls.append((source, dest))


class GroundSolidSpy:
    """
    Spy for ground solidity queries.
    """

    def __init__(self, *, solid: bool = True, speed: float = 300.0):
        self.solid = bool(solid)
        self.speed = float(speed)
        self.calls: list[tuple[float, float, float]] = []

    def is_solid_at_x(self, x1, x2, min_overlap: float = 1.0) -> bool:
        self.calls.append((float(x1), float(x2), float(min_overlap)))
        return self.solid

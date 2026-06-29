from pathlib import Path
from types import SimpleNamespace

import pygame as pg
import pytest

from main.core.assets.tileset_atlas import GroundTiles
from tests.helpers.constants import POWERUP_KEYS, UPGRADE_KEYS


@pytest.fixture(scope="session", autouse=True)
def _pygame_init():
    if not pg.get_init():
        pg.init()
    if not pg.font.get_init():
        pg.font.init()


def surf(size=(1, 1)) -> pg.Surface:
    """Small helper to create an alpha Surface."""
    return pg.Surface(size, pg.SRCALPHA)


@pytest.fixture
def surface_factory():
    return surf


@pytest.fixture
def fake_ground_tiles(surface_factory):
    def mk():
        return surface_factory((1, 1))

    return GroundTiles(
        top_left=mk(),
        top_mid=mk(),
        top_right=mk(),
        fill_mid=mk(),
        fill_left=mk(),
        fill_right=mk(),
    )


@pytest.fixture
def fake_atlas(surface_factory, fake_ground_tiles):
    return SimpleNamespace(
        ground=fake_ground_tiles,
        rock_tiles=[surface_factory((2, 2))],
        tree_sprites=[surface_factory((3, 3))],
        coin_base=surface_factory((4, 4)),
        heart_base=surface_factory((5, 5)),
    )


class Capture(dict):
    """Dict with a tiny convenience setter."""

    def set(self, key, value):
        self[key] = value
        return value


# used for capturing side-effects to assert later
@pytest.fixture
def capture():
    return Capture()


@pytest.fixture
def patch_assets_dir(monkeypatch):
    """Standardize ASSETS_DIR to a deterministic path."""
    from main.core.assets import assets_loader

    monkeypatch.setattr(assets_loader, "ASSETS_DIR", Path("/tmp/assets"))
    return Path("/tmp/assets")


@pytest.fixture
def patch_pg_image_load(monkeypatch, capture):
    """Patch pg.image.load and record last path."""
    import main.core.assets.assets_loader as loader_mod

    class FakeLoaded:
        def __init__(self, out: pg.Surface):
            self._out = out

        def convert_alpha(self):
            capture["convert_alpha_called"] = True
            return self._out

    def _patch(return_surface: pg.Surface):
        def fake_load(path):
            capture["path"] = path
            return FakeLoaded(return_surface)

        monkeypatch.setattr(loader_mod.pg.image, "load", fake_load)

    return _patch


@pytest.fixture
def headless_pygame(monkeypatch):
    # make display/font operations safe in CI/headless
    monkeypatch.setattr(pg.display, "set_caption", lambda *a, **k: None)
    monkeypatch.setattr(pg.display, "flip", lambda *a, **k: None)
    monkeypatch.setattr(pg, "quit", lambda *a, **k: None)
    monkeypatch.setattr(pg.event, "get", lambda: [])


@pytest.fixture
def save_file(tmp_path: Path) -> Path:
    return tmp_path / "save.json"


@pytest.fixture
def fake_collectible_assets(surface_factory):
    coins = SimpleNamespace(
        normal=surface_factory((10, 10)),
        double=surface_factory((15, 10)),
    )

    powerups_all = {k: surface_factory((8, 8)) for k in POWERUP_KEYS}

    return SimpleNamespace(
        collectibles=SimpleNamespace(
            coins=coins,
            powerups=SimpleNamespace(all=powerups_all),
        )
    )


# ---------------- shared factories (dedupe) ----------------


@pytest.fixture
def upgrades_factory():
    """
    Create a progress.upgrades dict with all required keys.
    Usage: upgrades_factory(max_lives_level=2)
    """
    def _make(**overrides: int) -> dict[str, int]:
        base = {k: 0 for k in UPGRADE_KEYS}
        base.update(overrides)
        return base

    return _make


@pytest.fixture
def save_data_factory(upgrades_factory):
    """
    Create a save-data dict in one place (for save/load tests).
    Usage: save_data_factory(coins_bank=200, high_score=123)
    """
    def _make(**overrides):
        base = {
            "coins_bank": 0,
            "high_score": 0,
            "upgrades": upgrades_factory(),
        }
        base.update(overrides)
        return base

    return _make


# ---------------- shared rect fixtures ----------------


@pytest.fixture
def rect_factory():
    """
    Factory fixture for creating pygame.Rects consistently.
    Usage:
        rect_factory(10, 20, 30, 40)
        rect_factory(pos=(10, 20), size=(30, 40))
    """
    def _make(
        x: int | None = None,
        y: int | None = None,
        w: int | None = None,
        h: int | None = None,
        *,
        pos: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
    ) -> pg.Rect:
        if pos is not None:
            x, y = pos
        if size is not None:
            w, h = size
        if x is None or y is None or w is None or h is None:
            raise ValueError("rect_factory requires x,y,w,h or pos=(x,y) and size=(w,h)")
        return pg.Rect(int(x), int(y), int(w), int(h))

    return _make


@pytest.fixture
def rects(rect_factory):
    """
    Common rects that tend to repeat in tests.
    Keep this minimal; add more only when you see real duplication.
    """
    return {
        "origin_1x1": rect_factory(0, 0, 1, 1),
        "origin_10x10": rect_factory(0, 0, 10, 10),
        "origin_12x12": rect_factory(0, 0, 12, 12),
        "at_10_20_12x8": rect_factory(10, 20, 12, 8),
    }


@pytest.fixture
def game_stub(surface_factory, headless_pygame):
    _ = headless_pygame  # ensure pg.font.SysFont is safe
    from tests.helpers.fakes import GameStub
    return GameStub(surface_factory)


@pytest.fixture
def player_frames_40x60_40x30(surface_factory):
    """Common player sprites used across tests (dedupe for pylint R0801)."""
    return SimpleNamespace(
        run_frames=[surface_factory((40, 60)), surface_factory((40, 60))],
        crouch_frames=[surface_factory((40, 30)), surface_factory((40, 30))],
    )

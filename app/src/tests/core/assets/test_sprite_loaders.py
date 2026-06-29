# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

import main.core.assets.sprite_loaders as sl
from main.core.assets.models import CoinSprites, PlayerSprites


def _load_from_mapping(mapping: dict[str, pg.Surface]):
    def fake_load_image(name: str) -> pg.Surface:
        return mapping[name]
    return fake_load_image


def test__scale_to_clamps_to_at_least_1px(surface_factory):
    base = surface_factory((10, 10))

    out = sl._scale_to(base, 0, 0)  # pylint: disable=protected-access
    assert isinstance(out, pg.Surface)
    assert out.get_size() == (1, 1)

    out2 = sl._scale_to(base, -100, 2)  # pylint: disable=protected-access
    assert out2.get_size() == (1, 2)


def test__scale_to_powerup_size_uses_constant(surface_factory):
    base = surface_factory((10, 10))

    out = sl._scale_to_powerup_size(base)  # pylint: disable=protected-access
    expected = int(sl.COIN_SIZE_PX * sl.POWERUP_TO_COIN)
    assert out.get_size() == (expected, expected)


def test_load_coin_sprites_builds_expected_sizes_and_loads_double(monkeypatch, surface_factory, capture):
    coin_base = surface_factory((10, 10))

    def fake_load_image(name: str) -> pg.Surface:
        capture["name"] = name
        return surface_factory((20, 20))

    monkeypatch.setattr(sl, "load_image", fake_load_image)

    expected_cw = int(coin_base.get_width() * 3.0)
    expected_ch = int(coin_base.get_height() * 3.0)

    out = sl.load_coin_sprites(coin_base)

    assert isinstance(out, CoinSprites)
    assert capture["name"] == "collectibles/double_coin.png"
    assert out.normal.get_size() == (expected_cw, expected_ch)
    assert out.double.get_size() == (int(expected_cw * 1.5), expected_ch)


def test_load_bird_frames_splits_flips_and_scales(monkeypatch, surface_factory):
    bird_sheet = surface_factory((600, 100))
    monkeypatch.setattr(sl, "load_image", lambda name: bird_sheet)

    out = sl.load_bird_frames()

    assert isinstance(out, list)
    assert len(out) == 2
    assert all(isinstance(x, pg.Surface) for x in out)
    assert out[0].get_size() == (45, 15)
    assert out[1].get_size() == (45, 15)


def test_load_player_frames_scales_run_and_crouch(monkeypatch, surface_factory):
    run1 = surface_factory((300, 150))
    run2 = surface_factory((300, 150))
    crouch1 = surface_factory((300, 150))
    crouch2 = surface_factory((300, 150))

    monkeypatch.setattr(
        sl,
        "load_image",
        _load_from_mapping(
            {
                "player/run1.png": run1,
                "player/run2.png": run2,
                "player/crouch1.png": crouch1,
                "player/crouch2.png": crouch2,
            }
        ),
    )

    out = sl.load_player_frames()

    assert isinstance(out, PlayerSprites)
    assert len(out.run_frames) == 2
    assert len(out.crouch_frames) == 2
    assert out.run_frames[0].get_size() == (100, 50)
    assert out.run_frames[1].get_size() == (100, 50)
    assert out.crouch_frames[0].get_size() == (100, 30)
    assert out.crouch_frames[1].get_size() == (100, 30)
    assert out.stand_size == (100, 50)
    assert out.crouch_size == (100, 30)


@pytest.mark.parametrize(
    "key, path",
    [
        ("shield", "collectibles/shield.png"),
        ("double_coins", "collectibles/double_coins.png"),
        ("double_score", "collectibles/double_score.png"),
    ],
)
def test_load_powerups_loads_expected_paths_and_scales(monkeypatch, surface_factory, key, path):
    loaded: list[str] = []

    def fake_load_image(name: str) -> pg.Surface:
        loaded.append(name)
        return surface_factory((10, 10))

    monkeypatch.setattr(sl, "load_image", fake_load_image)

    extra = surface_factory((20, 20))
    out = sl.load_powerups(extra_life_sprite=extra)

    expected_size = int(sl.COIN_SIZE_PX * sl.POWERUP_TO_COIN)

    assert path in loaded
    assert key in out
    assert out[key].get_size() == (expected_size, expected_size)

    assert "extra_life" in out
    assert out["extra_life"].get_size() == (expected_size, expected_size)


def test_load_shop_background_uses_expected_path(monkeypatch, surface_factory, capture):
    def fake_load_image(name: str) -> pg.Surface:
        capture["name"] = name
        return surface_factory((1, 1))

    monkeypatch.setattr(sl, "load_image", fake_load_image)

    out = sl.load_shop_background()

    assert isinstance(out, pg.Surface)
    assert capture["name"] == "background/shop-16by9.png"


def test_load_title_sign_scales_by_half(monkeypatch, surface_factory):
    base = surface_factory((200, 100))
    monkeypatch.setattr(sl, "load_image", lambda name: base)

    out = sl.load_title_sign()

    assert isinstance(out, pg.Surface)
    assert out.get_size() == (100, 50)

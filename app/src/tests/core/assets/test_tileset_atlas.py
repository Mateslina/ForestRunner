# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

from main.core.assets.tileset_atlas import build_tileset_atlas, sub_tileset, scale_sprites


def test_sub_tileset_returns_surface_of_rect_size(surface_factory):
    tileset = surface_factory((200, 200))
    rect = pg.Rect(10, 20, 32, 48)

    out = sub_tileset(tileset, rect)

    assert isinstance(out, pg.Surface)
    assert out.get_size() == (32, 48)


@pytest.mark.parametrize(
    "src_size, scale, expected",
    [
        ((10, 10), 1.0, (10, 10)),
        ((10, 10), 2.0, (20, 20)),
        ((40, 20), 0.5, (20, 10)),
    ],
)
def test_scale_sprites_scales_all_sprites(surface_factory, src_size, scale, expected):
    sprites = [surface_factory(src_size), surface_factory(src_size)]

    out = scale_sprites(sprites, scale)

    assert isinstance(out, list)
    assert len(out) == len(sprites)
    assert all(isinstance(s, pg.Surface) for s in out)
    assert all(s.get_size() == expected for s in out)


def test_build_tileset_atlas_shapes_and_counts(surface_factory):
    ts = 32
    tileset = surface_factory((20 * ts, 20 * ts))

    atlas = build_tileset_atlas(tileset, tile_size=ts, tree_scale=2.5, rock_scale=3.0)

    assert atlas.ground.top_left.get_size() == (ts, ts)
    assert atlas.ground.top_mid.get_size() == (ts, ts)
    assert atlas.ground.top_right.get_size() == (ts, ts)
    assert atlas.ground.fill_mid.get_size() == (ts, ts)
    assert atlas.ground.fill_left.get_size() == (ts, ts)
    assert atlas.ground.fill_right.get_size() == (ts, ts)

    assert len(atlas.rock_tiles) == 4
    assert all(t.get_size() == (int(ts * 3.0), int(ts * 3.0)) for t in atlas.rock_tiles)

    assert atlas.coin_base.get_size() == (ts, ts)
    assert atlas.heart_base.get_size() == (ts, ts)

    assert len(atlas.tree_sprites) == 4
    assert atlas.tree_sprites[0].get_size() == (int(4 * ts * 2.5), int(6 * ts * 2.5))

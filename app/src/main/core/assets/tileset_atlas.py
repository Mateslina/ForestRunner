"""
Tileset atlas construction.

This module provides helpers for slicing a tileset image into individual
sprites and grouping them into a structured atlas used by the game.
"""

from dataclasses import dataclass
import pygame as pg


@dataclass(frozen=True)
class GroundTiles:
    """Container for ground tile sprites extracted from the tileset."""

    top_left: pg.Surface
    top_mid: pg.Surface
    top_right: pg.Surface
    fill_mid: pg.Surface
    fill_left: pg.Surface
    fill_right: pg.Surface


@dataclass(frozen=True)
class TilesetAtlas:
    """Grouped sprites extracted from a tileset image."""

    ground: GroundTiles
    rock_tiles: list[pg.Surface]
    tree_sprites: list[pg.Surface]
    coin_base: pg.Surface
    heart_base: pg.Surface


def sub_tileset(tileset: pg.Surface, rect: pg.Rect) -> pg.Surface:
    """Return a subsurface of the tileset defined by the given rectangle."""
    return tileset.subsurface(rect)


def scale_sprites(sprites: list[pg.Surface], scale: float) -> list[pg.Surface]:
    """Scale all sprites by a fixed factor."""
    out: list[pg.Surface] = []
    for s in sprites:
        w = int(s.get_width() * scale)
        h = int(s.get_height() * scale)
        out.append(pg.transform.smoothscale(s, (w, h)))
    return out


def build_tileset_atlas(
    tileset: pg.Surface,
    tile_size: int = 32,
    tree_scale: float = 2.5,
    rock_scale: float = 3.0,
) -> TilesetAtlas:
    """
    Build a tileset atlas from a tileset surface.

    Splits the tileset into ground tiles, rocks, trees, and sprites
    for collectibles, and returns them grouped in a TilesetAtlas.
    """
    ts = tile_size

    ground = GroundTiles(
        top_left=sub_tileset(tileset, pg.Rect(0 * ts, 1 * ts, ts, ts)),
        top_mid=sub_tileset(tileset, pg.Rect(1 * ts, 0 * ts, ts, ts)),
        top_right=sub_tileset(tileset, pg.Rect(1 * ts, 1 * ts, ts, ts)),
        fill_mid=sub_tileset(tileset, pg.Rect(0 * ts, 0 * ts, ts, ts)),
        fill_left=sub_tileset(tileset, pg.Rect(2 * ts, 0 * ts, ts, ts)),
        fill_right=sub_tileset(tileset, pg.Rect(3 * ts, 0 * ts, ts, ts)),
    )

    rock_rects = [
        pg.Rect(7 * ts, 0 * ts, ts, ts),
        pg.Rect(6 * ts, 1 * ts, ts, ts),
        pg.Rect(9 * ts, 1 * ts, ts, ts),
        pg.Rect(9 * ts, 2 * ts, ts, ts),
    ]
    rock_tiles_raw = [sub_tileset(tileset, r) for r in rock_rects]
    rock_tiles = scale_sprites(rock_tiles_raw, rock_scale)

    tree_rects = [
        pg.Rect(0 * ts, 4 * ts, 4 * ts, 6 * ts),
        pg.Rect(4 * ts, 5 * ts, 4 * ts, 5 * ts),
        pg.Rect(8 * ts, 4 * ts, 5 * ts, 6 * ts),
        pg.Rect(13 * ts, 5 * ts, 4 * ts, 5 * ts),
    ]
    tree_raw = [sub_tileset(tileset, r) for r in tree_rects]
    tree_sprites = scale_sprites(tree_raw, tree_scale)

    coin_base = sub_tileset(tileset, pg.Rect(7 * ts, 3 * ts, ts, ts))
    heart_base = sub_tileset(tileset, pg.Rect(6 * ts, 4 * ts, ts, ts))

    return TilesetAtlas(
        ground=ground,
        rock_tiles=rock_tiles,
        tree_sprites=tree_sprites,
        coin_base=coin_base,
        heart_base=heart_base,
    )

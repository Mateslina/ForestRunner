"""
Asset container for the game.

Loads all image/sprite assets once and exposes them via small, grouped dataclasses.
"""

from main.core.assets.assets_loader import load_image
from main.core.assets.models import (
    ObstacleSprites,
    CollectibleSprites,
    PowerupSprites,
    UIAssets,
)
from main.core.assets.tileset_atlas import build_tileset_atlas, GroundTiles
from main.core.assets.sprite_loaders import (
    load_coin_sprites,
    load_bird_frames,
    load_player_frames,
    load_powerups,
    load_shop_background,
    load_title_sign,
)


class Assets:  # pylint: disable=too-few-public-methods
    """Loads and stores all game assets once and shares them across the game."""

    TILE_SIZE = 32

    def __init__(self) -> None:
        tileset = load_image("tileset.png")
        atlas = build_tileset_atlas(tileset, tile_size=self.TILE_SIZE)

        # expose ground tiles + trees
        self.ground: GroundTiles = atlas.ground
        self.tree_sprites = list(atlas.tree_sprites)

        # obstacles
        self.obstacles = ObstacleSprites(
            rock_tiles=atlas.rock_tiles,
            bird_frames=load_bird_frames(),
        )

        # coins (normal + double)
        self.collectibles = CollectibleSprites(
            coins=load_coin_sprites(atlas.coin_base),
            powerups=PowerupSprites(
                all=dict(load_powerups(extra_life_sprite=atlas.heart_base)),
            ),
        )

        # player frames
        self.player = load_player_frames()

        # ui
        self.ui = UIAssets(
            shop_background=load_shop_background(),
            title_sign=load_title_sign(),
        )

# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace


from main.core.assets.assets import Assets
from main.core.assets.tileset_atlas import GroundTiles
from tests.helpers.constants import POWERUP_KEYS


def test_assets_loads_and_sets_expected_fields(monkeypatch, fake_atlas, fake_ground_tiles, surface_factory):
    import main.core.assets.assets as assets_mod  # pylint: disable=import-outside-toplevel

    # arrange
    monkeypatch.setattr(assets_mod, "load_image", lambda path: surface_factory((64, 64)))
    monkeypatch.setattr(assets_mod, "build_tileset_atlas", lambda tileset, tile_size: fake_atlas)

    coins = [surface_factory((12, 12)), surface_factory((12, 12))]
    monkeypatch.setattr(assets_mod, "load_coin_sprites", lambda coin_base: coins)

    bird_frames = [surface_factory((7, 7)), surface_factory((7, 7))]
    monkeypatch.setattr(assets_mod, "load_bird_frames", lambda: bird_frames)

    player_frames = SimpleNamespace(
        run_frames=[surface_factory((40, 60)), surface_factory((40, 60))],
        crouch_frames=[surface_factory((40, 30)), surface_factory((40, 30))],
        stand_size=(40, 60),
        crouch_size=(40, 30),
    )
    monkeypatch.setattr(assets_mod, "load_player_frames", lambda: player_frames)

    powerups = {k: surface_factory((12, 12)) for k in POWERUP_KEYS}

    def _fake_load_powerups(*, extra_life_sprite):
        assert extra_life_sprite is fake_atlas.heart_base
        return list(powerups.items())

    monkeypatch.setattr(assets_mod, "load_powerups", _fake_load_powerups)

    shop_bg = surface_factory((100, 50))
    title_sign = surface_factory((80, 40))
    monkeypatch.setattr(assets_mod, "load_shop_background", lambda: shop_bg)
    monkeypatch.setattr(assets_mod, "load_title_sign", lambda: title_sign)

    # act
    a = Assets()

    # assert
    assert isinstance(a.ground, GroundTiles)
    assert a.ground is fake_ground_tiles
    assert a.ground.top_left is fake_ground_tiles.top_left
    assert a.ground.fill_right is fake_ground_tiles.fill_right
    assert a.tree_sprites == list(fake_atlas.tree_sprites)

    assert a.obstacles.rock_tiles == fake_atlas.rock_tiles
    assert a.obstacles.bird_frames == bird_frames

    assert a.collectibles.coins == coins
    assert a.collectibles.powerups.all == powerups

    assert a.player is player_frames

    assert a.ui.shop_background is shop_bg
    assert a.ui.title_sign is title_sign

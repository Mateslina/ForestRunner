# @generated [all] ChatGPT : generate tests based on class implementation
from pathlib import Path

import pygame as pg
import pytest

from main.core.assets import assets_loader


def test_load_image_uses_assets_dir_and_convert_alpha(
    patch_assets_dir,
    patch_pg_image_load,
    capture,
    surface_factory,
):
    patch_pg_image_load(surface_factory((5, 5)))

    out = assets_loader.load_image("tileset.png")

    assert capture["path"] == Path("/tmp/assets") / "tileset.png"
    assert capture["convert_alpha_called"] is True
    assert isinstance(out, pg.Surface)


@pytest.mark.parametrize(
    "name",
    [
        "tileset.png",
        "player/run_1.png",
        "ui/title_sign.png",
    ],
)
def test_load_image_joins_assets_dir_with_name(
    patch_assets_dir,
    patch_pg_image_load,
    capture,
    name,
    surface_factory,
):
    patch_pg_image_load(surface_factory((1, 1)))

    _ = assets_loader.load_image(name)

    assert capture["path"] == Path("/tmp/assets") / name

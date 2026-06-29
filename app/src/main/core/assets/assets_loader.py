"""
Asset loading utilities.

Provides helpers for loading image assets from the shared assets directory.
"""

from pathlib import Path
import pygame as pg

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "assets"


def load_image(name: str) -> pg.Surface:
    """Load an image from the assets folder with per-pixel alpha."""
    path = ASSETS_DIR / name
    return pg.image.load(path).convert_alpha()

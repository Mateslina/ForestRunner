# @generated [partially] ChatGPT : typing and suggested the factory/config model
"""
Game configuration and construction types.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Type

import pygame as pg

from main.core.game_state import GameState
from main.core.assets.assets import Assets
from main.core.background import ParallaxBackground
from main.core.save_system import load_save, save_game
from main.entities.player.player import Player
from main.entities.ground import Ground
from main.ui.hud import HUD
from main.ui.screens.base import BaseScreen


# --- screen typing ---
ScreenType = Type[BaseScreen]
ScreenMap = Mapping[GameState, ScreenType]


@dataclass
class SaveConfig:
    """Save/load callbacks."""
    loader: Callable[[], dict] = load_save
    writer: Callable[[int, dict[str, Any], int], None] = save_game


@dataclass
class PygameConfig:
    """Pygame runtime objects."""
    window: pg.Surface | None = None
    clock: pg.time.Clock | None = None


@dataclass
class FactoryConfig:
    """Factories for core systems."""
    background: Callable[..., Any] = ParallaxBackground
    player: Callable[..., Any] = Player
    ground: Callable[..., Any] = Ground
    hud: Callable[..., Any] = HUD


@dataclass
class FontConfig:
    """Font configuration."""
    name: str = "arialunicode"
    small_size: int = 28
    big_size: int = 56


@dataclass
class GameConfig:
    """Dependency injection / construction options."""
    assets: Assets | None = None
    save: SaveConfig = field(default_factory=SaveConfig)
    pygame: PygameConfig = field(default_factory=PygameConfig)
    factories: FactoryConfig = field(default_factory=FactoryConfig)
    fonts: FontConfig = field(default_factory=FontConfig)
    screen_map: ScreenMap | None = None

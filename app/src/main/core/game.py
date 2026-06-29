"""
Main game controller.

Initializes core systems, manages the main loop, handles screen switching,
and stores shared game-wide state.
"""

from dataclasses import dataclass
from typing import Any

import pygame as pg

from main.core.constants import WIDTH, HEIGHT, BASE_SPEED
from main.core.game_state import GameState
from main.core.assets.assets import Assets
from main.ui.screens.base import BaseScreen
from main.ui.screens.start import StartScreen
from main.ui.screens.playing.playing import PlayingScreen
from main.ui.screens.game_over import GameOverScreen
from main.ui.screens.shop.shop import ShopScreen

from main.core.game_config import (
    GameConfig,
    SaveConfig,
    PygameConfig,
    FactoryConfig,
    FontConfig,
    ScreenMap,
)


@dataclass
class RuntimeState:
    """Runtime-only state."""
    window: pg.Surface
    clock: pg.time.Clock
    running: bool = False
    screen: BaseScreen | None = None
    temp: dict | None = None


@dataclass
class ProgressState:
    """Persisted progress."""
    coins_bank: int
    upgrades: dict
    high_score: int


@dataclass
class Fonts:
    """Shared fonts."""
    small: Any
    big: Any


@dataclass
class GameContext:
    """Shared game systems used by screens."""
    assets: Assets
    background: Any
    player: Any
    ground: Any
    hud: Any
    fonts: Fonts
    progress: ProgressState


# @generated [partially] ChatGPT : suggested using the factory pattern and better dependency ijections for tests
class Game:
    """Main game controller handling loop and screen switching."""

    _DEFAULT_SCREENS: ScreenMap = {
        GameState.START: StartScreen,
        GameState.PLAYING: PlayingScreen,
        GameState.GAME_OVER: GameOverScreen,
        GameState.SHOP: ShopScreen,
    }

    def __init__(
        self,
        *,
        config: GameConfig | None = None,
        init_pygame: bool = True,
    ) -> None:
        cfg = config or GameConfig()

        if init_pygame:
            pg.init()  # pylint: disable=no-member

        self._screens: ScreenMap = cfg.screen_map or self._DEFAULT_SCREENS
        self._save_writer = cfg.save.writer

        self.runtime = self._init_runtime(cfg.pygame)
        self.ctx = self._init_context(cfg)

        self.set_screen(GameState.START)

    @staticmethod
    def _init_runtime(cfg: PygameConfig) -> RuntimeState:
        """Initialize pygame window/clock and runtime state."""
        window = cfg.window or pg.display.set_mode((WIDTH, HEIGHT))
        clock = cfg.clock or pg.time.Clock()
        pg.display.set_caption("Forest Runner")
        return RuntimeState(window=window, clock=clock)

    def _init_context(self, cfg: GameConfig) -> GameContext:
        """Initialize shared game systems (assets, world, UI, progress)."""
        assets = cfg.assets or Assets()
        progress = self._load_progress(cfg.save)
        fonts = self._build_fonts(cfg.fonts)

        background = self._build_background(cfg.factories, assets)
        player = cfg.factories.player(assets)
        ground = self._build_ground(cfg.factories, assets)
        hud = cfg.factories.hud(fonts.small, fonts.big, assets)

        return GameContext(
            assets=assets,
            background=background,
            player=player,
            ground=ground,
            hud=hud,
            fonts=fonts,
            progress=progress,
        )

    @staticmethod
    def _load_progress(cfg: SaveConfig) -> ProgressState:
        """Load persisted progress from storage."""
        save_data = cfg.loader()
        return ProgressState(
            coins_bank=save_data["coins_bank"],
            upgrades=save_data["upgrades"],
            high_score=save_data["high_score"],
        )

    @staticmethod
    def _build_fonts(cfg: FontConfig) -> Fonts:
        """Create shared fonts."""
        font_small = pg.font.SysFont(cfg.name, cfg.small_size)
        font_big = pg.font.SysFont(cfg.name, cfg.big_size)
        return Fonts(small=font_small, big=font_big)

    @staticmethod
    def _build_background(factories: FactoryConfig, assets: Assets) -> Any:
        """Create parallax background."""
        return factories.background(
            assets.tree_sprites,
            ground_fill_tile=assets.ground.fill_mid,
        )

    @staticmethod
    def _build_ground(factories: FactoryConfig, assets: Assets) -> Any:
        """Create ground system."""
        return factories.ground(BASE_SPEED, tiles=assets.ground)

    def run(self) -> None:
        """Start the main game loop."""
        self.runtime.running = True

        while self.runtime.running:
            dt = self.runtime.clock.tick(60) / 1000.0  # capped 60 fps

            for event in pg.event.get():
                if event.type == pg.QUIT:  # pylint: disable=no-member
                    self.runtime.running = False
                else:
                    self.runtime.screen.handle_events(event)

            self.runtime.screen.update(dt)
            self.draw()

        self._save_writer(
            self.ctx.progress.coins_bank,
            self.ctx.progress.upgrades,
            self.ctx.progress.high_score,
        )
        pg.quit()  # pylint: disable=no-member

    def set_screen(self, state: GameState) -> None:
        """Switch to a new game screen."""
        self.runtime.temp = None if state != GameState.GAME_OVER else self.runtime.temp

        if state == GameState.START:
            self.ctx.ground.reset(BASE_SPEED)

        self.runtime.screen = self._screens[state](self)

    def draw(self) -> None:
        """Draw the active screen and flip the display."""
        self.runtime.screen.draw()
        pg.display.flip()

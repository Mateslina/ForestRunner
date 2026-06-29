"""
Playing screen.

UI + input forwarding + rendering.
"""

import pygame as pg

from main.ui.screens.base import BaseScreen
from main.ui.screens.playing.playing_controller import PlayingController
from main.ui.hud import HudState


class PlayingScreen(BaseScreen):
    """Main gameplay screen"""

    def __init__(self, game):
        super().__init__(game)
        self.ctrl = PlayingController(game)

    def handle_events(self, event) -> None:
        if event.type == pg.KEYDOWN:  # pylint: disable=no-member
            if event.key == pg.K_UP:  # pylint: disable=no-member
                self.ctrl.on_jump()
            elif event.key == pg.K_DOWN:  # pylint: disable=no-member
                self.ctrl.set_crouch(True)

        elif event.type == pg.KEYUP:  # pylint: disable=no-member
            if event.key == pg.K_DOWN:  # pylint: disable=no-member
                self.ctrl.set_crouch(False)

    def update(self, dt: float) -> None:
        self.ctrl.update(dt)

    def draw(self) -> None:
        win = self.game.runtime.window

        self.game.ctx.background.draw(win)
        self.game.ctx.ground.draw(win)
        self.game.ctx.player.draw(win)

        self.ctrl.obstacles.draw(win)
        self.ctrl.collectibles.draw(win)

        hud_state = HudState(
            score=self.ctrl.display_score,
            collected_coins=self.ctrl.run.collected_coins,
            lives=self.ctrl.run.lives,
            max_lives=self.ctrl.run.max_lives,
            double_score_time=self.ctrl.run.buffs.double_score_time,
        )
        self.game.ctx.hud.draw(win, hud_state)

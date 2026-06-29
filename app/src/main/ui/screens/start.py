"""
Start screen.

Shows the title, controls hint, and buttons to play, open the shop, or quit.
"""

import pygame as pg

from main.ui.screens.base import BaseScreen
from main.ui.ui_helpers import (
    WHITE,
    layout_button_group,
    draw_button_group,
    clicked_button,
)
from main.core.game_state import GameState
from main.core.constants import HEIGHT, BASE_SPEED


_START_LABELS: dict[GameState, str] = {
    GameState.PLAYING: "PLAY",
    GameState.SHOP: "SHOP",
    GameState.QUIT: "QUIT",
}


class StartScreen(BaseScreen):
    """Main menu / start screen."""

    def __init__(self, game):
        super().__init__(game)
        self.buttons: dict[GameState, pg.Rect] = {}

    # ---------- UI helpers ----------

    def _draw_controls_hint(self, win: pg.Surface, w: int, h: int) -> None:
        controls_x = w - 300
        controls_y = h - 200

        font = self.game.ctx.fonts.small
        win.blit(font.render("Controls:", True, WHITE), (controls_x, controls_y))
        win.blit(font.render("↑  Jump", True, WHITE), (controls_x, controls_y + 28))
        win.blit(font.render("↓  Crouch", True, WHITE), (controls_x, controls_y + 56))

    def _draw_title(self, win: pg.Surface) -> None:
        sign = self.game.ctx.assets.ui.title_sign
        sign_rect = sign.get_rect(center=(win.get_width() // 2, HEIGHT // 3))
        win.blit(sign, sign_rect)

        title = self.game.ctx.fonts.big.render("FOREST RUNNER", True, WHITE)
        win.blit(
            title,
            (
                sign_rect.centerx - title.get_width() // 2,
                sign_rect.centery - title.get_height() // 2 + 30,
            ),
        )

    # ---------- screen lifecycle ----------

    def handle_events(self, event) -> None:
        action = clicked_button(event, self.buttons)
        if action is None:
            return

        if action == GameState.QUIT:
            self.game.runtime.running = False
        else:
            self.game.set_screen(action)

    def update(self, dt: float) -> None:
        self.game.ctx.ground.speed = BASE_SPEED
        self.game.ctx.background.update(dt, BASE_SPEED)
        self.game.ctx.ground.update(dt)

    def draw(self) -> None:
        win = self.game.runtime.window
        w, h = win.get_size()

        self.game.ctx.background.draw(win)
        self.game.ctx.ground.draw(win)

        self._draw_title(win)
        self._draw_controls_hint(win, w, h)

        self.buttons = layout_button_group(
            w,
            h,
            keys=[GameState.PLAYING, GameState.SHOP, GameState.QUIT],
        )
        draw_button_group(
            win,
            self.game.ctx.fonts.small,
            self.buttons,
            _START_LABELS,
        )

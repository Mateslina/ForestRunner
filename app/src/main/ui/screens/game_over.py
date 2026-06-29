"""
Game over screen.

Displays final results (score, high score, total coins) and provides
navigation actions to restart, open the shop, or return to the title.
"""

import pygame as pg

from main.ui.screens.base import BaseScreen
from main.ui.ui_helpers import (
    WHITE,
    layout_button_group,
    draw_button_group,
    clicked_button,
    draw_bank_coins_top_right,
)
from main.core.game_state import GameState
from main.core.constants import WIDTH, HEIGHT


_GAMEOVER_LABELS: dict[GameState, str] = {
    GameState.PLAYING: "RESTART",
    GameState.SHOP: "SHOP",
    GameState.START: "TITLE",
}


class GameOverScreen(BaseScreen):
    """Game over UI."""

    def __init__(self, game):
        super().__init__(game)

        temp = self.game.runtime.temp or {}
        self.final_score = temp.get("final_score", 0)
        self.run_coins = temp.get("coins_collected", 0)

        self.buttons: dict[GameState, pg.Rect] = {}

        self._overlay: pg.Surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)  # pylint: disable=no-member
        self._overlay.fill((0, 0, 0, 160))

        self._coin_ui_cache: dict = {}

    # ---------- UI helpers ----------

    def _draw_backdrop(self, win: pg.Surface) -> None:
        self.game.ctx.background.draw(win)
        self.game.ctx.ground.draw(win)
        self.game.ctx.player.draw(win)

    def _draw_title(self, win: pg.Surface, title_y: int) -> None:
        title = self.game.ctx.fonts.big.render("GAME OVER", True, WHITE)
        rect = title.get_rect(center=(WIDTH // 2, title_y))
        win.blit(title, rect)

    def _draw_scores(self, win: pg.Surface, w: int, title_y: int) -> None:
        # display the scores in two columns
        col_y_label = title_y + 80
        col_y_value = col_y_label + 46

        left_x = w // 2 - 140
        right_x = w // 2 + 140

        label_font = self.game.ctx.fonts.small
        value_font = self.game.ctx.fonts.big

        your_label = label_font.render("Your Score", True, WHITE)
        high_label = label_font.render("High Score", True, WHITE)

        your_value = value_font.render(str(self.final_score), True, WHITE)
        high_value = value_font.render(str(self.game.ctx.progress.high_score), True, WHITE)

        win.blit(your_label, (left_x - your_label.get_width() // 2, col_y_label))
        win.blit(high_label, (right_x - high_label.get_width() // 2, col_y_label))

        win.blit(your_value, (left_x - your_value.get_width() // 2, col_y_value))
        win.blit(high_value, (right_x - high_value.get_width() // 2, col_y_value))

    # ---------- input / update / draw ----------

    def handle_events(self, event) -> None:
        action = clicked_button(event, self.buttons)
        if action is not None:
            self.game.set_screen(action)

    def update(self, dt: float) -> None:
        _ = dt

    def draw(self) -> None:
        win = self.game.runtime.window
        w, h = win.get_size()

        self._draw_backdrop(win)
        win.blit(self._overlay, (0, 0))

        draw_bank_coins_top_right(
            win=win,
            window_w=w,
            coins_bank=self.game.ctx.progress.coins_bank,
            base_coin=self.game.ctx.assets.collectibles.coins.normal,
            cache=self._coin_ui_cache,
        )

        title_y = int(h * 0.18)
        self._draw_title(win, title_y)
        self._draw_scores(win, w, title_y)

        self.buttons = layout_button_group(
            w,
            h,
            keys=[GameState.PLAYING, GameState.SHOP, GameState.START],
        )
        draw_button_group(
            win,
            self.game.ctx.fonts.small,
            self.buttons,
            _GAMEOVER_LABELS,
        )

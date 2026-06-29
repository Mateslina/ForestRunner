"""
Shop screen.

Lets the player buy upgrades using coins earned in runs.
"""
# pylint: disable=R0801

import pygame as pg

from main.ui.screens.base import BaseScreen
from main.ui.ui_helpers import (
    WHITE,
    make_button_drawer,
    ButtonStyle,
    draw_bank_coins_top_right,
)
from main.ui.screens.shop.shop_logic import ShopLogic, DEFAULT_SHOP_ITEMS
from main.core.game_state import GameState
from main.core.constants import WIDTH, HEIGHT


class ShopScreen(BaseScreen):
    """Upgrade shop screen."""

    _BTN_BUY = (70, 170, 110)
    _BTN_LOCKED = (120, 120, 120)

    _BACK_W, _BACK_H = 120, 42
    _BACK_X, _BACK_Y = 20, 16

    _BUY_W, _BUY_H = 120, 38
    _BUY_GAP_Y = 38
    _BUY_RADIUS = 10

    def __init__(self, game):
        super().__init__(game)

        self.font = self.game.ctx.fonts.small
        self.font_big = self.game.ctx.fonts.big

        self.logic = ShopLogic(
            self.game.ctx.progress,
            items=DEFAULT_SHOP_ITEMS,
        )

        self.buttons: list[pg.Rect] = []
        self.back_button: pg.Rect | None = None

        self._bg: pg.Surface = pg.transform.smoothscale(
            self.game.ctx.assets.ui.shop_background, (WIDTH, HEIGHT)
        )
        self._coin_ui_cache: dict = {}

    # ---------- helpers ----------

    def _draw_back_button(self, win: pg.Surface) -> None:
        self.back_button = pg.Rect(
            self._BACK_X, self._BACK_Y, self._BACK_W, self._BACK_H
        )

        mx, my = pg.mouse.get_pos()
        hovered = self.back_button.collidepoint((mx, my))

        # creates a button drawing function
        draw_btn = make_button_drawer(win, self.font, ButtonStyle(radius=12))
        draw_btn(self.back_button, "Back", hovered)

    def _item_button_rect(self, cx: int, center_y: int, icon_h: int) -> pg.Rect:
        return pg.Rect(
            cx - self._BUY_W // 2,
            center_y + icon_h // 2 + self._BUY_GAP_Y,
            self._BUY_W,
            self._BUY_H,
        )

    # @generated [all] ChatGPT : make a draw item function tha will have the item icon and upgrade button centered below it
    def _draw_item(
        self, win: pg.Surface, item, cx: int, center_y: int
    ) -> pg.Rect:
        sprite = self.game.ctx.assets.collectibles.powerups.all[item.kind]
        sw, sh = sprite.get_size()
        win.blit(sprite, (cx - sw // 2, center_y - sh // 2))

        lvl = self.logic.level(item.key)
        lvl_surf = self.font.render(f"Lv {lvl}/{item.max_level}", True, WHITE)
        win.blit(lvl_surf, (cx - lvl_surf.get_width() // 2, center_y + sh // 2 + 8))

        btn_rect = self._item_button_rect(cx, center_y, sh)
        pg.draw.rect(
            win,
            self._BTN_BUY if self.logic.can_buy(item) else self._BTN_LOCKED,
            btn_rect,
            border_radius=self._BUY_RADIUS,
        )

        label = "MAX" if lvl >= item.max_level else str(self.logic.cost(item))
        label_surf = self.font.render(label, True, WHITE)
        win.blit(
            label_surf,
            (
                btn_rect.centerx - label_surf.get_width() // 2,
                btn_rect.centery - label_surf.get_height() // 2,
            ),
        )

        return btn_rect

    # ---------- input ----------

    def handle_events(self, event) -> None:
        if (
            event.type == pg.MOUSEBUTTONDOWN and event.button == 1  # pylint: disable=no-member
        ):
            if self.back_button is not None and self.back_button.collidepoint(
                event.pos
            ):
                self.game.set_screen(GameState.START)
                return

            # go through buy button - item pairs
            for rect, item in zip(self.buttons, self.logic.items):
                if rect.collidepoint(event.pos):
                    self.logic.buy(item)
                    return

    # not needed
    def update(self, dt: float) -> None:
        _ = dt

    # ---------- draw ----------

    def draw(self) -> None:
        win = self.game.runtime.window
        w, h = win.get_size()

        win.blit(self._bg, (0, 0))

        self._draw_back_button(win)
        draw_bank_coins_top_right(
            win=win,
            window_w=w,
            coins_bank=self.game.ctx.progress.coins_bank,
            base_coin=self.game.ctx.assets.collectibles.coins.normal,
            cache=self._coin_ui_cache,
        )

        # where to display each item
        center_y, spacing = int(h * 0.75), w // (len(self.logic.items) + 1)

        # draw all shop items at equal spacing and their buy buttons
        self.buttons.clear()
        for i, item in enumerate(self.logic.items):
            self.buttons.append(self._draw_item(win, item, spacing * (i + 1), center_y))
